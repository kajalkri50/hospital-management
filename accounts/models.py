"""
Custom user model with role-based access (patient, doctor, hospital admin, super admin).
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Application user; `is_superuser` aligns with Django admin for platform super admins."""

    class Role(models.TextChoices):
        PATIENT = "patient", "Patient"
        DOCTOR = "doctor", "Doctor"
        HOSPITAL_ADMIN = "hospital_admin", "Hospital Admin"
        SUPER_ADMIN = "super_admin", "Super Admin"

    role = models.CharField(
        max_length=32,
        choices=Role.choices,
        default=Role.PATIENT,
        db_index=True,
    )
    phone = models.CharField(max_length=32, blank=True)
    email = models.EmailField(unique=True,)


    def is_patient(self) -> bool:
        return self.role == self.Role.PATIENT

    def is_doctor_role(self) -> bool:
        return self.role == self.Role.DOCTOR

    def is_hospital_admin(self) -> bool:
        return self.role == self.Role.HOSPITAL_ADMIN

    def is_app_super_admin(self) -> bool:
        return self.role == self.Role.SUPER_ADMIN or self.is_superuser


class PatientProfile(models.Model):
    """Extended profile for patients (location for nearby search, emergency contact)."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="patient_profile",
    )
    address = models.CharField(max_length=512, blank=True)
    city = models.CharField(max_length=128, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    emergency_contact = models.CharField(max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"PatientProfile({self.user.username})"
