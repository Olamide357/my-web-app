from django import forms
from django.conf import settings


#===================== AIRTIME FORM ==================#

class AirtimeForm(forms.Form):
    phone_number = forms.CharField(max_length=15, label="Phone Number")
    amount = forms.DecimalField(min_value=50, max_digits=10, decimal_places=2, label="Amount")
    password = forms.CharField(widget=forms.PasswordInput, label="Wallet Password")

    def clean_phone_number(self):
        phone = self.cleaned_data['phone_number'].strip()
        # Remove spaces or dashes if any
        phone = phone.replace(" ", "").replace("-", "")
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must be numeric.")
        return phone

    def clean_amount(self):
        amt = self.cleaned_data['amount']
        if amt < 50:
            raise forms.ValidationError("Minimum airtime purchase is 50 NGN.")
        return amt

#======================================================#

# forms.py
from django import forms
from .models import DataPlan

class DataPurchaseForm(forms.Form):
    phone_number = forms.CharField(
        label="Phone Number",
        max_length=11,
        widget=forms.TextInput(attrs={"placeholder": "Enter Phone Number", "id": "id_phone_number"})
    )
    plan = forms.ModelChoiceField(
        queryset=DataPlan.objects.none(),  # we’ll set queryset dynamically
        label="Data Plan"
    )
    password = forms.CharField(
        label="Wallet Password",
        widget=forms.PasswordInput(attrs={"id": "id_password", "placeholder": "Enter Wallet Password"})
    )

    def __init__(self, *args, **kwargs):
        network = kwargs.pop("network", None)
        super().__init__(*args, **kwargs)
        if network:
            # Only show MTN plans
            self.fields["plan"].queryset = DataPlan.objects.filter(network=network)


#======================= TV FORMS =============================@
from .models import TVPlan

class TVPurchaseForm(forms.Form):
    smartcard_number = forms.CharField(
        label="Smart Card / IUC Number",
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "Enter Smart Card Number", "id": "id_smartcard"})
    )
    plan = forms.ModelChoiceField(
        queryset=TVPlan.objects.none(),
        label="TV Package"
    )
    password = forms.CharField(
        label="Wallet Password",
        widget=forms.PasswordInput(attrs={"id": "id_password", "placeholder": "Enter Wallet Password"})
    )

    def __init__(self, *args, **kwargs):
        provider = kwargs.pop("provider", None)
        super().__init__(*args, **kwargs)
        if provider:
            self.fields["plan"].queryset = TVPlan.objects.filter(provider=provider)

#==============================================================#

#================= ELECTRICITY ================================#
from django import forms
from django.core.validators import MinValueValidator

METER_TYPE_CHOICES = [
    ("prepaid", "Prepaid"),
    ("postpaid", "Postpaid"),
]

class ElectricityForm(forms.Form):
    meter_type = forms.ChoiceField(
        choices=METER_TYPE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select form-select-lg"})
    )
    meter_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "Enter meter number"
        })
    )
    amount = forms.DecimalField(
        decimal_places=2,
        min_value=100,
        validators=[MinValueValidator(100)],
        widget=forms.NumberInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "Enter amount"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "Enter wallet password"
        })
    )





























#========= IKEDC PREPAID FORM ================#
class prepaidForm(forms.Form):
    meter_number = forms.CharField(max_length=15, label='Meter Number')
    amount = forms.DecimalField(label='Amount(₦)', max_digits=10, decimal_places=2)
    password = forms.CharField(widget=forms.PasswordInput, label="Account Password")

#========= IKEDC POSTPAID FORM ================#
class postpaidForm(forms.Form):
    meter_number = forms.CharField(max_length=15, label='Meter Number')
    variation_code = forms.CharField(max_length=50)
    amount = forms.DecimalField(label='Amount(₦)', max_digits=10, decimal_places=2)
    password = forms.CharField(widget=forms.PasswordInput, label="Account Password")
