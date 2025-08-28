from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
import re
import random, string
from django.contrib.auth import authenticate, login, logout

'''
class SignupForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)
    referral_code = forms.CharField(max_length=20, required=False)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        if UserProfile.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Phone number already exists.")
        return phone

    def clean_password(self):
        password = self.cleaned_data.get("password")

        # At least 6 chars
        if len(password) < 6:
            raise forms.ValidationError("Password must be at least 6 characters long.")
        # At least one uppercase
        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        # At least one number
        if not re.search(r"\d", password):
            raise forms.ValidationError("Password must contain at least one number.")
        # At least one symbol
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise forms.ValidationError("Password must contain at least one special character.")

        return password

    @staticmethod
    def generate_referral():
        """Generate random referral code of 8 chars"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")

        return cleaned_data
'''

#=================== SIGNUP =========================#
from django import forms
from django.contrib.auth import get_user_model
from .models import UserProfile
import re
User = get_user_model()


class SignupForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    referral_code = forms.CharField(
        label="Referral Code (optional)",
        max_length=12,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ["username", "email", "phone"]

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if len(password) < 6:
            raise forms.ValidationError("Password must be at least 6 characters long.")
        # At least one uppercase
        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        # At least one number
        if not re.search(r"\d", password):
            raise forms.ValidationError("Password must contain at least one number.")
        # At least one symbol
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise forms.ValidationError("Password must contain at least one special character.")
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        referral_code = self.cleaned_data.get("referral_code")
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])

        if referral_code:
            try:
                referrer = User.objects.get(referral_code=referral_code)
                user.referred_by = referrer
            except User.DoesNotExist:
                pass  # invalid referral, ignore

        if commit:
            user.save()

            # If valid referral, reward both referrer and new user
            if user.referred_by:
                # user.credit(500)               # reward new user
                user.referred_by.credit(200)  # reward referrer

        return user


#======================= LOGIN ===============================#
'''
class LoginForm(forms.Form):
    identifier = forms.CharField(
        label="Email or Phone Number",
        max_length=150,
        required=True
    )
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get("identifier")
        password = cleaned_data.get("password")

        if identifier and password:
            try:
                # Try email first
                profile = UserProfile.objects.filter(user__email=identifier).first()

                # If not email, try phone
                if not profile:
                    profile = UserProfile.objects.filter(phone=identifier).first()

                if not profile:
                    raise forms.ValidationError("Invalid email/phone or password.")

                user = authenticate(username=profile.user.username, password=password)
                if not user:
                    raise forms.ValidationError("Invalid email/phone or password.")

            except UserProfile.DoesNotExist:
                raise forms.ValidationError("Invalid email/phone or password.")

        return cleaned_data

'''
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

class LoginForm(forms.Form):
    identifier = forms.CharField(
        label="Username, Email, or Phone",
        widget=forms.TextInput(attrs={"placeholder": "Enter Username, Email or Phone"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Enter Password"})
    )

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get("identifier")
        password = cleaned_data.get("password")

        if identifier and password:
            user = None

            # Try username
            from django.contrib.auth import authenticate
            user = authenticate(username=identifier, password=password)

            if not user:
                # Try email
                try:
                    user_obj = User.objects.get(email=identifier)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass

            if not user:
                # Try phone
                try:
                    user_obj = User.objects.get(phone=identifier)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass

            if not user:
                raise forms.ValidationError("Invalid login credentials.")

            cleaned_data["user"] = user
        return cleaned_data


from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password'
        })
    )

    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )