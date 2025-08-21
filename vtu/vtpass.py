import requests
import uuid
from django.conf import settings
from requests.auth import HTTPBasicAuth

def purchaseAirtime(phone, amount):
    url = f"{settings.VTPASS_BASE_URL}/pay"
    request_id = str(uuid.uuid4())  # unique transaction ID

    payload = {
        "serviceID": "etisalat",
        "amount": amount,
        "phone": phone,
        "request_id": request_id,
    }
    header = {
        "api-key":"cc969077fc1e06af06d73356bd05505b",
        "secret-key": "SK_317f59f75699dfee4d534955d4012d2947171d69cb1"
    }

    response = requests.post(
        url,
        json=payload,
        headers=header,
        timeout=30
    )

    return response.json()
