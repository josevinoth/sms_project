from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.db.models import Max
from ..models import PkProductionReturn, PkcostingInfo, StockMaintenance, Packingjobs
from ..sub_models.part_code_mod import PkpartcodeInfo
from ..sub_models.pk_costing_summary_mod import PkcostingsummaryInfo
from .general_utils import generate_next_number, get_financial_year, get_session_branch_id, get_branch_code


DIMENSION_TOLERANCE = 0.001


def _clean_dim(value):
    try:
        return round(float(value or 0), 4)
    except (TypeError, ValueError):
        return 0.0


def _same_dimensions(a_l, a_w, a_h, b_l, b_w, b_h):
    return (
        abs(_clean_dim(a_l) - _clean_dim(b_l)) <= DIMENSION_TOLERANCE and
        abs(_clean_dim(a_w) - _clean_dim(b_w)) <= DIMENSION_TOLERANCE and
        abs(_clean_dim(a_h) - _clean_dim(b_h)) <= DIMENSION_TOLERANCE
    )


def _source_partcode_for_return(production_return):
    item = production_return.pr_costing_item
    if not item:
        return None
    return item.ct_part_code or (
        item.ct_stock_purchase_number.sm_partcode
        if item.ct_stock_purchase_number and item.ct_stock_purchase_number.sm_partcode
        else None
    )


def _matching_partcode_for_dims(source_partcode, length, width, height):
    if not source_partcode:
        return None

    queryset = PkpartcodeInfo.objects.filter(
        pc_stock_description=source_partcode.pc_stock_description,
        pc_stock_type=source_partcode.pc_stock_type,
        pc_uom=source_partcode.pc_uom,
    )

    for partcode in queryset:
        if _same_dimensions(partcode.pc_length, partcode.pc_width, partcode.pc_height, length, width, height):
            return partcode
    return None


def _dimension_token(value):
    number = _clean_dim(value)
    text = f"{number:g}".replace(".", "P")
    return text or "0"


def _build_offcut_partcode(source_partcode, length, width, height):
    base = (source_partcode.pc_code if source_partcode else "RET").upper()
    dim_code = f"{_dimension_token(length)}X{_dimension_token(width)}X{_dimension_token(height)}"
    raw_code = f"{base}-OFF-{dim_code}"
    code = raw_code[:50]
    if not PkpartcodeInfo.objects.filter(pc_code=code).exists():
        return code

    suffix = 2
    while True:
        suffix_text = f"-{suffix}"
        code = f"{raw_code[:50 - len(suffix_text)]}{suffix_text}"
        if not PkpartcodeInfo.objects.filter(pc_code=code).exists():
            return code
        suffix += 1


def _create_offcut_partcode(source_partcode, length, width, height, user_id=None):
    values = {
        "pc_code": _build_offcut_partcode(source_partcode, length, width, height),
        "pc_stock_description": source_partcode.pc_stock_description,
        "pc_stock_type": source_partcode.pc_stock_type,
        "pc_uom": source_partcode.pc_uom,
        "pc_length": length,
        "pc_width": width,
        "pc_height": height,
        "pc_updated_by_id": user_id,
        "pc_con_length": source_partcode.pc_con_length or 0.0,
        "pc_diameter_width": source_partcode.pc_diameter_width,
    }

    try:
        with transaction.atomic():
            return PkpartcodeInfo.objects.create(**values)
    except IntegrityError:
        next_id = (PkpartcodeInfo.objects.aggregate(max_id=Max("id"))["max_id"] or 0) + 1
        return PkpartcodeInfo.objects.create(id=next_id, **values)


def _resolve_return_partcode(production_return, user_id=None, create_missing=False):
    source_partcode = _source_partcode_for_return(production_return)
    if not source_partcode:
        return None, "Missing original partcode"

    if production_return.pr_return_type != "Good":
        return None, "Damaged/Scrap - not added to usable stock"

    length = _clean_dim(production_return.pr_return_l)
    width = _clean_dim(production_return.pr_return_w)
    height = _clean_dim(production_return.pr_return_h)

    if _same_dimensions(length, width, height, source_partcode.pc_length, source_partcode.pc_width, source_partcode.pc_height):
        return source_partcode, "Same size - original partcode"

    matching_partcode = _matching_partcode_for_dims(source_partcode, length, width, height)
    if matching_partcode:
        return matching_partcode, "Offcut - matched existing partcode"

    if not create_missing:
        return None, "Offcut - new partcode will be created"

    if not source_partcode.pc_stock_description_id or not source_partcode.pc_stock_type_id:
        return None, "Cannot create offcut partcode because stock type/description is missing"

    new_partcode = _create_offcut_partcode(source_partcode, length, width, height, user_id)
    return new_partcode, "Offcut - created new partcode"


def _return_total_cft(production_return):
    length = _clean_dim(production_return.pr_return_l)
    width = _clean_dim(production_return.pr_return_w)
    height = _clean_dim(production_return.pr_return_h)
    qty = _clean_dim(production_return.pr_return_qty)
    return round(((height * length * width) / 144) * qty, 4) if qty else 0.0

@login_required(login_url='login_page')
def pk_return_acceptance_list(request):
    """
    Shows a list of all pending production returns grouped by job.
    The store team will use this to physically verify and accept the returned items into inventory.
    """
    pending_returns = PkProductionReturn.objects.filter(pr_status='Pending').select_related('pr_costing_item', 'pr_costing_item__ct_part_code')

    for production_return in pending_returns:
        target_partcode, target_action = _resolve_return_partcode(production_return, create_missing=False)
        production_return.target_partcode_preview = target_partcode
        production_return.target_action_preview = target_action
    
    # Group by Job Number for the UI
    jobs_dict = {}
    for pr in pending_returns:
        job_no = pr.pr_job_no
        if job_no not in jobs_dict:
            jobs_dict[job_no] = []
        jobs_dict[job_no].append(pr)
        
    # Convert dict to list of dicts for template iteration
    grouped_returns = [{'job_no': job, 'items': items} for job, items in jobs_dict.items()]

    context = {
        'grouped_returns': grouped_returns,
        'page_title': 'Return Acceptance Queue'
    }
    return render(request, 'asset_mgt_app/pk_return_acceptance_list.html', context)


@login_required(login_url='login_page')
@transaction.atomic
def pk_accept_production_return(request, job_no):
    """
    Accepts all pending returns for a specific job.
    - Updates PkcostingInfo quantities and costs
    - Creates StockMaintenance entries
    - Updates PkcostingsummaryInfo total cost
    - Sets PkProductionReturn status to Accepted
    - Sets Packingjobs pj_material_returned_flag to 'Returned'
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

    user_id = request.session.get('ses_userID')
    fy = get_financial_year()
    branch_id = get_session_branch_id(request)
    branch_code = get_branch_code(branch_id)
    prefix = f"{fy}_{branch_code}_GRN_PK_"

    pending_returns = PkProductionReturn.objects.filter(pr_job_no=job_no, pr_status='Pending')
    
    if not pending_returns.exists():
        messages.warning(request, f"No pending returns found for Job {job_no}.")
        return redirect('pk_return_acceptance_list')

    total_cost_reduced = 0.0
    errors = []

    for pr in pending_returns:
        try:
            item = pr.pr_costing_item
            if not item:
                continue

            current_qty = float(item.ct_na_quantity or item.ct_quantity or 0)
            if pr.pr_return_qty > current_qty:
                errors.append(f"Return qty exceeds available for '{item.ct_stock_description}'.")
                continue

            target_partcode = None
            target_action = "Damaged/Scrap - not added to usable stock"
            if pr.pr_return_type == 'Good':
                target_partcode, target_action = _resolve_return_partcode(pr, user_id=user_id, create_missing=True)
                if not target_partcode:
                    errors.append(f"Could not add returned stock for '{item.ct_stock_description}': {target_action}.")
                    continue

            # 1. Update Costing Info
            current_total_cost = float(item.ct_total_cost or (current_qty * pr.pr_rate))
            new_cost = max(0, current_total_cost - pr.pr_cost_to_reduce)
            
            item.ct_na_quantity = current_qty - pr.pr_return_qty
            item.ct_total_cost = new_cost
            item.ct_return_qty = (float(item.ct_return_qty) if item.ct_return_qty else 0) + pr.pr_return_qty
            item.ct_return_status = 'Accepted'
            item.ct_return_type = 'Onsite' if pr.pr_return_type == 'Damaged' else 'In-House'
            item.save()

            # 2. Create Stock Maintenance Entry for reusable stock only.
            # Damaged/scrap returns are accepted for traceability and costing, but not added to usable stock.
            desc = f"Production Return ({pr.pr_return_type}) | Job: {job_no}"
            if pr.pr_return_type == 'Good' and pr.pr_fraction < 1.0:
                desc += f" | Dims: {pr.pr_return_l}x{pr.pr_return_w}x{pr.pr_return_h} | Vol: {pr.pr_fraction:.2f}"
            elif pr.pr_return_type == 'Damaged':
                desc = f"Production Return (DAMAGED/SCRAP) | Job: {job_no} | Dims: {pr.pr_orig_l}x{pr.pr_orig_w}x{pr.pr_orig_h}"

            sm_entry = None
            if pr.pr_return_type == 'Good':
                total_cft = _return_total_cft(pr)
                unit_cft = round(total_cft / float(pr.pr_return_qty or 1), 4)
                unit_cost = pr.pr_rate * pr.pr_fraction
                desc = f"{desc} | Target Partcode: {target_partcode.pc_code} | {target_action}"

                sm_entry = StockMaintenance.objects.create(
                    sm_stock_type_id=3, # Return
                    sm_partcode=target_partcode,
                    sm_thickness=pr.pr_return_h,
                    sm_width=pr.pr_return_w,
                    sm_length=pr.pr_return_l,
                    sm_invoice_date=timezone.now().date(),
                    sm_invoice_no=str(item.ct_assessment_num.na_assessment_num) if item.ct_assessment_num else job_no,
                    sm_description=desc[:255],
                    sm_count=pr.pr_return_qty,
                    sm_cft=unit_cft,
                    sm_total_cft=total_cft,
                    sm_per_unit_cost=unit_cost,
                    sm_total_price=round(total_cft * float(pr.pr_rate or 0), 2),
                    sm_updated_by_id=user_id,
                )
                sm_entry.sm_stock_purchase_number = generate_next_number(StockMaintenance, 'sm_stock_purchase_number', prefix, 6)
                sm_entry.save(update_fields=['sm_stock_purchase_number'])

            # 3. Mark PR as Accepted
            pr.pr_status = 'Accepted'
            pr.pr_accepted_at = timezone.now()
            pr.pr_accepted_by_id = user_id
            pr.pr_grn_number = sm_entry.sm_stock_purchase_number if sm_entry else "DAMAGED/SCRAP-NO-STOCK"
            pr.save()

            total_cost_reduced += pr.pr_cost_to_reduce

        except Exception as e:
            errors.append(f"Error processing item: {str(e)}")

    # 4. Reduce job overall cost in PkcostingsummaryInfo
    if total_cost_reduced > 0:
        summary = PkcostingsummaryInfo.objects.select_for_update().filter(cs_job_no=job_no).first()
        if summary:
            try:
                if summary.cs_wood_cost:
                    summary.cs_wood_cost = max(0, float(summary.cs_wood_cost) - total_cost_reduced)
                if summary.cs_total_cost_wom:
                    summary.cs_total_cost_wom = max(0, float(summary.cs_total_cost_wom) - total_cost_reduced)
                if summary.cs_total_cost_wm:
                    margin = float(summary.cs_margin or 0)
                    summary.cs_total_cost_wm = summary.cs_total_cost_wom * (1 + margin / 100)
                if summary.cs_final_cost:
                    gst = float(summary.cs_gst or 0)
                    summary.cs_final_cost = summary.cs_total_cost_wm * (1 + gst / 100)
                summary.save()
            except Exception as e:
                errors.append(f"Cost summary update error: {str(e)}")

    # 5. Mark job as Returned in Packingjobs
    try:
        packing_job = Packingjobs.objects.filter(pj_job_no__iexact=job_no).first()
        if packing_job:
            packing_job.pj_material_returned_flag = 'Returned'
            packing_job.save()
    except Exception as e:
        errors.append(f"Job update error: {str(e)}")

    if errors:
        messages.warning(request, f"Accepted with some issues: {'; '.join(errors)}")
    else:
        messages.success(request, f"Successfully accepted returns for Job {job_no}. Inventory and job costs updated.")

    return redirect('pk_return_acceptance_list')
