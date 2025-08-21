from django.db import models
from django.contrib.auth.models import User
# Create your models here.

from django.db import models

class DataPlan(models.Model):
    NETWORK_CHOICES = [ ("MTN", "MTN"), ("GLO", "GLO"), ("AIRTEL", "AIRTEL"), ("9MOBILE", "9mobile"), ]

    network = models.CharField(max_length=20, choices=NETWORK_CHOICES) 
    plan_name = models.CharField(max_length=100) # e.g. "1GB Daily Plan"
    volume = models.CharField(max_length=50) # e.g. "1GB" 
    validity = models.CharField(max_length=50, blank=True, null=True) # e.g. "1 Day" 
    amount = models.DecimalField(max_digits=10, decimal_places=2) # e.g. 300.00 
    plan_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
 # code for API vendor 
     
    def __str__(self): 
        return f"{self.network} - {self.plan_name} ({self.amount})"


class TVPlan(models.Model):
    PROVIDER_CHOICES = [
        ("DSTV", "DSTV"),
        ("GOTV", "GOTV"),
        ("STARTIMES", "Startimes"),
    ]

    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    plan_name = models.CharField(max_length=100)  # e.g. DSTV Padi
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    # volume = models.CharField(max_length=50) # e.g. "1GB" 
    validity = models.CharField(max_length=50, blank=True, null=True) # e.g. "1 Day"
    plan_code = models.CharField(max_length=50)  # variation_code from VTpass

    def __str__(self):
        return f"{self.provider} - {self.plan_name} ({self.amount})"


#================ ELECTRICITY MODELS =====================@

class ElectricityPlan(models.Model):
    disco = models.CharField(max_length=50)  # e.g. IKEDC, AEDC, EEDC
    plan_type = models.CharField(max_length=20, choices=[("prepaid", "Prepaid"), ("postpaid", "Postpaid")])
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.disco.upper()} - {self.plan_type.capitalize()}"
