import json
from datetime import datetime
from django.contrib.auth.decorators import login_required
from ..forms import PkretrivalForm
from ..models import PkstockpurchasesInfo,PkcostingInfo,PkquotationsummaryInfo
from ..sub_models.stock_maintenance_mod import StockMaintenance
from django.shortcuts import render, redirect
from django.contrib import messages

def _stock_entry_ref(stock_entry):
    return stock_entry.sm_stock_purchase_number or stock_entry.sm_invoice_no or f"SM-{stock_entry.id}"


def _sum_abs_stock_counts(queryset):
    return sum(abs(float(qty or 0)) for qty in queryset.values_list('sm_count', flat=True))


def _available_qty_for_stock_entry(stock_entry):
    retrieved_qty = _sum_abs_stock_counts(
        StockMaintenance.objects.filter(
            sm_stock_type_id=2,
            sm_invoice_no=_stock_entry_ref(stock_entry),
            sm_partcode=stock_entry.sm_partcode,
        )
    )
    vendor_returned_qty = 0.0
    if stock_entry.sm_vendor_id:
        vendor_returned_qty = _sum_abs_stock_counts(
            StockMaintenance.objects.filter(
                sm_stock_type_id=3,
                sm_vendor=stock_entry.sm_vendor,
                sm_stock_purchase_number=_stock_entry_ref(stock_entry),
                sm_partcode=stock_entry.sm_partcode,
            )
        )
    return max(0.0, float(stock_entry.sm_count or 0.0) - retrieved_qty - vendor_returned_qty)



@login_required(login_url='login_page')
def pk_retrival_add(request, retrival_id='0'):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    na_assessment_num_id = request.session.get('na_assessment_id')

    # Handle single or comma-separated multiple IDs
    retrival_ids = [r_id for r_id in str(retrival_id).split(',') if r_id]
    primary_id = int(retrival_ids[0]) if retrival_ids else 0

    if request.method == "GET":
        if primary_id == 0:
            form = PkretrivalForm()
            total_req_qty = 0
        else:
            retrival = PkcostingInfo.objects.get(pk=primary_id)
            form = PkretrivalForm(instance=retrival)
            
            total_req_qty = 0.0
            for r_id in retrival_ids:
                r_obj = PkcostingInfo.objects.get(pk=int(r_id))
                total_req_qty += float(r_obj.ct_quantity_req or 0) * float(r_obj.ct_na_quantity or 1)
            
        context = {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'na_assessment_num_id': na_assessment_num_id,
            'total_req_qty': total_req_qty if primary_id != 0 else 0,
        }
        return render(request, "asset_mgt_app/pk_retrival_add.html", context)

    else:
        if primary_id == 0:
            form = PkretrivalForm(request.POST)
            if form.is_valid():
                form.save()
                print("Retrieval Form is Valid")
                last_id = PkcostingInfo.objects.latest('id').id
                messages.success(request, 'Record Updated Successfully')
                return redirect('/SMS/pk_retrival_update/' + str(last_id))
            else:
                print("Retrieval Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            retrival = PkcostingInfo.objects.get(pk=primary_id)
            form = PkretrivalForm(request.POST, instance=retrival)
            if form.is_valid():
                stock_purchase_num_id = request.POST.get('ct_stock_purchase_number')
                
                requested_qty = request.POST.get('total_req_qty')
                if not requested_qty:
                    requested_qty = 0.0
                    for r_id in retrival_ids:
                        r_obj = PkcostingInfo.objects.get(pk=int(r_id))
                        requested_qty += float(r_obj.ct_quantity_req or 0) * float(r_obj.ct_na_quantity or 1)
                
                print("Requested Qty (Grouped):", requested_qty)

                if stock_purchase_num_id:
                    try:
                        stock_purchase_obj = StockMaintenance.objects.get(id=stock_purchase_num_id)
                        stock_purchase_num = stock_purchase_obj.sm_stock_purchase_number or stock_purchase_obj.sm_invoice_no or f"SM-{stock_purchase_num_id}"
                        available_qty = _available_qty_for_stock_entry(stock_purchase_obj)
                        print(available_qty)
                        if float(requested_qty) > float(available_qty):
                            messages.error(request, 'Available quantity is less than requested quantity')
                            return redirect(request.META['HTTP_REFERER'])
                        else:
                            # Apply form updates (like status) to all grouped items
                            updated_primary = form.save()
                            stock_status = updated_primary.ct_stock_status.id
                            print("Stock Status ID:", stock_status)
    
                            # Apply to other grouped items
                            if len(retrival_ids) > 1:
                                for r_id in retrival_ids[1:]:
                                    r_obj = PkcostingInfo.objects.get(pk=int(r_id))
                                    r_obj.ct_stock_status = updated_primary.ct_stock_status
                                    r_obj.ct_stock_purchase_number = updated_primary.ct_stock_purchase_number
                                    r_obj.save()

                            if stock_status in [2, 4]:
                                ref_no = stock_purchase_num
                                
                                ids_str = ",".join(retrival_ids)
                                desc_suffix = f"(Costing IDs: {ids_str})"
                                
                                if not StockMaintenance.objects.filter(sm_stock_type_id=2, sm_invoice_no=ref_no, sm_description__endswith=desc_suffix).exists():
                                    try:
                                        actual_qty = float(requested_qty)
                                        StockMaintenance.objects.create(
                                            sm_stock_type_id=2, # Retrieval
                                            sm_invoice_date=datetime.now().date(),
                                            sm_invoice_no=ref_no,
                                            sm_description=f"Retrieved for Assessment {updated_primary.ct_assessment_num.na_assessment_num if updated_primary.ct_assessment_num else 'N/A'} {desc_suffix}",
                                            sm_partcode=stock_purchase_obj.sm_partcode,
                                            sm_count=actual_qty,
                                            sm_uom=stock_purchase_obj.sm_uom,
                                            sm_updated_by_id=user_id
                                        )
                                        messages.success(request, 'Stock Successfully Retrieved & Supplied for all grouped items.')
                                    except Exception as e:
                                        print(f"Error creating retrieval record: {e}")
                                        messages.warning(request, 'Stock supplied but retrieval transaction log failed.')
                                else:
                                    messages.success(request, 'Stock Successfully Retrieved & Supplied for all grouped items.')
                            else:
                                messages.success(request, 'Stock Not Retrieved')
                    except StockMaintenance.DoesNotExist:
                        messages.error(request, 'Selected stock purchase record not found.')
                        return redirect(request.META['HTTP_REFERER'])
                else:
                    messages.error(request, 'Please select a stock with purchase number')
                    return redirect(request.META['HTTP_REFERER'])
            else:
                print("Retrieval Form is Not Valid")
                for field, errors in form.errors.items():
                    for error in errors:
                        print(f"Error in {field}: {error}")
                        messages.error(request, f"Error in {field}: {error}")
                messages.error(request, 'Record Not Updated Successfully')

            return redirect(request.META['HTTP_REFERER'])

# List retrival
@login_required(login_url='login_page')
def pk_retrival_list(request):
    first_name = request.session.get('first_name')
    retrival_queryset = PkcostingInfo.objects.filter(ct_cost_type=8, ct_stock_status__in=[1, 3]).order_by('-ct_job_no', 'ct_part_code', '-id')

    grouped_retrival = {}
    for item in retrival_queryset:
        job_no = item.ct_job_no
        part_code_id = item.ct_part_code_id
        try:
            if item.ct_stock_purchase_number:
                stock_id = item.ct_stock_purchase_number.sm_stock_purchase_number or item.ct_stock_purchase_number.sm_invoice_no or 'None'
            else:
                stock_id = 'None'
        except Exception:
            stock_id = 'None'
        key = f"{job_no}_{part_code_id}_{stock_id}"
        
        if key not in grouped_retrival:
            grouped_retrival[key] = {
                'id': item.id,
                'ids': [str(item.id)],
                'job_no': job_no,
                'customer_name': item.ct_assessment_num.na_customer_name.cu_name if item.ct_assessment_num and item.ct_assessment_num.na_customer_name else (item.ct_customer_name.cu_name if item.ct_customer_name else '-'),
                'customer_po': item.ct_customer_po.po_num if item.ct_customer_po else '',
                'part_code': item.ct_part_code.pc_code if item.ct_part_code else 'None',
                'stock_type': str(item.ct_stock_type) if item.ct_stock_type else '',
                'description': item.ct_part_code.pc_stock_description.stock_description if item.ct_part_code and item.ct_part_code.pc_stock_description else (str(item.ct_stock_description) if item.ct_stock_description else ''),
                'quantity': float(item.ct_na_quantity or 0) * float(item.ct_quantity_req or 0),
                'stock_id': stock_id,
                'stock_status': item.ct_stock_status,
                'updated_at': item.ct_updated_at,
                'updated_by': item.ct_updated_by.first_name if item.ct_updated_by else '',
            }
        else:
            grouped_retrival[key]['ids'].append(str(item.id))
            grouped_retrival[key]['quantity'] += float(item.ct_na_quantity or 0) * float(item.ct_quantity_req or 0)
            
    for k, v in grouped_retrival.items():
        v['ids_csv'] = ",".join(v['ids'])

    context = {
        'grouped_list' : list(grouped_retrival.values()),
        'first_name': first_name,
    }
    return render(request,"asset_mgt_app/pk_retrival_list.html",context)

#Delete retrival
@login_required(login_url='login_page')
def pk_retrival_delete(request,retrival_id):
    retrival = PkcostingInfo.objects.get(pk=retrival_id)
    # Clean up both Retrieval (Type 2) and potential Return (Type 3) records linked to this costing ID
    StockMaintenance.objects.filter(sm_stock_type_id__in=[2, 3], sm_description__contains=f"(Costing ID: {retrival_id})").delete()
    retrival.delete()
    # return redirect('/SMS/pK_retrival_cancel')
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def pK_retrival_cancel(request):
    assessment_num_val = request.session.get('na_assessment_id')
    retrival_summary_id=PkquotationsummaryInfo.objects.get(qs_assessment_num=assessment_num_val).id
    return redirect('/SMS/pk_retrivalsummary_update/' + str(retrival_summary_id))

@login_required(login_url='login_page')
def pk_retrival_multi_update(request):
    if request.method == "POST":
        try:
            import json
            from datetime import datetime
            from django.http import JsonResponse
            data = json.loads(request.body)
            retrival_id = data.get('retrival_id')
            selections = data.get('selections', [])
            user_id = request.session.get('ses_userID')

            if not retrival_id or not selections:
                return JsonResponse({'success': False, 'message': 'Missing data'})

            original_retrival = PkcostingInfo.objects.get(pk=retrival_id)
            total_remaining_req = float(original_retrival.ct_quantity_req or 0) * float(original_retrival.ct_na_quantity or 1)

            # 1. STRICT BACKEND VALIDATION: Prevent negative stock
            for sel in selections:
                stock_id = sel.get('stock_id')
                qty = float(sel.get('qty', 0))
                if qty <= 0:
                    continue
                stock_purchase_obj = StockMaintenance.objects.get(id=stock_id)
                available_qty = _available_qty_for_stock_entry(stock_purchase_obj)
                # Allow a tiny float margin (0.001) for rounding issues, but strictly block over-retrieving
                if qty > (available_qty + 0.001):
                    return JsonResponse({
                        'success': False, 
                        'message': f"Critical Stock Error: You requested {qty} from {stock_purchase_obj.sm_stock_purchase_number}, but only {available_qty} is available! Retrieval blocked to prevent negative stock."
                    })

            # 2. PROCEED WITH CLONING AND RETRIEVAL
            first = True
            for sel in selections:
                stock_id = sel.get('stock_id')
                qty = float(sel.get('qty', 0))
                rate = float(sel.get('rate', 0))

                if qty <= 0:
                    continue

                stock_purchase_obj = StockMaintenance.objects.get(id=stock_id)
                ref_no = stock_purchase_obj.sm_stock_purchase_number or stock_purchase_obj.sm_invoice_no or f"SM-{stock_id}"

                # Create or update PkcostingInfo
                if first:
                    ret_obj = original_retrival
                    first = False
                else:
                    ret_obj = PkcostingInfo.objects.get(pk=retrival_id)
                    ret_obj.pk = None # Clone it
                
                # If per-job quantity was stored in ct_quantity_req, adjust it based on na_quantity ratio
                na_qty = float(ret_obj.ct_na_quantity or 1)
                ret_obj.ct_quantity_req = qty / na_qty
                ret_obj.ct_rate = rate
                # Calculate cost based on type
                if ret_obj.ct_cost_type.id == 8 and ret_obj.ct_stock_type and ret_obj.ct_stock_type.id == 1:
                    # Wood: CFT * Rate
                    ret_obj.ct_total_cost = float(ret_obj.ct_cft or 0) * qty * rate
                else:
                    ret_obj.ct_total_cost = qty * rate
                
                ret_obj.ct_stock_purchase_number = stock_purchase_obj
                ret_obj.ct_stock_status_id = 2 # Supplied
                ret_obj.save()

                # Deduct stock (create Type 2)
                if not StockMaintenance.objects.filter(sm_stock_type_id=2, sm_invoice_no=ref_no, sm_description__endswith=f"(Costing ID: {ret_obj.id})").exists():
                    StockMaintenance.objects.create(
                        sm_stock_type_id=2, # Retrieval
                        sm_invoice_date=datetime.now().date(),
                        sm_invoice_no=ref_no, 
                        sm_description=f"Retrieved for Assessment {ret_obj.ct_assessment_num.na_assessment_num if ret_obj.ct_assessment_num else 'N/A'} (Costing ID: {ret_obj.id})",
                        sm_partcode=stock_purchase_obj.sm_partcode,
                        sm_count=qty,
                        sm_uom=stock_purchase_obj.sm_uom,
                        sm_updated_by_id=user_id
                    )

            return JsonResponse({'success': True, 'message': 'Successfully processed multiple retrievals.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request'})