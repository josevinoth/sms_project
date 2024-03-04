import json
from django.contrib.auth.decorators import login_required
from ..forms import ModifyDimensionsForm,CostingSearchForm,PkcostingForm
from ..models import PkstockpurchasesInfo,PkcostingsummaryInfo,Stockdescription,PkcostingInfo
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
                messages.success(request, 'Record Updated Successfully')
            else:
                print("costing Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

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
    costing.delete()
    return redirect('/SMS/costing_list')

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
    queryset = PkstockpurchasesInfo.objects.all()
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
            'sp_thick_height',
            'sp_width',
            'sp_length',
            'sp_cft',
            'sp_rate',
            'sp_quantity',
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