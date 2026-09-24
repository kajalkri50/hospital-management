"""
Stripe Checkout session creation; demo fallback when keys missing in DEBUG.
"""

from __future__ import annotations

from django.conf import settings
from django.urls import reverse

from appointments.models import Appointment
from payments.models import Payment


def ensure_payment_and_checkout(request, appointment: Appointment) -> str | None:
    """
    Create Payment row and return Stripe Checkout URL, or None to skip redirect
    (demo mode / missing Stripe configuration).
    """
    payment, _ = Payment.objects.get_or_create(
        appointment=appointment,
        defaults={
            "amount_cents": 2500,
            "currency": "usd",
            "provider": Payment.Provider.STRIPE,
            "status": Payment.Status.PENDING,
        },
    )
    secret = getattr(settings, "STRIPE_SECRET_KEY", "") or ""
    if not secret:
        if settings.DEBUG:
            return None
        raise RuntimeError("STRIPE_SECRET_KEY is required when DEBUG=False")

    import stripe

    stripe.api_key = secret
    success_url = request.build_absolute_uri(
        reverse("payments:stripe_success") + f"?session_id={{CHECKOUT_SESSION_ID}}"
    )
    cancel_url = request.build_absolute_uri(reverse("payments:stripe_cancel"))
    session = stripe.checkout.Session.create(
        mode="payment",
        customer_email=request.user.email or None,
        success_url=success_url,
        cancel_url=cancel_url,
        line_items=[
            {
                "price_data": {
                    "currency": payment.currency,
                    "unit_amount": payment.amount_cents,
                    "product_data": {
                        "name": f"Appointment — {appointment.hospital.name}",
                        "description": f"Dr. {appointment.doctor.last_name} / {appointment.department.name}",
                    },
                },
                "quantity": 1,
            }
        ],
        metadata={"appointment_id": str(appointment.pk)},
    )
    payment.stripe_session_id = session.id
    payment.save()
    return session.url
