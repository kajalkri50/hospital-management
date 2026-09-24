from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, View

from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications/list.html"
    context_object_name = "notifications"

    def get_queryset(self):
        return self.request.user.notifications.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["unread_count"] = self.request.user.notifications.filter(read=False).count()
        return ctx


class NotificationMarkAllReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        request.user.notifications.filter(read=False).update(read=True)
        return redirect(reverse_lazy("notifications:list"))

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
