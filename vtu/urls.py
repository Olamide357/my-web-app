from django.urls import path
from . import views

urlpatterns = [
    path('airtime/mtn/', views.mtnAirtime, name='mtn_airtime'),
    path('airtime/glo/', views.gloAirtime, name='glo_airtime'),
    path('airtime/airtel/', views.airtelAirtime, name='airtel_airtime'),
    path('airtime/ninemobile/', views.ninemobileAirtime, name='ninemobile_airtime'),

    # DATA NETWORK
    path('data/mtn/', views.mtnData, name='mtn_data'),
    path('data/glo/', views.gloData, name='glo_data'),
    path('data/airtel/', views.airtelData, name='airtel_data'),
    path('data/ninemobile/', views.ninemobileData, name='ninemobile_data'),

    #TV
    path('tv/dstv/', views.DSTV, name='dstv'),
    path('tv/gotv/', views.GOTV, name='gotv'),
    path('tv/startime/', views.STARTIME, name='startime'),

    # ELECTRICITY
    path('electricty/ikedc-prepaid', views.IKEDCPrePaid, name='ikedc_prepaid'),
    path('electricty/ikedc-postpaid', views.IKEDCPostPaid, name='ikedc_postpaid'),
]