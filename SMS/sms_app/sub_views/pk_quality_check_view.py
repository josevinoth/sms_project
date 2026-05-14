from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from ..models import PkcostingsummaryInfo, PkcostingInfo, PkQualityCheck, PkQualityCheckItem, Packingjobs, PkneedassessmentInfo, MyUser
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

@login_required(login_url='login_page')
def pk_quality_check_list(request):
    qc_list = PkQualityCheck.objects.all().order_by('-id')
    return render(request, 'asset_mgt_app/pk_quality_check_list.html', {'qc_list': qc_list})

@login_required(login_url='login_page')
def pk_quality_check_add(request):
    first_name = request.session.get('first_name')
    assessment_id = request.session.get('na_assessment_id')
    
    if request.method == 'POST':
        job_no = request.POST.get('qc_job_no')
        status = request.POST.get('qc_status')
        remarks = request.POST.get('qc_remarks')
        
        with transaction.atomic():
            # Get costing summary
            costing_summary = PkcostingsummaryInfo.objects.filter(cs_job_no=job_no).first()
            if not costing_summary:
                return redirect('pk_quality_check_list')
            
            # Create or update Master
            qc_master, created = PkQualityCheck.objects.update_or_create(
                qc_job_no=job_no,
                defaults={
                    'qc_costing_summary': costing_summary,
                    'qc_status': status,
                    'qc_remarks': remarks,
                    'qc_wood_twist': request.POST.get('qc_wood_twist') == 'on',
                    'qc_seal': request.POST.get('qc_seal') == 'on',
                    'qc_cracks': request.POST.get('qc_cracks') == 'on',
                    'qc_pasting': request.POST.get('qc_pasting') == 'on',
                    'qc_conducted_by': request.user
                }
            )
            
            # Delete existing items to recreate
            PkQualityCheckItem.objects.filter(qc_master=qc_master).delete()
            
            # Save Item details based on submitted form data
            import re
            for key in request.POST.keys():
                match = re.match(r'accepted_qty_(\d+)', key)
                if match:
                    item_id = match.group(1)
                    costing_item = PkcostingInfo.objects.filter(id=item_id).first()
                    if costing_item:
                        qc_item = PkQualityCheckItem(
                            qc_master=qc_master,
                            qc_costing_item=costing_item,
                            qc_accepted_qty=float(request.POST.get(f'accepted_qty_{item_id}') or 0),
                            qc_rejected_qty=float(request.POST.get(f'rejected_qty_{item_id}') or 0),
                            check_type_of_work=request.POST.get(f'check_type_{item_id}') == 'on',
                            check_scope_of_work=request.POST.get(f'check_scope_{item_id}') == 'on',
                            check_wood_treatment=request.POST.get(f'check_treatment_{item_id}') == 'on',
                            check_wood_norms=request.POST.get(f'check_norms_{item_id}') == 'on',
                            check_lifting=request.POST.get(f'check_lifting_{item_id}') == 'on',
                            check_req_type=request.POST.get(f'check_req_{item_id}') == 'on',
                            check_wood_type=request.POST.get(f'check_wood_type_{item_id}') == 'on',
                            check_wood_description=request.POST.get(f'check_wood_desc_{item_id}') == 'on',
                        )
                        qc_item.save()
            
            # Update Packingjobs flag
            if status == 'Passed':
                Packingjobs.objects.filter(pj_job_no=job_no).update(pj_qc_completed_flag='Completed')
            else:
                Packingjobs.objects.filter(pj_job_no=job_no).update(pj_qc_completed_flag='Pending')

        return redirect('pk_quality_check_list')

    # GET: Prepare data for the form
    selected_job_no = request.GET.get('job_no', '')
    # Filter jobs that are Production Completed
    completed_jobs = Packingjobs.objects.filter(pj_production_completed_flag='Completed').values_list('pj_job_no', flat=True)
    costing_jobs = PkcostingsummaryInfo.objects.filter(cs_job_no__in=completed_jobs)
    
    # If a job_no was supplied in querystring, prepare server-side data to pre-fill the form
    server_items = []
    server_na_details = None
    server_customer = ''
    server_po = None
    server_po_date = ''
    if selected_job_no:
        try:
            summary = PkcostingsummaryInfo.objects.filter(cs_job_no__iexact=selected_job_no).first()
            print('DEBUG pk_quality_check_add prefill: selected_job_no=', selected_job_no, ' summary_found=', bool(summary))
            if summary:
                na = summary.cs_assessment_num
                po = summary.cs_customer_po
                server_customer = summary.cs_customer_name.cu_name if summary.cs_customer_name else (summary.cs_customer_new_name or '')
                server_po = po.po_num if po else ''
                server_po_date = po.po_date.strftime('%d-%m-%Y') if po and getattr(po, 'po_date', None) else ''

                # Build na_details (same as get_job_details_for_qc)
                na_details = {
                    'type_of_work': 'N/A', 'client_scope': 'N/A', 'wood_treatment': 'N/A',
                    'wood_norms': 'N/A', 'lifting': 'N/A', 'req_type': 'N/A', 'wood_type': 'N/A', 'wood_description': 'N/A'
                }
                if na:
                    na_details['type_of_work'] = getattr(na, 'na_type_of_work', getattr(na, 'type_of_work', 'N/A')) or 'N/A'
                    na_details['client_scope'] = getattr(na, 'na_scope_of_work', getattr(na, 'scope_of_work', 'N/A')) or 'N/A'
                    na_details['wood_treatment'] = getattr(na, 'na_wood_treatment', getattr(na, 'wood_treatment', 'N/A')) or 'N/A'
                    try:
                        norms_qs = getattr(na, 'na_wood_norms', None)
                        if norms_qs is not None and hasattr(norms_qs, 'all'):
                            na_details['wood_norms'] = ', '.join([str(x) for x in norms_qs.all()]) or 'N/A'
                    except Exception:
                        na_details['wood_norms'] = 'N/A'
                    na_details['lifting'] = getattr(na, 'na_lifting_specs', getattr(na, 'lifting_specs', 'N/A')) or 'N/A'
                    na_details['req_type'] = getattr(na, 'na_requirement_type', getattr(na, 'requirement_type', 'N/A')) or 'N/A'
                    na_details['wood_type'] = getattr(na, 'na_wood_type', getattr(na, 'wood_type', 'N/A')) or 'N/A'
                    na_details['wood_description'] = getattr(na, 'na_wood_description', getattr(na, 'wood_description', 'N/A')) or 'N/A'
                server_na_details = na_details

                # Build items list from costing items for this job
                costing_items = list(PkcostingInfo.objects.filter(ct_job_no__iexact=selected_job_no))
                if not costing_items:
                    costing_items = list(PkcostingInfo.objects.filter(ct_job_no__icontains=selected_job_no))
                from sms_app.sub_models.na_dimension_mod import Nadimension
                from sms_app.sub_models.pk_purchaseorder_mod import POdimension
                processed_boxes = set()
                for item in costing_items:
                    box_id = item.ct_requirement_id or item.ct_po_dimension_id
                    box_type = 'NA' if item.ct_requirement_id else 'PO'
                    if not box_id or (box_id, box_type) in processed_boxes:
                        continue
                    processed_boxes.add((box_id, box_type))
                    if box_type == 'NA':
                        box = Nadimension.objects.filter(id=box_id).first()
                        if box:
                            server_items.append({
                                'id': item.id,
                                'item_name': f"{box.nad_type_of_req} ({box.nad_item})",
                                'qty': box.nad_quantity,
                                'l': box.nad_length,
                                'w': box.nad_width,
                                'h': box.nad_height,
                                'thickness': box.nad_plywood_thickness or 'N/A',
                                'uom': str(box.nad_uom) if box.nad_uom else 'Nos'
                            })
                    else:
                        box = POdimension.objects.filter(id=box_id).first()
                        if box:
                            server_items.append({
                                'id': item.id,
                                'item_name': f"PO Item: {box.pod_item}",
                                'qty': box.pod_quantity,
                                'l': box.pod_length,
                                'w': box.pod_width,
                                'h': box.pod_height,
                                'thickness': box.pod_plywood_thickness or 'N/A',
                                'uom': str(box.pod_uom) if box.pod_uom else 'Nos'
                            })
        except Exception as e:
            print('DEBUG prefill error for job', selected_job_no, e)

    return render(request, 'asset_mgt_app/pk_quality_check_add.html', {
        'costing_jobs': costing_jobs,
        'selected_job_no': selected_job_no,
        'assessment_id': assessment_id,
        'current_stage': 7,
        'first_name': first_name,
        'items': server_items,
        'na_details': server_na_details,
        'customer_name': server_customer,
        'po_num': server_po,
        'po_date': server_po_date,
    })

@csrf_exempt
@login_required(login_url='login_page')
def get_job_details_for_qc(request):
    job_no = request.GET.get('job_no', '').strip()
    if not job_no:
        return JsonResponse({'status': 'error', 'message': 'Job No is missing'})
        
    try:
        print('DEBUG get_job_details_for_qc called for job_no:', job_no)
        # Try case-insensitive exact match first
        summary = PkcostingsummaryInfo.objects.filter(cs_job_no__iexact=job_no).first()
        # Fallback: try partial match if exact not found
        if not summary:
            summary = PkcostingsummaryInfo.objects.filter(cs_job_no__icontains=job_no).first()
        if not summary:
            return JsonResponse({'status': 'error', 'message': f'Job No {job_no} not found in costing records'})

        # Prefer Need Assessment (na) as the authoritative source for QC checklist fields
        na = summary.cs_assessment_num
        po = summary.cs_customer_po

        # default values
        na_details = {
            'type_of_work': 'N/A',
            'client_scope': 'N/A',
            'wood_treatment': 'N/A',
            'wood_norms': 'N/A',
            'lifting': 'N/A',
            'req_type': 'N/A',
            'wood_type': 'N/A',
            'wood_description': 'N/A',
        }

        if na:
            # Use defensive getattr and convert to string for JSON serialization
            na_details['type_of_work'] = str(getattr(na, 'na_type_of_work', getattr(na, 'type_of_work', 'N/A')) or 'N/A')
            na_details['client_scope'] = str(getattr(na, 'na_scope_of_work', getattr(na, 'scope_of_work', 'N/A')) or 'N/A')
            na_details['wood_treatment'] = str(getattr(na, 'na_wood_treatment', getattr(na, 'wood_treatment', 'N/A')) or 'N/A')
            # wood norms may be a ManyToMany; handle gracefully
            try:
                norms_qs = getattr(na, 'na_wood_norms', None)
                if norms_qs is not None and hasattr(norms_qs, 'all'):
                    na_details['wood_norms'] = ', '.join([str(x) for x in norms_qs.all()]) or 'N/A'
                else:
                    na_details['wood_norms'] = str(getattr(na, 'na_wood_norms', 'N/A') or 'N/A')
            except Exception:
                na_details['wood_norms'] = 'N/A'
            na_details['lifting'] = str(getattr(na, 'na_lifting_specs', getattr(na, 'lifting_specs', 'N/A')) or 'N/A')
            na_details['req_type'] = str(getattr(na, 'na_requirement_type', getattr(na, 'requirement_type', 'N/A')) or 'N/A')
            na_details['wood_type'] = str(getattr(na, 'na_wood_type', getattr(na, 'wood_type', 'N/A')) or 'N/A')
            na_details['wood_description'] = str(getattr(na, 'na_wood_description', getattr(na, 'wood_description', 'N/A')) or 'N/A')

        items_data = []
        costing_items = PkcostingInfo.objects.filter(ct_job_no=job_no)
        # Find costing items by job number. Try exact (case-insensitive) then fallback to partial match
        costing_items = list(PkcostingInfo.objects.filter(ct_job_no__iexact=job_no))
        if not costing_items:
            costing_items = list(PkcostingInfo.objects.filter(ct_job_no__icontains=job_no))
        print('DEBUG get_job_details_for_qc: found costing_items count=', len(costing_items))

        from sms_app.sub_models.na_dimension_mod import Nadimension
        from sms_app.sub_models.po_dimension_mod import POdimension
        processed_boxes = set()
        
        for item in costing_items:
            # A "Box" can be either an Nadimension or a POdimension
            box_id = item.ct_requirement_id or item.ct_po_dimension_id
            box_type = 'NA' if item.ct_requirement_id else 'PO'
            
            if not box_id or (box_id, box_type) in processed_boxes:
                continue
                
            processed_boxes.add((box_id, box_type))
            
            if box_type == 'NA':
                box = Nadimension.objects.filter(id=box_id).first()
                if box:
                    items_data.append({
                        'id': item.id,
                        'item_name': f"{box.nad_type_of_req} ({box.nad_item})",
                        'qty': box.nad_quantity,
                        'l': box.nad_length,
                        'w': box.nad_width,
                        'h': box.nad_height,
                        'thickness': box.nad_plywood_thickness or 'N/A',
                        'uom': str(box.nad_uom) if box.nad_uom else 'Nos'
                    })
            else:
                box = POdimension.objects.filter(id=box_id).first()
                if box:
                    items_data.append({
                        'id': item.id,
                        'item_name': f"PO Item: {box.pod_item}",
                        'qty': box.pod_quantity,
                        'l': box.pod_length,
                        'w': box.pod_width,
                        'h': box.pod_height,
                        'thickness': box.pod_plywood_thickness or 'N/A',
                        'uom': str(box.pod_uom) if box.pod_uom else 'Nos'
                    })
        
        # Check for existing QC data to allow "editing" or pre-filling
        existing_qc_data = None
        qc_master = PkQualityCheck.objects.filter(qc_job_no=job_no).first()
        if qc_master:
            existing_qc_data = {
                'status': qc_master.qc_status,
                'remarks': qc_master.qc_remarks,
                'wood_twist': qc_master.qc_wood_twist,
                'seal': qc_master.qc_seal,
                'cracks': qc_master.qc_cracks,
                'pasting': qc_master.qc_pasting,
                'items': {}
            }
            for q_item in PkQualityCheckItem.objects.filter(qc_master=qc_master):
                existing_qc_data['items'][q_item.qc_costing_item_id] = {
                    'acc': q_item.qc_accepted_qty,
                    'rej': q_item.qc_rejected_qty,
                    'c_type': q_item.check_type_of_work,
                    'c_scope': q_item.check_scope_of_work,
                    'c_treat': q_item.check_wood_treatment,
                    'c_norms': q_item.check_wood_norms,
                    'c_lift': q_item.check_lifting,
                    'c_req': q_item.check_req_type,
                    'c_wood': q_item.check_wood_type,
                    'c_desc': q_item.check_wood_description
                }
            
        data = {
            'status': 'success',
            'po_num': po.po_num if po else '',
            'po_id': po.id if po else '',
            'assessment_id': na.id if na else '',
            'assessment_num': getattr(na, 'na_assessment_num', '') if na else '',
            'customer_name': summary.cs_customer_name.cu_name if summary.cs_customer_name else summary.cs_customer_new_name or '',
            'na_details': na_details,
            'items': items_data,
            'existing_qc': existing_qc_data
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@login_required(login_url='login_page')
def pk_quality_check_pdf(request, qc_id):
    qc_master = get_object_or_404(PkQualityCheck, id=qc_id)
    qc_items = PkQualityCheckItem.objects.filter(qc_master=qc_master)
    
    summary = qc_master.qc_costing_summary
    po = summary.cs_customer_po
    na = summary.cs_assessment_num
    customer = summary.cs_customer_name.cu_name if summary.cs_customer_name else (summary.cs_customer_new_name or 'N/A')
    
    items_data = []
    for q_item in qc_items:
        # Resolve dimension information - prioritize PO Dimension
        costing_item = q_item.qc_costing_item
        po_dim = costing_item.ct_po_dimension if costing_item else None
        na_dim = costing_item.ct_requirement if costing_item else None
        
        # Use PO dim for quantities/dims if available, otherwise NA dim
        main_dim = po_dim if po_dim else na_dim
        
        # Map fields based on which dimension object we are using
        if po_dim:
            length = po_dim.pod_length
            width = po_dim.pod_width
            height = po_dim.pod_height
            qty = po_dim.pod_quantity
            item_code = po_dim.pod_item
            plywood = po_dim.pod_plywood_thickness
            uom = str(po_dim.pod_uom) if po_dim.pod_uom else 'Nos'
            wood_types = str(po_dim.pod_wood_type) if po_dim.pod_wood_type else 'N/A'
            wood_descs = str(po_dim.pod_wood_description) if po_dim.pod_wood_description else 'N/A'
        else:
            length = na_dim.nad_length if na_dim else 0
            width = na_dim.nad_width if na_dim else 0
            height = na_dim.nad_height if na_dim else 0
            qty = na_dim.nad_quantity if na_dim else 0
            item_code = na_dim.nad_item if na_dim else 'N/A'
            plywood = na_dim.nad_plywood_thickness if na_dim else 'N/A'
            uom = str(na_dim.nad_uom) if na_dim and na_dim.nad_uom else 'Nos'
            wood_types = ", ".join([str(w) for w in na_dim.nad_wood_type.all()]) if na_dim else 'N/A'
            wood_descs = ", ".join([str(w) for w in na_dim.nad_wood_description.all()]) if na_dim else 'N/A'

        # Need assessment info for checklist descriptions (General Specs)
        type_of_work = str(na.na_type_of_work) if na and na.na_type_of_work else 'N/A'
        scope_of_work = na.na_client_scope if na and na.na_client_scope else 'N/A'
        wood_treatment = str(na.na_wood_treatment_req) if na and na.na_wood_treatment_req else 'N/A'
        wood_norms = ", ".join([str(x) for x in na.na_wood_norms.all()]) if na else 'N/A'
        lifting = ", ".join([str(x) for x in na.na_special_requirements.all()]) if na else 'N/A'
        req_type = str(na.na_type_of_pack1) if na and na.na_type_of_pack1 else 'N/A'

        items_data.append({
            'q_item': q_item,
            'item_code': item_code,
            'length': length,
            'width': width,
            'height': height,
            'qty': qty,
            'plywood': plywood,
            'uom': uom,
            'desc_type_of_work': type_of_work,
            'desc_scope_of_work': scope_of_work,
            'desc_wood_treatment': wood_treatment,
            'desc_wood_norms': wood_norms,
            'desc_lifting': lifting,
            'desc_req_type': req_type,
            'desc_wood_type': wood_types,
            'desc_wood_description': wood_descs,
        })
        
    context = {
        'qc_master': qc_master,
        'po': po,
        'customer': customer,
        'items_data': items_data,
    }
    
    file_name = f"Quality_Check_{qc_master.qc_job_no}.pdf"
    template_path = 'asset_mgt_app/pk_quality_check_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We encountered an error while generating the PDF.')

    return response
