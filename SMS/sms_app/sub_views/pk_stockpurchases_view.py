from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from ..forms import PkstockpurchasesForm
from ..models import PkstockpurchasesInfo, PkpartcodeInfo, PkcostingInfo
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id

from ..sub_models.pk_stock_vendor_mod import PkstockvebdorInfo
from ..sub_models.stock_description_mod import Stockdescription
from ..sub_models.stock_maintenance_mod import StockMaintenance
from .stock_maintenance_view import get_part_totals


@login_required(login_url='login_page')
def stockpurchases_add(request, stockpurchases_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    stock_vendor_id = request.session.get('ses_stock_vendor_id')

    if request.method == "GET":
        # For GET request, render the form
        if stockpurchases_id == 0:
            form = PkstockpurchasesForm()  # Create a new form for adding a stock purchase
        else:
            stockpurchases = PkstockpurchasesInfo.objects.get(pk=stockpurchases_id)  # Fetch existing record
            form = PkstockpurchasesForm(instance=stockpurchases)  # Load data into form for editing

        pk_vendor_bill = request.session.get('ses_pk_vendor_bill')  # Retrieve session info
        context = {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'pk_vendor_bill': pk_vendor_bill,
            'stock_vendor_id': stock_vendor_id,
        }
        return render(request, "asset_mgt_app/pk_stockpurchases_add.html", context)

    else:
        if stockpurchases_id == 0:
            # Creating a new stock purchase entry
            form = PkstockpurchasesForm(request.POST, request.FILES)
            if form.is_valid():
                new_record = form.save()  # Save and get the instance
                last_id = new_record.id  # Directly get the saved ID

                # Generate Stock Purchase number based on financial year (Branch specific)
                fy = get_financial_year()
                
                # Try to get branch from vendor bill -> vendor
                branch_id = get_session_branch_id(request)
                if new_record.sp_vendor_bill_id:
                    vb = new_record.sp_vendor_bill_id
                    if vb.spv_vendor_name and vb.spv_vendor_name.vend_branch:
                        branch_id = vb.spv_vendor_name.vend_branch.id
                
                branch_code = get_branch_code(branch_id)
                prefix = f"{fy}_{branch_code}_GRN_PK_"
                new_record.sp_purchase_num = generate_next_number(PkstockpurchasesInfo, 'sp_purchase_num', prefix, 6)
                new_record.save(update_fields=['sp_purchase_num'])  # Efficient update

                messages.success(request, 'Record created successfully.')
                # return redirect(f'/SMS/stockpurchases_update/{last_id}')  # Redirect using last_id
                return redirect('/SMS/stockpurchases_insert')
            else:
                # Form is invalid, display an error
                messages.error(request, 'Form is not valid.')
                return redirect(request.META['HTTP_REFERER'])

        else:
            # Updating an existing stock purchase entry
            stockpurchases = PkstockpurchasesInfo.objects.get(pk=stockpurchases_id)
            form = PkstockpurchasesForm(request.POST, request.FILES, instance=stockpurchases)

            if form.is_valid():
                form.save()  # Save the updates
                messages.success(request, 'Record updated successfully.')
            else:
                # Form is invalid, display an error
                messages.error(request, 'Form is not valid.')

            return redirect(request.META['HTTP_REFERER'])
            # return redirect('/SMS/stockpurchases_insert')
        # forms_data = request.POST  # Capture all form data (including cloned forms)
        #
        # # Loop through the forms data and save each form
        # for form_key in forms_data:
        #     if form_key.startswith('form-'):  # Assuming form fields are prefixed with 'form-'
        #         form_data = forms_data[form_key]
        #         form = PkstockpurchasesForm(form_data)
        #
        #         if form.is_valid():
        #             # Save each form data to the database
        #             new_place = form.save()
        #             print("form saved to database")
        #             try:
        #                 last_id = PkstockpurchasesInfo.objects.latest('id').id
        #                 stockpurchases_num_next = str('GRN/PK/') + str(int((1000000 + last_id)))
        #             except ObjectDoesNotExist:
        #                 stockpurchases_num_next = str('GRN/PK/') + str('1000000')
        #
        #             # Update the new record with the stockpurchases number
        #             PkstockpurchasesInfo.objects.filter(id=new_place.id).update(sp_purchase_num=stockpurchases_num_next)
        #
        #             # Additional updates after form save
        #             PkstockpurchasesInfo.objects.filter(pk=new_place.id).update(
        #                 sp_thick_height_reduced=new_place.sp_thick_height,
        #                 sp_width_reduced=new_place.sp_width,
        #                 sp_length_reduced=new_place.sp_length,
        #                 sp_quantity_reduced=new_place.sp_quantity,
        #                 sp_cft_reduced=new_place.sp_total_cft
        #             )
        #
        #             messages.success(request, 'Record Updated Successfully')
        #         else:
        #             messages.error(request, 'Form is Not Valid')
        #             return redirect(request.META['HTTP_REFERER'])
        #     return redirect(request.META['HTTP_REFERER'])

        # return redirect('/SMS/stockpurchases_list')


# List stockpurchases
@login_required(login_url='login_page')
def stockpurchases_list(request):
    # Fetch all unique part codes from StockMaintenance
    part_codes = PkpartcodeInfo.objects.filter(
        id__in=StockMaintenance.objects.values('sm_partcode_id').distinct()
    ).order_by('pc_code')

    summary_data = []
    
    for part in part_codes:
        # Calculate totals for this part code
        totals = get_part_totals(part.id)
        
        # Only include if there's some activity
        if totals['overall_count'] > 0 or totals['retrieved_count'] > 0:
            desc = str(part.pc_stock_description) if part.pc_stock_description else "-"
            
            summary_data.append({
                'part_id': part.id,
                'part_code': part.pc_code,
                'description': desc,
                'uom': part.pc_uom.unit_of_measure if part.pc_uom else "-",
                'total_in': totals['overall_count'],
                'total_retrieved': totals['retrieved_count'],
                'available_balance': totals['current_count']
            })

    context = {
        'summary_data': summary_data
    }
    
    return render(request, "asset_mgt_app/pk_stockpurchases_list.html", context)

#Delete stockpurchases
@login_required(login_url='login_page')
def stockpurchases_delete(request,stockpurchases_id):
    stockpurchases = PkstockpurchasesInfo.objects.get(pk=stockpurchases_id)
    stockpurchases.delete()
    return redirect('/SMS/stockpurchases_list')

@login_required(login_url='login_page')
def stockpurchases_cancel(request):
    pk_vendor_bill = request.session.get('ses_pk_vendor_bill')
    id=PkstockvebdorInfo.objects.get(spv_vendor_bill=pk_vendor_bill).id
    url = '/SMS/pk_stock_vendor_update/' + str(id)
    return redirect(url)

# @login_required(login_url='login_page')
# def SP_fetch_stock_description(request):
#     stock_description_id = []
#     stock_description_val = []
#     stock_id = request.GET.get('stock_id')
#     # Fetch item_description Details
#     stock_descriptions = Stockdescription.objects.filter(id_stock_name=int(stock_id)).order_by('stock_description')
#     # Extract id and id_item_description attributes from queryset
#     for stock in stock_descriptions:
#         stock_description_id.append(stock.id)
#         stock_description_val.append(stock.stock_description)
#     # Create JSON response data
#     data = {
#         'stock_description_val': stock_description_val,
#         'stock_description_id': stock_description_id,
#     }
#
#     # Return JSON response
#     return JsonResponse(data)

@login_required(login_url='login_page')
def fetch_part_code_details(request):
    part_code_id = request.GET.get('part_code_id')  # Ensure this matches the frontend

    if not part_code_id:
        return JsonResponse({'error': 'Part code ID is required'}, status=400)

    try:
        # Use select_related to optimize foreign key fetching
        part_code = PkpartcodeInfo.objects.select_related(
            'pc_stock_type',
            'pc_stock_description',
            'pc_uom',
            'pc_stock_description__stock_received',
            'pc_stock_description__stock_Consumption'
        ).get(pk=part_code_id)

        stock_desc = part_code.pc_stock_description
        stock_received = stock_desc.stock_received if stock_desc and stock_desc.stock_received else None
        stock_consumption = stock_desc.stock_Consumption if stock_desc and stock_desc.stock_Consumption else None

        data = {
            'pc_stock_type': str(part_code.pc_stock_type) if part_code.pc_stock_type else '',
            'pc_stock_type_id': part_code.pc_stock_type.id if part_code.pc_stock_type else None,
            'pc_stock_description': str(stock_desc) if stock_desc else '',
            'pc_stock_description_id': stock_desc.id if stock_desc else None,
            'pc_uom': str(part_code.pc_uom) if part_code.pc_uom else '',
            'pc_uom_id': part_code.pc_uom.id if part_code.pc_uom else None,
            'pc_length': part_code.pc_length,
            'pc_width': part_code.pc_width,
            'pc_height': part_code.pc_height,
            'pc_size': part_code.pc_diameter_width,
            'pc_con_length': part_code.pc_con_length,

            # Stock Received & Consumption UOMs
            'stock_received': str(stock_received) if stock_received else '',
            'stock_received_id': stock_received.id if stock_received else None,
            'stock_consumption': str(stock_consumption) if stock_consumption else '',
            'stock_consumption_id': stock_consumption.id if stock_consumption else None,
        }

        return JsonResponse(data)
    except PkpartcodeInfo.DoesNotExist:
        return JsonResponse({'error': 'Part code not found'}, status=404)


@login_required(login_url='login_page')
def stock_usage_breakdown(request):
    part_id = request.GET.get('part_id')
    
    if not part_id:
        return JsonResponse({'error': 'Part ID is required'}, status=400)
    
    # We use StockMaintenance as the base because it is the actual source 
    # for the 'Retrieved' totals shown in the main list.
    sm_records = StockMaintenance.objects.filter(
        sm_partcode_id=part_id,
        sm_stock_type_id=2
    ).order_by('-sm_created_at')
    
    # We'll pre-fetch PkcostingInfo (linked records) to enrich the SM data
    # (Matching by part, cost_type=8, and trying to correlate by quantity/date if needed, 
    # but more robustly by sm_stock_purchase_number if saved there)
    
    # In current pk_costing_view.py, sm_ret.sm_count = costing.ct_quantity
    # Unfortunately there is no direct FK from SM back to PkcostingInfo.
    
    # Let's get all linked costing records for this part to try and match
    linked_costing = PkcostingInfo.objects.filter(
        ct_part_code_id=part_id,
        ct_cost_type_id=8
    ).select_related('ct_assessment_num', 'ct_customer_name')
    
    # Create a lookup map for linked data (Mapping by quantity + date)
    # Note: This is a best-effort enrichment given the lack of direct FK
    costing_map = {}
    for c in linked_costing:
        date_str = c.ct_created_at.strftime('%Y-%m-%d') if c.ct_created_at else "N/A"
        key = f"{date_str}_{c.ct_quantity}"
        costing_map[key] = c

    # Build a quick lookup by costing ID for direct matching
    costing_by_id = {c.id: c for c in linked_costing}

    data = []
    for sm in sm_records:
        date_obj = sm.sm_created_at or sm.sm_invoice_date
        date_str = date_obj.strftime('%Y-%m-%d') if date_obj else "N/A"
        date_full = date_obj.strftime('%Y-%m-%d %H:%M') if sm.sm_created_at else date_str
        
        assessment = "Manual/Legacy"
        customer = "N/A"
        usage_type = "Manual"
        linked = None

        # Strategy 1: Extract costing ID from sm_description (Standardized format: "... (Costing ID: XX)")
        if sm.sm_description and "(Costing ID: " in sm.sm_description:
            try:
                # The ID is between "(Costing ID: " and ")"
                costing_id_str = sm.sm_description.split("(Costing ID: ")[-1].split(")")[0]
                costing_id = int(costing_id_str)
                linked = costing_by_id.get(costing_id)
            except (ValueError, IndexError):
                pass

        # Strategy 2: Fallback for older records using "RET-GRN/PK/XXXXX-ID" format in sm_invoice_no
        if not linked and sm.sm_invoice_no and "RET-" in sm.sm_invoice_no:
            try:
                # The last segment after the final "-" is the costing entry ID
                costing_id = int(sm.sm_invoice_no.rsplit("-", 1)[-1])
                linked = costing_by_id.get(costing_id)
            except (ValueError, IndexError):
                pass

        # Strategy 2: Fallback - match by date + quantity key
        if not linked:
            key = f"{date_str}_{sm.sm_count}"
            linked = costing_map.get(key)

        # Strategy 3: Parse assessment from sm_description (e.g. "Retrieved for Assessment Assess_1000103")
        if linked:
            assessment = linked.ct_assessment_num.na_assessment_num if linked.ct_assessment_num else "N/A"
            customer = linked.ct_customer_name.cu_name if linked.ct_customer_name else (linked.ct_customer_new_name or "N/A")
            usage_type = "Automated"
        elif sm.sm_description and "Assessment " in sm.sm_description:
            try:
                assessment = sm.sm_description.split("Assessment ")[-1].strip()
                usage_type = "Historical"
            except:
                pass

        data.append({
            'assessment_num': assessment,
            'customer_name': customer,
            'quantity': sm.sm_count or 0.0,
            'date': date_full,
            'type': usage_type,
            'remarks': sm.sm_description or ""
        })
        
    return JsonResponse({'usage': data})

