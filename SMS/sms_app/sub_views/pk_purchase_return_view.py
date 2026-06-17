from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..models import PkcostingInfo, StockMaintenance
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id


@login_required(login_url='login_page')
def pk_purchase_return_list(request):
    """
    Shows all accepted stock items (ct_cost_type=8, stock accepted = status 4)
    that are not already fully returned.
    """
    first_name = request.session.get('first_name')

    # Get all accepted material costing items
    accepted_items = PkcostingInfo.objects.filter(
        ct_cost_type=8,
        ct_stock_status_id=4,  # Accepted/Received
        ct_is_purchase_return=False
    ).exclude(ct_na_quantity=0).order_by('-id')

    context = {
        'first_name': first_name,
        'accepted_items': accepted_items,
    }
    return render(request, 'asset_mgt_app/pk_purchase_return_list.html', context)


@csrf_exempt
@login_required(login_url='login_page')
def pk_process_purchase_return(request, costing_id):
    """
    Processes a bad quality return for a specific accepted item.
    - Deducts quantity from PkcostingInfo (warehouse).
    - Creates a StockMaintenance Debit Note entry.
    - Marks ct_is_purchase_return = True for tracking.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

    user_id = request.session.get('ses_userID')
    fy = get_financial_year()
    branch_id = get_session_branch_id(request)
    branch_code = get_branch_code(branch_id)
    prefix = f"{fy}_{branch_code}_GRN_PK_"

    return_qty_str = request.POST.get('return_qty', '0')
    return_reason = request.POST.get('return_reason', 'Bad Quality')

    try:
        return_qty = float(return_qty_str)
    except (ValueError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid return quantity.'})

    if return_qty <= 0:
        return JsonResponse({'status': 'error', 'message': 'Return quantity must be > 0.'})

    try:
        item = PkcostingInfo.objects.get(pk=costing_id)
        current_qty = float(item.ct_na_quantity or item.ct_quantity or 0)
        rate = float(item.ct_rate or 0)

        if return_qty > current_qty:
            return JsonResponse({'status': 'error', 'message': f'Return quantity ({return_qty}) exceeds available quantity ({current_qty}).'})

        # Reduce quantity
        new_qty = current_qty - return_qty
        item.ct_na_quantity = new_qty
        item.ct_total_cost = new_qty * rate
        item.ct_return_qty = (item.ct_return_qty or 0) + return_qty
        item.ct_return_reason = return_reason
        item.ct_return_type = 'Purchase'
        
        # If fully returned, mark it
        if new_qty <= 0:
            item.ct_is_purchase_return = True
            item.ct_return_status = 'Accepted'
        
        item.save()

        # Create StockMaintenance Return (Debit Note) entry (type=3)
        sm_return = StockMaintenance.objects.create(
            sm_stock_type_id=3,  # Return/Debit
            sm_partcode=item.ct_part_code,
            sm_thickness=item.ct_height or 0,
            sm_width=item.ct_width or 0,
            sm_length=item.ct_length or 0,
            sm_invoice_date=datetime.now().date(),
            sm_invoice_no=str(item.ct_assessment_num.na_assessment_num) if item.ct_assessment_num else "",
            sm_description=(
                f"Purchase Return (Bad Quality) - Vendor: "
                f"{item.ct_vendor.vn_name if hasattr(item, 'ct_vendor') and item.ct_vendor else 'Unknown'} | "
                f"Reason: {return_reason}"
            ),
            sm_count=return_qty,
            sm_total_cft=0,
            sm_per_unit_cost=rate,
            sm_updated_by_id=user_id,
        )
        sm_return.sm_stock_purchase_number = generate_next_number(
            StockMaintenance, 'sm_stock_purchase_number', prefix, 6
        )
        sm_return.save(update_fields=['sm_stock_purchase_number'])

        return JsonResponse({'status': 'success', 'message': 'Purchase return processed successfully.'})

    except PkcostingInfo.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Costing item not found.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
