from django.shortcuts import render, redirect
from .models import UserProfile
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile
from .forms import SignupForm, LoginForm

# Create your views here.

#===============  SIGNUP VIEW  =====================#
def signUp(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']
            referral = form.cleaned_data['referral_code']

            # Create User
            user = User.objects.create_user(username=username, email=email, password=password)

            # Create UserProfile
            profile = user.userprofile
            profile.phone=phone
            profile.referral_code=phone
            profile.save()

            # Handle referral bonus
            if referral:
                try:
                    referrer = UserProfile.objects.get(referral_code=referral)
                    referrer.wallet_balance += 200
                    referrer.save()
                    messages.success(request, f"You were referred by {referrer.user.username}. ₦200 reward added.")
                except UserProfile.DoesNotExist:
                    messages.warning(request, "Invalid referral code.")

            messages.success(request, "Signup successful. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})


#===============  LOGIN VIEW  =====================#
def logIn(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']

            # Find profile
            profile = UserProfile.objects.filter(user__email=identifier).first()
            if not profile:
                profile = UserProfile.objects.filter(phone=identifier).first()

            if profile:
                user = authenticate(username=profile.user.username, password=password)
                if user:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.username}!")
                    return redirect('dashboard')  # change to your dashboard name
            messages.error(request, "Invalid email/phone or password.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logOut(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')