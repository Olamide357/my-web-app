from django import forms
from .models import Beneficiary
from django.contrib.auth.models import User
from register.models import UserProfile

class BeneficiaryForm(forms.ModelForm):
    class Meta:
        model = Beneficiary
        fields = ['name', 'service_type', 'provider', 'account_number']

        widget = {
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'provider': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. MTN, DSTV, IKEDC PREPAID'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Beneficiary Name'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number, Meter, or IUC'})
        }

class editProfileForm(forms.ModelForm):
    phone = forms.CharField(max_length=15, required=False)
    class Meta:
        model = User
        fields = ['username', 'email']

class changePasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
