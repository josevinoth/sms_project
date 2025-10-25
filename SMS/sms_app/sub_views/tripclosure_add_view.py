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
            status_selected = (TripdetailInfo.objects.get(pk=tripclosure_id).tc_financestatus.id)
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

# List tripclosure
@login_required(login_url='login_page')
def tripclosure_list(request):
    first_name = request.session.get('first_name')
    context = {'tripclosure_list' : TripdetailInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/tripclosure_list.html",context)

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
    vehicle_category_id=EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_number).en_vehiclecategory

    if trip_category_id == '1':
        # Retrieve RoRateInfo based on the selected values
        try:
            ro_rate = RtratemasterInfo.objects.get(
                ro_fromlocation=from_location_id,
                ro_tolocation=to_location_id,
                ro_vehicletype=vehicle_type_id,
                ro_customer=customer_id,
                ro_customerdepartment=customer_department_id,
                ro_vehiclecategory_id=vehicle_category_id
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
    result = {}
    txn_list = []
    total_amount = 0.0
    from_date_str = from_date.strftime("%Y%m%d %H%M%S")
    print(from_date_str)
    to_date_str = to_date.strftime("%Y%m%d %H%M%S")
    print(to_date_str)
    print(vehicle_num.strip())
    contact = "9677022115"
    print(contact)
    payload = {
        "requestID": datetime.now().strftime("%Y%m%d%H%M%S%f"),
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
    print(f"Total toll amount for vehicle {vehicle_num}: {total_amount}")
    return total_amount,txn_list
