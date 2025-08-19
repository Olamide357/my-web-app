from django.db import models
from django.contrib.auth.models import User
import secrets, uuid
# Create your models here.

class WalletFunding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Funding: {self.amount} for {self.user.username} - {self.status}"



class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    account_name = models.CharField(max_length=200, blank=True, null=True)
    monnify_customer_code = models.CharField(max_length=100, blank=True, null=True)
    customer_code = models.CharField(max_length=50, blank=True, null=True)
    wallet_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"{self.user.username} Wallet"

