from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
import json

from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa

from ..forms import ConsignmentdetailaddForm,ConsignmentgoodsaddForm
from ..models import VehiclemasterInfo,Vehicle_allotmentInfo,ConsignmentgoodsInfo,ConsignmentdetailInfo,CustomerInfo,EnquirynoteInfo
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
@login_required(login_url='login_page')
def consignmentdetail_enquiry(request, enquiry_id, consignment_number):
    enquiry = get_object_or_404(EnquirynoteInfo, pk=enquiry_id)
    print('consignment_number', consignment_number)

    # ✅ Set both session keys here
    request.session['ses_enqiury_id'] = enquiry.id
    request.session['ses_enqiury_num'] = enquiry.en_enquirynumber

    if consignment_number == 'none' or consignment_number == '':
        return redirect('consignmentdetail_insert')
    else:
        return redirect('consignmentdetail_update', consignmentdetail_id=consignment_number)


@login_required(login_url='login_page')
def consignmentdetail_nav(request,consignmentdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print("I am inside Get add consignmentdetails")
    enquiry_num = EnquirynoteInfo.objects.get(pk=consignmentdetail_id).en_enquirynumber
    enquiry_num_id = consignmentdetail_id
    request.session['ses_enqiury_num'] = enquiry_num
    request.session['ses_enqiury_num_id'] = enquiry_num_id
    consignmentdetail_list=ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id)
    print('enquiry_num',enquiry_num)
    context = {
        'first_name': first_name,
        'user_id': user_id,
        'enquiry_num': enquiry_num,
        'enquiry_num_id': enquiry_num_id,
        'consignmentdetail_list': consignmentdetail_list,
        'consignmentdetail_id': consignmentdetail_id,
    }
    return render(request, "asset_mgt_app/consignmentdetail_nav.html", context)
@login_required(login_url='login_page')
def consignmentdetail_add(request, consignmentdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    enquiry_num = request.session.get('ses_enqiury_num')
    enquiry_num_id = request.session.get('ses_enqiury_id')

    print("Enquiry Number:", enquiry_num)
    print("Enquiry ID:", enquiry_num_id)

    # enquiry_num_id = request.session.get('enquiry_num_id')
    consignmentgoods_id_val = request.session.get('ses_consignment_id')
    enquiry_num_id = request.session.get('ses_enqiury_id')

    if consignmentdetail_id != 0:
        enquiry_num_id = ConsignmentdetailInfo.objects.get(id=consignmentdetail_id).co_enquirynumber.id

    if not enquiry_num_id or enquiry_num_id == 0:
        # Handle error, redirect or show message
        messages.error(request, "Invalid enquiry number. Please select a valid consignment.")
        return redirect('some_fallback_view')

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
        }
        return render(request, "asset_mgt_app/consignmentdetail_add.html", context)

    else:
        con_det_form = ConsignmentdetailaddForm(request.POST)

        if con_det_form.is_valid():
            vehicle_type = request.POST.get('vehicle_type_field')
            if consignmentdetail_id == 0:
                consignment_detail = con_det_form.save(commit=False)
                consignment_detail.save()  # Save to generate ID

                # Generate consignment number based on its own ID
                consignment_detail.co_consignmentnumber = f"CON_{1000000 + consignment_detail.id}"
                consignment_detail.co_vehicletype = vehicle_type
                consignment_detail.save(update_fields=['co_consignmentnumber', 'co_vehicletype'])

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
        else:
            for field, errors in con_det_form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")
                    messages.error(request, f"Error in {field}: {error}")
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
def consignment_note_pdf(request, consignment_note_id=0):
    try:
        consignment = ConsignmentdetailInfo.objects.get(pk=consignment_note_id)
        consignment_num = consignment.co_consignmentnumber
        vehicle_reg_num = consignment.co_vehicelnumber  # e.g., 'TN22DF8390'
        enquiry_id = consignment.co_enquirynumber_id

        # Get all related goods
        consignment_goods_list = ConsignmentgoodsInfo.objects.filter(
            cg_consignmentnumber=consignment_note_id
        ).order_by('id')

        # Get the VehiclemasterInfo ID for this registration number
        try:
            vehicle_master = VehiclemasterInfo.objects.get(vm_registrationnumber=vehicle_reg_num)
        except VehiclemasterInfo.DoesNotExist:
            vehicle_master = None

        vehicle_detail = None
        if vehicle_master:
            # Now filter Vehicle_allotmentInfo using the FK ID
            vehicle_detail = Vehicle_allotmentInfo.objects.filter(
                va_enquirynumber=enquiry_id
            ).filter(
                Q(va_vehiclenumber=vehicle_master.id) | Q(va_vehiclenumber_mkt=vehicle_master.id)
            ).first()

        if vehicle_detail:
            vehicle_number_val = [vehicle_reg_num]  # Already have registration number
            driver_name = [vehicle_detail.va_drivername]
            driver_lic = [vehicle_detail.va_driver_lic]
            driver_number = [vehicle_detail.va_drivernumber]
        else:
            vehicle_number_val = driver_name = driver_lic = driver_number = []

        context = {
            'consignment_details': [consignment],
            'consignment_goods_list': consignment_goods_list,
            'vehicle_details': [vehicle_detail] if vehicle_detail else [],
            'vehicle_number': vehicle_number_val,
            'Driver_name': driver_name,
            'Driver_lic': driver_lic,
            'Driver_number': driver_number,
        }

        # Prepare PDF
        file_name = f"Consignment_Note_{consignment_num}.pdf"
        template_path = 'asset_mgt_app/consignement_note_pdf.html'
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={file_name}'

        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')

        return response

    except ConsignmentdetailInfo.DoesNotExist:
        return HttpResponse("Invalid consignment note ID.")

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
    print('final_vehicle_list',final_vehicle_list)
    used_vehicles = list(
        ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_number)
        .values_list('co_vehicelnumber', flat=True)
    )
    print('used_vehicles',used_vehicles)
    available_vehicle_list = [v for v in final_vehicle_list if v not in used_vehicles]
    try:
        selected_vehicles = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id_val).co_vehicelnumber
    except ConsignmentdetailInfo.DoesNotExist:
        selected_vehicles = None  # Or set a default value
    print('selected_vehicles',selected_vehicles)
    print('available_vehicle_list',available_vehicle_list)
    return JsonResponse({'final_vehicle_list': available_vehicle_list,'selected_vehicles':selected_vehicles})


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
    en_fromlocation = request.session.get('ses_en_fromlocation')
    en_tolocation = request.session.get('ses_en_tolocation')

    print("in pdf function")
    print("Enquiry ID:", enquiry_num)
    print("Consignment ID:", consignment_id)
    print("From Location:", en_fromlocation)
    print("To Location:", en_tolocation)

    enquiry = EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num)
    vehicle = Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num)
    consignment = get_object_or_404(ConsignmentdetailInfo, pk=consignment_id)

    today = datetime.now().strftime("%d-%b-%Y")

    context = {
        'vehicle': vehicle,
        'consignment': consignment,
        'en_fromlocation': en_fromlocation,
        'en_tolocation': en_tolocation,
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
