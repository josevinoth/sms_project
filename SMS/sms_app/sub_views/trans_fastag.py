# views.py
import requests
from django.shortcuts import render
from datetime import datetime
from ..forms import trans_fastag_form

AUTH_TOKEN = "C223611027:95ef659313847c7485d43d66b8c5b9e8b817c9c136d2798333c5df693b6efc2a"
WALLET_ID = "W0122122713156600041"

def fastag_enquiry_view(request):
    result = None
    if request.method == 'POST':
        form = trans_fastag_form(request.POST)
        if form.is_valid():
            vehicle = form.cleaned_data['vehicleNumber']
            contact = form.cleaned_data['contactNumber']
            from_date = form.cleaned_data['fromDate'].strftime("%Y%m%d 000000")
            to_date = form.cleaned_data['toDate'].strftime("%Y%m%d 235959")

            payload = {
                "requestID": datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3],
                "requestTime": datetime.now().strftime("%Y%m%d%H%M"),
                "merchantID": "HDFCWL",
                "walletId": WALLET_ID,
                "requestSource": "BD",
                "fromDate": from_date,
                "toDate": to_date,
                "vehicleNumber": vehicle,
                "contactNumber": contact
            }

            headers = {
                'Content-Type': 'application/json',
                'Authorization': AUTH_TOKEN
            }

            try:
                response = requests.post(
                    "https://1paytag.hdfcbank.com/walletmware/api/wallet/txn/tollenquiry",
                    json=payload,
                    headers=headers
                )
                result = response.json()
            except requests.exceptions.RequestException as e:
                result = {"error": str(e)}
    else:
        form = trans_fastag_form()

    return render(request, 'fastag/enquiry.html', {'form': form, 'result': result})
