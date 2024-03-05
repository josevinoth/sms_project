from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from ..forms import PkstockpurchasesForm
from ..models import PkstockpurchasesInfo,PkstockvebdorInfo
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required(login_url='login_page')
def stockpurchases_add(request,stockpurchases_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if stockpurchases_id == 0:
            form = PkstockpurchasesForm()
        else:
            stockpurchases=PkstockpurchasesInfo.objects.get(pk=stockpurchases_id)
            form = PkstockpurchasesForm(instance=stockpurchases)
        pk_vendor_bill=request.session.get('ses_pk_vendor_bill')
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'pk_vendor_bill': pk_vendor_bill,
                }
        return render(request, "asset_mgt_app/pk_stockpurchases_add.html", context)
    else:
        if stockpurchases_id == 0:
            form = PkstockpurchasesForm(request.POST)
            if form.is_valid():
                # Generate Random stockpurchases number
                new_place = form.save()
                try:
                    last_id = PkstockpurchasesInfo.objects.latest('id').id
                    # stockpurchases_num_next = str('GRN/PK/') + str(int(((PkstockpurchasesInfo.objects.get(id=last_id)).sp_purchase_num).replace('GRN/PK/','')) + 1)
                    stockpurchases_num_next = str('GRN/PK/') + str(int((1000000 + last_id)))
                except ObjectDoesNotExist:
                    stockpurchases_num_next = str('GRN/PK/') + str('1000000')
                print("stockpurchases Form is Valid")
                last_id = (PkstockpurchasesInfo.objects.latest('id')).id
                PkstockpurchasesInfo.objects.filter(id=last_id).update(sp_purchase_num=stockpurchases_num_next)
                original_thick_height = PkstockpurchasesInfo.objects.get(pk=last_id).sp_thick_height
                original_width = PkstockpurchasesInfo.objects.get(pk=last_id).sp_width
                original_lenght = PkstockpurchasesInfo.objects.get(pk=last_id).sp_length
                original_qty = PkstockpurchasesInfo.objects.get(pk=last_id).sp_quantity
                original_cft = PkstockpurchasesInfo.objects.get(pk=last_id).sp_total_cft
                PkstockpurchasesInfo.objects.filter(pk=last_id).update(sp_thick_height_reduced=original_thick_height)
                PkstockpurchasesInfo.objects.filter(pk=last_id).update(sp_width_reduced=original_width)
                PkstockpurchasesInfo.objects.filter(pk=last_id).update(sp_length_reduced=original_lenght)
                PkstockpurchasesInfo.objects.filter(pk=last_id).update(sp_quantity_reduced=original_qty)
                PkstockpurchasesInfo.objects.filter(pk=last_id).update(sp_cft_reduced=original_cft)

                messages.success(request, 'Record Updated Successfully')
                url = new_place.get_absolute_url_pk_stock_purchases()
                return redirect(url)
            else:
                print("stockpurchases Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            stockpurchases = PkstockpurchasesInfo.objects.get(pk=stockpurchases_id)
            form = PkstockpurchasesForm(request.POST,instance=stockpurchases)
            if form.is_valid():
                form.save()
                print("stockpurchases Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("stockpurchases Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

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