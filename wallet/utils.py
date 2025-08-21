import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def create_dva(profile):
    """
    Assign a Paystack Dedicated Virtual Account to a user profile.
    """
    url = "https://api.paystack.co/dedicated_account/assign"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "email": profile.user.email,
        "first_name": profile.user.username,  # since you only have username
        "last_name": "User",                  # optional placeholder
        "phone": profile.phone,
        "preferred_bank": settings.PREFERRED_BANK_SLUG,  # e.g., "wema-bank"
        "country": "NG"  # Nigeria
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        logger.info(f"DVA response: {data}")

        if data['status']:
            profile.virtual_account_status = 'assigning'
            profile.paystack_customer_code = data['data']['customer']['customer_code']
            profile.save()
        else:
            logger.error(f"DVA creation failed: {data.get('message')}")

    except requests.exceptions.RequestException as e:
        logger.error(f"DVA request error: {str(e)}")
