"""Stripe (or future Razorpay) payment records tied to appointments."""

from django.db import models


class Payment(models.Model):
    class Provider(models.TextChoices):
        STRIPE = "stripe", "Stripe"
        RAZORPAY = "razorpay", "Razorpay"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    appointment = models.OneToOneField(
        "appointments.Appointment",
        on_delete=models.CASCADE,
        related_name="payment",
    )
    amount_cents = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=8, default="usd")
    provider = models.CharField(
        max_length=32,
        choices=Provider.choices,
        default=Provider.STRIPE,
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
        default=Status.PENDING,
    )
    stripe_session_id = models.CharField(max_length=255, blank=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True)
    transaction_ref = models.CharField(max_length=255, blank=True)
    raw_metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Payment {self.pk} — {self.status}"
