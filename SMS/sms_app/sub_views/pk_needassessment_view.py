from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from ..forms import PkneedassessmentForm,NadimensionForm
from ..models import  PkquotationsummaryInfo,PkquotationInfo,POdimension,PkpurchaseorderInfo,PkcostingsummaryInfo,PkcostingInfo,commentsInfo,User_extInfo,PkneedassessmentInfo,Nadimension
from django.shortcuts import render, redirect
from random import randint
from django.contrib import messages

@login_required(login_url='login_page')
def needassessment_add(request,needassessment_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    if request.method == "GET":
        if needassessment_id == 0:
            form = PkneedassessmentForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'role': role,
            }
        else:
            needassessment=PkneedassessmentInfo.objects.get(pk=needassessment_id)
            form = PkneedassessmentForm(instance=needassessment)
            needassessment_id=PkneedassessmentInfo.objects.get(pk=needassessment_id).id
            needassessment_num=PkneedassessmentInfo.objects.get(pk=needassessment_id).na_assessment_num
            request.session['na_assessment_id'] = needassessment_id
            request.session['na_assessment_num'] = needassessment_num
            na_dimension_list=Nadimension.objects.filter(nad_assess_num=needassessment_id)
            comments_list= commentsInfo.objects.filter(comments_ref=needassessment_num)
            context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'role': role,
                'na_dimension_list': na_dimension_list,
                'comments_list': comments_list,
                }
        return render(request, "asset_mgt_app/pk_needassessment_add.html", context)
    else:
        if needassessment_id == 0:
            form = PkneedassessmentForm(request.POST,request.FILES)
            if form.is_valid():
                # Generate Random Assessment number
                try:
                    last_id = PkneedassessmentInfo.objects.latest('id').id
                    assessment_num_next = str('Assess_') + str(int(((PkneedassessmentInfo.objects.get(id=last_id)).na_assessment_num).replace('Assess_', '')) + 1)
                except ObjectDoesNotExist:
                    assessment_num_next = str('Assess_') + str(randint(10000, 99999))
                form.save()
                print("needassessment Form is Valid")
                last_id = (PkneedassessmentInfo.objects.latest('id')).id
                PkneedassessmentInfo.objects.filter(id=last_id).update(na_assessment_num=assessment_num_next)
                messages.success(request, 'Record Updated Successfully')
                return redirect('/SMS/needassessment_update/'+ str(last_id))
            else:
                print("needassessment Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            needassessment = PkneedassessmentInfo.objects.get(pk=needassessment_id)
            form = PkneedassessmentForm(request.POST,request.FILES,instance=needassessment)
            if form.is_valid():
                form.save()
                print("needassessment Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("needassessment Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

# List needassessment
@login_required(login_url='login_page')
def needassessment_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    context = {
            'needassessment_list' : PkneedassessmentInfo.objects.all(),
            'first_name': first_name,
            'role': role,
        }
    return render(request,"asset_mgt_app/pk_needassessment_list.html",context)

#Delete needassessment
@login_required(login_url='login_page')
def needassessment_delete(request,needassessment_id):
    needassessment = PkneedassessmentInfo.objects.get(pk=needassessment_id)
    assessment_num = needassessment.na_assessment_num

    # Deleting PkcostingInfo objects
    Pkcosting_delete(assessment_num)

    # Deleting Pkcosting summary objects
    Pkcostingsummary_delete(assessment_num)

    # Deleting Pkpurchaseorders objects
    Pkpurchaseorder_delete(assessment_num)

    # Deleting Pkpurchaseorders dims objects
    Pkpurchaseorder_dim_delete(assessment_num)

    #Deleting Pkquotations objects
    Pkquotation_delete(assessment_num)

    # Deleting quotation summary objects
    Pkquotation_summary_delete(assessment_num)

    # Deleting need assessment objects
    needassessment.delete()

    return redirect('/SMS/needassessment_list')


def Pkcosting_delete(assessment_num):
    try:
        # Fetch the queryset for the matching records
        costing_objects = PkcostingInfo.objects.filter(ct_assessment_num=assessment_num)

        # Check if any objects were found
        if costing_objects.exists():
            # Delete the objects
            costing_objects.delete()
        else:
            # Handle the case where no objects were found, if needed
            print("No matching costing info found to delete.")
    except Exception as e:
        # Handle any unexpected exceptions
        print(f"An error occurred: {e}")


def Pkcostingsummary_delete(assessment_num):
    # Deleting PkcostingsummaryInfo objects
    try:
        costingsummary_objects = PkcostingsummaryInfo.objects.filter(cs_assessment_num=assessment_num)
        if costingsummary_objects.exists():
            costingsummary_objects.delete()
        else:
            print("No matching PkcostingsummaryInfo found to delete.")
    except Exception as e:
        print(f"An error occurred while deleting PkcostingsummaryInfo: {e}")


def Pkpurchaseorder_delete(assessment_num):
    # Deleting PkpurchaseorderInfo objects
    try:
        customer_po_objects = PkpurchaseorderInfo.objects.filter(po_assessment_num=assessment_num)
        if customer_po_objects.exists():
            customer_po_objects.delete()
        else:
            print("No matching PkpurchaseorderInfo found to delete.")
    except Exception as e:
        print(f"An error occurred while deleting PkpurchaseorderInfo: {e}")


def Pkpurchaseorder_dim_delete(assessment_num):
    # Deleting Pkpurchaseorder dimension objects
    try:
        customer_po_dim_objects = POdimension.objects.filter(pod_assess_num=assessment_num)
        if customer_po_dim_objects.exists():
            customer_po_dim_objects.delete()
        else:
            print("No matching Pkpurchaseorder dimensions found to delete.")
    except Exception as e:
        print(f"An error occurred while deleting Pkpurchaseorder dimensions: {e}")


def Pkquotation_delete(assessment_num):
    # Deleting PkquotationInfo objects
    try:
        quotation_objects = PkquotationInfo.objects.filter(pkqt_assessment_num=assessment_num)
        if quotation_objects.exists():
            quotation_objects.delete()
        else:
            print("No matching PkquotationInfo found to delete.")
    except Exception as e:
        print(f"An error occurred while deleting PkquotationInfo: {e}")


def Pkquotation_summary_delete(assessment_num):
    # Deleting PkquotationsummaryInfo objects
    try:
        quotationsummary_objects = PkquotationsummaryInfo.objects.filter(qs_assessment_num=assessment_num)
        if quotationsummary_objects.exists():
            quotationsummary_objects.delete()
        else:
            print("No matching PkquotationsummaryInfo found to delete.")
    except Exception as e:
        print(f"An error occurred while deleting PkquotationsummaryInfo: {e}")


@login_required(login_url='login_page')
def na_dimension_cancel(request,needassessment_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    needassessment_id=request.session.get('na_assessment_id')
    return redirect('/SMS/needassessment_update/' + str(needassessment_id))
@login_required(login_url='login_page')
def na_dimension_add(request, na_dimension_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    na_assessment_num_id=request.session.get('na_assessment_id')
    if request.method == "GET":
        if na_dimension_id == 0:
            form = NadimensionForm()
        else:
            na_dimensioninfo = Nadimension.objects.get(pk=na_dimension_id)
            form = NadimensionForm(instance=na_dimensioninfo)
        context={
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'na_assessment_num_id': na_assessment_num_id,
        }
        return render(request, "asset_mgt_app/na_dimension_add.html", context)
    else:
        if na_dimension_id == 0:
            form = NadimensionForm(request.POST)
            if form.is_valid():
                form.save()
                try:
                    last_id = Nadimension.objects.latest('id').id
                    na_item_num_next = str('Item_') + str(int(1000000 + last_id))
                except ObjectDoesNotExist:
                    na_item_num_next = str('Item_') + str(1000000)
                last_id = Nadimension.objects.latest('id').id
                Nadimension.objects.filter(id=last_id).update(nad_item=na_item_num_next)
                print("Main Form Saved")
                messages.success(request, "Record Updated Successfully")
            else:
                print("Main form not saved")
                messages.error(request, "Record Not Updated Successfully")
        else:
            na_dimensioninfo = Nadimension.objects.get(pk=na_dimension_id)
            form = NadimensionForm(request.POST, instance=na_dimensioninfo)
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
def na_dimension_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    context = {
        'user_id': user_id,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/na_dimension_list.html", context)
@login_required(login_url='login_page')
def na_dimension_delete(request, na_dimension_id):
    na_dimensioninfo = Nadimension.objects.get(pk=na_dimension_id)
    na_dimensioninfo.delete()
    return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/sales_list')