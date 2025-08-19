from django.db import models
from django.contrib.auth.models import User
import uuid
import secrets
# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, unique=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    referral_code = models.CharField(max_length=12, blank=True, null=True)

    currency = models.CharField(max_length=3, default='NGN')
    account_number = models.CharField(max_length=20, blank=True, null=True)
    account_name = models.CharField(max_length=20, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    account_status = models.CharField(max_length=20,choices=[('pending', 'Pending'), ('assigning', 'Assigning'), ('active', 'Active'), ('failed', 'Failed')], default='pending')

    paystack_customer_code = models.CharField(max_length=100, blank=True, null=True)
    # created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile - Balance: {self.wallet_balance} {self.currency}"
'''
class FundingTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Funding: {self.amount} for {self.user.username} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.reference:
            while True:
                ref = secrets.token_hex(16)
                if not FundingTransaction.objects.filter(reference=ref).exists():
                    self.reference = ref
                    break
        super().save(*args, **Kwargs)
        '''