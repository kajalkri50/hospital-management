"""
Template views: discovery, emergency, dashboards (patient / hospital admin / doctor).
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView

from accounts.mixins import HospitalAdminRequiredMixin
from accounts.models import User
from appointments.models import Appointment

from .models import Department, Doctor, Hospital, HospitalResources
from .services import annotate_hospitals_with_distance, filter_hospitals, nearest_emergency_hospitals
import json
from django.core.serializers.json import DjangoJSONEncoder
from .models import Hospital


def home(request):
    # Get all hospitals for the map
    all_hospitals = Hospital.objects.all()
    
    # Get featured hospitals (top 10 by rating) for the cards section
    featured_hospitals = (
        Hospital.objects.select_related("resources")
        .all()
        .order_by("-rating")[:10]
    )

    # Prepare JSON data for map
    hospitals_json = json.dumps(
        list(all_hospitals.values("name", "latitude", "longitude")),
        cls=DjangoJSONEncoder
    )

    return render(request, "home.html", {
        "featured_hospitals": featured_hospitals,
        "hospitals_json": hospitals_json
    })


def hospital_search(request):
    lat = request.GET.get("lat")
    lng = request.GET.get("lng")
    department = request.GET.get("department") or None
    min_rating = request.GET.get("min_rating")
    emergency_only = request.GET.get("emergency") == "1"
    min_beds = request.GET.get("min_beds")

    qs = filter_hospitals(
        department=department,
        min_rating=float(min_rating) if min_rating else None,
        emergency_only=emergency_only if request.GET.get("emergency") else None,
        min_general_beds=int(min_beds) if min_beds else None,
    )

    hospitals_data = []
    if lat and lng:
        try:
            la, ln = float(lat), float(lng)
            hospitals_data = annotate_hospitals_with_distance(qs, la, ln)
        except (TypeError, ValueError):
            hospitals_data = [{"hospital": h, "distance_km": None} for h in qs[:50]]
    else:
        hospitals_data = [{"hospital": h, "distance_km": None} for h in qs[:50]]

    departments = (
        Department.objects.values_list("name", flat=True).distinct().order_by("name")[:200]
    )
    return render(
        request,
        "hospitals/search.html",
        {
            "hospitals_data": hospitals_data,
            "department_choices": departments,
            "filters": {
                "lat": lat or "",
                "lng": lng or "",
                "department": department or "",
                "min_rating": min_rating or "",
                "emergency": emergency_only,
                "min_beds": min_beds or "",
            },
        },
    )


def hospital_detail(request, slug):
    hospital = get_object_or_404(Hospital, slug=slug)
    departments = hospital.departments.annotate(doc_count=Count("doctors")).order_by("name")
    resources = getattr(hospital, "resources", None)
    return render(
        request,
        "hospitals/detail.html",
        {"hospital": hospital, "departments": departments, "resources": resources},
    )


def doctor_list(request, slug):
    hospital = get_object_or_404(Hospital, slug=slug)
    doctors = hospital.doctors.select_related("department").order_by("department__name", "last_name")
    return render(
        request,
        "hospitals/doctor_list.html",
        {"hospital": hospital, "doctors": doctors},
    )


def doctor_detail(request, pk):
    doctor = get_object_or_404(Doctor.objects.select_related("hospital", "department"), pk=pk)
    schedules = doctor.schedules.all()
    return render(
        request,
        "hospitals/doctor_detail.html",
        {"doctor": doctor, "schedules": schedules},
    )


def emergency_page(request):
    return render(request, "emergency.html")


def emergency_results(request):
    """Accept lat/lng via GET or POST — show top 3 emergency hospitals."""
    lat = request.POST.get("lat") or request.GET.get("lat")
    lng = request.POST.get("lng") or request.GET.get("lng")
    if not lat or not lng:
        messages.error(request, "Location required for emergency search.")
        return redirect("hospitals:emergency")
    try:
        la, ln = float(lat), float(lng)
    except (TypeError, ValueError):
        messages.error(request, "Invalid coordinates.")
        return redirect("hospitals:emergency")
    top = nearest_emergency_hospitals(la, ln, limit=3)
    return render(request, "emergency_results.html", {"results": top, "lat": la, "lng": ln})


@login_required
def patient_dashboard(request):
    u = request.user
    if not (u.role == User.Role.PATIENT or u.is_app_super_admin()):
        return redirect("dashboard")
    upcoming = (
        u.appointments.filter(
            status__in=[
                Appointment.Status.PENDING_PAYMENT,
                Appointment.Status.PENDING_APPROVAL,
                Appointment.Status.CONFIRMED,
            ]
        )
        .select_related("hospital", "doctor", "department")
        .order_by("scheduled_at")[:8]
    )
    unread = u.notifications.filter(read=False).count()
    return render(
        request,
        "dashboard/patient.html",
        {"upcoming_appointments": upcoming, "unread_notifications": unread},
    )


def _managed_hospitals(user: User):
    if user.is_superuser or user.role == User.Role.SUPER_ADMIN:
        return Hospital.objects.all()
    return Hospital.objects.filter(admin_user=user)


class HospitalAdminDashboardView(HospitalAdminRequiredMixin, TemplateView):
    template_name = "admin_dashboard/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        hospitals = _managed_hospitals(self.request.user)
        hid = self.request.GET.get("hospital")
        hospital = None
        if hospitals.count() == 1:
            hospital = hospitals.first()
        elif hid:
            hospital = get_object_or_404(hospitals, pk=int(hid))
        elif hospitals.exists():
            hospital = hospitals.first()
        total_appts = Appointment.objects.filter(hospital__in=hospitals).count()
        pending = Appointment.objects.filter(
            hospital__in=hospitals, status=Appointment.Status.PENDING_APPROVAL
        ).count()
        ctx.update(
            {
                "managed_hospitals": hospitals,
                "selected_hospital": hospital,
                "total_appointments": total_appts,
                "pending_approvals": pending,
            }
        )
        if hospital:
            res = getattr(hospital, "resources", None)
            ctx["bed_snapshot"] = res
            ctx["recent_appointments"] = (
                Appointment.objects.filter(hospital=hospital)
                .select_related("patient", "doctor")
                .order_by("-created_at")[:10]
            )
        return ctx


@login_required
def doctor_portal(request):
    u = request.user
    if not u.is_doctor_role() and not u.is_app_super_admin():
        return redirect("dashboard")
    doc = getattr(u, "doctor_profile", None)
    if not doc:
        return render(
            request,
            "dashboard/doctor.html",
            {"doctor": None, "appointments": []},
        )
    appts = (
        Appointment.objects.filter(doctor=doc)
        .select_related("patient", "hospital")
        .order_by("-scheduled_at")[:20]
    )
    return render(request, "dashboard/doctor.html", {"doctor": doc, "appointments": appts})


@login_required
def hospital_admin_doctors(request):
    if not (request.user.is_hospital_admin() or request.user.is_app_super_admin()):
        raise Http404()
    hospitals = _managed_hospitals(request.user)
    hospital = None
    if hospitals.count() == 1:
        hospital = hospitals.first()
    elif request.GET.get("hospital"):
        hospital = get_object_or_404(hospitals, pk=int(request.GET["hospital"]))
    doctors = []
    if hospital:
        doctors = hospital.doctors.select_related("department").order_by("last_name")
    return render(
        request,
        "admin_dashboard/doctors.html",
        {"managed_hospitals": hospitals, "hospital": hospital, "doctors": doctors},
    )


@login_required
def hospital_admin_resources(request):
    if not (request.user.is_hospital_admin() or request.user.is_app_super_admin()):
        raise Http404()
    hospitals = _managed_hospitals(request.user)
    hospital = None
    if hospitals.count() == 1:
        hospital = hospitals.first()
    elif request.GET.get("hospital"):
        hospital = get_object_or_404(hospitals, pk=int(request.GET["hospital"]))
    resources = None
    if hospital:
        resources, _ = HospitalResources.objects.get_or_create(hospital=hospital)
    if request.method == "POST" and hospital and resources:
        resources.icu_beds_total = int(request.POST.get("icu_beds_total") or 0)
        resources.icu_beds_available = int(request.POST.get("icu_beds_available") or 0)
        resources.general_beds_total = int(request.POST.get("general_beds_total") or 0)
        resources.general_beds_available = int(request.POST.get("general_beds_available") or 0)
        resources.ventilators_available = int(request.POST.get("ventilators_available") or 0)
        resources.ambulances_available = int(request.POST.get("ambulances_available") or 0)
        resources.save()
        messages.success(request, "Resource counts updated.")
        return redirect(f"{request.path}?hospital={hospital.pk}")
    return render(
        request,
        "admin_dashboard/resources.html",
        {"managed_hospitals": hospitals, "hospital": hospital, "resources": resources},
    )


@login_required
def hospital_admin_appointments(request):
    if not (request.user.is_hospital_admin() or request.user.is_app_super_admin()):
        raise Http404()
    hospitals = _managed_hospitals(request.user)
    hospital = None
    if hospitals.count() == 1:
        hospital = hospitals.first()
    elif request.GET.get("hospital"):
        hospital = get_object_or_404(hospitals, pk=int(request.GET["hospital"]))
    appts = []
    if hospital:
        appts = (
            Appointment.objects.filter(hospital=hospital)
            .select_related("patient", "doctor", "department")
            .order_by("-scheduled_at")
        )
    if request.method == "POST" and hospital:
        aid = request.POST.get("appointment_id")
        action = request.POST.get("action")
        appt = get_object_or_404(Appointment, pk=aid, hospital=hospital)
        if action == "approve" and appt.status == Appointment.Status.PENDING_APPROVAL:
            appt.status = Appointment.Status.CONFIRMED
            appt.save()
            from notifications.services import notify_user

            notify_user(
                user=appt.patient,
                kind="appointment_confirmed",
                title="Appointment approved",
                body=f"Your appointment at {hospital.name} on {appt.scheduled_at} is confirmed.",
                appointment=appt,
            )
            messages.success(request, "Appointment approved.")
        elif action == "reject" and appt.status == Appointment.Status.PENDING_APPROVAL:
            appt.status = Appointment.Status.REJECTED
            appt.save()
            from notifications.services import notify_user

            notify_user(
                user=appt.patient,
                kind="appointment_cancelled",
                title="Appointment not approved",
                body=f"Your booking at {hospital.name} was not approved. Please contact the hospital.",
                appointment=appt,
            )
            messages.warning(request, "Appointment rejected.")
        return redirect(f"{request.path}?hospital={hospital.pk}")
    return render(
        request,
        "admin_dashboard/appointments.html",
        {"managed_hospitals": hospitals, "hospital": hospital, "appointments": appts},
    )
