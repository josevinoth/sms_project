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

    # All jobs that need return
    return_needed_jobs = Packingjobs.objects.filter(pj_material_returned_flag='Yes').order_by('-id')

    context = {
        'first_name': first_name,
        'return_needed_jobs': return_needed_jobs,
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
            costing_id = key.replace('return_qty_good_', '')
            good_qty_str = value
            damaged_qty_str = request.POST.get(f'return_qty_damaged_{costing_id}', '0')
        elif key.startswith('return_qty_damaged_'):
            continue
        else:
            costing_id = key.replace('return_qty_', '')
            good_qty_str = value
            damaged_qty_str = '0'

        if request.POST.get(f'return_qty_good_{costing_id}') and not key.startswith('return_qty_good_'):
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
            ret_l = float(request.POST.get(f'return_l_{costing_id}') or 0)
            ret_w = float(request.POST.get(f'return_w_{costing_id}') or 0)
            ret_h = float(request.POST.get(f'return_h_{costing_id}') or 0)
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
            cost_reduced_for_item = return_qty_good * fraction * rate

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
