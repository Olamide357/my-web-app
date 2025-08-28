from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'auth/password_reset.html'
    email_template_name = 'auth/password_reset_email.html'
    subject_template_name = 'auth/password_reset_subject.txt'

    success_url = reverse_lazy('password_reset_done')

    form_class = CustomPasswordResetForm

class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'auth/password_reset_confirm.html'

    success_url = reverse_lazy('password_reset_complete')

    form_class = CustomPasswordForm

class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'auth/password_reset_complete.html'