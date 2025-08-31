from django.shortcuts import render

# Create your views here.

def buyAirtime(request):
    return render(request, "buy_airtime.html")

def buyData(request):
    return render(request, "buy_data.html")

def buyTV(request):
    return render(request, "cable_tv.html")

def buyElectricity(request):
    return render(request, "pay_electricity.html")

def balanceCode(request):
    return render(request, "balance_code.html")

def contactUS(request):
    return render(request, "contact_us.html")

def FAQ(request):
    return render(request, "faq.html")