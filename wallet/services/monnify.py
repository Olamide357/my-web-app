import requests
from django.conf import settings
import base64

def get_monnify_token():
    key_secret = f"{settings.MONNIFY_API_KEY}:{settings.MONNIFY_SECRET_KEY}"
    token_bytes = base64.b64encode(key_secret.encode("utf-8"))
    token_str = token_bytes.decode("utf-8")
    
    headers = {
        "Authorization": f"Basic {token_str}",
        "Content-Type": "application/json"
    }
    url = "https://api.monnify.com/api/v1/auth/login"  # use live URL in production
    response = requests.post(url, headers=headers)
    data = response.json()
    if data.get("responseMessage") == "success":
        return data["responseBody"]["accessToken"]
    raise Exception("Monnify authentication failed")

def create_virtual_account(user, wallet):
    """
    Create a virtual account for a user
    """
    token = get_monnify_token()
    url = "https://api.monnify.com/api/v2/bank-transfer/reserved-accounts"  # live: change domain
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "accountName": f"{user.username} Wallet",
        "currencyCode": "NGN",
        "contractCode": settings.MONNIFY_CONTRACT_CODE,
        "customerEmail": user.email,
        "customerName": user.username,
        "preferredBanks": ["058"],  # optional: bank codes, e.g., Wema Bank=058
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    if data["responseMessage"] == "success":
        acct_data = data["responseBody"]
        wallet.account_number = acct_data["accountNumber"]
        wallet.account_name = acct_data["accountName"]
        wallet.bank_name = acct_data["bankName"]
        wallet.monnify_customer_id = acct_data["customerId"]
        wallet.save()
        return acct_data
    else:
        raise Exception(f"Monnify account creation failed: {data}")
