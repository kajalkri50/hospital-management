"""DRF serializers for REST endpoints."""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from accounts.models import PatientProfile, User
from appointments.models import Appointment
from hospitals.models import Doctor, Hospital


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("username", "email", "password", "phone")

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        pwd = validated_data.pop("password")
        user = User(**validated_data)
        user.role = User.Role.PATIENT
        user.set_password(pwd)
        user.save()
        PatientProfile.objects.get_or_create(user=user)
        return user


class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = (
            "id",
            "name",
            "slug",
            "address",
            "city",
            "state",
            "postal_code",
            "latitude",
            "longitude",
            "phone",
            "email",
            "rating",
            "emergency_available",
        )


class DoctorSerializer(serializers.ModelSerializer):
    hospital_name = serializers.CharField(source="hospital.name", read_only=True)
    department_name = serializers.CharField(source="department.name", read_only=True)
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = Doctor
        fields = (
            "id",
            "first_name",
            "last_name",
            "display_name",
            "specialization",
            "experience_years",
            "rating",
            "hospital",
            "hospital_name",
            "department",
            "department_name",
        )


class AppointmentBookSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField()
    department_id = serializers.IntegerField()
    scheduled_at = serializers.DateTimeField()
    notes = serializers.CharField(required=False, allow_blank=True, max_length=2000)


class AppointmentReadSerializer(serializers.ModelSerializer):
    hospital_name = serializers.CharField(source="hospital.name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.display_name", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "scheduled_at",
            "status",
            "hospital",
            "hospital_name",
            "doctor",
            "doctor_name",
            "department",
            "notes",
        )


class PaymentCreateSerializer(serializers.Serializer):
    appointment_id = serializers.IntegerField()
