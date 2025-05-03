import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from ..forms import VehicleallotmentForm
from ..models import Enquirynotevehicle,TripdetailInfo,OwnershipInfo,VehiclemasterInfo,EnquirynoteInfo,Vehicle_allotmentInfo
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse


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
def vehicle_allotment_add(request,vehicle_allotment_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    enquiry_num_id = request.session.get('ses_enqiury_id')

    if request.method == "GET":
        if vehicle_allotment_id == 0:
            print("I am inside Get add vehicle_allotments")
            enquiry_num_id = request.session.get('ses_enqiury_id')
            vehicle_allotment_form = VehicleallotmentForm()
            context = {
                'first_name': first_name,
                'user_id': user_id,
                'vehicle_allotment_form': vehicle_allotment_form,
                'enquiry_num_id': enquiry_num_id,
                'vehicle_allotment_list': Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num_id),
            }
        else:
            print("I am inside Get edit vehicle_allotments")
            enquiry_num= Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id).va_enquirynumber
            enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
            vehicle_allotment = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id)
            vehicle_allotment_form = VehicleallotmentForm(instance=vehicle_allotment)
            context = {
                'first_name': first_name,
                'user_id': user_id,
                'vehicle_allotment_form': vehicle_allotment_form,
                'enquiry_num_id': enquiry_num_id,
                'vehicle_allotment_list': Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num_id),
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

    # Get already allotted vehicle IDs
    used_vehicle_ids = Vehicle_allotmentInfo.objects.values_list('va_vehiclenumber_id', flat=True)

    # Exclude them from dropdown
    available_vehicles = VehiclemasterInfo.objects.filter(
        vm_vehicletype=vehicletype_placed,
        vm_ownership=vehicletype_source
    ).exclude(id__in=used_vehicle_ids).values_list('vm_registrationnumber', 'id')

    return JsonResponse({
        'vehicle_number_list': [v[0] for v in available_vehicles],
        'vehicle_number_list_id': [v[1] for v in available_vehicles]
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

from django.db.models import Sum

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
