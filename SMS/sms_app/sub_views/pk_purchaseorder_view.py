import json
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from ..forms import POdimensionForm,PkpurchaseorderForm
from ..models import User_extInfo,Nadimension,POdimension,PkneedassessmentInfo,PkpurchaseorderInfo,PkpurchaseorderAttachmentInfo,PkquotationsummaryInfo,PkcostingsummaryInfo, pk_stock_statusinfo, PkquotationInfo, PkcostingInfo, StatusList, StockMaintenance, CustomerInfo
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .pk_needassessment_view import Pkcosting_delete, Pkcostingsummary_delete, Pkpurchaseorder_delete, Pkpurchaseorder_dim_delete, get_tracker_flags
from django.db.models import Sum, Max, Q
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id

@login_required(login_url='login_page')
def purchaseorder_add(request, purchaseorder_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = role.id

    if request.method == "GET":
        if purchaseorder_id == 0:
            # Check if qs_id is passed from "Generate Purchase Order" button
            qs_id = request.GET.get('qs_id')
            initial_data = {}
            na_id = None
            if qs_id:
                try:
                    qs_obj = PkquotationsummaryInfo.objects.get(pk=qs_id)
                    na_id = qs_obj.qs_assessment_num_id
                    initial_data['po_assessment_num'] = na_id
                    initial_data['po_quotation_num'] = qs_obj.id
                    initial_data['po_customer_name'] = qs_obj.qs_customer_name_2_id
                    initial_data['po_customer_new_name'] = qs_obj.pkqt_customer_new_name or ''
                except PkquotationsummaryInfo.DoesNotExist:
                    pass
            form = PkpurchaseorderForm(initial=initial_data, na_id=na_id)
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'role': role,
                'role_id': role_id,
                'current_step': 'po',
            }
        else:
            purchaseorder = PkpurchaseorderInfo.objects.get(pk=purchaseorder_id)
            form = PkpurchaseorderForm(instance=purchaseorder)
            po_dimension_list = POdimension.objects.filter(pod_po_num=purchaseorder_id)
            
            # Calculate remaining qty for each dimension item
            for pod in po_dimension_list:
                jobbed_data = PkcostingInfo.objects.filter(
                    ct_po_dimension=pod,
                    ct_job_no__isnull=False
                ).exclude(ct_job_no='').values('ct_job_no').annotate(
                    job_qty=Max('ct_quantity_req')
                ).aggregate(total=Sum('job_qty'))
                
                already_jobbed_qty = jobbed_data['total'] or 0
                pod.remaining_qty = max(0, float(pod.pod_quantity) - float(already_jobbed_qty))

            # Safely get assessment num ID (handle None case)
            na_id = purchaseorder.po_assessment_num.id if purchaseorder.po_assessment_num else None
            
            # Set session variables for dimension insert/update
            request.session['ses_na_id'] = na_id
            request.session['purchaseorder_id'] = purchaseorder.id
            
            # Fetch linked costing summaries for the hub
            linked_costings = PkcostingsummaryInfo.objects.filter(cs_customer_po=purchaseorder_id)
            po_attachments = PkpurchaseorderAttachmentInfo.objects.filter(po=purchaseorder).order_by('-uploaded_at')
            
            context = {
                'form': form,
                'purchaseorder_id': purchaseorder_id,
                'first_name': first_name,
                'user_id': user_id,
                'na_id': na_id,
                'po_dimension_list': po_dimension_list,
                'role': role,
                'role_id': role_id,
                'linked_costings': linked_costings,
                'po_attachments': po_attachments,
                'current_step': 'po',
                'tracker_flags': get_tracker_flags(na_id),
            }
        return render(request, "asset_mgt_app/pk_purchaseorder_add.html", context)

    else:
        if purchaseorder_id == 0:
            # Add mode
            post_na_id = request.POST.get('po_assessment_num')
            form = PkpurchaseorderForm(request.POST, request.FILES, na_id=post_na_id)
            if form.is_valid():
                customer_po_num = form.cleaned_data['po_num']

                if not PkpurchaseorderInfo.objects.filter(po_num=customer_po_num).exists():
                    instance = form.save(commit=False)

                    # Set updated_by from session (excluded from form)
                    instance.po_updated_by_id = user_id

                    # Generate Sales Order number based on financial year (Branch specific)
                    fy = get_financial_year()
                    branch_id = get_session_branch_id(request)
                    branch_code = get_branch_code(branch_id)
                    prefix = f"{fy}_{branch_code}_PO_"
                    instance.sales_order_num = generate_next_number(PkpurchaseorderInfo, 'sales_order_num', prefix, 6)
                    instance.save()
                    
                    # Process multiple attachments
                    for f in request.FILES.getlist('po_attach_files'):
                        PkpurchaseorderAttachmentInfo.objects.create(
                            po=instance,
                            file=f,
                            filename=f.name
                        )
                    
                    # Set session variables for dimension insert/update after add
                    request.session['ses_na_id'] = instance.po_assessment_num.id if instance.po_assessment_num else None
                    request.session['purchaseorder_id'] = instance.id
                    
                    messages.success(request, 'Purchase Order Added Successfully')
                else:
                    messages.error(request, 'Please enter a Unique PO Number.')
            else:
                print("FORM ERRORS:", form.errors.as_json())
                messages.error(request, 'Please check your inputs.')

        else:
            # Edit mode
            purchaseorder = PkpurchaseorderInfo.objects.get(pk=purchaseorder_id)
            post_na_id = request.POST.get('po_assessment_num')
            form = PkpurchaseorderForm(request.POST, request.FILES, instance=purchaseorder, na_id=post_na_id)
            if form.is_valid():
                instance = form.save(commit=False)
                # Set updated_by from session (excluded from form)
                instance.po_updated_by_id = user_id
                # Do NOT regenerate sales_order_num when editing
                instance.sales_order_num = purchaseorder.sales_order_num
                instance.save()
                
                # Process multiple attachments
                for f in request.FILES.getlist('po_attach_files'):
                    PkpurchaseorderAttachmentInfo.objects.create(
                        po=instance,
                        file=f,
                        filename=f.name
                    )
                
                # Set session variables for dimension insert/update after edit
                request.session['ses_na_id'] = instance.po_assessment_num.id if instance.po_assessment_num else None
                request.session['purchaseorder_id'] = instance.id
                
                messages.success(request, 'Purchase Order Updated Successfully')
            else:
                print("FORM ERRORS:", form.errors.as_json())
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
                messages.error(request, "Update Failed")

        # Redirect to the last purchase order or current edited one
        last_id = purchaseorder_id if purchaseorder_id else PkpurchaseorderInfo.objects.order_by('-id').values_list('id', flat=True).first()
        return redirect('/SMS/purchaseorder_update/' + str(last_id))


@login_required(login_url='login_page')
def delete_po_attachment(request, att_id):
    if request.method == 'POST':
        try:
            att = PkpurchaseorderAttachmentInfo.objects.get(id=att_id)
            att.file.delete(save=False)
            att.delete()
            return JsonResponse({'status': 'success'})
        except PkpurchaseorderAttachmentInfo.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Attachment not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


# List purchaseorder
@login_required(login_url='login_page')
def purchaseorder_list(request):
    first_name = request.session.get('first_name')
    po_list = PkpurchaseorderInfo.objects.all().select_related('po_customer_name', 'po_status', 'po_updated_by').order_by('-id')

    # Collect distinct customers with orders
    order_customers = set()
    for po in po_list:
        cname = str(po.po_customer_name) if po.po_customer_name else (po.po_customer_new_name or '')
        if cname and cname.strip() and cname.strip() != '-':
            order_customers.add(cname.strip())
    order_customers = sorted(list(order_customers), key=lambda s: s.lower())

    # Collect other master customers
    all_master = CustomerInfo.objects.values_list('cu_name', flat=True).distinct()
    other_customers = sorted([c.strip() for c in all_master if c and c.strip() and c.strip() not in order_customers], key=lambda s: s.lower())

    selected_customer = request.GET.get('customer', '').strip()

    context = {
        'purchaseorder_list': po_list,
        'order_customers': order_customers,
        'other_customers': other_customers,
        'selected_customer': selected_customer,
        'first_name': first_name
    }
    return render(request, "asset_mgt_app/pk_purchaseorder_list.html", context)

#Delete purchaseorder
@login_required(login_url='login_page')
def purchaseorder_delete(request,purchaseorder_id):
    purchaseorder = PkpurchaseorderInfo.objects.get(pk=purchaseorder_id)
    assessment_num = purchaseorder.po_assessment_num

    # Deleting PkcostingInfo objects
    Pkcosting_delete(assessment_num)

    # Deleting Pkcosting summary objects
    Pkcostingsummary_delete(assessment_num)

    # Deleting Pkpurchaseorders objects
    Pkpurchaseorder_delete(assessment_num)

    # Deleting Pkpurchaseorders dims objects
    Pkpurchaseorder_dim_delete(assessment_num)

    return redirect('/SMS/purchaseorder_list')


@login_required(login_url='login_page')
def pk_get_customer(request):
    assessment_id = request.GET.get('assessment_num')  # Get the assessment ID from the request

    # Fetch the assessment record (returns None if not found)
    need_assessment = PkneedassessmentInfo.objects.filter(pk=assessment_id).first()

    if not need_assessment:
        # Return error if the assessment ID is invalid
        return JsonResponse({'error': 'Assessment not found'}, status=404)

    # Safely retrieve customer-related details
    customer_id = need_assessment.na_customer_name.id if need_assessment.na_customer_name else None
    customer_name = need_assessment.na_customer_name.cu_name if need_assessment.na_customer_name else None
    customer_new_name = need_assessment.na_customer_new_name if need_assessment.na_customer_new_name else None

    # Fetch the Quotation Number (returns None if not found)
    quotation_num = PkquotationsummaryInfo.objects.filter(
        qs_assessment_num=assessment_id, qs_status=5
    ).first()
    quotation_num_id = quotation_num.id if quotation_num else ""

    # Prepare the JSON response data
    data = {
        'customer_name': customer_name,
        'customer_new_name': customer_new_name,
        'customer_id': customer_id,
        'quotation_num_id': quotation_num_id,
    }

    # Update session with the selected assessment ID so dimension form gets it
    request.session['ses_na_id'] = assessment_id

    return JsonResponse(data)


@login_required(login_url='login_page')
def po_dimension_cancel(request,needassessment_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    purchaseorder_id=request.session.get('purchaseorder_id')
    return redirect('/SMS/purchaseorder_update/' + str(purchaseorder_id))
@login_required(login_url='login_page')
def po_dimension_add(request, po_dimension_id=0):
    global na_assessment_num_id
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    purchaseorder_id=request.session.get('purchaseorder_id')
    po = get_object_or_404(PkpurchaseorderInfo, id=purchaseorder_id)

    if request.method == "GET":
        if po_dimension_id == 0:
            form = POdimensionForm(initial={'pod_po_num': purchaseorder_id})
            form.fields['pod_assess_num'].queryset = PkneedassessmentInfo.objects.filter(na_customer_name=po.po_customer_name)
            na_assessment_num_id = request.session.get('ses_na_id')
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'purchaseorder_id': purchaseorder_id,
                'po': po,
                'na_assessment_num_id': na_assessment_num_id,
            }
        else:
            po_dimensioninfo = POdimension.objects.get(pk=po_dimension_id)
            form = POdimensionForm(instance=po_dimensioninfo)
            form.fields['pod_assess_num'].queryset = PkneedassessmentInfo.objects.filter(na_customer_name=po.po_customer_name)
            context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
            }
        return render(request, "asset_mgt_app/po_dimension_add.html", context)
    else:
        if po_dimension_id == 0:
            form = POdimensionForm(request.POST)
        else:
            dimension = get_object_or_404(POdimension, pk=po_dimension_id)
            form = POdimensionForm(request.POST, instance=dimension)
        
        form.fields['pod_assess_num'].queryset = PkneedassessmentInfo.objects.filter(na_customer_name=po.po_customer_name)

        # Check if form is valid
        if form.is_valid():
            dimension = form.save(commit=False)
            # Force link to the current PO from session
            dimension.pod_po_num = po
            
            # Set the updated_by field from session directly on server-side
            from ..models import MyUser
            try:
                dimension.pod_updated_by = MyUser.objects.get(id=user_id)
            except:
                pass
                
            dimension.save()
            
            if po_dimension_id == 0:
                messages.success(request, 'Dimension Saved Successfully')
            else:
                messages.success(request, 'Dimension Updated Successfully')
            
            # Redirect back to the Purchase Order update page
            return redirect('/SMS/purchaseorder_update/' + str(purchaseorder_id))
        else:
            # Debug errors and show to the user
            messages.error(request, 'Error: Please correct the errors below.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

        # Redefine context for rendering in case of validation errors
        context = {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'purchaseorder_id': purchaseorder_id,
            'po': po,
            'na_assessment_num_id': request.session.get('ses_na_id'),
        }
        return render(request, "asset_mgt_app/po_dimension_add.html", context)
@login_required(login_url='login_page')
def po_dimension_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    po_dimension_list=POdimension.objects.all()
    context = {
        'user_id': user_id,
        'first_name': first_name,
        'po_dimension_list': po_dimension_list,
    }
    return render(request, "asset_mgt_app/po_dimension_list.html", context)
@login_required(login_url='login_page')
def po_dimension_delete(request, po_dimension_id):
    po_dimensioninfo = POdimension.objects.get(pk=po_dimension_id)
    po_dimensioninfo.delete()
    return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/sales_list')
@login_required(login_url='login_page')
def pk_get_po_requirement_type(request):
    requirement_type_val = []
    ct_assessment_num_id = request.GET.get('ct_assessment_num')
    print('Assessment Number received:', ct_assessment_num_id)  # Debug log

    # Query Nadimension and ensure it fetches correct data
    na_dimension_id = Nadimension.objects.filter(nad_assess_num=ct_assessment_num_id)
    if na_dimension_id.exists():
        for a in na_dimension_id:
            requirement_type_val.append(str(a.nad_item))  # Collect nad_item values
    else:
        print('No records found for assessment number:', ct_assessment_num_id)

    # Return JSON response
    data = {
        'requirement_type_val': requirement_type_val,
    }
    print('Response data:', data)  # Log response data for debugging
    return JsonResponse(data)




@login_required(login_url='login_page')
def pk_create_batch_job(request):
    """
    Creates a new production job (Costing Summary) based on specific quantities
    manually entered for items in a PO.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'GET not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        po_id = data.get('po_id')
        items = data.get('items', [])
        pack_type = data.get('pack_type', 'In-House')

        if not po_id or not items:
            return JsonResponse({'success': False, 'message': 'Missing PO ID or items'}, status=400)

        po = get_object_or_404(PkpurchaseorderInfo, id=po_id)


        # Validate live stock availability for material part codes (Cost Type 8)
        po_dimension_ids = [it['id'] for it in items]
        selected_pods = POdimension.objects.filter(id__in=po_dimension_ids)
        insufficient_stock_items = []
        item_qty_map = {it['id']: float(it['qty']) for it in items}
        
        for pod in selected_pods:
            job_qty = item_qty_map.get(pod.id, 0.0)
            materials = PkquotationInfo.objects.filter(
                pkqt_requirement=pod.pod_nad,
                pkqt_cost_type_id=8
            ).select_related('pkqt_part_code', 'pkqt_stock_description')
            
            for q in materials:
                if not q.pkqt_part_code:
                    continue
                part_code_obj = q.pkqt_part_code
                part_code_str = part_code_obj.pc_code
                # Required count = per_item_req * job_qty
                per_item_req = float(q.pkqt_quantity_req) if q.pkqt_quantity_req is not None else (float(q.pkqt_quantity) if q.pkqt_quantity is not None else 1.0)
                if per_item_req <= 0:
                    continue
                total_needed = per_item_req * job_qty
                
                # Optimised: calculate available stock in 3 bulk queries instead of 3 per batch
                # 1. Total purchased (type=1)
                purchased_total = StockMaintenance.objects.filter(
                    sm_partcode=part_code_obj,
                    sm_stock_type_id=1
                ).aggregate(total=Sum('sm_count'))['total'] or 0.0
                
                # 2. Total retrieved/consumed (type=2) - linked back to type=1 via invoice no
                purchased_invoice_nos = list(StockMaintenance.objects.filter(
                    sm_partcode=part_code_obj,
                    sm_stock_type_id=1
                ).values_list('sm_invoice_no', flat=True))
                
                retrieved_total = StockMaintenance.objects.filter(
                    sm_partcode=part_code_obj,
                    sm_stock_type_id=2,
                    sm_invoice_no__in=purchased_invoice_nos
                ).aggregate(total=Sum('sm_count'))['total'] or 0.0
                
                # 3. Total vendor-returned (type=3)
                vendor_returned_total = StockMaintenance.objects.filter(
                    sm_partcode=part_code_obj,
                    sm_stock_type_id=3
                ).aggregate(total=Sum('sm_count'))['total'] or 0.0
                
                avail_qty = max(0.0, float(purchased_total) - abs(float(retrieved_total)) - abs(float(vendor_returned_total)))
                
                if avail_qty < total_needed:
                    insufficient_stock_items.append({
                        'quotation_id': q.id,
                        'pod_id': pod.id,
                        'item_name': pod.pod_item,
                        'part_code_id': part_code_obj.id,
                        'part_code': part_code_str,
                        'description': q.pkqt_stock_description.stock_description if q.pkqt_stock_description else '',
                        'needed_qty': round(total_needed, 2),
                        'per_unit_req': round(per_item_req, 2),
                        'job_qty': round(job_qty, 2),
                        'available_qty': round(avail_qty, 2),
                        'shortfall': round(total_needed - avail_qty, 2)
                    })

        # If user did not pass override flag, warn user and offer Partcode change option
        allow_stock_override = data.get('allow_stock_override', False)
        if insufficient_stock_items and not allow_stock_override:
            # Trigger email notification to Stock Team
            try:
                from .send_department_email import send_department_email
                subject = f"STOCK SHORTFALL ALERT - Sales Order #{po.po_num or po.id}"
                body = f"<h3>Stock Shortfall Alert for Sales Order #{po.po_num or po.id}</h3>"
                body += f"<p>Customer: <b>{po.po_customer_name or po.po_customer_new_name}</b></p>"
                body += "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse:collapse;'>"
                body += "tr style='background:#f2f2f2;'><th>Item</th><th>Part Code</th><th>Description</th><th>Needed Qty</th><th>Avail Qty</th><th>Shortfall</th></tr>"
                for item in insufficient_stock_items:
                    body += f"<tr><td>{item['item_name']}</td><td><b>{item['part_code']}</b></td><td>{item['description']}</td><td>{item['needed_qty']}</td><td style='color:red;'>{item['available_qty']}</td><td style='color:red;'><b>-{item['shortfall']}</b></td></tr>"
                body += "</table>"
                body += "<p>Please restock or advise alternative materials.</p>"
                
                # Send email - use recipient from request if provided, else fall back to settings
                extra_recipient = data.get('stock_alert_email', '').strip()
                if extra_recipient:
                    send_department_email('itadmin', subject, body, [extra_recipient], email_type=1)
            except Exception as mail_err:
                print(f"Stock Team notification email error: {mail_err}")

            return JsonResponse({
                'success': False,
                'stock_alert': True,
                'insufficient_stock_items': insufficient_stock_items,
                'message': 'Stock shortfall detected for one or more partcodes.'
            }, status=400)
        
        # 1. Generate unique Job Number (e.g., 24-25_BLR_JOB-0001)
        fy = get_financial_year()
        branch_id = get_session_branch_id(request)
        branch_code = get_branch_code(branch_id)
        prefix = f"{fy}_{branch_code}_JOB_"
        job_no = generate_next_number(PkcostingsummaryInfo, 'cs_job_no', prefix, 4)

        # 2. Get WIP Status (id=6)
        try:
            wip_status = StatusList.objects.get(id=6)
        except StatusList.DoesNotExist:
            wip_status = None

        # 3. Create the Costing Summary (The Job)
        # Using the PO's assessment as the primary one for the summary
        first_pod = POdimension.objects.get(id=items[0]['id'])
        summary = PkcostingsummaryInfo.objects.create(
            cs_customer_po=po,
            cs_assessment_num=po.po_assessment_num if po.po_assessment_num else first_pod.pod_assess_num,
            cs_customer_name=po.po_customer_name,
            cs_customer_new_name=po.po_customer_new_name,
            cs_status=wip_status,
            cs_job_no=job_no,
            cs_pack_type=pack_type,
            cs_updated_by_id=request.session.get('ses_userID')
        )

        # 4. Get stock status (id=1)
        try:
            stock_status_instance = pk_stock_statusinfo.objects.get(id=1)
        except pk_stock_statusinfo.DoesNotExist:
            stock_status_instance = None

        cloned_count = 0
        job_substitutions = data.get('substitutions', {})
        all_absorbed_ids = set()
        sub_map = {}
        if isinstance(job_substitutions, list):
            for s in job_substitutions:
                qid_k = str(s.get('quotation_id'))
                sub_map[qid_k] = s
                for a_id in s.get('absorbed_quotation_ids', []):
                    all_absorbed_ids.add(str(a_id))
        elif isinstance(job_substitutions, dict):
            for qid_k, s in job_substitutions.items():
                sub_map[str(qid_k)] = s
                for a_id in s.get('absorbed_quotation_ids', []):
                    all_absorbed_ids.add(str(a_id))

        for entry in items:
            pod_id = entry['id']
            job_qty = float(entry['qty'])
            
            pod = POdimension.objects.get(id=pod_id)
            
            # Backend Safety Check: Ensure we don't over-produce
            # Correctly identify already jobbed qty by summing unique job releases
            jobbed_data = PkcostingInfo.objects.filter(
                ct_po_dimension=pod,
                ct_job_no__isnull=False
            ).exclude(ct_job_no='').values('ct_job_no').annotate(
                job_qty=Max('ct_na_quantity')
            ).aggregate(total=Sum('job_qty'))
            
            already_jobbed_qty = jobbed_data['total'] or 0
            
            if (float(already_jobbed_qty) + job_qty) > (float(pod.pod_quantity) + 0.001): # Allow small float margin
                return JsonResponse({
                    'success': False, 
                    'message': f'Over-production for {pod.pod_item}. Remaining: {pod.pod_quantity - already_jobbed_qty}'
                }, status=400)
            
            # Find matching quotations for this item's specific requirements (Nadimension)
            quotations = PkquotationInfo.objects.filter(pkqt_requirement=pod.pod_nad)
            
            for q in quotations:
                str_qid = str(q.id)
                # If absorbed for this specific job, skip creating costing entry
                if str_qid in all_absorbed_ids:
                    continue

                per_req = float(q.pkqt_quantity_req) if q.pkqt_quantity_req is not None else (float(q.pkqt_quantity) if q.pkqt_quantity is not None else 0.0)
                if q.pkqt_cost_type_id == 8 and per_req <= 0 and str_qid not in sub_map:
                    continue  # Absorbed / not used in production

                # Check if this quotation has a job-specific substitution
                sub = sub_map.get(str_qid)
                part_code_obj = q.pkqt_part_code
                stock_desc_obj = q.pkqt_stock_description
                stock_type_obj = q.pkqt_stock_type
                uom_obj = q.pkqt_uom
                qty_req_val = float(q.pkqt_quantity_req or 0.0)
                rate_val = float(q.pkqt_rate or 0.0)
                total_cost_val = float(q.pkqt_total_cost or 0.0)
                width_val = q.pkqt_width_req
                height_val = q.pkqt_height_req
                length_val = q.pkqt_length_req

                if sub:
                    new_pc_id = sub.get('new_part_code_id')
                    if new_pc_id:
                        from sms_app.models import PkpartcodeInfo
                        pc_str = str(new_pc_id).strip()
                        try:
                            part_code_obj = PkpartcodeInfo.objects.get(pc_code=pc_str)
                        except PkpartcodeInfo.DoesNotExist:
                            if pc_str.isdigit():
                                part_code_obj = PkpartcodeInfo.objects.get(id=int(pc_str))
                        if part_code_obj:
                            if part_code_obj.pc_stock_description:
                                stock_desc_obj = part_code_obj.pc_stock_description
                            if part_code_obj.pc_stock_type:
                                stock_type_obj = part_code_obj.pc_stock_type
                            if part_code_obj.pc_uom:
                                uom_obj = part_code_obj.pc_uom
                    if sub.get('new_qty_req') is not None:
                        try:
                            qty_req_val = float(sub['new_qty_req'])
                        except (ValueError, TypeError):
                            pass
                    if sub.get('rate') is not None:
                        try:
                            rate_val = float(sub['rate'])
                        except (ValueError, TypeError):
                            pass
                    if sub.get('total_cost') is not None:
                        try:
                            total_cost_val = float(sub['total_cost'])
                        except (ValueError, TypeError):
                            pass
                    if sub.get('dim_l') is not None:
                        try:
                            length_val = float(sub['dim_l'])
                        except (ValueError, TypeError):
                            pass
                    if sub.get('dim_w') is not None:
                        try:
                            width_val = float(sub['dim_w'])
                        except (ValueError, TypeError):
                            pass
                    if sub.get('dim_h') is not None:
                        try:
                            height_val = float(sub['dim_h'])
                        except (ValueError, TypeError):
                            pass

                # Calculate ratio to scale total values based on the PO Job Quantity vs original Need Assessment Quantity
                old_qty = float(q.pkqt_na_quantity or 1)
                if old_qty == 0:
                    old_qty = 1
                ratio = job_qty / old_qty

                # Calculate batch quantity and total cost for this job
                calculated_qty = round(qty_req_val * job_qty) if sub else round(float(q.pkqt_quantity or 0) * ratio)
                calculated_box_cost = round(total_cost_val * job_qty, 2) if sub else round(float(q.pkqt_total_cost or 0) * job_qty, 2)

                PkcostingInfo.objects.create(
                    ct_cost_type=q.pkqt_cost_type,
                    ct_stock_description=stock_desc_obj,
                    ct_width=q.pkqt_width,
                    ct_height=q.pkqt_height,
                    ct_cft=q.pkqt_cft,
                    ct_rate=rate_val,
                    ct_days=q.pkqt_days,
                    ct_total_cost=total_cost_val,
                    ct_quantity=calculated_qty,
                    ct_size=q.pkqt_size,
                    ct_uom=uom_obj,
                    ct_assessment_num=q.pkqt_assessment_num,
                    ct_length=q.pkqt_length,
                    ct_stock_type=stock_type_obj,
                    ct_stock_purchase_number=q.pkqt_stock_purchase_number,
                    ct_item=q.pkqt_item,
                    ct_itemdescription=q.pkqt_itemdescription,
                    ct_requirement=q.pkqt_requirement,
                    ct_requirement_size=q.pkqt_requirement_size,
                    ct_width_req=width_val,
                    ct_height_req=height_val,
                    ct_length_req=length_val,
                    ct_quantity_req=qty_req_val,  # Retain per-unit requirement
                    ct_sqrt_req=round(float(q.pkqt_sqrt_req or 0) * ratio, 2),
                    ct_stock_status=stock_status_instance,
                    ct_customer_name=q.pkqt_customer_name,
                    ct_customer_new_name=q.pkqt_customer_new_name2,
                    ct_customer_po=po,
                    ct_updated_by=request.user,
                    ct_na_quantity=job_qty,  # The actual PO Job quantity
                    ct_totalbox_cost=calculated_box_cost,
                    ct_part_code=part_code_obj,
                    ct_total_cft_display=round(float(q.pkqt_total_cft_display or 0) * ratio, 2),
                    ct_po_dimension=pod,
                    ct_job_no=job_no  # Tag with unique job number
                )
                cloned_count += 1

        return JsonResponse({
            'success': True, 
            'redirect_url': f'/SMS/costingsummary_update/{summary.id}'
        })

    except Exception as e:
        print(f"Error in pk_create_batch_job: {str(e)}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required(login_url='login_page')
def pk_get_po_items_for_job(request):
    try:
        po_id = request.GET.get('po_id')
        if not po_id:
            return JsonResponse({'success': False, 'message': 'PO ID is required.'}, status=400)
        
        # Fetch all dimension items for this PO
        po_items = POdimension.objects.filter(pod_po_num_id=po_id)
        
        items_data = []
        for item in po_items:
            # Calculate already jobbed quantity by summing unique job releases
            jobbed_data = PkcostingInfo.objects.filter(
                ct_po_dimension=item,
                ct_job_no__isnull=False
            ).exclude(ct_job_no='').values('ct_job_no').annotate(
                job_qty=Max('ct_na_quantity')
            ).aggregate(total=Sum('job_qty'))
            
            already_jobbed_qty = jobbed_data['total'] or 0
            
            # Safely handle None or unexpected types for pod_quantity
            pod_qty = float(item.pod_quantity) if item.pod_quantity is not None else 0.0
            remaining_qty = max(0, pod_qty - float(already_jobbed_qty))
            
            items_data.append({
                'id': item.id,
                'item_name': item.pod_item,
                'ordered_qty': pod_qty,
                'already_jobbed_qty': float(already_jobbed_qty),
                'remaining_qty': float(remaining_qty),
            })
        
        return JsonResponse({'success': True, 'items': items_data})
    except Exception as e:
        import traceback
        error_msg = str(e) + "\n" + traceback.format_exc()
        return JsonResponse({'success': False, 'message': error_msg}, status=500)

@login_required(login_url='login_page')
def pk_update_quotation_partcode(request):
    """
    Updates the partcode and quantities on a PkquotationInfo record when user selects an alternative partcode.
    Supports setting new Qty Req (per unit) and new Batch Qty.
    Supports absorbing other partcodes into this one (e.g. when one bigger piece is used for multiple parts).
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        quotation_id = data.get('quotation_id')
        new_part_code_id = data.get('new_part_code_id')
        new_qty_req = data.get('new_qty_req')
        new_batch_qty = data.get('new_batch_qty')
        absorbed_quotation_ids = data.get('absorbed_quotation_ids', [])
        
        if not quotation_id or not new_part_code_id:
            return JsonResponse({'success': False, 'message': 'Missing quotation ID or new part code ID'}, status=400)
            
        quotation = PkquotationInfo.objects.get(id=quotation_id)
        from sms_app.models import PkpartcodeInfo
        pc_str = str(new_part_code_id).strip()
        try:
            new_pc = PkpartcodeInfo.objects.get(pc_code=pc_str)
        except PkpartcodeInfo.DoesNotExist:
            if pc_str.isdigit():
                new_pc = PkpartcodeInfo.objects.get(id=int(pc_str))
            else:
                raise

        update_master = data.get('update_master', False)
        if not update_master:
            msg = f'Part code substituted with {new_pc.pc_code} (Qty Req: {new_qty_req}) for this Job only.'
            if absorbed_quotation_ids:
                msg += f' {len(absorbed_quotation_ids)} other partcode(s) absorbed for this Job only.'
            return JsonResponse({'success': True, 'message': msg, 'is_job_scoped': True})
        
        quotation.pkqt_part_code = new_pc
        update_fields = ['pkqt_part_code']
        if new_pc.pc_stock_description:
            quotation.pkqt_stock_description = new_pc.pc_stock_description
            update_fields.append('pkqt_stock_description')
        if new_pc.pc_stock_type:
            quotation.pkqt_stock_type = new_pc.pc_stock_type
            update_fields.append('pkqt_stock_type')
        if new_pc.pc_uom:
            quotation.pkqt_uom = new_pc.pc_uom
            update_fields.append('pkqt_uom')

        if new_qty_req is not None:
            try:
                quotation.pkqt_quantity_req = float(new_qty_req)
                update_fields.append('pkqt_quantity_req')
            except (ValueError, TypeError):
                pass

        if new_batch_qty is not None:
            try:
                quotation.pkqt_quantity = float(new_batch_qty)
                update_fields.append('pkqt_quantity')
            except (ValueError, TypeError):
                pass
        elif new_qty_req is not None and quotation.pkqt_na_quantity:
            quotation.pkqt_quantity = float(new_qty_req) * float(quotation.pkqt_na_quantity)
            update_fields.append('pkqt_quantity')

        for dim_field, req_key in [('pkqt_length_req', 'dim_l'), ('pkqt_width_req', 'dim_w'), ('pkqt_height_req', 'dim_h')]:
            if req_key in data and data[req_key] is not None:
                try:
                    setattr(quotation, dim_field, float(data[req_key]))
                    update_fields.append(dim_field)
                except (ValueError, TypeError):
                    pass

        if 'rate' in data and data['rate'] is not None:
            try:
                quotation.pkqt_rate = float(data['rate'])
                update_fields.append('pkqt_rate')
            except (ValueError, TypeError):
                pass

        if 'total_cost' in data and data['total_cost'] is not None:
            try:
                quotation.pkqt_total_cost = float(data['total_cost'])
                update_fields.append('pkqt_total_cost')
            except (ValueError, TypeError):
                pass

        quotation.save(update_fields=list(set(update_fields)))

        # Handle absorbed quotation records (one partcode for multiple partcodes)
        absorbed_count = 0
        if absorbed_quotation_ids and isinstance(absorbed_quotation_ids, list):
            for abs_id in absorbed_quotation_ids:
                try:
                    if int(abs_id) == int(quotation_id):
                        continue
                    abs_q = PkquotationInfo.objects.get(id=int(abs_id))
                    abs_q.pkqt_quantity_req = 0.0
                    abs_q.pkqt_quantity = 0.0
                    abs_q.pkqt_total_cost = 0.0
                    abs_q.pkqt_totalbox_cost = 0.0
                    abs_q.save(update_fields=['pkqt_quantity_req', 'pkqt_quantity', 'pkqt_total_cost', 'pkqt_totalbox_cost'])
                    absorbed_count += 1
                except Exception as abs_err:
                    print(f"Error zeroing absorbed quotation {abs_id}: {abs_err}")

        msg = f'Part code updated to {new_pc.pc_code} (Qty Req: {quotation.pkqt_quantity_req})'
        if absorbed_count > 0:
            msg += f', and {absorbed_count} other partcode(s) set to 0 (absorbed into this piece).'

        return JsonResponse({'success': True, 'message': msg})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
