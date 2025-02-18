from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from ..forms import ConsignmentdetailaddForm,ConsignmentgoodsaddForm,ConsignmentgoodsnewaddForm
from ..models import VehiclemasterInfo,Vehicle_allotmentInfo,ConsignmentgoodsInfo,ConsignmentdetailInfo,CustomerInfo,EnquirynoteInfo
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
def consignmentdetail_add(request, consignmentdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    enquiry_num = request.session.get('ses_enqiury_num')
    consignmentgoods_id_val = request.session.get('ses_consignment_id')

    customer = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).en_customername
    customer_obj = CustomerInfo.objects.get(cu_name=customer)
    customer_id = customer_obj.id
    customer_code = customer_obj.cu_customercode

    if request.method == "GET":
        if consignmentdetail_id == 0:
            con_det_form = ConsignmentdetailaddForm()
            form = ConsignmentgoodsaddForm()
            cn_form = ConsignmentgoodsnewaddForm()
            enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
        else:
            enquiry_num = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id).co_enquirynumber
            consignmentdetail = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id)
            enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
            con_det_form = ConsignmentdetailaddForm(instance=consignmentdetail)
            form = ConsignmentgoodsaddForm()
            cn_form = ConsignmentgoodsnewaddForm()

        context = {
            'first_name': first_name,
            'user_id': user_id,
            'con_det_form': con_det_form,
            'form': form,
            'cn_form': cn_form,
            'enquiry_num': enquiry_num,
            'enquiry_num_id': enquiry_num_id,
            'customer_id': customer_id,
            'customer_code': customer_code,
            'consignmentgoods_id_val': consignmentgoods_id_val,
            'consignmentdetail_list': ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id),
        }
        return render(request, "asset_mgt_app/consignmentdetail_add.html", context)

    else:
        con_det_form = ConsignmentdetailaddForm(request.POST)
        form = ConsignmentgoodsaddForm(request.POST)
        cn_form = ConsignmentgoodsnewaddForm(request.POST)

        if con_det_form.is_valid() and form.is_valid() and cn_form.is_valid():
            if consignmentdetail_id == 0:
                last_id = ConsignmentdetailInfo.objects.latest('id').id if ConsignmentdetailInfo.objects.exists() else 0
                cons_num_next = f"CON_{1000000 if last_id == 0 else int(ConsignmentdetailInfo.objects.get(id=last_id).co_consignmentnumber.replace('CON_', '')) + 1}"

                consignment_detail = con_det_form.save()
                consignment_detail.co_consignmentnumber = cons_num_next
                consignment_detail.save()

                goods = form.save(commit=False)
                goods.consignmentdetail = consignment_detail
                goods.save()

                new_goods = cn_form.save(commit=False)
                new_goods.consignmentdetail = consignment_detail
                new_goods.save()

                messages.success(request, 'Record Updated Successfully')
                return redirect(f'/SMS/consignmentdetail_update/{consignment_detail.id}')
            else:
                consignmentdetail = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id)
                con_det_form = ConsignmentdetailaddForm(request.POST, instance=consignmentdetail)
                if con_det_form.is_valid():
                    con_det_form.save()
                    enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
                    consignmentdetail_list = list(ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id).values_list('co_consignmentnumber', flat=True))
                    consignmentdetail_list.sort()
                    EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_consignmentdetails=consignmentdetail_list)

                    messages.success(request, 'Record Updated Successfully')

                return redirect('/SMS/consignmentdetail_list/')

        messages.error(request, 'Record Not Saved. Please Enter All Required Fields')
        return redirect(request.META['HTTP_REFERER'])

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
    consignment_details = (ConsignmentdetailInfo.objects.filter(pk=consignment_note_id))
    consignment_goods_list=(ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber=consignment_note_id)).order_by('id')
    vehicle_details=(Vehicle_allotmentInfo.objects.filter(va_consignmentnumber=consignment_note_id))
    vehicle_number=(Vehicle_allotmentInfo.objects.filter(va_consignmentnumber=consignment_note_id).values_list('va_vehiclenumber',flat=True))
    Driver_name=(Vehicle_allotmentInfo.objects.filter(va_consignmentnumber=consignment_note_id).values_list('va_drivername',flat=True))
    Driver_lic=(Vehicle_allotmentInfo.objects.filter(va_consignmentnumber=consignment_note_id).values_list('va_driver_lic',flat=True))
    Driver_number=(Vehicle_allotmentInfo.objects.filter(va_consignmentnumber=consignment_note_id).values_list('va_drivernumber',flat=True))
    vehicle_number_val=[]
    for i in vehicle_number:
        reg_number=VehiclemasterInfo.objects.get(pk=i).vm_registrationnumber
        vehicle_number_val.append(reg_number)

    context = {
        'consignment_details': consignment_details,
        'consignment_goods_list': consignment_goods_list,
        'vehicle_details': vehicle_details,
        'vehicle_number': list(vehicle_number_val),
        'Driver_name': list(Driver_name),
        'Driver_lic': list(Driver_lic),
        'Driver_number': list(Driver_number),
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