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
from datetime import datetime

logger = logging.getLogger(__name__)
current_time = datetime.now().strftime('%Y%m%d%H%M') + "ab"
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
    profile = request.user
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
            reference = f"{current_time}" + secrets.token_hex(8)
            # reference = str(uuid.uuid4())  # unique transaction ID
            transaction = Transaction.objects.create(
                user=request.user,
                provider="MTN-AIRTIME",
                phone=phone,
                amount=amount,
                gross_amount=amount,
                cashback=0,
                reference=reference,
                status="pending",
                initial_amount=(profile.wallet_balance + amount),
                final_amount=(profile.wallet_balance)
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
                    profile.wallet_balance += amount
                    profile.save()

                    transaction.status = "failed"
                    transaction.final_amount = profile.wallet_balance
                    transaction.save()
                    messages.error(request, f"Airtime purchase failed: {data.get('response_description')}")

            except requests.exceptions.RequestException as e:
                # Refund wallet
                profile.wallet_balance += amount
                profile.save()
                transaction.status = "failed"
                transaction.final_amount=profile.wallet_balance
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
        # "beneficiaries": beneficiaries
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
def gloAirtime(request):
    cashback_percent = Decimal("2")
    profile = request.user
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
            reference = f"{current_time}" + secrets.token_hex(8)
            transaction = Transaction.objects.create(
                user=request.user,
                provider="GLO-AIRTIME",
                phone=phone,
                amount=amount,
                gross_amount=amount,
                cashback=0,
                reference=reference,
                status="pending",
                initial_amount=(profile.wallet_balance + amount),
                final_amount=(profile.wallet_balance)
            )

            # Call VTpass API
            payload = {
                "serviceID": "glo",
                "amount": float(amount),
                "phone": phone,
                "request_id": reference,
            }

            headers = {
                "api-key":f"{settings.VTPASS_APIKEY}",
                "secret-key": f"{settings.VTPASS_SECRET_KEY}"
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
                    transaction.status = "success"
                    transaction.save()
                    messages.success(request, f"GLO Airtime {amount} NGN sent to {phone}. Cashback ₦{cashback} credited.")
                else:
                    
                    # Refund wallet
                    profile.wallet_balance += amount
                    profile.save()
                    transaction.status = "failed"
                    transaction.final_amount=profile.wallet_balance
                    transaction.save()
                
                    messages.error(request, f"Airtime purchase failed: {data.get('response_description')}")

            except requests.exceptions.RequestException as e:
                # Refund wallet
                profile.wallet_balance += amount
                profile.save()
                transaction.status = "failed"
                transaction.final_amount = profile.wallet_balance
                transaction.save()
                messages.error(request, f"Network Error: {str(e)}")

            return redirect("glo_airtime")
    else:
        form = AirtimeForm()

    context = {
        "form": form,
        "profile": profile,
        # "beneficiaries": beneficiaries
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
    cashback_percent = Decimal("2")
    profile = request.user
    beneficiaries = Beneficiary.objects.filter(user=request.user, provider="Airtel")

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

            # Validate network: GLO prefixes
            # glo_prefixes = ["0805","0807","0811","0815","0817","0818","0905","0907","0915"]
            # if not any(phone.startswith(p) for p in glo_prefixes):
                # messages.error(request, "Phone number does not match GLO network.")
                # return render(request, "airtime/glo_airtime.html", {"form": form})

            # Check wallet balance
            if profile.wallet_balance < amount:
                messages.error(request, "Insufficient wallet balance.")
                return render(request, "airtime/airtel_airtime.html", {"form": form})

            # Deduct from wallet
            profile.wallet_balance -= amount
            profile.save()

            # Create transaction
            reference = f"{current_time}" + secrets.token_hex(8)
            transaction = Transaction.objects.create(
                user=request.user,
                provider="AIRTEL-AIRTIME",
                phone=phone,
                amount=amount,
                gross_amount=amount,
                cashback=0,
                reference=reference,
                status="pending",
                initial_amount=(profile.wallet_balance + amount),
                final_amount=(profile.wallet_balance)
            )

            # Call VTpass API
            payload = {
                "serviceID": "airtel",
                "amount": float(amount),
                "phone": phone,
                "request_id": reference,
            }

            headers = {
                "api-key":f"{settings.VTPASS_APIKEY}",
                "secret-key": f"{settings.VTPASS_SECRET_KEY}"
            }

            try:
                response = requests.post(f"{settings.VTPASS_BASE_URL}/pay", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                logger.info(f"AIRTEL airtime response: {data}")

                if data.get("code") == "000":
                    # Calculate cashback
                    cashback = round(amount * cashback_percent / 100, 2)
                    profile.wallet_balance += cashback
                    profile.save()

                    transaction.cashback = cashback
                    transaction.status = "success"
                    transaction.save()
                    messages.success(request, f"AIRTEL Airtime {amount} NGN sent to {phone}. Cashback ₦{cashback} credited.")
                else:
                    
                    # Refund wallet
                    profile.wallet_balance += amount
                    profile.save()
                    transaction.status = "failed"
                    transaction.final_amount=profile.wallet_balance
                    transaction.save()
                
                    messages.error(request, f"Airtime purchase failed: {data.get('response_description')}")

            except requests.exceptions.RequestException as e:
                # Refund wallet
                profile.wallet_balance += amount
                profile.save()
                transaction.status = "failed"
                transaction.final_amount = profile.wallet_balance
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
    cashback_percent = Decimal("2")
    profile = request.user
    beneficiaries = Beneficiary.objects.filter(user=request.user, provider="9Mobile")

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

            # Validate network: GLO prefixes
            # glo_prefixes = ["0805","0807","0811","0815","0817","0818","0905","0907","0915"]
            # if not any(phone.startswith(p) for p in glo_prefixes):
                # messages.error(request, "Phone number does not match GLO network.")
                # return render(request, "airtime/glo_airtime.html", {"form": form})

            # Check wallet balance
            if profile.wallet_balance < amount:
                messages.error(request, "Insufficient wallet balance.")
                return render(request, "airtime/ninemobile_airtime.html", {"form": form})

            # Deduct from wallet
            profile.wallet_balance -= amount
            profile.save()

            # Create transaction
            reference = f"{current_time}" + secrets.token_hex(8)
            transaction = Transaction.objects.create(
                user=request.user,
                provider="ETISALAT-AIRTIME",
                phone=phone,
                amount=amount,
                gross_amount=amount,
                cashback=0,
                reference=reference,
                status="pending",
                initial_amount=(profile.wallet_balance + amount),
                final_amount=(profile.wallet_balance)
            )

            # Call VTpass API
            payload = {
                "serviceID": "etisalat",
                "amount": float(amount),
                "phone": phone,
                "request_id": reference,
            }

            headers = {
                "api-key":f"{settings.VTPASS_APIKEY}",
                "secret-key": f"{settings.VTPASS_SECRET_KEY}"
            }

            try:
                response = requests.post(f"{settings.VTPASS_BASE_URL}/pay", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                logger.info(f"ETISALAT airtime response: {data}")

                if data.get("code") == "000":
                    # Calculate cashback
                    cashback = round(amount * cashback_percent / 100, 2)
                    profile.wallet_balance += cashback
                    profile.save()

                    transaction.cashback = cashback
                    transaction.status = "success"
                    transaction.save()
                    messages.success(request, f"ETISALAT Airtime {amount} NGN sent to {phone}. Cashback ₦{cashback} credited.")
                else:
                    
                    # Refund wallet
                    profile.wallet_balance += amount
                    profile.save()
                    transaction.status = "failed"
                    transaction.final_amount=profile.wallet_balance
                    transaction.save()
                
                    messages.error(request, f"Airtime purchase failed: {data.get('response_description')}")

            except requests.exceptions.RequestException as e:
                # Refund wallet
                profile.wallet_balance += amount
                profile.save()
                transaction.status = "failed"
                transaction.final_amount = profile.wallet_balance
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
    profile = request.user
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
            reference = f"{current_time}" + secrets.token_hex(8)
            transaction = Transaction.objects.create(
                user=request.user,
                provider="MTN-DATA",
                phone=phone,
                cashback = 0,
                amount=plan.amount,
                gross_amount=plan.amount,
                reference=reference,
                status="Pending",
                initial_amount=(profile.wallet_balance + plan.amount),
                final_amount=(profile.wallet_balance)
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
                    transaction.final_amount=profile.wallet_balance
                    transaction.save()
                    messages.error(request, f"Purchase failed: {data.get('response_description')}")

            except requests.exceptions.RequestException as e:
                transaction.status = "Failed"
                transaction.save()
                profile.wallet_balance += plan.amount
                profile.save()

                transaction.final_amount=profile.wallet_balance
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
    profile = request.user
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
            reference = f"{current_time}" + secrets.token_hex(8)
            transaction = Transaction.objects.create(
                user=request.user,
                provider="GLO-DATA",
                phone=phone,
                cashback = 0,
                amount=plan.amount,
                gross_amount=plan.amount,
                reference=reference,
                status="Pending",
                initial_amount=(profile.wallet_balance + plan.amount),
                final_amount=(profile.wallet_balance)
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

                    transaction.final_amount = profile.wallet_balance
                    transaction.save()
                    messages.error(request, f"Purchase failed: {data.get('response_description')}")

            except requests.exceptions.RequestException as e:
                transaction.status = "Failed"
                transaction.save()
                profile.wallet_balance += plan.amount
                profile.save()

                transaction.final_amount = profile.wallet_balance
                transaction.save()
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
    profile = request.user
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
            reference = f"{current_time}" + secrets.token_hex(8)
            transaction = Transaction.objects.create(
                user=request.user,
                provider="AIRTEL-DATA",
                phone=phone,
                cashback = 0,
                amount=plan.amount,
                gross_amount=plan.amount,
                reference=reference,
                status="Pending",
                initial_amount=(profile.wallet_balance + plan.amount),
                final_amount=(profile.wallet_balance)
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

                    transaction.final_amount = profile.wallet_balance
                    transaction.save()
                    messages.error(request, f"Purchase failed: {data.get('response_description')}")

            except requests.exceptions.RequestException as e:
                transaction.status = "Failed"
                transaction.save()
                profile.wallet_balance += plan.amount
                profile.save()

                transaction.final_amount = profile.wallet_balance
                transaction.save()
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
    profile = request.user
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
            reference = f"{current_time}" + secrets.token_hex(8)
            transaction = Transaction.objects.create(
                user=request.user,
                provider="ETISALAT-DATA",
                phone=phone,
                cashback = 0,
                amount=plan.amount,
                gross_amount=plan.amount,
                reference=reference,
                status="Pending",
                initial_amount=(profile.wallet_balance + plan.amount),
                final_amount=(profile.wallet_balance)
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
                    transaction.status = "failed"
                    transaction.save()
                    # Refund wallet
                    profile.wallet_balance += plan.amount
                    profile.save()

                    transaction.final_amount = profile.wallet_balance
                    transaction.save()
                    messages.error(request, f"Purchase failed: {data.get('response_description')}")

            except requests.exceptions.RequestException as e:
                transaction.status = "failed"
                transaction.save()
                profile.wallet_balance += plan.amount
                profile.save()

                transaction.final_amount = profile.wallet_balance
                transaction.save()
                messages.error(request, f"Network Error: {str(e)}")

            return redirect("ninemobile_data")
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
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import requests

@csrf_exempt
@login_required
def verify_iuc(request):
    if request.method == "POST":
        provider = request.POST.get("provider")  # dstv, gotv, startimes
        smartcard_number = request.POST.get("smartcard_number")

        if not provider or not smartcard_number:
            return JsonResponse({"success": False, "message": "Provider and smartcard number are required."})

        url = f"{settings.VTPASS_BASE_URL}/merchant-verify"
        headers = {
            "api-key": settings.VTPASS_APIKEY,
            "secret-key": settings.VTPASS_SECRET_KEY,
            # "public-key": settings.VTPASS_PUBLIC_KEY,
            "Content-Type": "application/json",
        }
        payload = {
            "billersCode": smartcard_number,
            "serviceID": provider,
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            data = response.json()
            print("VTPASS RESPONSE:", data)

            if data.get("code") == "000":
                customer_name = data["content"].get("Customer_Name", "Unknown")
            # print("VTPASS RESPONSE:", data)
                return JsonResponse({
                    "success": True,
                    "customer_name": customer_name,
                    "raw": data
                })
            else:
                return JsonResponse({
                    "success": False,
                    "message": data.get("response_description", "Verification failed"),
                    "raw": data
                })
        
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})

    
    return JsonResponse({"success": False, "message": "Invalid request method"})

#================ DSTV ======================#

@login_required
def DSTV(request):
    profile = request.user
    beneficiaries = Beneficiary.objects.filter(user=request.user, service_type="DSTV", provider="DSTV")

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

            reference = f"{current_time}" + secrets.token_hex(8)
            transaction = Transaction.objects.create(
                user=request.user,
                provider="DSTV",
                phone=smartcard,
                cashback=0,
                amount=plan.amount,
                gross_amount=plan.amount,
                reference=reference,
                status="Pending",
                initial_amount=(profile.wallet_balance + plan.amount),
                final_amount=(profile.wallet_balance)
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
                    transaction.status = "success"
                    transaction.save()
                    messages.success(request, f"{plan.plan_name} activated successfully for {smartcard}!")
                else:
                    transaction.status = "failed"
                    transaction.save()
                    profile.wallet_balance += plan.amount
                    profile.save()

                    transaction.final_amount = profile.wallet_balance
                    profile.save()
                    messages.error(request, f"Purchase failed: {data.get('response_description')}")
            except requests.exceptions.RequestException as e:
                transaction.status = "Failed"
                transaction.save()
                profile.wallet_balance += plan.amount
                profile.save()

                transaction.final_amount = profile.wallet_balance
                transaction.save()
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
    profile = request.user
    beneficiaries = Beneficiary.objects.filter(user=request.user, service_type="GOTV", provider="GOTV")

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

            reference = f"{current_time}" + secrets.token_hex(8)
            transaction = Transaction.objects.create(
                user=request.user,
                provider="GOTV",
                phone=smartcard,
                cashback=0,
                amount=plan.amount,
                gross_amount=plan.amount,
                reference=reference,
                status="Pending",
                initial_amount=(profile.wallet_balance + plan.amount),
                final_amount=(profile.wallet_balance)
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

                    transaction.final_amount = profile.wallet_balance
                    transaction.save()
                    messages.error(request, f"Purchase failed: {data.get('response_description')}")
            except requests.exceptions.RequestException as e:
                transaction.status = "Failed"
                transaction.save()
                profile.wallet_balance += plan.amount
                profile.save()

                transaction.final_amount = profile.wallet_balance
                transaction.save()
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
    profile = request.user
    beneficiaries = Beneficiary.objects.filter(user=request.user, service_type="STARTIMES", provider="STARTIMES")

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

            reference = f"{current_time}" + secrets.token_hex(8)
            transaction = Transaction.objects.create(
                user=request.user,
                provider="STARTIMES",
                phone=smartcard,
                cashback=0,
                amount=plan.amount,
                gross_amount=plan.amount,
                reference=reference,
                status="Pending",
                initial_amount=(profile.wallet_balance + plan.amount),
                final_amount=(profile.wallet_balance)
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

                    transaction.final_amount = profile.wallet_balance
                    transaction.save()
                    messages.error(request, f"Purchase failed: {data.get('response_description')}")
            except requests.exceptions.RequestException as e:
                transaction.status = "Failed"
                transaction.save()
                profile.wallet_balance += plan.amount
                profile.save()

                transaction.final_amount = profile.wallet_balance
                transaction.save()
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

# @login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@login_required
def verify_meter(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method"}, status=405)

    provider = request.POST.get("provider")  # e.g. ikeja-electric, eko-electric
    meter_number = request.POST.get("meter_number")
    meter_type = request.POST.get("meter_type")  # prepaid or postpaid

    # Validate input
    if not provider or not meter_number or not meter_type:
        return JsonResponse({
            "success": False,
            "message": "Provider, meter number, and meter type are required."
        }, status=400)

    url = f"{settings.VTPASS_BASE_URL}/merchant-verify"
    headers = {
        "api-key": settings.VTPASS_APIKEY,
        "secret-key": settings.VTPASS_SECRET_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "billersCode": meter_number,
        "serviceID": provider,
        "type": meter_type.lower(),  # normalize prepaid/postpaid
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        print("VTPASS RESPONSE:", data)
        logger.info("VTPASS VERIFY METER RESPONSE: %s", data)

        if data.get("code") == "000":  # ✅ Successful
            customer_name = (
                data.get("content", {}).get("Customer_Name")
                or data.get("content", {}).get("customerName")
                or "Unknown"
            )
            return JsonResponse({
                "success": True,
                "customer_name": customer_name,
                "provider": provider,
                "meter_type": meter_type,
                "raw": data,
            })

        # ❌ Failed verification
        return JsonResponse({
            "success": False,
            "message": data.get("response_description", "Verification failed"),
            "raw": data,
        }, status=400)

    except requests.exceptions.Timeout:
        return JsonResponse({"success": False, "message": "Request to provider timed out."}, status=504)
    except requests.exceptions.RequestException as e:
        return JsonResponse({"success": False, "message": f"Network error: {str(e)}"}, status=502)
    except Exception as e:
        logger.error("Unexpected error verifying meter: %s", e, exc_info=True)
        return JsonResponse({"success": False, "message": "Internal server error"}, status=500)



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
    profile = request.user

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

            reference = f"{current_time}" + secrets.token_hex(8)

            with db_transaction.atomic():
                profile.wallet_balance -= amount
                profile.save()

                transaction = Transaction.objects.create(
                    user=request.user,
                    provider="IKEDC",
                    meter_type=meter_type,
                    meter_number=meter_number,
                    gross_amount=amount,
                    amount=amount,
                    cashback=cashback,
                    token="",
                    reference=reference,
                    status="Pending",
                    initial_amount=profile.wallet_balance,
                    final_amount=(profile.wallet_balance - amount)
                )

                payload = {
                    "request_id": reference,
                    "serviceID": "ikeja-electric",
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
                        transaction.status = "Success"
                        transaction.save()

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
                        transaction.status = "Failed"
                        transaction.save()

                        profile.wallet_balance += final_amount
                        profile.save()

                        transaction.final_amount = profile.wallet_balance
                        transaction.save()

                        messages.error(request,
                        f"❌ Purchase failed: {data.get('response_description') or 'Unknown error'}")

                except requests.exceptions.RequestException as e:
                    transaction.status = "Failed"
                    transaction.save()

                    profile.wallet_balance += final_amount
                    profile.save()

                    transaction.final_amount = profile.wallet_balance
                    transaction.save()
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
    profile = request.user

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

            reference = f"{current_time}" + secrets.token_hex(8)

            with db_transaction.atomic():
                profile.wallet_balance -= amount
                profile.save()

                transaction = Transaction.objects.create(
                    user=request.user,
                    provider="EKEDC",
                    meter_type=meter_type,
                    meter_number=meter_number,
                    gross_amount=amount,
                    amount=amount,
                    cashback=cashback,
                    token="",
                    reference=reference,
                    status="pending",
                    initial_amount=(profile.wallet_balance + amount),
                    final_amount=(profile.wallet_balance)
                )

                payload = {
                    "request_id": reference,
                    "serviceID": "eko-electric",
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
                        transaction.status = "success"
                        transaction.save()

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
                        transaction.status = "failed"
                        transaction.save()

                        profile.wallet_balance += amount
                        profile.save()

                        transaction.final_amount = profile.wallet_balance
                        transaction.save()
                        messages.error(request,
                        f"❌ Purchase failed: {data.get('response_description') or 'Unknown error'}")

                except requests.exceptions.RequestException as e:
                    transaction.status = "failed"
                    transaction.save()

                    profile.wallet_balance += final_amount
                    profile.save()

                    transaction.final_amount = profile.wallet_balance
                    transaction.save()
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
    profile = request.user

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

            reference = f"{current_time}" + secrets.token_hex(8)

            with db_transaction.atomic():
                profile.wallet_balance -= amount
                profile.save()

                transaction = Transaction.objects.create(
                    user=request.user,
                    provider="AEDC",
                    meter_type=meter_type,
                    meter_number=meter_number,
                    gross_amount=amount,
                    amount=amount,
                    cashback=cashback,
                    token="",
                    reference=reference,
                    status="Pending",
                    initial_amount=(profile.wallet_balance + amount),
                    final_amount=(profile.wallet_balance)
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
                        transaction.status = "Success"
                        transaction.save()

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
                        transaction.status = "Failed"
                        transaction.save()

                        profile.wallet_balance += amount
                        profile.save()

                        transaction.final_amount = profile.wallet_balance
                        transaction.save()

                        messages.error(request,
                        f"❌ Purchase failed: {data.get('response_description') or 'Unknown error'}")

                except requests.exceptions.RequestException as e:
                    transaction.status = "Failed"
                    transaction.save()

                    profile.wallet_balance += amount
                    profile.save()

                    transaction.final_amount = profile.wallet_balance
                    transaction.save()

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
    profile = request.user

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

            reference = f"{current_time}" + secrets.token_hex(8)

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
                    status="Pending",
                initial_amount=(profile.wallet_balance + amount),
                final_amount=(profile.wallet_balance)
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
                        transaction_record.token = token
                        transaction_record.save()

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

                        transaction_record.final_amount = profile.wallet_balance
                        transaction_record.save()

                        messages.error(request,
                        f"❌ Purchase failed: {data.get('response_description') or 'Unknown error'}")

                except requests.exceptions.RequestException as e:
                    transaction_record.status = "Failed"
                    transaction_record.save()

                    profile.wallet_balance += amount
                    profile.save()

                    transaction_record.final_amount = profile.wallet_balance
                    transaction_record.save()

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
    profile = request.user

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

            reference = f"{current_time}" + secrets.token_hex(8)

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
                    status="Pending",
                initial_amount=(profile.wallet_balance + amount),
                final_amount=(profile.wallet_balance)
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
                        transaction_record.token = token
                        transaction_record.save()

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

                        transaction_record.final_amount = profile.wallet_balance
                        transaction_record.save()

                        messages.error(request,
                        f"❌ Purchase failed: {data.get('response_description') or 'Unknown error'}")

                except requests.exceptions.RequestException as e:
                    transaction_record.status = "Failed"
                    transaction_record.save()

                    profile.wallet_balance += amount
                    profile.save()

                    transaction_record.final_amount = profile.wallet_balance
                    transaction_record.save()

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
    profile = request.user

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

            reference = f"{current_time}" + secrets.token_hex(8)

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
                    status="Pending",
                initial_amount=(profile.wallet_balance  + amount),
                final_amount=(profile.wallet_balance)
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
                        transaction_record.token = token
                        transaction_record.save()

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

                        transaction_record.final_amount = profile.wallet_balance
                        transaction_record.save()

                        messages.error(request,
                        f"❌ Purchase failed: {data.get('response_description') or 'Unknown error'}")

                except requests.exceptions.RequestException as e:
                    transaction_record.status = "Failed"
                    transaction_record.save()

                    profile.wallet_balance += amount
                    profile.save()

                    transaction_record.final_amount = profile.wallet_balance
                    transaction_record.save()

                    messages.error(request, f"⚠️ Network Error:")

            return redirect("jos")

    else:
        form = ElectricityForm()

    return render(request, "electricity/jos.html", {
        "form": form,
        "profile": profile
    })

#=============================================================#