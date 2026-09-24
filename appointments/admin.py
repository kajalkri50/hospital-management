from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "hospital", "scheduled_at", "status")
    list_filter = ("status", "hospital")
    search_fields = ("patient__username", "doctor__last_name")
    date_hierarchy = "scheduled_at"
