from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from decimal import Decimal

import requests, json, uuid, hashlib, hmac

from .forms import FundWalletForm
from .models import WalletFunding, Wallet
from register.models import UserProfile
from base.models import Transaction
from .services.paystack import create_dedicated_account


# ==================-------- WALLET PAGE ---------------------==============@
@login_required
def wallet_page(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)

    if not wallet.account_number:
        try:
            create_virtual_account(request.user, wallet)
        except Exception as e:
            return render(request, "wallet/wallet.html", {"error": str(e)})

    context = {"wallet": wallet}
    return render(request, "wallet/wallet.html", context)


@login_required
def monnify_callback(request):
    """
    Called after user completes payment on Monnify page.
    You can also verify payment here using Monnify API.
    """
    reference = request.GET.get("paymentReference")
    if not reference:
        messages.error(request, "Payment reference missing.")
        return redirect("wallet_page")

    # Optional: call Monnify API to verify the payment reference
    # If verified, update Wallet model accordingly

    messages.success(request, "Payment successful! Your wallet has been funded.")
    return redirect("wallet_page")



@csrf_exempt
def monnify_webhook(request):
    if request.method != "POST":
        return JsonResponse({"status": False, "message": "Invalid request"}, status=400)

    # Get webhook payload and signature
    payload = request.body
    signature = request.headers.get("x-webhook-signature")

    # Verify signature
    secret_key = settings.MONNIFY_SECRET_KEY.encode("utf-8")
    calculated_signature = hmac.new(secret_key, payload, hashlib.sha512).hexdigest()

    if signature != calculated_signature:
        return JsonResponse({"status": False, "message": "Invalid signature"}, status=403)

    event = json.loads(payload)

    # Only process successful payment events
    if event.get("eventType") == "PAYMENT_SUCCESS":
        data = event["eventData"]
        account_number = data["virtualAccount"]["accountNumber"]
        amount_paid = data["amountPaid"]

        try:
            wallet = Wallet.objects.get(account_number=account_number)
            wallet.wallet_balance += amount_paid
            wallet.save()
        except Wallet.DoesNotExist:
            return JsonResponse({"status": False, "message": "Wallet not found"}, status=404)

        return JsonResponse({"status": True, "message": "Wallet funded successfully"})

    return JsonResponse({"status": True, "message": "Event ignored"})




# ---------------- PAYSTACK CALLBACK ----------------
@login_required
@csrf_exempt
def paystack_callback(request):
    reference = request.GET.get("reference")
    if not reference:
        messages.error(request, "No reference provided.")
        return redirect("fund_wallet")

    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

    try:
        response = requests.get(url, headers=headers, timeout=30)
        data = response.json()
    except Exception as e:
        messages.error(request, f"Verification Error: {str(e)}")
        return redirect("fund_wallet")

    if data.get("status") and data["data"]["status"] == "success":
        amount_paid = Decimal(data["data"]["amount"]) / Decimal(100)
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
        Transaction.objects.create(
            user=request.user,
            reference=reference,
            amount=Decimal(data["data"]["amount"]) / Decimal(100),
            status="failed"
        )
        messages.error(request, "Payment verification failed.")
        return redirect("fund_wallet")

# ---------------- PAYSTACK WEBHOOK ----------------
@csrf_exempt
def paystack_webhook(request):
    if request.method != "POST":
        return JsonResponse({"status": False, "message": "Invalid request"}, status=400)

    paystack_signature = request.headers.get("x-paystack-signature")
    body = request.body.decode("utf-8")

    hash_test = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
        msg=body.encode("utf-8"),
        digestmod=hashlib.sha512
    ).hexdigest()

    if hash_test != paystack_signature:
        return JsonResponse({"status": False, "message": "Invalid signature"}, status=403)

    event = json.loads(body)

    if event["event"] == "charge.success":
        data = event["data"]
        amount = int(data["amount"]) / 100
        customer_code = data["customer"]["customer_code"]

        try:
            wallet = Wallet.objects.get(paystack_customer_code=customer_code)
            wallet.balance += amount
            wallet.save()
        except Wallet.DoesNotExist:
            return JsonResponse({"status": False, "message": "Wallet not found"}, status=404)

        return JsonResponse({"status": True, "message": "Wallet funded successfully"})

    return JsonResponse({"status": True, "message": "Event ignored"})



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Wallet
from .services.monnify import create_virtual_account




