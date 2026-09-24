"""
Stripe return URLs and webhook endpoint.
"""

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from appointments.models import Appointment
from notifications.services import notify_user

from .models import Payment
from .services import ensure_payment_and_checkout


def stripe_success(request):
    session_id = request.GET.get("session_id")
    if not session_id:
        messages.error(request, "Missing payment session.")
        return redirect("appointments:history")
    if not getattr(settings, "STRIPE_SECRET_KEY", ""):
        messages.error(request, "Stripe is not configured.")
        return redirect("appointments:history")
    import stripe

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception:
        messages.error(request, "Could not verify payment.")
        return redirect("appointments:history")
    appt_id = (session.metadata or {}).get("appointment_id")
    if not appt_id:
        messages.error(request, "Invalid session metadata.")
        return redirect("appointments:history")
    appt = Appointment.objects.filter(pk=int(appt_id), patient=request.user).first()
    if not appt:
        messages.error(request, "Appointment not found.")
        return redirect("appointments:history")
    pay = getattr(appt, "payment", None)
    if pay:
        pay.status = Payment.Status.SUCCEEDED
        pay.stripe_payment_intent = session.payment_intent or ""
        pay.transaction_ref = session_id
        pay.save()
    if appt.status == Appointment.Status.PENDING_PAYMENT:
        appt.status = Appointment.Status.PENDING_APPROVAL
        appt.save()
    notify_user(
        user=request.user,
        kind="payment",
        title="Payment received",
        body="Your payment was successful. The hospital will confirm your appointment shortly.",
        appointment=appt,
    )
    messages.success(request, "Payment successful. Booking is pending hospital approval.")
    return redirect("appointments:history")


def stripe_cancel(request):
    messages.warning(request, "Payment cancelled. You can retry from appointment history.")
    return redirect("appointments:history")


@login_required
def start_checkout(request, pk):
    """Create or reuse Stripe Checkout session for a pending appointment."""
    appt = get_object_or_404(
        Appointment,
        pk=pk,
        patient=request.user,
        status=Appointment.Status.PENDING_PAYMENT,
    )
    url = ensure_payment_and_checkout(request, appt)
    if url:
        return redirect(url)
    messages.info(
        request,
        "Stripe is not configured. Use Demo pay (DEBUG) or set STRIPE_SECRET_KEY.",
    )
    return redirect("appointments:history")


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """Verify Stripe signature and mark payments succeeded (production path)."""

    def post(self, request, *args, **kwargs):
        payload = request.body
        sig = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", "") or ""
        if not secret:
            return HttpResponseBadRequest("Webhook not configured")
        import stripe

        try:
            event = stripe.Webhook.construct_event(payload=payload, sig_header=sig, secret=secret)
        except ValueError:
            return HttpResponseBadRequest("Invalid payload")
        except Exception:
            return HttpResponseBadRequest("Invalid signature")

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            appt_id = (session.get("metadata") or {}).get("appointment_id")
            if appt_id:
                appt = Appointment.objects.filter(pk=int(appt_id)).first()
                pay = Payment.objects.filter(appointment=appt).first() if appt else None
                if pay:
                    pay.status = Payment.Status.SUCCEEDED
                    pay.stripe_payment_intent = session.get("payment_intent") or ""
                    pay.save()
                if appt and appt.status == Appointment.Status.PENDING_PAYMENT:
                    appt.status = Appointment.Status.PENDING_APPROVAL
                    appt.save()
        return HttpResponse(status=200)


@login_required
def demo_complete_payment(request, pk):
    """DEV ONLY: mark appointment paid without Stripe (hackathon demos)."""
    if not settings.DEBUG:
        from django.http import Http404

        raise Http404()

    appt = get_object_or_404(Appointment, pk=pk, patient=request.user)
    if appt.status != Appointment.Status.PENDING_PAYMENT:
        messages.warning(request, "Nothing to pay for this appointment.")
        return redirect("appointments:history")
    pay, _ = Payment.objects.get_or_create(
        appointment=appt,
        defaults={
            "amount_cents": 2500,
            "currency": "usd",
            "provider": Payment.Provider.STRIPE,
            "status": Payment.Status.PENDING,
        },
    )
    pay.status = Payment.Status.SUCCEEDED
    pay.transaction_ref = "demo"
    pay.save()
    appt.status = Appointment.Status.PENDING_APPROVAL
    appt.save()
    notify_user(
        user=request.user,
        kind="payment",
        title="Demo payment complete",
        body="Booking is pending hospital approval.",
        appointment=appt,
    )
    messages.success(request, "Demo payment recorded.")
    return redirect("appointments:history")
