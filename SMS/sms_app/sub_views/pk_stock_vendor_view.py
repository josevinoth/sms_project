from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import JsonResponse
from django.db import transaction

from ..forms import PkstockvendorForm
from ..models import PkstockvebdorInfo,PkstockpurchasesInfo
from ..sub_models.stock_maintenance_mod import StockMaintenance
from django.shortcuts import render, redirect

def _purchase_ref(purchase_entry):
    return purchase_entry.sm_stock_purchase_number or purchase_entry.sm_invoice_no or f"SM-{purchase_entry.id}"


def _sum_abs_stock_counts(queryset):
    return sum(abs(float(qty or 0)) for qty in queryset.values_list('sm_count', flat=True))


def _vendor_returned_qty_for_purchase(purchase_entry):
    return _sum_abs_stock_counts(
        StockMaintenance.objects.filter(
            sm_stock_type_id=3,
            sm_vendor=purchase_entry.sm_vendor,
            sm_stock_purchase_number=_purchase_ref(purchase_entry),
            sm_partcode=purchase_entry.sm_partcode,
        )
    )


def _retrieved_qty_for_purchase(purchase_entry):
    return _sum_abs_stock_counts(
        StockMaintenance.objects.filter(
            sm_stock_type_id=2,
            sm_invoice_no=_purchase_ref(purchase_entry),
            sm_partcode=purchase_entry.sm_partcode,
        )
    )


def _vendor_returnable_qty_for_purchase(purchase_entry):
    original_qty = float(purchase_entry.sm_count or 0)
    returned_qty = _vendor_returned_qty_for_purchase(purchase_entry)
    retrieved_qty = _retrieved_qty_for_purchase(purchase_entry)
    return max(original_qty - returned_qty - retrieved_qty, 0), returned_qty, retrieved_qty

@login_required(login_url='login_page')
def pk_stock_vendor_add(request,stock_vendor_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if stock_vendor_id == 0:
            if 'ses_stock_vendor_id' in request.session:
                del request.session['ses_stock_vendor_id']
            if 'ses_pk_vendor_bill' in request.session:
                del request.session['ses_pk_vendor_bill']
            psv_form = PkstockvendorForm()
            pk_vendor_bill = ''
            stockpurchases_list = PkstockpurchasesInfo.objects.filter(sp_vendor_bill=pk_vendor_bill)
            stockmaintenance_list = []
        else:
            pk_vendor_bill = PkstockvebdorInfo.objects.get(pk=stock_vendor_id).spv_vendor_bill
            pk_vendor_bill_id = PkstockvebdorInfo.objects.get(pk=stock_vendor_id).id
            request.session['ses_pk_vendor_bill'] = pk_vendor_bill
            request.session['ses_stock_vendor_id'] = stock_vendor_id
            pk_stock_vendor = PkstockvebdorInfo.objects.get(pk=stock_vendor_id)
            psv_form = PkstockvendorForm(instance=pk_stock_vendor)
            # pk_vendor_bill = request.session.get('ses_pk_vendor_bill')
            stockpurchases_list = PkstockpurchasesInfo.objects.filter(sp_vendor_bill_id=pk_vendor_bill_id)
            stockmaintenance_list = list(
                StockMaintenance.objects
                .filter(Q(sm_vendor_id=pk_vendor_bill_id) | Q(sm_invoice_no=pk_vendor_bill))
                .order_by('-sm_created_at')
            )
            for item in stockmaintenance_list:
                if item.sm_stock_type_id == 1:
                    item.vendor_returnable_qty, item.vendor_returned_qty, item.vendor_retrieved_qty = _vendor_returnable_qty_for_purchase(item)
                else:
                    item.vendor_returnable_qty = 0
                    item.vendor_returned_qty = 0
                    item.vendor_retrieved_qty = 0
        context={
                'psv_form': psv_form,
                'first_name': first_name,
                'user_id': user_id,
                'stockpurchases_list': stockpurchases_list,
                'stockmaintenance_list': stockmaintenance_list,
        }
        return render(request, "asset_mgt_app/pk_stock_vendor_add.html", context)
    else:
        psv_form = PkstockvendorForm(request.POST)

        if psv_form.is_valid():
            spv_vendor_bill = psv_form.cleaned_data['spv_vendor_bill']
            
            if PkstockvebdorInfo.objects.filter(spv_vendor_bill=spv_vendor_bill).exclude(id=stock_vendor_id).exists():
                messages.error(request, 'Duplicate Found. Please enter a Unique Vendor Bill.')
                return redirect(request.META['HTTP_REFERER'])

            if stock_vendor_id == 0:
                new_place = psv_form.save()
                
                # Auto-link any unlinked StockMaintenance entries that match this new invoice number
                StockMaintenance.objects.filter(sm_invoice_no=new_place.spv_vendor_bill, sm_vendor__isnull=True).update(sm_vendor=new_place)

                messages.success(request, 'Record Saved Successfully')
                url = new_place.get_absolute_url_pk_stock_vendor()
                return redirect(url)
            else:
                pk_stock_vendor = PkstockvebdorInfo.objects.get(pk=stock_vendor_id)
                psv_form = PkstockvendorForm(request.POST, instance=pk_stock_vendor)
                psv_form.save()
                
                # Auto-link any unlinked StockMaintenance entries that match this invoice number
                StockMaintenance.objects.filter(sm_invoice_no=pk_stock_vendor.spv_vendor_bill, sm_vendor__isnull=True).update(sm_vendor=pk_stock_vendor)
                
                print("psv_form saved")
                messages.success(request, 'Record Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("Location psv_form not saved")
            messages.error(request, 'Record Not Saved. Please Enter All Required Fields')
            return redirect(request.META['HTTP_REFERER'])


# List places
@login_required(login_url='login_page')
def pk_stock_vendor_list(request):
    first_name = request.session.get('first_name')
    context = {'pk_stock_vendor_list' : PkstockvebdorInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_stock_vendor_list.html",context)

#Delete places
@login_required(login_url='login_page')
def pk_stock_vendor_delete(request,stock_vendor_id):
    pk_stock_vendor = PkstockvebdorInfo.objects.get(pk=stock_vendor_id)
    pk_stock_vendor.delete()
    return redirect('/SMS/pk_stock_vendor_list')

@login_required(login_url='login_page')
def pk_process_vendor_return(request, sm_id):
    """
    Processes a return directly from the vendor's stock purchases screen.
    It creates a new StockMaintenance entry (type 3 - Return) tied to the same vendor and invoice.
    """
    if request.method == "POST":
        try:
            original_sm = StockMaintenance.objects.get(pk=sm_id)
            return_qty = float(request.POST.get('return_qty', 0))
            return_reason = request.POST.get('return_reason', '').strip()
            
            if return_qty <= 0:
                messages.error(request, "Return quantity must be greater than zero.")
                return redirect('pk_stock_vendor_update', original_sm.sm_vendor_id)
                
            remaining_qty, returned_qty, retrieved_qty = _vendor_returnable_qty_for_purchase(original_sm)
            if remaining_qty <= 0:
                messages.error(request, "This purchase line has no remaining stock available for vendor return.")
                return redirect('pk_stock_vendor_update', original_sm.sm_vendor_id)

            if return_qty > remaining_qty:
                messages.error(request, f"Return quantity ({return_qty}) cannot exceed remaining returnable quantity ({remaining_qty}). Already returned: {returned_qty}. Already issued: {retrieved_qty}.")
                return redirect('pk_stock_vendor_update', original_sm.sm_vendor_id)
                
            # Create the Return Entry
            user_id = request.session.get('ses_userID')
            new_desc = f"Vendor Return: {return_reason}"
            if original_sm.sm_description:
                new_desc += f" (Ref: {original_sm.sm_description})"
                
            # Truncate if too long
            new_desc = new_desc[:255]
            
            original_qty = float(original_sm.sm_count or 0)
            cft_ratio = (return_qty / original_qty) if original_qty else 0
            return_cft = -abs(float(original_sm.sm_total_cft or 0) * cft_ratio)
            return_total_price = -abs(float(original_sm.sm_per_unit_cost or 0) * return_qty)

            return_sm = StockMaintenance.objects.create(
                sm_stock_type_id=3, # Return
                sm_invoice_date=original_sm.sm_invoice_date,
                sm_invoice_no=original_sm.sm_invoice_no,
                sm_stock_purchase_number=_purchase_ref(original_sm),
                sm_vendor=original_sm.sm_vendor,
                sm_partcode=original_sm.sm_partcode,
                sm_description=new_desc,
                sm_thickness=original_sm.sm_thickness,
                sm_width=original_sm.sm_width,
                sm_length=original_sm.sm_length,
                sm_uom=original_sm.sm_uom,
                sm_count=-abs(return_qty),
                sm_cft=-abs(float(original_sm.sm_cft or 0) * cft_ratio),
                sm_total_cft=return_cft,
                sm_per_unit_cost=original_sm.sm_per_unit_cost,
                sm_total_price=return_total_price,
                sm_updated_by_id=user_id
            )
            
            messages.success(request, f"Successfully processed return of {return_qty} for {original_sm.sm_partcode.pc_code if original_sm.sm_partcode else 'item'}.")
            return redirect('pk_stock_vendor_update', original_sm.sm_vendor_id)
            
        except ObjectDoesNotExist:
            messages.error(request, "Original stock entry not found.")
        except Exception as e:
            messages.error(request, f"Error processing return: {str(e)}")
            
    return redirect(request.META.get('HTTP_REFERER', '/SMS/pk_stock_vendor_list/'))


@login_required(login_url='login_page')
def pk_process_vendor_return_all(request, stock_vendor_id):
    """
    Return all remaining physical stock for the selected vendor bill.
    Already-returned and already-issued/retrieved quantities are skipped.
    """
    if request.method != "POST":
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        if request.META.get('HTTP_ACCEPT', '').find('application/json') != -1 or is_ajax:
            return JsonResponse({"error": "POST required"}, status=400)
        messages.error(request, 'Invalid request method for Return All (POST required).')
        return redirect('pk_stock_vendor_update', stock_vendor_id)

    try:
        with transaction.atomic():
            created = []
            skipped = []
            total_returned = 0.0
            user_id = request.session.get('ses_userID')
            purchase_items = StockMaintenance.objects.filter(sm_vendor_id=stock_vendor_id, sm_stock_type_id=1)

            for orig in purchase_items:
                original_qty = float(orig.sm_count or 0)
                remaining, already_returned, retrieved = _vendor_returnable_qty_for_purchase(orig)
                if remaining <= 0:
                    skipped.append({
                        'partcode': orig.sm_partcode.pc_code if orig.sm_partcode else None,
                        'purchase_number': _purchase_ref(orig),
                        'remaining': 0,
                    })
                    continue

                new_desc = f"Vendor Return (Return All) - Ref: {orig.sm_description or ''}"[:255]
                cft_ratio = (remaining / original_qty) if original_qty else 0
                return_cft = -abs(float(orig.sm_total_cft or 0) * cft_ratio)
                return_total_price = -abs(float(orig.sm_per_unit_cost or 0) * remaining)

                return_sm = StockMaintenance.objects.create(
                    sm_stock_type_id=3,
                    sm_invoice_date=orig.sm_invoice_date,
                    sm_invoice_no=orig.sm_invoice_no,
                    sm_stock_purchase_number=_purchase_ref(orig),
                    sm_vendor=orig.sm_vendor,
                    sm_partcode=orig.sm_partcode,
                    sm_description=new_desc,
                    sm_thickness=orig.sm_thickness,
                    sm_width=orig.sm_width,
                    sm_length=orig.sm_length,
                    sm_uom=orig.sm_uom,
                    sm_count=-abs(remaining),
                    sm_cft=-abs(float(orig.sm_cft or 0) * cft_ratio),
                    sm_total_cft=return_cft,
                    sm_per_unit_cost=orig.sm_per_unit_cost,
                    sm_total_price=return_total_price,
                    sm_updated_by_id=user_id,
                )

                created.append({
                    'partcode': orig.sm_partcode.pc_code if orig.sm_partcode else None,
                    'purchase_number': _purchase_ref(orig),
                    'qty_returned': remaining,
                    'return_id': return_sm.id,
                })
                total_returned += remaining

        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        wants_json = (request.META.get('HTTP_ACCEPT', '').find('application/json') != -1) or is_ajax
        if wants_json:
            return JsonResponse({
                'status': 'ok',
                'created': created,
                'skipped': skipped,
                'count_created': len(created),
                'total_returned': total_returned,
            })

        if created:
            messages.success(request, f"Return All: created {len(created)} return entries (total qty {total_returned}).")
        else:
            messages.info(request, "Return All: no items were eligible for return.")
        return redirect('pk_stock_vendor_update', stock_vendor_id)

    except Exception as e:
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
        if request.META.get('HTTP_ACCEPT', '').find('application/json') != -1 or is_ajax:
            return JsonResponse({'error': str(e)}, status=500)
        messages.error(request, f"Error processing Return All: {str(e)}")
        return redirect('pk_stock_vendor_update', stock_vendor_id)
