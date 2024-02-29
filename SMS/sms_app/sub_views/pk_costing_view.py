import json
from django.contrib.auth.decorators import login_required
from ..forms import PkcostingForm
from ..models import PkcostingsummaryInfo,Stockdescription,PkcostingInfo
from django.shortcuts import render, redirect
from django.http import HttpResponse
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
                }
        return render(request, "asset_mgt_app/pk_costing_add.html", context)
    else:
        if costing_id == 0:
            form = PkcostingForm(request.POST)
            if form.is_valid():
                form.save()
                print("costing Form is Valid")
                last_id = (PkcostingInfo.objects.latest('id')).id
                messages.success(request, 'Record Updated Successfully')
                return redirect('/SMS/costing_update/'+str(last_id))
            else:
                print("costing Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
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
def pk_item_search_page(request):
    if request.method == 'GET':
        cost_type = request.GET.get('ct_cost_type', '')
        stock_type = request.GET.get('ct_stock_type', '')
        stock_description = request.GET.get('ct_stock_description', '')

        # Filter the queryset based on the search parameters
        queryset = PkcostingInfo.objects.filter(
            ct_cost_type__cost_type__icontains=cost_type,
            ct_stock_type__pk_stocktype__icontains=stock_type,
            ct_stock_description__stock_description__icontains=stock_description,
        )

        # You may want to add more conditions to filter based on other fields

        context = {'queryset': queryset}
        return render(request, "asset_mgt_app/pk_item_search_page.html", context)
