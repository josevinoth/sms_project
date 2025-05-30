from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
import json
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa

from ..forms import ConsignmentdetailaddForm,ConsignmentgoodsaddForm
from ..models import VehiclemasterInfo,Vehicle_allotmentInfo,ConsignmentgoodsInfo,ConsignmentdetailInfo,CustomerInfo,EnquirynoteInfo
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime


@login_required(login_url='login_page')
def consignmentdetail_nav(request, consignmentdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print("I am inside Get add consignmentdetails")

    enquiry_num_id = consignmentdetail_id
    request.session['ses_enqiury_num_id'] = enquiry_num_id

    enquiry_obj = EnquirynoteInfo.objects.get(pk=enquiry_num_id)
    enquiry_num = enquiry_obj.en_enquirynumber
    request.session['ses_enqiury_num'] = enquiry_num
    vehicle_id_param = request.GET.get('vehicle_number')

    consignmentdetail_list = ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id)

    con_det_form = ConsignmentdetailaddForm()
    form = ConsignmentgoodsaddForm()

    context = {
        'first_name': first_name,
        'user_id': user_id,
        'con_det_form': con_det_form,
        'form': form,
        'enquiry_num': enquiry_num,
        'enquiry_num_id': enquiry_num_id,
        'consignmentdetail_list': consignmentdetail_list,
        'consignmentgoods_list': [],
        'vehicle_type': '',
        'vehicle_id_param': vehicle_id_param,
        'consignmentdetail_id': 0,
        'consignmentgoods_id_val': request.session.get('ses_consignment_id'),
    }
    return render(request, "asset_mgt_app/consignmentdetail_add.html", context)
@login_required(login_url='login_page')
def consignmentdetail_add(request, consignmentdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    enquiry_num = request.session.get('ses_enqiury_num')
    enquiry_num_id = request.session.get('ses_enqiury_num_id')
    consignmentgoods_id_val = request.session.get('ses_consignment_id')
    vehicle_id_param = request.GET.get('vehicle_number')


    customer = EnquirynoteInfo.objects.get(pk=enquiry_num_id).en_customername
    customer_obj = CustomerInfo.objects.get(cu_name=customer)
    customer_id = customer_obj.id
    customer_code = customer_obj.cu_customercode

    if request.method == "GET":
        if consignmentdetail_id == 0:
            con_det_form = ConsignmentdetailaddForm()
            form = ConsignmentgoodsaddForm()
            vehicle_type = ""
        else:
            request.session['ses_consignment_detail_id'] = consignmentdetail_id
            enquiry_num = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id).co_enquirynumber
            consignmentdetail = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id)
            con_det_form = ConsignmentdetailaddForm(instance=consignmentdetail)
            form = ConsignmentgoodsaddForm()
            vehicle_type = consignmentdetail.co_vehicletype

        context = {
            'first_name': first_name,
            'user_id': user_id,
            'con_det_form': con_det_form,
            'form': form,
            'enquiry_num': enquiry_num,
            'enquiry_num_id': enquiry_num_id,
            'customer_id': customer_id,
            'customer_code': customer_code,
            'consignmentdetail_id': consignmentdetail_id,
            'consignmentgoods_id_val': consignmentgoods_id_val,
            'consignmentdetail_list': ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id),
            'consignmentgoods_list': ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber=consignmentdetail_id),
            'vehicle_type': vehicle_type,
            'vehicle_id_param': vehicle_id_param,
        }
        return render(request, "asset_mgt_app/consignmentdetail_add.html", context)

    else:
        con_det_form = ConsignmentdetailaddForm(request.POST)

        if con_det_form.is_valid():
            vehicle_type = request.POST.get('vehicle_type_field')
            if consignmentdetail_id == 0:
                last_id = ConsignmentdetailInfo.objects.latest('id').id if ConsignmentdetailInfo.objects.exists() else 0
                cons_num_next = f"CON_{1000000 if last_id == 0 else int(ConsignmentdetailInfo.objects.get(id=last_id).co_consignmentnumber.replace('CON_', '')) + 1}"

                consignment_detail = con_det_form.save()
                consignment_detail.co_consignmentnumber = cons_num_next
                consignment_detail.co_vehicletype = vehicle_type
                consignment_detail.save()

                for field, errors in con_det_form.errors.items():
                    for error in errors:
                        print(f"Error in {field}: {error}")
                        messages.error(request, f"Error in {field}: {error}")
                messages.success(request, 'Record Updated Successfully')
                return redirect(f'/SMS/consignmentdetail_update/{consignment_detail.id}')
            else:
                consignmentdetail = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id)
                con_det_form = ConsignmentdetailaddForm(request.POST, instance=consignmentdetail)
                if con_det_form.is_valid():
                    consignment_detail = con_det_form.save(commit=False)  # <-- Don't save yet
                    consignment_detail.co_vehicletype = vehicle_type
                    con_det_form.save()
                    enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
                    consignmentdetail_list = list(ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id).values_list('co_consignmentnumber', flat=True))
                    consignmentdetail_list.sort()
                    EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_consignmentdetails=consignmentdetail_list)

                    messages.success(request, 'Record Updated Successfully')

                # return redirect('/SMS/consignmentdetail_list/')
                return redirect(request.META['HTTP_REFERER'])

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



@login_required(login_url='login_page')
def vehicle_allotted(request):
    enquiry_number = request.GET.get('enquiry_number')
    consignmentdetail_id_val = request.GET.get('consignmentdetail_id_val')
    vehicle_number_param = request.GET.get('vehicle_number', '')

    print(consignmentdetail_id_val)
    requested_vehicles = list(
        Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number)
        .select_related('va_vehiclenumber')
        .values_list('va_vehiclenumber__vm_registrationnumber', flat=True)
    )
    requested_vehicles_market = list(
        Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number)
        .values_list('va_vehiclenumber_mkt', flat=True)
    )

    final_vehicle_list = [v for v in (requested_vehicles + requested_vehicles_market) if v]

    used_vehicles = list(
        ConsignmentdetailInfo.objects.exclude(pk=consignmentdetail_id_val)
        .values_list('co_vehicelnumber', flat=True)
    )

    available_vehicle_list = [v for v in final_vehicle_list if v not in used_vehicles]
    try:
        selected_vehicles = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id_val).co_vehicelnumber
    except ConsignmentdetailInfo.DoesNotExist:
        selected_vehicles = None  # Or set a default value
    return JsonResponse({'final_vehicle_list': available_vehicle_list,'selected_vehicles':vehicle_number_param})


@login_required(login_url='login_page')
def consignmentdetail_cancel(request):
    first_name = request.session.get('first_name')
    enquiry_num_id = request.session.get('ses_enqiury_num_id')
    return redirect('/SMS/consignmentdetail_nav/'+ str(enquiry_num_id))


@login_required(login_url='login_page')
def get_vehicle_type(request, vehicle_id):
    try:
        vehicle_master = VehiclemasterInfo.objects.get(vm_registrationnumber=vehicle_id)
        allotment = Vehicle_allotmentInfo.objects.filter(va_vehiclenumber=vehicle_master).first()
    except VehiclemasterInfo.DoesNotExist:

        allotment = Vehicle_allotmentInfo.objects.filter(va_vehiclenumber_mkt=vehicle_id).first()

    if allotment and allotment.va_vehicletype_placed:
        vehicle_type = allotment.va_vehicletype_placed.vt_vehicletype
    else:
        vehicle_type = None

    return JsonResponse({'vehicle_type': vehicle_type})

@login_required(login_url='login_page')
def consignment_pdf_download(request):
    consignment_id = request.session.get('ses_consignment_detail_id')
    enquiry_num = request.session.get('ses_enqiury_num_id')
    print("in pdf function")
    print(enquiry_num)
    print(consignment_id)

    enquiry = EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num)
    print(enquiry)
    vehicle = Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num)
    consignment = get_object_or_404(ConsignmentdetailInfo, pk=consignment_id)
    # enquiry = get_object_or_404(EnquirynoteInfo, en_enquirynumber=enquiry_num)

    today = datetime.now().strftime("%d-%b-%Y")

    context = {
        'vehicle': vehicle,
        'consignment': consignment,
        # 'enquiry': enquiry,
        'today_date': today,
    }

    file_name = f"Consignment_{consignment.co_consignmentnumber}.pdf"
    template_path = 'asset_mgt_app/lorryhirechallan_pdf_template.html'

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF <pre>' + html + '</pre>')

    return response