from django import template
from django.urls import reverse
from ..models import PkneedassessmentInfo, PkquotationsummaryInfo, PkpurchaseorderInfo, PkcostingsummaryInfo, Packingjobs

register = template.Library()
@register.filter(name='split')
def split(value, arg):
    return value.split(arg)

@register.inclusion_tag('asset_mgt_app/pk_workflow_tracker.html')
def pk_workflow_tracker(assessment_id, current_stage):
    """
    Renders a progress bar for the PMS workflow.
    Expanded stages based on TL's process flow.
    """
    stages = [
        {'name': 'Assessment', 'url_name': 'needassessment_update', 'id': assessment_id},
        {'name': 'Quotation', 'url_name': 'pk_quotationsummary_update', 'id': None},
        {'name': 'Sales Order', 'url_name': 'purchaseorder_update', 'id': None},
        {'name': 'Costing', 'url_name': 'costingsummary_update', 'id': None},
        {'name': 'Acceptance', 'url_name': 'pk_acceptance_list', 'id': None},
        {'name': 'Production', 'url_name': 'pk_production_dashboard', 'id': None},
        {'name': 'Quality Check', 'url_name': 'pk_quality_check_list', 'id': None},
        {'name': 'Gate Pass / DC', 'url_name': 'packing_gate_list', 'id': None},
        {'name': 'Invoice', 'url_name': 'invoice_list', 'id': None},
    ]

    job_no = None
    pack_type = 'In-House'

    # Map existing records to stages
    if assessment_id:
        # Check for Quotation
        quot = PkquotationsummaryInfo.objects.filter(qs_assessment_num=assessment_id).first()
        if quot:
            stages[1]['id'] = quot.id
        
        # Check for PO
        po = PkpurchaseorderInfo.objects.filter(po_assessment_num=assessment_id).first()
        if po:
            stages[2]['id'] = po.id
            
        # Check for Costing
        costing = PkcostingsummaryInfo.objects.filter(cs_assessment_num=assessment_id).first()
        if costing:
            stages[3]['id'] = costing.id
            job_no = costing.cs_job_no
            if costing.cs_assessment_num and costing.cs_assessment_num.na_delivery_type:
                pack_type = str(costing.cs_assessment_num.na_delivery_type)

        # Check for Production/QC/GP status via Packingjobs
        if job_no:
            pj = Packingjobs.objects.filter(pj_job_no=job_no).first()
            if pj:
                # Always allow going to Dashboard/List views, but we mark them as 'done' if status is Completed
                stages[5]['id'] = assessment_id # Production Dashboard
                if pj.pj_production_completed_flag == 'Completed':
                    stages[6]['id'] = assessment_id # QC
                if pj.pj_qc_completed_flag == 'Completed':
                    stages[7]['id'] = assessment_id # Gate Pass

    # For On-Site jobs, the flow is slightly different in the slides (DC happens earlier)
    # But for the visual tracker, we keep a consistent logical sequence.
    
    return {
        'stages': stages,
        'current_stage': int(current_stage),
        'assessment_id': assessment_id,
        'pack_type': pack_type
    }
