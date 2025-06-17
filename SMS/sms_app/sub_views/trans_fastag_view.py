import requests
import hmac
import hashlib
from django.shortcuts import render
from datetime import datetime
from decouple import config
from ..forms import trans_fastag_form

# Load from .env
WALLET_ID = config("FASTAG_WALLET_ID")
MERCHANT_ID = config("FASTAG_MERCHANT_ID")
REQUEST_SOURCE = config("FASTAG_SOURCE", default="BD")
SECRET_KEY = config("FASTAG_SECRET")

def generate_checksum(message: str, secret: str) -> str:
    return 'C223611027:95ef659313847c7485d43d66b8c5b9e8b817c9c136d2798333c5df693b6efc2a'

def fastag_enquiry_view(request):
    result = {}
    txn_list = []
    total_amount = 0
    toll_count = 0

    if request.method == 'POST':
        form = trans_fastag_form(request.POST)
        if form.is_valid():
            vehicle = form.cleaned_data['vehicleNumber'].strip()
            contact = form.cleaned_data['contactNumber'].strip()
            from_date = form.cleaned_data['fromDate'].strftime("%Y%m%d") + " 000000"
            to_date = form.cleaned_data['toDate'].strftime("%Y%m%d") + " 235959"

            request_id = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
            request_time = datetime.now().strftime("%Y%m%d%H%M")

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

            # Prepare message for checksum
            message = request_id + WALLET_ID + request_time + MERCHANT_ID + REQUEST_SOURCE
            checksum = generate_checksum(message, SECRET_KEY)

            headers = {
                'Authorization': f'onepay:{checksum}',
                'Content-Type': 'application/json'
            }

            try:
                response = requests.post(
                    "https://1paytag.hdfcbank.com/walletmware/api/wallet/txn/tollenquiry",
                    json=payload,
                    headers=headers,
                    timeout=15
                )

                if response.status_code == 200:
                    try:
                        result = response.json()
                    except Exception:
                        result = {"error": "Failed to decode JSON from API."}
                        return render(request, 'asset_mgt_app/trans_fastag_add.html', {
                            'form': form, 'result': result
                        })

                    # Handle success and fallback messages
                    if result.get("resCode") == "WMESUC001":
                        txn_list = result.get("data", [])
                        toll_count = len(txn_list)
                        total_amount = sum(float(txn.get("amount", 0)) for txn in txn_list)
                        result["success"] = result.get("resMessage", "Success")
                    else:
                        result["error"] = result.get("resMessage", "No transactions found.")

                else:
                    result = {"error": f"API returned status {response.status_code}: {response.text}"}

            except requests.exceptions.RequestException as e:
                result = {"error": str(e)}

    else:
        form = trans_fastag_form()

    return render(request, 'asset_mgt_app/trans_fastag_add.html', {
        'form': form,
        'result': result,
        'txn_list': txn_list,
        'toll_count': toll_count,
        'total_amount': total_amount
    })
