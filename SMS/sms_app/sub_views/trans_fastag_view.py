# views.py
import requests
import hmac
import hashlib
from django.shortcuts import render
from datetime import datetime
from ..forms import trans_fastag_form
from decouple import config

WALLET_ID = config("FASTAG_WALLET_ID")
MERCHANT_ID = config("FASTAG_MERCHANT_ID")
REQUEST_SOURCE = config("FASTAG_SOURCE")
SECRET_KEY = config("FASTAG_SECRET")

def generate_checksum(message: str, secret: str) -> str:
    byte_key = bytes(secret, 'utf-8')
    message = bytes(message, 'utf-8')
    return hmac.new(byte_key, message, hashlib.sha256).hexdigest().upper()

def fastag_enquiry_view(request):
    result = None
    if request.method == 'POST':
        form = trans_fastag_form(request.POST)
        if form.is_valid():
            vehicle = form.cleaned_data['vehicleNumber']
            contact = form.cleaned_data['contactNumber']
            from_date = form.cleaned_data['fromDate'].strftime("%Y%m%d")
            to_date = form.cleaned_data['toDate'].strftime("%Y%m%d")

            request_id = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
            request_time = datetime.now().strftime("%Y%m%d%H%M")

            # Prepare payload
            payload = {
                "requestID": request_id,
                "requestTime": request_time,
                "merchantID": MERCHANT_ID,  # e.g., HDFCWL
                "walletId": WALLET_ID,
                "requestSource": REQUEST_SOURCE,  # e.g., SPINC
                "fromDate": from_date,
                "toDate": to_date,
                "vehicleNumber": vehicle,
                "contactNumber": contact
            }

            # ✅ Add this here — checksum calculation
            message = request_id + WALLET_ID + request_time + MERCHANT_ID + REQUEST_SOURCE
            checksum = generate_checksum(message, SECRET_KEY)

            # Prepare headers with calculated checksum
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'onepay:{checksum}'
            }

            # Send the request
            try:
                response = requests.post(
                    "https://1paytag.hdfcbank.com/walletmware/api/wallet/txn/tollenquiry",
                    json=payload,
                    headers=headers
                )
                result = response.json()
                print("RAW API RESPONSE:", response.text)
            except requests.exceptions.RequestException as e:
                result = {"error": str(e)}
    else:
        form = trans_fastag_form()

    return render(request, 'asset_mgt_app/trans_fastag_add.html', {'form': form, 'result': result})

