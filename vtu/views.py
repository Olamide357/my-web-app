from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from .utils import makeVTpassRequest
from .vtpass import purchaseAirtime


# from .decimal import Decimal
   # views.py
import requests, secrets, logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import AirtimeForm
from register.models import UserProfile
from base.models import Transaction, Beneficiary
from django.conf import settings
import requests
import uuid

logger = logging.getLogger(__name__)

# CashBack percent for Airtime
AIRTIME_CASHBACK_PERCENT = 0.02  # 2%

# Create your views here.
#=============================================================================================================================#

#========================================= AIRTIMES VIEWS ====================================================================#

#=============================================================================================================================#

#======================= MTN AIRTIME ================================#  
'''
@login_required
def mtnAirtime(request):
    cashback_percent = 2
    if request.method == "POST":
        phone = request.POST.get("phone")
        amount = request.POST.get("amount")

        result = purchaseAirtime(phone, amount)
        return JsonResponse(result, safe=False)

    return render(request, "airtime/mtn_airtime.html")
'''
@login_required
def mtnAirtime(request):
    cashback_percent = Decimal("2")
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    beneficiaries = Beneficiary.objects.filter(user=request.user, provider="MTN")
    if request.method == "POST":
        form = AirtimeForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            amount = form.cleaned_data['amount']
            password = form.cleaned_data['password']

            # Check wallet password
            if not request.user.check_password(password):
                messages.error(request, "Incorrect password.")
                return render(request, "airtime/mtn_airtime.html", {"form": form})

            # Validate network: MTN starts with 0703, 0706, 0803, 0806, 0813, 0816, 0810, 0814, 0903, 0906, 0913, 0916
            # mtn_prefixes = ["0703","0706","0803","0806","0813","0816","0810","0814","0903","0906","0913","0916"]
            # if not any(phone.startswith(p) for p in mtn_prefixes):
                # messages.error(request, "Phone number does not match MTN network.")
                # return render(request, "airtime/mtn_airtime.html", {"form": form})

            # Check wallet balance
            if profile.wallet_balance < amount:
                messages.error(request, "Insufficient wallet balance.")
                return render(request, "airtime/mtn_airtime.html", {"form": form})

            # Deduct from wallet
            profile.wallet_balance -= amount
            profile.save()

            # Create transaction
            # reference = "AIRTIME_" + secrets.token_hex(8)
            reference = str(uuid.uuid4())  # unique transaction ID
            transaction = Transaction.objects.create(
                user=request.user,
                provider="MTN",
                phone=phone,
                amount=amount,
                gross_amount=amount,
                cashback=0,
                reference=reference,
                status="pending"
            )

            url = f"{settings.VTPASS_BASE_URL}/pay"
            # Call VTpass API
            payload = {
                "serviceID": "mtn",
                "amount": float(amount),
                "phone": phone,
                "request_id": reference,
            }

            headers = {
                "api-key":f"{settings.VTPASS_APIKEY}",
                "secret-key": f"{settings.VTPASS_SECRET_KEY}"
            }

            try:
                
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                # data = purchaseAirtime(phone, amount)
                # return JsonResponse(data, safe=False)
                logger.info(f"VTpass MTN airtime response: {data}")

                if data.get("code") == "000":
                    # Calculate cashback
                    cashback = round(amount * cashback_percent / 100, 2)
                    profile.wallet_balance += cashback
                    profile.save()

                    transaction.cashback = cashback
                    transaction.status = "success"
                    transaction.save()
                    messages.success(request, f"MTN Airtime {amount} NGN sent to {phone}. Cashback ₦{cashback} credited.")
                else:
                    transaction.status = "failed"
                    transaction.save()

                    # Refund user if failed
                    profile.wallet_balance += amount
                    profile.save()
                    messages.error(request, f"Airtime purchase failed: {data.get('response_description')}")

            except requests.exceptions.RequestException as e:
                # Refund wallet
                profile.wallet_balance += amount
                profile.save()
                transaction.status = "failed"
                transaction.save()
                messages.error(request, f"Network Error: {str(e)}")

            return redirect("mtn_airtime")
    else:
        form = AirtimeForm()

    # Display recent MTN transactions
    # transactions = AirtimeTransaction.objects.filter(user=request.user, network="MTN").order_by("-created_at")[:10]

    context = {
        "form": form,
        # "transaction": transaction,
        "profile": profile,
        "beneficiaries": beneficiaries
    }
    return render(request, "airtime/mtn_airtime.html", context)


#====================== GLO AIRTIME =========================#
'''
@login_required
def gloAirtime(request):
    cashback_percent = 2
    if request.method == "POST":
        phone = request.POST.get("phone")
        amount = request.POST.get("amount")

        result = purchaseAirtime(phone, amount)
        return JsonResponse(result, safe=False)

    return render(request, "airtime/glo_airtime.html")

'''
# GLO Airtime View
@login_required
@login_required
def gloAirtime(request):
    cashback_percent = 2
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    beneficiaries = Beneficiary.objects.filter(user=request.user, provider="GLO")

    if request.method == "POST":
        form = AirtimeForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            amount = form.cleaned_data['amount']
            password = form.cleaned_data['password']

            # Check wallet password
            if not request.user.check_password(password):
                messages.error(request, "Incorrect password.")
                return render(request, "airtime/glo_airtime.html", {"form": form})

            # Validate network: GLO prefixes
            # glo_prefixes = ["0805","0807","0811","0815","0817","0818","0905","0907","0915"]
            # if not any(phone.startswith(p) for p in glo_prefixes):
                # messages.error(request, "Phone number does not match GLO network.")
                # return render(request, "airtime/glo_airtime.html", {"form": form})

            # Check wallet balance
            if profile.wallet_balance < amount:
                messages.error(request, "Insufficient wallet balance.")
                return render(request, "airtime/glo_airtime.html", {"form": form})

            # Deduct from wallet
            profile.wallet_balance -= amount
            profile.save()

            # Create transaction
            reference = "AIRTIME_" + secrets.token_hex(8)
            transaction = Transaction.objects.create(
                user=request.user,
                provider="GLO",
                phone=phone,
                amount=amount,
                gross_amount=amount,
                cashback=0,
                reference=reference,
                status="pending"
            )

            # Call VTpass API
            payload = {
                "serviceID": "glo",
                "amount": float(amount),
                "phone": phone,
                "request_id": reference,
            }

            headers = {
                "api-key":"cc969077fc1e06af06d73356bd05505b",
                "secret-key": "SK_317f59f75699dfee4d534955d4012d2947171d69cb1"
            }

            try:
                response = requests.post(f"{settings.VTPASS_BASE_URL}/pay", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                logger.info(f"GLO airtime response: {data}")

                if data.get("code") == "000":
                    # Calculate cashback
                    cashback = round(amount * cashback_percent / 100, 2)
                    profile.wallet_balance += cashback
                    profile.save()

                    transaction.cashback = cashback
                    transaction.status = "Success"
                    transaction.save()
                    messages.success(request, f"GLO Airtime {amount} NGN sent to {phone}. Cashback ₦{cashback} credited.")
                else:
                    transaction.status = "Failed"
                    transaction.save()
                    # Refund wallet
                    profile.wallet_balance += amount
                    profile.save()
                    messages.error(request, f"Airtime purchase failed: {data.get('response_description')}")

            except requests.exceptions.RequestException as e:
                # Refund wallet
                profile.wallet_balance += amount
                profile.save()
                transaction.status = "Failed"
                transaction.save()
                messages.error(request, f"Network Error: {str(e)}")

            return redirect("glo_airtime")
    else:
        form = AirtimeForm()

    context = {
        "form": form,
        "profile": profile,
        "beneficiaries": beneficiaries
    }
    return render(request, "airtime/glo_airtime.html", context)


    
#================ AIRTEL AIRTIME ============================#
'''
@login_required
def airtelAirtime(request):
    cashback_percent = 2
    if request.method == "POST":
        phone = request.POST.get("phone")
        amount = request.POST.get("amount")

        result = purchaseAirtime(phone, amount)
        return JsonResponse(result, safe=False)

    return render(request, "airtime/airtel_airtime.html")

'''
@login_required
def airtelAirtime(request):
    cashback_percent = 2
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    beneficiaries = Beneficiary.objects.filter(user=request.user, provider="AIRTEL")

    if request.method == "POST":
        form = AirtimeForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            amount = form.cleaned_data['amount']
            password = form.cleaned_data['password']

            # Check wallet password
            if not request.user.check_password(password):
                messages.error(request, "Incorrect password.")
                return render(request, "airtime/airtel_airtime.html", {"form": form})

            # Validate Airtel network prefixes
            # airtel_prefixes = ["0802","0808","0812","0701","0708","0901","0902","0904","0907","0912"]
            # if not any(phone.startswith(p) for p in airtel_prefixes):
                # messages.error(request, "Phone number does not match Airtel network.")
                # return render(request, "airtime/airtel_airtime.html", {"form": form})

            # Check wallet balance
            if profile.wallet_balance < amount:
                messages.error(request, "Insufficient wallet balance.")
                return render(request, "airtime/airtel_airtime.html", {"form": form})

            # Deduct wallet (only amount, cashback later)
            profile.wallet_balance -= amount
            profile.save()

            # Create transaction with cashback = 0 for now
            reference = "AIRTIME_" + secrets.token_hex(8)
            transaction = Transaction.objects.create(
                user=request.user,
                provider="AIRTEL",
                phone=phone,
                amount=amount,
                gross_amount=amount,
                cashback=0,
                reference=reference,
                status="Pending"
            )

            # Call VTpass API
            payload = {
                "serviceID": "airtel",
                "amount": float(amount),
                "phone": phone,
                "request_id": reference,
            }

            headers = {
                "api-key":"cc969077fc1e06af06d73356bd05505b",
                "secret-key": "SK_317f59f75699dfee4d534955d4012d2947171d69cb1"
            }

            try:
                response = requests.post(f"{settings.VTPASS_BASE_URL}/pay", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                logger.info(f"VTpass Airtel airtime response: {data}")

                if data.get("code") == "000":
                    # ✅ Success → add cashback
                    cashback = round(amount * cashback_percent / 100, 2)
                    profile.wallet_balance += cashback
                    profile.save()

                    transaction.cashback = cashback
                    transaction.status = "Success"
                    transaction.save()

                    messages.success(request, f"Airtel Airtime ₦{amount} sent to {phone}. Cashback ₦{cashback} credited.")
                else:
                    transaction.status = "Failed"
                    transaction.save()
                    # Refund user
                    profile.wallet_balance += amount
                    profile.save()
                    messages.error(request, f"Airtime purchase failed: {data.get('response_description')}")

            except requests.exceptions.RequestException as e:
                # Refund wallet
                profile.wallet_balance += amount
                profile.save()
                transaction.status = "Failed"
                transaction.save()
                messages.error(request, f"Network Error: {str(e)}")

            return redirect("airtel_airtime")
    else:
        form = AirtimeForm()

    context = {
        "form": form,
        "profile": profile,
        "beneficiaries": beneficiaries
    }
    return render(request, "airtime/airtel_airtime.html", context)


#================== 9MOBILE AIRTIME ========================#
'''
@login_required
def ninemobileAirtime(request):
    cashback_percent = 2
    if request.method == "POST":
        phone = request.POST.get("phone")
        amount = request.POST.get("amount")

        result = purchaseAirtime(phone, amount)
        return JsonResponse(result, safe=False)

    return render(request, "airtime/ninemobile_airtime.html")

'''
@login_required
def ninemobileAirtime(request):
    cashback_percent = 2
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    beneficiaries = Beneficiary.objects.filter(user=request.user, provider="9MOBILE")

    if request.method == "POST":
        form = AirtimeForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone_number']
            amount = form.cleaned_data['amount']
            password = form.cleaned_data['password']

            # Check wallet password
            if not request.user.check_password(password):
                messages.error(request, "Incorrect password.")
                return render(request, "airtime/ninemobile_airtime.html", {"form": form})

            # ✅ Validate 9mobile network prefixes
            # nine_mobile_prefixes = ["0809", "0817", "0818", "0908", "0909"]
            # if not any(phone.startswith(p) for p in nine_mobile_prefixes):
                # messages.error(request, "Phone number does not match 9mobile network.")
                # return render(request, "airtime/ninemobile_airtime.html", {"form": form})

            # Check wallet balance
            if profile.wallet_balance < amount:
                messages.error(request, "Insufficient wallet balance.")
                return render(request, "airtime/ninemobile_airtime.html", {"form": form})

            # Deduct wallet (only amount, cashback later)
            profile.wallet_balance -= amount
            profile.save()

            # Create transaction
            reference = "AIRTIME_9MOBILE_" + secrets.token_hex(8)
            transaction = Transaction.objects.create(
                user=request.user,
                provider="9MOBILE",
                phone=phone,
                amount=amount,
                gross_amount=amount,
                cashback=0,
                reference=reference,
                status="Pending"
            )

            # Call VTpass API
            payload = {
                "serviceID": "etisalat",
                "amount": float(amount),
                "phone": phone,
                "request_id": reference,
            }

            headers = {
                "api-key":"cc969077fc1e06af06d73356bd05505b",
                "secret-key": "SK_317f59f75699dfee4d534955d4012d2947171d69cb1"
            }

            try:
                response = requests.post(f"{settings.VTPASS_BASE_URL}/pay", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                logger.info(f"9mobile airtime response: {data}")

                if data.get("code") == "000":
                    # ✅ Success → add cashback
                    cashback = round(amount * cashback_percent / 100, 2)
                    profile.wallet_balance += cashback
                    profile.save()

                    transaction.cashback = cashback
                    transaction.status = "Success"
                    transaction.save()

                    messages.success(request, f"9mobile Airtime ₦{amount} sent to {phone}. Cashback ₦{cashback} credited.")
                else:
                    transaction.status = "Failed"
                    transaction.save()
                    # Refund user
                    profile.wallet_balance += amount
                    profile.save()
                    messages.error(request, f"Airtime purchase failed: {data.get('response_description')}")

            except requests.exceptions.RequestException as e:
                # Refund wallet
                profile.wallet_balance += amount
                profile.save()
                transaction.status = "Failed"
                transaction.save()
                messages.error(request, f"Network Error: {str(e)}")

            return redirect("ninemobile_airtime")
    else:
        form = AirtimeForm()

    context = {
        "form": form,
        "profile": profile,
        "beneficiaries": beneficiaries
    }
    return render(request, "airtime/ninemobile_airtime.html", context)



#==============================================================================================================================#
#================================================= DATA VIEWS =================================================================#
#==============================================================================================================================#

#==================== MTN DATA ===============================#


import uuid, requests
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from register.models import UserProfile
from .models import DataPlan
from base.models import Transaction, Beneficiary
from .forms import DataPurchaseForm


# ================= MTN DATA ================== #

@login_required
def mtnData(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    beneficiaries = Beneficiary.objects.filter(user=request.user, provider="MTN")

    if request.method == "POST":
        form = DataPurchaseForm(request.POST, network="MTN")
        if form.is_valid():
            phone = form.cleaned_data["phone_number"]
            plan = form.cleaned_data["plan"]
            password = form.cleaned_data["password"]

            # Check user password
            if not request.user.check_password(password):
                messages.error(request, "Incorrect wallet password.")
                return render(request, "data/mtn_data.html", {
                    "form": form,
                    "profile": profile,
                    "beneficiaries": beneficiaries
                })

            # Check wallet balance
            if profile.wallet_balance < plan.amount:
                messages.error(request, "Insufficient wallet balance.")
                return render(request, "data/mtn_data.html", {
                    "form": form,
                    "profile": profile,
                    "beneficiaries": beneficiaries
                })

            # Deduct wallet first
            profile.wallet_balance -= plan.amount
            profile.save()

            # Create a transaction
            reference = str(uuid.uuid4())
            transaction = Transaction.objects.create(
                user=request.user,
                provider="MTN-DATA",
                phone=phone,
                cashback = 0,
                amount=plan.amount,
                gross_amount=plan.amount,
                reference=reference,
                status="Pending"
            )

            # Prepare payload for VTpass
            payload = {
                "request_id": reference,
                "serviceID": "mtn-data",
                "amount": float(plan.amount),
                "phone": phone,
                "billersCode": phone,
                "variation_code": plan.plan_code
            }
            headers = {
                "api-key": settings.VTPASS_APIKEY,
                "secret-key": settings.VTPASS_SECRET_KEY
            }

            try:
                response = requests.post(f"{settings.VTPASS_BASE_URL}/pay", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                if data.get("code") == "000":
                    transaction.status = "Success"
                    transaction.save()
                    messages.success(request, f"{plan.plan_name} sent to {phone} successfully!")
                else:
                    transaction.status = "Failed"
                    transaction.save()
                    # Refund wallet
                    profile.wallet_balance += plan.amount
                    profile.save()
                    messages.error(request, f"Purchase failed: {data.get('response_description')}")

            except requests.exceptions.RequestException as e:
                transaction.status = "Failed"
                transaction.save()
                profile.wallet_balance += plan.amount
                profile.save()
                messages.error(request, f"Network Error: {str(e)}")

            return redirect("mtn_data")
    else:
        form = DataPurchaseForm(network="MTN")

    return render(request, "data/mtn_data.html", {
        "form": form,
        "profile": profile,
        "beneficiaries": beneficiaries
    })



# ================= GLO DATA ================== #
@login_required
def gloData(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    beneficiaries = Beneficiary.objects.filter(user=request.user, provider="GLO")

    if request.method == "POST":
        form = DataPurchaseForm(request.POST, network="GLO")
        if form.is_valid():
            phone = form.cleaned_data["phone_number"]
            plan = form.cleaned_data["plan"]
            password = form.cleaned_data["password"]

            # Check user password
            if not request.user.check_password(password):
                messages.error(request, "Incorrect wallet password.")
                return render(request, "data/glo_data.html", {
                    "form": form,
                    "profile": profile,
                    "beneficiaries": beneficiaries
                })

            # Check wallet balance
            if profile.wallet_balance < plan.amount:
                messages.error(request, "Insufficient wallet balance.")
                return render(request, "data/glo_data.html", {
                    "form": form,
                    "profile": profile,
                    "beneficiaries": beneficiaries
                })

            # Deduct wallet first
            profile.wallet_balance -= plan.amount
            profile.save()

            # Create a transaction
            reference = str(uuid.uuid4())
            transaction = Transaction.objects.create(
                user=request.user,
                provider="GLO-DATA",
                phone=phone,
                cashback = 0,
                amount=plan.amount,
                gross_amount=plan.amount,
                reference=reference,
                status="Pending"
            )

            # Prepare payload for VTpass
            payload = {
                "request_id": reference,
                "serviceID": "glo-data",
                "amount": float(plan.amount),
                "phone": phone,
                "billersCode": phone,
                "variation_code": plan.plan_code
            }
            headers = {
                "api-key": settings.VTPASS_APIKEY,
                "secret-key": settings.VTPASS_SECRET_KEY
            }

            try:
                response = requests.post(f"{settings.VTPASS_BASE_URL}/pay", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                if data.get("code") == "000":
                    transaction.status = "Success"
                    transaction.save()
                    messages.success(request, f"{plan.plan_name} sent to {phone} successfully!")
                else:
                    transaction.status = "Failed"
                    transaction.save()
                    # Refund wallet
                    profile.wallet_balance += plan.amount
                    profile.save()
                    messages.error(request, f"Purchase failed: {data.get('response_description')}")

            except requests.exceptions.RequestException as e:
                transaction.status = "Failed"
                transaction.save()
                profile.wallet_balance += plan.amount
                profile.save()
                messages.error(request, f"Network Error: {str(e)}")

            return redirect("glo_data")
    else:
        form = DataPurchaseForm(network="GLO")

    return render(request, "data/glo_data.html", {
        "form": form,
        "profile": profile,
        "beneficiaries": beneficiaries
    })



# ================= AIRTEL DATA ================== #
@login_required
def airtelData(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    beneficiaries = Beneficiary.objects.filter(user=request.user, provider="AIRTEL")

    if request.method == "POST":
        form = DataPurchaseForm(request.POST, network="AIRTEL")
        if form.is_valid():
            phone = form.cleaned_data["phone_number"]
            plan = form.cleaned_data["plan"]
            password = form.cleaned_data["password"]

            # Check user password
            if not request.user.check_password(password):
                messages.error(request, "Incorrect wallet password.")
                return render(request, "data/airtel_data.html", {
                    "form": form,
                    "profile": profile,
                    "beneficiaries": beneficiaries
                })

            # Check wallet balance
            if profile.wallet_balance < plan.amount:
                messages.error(request, "Insufficient wallet balance.")
                return render(request, "data/airtel_data.html", {
                    "form": form,
                    "profile": profile,
                    "beneficiaries": beneficiaries
                })

            # Deduct wallet first
            profile.wallet_balance -= plan.amount
            profile.save()

            # Create a transaction
            reference = str(uuid.uuid4())
            transaction = Transaction.objects.create(
                user=request.user,
                provider="AIRTEL-DATA",
                phone=phone,
                cashback = 0,
                amount=plan.amount,
                gross_amount=plan.amount,
                reference=reference,
                status="Pending"
            )

            # Prepare payload for VTpass
            payload = {
                "request_id": reference,
                "serviceID": "airtel-data",
                "amount": float(plan.amount),
                "phone": phone,
                "billersCode": phone,
                "variation_code": plan.plan_code
            }
            headers = {
                "api-key": settings.VTPASS_APIKEY,
                "secret-key": settings.VTPASS_SECRET_KEY
            }

            try:
                response = requests.post(f"{settings.VTPASS_BASE_URL}/pay", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                if data.get("code") == "000":
                    transaction.status = "Success"
                    transaction.save()
                    messages.success(request, f"{plan.plan_name} sent to {phone} successfully!")
                else:
                    transaction.status = "Failed"
                    transaction.save()
                    # Refund wallet
                    profile.wallet_balance += plan.amount
                    profile.save()
                    messages.error(request, f"Purchase failed: {data.get('response_description')}")

            except requests.exceptions.RequestException as e:
                transaction.status = "Failed"
                transaction.save()
                profile.wallet_balance += plan.amount
                profile.save()
                messages.error(request, f"Network Error: {str(e)}")

            return redirect("airtel_data")
    else:
        form = DataPurchaseForm(network="AIRTEL")

    return render(request, "data/airtel_data.html", {
        "form": form,
        "profile": profile,
        "beneficiaries": beneficiaries
    })



# ================= 9MOBILE DATA ================== #
@login_required
def ninemobileData(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    beneficiaries = Beneficiary.objects.filter(user=request.user, provider="9MOBILE")

    if request.method == "POST":
        form = DataPurchaseForm(request.POST, network="9MOBILE")
        if form.is_valid():
            phone = form.cleaned_data["phone_number"]
            plan = form.cleaned_data["plan"]
            password = form.cleaned_data["password"]

            # Check user password
            if not request.user.check_password(password):
                messages.error(request, "Incorrect wallet password.")
                return render(request, "data/ninemobile_data.html", {
                    "form": form,
                    "profile": profile,
                    "beneficiaries": beneficiaries
                })

            # Check wallet balance
            if profile.wallet_balance < plan.amount:
                messages.error(request, "Insufficient wallet balance.")
                return render(request, "data/ninemobile_data.html", {
                    "form": form,
                    "profile": profile,
                    "beneficiaries": beneficiaries
                })

            # Deduct wallet first
            profile.wallet_balance -= plan.amount
            profile.save()

            # Create a transaction
            reference = str(uuid.uuid4())
            transaction = Transaction.objects.create(
                user=request.user,
                provider="ETISALAT-DATA",
                phone=phone,
                cashback = 0,
                amount=plan.amount,
                gross_amount=plan.amount,
                reference=reference,
                status="Pending"
            )

            # Prepare payload for VTpass
            payload = {
                "request_id": reference,
                "serviceID": "etisalat-data",
                "amount": float(plan.amount),
                "phone": phone,
                "billersCode": phone,
                "variation_code": plan.plan_code
            }
            headers = {
                "api-key": settings.VTPASS_APIKEY,
                "secret-key": settings.VTPASS_SECRET_KEY
            }

            try:
                response = requests.post(f"{settings.VTPASS_BASE_URL}/pay", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                if data.get("code") == "000":
                    transaction.status = "Success"
                    transaction.save()
                    messages.success(request, f"{plan.plan_name} sent to {phone} successfully!")
                else:
                    transaction.status = "Failed"
                    transaction.save()
                    # Refund wallet
                    profile.wallet_balance += plan.amount
                    profile.save()
                    messages.error(request, f"Purchase failed: {data.get('response_description')}")

            except requests.exceptions.RequestException as e:
                transaction.status = "Failed"
                transaction.save()
                profile.wallet_balance += plan.amount
                profile.save()
                messages.error(request, f"Network Error: {str(e)}")

            return redirect("mtn_data")
    else:
        form = DataPurchaseForm(network="9MOBILE")

    return render(request, "data/ninemobile_data.html", {
        "form": form,
        "profile": profile,
        "beneficiaries": beneficiaries
    })


#============================================================#

#================= TV ======================================@
import uuid
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .forms import TVPurchaseForm
from register.models import UserProfile
from base.models import Transaction, Beneficiary

#========= VERIFY SMARTCARD ================#
@login_required
def verify_iuc(request):
    number = request.GET.get("number")
    provider = request.GET.get("provider")  # provider must be DSTV, GOTV, STARTIMES

    if not number or not provider:
        return JsonResponse({"success": False, "message": "Missing number or provider"})

    payload = {
        "serviceID": provider.lower(),   # vtpass expects dstv, gotv, startimes
        "billersCode": number,
    }
    headers = {
        "api-key": settings.VTPASS_API_KEY,
        "secret-key": settings.VTPASS_SECRET_KEY,
    }

    try:
        response = requests.post(
            f"{settings.VTPASS_BASE_URL}/merchant-verify",
            json=payload,
            headers=headers,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        if data.get("code") == "000":
            return JsonResponse({
                "success": True,
                "name": data["content"].get("Customer_Name", "Verified Customer")
            })
        else:
            return JsonResponse({
                "success": False,
                "message": data.get("response_description", "Verification failed")
            })
    except requests.exceptions.RequestException as e:
        return JsonResponse({"success": False, "message": f"Network error: {str(e)}"})


#================ DSTV ======================#

@login_required
def DSTV(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    beneficiaries = Beneficiary.objects.filter(user=request.user, service_type="DSTV")

    if request.method == "POST":
        form = TVPurchaseForm(request.POST, provider="DSTV")
        if form.is_valid():
            smartcard = form.cleaned_data["smartcard_number"]
            plan = form.cleaned_data["plan"]
            password = form.cleaned_data["password"]

            if not request.user.check_password(password):
                messages.error(request, "Incorrect wallet password.")
                return render(request, "tv/dstv.html", {
                    "form": form,
                    "profile": profile,
                    "beneficiaries": beneficiaries
                })

            if profile.wallet_balance < plan.amount:
                messages.error(request, "Insufficient wallet balance.")
                return render(request, "tv/dstv.html", {
                    "form": form,
                    "profile": profile,
                    "beneficiaries": beneficiaries
                })

            # Deduct balance
            profile.wallet_balance -= plan.amount
            profile.save()

            reference = str(uuid.uuid4())
            transaction = Transaction.objects.create(
                user=request.user,
                provider="DSTV",
                phone=smartcard,
                cashback=0,
                amount=plan.amount,
                gross_amount=plan.amount,
                reference=reference,
                status="Pending"
            )

            payload = {
                "request_id": reference,
                "serviceID": "dstv",
                "billersCode": smartcard,
                "variation_code": plan.plan_code,
                "amount": float(plan.amount),
                "phone": profile.phone,
                "subscription_type": "change"
            }
            headers = {
                "api-key": settings.VTPASS_APIKEY,
                "secret-key": settings.VTPASS_SECRET_KEY,
            }

            try:
                response = requests.post(f"{settings.VTPASS_BASE_URL}/pay", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                if data.get("code") == "000":
                    transaction.status = "Success"
                    transaction.save()
                    messages.success(request, f"{plan.plan_name} activated successfully for {smartcard}!")
                else:
                    transaction.status = "Failed"
                    transaction.save()
                    profile.wallet_balance += plan.amount
                    profile.save()
                    messages.error(request, f"Purchase failed: {data.get('response_description')}")
            except requests.exceptions.RequestException as e:
                transaction.status = "Failed"
                transaction.save()
                profile.wallet_balance += plan.amount
                profile.save()
                messages.error(request, f"Network Error: {str(e)}")

            return redirect("dstv")
    else:
        form = TVPurchaseForm(provider="DSTV")

    return render(request, "tv/dstv.html", {
        "form": form,
        "profile": profile,
        "beneficiaries": beneficiaries
    })




#================ GOTV ======================#

@login_required
def GOTV(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    beneficiaries = Beneficiary.objects.filter(user=request.user, service_type="GOTV")

    if request.method == "POST":
        form = TVPurchaseForm(request.POST, provider="GOTV")
        if form.is_valid():
            smartcard = form.cleaned_data["smartcard_number"]
            plan = form.cleaned_data["plan"]
            password = form.cleaned_data["password"]

            if not request.user.check_password(password):
                messages.error(request, "Incorrect wallet password.")
                return render(request, "tv/gotv.html", {
                    "form": form,
                    "profile": profile,
                    "beneficiaries": beneficiaries
                })

            if profile.wallet_balance < plan.amount:
                messages.error(request, "Insufficient wallet balance.")
                return render(request, "tv/gotv.html", {
                    "form": form,
                    "profile": profile,
                    "beneficiaries": beneficiaries
                })

            # Deduct balance
            profile.wallet_balance -= plan.amount
            profile.save()

            reference = str(uuid.uuid4())
            transaction = Transaction.objects.create(
                user=request.user,
                provider="GOTV",
                phone=smartcard,
                cashback=0,
                amount=plan.amount,
                gross_amount=plan.amount,
                reference=reference,
                status="Pending"
            )

            payload = {
                "request_id": reference,
                "serviceID": "gotv",
                "billersCode": smartcard,
                "variation_code": plan.plan_code,
                "amount": float(plan.amount),
                "phone": profile.phone,
                "subscription_type": "change"
            }
            headers = {
                "api-key": settings.VTPASS_APIKEY,
                "secret-key": settings.VTPASS_SECRET_KEY,
            }

            try:
                response = requests.post(f"{settings.VTPASS_BASE_URL}/pay", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                if data.get("code") == "000":
                    transaction.status = "Success"
                    transaction.save()
                    messages.success(request, f"{plan.plan_name} activated successfully for {smartcard}!")
                else:
                    transaction.status = "Failed"
                    transaction.save()
                    profile.wallet_balance += plan.amount
                    profile.save()
                    messages.error(request, f"Purchase failed: {data.get('response_description')}")
            except requests.exceptions.RequestException as e:
                transaction.status = "Failed"
                transaction.save()
                profile.wallet_balance += plan.amount
                profile.save()
                messages.error(request, f"Network Error: {str(e)}")

            return redirect("dstv")
    else:
        form = TVPurchaseForm(provider="GOTV")

    return render(request, "tv/gotv.html", {
        "form": form,
        "profile": profile,
        "beneficiaries": beneficiaries
    })







#================ STARTIME ======================#

@login_required
def STARTIME(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    beneficiaries = Beneficiary.objects.filter(user=request.user, service_type="STARTIMES")

    if request.method == "POST":
        form = TVPurchaseForm(request.POST, provider="STARTIMES")
        if form.is_valid():
            smartcard = form.cleaned_data["smartcard_number"]
            plan = form.cleaned_data["plan"]
            password = form.cleaned_data["password"]

            if not request.user.check_password(password):
                messages.error(request, "Incorrect wallet password.")
                return render(request, "tv/startime.html", {
                    "form": form,
                    "profile": profile,
                    "beneficiaries": beneficiaries
                })

            if profile.wallet_balance < plan.amount:
                messages.error(request, "Insufficient wallet balance.")
                return render(request, "tv/startime.html", {
                    "form": form,
                    "profile": profile,
                    "beneficiaries": beneficiaries
                })

            # Deduct balance
            profile.wallet_balance -= plan.amount
            profile.save()

            reference = str(uuid.uuid4())
            transaction = Transaction.objects.create(
                user=request.user,
                provider="STARTIMES",
                phone=smartcard,
                cashback=0,
                amount=plan.amount,
                gross_amount=plan.amount,
                reference=reference,
                status="Pending"
            )

            payload = {
                "request_id": reference,
                "serviceID": "startimes",
                "billersCode": smartcard,
                "variation_code": plan.plan_code,
                "amount": float(plan.amount),
                "phone": profile.phone,
                "subscription_type": "change"
            }
            headers = {
                "api-key": settings.VTPASS_APIKEY,
                "secret-key": settings.VTPASS_SECRET_KEY,
            }

            try:
                response = requests.post(f"{settings.VTPASS_BASE_URL}/pay", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

                if data.get("code") == "000":
                    transaction.status = "Success"
                    transaction.save()
                    messages.success(request, f"{plan.plan_name} activated successfully for {smartcard}!")
                else:
                    transaction.status = "Failed"
                    transaction.save()
                    profile.wallet_balance += plan.amount
                    profile.save()
                    messages.error(request, f"Purchase failed: {data.get('response_description')}")
            except requests.exceptions.RequestException as e:
                transaction.status = "Failed"
                transaction.save()
                profile.wallet_balance += plan.amount
                profile.save()
                messages.error(request, f"Network Error: {str(e)}")

            return redirect("startime")
    else:
        form = TVPurchaseForm(provider="STARTIMES")

    return render(request, "tv/startime.html", {
        "form": form,
        "profile": profile,
        "beneficiaries": beneficiaries
    })


#======================= ELECTRICITY =======================@

#----------------------- VERIFY METER -----------------------@
import requests
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required

@login_required
def verify_meter(request):
    """
    Universal verification for all electricity providers (prepaid/postpaid)
    """
    meter_number = request.GET.get("meter_number")
    disco = request.GET.get("disco")   # e.g. "ikedc", "aedc"
    meter_type = request.GET.get("meter_type")  # "prepaid" or "postpaid"

    if not meter_number or not disco or not meter_type:
        return JsonResponse({"success": False, "message": "Missing parameters."})

    # VTPass serviceID format example: "ikedc-prepaid" or "aedc-postpaid"
    service_id = f"{disco.lower()}"

    payload = {
        "serviceID": service_id,
        "billersCode": meter_number,
        "type": f"{meter_type.lower()}"
    }

    headers = {
        "api-key": settings.VTPASS_API_KEY,
        "secret-key": settings.VTPASS_SECRET_KEY,
    }

    try:
        response = requests.post(
            f"{settings.VTPASS_BASE_URL}/merchant-verify",
            json=payload,
            headers=headers,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        if data.get("code") == "000":
            content = data.get("content", {})
            return JsonResponse({
                "status": "success",
                "customer_name": content.get("Customer_Name", "Unknown"),
                "address": content.get("Address", "N/A"),
                "meter_number": meter_number,
                "disco": disco.upper(),
                "meter_type": meter_type.capitalize()
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": data.get("response_description", "Verification failed.")
            })

    except requests.RequestException as e:
        return JsonResponse({"success": False, "message": str(e)})

#------------------- IKEDC PREPAID -----------------------@
import uuid
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import transaction as db_transaction
from decimal import Decimal
from register.models import UserProfile
from base.models import Transaction
from .forms import ElectricityForm

DISCO_MAP = {
    "IKEDC": "ikeja-electric",
}

@login_required
def IKEDC(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ElectricityForm(request.POST)
        if form.is_valid():
            meter_type = form.cleaned_data["meter_type"]
            meter_number = form.cleaned_data["meter_number"].strip()
            amount = form.cleaned_data["amount"]
            password = form.cleaned_data["password"]

            # Wallet password check
            if not request.user.check_password(password):
                messages.error(request, "Incorrect wallet password.")
                return redirect("ikedc")


            cashback = (amount * Decimal("0.02")).quantize(Decimal("0.01"))

            final_amount = amount - cashback

            if profile.wallet_balance < amount:
                messages.error(request, "Insufficient wallet balance.")
                return redirect("ikedc")

            reference = str(uuid.uuid4())

            with db_transaction.atomic():
                profile.wallet_balance -= amount
                profile.save()

                transaction_record = Transaction.objects.create(
                    user=request.user,
                    provider="IKEDC",
                    meter_type=meter_type,
                    meter_number=meter_number,
                    gross_amount=amount,
                    amount=amount,
                    cashback=cashback,
                    token="",
                    reference=reference,
                    status="Pending"
                )

                payload = {
                    "request_id": reference,
                    "serviceID": DISCO_MAP["IKEDC"],
                    "billersCode": meter_number,
                    "variation_code": meter_type,
                    "amount": float(amount),
                    "phone": profile.phone
                }
                headers = {
                    "api-key": settings.VTPASS_APIKEY,
                    "secret-key": settings.VTPASS_SECRET_KEY
                }

                try:
                    response = requests.post(f"{settings.VTPASS_BASE_URL}/pay",
                                             json=payload, headers=headers, timeout=20)
                    response.raise_for_status()
                    data = response.json()

                    if data.get("code") == "000":
                        transaction_record.status = "Success"
                        transaction_record.save()

                        token = data.get("content", {}).get("token")
                        transaction.token = token
                        transaction.save()

                        profile.wallet_balance += cashback
                        profile.save()

                        messages.success(
                            request,
                            f"✅ Electricity {meter_type} token purchased for {meter_number}. Cashback ₦{cashback:.2f} applied!"
                        )
                    else:
                        transaction_record.status = "Failed"
                        transaction_record.save()

                        profile.wallet_balance += final_amount
                        profile.save()

                        messages.error(request,
                                       f"❌ Purchase failed: {data.get('response_description') or 'Unknown error'}")

                except requests.exceptions.RequestException as e:
                    transaction_record.status = "Failed"
                    transaction_record.save()

                    profile.wallet_balance += final_amount
                    profile.save()

                    messages.error(request, f"⚠️ Network Error: {str(e)}")

            return redirect("ikedc")

    else:
        form = ElectricityForm()

    return render(request, "electricity/ikedc_prepaid.html", {
        "form": form,
        "profile": profile
    })



#===========================================================#

#================ EKEDC VIEWS ===============================#
import uuid
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import transaction as db_transaction
from decimal import Decimal
from register.models import UserProfile
from base.models import Transaction
from .forms import ElectricityForm

DISCO_MAP = {
    "EKEDC": "eko-electric",
}

@login_required
def EKEDC(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ElectricityForm(request.POST)
        if form.is_valid():
            meter_type = form.cleaned_data["meter_type"]
            meter_number = form.cleaned_data["meter_number"].strip()
            amount = form.cleaned_data["amount"]
            password = form.cleaned_data["password"]

            # Wallet password check
            if not request.user.check_password(password):
                messages.error(request, "Incorrect wallet password.")
                return redirect("ekedc")


            cashback = (amount * Decimal("0.02")).quantize(Decimal("0.01"))

            if profile.wallet_balance < amount:
                messages.error(request, "Insufficient wallet balance.")
                return redirect("ekedc")

            reference = str(uuid.uuid4())

            with db_transaction.atomic():
                profile.wallet_balance -= amount
                profile.save()

                transaction_record = Transaction.objects.create(
                    user=request.user,
                    provider="EKEDC",
                    meter_type=meter_type,
                    meter_number=meter_number,
                    gross_amount=amount,
                    amount=amount,
                    cashback=cashback,
                    token="",
                    reference=reference,
                    status="Pending"
                )

                payload = {
                    "request_id": reference,
                    "serviceID": DISCO_MAP["EKEDC"],
                    "billersCode": meter_number,
                    "variation_code": meter_type,
                    "amount": float(amount),
                    "phone": profile.phone
                }
                headers = {
                    "api-key": settings.VTPASS_APIKEY,
                    "secret-key": settings.VTPASS_SECRET_KEY
                }

                try:
                    response = requests.post(f"{settings.VTPASS_BASE_URL}/pay",
                                             json=payload, headers=headers, timeout=20)
                    response.raise_for_status()
                    data = response.json()

                    if data.get("code") == "000":
                        transaction_record.status = "Success"
                        transaction_record.save()

                        token = data.get("content", {}).get("token")
                        transaction.token = token
                        transaction.save()

                        profile.wallet_balance += cashback
                        profile.save()

                        messages.success(
                            request,
                            f"✅ Electricity {meter_type} token purchased for {meter_number}. Cashback ₦{cashback:.2f} applied!"
                        )
                    else:
                        transaction_record.status = "Failed"
                        transaction_record.save()

                        profile.wallet_balance += amount
                        profile.save()

                        messages.error(request,
                                       f"❌ Purchase failed: {data.get('response_description') or 'Unknown error'}")

                except requests.exceptions.RequestException as e:
                    transaction_record.status = "Failed"
                    transaction_record.save()

                    profile.wallet_balance += final_amount
                    profile.save()

                    messages.error(request, f"⚠️ Network Error: {str(e)}")

            return redirect("ekedc")

    else:
        form = ElectricityForm()

    return render(request, "electricity/ekedc.html", {
        "form": form,
        "profile": profile
    })

#=============================================================@

#================ AEDC VIEWS ===============================#
import uuid
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import transaction as db_transaction
from decimal import Decimal
from register.models import UserProfile
from base.models import Transaction
from .forms import ElectricityForm

DISCO_MAP = {
    "AEDC": "abuja-electric",
}

@login_required
def AEDC(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ElectricityForm(request.POST)
        if form.is_valid():
            meter_type = form.cleaned_data["meter_type"]
            meter_number = form.cleaned_data["meter_number"].strip()
            amount = form.cleaned_data["amount"]
            password = form.cleaned_data["password"]

            # Wallet password check
            if not request.user.check_password(password):
                messages.error(request, "Incorrect wallet password.")
                return redirect("aedc")


            cashback = (amount * Decimal("0.02")).quantize(Decimal("0.01"))

            if profile.wallet_balance < amount:
                messages.error(request, "Insufficient wallet balance.")
                return redirect("aedc")

            reference = str(uuid.uuid4())

            with db_transaction.atomic():
                profile.wallet_balance -= amount
                profile.save()

                transaction_record = Transaction.objects.create(
                    user=request.user,
                    provider="AEDC",
                    meter_type=meter_type,
                    meter_number=meter_number,
                    gross_amount=amount,
                    amount=amount,
                    cashback=cashback,
                    token="",
                    reference=reference,
                    status="Pending"
                )

                payload = {
                    "request_id": reference,
                    "serviceID": "abuja-electric",
                    "billersCode": meter_number,
                    "variation_code": meter_type,
                    "amount": float(amount),
                    "phone": profile.phone
                }
                headers = {
                    "api-key": settings.VTPASS_APIKEY,
                    "secret-key": settings.VTPASS_SECRET_KEY
                }

                try:
                    response = requests.post(f"{settings.VTPASS_BASE_URL}/pay",
                                             json=payload, headers=headers, timeout=20)
                    response.raise_for_status()
                    data = response.json()

                    if data.get("code") == "000":
                        transaction_record.status = "Success"
                        transaction_record.save()

                        token = data.get("content", {}).get("token")
                        transaction.token = token
                        transaction.save()

                        profile.wallet_balance += cashback
                        profile.save()

                        messages.success(
                            request,
                            f"✅ Electricity {meter_type} token purchased for {meter_number}. Cashback ₦{cashback:.2f} applied!"
                        )
                    else:
                        transaction_record.status = "Failed"
                        transaction_record.save()

                        profile.wallet_balance += amount
                        profile.save()

                        messages.error(request,
                                       f"❌ Purchase failed: {data.get('response_description') or 'Unknown error'}")

                except requests.exceptions.RequestException as e:
                    transaction_record.status = "Failed"
                    transaction_record.save()

                    profile.wallet_balance += amount
                    profile.save()

                    messages.error(request, f"⚠️ Network Error: {str(e)}")

            return redirect("aedc")

    else:
        form = ElectricityForm()

    return render(request, "electricity/aedc.html", {
        "form": form,
        "profile": profile
    })


#============================================================@

#================ KADUNA VIEWS ===============================#
import uuid
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import transaction as db_transaction
from decimal import Decimal
from register.models import UserProfile
from base.models import Transaction
from .forms import ElectricityForm

DISCO_MAP = {
    "KADUNA": "kaduna-electric",
}

@login_required
def KADUNA(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ElectricityForm(request.POST)
        if form.is_valid():
            meter_type = form.cleaned_data["meter_type"]
            meter_number = form.cleaned_data["meter_number"].strip()
            amount = form.cleaned_data["amount"]
            password = form.cleaned_data["password"]

            # Wallet password check
            if not request.user.check_password(password):
                messages.error(request, "Incorrect wallet password.")
                return redirect("kaduna")


            cashback = (amount * Decimal("0.02")).quantize(Decimal("0.01"))

            if profile.wallet_balance < amount:
                messages.error(request, "Insufficient wallet balance.")
                return redirect("kaduna")

            reference = str(uuid.uuid4())

            with db_transaction.atomic():
                profile.wallet_balance -= amount
                profile.save()

                transaction_record = Transaction.objects.create(
                    user=request.user,
                    provider="KADUNA",
                    meter_type=meter_type,
                    meter_number=meter_number,
                    gross_amount=amount,
                    amount=amount,
                    cashback=cashback,
                    token="",
                    reference=reference,
                    status="Pending"
                )

                payload = {
                    "request_id": reference,
                    "serviceID": "kaduna-electric",
                    "billersCode": meter_number,
                    "variation_code": meter_type,
                    "amount": float(amount),
                    "phone": profile.phone
                }
                headers = {
                    "api-key": settings.VTPASS_APIKEY,
                    "secret-key": settings.VTPASS_SECRET_KEY
                }

                try:
                    response = requests.post(f"{settings.VTPASS_BASE_URL}/pay",
                                             json=payload, headers=headers, timeout=20)
                    response.raise_for_status()
                    data = response.json()

                    if data.get("code") == "000":
                        transaction_record.status = "Success"
                        transaction_record.save()

                        token = data.get("content", {}).get("token")
                        transaction.token = token
                        transaction.save()

                        profile.wallet_balance += cashback
                        profile.save()

                        messages.success(
                            request,
                            f"✅ Electricity {meter_type} token purchased for {meter_number}. Cashback ₦{cashback:.2f} applied!"
                        )
                    else:
                        transaction_record.status = "Failed"
                        transaction_record.save()

                        profile.wallet_balance += amount
                        profile.save()

                        messages.error(request,
                                       f"❌ Purchase failed: {data.get('response_description') or 'Unknown error'}")

                except requests.exceptions.RequestException as e:
                    transaction_record.status = "Failed"
                    transaction_record.save()

                    profile.wallet_balance += amount
                    profile.save()

                    messages.error(request, f"⚠️ Network Error:")

            return redirect("kaduna")

    else:
        form = ElectricityForm()

    return render(request, "electricity/kaduna.html", {
        "form": form,
        "profile": profile
    })

#=============================================================#

#================ IBEDC VIEWS ===============================#
import uuid
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import transaction as db_transaction
from decimal import Decimal
from register.models import UserProfile
from base.models import Transaction
from .forms import ElectricityForm

DISCO_MAP = {
    "IBEDC": "ibadan-electric",
}

@login_required
def IBEDC(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ElectricityForm(request.POST)
        if form.is_valid():
            meter_type = form.cleaned_data["meter_type"]
            meter_number = form.cleaned_data["meter_number"].strip()
            amount = form.cleaned_data["amount"]
            password = form.cleaned_data["password"]

            # Wallet password check
            if not request.user.check_password(password):
                messages.error(request, "Incorrect wallet password.")
                return redirect("ibedc")


            cashback = (amount * Decimal("0.02")).quantize(Decimal("0.01"))

            if profile.wallet_balance < amount:
                messages.error(request, "Insufficient wallet balance.")
                return redirect("ibedc")

            reference = str(uuid.uuid4())

            with db_transaction.atomic():
                profile.wallet_balance -= amount
                profile.save()

                transaction_record = Transaction.objects.create(
                    user=request.user,
                    provider="IBEDC",
                    meter_type=meter_type,
                    meter_number=meter_number,
                    gross_amount=amount,
                    amount=amount,
                    cashback=cashback,
                    reference=reference,
                    token="",
                    status="Pending"
                )

                payload = {
                    "request_id": reference,
                    "serviceID": "ibadan-electric",
                    "billersCode": meter_number,
                    "variation_code": meter_type,
                    "amount": float(amount),
                    "phone": profile.phone
                }
                headers = {
                    "api-key": settings.VTPASS_APIKEY,
                    "secret-key": settings.VTPASS_SECRET_KEY
                }

                try:
                    response = requests.post(f"{settings.VTPASS_BASE_URL}/pay",
                                             json=payload, headers=headers, timeout=20)
                    response.raise_for_status()
                    data = response.json()

                    if data.get("code") == "000":
                        transaction_record.status = "Success"
                        transaction_record.save()

                        token = data.get("content", {}).get("token")
                        transaction.token = token
                        transaction.save()

                        profile.wallet_balance += cashback
                        profile.save()

                        messages.success(
                            request,
                            f"✅ Electricity {meter_type} token purchased for {meter_number}. Cashback ₦{cashback:.2f} applied!"
                        )
                    else:
                        transaction_record.status = "Failed"
                        transaction_record.save()

                        profile.wallet_balance += amount
                        profile.save()

                        messages.error(request,
                                       f"❌ Purchase failed: {data.get('response_description') or 'Unknown error'}")

                except requests.exceptions.RequestException as e:
                    transaction_record.status = "Failed"
                    transaction_record.save()

                    profile.wallet_balance += amount
                    profile.save()

                    messages.error(request, f"⚠️ Network Error:")

            return redirect("ibedc")

    else:
        form = ElectricityForm()

    return render(request, "electricity/ibedc.html", {
        "form": form,
        "profile": profile
    })

#=============================================================#

#================ JOS VIEWS ===============================#
import uuid
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db import transaction as db_transaction
from decimal import Decimal
from register.models import UserProfile
from base.models import Transaction
from .forms import ElectricityForm

DISCO_MAP = {
    "JOS": "jos-electric",
}

@login_required
def JOS(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ElectricityForm(request.POST)
        if form.is_valid():
            meter_type = form.cleaned_data["meter_type"]
            meter_number = form.cleaned_data["meter_number"].strip()
            amount = form.cleaned_data["amount"]
            password = form.cleaned_data["password"]

            # Wallet password check
            if not request.user.check_password(password):
                messages.error(request, "Incorrect wallet password.")
                return redirect("jos")


            cashback = (amount * Decimal("0.02")).quantize(Decimal("0.01"))

            if profile.wallet_balance < amount:
                messages.error(request, "Insufficient wallet balance.")
                return redirect("jos")

            reference = str(uuid.uuid4())

            with db_transaction.atomic():
                profile.wallet_balance -= amount
                profile.save()

                transaction_record = Transaction.objects.create(
                    user=request.user,
                    provider="JOS",
                    meter_type=meter_type,
                    meter_number=meter_number,
                    gross_amount=amount,
                    amount=amount,
                    cashback=cashback,
                    token="",
                    reference=reference,
                    status="Pending"
                )

                payload = {
                    "request_id": reference,
                    "serviceID": DISCO_MAP["JOS"],
                    "billersCode": meter_number,
                    "variation_code": meter_type,
                    "amount": float(amount),
                    "phone": profile.phone
                }
                headers = {
                    "api-key": settings.VTPASS_APIKEY,
                    "secret-key": settings.VTPASS_SECRET_KEY
                }

                try:
                    response = requests.post(f"{settings.VTPASS_BASE_URL}/pay",
                                             json=payload, headers=headers, timeout=20)
                    response.raise_for_status()
                    data = response.json()

                    if data.get("code") == "000":
                        transaction_record.status = "Success"
                        transaction_record.save()

                        token = data.get("content", {}).get("token")
                        transaction.token = token
                        transaction.save()

                        profile.wallet_balance += cashback
                        profile.save()

                        messages.success(
                            request,
                            f"✅ Electricity {meter_type} token purchased for {meter_number}. Cashback ₦{cashback:.2f} applied!"
                        )
                    else:
                        transaction_record.status = "Failed"
                        transaction_record.save()

                        profile.wallet_balance += amount
                        profile.save()

                        messages.error(request,
                                       f"❌ Purchase failed: {data.get('response_description') or 'Unknown error'}")

                except requests.exceptions.RequestException as e:
                    transaction_record.status = "Failed"
                    transaction_record.save()

                    profile.wallet_balance += amount
                    profile.save()

                    messages.error(request, f"⚠️ Network Error:")

            return redirect("jos")

    else:
        form = ElectricityForm()

    return render(request, "electricity/jos.html", {
        "form": form,
        "profile": profile
    })

#=============================================================#