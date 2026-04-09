import json
from datetime import datetime, timedelta

import requests
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from ..forms import TripclosurefilesForm,TripclosureaddForm
from ..models import RtratemasterInfo,User_extInfo,Trip_closure_files_Info,EnquirynoteInfo,TripdetailInfo,Tripstatusinfo
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.http import JsonResponse
from ..sub_models.haltingcharges_mod import Haltingcharges
from ..models import EnquirynoteInfo

from django.core.paginator import Paginator


@login_required(login_url='login_page')
def tripclosure_enquiry(request,enquiry_id,trip_num):
    # Fetch the enquiry object (optional - only needed if you want to verify or log it)
    enquiry = get_object_or_404(EnquirynoteInfo, pk=enquiry_id)
    print('enquiry_id',enquiry_id)
    print('trip_num',trip_num)
    # If no trip is associated, store enquiry ID in session and redirect to insert
    if trip_num == 'none' or trip_num == '':
        request.session['ses_enqiury_id'] = enquiry_id
        return redirect('tripclosure_insert')  # Define this URL in urls.py
    else:
        trip_id = TripdetailInfo.objects.get(tr_tripnumber=trip_num).id
        print('trip_id:', trip_id)
        # If trip_id is provided, redirect to update
        return redirect('tripclosure_update', tripclosure_id=trip_id)  # tripdetail_id is a keyword argument in the URL
@login_required(login_url='login_page')
def tripclosure_nav(request,tripclosure_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print("I a m inside Get add tripclosure")
    tripclosure_form = TripclosureaddForm(request.POST)
    tripclosurefiles_form = TripclosurefilesForm(request.POST,request.FILES)
    enquiry_num = EnquirynoteInfo.objects.get(pk=tripclosure_id).en_enquirynumber
    enquiry_num_id = EnquirynoteInfo.objects.get(pk=tripclosure_id).id
    request.session['ses_enqiury_id'] = enquiry_num
    tripclosure_list=TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num_id)
    status_list = Tripstatusinfo.objects.filter(id__in=[4,5,6,7])
    context = {
        'first_name': first_name,
        'user_id': user_id,
        'tripclosure_form': tripclosure_form,
        'tripclosurefiles_form': tripclosurefiles_form,
        'enquiry_num': enquiry_num,
        'tripclosure_list': tripclosure_list,
        'status_list': status_list,
    }
    if tripclosure_form.is_valid():
        tripclosure_form.save()
        print("Main Form is Valid")
        tripclosure_list = TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num).values_list('tr_tripnumber', flat=True)
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_tripclosure=list(tripclosure_list))
        messages.success(request, 'Record Updated Successfully')
    else:
        print("Main Form is not Valid")
        messages.error(request, 'Record Not Saved.Please Enter All Required Fields')

    if tripclosurefiles_form.is_valid():
        tripclosurefiles_form.save()
        messages.success(request, 'Record Updated Successfully')
        print("Trip Closure files Form Saved")
    else:
        messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
        print("Trip Closure files Form not Saved")
    return render(request, "asset_mgt_app/tripclosure_add.html", context)

@login_required(login_url='login_page')
def tripclosure_add(request,tripclosure_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    if request.method == "GET":
        print("I am inside Get edit Trip Closure")
        if tripclosure_id == 0:
            enquiry_num = TripdetailInfo.objects.get(pk=tripclosure_id).tr_enquirynumber
            print("I am inside Get add Tripclosure")
            tripclosure_form = TripclosureaddForm()
            tripclosurefiles_form = TripclosurefilesForm()
            status_list = list(Tripstatusinfo.objects.filter(id__in=[4,5,6,7]))
            context = {
                'tripclosure_form': tripclosure_form,
                'tripclosurefiles_form': tripclosurefiles_form,
                'first_name': first_name,
                'enquiry_num': enquiry_num,
                'status_list': status_list,
            }
        else:
            trip_num = TripdetailInfo.objects.get(pk=tripclosure_id).tr_tripnumber
            print("Inside Trip closure edit")
            enquiry_num = TripdetailInfo.objects.get(pk=tripclosure_id).tr_enquirynumber
            enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
            consignment_num = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).en_consignmentdetails
            tripclosure = TripdetailInfo.objects.get(tr_tripnumber=trip_num)
            tripclosure_form = TripclosureaddForm(instance=tripclosure)
            tripclosure_files = Trip_closure_files_Info.objects.filter(tcf_tripnumber=trip_num).first()
            tripclosurefiles_form = TripclosurefilesForm(instance=tripclosure_files)
            trip = TripdetailInfo.objects.get(pk=tripclosure_id)

            status_selected = (
                trip.tc_financestatus.id
                if trip.tc_financestatus
                else None
            )
            status_list = list(Tripstatusinfo.objects.filter(id__in=[4,5,6,7]))
            context = {
                'tripclosure_form': tripclosure_form,
                'tripclosurefiles_form': tripclosurefiles_form,
                'first_name': first_name,
                'enquiry_num': enquiry_num,
                'consignment_num': consignment_num,
                'user_id': user_id,
                'role': role,
                'status_list': status_list,
                'status_selected': status_selected,
                'tripclosure_list': TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num),
            }
        return render(request, "asset_mgt_app/tripclosure_add.html", context)
    else:
        if tripclosure_id == 0:
            print("Inside Trip closure post add")
            tripclosure_form = TripclosureaddForm(request.POST)
            tripclosurefiles_form = TripclosurefilesForm(request.POST,request.FILES)
            if tripclosure_form.is_valid():
                tripclosure_form.save()
                print("Trip Closure Main Form Saved")
            else:
                print("Trip Closure Main Form not Saved")

            if tripclosurefiles_form.is_valid():
                tripclosurefiles_form.save()
                print("Trip Closure files Form Saved")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Trip Closure files Form not Saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
            return redirect(request.META['HTTP_REFERER'])
        else:
            print("Inside Trip closure post edit")
            trip_num = TripdetailInfo.objects.get(pk=tripclosure_id).tr_tripnumber
            tripclosure = TripdetailInfo.objects.get(tr_tripnumber=trip_num)
            tripclosure_form = TripclosureaddForm(request.POST,instance=tripclosure)
            tripclosure_files = Trip_closure_files_Info.objects.filter(tcf_tripnumber=trip_num).first()
            tripclosurefiles_form = TripclosurefilesForm(request.POST,request.FILES,instance=tripclosure_files)

            if tripclosure_form.is_valid():
                tripclosure_form.save()
                print("Trip Closure Main Form Saved")
                enquiry_num = TripdetailInfo.objects.get(pk=tripclosure_id).tr_enquirynumber
                enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
                tripclosure_list = TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num_id).values_list(
                    'tc_financestatus', flat=True)
                tripclousre_status = []
                for i in tripclosure_list:
                    tripclousre_status.append(Tripstatusinfo.objects.get(id=i).status)
                EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_tripclosure=tripclousre_status)
            else:
                print("Trip Closure Main Form not Saved")

            if tripclosurefiles_form.is_valid():
                tripclosurefiles_form.save()
                print("Trip Closure files Form Saved")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Trip Closure files Form not Saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
            return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/enquirynote_list')

@login_required(login_url='login_page')
def tripclosure_list(request):
    first_name = request.session.get('first_name')
    branch = request.GET.get('branch', '')
    selected_status = request.GET.get('trip_status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    status_list = Tripstatusinfo.objects.filter(id__in=[4, 5, 6, 7])

    context = {
        'first_name': first_name,
        'branch': branch,
        'status_list': status_list,
        'selected_status': int(selected_status) if selected_status else None,
        'date_from': date_from,
        'date_to': date_to,
    }

    return render(request, "asset_mgt_app/tripclosure_list.html", context)


@login_required(login_url='login_page')
def tripclosure_list_ajax(request):
    """Server-side DataTables AJAX endpoint for Trip Closure List."""
    from django.db.models import Q

    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 50))
    search_value = request.GET.get('search[value]', '').strip()

    branch = request.GET.get('branch', '').strip()
    selected_status = request.GET.get('trip_status', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    qs = TripdetailInfo.objects.select_related(
        'tr_enquirynumber', 'tr_consignmentnumber', 'tc_financestatus'
    ).all()

    # Branch filter
    if branch == 'MAA':
        qs = qs.filter(tr_consignmentnumber__co_consignmentnumber__icontains='MAA')
    elif branch == 'BLR':
        qs = qs.filter(tr_consignmentnumber__co_consignmentnumber__icontains='BLR')

    if selected_status:
        qs = qs.filter(tc_financestatus_id=selected_status)

    if date_from:
        qs = qs.filter(tr_created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(tr_created_at__date__lte=date_to)

    records_total = qs.count()

    # Global search
    if search_value:
        qs = qs.filter(
            Q(tr_tripnumber__icontains=search_value) |
            Q(tr_enquirynumber__en_enquirynumber__icontains=search_value) |
            Q(tr_consignmentnumber__co_consignmentnumber__icontains=search_value) |
            Q(tc_financestatus__status__icontains=search_value)
        )

    records_filtered = qs.count()

    # Ordering
    order_col = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'desc')
    col_map = {
        0: 'tr_created_at',
        1: 'tr_enquirynumber__en_enquirynumber',
        2: 'tr_consignmentnumber__co_consignmentnumber',
        3: 'tr_tripnumber',
        4: 'tc_tripcost',
        5: 'tc_parkingcost',
        6: 'tc_tollcost',
        7: 'tc_loadingcost',
        8: 'tc_unloadingcost',
        9: 'tc_weighmentcost',
        10: 'tc_handlingcost',
        11: 'tc_pod',
        12: 'tc_financestatus__status',
    }
    order_field = col_map.get(order_col, 'id')
    if order_dir == 'desc':
        order_field = '-' + order_field
    qs = qs.order_by(order_field)

    if length != -1:
        qs = qs[start:start + length]
    else:
        qs = qs[start:]

    data = []
    for t in qs:
        data.append([
            t.tr_created_at.strftime('%Y-%m-%d') if t.tr_created_at else '',
            str(t.tr_enquirynumber) if t.tr_enquirynumber else '',
            str(t.tr_consignmentnumber) if t.tr_consignmentnumber else '',
            t.tr_tripnumber or '',
            str(t.tc_tripcost) if t.tc_tripcost is not None else '0',
            str(t.tc_parkingcost) if t.tc_parkingcost is not None else '0',
            str(t.tc_tollcost) if t.tc_tollcost is not None else '0',
            str(t.tc_loadingcost) if t.tc_loadingcost is not None else '0',
            str(t.tc_unloadingcost) if t.tc_unloadingcost is not None else '0',
            str(t.tc_weighmentcost) if t.tc_weighmentcost is not None else '0',
            str(t.tc_handlingcost) if t.tc_handlingcost is not None else '0',
            str(t.tc_pod) if t.tc_pod else '',
            str(t.tc_financestatus) if t.tc_financestatus else '',
            t.id,  # for edit URL (index 13)
            t.id,  # for delete URL (index 14)
        ])

    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data,
    })


#Delete tripclosure
@login_required(login_url='login_page')
def tripclosure_delete(request,tripclosure_id):
    tripclosure = TripdetailInfo.objects.get(pk=tripclosure_id)
    tripclosure.delete()
    return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/tripclosure_list')
@login_required(login_url='login_page')
def transport_calculate_trip_charges(request):
    # Retrieve parameters from the AJAX request
    from_location_id = request.GET.get('from_location')
    to_location_id = request.GET.get('to_location')
    vehicle_type_id = request.GET.get('vehicle_type')

    enquiry_number_id = request.GET.get('enquirynumber')
    trip_category_id = request.GET.get('trip_category')

    enquiry_number = EnquirynoteInfo.objects.get(pk=enquiry_number_id).en_enquirynumber
    customer_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_number).en_customername
    customer_department_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_number).en_customerdepartment
    # vehicle_category_id=EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_number).en_vehiclecategory

    if trip_category_id == '1':
        # Retrieve RoRateInfo based on the selected values
        try:
            ro_rate = RtratemasterInfo.objects.get(
                ro_fromlocation=from_location_id,
                ro_tolocation=to_location_id,
                ro_vehicletype=vehicle_type_id,
                ro_customer=customer_id,
                ro_customerdepartment=customer_department_id,
                # ro_vehiclecategory_id=vehicle_category_id
            ).ro_rate
            print('ro_rate',ro_rate)
            return JsonResponse({'ro_rate': ro_rate})

        except RtratemasterInfo.DoesNotExist:
            print("Doest not exist")
            # Handle the case where the RoRateInfo does not exist
            return JsonResponse({'ro_rate': 0})
    else:
        # Return 100 if trip_category is not 1
        return JsonResponse({'ro_rate': 100})

@csrf_exempt
@require_GET
def get_fastag_toll_cost_ajax(request):
    """
    AJAX endpoint to return FASTag toll cost details for a trip.
    """
    result = {"success": False, "error": None, "total_amount": 0.0, "txn_list": []}

    trip_num = request.GET.get('trip_num')
    if not trip_num:
        result["error"] = "Trip number not provided."
        return JsonResponse(result)

    try:
        trip = TripdetailInfo.objects.get(tr_tripnumber=trip_num)
        vehicle_num = trip.tr_vehiclenumber
        from_date = trip.tr_departeddate
        to_date = trip.tr_reporteddate

        total_amount, txn_list = calculate_toll(vehicle_num, from_date, to_date)

        result["success"] = True
        result["total_amount"] = total_amount
        result["txn_list"] = txn_list

    except TripdetailInfo.DoesNotExist:
        result["error"] = "Trip not found."
    except Exception as e:
        result["error"] = str(e)

    return JsonResponse(result, safe=False)


def calculate_toll(vehicle_num, from_date, to_date):
    """
    Calls HDFC FASTag toll API and calculates total toll cost.
    """
    txn_list = []
    total_amount = 0.0

    # Convert dates to required format
    from_date_str = from_date.strftime("%Y%m%d %H%M%S")
    to_date_str = to_date.strftime("%Y%m%d %H%M%S")
    contact = "9677022115"

    print(f"🔹 Fetching toll data for vehicle {vehicle_num} from {from_date_str} to {to_date_str}")

    payload = {
        "requestID": datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3],
        "requestTime": datetime.now().strftime("%Y%m%d%H%M"),
        "merchantID": "HDFCWL",
        "walletId": "W0122122713156600041",
        "requestSource": "BD",
        "fromDate": from_date_str,
        "toDate": to_date_str,
        "vehicleNumber": vehicle_num.strip(),
        "contactNumber": contact
    }

    headers = {
        "Authorization": "C223611027:95ef659313847c7485d43d66b8c5b9e8b817c9c136d2798333c5df693b6efc2a",
        "Content-Type": "application/json",
        "salt": "95ef659313847c7485d43d66b8c5b9e8b817c9c136d2798333c5df693b6efc2a"
    }

    try:
        response = requests.post(
            "https://corptag.hdfc.bank.in/walletmware/api/wallet/txn/tollenquiry",
            json=payload,
            headers=headers,
            timeout=20
        )

        print(f"🌐 FASTag API Response Status: {response.status_code}")

        if response.status_code == 200:
            try:
                api_data = response.json()
            except ValueError:
                print("❌ API did not return valid JSON. Response was:")
                print(response.text[:300])
                return 0.0, []

            res_code = api_data.get("resCode", "").strip().upper()
            res_msg = api_data.get("resMessage", "")
            txn_list = api_data.get("data", [])

            print(f"resCode={res_code}, Message={res_msg}, Transactions={len(txn_list)}")

            if res_code == "SUCCESS" and isinstance(txn_list, list):
                for idx, txn in enumerate(txn_list):
                    try:
                        amount = float(txn.get("txnAmt", 0))
                        total_amount += amount
                        print(f"  ✅ {txn.get('tollplazaname', '')}: ₹{amount}")
                    except Exception as e:
                        print(f"  ⚠️ Failed to parse txnAmt for {txn}: {e}")
            else:
                print(f"⚠️ API returned error: {res_msg}")
        else:
            print(f"❌ API returned HTTP {response.status_code}")
            print(response.text[:300])

    except requests.exceptions.RequestException as e:
        print("❌ Request failed:", str(e))

    print(f"✅ Total toll amount for {vehicle_num}: ₹{total_amount}")
    return total_amount, txn_list


@login_required(login_url='login_page')
def get_halting_charge(request):
    enquiry_id = request.GET.get('enquiry_id')
    trip_type_id = request.GET.get('trip_type')

    print("==============================================")
    print("🔍 Enquiry ID Received:", enquiry_id)
    print("🔍 Trip Type ID Received:", trip_type_id)
    print("==============================================")

    if not enquiry_id:
        print("❌ enquiry_id missing!")
        return JsonResponse({'status': False, 'halting_charge': 0})

    try:
        enquiry = EnquirynoteInfo.objects.get(pk=enquiry_id)
        customer_id = enquiry.en_customername_id
        print("✅ Customer ID fetched:", customer_id)
    except EnquirynoteInfo.DoesNotExist:
        print("❌ Enquiry not found by ID")
        return JsonResponse({'status': False, 'halting_charge': 0})

    try:
        halting = Haltingcharges.objects.get(
            hc_Customer_name=customer_id,
            hc_trip_type=trip_type_id
        )
        print("🎉 Halting Charge Found:", halting.hc_charges)
        return JsonResponse({'status': True, 'halting_charge': halting.hc_charges})

    except Haltingcharges.DoesNotExist:
        print("❌ No halting match found")
        return JsonResponse({'status': False, 'halting_charge': 0})


@login_required(login_url='login_page')
def get_cancellation_charge(request):
    """
    Returns the cancellation charge from ChargeMasterInfo
    based on the enquiry's customer and the trip's vehicle type.
    Charge type ID 1 = 'Cancellation charge'
    """
    from ..sub_models.charge_master_mod import ChargeMasterInfo

    enquiry_id = request.GET.get('enquiry_id')
    vehicle_type_id = request.GET.get('vehicle_type_id')

    if not enquiry_id or not vehicle_type_id:
        return JsonResponse({'status': False, 'cancellation_charge': 0})

    try:
        enquiry = EnquirynoteInfo.objects.get(pk=enquiry_id)
        customer_id = enquiry.en_customername_id
    except EnquirynoteInfo.DoesNotExist:
        return JsonResponse({'status': False, 'cancellation_charge': 0})

    try:
        charge = ChargeMasterInfo.objects.get(
            cm_customer_id=customer_id,
            cm_vehicle_type_id=vehicle_type_id,
            cm_charge_type_id=1  # Cancellation charge
        )
        return JsonResponse({'status': True, 'cancellation_charge': charge.cm_amount})
    except ChargeMasterInfo.DoesNotExist:
        return JsonResponse({'status': False, 'cancellation_charge': 0})
