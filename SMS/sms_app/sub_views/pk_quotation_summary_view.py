from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from xhtml2pdf import pisa

from ..views import Pkcosting_delete,Pkcostingsummary_delete,Pkpurchaseorder_delete,Pkpurchaseorder_dim_delete,Pkquotation_delete,Pkquotation_summary_delete,get_tracker_flags
from ..forms import PkcostingsummaryForm,PkquotationsummaryForm
from ..models import pk_stock_statusinfo,PkcostingInfo,User_extInfo,Nadimension,PkquotationsummaryInfo,PkneedassessmentInfo,PkquotationInfo,PkcostingsummaryInfo,PkpurchaseorderInfo,StatusList,POdimension
from django.shortcuts import render, redirect
from django.db.models.aggregates import Sum
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id
from ..sub_models.stock_maintenance_mod import StockMaintenance


@login_required(login_url='login_page')
def pk_quotationsummary_add(request, pk_quotationsummary_id=0):
    global financial_year, last_id
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = User_extInfo.objects.get(user=user_id).emp_role.id

    if request.method == "GET":
        if pk_quotationsummary_id == 0:
            # Check if na_id is passed from "Convert to Quotation" button
            na_id = request.GET.get('na_id')
            initial_data = {}
            if na_id:
                try:
                    na_obj = PkneedassessmentInfo.objects.get(pk=na_id)
                    initial_data['qs_assessment_num'] = na_obj.id
                    initial_data['qs_customer_name_2'] = na_obj.na_customer_name_id
                    initial_data['pkqt_customer_new_name'] = na_obj.na_customer_new_name or ''
                except PkneedassessmentInfo.DoesNotExist:
                    pass
            form = PkquotationsummaryForm(initial=initial_data, na_id=na_id)
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'role': role,
                'role_id': role_id,
                'current_step': 'quotation',
            }
        else:
            quotationsummary = PkquotationsummaryInfo.objects.get(pk=pk_quotationsummary_id)
            needassessment_num = quotationsummary.qs_assessment_num
            needassessment_id = PkneedassessmentInfo.objects.get(na_assessment_num=needassessment_num).id
            customer_name_id = quotationsummary.qs_customer_name_2.id if quotationsummary.qs_customer_name_2 else None
            customer_new_name_id = quotationsummary.pkqt_customer_new_name if quotationsummary.pkqt_customer_new_name else ""

            request.session['na_assessment_id'] = needassessment_id
            request.session['na_customer_name_id'] = customer_name_id
            request.session['na_customer_new_name'] = customer_new_name_id
            form = PkquotationsummaryForm(instance=quotationsummary)
            quotation_list = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id)

            # Aggregate costs
            def get_aggregate_cft(assessment_id, cost_type, stock_types=None):
                filter_kwargs = {'pkqt_assessment_num': assessment_id, 'pkqt_cost_type': cost_type}
                if stock_types:
                    filter_kwargs['pkqt_stock_type__in'] = stock_types
                cost = PkquotationInfo.objects.filter(**filter_kwargs).aggregate(Sum('pkqt_sqrt_req'))[
                    'pkqt_sqrt_req__sum']
                return round(cost, 2) if cost is not None else 0.0

            def get_aggregate_cost(assessment_id, cost_type, stock_types=None):
                filter_kwargs = {'pkqt_assessment_num': assessment_id, 'pkqt_cost_type': cost_type}
                if stock_types:
                    filter_kwargs['pkqt_stock_type__in'] = stock_types
                cost = PkquotationInfo.objects.filter(**filter_kwargs).aggregate(Sum('pkqt_totalbox_cost'))[
                    'pkqt_totalbox_cost__sum']
                return round(cost, 2) if cost is not None else 0.0

            wood_cost = get_aggregate_cost(needassessment_id, 8, [1, 4])
            total_cft = get_aggregate_cft(needassessment_id, 8, [1])
            engineer_cost = get_aggregate_cost(needassessment_id, 2)
            packing_labour_cost = get_aggregate_cost(needassessment_id, 3)
            labour_cost = packing_labour_cost
            crane_cost = get_aggregate_cost(needassessment_id, 6)
            ht_cost = PkquotationInfo.objects.filter(
                pkqt_assessment_num=needassessment_id,
                pkqt_cost_type=5
            ).aggregate(Sum('pkqt_total_cost'))['pkqt_total_cost__sum'] or 0.0

            ht_cost = round(ht_cost, 2)
            management_cost = get_aggregate_cost(needassessment_id, 7)
            material_cost = get_aggregate_cost(needassessment_id, 8, [2])
            transport_cost = get_aggregate_cost(needassessment_id, 4)

            # Update quotation summary
            PkquotationsummaryInfo.objects.filter(qs_assessment_num=needassessment_id).update(
                qs_wood_cost=wood_cost,
                qs_total_cft=total_cft,
                qs_engineer_cost=engineer_cost,
                qs_labour_cost=labour_cost,
                qs_crane_cost=crane_cost,
                qs_ht_cost=ht_cost,
                qs_management_cost=management_cost,
                qs_material_cost=material_cost,
                qs_transport_cost=transport_cost
            )

            # Fetch linked POs for the hub
            linked_pos = PkpurchaseorderInfo.objects.filter(po_quotation_num=pk_quotationsummary_id)

            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'quotation_list': quotation_list,
                'wood_cost': wood_cost,
                'engineer_cost': engineer_cost,
                'labour_cost': labour_cost,
                'crane_cost': crane_cost,
                'ht_cost': ht_cost,
                'management_cost': management_cost,
                'material_cost': material_cost,
                'transport_cost': transport_cost,
                'role_id': role_id,
                'role': role,
                'linked_pos': linked_pos,
                'current_step': 'quotation',
                'tracker_flags': get_tracker_flags(needassessment_id),
            }

        return render(request, "asset_mgt_app/pk_quotationsummary_add.html", context)

    else:
        post_na_id = request.POST.get('qs_assessment_num')
        if pk_quotationsummary_id == 0:
            form = PkquotationsummaryForm(request.POST, na_id=post_na_id)
        else:
            quotationsummary = PkquotationsummaryInfo.objects.get(pk=pk_quotationsummary_id)
            form = PkquotationsummaryForm(request.POST, instance=quotationsummary, na_id=post_na_id)

        if form.is_valid():
            print("Requirement Form is Valid")
            quotation_num = form.cleaned_data['qs_quotation_number']
            
            # Uniqueness check logic
            is_duplicate = False
            if quotation_num:
                is_duplicate = PkquotationsummaryInfo.objects.filter(qs_quotation_number=quotation_num).exclude(id=pk_quotationsummary_id).exists()
                
            if not is_duplicate:
                instance = form.save()
                if pk_quotationsummary_id == 0:
                    try:
                        # Generate Quotation Summary number based on financial year (Branch specific)
                        fy = get_financial_year()
                        branch_id = get_session_branch_id(request)
                        branch_code = get_branch_code(branch_id)
                        prefix = f"{fy}_{branch_code}_QS_"
                        quotation_num_next = generate_next_number(PkquotationsummaryInfo, 'qs_quotation_number', prefix, 6)
                        
                        # Update the instance with the generated number
                        instance.qs_quotation_number = quotation_num_next
                        instance.save()
                        messages.success(request, 'Record Created Successfully with Quotation Number: ' + quotation_num_next)
                        last_id = instance.id # For redirection
                    except Exception as e:
                        print(f"Error generating quotation number: {str(e)}")
                        last_id = instance.id
                else:
                    last_id = pk_quotationsummary_id
                    messages.success(request, 'Record Updated Successfully')
                
                # Fetch the saved instance to check the status and update parent assessment
                saved_summary = PkquotationsummaryInfo.objects.get(id=last_id)
                if saved_summary.qs_status and saved_summary.qs_status.id == 5:
                    if saved_summary.qs_assessment_num:
                        saved_summary.qs_assessment_num.na_status_id = 5
                        saved_summary.qs_assessment_num.save()
                        
                if pk_quotationsummary_id == 0:
                    return redirect('/SMS/pk_quotationsummary_update/' + str(last_id))
                else:
                    # Redirect back to where they came from or referer
                    referer = request.META.get('HTTP_REFERER')
                    if referer:
                        return redirect(referer)
                    else:
                        return redirect('/SMS/pk_quotationsummary_list')
            else:
                messages.error(request, 'Please enter a Unique Quotation Number.')
        else:
            messages.error(request, 'Record NOT Updated Successfully')
            # If the form is not valid, print errors for debugging
            print(f"Form errors: {form.errors}")
        
        # In case of error (duplicate or invalid form), instead of just REFERER which can cause issues or redirect loops if they just clicked submit
        # we try to stay on the same page or redirect back
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('/SMS/pk_quotationsummary_list')
# List quotationsummary
@login_required(login_url='login_page')
def pk_quotationsummary_list(request):
    first_name = request.session.get('first_name')
    context = {'quotationsummary_list' : PkquotationsummaryInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_quotationsummary_list.html",context)

#Delete quotationsummary
@login_required(login_url='login_page')
def pk_quotationsummary_delete(request,pk_quotationsummary_id):
    quotationsummary = PkquotationsummaryInfo.objects.get(pk=pk_quotationsummary_id)
    assessment_num=quotationsummary.qs_assessment_num

    # Deleting PkcostingInfo objects
    Pkcosting_delete(assessment_num)

    # Deleting Pkcosting summary objects
    Pkcostingsummary_delete(assessment_num)

    # Deleting Pkpurchaseorders objects
    Pkpurchaseorder_delete(assessment_num)

    # Deleting Pkpurchaseorders dims objects
    Pkpurchaseorder_dim_delete(assessment_num)

    # Deleting Pkquotations objects
    Pkquotation_delete(assessment_num)

    # Deleting quotation summary objects
    Pkquotation_summary_delete(assessment_num)

    return redirect('/SMS/pk_quotationsummary_list')


@login_required(login_url='login_page')
def pk_quotation_summary_check_unique_field(request):
    qs_assessment_num = request.GET.get('qs_assessment_num')

    try:
        need_assessment = PkneedassessmentInfo.objects.get(id=qs_assessment_num)

        # Safely access fields, handling possible None values
        customer_name_id = need_assessment.na_customer_name.id if need_assessment.na_customer_name else None
        customer_new_name = need_assessment.na_customer_new_name if need_assessment.na_customer_new_name else ""

    except ObjectDoesNotExist:
        # Return an error if the specified assessment does not exist
        return JsonResponse({'error': 'Assessment not found'}, status=404)

    # Check if the assessment number already exists in the PkquotationsummaryInfo table
    exists = PkquotationsummaryInfo.objects.filter(qs_assessment_num=qs_assessment_num).exists()

    return JsonResponse({
        'exists': exists,
        'customer_name_id': customer_name_id,
        'customer_new_name': customer_new_name,
    })

@login_required(login_url='login_page')
def pk_bvm_quotation_pdf(request,quotation_id=0):
    needassessment_id = request.session.get('na_assessment_id')
    address=PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id).qs_address
    cost_includes=PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id).qs_cost_includes
    notes=PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id).qs_notes
    terms_condition=PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id).qs_terms_condition
    client_scope=PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id).qs_client_scope
    bvm_scope=PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id).qs_bvm_scope
    needassessment_num=PkneedassessmentInfo.objects.get(pk=needassessment_id).na_assessment_num
    quotation=Nadimension.objects.filter(nad_assess_num=needassessment_id)
    # get requirement type from need assessment dimension model
    na_req=Nadimension.objects.filter(nad_assess_num=needassessment_id)
    quotation_number = PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id).qs_quotation_number
    margin = PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id).qs_margin
    gst_val = PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id).qs_gst
    quotation_summary = PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id)
    customer_obj = quotation_summary.qs_customer_name_2
    new_customer_name = quotation_summary.pkqt_customer_new_name

    if customer_obj and customer_obj.id == 210:
        customer_display_name = f"Mr. {new_customer_name}"
    elif customer_obj:
        customer_display_name = f"Mr. {customer_obj.cu_name}"
    else:
        customer_display_name = f"Mr. {new_customer_name}" if new_customer_name else ""
    total_sum=0
    for i in na_req:
        k=i.id
        qty=i.nad_quantity
        print('i', i)
        print('k', k)
        print('qty', qty)
        total_cost_wom=PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id,pkqt_requirement=i).aggregate(total_cost=Sum('pkqt_total_cost'))['total_cost'] or 0
        print('total_cost_wom',total_cost_wom)
        total_cost=total_cost_wom+(total_cost_wom*margin/100)
        try:
            Nadimension.objects.filter(pk=k).update(nad_cost_unit=round(total_cost,0))
        except:
            Nadimension.objects.filter(pk=k).update(nad_cost_unit=0)
        try:
            Nadimension.objects.filter(pk=k).update(nad_cost_total=round(total_cost*qty,0))
        except:
            Nadimension.objects.filter(pk=k).update(nad_cost_total=0)
        # total_sum=round((total_sum+total_cost),2)
    totalbox_cost = Nadimension.objects.filter(nad_assess_num=needassessment_id).aggregate(totalbox_cost=Sum('nad_cost_total'))['totalbox_cost'] or 0

    print('totalbox_cost',totalbox_cost)
    gst=round(totalbox_cost*gst_val/100,0)
    final_cost=round((totalbox_cost+gst),0)
    today = datetime.now()
    formatted_date = today.strftime("%d-%b-%Y")
    context = {
        'address': address,
        'cost_includes': cost_includes,
        'notes': notes,
        'terms_condition': terms_condition,
        'client_scope': client_scope,
        'bvm_scope': bvm_scope,
        'quotation': quotation,
        'total_sum': totalbox_cost,
        'gst': gst,
        'gst_val': gst_val,
        'final_cost': final_cost,
        'quotation_number': quotation_number,
        'today_date': formatted_date,
        'customer_name': customer_display_name,
    }
    file_name = str("Quotation_") + str(needassessment_num) + str(".pdf")
    template_path = 'asset_mgt_app/bvm_pk_quotation_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    template = get_template(template_path)
    html = template.render(context)

    # Create PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We has some error <pre>' + html + '</pre>')
    return response


@login_required(login_url='login_page')
def pk_quotationsummary_clone(request, pk_quotationsummary_id):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = User_extInfo.objects.get(user=user_id).emp_role.id
    quotationsummary = get_object_or_404(PkquotationsummaryInfo, pk=pk_quotationsummary_id)

    if request.method == "GET":
        na_id = quotationsummary.qs_assessment_num.id if quotationsummary.qs_assessment_num else None

        # Prefill the form with values from the quotation summary
        form = PkcostingsummaryForm(na_id=na_id, initial={
            'cs_assessment_num': quotationsummary.qs_assessment_num,
            'cs_wood_cost': quotationsummary.qs_wood_cost,
            'cs_engineer_cost': quotationsummary.qs_engineer_cost,
            'cs_labour_cost': quotationsummary.qs_labour_cost,
            'cs_margin': quotationsummary.qs_margin,
            'cs_total_cost_wm': quotationsummary.qs_total_cost_wm,
            'cs_rate_per_cft': quotationsummary.qs_rate_per_cft,
            'cs_total_cft': quotationsummary.qs_total_cft,
            'cs_crane_cost': quotationsummary.qs_crane_cost,
            'cs_ht_cost': quotationsummary.qs_ht_cost,
            'cs_management_cost': quotationsummary.qs_management_cost,
            'cs_material_cost': quotationsummary.qs_material_cost,
            'cs_transport_cost': quotationsummary.qs_transport_cost,
            'cs_total_cost_wom': quotationsummary.qs_total_cost_wom,
            'cs_address': quotationsummary.qs_address,
            'cs_cost_includes': quotationsummary.qs_cost_includes,
            'cs_notes': quotationsummary.qs_notes,
            'cs_terms_condition': quotationsummary.qs_terms_condition,
            'cs_client_scope': quotationsummary.qs_client_scope,
            'cs_bvm_scope': quotationsummary.qs_bvm_scope,
            'cs_customer_name': quotationsummary.qs_customer_name_2,
            'cs_customer_new_name': quotationsummary.pkqt_customer_new_name,
            'cs_gst': quotationsummary.qs_gst,
            'cs_final_cost': quotationsummary.qs_final_cost,
            'cs_estimation_type': 1,
        })

        context = {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'role': role,
            'role_id': role_id,
        }
        return render(request, "asset_mgt_app/pk_costingsummary_add.html", context)

    elif request.method == "POST":
        costing_summary_id = None
        na_id = request.POST.get('cs_assessment_num')
        form = PkcostingsummaryForm(request.POST, request.FILES, na_id=na_id)
        if form.is_valid():
            customer_po = form.cleaned_data['cs_customer_po']

            # Check for an existing costing summary with the same assessment number and customer PO
            existing_summary = PkcostingsummaryInfo.objects.filter(
                cs_assessment_num=quotationsummary.qs_assessment_num,
                cs_customer_po=customer_po
            ).exists()

            if existing_summary:
                messages.error(request, 'A costing summary with the same assessment number and customer PO already exists.')
            else:
                # Create a new costing summary and copy all the necessary values from quotation
                costing_summary = form.save(commit=False)
                costing_summary.cs_updated_by_id = user_id
                costing_summary.save()
                messages.success(request, 'Costing summary cloned and saved successfully.')
                costing_summary_id = costing_summary.id


                # Fetch the quotation data using cs_assessment_num
                quotations = PkquotationInfo.objects.filter(
                    pkqt_assessment_num=quotationsummary.qs_assessment_num,
                )
                print(f"DEBUG: Found {quotations.count()} quotations for assessment {quotationsummary.qs_assessment_num}")
                stock_status_instance = pk_stock_statusinfo.objects.get(id=1)
                if quotations.exists():
                    for quotation in quotations:
                        print(f"DEBUG: Cloning quotation ID {quotation.id} / Item {quotation.pkqt_item}")
                        # Fetch quotation data and directly save it to costing summary
                        try:
                            costing_info = PkcostingInfo.objects.create(
                                ct_cost_type=quotation.pkqt_cost_type,
                                ct_stock_description=quotation.pkqt_stock_description,
                                ct_width=quotation.pkqt_width,
                                ct_height=quotation.pkqt_height,
                                ct_cft=quotation.pkqt_cft,
                                ct_rate=quotation.pkqt_rate,
                                ct_days=quotation.pkqt_days,
                                ct_total_cost=quotation.pkqt_total_cost,
                                ct_quantity=quotation.pkqt_quantity,
                                ct_size=quotation.pkqt_size,
                                ct_uom=quotation.pkqt_uom,
                                ct_assessment_num=quotation.pkqt_assessment_num,
                                ct_length=quotation.pkqt_length,
                                ct_stock_type=quotation.pkqt_stock_type,
                                ct_stock_purchase_number=quotation.pkqt_stock_purchase_number,
                                ct_item=quotation.pkqt_item,
                                ct_itemdescription=quotation.pkqt_itemdescription,
                                ct_requirement=quotation.pkqt_requirement,
                                ct_requirement_size=quotation.pkqt_requirement_size,
                                ct_width_req=quotation.pkqt_width_req,
                                ct_height_req=quotation.pkqt_height_req,
                                ct_length_req=quotation.pkqt_length_req,
                                ct_quantity_req=quotation.pkqt_quantity_req,
                                ct_sqrt_req=quotation.pkqt_sqrt_req,
                                ct_stock_status=stock_status_instance,
                                ct_customer_name=quotation.pkqt_customer_name,
                                ct_customer_new_name=quotation.pkqt_customer_new_name2,
                                ct_customer_po=customer_po,
                                ct_updated_by=request.user,
                                ct_na_quantity=quotation.pkqt_na_quantity,
                                ct_totalbox_cost=quotation.pkqt_totalbox_cost,
                                ct_part_code=quotation.pkqt_part_code,
                                ct_weight_sqft=quotation.pkqt_weight_sqft,
                                ct_weight_received=quotation.pkqt_weight_received,
                                ct_weight_Consumption=quotation.pkqt_weight_Consumption,
                                ct_total_cft_display=quotation.pkqt_total_cft_display,
                            )

                            # Create StockMaintenance Retrieval Record if it's a stock item (Type 8, Stock Type 1/4)
                            if quotation.pkqt_cost_type.id == 8 and quotation.pkqt_stock_purchase_number:
                                # User request: original GRN number should be in the 'sm_invoice_no' field for retrievals.
                                # No more 'RET-CLONE-' prefix.
                                ref_no = quotation.pkqt_stock_purchase_number
                                StockMaintenance.objects.create(
                                    sm_stock_type_id=2, # Retrieval
                                    sm_invoice_date=datetime.now().date(),
                                    sm_invoice_no=ref_no, # Standardizing: Putting original GRN here
                                    sm_description=f"Retrieved via Cloning for Assessment {quotation.pkqt_assessment_num}",
                                    sm_count=quotation.pkqt_quantity or 0,
                                    sm_total_cft=quotation.pkqt_sqrt_req or 0,
                                    sm_per_unit_cost=quotation.pkqt_rate or 0,
                                    sm_total_price=quotation.pkqt_totalbox_cost or 0,
                                    sm_updated_by_id=user_id
                                )
                            print(f"DEBUG: Successfully created costing info for quotation ID {quotation.id}")
                        except Exception as e:
                            print(f"DEBUG: Error cloning quotation ID {quotation.id} - {str(e)}")
                    messages.success(request, 'Quotation data saved to costing info successfully.')
                else:
                    messages.error(request, 'Quotation data could not be found.')
        else:
            # If the form is not valid, display specific field errors
            for field, errors in form.errors.items():
                messages.error(request, f"Error in {field}: {', '.join(errors)}")
            messages.error(request, 'Form is not valid. Please correct the errors.')

            # Check if costing_summary_id is set before redirecting
        if costing_summary_id:
            return redirect('/SMS/costingsummary_update/' + str(costing_summary_id))
        else:
            return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='login_page')
def pk_quotationsummary_clone_po(request, purchaseorder_id):
    """
    Clones all items from the Purchase Order Dimensions into a single Costing Summary.
    Uses 'Line-Level' cloning to support multiple lines of the same item with different quantities/dates.
    """
    po = get_object_or_404(PkpurchaseorderInfo, id=purchaseorder_id)
    po_items = POdimension.objects.filter(pod_po_num=po)
    
    # Get stock status for costing (default 1)
    try:
        stock_status_instance = pk_stock_statusinfo.objects.get(id=1)
    except pk_stock_statusinfo.DoesNotExist:
        stock_status_instance = None

    cloned_count = 0
    
    # NEW: Cleanup existing costing records for this PO that are no longer in the PO dimensions
    # Using Line-Level ID (POdimension ID) for cleanup
    current_pod_ids = po_items.values_list('id', flat=True)
    PkcostingInfo.objects.filter(ct_customer_po=po).exclude(ct_po_dimension_id__in=current_pod_ids).delete()

    for po_item in po_items:
        # Find all quotation details matching this item (Nadimension)
        quotations = PkquotationInfo.objects.filter(
            pkqt_requirement=po_item.pod_nad
        )
        
        for q in quotations:
            # Check if already cloned to prevent duplicates for this SPECIFIC PO LINE
            if not PkcostingInfo.objects.filter(
                ct_customer_po=po,
                ct_po_dimension=po_item,
                ct_cost_type=q.pkqt_cost_type
            ).exists():
                PkcostingInfo.objects.create(
                    ct_cost_type=q.pkqt_cost_type,
                    ct_stock_description=q.pkqt_stock_description,
                    ct_width=q.pkqt_width,
                    ct_height=q.pkqt_height,
                    ct_cft=q.pkqt_cft,
                    ct_rate=q.pkqt_rate,
                    ct_days=q.pkqt_days,
                    ct_total_cost=q.pkqt_total_cost,
                    ct_quantity=q.pkqt_quantity,
                    ct_size=q.pkqt_size,
                    ct_uom=q.pkqt_uom,
                    ct_assessment_num=q.pkqt_assessment_num,
                    ct_length=q.pkqt_length,
                    ct_stock_type=q.pkqt_stock_type,
                    ct_stock_purchase_number=q.pkqt_stock_purchase_number,
                    ct_item=q.pkqt_item,
                    ct_itemdescription=q.pkqt_itemdescription,
                    ct_requirement=q.pkqt_requirement,
                    ct_requirement_size=q.pkqt_requirement_size,
                    ct_width_req=q.pkqt_width_req,
                    ct_height_req=q.pkqt_height_req,
                    ct_length_req=q.pkqt_length_req,
                    ct_quantity_req=po_item.pod_quantity,  # IMPORTANT: Use quantity from PO line
                    ct_sqrt_req=q.pkqt_sqrt_req,
                    ct_stock_status=stock_status_instance,
                    ct_customer_name=q.pkqt_customer_name,
                    ct_customer_new_name=q.pkqt_customer_new_name2,
                    ct_customer_po=po,
                    ct_updated_by=request.user,
                    ct_na_quantity=q.pkqt_na_quantity,
                    ct_totalbox_cost=q.pkqt_totalbox_cost,
                    ct_part_code=q.pkqt_part_code,
                    ct_total_cft_display=q.pkqt_total_cft_display,
                    ct_po_dimension=po_item,  # NEW: Link to the specific PO line
                )
                cloned_count += 1

    # Ensure Costing Summary exists for this PO
    try:
        wip_status = StatusList.objects.get(id=6)
    except StatusList.DoesNotExist:
        wip_status = None

    summary, created = PkcostingsummaryInfo.objects.get_or_create(
        cs_customer_po=po,
        defaults={
            'cs_assessment_num': po_items.first().pod_assess_num if po_items.exists() else po.po_assessment_num,
            'cs_customer_name': po.po_customer_name,
            'cs_status': wip_status,
        }
    )

    if cloned_count > 0:
        messages.success(request, f'Successfully cloned {cloned_count} items to Costing.')
    else:
        messages.info(request, 'No new items found to clone for this PO (Already synced or missing quotations).')
    
    # Redirect to the Costing Summary update page
    if summary:
        return redirect('/SMS/costingsummary_update/' + str(summary.id))
    
    return redirect('costing_list')