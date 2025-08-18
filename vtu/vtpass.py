import requests
import uuid
from django.conf import settings

def purchaseAirtime(service_id, phone, amount):
    url = f"{settings.VTPASS_BASE_URL}/pay"
    headers = {
        "api-key": f"{settings.VTPASS_APIKEY}",
        "secret-key": f"{settings.VTPASS_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "serviceID": service_id,
        "amount": str(amount),
        "phone": phone,
        "request_id": str(uuid.uuid4())
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()