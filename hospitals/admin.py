from django.contrib import admin

from .models import Department, Doctor, DoctorSchedule, Hospital, HospitalResources


class DepartmentInline(admin.TabularInline):
    model = Department
    extra = 0


class HospitalResourcesInline(admin.StackedInline):
    model = HospitalResources
    can_delete = False


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "emergency_available", "rating")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "city")
    inlines = [DepartmentInline, HospitalResourcesInline]


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "hospital")
    list_filter = ("hospital",)


class DoctorScheduleInline(admin.TabularInline):
    model = DoctorSchedule
    extra = 0


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("display_name", "hospital", "department", "specialization")
    list_filter = ("hospital", "department")
    search_fields = ("first_name", "last_name", "specialization")
    inlines = [DoctorScheduleInline]


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ("doctor", "weekday", "start_time", "end_time")


@admin.register(HospitalResources)
class HospitalResourcesAdmin(admin.ModelAdmin):
    list_display = (
        "hospital",
        "icu_beds_available",
        "general_beds_available",
        "ventilators_available",
        "ambulances_available",
        "updated_at",
    )
