from django.db import models
from django.contrib.auth.models import User
import secrets, uuid
# Create your models here.


class FundingTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gross_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Original amount
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Fee deducted
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Credited amount
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.net_amount} NGN ({self.status})"

