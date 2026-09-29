
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse

from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models import PkcostingInfo, StockMaintenance, Packingjobs, PkProductionReturn
from ..sub_models.pk_costing_summary_mod import PkcostingsummaryInfo
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id


@login_required(login_url='login_page')
def pk_production_return_list(request):
    """
    Shows all jobs that have Material Loop = 'Yes' (Return Needed).
    NA user selects the job to process the return.
    """
    first_name = request.session.get('first_name')

    # All jobs that need return (pending submission)
    return_needed_jobs = Packingjobs.objects.filter(pj_material_returned_flag__in=['Yes', 'Needed']).order_by('-id')

    # Jobs already submitted but pending store acceptance (admin can still edit)
    pending_return_jobs = Packingjobs.objects.filter(pj_material_returned_flag='Pending Return').order_by('-id')

    context = {
        'first_name': first_name,
        'return_needed_jobs': return_needed_jobs,
        'pending_return_jobs': pending_return_jobs,
    }
    return render(request, 'asset_mgt_app/pk_production_return_list.html', context)


@login_required(login_url='login_page')
def pk_production_return_detail(request, job_no):
    first_name = request.session.get('first_name')
    material_items = PkcostingInfo.objects.filter(
        ct_job_no=job_no, 
        ct_cost_type=8,
        ct_stock_status_id=4
    ).select_related('ct_part_code', 'ct_stock_purchase_number').order_by('ct_part_code__pc_code', 'id')

    # Group by Part Code
    grouped_items = {}
    for item in material_items:
        pc = item.ct_part_code.pc_code if item.ct_part_code else 'Misc'
        if pc not in grouped_items:
            grouped_items[pc] = {
                'part_code': pc,
                'description': item.ct_stock_description,
                'cost_type': item.ct_cost_type,
                'grn': item.ct_grn.sm_stock_purchase_number if item.ct_grn else (item.ct_stock_purchase_number.sm_stock_purchase_number if item.ct_stock_purchase_number else ''),
                'job_qty': item.ct_na_quantity or 1,
                'qty_req': item.ct_quantity_req or 1,
                'total_qty': 0,
                'ids': [],
                'length': item.ct_length_req or 0,
                'width': item.ct_width_req or 0,
                'height': item.ct_height_req or 0,
            }
        grouped_items[pc]['total_qty'] += float(item.ct_quantity or 0)
        grouped_items[pc]['ids'].append(str(item.id))

    for k, v in grouped_items.items():
        v['ids_csv'] = ",".join(v['ids'])
        
    context = {
        'first_name': first_name,
        'job_no': job_no,
        'grouped_items': list(grouped_items.values()),
    }
    return render(request, 'asset_mgt_app/pk_production_return_detail.html', context)



@csrf_exempt
@login_required(login_url='login_page')
def pk_production_return_submit(request, job_no):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

    user_id = request.session.get('ses_userID')
    errors = []
    items_processed = 0

    # The frontend now submits returns by Part Code.
    # We will get fields like return_qty_good_P104030, ids_csv_P104030
    for key, value in request.POST.items():
        if not key.startswith('return_qty_good_'):
            continue
            
        pc = key.replace('return_qty_good_', '')
        base_pc = pc.split('_split')[0]
        good_qty = float(value or 0)
        damaged_qty = float(request.POST.get(f'return_qty_damaged_{pc}') or 0)
        total_return = good_qty + damaged_qty
        
        if total_return <= 0:
            continue
            
        ids_csv = request.POST.get(f'ids_csv_{base_pc}', '')
        if not ids_csv:
            continue
            
        ids = [int(x) for x in ids_csv.split(',')]
        
        # Distribute the total return across the associated PkcostingInfo records
        remaining_good = good_qty
        remaining_damaged = damaged_qty
        
        actual_ret_l = float(request.POST.get(f'return_l_{pc}') or 0)
        actual_ret_w = float(request.POST.get(f'return_w_{pc}') or 0)
        actual_ret_h = float(request.POST.get(f'return_h_{pc}') or 0)

        for pk_id in ids:
            if remaining_good <= 0 and remaining_damaged <= 0:
                break
                
            try:
                item = PkcostingInfo.objects.get(pk=pk_id)
            except PkcostingInfo.DoesNotExist:
                continue
                
            # Get already returned quantity for this item
            prev_returns = PkProductionReturn.objects.filter(pr_costing_item=item).aggregate(Sum('pr_return_qty'))['pr_return_qty__sum'] or 0
            available_to_return = float(item.ct_quantity or 0) - float(prev_returns)
            
            if available_to_return <= 0:
                continue
                
            orig_l = float(item.ct_length_req or 0)
            orig_w = float(item.ct_width_req or 0)
            orig_h = float(item.ct_height_req or 0)
            rate = float(item.ct_rate or 0)
            
            orig_vol = orig_l * orig_w * orig_h
            ret_vol = actual_ret_l * actual_ret_w * actual_ret_h
            fraction = (ret_vol / orig_vol) if (orig_vol > 0 and ret_vol > 0) else 1.0
            
            # Apportion Good Qty
            apportion_good = min(remaining_good, available_to_return)
            if apportion_good > 0:
                PkProductionReturn.objects.create(
                    pr_job_no=job_no,
                    pr_costing_item=item,
                    pr_return_qty=apportion_good,
                    pr_return_l=actual_ret_l,
                    pr_return_w=actual_ret_w,
                    pr_return_h=actual_ret_h,
                    pr_orig_l=orig_l,
                    pr_orig_w=orig_w,
                    pr_orig_h=orig_h,
                    pr_rate=rate,
                    pr_fraction=fraction,
                    pr_cost_to_reduce=apportion_good * rate * fraction,
                    pr_return_type='Good',
                    pr_status='Pending',
                    pr_created_by_id=user_id,
                )
                remaining_good -= apportion_good
                available_to_return -= apportion_good
                items_processed += 1
                
            # Apportion Damaged Qty
            apportion_damaged = min(remaining_damaged, available_to_return)
            if apportion_damaged > 0:
                PkProductionReturn.objects.create(
                    pr_job_no=job_no,
                    pr_costing_item=item,
                    pr_return_qty=apportion_damaged,
                    pr_return_l=orig_l,
                    pr_return_w=orig_w,
                    pr_return_h=orig_h,
                    pr_orig_l=orig_l,
                    pr_orig_w=orig_w,
                    pr_orig_h=orig_h,
                    pr_rate=rate,
                    pr_fraction=1.0,
                    pr_cost_to_reduce=0.0,
                    pr_return_type='Damaged',
                    pr_status='Pending',
                    pr_created_by_id=user_id,
                )
                remaining_damaged -= apportion_damaged
                available_to_return -= apportion_damaged
                items_processed += 1

    if not errors:
        try:
            packing_job = Packingjobs.objects.filter(pj_job_no__iexact=job_no).first()
            if packing_job:
                packing_job.pj_material_returned_flag = 'Pending Return'
                packing_job.save()
        except Exception as e:
            errors.append(f"Job update error: {str(e)}")

    if errors:
        messages.warning(request, f"Return processed with some issues: {'; '.join(errors)}")
    else:
        messages.success(request, f"Production return for Job {job_no} submitted for store acceptance.")

    return redirect('pk_production_return_list')


@login_required(login_url='login_page')
def pk_production_return_edit(request, job_no):
    """
    Admin view: Shows all PENDING PkProductionReturn records for a job
    so the admin can correct quantities/dimensions before store accepts them.
    """
    first_name = request.session.get('first_name')
    role = request.session.get('ses_role', '')

    # Only allow admin/manager roles
    # (you can tighten this check to your role names)
    pending_returns = PkProductionReturn.objects.filter(
        pr_job_no=job_no,
        pr_status='Pending'
    ).select_related('pr_costing_item').order_by('ct_part_code__pc_code', 'id')

    context = {
        'first_name': first_name,
        'job_no': job_no,
        'pending_returns': pending_returns,
        'role': role,
    }
    return render(request, 'asset_mgt_app/pk_production_return_edit.html', context)


@csrf_exempt
@login_required(login_url='login_page')
def pk_production_return_edit_save(request, job_no):
    """
    Admin view: Saves edited return quantities and dimensions.
    Deletes old pending records for the job and recreates them with updated values.
    """
    if request.method != 'POST':
        return redirect('pk_production_return_list')

    user_id = request.session.get('ses_userID')

    # Collect all pr_ids being edited
    pr_ids = request.POST.getlist('pr_id')

    errors = []
    updated_count = 0

    for pr_id in pr_ids:
        try:
            ret_record = PkProductionReturn.objects.get(pk=pr_id, pr_status='Pending')
        except PkProductionReturn.DoesNotExist:
            errors.append(f"Return record {pr_id} not found or already accepted.")
            continue

        try:
            new_qty = float(request.POST.get(f'edit_qty_{pr_id}') or 0)
            new_l = float(request.POST.get(f'edit_l_{pr_id}') or 0)
            new_w = float(request.POST.get(f'edit_w_{pr_id}') or 0)
            new_h = float(request.POST.get(f'edit_h_{pr_id}') or 0)
        except (ValueError, TypeError):
            errors.append(f"Invalid values for record {pr_id}.")
            continue

        if new_qty <= 0:
            # Admin set qty to 0 — delete this return record
            ret_record.delete()
            updated_count += 1
            continue

        # Recalculate fraction
        orig_l = ret_record.pr_orig_l or 0
        orig_w = ret_record.pr_orig_w or 0
        orig_h = ret_record.pr_orig_h or 0
        orig_vol = orig_l * orig_w * orig_h

        actual_l = new_l if new_l > 0 else orig_l
        actual_w = new_w if new_w > 0 else orig_w
        actual_h = new_h if new_h > 0 else orig_h
        ret_vol = actual_l * actual_w * actual_h

        fraction = min(ret_vol / orig_vol, 1.0) if (orig_vol > 0 and ret_vol > 0) else 1.0

        ret_record.pr_return_qty = new_qty
        ret_record.pr_return_l = actual_l
        ret_record.pr_return_w = actual_w
        ret_record.pr_return_h = actual_h
        ret_record.pr_fraction = fraction
        ret_record.save()
        updated_count += 1

    if errors:
        messages.warning(request, f"Some records could not be updated: {'; '.join(errors)}")
    else:
        messages.success(request, f"Return records for Job {job_no} updated successfully ({updated_count} items).")

    # --- Handle dynamically added "splits" from the Edit page ---
    for key in request.POST.keys():
        if key.startswith('new_split_qty_'):
            raw_id = key.replace('new_split_qty_', '')
            base_pr_id = raw_id.split('_')[0]
            
            try:
                new_qty = float(request.POST.get(key) or 0)
            except ValueError:
                continue
                
            if new_qty <= 0:
                continue
                
            try:
                base_record = PkProductionReturn.objects.get(pk=base_pr_id)
            except PkProductionReturn.DoesNotExist:
                continue
                
            try:
                new_l = float(request.POST.get(f'new_split_l_{raw_id}') or 0)
                new_w = float(request.POST.get(f'new_split_w_{raw_id}') or 0)
                new_h = float(request.POST.get(f'new_split_h_{raw_id}') or 0)
            except ValueError:
                new_l = new_w = new_h = 0
                
            orig_l = base_record.pr_orig_l or 0
            orig_w = base_record.pr_orig_w or 0
            orig_h = base_record.pr_orig_h or 0
            orig_vol = orig_l * orig_w * orig_h

            actual_l = new_l if new_l > 0 else orig_l
            actual_w = new_w if new_w > 0 else orig_w
            actual_h = new_h if new_h > 0 else orig_h
            ret_vol = actual_l * actual_w * actual_h

            fraction = min(ret_vol / orig_vol, 1.0) if (orig_vol > 0 and ret_vol > 0) else 1.0
            
            # Create the new split record
            PkProductionReturn.objects.create(
                pr_job_no=base_record.pr_job_no,
                pr_costing_item=base_record.pr_costing_item,
                pr_return_qty=new_qty,
                pr_return_l=actual_l,
                pr_return_w=actual_w,
                pr_return_h=actual_h,
                pr_orig_l=orig_l,
                pr_orig_w=orig_w,
                pr_orig_h=orig_h,
                pr_rate=base_record.pr_rate,
                pr_fraction=fraction,
                pr_cost_to_reduce=0.0,
                pr_return_type=base_record.pr_return_type,
                pr_status='Pending',
                pr_created_by_id=user_id,
            )

    return redirect('pk_production_return_list')


@login_required(login_url='login_page')
def pk_production_return_reset(request, job_no):
    """
    Admin view: Rejects/Resets a pending return, sending it back to the original queue.
    Deletes all pending return records for this job and resets the job flag.
    """
    first_name = request.session.get('first_name')
    
    # 1. Delete all pending PkProductionReturn records for this job
    deleted_count, _ = PkProductionReturn.objects.filter(
        pr_job_no=job_no, 
        pr_status='Pending'
    ).delete()
    
    # 2. Reset the flag on Packingjobs back to 'Yes'
    try:
        packing_job = Packingjobs.objects.filter(pj_job_no__iexact=job_no).first()
        if packing_job:
            packing_job.pj_material_returned_flag = 'Yes'
            packing_job.save()
            messages.success(request, f"Job {job_no} has been successfully reset. It is now back in the 'Return Needed' queue.")
        else:
            messages.warning(request, f"Job {job_no} reset, but the packing job record could not be found.")
    except Exception as e:
        messages.error(request, f"Error resetting job {job_no}: {str(e)}")
        
    return redirect('pk_production_return_list')


@login_required(login_url='login_page')
def pk_production_return_pdf(request, job_no):
    returns = PkProductionReturn.objects.filter(pr_job_no=job_no, pr_status='Accepted')
    
    if not returns.exists():
        return HttpResponse('No accepted returns found for this job.')
        
    # Get basic job info from the first return
    first_return = returns.first()
    
    # We will try to fetch the job details from Packingjobs
    from sms_app.models import Packingjobs
    job = Packingjobs.objects.filter(pj_job_no=job_no).first()
    customer = job.pj_customer if job else 'N/A'
    
    context = {
        'job_no': job_no,
        'customer': customer,
        'returns': returns,
        'date': first_return.pr_accepted_at if first_return.pr_accepted_at else first_return.pr_created_at
    }
    
    file_name = f"Production_Return_{job_no}.pdf"
    template_path = 'asset_mgt_app/pk_production_return_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We encountered an error while generating the PDF.')
    return response
