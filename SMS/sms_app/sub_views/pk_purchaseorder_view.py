from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from ..forms import PkpurchaseorderForm
from ..models import PkneedassessmentInfo,PkpurchaseorderInfo
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
            form = PkpurchaseorderForm(request.POST,request.FILES)
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
            form = PkpurchaseorderForm(request.POST,request.FILES,instance=purchaseorder)
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

@login_required(login_url='login_page')
def pk_get_customer(request):
    customer_id = []
    customer_name = []
    assessment_id = request.GET.get('assessment_num')
    # Fetch item_description Details
    customer_id = PkneedassessmentInfo.objects.get(pk=assessment_id).na_customer_name.id
    customer_name = PkneedassessmentInfo.objects.get(pk=assessment_id).na_customer_name.cu_name
    print('customer_name',customer_name)
    print('customer_id',customer_id)
    # Create JSON response data
    data = {
        'customer_name': customer_name,
        'customer_id': customer_id,
    }

    # Return JSON response
    return JsonResponse(data)