from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("payments/start/<int:pk>/", views.start_checkout, name="start_checkout"),
    path("payments/stripe/success/", views.stripe_success, name="stripe_success"),
    path("payments/stripe/cancel/", views.stripe_cancel, name="stripe_cancel"),
    path("payments/stripe/webhook/", views.StripeWebhookView.as_view(), name="stripe_webhook"),
    path("payments/demo/<int:pk>/", views.demo_complete_payment, name="demo_pay"),
]
