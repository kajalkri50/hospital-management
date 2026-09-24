from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .forms import PatientRegistrationForm, ProfileForm
from .models import PatientProfile, User
import random
from django.core.mail import send_mail
from decouple import config

def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        if 'otp' in request.POST:
            otp = request.session.get('otp')
            user_otp = request.POST.get('otp')
            if otp and str(otp) == str(user_otp):
                # OTP is correct, create the user
                form_data = request.session.get('form_data')
                form = PatientRegistrationForm(form_data)
                if form.is_valid():
                    user = form.save()
                    login(request, user)
                    messages.success(request, "Account created. Welcome!")
                    return redirect("dashboard")
                else:
                    messages.error(request, "Form data is invalid. Please try again.")
                    return redirect("accounts:register")
            else:
                messages.error(request, "Invalid OTP. Please try again.")
                return redirect("accounts:register")
        else:    
            form = PatientRegistrationForm(request.POST)
            if form.is_valid():

                # Generate OTP and send email
                otp = random.randint(100000, 999999)
                request.session['otp'] = otp
                request.session['form_data'] = request.POST
                email = form.cleaned_data.get('email')
                send_mail(
                    subject='Your OTP for Smart Hospital Finder Signup',
                    message=f'Your OTP is: {otp}',
                    from_email=f"Smart Hospital Finder <{config('EMAIL_HOST_USER')}>",
                    recipient_list=[form.cleaned_data['email']],
                    fail_silently=False,
                )
                return render(request, "accounts/register.html", {"form": form, "otp_sent": True})
    else:
        form = PatientRegistrationForm()
    return render(request, "accounts/register.html", {"form": form, "otp_sent": False})


class AppLoginView(LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class AppLogoutView(LogoutView):
    next_page = reverse_lazy("hospitals:home")


def dashboard_router(request):
    """Send users to the right dashboard by role."""
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    u: User = request.user
    if u.is_app_super_admin() or u.is_hospital_admin():
        return redirect("hospitals:hospital_admin_dashboard")
    if u.is_doctor_role():
        return redirect("hospitals:doctor_portal")
    return redirect("hospitals:patient_dashboard")


class ProfileUpdateView(UpdateView):
    model = PatientProfile
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        profile, _ = PatientProfile.objects.get_or_create(user=self.request.user)
        return profile

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Profile updated.")
        return super().form_valid(form)
