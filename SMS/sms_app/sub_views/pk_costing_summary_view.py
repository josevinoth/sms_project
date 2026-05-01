from datetime import datetime
import openpyxl
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from xhtml2pdf import pisa
from ..forms import PkcostingsummaryForm
from ..models import User_extInfo,PkpurchaseorderInfo,POdimension,PkcostingsummaryInfo,PkneedassessmentInfo,PkcostingInfo,CustomerInfo
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models.aggregates import Sum
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum
from ..sub_models.na_dimension_mod import Nadimension
from ..views import Pkcosting_delete,Pkcostingsummary_delete,get_tracker_flags

@login_required(login_url='login_page')
def costingsummary_add(request,costingsummary_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = User_extInfo.objects.get(user=user_id).emp_role.id
    if request.method == "GET":
        if costingsummary_id == 0:
            print('Inside costing summary Get add')
            form = PkcostingsummaryForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'role': role,
                'role_id': role_id,
            }
        else:
            print('Inside costing summary Get edit')
            costingsummary=PkcostingsummaryInfo.objects.get(pk=costingsummary_id)
            needassessment_num = PkcostingsummaryInfo.objects.get(pk=costingsummary_id).cs_assessment_num
            needassessment_id = PkneedassessmentInfo.objects.get(na_assessment_num=needassessment_num).id
            customer_name_id = PkcostingsummaryInfo.objects.get(pk=costingsummary_id).cs_customer_name.id
            customer_po_id = PkcostingsummaryInfo.objects.get(pk=costingsummary_id).cs_customer_po.id
            request.session['na_assessment_id'] = needassessment_id
            request.session['na_customer_name_id'] = customer_name_id
            request.session['ses_customer_po_id'] = customer_po_id
            request.session['ses_costing_summary_id'] = costingsummary_id
            form = PkcostingsummaryForm(instance=costingsummary)
            # Filtering Logic: prioritize Job Number if available
            job_no = costingsummary.cs_job_no
            
            if job_no:
                # Job-based summary (Group multiple NAs by Job No)
                costing_list = PkcostingInfo.objects.filter(ct_job_no=job_no, ct_customer_po=customer_po_id)
                base_filter = {'ct_job_no': job_no, 'ct_customer_po': customer_po_id}
            else:
                # Legacy / Manual summary (Single NA)
                costing_list = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id, ct_customer_po=customer_po_id)
                base_filter = {'ct_assessment_num': needassessment_id, 'ct_customer_po': customer_po_id}

            Invoice = PkcostingInfo.objects.filter(**base_filter).values_list('ct_stock_status', flat=True)
            if all(status in [4] for status in Invoice) and len(Invoice) > 0:
                output = 1
            else:
                output = 0

            # Combined Wood Cost
            wood_cost = PkcostingInfo.objects.filter(ct_stock_type__in=[1, 4], ct_cost_type=8, **base_filter).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            if wood_cost is not None:
                wood_cost = round(wood_cost, 2)
            else:
                wood_cost = 0.0
            PkcostingsummaryInfo.objects.filter(pk=costingsummary_id).update(cs_wood_cost=wood_cost)

            # Combined Total CFT
            total_cft = PkcostingInfo.objects.filter(ct_cost_type=8, ct_stock_type=1, **base_filter).aggregate(Sum('ct_sqrt_req'))['ct_sqrt_req__sum']
            if total_cft is not None:
                total_cft = round(total_cft, 2)
            else:
                total_cft = 0.0
            PkcostingsummaryInfo.objects.filter(pk=costingsummary_id).update(cs_total_cft=total_cft)

            # Combined Engineer Cost
            engineer_cost = PkcostingInfo.objects.filter(ct_cost_type=2, **base_filter).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            if engineer_cost is not None:
                engineer_cost = round(engineer_cost, 2)
            else:
                engineer_cost = 0.0
            PkcostingsummaryInfo.objects.filter(pk=costingsummary_id).update(cs_engineer_cost=engineer_cost)

            # Combined Packing/Labour Cost
            packing_labour_cost = PkcostingInfo.objects.filter(ct_cost_type=3, **base_filter).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            if packing_labour_cost is not None:
                packing_labour_cost = round(packing_labour_cost, 2)
            else:
                packing_labour_cost = 0.0
            labour_cost = packing_labour_cost
            PkcostingsummaryInfo.objects.filter(pk=costingsummary_id).update(cs_labour_cost=labour_cost)

            # Combined Crane Cost
            crane_cost = PkcostingInfo.objects.filter(ct_cost_type=6, **base_filter).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            if crane_cost is not None:
                crane_cost = round(crane_cost, 2)
            else:
                crane_cost = 0.0
            PkcostingsummaryInfo.objects.filter(pk=costingsummary_id).update(cs_crane_cost=crane_cost)

            # Combined HT Cost
            ht_cost = PkcostingInfo.objects.filter(ct_cost_type=5, **base_filter).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            if ht_cost is not None:
                ht_cost = round(ht_cost, 2)
            else:
                ht_cost = 0.0
            PkcostingsummaryInfo.objects.filter(pk=costingsummary_id).update(cs_ht_cost=ht_cost)

            # Combined Management Cost
            management_cost = PkcostingInfo.objects.filter(ct_cost_type=7, **base_filter).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            if management_cost is not None:
                management_cost = round(management_cost, 2)
            else:
                management_cost = 0.0
            PkcostingsummaryInfo.objects.filter(pk=costingsummary_id).update(cs_management_cost=management_cost)

            # Combined Material Cost (Consumables)
            material_cost = PkcostingInfo.objects.filter(ct_cost_type=8, ct_stock_type=2, **base_filter).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            if material_cost is not None:
                material_cost = round(material_cost, 2)
            else:
                material_cost = 0.0
            PkcostingsummaryInfo.objects.filter(pk=costingsummary_id).update(cs_material_cost=material_cost)

            # Combined Transport Cost
            transport_cost = PkcostingInfo.objects.filter(ct_cost_type=4, **base_filter).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            if transport_cost is not None:
                transport_cost = round(transport_cost, 2)
            else:
                transport_cost = 0.0
            PkcostingsummaryInfo.objects.filter(pk=costingsummary_id).update(cs_transport_cost=transport_cost)
            context={
                    'form': form,
                    'first_name': first_name,
                    'user_id': user_id,
                    'costing_list': costing_list,
                    'wood_cost': wood_cost,
                    'engineer_cost': engineer_cost,
                    'labour_cost': labour_cost,
                    'crane_cost': crane_cost,
                    'ht_cost': ht_cost,
                    'management_cost': management_cost,
                    'material_cost': material_cost,
                    'transport_cost': transport_cost,
                    'role_id': role_id,
                    'output': output,
                    'current_step': 'costing',
                    'retrival_list': costing_list.filter(ct_cost_type=8, ct_stock_status__in=[1, 3]),
                    'acceptance_list': costing_list.filter(ct_cost_type=8, ct_stock_status=2),
                    'tracker_flags': get_tracker_flags(needassessment_id),
                    }
        return render(request, "asset_mgt_app/pk_costingsummary_add.html", context)
    else:
        print('costingsummary_id',costingsummary_id)
        if costingsummary_id == 0:
            print("Inside pk_costing_summary post add")
            form = PkcostingsummaryForm(request.POST)
            if form.is_valid():
                form.save()
                print("PkcostingsummaryInfo Form is Valid")
                last_id = (PkcostingsummaryInfo.objects.latest('id')).id
                messages.success(request, 'Record Updated Successfully')
                return redirect('/SMS/costingsummary_update/' + str(last_id))
            else:
                print("PkcostingsummaryInfo Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("Inside pk_costing_summary post edit")
            costingsummary = PkcostingsummaryInfo.objects.get(pk=costingsummary_id)
            form = PkcostingsummaryForm(request.POST,instance=costingsummary)
            if form.is_valid():
                form.save()
                print("PkcostingsummaryForm Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("PkcostingsummaryForm Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/costingsummary_list')

@login_required(login_url='login_page')
def costingsummary_list(request):
    first_name = request.session.get('first_name')
    summaries = PkcostingsummaryInfo.objects.all().order_by('-id')
    
    combined_list = []
    for s in summaries:
        # Fetch any one item from PkcostingInfo to show status and excess status
        # Match by assessment and customer PO
        costing_item = PkcostingInfo.objects.filter(
            ct_assessment_num=s.cs_assessment_num,
            ct_customer_po=s.cs_customer_po
        ).first()
        combined_list.append((s, costing_item))

    context = {
        'combined_list': combined_list,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/pk_costingsummary_list.html", context)


#Delete costingsummary
@login_required(login_url='login_page')
def costingsummary_delete(request, costingsummary_id):
    costingsummary = get_object_or_404(PkcostingsummaryInfo, pk=costingsummary_id)
    assessment_num = costingsummary.cs_assessment_num
    job_no = costingsummary.cs_job_no

    # Deleting PkcostingInfo objects (Job-aware)
    Pkcosting_delete(assessment_num, job_no=job_no)

    # Deleting Pkcosting summary objects (Job-aware)
    Pkcostingsummary_delete(assessment_num, job_no=job_no)

    return redirect('/SMS/costingsummary_list')

@login_required(login_url='login_page')
def pk_costing_get_customer(request):
    cs_assessment_num = request.GET.get('cs_assessment_num')
    cs_id = request.GET.get('cs_id')  # Might be passed
    
    customer_name_id = PkneedassessmentInfo.objects.get(id=cs_assessment_num).na_customer_name.id
    customer_po_qs = PkpurchaseorderInfo.objects.filter(po_assessment_num=cs_assessment_num)
    
    customer_po_name = list(customer_po_qs.values_list('po_num', flat=True))
    customer_po_id = list(customer_po_qs.values_list('id', flat=True))
    
    # Check if there is an existing PO for this costing summary that should be included
    if cs_id and cs_id != 'None':
        try:
            summary = PkcostingsummaryInfo.objects.get(id=cs_id)
            if summary.cs_customer_po and summary.cs_customer_po.id not in customer_po_id:
                customer_po_id.append(summary.cs_customer_po.id)
                customer_po_name.append(summary.cs_customer_po.po_num)
        except PkcostingsummaryInfo.DoesNotExist:
            pass

    customer = CustomerInfo.objects.get(id=customer_name_id)
    job_no_qs = PkcostingsummaryInfo.objects.filter(cs_assessment_num=cs_assessment_num).values_list('cs_job_no', flat=True).distinct()
    job_no_list = list(job_no_qs)

    return JsonResponse(
        {
            'customer_name_id':customer_name_id,
            'customer_po_id':customer_po_id,
            'customer_po_name':customer_po_name,
            'customer_address': customer.cu_address,
            'customer_gstin': customer.cu_gst,
            'job_no_list': job_no_list,
        }
    )

@login_required(login_url='login_page')
def pk_costing_summary_check_unique_field(request):
    cs_assessment_num = request.GET.get('cs_assessment_num')
    cs_po_num = request.GET.get('cs_customer_po_num')
    exists = PkcostingsummaryInfo.objects.filter(cs_assessment_num=cs_assessment_num,cs_customer_po=cs_po_num).exists()
    return JsonResponse(
        {
            'exists': exists,
        }
    )

@login_required(login_url='login_page')
def pk_bvm_invoice_pdf(request, invoice_id=0):
    if invoice_id == 0:
        costing_summary_id = request.session.get('ses_costing_summary_id')
    else:
        costing_summary_id = invoice_id
    
    summary = get_object_or_404(PkcostingsummaryInfo, pk=costing_summary_id)
    job_no = summary.cs_job_no
    cs_po_num = summary.cs_customer_po
    
    # Get base filter
    if job_no:
        base_filter = {'ct_job_no': job_no, 'ct_customer_po': cs_po_num}
    else:
        base_filter = {'ct_assessment_num': summary.cs_assessment_num, 'ct_customer_po': cs_po_num}

    invoices = PkcostingInfo.objects.filter(**base_filter)
    
    # Requirements (Items in this job)
    na_req = invoices.values('ct_requirement').distinct()
    margin = summary.cs_margin
    totalbox_cost = 0

    # Calculate and store for this job specifically
    for req in na_req:
        k = req['ct_requirement']
        if not k: continue
        
        # Aggregate base costs for this specific requirement WITHIN THIS JOB
        total_cost_wom = PkcostingInfo.objects.filter(ct_requirement=k, **base_filter).aggregate(total_cost=Sum('ct_total_cost'))['total_cost'] or 0
        total_cost_with_margin = total_cost_wom + (total_cost_wom * margin / 100)
        
        # Get one representative line to find na_quantity for this item
        rep_line = PkcostingInfo.objects.filter(ct_requirement=k, **base_filter).first()
        qty = rep_line.ct_na_quantity if rep_line else 1
        
        # Update lines only for this specific job to prevent affecting other jobs
        PkcostingInfo.objects.filter(ct_requirement=k, **base_filter).update(
            ct_total_cost=round(total_cost_with_margin, 2),
            ct_totalbox_cost=round(total_cost_with_margin * qty, 2)
        )
        
        totalbox_cost += (total_cost_with_margin * qty)

    gst_val = summary.cs_gst
    gst = round(totalbox_cost * gst_val / 100, 2)
    final_cost = round((totalbox_cost + gst), 2)
    
    today = datetime.now()
    formatted_date = today.strftime("%d-%b-%Y")
    
    context = {
        'address': summary.cs_address,
        'cost_includes': summary.cs_cost_includes,
        'notes': summary.cs_notes,
        'terms_condition': summary.cs_terms_condition,
        'client_scope': summary.cs_client_scope,
        'bvm_scope': summary.cs_bvm_scope,
        'invoices': invoices,
        'total_sum': round(totalbox_cost, 2),
        'gst_val': gst_val,
        'gst': gst,
        'final_cost': final_cost,
        'po_number': cs_po_num,
        'today_date': formatted_date,
    }
    
    file_name = f"Invoice_{summary.cs_job_no or summary.cs_assessment_num}_{cs_po_num}.pdf"
    template_path = 'asset_mgt_app/bvm_pk_invoice_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'

    template = get_template(template_path)
    html = template.render(context)

    # Create PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We has some error <pre>' + html + '</pre>')
    return response

def pk_bvm_invoice_excel(request, invoice_id=0):
    if invoice_id == 0:
        costing_summary_id = request.session.get('ses_costing_summary_id')
    else:
        costing_summary_id = invoice_id
        
    summary = get_object_or_404(PkcostingsummaryInfo, pk=costing_summary_id)
    job_no = summary.cs_job_no
    cs_po_num = summary.cs_customer_po
    
    if job_no:
        base_filter = {'ct_job_no': job_no, 'ct_customer_po': cs_po_num}
        # For Excel, we also show the PO Dimensions specifically assigned to this job
        job_dimensions = POdimension.objects.filter(ct_po_id=cs_po_num.id) # This might need a link or we filter by pod_po_num
        pod_ids = PkcostingInfo.objects.filter(**base_filter).values_list('ct_po_dimension_id', flat=True).distinct()
        invoices = POdimension.objects.filter(id__in=pod_ids)
    else:
        invoices = POdimension.objects.filter(pod_assess_num=summary.cs_assessment_num, pod_po_num=cs_po_num)

    margin = summary.cs_margin
    totalbox_cost = 0

    # Sync and sum costs
    for i in invoices:
        k = i.id
        total_cost_wom = PkcostingInfo.objects.filter(ct_po_dimension=i, **base_filter).aggregate(total_cost=Sum('ct_total_cost'))['total_cost'] or 0
        total_cost_with_margin = total_cost_wom + (total_cost_wom * margin / 100)
        
        # Update dimension record for display
        POdimension.objects.filter(pk=k).update(
            pod_cost_unit=round(total_cost_with_margin, 2),
            pod_cost_total=round(total_cost_with_margin * i.pod_quantity, 2)
        )
        totalbox_cost += (total_cost_with_margin * i.pod_quantity)

    gst_val = summary.cs_gst
    gst = round(totalbox_cost * gst_val / 100, 2)
    final_cost = round((totalbox_cost + gst), 2)
    today = datetime.now().strftime("%d-%b-%Y")

    # Create an Excel workbook and add a worksheet.
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Invoice"

    # Write the header
    ws.append([
        "Address", "Cost Includes", "Notes", "Terms & Conditions",
        "Client Scope", "BVM Scope", "PO Number", "Total Sum",
        "GST Value", "GST", "Final Cost", "Date"
    ])
    # Write the summary info
    ws.append([
        summary.cs_address, summary.cs_cost_includes, summary.cs_notes, summary.cs_terms_condition,
        summary.cs_client_scope, summary.cs_bvm_scope, summary.cs_customer_po.po_num if summary.cs_customer_po else '', 
        round(totalbox_cost, 2),
        gst_val, gst, final_cost, today
    ])

    # Write the invoice items header
    ws.append([
        "Item", "Type of Requirement", "Length", "Width",
        "Height", "Quantity", "Total Cost", "Unit Cost"
    ])
    # Write the invoice items
    for invoice in invoices:
        ws.append([
            invoice.pod_item, invoice.pod_type_of_req, invoice.pod_length, invoice.pod_width,
            invoice.pod_height, invoice.pod_quantity, invoice.pod_cost_total, invoice.pod_cost_unit
        ])

    # Create an HttpResponse with the appropriate Excel content type
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file_name = f"Invoice_{needassessment_num}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    # Save the workbook to the response
    wb.save(response)
    return response

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
    na_uom_id=str(a.nad_uom.id)
    na_length=str(a.nad_length)
    na_width=str(a.nad_width)
    na_height = str(a.nad_height)


    data = {
        'na_dimension_box_val': na_dimension_box_val,
        'na_dimension_type': na_dimension_type,
        'na_dimension_type_id': na_dimension_type_id,
        'na_uom': na_uom,
        'na_uom_id': na_uom_id,
        'na_length': na_length,
        'na_width': na_width,
        'na_height': na_height,
    }
    return JsonResponse(data)


@login_required(login_url='login_page')
def export_cost_assessment_to_excel(request):
    costing_summary_id = request.session.get('ses_costing_summary_id')
    summary = get_object_or_404(PkcostingsummaryInfo, pk=costing_summary_id)
    job_no = summary.cs_job_no
    customer_po_id = summary.cs_customer_po.id

    if job_no:
        costing_list = PkcostingInfo.objects.filter(ct_job_no=job_no, ct_customer_po=customer_po_id, ct_cost_type=8)
    else:
        assessment_number = request.session.get('na_assessment_id')
        costing_list = PkcostingInfo.objects.filter(ct_assessment_num=assessment_number, ct_customer_po=customer_po_id, ct_cost_type=8)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Cost Assessment Report"

    # Define headers for the columns in the report
    headers = [
        'ID', 'Created On', 'Stock Purchase Number', 'Assessment Number', 'Customer Name',
        'Customer PO', 'Job Type', 'Cost Type', 'Stock Type', 'Stock Description',
        'Width (in)', 'Height (in)', 'Length (ft)', 'Job Type Quantity', 'Size', 'UOM',
        'Total CFT', 'Rate/QTY (CFT)', 'Days', 'Unit Cost',
        'Total Cost', 'Stock Status', 'Updated at', 'Updated By'
    ]
    ws.append(headers)

    # Populate the worksheet with data from the filtered queryset
    for costinginfo in costing_list:
        ws.append([
            costinginfo.id,
            costinginfo.ct_created_at.strftime('%Y-%m-%d') if costinginfo.ct_created_at else '',
            str(costinginfo.ct_stock_purchase_number) if costinginfo.ct_stock_purchase_number else '',
            str(costinginfo.ct_assessment_num) if costinginfo.ct_customer_name else '',
            str(costinginfo.ct_customer_name) if costinginfo.ct_customer_name else '',
            str(costinginfo.ct_customer_po) if costinginfo.ct_customer_po else '',
            str(costinginfo.ct_requirement) if costinginfo.ct_requirement else '',
            str(costinginfo.ct_cost_type) if costinginfo.ct_cost_type else '',
            str(costinginfo.ct_stock_type) if costinginfo.ct_stock_type else '',
            str(costinginfo.ct_stock_description) if costinginfo.ct_stock_description else '',
            costinginfo.ct_width_req,
            costinginfo.ct_height_req,
            costinginfo.ct_length_req,
            costinginfo.ct_quantity,
            costinginfo.ct_size,
            str(costinginfo.ct_uom) if costinginfo.ct_uom else '',
            costinginfo.ct_sqrt_req,
            costinginfo.ct_rate,
            costinginfo.ct_days,
            costinginfo.ct_total_cost,
            costinginfo.ct_totalbox_cost,
            str(costinginfo.ct_stock_status) if costinginfo.ct_stock_status else '',
            costinginfo.ct_updated_at.strftime('%Y-%m-%d') if costinginfo.ct_updated_at else '',
            str(costinginfo.ct_updated_by) if costinginfo.ct_updated_by else ''
        ])

    # Set up the response for file download with appropriate headers
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Cost_Assessment_Report_{}.xlsx'.format(
        datetime.now().strftime('%Y%m%d_%H%M%S')
    )

    # Save the workbook directly to the response object
    wb.save(response)

    return response

@login_required(login_url='login_page')
def get_partcode_summary(request):
    part_code_id = request.GET.get('part_code_id')
    if not part_code_id:
        return JsonResponse({'error': 'Missing part_code_id'}, status=400)
    
    # Get total purchased (Stock IN)
    purchases = PkstockpurchasesInfo.objects.filter(sp_part_code_id=part_code_id)
    total_in = purchases.aggregate(Sum('sp_cft'))['sp_cft__sum'] or 0.0
    
    # Get total retrieved across all assessments - status > 1 means retrieved
    retrievals = PkcostingInfo.objects.filter(
        ct_part_code_id=part_code_id, 
        ct_cost_type=8, 
        ct_stock_status__in=[2, 4]
    )
    total_retrieved = retrievals.aggregate(Sum('ct_cft'))['ct_cft__sum'] or 0.0
    
    # Get returns (status 3)
    returns = PkcostingInfo.objects.filter(
        ct_part_code_id=part_code_id, 
        ct_cost_type=8, 
        ct_stock_status=3
    )
    total_returned = returns.aggregate(Sum('ct_cft'))['ct_cft__sum'] or 0.0
    
    # Calculate available
    current_available = total_in - total_retrieved + total_returned

    # Build assessment breakdown
    assessment_breakdown = []
    for r in retrievals.order_by('-ct_updated_at'):
        assessment_breakdown.append({
            'assessment_num': r.ct_assessment_num,
            'qty_cft': round(r.ct_cft, 2),
            'date': r.ct_updated_at.strftime('%Y-%m-%d %H:%M') if r.ct_updated_at else ''
        })

    data = {
        'total_in': round(total_in, 2),
        'total_retrieved': round(total_retrieved, 2),
        'total_returned': round(total_returned, 2),
        'current_available': round(current_available, 2),
        'breakdown': assessment_breakdown
    }
    return JsonResponse(data)