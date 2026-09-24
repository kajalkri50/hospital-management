from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("notifications/", views.NotificationListView.as_view(), name="list"),
    path("notifications/read-all/", views.NotificationMarkAllReadView.as_view(), name="mark_all_read"),
]
