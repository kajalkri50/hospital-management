"""
Create in-app notifications and send email when SMTP is configured.
"""

from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail

from .models import Notification


def notify_user(
    *,
    user,
    kind: str,
    title: str,
    body: str = "",
    appointment=None,
    send_email: bool = True,
) -> Notification:
    n = Notification.objects.create(
        user=user,
        kind=kind,
        title=title,
        body=body,
        appointment=appointment,
    )
    if send_email and user.email:
        try:
            send_mail(
                subject=title,
                message=body or title,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            pass
    return n
