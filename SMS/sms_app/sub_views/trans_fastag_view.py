import requests
from django.shortcuts import render
from datetime import datetime
from ..forms import trans_fastag_form  # Adjust import if needed

def fastag_enquiry_view(request):
    result = {}
    txn_list = []
    total_amount = 0.0
    toll_count = 0

    if request.method == 'POST':
        form = trans_fastag_form(request.POST)
        if form.is_valid():
            vehicle = form.cleaned_data['vehicleNumber'].strip()
            contact = form.cleaned_data['contactNumber'].strip()
            from_date = form.cleaned_data['fromDate'].strftime("%Y%m%d %H%M%S")
            to_date = form.cleaned_data['toDate'].strftime("%Y%m%d %H%M%S")

            print("From DateTime for API:", from_date)
            print("To DateTime for API:", to_date)

            payload = {
                "requestID": datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3],
                "requestTime": datetime.now().strftime("%Y%m%d%H%M"),
                "merchantID": "HDFCWL",
                "walletId": "W0122122713156600041",
                "requestSource": "BD",
                "fromDate": from_date,
                "toDate": to_date,
                "vehicleNumber": vehicle,
                "contactNumber": contact
            }

            headers = {
                'Authorization': 'C223611027:95ef659313847c7485d43d66b8c5b9e8b817c9c136d2798333c5df693b6efc2a',
                'Content-Type': 'application/json',
                'salt': '95ef659313847c7485d43d66b8c5b9e8b817c9c136d2798333c5df693b6efc2a'
            }

            try:
                response = requests.post(
                    "https://1paytag.hdfcbank.com/walletmware/api/wallet/txn/tollenquiry",
                    json=payload,
                    headers=headers,
                    timeout=15
                )

                if response.status_code == 200:
                    api_data = response.json()
                    res_code = api_data.get("resCode", "").strip().upper()
                    res_msg = api_data.get("resMessage", "")
                    txn_list = api_data.get("data", [])
                    print("DEBUG resCode:", repr(api_data.get("resCode")))
                    print("DEBUG resMessage:", repr(api_data.get("resMessage")))
                    print("DEBUG txn_list type:", type(api_data.get("data")))

                    print(f"res_code = {res_code}, txn_list count = {len(txn_list)}")

                    if res_code in [res_code, "SUCCESS"] and isinstance(txn_list, list):
                        toll_count = len(txn_list)
                        total_amount = 0.0

                        for idx, txn in enumerate(txn_list):
                            raw_amt = txn.get("txnAmt", "0")
                            try:
                                amount = float(str(raw_amt).strip())
                                print(f"[{idx}] txnAmt = {amount}")
                                total_amount += amount
                            except Exception as e:
                                print(f"[{idx}] Failed to parse txnAmt={raw_amt}: {e}")

                        result["success"] = f"{res_msg}: {toll_count} transactions"
                        result["error"] = None
                    else:
                        result["success"] = None
                        result["error"] = f"API ERROR: {res_msg or 'No message'}"
                else:
                    result = {
                        "success": None,
                        "error": f"API returned status {response.status_code}: {response.text}"
                    }

            except requests.exceptions.RequestException as e:
                result = {"success": None, "error": str(e)}
    else:
        form = trans_fastag_form()

    print("✅ Final total_amount to template:", total_amount)

    return render(request, 'asset_mgt_app/trans_fastag_add.html', {
        'form': form,
        'result': result,
        'txn_list': txn_list,
        'toll_count': toll_count,
        'total_amount': total_amount,
    })
