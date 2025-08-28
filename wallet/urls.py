from django.urls import path
from . import views

urlpatterns = [
    path("wallet/", views.fund_wallet, name="wallet"),

    # DVA
    path("check_dva/", views.check_dva, name="check_dva"),
    path("generate_dva/", views.generate_dva, name="generate_dva"),
    path("dva_auto_credit/", views.dva_auto_credit, name="dva_auto_credit"),

    # Inline Paystack
    path("create_pending_transaction/", views.create_pending_transaction, name="create_pending_transaction"),
    path("wallet/paystack_callback/", views.paystack_callback, name="paystack_callback"),

    # Webhook (optional; configure URL in Paystack dashboard)
    path("paystack_webhook/", views.paystack_webhook, name="paystack_webhook"),
]
