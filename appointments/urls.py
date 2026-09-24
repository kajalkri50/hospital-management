from django.urls import path

from . import views

app_name = "appointments"

urlpatterns = [
    path("hospitals/<slug:slug>/book/", views.book_appointment, name="book"),
    path("appointments/history/", views.appointment_history, name="history"),
    path("appointments/<int:pk>/cancel/", views.cancel_appointment, name="cancel"),
    path("appointments/<int:pk>/reschedule/", views.reschedule_appointment, name="reschedule"),
]
