from django.shortcuts import render, redirect
from .models import UserProfile
from django.http import HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import SignupForm, LoginForm
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.urls import reverse
from .utils import create_paystack_customer

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.core.mail import EmailMessage
from django.contrib import messages
from django.shortcuts import render, redirect
from django.template.loader import render_to_string


# Create your views here.

#===============  SIGNUP VIEW  =====================#
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignupForm
from .models import UserProfile

# Make sure you import your Paystack function
# from .paystack_utils import create_paystack_customer  

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login
from .forms import SignupForm
from .models import UserProfile
from .utils import create_paystack_customer
from django.db import IntegrityError, transaction

'''
def signUp(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            password = form.cleaned_data['password']
            referral_code_input = form.cleaned_data.get('referral_code')

            try:
                with transaction.atomic():  # ensure DB integrity
                    # Create User
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password
                    )

                    # Create or get UserProfile
                    profile, created = UserProfile.objects.get_or_create(
                        user=user,
                        defaults={"phone": phone}
                    )

                    if not created and not profile.phone:
                        profile.phone = phone
                        profile.save()

                    # Attach Paystack Customer Code
                    try:
                        customer_code = create_paystack_customer(
                            email=email,
                            first_name=username,
                            last_name="User"
                        )
                        profile.paystack_customer_code = customer_code
                        profile.save()
                    except Exception as e:
                        messages.warning(request, f"Paystack customer creation failed: {e}")

                    # Handle referral
                    if referral_code_input:
                        try:
                            referrer = UserProfile.objects.get(referral_code=referral_code_input)
                            referrer.credit(200)  # assuming you have a credit() method
                            messages.success(request, f"You were referred by {referrer.user.username}.")
                        except UserProfile.DoesNotExist:
                            messages.warning(request, "Invalid referral code.")

                    # Login new user
                    login(request, user)
                    messages.success(request, f"Account created successfully. Welcome, {username}!")
                    return redirect('dashboard')  # change to your actual dashboard route

            except IntegrityError:
                messages.error(request, "A user with this email, phone, or username already exists.")
                return redirect('signup')

        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})
'''
#================ SIGNUP VIEW ==================#
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import SignupForm
from django.contrib.auth.models import User
from .models import UserProfile


def signUp(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # login(request, user)  # auto login
            messages.success(request, "Account created successfully 🎉")
            return redirect("login")
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SignupForm()

    return render(request, "signup.html", {"form": form})


#===============  LOGIN VIEW  =====================#
'''
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

'''
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import LoginForm

def logIn(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get("user")
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid login credentials.")
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


def logOut(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

#================= FORGET PASSWORD SETUP ======================@

from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'auth/password_reset.html'
    email_template_name = 'auth/password_reset_email.html'
    subject_template_name = 'auth/password_reset_subject.txt'

    success_url = reverse_lazy('password_reset_done')

    form_class = CustomPasswordResetForm

class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'auth/password_reset_done.html'
    
class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'auth/password_reset_confirm.html'

    success_url = reverse_lazy('password_reset_complete')

    form_class = CustomSetPasswordForm

class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'auth/password_reset_complete.html'