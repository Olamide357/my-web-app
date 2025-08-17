from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from register.models import UserProfile
from .forms import AirtimeForm, mtnDataForm, gloDataForm, airtelDataForm, ninemobileDataForm, DSTVForm, GOTVForm, STARTIMESForm, prepaidForm, postpaidForm
from django.http import JsonResponse
import requests, uuid, json,logging
from base.models import Transaction
from django.conf import settings
from .utils import makeVTpassRequest
# from .decimal import Decimal


# Create your views here.
#=============================================================================================================================#
#========================================= AIRTIMES VIEWS ====================================================================#
#=============================================================================================================================#

#======================= MTN AIRTIME ================================#  

@login_required
def mtnAirtime(request):
    provider = request.GET.get('provider', '')
    phone = request.GET.get('phone', '')
    if request.method == 'POST':
        form = AirtimeForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            amount = form.cleaned_data['amount']
            password = form.cleaned_data['password']

            if not request.user.check_password(password):
                messages.error(request, "Incorrect Password")
                return redirect('mtn_airtime')
            
            profile = UserProfile.objects.get(user=request.user)
            if profile.wallet_balance < amount:
                messages.error(request, "Insufficient wallet balance")
                return redirect('mtn_airtime')

            request_id = str(uuid.uuid4())

            transaction = Transaction.objects.create(
                        user=request.user,
                        amount = amount,
                        phone=phone,
                        status= "pending",
                        request_id=request_id,
                    )

            url = f"{settings.SMEPLUG_BASE}/airtime/purchase"

            payload = {
            "network_id": 1,
            "amount": str(amount),
            "phone": phone,
            "request_id": request_id
        }

            headers = {
            "Authorization": f"Bearer {settings.SMEPLUG_API_KEY}",
            "Content-Type": "application/json",
        }

            try:
                response = requests.post(url, json=payload, headers=headers,timeout=30)

                if response.status_code != 200:
                    messages.error(request, f"SMEPLUG API Request failed: {response.text} ")
                    return redirect('mtn_airtime')
                data = response.json()

                if data.get('status') is True:
                    profile.wallet_balance -= amount
                    profile.save()
                    transaction.status = "success"
                    transaction.save()
                    messages.success(request, f"MTN Airtime purchase successful.\nRef: {request_id}")

                    return redirect('receipt')
                
                else:
                    messages.error(request, f"SMEplug Error: {data.get('msg') or data.get('errors')}")
                    transaction.status = "failed"
                    transaction.save()
                    return redirect('mtn_airtime')

            except requests.RequestException as e:
                messages.error(request, f"Error contacting SMEplug: {e}")
                transaction.status = "failed"
                transaction.save()
                return redirect('mtn_airtime')

    else:
        form = AirtimeForm(initial={'provider': provider, 'phone': phone})

    return render(request, 'airtime/mtn_airtime.html', {'form': form})
    
#====================== GLO AIRTIME =========================#
@login_required
def gloAirtime(request):
    provider = request.GET.get('provider', '')
    phone = request.GET.get('phone', '')
    if request.method == 'POST':
        form = AirtimeForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            amount = form.cleaned_data['amount']
            password = form.cleaned_data['password']

            if not request.user.check_password(password):
                messages.error(request, "Incorrect Password")
                return redirect('glo_airtime')
            
            profile = UserProfile.objects.get(user=request.user)
            if profile.wallet_balance < amount:
                messages.error(request, "Insufficient wallet balance")
                return redirect('glo_airtime')

            request_id = str(uuid.uuid4())

            transaction = Transaction.objects.create(
                        user=request.user,
                        amount = amount,
                        phone=phone,
                        status= "pending",
                        request_id=request_id
                    )

            url = f"{settings.SMEPLUG_BASE}/airtime/purchase"

            payload = {
            "network_id": 2,
            "amount": str(amount),
            "phone": phone,
            "request_id": request_id
        }

            headers = {
            "Authorization": f"Bearer {settings.SMEPLUG_API_KEY}",
            "Content-Type": "application/json",
        }

            try:
                response = requests.post(url, json=payload, headers=headers,timeout=30)

                if response.status_code != 200:
                    messages.error(request, f"SMEPLUG API Request failed: {response.text} ")
                    return redirect('glo_airtime')
                data = response.json()

                if data.get('status') is True:
                    profile.wallet_balance -= amount
                    profile.save()
                    messages.success(request, f"MTN Airtime purchase successful.\nRef: {request_id}")
                
                else:
                    messages.error(request, f"SMEplug Error: {data.get('msg') or data.get('errors')}")
                
                return redirect('glo_airtime')

            except requests.RequestException as e:
                messages.error(request, f"Error contacting SMEplug: {e}")
                return redirect('glo_airtime')

    else:
        form = AirtimeForm(initial={'phone': phone})

    return render(request, 'airtime/glo_airtime.html', {'provider': provider, 'form': form})
    
#================ AIRTEL AIRTIME ============================#
@login_required
def airtelAirtime(request):
    provider = request.GET.get('provider', '')
    phone = request.GET.get('phone', '')
    if request.method == 'POST':
        form = AirtimeForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            amount = form.cleaned_data['amount']
            password = form.cleaned_data['password']

            if not request.user.check_password(password):
                messages.error(request, "Incorrect Password")
                return redirect('airtel_airtime')
            
            profile = UserProfile.objects.get(user=request.user)
            if profile.wallet_balance < amount:
                messages.error(request, "Insufficient wallet balance")
                return redirect('airtel_airtime')

            request_id = str(uuid.uuid4())

            transaction = Transaction.objects.create(
                        user=request.user,
                        amount = amount,
                        phone=phone,
                        status= "pending",
                        request_id=request_id
                    )

            url = f"{settings.SMEPLUG_BASE}/airtime/purchase"

            payload = {
            "network_id": 3,
            "amount": str(amount),
            "phone": phone,
            "request_id": request_id
        }

            headers = {
            "Authorization": f"Bearer {settings.SMEPLUG_API_KEY}",
            "Content-Type": "application/json",
        }

            try:
                response = requests.post(url, json=payload, headers=headers,timeout=30)

                if response.status_code != 200:
                    messages.error(request, f"SMEPLUG API Request failed: {response.text} ")
                    return redirect('glo_airtime')
                data = response.json()

                if data.get('status') is True:
                    profile.wallet_balance -= amount
                    profile.save()
                    messages.success(request, f"Airtel Airtime purchase successful.\nRef: {request_id}")
                
                else:
                    messages.error(request, f"SMEplug Error: {data.get('msg') or data.get('errors')}")
                
                return redirect('airtel_airtime')

            except requests.RequestException as e:
                messages.error(request, f"Error contacting SMEplug: {e}")
                return redirect('airtel_airtime')

    else:
        form = AirtimeForm(initial={'provider': provider, 'phone': phone})

    return render(request, 'airtime/airtel_airtime.html', {'form': form})

#================== 9MOBILE AIRTIME ========================#
@login_required
def ninemobileAirtime(request):
    provider = request.GET.get('provider', '')
    phone = request.GET.get('phone', '')
    if request.method == 'POST':
        form = AirtimeForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            amount = form.cleaned_data['amount']
            password = form.cleaned_data['password']

            if not request.user.check_password(password):
                messages.error(request, "Incorrect Password")
                return redirect('ninemobile_airtime')
            
            profile = UserProfile.objects.get(user=request.user)
            if profile.wallet_balance < amount:
                messages.error(request, "Insufficient wallet balance")
                return redirect('ninemobile_airtime')

            request_id = str(uuid.uuid4())

            transaction = Transaction.objects.create(
                        user=request.user,
                        amount = amount,
                        phone=phone,
                        status= "pending",
                        request_id=request_id
                    )

            url = f"{settings.SMEPLUG_BASE}/airtime/purchase"

            payload = {
            "network_id": 4,
            "amount": str(amount),
            "phone": phone,
            "request_id": request_id
        }

            headers = {
            "Authorization": f"Bearer {settings.SMEPLUG_API_KEY}",
            "Content-Type": "application/json",
        }

            try:
                response = requests.post(url, json=payload, headers=headers,timeout=30)

                if response.status_code != 200:
                    messages.error(request, f"SMEPLUG API Request failed: {response.text} ")
                    return redirect('ninemobile_airtime')
                data = response.json()

                if data.get('status') is True:
                    profile.wallet_balance -= amount
                    profile.save()
                    messages.success(request, f"9Mobile Airtime purchase successful.\nRef: {request_id}")
                
                else:
                    messages.error(request, f"SMEplug Error: {data.get('msg') or data.get('errors')}")
                
                return redirect('ninemobile_airtime')

            except requests.RequestException as e:
                messages.error(request, f"Error contacting SMEplug: {e}")
                return redirect('ninemobile_airtime')

    else:
        form = AirtimeForm(initial={'provider': provider, 'phone': phone})

    return render(request, 'airtime/ninemobile_airtime.html', {'form': form})


#==============================================================================================================================#
#================================================= DATA VIEWS =================================================================#
#==============================================================================================================================#

#==================== MTN DATA ===============================#
def mtnData(request):
    
    if request.method == 'POST':
        form = mtnDataForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            plan_id = form.cleaned_data['plan']
            password = form.cleaned_data['password']
            price = form.get_mtnplan_price()

            if not request.user.check_password(password):
                messages.error(request, 'Incorrect password')
                return redirect('mtn_data')

            profile = UserProfile.objects.get(user=request.user)
            if profile.wallet_balance < price:
                messages.error(request, 'Insufficient wallet balance')
                return redirect('mtn_data')

            request_id = str(uuid.uuid4())
            
            transaction = Transaction.objects.create(
                user=request.user,
                service='data',
                provider='MTN',
                amount=price,
                phone=phone,
                status='pending',
                request_id=request_id
            )
            payload = {
                "username": f"{settings.PAYGOLD_USERNAME}",
                "password": f"{settings.PAYGOLD_PASSWORD}",
                "network_id": "mtn",
                "variation_id": plan_id,
                "phone": phone
                # "referenceId": request_id
            }
            headers = {
                "Accept": "application/json",
                "User-Agent": "Django-App/1.0"
            }
            url =f"{settings.PAYGOLD_BASE_URL}/data"
            try:
                response = requests.get(url, json=payload, timeout=30)

                # if response.status_code != 200:
                #     messages.error(request, f"API Error: {response.text}")
                #     return redirect('mtn_data')
                
                data = response.json()

                if data.get("status") == "success":
                    profile.wallet_balance -= price
                    profile.save()

                    transaction.status = 'success'
                    transaction.save()
                    messages.success(request, 'GLO Data purchase successfully!')
                    return redirect('receipt')
                
                else:
                    transaction.status = "failed"
                    transaction.save()
                    messages.error(request, f"Failed {data.get('msg') or data.get('message')}")


            except Exception as e:
                transaction.status = "failed"
                transaction.save()
                messages.error(request, f"API Connection Error: {str(e)}")
                return redirect('mtn_data')

    else:
        form = mtnDataForm()

    return render(request, 'data/mtn_data.html', {'form': form})

#==================== GLO DATA ===============================#
def gloData(request):
    
    if request.method == 'POST':
        form = gloDataForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data["phone_number"]
            plan_id = form.cleaned_data['plan']
            password = form.cleaned_data['password']
            price = form.get_gloplan_price()

            if not request.user.check_password(password):
                messages.error(request, 'Incorrect password')
                return redirect('glo_data')

            profile = UserProfile.objects.get(user=request.user)
            if profile.wallet_balance < price:
                messages.error(request, 'Insufficient wallet balance')
                return redirect('glo_data')

            request_id = str(uuid.uuid4())
            transaction = Transaction.objects.create(
                        user=request.user,
                        service='data',
                        provider='GLO',
                        amount=price,
                        phone = phone_number,
                        status='success',
                        request_id=request_id
                    )
            payload = {
                "referenceId": request_id,
                "network": "glo-cg",
                "plan": plan_id,
                "phoneNumber": phone_number,
                "purchase": "data",
            }
            headers = {
                "Authorization": f"Basic {settings.BASE64}",
                "Content-Type": "application/json"
            }
            url =f"{settings.NEARLYFREE_URL}/purchase"
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=30)

                if response.status_code != 200:
                    messages.error(request, f"API Error: {response.text}")
                    return redirect('glo_data')
                
                data = response.json()

                if data.get("status") == "successful":
                    profile.wallet_balance -= price
                    profile.save()
                    messages.success(request, 'GLO Data purchase successfully!')
                    return redirect('receipt')
                
                else:
                    messages.error(request, f"Failed {data.get('msg')}")

            except Exception as e:
                messages.error(request, f"API Error: {str(e)}")
                return redirect('glo_data')

    else:
        form = gloDataForm()

    return render(request, 'data/glo_data.html', {'form': form})


#==================== AIRTEL DATA ===============================#
def airtelData(request):
    if request.method == 'POST':
        form = airtelDataForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            plan = form.cleaned_data['plan']
            password = form.cleaned_data['password']
            if not request.user.check_password(password):
                messages.error(request, 'Incorrect password')
                return redirect('airtel_data')
            
            plan_dict = dict(airtelDataForm.DATA_CHOICES)
            plan_price = 0
            if '₦' in plan_dict[plan]:
                plan_price = int(plan_dict[plan].split('₦')[-1])

            profile = UserProfile.objects.get(user=request.user)
            if profile.wallet_balance < plan_price:
                messages.error(request, 'Insufficient wallet balance')
                return redirect('airtel_data')

            request_id = str(uuid.uuid4())
            payload = {
                "serviceID": "airtel-data",
                "variation_code": plan,
                "request_id": request_id,
                "phone": phone,
            }
            headers = {
                "api-key": "your-api-key",
                "public-key": "your-public-key",
                "Content-Type": "application/json"
            }
            try:
                response = request.post("https://vtpass.com/api/pay", json=payload, headers=headers)
                result = response.json()
                if result.get("code") == "000":
                    profile.wallet_balance -= plan_price
                    profile.save()

                    Transaction.objects.create(
                        user=request.user,
                        service='data',
                        provider='Airtel',
                        amount=plan_price,
                        phone=phone,
                        status='success',
                        request_id=request_id
                    )
                    messages.success(request, 'Airtel Data purchase successfully!')
                    return redirect('airtel_data')
                
                else:
                    messages.error(request, f"Failed {result.get('response_description')}")

            except Exception as e:
                messages.error(request, f"API Error: {str(e)}")

    else:
        form = airtelDataForm()

    return render(request, 'data/airtel_data.html', {'form': form})

#==================== 9MOBILE DATA ===============================#
def ninemobileData(request):
    if request.method == 'POST':
        form = airtelDataForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            plan = form.cleaned_data['plan']
            password = form.cleaned_data['password']
            if not request.user.check_password(password):
                messages.error(request, 'Incorrect password')
                return redirect('ninemobile_data')
            
            plan_dict = dict(ninemobileDataForm.DATA_CHOICES)
            plan_price = 0
            if '₦' in plan_dict[plan]:
                plan_price = int(plan_dict[plan].split('₦')[-1])

            profile = UserProfile.objects.get(user=request.user)
            if profile.wallet_balance < plan_price:
                messages.error(request, 'Insufficient wallet balance')
                return redirect('ninemobile_data')

            request_id = str(uuid.uuid4())
            payload = {
                "serviceID": "etisalat-data",
                "variation_code": plan,
                "request_id": request_id,
                "phone": phone,
            }
            headers = {
                "api-key": "your-api-key",
                "public-key": "your-public-key",
                "Content-Type": "application/json"
            }
            try:
                response = request.post("https://vtpass.com/api/pay", json=payload, headers=headers)
                result = response.json()
                if result.get("code") == "000":
                    profile.wallet_balance -= plan_price
                    profile.save()

                    Transaction.objects.create(
                        user=request.user,
                        service='data',
                        provider='9Mobile',
                        amount=plan_price,
                        phone=phone,
                        status='success',
                        request_id=request_id
                    )
                    messages.success(request, 'Airtel Data purchase successfully!')
                    return redirect('ninemobile_data')
                
                else:
                    messages.error(request, f"Failed {result.get('response_description')}")

            except Exception as e:
                messages.error(request, f"API Error: {str(e)}")

    else:
        form = ninemobileDataForm()

    return render(request, 'data/ninemobile_data.html', {'form': form})




#======================================= TV SUBSCRIPTION ====================================================#

#========================= DSTV =================================#

def DSTV(request):
    if request.method == 'POST':
        form = DSTVForm(request.POST)
        if form.is_valid():
            smartcard = form.cleaned_data['smartcard_number']
            plan = form.cleaned_data['plan']
            password = form.cleaned_data['password']
            if not request.user.check_password(password):
                messages.error(request, 'Incorrect password')
                return redirect('dstv')
            
            plan_dict = dict(DSTVForm.PLAN_CHOICES)
            plan_price = 0
            if '₦' in plan_dict[plan]:
                plan_price = int(plan_dict[plan].split('₦')[-1])

            profile = UserProfile.objects.get(user=request.user)
            if profile.wallet_balance < plan_price:
                messages.error(request, 'Insufficient wallet balance')
                return redirect('dstv')

            headers = {
                "api-key": "your-api-key",
                "public-key": "your-public-key",
                "Content-Type": "application/json"
            }
            validation_payload = {
                "billersCode": smartcard,
                "serviceID": "dstv",
            }
            
            try:
                validate_res = requests.post("https://vtpass.com/api/merchant-verify", json=validation_payload, headers=headers).json()
                if validate_res.get("code") != "000":
                    messages.error(request, f"Smartcard validation failed: {validate_res.get('response_description')}")
                    return redirect('dstv')
            except Exception as e:
                messages.error(request, f"Validation API Error: {str(e)}")
                return redirect('dstv')
            
            request_id = str(uuid.uuid4())
            payload = {
                "serviceID": "dstv",
                "billersCode": smartcard,
                "variation_code": plan,
                "amount": str(plan_price),
                "phone": request.user.username,
                "request_id": request_id
            }
            try:
                pay_res = requests.post("https://vtpass.com/api/pay", json=payload, headers=headers).json()
                if pay_res.get("code") == "000":
                    profile.wallet_balance -= plan_price
                    profile.save()

                    Transaction.objects.create(
                        user=request.user,
                        service='tv',
                        provider='DSTV',
                        amount=plan_price,
                        phone=smartcard,
                        status='success',
                        request_id=request_id
                    )
                    messages.success(request, 'DSTV subscription purchase successfully!')
                    return redirect('dstv')
                
                else:
                    messages.error(request, f"Purchase failed {pay_res.get('response_description')}")

            except Exception as e:
                messages.error(request, f"Payment API Error: {str(e)}")

    else:
        form = DSTVForm()

    return render(request, 'tv/dstv.html', {'form': form})

#=====GOTV
def GOTV(request):
    if request.method == 'POST':
        form = GOTVForm(request.POST)
        if form.is_valid():
            smartcard = form.cleaned_data['smartcard_number']
            plan = form.cleaned_data['plan']
            password = form.cleaned_data['password']
            if not request.user.check_password(password):
                messages.error(request, 'Incorrect password')
                return redirect('gotv')
            
            plan_dict = dict(GOTVForm.PLAN_CHOICES)
            plan_price = 0
            if '₦' in plan_dict[plan]:
                plan_price = int(plan_dict[plan].split('₦')[-1])

            profile = UserProfile.objects.get(user=request.user)
            if profile.wallet_balance < plan_price:
                messages.error(request, 'Insufficient wallet balance')
                return redirect('gotv')

            headers = {
                "api-key": "your-api-key",
                "public-key": "your-public-key",
                "Content-Type": "application/json"
            }
            validation_payload = {
                "billersCode": smartcard,
                "serviceID": "gotv",
            }
            
            try:
                validate_res = requests.post("https://vtpass.com/api/merchant-verify", json=validation_payload, headers=headers).json()
                if validate_res.get("code") != "000":
                    messages.error(request, f"Smartcard validation failed: {validate_res.get('response_description')}")
                    return redirect('gotv')
            except Exception as e:
                messages.error(request, f"Validation API Error: {str(e)}")
                return redirect('gotv')
            
            request_id = str(uuid.uuid4())
            payload = {
                "serviceID": "gotv",
                "billersCode": smartcard,
                "variation_code": plan,
                "amount": str(plan_price),
                "phone": request.user.username,
                "request_id": request_id
            }
            try:
                pay_res = requests.post("https://vtpass.com/api/pay", json=payload, headers=headers).json()
                if pay_res.get("code") == "000":
                    profile.wallet_balance -= plan_price
                    profile.save()

                    Transaction.objects.create(
                        user=request.user,
                        service='tv',
                        provider='GOTV',
                        amount=plan_price,
                        phone=smartcard,
                        status='success',
                        request_id=request_id
                    )
                    messages.success(request, 'GOTV subscription purchase successfully!')
                    return redirect('gotv')
                
                else:
                    messages.error(request, f"Purchase failed {pay_res.get('response_description')}")

            except Exception as e:
                messages.error(request, f"Payment API Error: {str(e)}")

    else:
        form = GOTVForm()

    return render(request, 'tv/gotv.html', {'form': form})

#=====STARTIMES
def STARTIME(request):
    if request.method == 'POST':
        form = STARTIMESForm(request.POST)
        if form.is_valid():
            smartcard = form.cleaned_data['smartcard_number']
            plan = form.cleaned_data['plan']
            password = form.cleaned_data['password']
            if not request.user.check_password(password):
                messages.error(request, 'Incorrect password')
                return redirect('startime')
            
            plan_dict = dict(STARTIMESForm.PLAN_CHOICES)
            plan_price = 0
            if '₦' in plan_dict[plan]:
                plan_price = int(plan_dict[plan].split('₦')[-1])

            profile = UserProfile.objects.get(user=request.user)
            if profile.wallet_balance < plan_price:
                messages.error(request, 'Insufficient wallet balance')
                return redirect('startime')

            headers = {
                "api-key": "your-api-key",
                "public-key": "your-public-key",
                "Content-Type": "application/json"
            }
            validation_payload = {
                "billersCode": smartcard,
                "serviceID": "startimes",
            }
            
            try:
                validate_res = requests.post("https://vtpass.com/api/merchant-verify", json=validation_payload, headers=headers).json()
                if validate_res.get("code") != "000":
                    messages.error(request, f"Smartcard/IUC validation failed: {validate_res.get('response_description')}")
                    return redirect('startime')
            except Exception as e:
                messages.error(request, f"Validation API Error: {str(e)}")
                return redirect('startime')
            
            request_id = str(uuid.uuid4())
            payload = {
                "serviceID": "startimes",
                "billersCode": smartcard,
                "variation_code": plan,
                "amount": str(plan_price),
                "phone": request.user.username,
                "request_id": request_id
            }
            try:
                pay_res = requests.post("https://vtpass.com/api/pay", json=payload, headers=headers).json()
                if pay_res.get("code") == "000":
                    profile.wallet_balance -= plan_price
                    profile.save()

                    Transaction.objects.create(
                        user=request.user,
                        service='tv',
                        provider='Startimes',
                        amount=plan_price,
                        phone=smartcard,
                        status='success',
                        request_id=request_id
                    )
                    messages.success(request, 'Startimes subscription purchase successfully!')
                    return redirect('startime')
                
                else:
                    messages.error(request, f"Purchase failed {pay_res.get('response_description')}")

            except Exception as e:
                messages.error(request, f"Payment API Error: {str(e)}")

    else:
        form = STARTIMESForm()

    return render(request, 'tv/startime.html', {'form': form})

#==========================================================================================================#

#==========================================================================================================#

# IKEDCPrepaidView
from .forms import prepaidForm
def IKEDCPrePaid(request):
    customer_name = None
    verified = False

    if request.method == 'POST':
        form = prepaidForm(request.POST)
        if form.is_valid():
            meter_number = form.cleaned_data['meter_number']
            amount = form.cleaned_data['amount']
            password = form.cleaned_data['password']

            if 'verify' in request.POST:
                headers = {
                    "api-key": "your-api-key",
                    "public-key": "your-public-key",
                    "Content-Type": "application/json"
                }
                validation_payload = {
                    "billersCode": meter_number,
                    "serviceID": "ikedc-prepaid"
                }
                try:
                    validate_res = requests.post("https://vtpass.com/api/merchant-verify", json=validation_payload, headers=headers).json()
                    
                    if validate_res.get("code") == "000":
                        customer_name = validate_res['content'].get('Customer_Name', 'Unknown')
                        messages.success(request, f"Meter verified: {customer_name}")
                        verified=True
                    else:
                        messages.error(request, f"Meter validation failed: {validation_res.get('response_description')}")
                        return redirect('ikedc_prepaid')

                except Exception as e:
                    messages.error(request, f"Validation API Error: {str(e)}")

            elif 'pay' in request.POST:


                if not request.user.check_password(password):
                    messages.error(request, "Incorrect password")
                    return redirect('ikedc_prepaid')

                profile = UserProfile.objects.get(user=request.user)
                if profile.wallet_balance < amount:
                    messages.error(request, "Insufficient wallet balance")
                    return redirect('ikedc_prepaid')

                headers = {
                    "api-key": "your-api-key",
                    "public-key": "your-public-key",
                    "Content-Type": "application/json"
                }

            request_id = str(uuid.uuid4())
            payload = {
                "serviceID": "ikedc-prepaid",
                "billersCode": meter_number,
                "variation_code": "prepaid",
                "amount": str(amount),
                "phone": request.user.username,
                "request_id": request_id
            }

            try:
                pay_res = requests.post("https://vtpass.com/api/pay", json=payload, headers=headers).json()

                if pay_res.get("code") == "000":
                    profile.wallet_balance -= amount
                    profile.save()

                    token = pay_res['content']['transaction'].get('token')
                    customer_name = pay_res['content'].get('customer_name', '')
                    Transaction.objects.create(
                        user=request.user,
                        service='electricity',
                        provider='IKEDC - Prepaid',
                        amount=amount,
                        phone=meter_number,
                        status='success',
                        request_id=request_id,
                        token=token,
                        customer_name=customer_name
                    )
                    messages.success(request, 'IKEDC Prepaid bill payment successful\nToken: {token}')
                    return redirect('ikedc_prepaid')
                
                else:
                    messages.error(request, f"Purchase failed: {pay_res.get('response_description')}")
            
            except Exception as e:
                messages.error(request, f"Payment API Error: {str(e)}")
    else:
        form = prepaidForm()
    return render(request, 'electricity/ikedc_prepaid.html', {'form': form, "customer_name": customer_name, "verified": verified})

# IKEDCPostpaidView
from .forms import postpaidForm
def IKEDCPostPaid(request):
    customer_name = None
    verified = False

    if request.method == 'POST':
        form = postpaidForm(request.POST)
        if form.is_valid():
            meter_number = form.cleaned_data['meter_number']
            amount = form.cleaned_data['amount']
            password = form.cleaned_data['password']

            if 'verify' in request.POST:
                headers = {
                    "api-key": "your-api-key",
                    "public-key": "your-public-key",
                    "Content-Type": "application/json"
                }
                validation_payload = {
                    "billersCode": meter_number,
                    "serviceID": "ikedc-postpaid"
                }
                try:
                    validate_res = requests.post("https://vtpass.com/api/merchant-verify", json=validation_payload, headers=headers).json()
                    
                    if validate_res.get("code") == "000":
                        customer_name = validate_res['content'].get('Customer_Name', 'Unknown')
                        messages.success(request, f"Meter verified: {customer_name}")
                        verified=True
                    else:
                        messages.error(request, f"Meter validation failed: {validation_res.get('response_description')}")

                except Exception as e:
                    messages.error(request, f"Validation API Error: {str(e)}")

            elif 'pay' in request.POST:


                if not request.user.check_password(password):
                    messages.error(request, "Incorrect password")
                    return redirect('ikedc_postpaid')

                profile = UserProfile.objects.get(user=request.user)
                if profile.wallet_balance < amount:
                    messages.error(request, "Insufficient wallet balance")
                    return redirect('ikedc_postpaid')

                headers = {
                    "api-key": "your-api-key",
                    "public-key": "your-public-key",
                    "Content-Type": "application/json"
                }

            request_id = str(uuid.uuid4())
            payload = {
                "serviceID": "ikedc-postpaid",
                "billersCode": meter_number,
                "variation_code": "postpaid",
                "amount": str(amount),
                "phone": request.user.username,
                "request_id": request_id
            }

            try:
                pay_res = requests.post("https://vtpass.com/api/pay", json=payload, headers=headers).json()

                if pay_res.get("code") == "000":
                    profile.wallet_balance -= amount
                    profile.save()

                    customer_name = pay_res['content'].get('customer_name', '')
                    Transaction.objects.create(
                        user=request.user,
                        service='electricity',
                        provider='IKEDC - Postpaid',
                        amount=amount,
                        phone=meter_number,
                        status='success',
                        request_id=request_id,
                        token=None,
                        customer_name=customer_name
                    )
                    messages.success(request, 'IKEDC Postpaid bill payment successful!')
                    return redirect('ikedc_postpaid')
                
                else:
                    messages.error(request, f"Purchase failed: {pay_res.get('response_description')}")
            
            except Exception as e:
                messages.error(request, f"Payment API Error: {str(e)}")
    else:
        form = postpaidForm()
    return render(request, 'electricity/ikedc_postpaid.html', {'form': form, "customer_name": customer_name, 'verified': verified})
