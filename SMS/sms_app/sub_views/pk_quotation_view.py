import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..forms import PkquotationForm
from ..models import Nadimension,PkstockpurchasesInfo,PkquotationInfo,PkquotationsummaryInfo
from django.shortcuts import render, redirect

from django.contrib import messages

@login_required(login_url='login_page')
def pk_quotation_add(request,quotation_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    na_assessment_num_id = request.session.get('na_assessment_id')
    na_customer_name_id = request.session.get('na_customer_name_id')
    print('na_customer_name_id', na_customer_name_id)
    if request.method == "GET":
        if quotation_id == 0:
            form = PkquotationForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'na_assessment_num_id': na_assessment_num_id,
                'na_customer_name_id': na_customer_name_id,
                'quotation_list': PkquotationInfo.objects.filter(pkqt_assessment_num=na_assessment_num_id),
            }
        else:
            quotation = PkquotationInfo.objects.get(pk=quotation_id)
            form = PkquotationForm(instance=quotation)
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'na_assessment_num_id': na_assessment_num_id,
                'quotation_list': PkquotationInfo.objects.filter(pkqt_assessment_num=na_assessment_num_id),
            }
        return render(request, "asset_mgt_app/pk_quotation_add.html", context)
    else:
        if quotation_id == 0:
            print("Inside PK quotation post add")
            form = PkquotationForm(request.POST)
            if form.is_valid():
                cost_type_id = request.POST.get('pkqt_cost_type')
                print('cost_type_id', cost_type_id)
                if int(cost_type_id) == 8:
                    stock_purchase_num_id = request.POST.get('pkqt_stock_purchase_number')
                    stock_purchase_num = PkstockpurchasesInfo.objects.get(id=stock_purchase_num_id).sp_purchase_num
                    stock_qty = request.POST.get('pkqt_quantity')
                    stock_qty_available = PkstockpurchasesInfo.objects.get(id=stock_purchase_num_id).sp_quantity_reduced
                    if int(stock_qty) <= 0:
                        messages.error(request, 'Quantity should be greater than 0')
                        return redirect(request.META['HTTP_REFERER'])
                    elif int(stock_qty) > stock_qty_available:
                        error_message = f'Quantity should be less than or equal to available stock {stock_purchase_num} quantity {stock_qty_available}'
                        messages.error(request, error_message)
                        return redirect(request.META['HTTP_REFERER'])
                    else:
                        form.save()
                        print("quotation Form is Valid")
                        # last_id = (PkquotationInfo.objects.latest('id')).id
                        # stock_status = (PkquotationInfo.objects.latest('id')).pkqt_stock_status
                        # print('stock_status',stock_status)
                        # if stock_status ==2:
                        #     messages.success(request, 'Stock Successfully Retrieved & Supplied')
                        #     update_reduced_dimensions(stock_purchase_num,last_id)
                        # else:
                        #     messages.success(request, 'Stock Updated Successfully')
                        messages.success(request, 'Stock Updated Successfully')
                else:
                    form.save()
                    messages.success(request, 'Stock Updated Successfully')
                # return redirect('/SMS/pk_quotation_update/'+str(last_id))
                return redirect('/SMS/pk_quotation_insert/')
            else:
                print("quotation Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("Inside PK quotation post Edit")
            quotation = PkquotationInfo.objects.get(pk=quotation_id)
            form = PkquotationForm(request.POST, instance=quotation)
            if form.is_valid():
                form.save()
                print("quotation Form is Valid")
                stock_purchase_num = PkquotationInfo.objects.get(pk=quotation_id).pkqt_stock_purchase_number
                last_id = quotation_id
                cost_type_id = PkquotationInfo.objects.get(pk=quotation_id).pkqt_cost_type.id
                if int(cost_type_id) == 8:
                    stock_purchase_num_id = request.POST.get('pkqt_stock_purchase_number')
                    stock_purchase_num = PkstockpurchasesInfo.objects.get(id=stock_purchase_num_id).sp_purchase_num
                    stock_qty = request.POST.get('pkqt_quantity')
                    stock_qty_available = PkstockpurchasesInfo.objects.get(id=stock_purchase_num_id).sp_quantity_reduced
                    if int(stock_qty) <= 0:
                        messages.error(request, 'Quantity should be greater than 0')
                        return redirect(request.META['HTTP_REFERER'])
                    elif int(stock_qty) > stock_qty_available:
                        error_message = f'Quantity should be less than or equal to available stock {stock_purchase_num} quantity {stock_qty_available}'
                        messages.error(request, error_message)
                        return redirect(request.META['HTTP_REFERER'])
                    else:
                        form.save()
                        print("quotation Form is Valid")
                        # last_id = (PkquotationInfo.objects.latest('id')).id
                        # stock_status = (PkquotationInfo.objects.latest('id')).pkqt_stock_status
                        # print('stock_status',stock_status)
                        # if stock_status ==2:
                        #     messages.success(request, 'Stock Successfully Retrieved & Supplied')
                        #     update_reduced_dimensions(stock_purchase_num,last_id)
                        # else:
                        #     messages.success(request, 'Stock Updated Successfully')
                        messages.success(request, 'Stock Updated Successfully')
                else:
                    form.save()
                    messages.success(request, 'Stock Updated Successfully')
            else:
                print("quotation Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

# List quotation
@login_required(login_url='login_page')
def pk_quotation_list(request):
    first_name = request.session.get('first_name')
    context = {'pk_quotaiton_list' : PkquotationInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_quotation_list.html",context)

#Delete quotation
@login_required(login_url='login_page')
def pk_quotation_delete(request,quotation_id):
    quotation = PkquotationInfo.objects.get(pk=quotation_id)
    quotation.delete()
    # return redirect('/SMS/pK_quotation_cancel')
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def pK_quotation_cancel(request):
    assessment_num_val = request.session.get('na_assessment_id')
    quotation_summary_id=PkquotationsummaryInfo.objects.get(qs_assessment_num=assessment_num_val).id
    return redirect('/SMS/pk_quotationsummary_update/' + str(quotation_summary_id))

@login_required(login_url='login_page')
def pk_get_pk_requirement_type(request):
    requirement_type_id = []
    requirement_type_val = []
    ct_assessment_num_id = request.GET.get('ct_assessment_num_id')
    print('ct_assessment_num_id',ct_assessment_num_id)
    # Fetch requirement type from Need Assessment dimension
    na_dimension_id = Nadimension.objects.filter(nad_assess_num=ct_assessment_num_id)
    for a in na_dimension_id:
        requirement_type_id.append(a.id)
        requirement_type_val.append(str(a.nad_item)+str(' (')+str(a.nad_type_of_req)+str(' ')+str(a.nad_length)+str('x')+str(a.nad_width)+str('x')+str(a.nad_height)+str(')'))

    data = {
        'requirement_type_val': requirement_type_val,
        'requirement_type_id': requirement_type_id,
    }
    return JsonResponse(data)

@login_required(login_url='login_page')
def pk_store_na_dimension_id(request):
    na_dimension_box_val = []
    ct_requirement_id= request.GET.get('ct_requirement_id')
    # Fetch requirement type from need assessment
    a = Nadimension.objects.get(pk=ct_requirement_id)
    na_dimension_box_val.append(str(a.nad_type_of_req)+str(' (')+str(a.nad_length)+str('x')+str(a.nad_width)+str('x')+str(a.nad_height)+str(')'))

    data = {
        'na_dimension_box_val': na_dimension_box_val,
    }
    return JsonResponse(data)