from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
import json

from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa

from ..forms import ConsignmentdetailaddForm,ConsignmentgoodsaddForm
from ..models import VehiclemasterInfo,User_extInfo,Location_info,Vehicle_allotmentInfo,ConsignmentgoodsInfo,ConsignmentdetailInfo,CustomerInfo,EnquirynoteInfo, MyUser
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime

from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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
    user_branch = User_extInfo.objects.get(user_id=user_id).emp_branch
    user_branch_id = Location_info.objects.get(loc_name=user_branch).id
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
        'user_branch': user_branch,
    }
    return render(request, "asset_mgt_app/consignmentdetail_nav.html", context)

@login_required(login_url='login_page')
def consignmentdetail_add(request, consignmentdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    user_branch = User_extInfo.objects.get(user_id=user_id).emp_branch
    user_branch_id = Location_info.objects.get(loc_name=user_branch).id
    enquiry_num = request.session.get('ses_enqiury_num')
    enquiry_num_id = request.session.get('ses_enqiury_id')

    print("Enquiry Number:", enquiry_num)
    print("Enquiry ID:", enquiry_num_id)

    # enquiry_num_id = request.session.get('enquiry_num_id')
    consignmentgoods_id_val = request.session.get('ses_consignment_id')
    enquiry_num_id = request.session.get('ses_enqiury_id')
    has_invoice_or_ewaybill = ConsignmentgoodsInfo.objects.filter(
        cg_consignmentnumber=consignmentdetail_id
    ).filter(
        Q(cg_consignerinvoice__isnull=False, cg_consignerinvoice__gt='') |
        Q(cg_ebillno__isnull=False, cg_ebillno__gt='')
    ).exists()

    if consignmentdetail_id != 0:
        enquiry_num_id = ConsignmentdetailInfo.objects.get(id=consignmentdetail_id).co_enquirynumber.id

    if not enquiry_num_id or enquiry_num_id == 0:
        # Handle error, redirect or show message
        messages.error(request, "Invalid enquiry number. Please select a valid consignment.")
        return redirect('some_fallback_view')

    customer = EnquirynoteInfo.objects.get(pk=enquiry_num_id).en_customername
    customer_obj = CustomerInfo.objects.filter(cu_name=customer).first()
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
            'user_branch': user_branch,
            'has_invoice_or_ewaybill': has_invoice_or_ewaybill,  # ✅ Add this flag

        }
        return render(request, "asset_mgt_app/consignmentdetail_add.html", context)

    else:
        con_det_form = ConsignmentdetailaddForm(request.POST)

        if con_det_form.is_valid():
            vehicle_type = request.POST.get('vehicle_type_field')
            if consignmentdetail_id == 0:
                consignment_detail = con_det_form.save(commit=False)
                consignment_detail.save()  # Save to generate ID
                if user_branch_id == 1:
                    branch = 'BLR_'
                elif user_branch_id == 2:
                    branch = 'MAA_'
                elif user_branch_id == 3:
                    branch = 'PNY_'
                else:
                    branch = 'HYD_'
                # Generate consignment number based on its own ID
                consignment_detail.co_consignmentnumber = str(branch)+f"CON_{1000000 + consignment_detail.id}"
                consignment_detail.co_vehicletype = vehicle_type
                consignment_detail.save(update_fields=['co_consignmentnumber', 'co_vehicletype'])

                return redirect(f'/SMS/consignmentdetail_update/{consignment_detail.id}')
            else:
                consignmentdetail = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id)
                con_det_form = ConsignmentdetailaddForm(request.POST, instance=consignmentdetail)
                if con_det_form.is_valid():
                    consignment_detail = con_det_form.save(commit=False)
                    consignment_detail.co_vehicletype = vehicle_type
                    consignment_detail.save()

                    enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
                    consignmentdetail_list = list(
                        ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id)
                        .values_list('co_consignmentnumber', flat=True)
                    )
                    consignmentdetail_list.sort()
                    EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(
                        en_consignmentdetails=consignmentdetail_list)

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

    # Filters
    customer_id = request.GET.get('customer')
    updated_by_id = request.GET.get('updated_by')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    branch = request.GET.get('branch', '')

    customers = CustomerInfo.objects.all().order_by('cu_name')
    employees = User_extInfo.objects.filter(
        emp_organisation_id=2
    ).select_related('user').order_by('user__first_name')

    # Base Query
    consignment_qs = ConsignmentdetailInfo.objects.select_related(
        'co_enquirynumber',
        'co_customer',
        'co_status',
        'co_lastmodifiedby'
    ).prefetch_related('cg_consignmentnumber')

    # Apply Filters
    if customer_id:
        consignment_qs = consignment_qs.filter(co_customer_id=customer_id)

    if updated_by_id:
        consignment_qs = consignment_qs.filter(co_lastmodifiedby_id=updated_by_id)

    if date_from:
        consignment_qs = consignment_qs.filter(co_consignmentdate__gte=date_from)

    if date_to:
        consignment_qs = consignment_qs.filter(co_consignmentdate__lte=date_to)

    if branch == 'MAA':
        consignment_qs = consignment_qs.filter(co_consignmentnumber__istartswith='MAA')
    elif branch == 'BLR':
        consignment_qs = consignment_qs.filter(co_consignmentnumber__istartswith='BLR')

    consignments = []

    # Build presentation fields (replacing @property logic)
    for obj in consignment_qs.order_by('-id'):

        goods = obj.cg_consignmentnumber.first()

        obj.co_consigner = goods.cg_consigner if goods else ''
        obj.co_consignee = goods.cg_consignee if goods else ''
        obj.co_consignerinvoice = goods.cg_consignerinvoice if goods else ''
        obj.co_consignervalue = goods.cg_consignervalue if goods else ''
        obj.co_valueininr = goods.cg_valueininr if goods else ''
        obj.co_noofpieces = goods.cg_qty if goods else ''
        obj.co_weight = goods.cg_weight if goods else ''
        obj.co_ebillno = goods.cg_ebillno if goods else ''
        obj.co_dateofissue = goods.cg_dateofissue if goods else ''
        obj.co_dateofvalidity = goods.cg_dateofvalidity if goods else ''
        obj.co_dimension = (
            f"{goods.cg_length}x{goods.cg_width}x{goods.cg_height}" if goods else ''
        )

        obj.co_movement = (
            obj.co_enquirynumber.en_movement_type if obj.co_enquirynumber else ''
        )

        obj.display_from_location = (
            obj.co_fromlocaion or
            (obj.co_enquirynumber.en_fromlocaion if obj.co_enquirynumber else '')
        )

        obj.display_to_location = (
            obj.co_tolocation or
            (obj.co_enquirynumber.en_tolocation if obj.co_enquirynumber else '')
        )

        consignments.append(obj)

    context = {
        'consignmentdetail_list': consignments,
        'first_name': first_name,
        'customers': customers,
        'employees': employees,
        'selected_customer': int(customer_id) if customer_id else None,
        'selected_updated_by': int(updated_by_id) if updated_by_id else None,
        'date_from': date_from,
        'date_to': date_to,
        'branch': branch,
    }

    return render(request, "asset_mgt_app/consignmentdetail_list.html", context)


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
@xframe_options_exempt
def consignment_note_pdf(request, consignment_note_id=0):
    try:
        consignment = ConsignmentdetailInfo.objects.get(pk=consignment_note_id)
        consignment_num = consignment.co_consignmentnumber
        vehicle_reg_num = consignment.co_vehicelnumber  # e.g., TN22DF8390
        enquiry_id = consignment.co_enquirynumber_id

        # All related goods
        consignment_goods_list = ConsignmentgoodsInfo.objects.filter(
            cg_consignmentnumber=consignment_note_id
        ).order_by('id')

        vehicle_detail = None

        # ----------------------------------------------------
        # 1️⃣ FIRST TRY → MARKET VEHICLE MATCH (string match)
        # ----------------------------------------------------
        vehicle_detail = Vehicle_allotmentInfo.objects.filter(
            va_enquirynumber=enquiry_id,
            va_vehiclenumber_mkt=vehicle_reg_num
        ).first()

        # ----------------------------------------------------
        # 2️⃣ IF NOT MARKET → TRY OWN VEHICLE MATCH (FK)
        # ----------------------------------------------------
        if not vehicle_detail:
            try:
                vehicle_master = VehiclemasterInfo.objects.get(vm_registrationnumber=vehicle_reg_num)
                vehicle_detail = Vehicle_allotmentInfo.objects.filter(
                    va_enquirynumber=enquiry_id,
                    va_vehiclenumber=vehicle_master.id
                ).first()
            except VehiclemasterInfo.DoesNotExist:
                vehicle_detail = None

        # ----------------------------------------------------
        # 3️⃣ EXTRACT VALUES TO SEND TO TEMPLATE
        # ----------------------------------------------------
        vehicle_number_val = []
        driver_name = []
        driver_lic = []
        driver_number = []

        if vehicle_detail:
            # OWN VEHICLE
            if vehicle_detail.va_vehiclenumber:
                vehicle_number_val.append(vehicle_detail.va_vehiclenumber.vm_registrationnumber)

            # MARKET VEHICLE
            if vehicle_detail.va_vehiclenumber_mkt:
                vehicle_number_val.append(vehicle_detail.va_vehiclenumber_mkt)

            driver_name.append(vehicle_detail.va_drivername)
            driver_lic.append(vehicle_detail.va_driver_lic)
            driver_number.append(vehicle_detail.va_drivernumber)

        context = {
            'consignment_details': [consignment],
            'consignment_goods_list': consignment_goods_list,
            'vehicle_details': [vehicle_detail] if vehicle_detail else [],
            'vehicle_number': vehicle_number_val,
            'Driver_name': driver_name,
            'Driver_lic': driver_lic,
            'Driver_number': driver_number,
        }

        # ----------------------------------------------------
        #           CREATE PDF
        # ----------------------------------------------------
        file_name = f"Consignment_Note_{consignment_num}.pdf"
        template_path = 'asset_mgt_app/consignement_note_pdf.html'

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename={file_name}'

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
