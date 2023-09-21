from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from ..forms import TripclosurefilesForm,TripdetailaddForm
from ..models import Vehicle_allotmentInfo,ConsignmentdetailInfo,Tripstatusinfo,Trip_closure_files_Info,EnquirynoteInfo,TripdetailInfo
from django.shortcuts import render, redirect
from django.http import HttpResponse
import json
@login_required(login_url='login_page')
def tripdetail_nav(request,tripdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print("I am inside Get add tripetails")
    # con_det_form = ConsignmentdetailaddForm()
    trip_det_form = TripdetailaddForm(request.POST)
    tripclosurefiles_form = TripclosurefilesForm(request.POST, request.FILES)
    enquiry_num = EnquirynoteInfo.objects.get(pk=tripdetail_id).en_enquirynumber
    enquiry_num_id = EnquirynoteInfo.objects.get(pk=tripdetail_id).id
    request.session['ses_enqiury_id'] = enquiry_num_id
    tripdetail_list=TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num_id)
    status_list = Tripstatusinfo.objects.filter(id__in=[1, 2, 3])
    consignment_list = ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id)
    context = {
        'first_name': first_name,
        'user_id': user_id,
        'trip_det_form': trip_det_form,
        'tripclosurefiles_form': tripclosurefiles_form,
        'enquiry_num': enquiry_num,
        'enquiry_num_id': enquiry_num_id,
        'tripdetail_list': tripdetail_list,
        'status_list': status_list,
        'consignment_list': consignment_list,
    }
    if trip_det_form.is_valid():
        trip_status_list = list(TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num_id).values_list('tc_financestatus', flat=True))
        print('trip_status_list', trip_status_list)
        for i in trip_status_list:
            if i == 1:
                messages.error(request, 'Please close Open Trip against this enquiry and try to create new Trip')
                return redirect(request.META['HTTP_REFERER'])
            else:
                pass
        try:
            last_id = TripdetailInfo.objects.latest('id').id
            trip_num_next = str('TN_') + str(int(((TripdetailInfo.objects.get(id=last_id)).tr_tripnumber).replace('TN_', '')) + 1)
        except ObjectDoesNotExist:
            trip_num_next = str('TN_') + str(1000000)
        trip_det_form.save()
        tripclosurefiles_form.save()
        print("Trip Details Main Form is Valid")
        last_id = TripdetailInfo.objects.latest('id').id
        last_id_files = Trip_closure_files_Info.objects.latest('id').id
        TripdetailInfo.objects.filter(id=last_id).update(tr_tripnumber=trip_num_next)
        Trip_closure_files_Info.objects.filter(id=last_id_files).update(tcf_tripnumber=trip_num_next)
        tripdetail_list = TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num_id).values_list('tr_tripnumber', flat=True)
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_tripdetails=list(tripdetail_list))
        messages.success(request, 'Record Updated Successfully')
    else:
        print("Trip Details Main Form is not Valid")
        messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
    return render(request, "asset_mgt_app/tripdetail_add.html", context)

@login_required(login_url='login_page')
def tripdetail_add(request,tripdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if tripdetail_id == 0:
            print("I am inside Get add tripdetails")
            trip_det_form = TripdetailaddForm()
            tripclosurefiles_form = TripclosurefilesForm()
            enquiry_num_id = request.session.get('ses_enqiury_id')
            status_list = Tripstatusinfo.objects.filter(id__in=[1, 2, 3])
            consignment_list = ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id)
            context = {
                'first_name': first_name,
                'user_id': user_id,
                'trip_det_form': trip_det_form,
                'tripclosurefiles_form': tripclosurefiles_form,
                'enquiry_num_id': enquiry_num_id,
                'status_list': status_list,
                'consignment_list': consignment_list,
                'tripdetail_list': TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num_id),
            }
        else:
            trip_num = TripdetailInfo.objects.get(pk=tripdetail_id).tr_tripnumber
            enquiry_num = TripdetailInfo.objects.get(pk=tripdetail_id).tr_enquirynumber
            enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
            tripdetail = TripdetailInfo.objects.get(pk=tripdetail_id)
            trip_det_form = TripdetailaddForm(instance=tripdetail)
            tripclosure_files = Trip_closure_files_Info.objects.get(tcf_tripnumber=trip_num)
            tripclosurefiles_form = TripclosurefilesForm(instance=tripclosure_files)
            status_list = Tripstatusinfo.objects.filter(id__in=[1, 2, 3])
            status_selected = (TripdetailInfo.objects.get(pk=tripdetail_id).tc_financestatus.id)
            consignment_selected = (TripdetailInfo.objects.get(pk=tripdetail_id).tr_consignmentnumber.id)
            consignment_list = ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id)
            context = {
                'first_name': first_name,
                'user_id': user_id,
                'trip_det_form': trip_det_form,
                'tripclosurefiles_form': tripclosurefiles_form,
                'enquiry_num_id': enquiry_num_id,
                'status_list': status_list,
                'status_selected': status_selected,
                'consignment_selected': consignment_selected,
                'consignment_list': consignment_list,
                'tripdetail_list': TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num_id),
            }
        return render(request, "asset_mgt_app/tripdetail_add.html", context)
    else:
        if tripdetail_id == 0:
            print("I am inside post add tripdetails")
            trip_det_form = TripdetailaddForm(request.POST)
            tripclosurefiles_form = TripclosurefilesForm(request.POST, request.FILES)
            enquiry_num = request.session.get('ses_enqiury_id')
            if trip_det_form.is_valid():
                # enquiry_number = request.GET.get('enquiry_number')
                # consignment_number = request.GET.get('consignment_number')
                # consignment_number=TripdetailInfo.objects.get(pk=tripdetail_id).tr_consignmentnumber
                # vehicle_number=TripdetailInfo.objects.get(pk=tripdetail_id).tr_vehiclenumber
                # print('consignment_number',consignment_number)
                # print('vehicle_number',vehicle_number)
                trip_status_list=list(TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num).values_list('tc_financestatus',flat=True))
                print('trip_status_list',trip_status_list)
                for i in trip_status_list:
                    if i==1:
                        messages.error(request, 'Please close Open Trip against this enquiry and try to create new Trip')
                        return redirect(request.META['HTTP_REFERER'])
                    else:
                        pass
                try:
                    last_id = TripdetailInfo.objects.latest('id').id
                    trip_num_next = str('TN_') + str(int(((TripdetailInfo.objects.get(id=last_id)).tr_tripnumber).replace('TN_', '')) + 1)
                except ObjectDoesNotExist:
                    trip_num_next = str('TN_') + str(1000000)
                trip_det_form.save()
                tripclosurefiles_form.save()
                print("Main Form is Valid")
                last_id = TripdetailInfo.objects.latest('id').id
                last_id_files = Trip_closure_files_Info.objects.latest('id').id
                TripdetailInfo.objects.filter(id=last_id).update(tr_tripnumber=trip_num_next)
                Trip_closure_files_Info.objects.filter(id=last_id_files).update(tcf_tripnumber=trip_num_next)
                tripdetail_list = TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num).values_list('tr_tripnumber', flat=True)
                EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_tripdetails=list(tripdetail_list))
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Main Form is not Valid")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
        else:
            print("I am inside post edit tripdetails")
            trip_num = TripdetailInfo.objects.get(pk=tripdetail_id).tr_tripnumber
            tripdetail = TripdetailInfo.objects.get(pk=tripdetail_id)
            trip_det_form = TripdetailaddForm(request.POST, instance=tripdetail)
            tripclosure_files = Trip_closure_files_Info.objects.get(tcf_tripnumber=trip_num)
            tripclosurefiles_form = TripclosurefilesForm(request.POST, request.FILES, instance=tripclosure_files)

            enquiry_num = request.session.get('ses_enqiury_id')
            if trip_det_form.is_valid():
                trip_det_form.save()
                tripclosurefiles_form.save()
                print("Main Form is Valid")
                tripdetail_list = TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num).values_list('tr_tripnumber', flat=True)
                print(tripdetail_list)
                EnquirynoteInfo.objects.filter(pk=enquiry_num).update(en_tripdetails=list(tripdetail_list))
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Main Form is not Valid")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
        return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/enquirynote_list')

# List tripdetail
@login_required(login_url='login_page')
def tripdetail_list(request):
    first_name = request.session.get('first_name')
    context = {'tripdetail_list' : TripdetailInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/tripdetail_list.html",context)

#Delete tripdetail
@login_required(login_url='login_page')
def tripdetail_delete(request,tripdetail_id):
    tripdetail = TripdetailInfo.objects.get(pk=tripdetail_id)
    enquiry_num = TripdetailInfo.objects.get(pk=tripdetail_id).tr_enquirynumber
    trip_num = TripdetailInfo.objects.get(pk=tripdetail_id).tr_tripnumber
    tripdetail.delete()
    try:
        tripdetail_list = TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num).values_list('tr_tripnumber',flat=True)
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_tripdetails=list(tripdetail_list))
    except ObjectDoesNotExist:
        tripdetail_list = []
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_tripdetails=list(tripdetail_list))
    trip_closure_files=list(Trip_closure_files_Info.objects.filter(tcf_tripnumber=trip_num).values_list('tcf_tripnumber',flat=True))
    for i in trip_closure_files:
        trip_files = Trip_closure_files_Info.objects.get(tcf_tripnumber=i)
        trip_files.delete()
    # return redirect('/SMS/tripdetail_list')
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def load_vehicle_details(request):
    enquiry_number = request.GET.get('enquiry_number')
    consignment_number = request.GET.get('consignment_number')
    vehicle_type_requested=list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,va_consignmentnumber=consignment_number).values_list('va_vehicletype',flat=True))
    vehicle_type_placed=list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,va_consignmentnumber=consignment_number).values_list('va_vehicletype_placed',flat=True))
    vehicletype_source = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,va_consignmentnumber=consignment_number).values_list('va_vehiclesource', flat=True))
    vehicletype_number = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,va_consignmentnumber=consignment_number).values_list('va_vehiclenumber', flat=True))
    driver_name = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,va_consignmentnumber=consignment_number).values_list('va_drivername', flat=True))
    driver_number = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,va_consignmentnumber=consignment_number).values_list('va_driver_lic', flat=True))
    driver_license = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,va_consignmentnumber=consignment_number).values_list('va_drivernumber', flat=True))

    data = {
        'vehicle_type_requested': vehicle_type_requested,
        'vehicle_type_placed': vehicle_type_placed,
        'vehicletype_source': vehicletype_source,
        'vehicletype_number': vehicletype_number,
        'driver_name': driver_name,
        'driver_number': driver_number,
        'driver_license': driver_license,
    }
    return HttpResponse(json.dumps(data))