from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
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
            if form.is_valid():
                try:
                    last_id = EnquirynoteInfo.objects.latest('id').id
                    enquiry_num_next = str('EN_') + str(
                        int(((EnquirynoteInfo.objects.get(id=last_id)).en_enquirynumber).replace('EN_', '')) + 1)
                except ObjectDoesNotExist:
                    enquiry_num_next = str('EN_') + str(1000000)
                form.save()
                print("Enquiry Main Form Saved")
                last_id = EnquirynoteInfo.objects.latest('id').id
                EnquirynoteInfo.objects.filter(id=last_id).update(en_enquirynumber=enquiry_num_next)
                messages.success(request, 'Record Updated Successfully')
                enquiry_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num_next).id
                return redirect('/SMS/enquirynote_update/' + str(enquiry_id))
            else:
                print("Enquiry Main Form not Saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("I am inside post edit Enquirynote")
            enquirynote = EnquirynoteInfo.objects.get(pk=enquirynote_id)
            form = EnquirynoteaddForm(request.POST,instance=enquirynote)
            if form.is_valid():
                form.save()
                print("Enquiry Main Form Saved")
                messages.success(request, 'Record Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
            else:
                print("Enquiry Main Form not Saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
                return redirect(request.META['HTTP_REFERER'])
            # return redirect('/SMS/enquirynote_list')

# List enquirynote
@login_required(login_url='login_page')
def enquirynote_list(request):
    global consignment_status_id, trip_details_status_id
    print("Inside Enquiry List")
    first_name = request.session.get('first_name')
    enquiry_num_list=EnquirynoteInfo.objects.all()
    for m in enquiry_num_list:
        try:
            consignment_status_id_list=[]
            consignment_status = ConsignmentdetailInfo.objects.filter(co_enquirynumber=m).values_list('co_status',flat=True)
            for i in consignment_status:
                consignment_status_id_list = consignment_status_id_list.append(StatusList.objects.get(status_title=i).id)
            if all(element == 5 for element in (consignment_status_id_list)):
                consignment_status_id=5
        except ObjectDoesNotExist:
            consignment_status_id=6
        try:
            trip_status_id_list=[]
            trip_details_status = TripdetailInfo.objects.filter(tr_enquirynumber=m).values_list('tr_status',flat=True)
            for j in trip_details_status:
                trip_status_id_list = trip_status_id_list.append(StatusList.objects.get(status_title=j).id)
            if all(element == 5 for element in (trip_status_id_list)):
                trip_details_status_id=5
        except ObjectDoesNotExist:
            trip_details_status_id = 6
        try:
            trip_closure_status_id=[]
            trip_closure_status = TripclosureInfo.objects.filter(tc_enquirynumber=m).values_list('tc_financestatus',flat=True)
            for k in trip_closure_status:
                trip_closure_status_id.append(StatusList.objects.get(status_title=k).id)
            if all(element == 5 for element in (trip_closure_status_id)):
                trip_closure_status_id=5
        except ObjectDoesNotExist:
            trip_closure_status_id = 6

        if consignment_status_id == 5 and trip_details_status_id==5 and trip_closure_status_id==5:
            EnquirynoteInfo.objects.filter(en_enquirynumber=m).update(en_status=5)
        else:
            EnquirynoteInfo.objects.filter(en_enquirynumber=m).update(en_status=6)

    context = {
                'enquirynote_list' : EnquirynoteInfo.objects.all(),
                'consignmentdetail_list': ConsignmentdetailInfo.objects.all(),
                'tripdetails_list': TripdetailInfo.objects.all(),
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
    enquiry_num = EnquirynoteInfo.objects.get(pk=enquirynote_id).en_enquirynumber
    enquiry_num_id = EnquirynoteInfo.objects.get(pk=enquirynote_id).id
    consignment_num_list = list(ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id).values_list('co_consignmentnumber',flat=True))
    tripdetails_list=list(TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num_id).values_list('tr_tripnumber',flat=True))
    for i in consignment_num_list:
        consignment_note=ConsignmentdetailInfo.objects.get(co_consignmentnumber=i)
        consignment_note.delete()
    for j in tripdetails_list:
        tripdetails_note=TripdetailInfo.objects.get(tr_tripnumber=j)
        tripdetails_note.delete()
    enquirynote = EnquirynoteInfo.objects.get(pk=enquirynote_id)
    enquirynote.delete()
    return redirect('/SMS/enquirynote_list')