import base64
import json
import logging
from datetime import datetime

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


# Authenticating my app with the MPESA Daraja API,so that I can use the STK Push API
# This function logs my app into the MPESA Daraja API and returns an access token that lets me make payment requests
# The first line builds the URL for the MPESA OAuth endpoint, which is used to get an access token.
##The second line sends a GET request to that URL, using the consumer key and secret for authentication.
##The response is expected to be a JSON object containing the access token, which is extracted and returned.
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


# The `initiate_stk_push` function is responsible for sending a payment request to the M-Pesa Daraja API so that the user receives an STK Push prompt on their phone.
# Here's a breakdown of what this function does:
# 1. **Gets an access token**
# Calls `get_access_token()` to authenticate and get a token needed for the API request.

# 2. **Prepares required data**
# - Generates a timestamp in the required format.
# - Creates a password by encoding your shortcode, passkey, and timestamp (as required by M-Pesa).

# 3. **Builds the request headers**
# - Includes the access token for authorization.
# - Sets the content type to JSON.

# 4. **Builds the request payload**
# - Includes all the information M-Pesa needs: business shortcode, password, timestamp, transaction type, amount, phone numbers, callback URL, account reference, and description.

# 5. **Sends the request**
# - Makes a POST request to the M-Pesa STK Push endpoint with the payload and headers.

# 6. **Returns the response**
# - Returns the JSON response from M-Pesa, which tells you if the request was accepted and provides a CheckoutRequestID for tracking.


### In summary:
# initiate_stk_push` is the function that actually **initiates the payment process**.
# It tells M-Pesa to send a payment prompt to the user's phone, so they can enter their PIN and complete the payment.


# Function of the payload dictionary
# `payload`, which is being prepared for an API request—most likely to the M-Pesa payment gateway for initiating an STK Push transaction. Each key in the dictionary corresponds to a required parameter for the M-Pesa API.
# - `"BusinessShortCode"` and `"PartyB"` are both set to `settings.MPESA_SHORTCODE`, which is typically the unique identifier assigned to the business by M-Pesa.
# - `"Password"` and `"Timestamp"` are security-related fields, usually generated dynamically to authenticate the request.
# - `"TransactionType"` is set to `"CustomerPayBillOnline"`, specifying the type of transaction being performed.
# - `"Amount"` is the transaction amount, and `"PartyA"` and `"PhoneNumber"` both refer to the customer's phone number that will receive the payment prompt.
# - `"CallBackURL"` is the endpoint where M-Pesa will send the transaction result.
# - `"AccountReference"` and `"TransactionDesc"` provide additional context for the transaction, such as a reference number and a description.

# This dictionary will likely be serialized to JSON and sent as the body of an HTTP POST request to the M-Pesa API. Each field must be correctly populated for the transaction to be processed successfully.

###Function of the last code segment
# This code segment is responsible for sending the STK Push payment request to the M-Pesa API and handling the response. First, it constructs the API endpoint URL by combining the base URL from your Django settings with the specific path for the STK Push process request. This ensures that the request is sent to the correct M-Pesa endpoint.
# Next, the code uses the `requests.post` method to send an HTTP POST request to the constructed URL. It includes the `payload` dictionary as the JSON body of the request and attaches the necessary HTTP headers (such as authorization and content type). This step actually initiates the payment process by communicating with the M-Pesa API.
# Finally, the function returns the JSON-decoded response from the API. This response typically contains information about whether the request was successful, along with details like a `CheckoutRequestID` that can be used to track the transaction status.
