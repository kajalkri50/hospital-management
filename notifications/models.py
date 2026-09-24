"""In-app and email-backed notification log."""

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from decouple import config


class Notification(models.Model):
    class Kind(models.TextChoices):
        APPOINTMENT_CONFIRMED = "appointment_confirmed", "Appointment confirmed"
        APPOINTMENT_REMINDER = "appointment_reminder", "Appointment reminder"
        APPOINTMENT_CANCELLED = "appointment_cancelled", "Appointment cancelled"
        EMERGENCY_ALERT = "emergency_alert", "Emergency alert"
        PAYMENT = "payment", "Payment"
        GENERIC = "generic", "Generic"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    kind = models.CharField(max_length=64, choices=Kind.choices, default=Kind.GENERIC)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    read = models.BooleanField(default=False)
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} → {self.user}"
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Send email for certain notification kinds
        if self.kind in [self.Kind.APPOINTMENT_CONFIRMED, self.Kind.APPOINTMENT_REMINDER, self.Kind.APPOINTMENT_CANCELLED, self.Kind.EMERGENCY_ALERT]:
            send_mail(
                subject=self.title,
                message=self.body,
                from_email=f"Smart Hospital Finder <{config('EMAIL_HOST_USER')}>",
                recipient_list=[self.user.email],
                fail_silently=True,
            )


