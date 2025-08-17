from django.urls import path
from .import views

urlpatterns = [
    path('fund/', views.fundWallet, name='fund_wallet'),
    path('callback/', views.paystack_callback, name='wallet_callback'),

    # path('webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),
    # path('check-reserved-account/', views.check_paystack_account_status, name='check_paystack_account'),
]