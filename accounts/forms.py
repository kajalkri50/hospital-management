from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import PatientProfile, User


class PatientRegistrationForm(UserCreationForm):
    """Public self-registration defaults to Patient role."""

    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=32, required=False)

    class Meta:
        model = User
        fields = ("username", "email", "phone", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data.get("phone") or ""
        user.role = User.Role.PATIENT
        if commit:
            user.save()
            PatientProfile.objects.get_or_create(user=user)
        return user


class ProfileForm(forms.ModelForm):
    # Include user fields
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=32, required=False)

    class Meta:
        model = PatientProfile
        fields = ("address", "city", "latitude", "longitude", "emergency_contact")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            self.fields['phone'].initial = self.instance.user.phone

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        user.phone = self.cleaned_data.get('phone', '')
        if commit:
            user.save()
            profile.save()
        return profile
