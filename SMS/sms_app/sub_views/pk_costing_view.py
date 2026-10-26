import json
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity
from django.db import transaction
from django.db.models import Sum, Q, F

from ..forms import ModifyDimensionsForm,CostingSearchForm,PkcostingForm
from ..models import POdimension,Nadimension,pk_itemdescriptionInfo,PkstockpurchasesInfo,PkcostingsummaryInfo,Stockdescription,PkcostingInfo,Costtype,Pkstocktype,pk_itemInfo,PkpartcodeInfo,Pkwooddescription,pk_stock_statusinfo
from ..sub_models.stock_maintenance_mod import StockMaintenance
# from ..sub_models.stocktype_maintenance_mod import Stock_type_maintenance
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from .general_utils import get_branch_code, get_session_branch_id, get_financial_year

def _stock_entry_ref(stock_entry):
    return stock_entry.sm_stock_purchase_number or stock_entry.sm_invoice_no or f"SM-{stock_entry.id}"


def _sum_abs_stock_counts(queryset):
    return sum(abs(float(qty or 0)) for qty in queryset.values_list('sm_count', flat=True))


def _retrieved_qty_for_stock_entry(stock_entry):
    return _sum_abs_stock_counts(
        StockMaintenance.objects.filter(
            sm_stock_type_id=2,
            sm_invoice_no=_stock_entry_ref(stock_entry),
            sm_partcode=stock_entry.sm_partcode,
        )
    )


def _vendor_returned_qty_for_stock_entry(stock_entry):
    if not stock_entry.sm_vendor_id:
        return 0.0
    return _sum_abs_stock_counts(
        StockMaintenance.objects.filter(
            sm_stock_type_id=3,
            sm_vendor=stock_entry.sm_vendor,
            sm_stock_purchase_number=_stock_entry_ref(stock_entry),
            sm_partcode=stock_entry.sm_partcode,
        )
    )


def _available_qty_for_stock_entry(stock_entry):
    original_qty = float(stock_entry.sm_count or 0.0)
    retrieved_qty = _retrieved_qty_for_stock_entry(stock_entry)
    vendor_returned_qty = _vendor_returned_qty_for_stock_entry(stock_entry)
    return max(0.0, original_qty - retrieved_qty - vendor_returned_qty)


@transaction.atomic
@login_required(login_url='login_page')
def costing_add(request, costing_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    na_assessment_num_id = request.session.get('na_assessment_id')
    na_customer_name_id = request.session.get('na_customer_name_id')
    na_customer_new_name_id = request.session.get('na_customer_new_name')
    ses_customer_po_id = request.session.get('ses_customer_po_id')
    print('ses_customer_po_id', ses_customer_po_id)

    if request.method == "GET":
        if costing_id == 0:
            print("Inside PK quotation GET add")

            # # Fetch session data with a default value
            # ct_cost_type_id = request.session.get('last_cs_cost_type', None)
            # ct_job_type_id = request.session.get('last_cs_job_type', None)
            # ct_job_type_quant_id = request.session.get('last_cs_job_type_quantity', None)
            # ct_stock_type_id = request.session.get('last_cs_stock_type_quantity', None)
            # ct_stock_description_id = request.session.get('last_cs_stock_desc_quantity', None)
            # ct_item_type_id = request.session.get('last_cs_item_type', None)
            # ct_item_description_id = request.session.get('last_cs_item_desc', None)
            #
            # # Retrieve objects safely
            # initial_data = {
            #     'ct_cost_type': Costtype.objects.filter(id=ct_cost_type_id).first(),
            #     'ct_requirement': Nadimension.objects.filter(id=ct_job_type_id).first() if ct_job_type_id else None,
            #     'ct_na_quantity': ct_job_type_quant_id,
            #     'ct_stock_type': Pkstocktype.objects.filter(id=ct_stock_type_id).first() if ct_stock_type_id else None,
            #     'ct_stock_description':  Stockdescription.objects.filter(id=ct_stock_description_id).first() if ct_stock_description_id else None,
            #     'ct_item': pk_itemInfo.objects.filter(id=ct_item_type_id).first() if ct_item_type_id else None,
            #     'ct_itemdescription': pk_itemdescriptionInfo.objects.filter(id=ct_item_description_id).first() if ct_item_description_id else None,
            # }
            #
            # print("Initial Data:", initial_data)

            form = PkcostingForm(
                assessment_id=na_assessment_num_id,
                initial={'ct_customer_po': ses_customer_po_id}
            )
        else:
            costing = get_object_or_404(PkcostingInfo, pk=costing_id)
            form = PkcostingForm(instance=costing)

        # Build job list and current job no explicitly for debugging and clarity
        job_no_list_qs = list(PkcostingsummaryInfo.objects.filter(cs_assessment_num=na_assessment_num_id, cs_customer_po=ses_customer_po_id).values_list('cs_job_no', flat=True).distinct())
        # Fallback: if no jobs found for assessment+PO, try by assessment only
        if not job_no_list_qs and na_assessment_num_id:
            job_no_list_qs = list(PkcostingsummaryInfo.objects.filter(cs_assessment_num=na_assessment_num_id).values_list('cs_job_no', flat=True).distinct())
        current_job_no_val = None
        ses_cs_id = request.session.get('ses_costing_summary_id')
        if ses_cs_id:
            current_job_no_val = PkcostingsummaryInfo.objects.filter(id=ses_cs_id).values_list('cs_job_no', flat=True).first()
        # If still not available, pick the first job from the job list if present
        if not current_job_no_val and job_no_list_qs:
            current_job_no_val = job_no_list_qs[0]

        # Debug prints to understand why job list may be empty
        print('DEBUG: na_assessment_num_id=', na_assessment_num_id, 'ses_customer_po_id=', ses_customer_po_id, 'ses_costing_summary_id=', request.session.get('ses_costing_summary_id'))
        print('DEBUG: job_no_list_qs=', job_no_list_qs)

        # Calculate total wood CFT per requirement for the current job number (Wood: 1, 5; excluding reused wood weight in Kg)
        job_cft_qs = PkcostingInfo.objects.filter(
            ct_job_no=current_job_no_val,
            ct_cost_type=8,
            ct_stock_type__in=[1, 5]
        ).exclude(
            ct_part_code__pc_code__icontains='RE'
        ).exclude(
            ct_stock_description__stock_description__icontains='RE - Used'
        ).exclude(
            ct_stock_description__stock_description__icontains='RE-Used'
        ).exclude(
            ct_stock_description__stock_description__icontains='Reused'
        ).values('ct_requirement').annotate(
            total=Sum(F('ct_sqrt_req') * F('ct_na_quantity'))
        )
        job_cft_map = {}
        for j in job_cft_qs:
            if j['ct_requirement']:
                job_cft_map[str(j['ct_requirement'])] = round(j['total'] or 0.0, 3)
        job_cft_map_json = json.dumps(job_cft_map)

        # Dynamic total CFT for the current job/assessment
        aggregate_cft = PkcostingInfo.objects.filter(
            ct_job_no=current_job_no_val,
            ct_cost_type=8,
            ct_stock_type__in=[1, 5]
        ).exclude(
            ct_part_code__pc_code__icontains='RE'
        ).exclude(
            ct_stock_description__stock_description__icontains='RE - Used'
        ).exclude(
            ct_stock_description__stock_description__icontains='RE-Used'
        ).exclude(
            ct_stock_description__stock_description__icontains='Reused'
        ).aggregate(total=Sum(F('ct_sqrt_req') * F('ct_na_quantity')))['total']
        total_cft_display_val = round(aggregate_cft, 3) if aggregate_cft is not None else 0.0

        context = {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'na_assessment_num_id': na_assessment_num_id,
            'na_customer_name_id': na_customer_name_id,
            'na_customer_new_name_id': na_customer_new_name_id,
            'ses_customer_po_id': ses_customer_po_id,
            'costing_list': PkcostingInfo.objects.filter(
                ct_job_no=current_job_no_val
            ).order_by('-id'),
            'excess_costing_list': PkcostingInfo.objects.all(),
            'total_cft_display': total_cft_display_val,
            'job_cft_map_json': job_cft_map_json,
            'job_no_list': job_no_list_qs,
            # Preserve user's selected job number (if any) so the manual select keeps the choice on error
            'current_job_no': current_job_no_val
        }
        return render(request, "asset_mgt_app/pk_costing_add.html", context)

    else:
        print('POST data:', dict(request.POST))
        if costing_id == 0:
            print("Inside PK Costing post add")
            form = PkcostingForm(request.POST,assessment_id=request.POST.get('ct_assessment_num'))
        else:
            costing = get_object_or_404(PkcostingInfo, pk=costing_id)
            form = PkcostingForm(
                request.POST,
                instance=costing,
                assessment_id=request.POST.get('ct_assessment_num')
            )
        if form.is_valid():
            print('Form is valid')
            
            # --- BACKEND OVERRIDE FOR TOTAL COST ---
            # To ensure the total cost is always correctly calculated regardless of JS calculation errors
            costing_temp = form.save(commit=False)
            qty = float(costing_temp.ct_na_quantity or 0)

            # Be defensive: ct_cost_type may be missing or empty (e.g. placeholder). Default to 0.
            cost_type_raw = request.POST.get('ct_cost_type') or '0'
            try:
                cost_type_id = int(cost_type_raw)
            except (ValueError, TypeError):
                cost_type_id = 0

            if cost_type_id in [3, 9]:  # Labour Cost (In-house / On-site)
                rate = float(costing_temp.ct_rate or 0)
                days = float(costing_temp.ct_days or 1)
                qty_req = float(costing_temp.ct_quantity_req or 1)
                unit_cost = rate * days * qty_req
                form.instance.ct_total_cost = round(unit_cost, 2)
                form.instance.ct_totalbox_cost = round(unit_cost * qty, 2)
            elif cost_type_id == 5:  # HT Cost
                rate = float(costing_temp.ct_rate or 0)
                unit_cft = float(costing_temp.ct_sqrt_req or 0)
                unit_cost = rate * unit_cft
                form.instance.ct_total_cost = round(unit_cost, 2)
                form.instance.ct_totalbox_cost = round(unit_cost * qty, 2)
            elif cost_type_id == 8:  # Packing Material Cost
                part_code_obj = costing_temp.ct_part_code
                pc_code_val = (part_code_obj.pc_code if part_code_obj and part_code_obj.pc_code else '').upper()
                desc_val = str(costing_temp.ct_stock_description or '').upper()
                is_reused = ('RE' in pc_code_val) or ('RE - USED' in desc_val) or ('RE-USED' in desc_val) or ('REUSED' in desc_val)

                rate = float(costing_temp.ct_rate or 0)
                q_req = float(costing_temp.ct_quantity_req or 0)

                if is_reused:
                    unit_cost = round(rate * q_req, 2)
                    form.instance.ct_sqrt_req = round(q_req, 3)
                    form.instance.ct_cft = 0.0
                    form.instance.ct_total_cost = unit_cost
                    form.instance.ct_totalbox_cost = round(unit_cost * qty, 2)
                else:
                    unit_cost = float(costing_temp.ct_total_cost or 0)
                    # If unit_cost came in as 0 or <= 0, recalculate from dimensions & rate
                    if unit_cost <= 0:
                        stock_type_raw = request.POST.get('ct_stock_type') or (costing_temp.ct_stock_type.id if costing_temp.ct_stock_type else 0)
                        try:
                            st_id = int(stock_type_raw)
                        except (ValueError, TypeError):
                            st_id = 0
                        if st_id in [1, 5]:  # Wood
                            l = float(costing_temp.ct_length_req or 0)
                            w = float(costing_temp.ct_width_req or 0)
                            h = float(costing_temp.ct_height_req or 0)
                            cft_unit = (l * w * h / 144) * (q_req if q_req else 1)
                            unit_cost = round(rate * cft_unit, 2)
                            form.instance.ct_sqrt_req = round(cft_unit, 3)
                        elif st_id in [4, 6]:  # Plywood
                            l = float(costing_temp.ct_length_req or 0)
                            w = float(costing_temp.ct_width_req or 0)
                            sqft_unit = ((l * w) / 144.0) * (q_req if q_req else 1)
                            unit_cost = round(rate * sqft_unit, 2)
                            form.instance.ct_sqrt_req = round(sqft_unit, 3)
                        else:
                            unit_cost = round(rate * q_req, 2)
                    form.instance.ct_total_cost = round(unit_cost, 2)
                    form.instance.ct_totalbox_cost = round(unit_cost * qty, 2)
            else:
                unit_cost = float(costing_temp.ct_total_cost or 0)
                form.instance.ct_totalbox_cost = round(unit_cost * qty, 2)
            # ---------------------------------------

            if cost_type_id == 8:  # For stock-related cost types
                stock_purchase_num_id = request.POST.get('ct_stock_purchase_number')
                print('stock_purchase_num_id',stock_purchase_num_id)
                if stock_purchase_num_id:
                        try:
                            # Fetch stock purchase record from StockMaintenance (not PkstockpurchasesInfo)
                            stock_purchase = StockMaintenance.objects.get(id=stock_purchase_num_id)
                            stock_purchase_num = stock_purchase.sm_stock_purchase_number or stock_purchase.sm_invoice_no or f"SM-{stock_purchase_num_id}"
                            stock_qty_available = _available_qty_for_stock_entry(stock_purchase)

                            # Validate quantity
                            stock_qty_str = request.POST.get('ct_quantity', None)
                            if not stock_qty_str:
                                messages.error(request, 'Quantity is required.')
                                return redirect(request.META.get('HTTP_REFERER', '/'))

                            try:
                                stock_qty = float(stock_qty_str)
                            except ValueError:
                                messages.error(request, 'Invalid quantity value. It should be a number.')
                                return redirect(request.META.get('HTTP_REFERER', '/'))

                            if stock_qty > stock_qty_available:
                                messages.error(request, f'Available quantity is less than requested quantity. Available: {stock_qty_available}.')
                                return redirect(request.META.get('HTTP_REFERER', '/'))

                            # Save the record - ensure we don't lose the stock reference
                            costing = form.save(commit=False)
                            if stock_purchase_num_id:
                                costing.ct_stock_purchase_number_id = stock_purchase_num_id
                            costing.save()
                            form.save_m2m()
                            # Extract relevant fields
                            cost_type = costing.ct_cost_type.id
                            stock_type = costing.ct_stock_type.id
                            assessment_id = costing.ct_assessment_num.id

                            if cost_type == 8 and stock_type in [1, 5]:
                                total_cft = PkcostingInfo.objects.filter(
                                    ct_assessment_num=assessment_id,
                                    ct_cost_type=8,
                                    ct_stock_type__in=[1, 5]
                                ).aggregate(total=Sum(F('ct_sqrt_req') * F('ct_na_quantity')))['total'] or 0.0
                                print("total_cft", total_cft)
                                request.session['ct_total_cft_display'] = round(total_cft, 2)
                            else:
                                request.session['ct_total_cft_display'] = 0.0

                            if costing.ct_stock_status.id in [2, 4]:
                                try:
                                    # User request: original GRN number should be in the 'sm_invoice_no' field for retrievals.
                                    # No more 'RET-' prefix.
                                    ref_no = stock_purchase_num
                                    if not StockMaintenance.objects.filter(sm_stock_type_id=2, sm_invoice_no=ref_no, sm_description__endswith=f"(Costing ID: {costing.id})").exists():
                                        StockMaintenance.objects.create(
                                            sm_stock_type_id=2, # Retrieval
                                            sm_invoice_date=datetime.now().date(),
                                            sm_invoice_no=ref_no, # Standardizing: Putting original GRN here
                                            sm_description=f"Retrieved via Costing for Assessment {costing.ct_assessment_num.na_assessment_num if costing.ct_assessment_num else 'N/A'} (Costing ID: {costing.id})",
                                            sm_partcode=stock_purchase.sm_partcode,
                                            sm_count=float(costing.ct_quantity or stock_qty),
                                            sm_uom=stock_purchase.sm_uom,
                                            sm_updated_by_id=user_id
                                        )
                                    # Note: We NO LONGER subtract from stock_purchase.sm_count here
                                    # because the balance is aggregated as (Total In - Retrieved).
                                except Exception as e:
                                    print(f"Error creating retrieval record from costing: {e}")

                            messages.success(request, 'Record Saved Successfully')
                        except StockMaintenance.DoesNotExist:
                            messages.error(request, f'Stock batch with ID {stock_purchase_num_id} not found.')
                            print(f"Stock batch with ID {stock_purchase_num_id} not found.")

                else:
                    # GATE CLOSED: Stock costing (cost_type=8) MUST have a GRN selected.
                    # Without a GRN, the record will appear as a dead/orphan entry in the Retrieval list.
                    messages.error(request, 'Please select a Stock / GRN before saving a stock costing entry.')
                    return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                # If cost type is not stock-related, save the record
                form.save()
                messages.success(request, 'Record Saved Successfully')

                # Store values in session after saving
            # request.session['last_cs_cost_type'] = form.cleaned_data.get('ct_cost_type').id if form.cleaned_data.get('ct_cost_type') else None
            # request.session['last_cs_job_type'] = form.cleaned_data.get('ct_requirement').id if form.cleaned_data.get('ct_requirement') else None
            # request.session['last_cs_job_type_quantity'] = form.cleaned_data.get('ct_na_quantity') if form.cleaned_data.get('ct_na_quantity') else None
            # request.session['last_cs_stock_type_quantity'] = form.cleaned_data.get('ct_stock_type').id if form.cleaned_data.get('ct_stock_type') else None
            # request.session['last_cs_stock_desc_quantity'] = form.cleaned_data.get('ct_stock_description').id if form.cleaned_data.get('ct_stock_description') else None
            # request.session['last_cs_item_type'] = form.cleaned_data.get('ct_item').id if form.cleaned_data.get('ct_item') else None
            # request.session['last_cs_item_desc'] = form.cleaned_data.get('ct_itemdescription').id if form.cleaned_data.get('ct_itemdescription') else None


            return redirect('/SMS/costing_insert/')

        else:
            print("Costing form is not valid.")
            messages.error(request, 'Record Not Updated Successfully')

            # Display form errors in server logs and flash messages
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")
                    messages.error(request, f"Error in {field}: {error}")

            # Rebuild job list and current value for rendering with errors
            job_no_list_qs = list(PkcostingsummaryInfo.objects.filter(cs_assessment_num=na_assessment_num_id, cs_customer_po=ses_customer_po_id).values_list('cs_job_no', flat=True).distinct())
            if not job_no_list_qs and na_assessment_num_id:
                job_no_list_qs = list(PkcostingsummaryInfo.objects.filter(cs_assessment_num=na_assessment_num_id).values_list('cs_job_no', flat=True).distinct())
            current_job_no_val = request.POST.get('ct_job_no') or None
            if not current_job_no_val:
                ses_cs_id = request.session.get('ses_costing_summary_id')
                if ses_cs_id:
                    current_job_no_val = PkcostingsummaryInfo.objects.filter(id=ses_cs_id).values_list('cs_job_no', flat=True).first()
            if not current_job_no_val and job_no_list_qs:
                current_job_no_val = job_no_list_qs[0]
            print('DEBUG (POST error render): na_assessment_num_id=', na_assessment_num_id, 'ses_customer_po_id=', ses_customer_po_id)
            print('DEBUG (POST error render): job_no_list_qs=', job_no_list_qs, 'current_job_no_val=', current_job_no_val)

            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'na_assessment_num_id': na_assessment_num_id,
                'na_customer_name_id': na_customer_name_id,
                'na_customer_new_name_id': na_customer_new_name_id,
                'ses_customer_po_id': ses_customer_po_id,
                'costing_list': PkcostingInfo.objects.filter(
                    ct_assessment_num=na_assessment_num_id,
                    ct_customer_po=ses_customer_po_id,
                    ct_job_no=current_job_no_val
                ).order_by('-id'),
                'excess_costing_list': PkcostingInfo.objects.all(),
                'total_cft_display': request.session.get('ct_total_cft_display', 0),
                'job_no_list': job_no_list_qs,
                'current_job_no': current_job_no_val
            }

            return render(request, "asset_mgt_app/pk_costing_add.html", context)
        # End of POST handling - everything either redirected or rendered above


@login_required(login_url='login_page')
def pk_return_excess_to_stock(request, costing_id):
    costing = get_object_or_404(PkcostingInfo, pk=costing_id)
    user_id = request.session.get('ses_userID')

    if costing.ct_excess_status and costing.ct_excess_status.id == 3:  # Excess
        # Create Return Record in StockMaintenance
        # Ensure dimensions and part code are preserved for accurate inventory
        sm_return = StockMaintenance.objects.create(
            sm_stock_type_id=3,  # Return
            sm_partcode=costing.ct_part_code,
            sm_thickness=costing.ct_exe_height_req or 0,
            sm_width=costing.ct_exe_width_req or 0,
            sm_length=costing.ct_exe_length_req or 0,
            sm_invoice_date=datetime.now().date(),
            sm_invoice_no=str(costing.ct_assessment_num.na_assessment_num) if costing.ct_assessment_num else "",
            sm_description=f"Excess Return from Assessment {costing.ct_assessment_num.na_assessment_num if costing.ct_assessment_num else 'N/A'}",
            sm_count=costing.ct_exe_quantity_req or 0,
            sm_total_cft=costing.ct_exe_sqrt_req or 0,
            sm_per_unit_cost=costing.ct_rate or 0,
            sm_total_price=0,
            sm_updated_by_id=user_id
        )
        # Auto-generate branch-specific GRN number for return
        fy = get_financial_year()
        branch_id = get_session_branch_id(request)
        branch_code = get_branch_code(branch_id)
        sm_return.sm_stock_purchase_number = f"GRN/{branch_code}/{fy}/{sm_return.id}"
        sm_return.save(update_fields=['sm_stock_purchase_number'])
        # Update status to Returned (assuming 5 is Returned or similar)
        # For now, let's keep it 5 but maybe add a message
        messages.success(request, f'Excess stock of {costing.ct_exe_quantity_req} returned to ledger.')

    return redirect(request.META.get('HTTP_REFERER', '/'))


def update_reduced_dimensions(stock_purchase_num,last_id):
    requested_qty = PkcostingInfo.objects.get(pk=last_id).ct_quantity_req
    requested_overall_qty = PkcostingInfo.objects.get(pk=last_id).ct_na_quantity
    requested_cft = PkcostingInfo.objects.get(pk=last_id).ct_sqrt_req
    prev_qty = PkstockpurchasesInfo.objects.get(sp_purchase_num=stock_purchase_num).sp_quantity
    prev_cft = PkstockpurchasesInfo.objects.get(sp_purchase_num=stock_purchase_num).sp_cft
    current_qty = prev_qty - (requested_qty * requested_overall_qty)
    current_cft = prev_cft - (requested_cft * requested_overall_qty)
    PkstockpurchasesInfo.objects.filter(sp_purchase_num=stock_purchase_num).update(sp_quantity=current_qty)
    PkstockpurchasesInfo.objects.filter(sp_purchase_num=stock_purchase_num).update(sp_cft=round(current_cft,2))



# List costing
@login_required(login_url='login_page')
def costing_list(request):
    first_name = request.session.get('first_name')
    context = {'costing_list' : PkcostingInfo.objects.all().order_by('-id'),
                           'excess_costing_list': PkcostingInfo.objects.filter(ct_stock_status=4),
'first_name': first_name}
    return render(request,"asset_mgt_app/pk_costing_list.html",context)

#Delete costing
@login_required(login_url='login_page')
def costing_delete(request,costing_id):
    costing = PkcostingInfo.objects.get(pk=costing_id)
    stock_purchase_num = PkcostingInfo.objects.get(pk=costing_id).ct_stock_purchase_number
    cost_type_id = PkcostingInfo.objects.get(pk=costing_id).ct_cost_type.id
    if cost_type_id == 8:
        # Clean up both Retrieval (Type 2) and Return (Type 3) records linked to this costing ID
        StockMaintenance.objects.filter(sm_stock_type_id__in=[2, 3], sm_description__contains=f"(Costing ID: {costing_id})").delete()
    costing.delete()
    print("Successfully Deleted")
    # return redirect('/SMS/costing_list')
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def load_stock_description(request):
    stock_type = request.GET.get('stock_type')
    stock_description = []
    stock_description_id = []
    if stock_type:
        seen = set()
        qs = Stockdescription.objects.filter(stock_type=stock_type).order_by('stock_description').values('id', 'stock_description')
        for item in qs:
            desc = item['stock_description']
            if desc and desc not in seen:
                seen.add(desc)
                stock_description.append(desc)
                stock_description_id.append(item['id'])
    data = {
        'stock_description': stock_description,
        'stock_description_id': stock_description_id,
    }
    return HttpResponse(json.dumps(data), content_type='application/json')
@login_required(login_url='login_page')
def load_pk_wood_description(request):
    stock_type = request.GET.get('stock_type')
    if stock_type == '0' or stock_type == '':
        pk_wood_description_objs = Pkwooddescription.objects.none()
    else:
        # Include records with matching type OR where type is NULL
        pk_wood_description_objs = Pkwooddescription.objects.filter(Q(pk_wood_type_id=stock_type) | Q(pk_wood_type_id__isnull=True)).order_by('pk_wood_description')

    wood_description = []
    wood_description_id = []
    for i in pk_wood_description_objs:
        wood_description.append(i.pk_wood_description)
        wood_description_id.append(i.id)

    data = {
        'stock_description': wood_description,
        'stock_description_id': wood_description_id,
    }
    return HttpResponse(json.dumps(data))

@login_required(login_url='login_page')
def costing_cancel(request):
    assessment_num_val = request.session.get('na_assessment_id')
    # costing_summary_id=PkcostingsummaryInfo.objects.get(cs_assessment_num=assessment_num_val).id
    costing_summary_id = request.session.get('ses_costing_summary_id')
    return redirect('/SMS/costingsummary_update/' + str(costing_summary_id))

@login_required(login_url='login_page')
def pk_item_search_page_costing(request):
    from django.db.models import Sum, Case, When, FloatField, Avg
    from django.contrib.postgres.search import TrigramSimilarity

    part_code = request.GET.get('part_code')
    stock_type = request.GET.get('stock_type')
    stock_description = request.GET.get('stock_description')
    length_req = request.GET.get('length_req')
    width_req = request.GET.get('width_req')
    height_req = request.GET.get('height_req')

    parts = PkpartcodeInfo.objects.all()
    if part_code:
        if part_code.isdigit():
            parts = parts.filter(id=int(part_code))
        else:
            parts = parts.filter(pc_code__icontains=part_code)

    if stock_type and stock_type != '0':
        parts = parts.filter(pc_stock_type_id=stock_type)
    if stock_description and stock_description != '0':
        parts = parts.filter(pc_stock_description_id=stock_description)

    p_ids = list(parts.values_list('id', flat=True))

    if not p_ids and part_code and not part_code.isdigit():
        p_ids = list(PkpartcodeInfo.objects.annotate(
            similarity=TrigramSimilarity('pc_code', part_code)
        ).filter(similarity__gt=0.3).order_by('-similarity').values_list('id', flat=True)[:5])

    # 2. Calculate FIFO stock batches for all matching parts
    formatted_results = []
    if p_ids:
        parts_dict = {
            p.id: p
            for p in PkpartcodeInfo.objects.filter(id__in=p_ids).select_related(
                'pc_stock_description', 'pc_stock_type', 'pc_uom'
            )
        }

        # Bulk fetch retrieved quantities (Stock Type 2)
        retrieved_qs = (
            StockMaintenance.objects.filter(
                sm_partcode_id__in=p_ids,
                sm_stock_type_id=2
            ).values('sm_partcode_id', 'sm_invoice_no').annotate(total=Sum('sm_count'))
        )
        retrieved_map = {
            (r['sm_partcode_id'], r['sm_invoice_no']): abs(float(r['total'] or 0.0))
            for r in retrieved_qs
        }

        # Bulk fetch vendor returned quantities (Stock Type 3)
        returned_qs = (
            StockMaintenance.objects.filter(
                sm_partcode_id__in=p_ids,
                sm_stock_type_id=3,
                sm_vendor__isnull=False
            ).values('sm_partcode_id', 'sm_stock_purchase_number', 'sm_vendor_id').annotate(total=Sum('sm_count'))
        )
        returned_map = {
            (r['sm_partcode_id'], r['sm_stock_purchase_number'], r['sm_vendor_id']): abs(float(r['total'] or 0.0))
            for r in returned_qs
        }

        in_batches = (
            StockMaintenance.objects
            .filter(sm_partcode_id__in=p_ids)
            .filter(Q(sm_stock_type_id=1) | Q(sm_stock_type_id=3, sm_count__gt=0))
            .exclude(sm_stock_type_id=3, sm_vendor__isnull=False, sm_description__startswith='Vendor Return')
            .order_by('sm_invoice_date', 'id')
        )

        for batch in in_batches:
            p = parts_dict.get(batch.sm_partcode_id)
            if not p:
                continue

            ref = _stock_entry_ref(batch)
            retrieved_qty = retrieved_map.get((batch.sm_partcode_id, ref), 0.0)
            vendor_returned_qty = (
                returned_map.get((batch.sm_partcode_id, ref, batch.sm_vendor_id), 0.0)
                if batch.sm_vendor_id else 0.0
            )

            original_qty = float(batch.sm_count or 0.0)
            available_qty = max(0.0, original_qty - retrieved_qty - vendor_returned_qty)

            if available_qty > 0:
                batch_cft = batch.sm_total_cft or 0.0
                available_ratio = (available_qty / original_qty) if original_qty else 0.0
                available_cft = float(batch_cft or 0.0) * available_ratio

                formatted_results.append({
                    'id': batch.id,
                    'partcode_id': p.id,
                    'sp_vendor_bill_id': batch.sm_invoice_no,
                    'sp_stock_in_date': batch.sm_invoice_date.strftime('%d-%m-%Y') if batch.sm_invoice_date else '',
                    'sp_purchase_num': batch.sm_stock_purchase_number or batch.sm_invoice_no,
                    'sp_part_code__pc_code': p.pc_code,
                    'sp_stock_type__pk_stocktype': p.pc_stock_type.pk_stocktype if p.pc_stock_type else '',
                    'sp_stock_description__stock_description': p.pc_stock_description.stock_description if p.pc_stock_description else '',
                    'sp_thick_height': batch.sm_thickness,
                    'sp_width': batch.sm_width,
                    'sp_length': batch.sm_length,
                    'sp_cft': round(max(0, available_cft), 4),
                    'sp_quantity': round(max(0, available_qty), 2),
                    'sp_rate': round(batch.sm_per_unit_cost or 0.0, 2),
                    'sp_uom__unit_of_measure': p.pc_uom.unit_of_measure if p.pc_uom else '',
                    'sp_size': f"{batch.sm_thickness}x{batch.sm_width}x{batch.sm_length}"
                })

    return JsonResponse(formatted_results, safe=False)
@login_required(login_url='login_page')
def pk_item_search_page(request):
    form = CostingSearchForm(request.GET)
    results = []
    if form.is_valid():
        stock_description = form.cleaned_data.get('stock_description')
        stock_type = form.cleaned_data.get('stock_type')
        queryset = PkstockpurchasesInfo.objects.all()
        if stock_description:
            queryset = queryset.filter(sp_stock_description=stock_description)
        if stock_type:
            queryset = queryset.filter(sp_stock_type=stock_type)
        results = queryset
    return render(request, 'asset_mgt_app/pk_item_search_page.html', {'form': form, 'results': results})

@login_required(login_url='login_page')
def modify_dimensions_view(request):
    results = PkstockpurchasesInfo.objects.all()
    if request.method == 'POST':
        form = ModifyDimensionsForm(request.POST)
        if form.is_valid():
            selected_row_id = request.POST.get('selected_row')
            modified_thick_height = form.cleaned_data['modified_thick_height']
            modified_width = form.cleaned_data['modified_width']
            modified_length = form.cleaned_data['modified_length']

            # Get the selected row
            selected_row = PkstockpurchasesInfo.objects.get(id=selected_row_id)

            # Modify dimensions
            selected_row.sp_thick_height -= modified_thick_height
            selected_row.sp_width -= modified_width
            selected_row.sp_length -= modified_length

            # Save the modified row
            selected_row.save()

            # return redirect('your_redirect_view_name')
            return redirect(request.META['HTTP_REFERER'])
    else:
        form = ModifyDimensionsForm()

    return render(request, 'asset_mgt_app/pk_item_search_page_select.html', {'form': form, 'results': results})

@login_required(login_url='login_page')
def pk_get_item_description(request):
    item_description_id = []
    item_description_val = []
    item_id = request.GET.get('item_id')
    print('item_id',item_id)
    # Fetch item_description Details
    item_descriptions = pk_itemdescriptionInfo.objects.filter(id_item_name=int(item_id)).order_by('id_item_description')
    # Extract id and id_item_description attributes from queryset
    for item in item_descriptions:
        item_description_id.append(item.id)
        item_description_val.append(item.id_item_description)
    # Create JSON response data
    data = {
        'item_description_val': item_description_val,
        'item_description_id': item_description_id,
    }

    # Return JSON response
    return JsonResponse(data)

@login_required(login_url='login_page')
def pk_get_po_requirement_type(request):
    ct_assessment_num_id = request.GET.get('ct_assessment_num_id')
    ct_customer_po_id = request.GET.get('ct_customer_po_id')
    job_no = request.GET.get('job_no')

    filter_q = Q()
    if ct_assessment_num_id:
        if str(ct_assessment_num_id).isdigit():
            filter_q &= Q(pod_assess_num_id=ct_assessment_num_id)
        else:
            filter_q &= Q(pod_assess_num__na_assessment_num=ct_assessment_num_id)

    if ct_customer_po_id:
        po_str = str(ct_customer_po_id)
        if po_str.isdigit() and len(po_str) < 8:
            filter_q &= (Q(pod_po_num_id=ct_customer_po_id) | Q(pod_po_num__po_num=ct_customer_po_id))
        else:
            filter_q &= Q(pod_po_num__po_num=ct_customer_po_id)

    po_dimensions = POdimension.objects.filter(filter_q).select_related('pod_nad', 'pod_type_of_req')

    # If job_no is provided, narrow down to items used in that specific job
    if job_no:
        used_nad_ids = list(PkcostingInfo.objects.filter(ct_job_no=job_no).values_list('ct_requirement_id', flat=True).distinct())
        if used_nad_ids:
            po_dimensions = po_dimensions.filter(pod_nad_id__in=used_nad_ids)

    po_requirement_type_id = []
    po_requirement_type_val = []
    po_dimension_id = []

    for dimension in po_dimensions:
        nad_id = dimension.pod_nad.id if dimension.pod_nad else dimension.id
        po_requirement_type_id.append(nad_id)
        type_str = str(dimension.pod_type_of_req) if dimension.pod_type_of_req else ""
        po_requirement_type_val.append(f"{dimension.pod_item} ({type_str} {dimension.pod_length}x{dimension.pod_width}x{dimension.pod_height})")
        po_dimension_id.append(dimension.id)

    data = {
        'po_requirement_type_val': po_requirement_type_val,
        'po_requirement_type_id': po_requirement_type_id,
        'po_dimension_id': po_dimension_id,
    }
    return JsonResponse(data)

@login_required(login_url='login_page')
def pk_store_po_dimension_id(request):
    ct_requirement_id = request.GET.get('ct_requirement_id')
    ct_customer_po = request.GET.get('ct_customer_po')
    job_no = request.GET.get('job_no')
    
    # Validation: Return empty response if required parameters are missing
    if not ct_requirement_id or not ct_customer_po:
        return JsonResponse({'error': 'Missing parameters'}, status=200)

    b = None
    try:
        b = POdimension.objects.select_related('pod_nad', 'pod_type_of_req', 'pod_uom').get(id=ct_requirement_id)
    except (POdimension.DoesNotExist, ValueError):
        pass

    if not b:
        # Fallback if ct_requirement_id is the Nadimension ID instead of POdimension ID
        po_str = str(ct_customer_po)
        po_filter = Q(pod_po_num__po_num=po_str)
        if po_str.isdigit() and len(po_str) < 8:
            po_filter |= Q(pod_po_num_id=po_str)
        b = POdimension.objects.filter(
            Q(pod_nad_id=ct_requirement_id) & po_filter
        ).select_related('pod_nad', 'pod_type_of_req', 'pod_uom').order_by('-id').first()

    if not b:
        return JsonResponse({'error': 'Not found'}, status=200)

    # pod_quantity for costing calculation always comes from POdimension (quantity given when creating job number)
    pod_quantity = b.pod_quantity
    pod_item_id = ""
    pod_itemdescription_id = ""

    # na_qty_display: from Nadimension (Need Assessment quantity) — used for display in the costing list
    na_qty_display = b.pod_nad.nad_quantity if b.pod_nad else 0

    if job_no:
        # Fetch existing costing record to pre-fill item/itemdescription for convenience when editing
        # IMPORTANT: pod_quantity is NOT overridden here — costing always uses POdimension quantity
        costing_record = PkcostingInfo.objects.filter(ct_job_no=job_no, ct_requirement=b.pod_nad).first()

        if not costing_record:
            costing_record = PkcostingInfo.objects.filter(ct_job_no=job_no, ct_po_dimension=b).first()

        if not costing_record:
            costing_record = PkcostingInfo.objects.filter(
                ct_job_no=job_no,
                ct_assessment_num=b.pod_assess_num,
                ct_uom=b.pod_uom
            ).first()

        if costing_record:
            # Only pre-fill item/itemdescription — keep pod_quantity from POdimension
            # Pull Job Qty from Job instead of PO if editing an existing job
            if costing_record.ct_na_quantity is not None:
                pod_quantity = costing_record.ct_na_quantity
                
            if costing_record.ct_item:
                pod_item_id = str(costing_record.ct_item.id)
            if costing_record.ct_itemdescription:
                pod_itemdescription_id = str(costing_record.ct_itemdescription.id)

    po_dimension_box_val = f"{b.pod_item} ({b.pod_type_of_req} {b.pod_length}x{b.pod_width}x{b.pod_height})"
    pod_dimension_type = str(b.pod_dimension_type)
    pod_dimension_type_id = str(b.pod_type_of_req.id)
    pod_uom = str(b.pod_uom)
    pod_uom_id = str(b.pod_uom.id)
    pod_length = str(b.pod_length)
    pod_width = str(b.pod_width)
    pod_height = str(b.pod_height)

    # Return the Nadimension ID (pod_nad) so the form field ct_requirement is set correctly
    pod_nad_id = str(b.pod_nad.id) if b.pod_nad else ""

    # Calculate wood CFT for this job and requirement (Pine Wood=1, Rubber Wood=5)
    job_wood_cft = 0.0
    if b.pod_nad and job_no:
        total_cft_val = PkcostingInfo.objects.filter(
            ct_job_no=job_no,
            ct_requirement=b.pod_nad,
            ct_cost_type=8,
            ct_stock_type__in=[1, 5]
        ).aggregate(total=Sum(F('ct_sqrt_req') * F('ct_na_quantity')))['total']
        job_wood_cft = round(total_cft_val, 3) if total_cft_val is not None else 0.0
    elif b.pod_nad:
        total_cft_val = PkcostingInfo.objects.filter(
            ct_requirement=b.pod_nad,
            ct_cost_type=8,
            ct_stock_type__in=[1, 5]
        ).aggregate(total=Sum(F('ct_sqrt_req') * F('ct_na_quantity')))['total']
        job_wood_cft = round(total_cft_val, 3) if total_cft_val is not None else 0.0

    data = {
        'po_dimension_box_val': po_dimension_box_val,
        'pod_dimension_type': pod_dimension_type,
        'pod_type_of_req_id': pod_dimension_type_id,
        'pod_uom': pod_uom,
        'pod_uom_id': pod_uom_id,
        'pod_length': pod_length,
        'pod_width': pod_width,
        'pod_height': pod_height,
        'pod_quantity': str(pod_quantity),        # Job creation quantity (POdimension) — used for costing calc
        'na_qty_display': str(na_qty_display),    # Need Assessment quantity — for display in list
        'pod_item_id': pod_item_id,
        'pod_itemdescription_id': pod_itemdescription_id,
        'pod_nad_id': pod_nad_id,
        'job_total_cft': job_wood_cft,
    }

    return JsonResponse(data)





