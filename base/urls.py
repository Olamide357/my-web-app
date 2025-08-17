from django.urls import path
from . import views

urlpatterns = [
    path('', views.homePage, name='homepage'),
    path('dashboard', views.dashboardPage, name='dashboard'),
    path('transaction/history', views.historyPage, name='history'),

    path('transactions/receipt/<int:transaction_id>/ajax/', views.transactionReceipt, name='receipt'),
    path('transactions/receipt/<int:transaction_id>/pdf/', views.transactionReceiptPDF, name='pdf'),

    # BENEFICIARIES
    path('beneficiaries/', views.beneficiaryPage, name='beneficiary_list'),
    path('beneficiaries/add/', views.addBeneficiary, name='addbeneficiary'),
    path('beneficiaries/edit/<int:pk>/', views.editBeneficiary, name='editbeneficiary'),
    path('beneficiaries/delete/<int:beneficiary_id>/', views.deleteBeneficiary, name='deletebeneficiary'),
    path('use/<int:pk>/', views.useBeneficiary, name='usebeneficiary'),

    # ABOUT
    path('about/', views.aboutPage, name='about'),
    path('edit-account/', views.editAccount, name='edit'),

    # Delete Account
    path('delete-account/', views.deleteAccount, name='delete_account'),
]