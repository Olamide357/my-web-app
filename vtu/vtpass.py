import requests
import uuid
from django.conf import settings
from requests.auth import HTTPBasicAuth

def purchaseAirtime(phone, amount):
    url = f"{settings.VTPASS_BASE_URL}/pay"
    request_id = str(uuid.uuid4())  # unique transaction ID

    payload = {
        "serviceID": "mtn",
        "amount": amount,
        "phone": phone,
        "request_id": request_id,
    }
    header = {
        "api-key":"55eb5ed06fe22929ef41601db3956381",
        "secret-key": "SK_181f8acb7e54f463e3b936eb81136bd7e398324c780"
    }

    response = requests.post(
        url,
        json=payload,
        headers=header,
        timeout=30
    )

    return response.json()
