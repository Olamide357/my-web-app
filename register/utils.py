import requests
from django.conf import settings

def create_paystack_customer(email, first_name="", last_name=""):
    url = "https://api.paystack.co/customer"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
    }

    response = requests.post(url, headers=headers, json=data)
    res_data = response.json()

    if res_data.get("status"):
        return res_data["data"]["customer_code"]
    else:
        raise Exception(f"Paystack customer creation failed: {res_data}")
