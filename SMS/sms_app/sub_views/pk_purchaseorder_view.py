from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from ..forms import PkpurchaseorderForm
from ..models import PkpurchaseorderInfo
from django.shortcuts import render, redirect
from random import randint
from django.contrib import messages

@login_required(login_url='login_page')
def purchaseorder_add(request,purchaseorder_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if purchaseorder_id == 0:
            form = PkpurchaseorderForm()
        else:
            purchaseorder=PkpurchaseorderInfo.objects.get(pk=purchaseorder_id)
            form = PkpurchaseorderForm(instance=purchaseorder)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                }
        return render(request, "asset_mgt_app/pk_purchaseorder_add.html", context)
    else:
        if purchaseorder_id == 0:
            form = PkpurchaseorderForm(request.POST)
            if form.is_valid():
                # Generate Random purchaseorder number
                try:
                    last_id = PkpurchaseorderInfo.objects.latest('id').id
                    purchaseorder_num_next = str('PO_') + str(
                        int(((PkpurchaseorderInfo.objects.get(id=last_id)).po_num).replace('PO_','')) + 1)
                except ObjectDoesNotExist:
                    purchaseorder_num_next = str('PO_') + str(1000000)
                form.save()
                print("PkpurchaseorderInfo Form is Valid")
                last_id = (PkpurchaseorderInfo.objects.latest('id')).id
                PkpurchaseorderInfo.objects.filter(id=last_id).update(po_num=purchaseorder_num_next)
                messages.success(request, 'Record Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
                # return redirect('/SMS/purchaseorder_update/')
            else:
                print("PkpurchaseorderInfo Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            purchaseorder = PkpurchaseorderInfo.objects.get(pk=purchaseorder_id)
            form = PkpurchaseorderForm(request.POST,instance=purchaseorder)
            if form.is_valid():
                form.save()
                print("PkpurchaseorderForm Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("PkpurchaseorderForm Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

# List purchaseorder
@login_required(login_url='login_page')
def purchaseorder_list(request):
    first_name = request.session.get('first_name')
    context = {'purchaseorder_list' : PkpurchaseorderInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_purchaseorder_list.html",context)

#Delete purchaseorder
@login_required(login_url='login_page')
def purchaseorder_delete(request,purchaseorder_id):
    purchaseorder = PkpurchaseorderInfo.objects.get(pk=purchaseorder_id)
    purchaseorder.delete()
    return redirect('/SMS/purchaseorder_list')