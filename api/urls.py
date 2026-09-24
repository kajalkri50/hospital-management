from django.urls import path

from . import views

app_name = "api"

urlpatterns = [
    path("csrf/", views.EnsureCsrfCookieView.as_view(), name="csrf"),
    path("register/", views.RegisterAPIView.as_view(), name="register"),
    path("login/", views.LoginAPIView.as_view(), name="login"),
    path("hospitals/nearby/", views.HospitalsNearbyAPIView.as_view(), name="hospitals_nearby"),
    path("hospitals/<int:pk>/", views.HospitalDetailAPIView.as_view(), name="hospital_detail"),
    path("hospitals/<int:hospital_id>/resources/", views.HospitalResourcesPollAPIView.as_view(), name="hospital_resources"),
    path("doctors/<int:hospital_id>/", views.DoctorsByHospitalAPIView.as_view(), name="doctors_by_hospital"),
    path("emergency/nearest/", views.EmergencyNearestAPIView.as_view(), name="emergency_nearest"),
    path("appointments/book/", views.AppointmentBookAPIView.as_view(), name="appointments_book"),
    path("appointments/user/", views.UserAppointmentsAPIView.as_view(), name="appointments_user"),
    path("payment/", views.PaymentCreateAPIView.as_view(), name="payment"),
]
