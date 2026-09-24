"""
Appointment slot generation and conflict checks.
"""

from __future__ import annotations

import datetime as dt
from typing import List

from django.utils import timezone

from hospitals.models import Doctor, DoctorSchedule

from .models import Appointment


def _combine_local(date: dt.date, t: dt.time) -> dt.datetime:
    return dt.datetime.combine(date, t, tzinfo=timezone.get_current_timezone())


def get_available_slots(doctor: Doctor, on_date: dt.date, slot_minutes: int = 30) -> List[dt.datetime]:
    """
    Build candidate slots from DoctorSchedule for the date's weekday,
    excluding times already booked for this doctor.
    """
    weekday = on_date.weekday()  # Monday=0 ... Sunday=6 (matches DoctorSchedule.Weekday)
    schedules = DoctorSchedule.objects.filter(doctor=doctor, weekday=weekday)
    booked = set(
        Appointment.objects.filter(
            doctor=doctor,
            scheduled_at__date=on_date,
            status__in=[
                Appointment.Status.PENDING_PAYMENT,
                Appointment.Status.PENDING_APPROVAL,
                Appointment.Status.CONFIRMED,
            ],
        ).values_list("scheduled_at", flat=True)
    )
    slots: List[dt.datetime] = []
    for sch in schedules:
        step = sch.slot_minutes or slot_minutes
        start = dt.datetime.combine(on_date, sch.start_time, tzinfo=timezone.get_current_timezone())
        end = dt.datetime.combine(on_date, sch.end_time, tzinfo=timezone.get_current_timezone())
        cur = start
        while cur + dt.timedelta(minutes=step) <= end:
            if cur not in booked:
                slots.append(cur)
            cur += dt.timedelta(minutes=step)
    slots.sort()
    return slots
