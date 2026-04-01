from django.contrib.auth.decorators import login_required
from .general_utils import get_financial_year, generate_next_number
from django.core.exceptions import ObjectDoesNotExist

from ..forms import PkreturnForm
from ..models import PkstockpurchasesInfo,PkcostingInfo
from django.shortcuts import render, redirect
from django.contrib import messages


# Stock Purchases List - Only display where sp_status = 2
@login_required(login_url='login_page')
def stockpurchases_add(request, stockpurchases_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        # For GET request, render the form
        if stockpurchases_id == 0:
            form = PkreturnForm()  # Create a new form for adding a stock purchase
        else:
            stockpurchases = PkstockpurchasesInfo.objects.get(pk=stockpurchases_id)  # Fetch existing record
            form = PkreturnForm(instance=stockpurchases)  # Load data into form for editing

        pk_vendor_bill = request.session.get('ses_pk_vendor_bill')  # Retrieve session info
        context = {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'pk_vendor_bill': pk_vendor_bill,
        }
        return render(request, "asset_mgt_app/pk_stockpurchases_add.html", context)

    else:
        if stockpurchases_id == 0:
            # Creating a new stock purchase entry
            form = PkreturnForm(request.POST, request.FILES)
            if form.is_valid():
                instance = form.save()  # Save the new record and get the instance
                # Generate Stock Purchase (Return) number based on financial year
                fy = get_financial_year()
                prefix = f"{fy}_GRN_PK_"
                stockpurchases_num_next = generate_next_number(PkstockpurchasesInfo, 'sp_purchase_num', prefix, 6)

                # Update the new record with the generated stock purchase number using the instance ID
                PkstockpurchasesInfo.objects.filter(id=instance.id).update(sp_purchase_num=stockpurchases_num_next)

                # Fetch the ID of the newly created stock purchase
                stock_id = instance.id

                messages.success(request, 'Record created successfully.')
                return redirect('/SMS/stockpurchases_update/' + str(stock_id))  # Redirect to the update page

            else:
                # Form is invalid, display an error
                messages.error(request, 'Form is not valid.')
                return redirect(request.META['HTTP_REFERER'])

        else:
            # Updating an existing stock purchase entry
            stockpurchases = PkstockpurchasesInfo.objects.get(pk=stockpurchases_id)
            form = PkreturnForm(request.POST, request.FILES, instance=stockpurchases)

            if form.is_valid():
                form.save()  # Save the updates
                messages.success(request, 'Record updated successfully.')
            else:
                # Form is invalid, display an error
                messages.error(request, 'Form is not valid.')

            return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login_page')
def pk_return_list(request):
    first_name = request.session.get('first_name')
    # Filtering records where sp_status=2
    return_list = PkcostingInfo.objects.filter( ct_excess_status=1)

    context = {
        'return_list': return_list,
        'first_name': first_name
    }
    return render(request, "asset_mgt_app/pk_return_list.html", context)
