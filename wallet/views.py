import requests, json, logging
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from base.models import Transaction
from register.models import UserProfile
from .forms import FundingWalletForm

logger = logging.getLogger(__name__)

# ------------------- CREATE DVA -------------------
def create_dva(profile):
    if profile.virtual_account_number or profile.virtual_account_status == 'assigning':
        return
    url = "https://api.paystack.co/dedicated_account/assign"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    payload = {
        "email": profile.user.email,
        "first_name": profile.user.username,
        "last_name": "User",
        "phone": profile.phone,
        "preferred_bank": settings.PREFERRED_BANK_SLUG,
        "country": "NG"
    }
    try:
        resp = requests.post(url, json=payload, headers=headers)
        data = resp.json()
        if data['status']:
            profile.virtual_account_status = 'assigning'
            profile.paystack_customer_code = data['data']['customer']['customer_code']
            profile.save()
        else:
            logger.error(f"DVA creation failed: {data.get('message')}")
    except Exception as e:
        logger.error(f"DVA request error: {str(e)}")

# ------------------- WALLET PAGE -------------------
@login_required
def wallet_page(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.virtual_account_number and profile.virtual_account_status != 'assigning':
        create_dva(profile)

    transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:10]
    form = FundingWalletForm()

    return render(request, 'wallet/wallet.html', {
        'profile': profile,
        'form': form,
        'transactions': transactions
    })

# ------------------- FUND WALLET FORM -------------------
@login_required
def fund_wallet(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = FundingWalletForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            fee = form.cleaned_data['fee']
            net_amount = form.cleaned_data['net_amount']

            # Create transaction
            transaction = Transaction.objects.create(
                user=request.user,
                amount=amount,
                fee_amount=fee,
                net_amount=net_amount,
                status='Pending'
            )

            # Render confirmation page with Paystack inline button
            return render(request, 'wallet/wallet.html', {
                'profile': profile,
                'form': form,
                'amount': amount,
                'fee': fee,
                'net_amount': net_amount,
                'reference': transaction.reference
            })
        else:
            messages.error(request, "Amount must be at least 100 NGN.")
    else:
        form = FundingWalletForm()
    return render(request, 'wallet/fund_wallet_form.html', {'form': form, 'profile': profile})

# ------------------- PAYSTACK CALLBACK -------------------
@login_required
def paystack_callback(request):
    reference = request.GET.get('reference')
    if not reference:
        messages.error(request, "Invalid callback.")
        return redirect('wallet_page')

    transaction = Transaction.objects.filter(reference=reference, user=request.user).first()
    if not transaction:
        messages.error(request, "Transaction not found.")
        return redirect('wallet_page')

    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

    try:
        resp = requests.get(url, headers=headers)
        data = resp.json()
        if data['status'] and data['data']['status'] == 'success':
            transaction.status = 'Success'
            profile = UserProfile.objects.get(user=request.user)
            profile.wallet_balance += transaction.net_amount
            profile.save()
            transaction.save()
            messages.success(request, f"Wallet funded ₦{transaction.net_amount} (fee ₦{transaction.fee_amount}).")
        else:
            transaction.status = 'Failed'
            transaction.save()
            messages.error(request, "Payment verification failed.")
    except Exception as e:
        messages.error(request, f"Verification error: {str(e)}")

    return redirect('wallet_page')

# ------------------- PAYSTACK WEBHOOK -------------------
@csrf_exempt
def paystack_webhook(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    try:
        payload = json.loads(request.body)
        event = payload.get('event')
        data = payload.get('data')

        if event == 'charge.success':
            reference = data.get('reference')
            amount = data.get('amount') / 100

            try:
                customer_code = data['customer']['customer_code']
                profile = UserProfile.objects.get(paystack_customer_code=customer_code)

                transaction, created = Transaction.objects.get_or_create(
                    reference=reference,
                    defaults={
                        'user': profile.user,
                        'amount': amount,
                        'fee_amount': 0,
                        'net_amount': 0,
                        'status': 'Pending'
                    }
                )

                if transaction.status != 'Success':
                    fee = calculate_fee(amount)
                    net_amount = amount - fee
                    profile.wallet_balance += net_amount
                    profile.save()

                    transaction.fee_amount = fee
                    transaction.net_amount = net_amount
                    transaction.status = 'Success'
                    transaction.save()
                    logger.info(f"Wallet funded ₦{net_amount} for {profile.user.username}, fee ₦{fee}.")

            except UserProfile.DoesNotExist:
                logger.error(f"No profile found for customer_code {customer_code}")

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return HttpResponse(status=400)

    return HttpResponse(status=200)

from django.views.decorators.http import require_POST
from django.http import JsonResponse

@login_required
@require_POST
def create_pending_transaction(request):
    try:
        amount = float(request.POST.get('amount'))
        if amount < 100:
            return JsonResponse({'error': 'Amount must be at least 100 NGN.'}, status=400)

        # Calculate fee
        fee = calculate_fee(amount)
        net_amount = amount - fee

        # Create pending transaction
        transaction = FundingTransaction.objects.create(
            user=request.user,
            amount=amount,
            fee_amount=fee,
            net_amount=net_amount,
            status='Pending'
        )

        return JsonResponse({
            'reference': transaction.reference,
            'amount': amount,
            'fee': fee,
            'net_amount': net_amount
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
