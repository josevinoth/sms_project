from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
import json

from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template, render_to_string
from xhtml2pdf import pisa

from ..forms import ConsignmentdetailaddForm,ConsignmentgoodsaddForm
from ..models import VehiclemasterInfo,User_extInfo,Location_info,Vehicle_allotmentInfo,ConsignmentgoodsInfo,ConsignmentdetailInfo,CustomerInfo,EnquirynoteInfo, MyUser, DeletionLog, TripdetailInfo, OwnershipInfo, VehicletypeInfo, Trip_category_info
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id

from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

@login_required(login_url='login_page')
def consignmentdetail_enquiry(request, enquiry_id, consignment_number):
    enquiry = get_object_or_404(EnquirynoteInfo, pk=enquiry_id)
    print('consignment_number', consignment_number)

    # ✅ Set both session keys here
    request.session['enquiry_num_id'] = enquiry.id
    request.session['ses_enqiury_id'] = enquiry.id
    request.session['ses_enqiury_num'] = enquiry.en_enquirynumber

    if consignment_number == 'none' or consignment_number == '':
        return redirect(f"{reverse('consignmentdetail_insert')}?enq_id={enquiry.id}")
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
    request.session['enquiry_num_id'] = enquiry_num_id
    request.session['ses_enqiury_id'] = enquiry_num_id
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
    
    enq_id_param = request.GET.get('enq_id')
    if enq_id_param:
        enquiry_num_id = int(enq_id_param)
        request.session['enquiry_num_id'] = enquiry_num_id
        request.session['ses_enqiury_id'] = enquiry_num_id
        try:
            enquiry = EnquirynoteInfo.objects.get(pk=enquiry_num_id)
            request.session['ses_enqiury_num'] = enquiry.en_enquirynumber
            enquiry_num = enquiry.en_enquirynumber
        except ObjectDoesNotExist:
            pass
    else:
        # Prioritize 'enquiry_num_id' over the misspelled session key
        enquiry_num_id = request.session.get('enquiry_num_id') or request.session.get('ses_enqiury_id')

    print("Enquiry Number:", enquiry_num)
    print("Enquiry ID:", enquiry_num_id)

    consignmentgoods_id_val = request.session.get('ses_consignment_id')
    has_invoice_or_ewaybill = ConsignmentgoodsInfo.objects.filter(
        cg_consignmentnumber=consignmentdetail_id
    ).filter(
        Q(cg_consignerinvoice__isnull=False, cg_consignerinvoice__gt='') |
        Q(cg_ebillno__isnull=False, cg_ebillno__gt='')
    ).exists()

    if consignmentdetail_id != 0:
        try:
            enquiry_num_id = ConsignmentdetailInfo.objects.get(id=consignmentdetail_id).co_enquirynumber.id
        except ConsignmentdetailInfo.DoesNotExist:
            pass

    if not enquiry_num_id or enquiry_num_id == 0:
        # Handle error, redirect to enquirynote_list instead of self or placeholder
        messages.error(request, "Enquiry context missing. Please select an enquiry first.")
        return redirect('enquirynote_list')

    customer = EnquirynoteInfo.objects.get(pk=enquiry_num_id).en_customername
    customer_obj = CustomerInfo.objects.filter(cu_name=customer).first()
    customer_id = customer_obj.id
    customer_code = customer_obj.cu_customercode

    if request.method == "GET":
        existing_cancellation_charge = 0.0
        if consignmentdetail_id == 0:
            con_det_form = ConsignmentdetailaddForm(initial={'co_enquirynumber': enquiry_num_id, 'co_customer': customer_id})
            form = ConsignmentgoodsaddForm(initial={'cg_consignmentnumber': 0})
            vehicle_type = ""
        else:
            request.session['ses_consignment_detail_id'] = consignmentdetail_id
            enquiry_num = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id).co_enquirynumber
            consignmentdetail = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id)
            con_det_form = ConsignmentdetailaddForm(instance=consignmentdetail)
            form = ConsignmentgoodsaddForm(initial={'cg_consignmentnumber': consignmentdetail_id})
            vehicle_type = consignmentdetail.co_vehicletype
            
            existing_dummy = TripdetailInfo.objects.filter(tr_consignmentnumber=consignmentdetail).first()
            if existing_dummy and existing_dummy.tc_cancellation:
                existing_cancellation_charge = existing_dummy.tc_cancellation

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
            'existing_cancellation_charge': existing_cancellation_charge,
        }
        return render(request, "asset_mgt_app/consignmentdetail_add.html", context)

    else:
        con_det_form = ConsignmentdetailaddForm(request.POST)

        if con_det_form.is_valid():
            vehicle_type = request.POST.get('vehicle_type_field')
            if consignmentdetail_id == 0:
                consignment_detail = con_det_form.save(commit=False)
                # Determine branch name using centralized utility
                branch_id = get_session_branch_id(request)
                
                # Robust fallback for Consignment: Try to derive branch from Enquiry number prefix
                # (This helps if both session and user profile are ambiguous, which shouldn't happen but is extra safe)
                if branch_id == 1 and consignment_detail.co_enquirynumber and consignment_detail.co_enquirynumber.en_enquirynumber:
                    en_num = consignment_detail.co_enquirynumber.en_enquirynumber
                    if "_MAA_" in en_num: branch_id = 2
                    elif "_BLR_" in en_num: branch_id = 1
                    elif "_HYD_" in en_num: branch_id = 4
                
                branch_code = get_branch_code(branch_id)
                
                # Generate consignment number with financial year and branch name
                # Example format: 26-27_MAA_T_00001
                current_fy = get_financial_year()
                prefix = f"{current_fy}_{branch_code}_T_"
                consignment_detail.co_consignmentnumber = generate_next_number(ConsignmentdetailInfo, 'co_consignmentnumber', prefix, 5)
                
                consignment_detail.co_vehicletype = vehicle_type
                consignment_detail.co_createdby = request.user
                consignment_detail.save()

                # --- NEW LOGIC: Handle Cancellation without Trip ---
                status_id = int(request.POST.get('co_status') or 0)
                if status_id in [9, 10]:
                    cancellation_charge = float(request.POST.get('consignment_cancellation_charge', '0.0'))
                    trip_status_id = 10 if status_id == 9 else 11
                    
                    existing_dummy = TripdetailInfo.objects.filter(tr_consignmentnumber=consignment_detail).first()
                    if not existing_dummy:
                        branch_id = get_session_branch_id(request)
                        branch_code = get_branch_code(branch_id)
                        current_fy = get_financial_year()
                        prefix = f"{current_fy}_{branch_code}_TN_"
                        trip_num_next = generate_next_number(TripdetailInfo, 'tr_tripnumber', prefix, 7)
                        
                        default_ownership = OwnershipInfo.objects.first()
                        default_vehicletype = VehicletypeInfo.objects.first()
                        default_category = Trip_category_info.objects.first()

                        TripdetailInfo.objects.create(
                            tr_enquirynumber=consignment_detail.co_enquirynumber,
                            tr_consignmentnumber=consignment_detail,
                            tr_tripnumber=trip_num_next,
                            tr_vehiclesource=default_ownership,
                            tr_vehicletype=default_vehicletype,
                            tr_vehicletype_placed=default_vehicletype,
                            tr_category=default_category,
                            tc_financestatus_id=trip_status_id,
                            tc_cancellation=cancellation_charge,
                            tc_cancellation_check=(status_id == 9),
                            tr_updated_by=request.user
                        )

                return redirect(f'/SMS/consignmentdetail_update/{consignment_detail.id}')
            else:
                consignmentdetail = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id)
                con_det_form = ConsignmentdetailaddForm(request.POST, instance=consignmentdetail)
                if con_det_form.is_valid():
                    consignment_detail = con_det_form.save(commit=False)
                    consignment_detail.co_vehicletype = vehicle_type
                    consignment_detail.save()

                    # --- NEW LOGIC: Handle Cancellation without Trip ---
                    status_id = int(request.POST.get('co_status') or 0)
                    if status_id in [9, 10]:
                        cancellation_charge = float(request.POST.get('consignment_cancellation_charge', '0.0'))
                        trip_status_id = 10 if status_id == 9 else 11
                        
                        existing_dummy = TripdetailInfo.objects.filter(tr_consignmentnumber=consignment_detail).first()
                        if not existing_dummy:
                            branch_id = get_session_branch_id(request)
                            branch_code = get_branch_code(branch_id)
                            current_fy = get_financial_year()
                            prefix = f"{current_fy}_{branch_code}_TN_"
                            trip_num_next = generate_next_number(TripdetailInfo, 'tr_tripnumber', prefix, 7)
                            
                            default_ownership = OwnershipInfo.objects.first()
                            default_vehicletype = VehicletypeInfo.objects.first()
                            default_category = Trip_category_info.objects.first()

                            TripdetailInfo.objects.create(
                                tr_enquirynumber=consignment_detail.co_enquirynumber,
                                tr_consignmentnumber=consignment_detail,
                                tr_tripnumber=trip_num_next,
                                tr_vehiclesource=default_ownership,
                                tr_vehicletype=default_vehicletype,
                                tr_vehicletype_placed=default_vehicletype,
                                tr_category=default_category,
                                tc_financestatus_id=trip_status_id,
                                tc_cancellation=cancellation_charge,
                                tc_cancellation_check=(status_id == 9),
                                tr_updated_by=request.user
                            )
                        else:
                            # Update existing dummy trip if they changed the charge
                            existing_dummy.tc_cancellation = cancellation_charge
                            existing_dummy.tc_cancellation_check = (status_id == 9)
                            existing_dummy.tc_financestatus_id = trip_status_id
                            existing_dummy.save()

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

    # Dropdowns
    customers = CustomerInfo.objects.filter(cu_name__icontains='(T)').order_by('cu_name')
    employees = User_extInfo.objects.filter(
        emp_organisation_id=2
    ).select_related('user').order_by('user__first_name')

    customer_id = request.GET.get('customer')
    updated_by_id = request.GET.get('updated_by')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    branch = request.GET.get('branch', '')

    context = {
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


@login_required(login_url='login_page')
def consignmentdetail_list_ajax(request):
    """Server-side DataTables AJAX endpoint for Consignment Detail List."""
    from django.db.models import Q, Sum
    from ..models import TransInvoiceInfo

    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 50))
    search_value = request.GET.get('search[value]', '').strip()

    # Filters
    customer_id = request.GET.get('customer')
    updated_by_id = request.GET.get('updated_by')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    branch = request.GET.get('branch', '')

    qs = ConsignmentdetailInfo.objects.select_related(
        'co_enquirynumber', 'co_customer', 'co_status', 'co_lastmodifiedby', 'co_createdby',
        'co_fromlocaion', 'co_tolocation', 'co_enquirynumber__en_fromlocaion',
        'co_enquirynumber__en_tolocation', 'co_enquirynumber__en_movement_type'
    ).prefetch_related('cg_consignmentnumber', 'cg_consignmentnumber__cg_consigner', 'cg_consignmentnumber__cg_consignee').all()

    # Apply Filters
    if customer_id:
        qs = qs.filter(co_customer_id=customer_id)
    if updated_by_id:
        qs = qs.filter(co_lastmodifiedby_id=updated_by_id)
    if date_from:
        qs = qs.filter(co_consignmentdate__gte=date_from)
    if date_to:
        qs = qs.filter(co_consignmentdate__lte=date_to)
    if branch == 'MAA':
        qs = qs.filter(co_consignmentnumber__icontains='MAA')
    elif branch == 'BLR':
        qs = qs.filter(co_consignmentnumber__icontains='BLR')

    records_total = qs.count()

    # Global search
    if search_value:
        qs = qs.filter(
            Q(co_consignmentnumber__icontains=search_value) |
            Q(co_vehicelnumber__icontains=search_value) |
            Q(co_customer__cu_name__icontains=search_value) |
            Q(co_enquirynumber__en_enquirynumber__icontains=search_value) |
            Q(co_status__status_title__icontains=search_value) |
            Q(co_lastmodifiedby__first_name__icontains=search_value) |
            Q(co_lastmodifiedby__last_name__icontains=search_value) |
            Q(co_fromlocaion__place_name__icontains=search_value) |
            Q(co_tolocation__place_name__icontains=search_value) |
            Q(cg_consignmentnumber__cg_consigner__consigner_name__icontains=search_value) |
            Q(cg_consignmentnumber__cg_consignee__consignee_name__icontains=search_value) |
            Q(cg_consignmentnumber__cg_consignerinvoice__icontains=search_value) |
            Q(cg_consignmentnumber__cg_ebillno__icontains=search_value) |
            Q(transinvoiceinfo__ti_inv_no__icontains=search_value)
        ).distinct()

    records_filtered = qs.count()

    # Ordering - Mapping UI columns to DB fields
    order_col = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'desc')
    col_map = {
        0: 'id',
        1: 'co_created_at',
        2: 'co_customer__cu_name',
        3: 'co_enquirynumber__en_enquirynumber',
        4: 'co_consignmentnumber',
        5: 'co_consignmentdate',
        6: 'co_vehicelnumber',
        7: 'co_fromlocaion__place_name',
        8: 'co_tolocation__place_name',
        9: 'cg_consignmentnumber__cg_consigner__consigner_name',
        10: 'cg_consignmentnumber__cg_consignee__consignee_name',
        11: 'cg_consignmentnumber__cg_consignerinvoice',
        12: 'cg_consignmentnumber__cg_consignervalue',
        13: 'cg_consignmentnumber__cg_valueininr',
        14: 'cg_consignmentnumber__cg_qty',
        15: 'cg_consignmentnumber__cg_weight',
        16: 'cg_consignmentnumber__cg_ebillno',
        17: 'cg_consignmentnumber__cg_consignerinvoice_date',
        18: 'cg_consignmentnumber__cg_dateofvalidity',
        19: 'co_containerdescription',
        21: 'co_enquirynumber__en_movement_type__mt_movementtype',
        22: 'co_status__status_title',
        23: 'co_updated_at',
        24: 'co_lastmodifiedby__first_name',
        25: 'co_createdby__first_name',
    }
    order_field = col_map.get(order_col, 'id')
    if order_dir == 'desc':
        order_field = '-' + order_field
    qs = qs.order_by(order_field)

    # Slice for pagination
    if length == -1:
        page_qs = list(qs[start:])
    else:
        page_qs = list(qs[start:start + length])

    # Bulk-fetch invoice info for this page's consignments
    page_cons_ids = [obj.id for obj in page_qs]
    invoice_map = {}  # consignment_id -> (inv_no, ti_total)
    for inv in TransInvoiceInfo.objects.filter(
        ti_consignment_id__in=page_cons_ids
    ).values('ti_consignment_id', 'ti_inv_no', 'ti_total'):
        invoice_map[inv['ti_consignment_id']] = (
            inv['ti_inv_no'] or '',
            inv['ti_total'] or 0,
        )

    data = []
    # Fetch data
    for obj in page_qs:
        related_goods = obj.cg_consignmentnumber.all()
        # For multiple goods, we sum up totals and take the first one for individual fields
        goods = related_goods[0] if related_goods else None
        
        consigner = str(goods.cg_consigner) if (goods and goods.cg_consigner) else ''
        consignee = str(goods.cg_consignee) if (goods and goods.cg_consignee) else ''
        invoice = goods.cg_consignerinvoice if goods else ''
        
        total_qty = 0
        total_weight = 0
        total_value = 0
        total_value_inr = 0
        
        for g in related_goods:
            total_qty += g.cg_qty or 0
            total_weight += g.cg_weight or 0
            total_value += g.cg_consignervalue or 0
            total_value_inr += g.cg_valueininr or 0
        
        ebill = goods.cg_ebillno if goods else ''
        issue_date = goods.cg_consignerinvoice_date.strftime('%Y-%m-%d') if (goods and goods.cg_consignerinvoice_date) else ''
        validity_date = goods.cg_dateofvalidity.strftime('%Y-%m-%d') if (goods and goods.cg_dateofvalidity) else ''
        dimension = f"{goods.cg_length}x{goods.cg_width}x{goods.cg_height}" if goods else ''
        
        display_from = str(obj.co_fromlocaion) if obj.co_fromlocaion else (str(obj.co_enquirynumber.en_fromlocaion) if obj.co_enquirynumber else '')
        display_to = str(obj.co_tolocation) if obj.co_tolocation else (str(obj.co_enquirynumber.en_tolocation) if obj.co_enquirynumber else '')
        movement = str(obj.co_enquirynumber.en_movement_type) if (obj.co_enquirynumber and obj.co_enquirynumber.en_movement_type) else ''

        inv_no, inv_total = invoice_map.get(obj.id, ('', 0))

        data.append([
            obj.id,                                     # 0: ID
            obj.co_created_at.strftime('%Y-%m-%d') if obj.co_created_at else '', # 1: Created On
            str(obj.co_customer) if obj.co_customer else '',  # 2: Customer Name
            str(obj.co_enquirynumber) if obj.co_enquirynumber else '', # 3: Enquiry Number
            obj.co_consignmentnumber or '',             # 4: Consignment Number
            obj.co_consignmentdate.strftime('%Y-%m-%d') if obj.co_consignmentdate else '', # 5: Consignment Date
            obj.co_vehicelnumber or '',                 # 6: Vehicle Number
            display_from,                               # 7: From Location
            display_to,                                 # 8: To Location
            consigner,                                  # 9: Consigner
            consignee,                                  # 10: Consignee
            invoice,                                    # 11: Consigner Invoice
            str(total_value),                           # 12: Value
            str(total_value_inr),                       # 13: Value in INR
            str(total_qty),                             # 14: No. of Pieces
            str(total_weight),                          # 15: Weight
            ebill,                                      # 16: Eway-Bill No.
            issue_date,                                 # 17: Date of Issue
            validity_date,                              # 18: Date of Validity
            obj.co_containerdescription or '',          # 19: Container Description
            dimension,                                  # 20: Dimension
            movement,                                   # 21: Movement
            str(obj.co_status) if obj.co_status else '', # 22: Status
            obj.co_updated_at.strftime('%Y-%m-%d') if obj.co_updated_at else '', # 23: Updated On
            str(obj.co_lastmodifiedby) if obj.co_lastmodifiedby else '', # 24: Updated By
            str(obj.co_createdby) if hasattr(obj, 'co_createdby') and obj.co_createdby else '', # 25: Created By
            inv_no,                                     # 26: Invoice Number
            inv_total,                                  # 27: Invoice Amount
            obj.id,                                     # 28: Edit
            obj.id,                                     # 29: Delete
        ])

    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data,
    })


#Delete consignmentdetail
@login_required(login_url='login_page')
def consignmentdetail_delete(request,consignmentdetail_id):
    print("Inside Delete")
    consignmentdetail = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id)
    enquiry_num = consignmentdetail.co_enquirynumber
    
    reason = request.POST.get('deletion_reason', 'No reason provided')
    identifier = consignmentdetail.co_consignmentnumber
    
    DeletionLog.objects.create(
        dl_model_name='ConsignmentdetailInfo',
        dl_record_id=consignmentdetail_id,
        dl_record_identifier=identifier,
        dl_deleted_by=request.user,
        dl_reason=reason
    )
    
    consignmentdetail.delete()
    try:
        consignmentdetail_list = ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num).values_list('co_consignmentnumber', flat=True)
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num.en_enquirynumber).update(en_consignmentdetails=list(consignmentdetail_list))
    except ObjectDoesNotExist:
        consignmentdetail_list=[]
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num.en_enquirynumber).update(en_consignmentdetails=list(consignmentdetail_list))
    return redirect(request.META.get('HTTP_REFERER', '/SMS/consignmentdetail_list'))

@login_required(login_url='login_page')
@xframe_options_exempt
def consignment_note_pdf(request, consignment_note_id=0):
    try:
        consignment = ConsignmentdetailInfo.objects.get(pk=consignment_note_id)
        consignment_num = consignment.co_consignmentnumber
        vehicle_reg_num = consignment.co_vehicelnumber  # e.g., TN22DF8390
        enquiry_id = consignment.co_enquirynumber_id

        # All related goods
        consignment_goods_list = list(ConsignmentgoodsInfo.objects.filter(
            cg_consignmentnumber=consignment_note_id
        ).order_by('id'))

        # Replace slashes and commas with space suffixes in memory to enable word wrapping in the PDF table
        for goods in consignment_goods_list:
            if goods.cg_consignerinvoice:
                goods.cg_consignerinvoice = goods.cg_consignerinvoice.replace('/', '/ ').replace(',', ', ')
            if goods.cg_hawbno:
                goods.cg_hawbno = goods.cg_hawbno.replace('/', '/ ').replace(',', ', ')
            if goods.cg_ebillno:
                goods.cg_ebillno = goods.cg_ebillno.replace('/', '/ ').replace(',', ', ')

        vehicle_detail = None

        # ----------------------------------------------------
        # 1️⃣ FIRST TRY → MARKET VEHICLE MATCH (string match)
        # ----------------------------------------------------
        vehicle_detail = Vehicle_allotmentInfo.objects.filter(
            va_enquirynumber=enquiry_id,
            va_vehiclenumber_mkt=vehicle_reg_num
        ).last()

        # ----------------------------------------------------
        # 2️⃣ IF NOT MARKET → TRY OWN VEHICLE MATCH (FK)
        # ----------------------------------------------------
        if not vehicle_detail:
            try:
                vehicle_master = VehiclemasterInfo.objects.get(vm_registrationnumber=vehicle_reg_num)
                vehicle_detail = Vehicle_allotmentInfo.objects.filter(
                    va_enquirynumber=enquiry_id,
                    va_vehiclenumber=vehicle_master.id
                ).last()
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

            # ✅ Only use Driver Name, remove ID in brackets
            raw_name = vehicle_detail.va_drivername or ""
            clean_name = raw_name.split('(')[0].strip()
            driver_name.append(clean_name)
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
        Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number, va_status_id__in=[1, 2, 3])
        .select_related('va_vehiclenumber')
        .values_list('va_vehiclenumber__vm_registrationnumber', flat=True)
    )
    requested_vehicles_market = list(
        Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number, va_status_id__in=[1, 2, 3])
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
        allotment = Vehicle_allotmentInfo.objects.filter(va_vehiclenumber=vehicle_master).last()
    except VehiclemasterInfo.DoesNotExist:

        allotment = Vehicle_allotmentInfo.objects.filter(va_vehiclenumber_mkt=vehicle_id).last()

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
