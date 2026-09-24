from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "appointment", "amount_cents", "currency", "provider", "status")
    list_filter = ("status", "provider")
    search_fields = ("stripe_session_id", "transaction_ref")
