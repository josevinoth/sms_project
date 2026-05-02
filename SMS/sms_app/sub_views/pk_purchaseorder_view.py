import json
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from ..forms import POdimensionForm,PkpurchaseorderForm
from ..models import User_extInfo,Nadimension,POdimension,PkneedassessmentInfo,PkpurchaseorderInfo,PkquotationsummaryInfo,PkcostingsummaryInfo, pk_stock_statusinfo, PkquotationInfo, PkcostingInfo, StatusList
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..views import Pkcosting_delete,Pkcostingsummary_delete,Pkpurchaseorder_delete,Pkpurchaseorder_dim_delete,get_tracker_flags
from django.db.models import Sum, Max
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
            
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'na_id': na_id,
                'po_dimension_list': po_dimension_list,
                'role': role,
                'role_id': role_id,
                'linked_costings': linked_costings,
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


# List purchaseorder
@login_required(login_url='login_page')
def purchaseorder_list(request):
    first_name = request.session.get('first_name')
    context = {'purchaseorder_list' : PkpurchaseorderInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_purchaseorder_list.html",context)

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
            form = POdimensionForm()
            form.fields['pod_assess_num'].queryset = PkneedassessmentInfo.objects.filter(na_customer_name=po.po_customer_name)
            na_assessment_num_id = request.session.get('ses_na_id')
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'purchaseorder_id': purchaseorder_id,
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
            form.save()
            if po_dimension_id == 0:
                messages.success(request, 'Record Saved Successfully')
            else:
                messages.success(request, 'Record Updated Successfully')
        else:
            # Debug errors and show to the user
            messages.error(request, 'Error: Please correct the errors below.')
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")
                    messages.error(request, f"Error in {field}: {error}")

            # Redirect back to the previous page
        return redirect(request.META.get('HTTP_REFERER', '/'))
        # return redirect('/SMS/needassessment_list')
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
                job_qty=Max('ct_quantity_req')
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
                PkcostingInfo.objects.create(
                    ct_cost_type=q.pkqt_cost_type,
                    ct_stock_description=q.pkqt_stock_description,
                    ct_width=q.pkqt_width,
                    ct_height=q.pkqt_height,
                    ct_cft=q.pkqt_cft,
                    ct_rate=q.pkqt_rate,
                    ct_days=q.pkqt_days,
                    ct_total_cost=q.pkqt_total_cost,
                    ct_quantity=q.pkqt_quantity,
                    ct_size=q.pkqt_size,
                    ct_uom=q.pkqt_uom,
                    ct_assessment_num=q.pkqt_assessment_num,
                    ct_length=q.pkqt_length,
                    ct_stock_type=q.pkqt_stock_type,
                    ct_stock_purchase_number=q.pkqt_stock_purchase_number,
                    ct_item=q.pkqt_item,
                    ct_itemdescription=q.pkqt_itemdescription,
                    ct_requirement=q.pkqt_requirement,
                    ct_requirement_size=q.pkqt_requirement_size,
                    ct_width_req=q.pkqt_width_req,
                    ct_height_req=q.pkqt_height_req,
                    ct_length_req=q.pkqt_length_req,
                    ct_quantity_req=job_qty,  # CRITICAL: Use the SPECIFIED JOB QUANTITY
                    ct_sqrt_req=q.pkqt_sqrt_req,
                    ct_stock_status=stock_status_instance,
                    ct_customer_name=q.pkqt_customer_name,
                    ct_customer_new_name=q.pkqt_customer_new_name2,
                    ct_customer_po=po,
                    ct_updated_by=request.user,
                    ct_na_quantity=q.pkqt_na_quantity,
                    ct_totalbox_cost=q.pkqt_totalbox_cost,
                    ct_part_code=q.pkqt_part_code,
                    ct_total_cft_display=q.pkqt_total_cft_display,
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
    po_id = request.GET.get('po_id')
    if not po_id:
        return JsonResponse({'success': False, 'message': 'PO ID is required.'}, status=400)
    
    # Fetch all dimension items for this PO
    po_items = POdimension.objects.filter(pod_po_num_id=po_id)
    
    items_data = []
    for item in po_items:
        # Calculate already jobbed quantity by summing unique job releases
        # We group by job_no and take one representative qty (Max) to avoid double counting 
        # multiple specifications (e.g. Wood Base + Wood Lid) for the same job.
        jobbed_data = PkcostingInfo.objects.filter(
            ct_po_dimension=item,
            ct_job_no__isnull=False
        ).exclude(ct_job_no='').values('ct_job_no').annotate(
            job_qty=Max('ct_quantity_req')
        ).aggregate(total=Sum('job_qty'))
        
        already_jobbed_qty = jobbed_data['total'] or 0
        remaining_qty = max(0, float(item.pod_quantity) - float(already_jobbed_qty))
        
        items_data.append({
            'id': item.id,
            'item_name': item.pod_item,
            'ordered_qty': item.pod_quantity,
            'already_jobbed_qty': float(already_jobbed_qty),
            'remaining_qty': float(remaining_qty),
        })
    
    return JsonResponse({'success': True, 'items': items_data})
