"""Reusable access control for role-based dashboards."""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import User


class PatientRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self) -> bool:
        u = self.request.user
        return u.is_authenticated and (u.role == User.Role.PATIENT or u.is_app_super_admin())


class HospitalAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self) -> bool:
        u = self.request.user
        return u.is_authenticated and (u.is_hospital_admin() or u.is_app_super_admin())
