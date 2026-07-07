from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.db.models import Max
from ..models import PkProductionReturn, PkcostingInfo, StockMaintenance, Packingjobs
from ..sub_models.part_code_mod import PkpartcodeInfo
from ..sub_models.stock_description_mod import Stockdescription
from ..sub_models.pk_costing_summary_mod import PkcostingsummaryInfo
from ..models import User_extInfo
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
    """
    Search ALL part codes of the same stock_type AND same base material name
    for a matching dimension.
    Base material = text before ' - ' in the description (e.g. 'Pine wood' from 'Pine wood - 4 * 4 * 9.5')
    """
    # Get the base material name from source partcode description
    source_desc = str(source_partcode.pc_stock_description) if source_partcode.pc_stock_description else ''
    source_base = source_desc.split(' - ')[0].strip().lower()

    queryset = PkpartcodeInfo.objects.filter(
        pc_stock_type=source_partcode.pc_stock_type,
    ).exclude(pc_length=0, pc_width=0, pc_height=0).select_related('pc_stock_description')

    for partcode in queryset:
        if _same_dimensions(partcode.pc_length, partcode.pc_width, partcode.pc_height, length, width, height):
            # Also verify base material name matches
            pc_desc = str(partcode.pc_stock_description) if partcode.pc_stock_description else ''
            pc_base = pc_desc.split(' - ')[0].strip().lower()
            if source_base and pc_base and source_base == pc_base:
                return partcode
            elif not source_base:
                # If source has no description, match by dims only (original behaviour)
                return partcode
    return None


def _dim_to_code_token(value):
    """Convert dimension to code token: 1 -> '10', 1.2 -> '12', 3.5 -> '35', 14 -> '140' (multiply by 10, no dot)"""
    v = _clean_dim(value)
    # Multiply by 10 to shift one decimal, format as integer
    token = str(int(round(v * 10)))
    return token or '0'


def _build_new_partcode_code(source_partcode, height, width, length):
    """
    Build a part code in the same format as existing codes:
    E.g. K035140  =  prefix K + height(1->10) + width(3.5->35) + length(14->140)
    Derives prefix from source_partcode.pc_code first letter(s).
    """
    # Get the alphabetic prefix from the source part code
    prefix = ''
    for ch in (source_partcode.pc_code if source_partcode else 'RET'):
        if ch.isalpha():
            prefix += ch
        else:
            break
    prefix = prefix.upper() or 'RET'

    h_tok = _dim_to_code_token(height)
    w_tok = _dim_to_code_token(width)
    l_tok = _dim_to_code_token(length)
    raw_code = f"{prefix}{h_tok}{w_tok}{l_tok}"

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
    """
    Create a NEW part code + Stockdescription entry for a returned offcut
    using the format:  K121625 / 'Kiln-dry wood - 1.2 * 1.6 * 2.5'
    """
    # Format the description name: derive base material name from existing description
    # e.g. 'Kiln-dry wood - 1 * 3.5 * 14'  ->  base = 'Kiln-dry wood'
    orig_desc_name = str(source_partcode.pc_stock_description)
    # Strip the size suffix if it contains " - " and numbers/asterisks
    base_material = orig_desc_name.split(' - ')[0].strip()

    # Format dimensions cleanly: remove trailing zeros
    def fmt(v):
        n = _clean_dim(v)
        return f"{n:g}"

    new_desc_name = f"{base_material} - {fmt(height)} * {fmt(width)} * {fmt(length)}"
    new_pc_code = _build_new_partcode_code(source_partcode, height, width, length)

    # Get or create the Stockdescription entry
    stock_desc, _ = Stockdescription.objects.get_or_create(
        stock_description=new_desc_name,
        defaults={
            'stock_type': source_partcode.pc_stock_type,
            'stock_received': source_partcode.pc_uom,
            'stock_Consumption': source_partcode.pc_uom,
        }
    )

    values = {
        "pc_code": new_pc_code,
        "pc_stock_description": stock_desc,
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

    # Try to create a new offcut partcode
    # If source partcode is missing stock_description or stock_type, try to get them from the costing item
    if not source_partcode.pc_stock_description_id:
        item = production_return.pr_costing_item
        if item:
            desc_name = str(item.ct_stock_description) if item.ct_stock_description else None
            if desc_name:
                stock_desc, _ = Stockdescription.objects.get_or_create(
                    stock_description=desc_name,
                    defaults={
                        'stock_type': source_partcode.pc_stock_type,
                        'stock_received': source_partcode.pc_uom,
                        'stock_Consumption': source_partcode.pc_uom,
                    }
                )
                source_partcode.pc_stock_description = stock_desc

    if not source_partcode.pc_stock_type_id:
        # Fall back to returning the source partcode itself (same size)
        return source_partcode, "Same size - original partcode (fallback)"

    if not source_partcode.pc_stock_description_id:
        # Still missing description — use source partcode as fallback
        return source_partcode, "Same size - original partcode (fallback)"

    new_partcode = None
    try:
        new_partcode = _create_offcut_partcode(source_partcode, length, width, height, user_id)
    except Exception:
        pass

    if new_partcode:
        return new_partcode, "Offcut - created new partcode"
    else:
        # Fall back to the source partcode if new offcut creation fails
        return source_partcode, "Same size - original partcode (fallback)"


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

    user_id = request.session.get('ses_userID')
    try:
        user_ext = User_extInfo.objects.get(user=user_id)
        is_admin = (user_ext.emp_role.role_name.lower() == 'admin' or user_ext.emp_role.id == 1)
    except:
        is_admin = False

    context = {
        'grouped_returns': grouped_returns,
        'page_title': 'Return Acceptance Queue',
        'is_admin': is_admin,
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
            # Check if updated values were submitted via POST
            if f'return_qty_{pr.id}' in request.POST:
                new_qty = _clean_dim(request.POST.get(f'return_qty_{pr.id}'))
                new_l = _clean_dim(request.POST.get(f'return_l_{pr.id}', pr.pr_return_l))
                new_w = _clean_dim(request.POST.get(f'return_w_{pr.id}', pr.pr_return_w))
                new_h = _clean_dim(request.POST.get(f'return_h_{pr.id}', pr.pr_return_h))
                
                if new_qty != pr.pr_return_qty or new_l != pr.pr_return_l or new_w != pr.pr_return_w or new_h != pr.pr_return_h:
                    pr.pr_return_qty = new_qty
                    pr.pr_return_l = new_l
                    pr.pr_return_w = new_w
                    pr.pr_return_h = new_h
                    
                    # Recalculate fraction and cost reduction
                    orig_vol = pr.pr_orig_l * pr.pr_orig_w * pr.pr_orig_h
                    ret_vol = new_l * new_w * new_h
                    fraction = min(ret_vol / orig_vol, 1.0) if (orig_vol > 0 and ret_vol > 0) else 1.0
                    pr.pr_fraction = fraction
                    pr.pr_cost_to_reduce = new_qty * fraction * pr.pr_rate
                    pr.save()

            item = pr.pr_costing_item
            if not item:
                continue

            current_qty = float(item.ct_na_quantity or item.ct_quantity or 0)
            # Cap return qty to current available (handles re-try after partial accept)
            effective_return_qty = min(pr.pr_return_qty, max(current_qty, 0))

            target_partcode = None
            target_action = "Damaged/Scrap - not added to usable stock"
            if pr.pr_return_type == 'Good':
                try:
                    target_partcode, target_action = _resolve_return_partcode(pr, user_id=user_id, create_missing=True)
                except Exception as e:
                    target_partcode = _source_partcode_for_return(pr)
                    target_action = f"Fallback to source partcode (error: {str(e)[:60]})"
                if not target_partcode:
                    errors.append(f"Could not resolve partcode for '{item.ct_stock_description}': {target_action}. Accepting anyway.")
                    # Still mark it accepted so it doesn't loop forever
                    pr.pr_status = 'Accepted'
                    pr.pr_accepted_at = timezone.now()
                    pr.pr_accepted_by_id = user_id
                    pr.pr_grn_number = "NO-STOCK-ENTRY"
                    pr.save()
                    continue

            # 1. Update Costing Info
            current_total_cost = float(item.ct_total_cost or (current_qty * pr.pr_rate))
            new_cost = max(0, current_total_cost - pr.pr_cost_to_reduce)

            item.ct_na_quantity = max(0, current_qty - effective_return_qty)
            item.ct_total_cost = new_cost
            item.ct_return_qty = (float(item.ct_return_qty) if item.ct_return_qty else 0) + effective_return_qty
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
                desc = f"{desc} | Partcode: {target_partcode.pc_code} | {target_action}"

                # Always create a new stock entry (Ledger append-only)
                # to prevent mutating previous retrievals or purchases.
                sm_entry = StockMaintenance.objects.create(
                    sm_stock_type_id=3,  # Return
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

    # 5. Mark job as Returned in Packingjobs ONLY if all PR records are now accepted
    remaining_pending = PkProductionReturn.objects.filter(pr_job_no=job_no, pr_status='Pending').count()
    try:
        packing_job = Packingjobs.objects.filter(pj_job_no__iexact=job_no).first()
        if packing_job:
            if remaining_pending == 0:
                packing_job.pj_material_returned_flag = 'Returned'
            else:
                # Some items still pending — keep as Pending Return so it stays visible
                packing_job.pj_material_returned_flag = 'Pending Return'
            packing_job.save()
    except Exception as e:
        errors.append(f"Job update error: {str(e)}")

    if errors:
        messages.warning(request, f"Accepted with some issues: {'; '.join(errors)}")
    else:
        messages.success(request, f"Successfully accepted returns for Job {job_no}. Inventory and job costs updated.")

    return redirect('pk_return_acceptance_list')


@login_required(login_url='login_page')
@transaction.atomic
def pk_reject_production_return(request, job_no):
    """
    Rejects all pending returns for a specific job back to Production.
    - Sets PkProductionReturn status to 'Rejected'
    - Sets Packingjobs pj_material_returned_flag back to 'Yes' (Return Needed)
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

    pending_returns = PkProductionReturn.objects.filter(pr_job_no=job_no, pr_status='Pending')
    
    if not pending_returns.exists():
        messages.warning(request, f"No pending returns found for Job {job_no}.")
        return redirect('pk_return_acceptance_list')

    # 1. Mark PR as Rejected
    pending_returns.update(pr_status='Rejected')

    # 2. Reset job as Return Needed in Packingjobs
    try:
        packing_job = Packingjobs.objects.filter(pj_job_no__iexact=job_no).first()
        if packing_job:
            packing_job.pj_material_returned_flag = 'Yes'
            packing_job.save()
    except Exception as e:
        messages.error(request, f"Error updating job status: {str(e)}")

    messages.success(request, f"Successfully rejected returns for Job {job_no}. Sent back to Production.")
    return redirect('pk_return_acceptance_list')
