from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from decimal import Decimal
import random, string


# Helper function for referral codes
def generate_referral_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


# =========================
# Custom User Manager
# =========================
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, phone, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        if not email:
            raise ValueError("Email is required")
        if not phone:
            raise ValueError("Phone number is required")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, email, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(username, email, phone, password, **extra_fields)


# =========================
# Custom User Model
# =========================
class UserProfile(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)

    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    referral_code = models.CharField(max_length=12, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True, related_name="referrals"
    )

    currency = models.CharField(max_length=5, default='NGN')
    virtual_account_number = models.CharField(max_length=100, blank=True, null=True)
    virtual_account_name = models.CharField(max_length=100, blank=True, null=True)
    virtual_account_bank = models.CharField(max_length=100, blank=True, null=True)
    virtual_account_status = models.CharField(
        max_length=100,
        choices=[
            ('pending', 'Pending'),
            ('assigning', 'Assigning'),
            ('active', 'Active'),
            ('failed', 'Failed')
        ],
        default='pending'
    )

    paystack_customer_code = models.CharField(max_length=100, blank=True, null=True)

    # Django permission fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True, blank=True, null=True) #default='2025-08-26 05:11:00'

    objects = CustomUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "phone"]

    def __str__(self):
        return f"{self.username} - {self.email}"

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = generate_referral_code()
        super().save(*args, **kwargs)

    def credit(self, amount):
        self.wallet_balance += Decimal(amount)
        self.save()
