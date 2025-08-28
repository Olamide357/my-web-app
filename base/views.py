from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.utils.dateformat import DateFormat
from .models import Beneficiary, Transaction
from .forms import BeneficiaryForm, changePasswordForm, editProfileForm
from register.models import UserProfile

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.contrib.auth import update_session_auth_hash


# Create your views here.

def homePage(request):
    return render(request, 'home.html')

def dashboardPage(request):
    return render(request, 'dashboard.html')
#===================== History Views ================================================================#
# from wallet.models import FundingTransaction
# History Page
@login_required
def historyPage(request):
    query = request.GET.get("q", "").strip()
    transactions = Transaction.objects.filter(user=request.user).order_by("-date")

    # 🔎 Search by date or reference
    if query:
        try:
            # If user typed a date like 2025-08-20
            search_date = parse_date(query)
            if search_date:
                transactions = transactions.filter(created_at__date=search_date)
            else:
                transactions = transactions.filter(
                    Q(reference__icontains=query) |
                    Q(provider__icontains=query) |
                    Q(phone__icontains=query)
                )
        except Exception:
            pass

    paginator = Paginator(transactions, 10)  # 10 per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "history.html", {
        "page_obj": page_obj,
        "query": query,
    })
    

# Receipt
def transactionReceipt(request, transaction_id):
    txn = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    data = {
        "date": DateFormat(txn.date).format("d M Y H:i"),
        "service": txn.service.title(),
        "provider": txn.provider,
        "amount": f"₦{txn.amount}",
        "phone_or_meter": txn.phone_or_meter,
        "status": txn.status.title(),
        "reference_id": txn.reference_id
    }
    return JsonResponse(data)

# Receipt Download View
def transactionReceiptPDF(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    pdf = render_to_pdf('receiptPDF.html', {'transaction': txn})

    if pdf:
        filename = f"Receipt_{transaction.request_id}.pdf"
        response = HttpResponse(pdf, content_type='application/pdf')
        content = f"attachment; filename={filename}"

        response['content-Disposition'] = content
        return response
    return HttpResponse("Error generating PDF", status=500)

#==================== History End ==============#

#====================================== BENEFICIARY =======================================#
# BENEFICIARY VIEWS
def beneficiaryPage(request):
    beneficiaries = Beneficiary.objects.filter(user=request.user).order_by('-date_added')
    return render(request, 'beneficiary.html', {'beneficiaries': beneficiaries})

# ADD BENEFICIARY VIEWS
def addBeneficiary(request):
    if request.method == 'POST':
        form = BeneficiaryForm(request.POST)
        if form.is_valid():
            beneficiary = form.save(commit=False)
            beneficiary.user = request.user
            beneficiary.save()
            messages.success(request, 'Beneficiary added successfully.')
            return redirect('beneficiary_list')
    else:
        form = BeneficiaryForm()
    return render(request, 'addbeneficiary.html', {'form': form})

# EDIT BENEFICIARY VIEWS
def editBeneficiary(request, pk):
    beneficiary = get_object_or_404(Beneficiary, pk=pk, user=request.user)
    if request.method == 'POST':
        form = BeneficiaryForm(request.POST, instance=beneficiary)

        if form.is_valid():
            form.save()
            messages.success(request, "Beneficiary updated successfully.")
            return redirect('beneficiary_list')
    
    else:
        form = BeneficiaryForm(instance=beneficiary)
    return render(request, 'editbeneficiary.html', {'form': form})

# DELETE BENEFICIARY VIEWS
def deleteBeneficiary(request, beneficiary_id):
    beneficiary = get_object_or_404(Beneficiary, id=beneficiary_id, user=request.user)
    if request.method == 'POST':
        beneficiary.delete()
        messages.success(request, 'Beneficiary deleted successfully.')
        return redirect('beneficiary_list')
    return render(request, 'deletebeneficiary.html', {'beneficiary': beneficiary})

# USE BENEFECIARY
from django.urls import reverse
from django.http import Http404
def useBeneficiary(request, pk):
    beneficiary = get_object_or_404(Beneficiary, pk=pk, user=request.user)

    service_provider_map = {
        'airtime': {
            'MTN': 'mtn_airtime',
            'GLO': 'glo_airtime',
            'AIRTEL': 'airtel_airtime',
            '9MOBILE': 'ninemobile_airtime',
        },
        'data': {
            'MTN': 'mtn_data',
            'GLO': 'glo_data',
            'AIRTEL': 'airtel_data',
            '9MOBILE': 'ninemobile_data',
            'ETISALAT': 'ninemobile_data',
        },
        'tv': {
            'DSTV': 'dstv',
            'GOTV': 'gotv',
            'STARTIME': 'startime',
            'STARTIMES': 'startime',
        },
        'electricity': {
            'IKEDC': 'ikedc',
            'EKEDC': 'ekedc',
            'AEDC': 'aedc',
            'KADUNA': 'kaduna',
            'IBEDC': 'ibedc',
            'JOS': 'jos',
        },
    }
    service = beneficiary.service_type.lower()
    provider = beneficiary.provider.upper()
    url_name = service_provider_map.get(service, {}).get(provider)
    if not url_name:
        raise Http404("Invalid service or provider")

    base_url = reverse(url_name)
    return redirect(f'{base_url}?phone={beneficiary.account_number}')
#=============== BENEFICIARY END =====================#

#================== ABOUT VIEWS =====================#
@login_required
def aboutPage(request):
    return render(request, 'about.html')

from django.contrib.auth import update_session_auth_hash
from .forms import editProfileForm, changePasswordForm

@login_required
def editAccount(request):
    profile = request.user
    # user_profile, created = UserProfile.objects.get_or_create(user=user)
    if request.method == 'POST':
        if 'edit_profile' in request.POST:
            profile_form = editProfileForm(request.POST, instance=profile)
            password_form = changePasswordForm()
            
            if profile_form.is_valid():
                updated_user=profile_form.save(commit=False)
                updated_user.email = profile_form.cleaned_data.get("email", profile.email)
                updated_user.save()

                # Save phone number to UserProfile
                phone = profile_form.cleaned_data.get("phone")
                if phone and phone != profile.phone:
                    profile.phone = phone
                    profile.save()

                messages.success(request, "✅ Profile updated successfully.")
                return redirect("about")
            else:
                messages.error(request, "⚠️ Please correct the errors below.")

        elif "change_password" in request.POST:
            profile_form = EditProfileForm(instance=user, user=user)
            password_form = changePasswordForm(request.POST)

            if password_form.is_valid():
                new_password = password_form.cleaned_data["new_password"]
                confirm_password = password_form.cleaned_data["confirm_password"]

                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.save()

                    update_session_auth_hash(request, user)  # keep logged in
                    messages.success(request, "🔒 Password changed successfully.")
                    return redirect("edit_account")

                else:
                    messages.error(request, "❌ Passwords do not match.")
            else:
                messages.error(request, "⚠️ Please correct the errors below.")

    else:  # GET
        profile_form = editProfileForm(instance=profile)#, user=user, initial={"phone": UserProfile.phone, "email": user.email})
        password_form = changePasswordForm()

    return render(
        request,
        "edit.html",
        {"profile_form": profile_form, "password_form": password_form},
    )
#============== DELETE ACCOUNT VIEWS =============#
@login_required
def deleteAccount(request):
    user = request.user
    user.is_active = False
    user.save()
    messages.success(request, "Your account has been deleted.")
    return redirect('homepage')