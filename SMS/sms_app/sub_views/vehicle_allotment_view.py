import json
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from ..forms import VehicleallotmentForm
from ..models import TripdetailInfo,OwnershipInfo,VehiclemasterInfo,ConsignmentdetailInfo,EnquirynoteInfo,Vehicle_allotmentInfo
from django.shortcuts import render, redirect
from django.http import HttpResponse
@login_required(login_url='login_page')
def vehicle_allotment_nav(request,vehicle_allotment_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print("I am inside Get add tripetails")
    # con_det_form = ConsignmentdetailaddForm()
    vehicle_allotment_form = VehicleallotmentForm(request.POST)
    enquiry_num = EnquirynoteInfo.objects.get(pk=vehicle_allotment_id).en_enquirynumber
    enquiry_num_id = EnquirynoteInfo.objects.get(pk=vehicle_allotment_id).id
    request.session['ses_enqiury_id'] = enquiry_num_id
    vehicle_type_requested=EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).en_vehicletype.id
    consignment_list=ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id)
    vehicle_allotment_list=Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num_id)
    context = {
        'first_name': first_name,
        'user_id': user_id,
        'vehicle_allotment_form': vehicle_allotment_form,
        'enquiry_num': enquiry_num,
        'enquiry_num_id': enquiry_num_id,
        'consignment_list': consignment_list,
        'vehicle_allotment_list': vehicle_allotment_list,
        'vehicle_type_requested': vehicle_type_requested,
    }
    if vehicle_allotment_form.is_valid():
        vehicle_allotment_form.save()
        print("Main Form is Valid")
        print("enquiry_num_id",enquiry_num_id)
        # enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
        vehicle_allotment_list = list((Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num_id).values_list('va_vehiclenumber', flat=True)).distinct())
        filterd_vehicle_allotment_list=[i for i in vehicle_allotment_list if i is not None]
        vehicle_numbers = []
        for i in filterd_vehicle_allotment_list:
            print(i)
            vehicle_numbers.append(str(VehiclemasterInfo.objects.get(id=i).vm_registrationnumber))
        try:
            EnquirynoteInfo.objects.filter(id=enquiry_num_id).update(en_vehicle_allotment=vehicle_numbers)
        except ObjectDoesNotExist:
            EnquirynoteInfo.objects.filter(id=enquiry_num_id).update(en_vehicle_allotment=vehicle_numbers)
        messages.success(request, 'Record Updated Successfully')
    else:
        print("Main Form is not Valid")
        messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
    return render(request, "asset_mgt_app/vehicle_allotment_add.html", context)

@login_required(login_url='login_page')
def vehicle_allotment_add(request,vehicle_allotment_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    enquiry_num_id = request.session.get('ses_enqiury_id')
    consignment_number=list(ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id).values_list("co_consignmentnumber",flat=True))
    consignment_id=list(ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id).values_list("id",flat=True))

    if request.method == "GET":
        if vehicle_allotment_id == 0:
            print("I am inside Get add vehicle_allotments")
            enquiry_num_id = request.session.get('ses_enqiury_id')
            vehicle_allotment_form = VehicleallotmentForm()
            consignment_list = ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id)
            vehicle_type_requested = EnquirynoteInfo.objects.get(id=enquiry_num_id).en_vehicletype.id
            context = {
                'first_name': first_name,
                'user_id': user_id,
                'vehicle_allotment_form': vehicle_allotment_form,
                'enquiry_num_id': enquiry_num_id,
                'vehicle_allotment_list': Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num_id),
                'consignment_id': consignment_id,
                'consignment_number': consignment_number,
                'consignment_list': consignment_list,
                'vehicle_type_requested': vehicle_type_requested,
            }
        else:
            print("I am inside Get edit vehicle_allotments")
            enquiry_num= Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id).va_enquirynumber
            enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
            vehicle_allotment = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id)
            vehicle_allotment_form = VehicleallotmentForm(instance=vehicle_allotment)
            consignment_list = ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id)
            consignment_selected = (Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id).va_consignmentnumber.id)
            context = {
                'first_name': first_name,
                'user_id': user_id,
                'vehicle_allotment_form': vehicle_allotment_form,
                'enquiry_num_id': enquiry_num_id,
                'vehicle_allotment_list': Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num_id),
                'consignment_id':consignment_id,
                'consignment_number':consignment_number,
                'consignment_list':consignment_list,
                'consignment_selected':consignment_selected,
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
            vehicle_allotment_list = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num_id).values_list('va_vehiclenumber', flat=True))
            vehicle_numbers=[]
            for i in vehicle_allotment_list:
                vehicle_numbers.append(str(VehiclemasterInfo.objects.get(id=i).vm_registrationnumber))
            EnquirynoteInfo.objects.filter(id=enquiry_num_id).update(en_vehicle_allotment=vehicle_numbers)
            messages.success(request, 'Record Updated Successfully')
        else:
            print("Main Form is not Valid")
            messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
        return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/enquirynote_list')

# List vehicle_allotment
@login_required(login_url='login_page')
def vehicle_allotment_list(request):
    first_name = request.session.get('first_name')
    context = {'vehicle_allotment_list' : Vehicle_allotmentInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/vehicle_allotment_list.html",context)

#Delete vehicle_allotment
@login_required(login_url='login_page')
def vehicle_allotment_delete(request,vehicle_allotment_id):
    vehicle_allotment = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id)
    enquiry_num = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id).va_enquirynumber
    enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
    vehicle_allotment.delete()
    vehicle_allotment_list = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num_id).values_list('va_vehiclenumber',flat=True))
    vehicle_numbers = []
    for i in vehicle_allotment_list:
        vehicle_numbers.append(str(VehiclemasterInfo.objects.get(id=i).vm_registrationnumber))
    try:
        EnquirynoteInfo.objects.filter(id=enquiry_num_id).update(en_vehicle_allotment=vehicle_numbers)
    except ObjectDoesNotExist:
        EnquirynoteInfo.objects.filter(id=enquiry_num_id).update(en_vehicle_allotment=vehicle_numbers)

    # return redirect('/SMS/vehicle_allotment_list')
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def load_vehicle_source(request):
    vehicletype_placed = request.GET.get('vehicletype_placed')
    vehicle_source_name_list=[]
    vehicle_source_id_list=[]

    # Fetch vehicle alloted in a trip
    vehicle_alloted_list=list(TripdetailInfo.objects.filter(tc_financestatus=1).values_list('tr_vehiclenumber',flat=True))
    vehicle_master_list=list(VehiclemasterInfo.objects.all().values_list('id',flat=True))

    # Fetch vehicle Source
    vehicle_available_list = []
    for element in vehicle_master_list:
        if element not in vehicle_alloted_list:
            vehicle_available_list.append(element)
    for i in vehicle_available_list:
        vehicle_type_available=VehiclemasterInfo.objects.get(pk=i).vm_vehicletype.id
        if (vehicle_type_available==int(vehicletype_placed)):
            vehicle_source = VehiclemasterInfo.objects.get(pk=i).vm_ownership.id
            vehicle_source_id=OwnershipInfo.objects.get(pk=vehicle_source).id
            vehicle_source_name=OwnershipInfo.objects.get(pk=vehicle_source).ow_ownership

            if vehicle_source_id not in vehicle_source_id_list:
                vehicle_source_id_list.append(vehicle_source_id)
            if vehicle_source_name not in vehicle_source_name_list:
                vehicle_source_name_list.append(vehicle_source_name)
        else:
            pass
    data = {
        'vehicle_source_name':vehicle_source_name_list,
        'vehicle_source_id':vehicle_source_id_list,
    }
    return HttpResponse(json.dumps(data))
@login_required(login_url='login_page')
def load_vehicle_number(request):
    vehicletype_placed = request.GET.get('vehicletype_placed')
    vehicletype_source = request.GET.get('vehicletype_source')
    vehicle_number_list=list(VehiclemasterInfo.objects.filter(vm_vehicletype=vehicletype_placed,vm_ownership=vehicletype_source).values_list('vm_registrationnumber',flat=True))
    vehicle_number_list_id=[]
    for i in vehicle_number_list:
        vehicle_number_list_id.append(VehiclemasterInfo.objects.get(vm_registrationnumber=i).id)
    data = {
        'vehicle_number_list': vehicle_number_list,
        'vehicle_number_list_id': vehicle_number_list_id,
    }
    return HttpResponse(json.dumps(data))

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