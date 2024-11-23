from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from ..forms import POdimensionForm,PkpurchaseorderForm
from ..models import User_extInfo,Nadimension,POdimension,PkneedassessmentInfo,PkpurchaseorderInfo,PkquotationsummaryInfo
from django.shortcuts import render, redirect
from django.contrib import messages
from ..views import Pkcosting_delete,Pkcostingsummary_delete,Pkpurchaseorder_delete,Pkpurchaseorder_dim_delete


@login_required(login_url='login_page')
def purchaseorder_add(request,purchaseorder_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = User_extInfo.objects.get(user=user_id).emp_role.id
    if request.method == "GET":
        if purchaseorder_id == 0:
            form = PkpurchaseorderForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'role': role,
                'role_id': role_id,
            }
        else:
            purchaseorder=PkpurchaseorderInfo.objects.get(pk=purchaseorder_id)
            form = PkpurchaseorderForm(instance=purchaseorder)
            purchaseorder_id = PkpurchaseorderInfo.objects.get(pk=purchaseorder_id).id
            purchaseorder_num = PkpurchaseorderInfo.objects.get(pk=purchaseorder_id).po_assessment_num
            request.session['purchaseorder_id'] = purchaseorder_id
            na_id = PkpurchaseorderInfo.objects.get(pk=purchaseorder_id).po_assessment_num.id
            print('na_id',na_id)
            request.session['ses_na_id'] = na_id
            po_dimension_list = POdimension.objects.filter(pod_po_num=purchaseorder_id)
            context={
                    'form': form,
                    'first_name': first_name,
                    'user_id': user_id,
                    'na_id': na_id,
                    'po_dimension_list': po_dimension_list,
                    'role': role,
                    'role_id': role_id,
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
            last_id = PkpurchaseorderInfo.objects.order_by('-id').values_list('id', flat=True).first()
            # return redirect(request.META['HTTP_REFERER'])
            return redirect('/SMS/purchaseorder_update/' + str(last_id))
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
    assessment_num = purchaseorder.po_assessment_num

    # Deleting PkcostingInfo objects
    Pkcosting_delete(assessment_num)

    # Deleting Pkcosting summary objects
    Pkcostingsummary_delete(assessment_num)

    # Deleting Pkpurchaseorders objects
    Pkpurchaseorder_delete(assessment_num)

    # Deleting Pkpurchaseorders dims objects
    Pkpurchaseorder_dim_delete(assessment_num)

    return redirect('/SMS/purchaseorder_list')


@login_required(login_url='login_page')
def pk_get_customer(request):
    assessment_id = request.GET.get('assessment_num')  # Get the assessment ID from the request

    # Fetch the assessment record (returns None if not found)
    need_assessment = PkneedassessmentInfo.objects.filter(pk=assessment_id).first()

    if not need_assessment:
        # Return error if the assessment ID is invalid
        return JsonResponse({'error': 'Assessment not found'}, status=404)

    # Safely retrieve customer-related details
    customer_id = need_assessment.na_customer_name.id if need_assessment.na_customer_name else None
    customer_name = need_assessment.na_customer_name.cu_name if need_assessment.na_customer_name else None
    customer_new_name = need_assessment.na_customer_new_name if need_assessment.na_customer_new_name else None

    # Fetch the Quotation Number (returns None if not found)
    quotation_num = PkquotationsummaryInfo.objects.filter(
        qs_assessment_num=assessment_id, qs_status=5
    ).first()
    quotation_num_id = quotation_num.id if quotation_num else ""

    # Prepare the JSON response data
    data = {
        'customer_name': customer_name,
        'customer_new_name': customer_new_name,
        'customer_id': customer_id,
        'quotation_num_id': quotation_num_id,
    }

    return JsonResponse(data)


@login_required(login_url='login_page')
def po_dimension_cancel(request,needassessment_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    purchaseorder_id=request.session.get('purchaseorder_id')
    return redirect('/SMS/purchaseorder_update/' + str(purchaseorder_id))
@login_required(login_url='login_page')
def po_dimension_add(request, po_dimension_id=0):
    global na_assessment_num_id
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    purchaseorder_id=request.session.get('purchaseorder_id')
    if request.method == "GET":
        if po_dimension_id == 0:
            form = POdimensionForm()
            na_assessment_num_id = request.session.get('ses_na_id')
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'purchaseorder_id': purchaseorder_id,
                'na_assessment_num_id': na_assessment_num_id,
            }
        else:
            po_dimensioninfo = POdimension.objects.get(pk=po_dimension_id)
            form = POdimensionForm(instance=po_dimensioninfo)
            context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
            }
        return render(request, "asset_mgt_app/po_dimension_add.html", context)
    else:
        if po_dimension_id == 0:
            form = POdimensionForm(request.POST)
        else:
            dimension = POdimension.objects.get(pk=po_dimension_id)
            form = POdimensionForm(request.POST, instance=dimension)
        if form.is_valid():
            form.save()
            if po_dimension_id == 0:
                messages.success(request, 'Record Saved Successfully')
            else:
                messages.success(request, 'Record Updated Successfully')
        else:
            messages.error(request, 'Error: Please correct the errors below.')

        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error in {field}: {error}")
                messages.error(request, f"Error in {field}: {error}")
        return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/needassessment_list')
@login_required(login_url='login_page')
def po_dimension_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    po_dimension_list=POdimension.objects.all()
    context = {
        'user_id': user_id,
        'first_name': first_name,
        'po_dimension_list': po_dimension_list,
    }
    return render(request, "asset_mgt_app/po_dimension_list.html", context)
@login_required(login_url='login_page')
def po_dimension_delete(request, po_dimension_id):
    po_dimensioninfo = POdimension.objects.get(pk=po_dimension_id)
    po_dimensioninfo.delete()
    return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/sales_list')
@login_required(login_url='login_page')
def pk_get_po_requirement_type(request):
    requirement_type_val = []
    ct_assessment_num_id = request.GET.get('ct_assessment_num')
    print('Assessment Number received:', ct_assessment_num_id)  # Debug log

    # Query Nadimension and ensure it fetches correct data
    na_dimension_id = Nadimension.objects.filter(nad_assess_num=ct_assessment_num_id)
    if na_dimension_id.exists():
        for a in na_dimension_id:
            requirement_type_val.append(str(a.nad_item))  # Collect nad_item values
    else:
        print('No records found for assessment number:', ct_assessment_num_id)

    # Return JSON response
    data = {
        'requirement_type_val': requirement_type_val,
    }
    print('Response data:', data)  # Log response data for debugging
    return JsonResponse(data)
