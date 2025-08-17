import requests
from django.conf import settings

def makeVTpassRequest(phone, amount):
    headers = {
        "Authorization": f"Bearer{settings.SMEPLUG_API_KEY}",
        'Content-Type': "application/json"
    }
    payload = {
        "network": "mtn",
        "phone": phone,
        "amount": amount
    }
    try:
        url = f"{settings.SMEPLUG_BASE}/airtime/purchase"
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    except requests.RequestException as e:
        return {"status": "error", "messages": str(e)}
