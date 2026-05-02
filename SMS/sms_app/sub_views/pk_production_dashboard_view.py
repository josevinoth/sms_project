from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from sms_app.sub_models.pk_costing_summary_mod import PkcostingsummaryInfo
from sms_app.sub_models.packing_jobs_mod import Packingjobs
from django.views.decorators.csrf import csrf_exempt


@login_required(login_url='login_page')
def pk_production_dashboard(request):
    first_name = request.session.get('first_name')

    # Pull all Costing Summary entries that have a confirmed Job No
    costing_jobs = (
        PkcostingsummaryInfo.objects
        .exclude(cs_job_no__isnull=True)
        .exclude(cs_job_no='')
        .select_related('cs_customer_name', 'cs_assessment_num')
        .order_by('-id')
    )

    # Build a lookup of existing status flags keyed by job_no
    status_map = {
        pj.pj_job_no: pj
        for pj in Packingjobs.objects.all()
    }

    # Merge: augment each costing job with its production/material status
    dashboard_rows = []
    for job in costing_jobs:
        job_no = job.cs_job_no

        # Get or create a status record for this job_no (auto-seed with Pending)
        if job_no not in status_map:
            status_tracker = Packingjobs.objects.create(
                pj_job_no=job_no,
                pj_customer=job.cs_customer_name.cu_name if job.cs_customer_name else job.cs_customer_new_name or '',
                pj_pack_type=job.cs_pack_type or 'In-House',
                pj_production_completed_flag='Pending',
                pj_material_returned_flag='Pending',
                pj_qc_completed_flag='Pending',
            )
        else:
            status_tracker = status_map[job_no]

        dashboard_rows.append({
            'costing': job,
            'tracker': status_tracker,
        })

    context = {
        'first_name': first_name,
        'dashboard_rows': dashboard_rows,
        'assessment_id': request.session.get('na_assessment_id'),
        'current_stage': 6,
    }
    return render(request, 'asset_mgt_app/pk_production_dashboard.html', context)


@csrf_exempt
@login_required(login_url='login_page')
def update_production_status(request):
    if request.method == 'POST':
        job_no = request.POST.get('job_no')
        production_status = request.POST.get('production_status')
        material_status = request.POST.get('material_status')

        if not job_no:
            return JsonResponse({'status': 'error', 'message': 'job_no is required'})

        try:
            # Normalize job_no to prevent mismatches
            job_no = job_no.strip()
            
            # Get or create the Packingjobs tracker record for this job_no
            # We use filter().first() to be more resilient than get()
            job = Packingjobs.objects.filter(pj_job_no=job_no).first()
            
            if not job:
                job = Packingjobs.objects.create(
                    pj_job_no=job_no,
                    pj_production_completed_flag='Pending',
                    pj_material_returned_flag='Pending',
                    pj_qc_completed_flag='Pending',
                    pj_pack_type=PkcostingsummaryInfo.objects.filter(cs_job_no=job_no).values_list('cs_pack_type', flat=True).first() or 'In-House'
                )
            
            if production_status:
                job.pj_production_completed_flag = production_status
            if material_status:
                job.pj_material_returned_flag = material_status
            job.save()
            return JsonResponse({'status': 'success', 'message': 'Status updated successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
