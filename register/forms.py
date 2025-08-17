from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from django.contrib.auth import authenticate

class SignupForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    referral_code = forms.CharField(max_length=20, required=False)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if UserProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Phone number already exists.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data





class LoginForm(forms.Form):
    identifier = forms.CharField(
        label="Email or Phone Number",
        max_length=150,
        required=True
    )
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get("identifier")
        password = cleaned_data.get("password")

        if identifier and password:
            try:
                # Try email first
                profile = UserProfile.objects.filter(user__email=identifier).first()

                # If not email, try phone
                if not profile:
                    profile = UserProfile.objects.filter(phone=identifier).first()

                if not profile:
                    raise forms.ValidationError("Invalid email/phone or password.")

                user = authenticate(username=profile.user.username, password=password)
                if not user:
                    raise forms.ValidationError("Invalid email/phone or password.")

            except UserProfile.DoesNotExist:
                raise forms.ValidationError("Invalid email/phone or password.")

        return cleaned_data