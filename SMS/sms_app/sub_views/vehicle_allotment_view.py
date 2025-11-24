import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Q
from ..forms import VehicleallotmentForm
from ..models import Enquirynotevehicle,TripdetailInfo,OwnershipInfo,VehiclemasterInfo,EnquirynoteInfo,Vehicle_allotmentInfo,VendorratemasterInfo1, RtratemasterInfo
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .send_department_email import send_department_email

from ..sub_models.vendor_info_mod import Vendor_info


@login_required(login_url='login_page')
def vehicle_allotment_enquiry(request, enquiry_id, vehicle_number):
    # You can now use enquiry_id and vehicle_number
    enquiry = get_object_or_404(EnquirynoteInfo, pk=enquiry_id)
    print('vehicle_number',vehicle_number)
    try:
        vehicle_number_id = VehiclemasterInfo.objects.get(vm_registrationnumber=vehicle_number).id
    except VehiclemasterInfo.DoesNotExist:
        vehicle_number_id = None
    print('vehicle_number_id',vehicle_number_id)
    # Example: filter vehicle allotment by both
    vehicle_allotment = Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry).filter(Q(va_vehiclenumber_mkt=vehicle_number) | Q(va_vehiclenumber=vehicle_number_id)).first()  # get first matching record or None
    if vehicle_allotment:
        # Redirect to the update URL with the found vehicle_allotment id
        return redirect('vehicle_allotment_update', vehicle_allotment_id=vehicle_allotment.id)
    else:
        # Handle case when no allotment found, e.g. redirect to a create page or show error
        # For example, redirect to a create page:
        request.session['enquiry_num_id'] = enquiry_id
        return redirect('vehicle_allotment_insert')  # Adjust this as per your URL names

@login_required(login_url='login_page')
def vehicle_allotment_nav(request,vehicle_allotment_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    request.session['ses_enqiury_id'] = vehicle_allotment_id
    print("I am inside Get add tripetails")
    vehicle_allotment_form = VehicleallotmentForm()
    vehicle_allotment_list=Vehicle_allotmentInfo.objects.filter(va_enquirynumber=vehicle_allotment_id)
    context = {
        'vehicle_allotment_list': Vehicle_allotmentInfo.objects.all(),
        'first_name': first_name,
        'user_id': user_id,
        'vehicle_allotment_form': vehicle_allotment_form,
        'vehicle_allotment_list': vehicle_allotment_list,
    }
    return render(request, "asset_mgt_app/vehicle_allotment_add.html", context)

@login_required(login_url='login_page')
def vehicle_allotment_add(request,vehicle_allotment_id=0,enquiry_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if vehicle_allotment_id == 0:
            print("I am inside Get add vehicle_allotments")
            request.session['ses_vehicle_allotment_id'] = vehicle_allotment_id
            enquiry_num_id = request.session.get('enquiry_num_id')
            enquiry_num_id = enquiry_num_id
            vehicle_allotment_form = VehicleallotmentForm()
            print('enquiry_num_id',enquiry_num_id)
            try:
                vehicle_allotment_list= Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num_id)
            except ObjectDoesNotExist:
                vehicle_allotment_list = []
            vehicles = VehiclemasterInfo.objects.all()

            context = {
                'first_name': first_name,
                'user_id': user_id,
                'vehicle_allotment_form': vehicle_allotment_form,
                'enquiry_num_id': enquiry_num_id,
                'vehicle_allotment_list': vehicle_allotment_list,
                'vehicles_data': vehicles,
            }
        else:
            print("I am inside Get edit vehicle_allotments")
            enquiry_num= Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id).va_enquirynumber
            enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
            vehicle_allotment = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id)
            vehicle_allotment_form = VehicleallotmentForm(instance=vehicle_allotment)
            vehicles = VehiclemasterInfo.objects.all()
            for v in VehiclemasterInfo.objects.all():
                print(v.id, v.vm_policyexpirydate)
            context = {
                'first_name': first_name,
                'user_id': user_id,
                'vehicle_allotment_form': vehicle_allotment_form,
                'enquiry_num_id': enquiry_num_id,
                'vehicle_allotment_list': Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num_id),
                'va': vehicle_allotment,
                'vehicles_data': vehicles,
            }
        return render(request, "asset_mgt_app/vehicle_allotment_add.html", context)
    else:
        if vehicle_allotment_id == 0:
            print("I am inside post add vehicle_allotments")
            vehicle_allotment_form = VehicleallotmentForm(request.POST)
        else:
            print("I am inside post edit vehicle_allotments")
            vehicle_allotment = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id)
            vehicle_allotment_form = VehicleallotmentForm(request.POST, instance=vehicle_allotment)
        enquiry_num_id = request.session.get('ses_enqiury_id')
        if vehicle_allotment_form.is_valid():
            vehicle_allotment_form.save()
            print("Main Form is Valid")
            # vehicle_allotment_list = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num_id).values_list('va_vehiclenumber', flat=True))
            # vehicle_numbers=[]
            # for i in vehicle_allotment_list:
            #     vehicle_numbers.append(str(VehiclemasterInfo.objects.get(id=i).vm_registrationnumber))
            # EnquirynoteInfo.objects.filter(id=enquiry_num_id).update(en_vehicle_allotment=vehicle_numbers)
            messages.success(request, 'Record Updated Successfully')
        else:
            print("Main Form is not Valid")
            for field, errors in vehicle_allotment_form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")
                    messages.error(request, f"Error in {field}: {error}")
            messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
        return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/enquirynote_list')

# List vehicle_allotment
@login_required(login_url='login_page')
def vehicle_allotment_list(request):
    first_name = request.session.get('first_name')
    context = {'vehicle_allotment_list' : Vehicle_allotmentInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/vehicle_allotment_add.html",context)

#Delete vehicle_allotment
@login_required(login_url='login_page')
def vehicle_allotment_delete(request,vehicle_allotment_id):
    vehicle_allotment = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id)
    enquiry_num = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id).va_enquirynumber
    enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
    vehicle_allotment.delete()
    # vehicle_allotment_list = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num_id).values_list('va_vehiclenumber',flat=True))
    # vehicle_numbers = []
    # for i in vehicle_allotment_list:
    #     vehicle_numbers.append(str(VehiclemasterInfo.objects.get(id=i).vm_registrationnumber))
    # try:
    #     EnquirynoteInfo.objects.filter(id=enquiry_num_id).update(en_vehicle_allotment=vehicle_numbers)
    # except ObjectDoesNotExist:
    #     EnquirynoteInfo.objects.filter(id=enquiry_num_id).update(en_vehicle_allotment=vehicle_numbers)

    # return redirect('/SMS/vehicle_allotment_list')
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def load_vehicle_source(request):
    vehicletype_placed = request.GET.get('vehicletype_placed')
    print('vehicletype_placed',vehicletype_placed)
    if not vehicletype_placed:
        return HttpResponse(json.dumps({'error': 'Vehicle type not provided'}), status=400)

    vehicle_source_name_list = []
    vehicle_source_id_list = []

    # Fetch vehicles allotted in a trip
    vehicle_allotted_list = list(
        TripdetailInfo.objects.filter(tr_vehiclesource__in=[1,2],tc_financestatus=1).values_list('tr_vehiclenumber', flat=True)
    )

    # Fetch all vehicle master records, avoiding repetitive queries
    vehicle_master_queryset = VehiclemasterInfo.objects.exclude(vm_registrationnumber__in=vehicle_allotted_list).select_related('vm_vehicletype', 'vm_ownership')

    # Filter available vehicles by vehicle type
    matching_vehicles = [
        vehicle for vehicle in vehicle_master_queryset
        if vehicle.vm_vehicletype and vehicle.vm_vehicletype.id == int(vehicletype_placed)
    ]

    # Prepare ownership information
    ownership_cache = {}  # Cache ownership info to avoid duplicate queries
    for vehicle in matching_vehicles:
        ownership = vehicle.vm_ownership
        if ownership:
            if ownership.id not in ownership_cache:
                ownership_cache[ownership.id] = ownership.ow_ownership
            if ownership.id not in vehicle_source_id_list:
                vehicle_source_id_list.append(ownership.id)
            if ownership_cache[ownership.id] not in vehicle_source_name_list:
                vehicle_source_name_list.append(ownership_cache[ownership.id])

    # Handle case when no matching vehicles are found
    if not matching_vehicles:
        fallback_ownership = OwnershipInfo.objects.filter(pk=3).first()
        if fallback_ownership:
            if fallback_ownership.id not in vehicle_source_id_list:
                vehicle_source_id_list.append(fallback_ownership.id)
            if fallback_ownership.ow_ownership not in vehicle_source_name_list:
                vehicle_source_name_list.append(fallback_ownership.ow_ownership)

    # Prepare and return response
    data = {
        'vehicle_source_name': vehicle_source_name_list,
        'vehicle_source_id': vehicle_source_id_list,
    }
    return HttpResponse(json.dumps(data))

@login_required(login_url='login_page')
def load_vehicle_number(request):
    vehicletype_placed = request.GET.get('vehicletype_placed')
    vehicletype_source = request.GET.get('vehicletype_source')

    # basic validation
    if not vehicletype_placed or not vehicletype_source:
        return JsonResponse({'vehicle_number_list': [], 'vehicle_number_list_id': []})

    # 1) registration numbers that are in closed (2) or settled (7) trips for the given type+source
    inactive_regs = TripdetailInfo.objects.filter(
        tc_financestatus_id__in=[2,3,4,6,7],
        tr_vehicletype_placed=vehicletype_placed,
        tr_vehiclesource=vehicletype_source,
        tr_vehiclenumber__isnull=False
    ).values_list('tr_vehiclenumber', flat=True).distinct()
    inactive_regs = list(inactive_regs)  # make membership checks reliable

    # 2) registration numbers that are currently active (exclude these)
    active_regs = TripdetailInfo.objects.filter(
        tc_financestatus_id=1,
        tr_vehiclenumber__isnull=False
    ).values_list('tr_vehiclenumber', flat=True)
    active_regs = list(active_regs)

    # 3) vehicle ids already allotted (you may want to filter this to only 'active' allotments if you have a status field)
    used_vehicle_ids = list(Vehicle_allotmentInfo.objects.values_list('va_vehiclenumber_id', flat=True))
    # remove None if present
    used_vehicle_ids = [vid for vid in used_vehicle_ids if vid is not None]

    # 4) Get vehicles matching type+ownership
    candidate_qs = VehiclemasterInfo.objects.filter(
        vm_vehicletype=vehicletype_placed,
        vm_ownership=vehicletype_source
    ).values_list('id', 'vm_registrationnumber')

    vehicle_data = []
    seen_regs = set()

    for vid, reg in candidate_qs:
        # skip duplicates
        if reg in seen_regs:
            continue

        # Skip vehicles that are currently active in a trip
        if reg in active_regs:
            continue

        # If vehicle is already allotted (and NOT part of inactive list), skip it
        # (This keeps vehicles that were used in closed/settled trips available.)
        if vid in used_vehicle_ids and reg not in inactive_regs:
            continue

        # Add hint if it was in closed/settled trips
        label = reg
        if reg in inactive_regs:
            label = f"{reg}"

        vehicle_data.append({'id': vid, 'number': label})
        seen_regs.add(reg)

    return JsonResponse({
        'vehicle_number_list': [v['number'] for v in vehicle_data],
        'vehicle_number_list_id': [v['id'] for v in vehicle_data]
    })


@login_required(login_url='login_page')
def load_driver_details(request):
    vehicle_number = request.GET.get('vehicle_number')
    driver_name=list(VehiclemasterInfo.objects.filter(pk=vehicle_number).values_list('vm_primarydrivername',flat=True))
    driver_number=list(VehiclemasterInfo.objects.filter(pk=vehicle_number).values_list('vm_primarydrivermob',flat=True))
    driver_license=list(VehiclemasterInfo.objects.filter(pk=vehicle_number).values_list('vm_primarydriver_license',flat=True))
    driver_license_exp_date=list(VehiclemasterInfo.objects.filter(pk=vehicle_number).values_list('vm_primarydriver_license_exp_date',flat=True))
    data = {
        'driver_name': driver_name,
        'driver_number': driver_number,
        'driver_license': driver_license,
        'driver_license_exp_date': driver_license_exp_date,
    }
    return HttpResponse(json.dumps(data))

def vehicle_type_counts(request):
    print("I am a vehicle type")
    enquiry_number = request.GET.get('enquiry_number')
    print('Enquiry Number:', enquiry_number)

    # Get sum of env_quantity for each vehicle type
    vehicle_counts = Enquirynotevehicle.objects.filter(env_enquirynumber=enquiry_number).values('env_vehicletype').annotate(total_quantity=Sum('env_quantity'))

    print('Vehicle Counts:', vehicle_counts)

    count_dict = {item['env_vehicletype']: item['total_quantity'] for item in vehicle_counts}
    print('count_dict :', count_dict)
    return JsonResponse({'vehicle_counts': count_dict})


@login_required(login_url='login_page')
def vehicle_requested(request):
    enquiry_number = request.GET.get('enquiry_number')

    requested_vehicles = Enquirynotevehicle.objects.filter(env_enquirynumber=enquiry_number)\
        .values('env_vehicletype__id', 'env_vehicletype__vt_vehicletype')\
        .annotate(requested_qty=Sum('env_quantity'))

    vehicle_list = []

    for rv in requested_vehicles:
        vehicle_type_id = rv['env_vehicletype__id']
        vehicle_type_name = rv['env_vehicletype__vt_vehicletype']
        requested_qty = rv['requested_qty']

        # FIXED: Use va_enquirynumber_id instead of nested lookup
        allotted_qty = Vehicle_allotmentInfo.objects.filter(
            va_enquirynumber_id=enquiry_number,
            va_vehicletype_id=vehicle_type_id
        ).count()

        remaining = requested_qty - allotted_qty

        if remaining > 0:
            vehicle_list.append({
                'id': vehicle_type_id,
                'name': vehicle_type_name,
                'remaining': remaining
            })

    return JsonResponse({'vehicles': vehicle_list})


def get_remaining_quantity(request, enquiry_id, vehicle_type_id):
    enquiry_number = request.GET.get('enquiry_number')
    try:
        # Total requested
        requested = Enquirynotevehicle.objects.filter(
            env_enquirynumber_id=enquiry_id,
            env_vehicletype_id=vehicle_type_id
        ).aggregate(total=Sum('env_quantity'))['total'] or 0

        # Count of allotted vehicles of the same type
        allotted = Vehicle_allotmentInfo.objects.filter(
            va_enquirynumber_id=enquiry_id,
            va_vehicletype_id=vehicle_type_id
        ).count()

        remaining = requested - allotted
        return JsonResponse({'remaining': max(remaining, 0)})

    except Exception as e:
        return JsonResponse({'remaining': 0, 'error': str(e)})

@login_required(login_url='login_page')
def get_vendor_buy_rate(request):
    vehicle_id = request.GET.get('vehicle_id')  # This is actually a vehicle type ID, not the Vehicle_allotmentInfo ID
    vendor_id = request.GET.get('vendor_id')
    enquiry_id = request.session.get('enquiry_num_id')

    print("vehicle_id:", vehicle_id)
    print("vendor_id:", vendor_id)
    print("enquiry_id:", enquiry_id)


    enquiry = EnquirynoteInfo.objects.get(id=enquiry_id)


    # Filter for the matching vendor rate
    rate = VendorratemasterInfo1.objects.filter(
        vr1_vendor_id=vendor_id,
        vr1_fromlocation=enquiry.en_fromlocaion,
        vr1_tolocation=enquiry.en_tolocation,
        vr1_vehicletype=vehicle_id  # This is likely a ForeignKey ID
    ).first()

    buy_rate = str(rate.vr1_rate) if rate else "0"
    print("Buy Rate:", buy_rate)

    data = {
        'buy_rate': buy_rate,
    }
    return JsonResponse(data)
@login_required(login_url='login_page')
def get_vendor_sale_rate(request):
    checkbox_id = request.GET.get('checkbox_id')  # 'chk_requested' or 'chk_placed'
    vehicle_requested = request.GET.get('vehicle_requested')
    vehicle_placed = request.GET.get('vehicle_placed')
    vendor_id = request.GET.get('vendor_id')
    enquiry_id = request.session.get('enquiry_num_id')

    if not enquiry_id:
        return JsonResponse({'sale_rate': "0"})

    enquiry = EnquirynoteInfo.objects.get(id=enquiry_id)

    # Determine which vehicle type to use based on the checkbox
    if checkbox_id == 'chk_requested':
        vehicle_id = vehicle_requested
    elif checkbox_id == 'chk_placed':
        vehicle_id = vehicle_placed
    else:
        return JsonResponse({'sale_rate': "0"})

    if not vehicle_id:
        return JsonResponse({'sale_rate': "0"})

    # Filter for the matching vendor rate
    rate = RtratemasterInfo.objects.filter(
        ro_customer=enquiry.en_customername,
        ro_fromlocation=enquiry.en_fromlocaion,
        ro_tolocation=enquiry.en_tolocation,
        ro_vehicletype=vehicle_id  # ForeignKey to vehicle type
    ).first()

    sale_rate = str(rate.ro_rate) if rate else "0"

    return JsonResponse({'sale_rate': sale_rate})

@login_required(login_url='login_page')
def vendor_filter(request):
    enquiry_num = request.GET.get('enquiry_num')

    try:
        enquiry = EnquirynoteInfo.objects.get(id=enquiry_num)
        from_location = enquiry.en_fromlocaion
        to_location = enquiry.en_tolocation

        vendors = VendorratemasterInfo1.objects.filter(
            vr1_fromlocation=from_location,
            vr1_tolocation=to_location
        ).select_related('vr1_vendor').values(
            'vr1_vendor__id',
            'vr1_vendor__vend_name'  # ✅ Use actual field name
        ).distinct()

        vendor_list = [
            {'id': v['vr1_vendor__id'], 'name': v['vr1_vendor__vend_name']}
            for v in vendors
        ]

        return JsonResponse({'vendor_filter': vendor_list})

    except EnquirynoteInfo.DoesNotExist:
        return JsonResponse({'vendor_filter': [], 'error': 'Invalid Enquiry Number'}, status=400)
    except EnquirynoteInfo.DoesNotExist:
        return JsonResponse({'vendor_filter': [], 'error': 'Invalid Enquiry Number'}, status=400)

@login_required(login_url='login_page')
def vehicle_allotment_email(request):
    recipient = request.POST.get('recipient')
    va_id = request.POST.get('va_id')

    if not va_id:
        messages.error(request, "Vehicle Allotment ID is missing. Please try again.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        va = Vehicle_allotmentInfo.objects.get(pk=va_id)
    except Vehicle_allotmentInfo.DoesNotExist:
        messages.error(request, "Vehicle allotment record not found.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Convert recipient string to list
    recipient_list = [email.strip() for email in recipient.split(',') if email.strip()]

    subject = f"Vehicle Allotment Update - {va.va_vehiclenumber}"

    email_body = f"""
        <html>
            <head>
                <style>
                    table {{
                        width: 60%;
                        border-collapse: collapse;
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                        border: 1px solid black;
                    }}
                    th, td {{
                        border: 1px solid black;
                        padding: 10px;
                    }}
                    th {{
                        background-color: #f4f4f4;
                        color: #333;
                        text-align: left;
                    }}
                    td {{
                        vertical-align: top;
                    }}
                    .remarks div {{
                        margin-bottom: 10px;
                    }}
                </style>
            </head>
            <body>
                <p>Dear Team,</p>
                <p>Please find below the vehicle allotment details:</p>
                <table>
                    <tr><th>Enquiry Number</th><td>{va.va_enquirynumber}</td></tr>
                    <tr><th>Vehicle Source</th><td>{va.va_vehiclesource}</td></tr>
                    <tr><th>Vehicle Type Requested</th><td>{va.va_vehicletype}</td></tr>
                    <tr><th>Vehicle Type Placed</th><td>{va.va_vehicletype_placed}</td></tr>
                    <tr><th>Vehicle Number</th><td>{va.va_vehiclenumber}</td></tr>
                    <tr><th>Driver Name</th><td>{va.va_drivername}</td></tr>
                    <tr><th>Driver License</th><td>{va.va_driver_lic}</td></tr>
                    <tr><th>License Expiry</th><td>{va.va_driver_lic_expiry}</td></tr>
                    <tr><th>Driver Contact</th><td>{va.va_drivernumber}</td></tr>
                    <tr><th>Vendor</th><td>{va.va_vendor}</td></tr>
                    <tr><th>Updated By</th><td>{va.va_updated_by}</td></tr>
                    <tr>
                        <th>Remarks</th>
                        <td class="remarks">
                            {''.join(f'<div>{remark}</div>' for remark in (va.va_remarks or '').splitlines())}
                        </td>
                    </tr>
                </table>
                <p>Regards,<br>Transport Admin</p>
            </body>
        </html>
    """

    # Send email (no attachment for allotment email)
    send_department_email(
        department='itadmin',
        subject=subject,
        message=email_body,
        recipient_list=recipient_list,
        email_type=1
    )

    messages.success(request, "Vehicle Allotment email sent successfully.")
    return redirect(request.META.get('HTTP_REFERER', '/'))