from django.shortcuts import render,redirect
import requests, json, logging, base64, uuid, hashlib, hmac,time
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse
from .forms import FundWalletForm
from .models import  WalletFunding
from register.models import UserProfile
from django.urls import reverse
from decimal import Decimal
from base.models import Transaction

# Create your views here.
@login_required
@login_required
def fundWallet(request):
    print("== Fund Wallet View Called ==")  # debug

    if request.method == "POST":
        print("== POST detected ==")
        amount = request.POST.get("amount")
        print("Amount entered:", amount)

        try:
            amount = int(amount) * 100  # convert to kobo
        except:
            messages.error(request, "Invalid amount")
            return redirect("fund_wallet")

        email = request.user.email or "test@example.com"
        reference = str(uuid.uuid4())

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "email": email,
            "amount": amount,
            "reference": reference,
            "callback_url": request.build_absolute_uri(reverse("wallet_callback"))
        }

        url = "https://api.paystack.co/transaction/initialize"
        print("Sending payload:", payload)

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            print("Raw response:", response.text)
            data = response.json()
        except Exception as e:
            print("Paystack request failed:", str(e))
            messages.error(request, f"API Error: {str(e)}")
            return redirect("fund_wallet")

        if data.get("status"):
            print("Redirecting to:", data["data"]["authorization_url"])
            return redirect(data["data"]["authorization_url"])
        else:
            print("Paystack Error:", data)
            messages.error(request, f"Paystack Error: {data.get('message')}")
            return redirect("fund_wallet")

    return render(request, "wallet/fund_wallet.html")


@login_required
@csrf_exempt
def paystack_callback(request):
    reference = request.GET.get("reference")
    if not reference:
        messages.error(request, "No reference provided.")
        return redirect("fund_wallet")

    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        data = response.json()
        print("Verification response:", data)
    except Exception as e:
        messages.error(request, f"Verification Error: {str(e)}")
        return redirect("fund_wallet")

    if data.get("status") and data["data"]["status"] == "success":
        amount_paid = Decimal(data["data"]["amount"]) / Decimal(100)  # convert from kobo
        profile = request.user.userprofile
        profile.wallet_balance += amount_paid
        profile.save()

        Transaction.objects.create(
            user=request.user,
            reference=reference,
            amount=amount_paid,
            status="success"
        )

        messages.success(request, f"Wallet funded with ₦{amount_paid} successfully!")
        return redirect("dashboard")
    else:
        messages.error(request, "Payment verification failed.")

        Transaction.objects.create(
            user=request.user,
            reference=reference,
            amount=Decimal(data["data"]["amount"]) /Decimal(100),
            status="failed"
        )
        return redirect("fund_wallet")
