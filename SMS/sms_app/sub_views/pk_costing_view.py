import json
from django.contrib.auth.decorators import login_required
from ..forms import ModifyDimensionsForm,CostingSearchForm,PkcostingForm
from ..models import POdimension,Nadimension,pk_itemdescriptionInfo,PkstockpurchasesInfo,PkcostingsummaryInfo,Stockdescription,PkcostingInfo
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages

@login_required(login_url='login_page')
def costing_add(request,costing_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    na_assessment_num_id = request.session.get('na_assessment_id')
    na_customer_name_id = request.session.get('na_customer_name_id')
    ses_customer_po_id = request.session.get('ses_customer_po_id')

    if request.method == "GET":
        if costing_id == 0:
            form = PkcostingForm()
        else:
            costing = get_object_or_404(PkcostingInfo, pk=costing_id)
            form = PkcostingForm(instance=costing)

        context = {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'na_assessment_num_id': na_assessment_num_id,
            'na_customer_name_id': na_customer_name_id,
            'ses_customer_po_id': ses_customer_po_id,
            'costing_list': PkcostingInfo.objects.filter(ct_assessment_num=na_assessment_num_id),
        }
        return render(request, "asset_mgt_app/pk_costing_add.html", context)

    else:
        if costing_id == 0:
            form = PkcostingForm(request.POST)
        else:
            costing = get_object_or_404(PkcostingInfo, pk=costing_id)
            form = PkcostingForm(request.POST, instance=costing)

        if form.is_valid():
            cost_type_id = request.POST.get('ct_cost_type')
            if int(cost_type_id) == 8:
                stock_purchase_num_id = request.POST.get('ct_stock_purchase_number')
                stock_qty = int(request.POST.get('ct_quantity'))
                stock_purchase = get_object_or_404(PkstockpurchasesInfo, id=stock_purchase_num_id)

                if stock_qty <= 0:
                    messages.error(request, 'Quantity should be greater than 0')
                elif stock_qty > stock_purchase.sp_quantity_reduced:
                    error_message = f'Quantity should be less than or equal to available stock {stock_purchase.sp_purchase_num} quantity {stock_purchase.sp_quantity_reduced}'
                    messages.error(request, error_message)
                else:
                    form.save()
                    messages.success(request, 'Stock Updated Successfully')
                    return redirect('/SMS/costing_insert/')
            else:
                form.save()
                messages.success(request, 'Stock Updated Successfully')
                return redirect('/SMS/costing_insert/')
        else:
            print("Costing Form is Not Valid")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")
                    messages.error(request, f"Error in {field}: {error}")
            messages.error(request, 'Record Not Updated Successfully')

        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

def update_reduced_dimensions(stock_purchase_num,last_id):
    qty = PkcostingInfo.objects.get(pk=last_id).ct_quantity
    cft = PkcostingInfo.objects.get(pk=last_id).ct_cft
    prev_qty = PkstockpurchasesInfo.objects.get(sp_purchase_num=stock_purchase_num).sp_quantity_reduced
    prev_cft = PkstockpurchasesInfo.objects.get(sp_purchase_num=stock_purchase_num).sp_cft_reduced
    current_qty = prev_qty - qty
    current_cft = prev_cft - cft
    PkstockpurchasesInfo.objects.filter(sp_purchase_num=stock_purchase_num).update(sp_quantity_reduced=current_qty)
    PkstockpurchasesInfo.objects.filter(sp_purchase_num=stock_purchase_num).update(sp_cft_reduced=round(current_cft,2))

def append_reduced_dimensions(stock_purchase_num,costing_id):
    length = PkcostingInfo.objects.get(pk=costing_id).ct_length
    qty = PkcostingInfo.objects.get(pk=costing_id).ct_quantity
    cft = PkcostingInfo.objects.get(pk=costing_id).ct_cft

    prev_length = PkstockpurchasesInfo.objects.get(sp_purchase_num=stock_purchase_num).sp_length_reduced
    prev_qty = PkstockpurchasesInfo.objects.get(sp_purchase_num=stock_purchase_num).sp_quantity_reduced
    prev_cft = PkstockpurchasesInfo.objects.get(sp_purchase_num=stock_purchase_num).sp_cft_reduced

    if prev_length>=length:
        current_length = prev_length + length
        current_cft= prev_cft + cft
    else:
        current_length = prev_length
        current_cft= prev_cft

    if prev_qty >= qty:
        current_qty=prev_qty+qty
    else:
        current_qty = prev_qty

    PkstockpurchasesInfo.objects.filter(sp_purchase_num=stock_purchase_num).update(sp_length_reduced=current_length)
    PkstockpurchasesInfo.objects.filter(sp_purchase_num=stock_purchase_num).update(sp_quantity_reduced=current_qty)
    PkstockpurchasesInfo.objects.filter(sp_purchase_num=stock_purchase_num).update(sp_cft_reduced=current_cft)

# List costing
@login_required(login_url='login_page')
def costing_list(request):
    first_name = request.session.get('first_name')
    context = {'costing_list' : PkcostingInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_costing_list.html",context)

#Delete costing
@login_required(login_url='login_page')
def costing_delete(request,costing_id):
    costing = PkcostingInfo.objects.get(pk=costing_id)
    stock_purchase_num = PkcostingInfo.objects.get(pk=costing_id).ct_stock_purchase_number
    cost_type_id = PkcostingInfo.objects.get(pk=costing_id).ct_cost_type.id
    if cost_type_id == 8:
        append_reduced_dimensions(stock_purchase_num, costing_id)
    else:
        pass
    costing.delete()
    print("Successfully Deleted")
    # return redirect('/SMS/costing_list')
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def load_stock_description(request):
    stock_description_id= []
    stock_type = request.GET.get('stock_type')
    # Fetch cost_description Details
    stock_description = list(Stockdescription.objects.filter(stock_type=stock_type).values_list('stock_description', flat=True).distinct())
    stock_description.sort()
    for j in stock_description:
        stock_description_id.append(Stockdescription.objects.get(stock_description=j).id)
    data = {
        'stock_description':stock_description,
        'stock_description_id': stock_description_id,
    }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))

@login_required(login_url='login_page')
def costing_cancel(request):
    assessment_num_val = request.session.get('na_assessment_id')
    costing_summary_id=PkcostingsummaryInfo.objects.get(cs_assessment_num=assessment_num_val).id
    return redirect('/SMS/costingsummary_update/' + str(costing_summary_id))

@login_required(login_url='login_page')
def pk_item_search_page_costing(request):
    stock_type = request.GET.get('stock_type')
    stock_description = request.GET.get('stock_description')
    length_req = request.GET.get('length_req')
    width_req = request.GET.get('width_req')
    height_req = request.GET.get('height_req')

    # Print statements for debugging
    print('length_req:', length_req)
    print('width_req:', width_req)
    print('height_req:', height_req)

    # Query the database
    queryset = PkstockpurchasesInfo.objects.filter(
        sp_quantity_reduced__gt=0,
        sp_stock_description=stock_description if stock_description else '',
        sp_stock_type=stock_type if stock_type else '',
        sp_thick_height__gte=height_req if height_req else float('inf'),
        sp_width__gte=width_req if width_req else float('inf'),
        sp_length__gte=length_req if length_req else float('inf')
    )

    # Function to format date
    def format_date(date):
        return date.strftime('%B %d, %Y') if date else ''

    # Serialize the queryset to JSON with date formatting
    results = list(queryset.values(
        'id',
        'sp_vendor_bill',
        'sp_stock_in_date',
        'sp_purchase_num',
        'sp_category__category',
        'sp_stock_type__pk_stocktype',
        'sp_stock_description__stock_description',
        'sp_source__source',
        'sp_thick_height_reduced',
        'sp_width_reduced',
        'sp_length_reduced',
        'sp_cft_reduced',
        'sp_rate',
        'sp_quantity_reduced',
        'sp_uom__unit_of_measure',
        'sp_uom',
        'sp_size',
    ))

    # Apply date formatting to the results
    for result in results:
        result['sp_stock_in_date'] = format_date(result['sp_stock_in_date'])

    return JsonResponse(results, safe=False)

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

    # Fetch requirement type from Need Assessment dimension
    po_dimensions = POdimension.objects.filter(pod_assess_num=ct_assessment_num_id, pod_po_num=ct_customer_po_id)

    po_requirement_type_id = []
    po_requirement_type_val = []

    for dimension in po_dimensions:
        po_requirement_type_id.append(dimension.id)
        po_requirement_type_val.append(f"{dimension.pod_item} ({dimension.pod_type_of_req} {dimension.pod_length}x{dimension.pod_width}x{dimension.pod_height})")
        # po_requirement_type_val.append(dimension.pod_item)

    data = {
        'po_requirement_type_val': po_requirement_type_val,
        'po_requirement_type_id': po_requirement_type_id,
    }
    return JsonResponse(data)

@login_required(login_url='login_page')
def pk_store_po_dimension_id(request):
    # Initialize the list
    po_dimension_box_val = []

    # Fetch the requirement ID from the request
    ct_requirement_id = request.GET.get('ct_requirement_id')

    # Fetch the requirement type from PO using the primary key
    b = POdimension.objects.get(pk=ct_requirement_id)

    # Append the formatted string to the list
    po_dimension_box_val.append(
        f"{b.pod_type_of_req} ({b.pod_length}x{b.pod_width}x{b.pod_height})"
    )

    # Convert the list to a single string without brackets
    po_dimension_box_str = ', '.join(po_dimension_box_val)

    # Create the data dictionary with the string value
    data = {
        'po_dimension_box_val': po_dimension_box_str,
    }
    return JsonResponse(data)


