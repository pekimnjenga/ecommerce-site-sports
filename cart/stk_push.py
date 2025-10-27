import base64
import json
import logging
from datetime import datetime

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def get_access_token():
    url = f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(
        url, auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET)
    )

    try:
        data = response.json()
        return data.get("access_token")
    except ValueError:
        print("Access token response was not valid JSON:", response.text)
        return None


def initiate_stk_push(phone_number, amount, account_reference, transaction_desc):
    access_token = get_access_token()
    if not access_token:
        print("Failed to retrieve access token.")
        return {}

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()
    ).decode()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": float(amount),
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc,
    }

    logger.info("Actual STK Push payload: %s", json.dumps(payload, indent=2))

    url = f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest"
    response = requests.post(url, json=payload, headers=headers)

    try:
        return response.json()
    except ValueError:
        print("STK Push response was not valid JSON:", response.text)
        return {}
