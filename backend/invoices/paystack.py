import requests
from django.conf import settings


PAYSTACK_BASE_URL = "https://api.paystack.co"


def initialize_transaction(email, amount_kobo, reference, callback_url=None):
    """
    Asks Paystack to start a payment session.
    amount_kobo: amount in the smallest currency unit (e.g. cents/kobo) - Paystack always expects this, never decimal amounts.
    Returns Paystack's response dict, which includes an 'authorization_url' the client opens to pay.
    """
    url = f"{PAYSTACK_BASE_URL}/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "email": email,
        "amount": amount_kobo,
        "reference": reference,
    }
    if callback_url:
        payload["callback_url"] = callback_url

    response = requests.post(url, json=payload, headers=headers)
    return response.json()


def verify_transaction(reference):
    """
    Confirms with Paystack whether a transaction actually succeeded.
    Never trust a client's claim that payment succeeded - always verify server-side.
    """
    url = f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    response = requests.get(url, headers=headers)
    return response.json()
