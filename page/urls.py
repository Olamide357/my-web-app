from django.urls import path
from . import views

urlpatterns = [
    path('buy-airtime/', views.buyAirtime, name='buy_airtime'),

    path('buy-data/', views.buyData, name='buy_data'),

    path('buy-tv/', views.buyTV, name='buy_tv'),

    path('buy-electricity/', views.buyElectricity, name='buy_electricity'),

    path('balance_code/', views.balanceCode, name='balance_code'),

    path('contact_us/', views.contactUS, name='contact_us'),

    path('faq/', views.FAQ, name='faq'),
]