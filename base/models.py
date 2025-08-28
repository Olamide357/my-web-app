from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

class Beneficiary(models.Model):
    SERVICE_CHOICES = [
        ('airtime', 'Airtime'),
        ('data', 'Data'),
        ('tv', 'TV'),
        ('electricity', 'Electricity')
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    provider = models.CharField(max_length=100)
    account_number = models.CharField(max_length=20)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.provider}"



class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("airtime", "Airtime Purchase"),
        ("data", "Data Purcase"),
        ("wallet_fund", "Wallet Funding"),
        ("quick_transfer", "Quick Transfer"),
        ("electricity", "Electricity"),
        ("tv", "TV Subscription"),
    ]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    METER_TYPE_CHOICES = [
        ("prepaid", "Prepaid"),
        ("postpaid", "Postpaid"),
    ]

    PROVIDER_CHOICES = [
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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="vtu_transaction")

    service = models.CharField(max_length=20) #airtime, data, 

    provider = models.CharField(max_length=20, blank=True, null=True) #Glo, MTN, etc

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    phone = models.CharField(max_length=15, null=True, blank=True)

    smartcard_number = models.CharField(max_length=30, blank=True, null=True)

    cashback = models.DecimalField(max_digits=10, decimal_places=2)

    meter_number = models.CharField(max_length=30, blank=True, null=True)

    meter_type = models.CharField(max_length=10, choices=METER_TYPE_CHOICES)

    variation_code = models.CharField(max_length=50, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    token = models.CharField(max_length=100, null=True, blank=True)

    # name = models.CharField(max_length=100)
    external_status = models.CharField(max_length=50, blank=True, null=True)

    raw_response = models.JSONField(blank=True, null=True)

    initial_amount = models.DecimalField(max_digits=10, decimal_places=2)

    final_amount = models.DecimalField(max_digits=10, decimal_places=2)

    date = models.DateTimeField(auto_now_add=True)

    customer_name = models.CharField(max_length=100, null=True, blank=True)

    reference = models.CharField(max_length=100, unique=True)

    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    
    
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Original amount
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Fee deducted
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    # meter_type = models.CharField(max_length=20, default="prepaid")
    bank_name = models.CharField(max_length=50, blank=True, null=True)

    method = models.CharField(max_length=20, choices=(
        ("dva", "DVA"),
        ("inline", "Inline"),
    ), default="dva")
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    

    def __str__(self):
        return f"{self.user.username} | {self.service} | {self.amount} | {self.status}"





