from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
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
        form = PkpurchaseorderForm(request.POST, request.FILES)
        if form.is_valid():
            customer_po_num = form.cleaned_data['po_num']
            if not PkpurchaseorderInfo.objects.filter(po_num=customer_po_num).exclude(id=purchaseorder_id).exists():
                if purchaseorder_id == 0:
                    print("Inside post add")
                    form.save()
                    print("PkpurchaseorderForm Form is Valid")
                    messages.success(request, 'Record Updated Successfully')
                else:
                    print("Inside post edit")
                    purchaseorder = PkpurchaseorderInfo.objects.get(pk=purchaseorder_id)
                    form = PkpurchaseorderForm(request.POST, request.FILES, instance=purchaseorder)
                    form.save()
                    print("PkpurchaseorderForm Form is Valid")
                    messages.success(request, 'Record Updated Successfully')

            else:
                print("Duplicate customer PO found")
                messages.error(request, 'Please enter a Unique PO Number.')
            return redirect(request.META['HTTP_REFERER'])
        else:
            print("PkpurchaseorderInfo Form is Not Valid")
            messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])

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
    # Create JSON response data
    data = {
        'customer_name': customer_name,
        'customer_id': customer_id,
    }

    # Return JSON response
    return JsonResponse(data)