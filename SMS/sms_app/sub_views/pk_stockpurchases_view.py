from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from ..forms import PkstockpurchasesForm
from ..models import PkstockpurchasesInfo
from django.shortcuts import render, redirect
from django.contrib import messages

from ..sub_models.pk_stock_vendor_mod import PkstockvebdorInfo
from ..sub_models.stock_description_mod import Stockdescription


@login_required(login_url='login_page')
def stockpurchases_add(request, stockpurchases_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

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
        }
        return render(request, "asset_mgt_app/pk_stockpurchases_add.html", context)

    else:
        if stockpurchases_id == 0:
            # Creating a new stock purchase entry
            form = PkstockpurchasesForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()  # Save the new record
                try:
                    # Get the latest record ID
                    last_id = PkstockpurchasesInfo.objects.order_by('-id').values_list('id', flat=True).first()
                    reg_number = 1000000 + last_id  # Generate a new purchase number based on last ID
                except ObjectDoesNotExist:
                    reg_number = 1000000  # Start with 1000000 if no records exist

                # Create the stock purchase number
                stockpurchases_num_next = str('GRN/PK/') + str(reg_number)

                # Update the new record with the generated stock purchase number
                PkstockpurchasesInfo.objects.filter(id=last_id).update(sp_purchase_num=stockpurchases_num_next)

                # Fetch the ID of the newly created stock purchase
                stock_id = PkstockpurchasesInfo.objects.get(sp_purchase_num=stockpurchases_num_next).id

                messages.success(request, 'Record created successfully.')
                return redirect('/SMS/stockpurchases_update/' + str(stock_id))  # Redirect to the update page

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
    first_name = request.session.get('first_name')
    context = {'stockpurchases_list' : PkstockpurchasesInfo.objects.filter(sp_quantity__gt=0),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_stockpurchases_list.html",context)

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