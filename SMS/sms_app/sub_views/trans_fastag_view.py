# views.py
import requests
import hmac
import hashlib
from django.shortcuts import render
from datetime import datetime
from ..forms import trans_fastag_form

WALLET_ID = "W0122122713156600041"
MERCHANT_ID = "HDFCWL"
REQUEST_SOURCE = "SPINC"
SECRET_KEY = "OnePay#Test123"

def generate_checksum(message: str, secret_key: str) -> str:
    byte_key = secret_key.encode()
    message = message.encode()
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
                "merchantID": MERCHANT_ID,
                "walletId": WALLET_ID,
                "requestSource": REQUEST_SOURCE,
                "fromDate": from_date,
                "toDate": to_date,
                "vehicleNumber": vehicle,
                "contactNumber": contact
            }
            # Generate checksum
            checksum_input = request_id + WALLET_ID + request_time + MERCHANT_ID + REQUEST_SOURCE
            checksum = generate_checksum(checksum_input, SECRET_KEY)

            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'onepay:{checksum}'
            }

            # Debug logs (optional)
            print("Payload:", payload)
            print("Checksum string:", checksum_input)
            print("Generated checksum:", checksum)

            try:
                response = requests.post(
                    "https://1paytag.hdfcbank.com/walletmware/api/wallet/txn/tollenquiry",
                    json=payload,
                    headers=headers
                )
                result = response.json()
                print("API response:", result)
            except requests.exceptions.RequestException as e:
                result = {"error": str(e)}
    else:
        form = trans_fastag_form()

    return render(request, 'asset_mgt_app/trans_fastag_add.html', {'form': form, 'result': result})
