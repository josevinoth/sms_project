from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from ..forms import ConsignmentdetailaddForm
from ..models import Vehicle_allotmentInfo,ConsignmentgoodsInfo,ConsignmentdetailInfo,CustomerInfo,EnquirynoteInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def consignmentdetail_nav(request,consignmentdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print("I am inside Get add consignmentdetails")
    enquiry_num = EnquirynoteInfo.objects.get(pk=consignmentdetail_id).en_enquirynumber
    enquiry_num_id = EnquirynoteInfo.objects.get(pk=consignmentdetail_id).id
    request.session['ses_enqiury_num'] = enquiry_num
    consignmentdetail_list=ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id)
    context = {
        'first_name': first_name,
        'user_id': user_id,
        'enquiry_num': enquiry_num,
        'enquiry_num_id': enquiry_num_id,
        'consignmentdetail_list': consignmentdetail_list,
    }
    return render(request, "asset_mgt_app/consignmentdetail_nav.html", context)
@login_required(login_url='login_page')
def consignmentdetail_add(request,consignmentdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    enquiry_num = request.session.get('ses_enqiury_num')
    customer = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).en_customername
    customer_id = CustomerInfo.objects.get(cu_name=customer).id
    if request.method == "GET":
        if consignmentdetail_id == 0:
            print("I am inside Get add consignmentdetails")
            con_det_form = ConsignmentdetailaddForm()
            enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
        else:
            enquiry_num = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id).co_enquirynumber
            consignmentdetail=ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id)
            enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
            con_det_form = ConsignmentdetailaddForm(instance=consignmentdetail)
        context = {
            'first_name': first_name,
            'user_id': user_id,
            'con_det_form': con_det_form,
            'enquiry_num': enquiry_num,
            'enquiry_num_id': enquiry_num_id,
            'customer_id': customer_id,
            'consignmentdetail_list': ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id),
        }
        return render(request, "asset_mgt_app/consignmentdetail_add.html", context)
    else:
        if consignmentdetail_id == 0:
            print("I am inside post add consignmentdetails")
            con_det_form = ConsignmentdetailaddForm(request.POST)
            if con_det_form.is_valid():
                try:
                    last_id = ConsignmentdetailInfo.objects.latest('id').id
                    cons_num_next = str('CON_') + str(int(((ConsignmentdetailInfo.objects.get(id=last_id)).co_consignmentnumber).replace('CON_', '')) + 1)
                except ObjectDoesNotExist:
                    cons_num_next = str('CON_') + str(1000000)
                con_det_form.save()
                print("Consignement Main Form Saved")
                last_id = ConsignmentdetailInfo.objects.latest('id').id
                ConsignmentdetailInfo.objects.filter(id=last_id).update(co_consignmentnumber=cons_num_next)
                messages.success(request, 'Record Updated Successfully')
                cons_id = ConsignmentdetailInfo.objects.get(co_consignmentnumber=cons_num_next).id
                return redirect('/SMS/consignmentdetail_update/' + str(cons_id))
            else:
                print("Consignement Main Form not Saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("I am inside post edit consignmentdetails")
            consignmentdetail = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id)
            con_det_form = ConsignmentdetailaddForm(request.POST,instance=consignmentdetail)
            if con_det_form.is_valid():
                con_det_form.save()
                print("Main Form is Valid")
                enquiry_num = request.session.get('ses_enqiury_num')
                enquiry_num_id=EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
                consignmentdetail_list=list(ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id).values_list('co_consignmentnumber',flat=True))
                consignmentdetail_list.sort()
                EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_consignmentdetails=consignmentdetail_list)
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
    print("Inside Delete")
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

@login_required(login_url='login_page')
def consignment_note_pdf(request,consignment_note_id=0):
    consignment_num=ConsignmentdetailInfo.objects.get(pk=consignment_note_id).co_consignmentnumber
    consignment_details = (ConsignmentdetailInfo.objects.filter(pk=consignment_note_id)).order_by('id')
    consignment_goods_list=(ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber=consignment_note_id)).order_by('id')
    vehicle_allotment_list=(Vehicle_allotmentInfo.objects.filter(va_consignmentnumber=consignment_note_id)).order_by('id')
    context = {
        'consignment_details': consignment_details,
        'consignment_goods_list': consignment_goods_list,
        'vehicle_allotment_list': vehicle_allotment_list,
    }
    file_name = str("Consignement Note_") + str(consignment_num) + str(".pdf")
    template_path = 'asset_mgt_app/consignement_note_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    template = get_template(template_path)
    html = template.render(context)

    # Create PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We has some error <pre>' + html + '</pre>')
    return response