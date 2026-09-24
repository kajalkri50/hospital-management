"""
REST API layer — session auth for browser clients; validate inputs on all mutations.
"""

from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from appointments.models import Appointment
from appointments.services import get_available_slots
from hospitals.models import Department, Doctor, Hospital
from hospitals.services import annotate_hospitals_with_distance, filter_hospitals, nearest_emergency_hospitals
from payments.models import Payment
from payments.services import ensure_payment_and_checkout

from .serializers import (
    AppointmentBookSerializer,
    AppointmentReadSerializer,
    DoctorSerializer,
    HospitalSerializer,
    PaymentCreateSerializer,
    UserRegistrationSerializer,
)


@method_decorator(ensure_csrf_cookie, name="dispatch")
class EnsureCsrfCookieView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"detail": "CSRF cookie set"})


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = UserRegistrationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        login(request, user)
        return Response(
            {"id": user.id, "username": user.username, "role": user.role},
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        login(request, user)
        return Response({"id": user.id, "username": user.username, "role": user.role})


class HospitalsNearbyAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        department = request.query_params.get("department")
        min_rating = request.query_params.get("min_rating")
        emergency = request.query_params.get("emergency")
        min_beds = request.query_params.get("min_beds")

        qs = filter_hospitals(
            department=department,
            min_rating=float(min_rating) if min_rating else None,
            emergency_only=emergency in ("1", "true", "True") if emergency else None,
            min_general_beds=int(min_beds) if min_beds else None,
        )
        if not lat or not lng:
            data = HospitalSerializer(qs[:50], many=True).data
            return Response({"results": data})

        la, ln = float(lat), float(lng)
        ranked = annotate_hospitals_with_distance(qs, la, ln)
        out = []
        for row in ranked[:50]:
            h = row["hospital"]
            s = HospitalSerializer(h).data
            s["distance_km"] = row["distance_km"]
            out.append(s)
        return Response({"results": out})


class HospitalDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        h = get_object_or_404(Hospital, pk=pk)
        return Response(HospitalSerializer(h).data)


class DoctorsByHospitalAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, hospital_id):
        docs = Doctor.objects.filter(hospital_id=hospital_id).select_related("hospital", "department")
        return Response(DoctorSerializer(docs, many=True).data)


class AppointmentBookAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = AppointmentBookSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        doctor = get_object_or_404(Doctor, pk=ser.validated_data["doctor_id"])
        dept = get_object_or_404(Department, pk=ser.validated_data["department_id"], hospital=doctor.hospital)
        if dept.pk != doctor.department_id:
            return Response({"detail": "Department mismatch"}, status=status.HTTP_400_BAD_REQUEST)
        when = ser.validated_data["scheduled_at"]
        if timezone.is_naive(when):
            when = timezone.make_aware(when, timezone.get_current_timezone())
        slots = get_available_slots(doctor, when.date())

        def norm(t):
            return t.replace(second=0, microsecond=0)

        if norm(when) not in {norm(s) for s in slots}:
            return Response({"detail": "Slot not available"}, status=status.HTTP_400_BAD_REQUEST)
        appt = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            hospital=doctor.hospital,
            department=dept,
            scheduled_at=when,
            status=Appointment.Status.PENDING_PAYMENT,
            notes=ser.validated_data.get("notes") or "",
        )
        return Response(AppointmentReadSerializer(appt).data, status=status.HTTP_201_CREATED)


class UserAppointmentsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = request.user.appointments.select_related("hospital", "doctor", "department")
        return Response(AppointmentReadSerializer(qs, many=True).data)


class PaymentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = PaymentCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        appt = get_object_or_404(
            Appointment,
            pk=ser.validated_data["appointment_id"],
            patient=request.user,
            status=Appointment.Status.PENDING_PAYMENT,
        )
        url = ensure_payment_and_checkout(request, appt)
        if not url:
            Payment.objects.get_or_create(
                appointment=appt,
                defaults={
                    "amount_cents": 2500,
                    "currency": "usd",
                    "provider": Payment.Provider.STRIPE,
                    "status": Payment.Status.PENDING,
                },
            )
            return Response(
                {"checkout_url": None, "detail": "Stripe not configured; use demo pay in DEBUG or set keys."},
                status=status.HTTP_200_OK,
            )
        return Response({"checkout_url": url})


class EmergencyNearestAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        if not lat or not lng:
            return Response({"detail": "lat and lng required"}, status=status.HTTP_400_BAD_REQUEST)
        top = nearest_emergency_hospitals(float(lat), float(lng), limit=3)
        results = []
        for row in top:
            h = row["hospital"]
            data = HospitalSerializer(h).data
            data["distance_km"] = row["distance_km"]
            results.append(data)
        return Response({"results": results})


class HospitalResourcesPollAPIView(APIView):
    """Public read for bed counts — polled every few seconds from the UI."""

    permission_classes = [AllowAny]

    def get(self, request, hospital_id):
        h = get_object_or_404(Hospital, pk=hospital_id)
        res = getattr(h, "resources", None)
        if not res:
            return Response(
                {
                    "hospital_id": h.id,
                    "icu_beds_available": 0,
                    "general_beds_available": 0,
                    "ventilators_available": 0,
                    "ambulances_available": 0,
                    "updated_at": None,
                }
            )
        return Response(
            {
                "hospital_id": h.id,
                "icu_beds_available": res.icu_beds_available,
                "general_beds_available": res.general_beds_available,
                "ventilators_available": res.ventilators_available,
                "ambulances_available": res.ambulances_available,
                "updated_at": res.updated_at.isoformat() if res.updated_at else None,
            }
        )
