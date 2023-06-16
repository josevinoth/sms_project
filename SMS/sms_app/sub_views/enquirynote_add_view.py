from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from ..forms import ConsignmentdetailaddForm,EnquirynoteaddForm
from ..models import StatusList,TripclosureInfo,TripdetailInfo,ConsignmentdetailInfo,EnquirynoteInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def enquirynote_add(request,enquirynote_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print(user_id)
    if request.method == "GET":
        if enquirynote_id == 0:
            print("I am inside Get add Enquirynote")
            form = EnquirynoteaddForm()
        else:
            print("I am inside get edit Enuirynote")
            enquirynote=EnquirynoteInfo.objects.get(pk=enquirynote_id)
            tr_enqiury_id = EnquirynoteInfo.objects.get(pk=enquirynote_id).en_enquirynumber
            request.session['ses_enqiury_id'] = tr_enqiury_id
            tr_enqiury_id_ses = request.session.get('ses_enqiury_id')
            form = EnquirynoteaddForm(instance=enquirynote)
        context={
            'user_id': user_id,
            'form': form,
            'first_name': first_name,
        }
        return render(request, "asset_mgt_app/enquirynote_add.html",context)
    else:
        if enquirynote_id == 0:
            print("I am inside post add Enuirynote")
            form = EnquirynoteaddForm(request.POST)
        else:
            print("I am inside post edit Enquirynote")
            enquirynote = EnquirynoteInfo.objects.get(pk=enquirynote_id)
            form = EnquirynoteaddForm(request.POST,instance=enquirynote)
        if form.is_valid():
            form.save()
            print("Main Form Saved")
        else:
            print("Main Form not Saved")
        return redirect('/SMS/enquirynote_list')

# List enquirynote
@login_required(login_url='login_page')
def enquirynote_list(request):
    print("Inside Enquiry List")
    first_name = request.session.get('first_name')
    open_cons_num_end_data=EnquirynoteInfo.objects.filter(en_consignmentdetails=None).values_list('en_enquirynumber',flat=True)
    enquiry_list_cons_data=ConsignmentdetailInfo.objects.filter().values_list('co_enquirynumber',flat=True)
    for i in open_cons_num_end_data:
        if i in enquiry_list_cons_data:
            cons_num_cons_data=ConsignmentdetailInfo.objects.get(co_enquirynumber=i).co_consignmentnumber
            EnquirynoteInfo.objects.filter(en_enquirynumber=i).update(en_consignmentdetails=cons_num_cons_data)

    open_trip_num_data = EnquirynoteInfo.objects.filter(en_tripdetails=None).values_list('en_enquirynumber',flat=True)
    trip_list_data=TripdetailInfo.objects.filter().values_list('tr_enquirynumber',flat=True)
    for j in open_trip_num_data:
        if j in trip_list_data:
            trip_num_trip_data = TripdetailInfo.objects.get(tr_enquirynumber=j).tr_tripnumber
            EnquirynoteInfo.objects.filter(en_enquirynumber=j).update(en_tripdetails=trip_num_trip_data)

    open_trip_cloure_data=EnquirynoteInfo.objects.filter(en_tripclosure=None).values_list('en_enquirynumber',flat=True)
    trip_closure_list_data=TripclosureInfo.objects.filter().values_list('tc_enquirynumber',flat=True)
    for k in open_trip_cloure_data:
        if k in trip_closure_list_data:
            trip_closure_trip_data=TripclosureInfo.objects.get(tc_enquirynumber=k).tc_tripnumber
            EnquirynoteInfo.objects.filter(en_enquirynumber=k).update(en_tripclosure=trip_closure_trip_data)
    enquiry_num_list=EnquirynoteInfo.objects.filter()
    for m in enquiry_num_list:
        print(m)
        try:
            consignment_status_id_list=[]
            consignment_status = ConsignmentdetailInfo.objects.filter(co_enquirynumber=m).values_list('co_status',flat=True)
            print(consignment_status)
            for i in consignment_status:
                consignment_status_id_list = consignment_status_id_list.append(StatusList.objects.get(status_title=i).id)
            if all(element == 5 for element in (consignment_status_id_list)):
                consignment_status_id=5
        except ObjectDoesNotExist:
            consignment_status_id=6
        try:
            trip_details_status = TripdetailInfo.objects.get(tr_enquirynumber=m).tr_status
            trip_details_status_id = StatusList.objects.get(status_title=trip_details_status).id
        except ObjectDoesNotExist:
            trip_details_status_id = 6
        try:
            trip_closure_status = TripclosureInfo.objects.get(tc_enquirynumber=m).tc_financestatus
            trip_closure_status_id = StatusList.objects.get(status_title=trip_closure_status).id
        except ObjectDoesNotExist:
            trip_closure_status_id = 6

        if consignment_status_id == 5 and trip_details_status_id==5 and trip_closure_status_id==5:
            EnquirynoteInfo.objects.filter(en_enquirynumber=m).update(en_status=5)
        else:
            EnquirynoteInfo.objects.filter(en_enquirynumber=m).update(en_status=6)

    context = {
                'enquirynote_list' : EnquirynoteInfo.objects.all(),
                # 'consignmentdetail_list': ConsignmentdetailInfo.objects.all(),
                'first_name': first_name
                }
    return render(request,"asset_mgt_app/enquirynote_list.html",context)

# Connect to consignemnt Note
@login_required(login_url='login_page')
def consignment_note_connect(request,enquirynote_id):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    enquiry_num=EnquirynoteInfo.objects.get(pk=enquirynote_id).en_enquirynumber
    request.session['ses_enquiry_note']=enquiry_num
    try:
        consignment_num=ConsignmentdetailInfo.objects.get(co_enquirynumber=enquiry_num).co_consignmentnumber
    except ObjectDoesNotExist:
        consignment_num=None

    if request.method == "GET":
        if consignment_num==None:
            print("I am inside Get add consignmentdetails")
            con_det_form = ConsignmentdetailaddForm()
        else:
            print("I am inside get edit consignmentdetails")
            try:
                consignmentdetail = ConsignmentdetailInfo.objects.get(co_consignmentnumber=consignment_num)
            except ObjectDoesNotExist:
                consignmentdetail = None
            con_det_form = ConsignmentdetailaddForm(instance=consignmentdetail)
        context = {
            'first_name': first_name,
            'con_det_form': con_det_form,
            'enquiry_num': enquiry_num,
            'user_id': user_id,
            'consignmentdetail_list': ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num),
        }
        return render(request, "asset_mgt_app/consignmentdetail_add.html", context)
    else:
        if consignment_num==None:
            print("I am inside post add consignmentdetails")
            con_det_form = ConsignmentdetailaddForm(request.POST)
        else:
            print("I am inside post edit consignmentdetails")
            try:
                consignmentdetail = ConsignmentdetailInfo.objects.get(co_consignmentnumber=consignment_num)
            except ObjectDoesNotExist:
                consignmentdetail = None
            con_det_form = ConsignmentdetailaddForm(request.POST, instance=consignmentdetail)
        if con_det_form.is_valid():
            con_det_form.save()
            print("Main Form is Valid")
        else:
            print("Main Form is not Valid")

        return redirect('/SMS/enquirynote_list')
#Delete enquirynote
@login_required(login_url='login_page')
def enquirynote_delete(request,enquirynote_id):
    enquirynote = EnquirynoteInfo.objects.get(pk=enquirynote_id)
    enquirynote.delete()
    return redirect('/SMS/enquirynote_list')