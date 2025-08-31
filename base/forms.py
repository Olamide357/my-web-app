from django import forms
from .models import Beneficiary
from django.contrib.auth.models import User
from register.models import UserProfile


PROVIDER_CHOICES = [
         ("MTN", "MTN"),
    ("GLO", "GLO"),
    ("AIRTEL", "Airtel"),
    ("9MOBILE", "9Mobile"),
    ("DSTV", "DSTV"),
    ("GOTV", "GOTV"),
    ("STARTIMES", "Startimes"),
        ("IKEDC", "IKEDC"),
        ("AEDC", "AEDC"),
        ("EEDC", "EEDC"),
        ("KEDCO", "KEDCO"),
        ("IBEDC", "IBEDC"),
        ("PHED", "PHED"),
        ("JEDC", "JEDC"),
        ("KAEDCO", "KAEDCO"),
        ("BEDC", "BEDC"),
        ("EKEDC", "EKEDC"),
    ]
class BeneficiaryForm(forms.ModelForm):

    # provider = forms.ChoiceField(
    #     choices=PROVIDER_CHOICES,
    #     widget=forms.Select(attrs={"class": "form-control"})
    # )

    class Meta:
        model = Beneficiary
        fields = ['name', 'service_type', 'provider', 'account_number']

        widget = {
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'provider': forms.Select(attrs={'class': 'form-control', 'placeholder': 'e.g. MTN, DSTV, IKEDC'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Beneficiary Name'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number, Meter, or IUC'})
        }

class editProfileForm(forms.ModelForm):
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'email','phone']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)  # pass current user
        super().__init__(*args, **kwargs)

        # Make username read-only
        self.fields["username"].disabled = True
        self.fields["username"].widget.attrs["readonly"] = True

        # Add nice placeholders & bootstrap classes
        self.fields["email"].widget.attrs.update({"class": "form-control", "placeholder": "Email"})
        self.fields["phone"].widget.attrs.update({"class": "form-control", "placeholder": "Phone number"})

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if UserProfile.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if UserProfile.objects.exclude(pk=self.instance.pk).filter(phone=phone).exists():
            raise forms.ValidationError("This phone number is already in use.")
        return phone

import re
from django import forms

class changePasswordForm(forms.Form):
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter new password"})
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm new password"})
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if password:
            if len(password) < 6:
                self.add_error("new_password", "Password must be at least 6 characters long.")
            if not re.search(r"[A-Z]", password):
                self.add_error("new_password", "Password must contain at least one uppercase letter.")
            if not re.search(r"\d", password):
                self.add_error("new_password", "Password must contain at least one number.")
            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
                self.add_error("new_password", "Password must contain at least one special character.")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")

        return cleaned_data
