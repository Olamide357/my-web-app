from django.urls import path
from .import views

urlpatterns = [
    path('callback/', views.paystack_callback, name='wallet_callback'),
    path("wallet/create-account/", views.create_virtual_account, name="create_virtual_account"),
    # path("paystack/webhook/", views.paystack_webhook, name="paystack_webhook"),
    # path('webhook/paystack/', views.paystack_webhook, name='paystack_webhook'),
    # path('check-reserved-account/', views.check_paystack_account_status, name='check_paystack_account'),
    # path("wallet/", views.wallet_page, name="wallet"),

    path("wallet/", views.wallet_page, name="wallet"),
    path("wallet/monnify-webhook/", views.monnify_webhook, name="monnify_webhook"),
    path("wallet/monnify-callback/", views.monnify_callback, name="monnify_callback"),

]