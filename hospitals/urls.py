from django.urls import path

from . import views

app_name = "hospitals"

urlpatterns = [
    path("", views.home, name="home"),
    path("hospitals/search/", views.hospital_search, name="search"),
    path("hospitals/<slug:slug>/", views.hospital_detail, name="detail"),
    path("hospitals/<slug:slug>/doctors/", views.doctor_list, name="doctor_list"),
    path("doctors/<int:pk>/", views.doctor_detail, name="doctor_detail"),
    path("emergency/", views.emergency_page, name="emergency"),
    path("emergency/results/", views.emergency_results, name="emergency_results"),
    path("dashboard/patient/", views.patient_dashboard, name="patient_dashboard"),
    path("hospital-admin/", views.HospitalAdminDashboardView.as_view(), name="hospital_admin_dashboard"),
    path("hospital-admin/doctors/", views.hospital_admin_doctors, name="hospital_admin_doctors"),
    path("hospital-admin/resources/", views.hospital_admin_resources, name="hospital_admin_resources"),
    path("hospital-admin/appointments/", views.hospital_admin_appointments, name="hospital_admin_appointments"),
    path("doctor-portal/", views.doctor_portal, name="doctor_portal"),
]
