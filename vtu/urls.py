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
    path("verify-iuc/", views.verify_iuc, name="verify_iuc"),
    path('tv/dstv/', views.DSTV, name='dstv'),
    path('tv/gotv/', views.GOTV, name='gotv'),
    path('tv/startime/', views.STARTIME, name='startime'),
    

    # ELECTRICITY
    path("verify-meter/", views.verify_meter, name="verify_iuc"),
    path('electricty/ikedc', views.IKEDC, name='ikedc'),
    path('electricty/ekedc', views.EKEDC, name='ekedc'),
    path('electricty/aedc', views.AEDC, name='aedc'),
    path('electricty/kaduna', views.KADUNA, name='kaduna'),
    path('electricty/ibedc', views.IBEDC, name='ibedc'),
    path('electricty/jos', views.JOS, name='jos'),

]