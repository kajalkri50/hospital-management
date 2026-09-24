"""Patient appointments with approval workflow for hospital admins."""

from django.conf import settings
from django.db import models
from django.core.mail import send_mail
from decouple import config


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "Pending payment"
        PENDING_APPROVAL = "pending_approval", "Pending approval"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"
        REJECTED = "rejected", "Rejected"

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    doctor = models.ForeignKey(
        "hospitals.Doctor",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    hospital = models.ForeignKey(
        "hospitals.Hospital",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    department = models.ForeignKey(
        "hospitals.Department",
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    scheduled_at = models.DateTimeField(db_index=True)
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-scheduled_at"]

    def __str__(self) -> str:
        return f"Appointment {self.pk} — {self.patient} @ {self.scheduled_at}"
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        send_mail(
            subject=f"Appointment {self.get_status_display()}",
            message=f"Your appointment with Dr. {self.doctor.first_name} {self.doctor.last_name} at {self.hospital.name} on {self.scheduled_at} is now {self.get_status_display()}.",
            from_email=f"Smart Hospital Finder <{config('EMAIL_HOST_USER')}>",
            recipient_list=[self.patient.email, self.hospital.admin_user.email],
            fail_silently=True,
        )

    
