from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..forms import TripclosurefilesForm,TripclosureaddForm
from ..models import RtratemasterInfo,User_extInfo,Trip_closure_files_Info,EnquirynoteInfo,TripdetailInfo,Tripstatusinfo
from django.shortcuts import render, redirect
from django.contrib import messages

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
            tripclosure_files = Trip_closure_files_Info.objects.get(tcf_tripnumber=trip_num)
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
            tripclosure_files = Trip_closure_files_Info.objects.get(tcf_tripnumber=trip_num)
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
