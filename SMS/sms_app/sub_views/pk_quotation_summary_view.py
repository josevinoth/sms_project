from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from xhtml2pdf import pisa

from ..views import Pkcosting_delete,Pkcostingsummary_delete,Pkpurchaseorder_delete,Pkpurchaseorder_dim_delete,Pkquotation_delete,Pkquotation_summary_delete
from ..forms import PkcostingsummaryForm,PkquotationsummaryForm
from ..models import pk_stock_statusinfo,PkcostingInfo,User_extInfo,Nadimension,PkquotationsummaryInfo,PkneedassessmentInfo,PkquotationInfo,PkcostingsummaryInfo
from django.shortcuts import render, redirect
from django.db.models.aggregates import Sum
from django.contrib import messages
from django.http import JsonResponse, HttpResponse


@login_required(login_url='login_page')
def pk_quotationsummary_add(request, pk_quotationsummary_id=0):
    global financial_year, last_id
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = User_extInfo.objects.get(user=user_id).emp_role.id

    if request.method == "GET":
        if pk_quotationsummary_id == 0:
            form = PkquotationsummaryForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'role': role,
                'role_id': role_id,
            }
        else:
            quotationsummary = PkquotationsummaryInfo.objects.get(pk=pk_quotationsummary_id)
            needassessment_num = quotationsummary.qs_assessment_num
            needassessment_id = PkneedassessmentInfo.objects.get(na_assessment_num=needassessment_num).id
            customer_name_id = quotationsummary.qs_customer_name_2.id
            request.session['na_assessment_id'] = needassessment_id
            request.session['na_customer_name_id'] = customer_name_id
            form = PkquotationsummaryForm(instance=quotationsummary)
            quotation_list = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id)

            # Aggregate costs
            def get_aggregate_cost(assessment_id, cost_type, stock_types=None):
                filter_kwargs = {'pkqt_assessment_num': assessment_id, 'pkqt_cost_type': cost_type}
                if stock_types:
                    filter_kwargs['pkqt_stock_type__in'] = stock_types
                cost = PkquotationInfo.objects.filter(**filter_kwargs).aggregate(Sum('pkqt_total_cost'))[
                    'pkqt_total_cost__sum']
                return round(cost, 2) if cost is not None else 0.0

            wood_cost = get_aggregate_cost(needassessment_id, 8, [1, 4])
            total_cft = get_aggregate_cost(needassessment_id, 8, [1])
            engineer_cost = get_aggregate_cost(needassessment_id, 2)
            packing_labour_cost = get_aggregate_cost(needassessment_id, 3)
            labour_cost = packing_labour_cost
            crane_cost = get_aggregate_cost(needassessment_id, 6)
            ht_cost = get_aggregate_cost(needassessment_id, 5)
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
            }

        return render(request, "asset_mgt_app/pk_quotationsummary_add.html", context)

    else:
        if pk_quotationsummary_id == 0:
            form = PkquotationsummaryForm(request.POST)
        else:
            quotationsummary = PkquotationsummaryInfo.objects.get(pk=pk_quotationsummary_id)
            form = PkquotationsummaryForm(request.POST, instance=quotationsummary)

        if form.is_valid():
            print("Requirement Form is Valid")
            quotation_num = form.cleaned_data['qs_quotation_number']
            if not PkquotationsummaryInfo.objects.filter(qs_quotation_number=quotation_num).exclude(id=pk_quotationsummary_id).exists():
                form.save()
                if pk_quotationsummary_id==0:
                    try:
                        last_id = (PkquotationsummaryInfo.objects.values_list('id', flat=True)).last()
                        quotation_number=100000+last_id
                        date_to_check = datetime.now()
                        current_year = date_to_check.year
                        end_of_march = datetime(current_year, 3, 31)
                        if date_to_check <= end_of_march:
                            financial_year = f"{current_year - 1}-{str(current_year)[-2:]}"
                        else:
                            financial_year = f"{current_year}-{str(current_year + 1)[-2:]}"
                        # req_num_next = str('Req_') + str(int(((RequirementsInfo.objects.get(id=last_id)).req_number).replace('Req_', '')) + 1)
                    except ObjectDoesNotExist:
                        quotation_number=100000
                    quotation_number = f'{quotation_number:03}'
                    quotation_num_next = f'BVM/PKG/{financial_year}/{quotation_number}'
                    PkquotationsummaryInfo.objects.filter(id=last_id).update(qs_quotation_number=quotation_num_next)
                    messages.success(request, 'Record Updated Successfully')
                # if pk_quotationsummary_id == 0:
                    last_id = PkquotationsummaryInfo.objects.latest('id').id
                    return redirect('/SMS/pk_quotationsummary_update/' + str(last_id))
                else:
                    form.save()
                    messages.success(request, 'Record Updated Successfully')
                    return redirect(request.META['HTTP_REFERER'])
            else:
                messages.error(request, 'Please enter a Unique Quotation Number.')
        else:
            messages.error(request, 'Record NOT Updated Successfully')
        return redirect(request.META['HTTP_REFERER'])
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
    customer_name_id=PkneedassessmentInfo.objects.get(id=qs_assessment_num).na_customer_name.id
    exists = PkquotationsummaryInfo.objects.filter(qs_assessment_num=qs_assessment_num).exists()
    return JsonResponse(
        {
            'exists': exists,
            'customer_name_id':customer_name_id,
        }
    )

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
    total_sum=0
    for i in na_req:
        j=i.nad_item
        k=i.id
        qty=i.nad_quantity
        total_cost_wom=PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id,pkqt_requirement=i).aggregate(total_cost=Sum('pkqt_total_cost'))['total_cost'] or 0
        total_cost=total_cost_wom+(total_cost_wom*margin/100)
        Nadimension.objects.filter(pk=k).update(nad_cost_total=round(total_cost,2))
        try:
            Nadimension.objects.filter(pk=k).update(nad_cost_unit=round(total_cost/qty,2))
        except:
            Nadimension.objects.filter(pk=k).update(nad_cost_unit=0)
        total_sum=round((total_sum+total_cost),2)
    gst=round(total_sum*gst_val/100,2)
    final_cost=round((total_sum+gst),2)
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
        'total_sum': total_sum,
        'gst': gst,
        'gst_val': gst_val,
        'final_cost': final_cost,
        'quotation_number': quotation_number,
        'today_date': formatted_date,
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
        # Prefill the form with values from the quotation summary
        form = PkcostingsummaryForm(initial={
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
        form = PkcostingsummaryForm(request.POST)
        costing_summary_id = None  # Initialize costing_summary_id
        if form.is_valid():
            pkqt_customer_po = form.cleaned_data['cs_customer_po']
            # Check for an existing costing summary with the same assessment number
            existing_summary = PkcostingsummaryInfo.objects.filter(cs_assessment_num=quotationsummary.qs_assessment_num,cs_customer_po=pkqt_customer_po).exists()

            if existing_summary:
                messages.error(request, 'A costing summary with the same assessment number already exists.')
            else:
                # Create a new costing summary and copy all the necessary values from quotation
                costing_summary = form.save(commit=False)
                costing_summary.cs_updated_by = request.user  # Set the current user as the one updating
                costing_summary.save()
                messages.success(request, 'Costing summary cloned and saved successfully.')
                costing_summary_id = costing_summary.id


                # Fetch the quotation data using cs_assessment_num and cs_customer_po
                quotations = PkquotationInfo.objects.filter(
                    pkqt_assessment_num=quotationsummary.qs_assessment_num,
                )
                stock_status_instance = pk_stock_statusinfo.objects.get(id=1)
                if quotations.exists():
                    for quotation in quotations:
                        # Fetch quotation data and directly save it to costing summary
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
                            ct_stock_status=stock_status_instance,
                            ct_customer_name=quotation.pkqt_customer_name,
                            ct_customer_po=pkqt_customer_po,
                            ct_updated_by=request.user,
                        )
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


