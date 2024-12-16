from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from ..forms import PkexcessForm
from ..models import PkcostingInfo
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


# Stock Purchases List - Only display where sp_status = 2
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from ..forms import PkreturnForm
from ..models import PkstockpurchasesInfo
from django.shortcuts import render, redirect
from django.contrib import messages



@login_required(login_url='login_page')
def pk_excess_stock_add(request, costing_id=0):
        first_name = request.session.get('first_name')
        user_id = request.session.get('ses_userID')
        na_assessment_num_id = request.session.get('na_assessment_id')
        na_customer_name_id = request.session.get('na_customer_name_id')
        na_customer_new_name_id = request.session.get('na_customer_new_name')
        ses_customer_po_id = request.session.get('ses_customer_po_id')
        print('ses_customer_po_id', ses_customer_po_id)

        if request.method == "GET":
            if costing_id == 0:
                form = PkexcessForm()
            else:
                costing = get_object_or_404(PkcostingInfo, pk=costing_id)
                form = PkexcessForm(instance=costing)

            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'na_assessment_num_id': na_assessment_num_id,
                'na_customer_name_id': na_customer_name_id,
                'na_customer_new_name_id': na_customer_new_name_id,
                'ses_customer_po_id': ses_customer_po_id,
                'costing_list': PkcostingInfo.objects.filter(ct_assessment_num=na_assessment_num_id,
                                                             ct_customer_po=ses_customer_po_id),
                'excess_costing_list': PkcostingInfo.objects.all(),
            }
            return render(request, "asset_mgt_app/pk_excess_return.html", context)

        else:
            if costing_id == 0:
                print("Inside PK Costing post add")
                form = PkexcessForm(request.POST)
            else:
                costing = get_object_or_404(PkcostingInfo, pk=costing_id)
                form = PkexcessForm(request.POST, instance=costing)

            if form.is_valid():
                print('Form is valid')
                cost_type_id = request.POST.get('ct_cost_type')

                if int(cost_type_id) == 8:  # For stock-related cost types
                    stock_purchase_num_id = request.POST.get('ct_stock_purchase_number')
                    print('stock_purchase_num_id', stock_purchase_num_id)
                    if stock_purchase_num_id:
                        try:
                            # Fetch stock purchase record
                            stock_purchase = PkstockpurchasesInfo.objects.get(id=stock_purchase_num_id)
                            stock_purchase_num = stock_purchase.sp_purchase_num
                            stock_qty_available = stock_purchase.sp_quantity_reduced

                            # Validate quantity
                            stock_qty_str = request.POST.get('ct_quantity', None)
                            if not stock_qty_str:
                                messages.error(request, 'Quantity is required.')
                                return redirect(request.META['HTTP_REFERER'])

                            try:
                                stock_qty = int(stock_qty_str)
                            except ValueError:
                                messages.error(request, 'Invalid quantity value. It should be a number.')
                                return redirect(request.META['HTTP_REFERER'])

                            form.save()
                            print("Costing form is valid and stock updated.")
                            messages.success(request, 'Stock Updated Successfully')
                        except PkstockpurchasesInfo.DoesNotExist:
                            pass

                    else:
                        # No stock purchase number provided, still save the record
                        form.save()
                        messages.success(request, 'Record Saved Successfully')
                else:
                    # If cost type is not stock-related, save the record
                    form.save()
                    messages.success(request, 'Record Saved Successfully')

                return redirect(request.META['HTTP_REFERER'])

            else:
                print("Costing form is not valid.")
                messages.error(request, 'Record Not Updated Successfully')

            return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

# List retrival
@login_required(login_url='login_page')
def pk_excess_stock_list(request):
    first_name = request.session.get('first_name')
    excess_costing_list = PkcostingInfo.objects.filter(ct_stock_status=4, ct_excess_status=3)

    context = {
        'excess_costing_list': excess_costing_list,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/pk_excess_stock_list.html", context)

@login_required(login_url='login_page')
def pk_excess_stock_cancel(request):
    assessment_num_val = request.session.get('na_assessment_id')
    # costing_summary_id=PkcostingsummaryInfo.objects.get(cs_assessment_num=assessment_num_val).id
    return redirect('/SMS/pk_excess_stock_list/' )