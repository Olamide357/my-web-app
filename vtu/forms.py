from django import forms
from django.conf import settings


#===================== AIRTIME FORM ==================#
class AirtimeForm(forms.Form):
    phone = forms.CharField(max_length=11, label='Phone Number')
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    password = forms.CharField(widget=forms.PasswordInput, label='Account Password')
#======================================================#

MTN_DATA_CHOICES = [
        ("500", '500MB SME (30 Days) - ₦250'),
        ("M1024", '1GB SME (30 Days) - ₦600'),
        ('M2024', '2GB SME (30 Days) -  ₦1200'),
        ('3000', '3GB SME 30 Days -  ₦1500'),
        ("5000", "5GB SME (30 Days) - ₦2500"),
        ("10000", "10GB SME (30 Days) - ₦5000")
    ]

GLO_DATA_CHOICES = [
        ("glo-cg_m_200mb", '200MB (30 Days) CG - ₦70'),
        ("glo-cg_m_500mb", '500MB (30 Days) CG - ₦225'),
        ("glo-cg_m_500mb", '1GB (30 Days) CG - ₦450'),
        ("glo-cg_m_500mb", '2GB (30 Days) CG - ₦800'),
        ("glo-cg_m_500mb", '3GB (30 Days) CG - ₦1200'),
        ("glo-cg_m_500mb", '5GB (30 Days) CG - ₦2200'),
        ("glo-cg_m_10gb", '10GB (30 Days) CG - ₦4300'),
    ]


#============= MTN DATA FORM ======================#
class mtnDataForm(forms.Form):
    phone = forms.CharField(max_length=11, label='Phone Number')
    plan = forms.ChoiceField(choices=MTN_DATA_CHOICES, label='Select Plan')
    # variation_code = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput, label='Account Password')
    # network_id = 1

    def get_mtnplan_price(self):
        selected_plan = self.cleaned_data.get("plan")
        for code, label in MTN_DATA_CHOICES:
            if code == selected_plan:
                try:
                    return int(label.split("₦")[-1])
                except:
                    return None
        return None
#======================================================#

#================ GLO DATA FORM =======================#
class gloDataForm(forms.Form):
    phone_number = forms.CharField(max_length=11, label='Phone Number')
    plan = forms.ChoiceField(choices=GLO_DATA_CHOICES, label='Select Plan')
    # variation_code = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput, label='Account Password')
    # network_id = 4

    def get_gloplan_price(self):
        selected_plan = self.cleaned_data.get("plan")
        for code, label in GLO_DATA_CHOICES:
            if code == selected_plan:
                try:
                    return int(label.split("₦")[-1])
                except:
                    return None
        return None
#======================================================#


class airtelDataForm(forms.Form):
    DATA_CHOICES = [
        ('airtel-500mb', '500MB - ₦150'),
        ('airtel-1gb', '1GB - ₦300'),
        ('airtel-2gb', '2GB - ₦500'),
        ('airtel-5gb', '5GB - ₦1000'),
    ]

    phone = forms.CharField(max_length=11, label='Phone Number')
    plan = forms.ChoiceField(choices=DATA_CHOICES, label='Select Plan')
    # variation_code = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput, label='Account Password')

class ninemobileDataForm(forms.Form):
    DATA_CHOICES = [
        ('etisalat-500mb', '500MB - ₦70'),
        ('etisalat-1gb', '1GB - ₦300'),
        ('etisalat-2gb', '2GB - ₦500'),
        ('etisalat-5gb', '5GB - ₦1000'),
    ]

    phone = forms.CharField(max_length=11, label='Phone Number')
    plan = forms.ChoiceField(choices=DATA_CHOICES, label='Select Plan')
    # variation_code = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput, label='Account Password')




#========================= TV FORMS ====================================================#

#====DSTV
class DSTVForm(forms.Form):
    PLAN_CHOICES = [
        ('dstv-padi', 'DSTV Padi - ₦2500'),
        ('dstv-yanga', 'DSTV Yanga - ₦3500'),
        ('dstv-confam', 'DSTV Confam - ₦6200'),
        ('dstv-compact', 'DSTV Compact - ₦10700'),
    ]

    smartcard_number = forms.CharField(max_length=30, label='Smartcard Number')
    plan = forms.ChoiceField(choices=PLAN_CHOICES, label='Select Plan')
    # variation_code = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput, label='Account Password')

#====GOTV
class GOTVForm(forms.Form):
    PLAN_CHOICES = [
        ('gotv-smallie', 'GOTV Smallie - ₦1500'),
        ('gotv-jinja', 'GOTV Jinja - ₦3000'),
        ('gotv-jolli', 'GOTV Jolli - ₦6200'),
        ('gotv-max', 'GOTV Max - ₦10700'),
    ]

    smartcard_number = forms.CharField(max_length=10, label='IUC Number')
    plan = forms.ChoiceField(choices=PLAN_CHOICES, label='Select Plan')
    # variation_code = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput, label='Account Password')

#====STARTIMES
class STARTIMESForm(forms.Form):
    PLAN_CHOICES = [
        ('nova', 'Nova - ₦1200'),
        ('basic', 'Basic - ₦2000'),
        ('classic', 'Classic - ₦4000'),
        ('super', 'Super - ₦6000'),
    ]

    smartcard_number = forms.CharField(max_length=10, label='Smartcard/IUC Number')
    plan = forms.ChoiceField(choices=PLAN_CHOICES, label='Select Plan')
    # variation_code = forms.CharField(max_length=50)
    password = forms.CharField(widget=forms.PasswordInput, label='Account Password')


#=========================== ELECTRICITY ==============================#

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
