from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from ..models import PkcostingsummaryInfo, PkcostingInfo, PkQualityCheck, PkQualityCheckItem, Packingjobs, PkneedassessmentInfo, MyUser
from django.views.decorators.csrf import csrf_exempt

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
            
            # Delete existing items to recreate (cleaner for dynamic tables)
            PkQualityCheckItem.objects.filter(qc_master=qc_master).delete()
            
            # Save Item details
            costing_items = PkcostingInfo.objects.filter(ct_job_no=job_no)
            for item in costing_items:
                item_id = str(item.id)
                qc_item = PkQualityCheckItem(
                    qc_master=qc_master,
                    qc_costing_item=item,
                    qc_accepted_qty=float(request.POST.get(f'accepted_qty_{item_id}', 0)),
                    qc_rejected_qty=float(request.POST.get(f'rejected_qty_{item_id}', 0)),
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
    
    return render(request, 'asset_mgt_app/pk_quality_check_add.html', {
        'costing_jobs': costing_jobs,
        'selected_job_no': selected_job_no,
        'assessment_id': assessment_id,
        'current_stage': 7,
        'first_name': first_name
    })

@csrf_exempt
@login_required(login_url='login_page')
def get_job_details_for_qc(request):
    job_no = request.GET.get('job_no', '').strip()
    if not job_no:
        return JsonResponse({'status': 'error', 'message': 'Job No is missing'})
        
    try:
        summary = PkcostingsummaryInfo.objects.filter(cs_job_no=job_no).first()
        if not summary:
            return JsonResponse({'status': 'error', 'message': f'Job No {job_no} not found in costing records'})
            
        po = summary.cs_customer_po
        na = summary.cs_assessment_num
        
        # Pull checklist requirements from Need Assessment if available
        wood_norms = ""
        special_reqs = ""
        na_details = {
            'type_of_work': 'N/A',
            'client_scope': 'N/A',
            'wood_treatment': 'N/A',
            'wood_norms': 'N/A',
            'lifting': 'N/A',
            'req_type': 'N/A',
        }
        
        if na:
            wood_norms = ", ".join([str(x) for x in na.na_wood_norms.all()])
            special_reqs = ", ".join([str(x) for x in na.na_special_requirements.all()])
            na_details = {
                'type_of_work': str(na.na_type_of_work) if na.na_type_of_work else 'N/A',
                'client_scope': na.na_client_scope or 'N/A',
                'wood_treatment': str(na.na_wood_treatment_req) if na.na_wood_treatment_req else 'N/A',
                'wood_norms': wood_norms or 'N/A',
                'lifting': special_reqs or 'N/A',
                'req_type': str(na.na_type_of_pack1) if na.na_type_of_pack1 else 'N/A',
            }
        
        items_data = []
        costing_items = PkcostingInfo.objects.filter(ct_job_no=job_no)
        for item in costing_items:
            items_data.append({
                'id': item.id,
                'item_name': str(item.ct_item) if item.ct_item else (str(item.ct_itemdescription) if item.ct_itemdescription else 'Item'),
                'qty': item.ct_quantity_req,
                'l': item.ct_length,
                'w': item.ct_width,
                'h': item.ct_height,
                'thickness': item.ct_size or 'N/A',
                'uom': str(item.ct_uom) if item.ct_uom else 'Nos'
            })
            
        data = {
            'status': 'success',
            'customer': summary.cs_customer_name.cu_name if summary.cs_customer_name else (summary.cs_customer_new_name or 'N/A'),
            'po_no': po.po_num if po else 'N/A',
            'po_date': po.po_date.strftime('%Y-%m-%d') if po and po.po_date else 'N/A',
            'na_details': na_details,
            'items': items_data
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
