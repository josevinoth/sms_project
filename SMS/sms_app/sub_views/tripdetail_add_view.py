from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from ..forms import TripdetailaddForm
from ..models import EnquirynoteInfo,TripdetailInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def tripdetail_nav(request,tripdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print("I am inside Get add tripetails")
    # con_det_form = ConsignmentdetailaddForm()
    trip_det_form = TripdetailaddForm(request.POST)
    enquiry_num = EnquirynoteInfo.objects.get(pk=tripdetail_id).en_enquirynumber
    request.session['ses_enqiury_id'] = enquiry_num
    tripdetail_list=TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num)
    context = {
        'first_name': first_name,
        'user_id': user_id,
        'trip_det_form': trip_det_form,
        'enquiry_num': enquiry_num,
        'tripdetail_list': tripdetail_list,
    }
    if trip_det_form.is_valid():
        trip_det_form.save()
        print("Main Form is Valid")
        tripdetail_list = TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num).values_list('tr_tripnumber', flat=True)
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_tripdetails=list(tripdetail_list))
        messages.success(request, 'Record Updated Successfully')
    else:
        print("Main Form is not Valid")
        messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
    return render(request, "asset_mgt_app/tripdetail_add.html", context)

@login_required(login_url='login_page')
def tripdetail_add(request,tripdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if tripdetail_id == 0:
            print("I am inside Get add tripdetails")
            enquiry_num = request.session.get('ses_enqiury_id')
            trip_det_form = TripdetailaddForm()
        else:
            enquiry_num = TripdetailInfo.objects.get(pk=tripdetail_id).tr_enquirynumber
            tripdetail = TripdetailInfo.objects.get(pk=tripdetail_id)
            trip_det_form = TripdetailaddForm(instance=tripdetail)
        context = {
            'first_name': first_name,
            'user_id': user_id,
            'trip_det_form': trip_det_form,
            'enquiry_num': enquiry_num,
            'tripdetail_list': TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num),
        }
        return render(request, "asset_mgt_app/tripdetail_add.html", context)
    else:
        if tripdetail_id == 0:
            print("I am inside post add tripdetails")
            trip_det_form = TripdetailaddForm(request.POST)
        else:
            print("I am inside post edit tripdetails")
            tripdetail = TripdetailInfo.objects.get(pk=tripdetail_id)
            trip_det_form = TripdetailaddForm(request.POST, instance=tripdetail)
        enquiry_num = request.session.get('ses_enqiury_id')
        if trip_det_form.is_valid():
            trip_det_form.save()
            print("Main Form is Valid")
            tripdetail_list = TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num).values_list('tr_tripnumber', flat=True)
            EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_tripdetails=list(tripdetail_list))
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
    tripdetail.delete()
    try:
        tripdetail_list = TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num).values_list('tr_tripnumber',flat=True)
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_tripdetails=list(tripdetail_list))
    except ObjectDoesNotExist:
        tripdetail_list = []
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_tripdetails=list(tripdetail_list))

    # return redirect('/SMS/tripdetail_list')
    return redirect(request.META['HTTP_REFERER'])