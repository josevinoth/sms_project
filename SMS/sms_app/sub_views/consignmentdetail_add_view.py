from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..forms import ConsignmentdetailaddForm
from ..models import ConsignmentdetailInfo,VehicledetailInfo,EnquirynoteInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def consignmentdetail_add(request,consignmentdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if consignmentdetail_id == 0:
            print("I am inside Get add consignmentdetails")
            con_det_form = ConsignmentdetailaddForm()
            enquiry_num = request.session.get('ses_enquiry_note')
            print(enquiry_num)
        else:
            print("I am inside get edit consignmentdetails")
            consignmentdetail=ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id)
            con_det_form = ConsignmentdetailaddForm(instance=consignmentdetail)
            enquiry_num=ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id).co_enquirynumber
        context = {
            'first_name': first_name,
            'user_id': user_id,
            'con_det_form': con_det_form,
            'enquiry_num': enquiry_num,
            'consignmentdetail_list': ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num),
        }
        return render(request, "asset_mgt_app/consignmentdetail_add.html", context)
    else:
        if consignmentdetail_id == 0:
            print("I am inside post add consignmentdetails")
            con_det_form = ConsignmentdetailaddForm(request.POST)
        else:
            print("I am inside post edit consignmentdetails")
            consignmentdetail = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id)
            con_det_form = ConsignmentdetailaddForm(request.POST,instance=consignmentdetail)
        if con_det_form.is_valid():
            con_det_form.save()
            print("Main Form is Valid")
            messages.success(request, 'Record Updated Successfully')
        else:
            print("Main Form is not Valid")
            messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
        return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/consignmentdetail_list')

# List consignmentdetail
@login_required(login_url='login_page')
def consignmentdetail_list(request):
    first_name = request.session.get('first_name')
    context = {
                'consignmentdetail_list' : ConsignmentdetailInfo.objects.all(),
                'first_name': first_name
            }
    return render(request,"asset_mgt_app/consignmentdetail_list.html",context)

#Delete consignmentdetail
@login_required(login_url='login_page')
def consignmentdetail_delete(request,consignmentdetail_id):
    consignmentdetail = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id)
    consignmentdetail.delete()
    return redirect('/SMS/consignmentdetail_list')