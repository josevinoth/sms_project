from datetime import datetime
from django.contrib.auth.decorators import login_required
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
    return_needed_jobs = Packingjobs.objects.filter(pj_material_returned_flag='Yes').order_by('-id')

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
    """
    Shows all material items for a given job_no so the NA user can enter how many to return.
    Looks up by ct_job_no first, then falls back to assessment_num + customer_po from summary.
    """
    first_name = request.session.get('first_name')

    material_items = PkcostingInfo.objects.none()

    # First try: filter directly by ct_job_no
    material_items = PkcostingInfo.objects.filter(
        ct_job_no=job_no,
        ct_cost_type=8,
    ).order_by('id')

    # Second try: look up via PkcostingsummaryInfo if nothing found
    if not material_items.exists():
        summary = PkcostingsummaryInfo.objects.filter(cs_job_no=job_no).first()
        if summary:
            material_items = PkcostingInfo.objects.filter(
                ct_assessment_num=summary.cs_assessment_num,
                ct_customer_po=summary.cs_customer_po,
                ct_cost_type=8,
            ).order_by('id')

    # Third try: any costing record linked to this job (no cost_type filter)
    if not material_items.exists():
        summary = PkcostingsummaryInfo.objects.filter(cs_job_no=job_no).first()
        if summary:
            material_items = PkcostingInfo.objects.filter(
                ct_assessment_num=summary.cs_assessment_num,
                ct_customer_po=summary.cs_customer_po,
            ).order_by('id')

    # Check if job is On-Site
    is_onsite = False
    packing_job = Packingjobs.objects.filter(pj_job_no__iexact=job_no).first()
    if packing_job and packing_job.pj_pack_type and 'On-Site' in packing_job.pj_pack_type:
        is_onsite = True

    context = {
        'first_name': first_name,
        'job_no': job_no,
        'material_items': material_items,
        'is_onsite': is_onsite,
    }
    return render(request, 'asset_mgt_app/pk_production_return_detail.html', context)



@csrf_exempt
@login_required(login_url='login_page')
def pk_production_return_submit(request, job_no):
    """
    Processes all the return quantities submitted by the NA user.
    Creates Pending PkProductionReturn records for store acceptance.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

    user_id = request.session.get('ses_userID')
    errors = []
    items_processed = 0

    for key, value in request.POST.items():
        if not key.startswith('return_qty_good_') and not key.startswith('return_qty_'):
            continue

        if key.startswith('return_qty_good_'):
            raw_id = key.replace('return_qty_good_', '')
            costing_id = raw_id.split('_split')[0]
            
            good_qty_str = value
            damaged_qty_str = request.POST.get(f'return_qty_damaged_{raw_id}', '0')
        elif key.startswith('return_qty_damaged_'):
            continue
        else:
            raw_id = key.replace('return_qty_', '')
            costing_id = raw_id.split('_split')[0]
            
            good_qty_str = value
            damaged_qty_str = '0'

        if request.POST.get(f'return_qty_good_{raw_id}') and not key.startswith('return_qty_good_'):
            continue

        try:
            return_qty_good = float(good_qty_str or 0)
            return_qty_damaged = float(damaged_qty_str or 0)
            total_return_qty = return_qty_good + return_qty_damaged
        except (ValueError, TypeError):
            continue

        if total_return_qty <= 0:
            continue

        try:
            ret_l = float(request.POST.get(f'return_l_{raw_id}') or 0)
            ret_w = float(request.POST.get(f'return_w_{raw_id}') or 0)
            ret_h = float(request.POST.get(f'return_h_{raw_id}') or 0)
        except (ValueError, TypeError):
            ret_l = ret_w = ret_h = 0

        try:
            item = PkcostingInfo.objects.get(pk=costing_id)
            rate = float(item.ct_rate or 0)
            orig_l = float(item.ct_length or 0)
            orig_w = float(item.ct_width or 0)
            orig_h = float(item.ct_height or 0)
            orig_vol = orig_l * orig_w * orig_h

            actual_ret_l = ret_l if ret_l > 0 else orig_l
            actual_ret_w = ret_w if ret_w > 0 else orig_w
            actual_ret_h = ret_h if ret_h > 0 else orig_h
            ret_vol = actual_ret_l * actual_ret_w * actual_ret_h

            fraction = min(ret_vol / orig_vol, 1.0) if (orig_vol > 0 and ret_vol > 0) else 1.0
            cost_reduced_for_item = 0.0  # Do not reduce cost from costing as per user requirement

            if return_qty_good > 0:
                PkProductionReturn.objects.create(
                    pr_job_no=job_no,
                    pr_costing_item=item,
                    pr_return_qty=return_qty_good,
                    pr_return_l=actual_ret_l,
                    pr_return_w=actual_ret_w,
                    pr_return_h=actual_ret_h,
                    pr_orig_l=orig_l,
                    pr_orig_w=orig_w,
                    pr_orig_h=orig_h,
                    pr_rate=rate,
                    pr_fraction=fraction,
                    pr_cost_to_reduce=cost_reduced_for_item,
                    pr_return_type='Good',
                    pr_status='Pending',
                    pr_created_by_id=user_id,
                )

            if return_qty_damaged > 0:
                PkProductionReturn.objects.create(
                    pr_job_no=job_no,
                    pr_costing_item=item,
                    pr_return_qty=return_qty_damaged,
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

            items_processed += 1

        except PkcostingInfo.DoesNotExist:
            errors.append(f"Costing item ID {costing_id} not found.")
        except Exception as e:
            errors.append(f"Error for item {costing_id}: {str(e)}")

    if items_processed == 0 and not errors:
        return redirect('pk_production_return_list')

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
    ).select_related('pr_costing_item').order_by('id')

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
