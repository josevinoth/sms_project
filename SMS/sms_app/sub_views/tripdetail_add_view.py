from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from ..forms import TripdetailaddForm
from ..models import ConsignmentdetailInfo,EnquirynoteInfo,TripdetailInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def tripdetail_add(request,tripdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    enquiry_num = EnquirynoteInfo.objects.get(pk=tripdetail_id).en_enquirynumber
    consignment_num = EnquirynoteInfo.objects.get(pk=tripdetail_id).en_consignmentdetails
    print('enquiry_num', enquiry_num)
    try:
        trip_num = TripdetailInfo.objects.get(tr_enquirynumber=enquiry_num).tr_tripnumber
    except ObjectDoesNotExist:
        trip_num = None
    print('trip_num', trip_num)

    if request.method == "GET":
        if trip_num == None:
            print("I am inside Get add Trip Details")
            form = TripdetailaddForm()
        else:
            print("I am inside get edit Trip Details")
            try:
                tripdetail=TripdetailInfo.objects.get(tr_tripnumber=trip_num)
            except ObjectDoesNotExist:
                tripdetail=None
            form = TripdetailaddForm(instance=tripdetail)
        context={
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'enquiry_num': enquiry_num,
            'consignment_num': consignment_num,
        }
        return render(request, "asset_mgt_app/tripdetail_add.html", context)
    else:
        if trip_num == None:
            print("I am inside post add Trip Details")
            form = TripdetailaddForm(request.POST)
        else:
            print("I am inside post edit Trip Details")
            try:
                tripdetail = TripdetailInfo.objects.get(tr_tripnumber=trip_num)
            except ObjectDoesNotExist:
                tripdetail = None
            form = TripdetailaddForm(request.POST,instance=tripdetail)
        if form.is_valid():
            form.save()
            print("Main Form Saved")
        else:
            print("Main Form not Saved")
        return redirect('/SMS/enquirynote_list')

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
    tripdetail.delete()
    return redirect('/SMS/tripdetail_list')