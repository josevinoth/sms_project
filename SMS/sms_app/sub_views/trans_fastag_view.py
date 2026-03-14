import requests
from django.shortcuts import render
from datetime import datetime
from ..forms import trans_fastag_form  # Adjust import if needed
from django.http import HttpResponse
from openpyxl import Workbook
from io import BytesIO
from ..models import TripdetailInfo  # Import for lookup

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
                    "https://corptag.hdfc.bank.in/walletmware/api/wallet/txn/tollenquiry",
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
        'vehicle': request.POST.get('vehicleNumber', ''),
        'contact': request.POST.get('contactNumber', ''),
        'fromDate': request.POST.get('fromDate', ''),
        'toDate': request.POST.get('toDate', ''),
    })

def trans_fastag_export_excel(request):
    vehicle = request.GET.get('vehicle', '').strip()
    contact = request.GET.get('contact', '').strip()
    from_date_str = request.GET.get('fromDate', '')
    to_date_str = request.GET.get('toDate', '')

    if not vehicle or not from_date_str or not to_date_str:
        return HttpResponse("Missing parameters", status=400)

    try:
        # Handle '2026-02-07T11:11' or '2026-02-07'
        if 'T' in from_date_str:
            from_date_obj = datetime.strptime(from_date_str, "%Y-%m-%dT%H:%M")
        else:
            from_date_obj = datetime.strptime(from_date_str, "%Y-%m-%d")

        if 'T' in to_date_str:
            to_date_obj = datetime.strptime(to_date_str, "%Y-%m-%dT%H:%M")
        else:
            to_date_obj = datetime.strptime(to_date_str, "%Y-%m-%d")
            
        from_date_api = from_date_obj.strftime("%Y%m%d %H%M00")
        to_date_api = to_date_obj.strftime("%Y%m%d %H%M59")
    except Exception as e:
        print(f"DEBUG: Date parsing error: {e}")
        return HttpResponse(f"Invalid date format: {e}", status=400)

    payload = {
        "requestID": datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3],
        "requestTime": datetime.now().strftime("%Y%m%d%H%M"),
        "merchantID": "HDFCWL",
        "walletId": "W0122122713156600041",
        "requestSource": "BD",
        "fromDate": from_date_api,
        "toDate": to_date_api,
        "vehicleNumber": vehicle,
        "contactNumber": contact
    }

    headers = {
        'Authorization': 'C223611027:95ef659313847c7485d43d66b8c5b9e8b817c9c136d2798333c5df693b6efc2a',
        'Content-Type': 'application/json',
        'salt': '95ef659313847c7485d43d66b8c5b9e8b817c9c136d2798333c5df693b6efc2a'
    }

    txn_list = []
    try:
        response = requests.post(
            "https://corptag.hdfc.bank.in/walletmware/api/wallet/txn/tollenquiry",
            json=payload,
            headers=headers,
            timeout=15
        )
        if response.status_code == 200:
            api_data = response.json()
            txn_list = api_data.get("data", [])
    except Exception:
        pass

    wb = Workbook()
    ws = wb.active
    ws.title = "Fastag Export"

    # Headers based on image (removed "Fastag format", added "NARRATION")
    headers = [
        "VOUCHER NUMBER", "DATE", "REF NO.", "SUNDRY CREDITORS", 
        "AMOUNT", "EXPENSES LEDGER", "AMOUNT", "PRIMARY COST CATEGORY", 
        "JOB NO", "VEH. NO.", "CUSTOMER", "NARRATION"
    ]
    ws.append(headers)

    # Column widths (shifted from B->A, E->D, etc.)
    ws.column_dimensions["A"].width = 25 # VOUCHER NUMBER
    ws.column_dimensions["D"].width = 20 # SUNDRY CREDITORS
    ws.column_dimensions["H"].width = 20 # PRIMARY COST CATEGORY
    ws.column_dimensions["I"].width = 20 # JOB NO
    ws.column_dimensions["K"].width = 25 # CUSTOMER
    ws.column_dimensions["L"].width = 30 # NARRATION

    def get_financial_year(date_obj):
        year = date_obj.year
        if date_obj.month >= 4:
            return f"{str(year)[2:]}{str(year+1)[2:]}"
        else:
            return f"{str(year-1)[2:]}{str(year)[2:]}"

    for idx, txn in enumerate(txn_list, 1):
        posted_time = txn.get("txnPostedtime", "")
        amt = txn.get("txnAmt", 0)
        
        try:
            # Format: '2026-03-02 14:30:00' or similar from API
            date_dt = datetime.strptime(posted_time, "%Y-%m-%d %H:%M:%S")
        except:
            date_dt = from_date_obj

        # Voucher Serial: Fst_MM_FY-001
        mm = date_dt.strftime("%m")
        fy = get_financial_year(date_dt)
        voucher_no = f"Fst_{mm}_{fy}-{str(idx).zfill(3)}"
        
        # Ref No: Apr-26
        ref_no = date_dt.strftime('%b-%y')

        # Lookup Trip details for metadata
        # Find trip starting before or on the transaction date with the same vehicle
        trip = TripdetailInfo.objects.filter(
            tr_vehiclenumber__iexact=vehicle,
            tr_departeddate__date__lte=date_dt.date()
        ).order_by('-tr_departeddate').first()

        primary_cost_category = ""
        job_no = ""
        customer_name = ""
        
        if trip:
            primary_cost_category = str(trip.tr_vehiclesource) if trip.tr_vehiclesource else ""
            job_no = str(trip.tr_consignmentnumber) if trip.tr_consignmentnumber else ""
            customer = None
            if trip.tr_enquirynumber:
                customer = trip.tr_enquirynumber.en_customername
            if customer:
                customer_name = customer.cu_name or customer.cu_name or ""

        row = [
            voucher_no,
            date_dt.strftime("%d/%m/%Y"),
            ref_no,
            "Fastag - Trans",
            amt,
            "Toll",
            amt,
            primary_cost_category,
            job_no,
            vehicle,
            customer_name,
            txn.get("tollplazaname", "")
        ]
        ws.append(row)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    filename = f"Fastag_{vehicle}_{from_date_str}_to_{to_date_str}.xlsx"
    response = HttpResponse(
        buffer.getvalue(), 
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
