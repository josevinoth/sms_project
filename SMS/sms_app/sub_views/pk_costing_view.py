import json
from html import unescape

from django.contrib.auth.decorators import login_required
from ..forms import ModifyDimensionsForm,CostingSearchForm,PkcostingForm
from ..models import Natypeofreq,Nadimension,pk_itemdescriptionInfo,PkstockpurchasesInfo,PkcostingsummaryInfo,Stockdescription,PkcostingInfo
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages

@login_required(login_url='login_page')
def costing_add(request,costing_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    na_assessment_num_id = request.session.get('na_assessment_id')

    if request.method == "GET":
        if costing_id == 0:
            form = PkcostingForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'na_assessment_num_id': na_assessment_num_id,
                'costing_list': PkcostingInfo.objects.filter(ct_assessment_num=na_assessment_num_id),
            }
        else:
            costing=PkcostingInfo.objects.get(pk=costing_id)
            form = PkcostingForm(instance=costing)
            context={
                    'form': form,
                    'first_name': first_name,
                    'user_id': user_id,
                    'na_assessment_num_id': na_assessment_num_id,
                    'costing_list': PkcostingInfo.objects.filter(ct_assessment_num=na_assessment_num_id),
                    }
        return render(request, "asset_mgt_app/pk_costing_add.html", context)
    else:
        if costing_id == 0:
            print("Inside PK Costing post add")
            form = PkcostingForm(request.POST)
            if form.is_valid():
                form.save()
                print("costing Form is Valid")
                last_id = (PkcostingInfo.objects.latest('id')).id
                stock_purchase_num=PkcostingInfo.objects.get(pk=last_id).ct_stock_purchase_number
                cost_type_id = PkcostingInfo.objects.get(pk=last_id).ct_cost_type.id
                if cost_type_id==8:
                    update_reduced_dimensions(stock_purchase_num,last_id)
                else:
                    pass
                messages.success(request, 'Record Updated Successfully')
                # return redirect('/SMS/costing_update/'+str(last_id))
                return redirect('/SMS/costing_insert/')
            else:
                print("costing Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("Inside PK Costing post Edit")
            costing = PkcostingInfo.objects.get(pk=costing_id)
            form = PkcostingForm(request.POST,instance=costing)
            if form.is_valid():
                form.save()
                print("costing Form is Valid")
                stock_purchase_num = PkcostingInfo.objects.get(pk=costing_id).ct_stock_purchase_number
                last_id=costing_id
                cost_type_id=PkcostingInfo.objects.get(pk=costing_id).ct_cost_type.id
                if cost_type_id==8:
                    update_reduced_dimensions(stock_purchase_num,last_id)
                else:
                    pass
                messages.success(request, 'Record Updated Successfully')
            else:
                print("costing Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

def update_reduced_dimensions(stock_purchase_num,last_id):
    length = PkcostingInfo.objects.get(pk=last_id).ct_length
    qty = PkcostingInfo.objects.get(pk=last_id).ct_quantity
    cft = PkcostingInfo.objects.get(pk=last_id).ct_cft

    prev_length = PkstockpurchasesInfo.objects.get(sp_purchase_num=stock_purchase_num).sp_length_reduced
    prev_qty = PkstockpurchasesInfo.objects.get(sp_purchase_num=stock_purchase_num).sp_quantity_reduced
    prev_cft = PkstockpurchasesInfo.objects.get(sp_purchase_num=stock_purchase_num).sp_cft_reduced

    if prev_length>=length:
        current_length = prev_length - length
        current_cft= prev_cft - cft
    else:
        current_length = prev_length
        current_cft= prev_cft

    if prev_qty >= qty:
        current_qty=prev_qty-qty
    else:
        current_qty = prev_qty

    PkstockpurchasesInfo.objects.filter(sp_purchase_num=stock_purchase_num).update(sp_length_reduced=current_length)
    PkstockpurchasesInfo.objects.filter(sp_purchase_num=stock_purchase_num).update(sp_quantity_reduced=current_qty)
    PkstockpurchasesInfo.objects.filter(sp_purchase_num=stock_purchase_num).update(sp_cft_reduced=current_cft)

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
    print('stock_description',stock_description)
    print('stock_description_id',stock_description_id)
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
    # queryset = PkstockpurchasesInfo.objects.all()
    queryset = PkstockpurchasesInfo.objects.filter(sp_quantity_reduced__gt=0)
    if stock_description:
        queryset = queryset.filter(sp_stock_description=stock_description)
    if stock_type:
        queryset = queryset.filter(sp_stock_type=stock_type)
        # Serialize the queryset to JSON
        results = list(queryset.values(
            'id',
            'sp_vendor_bill',
            'sp_purchase_num',
            'sp_category__category',
            'sp_stock_type__pk_stocktype',  # Replace 'name' with the actual field in the related model
            'sp_stock_description__stock_description',
            'sp_source__source',  # Replace 'name' with the actual field in the related model
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
    # Serialize the queryset to JSON and return it
    # results = list(queryset.values())
    print('results', results)
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
    item_descriptions = pk_itemdescriptionInfo.objects.filter(id_item_name=item_id).order_by('id_item_description')

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
def pk_get_pk_requirement_type(request):
    requirement_type_id = []
    requirement_type_val = []
    ct_assessment_num_id = request.GET.get('ct_assessment_num_id')
    print('ct_assessment_num_id',ct_assessment_num_id)
    # Fetch requirement type
    requirement_type = Nadimension.objects.filter(nad_assess_num=ct_assessment_num_id).values_list('nad_type_of_req',flat=True)
    # Extract id and id_item_description attributes from queryset
    for type in requirement_type:
        requirement_type_id.append(Natypeofreq.objects.get(id=type).id)
        requirement_type_val.append(Natypeofreq.objects.get(id=type).type_of_req)
    # Create JSON response data
    data = {
        'requirement_type_val': requirement_type_val,
        'requirement_type_id': requirement_type_id,
    }

    # Return JSON response
    return JsonResponse(data)

