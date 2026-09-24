"""
Hospitals, departments, doctors, schedules, and bed/resource inventory.
"""

from django.conf import settings
from django.db import models


class Hospital(models.Model):
    """Healthcare facility with geo coordinates for distance and map display."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    address = models.CharField(max_length=512)
    city = models.CharField(max_length=128, blank=True)
    state = models.CharField(max_length=128, blank=True)
    postal_code = models.CharField(max_length=32, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    phone = models.CharField(max_length=64, blank=True)
    email = models.EmailField(unique=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.0)
    emergency_available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    cover_image = models.URLField(
        max_length=512,
        blank=True,
        help_text="Exterior or campus photo URL (HTTPS) for cards and landing page.",
    )
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="administered_hospitals",
        limit_choices_to={"role": "hospital_admin"},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    @property
    def safe_resources(self):
        """Safe when no `HospitalResources` row exists (avoids RelatedObjectDoesNotExist in templates)."""
        return HospitalResources.objects.filter(hospital=self).first()


class Department(models.Model):
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="departments")
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["hospital", "name"]
        unique_together = [["hospital", "name"]]

    def __str__(self) -> str:
        return f"{self.hospital.name} — {self.name}"


class Doctor(models.Model):
    """Doctor may optionally link to a User for portal login."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="doctor_profile",
    )
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name="doctors")
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="doctors")
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    specialization = models.CharField(max_length=255)
    experience_years = models.PositiveSmallIntegerField(default=0)
    bio = models.TextField(blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.5)

    class Meta:
        ordering = ["hospital", "last_name", "first_name"]

    def __str__(self) -> str:
        return f"Dr. {self.first_name} {self.last_name}"

    @property
    def display_name(self) -> str:
        return f"Dr. {self.first_name} {self.last_name}"


class DoctorSchedule(models.Model):
    """Weekly recurring availability; used to propose booking slots."""

    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="schedules")
    weekday = models.IntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_minutes = models.PositiveSmallIntegerField(default=30)

    class Meta:
        ordering = ["doctor", "weekday", "start_time"]

    def __str__(self) -> str:
        return f"{self.doctor} — {self.get_weekday_display()}"


class HospitalResources(models.Model):
    """ICU/general beds, ventilators, ambulances — polled by patients for “real-time” UI."""

    hospital = models.OneToOneField(Hospital, on_delete=models.CASCADE, related_name="resources")
    icu_beds_total = models.PositiveIntegerField(default=0)
    icu_beds_available = models.PositiveIntegerField(default=0)
    general_beds_total = models.PositiveIntegerField(default=0)
    general_beds_available = models.PositiveIntegerField(default=0)
    ventilators_available = models.PositiveIntegerField(default=0)
    ambulances_available = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Resources({self.hospital.name})"
