import json
from django.contrib.auth.decorators import login_required
from ..forms import PkretrivalForm
from ..models import PkstockpurchasesInfo,PkcostingInfo,PkquotationsummaryInfo
from django.shortcuts import render, redirect
from ..views import update_reduced_dimensions
from django.contrib import messages

@login_required(login_url='login_page')
def pk_retrival_add(request, retrival_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    na_assessment_num_id = request.session.get('na_assessment_id')

    if request.method == "GET":
        if retrival_id == 0:
            form = PkretrivalForm()
        else:
            retrival = PkcostingInfo.objects.get(pk=retrival_id)
            form = PkretrivalForm(instance=retrival)
        context = {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'na_assessment_num_id': na_assessment_num_id,
        }
        return render(request, "asset_mgt_app/pk_retrival_add.html", context)

    else:
        if retrival_id == 0:
            form = PkretrivalForm(request.POST)
            if form.is_valid():
                form.save()
                print("Retrieval Form is Valid")
                last_id = PkcostingInfo.objects.latest('id').id
                messages.success(request, 'Record Updated Successfully')
                return redirect('/SMS/pk_retrival_update/' + str(last_id))
            else:
                print("Retrieval Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            retrival = PkcostingInfo.objects.get(pk=retrival_id)
            form = PkretrivalForm(request.POST, instance=retrival)
            if form.is_valid():
                stock_purchase_num_id = request.POST.get('ct_stock_purchase_number')
                requested_qty = request.POST.get('ct_quantity_req')
                print(requested_qty)

                if stock_purchase_num_id:
                    stock_purchase_obj = PkstockpurchasesInfo.objects.get(id=stock_purchase_num_id)
                    stock_purchase_num = stock_purchase_obj.sp_purchase_num
                    available_qty = stock_purchase_obj.sp_quantity or 0
                    print(available_qty)
                    if float(requested_qty) > float(available_qty):
                        messages.error(request, 'Available quantity is less than requested quantity')
                        return redirect(request.META['HTTP_REFERER'])
                    else:
                        stock_status = retrival.ct_stock_status.id
                        print("Stock Status ID:", stock_status)

                        if stock_status == 2:
                            form.save()
                            stock_purchase_obj.sp_quantity_reduced = float(available_qty) - float(requested_qty)
                            stock_purchase_obj.save()

                            messages.success(request, 'Stock Successfully Retrieved & Supplied')
                            update_reduced_dimensions(stock_purchase_num, retrival_id)
                        else:
                            messages.success(request, 'Stock Not Retrieved')
                else:
                    messages.error(request, 'Please select a stock with purchase number')
                    return redirect(request.META['HTTP_REFERER'])
            else:
                print("Retrieval Form is Not Valid")
                for field, errors in form.errors.items():
                    for error in errors:
                        print(f"Error in {field}: {error}")
                        messages.error(request, f"Error in {field}: {error}")
                messages.error(request, 'Record Not Updated Successfully')

            return redirect(request.META['HTTP_REFERER'])

# List retrival
@login_required(login_url='login_page')
def pk_retrival_list(request):
    first_name = request.session.get('first_name')
    context = {
                'pk_retrival_list' : PkcostingInfo.objects.filter(ct_cost_type=8,ct_stock_status__in=[1, 3]).order_by('-id'),
                'first_name': first_name
               }
    return render(request,"asset_mgt_app/pk_retrival_list.html",context)

#Delete retrival
@login_required(login_url='login_page')
def pk_retrival_delete(request,retrival_id):
    retrival = PkcostingInfo.objects.get(pk=retrival_id)
    retrival.delete()
    # return redirect('/SMS/pK_retrival_cancel')
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def pK_retrival_cancel(request):
    assessment_num_val = request.session.get('na_assessment_id')
    retrival_summary_id=PkquotationsummaryInfo.objects.get(qs_assessment_num=assessment_num_val).id
    return redirect('/SMS/pk_retrivalsummary_update/' + str(retrival_summary_id))