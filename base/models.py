from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Beneficiary(models.Model):
    SERVICE_CHOICES = [
        ('airtime', 'Airtime'),
        ('data', 'Data'),
        ('tv', 'TV'),
        ('electricity', 'Electricity')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    provider = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vtu_transaction")
    service = models.CharField(max_length=20) #airtime, data, 
    provider = models.CharField(max_length=20) #Glo, MTN, etc
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone = models.CharField(max_length=15)
    smartcard_number = models.CharField(max_length=30, blank=True, null=True)
    meter_number = models.CharField(max_length=30, blank=True, null=True)
    variation_code = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_id = models.CharField(max_length=100)
    token = models.CharField(max_length=100, null=True, blank=True)

    external_status = models.CharField(max_length=50, blank=True, null=True)
    raw_response = models.JSONField(blank=True, null=True)

    date = models.DateTimeField(auto_now_add=True)
    customer_name = models.CharField(max_length=100, null=True, blank=True)
    reference = models.CharField(max_length=100, unique=True)
    # amount = models.DecimalField(max_digits=10, decimal_places=2)
    # status = models.CharField(max_length=20)
    # created_at = models.DateTimeField(auto_now_add=True)

    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)

    class Meta:
        unique_together = ('request_id',)

    def __str__(self):
        return f"{self.user.username} | {self.service} | {self.amount} | {self.status}"

