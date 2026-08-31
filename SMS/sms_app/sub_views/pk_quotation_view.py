from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, F
from django.http import JsonResponse
from ..forms import PkquotationForm
from ..models import User_extInfo,Nadimension,PkstockpurchasesInfo,PkquotationInfo,PkquotationsummaryInfo,Costtype,Pkstocktype,Stockdescription,pk_itemInfo,pk_itemdescriptionInfo,StockMaintenance
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
            # Calculate total_cft_display dynamically for the assessment (Wood ONLY)
            aggregate_cft = PkquotationInfo.objects.filter(
                pkqt_assessment_num=na_assessment_num_id,
                pkqt_cost_type=8,
                pkqt_stock_type=1
            ).aggregate(total=Sum(F('pkqt_sqrt_req') * F('pkqt_na_quantity')))['total']
            project_total_cft = round(aggregate_cft, 3) if aggregate_cft is not None else 0.0

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
                'total_cft_display': project_total_cft,

            }
        else:
            print("Inside PK quotation get edit")
            quotation = PkquotationInfo.objects.get(pk=quotation_id)
            form = PkquotationForm(instance=quotation)
            
            # Calculate total_cft_display dynamically for the assessment (Wood ONLY)
            aggregate_cft = PkquotationInfo.objects.filter(
                pkqt_assessment_num=na_assessment_num_id,
                pkqt_cost_type=8,
                pkqt_stock_type=1
            ).aggregate(total=Sum(F('pkqt_sqrt_req') * F('pkqt_na_quantity')))['total']
            project_total_cft = round(aggregate_cft, 3) if aggregate_cft is not None else 0.0
            
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'role': role,
                'role_id': role_id,
                'na_assessment_num_id': na_assessment_num_id,
                'quotation_list': PkquotationInfo.objects.filter(pkqt_assessment_num=na_assessment_num_id),
                'total_cft_display': project_total_cft,
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
                        # Fetch stock maintenance record using StockMaintenance
                        stock_purchase = StockMaintenance.objects.get(id=stock_purchase_num_id)
                        stock_purchase_num = stock_purchase.sm_stock_purchase_number
                        stock_qty_available = stock_purchase.sm_count

                        stock_qty_str = request.POST.get('pkqt_quantity', None)
                        if not stock_qty_str:
                            messages.error(request, 'Quantity is required.')
                            return redirect(request.META['HTTP_REFERER'])

                        try:
                            stock_qty = float(stock_qty_str)
                        except ValueError:
                            messages.error(request, 'Invalid quantity value. It should be a number.')
                            return redirect(request.META['HTTP_REFERER'])

                        if stock_qty > stock_qty_available:
                            error_message = (
                                f"Insufficient stock for {stock_purchase.sm_partcode.pc_code}. "
                                f"Available: {stock_qty_available}, Requested: {stock_qty}"
                            )
                            messages.error(request, error_message)
                            return redirect(request.META['HTTP_REFERER'])

                            # ✅ Store selected values in session even when validation fails
                            # request.session['last_cost_type'] = form.cleaned_data.get(
                            #     'pkqt_cost_type').id if form.cleaned_data.get('pkqt_cost_type') else None

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

                        quotation = form.save()

                        # Extract relevant fields
                        cost_type = quotation.pkqt_cost_type.id
                        stock_type = quotation.pkqt_stock_type.id
                        assessment_id = quotation.pkqt_assessment_num.id

                        # ✅ Only for cost_type = 8 and Wood stock_type = 1
                        if cost_type == 8 and stock_type == 1:
                            total_cft = PkquotationInfo.objects.filter(
                                pkqt_assessment_num=assessment_id,
                                pkqt_cost_type=8,
                                pkqt_stock_type=1
                            ).aggregate(total=Sum(F('pkqt_sqrt_req') * F('pkqt_na_quantity')))['total'] or 0.0
                            print("total_cft", total_cft)
                            request.session['total_cft_display'] = round(total_cft, 3)
                        else:
                            request.session['total_cft_display'] = 0.0

                        print("Quotation form is valid and stock updated.")
                        messages.success(request, 'Stock Updated Successfully')

                    except StockMaintenance.DoesNotExist:
                        messages.error(request, 'Selected stock purchase record not found.')
                        return redirect(request.META['HTTP_REFERER'])
                else:
                    quotation=form.save()
                    # Extract relevant fields
                    cost_type = quotation.pkqt_cost_type.id
                    stock_type = quotation.pkqt_stock_type.id
                    assessment_id = quotation.pkqt_assessment_num.id

                    # ✅ Only for cost_type = 8 and Wood stock_type = 1
                    if cost_type == 8 and stock_type == 1:
                        total_cft = PkquotationInfo.objects.filter(
                            pkqt_assessment_num=assessment_id,
                            pkqt_cost_type=8,
                            pkqt_stock_type=1
                        ).aggregate(total=Sum(F('pkqt_sqrt_req') * F('pkqt_na_quantity')))['total'] or 0.0
                        print("total_cft", total_cft)
                        request.session['total_cft_display'] = round(total_cft, 3)
                    else:
                        request.session['total_cft_display'] = 0.0

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
    context = {'pk_quotaiton_list' : PkquotationInfo.objects.all().order_by('-id'),'first_name': first_name}
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
    stock_type = request.GET.get('stock_type')
    print('ct_assessment_num_id', ct_assessment_num_id, 'stock_type', stock_type)
    
    if not ct_assessment_num_id:
        return JsonResponse({'requirement_type_val': [], 'requirement_type_id': [], 'requirement_type': ''})

    if str(ct_assessment_num_id).isdigit():
        na_dimension_id = Nadimension.objects.filter(nad_assess_num=ct_assessment_num_id)
    else:
        na_dimension_id = Nadimension.objects.filter(nad_assess_num__na_assessment_num=ct_assessment_num_id)
    
    if stock_type and stock_type != '0' and stock_type != 'None' and stock_type != '':
        na_dimension_id = na_dimension_id.filter(nad_wood_type=stock_type)
    
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
    ct_requirement_id = request.GET.get('ct_requirement_id')
    print('ct_requirement_id', ct_requirement_id)

    empty_response = {
        'na_dimension_box_val': [],
        'na_dimension_type': '',
        'na_dimension_type_id': '',
        'na_uom': '',
        'na_uom_id': '',
        'na_length': 0,
        'na_width': 0,
        'na_height': 0,
        'na_quantity': 0,
        'na_wood_type_id': '',
        'na_wood_desc_id': '',
        'na_type_of_req_id': '',
    }

    # Guard: return empty response if no valid ID provided
    if not ct_requirement_id or not str(ct_requirement_id).strip().isdigit():
        return JsonResponse(empty_response)

    try:
        a = Nadimension.objects.get(pk=ct_requirement_id)
    except Nadimension.DoesNotExist:
        return JsonResponse(empty_response)

    na_dimension_box_val.append(
        str(a.nad_type_of_req) + ' (' + str(a.nad_length) + 'x' + str(a.nad_width) + 'x' + str(a.nad_height) + ')'
    )
    data = {
        'na_dimension_box_val': na_dimension_box_val,
        'na_dimension_type': str(a.nad_dimension_type),
        'na_dimension_type_id': str(a.nad_dimension_type.id),
        'na_uom': str(a.nad_uom),
        'na_uom_id': str(a.nad_uom.id),
        'na_length': str(a.nad_length),
        'na_width': str(a.nad_width),
        'na_height': str(a.nad_height),
        'na_quantity': str(a.nad_quantity),
        'na_wood_type_id': a.nad_wood_type.first().id if a.nad_wood_type.exists() else "",
        'na_wood_desc_id': a.nad_wood_description.first().id if a.nad_wood_description.exists() else "",
        'na_type_of_req_id': a.nad_type_of_req.id if a.nad_type_of_req else "",
    }
    return JsonResponse(data)