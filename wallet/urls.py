from django.urls import path
from . import views

urlpatterns = [
    path('wallet/', views.wallet_page, name='wallet'),
    path('wallet/create-transaction/', views.create_pending_transaction, name='create_pending_transaction'),
    path('wallet/paystack-callback/', views.paystack_callback, name='paystack_callback'),
]
