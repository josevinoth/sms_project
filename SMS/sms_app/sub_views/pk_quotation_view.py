from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from ..forms import PkquotationForm
from ..models import User_extInfo,Nadimension,PkstockpurchasesInfo,PkquotationInfo,PkquotationsummaryInfo,Costtype,Pkstocktype,Stockdescription,pk_itemInfo,pk_itemdescriptionInfo
from django.shortcuts import render, redirect
from django.contrib import messages


@transaction.atomic
@login_required(login_url='login_page')
def pk_quotation_add(request, quotation_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    na_assessment_num_id = request.session.get('na_assessment_id')
    na_customer_name_id = request.session.get('na_customer_name_id')
    na_customer_new_name_id = request.session.get('na_customer_new_name')

    try:
        user_ext = User_extInfo.objects.get(user=user_id)
        role = user_ext.emp_role
        role_id = user_ext.emp_role.id
    except User_extInfo.DoesNotExist:
        messages.error(request, "User role not found.")
        return redirect('some_error_page')

    if request.method == "GET":
        if quotation_id == 0:
            print("Inside PK quotation GET add")

            # # ✅ Retrieve stored values (IDs) from session safely
            # pkqt_cost_type_id = request.session.get('last_cost_type')
            # pkqt_job_type_id = request.session.get('last_job_type')
            # pkqt_job_type_quant_id = request.session.get('last_job_type_quantity')
            # pkqt_stock_type_id = request.session.get('last_stock_type_quantity')
            # pkqt_stock_description_id = request.session.get('last_stock_desc_quantity')
            # pkqt_item_type_id = request.session.get('last_item_type')
            # pkqt_item_description_id = request.session.get('last_item_desc')
            #
            # initial_data = {
            #     'pkqt_cost_type': Costtype.objects.filter(id=pkqt_cost_type_id).first(),
            #     'pkqt_requirement': Nadimension.objects.filter(id=pkqt_job_type_id).first() if pkqt_job_type_id else None,
            #     'pkqt_na_quantity': pkqt_job_type_quant_id,
            #     'pkqt_stock_type': Pkstocktype.objects.filter(id=pkqt_stock_type_id).first() if pkqt_stock_type_id else None,
            #     'pkqt_stock_description': Stockdescription.objects.filter(id=pkqt_stock_description_id).first() if pkqt_stock_description_id else None,
            #     'pkqt_item': pk_itemInfo.objects.filter(id=pkqt_item_type_id).first() if pkqt_item_type_id else None,
            #     'pkqt_itemdescription': pk_itemdescriptionInfo.objects.filter(id=pkqt_item_description_id).first() if pkqt_item_description_id else None,
            #
            # }
            # print(initial_data)

            # form = PkquotationForm(initial=initial_data)
            form = PkquotationForm
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'na_assessment_num_id': na_assessment_num_id,
                'na_customer_name_id': na_customer_name_id,
                'na_customer_new_name_id': na_customer_new_name_id,
                'role': role,
                'role_id': role_id,
                'quotation_list': PkquotationInfo.objects.filter(pkqt_assessment_num=na_assessment_num_id),
            }
        else:
            print("Inside PK quotation get edit")
            quotation = PkquotationInfo.objects.get(pk=quotation_id)
            form = PkquotationForm(instance=quotation)
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'role': role,
                'role_id': role_id,
                'na_assessment_num_id': na_assessment_num_id,
                'quotation_list': PkquotationInfo.objects.filter(pkqt_assessment_num=na_assessment_num_id),
            }
        return render(request, "asset_mgt_app/pk_quotation_add.html", context)

    else:  # POST request
        if quotation_id == 0:
            print("Inside PK quotation post add")
            form = PkquotationForm(request.POST)
        else:
            print("Inside PK quotation post Edit")
            quotation = PkquotationInfo.objects.get(pk=quotation_id)
            form = PkquotationForm(request.POST, instance=quotation)

        if form.is_valid():
            print('Form is valid')
            cost_type_id = request.POST.get('pkqt_cost_type')

            if int(cost_type_id) == 8:  # For stock-related cost types
                stock_purchase_num_id = request.POST.get('pkqt_stock_purchase_number')
                if stock_purchase_num_id:
                    try:
                        stock_purchase = PkstockpurchasesInfo.objects.get(id=stock_purchase_num_id)
                        stock_purchase_num = stock_purchase.sp_purchase_num
                        stock_qty_available = stock_purchase.sp_quantity_reduced

                        stock_qty_str = request.POST.get('pkqt_quantity', None)
                        if not stock_qty_str:
                            messages.error(request, 'Quantity is required.')
                            return redirect(request.META['HTTP_REFERER'])

                        try:
                            stock_qty = int(stock_qty_str)
                        except ValueError:
                            messages.error(request, 'Invalid quantity value. It should be a number.')

                            # ✅ Store selected values in session even when validation fails
                            request.session['last_cost_type'] = form.cleaned_data.get(
                                'pkqt_cost_type').id if form.cleaned_data.get('pkqt_cost_type') else None

                            return redirect(request.META['HTTP_REFERER'])

                        # ✅ Uncomment this if stock validation is needed
                        # if stock_qty <= 0:
                        #     messages.error(request, 'Quantity should be greater than 0.')
                        #     return redirect(request.META['HTTP_REFERER'])
                        # elif stock_qty > stock_qty_available:
                        #     error_message = (
                        #         f'Quantity should be less than or equal to available stock: '
                        #         f'{stock_purchase_num}. Available quantity: {stock_qty_available}.'
                        #     )
                        #     messages.error(request, error_message)
                        #     return redirect(request.META['HTTP_REFERER'])

                        form.save()
                        print("Quotation form is valid and stock updated.")
                        messages.success(request, 'Stock Updated Successfully')

                    except PkstockpurchasesInfo.DoesNotExist:
                        pass  # Ignore if stock purchase number is not found
                else:
                    form.save()
                    messages.warning(request, 'Stock saved without Stock Purchase Number')
            else:
                form.save()
                messages.success(request, 'Quotation Updated Successfully')

            # ✅ Store selected values in session after a successful form save
            # request.session['last_cost_type'] = form.cleaned_data.get('pkqt_cost_type').id if form.cleaned_data.get('pkqt_cost_type') else None
            # request.session['last_job_type'] = form.cleaned_data.get('pkqt_requirement').id if form.cleaned_data.get('pkqt_requirement') else None
            # request.session['last_job_type_quantity'] = form.cleaned_data.get('pkqt_na_quantity') if form.cleaned_data.get('pkqt_na_quantity') else None
            # request.session['last_stock_type_quantity'] = form.cleaned_data.get('pkqt_stock_type').id if form.cleaned_data.get('pkqt_stock_type') else None
            # request.session['last_stock_desc_quantity'] = form.cleaned_data.get('pkqt_stock_description').id if form.cleaned_data.get('pkqt_stock_description') else None
            # request.session['last_item_type'] = form.cleaned_data.get('pkqt_item').id if form.cleaned_data.get('pkqt_item') else None
            # request.session['last_item_desc'] = form.cleaned_data.get('pkqt_itemdescription').id if form.cleaned_data.get('pkqt_itemdescription') else None
            # request.session['last_box_id_clearance_l'] = form.cleaned_data.get('pkqt_box_id_clearance_l') if form.cleaned_data.get('pkqt_box_id_clearance_l') else None
            # request.session['last_box_id_clearance_w'] = form.cleaned_data.get('pkqt_box_id_clearance_w') if form.cleaned_data.get('pkqt_box_id_clearance_w') else None
            # request.session['last_box_id_clearance_h'] = form.cleaned_data.get('pkqt_box_id_clearance_h') if form.cleaned_data.get('pkqt_box_id_clearance_h') else None
            # request.session['last_box_od_clearance_l'] = form.cleaned_data.get('pkqt_box_od_clearance_l') if form.cleaned_data.get('pkqt_box_od_clearance_l') else None
            # request.session['last_box_od_clearance_w'] = form.cleaned_data.get('pkqt_box_od_clearance_w') if form.cleaned_data.get('pkqt_box_od_clearance_w') else None
            # request.session['last_box_od_clearance_h'] = form.cleaned_data.get('pkqt_box_od_clearance_h') if form.cleaned_data.get('pkqt_box_od_clearance_h') else None

            return redirect('/SMS/pk_quotation_insert/')

        else:
            print("Quotation form is not valid.")
            messages.error(request, 'Record Not Updated Successfully')

            # Debugging: Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")
                    messages.error(request, f"Error in {field}: {error}")

        return redirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


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
    requirement_type = []
    ct_assessment_num_id = request.GET.get('ct_assessment_num_id')
    print('ct_assessment_num_id',ct_assessment_num_id)
    na_dimension_id = Nadimension.objects.filter(nad_assess_num=ct_assessment_num_id)
    for a in na_dimension_id:
        requirement_type_id.append(a.id)
        requirement_type_val.append(str(a.nad_item)+str(' (')+str(a.nad_type_of_req)+str(' ')+str(a.nad_length)+str('x')+str(a.nad_width)+str('x')+str(a.nad_height)+str(')'))
        requirement_type= str(a.nad_item)
    data = {
        'requirement_type_val': requirement_type_val,
        'requirement_type_id': requirement_type_id,
        'requirement_type': requirement_type,
    }
    return JsonResponse(data)

@login_required(login_url='login_page')
def pk_store_na_dimension_id(request):
    na_dimension_box_val = []
    ct_requirement_id= request.GET.get('ct_requirement_id')
    print('ct_requirement_id',ct_requirement_id)
    # Fetch requirement type from need assessment

    a = Nadimension.objects.get(pk=ct_requirement_id)

    na_dimension_box_val.append(str(a.nad_type_of_req)+str(' (')+str(a.nad_length)+str('x')+str(a.nad_width)+str('x')+str(a.nad_height)+str(')'))
    na_dimension_type =str(a.nad_dimension_type)
    na_dimension_type_id = str(a.nad_dimension_type.id)
    na_uom=str(a.nad_uom)
    na_length=str(a.nad_length)
    na_width=str(a.nad_width)
    na_height = str(a.nad_height)
    na_quantity = str(a.nad_quantity)


    data = {
        'na_dimension_box_val': na_dimension_box_val,
        'na_dimension_type': na_dimension_type,
        'na_dimension_type_id': na_dimension_type_id,
        'na_uom': na_uom,
        'na_length': na_length,
        'na_width': na_width,
        'na_height': na_height,
        'na_quantity': na_quantity,
    }
    return JsonResponse(data)