import json
import logging
from decimal import Decimal
from datetime import timedelta

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from base.models import Transaction
from register.models import UserProfile

logger = logging.getLogger(__name__)

PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
PAYSTACK_PUBLIC_KEY = settings.PAYSTACK_PUBLIC_KEY
PAYSTACK_BASE_URL = "https://api.paystack.co"


# ------------------- Helpers -------------------
def calculate_fee(amount: Decimal) -> Decimal:
    """
    Deduct ₦50 if amount < 10,000, otherwise 1.5% capped at 2,000.
    """
    if amount < 10000:
        return Decimal("20.00")
    fee = amount * Decimal("0.015")
    return min(fee, Decimal("2000.00")).quantize(Decimal("1.00"))


def ensure_paystack_customer(profile: UserProfile):
    """
    Ensure a Paystack customer exists for this profile; create if missing.
    """
    if profile.paystack_customer_code:
        return profile.paystack_customer_code

    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    payload = {
        "email": profile.email,
        "first_name": profile.username,   # per your request
        "last_name": "User",
        "phone": profile.phone or "",
    }
    res = requests.post(f"{PAYSTACK_BASE_URL}/customer", headers=headers, json=payload).json()
    if not res.get("status"):
        raise ValueError(res.get("message") or "Unable to create Paystack customer.")

    profile.paystack_customer_code = res["data"]["customer_code"]
    profile.save(update_fields=["paystack_customer_code"])
    return profile.paystack_customer_code


def create_or_get_dva(profile):
    """
    Create (once) or return cached DVA details.
    """
    # profile = request.user
    # Already has DVA
    if profile.virtual_account_number and profile.virtual_account_bank:
        return {
            "status": True,
            "account_number": profile.virtual_account_number,
            "account_name": profile.virtual_account_name,
            "bank_name": profile.virtual_account_bank,
        }

    # Create
    customer_code = ensure_paystack_customer(profile)
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}", "content-type": "application/json",}
    payload = {
        "phone": profile.phone,
        "customer": customer_code,
        "preferred_bank": "wema-bank",
    }
    resp = requests.post(f"{PAYSTACK_BASE_URL}/dedicated_account", headers=headers, json=payload).json()
    if not resp.get("status") or "data" not in resp:
        return {"status": False, "message": resp.get("message", "Error creating DVA")}

    acc = resp["data"]
    profile.virtual_account_number = acc["account_number"]
    profile.virtual_account_name = acc["account_name"]
    profile.virtual_account_bank = acc["bank"]["name"]
    profile.save(update_fields=["virtual_account_number", "virtual_account_name", "virtual_account_bank"])

    return {
        "status": True,
        "account_number": profile.virtual_account_number,
        "account_name": profile.virtual_account_name,
        "bank_name": profile.virtual_account_bank,
    }


# ------------------- Pages -------------------
@login_required
def fund_wallet(request):
    """
    Main page — shows amount form first. If no DVA yet, shows 'Generate DVA' and Inline Paystack.
    If DVA exists, shows amount form first; reveals DVA details when user clicks the 'Bank transfer' path.
    """
    profile = request.user
    return render(request, "wallet/fund_wallet.html", {
        "profile": profile,
        "PAYSTACK_PUBLIC_KEY": PAYSTACK_PUBLIC_KEY,
    })


# ------------------- AJAX: Check / Create DVA -------------------
@login_required
def check_dva(request):
    try:
        profile = request.user
    except UserProfile.DoesNotExist:
        return JsonResponse({"success": False, "has_dva": False, "message": "No profile found."}, status=400)

    if profile.virtual_account_number and profile.virtual_account_bank:
        return JsonResponse({
            "success": True,
            "has_dva": True,
            "bank_name": profile.virtual_account_bank,
            "account_number": profile.virtual_account_number,
            "account_name": profile.virtual_account_name,
        })
    return JsonResponse({"success": True, "has_dva": False})


@login_required
def generate_dva(request):
    if request.method != "POST":
        return JsonResponse({"status": False, "message": "Invalid method."}, status=405)
    try:
        result = create_or_get_dva(request.user)
        return JsonResponse(result, status=200 if result.get("status") else 400)
    except Exception as e:
        return JsonResponse({"status": False, "message": str(e)}, status=400)


# ------------------- Inline Paystack -------------------
from django.http import JsonResponse
import uuid
@login_required
def create_pending_transaction(request):
    profile = user=request.user
    """
    Create a pending transaction before opening Paystack inline.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        amount = Decimal(request.POST.get("amount", "0"))
        if amount < 100:
            return JsonResponse({"error": "Minimum amount is 100 NGN"}, status=400)

        fee = calculate_fee(amount)
        net_amount = amount - fee

        reference = f"PSK-{uuid.uuid4().hex[:12]}"

        txn = Transaction.objects.create(
            user=request.user,
            service="wallet",
            provider="paystack",
            amount=amount,
            gross_amount=amount,
            fee_amount=fee,
            net_amount=net_amount,
            status="pending",
            transaction_type="wallet_fund",
            # Fill “strict” fields to avoid NOT NULL issues
            customer_name=request.user.username,
            bank_name="",
            cashback=Decimal("0.00"),
            # currency="NGN",
            initial_amount=profile.wallet_balance,
            final_amount=Decimal("0.00"),
            raw_response={},
            reference=reference, 
        )
        return JsonResponse({
            "status": "success",
            "reference": txn.reference,
            "public_key": settings.PAYSTACK_PUBLIC_KEY,
            "email": request.user.email or "noemail@example.com",
            "amount": int(amount * 100),  # Paystack expects kobo
            "fee": float(fee),
            "net_amount": float(net_amount),
        })
    except Exception as e:
        logger.exception("create_pending_transaction error")
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def paystack_callback(request):
    """
    Verify Paystack payment and update wallet.
    (Called after inline Paystack success callback)
    """
    reference = request.GET.get("reference")
    if not reference:
        return JsonResponse({"ok": False, "message": "Missing reference"}, status=400)

    txn = Transaction.objects.filter(reference=reference, user=request.user).first()
    if not txn:
        return JsonResponse({"ok": False, "message": "Transaction not found."}, status=404)

    if txn.status == "success":
        # already credited
        return JsonResponse({"ok": True, "credited": 0, "message": "Already processed."})

    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    res = requests.get(f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}", headers=headers).json()

    if res.get("status") and res.get("data", {}).get("status") == "success":
        # Credit wallet with net amount
        profile = request.user.userprofile
        profile.wallet_balance += txn.net_amount
        profile.save(update_fields=["wallet_balance"])

        txn.status = "success"
        txn.provider = (res.get("data", {}).get("channel") or "paystack")
        txn.bank_name = res.get("data", {}).get("authorization", {}).get("bank", "") or ""
        txn.raw_response = res
        txn.save(update_fields=["status", "provider", "bank_name", "raw_response"])

        return JsonResponse({"ok": True, "credited": float(txn.net_amount)})
    else:
        txn.status = "failed"
        txn.raw_response = res
        txn.save(update_fields=["status", "raw_response"])
        return JsonResponse({"ok": False, "message": "Verification failed."}, status=400)


# ------------------- DVA Auto-Credit (polled by frontend) -------------------
@login_required
def dva_auto_credit(request):
    """
    Poll Paystack DVA requery and credit any *new* inbound transfers.
    Returns how much was credited now (if any).
    """
    if request.method != "GET":
        return JsonResponse({"success": False, "error": "Invalid method."}, status=405)

    profile = request.user
    if not (profile.virtual_account_number and profile.virtual_account_bank):
        return JsonResponse({"success": False, "error": "No DVA assigned yet."}, status=400)

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    params = {
        "account_number": profile.virtual_account_number,
        "provider_slug": "wema-bank",
        "date": timezone.now().strftime("%Y-%m-%d"),
    }

    try:
        res = requests.get(f"{PAYSTACK_BASE_URL}/dedicated_account/requery", headers=headers, params=params, timeout=15)
        data = res.json()

        if not data.get("status"):
            return JsonResponse({"success": False, "error": data.get("message", "Failed to query DVA")}, status=400)

        txns = data.get("data", {}).get("transactions", []) or []
        credited_total = Decimal("0.00")
        last_net = Decimal("0.00")

        # Only consider recent transactions (last 1 day) to be safe
        for t in txns:
            ref = t.get("reference")
            t_amount = Decimal(str(t.get("amount", "0")))  # Paystack DVA amount is already NGN units
            # Skip if we already recorded this reference
            if not ref or Transaction.objects.filter(reference=ref).exists():
                continue

            fee = calculate_fee(t_amount)
            net_amount = t_amount - fee

            # Credit wallet
            profile.wallet_balance += net_amount
            profile.save(update_fields=["wallet_balance"])

            Transaction.objects.create(
                user=request.user,
                service="wallet",
                provider="DVA Transfer",
                amount=t_amount,
                gross_amount=t_amount,
                fee_amount=fee,
                net_amount=net_amount,
                status="success",
                transaction_type="wallet_fund",
                reference=ref,  # keep original reference so we can de-duplicate correctly
                customer_name=request.user.username,
                bank_name=profile.virtual_account_bank,
                cashback=Decimal("0.00"),
                # currency="NGN",
                raw_response=t,
            )

            credited_total += net_amount
            last_net = net_amount

        if credited_total > 0:
            return JsonResponse({
                "success": True,
                "credited": float(credited_total),
                "last_net": float(last_net),
                "message": f"Wallet credited successfully with ₦{credited_total}",
            })
        return JsonResponse({"success": True, "credited": 0})
    except Exception as e:
        logger.exception("dva_auto_credit error")
        return JsonResponse({"success": False, "error": str(e)}, status=400)


# ------------------- Paystack Webhook (optional, keep active) -------------------
'''
@csrf_exempt
def paystack_webhook(request):
    """
    Handle Paystack webhook for inline payments + DVA auto-credit.
    """
    try:
        payload = json.loads(request.body or "{}")
        event = payload.get("event")
        data = payload.get("data", {})
        reference = data.get("reference")

        logger.info("Paystack webhook received: %s", payload)

        # --- Detect Amount ---
        amount = Decimal("0.00")
        if event and event.startswith("charge."):
            # Inline payment = Kobo
            amount = Decimal(data.get("amount", 0)) / 100
        elif event and event.startswith("transfer."):
            # DVA = NGN already
            amount = Decimal(str(data.get("amount", "0")))

        # --- Find User ---
        profile = None
        customer = data.get("customer") or {}
        customer_code = customer.get("customer_code")

        if customer_code:
            profile = UserProfile.objects.filter(paystack_customer_code=customer_code).first()

        if not profile and reference:
            t = Transaction.objects.filter(reference=reference).first()
            if t:
                profile = t.user.userprofile

        if not profile or amount <= 0:
            logger.warning("Webhook: Could not find profile for event=%s, ref=%s", event, reference)
            return HttpResponse(status=200)

        # --- Prevent double credit ---
        if reference and Transaction.objects.filter(reference=reference, status="success").exists():
            return HttpResponse(status=200)

        # --- Credit Wallet ---
        fee = calculate_fee(amount)
        net_amount = amount - fee
        profile.wallet_balance += net_amount
        profile.save(update_fields=["wallet_balance"])

        Transaction.objects.create(
            user=profile.user,
            service="wallet",
            provider=data.get("channel", "paystack"),
            amount=amount,
            gross_amount=amount,
            fee_amount=fee,
            net_amount=net_amount,
            status="success",
            transaction_type="wallet_fund",
            reference=reference or f"PS-{timezone.now().timestamp()}",
            customer_name=profile.user.username,
            bank_name=(data.get("authorization", {}) or {}).get("bank", "") or "",
            cashback=Decimal("0.00"),
            currency="NGN",
            raw_response=data,
        )

        logger.info("Webhook: Credited %s for user %s via %s", net_amount, profile.user.username, event)
        return HttpResponse(status=200)

    except Exception:
        logger.exception("paystack_webhook error")
        return HttpResponse(status=200)
'''


import json
import logging
from decimal import Decimal
from django.http import HttpResponse
from django.utils import timezone
from base.models import Transaction
from register.models import UserProfile
# from .utils import calculate_fee   # make sure you have this

logger = logging.getLogger(__name__)
@csrf_exempt
def paystack_webhook(request):
    """
    Handles both Inline Payments and DVA (Dedicated Virtual Account) Transfers.
    """
    try:
        payload = json.loads(request.body or "{}")
        event = payload.get("event")
        data = payload.get("data", {})
        reference = data.get("reference")

        logger.info(f"Paystack webhook event: {event}, ref={reference}")

        # Normalize amount
        amount = Decimal(str(data.get("amount", "0")))
        if event and event.startswith("charge."):
            amount = amount / 100  # Paystack sends kobo for charges

        if amount <= 0:
            return HttpResponse(status=200)

        # Identify profile
        profile = None
        customer = data.get("customer") or {}
        customer_code = customer.get("customer_code")

        if customer_code:
            profile = UserProfile.objects.filter(paystack_customer_code=customer_code).first()

        if not profile and reference:
            txn = Transaction.objects.filter(reference=reference).first()
            if txn:
                profile = txn.user

        if not profile:
            logger.warning(f"No profile found for webhook ref={reference}")
            return HttpResponse(status=200)

        # Prevent duplicate credits
        if reference and Transaction.objects.filter(reference=reference, status="success").exists():
            return HttpResponse(status=200)

        # Apply fee & credit
        fee = calculate_fee(amount)
        net_amount = amount - fee
        profile.wallet_balance += net_amount
        profile.save(update_fields=["wallet_balance"])

        Transaction.objects.create(
            user=profile,
            service="wallet",
            provider=data.get("channel", "paystack"),
            amount=amount,
            gross_amount=amount,
            fee_amount=fee,
            net_amount=net_amount,
            status="success",
            transaction_type="wallet_fund",
            reference=reference or f"PS-{uuid.uuid4().hex[:12]}",
            customer_name=profile.username,
            bank_name=(data.get("authorization", {}) or {}).get("bank", ""),
            cashback=Decimal("0.00"),
            currency="NGN",
            raw_response=data,
            method="dva" if "dedicatedaccount" in (event or "") else "inline",
        )

        logger.info(f"Wallet credited: user={profile.username}, amount={net_amount}")
        return HttpResponse(status=200)

    except Exception:
        logger.exception("paystack_webhook error")
        return HttpResponse(status=200)
