"""
URL configuration — web UI, REST API (`/api/`), Stripe webhook, chatbot endpoint.
"""

from django.contrib import admin
from django.urls import include, path

from accounts import views as account_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", account_views.dashboard_router, name="dashboard"),
    path("accounts/", include("accounts.urls")),
    path("api/", include("api.urls")),
    path("", include("appointments.urls")),
    path("", include("payments.urls")),
    path("", include("notifications.urls")),
    path("", include("chatbot.urls")),
    path("", include("hospitals.urls")),
]
