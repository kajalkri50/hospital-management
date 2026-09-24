"""
Booking workflow, appointment history, cancel/reschedule.
"""

import datetime as dt

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import User
from hospitals.models import Department, Doctor, Hospital

from .models import Appointment
from .services import get_available_slots


@login_required
def book_appointment(request, slug):
    if request.user.role != User.Role.PATIENT and not request.user.is_app_super_admin():
        raise Http404()
    hospital = get_object_or_404(Hospital, slug=slug)
    departments = hospital.departments.order_by("name")
    doctors = hospital.doctors.select_related("department").order_by("department__name", "last_name")
    selected_dept = request.GET.get("department_id")
    if selected_dept:
        try:
            doctors = doctors.filter(department_id=int(selected_dept))
        except ValueError:
            pass
    selected_doctor = request.GET.get("doctor_id")
    date_str = request.GET.get("date") or timezone.localdate().isoformat()

    try:
        on_date = dt.date.fromisoformat(date_str)
    except ValueError:
        on_date = timezone.localdate()

    doctor = None
    slots = []
    if selected_doctor:
        doctor = get_object_or_404(Doctor, pk=int(selected_doctor), hospital=hospital)
        slots = get_available_slots(doctor, on_date)

    if request.method == "POST":
        doctor = get_object_or_404(Doctor, pk=int(request.POST["doctor_id"]), hospital=hospital)
        dept = get_object_or_404(Department, pk=int(request.POST["department_id"]), hospital=hospital)
        if dept.pk != doctor.department_id:
            messages.error(request, "Department does not match selected doctor.")
            return redirect(request.path + f"?doctor_id={doctor.pk}&date={on_date.isoformat()}")
        slot_raw = request.POST.get("scheduled_at")
        if not slot_raw:
            messages.error(request, "Choose a time slot.")
            return redirect(request.path + f"?doctor_id={doctor.pk}&date={on_date.isoformat()}")
        scheduled_at = timezone.datetime.fromisoformat(slot_raw.replace("Z", "+00:00"))
        if timezone.is_naive(scheduled_at):
            scheduled_at = timezone.make_aware(scheduled_at, timezone.get_current_timezone())
        cand = get_available_slots(doctor, scheduled_at.date())

        def norm(t):
            return t.replace(second=0, microsecond=0)

        if norm(scheduled_at) not in {norm(s) for s in cand}:
            messages.error(request, "That slot is no longer available.")
            return redirect(request.path + f"?doctor_id={doctor.pk}&date={scheduled_at.date().isoformat()}")
        appt = Appointment.objects.create(
            patient=request.user,
            doctor=doctor,
            hospital=hospital,
            department=dept,
            scheduled_at=scheduled_at,
            status=Appointment.Status.PENDING_PAYMENT,
            notes=request.POST.get("notes", "")[:2000],
        )
        from payments.services import ensure_payment_and_checkout

        url = ensure_payment_and_checkout(request, appt)
        if url:
            return redirect(url)
        messages.info(request, "Appointment created. Complete payment when ready from your history.")
        return redirect("appointments:history")

    return render(
        request,
        "appointments/book.html",
        {
            "hospital": hospital,
            "departments": departments,
            "doctors": doctors,
            "selected_dept": selected_dept,
            "doctor": doctor,
            "slots": slots,
            "on_date": on_date,
            "date_str": on_date.isoformat(),
        },
    )


@login_required
def appointment_history(request):
    from django.conf import settings

    appts = (
        request.user.appointments.select_related("hospital", "doctor", "department", "payment")
        .order_by("-scheduled_at")
    )
    return render(
        request,
        "appointments/history.html",
        {"appointments": appts, "debug": settings.DEBUG},
    )


@login_required
def cancel_appointment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, patient=request.user)
    if appt.status in (Appointment.Status.CANCELLED, Appointment.Status.COMPLETED, Appointment.Status.REJECTED):
        messages.warning(request, "This appointment cannot be cancelled.")
        return redirect("appointments:history")
    if request.method == "POST":
        appt.status = Appointment.Status.CANCELLED
        appt.save()
        from notifications.services import notify_user

        notify_user(
            user=request.user,
            kind="appointment_cancelled",
            title="Appointment cancelled",
            body=f"Cancelled appointment at {appt.hospital.name} on {appt.scheduled_at}.",
            appointment=appt,
        )
        messages.success(request, "Appointment cancelled.")
        return redirect("appointments:history")
    return render(request, "appointments/cancel_confirm.html", {"appointment": appt})


@login_required
def reschedule_appointment(request, pk):
    appt = get_object_or_404(Appointment, pk=pk, patient=request.user)
    if appt.status not in (
        Appointment.Status.CONFIRMED,
        Appointment.Status.PENDING_APPROVAL,
    ):
        messages.warning(request, "Only confirmed or pending appointments can be rescheduled.")
        return redirect("appointments:history")
    date_str = request.GET.get("date") or appt.scheduled_at.date().isoformat()
    try:
        on_date = dt.date.fromisoformat(date_str)
    except ValueError:
        on_date = appt.scheduled_at.date()
    slots = get_available_slots(appt.doctor, on_date)
    if request.method == "POST":
        slot_raw = request.POST.get("scheduled_at")
        if not slot_raw:
            messages.error(request, "Pick a new slot.")
            return redirect(request.path)
        new_t = timezone.datetime.fromisoformat(slot_raw.replace("Z", "+00:00"))
        if timezone.is_naive(new_t):
            new_t = timezone.make_aware(new_t, timezone.get_current_timezone())
        cand = get_available_slots(appt.doctor, new_t.date())

        def norm(t):
            return t.replace(second=0, microsecond=0)

        if norm(new_t) not in {norm(s) for s in cand}:
            messages.error(request, "That slot is not available.")
            return redirect(request.path)
        appt.scheduled_at = new_t
        appt.status = Appointment.Status.PENDING_APPROVAL
        appt.save()
        messages.success(request, "Rescheduled; pending hospital approval.")
        return redirect("appointments:history")
    return render(
        request,
        "appointments/reschedule.html",
        {"appointment": appt, "slots": slots, "on_date": on_date},
    )
