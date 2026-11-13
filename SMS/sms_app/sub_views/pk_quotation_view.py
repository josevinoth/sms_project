from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, F, Q
from django.http import JsonResponse
from ..forms import PkquotationForm
from ..models import User_extInfo,Nadimension,PkstockpurchasesInfo,PkquotationInfo,PkquotationsummaryInfo,Costtype,Pkstocktype,Stockdescription,pk_itemInfo,pk_itemdescriptionInfo,StockMaintenance,PkpartcodeInfo,PkneedassessmentInfo,Unitofmeasure,Natypeofreq
from django.shortcuts import render, redirect
from django.contrib import messages


def recalculate_dependent_costs(assessment_id, request=None):
    from django.db.models import Sum, F, Q
    from ..models import PkquotationInfo
    
    # Calculate total_cft_display dynamically for the assessment (Wood ONLY, excluding reused wood)
    aggregate_cft = PkquotationInfo.objects.filter(
        pkqt_assessment_num=assessment_id,
        pkqt_cost_type=8,
        pkqt_stock_type__in=[1, 5]
    ).exclude(
        pkqt_part_code__pc_code__icontains='RE'
    ).exclude(
        pkqt_stock_description__stock_description__icontains='RE - Used'
    ).exclude(
        pkqt_stock_description__stock_description__icontains='RE-Used'
    ).exclude(
        pkqt_stock_description__stock_description__icontains='Reused'
    ).aggregate(total=Sum(F('pkqt_sqrt_req') * F('pkqt_na_quantity')))['total']
    
    total_cft = round(aggregate_cft, 3) if aggregate_cft is not None else 0.0
    if request:
        request.session['total_cft_display'] = total_cft

    # Find HT Cost entries for this assessment and recalculate them automatically per Job Type
    ht_costs = PkquotationInfo.objects.filter(
        pkqt_assessment_num=assessment_id,
        pkqt_cost_type=5
    ).select_related('pkqt_requirement')

    for ht in ht_costs:
        if ht.pkqt_requirement:
            job_wood_cft = PkquotationInfo.objects.filter(
                pkqt_assessment_num=assessment_id,
                pkqt_requirement=ht.pkqt_requirement,
                pkqt_cost_type=8,
                pkqt_stock_type__in=[1, 5]
            ).exclude(
                pkqt_part_code__pc_code__icontains='RE'
            ).exclude(
                pkqt_stock_description__stock_description__icontains='RE - Used'
            ).exclude(
                pkqt_stock_description__stock_description__icontains='RE-Used'
            ).exclude(
                pkqt_stock_description__stock_description__icontains='Reused'
            ).aggregate(total=Sum(F('pkqt_sqrt_req') * F('pkqt_na_quantity')))['total']
            current_cft = round(job_wood_cft, 3) if job_wood_cft is not None else 0.0
        else:
            current_cft = total_cft

        na_quantity = float(ht.pkqt_na_quantity or (ht.pkqt_requirement.nad_na_quantity if ht.pkqt_requirement and ht.pkqt_requirement.nad_na_quantity else 1) or 1)
        rate = float(ht.pkqt_rate or 0)
        
        # Unit CFT per box for this job type
        unit_cft = (current_cft / na_quantity) if na_quantity else 0.0
        
        # Cost per box
        totalCost = rate * unit_cft
        
        # Total cost for all boxes of this job type
        totalboxCost = totalCost * na_quantity
        
        ht.pkqt_sqrt_req = round(unit_cft, 3)
        ht.pkqt_total_cost = round(totalCost, 2)
        ht.pkqt_totalbox_cost = round(totalboxCost, 2)
        ht.save()

def get_plywood_sheets_catalog():
    """Returns sorted standard and warehouse plywood stock sheets for 2D Cut Sheet Optimizer."""
    plywood_qs = PkpartcodeInfo.objects.filter(
        Q(pc_stock_description__stock_type_id__in=[4, 6]) | Q(pc_stock_type_id__in=[4, 6])
    ).select_related('pc_stock_description').distinct()

    standard_plywood_sheets = []
    other_plywood_sheets = []

    for p in plywood_qs:
        l_ft = float(p.pc_length or 0.0)
        w_ft = float(p.pc_width or 0.0)
        t_mm = float(p.pc_height or 0.0)
        if l_ft <= 0 or w_ft <= 0:
            continue
        l_in = round(l_ft * 12.0, 1)
        w_in = round(w_ft * 12.0, 1)
        sqft = round(l_ft * w_ft, 2)
        desc_name = p.pc_stock_description.stock_description if p.pc_stock_description else ''
        t_str = f" • {int(t_mm) if t_mm.is_integer() else t_mm}mm" if t_mm > 0 else ""
        label = f"{p.pc_code} — {int(l_ft) if l_ft.is_integer() else l_ft}×{int(w_ft) if w_ft.is_integer() else w_ft} ft ({int(l_in) if l_in.is_integer() else l_in}×{int(w_in) if w_in.is_integer() else w_in} in / {sqft:g} sqft){t_str}"
        sheet_data = {
            'code': p.pc_code,
            'l_ft': l_ft,
            'w_ft': w_ft,
            'l_in': l_in,
            'w_in': w_in,
            't_mm': t_mm,
            'sqft': sqft,
            'label': label,
            'desc': desc_name,
        }
        if (l_ft in [8.0, 7.0, 6.0] and w_ft in [4.0, 5.0]):
            standard_plywood_sheets.append(sheet_data)
        else:
            other_plywood_sheets.append(sheet_data)

    standard_plywood_sheets.sort(key=lambda s: (-s['l_ft'], -s['w_ft'], -s['t_mm'], s['code']))
    other_plywood_sheets.sort(key=lambda s: (-s['sqft'], s['code']))
    return standard_plywood_sheets, other_plywood_sheets


@transaction.atomic
@login_required(login_url='login_page')
def pk_quotation_add(request, quotation_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID') or (request.user.id if request.user.is_authenticated else None)
    na_assessment_num_id = request.session.get('na_assessment_id') or request.session.get('na_assessment_num_id') or request.GET.get('assessment_id')
    if na_assessment_num_id:
        request.session['na_assessment_id'] = na_assessment_num_id
        request.session['na_assessment_num_id'] = na_assessment_num_id
    na_customer_name_id = request.session.get('na_customer_name_id')
    na_customer_new_name_id = request.session.get('na_customer_new_name')

    user_ext = User_extInfo.objects.filter(user=user_id).first() if user_id else None
    role = user_ext.emp_role if user_ext else None
    role_id = role.id if role else 1

    if request.method == "GET":
        if quotation_id == 0:
            # Check if a specific requirement/item ID is passed in query params
            req_id_param = request.GET.get('requirement_id') or request.GET.get('req_id')
            if req_id_param and str(req_id_param).isdigit():
                req_id_param = int(req_id_param)
                request.session['last_job_type'] = req_id_param
            else:
                req_id_param = 0

            # Retrieve stored values (IDs) from session safely for continuous data entry
            pkqt_cost_type_id = request.session.get('last_cost_type')
            pkqt_job_type_id = req_id_param or request.session.get('last_job_type')
            pkqt_job_type_quant_id = request.session.get('last_job_type_quantity')
            pkqt_part_code_id = request.session.get('last_part_code')
            pkqt_stock_type_id = request.session.get('last_stock_type_quantity')
            pkqt_stock_description_id = request.session.get('last_stock_desc_quantity')
            pkqt_item_type_id = request.session.get('last_item_type')
            pkqt_item_description_id = request.session.get('last_item_desc')

            initial_data = {}
            if pkqt_cost_type_id:
                initial_data['pkqt_cost_type'] = pkqt_cost_type_id
            if pkqt_job_type_id:
                initial_data['pkqt_requirement'] = pkqt_job_type_id
            if pkqt_job_type_quant_id:
                initial_data['pkqt_na_quantity'] = pkqt_job_type_quant_id
            if pkqt_part_code_id:
                initial_data['pkqt_part_code'] = pkqt_part_code_id
            if pkqt_stock_type_id:
                initial_data['pkqt_stock_type'] = pkqt_stock_type_id
            if pkqt_stock_description_id:
                initial_data['pkqt_stock_description'] = pkqt_stock_description_id
            if pkqt_item_type_id:
                initial_data['pkqt_item'] = pkqt_item_type_id
            if pkqt_item_description_id:
                initial_data['pkqt_itemdescription'] = pkqt_item_description_id

            import json
            # Calculate CFT map by job type (Wood ONLY, excluding reused wood)
            job_cft_qs = PkquotationInfo.objects.filter(
                pkqt_assessment_num=na_assessment_num_id,
                pkqt_cost_type=8,
                pkqt_stock_type__in=[1, 5]
            ).exclude(
                pkqt_part_code__pc_code__icontains='RE'
            ).exclude(
                pkqt_stock_description__stock_description__icontains='RE - Used'
            ).exclude(
                pkqt_stock_description__stock_description__icontains='RE-Used'
            ).exclude(
                pkqt_stock_description__stock_description__icontains='Reused'
            ).values('pkqt_requirement').annotate(
                total=Sum(F('pkqt_sqrt_req') * F('pkqt_na_quantity'))
            )
            job_cft_map = {}
            for j in job_cft_qs:
                if j['pkqt_requirement']:
                    job_cft_map[str(j['pkqt_requirement'])] = round(j['total'] or 0.0, 3)
            job_cft_map_json = json.dumps(job_cft_map)

            form = PkquotationForm(initial=initial_data)
            # Calculate total_cft_display dynamically for the assessment (Wood ONLY, excluding reused wood)
            aggregate_cft = PkquotationInfo.objects.filter(
                pkqt_assessment_num=na_assessment_num_id,
                pkqt_cost_type=8,
                pkqt_stock_type__in=[1, 5]
            ).exclude(
                pkqt_part_code__pc_code__icontains='RE'
            ).exclude(
                pkqt_stock_description__stock_description__icontains='RE - Used'
            ).exclude(
                pkqt_stock_description__stock_description__icontains='RE-Used'
            ).exclude(
                pkqt_stock_description__stock_description__icontains='Reused'
            ).aggregate(total=Sum(F('pkqt_sqrt_req') * F('pkqt_na_quantity')))['total']
            project_total_cft = round(aggregate_cft, 3) if aggregate_cft is not None else 0.0

            quoted_req_ids = set(PkquotationInfo.objects.filter(pkqt_assessment_num=na_assessment_num_id).values_list('pkqt_requirement_id', flat=True))
            requirements_list = list(Nadimension.objects.filter(nad_assess_num_id=na_assessment_num_id))
            for r in requirements_list:
                r.is_quoted = r.id in quoted_req_ids
            has_quoted = any(r.is_quoted for r in requirements_list)
            summary_info = PkquotationsummaryInfo.objects.filter(qs_assessment_num_id=na_assessment_num_id).first()

            from .general_utils import generate_next_number, get_financial_year
            fy = get_financial_year()
            next_item_number = generate_next_number(Nadimension, 'nad_item', f"{fy}_MAA_ITM_", 6)
            unquoted_list = [r for r in requirements_list if not getattr(r, 'is_quoted', False)]
            standard_plywood_sheets, other_plywood_sheets = get_plywood_sheets_catalog()

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
                'job_cft_map_json': job_cft_map_json,
                'requirements_list': requirements_list,
                'unquoted_list': unquoted_list,
                'summary_info': summary_info,
                'has_quoted': has_quoted,
                'typeofreq_list': Natypeofreq.objects.all().order_by('type_of_req'),
                'next_item_number': next_item_number,
                'selected_requirement_id': req_id_param,
                'standard_plywood_sheets': standard_plywood_sheets,
                'other_plywood_sheets': other_plywood_sheets,
            }
        else:
            print("Inside PK quotation get edit")
            import json
            job_cft_qs = PkquotationInfo.objects.filter(
                pkqt_assessment_num=na_assessment_num_id,
                pkqt_cost_type=8,
                pkqt_stock_type__in=[1, 5]
            ).exclude(
                pkqt_part_code__pc_code__icontains='RE'
            ).exclude(
                pkqt_stock_description__stock_description__icontains='RE - Used'
            ).exclude(
                pkqt_stock_description__stock_description__icontains='RE-Used'
            ).exclude(
                pkqt_stock_description__stock_description__icontains='Reused'
            ).values('pkqt_requirement').annotate(
                total=Sum(F('pkqt_sqrt_req') * F('pkqt_na_quantity'))
            )
            job_cft_map = {}
            for j in job_cft_qs:
                if j['pkqt_requirement']:
                    job_cft_map[str(j['pkqt_requirement'])] = round(j['total'] or 0.0, 3)
            job_cft_map_json = json.dumps(job_cft_map)

            quotation = PkquotationInfo.objects.get(pk=quotation_id)
            form = PkquotationForm(instance=quotation)
            
            # Calculate total_cft_display dynamically for the assessment (Wood ONLY, excluding reused wood)
            aggregate_cft = PkquotationInfo.objects.filter(
                pkqt_assessment_num=na_assessment_num_id,
                pkqt_cost_type=8,
                pkqt_stock_type__in=[1, 5]
            ).exclude(
                pkqt_part_code__pc_code__icontains='RE'
            ).exclude(
                pkqt_stock_description__stock_description__icontains='RE - Used'
            ).exclude(
                pkqt_stock_description__stock_description__icontains='RE-Used'
            ).exclude(
                pkqt_stock_description__stock_description__icontains='Reused'
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
                'job_cft_map_json': job_cft_map_json,
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
                            return redirect(request.META.get('HTTP_REFERER') or '/SMS/pk_quotation_insert/')

                        try:
                            stock_qty = float(stock_qty_str)
                        except ValueError:
                            messages.error(request, 'Invalid quantity value. It should be a number.')
                            return redirect(request.META.get('HTTP_REFERER') or '/SMS/pk_quotation_insert/')

                        if stock_qty > stock_qty_available:
                            error_message = (
                                f"Insufficient stock for {stock_purchase.sm_partcode.pc_code}. "
                                f"Available: {stock_qty_available}, Requested: {stock_qty}"
                            )
                            messages.error(request, error_message)
                            return redirect(request.META.get('HTTP_REFERER') or '/SMS/pk_quotation_insert/')

                            # ✅ Store selected values in session even when validation fails
                            # request.session['last_cost_type'] = form.cleaned_data.get(
                            #     'pkqt_cost_type').id if form.cleaned_data.get('pkqt_cost_type') else None

                            return redirect(request.META.get('HTTP_REFERER') or '/SMS/pk_quotation_insert/')

                        # ✅ Uncomment this if stock validation is needed
                        # if stock_qty <= 0:
                        #     messages.error(request, 'Quantity should be greater than 0.')
                        #     return redirect(request.META.get('HTTP_REFERER') or '/SMS/pk_quotation_insert/')
                        # elif stock_qty > stock_qty_available:
                        #     error_message = (
                        #         f'Quantity should be less than or equal to available stock: '
                        #         f'{stock_purchase_num}. Available quantity: {stock_qty_available}.'
                        #     )
                        #     messages.error(request, error_message)
                        #     return redirect(request.META.get('HTTP_REFERER') or '/SMS/pk_quotation_insert/')

                        form.save()

                        quotation = form.save()

                        # Extract relevant fields
                        cost_type = quotation.pkqt_cost_type.id
                        stock_type = quotation.pkqt_stock_type.id
                        assessment_id = quotation.pkqt_assessment_num.id

                        # ✅ Only for cost_type = 8 and Wood stock_type in [1, 5]
                        if cost_type == 8 and stock_type in [1, 5]:
                            total_cft = PkquotationInfo.objects.filter(
                                pkqt_assessment_num=assessment_id,
                                pkqt_cost_type=8,
                                pkqt_stock_type__in=[1, 5]
                            ).exclude(
                                pkqt_part_code__pc_code__icontains='RE'
                            ).exclude(
                                pkqt_stock_description__stock_description__icontains='RE - Used'
                            ).exclude(
                                pkqt_stock_description__stock_description__icontains='RE-Used'
                            ).exclude(
                                pkqt_stock_description__stock_description__icontains='Reused'
                            ).aggregate(total=Sum(F('pkqt_sqrt_req') * F('pkqt_na_quantity')))['total'] or 0.0
                            print("total_cft", total_cft)
                            request.session['total_cft_display'] = round(total_cft, 3)
                        else:
                            request.session['total_cft_display'] = 0.0

                        print("Quotation form is valid and stock updated.")
                        messages.success(request, 'Stock Updated Successfully')

                    except StockMaintenance.DoesNotExist:
                        messages.error(request, 'Selected stock purchase record not found.')
                        return redirect(request.META.get('HTTP_REFERER') or '/SMS/pk_quotation_insert/')
                else:
                    quotation=form.save()
                    # Extract relevant fields
                    cost_type = quotation.pkqt_cost_type.id
                    stock_type = quotation.pkqt_stock_type.id
                    assessment_id = quotation.pkqt_assessment_num.id

                    # ✅ Only for cost_type = 8 and Wood stock_type in [1, 5]
                    if cost_type == 8 and stock_type in [1, 5]:
                        total_cft = PkquotationInfo.objects.filter(
                            pkqt_assessment_num=assessment_id,
                            pkqt_cost_type=8,
                            pkqt_stock_type__in=[1, 5]
                        ).exclude(
                            pkqt_part_code__pc_code__icontains='RE'
                        ).exclude(
                            pkqt_stock_description__stock_description__icontains='RE - Used'
                        ).exclude(
                            pkqt_stock_description__stock_description__icontains='RE-Used'
                        ).exclude(
                            pkqt_stock_description__stock_description__icontains='Reused'
                        ).aggregate(total=Sum(F('pkqt_sqrt_req') * F('pkqt_na_quantity')))['total'] or 0.0
                        print("total_cft", total_cft)
                        request.session['total_cft_display'] = round(total_cft, 3)
                    else:
                        request.session['total_cft_display'] = 0.0

                    messages.warning(request, 'Stock saved without Stock Purchase Number')
            else:
                quotation = form.save()

                messages.success(request, 'Quotation Updated Successfully')

            recalculate_dependent_costs(quotation.pkqt_assessment_num.id, request)

            # Store selected values in session after a successful form save for continuous entry
            if form.cleaned_data.get('pkqt_cost_type'):
                request.session['last_cost_type'] = form.cleaned_data.get('pkqt_cost_type').id
            if form.cleaned_data.get('pkqt_requirement'):
                request.session['last_job_type'] = form.cleaned_data.get('pkqt_requirement').id
            if form.cleaned_data.get('pkqt_na_quantity'):
                request.session['last_job_type_quantity'] = form.cleaned_data.get('pkqt_na_quantity')
            if form.cleaned_data.get('pkqt_part_code'):
                request.session['last_part_code'] = form.cleaned_data.get('pkqt_part_code').id
            if form.cleaned_data.get('pkqt_stock_type'):
                request.session['last_stock_type_quantity'] = form.cleaned_data.get('pkqt_stock_type').id
            if form.cleaned_data.get('pkqt_stock_description'):
                request.session['last_stock_desc_quantity'] = form.cleaned_data.get('pkqt_stock_description').id
            if form.cleaned_data.get('pkqt_item'):
                request.session['last_item_type'] = form.cleaned_data.get('pkqt_item').id
            if form.cleaned_data.get('pkqt_itemdescription'):
                request.session['last_item_desc'] = form.cleaned_data.get('pkqt_itemdescription').id

            return redirect('/SMS/pk_quotation_insert/')

        else:
            print("Quotation form is not valid.")
            messages.error(request, 'Record Not Updated Successfully')

            # Debugging: Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")
                    messages.error(request, f"Error in {field}: {error}")

        return redirect(request.META.get('HTTP_REFERER') or '/SMS/pk_quotation_insert/')


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
    assessment_id = quotation.pkqt_assessment_num.id
    quotation.delete()
    recalculate_dependent_costs(assessment_id, request)
    # return redirect('/SMS/pK_quotation_cancel')
    return redirect(request.META.get('HTTP_REFERER') or '/SMS/pk_quotation_insert/')

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
        'job_total_cft': 0.0,
    }

    # Guard: return empty response if no valid ID provided
    if not ct_requirement_id or not str(ct_requirement_id).strip().isdigit():
        return JsonResponse(empty_response)

    try:
        a = Nadimension.objects.get(pk=ct_requirement_id)
    except Nadimension.DoesNotExist:
        return JsonResponse(empty_response)

    job_wood_cft = PkquotationInfo.objects.filter(
        pkqt_requirement_id=ct_requirement_id,
        pkqt_cost_type=8,
        pkqt_stock_type__in=[1, 5]
    ).exclude(
        pkqt_part_code__pc_code__icontains='RE'
    ).exclude(
        pkqt_stock_description__stock_description__icontains='RE - Used'
    ).exclude(
        pkqt_stock_description__stock_description__icontains='RE-Used'
    ).exclude(
        pkqt_stock_description__stock_description__icontains='Reused'
    ).aggregate(total=Sum(F('pkqt_sqrt_req') * F('pkqt_na_quantity')))['total']
    job_wood_cft = round(job_wood_cft, 3) if job_wood_cft is not None else 0.0

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
        'job_total_cft': job_wood_cft,
    }
    return JsonResponse(data)

# ==============================================================================
# EXCEL-STYLE FAST QUOTATION MATRIX ENDPOINTS
# ==============================================================================

def get_wood_pc(h, w, l):
    try:
        ih = int(round(float(h) * 10))
        iw = int(round(float(w) * 10))
        il = int(round(float(l) * 10))
        target_code = f"K{ih}{iw}{il}"
        pc = PkpartcodeInfo.objects.filter(pc_code=target_code).first()
        if pc:
            return pc
    except Exception:
        pass
    return PkpartcodeInfo.objects.filter(pc_stock_type_id=1).first()


def get_pc_for_sd(stock_desc_id, default_code=None):
    if default_code:
        pc = PkpartcodeInfo.objects.filter(pc_code=default_code).first()
        if pc:
            return pc
    if stock_desc_id:
        pc = PkpartcodeInfo.objects.filter(pc_stock_description_id=stock_desc_id).first()
        if pc:
            return pc
    return None


@login_required(login_url='login_page')
def load_quotation_matrix(request):
    """
    Returns initial matrix parameters, requirements, standard catalogs and any previously saved quotation rows.
    """
    assessment_id = request.GET.get('assessment_id') or request.session.get('na_assessment_id')
    requirement_id = request.GET.get('requirement_id')

    if not assessment_id:
        return JsonResponse({'status': 'error', 'message': 'No assessment ID found in session or parameters.'}, status=400)

    if str(assessment_id).strip().isdigit():
        assess_obj = PkneedassessmentInfo.objects.filter(id=int(assessment_id)).first()
    else:
        assess_obj = PkneedassessmentInfo.objects.filter(na_assessment_num=str(assessment_id).strip()).first()

    if not assess_obj:
        return JsonResponse({'status': 'error', 'message': f'Assessment {assessment_id} not found.'}, status=404)

    assessment_id = assess_obj.id
    reqs = Nadimension.objects.filter(nad_assess_num=assess_obj)

    summary_id = request.GET.get('summary_id') or request.session.get('quotationsummary_id')
    summary_obj = None
    if summary_id:
        summary_obj = PkquotationsummaryInfo.objects.filter(id=summary_id).first()
    if not summary_obj:
        summary_obj = PkquotationsummaryInfo.objects.filter(qs_assessment_num=assess_obj, qs_is_latest=True).first()

    if summary_obj:
        quoted_req_ids = set(PkquotationInfo.objects.filter(pkqt_assessment_num=assess_obj, pkqt_quotation_summary=summary_obj).values_list('pkqt_requirement_id', flat=True))
    else:
        quoted_req_ids = set(PkquotationInfo.objects.filter(pkqt_assessment_num=assess_obj).values_list('pkqt_requirement_id', flat=True))

    req_list = []
    active_req = None
    first_quoted_req = None

    for r in reqs:
        is_quoted = r.id in quoted_req_ids
        r_data = {
            'id': r.id,
            'name': str(r.nad_item or f'Box Item #{r.id}'),
            'type_of_req': str(r.nad_type_of_req) if r.nad_type_of_req else 'Plywood Box',
            'length': float(r.nad_length or 0.0),
            'width': float(r.nad_width or 0.0),
            'height': float(r.nad_height or 0.0),
            'uom': str(r.nad_uom) if r.nad_uom else 'cm',
            'quantity': int(r.nad_quantity or 1),
            'clearance': float(r.nad_plywood_thickness) if r.nad_plywood_thickness is not None else (float(r.nad_clearance) if r.nad_clearance is not None else 0.0),
            'plywood_thickness': float(r.nad_plywood_thickness) if r.nad_plywood_thickness is not None else 0.0,
            'clr_length': float(r.nad_clr_length or 0.0),
            'clr_width': float(r.nad_clr_width or 0.0),
            'clr_top': float(r.nad_clr_top or 0.0),
            'thk_length': float(r.nad_thk_length or 7.0),
            'thk_width': float(r.nad_thk_width or 7.0),
            'thk_height': float(r.nad_thk_height or 20.0),
            'dimension_type': str(r.nad_dimension_type.dimension_type if r.nad_dimension_type else 'Cargo OD'),
            'job_weight': float(r.nad_job_weight or 0.0),
            'customer_part_code': r.nad_customer_part_code or '',
            'type_of_req_id': r.nad_type_of_req_id,
            'is_quoted': is_quoted,
        }
        req_list.append(r_data)
        if is_quoted and not first_quoted_req:
            first_quoted_req = r_data
        if requirement_id and str(r.id) == str(requirement_id):
            active_req = r_data

    if not active_req and req_list:
        active_req = first_quoted_req if first_quoted_req else req_list[0]

    summary_id_param = request.GET.get('summary_id') or request.session.get('quotationsummary_id')
    summary = None
    if summary_id_param and str(summary_id_param).strip().isdigit():
        summary = PkquotationsummaryInfo.objects.filter(id=int(summary_id_param)).first()
    if not summary:
        summary = PkquotationsummaryInfo.objects.filter(qs_assessment_num=assess_obj, qs_is_latest=True).first()
    if not summary:
        summary = PkquotationsummaryInfo.objects.filter(qs_assessment_num=assess_obj).order_by('-id').first()
    if summary:
        request.session['quotationsummary_id'] = summary.id
    margin_pct = float(summary.qs_margin) if (summary and summary.qs_margin is not None) else 0.0
    wood_rate = float(summary.qs_rate_per_cft) if (summary and summary.qs_rate_per_cft) else 0.0
    ply_rate = float(getattr(summary, "qs_rate_per_sqft", 0.0) or 0.0)

    existing_rows = []
    saved_nails = []
    saved_materials = []

    if active_req:
        active_req_id = active_req['id']
        q_filter = {
            'pkqt_assessment_num': assess_obj,
            'pkqt_requirement_id': active_req_id,
        }
        if summary:
            q_filter['pkqt_quotation_summary'] = summary
        rows = PkquotationInfo.objects.filter(**q_filter).select_related(
            'pkqt_cost_type', 'pkqt_stock_type', 'pkqt_stock_description', 'pkqt_item', 'pkqt_itemdescription', 'pkqt_part_code', 'pkqt_uom'
        )

        for row in rows:
            desc_str = ''
            if row.pkqt_itemdescription:
                desc_str = row.pkqt_itemdescription.id_item_description
            elif row.pkqt_stock_description:
                desc_str = row.pkqt_stock_description.stock_description
            elif row.pkqt_item:
                desc_str = row.pkqt_item.item_name

            code = row.pkqt_part_code.pc_code if row.pkqt_part_code else ''
            qty = float(row.pkqt_quantity_req or 0.0)
            rate = float(row.pkqt_rate or 0.0)
            total = float(row.pkqt_total_cost or 0.0)

            if row.pkqt_stock_type_id in [4, 6] and rate > 0 and not ply_rate:
                ply_rate = rate

            is_nail = (row.pkqt_stock_type_id == 2 and (code.startswith('N') or 'nail' in desc_str.lower()))
            if is_nail:
                saved_nails.append({
                    'id': row.id,
                    'name': desc_str,
                    'code': code,
                    'stock_purchase_id': row.pkqt_part_code_id or '',
                    'qty': qty,
                    'rate': rate,
                    'total_cost': total,
                })
                continue

            is_material = (row.pkqt_stock_type_id == 2 or row.pkqt_cost_type_id in [1, 2, 7])
            if is_material:
                saved_materials.append({
                    'id': row.id,
                    'name': desc_str,
                    'code': code,
                    'stock_purchase_id': row.pkqt_part_code_id or '',
                    'qty': qty,
                    'rate': rate,
                    'total_cost': total,
                })
                continue

            # Skip operational costs (Labour, Transport, HT, Crane, Fumigation) from structure table
            if row.pkqt_cost_type_id in [3, 4, 5, 6, 9, 10] or not row.pkqt_stock_type_id:
                continue

            sec_name = 'BASE'
            sec_class = 'sec-base'
            iname = (row.pkqt_item.item_name if row.pkqt_item else '').upper()
            dname = desc_str.upper()
            if 'BASE' in iname or 'BASE' in dname or 'LIFTING' in dname or 'DECK' in dname:
                sec_name = 'BASE'
                sec_class = 'sec-base'
            elif 'LENGTH' in iname or 'LENGTH' in dname:
                sec_name = 'LENGTH (2 SIDES)'
                sec_class = 'sec-length'
            elif 'WIDTH' in iname or 'WIDTH' in dname:
                sec_name = 'WIDTH (2 SIDES)'
                sec_class = 'sec-width'
            elif 'TOP' in iname or 'TOP' in dname:
                sec_name = 'TOP'
                sec_class = 'sec-top'
            elif 'ARREST' in iname or 'SUPPORT' in iname or 'ARREST' in dname or 'SUPPORT' in dname:
                sec_name = 'SUPPORTS & ARREST'
                sec_class = 'sec-supports'

            # Disambiguate legacy single-word descriptions (so user clearly sees Panel vs Frame)
            clean_name = desc_str
            if clean_name.strip().upper() == 'LENGTH':
                clean_name = 'LENGTH PANEL' if row.pkqt_stock_type_id in [4, 6] else 'LENGTH FRAME (HORIZ)'
            elif clean_name.strip().upper() == 'WIDTH':
                clean_name = 'WIDTH PANEL' if row.pkqt_stock_type_id in [4, 6] else 'WIDTH FRAME (HORIZ)'
            elif clean_name.strip().upper() == 'HEIGHT':
                clean_name = 'HEIGHT FRAME (VERT)'
            elif clean_name.strip().upper() == 'TOP ARREST' and row.pkqt_stock_type_id in [4, 6]:
                clean_name = 'TOP PANEL'

            existing_rows.append({
                'id': row.id,
                'section': sec_name,
                'secClass': sec_class,
                'cost_type_id': row.pkqt_cost_type_id,
                'cost_type_name': row.pkqt_cost_type.cost_type if row.pkqt_cost_type else '',
                'stock_type_id': row.pkqt_stock_type_id,
                'stock_description_id': row.pkqt_stock_description_id,
                'stock_description': row.pkqt_stock_description.stock_description if row.pkqt_stock_description else '',
                'item_name': clean_name,
                'name': clean_name,
                'part_code': code,
                'mat': 'plywood' if row.pkqt_stock_type_id in [4, 6] else 'wood',
                'l': float(row.pkqt_length_req or 0.0),
                'w': float(row.pkqt_width_req or 0.0),
                'h': float(row.pkqt_height_req or 0.0),
                'nos': float(row.pkqt_quantity_req or 0.0),
                'sqrt_req': float(row.pkqt_sqrt_req or 0.0),
                'rate': rate,
                'total_cost': total,
                'totalbox_cost': float(row.pkqt_totalbox_cost or 0.0),
            })

    # Sort structural items by canonical section order so sections never repeat
    sec_order = {'BASE': 1, 'LENGTH (2 SIDES)': 2, 'WIDTH (2 SIDES)': 3, 'TOP': 4, 'SUPPORTS & ARREST': 5}
    existing_rows.sort(key=lambda r: (sec_order.get(r.get('section', ''), 99), r.get('id', 0)))

    if not ply_rate and assess_obj:
        ply_row = PkquotationInfo.objects.filter(pkqt_assessment_num=assess_obj, pkqt_stock_type_id__in=[4, 6], pkqt_rate__gt=0).first()
        if ply_row:
            ply_rate = float(ply_row.pkqt_rate)

    op_costs = {
        'crane': 0.0,
        'transport': 0.0,
        'labour': 0.0,
        'onsite_labour': 0.0,
        'ht': 0.0,
        'fumigation': 0.0,
    }
    if active_req:
        for row in rows:
            ct = row.pkqt_cost_type_id
            rate = float(row.pkqt_rate or row.pkqt_total_cost or 0.0)
            if ct == 6: op_costs['crane'] = rate
            elif ct == 4: op_costs['transport'] = rate
            elif ct == 3: op_costs['labour'] = rate
            elif ct == 9: op_costs['onsite_labour'] = rate
            elif ct == 5: op_costs['ht'] = rate
            elif ct == 10: op_costs['fumigation'] = rate

    return JsonResponse({
        'status': 'success',
        'assessment_id': assessment_id,
        'assessment_num': assess_obj.na_assessment_num,
        'requirements': req_list,
        'active_requirement': active_req,
        'rates': {
            'wood_rate': wood_rate,
            'ply_rate': ply_rate,
            'margin_pct': margin_pct,
            'ply_wastage_pct': 0.0,
        },
        'existing_rows': existing_rows,
        'saved_nails': saved_nails,
        'saved_materials': saved_materials,
        'operational_costs': op_costs,
        'saved_custom_breakdown': [
            {
                'label': (r.pkqt_itemdescription.id_item_description if r.pkqt_itemdescription else 'Other Charges'),
                'amount': float(r.pkqt_rate or r.pkqt_total_cost or 0.0)
            }
            for r in rows if r.pkqt_cost_type_id == 11 or (r.pkqt_cost_type and 'other' in r.pkqt_cost_type.cost_type.lower())
        ],
        'summary': {
            'id': summary.id if summary else None,
            'wood_cost': float(summary.qs_wood_cost or 0.0) if summary else 0.0,
            'plywood_cost': float(summary.qs_plywood_cost or 0.0) if summary else 0.0,
            'consumables_cost': float(summary.qs_material_cost or 0.0) if summary else 0.0,
            'labour_cost': float(summary.qs_labour_cost or 0.0) if summary else 0.0,
            'transport_cost': float(summary.qs_transport_cost or 0.0) if summary else 0.0,
            'grand_total': float(summary.qs_final_cost or summary.qs_total_cost_wm or 0.0) if summary else 0.0,
        } if summary else None
    })


@transaction.atomic
@login_required(login_url='login_page')
def save_quotation_matrix(request):
    """
    Saves the complete quotation breakdown submitted from the Excel Matrix in a single atomic transaction.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST method required.'}, status=405)

    import json
    try:
        data = json.loads(request.body)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Invalid JSON payload: {str(e)}'}, status=400)

    assessment_id = data.get('assessment_id') or request.session.get('na_assessment_id')
    requirement_id = data.get('requirement_id')
    user_id = request.session.get('ses_userID')

    if not assessment_id:
        return JsonResponse({'status': 'error', 'message': 'Missing assessment_id.'}, status=400)

    if str(assessment_id).strip().isdigit():
        assess_obj = PkneedassessmentInfo.objects.filter(id=int(assessment_id)).first()
    else:
        assess_obj = PkneedassessmentInfo.objects.filter(na_assessment_num=str(assessment_id).strip()).first()

    if not assess_obj:
        return JsonResponse({'status': 'error', 'message': f'Assessment {assessment_id} not found.'}, status=404)

    req_obj = Nadimension.objects.filter(id=requirement_id).first() if requirement_id else None
    if not req_obj:
        return JsonResponse({'status': 'error', 'message': 'Missing or invalid requirement_id.'}, status=400)

    box_specs = data.get('box_specs', {})
    if box_specs:
        if box_specs.get('length'):
            req_obj.nad_length = float(box_specs['length'])
        if box_specs.get('width'):
            req_obj.nad_width = float(box_specs['width'])
        if box_specs.get('height'):
            req_obj.nad_height = float(box_specs['height'])
        if box_specs.get('clearance'):
            req_obj.nad_clearance = float(box_specs['clearance'])
        req_obj.save()

    box_qty = int(req_obj.nad_quantity or 1)

    # Clean existing rows for this specific requirement to prevent duplication
    summary_id = data.get('summary_id') or request.session.get('quotationsummary_id')
    summary_record = None
    if summary_id:
        summary_record = PkquotationsummaryInfo.objects.filter(id=summary_id).first()
    if not summary_record:
        summary_record = PkquotationsummaryInfo.objects.filter(qs_assessment_num=assess_obj, qs_is_latest=True).first()
    if not summary_record:
        summary_record = PkquotationsummaryInfo.objects.filter(qs_assessment_num=assess_obj).first()

    del_qs = PkquotationInfo.objects.filter(
        pkqt_assessment_num=assess_obj,
        pkqt_requirement=req_obj
    )
    if summary_record:
        del_qs = del_qs.filter(pkqt_quotation_summary=summary_record)
    del_qs.delete()

    created_count = 0

    # 1. Save Structural Wood & Plywood Items
    structural_items = data.get('structural_items', [])
    for s in structural_items:
        mat_type = s.get('material_type') or s.get('mat_type', 'wood')
        name = s.get('name', 'Structural Item')
        l_val = float(s.get('length') or s.get('l') or 0.0)
        w_val = float(s.get('width') or s.get('w') or 0.0)
        h_val = float(s.get('height') or s.get('h') or 0.0)
        nos_val = float(s.get('nos') or 0.0)
        unit_val = float(s.get('calc_val') or s.get('unit_val') or 0.0)
        rate_val = float(s.get('rate') or 0.0)
        total_val = float(s.get('total_cost') or s.get('total') or 0.0)
        totalbox_val = round(total_val * box_qty, 2)

        stock_type_id = 4 if mat_type == 'plywood' else 1
        stock_desc_obj = Stockdescription.objects.filter(stock_type_id=stock_type_id).first()

        section_str = (s.get('section') or '').upper()
        item_obj = None
        if 'BASE' in section_str or 'BASE' in name.upper():
            item_obj = pk_itemInfo.objects.filter(item_name__iexact='BASE').first()
        elif 'LENGTH' in section_str or 'LENGTH' in name.upper():
            item_obj = pk_itemInfo.objects.filter(item_name__icontains='LENGTH').first()
        elif 'WIDTH' in section_str or 'WIDTH' in name.upper():
            item_obj = pk_itemInfo.objects.filter(item_name__icontains='WIDTH').first()
        elif 'TOP' in section_str or 'TOP' in name.upper():
            item_obj = pk_itemInfo.objects.filter(item_name__iexact='TOP').first()
        elif 'SUPPORT' in section_str or 'ARREST' in section_str or 'ARREST' in name.upper():
            item_obj = pk_itemInfo.objects.filter(item_name__icontains='ARREST').first() or pk_itemInfo.objects.filter(item_name__icontains='SUPPORT').first()

        uom_obj = None
        if mat_type == 'wood':
            uom_obj = Unitofmeasure.objects.filter(unit_of_measure__iexact='CFT').first()
        elif mat_type == 'plywood':
            uom_obj = Unitofmeasure.objects.filter(unit_of_measure__iexact='Sq.ft').first()

        part_code_str = s.get('part_code', '').strip()
        part_code_obj = None
        if part_code_str:
            part_code_obj = PkpartcodeInfo.objects.filter(pc_code=part_code_str).first()
        if not part_code_obj:
            if mat_type == 'wood':
                part_code_obj = get_wood_pc(h_val, w_val, l_val)
            else:
                part_code_obj = get_pc_for_sd(stock_desc_obj.id if stock_desc_obj else None, default_code='PY1410')

        # Stock Purchase Number / GRN linking
        stock_purchase_id = s.get('stock_purchase_id')
        grn_number = s.get('grn_number')
        sp_obj = None
        if stock_purchase_id:
            sp_obj = StockMaintenance.objects.filter(id=stock_purchase_id).first()
        elif grn_number:
            sp_obj = StockMaintenance.objects.filter(sm_stock_purchase_number=grn_number).first()
        elif part_code_obj:
            sp_obj = StockMaintenance.objects.filter(sm_partcode=part_code_obj, sm_stock_purchase_number__isnull=False).order_by('-id').first()

        desc_obj = pk_itemdescriptionInfo.objects.filter(id_item_description__iexact=name).first()
        if not desc_obj and name:
            first_word = name.split()[0]
            desc_obj = pk_itemdescriptionInfo.objects.filter(id_item_description__icontains=first_word).first()
        if not desc_obj and name:
            try:
                desc_obj, _ = pk_itemdescriptionInfo.objects.get_or_create(id_item_name=item_obj, id_item_description=name)
            except Exception:
                desc_obj = None

        PkquotationInfo.objects.create(
            pkqt_assessment_num=assess_obj,
            pkqt_quotation_summary=summary_record,
            pkqt_requirement=req_obj,
            pkqt_cost_type_id=8,
            pkqt_stock_type_id=stock_type_id,
            pkqt_stock_description=stock_desc_obj,
            pkqt_item=item_obj,
            pkqt_itemdescription=desc_obj,
            pkqt_part_code=part_code_obj,
            pkqt_stock_purchase_number=sp_obj,
            pkqt_uom=uom_obj,
            pkqt_length_req=l_val,
            pkqt_width_req=w_val,
            pkqt_height_req=h_val,
            pkqt_quantity=round(nos_val * box_qty, 2),
            pkqt_quantity_req=nos_val,
            pkqt_sqrt_req=unit_val,
            pkqt_rate=rate_val,
            pkqt_total_cost=total_val,
            pkqt_totalbox_cost=totalbox_val,
            pkqt_na_quantity=box_qty,
            pkqt_updated_by_id=user_id,
        )
        created_count += 1

    # 2. Save Nails
    nails = data.get('nails', [])
    nail_uom = Unitofmeasure.objects.filter(unit_of_measure__iexact='Kgms').first()
    for n in nails:
        qty_val = float(n.get('qty') or 0.0)
        rate_val = float(n.get('rate') or 0.0)
        if qty_val > 0 and rate_val > 0:
            total_val = round(qty_val * rate_val, 2)
            totalbox_val = round(total_val * box_qty, 2)
            code = n.get('code', 'N130S')
            desc = n.get('desc', 'Nail')

            nail_sd = Stockdescription.objects.filter(stock_description__icontains=desc).first() or                       Stockdescription.objects.filter(stock_type_id=2).first()
            part_code_obj = get_pc_for_sd(nail_sd.id if nail_sd else None, default_code=code)

            sp_nail = None
            if n.get('stock_purchase_id'):
                sp_nail = StockMaintenance.objects.filter(id=n.get('stock_purchase_id')).first()
            elif part_code_obj:
                sp_nail = StockMaintenance.objects.filter(sm_partcode=part_code_obj, sm_stock_purchase_number__isnull=False).order_by('-id').first()

            PkquotationInfo.objects.create(
                pkqt_assessment_num=assess_obj,
                pkqt_quotation_summary=summary_record,
                pkqt_requirement=req_obj,
                pkqt_cost_type_id=8,
                pkqt_stock_type_id=2,
                pkqt_stock_description=nail_sd,
                pkqt_itemdescription=None,
                pkqt_part_code=part_code_obj,
                pkqt_stock_purchase_number=sp_nail,
                pkqt_uom=nail_uom,
                pkqt_quantity=round(qty_val * box_qty, 2),
                pkqt_quantity_req=qty_val,
                pkqt_sqrt_req=qty_val,
                pkqt_rate=rate_val,
                pkqt_total_cost=total_val,
                pkqt_totalbox_cost=totalbox_val,
                pkqt_na_quantity=box_qty,
                pkqt_updated_by_id=user_id,
            )
            created_count += 1

    # 3. Save Consumables / Packing Materials
    materials = data.get('materials', [])
    mat_uom = Unitofmeasure.objects.filter(unit_of_measure__iexact='Nos').first()
    for m in materials:
        qty_val = float(m.get('qty') or 0.0)
        rate_val = float(m.get('rate') or 0.0)
        if qty_val > 0 and rate_val > 0:
            total_val = round(qty_val * rate_val, 2)
            totalbox_val = round(total_val * box_qty, 2)
            code = m.get('code', '')
            name = m.get('name', 'Consumable')

            sd_obj = Stockdescription.objects.filter(stock_description__icontains=name).first() or                      Stockdescription.objects.filter(stock_type_id=2).first()
            part_code_obj = get_pc_for_sd(sd_obj.id if sd_obj else None, default_code=code)

            sp_mat = None
            if m.get('stock_purchase_id'):
                sp_mat = StockMaintenance.objects.filter(id=m.get('stock_purchase_id')).first()
            elif part_code_obj:
                sp_mat = StockMaintenance.objects.filter(sm_partcode=part_code_obj, sm_stock_purchase_number__isnull=False).order_by('-id').first()

            PkquotationInfo.objects.create(
                pkqt_assessment_num=assess_obj,
                pkqt_quotation_summary=summary_record,
                pkqt_requirement=req_obj,
                pkqt_cost_type_id=8,
                pkqt_stock_type_id=2,
                pkqt_stock_description=sd_obj,
                pkqt_itemdescription=None,
                pkqt_part_code=part_code_obj,
                pkqt_stock_purchase_number=sp_mat,
                pkqt_uom=mat_uom,
                pkqt_quantity=round(qty_val * box_qty, 2),
                pkqt_quantity_req=qty_val,
                pkqt_sqrt_req=qty_val,
                pkqt_rate=rate_val,
                pkqt_total_cost=total_val,
                pkqt_totalbox_cost=totalbox_val,
                pkqt_na_quantity=box_qty,
                pkqt_updated_by_id=user_id,
            )
            created_count += 1

    # 4. Save HT, Labour, Transport, Crane, Fumigation and Custom Breakdown Items if non-zero
    other_costs = data.get('other_costs', {})
    svc_uom = Unitofmeasure.objects.filter(unit_of_measure__iexact='Nos').first()
    cost_mappings = [
        ('ht_cost', 5),
        ('labour_cost', 3),            # In-house Labour
        ('onsite_labour_cost', 9),     # On-site Labour
        ('transport_cost', 4),
        ('crane_cost', 6),
        ('fumigation_cost', 10),
    ]
    for cost_key, c_type_id in cost_mappings:
        amt = float(other_costs.get(cost_key) or data.get(cost_key) or 0.0)
        if amt > 0:
            totalbox_val = round(amt * box_qty, 2)
            PkquotationInfo.objects.create(
                pkqt_assessment_num=assess_obj,
                pkqt_quotation_summary=summary_record,
                pkqt_requirement=req_obj,
                pkqt_cost_type_id=c_type_id,
                pkqt_itemdescription=None,
                pkqt_uom=svc_uom,
                pkqt_quantity=round(1.0 * box_qty, 2),
                pkqt_quantity_req=1.0,
                pkqt_sqrt_req=1.0,
                pkqt_rate=amt,
                pkqt_total_cost=amt,
                pkqt_totalbox_cost=totalbox_val,
                pkqt_na_quantity=box_qty,
                pkqt_updated_by_id=user_id,
            )
            created_count += 1

    # Custom Breakdown Line Items (e.g. Outstation Cost, Handling, Extra Manning)
    custom_breakdown_items = data.get('custom_breakdown_items', [])
    other_charges_type = Costtype.objects.filter(id=11).first() or Costtype.objects.filter(cost_type__icontains='Other').first() or Costtype.objects.first()
    other_sd = Stockdescription.objects.filter(id=9256).first() or Stockdescription.objects.filter(stock_description__icontains='Other Charges').first()
    base_item = pk_itemInfo.objects.filter(id=1).first() or pk_itemInfo.objects.first()
    for cb in custom_breakdown_items:
        amt = float(cb.get('amount') or 0.0)
        label = (cb.get('label') or 'Other Charges').strip()
        if amt > 0:
            totalbox_val = round(amt * box_qty, 2)
            desc_obj = pk_itemdescriptionInfo.objects.filter(id_item_description__iexact=label).first()
            if not desc_obj:
                try:
                    desc_obj, _ = pk_itemdescriptionInfo.objects.get_or_create(id_item_name=base_item, id_item_description=label)
                except Exception:
                    desc_obj = None

            PkquotationInfo.objects.create(
                pkqt_assessment_num=assess_obj,
                pkqt_quotation_summary=summary_record,
                pkqt_requirement=req_obj,
                pkqt_cost_type_id=other_charges_type.id if other_charges_type else 11,
                pkqt_stock_description=other_sd,
                pkqt_itemdescription=desc_obj,
                pkqt_uom=svc_uom,
                pkqt_quantity=round(1.0 * box_qty, 2),
                pkqt_quantity_req=1.0,
                pkqt_sqrt_req=1.0,
                pkqt_rate=amt,
                pkqt_total_cost=amt,
                pkqt_totalbox_cost=totalbox_val,
                pkqt_na_quantity=box_qty,
                pkqt_updated_by_id=user_id,
            )
            created_count += 1

    # 5. Update or Create PkquotationsummaryInfo
    summary_data = data.get('summary', {})
    summary = summary_record
    if not summary:
        summary = PkquotationsummaryInfo.objects.filter(qs_assessment_num=assess_obj, qs_is_latest=True).first()
    if not summary:
        summary = PkquotationsummaryInfo(
            qs_assessment_num=assess_obj,
            qs_quotation_number=f"QS_{assess_obj.na_assessment_num}",
        )

    unit_wood = float(summary_data.get('wood_cost') or data.get('total_wood_cost') or 0.0)
    unit_ply = float(summary_data.get('plywood_cost') or data.get('total_ply_cost') or 0.0)
    unit_mat = float(summary_data.get('consumables_cost') or data.get('total_material_cost') or 0.0)
    unit_inhouse_labour = float(summary_data.get('labour_cost') or other_costs.get('labour_cost') or data.get('labour_cost') or 0.0)
    unit_onsite_labour = float(summary_data.get('onsite_labour_cost') or other_costs.get('onsite_labour_cost') or data.get('onsite_labour_cost') or 0.0)
    unit_transport = float(summary_data.get('transport_cost') or other_costs.get('transport_cost') or data.get('transport_cost') or 0.0)
    unit_crane = float(summary_data.get('crane_cost') or other_costs.get('crane_cost') or data.get('crane_cost') or 0.0)
    unit_ht = float(summary_data.get('ht_cost') or other_costs.get('ht_cost') or data.get('ht_cost') or 0.0)

    margin_val = float(summary_data.get('margin_pct') or data.get('margin_pct') or 0.0)
    summary.qs_margin = margin_val

    all_summary_items = PkquotationInfo.objects.filter(pkqt_assessment_num=assess_obj)
    if summary.id:
        all_summary_items = all_summary_items.filter(pkqt_quotation_summary=summary)

    tot_wood = round(sum(q.pkqt_totalbox_cost or 0.0 for q in all_summary_items if q.pkqt_cost_type_id == 8 and q.pkqt_stock_type_id in [1, 5]), 2)
    tot_ply = round(sum(q.pkqt_totalbox_cost or 0.0 for q in all_summary_items if q.pkqt_cost_type_id == 8 and q.pkqt_stock_type_id in [4, 6]), 2)
    tot_mat = round(sum(q.pkqt_totalbox_cost or 0.0 for q in all_summary_items if q.pkqt_cost_type_id == 8 and q.pkqt_stock_type_id == 2), 2)
    tot_labour = round(sum(q.pkqt_totalbox_cost or 0.0 for q in all_summary_items if q.pkqt_cost_type_id in [3, 9]), 2)
    tot_transport = round(sum(q.pkqt_totalbox_cost or 0.0 for q in all_summary_items if q.pkqt_cost_type_id == 4), 2)
    tot_crane = round(sum(q.pkqt_totalbox_cost or 0.0 for q in all_summary_items if q.pkqt_cost_type_id == 6), 2)
    tot_ht = round(sum(q.pkqt_totalbox_cost or 0.0 for q in all_summary_items if q.pkqt_cost_type_id == 5), 2)
    tot_custom = round(sum(q.pkqt_totalbox_cost or 0.0 for q in all_summary_items if q.pkqt_cost_type_id == 11), 2)
    tot_engineer = round(sum(q.pkqt_totalbox_cost or 0.0 for q in all_summary_items if q.pkqt_cost_type_id == 2), 2)
    tot_cft = round(sum((q.pkqt_sqrt_req or 0.0) * (q.pkqt_na_quantity or 1) for q in all_summary_items if q.pkqt_cost_type_id == 8 and q.pkqt_stock_type_id in [1, 5]), 3)
    tot_sqft = round(sum((q.pkqt_sqrt_req or 0.0) * (q.pkqt_na_quantity or 1) for q in all_summary_items if q.pkqt_cost_type_id == 8 and q.pkqt_stock_type_id in [4, 6]), 3)

    summary.qs_wood_cost = tot_wood
    summary.qs_plywood_cost = tot_ply
    summary.qs_material_cost = tot_mat
    summary.qs_labour_cost = tot_labour
    summary.qs_transport_cost = tot_transport
    summary.qs_crane_cost = tot_crane
    summary.qs_ht_cost = tot_ht
    summary.qs_engineer_cost = tot_engineer
    summary.qs_total_cft = tot_cft
    summary.qs_total_sqft = tot_sqft
    if tot_cft > 0:
        summary.qs_rate_per_cft = round(tot_wood / tot_cft, 2)
    if tot_sqft > 0:
        summary.qs_rate_per_sqft = round(tot_ply / tot_sqft, 2)

    tot_wom = round(tot_wood + tot_ply + tot_mat + tot_labour + tot_transport + tot_crane + tot_ht + tot_custom + tot_engineer, 2)
    tot_wm = round(tot_wom * (1.0 + (margin_val / 100.0)), 2)
    summary.qs_total_cost_wom = tot_wom
    summary.qs_total_cost_wm = tot_wm
    summary.qs_final_cost = tot_wm
    if user_id:
        summary.qs_updated_by_id = user_id
    summary.save()

    recalculate_dependent_costs(assess_obj.id, request)

    return JsonResponse({
        'status': 'success',
        'message': f'Quotation matrix saved successfully with {created_count} items.',
        'created_count': created_count,
        'summary_id': summary.id,
        'grand_total': float(summary.qs_final_cost or 0.0),
    })


@login_required(login_url='login_page')
def matrix_part_code_search(request):
    """
    Search part codes and warehouse GRN stock batches with live filtering.
    """
    query = request.GET.get('q', '').strip()
    stock_type = request.GET.get('type', '').strip().lower()
    limit = int(request.GET.get('limit', 40))

    results = []

    # If specifically searching GRN batches or query contains GRN
    if stock_type == 'grn' or 'grn' in query.lower():
        sm_qs = StockMaintenance.objects.filter(
            sm_stock_purchase_number__isnull=False,
            sm_stock_type_id=1
        ).select_related('sm_partcode', 'sm_partcode__pc_stock_type', 'sm_partcode__pc_stock_description', 'sm_partcode__pc_uom')

        if query:
            sm_qs = sm_qs.filter(
                Q(sm_stock_purchase_number__icontains=query) |
                Q(sm_partcode__pc_code__icontains=query) |
                Q(sm_description__icontains=query)
            )

        for batch in sm_qs.order_by('-id')[:limit]:
            p = batch.sm_partcode
            results.append({
                'id': p.id if p else batch.id,
                'stock_purchase_id': batch.id,
                'code': p.pc_code if p else '',
                'grn_number': batch.sm_stock_purchase_number,
                'stock_type': p.pc_stock_type.pk_stocktype if p and p.pc_stock_type else 'Warehouse Stock',
                'description': batch.sm_description or (p.pc_stock_description.stock_description if p and p.pc_stock_description else ''),
                'length': float(batch.sm_length or (p.pc_length if p else 0.0) or 0.0),
                'width': float(batch.sm_width or (p.pc_width if p else 0.0) or 0.0),
                'height': float(batch.sm_thickness or (p.pc_height if p else 0.0) or 0.0),
                'available_qty': float(batch.sm_count or 0.0),
                'batch_rate': float(batch.sm_per_unit_cost or 0.0),
                'uom': p.pc_uom.unit_of_measure if p and p.pc_uom else '',
                'is_grn': True,
                'is_wood': (p.pc_stock_type_id in [1, 5]) if (p and p.pc_stock_type_id) else True,
                'is_plywood': (p.pc_stock_type_id in [4, 6]) if (p and p.pc_stock_type_id) else False,
            })
        return JsonResponse({'status': 'success', 'results': results})

    # Otherwise query standard PkpartcodeInfo catalog
    qs = PkpartcodeInfo.objects.all().select_related('pc_stock_type', 'pc_stock_description', 'pc_uom')

    if stock_type == 'wood':
        qs = qs.filter(Q(pc_stock_type_id__in=[1, 5]) | Q(pc_code__startswith='K') | Q(pc_code__startswith='RW'))
    elif stock_type == 'plywood':
        qs = qs.filter(Q(pc_stock_type_id__in=[4, 6]) | Q(pc_code__startswith='PY') | Q(pc_code__startswith='MPY'))
    elif stock_type == 'nails':
        qs = qs.filter(Q(pc_code__startswith='N') | Q(pc_stock_description__stock_description__icontains='nail'))
    elif stock_type == 'consumables':
        qs = qs.filter(pc_stock_type_id=2)

    if query:
        qs = qs.filter(
            Q(pc_code__icontains=query) |
            Q(pc_stock_description__stock_description__icontains=query)
        )

    partcodes = list(qs.order_by('pc_code')[:limit])
    pc_ids = [p.id for p in partcodes]

    # Map latest active GRN batch for each part code if exists in warehouse
    grn_map = {}
    if pc_ids:
        batches = StockMaintenance.objects.filter(
            sm_partcode_id__in=pc_ids,
            sm_stock_purchase_number__isnull=False,
            sm_stock_type_id=1
        ).order_by('-id')
        for b in batches:
            if b.sm_partcode_id not in grn_map:
                grn_map[b.sm_partcode_id] = b

    for pc in partcodes:
        st_name = pc.pc_stock_type.pk_stocktype if pc.pc_stock_type else ''
        sd_name = pc.pc_stock_description.stock_description if pc.pc_stock_description else ''
        uom_name = pc.pc_uom.unit_of_measure if pc.pc_uom else ''
        grn_batch = grn_map.get(pc.id)

        results.append({
            'id': pc.id,
            'stock_purchase_id': grn_batch.id if grn_batch else None,
            'grn_number': grn_batch.sm_stock_purchase_number if grn_batch else '',
            'available_qty': float(grn_batch.sm_count or 0.0) if grn_batch else None,
            'batch_rate': float(grn_batch.sm_per_unit_cost or 0.0) if grn_batch else None,
            'code': pc.pc_code,
            'stock_type': st_name,
            'stock_type_id': pc.pc_stock_type_id,
            'description': sd_name,
            'length': float(pc.pc_length or 0.0),
            'width': float(pc.pc_width or 0.0),
            'height': float(pc.pc_height or 0.0),
            'uom': uom_name,
            'is_wood': (pc.pc_stock_type_id in [1, 5]) or pc.pc_code.startswith('K') or pc.pc_code.startswith('RW'),
            'is_plywood': (pc.pc_stock_type_id in [4, 6]) or pc.pc_code.startswith('PY') or pc.pc_code.startswith('MPY'),
        })

    return JsonResponse({'status': 'success', 'results': results})


@login_required(login_url='login_page')
def box_costing_matrix_view(request, na_assessment_num_id=0, requirement_id=0):
    """
    Dedicated Standalone Page for Fast Excel-Style Box Costing Matrix.
    """
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if not requirement_id:
        req_param = request.GET.get('requirement_id') or request.GET.get('req_id')
        if req_param and str(req_param).isdigit():
            requirement_id = int(req_param)

    if na_assessment_num_id == 0:
        na_assessment_num_id = request.session.get('na_assessment_id') or request.session.get('na_assessment_num_id', 0)
        if not na_assessment_num_id:
            latest_assess = PkneedassessmentInfo.objects.order_by('-id').first()
            if latest_assess:
                na_assessment_num_id = latest_assess.id

    assess_obj = PkneedassessmentInfo.objects.filter(id=na_assessment_num_id).first()
    if not assess_obj:
        summary_lookup = PkquotationsummaryInfo.objects.filter(id=na_assessment_num_id).first()
        if summary_lookup and summary_lookup.qs_assessment_num:
            assess_obj = summary_lookup.qs_assessment_num

    if not assess_obj:
        messages.error(request, "Assessment record not found.")
        return redirect('pk_quotationsummary_list')

    # Update session so other quotation views stay in sync
    request.session['na_assessment_id'] = assess_obj.id
    request.session['na_assessment_num_id'] = assess_obj.id

    requirements = Nadimension.objects.filter(nad_assess_num_id=assess_obj.id).order_by('id')
    requirements_list = []
    has_quoted = False

    for req in requirements:
        is_quoted = PkquotationInfo.objects.filter(
            pkqt_assessment_num=assess_obj,
            pkqt_requirement=req
        ).exists()
        if is_quoted:
            has_quoted = True

        requirements_list.append({
            'id': req.id,
            'nad_item': req.nad_item,
            'nad_type_of_req': req.nad_type_of_req or '',
            'nad_length': float(req.nad_length or 0.0),
            'nad_width': float(req.nad_width or 0.0),
            'nad_height': float(req.nad_height or 0.0),
            'nad_uom': req.nad_uom or 'cm',
            'nad_quantity': req.nad_quantity or 1,
            'nad_clearance': float(req.nad_clearance) if req.nad_clearance is not None else 0.0,
            'nad_plywood_thickness': float(req.nad_plywood_thickness) if req.nad_plywood_thickness is not None else 0.0,
            'nad_clr_length': float(req.nad_clr_length or 0.0),
            'nad_clr_width': float(req.nad_clr_width or 0.0),
            'nad_clr_top': float(req.nad_clr_top or 0.0),
            'nad_thk_length': float(req.nad_thk_length or 7.0),
            'nad_thk_width': float(req.nad_thk_width or 7.0),
            'nad_thk_height': float(req.nad_thk_height or 20.0),
            'nad_dimension_type': str(req.nad_dimension_type.dimension_type if req.nad_dimension_type else 'Cargo OD'),
            'nad_job_weight': float(req.nad_job_weight or 0.0),
            'nad_customer_part_code': req.nad_customer_part_code or '',
            'nad_type_of_req_id': req.nad_type_of_req_id,
            'is_quoted': is_quoted,
        })

    summary_id_param = request.GET.get('summary_id') or request.session.get('quotationsummary_id')
    summary = None
    if summary_id_param and str(summary_id_param).strip().isdigit():
        summary = PkquotationsummaryInfo.objects.filter(id=int(summary_id_param)).first()
    if not summary:
        summary = PkquotationsummaryInfo.objects.filter(qs_assessment_num=assess_obj, qs_is_latest=True).first()
    if not summary:
        summary = PkquotationsummaryInfo.objects.filter(qs_assessment_num=assess_obj).order_by('-id').first()
    if summary:
        request.session['quotationsummary_id'] = summary.id

    # Auto-select the unquoted/pending requirement for creating a new quote.
    # If the user wants to view/edit a previously saved quote, they click the Edit icon on that row.
    if not requirement_id and requirements_list:
        unquoted_req = next((r['id'] for r in requirements_list if not r.get('is_quoted')), None)
        if unquoted_req:
            requirement_id = unquoted_req
        elif request.GET.get('mode') == 'new':
            requirement_id = None
        else:
            requirement_id = requirements_list[0]['id']

    typeofreq_list = Natypeofreq.objects.all().order_by('type_of_req')
    from .general_utils import generate_next_number, get_financial_year
    fy = get_financial_year()
    next_item_number = generate_next_number(Nadimension, 'nad_item', f"{fy}_MAA_ITM_", 6)
    unquoted_list = [r for r in requirements_list if not r.get('is_quoted')]

    # Build dictionary of existing operational costs per requirement
    import json
    operational_costs_map = {}
    q_filter = {'pkqt_assessment_num': assess_obj}
    if summary:
        q_filter['pkqt_quotation_summary'] = summary

    op_items = PkquotationInfo.objects.filter(**q_filter).filter(pkqt_cost_type_id__in=[3, 4, 5, 6, 9, 10, 11])
    saved_custom_breakdown = []
    for item in op_items:
        r_id = item.pkqt_requirement_id
        if r_id not in operational_costs_map:
            operational_costs_map[r_id] = {
                'crane': 0.0, 'transport': 0.0, 'labour': 0.0, 'onsite_labour': 0.0, 'ht': 0.0, 'fumigation': 0.0, 'custom_items': []
            }
        ct = item.pkqt_cost_type_id
        rate = float(item.pkqt_rate or item.pkqt_total_cost or 0.0)
        if ct == 6: operational_costs_map[r_id]['crane'] = rate
        elif ct == 4: operational_costs_map[r_id]['transport'] = rate
        elif ct == 3: operational_costs_map[r_id]['labour'] = rate
        elif ct == 9: operational_costs_map[r_id]['onsite_labour'] = rate
        elif ct == 5: operational_costs_map[r_id]['ht'] = rate
        elif ct == 10: operational_costs_map[r_id]['fumigation'] = rate
        elif ct == 11 or (item.pkqt_cost_type and 'other' in item.pkqt_cost_type.cost_type.lower()):
            lbl = item.pkqt_itemdescription.id_item_description if item.pkqt_itemdescription else 'Other Charges'
            operational_costs_map[r_id]['custom_items'].append({'label': lbl, 'amount': rate})
            if r_id == requirement_id:
                saved_custom_breakdown.append({'label': lbl, 'amount': rate})

    standard_plywood_sheets, other_plywood_sheets = get_plywood_sheets_catalog()

    # Preload saved structural items, nails, and materials for selected requirement
    saved_structural_items = []
    saved_nails_items = []
    saved_materials_items = []
    wood_rate = float(summary.qs_rate_per_cft or 0.0) if summary else 0.0
    ply_rate = 0.0

    if requirement_id:
        req_rows_filter = {'pkqt_assessment_num': assess_obj, 'pkqt_requirement_id': requirement_id}
        if summary:
            req_rows_filter['pkqt_quotation_summary'] = summary
        req_saved_rows = PkquotationInfo.objects.filter(**req_rows_filter).select_related(
            'pkqt_cost_type', 'pkqt_stock_type', 'pkqt_stock_description', 'pkqt_item', 'pkqt_itemdescription', 'pkqt_part_code', 'pkqt_uom'
        )

        for row in req_saved_rows:
            desc_str = ''
            if row.pkqt_itemdescription: desc_str = row.pkqt_itemdescription.id_item_description
            elif row.pkqt_stock_description: desc_str = row.pkqt_stock_description.stock_description
            elif row.pkqt_item: desc_str = row.pkqt_item.item_name

            code = row.pkqt_part_code.pc_code if row.pkqt_part_code else ''
            qty = float(row.pkqt_quantity_req or 0.0)
            rate = float(row.pkqt_rate or 0.0)
            total = float(row.pkqt_total_cost or 0.0)

            if row.pkqt_stock_type_id in [4, 6] and rate > 0 and not ply_rate:
                ply_rate = rate

            is_nail = (row.pkqt_stock_type_id == 2 and (code.startswith('N') or 'nail' in desc_str.lower()))
            if is_nail:
                saved_nails_items.append({'id': row.id, 'name': desc_str, 'code': code, 'qty': qty, 'rate': rate, 'total_cost': total})
                continue

            is_material = (row.pkqt_stock_type_id == 2 or row.pkqt_cost_type_id in [1, 2, 7])
            if is_material:
                saved_materials_items.append({'id': row.id, 'name': desc_str, 'code': code, 'qty': qty, 'rate': rate, 'total_cost': total})
                continue

            # Skip operational costs (Labour, Transport, HT, Crane, Fumigation) from structure table
            if row.pkqt_cost_type_id in [3, 4, 5, 6, 9, 10] or not row.pkqt_stock_type_id:
                continue

            sec_name = 'BASE'
            sec_class = 'sec-base'
            iname = (row.pkqt_item.item_name if row.pkqt_item else '').upper()
            dname = desc_str.upper()
            if 'BASE' in iname or 'BASE' in dname or 'LIFTING' in dname or 'DECK' in dname:
                sec_name = 'BASE'
                sec_class = 'sec-base'
            elif 'LENGTH' in iname or 'LENGTH' in dname:
                sec_name = 'LENGTH (2 SIDES)'
                sec_class = 'sec-length'
            elif 'WIDTH' in iname or 'WIDTH' in dname:
                sec_name = 'WIDTH (2 SIDES)'
                sec_class = 'sec-width'
            elif 'TOP' in iname or 'TOP' in dname:
                sec_name = 'TOP'
                sec_class = 'sec-top'
            elif 'ARREST' in iname or 'SUPPORT' in iname:
                sec_name = 'SUPPORTS & ARREST'
                sec_class = 'sec-supports'

            clean_name = desc_str
            if clean_name.strip().upper() == 'LENGTH':
                clean_name = 'LENGTH PANEL' if row.pkqt_stock_type_id in [4, 6] else 'LENGTH FRAME (HORIZ)'
            elif clean_name.strip().upper() == 'WIDTH':
                clean_name = 'WIDTH PANEL' if row.pkqt_stock_type_id in [4, 6] else 'WIDTH FRAME (HORIZ)'
            elif clean_name.strip().upper() == 'HEIGHT':
                clean_name = 'HEIGHT FRAME (VERT)'
            elif clean_name.strip().upper() == 'TOP ARREST' and row.pkqt_stock_type_id in [4, 6]:
                clean_name = 'TOP PANEL'

            saved_structural_items.append({
                'id': row.id, 'section': sec_name, 'secClass': sec_class,
                'name': clean_name, 'part_code': code,
                'mat': 'plywood' if row.pkqt_stock_type_id in [4, 6] else 'wood',
                'l': float(row.pkqt_length_req or 0.0), 'w': float(row.pkqt_width_req or 0.0), 'h': float(row.pkqt_height_req or 0.0),
                'nos': float(row.pkqt_quantity_req or 0.0), 'rate': rate, 'total_cost': total
            })

    if not ply_rate and assess_obj:
        ply_row = PkquotationInfo.objects.filter(pkqt_assessment_num=assess_obj, pkqt_stock_type_id__in=[4, 6], pkqt_rate__gt=0).first()
        if ply_row:
            ply_rate = float(ply_row.pkqt_rate)

    context = {
        'na_assessment_num_id': assess_obj.id,
        'assessment_num': assess_obj.na_assessment_num,
        'customer_name': str(assess_obj.na_customer_name) if assess_obj.na_customer_name else '',
        'requirements_list': requirements_list,
        'unquoted_list': unquoted_list,
        'has_quoted': has_quoted,
        'selected_requirement_id': requirement_id,
        'summary': summary,
        'summary_id': summary.id if summary else 0,
        'typeofreq_list': typeofreq_list,
        'next_item_number': next_item_number,
        'operational_costs_json': json.dumps(operational_costs_map),
        'standard_plywood_sheets': standard_plywood_sheets,
        'other_plywood_sheets': other_plywood_sheets,
        'saved_structural_json': json.dumps(saved_structural_items),
        'saved_nails_json': json.dumps(saved_nails_items),
        'saved_materials_json': json.dumps(saved_materials_items),
        'saved_custom_breakdown_json': json.dumps(saved_custom_breakdown),
        'wood_rate': wood_rate,
        'ply_rate': ply_rate,
    }

    return render(request, 'asset_mgt_app/box_costing_matrix.html', context)


@login_required(login_url='login_page')
def matrix_create_box_item(request):
    """
    Fast 1-Click creation of a new Box / Job Item (Nadimension) directly from Box Costing Matrix.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST method required.'}, status=405)

    import json
    from .general_utils import generate_next_number, get_financial_year

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    assessment_id = data.get('assessment_id')
    assess_obj = PkneedassessmentInfo.objects.filter(id=assessment_id).first()
    if not assess_obj:
        summary_lookup = PkquotationsummaryInfo.objects.filter(id=assessment_id).first()
        if summary_lookup and summary_lookup.qs_assessment_num:
            assess_obj = summary_lookup.qs_assessment_num

    if not assess_obj:
        return JsonResponse({'status': 'error', 'message': 'Invalid assessment number.'})

    type_of_req_id = data.get('type_of_req_id')
    req_type_obj = None
    if type_of_req_id:
        req_type_obj = Natypeofreq.objects.filter(id=type_of_req_id).first()
    if not req_type_obj:
        req_type_obj = Natypeofreq.objects.filter(type_of_req__icontains='Plywood Box').first() or Natypeofreq.objects.first()

    length = float(data.get('length') or 0.0)
    width = float(data.get('width') or 0.0)
    height = float(data.get('height') or 0.0)
    raw_clr = data.get('clearance')
    clearance = float(raw_clr) if (raw_clr is not None and str(raw_clr).strip() != '') else 0.0
    qty = int(data.get('quantity') or 1)
    user_id = request.session.get('ses_userID')

    if length <= 0 or width <= 0 or height <= 0:
        return JsonResponse({'status': 'error', 'message': 'Length, Width, and Height must be greater than zero.'})

    custom_item_num = (data.get('item_number') or '').strip()
    if custom_item_num:
        next_item_num = custom_item_num
    else:
        fy = get_financial_year()
        prefix = f"{fy}_MAA_ITM_"
        next_item_num = generate_next_number(Nadimension, 'nad_item', prefix, 6)

    cm_uom = Unitofmeasure.objects.filter(id=3).first() or Unitofmeasure.objects.filter(unit_of_measure__iexact='cm').first()

    new_dim = Nadimension.objects.create(
        nad_assess_num=assess_obj,
        nad_item=next_item_num,
        nad_type_of_req=req_type_obj,
        nad_length=length,
        nad_width=width,
        nad_height=height,
        nad_clearance=clearance,
        nad_plywood_thickness=clearance,
        nad_quantity=qty,
        nad_uom=cm_uom,
        nad_updated_by_id=user_id,
    )

    return JsonResponse({
        'status': 'success',
        'message': f'New box {next_item_num} created successfully.',
        'item': {
            'id': new_dim.id,
            'nad_item': new_dim.nad_item,
            'nad_type_of_req': str(new_dim.nad_type_of_req.type_of_req) if new_dim.nad_type_of_req else 'Box',
            'length': float(new_dim.nad_length or 0.0),
            'width': float(new_dim.nad_width or 0.0),
            'height': float(new_dim.nad_height or 0.0),
            'clearance': float(new_dim.nad_clearance) if new_dim.nad_clearance is not None else 0.0,
            'plywood_thickness': float(new_dim.nad_plywood_thickness) if new_dim.nad_plywood_thickness is not None else 0.0,
            'dim_type': str(new_dim.nad_dimension_type.dimension_type if new_dim.nad_dimension_type else 'Cargo OD'),
            'quantity': int(new_dim.nad_quantity or 1),
            'uom': str(new_dim.nad_uom.unit_of_measure) if new_dim.nad_uom else 'cm',
            'is_quoted': False,
        }
    })
