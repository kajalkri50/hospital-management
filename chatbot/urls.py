from django.urls import path

from . import views

app_name = "chatbot"

urlpatterns = [
    path("chatbot/message/", views.ChatbotMessageView.as_view(), name="message"),
]
