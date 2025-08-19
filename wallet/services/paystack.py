import requests
import os

PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")
BASE_URL = "https://api.paystack.co"

headers = {
    "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
    "Content-Type": "application/json"
}

def create_dedicated_account(customer_email, first_name, last_name, user_id):
    """
    Create a Paystack dedicated virtual account for a user.
    """
    url = f"{BASE_URL}/dedicated_account"
    payload = {
        "customer": customer_email,
        "preferred_bank": "wema-bank",  # You can change bank e.g. providus-bank
        "first_name": first_name,
        "last_name": last_name,
        "phone": "08012345678",
        "metadata": {
            "user_id": user_id
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()
