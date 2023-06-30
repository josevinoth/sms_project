from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from ..forms import TripclosureaddForm
from ..models import User_extInfo,TripdetailInfo,EnquirynoteInfo,TripclosureInfo
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required(login_url='login_page')
def tripclosure_nav(request,tripclosure_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print("I am inside Get add tripetails")
    # con_det_form = ConsignmentdetailaddForm()
    tripclosure_form = TripclosureaddForm(request.POST)
    enquiry_num = EnquirynoteInfo.objects.get(pk=tripclosure_id).en_enquirynumber
    request.session['ses_enqiury_id'] = enquiry_num
    tripclosure_list=TripclosureInfo.objects.filter(tc_enquirynumber=enquiry_num)
    context = {
        'first_name': first_name,
        'user_id': user_id,
        'tripclosure_form': tripclosure_form,
        'enquiry_num': enquiry_num,
        'tripclosure_list': tripclosure_list,
    }
    if tripclosure_form.is_valid():
        tripclosure_form.save()
        print("Main Form is Valid")
        tripclosure_list = TripclosureInfo.objects.filter(tc_enquirynumber=enquiry_num).values_list('tc_tripnumber', flat=True)
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_tripclosure=list(tripclosure_list))
        messages.success(request, 'Record Updated Successfully')
    else:
        print("Main Form is not Valid")
        messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
    return render(request, "asset_mgt_app/tripclosure_add.html", context)

@login_required(login_url='login_page')
def tripclosure_add(request,tripclosure_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    enquiry_num = EnquirynoteInfo.objects.get(pk=tripclosure_id).en_enquirynumber
    consignment_num = EnquirynoteInfo.objects.get(pk=tripclosure_id).en_consignmentdetails
    print('enquiry_num',enquiry_num)
    try:
        trip_num = TripdetailInfo.objects.get(tr_enquirynumber=enquiry_num).tr_tripnumber
    except ObjectDoesNotExist:
        trip_num = None

    try:
        trip_closure_num = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).en_tripclosure
    except ObjectDoesNotExist:
        trip_closure_num = None
    print('trip_num', trip_num)
    if request.method == "GET":
        if trip_closure_num == None:
            print("I am inside Get add Trip Closure")
            form = TripclosureaddForm()
        else:
            print("I am inside Get edit Trip Closure")
            try:
                tripclosure = TripclosureInfo.objects.get(tc_tripnumber=trip_num)
            except ObjectDoesNotExist:
                tripclosure = None
            form = TripclosureaddForm(instance=tripclosure)
        context = {
            'form': form,
            'first_name': first_name,
            'enquiry_num': enquiry_num,
            'consignment_num': consignment_num,
            'trip_num': trip_num,
            'user_id': user_id,
            'role': role,
            # 'tripclosure_list': TripdetailInfo.objects.filter(tc_enquirynumber=enquiry_num),
        }
        return render(request, "asset_mgt_app/tripclosure_add.html", context)
    else:
        if trip_closure_num == None:
            print("I am inside post add Trip Closure")
            form = TripclosureaddForm(request.POST)
        else:
            print("I am inside post edit Trip Closure")
            tripclosure = TripclosureInfo.objects.get(tc_tripnumber=trip_num)
            form = TripclosureaddForm(request.POST,instance=tripclosure)
        if form.is_valid():
            form.save()
            print("Main Form Saved")
        else:
            print("Main Form not Saved")
        return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/enquirynote_list')

# List tripclosure
@login_required(login_url='login_page')
def tripclosure_list(request):
    first_name = request.session.get('first_name')
    context = {'tripclosure_list' : TripclosureInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/tripclosure_list.html",context)

#Delete tripclosure
@login_required(login_url='login_page')
def tripclosure_delete(request,tripclosure_id):
    tripclosure = TripclosureInfo.objects.get(pk=tripclosure_id)
    tripclosure.delete()
    return redirect('/SMS/tripclosure_list')