from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from ..forms import POdimensionForm,PkpurchaseorderForm
from ..models import POdimension,PkneedassessmentInfo,PkpurchaseorderInfo
from django.shortcuts import render, redirect
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
            purchaseorder_id = PkpurchaseorderInfo.objects.get(pk=purchaseorder_id).id
            print('purchaseorder_id',purchaseorder_id)
            purchaseorder_num = PkpurchaseorderInfo.objects.get(pk=purchaseorder_id).po_assessment_num
            print('purchaseorder_num',purchaseorder_num)
            request.session['purchaseorder_id'] = purchaseorder_id
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

@login_required(login_url='login_page')
def po_dimension_cancel(request,needassessment_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    purchaseorder_id=request.session.get('purchaseorder_id')
    return redirect('/SMS/purchaseorder_update/' + str(purchaseorder_id))
@login_required(login_url='login_page')
def po_dimension_add(request, po_dimension_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    po_assessment_num_id=request.session.get('po_assessment_id')
    if request.method == "GET":
        if po_dimension_id == 0:
            form = POdimensionForm()
        else:
            po_dimensioninfo = POdimension.objects.get(pk=po_dimension_id)
            form = POdimensionForm(instance=po_dimensioninfo)
        context={
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'po_assessment_num_id': po_assessment_num_id,
        }
        return render(request, "asset_mgt_app/po_dimension_add.html", context)
    else:
        if po_dimension_id == 0:
            form = POdimensionForm(request.POST)
            if form.is_valid():
                form.save()
                try:
                    last_id = POdimension.objects.latest('id').id
                    po_item_num_next = str('Item_') + str(int(1000000 + last_id))
                except ObjectDoesNotExist:
                    po_item_num_next = str('Item_') + str(1000000)
                last_id = POdimension.objects.latest('id').id
                POdimension.objects.filter(id=last_id).update(nad_item=po_item_num_next)
                print("Main Form Saved")
                messages.success(request, "Record Updated Successfully")
            else:
                print("Main form not saved")
                messages.error(request, "Record Not Updated Successfully")
        else:
            po_dimensioninfo = POdimension.objects.get(pk=po_dimension_id)
            form = POdimensionForm(request.POST, instance=po_dimensioninfo)
            if form.is_valid():
                form.save()
                print("Main Form Saved")
                messages.success(request,"Record Updated Successfully")
            else:
                print("Main form not saved")
                messages.error(request,"Record Not Updated Successfully")
        # return redirect('/SMS/needassessment_list')
        return redirect(request.META['HTTP_REFERER'])
@login_required(login_url='login_page')
def po_dimension_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    context = {
        'user_id': user_id,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/po_dimension_list.html", context)
@login_required(login_url='login_page')
def po_dimension_delete(request, po_dimension_id):
    po_dimensioninfo = POdimension.objects.get(pk=po_dimension_id)
    po_dimensioninfo.delete()
    return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/sales_list')