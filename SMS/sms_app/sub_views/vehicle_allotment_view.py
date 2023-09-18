from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from ..forms import VehicleallotmentForm
from ..models import VehiclemasterInfo,ConsignmentdetailInfo,EnquirynoteInfo,Vehicle_allotmentInfo
from django.shortcuts import render, redirect

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
    vehicle_allotment_list=Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num_id)
    context = {
        'first_name': first_name,
        'user_id': user_id,
        'vehicle_allotment_form': vehicle_allotment_form,
        'enquiry_num': enquiry_num,
        'enquiry_num_id': enquiry_num_id,
        'vehicle_allotment_list': vehicle_allotment_list,
    }
    if vehicle_allotment_form.is_valid():
        vehicle_allotment_form.save()
        print("Main Form is Valid")
        enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
        vehicle_allotment_list = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num_id).values_list('va_vehiclenumber', flat=True))
        vehicle_numbers = []
        for i in vehicle_allotment_list:
            vehicle_numbers.append(str(VehiclemasterInfo.objects.get(id=i).ve_vehiclenumber))
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
        else:
            print("I am inside Get edit vehicle_allotments")
            enquiry_num= Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id).va_enquirynumber
            enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
            vehicle_allotment = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id)
            vehicle_allotment_form = VehicleallotmentForm(instance=vehicle_allotment)
        print(enquiry_num_id)
        context = {
            'first_name': first_name,
            'user_id': user_id,
            'vehicle_allotment_form': vehicle_allotment_form,
            'enquiry_num_id': enquiry_num_id,
            'vehicle_allotment_list': Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num_id),
            'consignment_id':consignment_id,
            'consignment_number':consignment_number,
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