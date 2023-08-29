from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from ..forms import ConsignmentdetailaddForm
from ..models import ConsignmentdetailInfo,CustomerInfo,EnquirynoteInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def consignmentdetail_nav(request,consignmentdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print("I am inside Get add consignmentdetails")
    # con_det_form = ConsignmentdetailaddForm()
    con_det_form = ConsignmentdetailaddForm(request.POST)
    enquiry_num = EnquirynoteInfo.objects.get(pk=consignmentdetail_id).en_enquirynumber
    request.session['ses_enqiury_id'] = enquiry_num
    consignmentdetail_list=ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num)
    customer=EnquirynoteInfo.objects.get(pk=consignmentdetail_id).en_customername
    customer_id=CustomerInfo.objects.get(cu_name=customer).id
    context = {
        'first_name': first_name,
        'user_id': user_id,
        'con_det_form': con_det_form,
        'enquiry_num': enquiry_num,
        'consignmentdetail_list': consignmentdetail_list,
        'customer_id': customer_id,
    }
    if con_det_form.is_valid():
        con_det_form.save()
        print("Main Form is Valid")
        consignmentdetail_list = ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num).values_list('co_consignmentnumber', flat=True)
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_consignmentdetails=list(consignmentdetail_list))
        messages.success(request, 'Record Updated Successfully')
    else:
        print("Main Form is not Valid")
        messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
    return render(request, "asset_mgt_app/consignmentdetail_add.html", context)
@login_required(login_url='login_page')
def consignmentdetail_add(request,consignmentdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    enquiry_num = request.session.get('ses_enqiury_id')
    customer = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).en_customername
    customer_id = CustomerInfo.objects.get(cu_name=customer).id
    if request.method == "GET":
        if consignmentdetail_id == 0:
            print("I am inside Get add consignmentdetails")
            con_det_form = ConsignmentdetailaddForm()
        else:
            enquiry_num = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id).co_enquirynumber
            consignmentdetail=ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id)
            con_det_form = ConsignmentdetailaddForm(instance=consignmentdetail)
        context = {
            'first_name': first_name,
            'user_id': user_id,
            'con_det_form': con_det_form,
            'enquiry_num': enquiry_num,
            'customer_id': customer_id,
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
            enquiry_num = request.session.get('ses_enqiury_id')
            consignmentdetail_list=ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num).values_list('co_consignmentnumber',flat=True)
            EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_consignmentdetails=list(consignmentdetail_list))
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
    enquiry_num = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id).co_enquirynumber
    consignmentdetail.delete()
    try:
        consignmentdetail_list = ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num).values_list('co_consignmentnumber', flat=True)
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_consignmentdetails=list(consignmentdetail_list))
    except ObjectDoesNotExist:
        consignmentdetail_list=[]
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_consignmentdetails=list(consignmentdetail_list))
    # return redirect('/SMS/consignmentdetail_list')
    return redirect(request.META['HTTP_REFERER'])