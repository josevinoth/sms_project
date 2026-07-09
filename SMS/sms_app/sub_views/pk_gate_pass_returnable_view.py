from django.contrib.auth.decorators import login_required
from ..forms import GatepassreturnForm
from ..models import PackingGateReturn, Warehouse_goods_info, POdimension, User, PkpurchaseorderInfo, PkcostingsummaryInfo, CustomerInfo, PkneedassessmentInfo, PkcostingInfo
from ..sub_models.packing_jobs_mod import Packingjobs
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import render, redirect

from .pk_needassessment_view import get_tracker_flags
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id

@login_required(login_url='login_page')
def gate_return_add(request, gate_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    gate_list = PackingGateReturn.objects.all().order_by('-id')
    
    if request.method == "GET":
        if gate_id == 0:
            job_no = request.GET.get('job_no')
            initial_data = {}
            costing = None
            if job_no:
                costing = PkcostingsummaryInfo.objects.filter(cs_job_no=job_no).first()
                if costing:
                    pack_type = Packingjobs.objects.filter(pj_job_no=job_no).values_list('pj_pack_type', flat=True).first() or 'In-House'
                    po_obj = PkpurchaseorderInfo.objects.filter(po_assessment_num=costing.cs_assessment_num).first()
                    initial_data = {
                        'gp_job_no': job_no,
                        'gp_customer_name': costing.cs_customer_name,
                        'gp_customer_po': po_obj,
                        'gp_assessment_num': costing.cs_assessment_num,
                        'gp_document_category': 'Delivery Challan' if 'On-Site' in pack_type else 'Gate Pass',
                        'gp_sales_order_po': po_obj.sales_order_num if po_obj else '',
                        'gp_customer_gstin': costing.cs_customer_name.cu_gst if costing.cs_customer_name else '',
                        'gp_customer_bill_to_gstin': costing.cs_customer_name.cu_gst if costing.cs_customer_name else '',
                        'gp_packing_location': costing.cs_assessment_num.na_packing_field if costing.cs_assessment_num else None,
                    }
            
            pack_type = Packingjobs.objects.filter(pj_job_no=job_no).values_list('pj_pack_type', flat=True).first() if job_no else 'In-House'
            
            form = GatepassreturnForm(initial=initial_data)
            assessment_id = request.session.get('na_assessment_id') or (costing.cs_assessment_num.id if job_no and costing else None)
            
            context = {
                'form':form,
                'first_name': first_name,
                'gate_list': gate_list,
                'assessment_id': assessment_id,
                'current_step': 'gate_pass',
                'tracker_flags': get_tracker_flags(assessment_id),
                'pack_type': pack_type,
                'user_id': user_id,
                'gp_employee': initial_data.get('gp_employee','') if isinstance(initial_data, dict) else '',
            }
        else:
            gate = PackingGateReturn.objects.get(pk=gate_id)
            form = GatepassreturnForm(instance=gate)
            
            # Get all assessment numbers associated with this Job No from the costing info
            assess_ids = PkcostingInfo.objects.filter(
                ct_job_no=gate.gp_job_no
            ).values_list('ct_assessment_num', flat=True).distinct()
            
            gatepassreturn_list = POdimension.objects.filter(
                pod_assess_num__in=assess_ids, 
                pod_po_num=gate.gp_customer_po
            )
            
            assessment_id = request.session.get('na_assessment_id') or (assess_ids[0] if assess_ids else None)
            
            context = {
                'form':form,
                'gatepassreturn_list': gatepassreturn_list,
                'first_name': first_name,
                'gate': gate,
                'assessment_id': assessment_id,
                'current_step': 'gate_pass',
                'tracker_flags': get_tracker_flags(assessment_id),
                'pack_type': Packingjobs.objects.filter(pj_job_no=gate.gp_job_no).values_list('pj_pack_type', flat=True).first() or 'In-House',
                'user_id': user_id,
                'gp_employee': getattr(gate, 'gp_employee', '') if gate else '',
            }
        return render(request, "asset_mgt_app/pk_gate_pass_return_add.html", context)

    else:
        if gate_id == 0:
            form = GatepassreturnForm(request.POST)
        else:
            delivery = PackingGateReturn.objects.get(pk=gate_id)
            form = GatepassreturnForm(request.POST, instance=delivery)
        if form.is_valid():
            gate_pass = form.save(commit=False)
            # Set default category only if not provided by form
            if not gate_pass.gp_document_category:
                job = Packingjobs.objects.filter(pj_job_no=gate_pass.gp_job_no).first()
                if job and 'On-Site' in job.pj_pack_type:
                    gate_pass.gp_document_category = 'Delivery Challan'
                else:
                    gate_pass.gp_document_category = 'Gate Pass'
            gate_pass.save()
            form.save_m2m() # Required for ManyToMany with commit=False

            # If tools are selected, mark them as 'In Use'
            if gate_pass.gp_tools.exists():
                gate_pass.gp_tools.all().update(tm_status='In Use')

            if gate_id == 0:
                messages.success(request, 'Record Saved Successfully')
            else:
                messages.success(request, 'Record Updated Successfully')
        else:
            messages.error(request, 'Error: Please correct the errors below.')

        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error in {field}: {error}")
                messages.error(request, f"Error in {field}: {error}")
        return redirect(request.META['HTTP_REFERER'])


# List gatepass
@login_required(login_url='login_page')
def gate_return_list(request):
    first_name = request.session.get('first_name')
    gate_list = PackingGateReturn.objects.all().order_by('-id')
    context = {'gate_list': gate_list, 'first_name': first_name}
    return render(request,"asset_mgt_app/pk_gate_pass_returnable_list.html",context)

#Delete gatepass
@login_required(login_url='login_page')
def gate_return_delete(request,gate_id):
    gate = PackingGateReturn.objects.get(pk=gate_id)
    gate.delete()
    return redirect('/SMS/packing_gate_list')


@login_required(login_url='login_page')
def gate_return_pdf(request, gate_id):
    gate = PackingGateReturn.objects.filter(id=gate_id).first()
    # Pull items directly linked to this Job Number via the Costing info
    # Use a fallback strategy for older records where the direct link might be missing
    pod_ids = list(PkcostingInfo.objects.filter(
        ct_job_no=gate.gp_job_no
    ).values_list('ct_po_dimension', flat=True).distinct())
    
    # Filter out None values
    pod_ids = [pid for pid in pod_ids if pid is not None]
    
    if pod_ids:
        gatepass_list = POdimension.objects.filter(id__in=pod_ids)
    else:
        # Fallback: Find assessments linked to this Job No and filter PO items by them
        assessments = PkcostingInfo.objects.filter(
            ct_job_no=gate.gp_job_no
        ).values_list('ct_assessment_num', flat=True).distinct()
        
        gatepass_list = POdimension.objects.filter(
            pod_assess_num__in=assessments, 
            pod_po_num=gate.gp_customer_po
        )

    if not gate:
        messages.error(request, "Record not found.")
        return redirect('/SMS/packing_gate_list')

    wh_location = None
    if gate.gp_assessment_num:
        wh_location = Warehouse_goods_info.objects.filter(wh_dispatch_num=gate.gp_assessment_num).values_list(
            'wh_branch__loc_name', flat=True).order_by('id').first()

    print("Warehouse Location:", wh_location)
    
    # Removed faulty HSN fallback since Nadimension does not have an HSN code field

    if not wh_location:
        wh_location = "BVM Chennai"

    import os
    from django.conf import settings
    logo_path = os.path.join(settings.MEDIA_ROOT, 'logo1.png')

    total_sum = sum(item.pod_total_value or 0 for item in gatepass_list)

    context = {
        'gate': gate,
        'gatepass_list': gatepass_list,
        'wh_location': wh_location,
        'logo_path': logo_path if os.path.exists(logo_path) else None,
        'total_sum': total_sum,
    }

    category = gate.gp_document_category if gate.gp_document_category else "Gate Pass"
    file_name = f"{category}_{gate_id}.pdf"
    template_path = 'asset_mgt_app/pk_gate_pass_return.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We encountered an error while generating the PDF.')

    return response

@login_required(login_url='login_page')
def gate_return_employee_id(request):
    user_id = request.GET.get('id', None)
    employee_value = ''
    debug_msg = ''
    
    if user_id:
        try:

            from django.contrib.auth.models import User
            user = None
            
            # Remove any leading/trailing whitespace
            user_id = user_id.strip()
            
            # 1. Try finding by ID (PK)
            if user_id.isdigit():
                user = User.objects.filter(id=user_id).first()
                if user: debug_msg = f"Found by ID: {user_id}"
            
            # 2. Try finding by username (exact match)
            if not user:
                user = User.objects.filter(username=user_id).first()
                if user: debug_msg = f"Found by Username: {user_id}"
                
            # 3. Try finding by Full Name (case-insensitive)
            if not user:
                from django.db.models.functions import Concat, Trim
                from django.db.models import Value
                
                # Use Trim to handle cases where first_name or last_name might be empty resulting in trailing/leading spaces
                user = User.objects.annotate(
                    full_name=Trim(Concat('first_name', Value(' '), 'last_name'))
                ).filter(full_name__iexact=user_id.strip()).first()
                
                if user: debug_msg = f"Found by Full Name: {user_id}"

            
            if user:
                employee_value = user.username
            else:
                debug_msg = f"No user found for: {user_id}"
                
        except Exception as e:
            debug_msg = f"Error: {str(e)}"
            
    return JsonResponse({
        'employee': employee_value,
        'debug': debug_msg,
        'received_id': user_id
    })




@login_required(login_url='login_page')
def update_dc_item_financials(request):
    if request.method == 'POST':
        pod_id = request.POST.get('pod_id')
        base_value = request.POST.get('base_value', 0)
        gst_rate = request.POST.get('gst_rate', 0)
        gst_amount = request.POST.get('gst_amount', 0)
        total_value = request.POST.get('total_value', 0)
        returnable = request.POST.get('returnable', 'Non-Returnable')
        
        try:
            pod = POdimension.objects.get(id=pod_id)
            pod.pod_base_value = float(base_value)
            pod.pod_gst_rate = float(gst_rate)
            pod.pod_gst_amount = float(gst_amount)
            pod.pod_total_value = float(total_value)
            pod.pod_returnable_status = returnable
            pod.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)


@login_required(login_url='login_page')
def gate_pass_get_jobs_by_customer(request):
    customer_id = request.GET.get('customer_id')
    user = CustomerInfo.objects.filter(id=customer_id).first()
    
    # Get Job Numbers that ALREADY have a Gate Pass
    existing_jobs = set(PackingGateReturn.objects.values_list('gp_job_no', flat=True))

    # Retrieve jobs that have been approved on the Dashboard (Production AND QC must be Completed)
    valid_jobs = Packingjobs.objects.filter(
        pj_production_completed_flag='Completed',
        pj_qc_completed_flag='Completed'
    ).values_list('pj_job_no', flat=True)

    # Get unique Job Numbers for this customer
    job_no_qs = PkcostingsummaryInfo.objects.filter(
        cs_customer_name=customer_id,
        cs_job_no__isnull=False,
        cs_job_no__in=valid_jobs
    ).exclude(cs_job_no='').values_list('cs_job_no', flat=True).distinct()
    
    # Filter out jobs that already have a gate pass
    job_no_list = [job for job in job_no_qs if job not in existing_jobs]
    
    return JsonResponse({
        'customer_gstin': user.cu_gst if user else '',
        'job_no_list': job_no_list
    })

@login_required(login_url='login_page')
def gate_pass_get_job_details(request):
    job_no = request.GET.get('job_no')
    customer_id = request.GET.get('customer_id')
    
    # Find the costing record for this job and customer
    costing = PkcostingsummaryInfo.objects.filter(
        cs_job_no=job_no, 
        cs_customer_name=customer_id
    ).first()
    
    data = {
        'po_id': '',
        'po_num': '',
        'sales_order': '',
        'assessment_id': '',
        'po_list_id': [],
        'po_list_name': [],
        'customer_gstin': '',
        'bvm_inv_no': '',
        'hsn_code': '',
    }
    
    if costing:
        po = costing.cs_customer_po
        data['po_id'] = po.id if po else ''
        data['po_num'] = po.po_num if po else ''
        data['sales_order'] = po.sales_order_num if po else ''
        data['assessment_id'] = costing.cs_assessment_num.id if costing.cs_assessment_num else ''
        
        # Packing Type & Document Category
        pack_type = Packingjobs.objects.filter(pj_job_no=job_no).values_list('pj_pack_type', flat=True).first() or 'In-House'
        data['pack_type'] = pack_type
        data['document_category'] = 'Delivery Challan' if 'On-Site' in pack_type else 'Gate Pass'
        
        # Reference Fields from Costing
        data['customer_gstin'] = costing.cs_customer_name.cu_gst if costing.cs_customer_name else ''
        data['bvm_inv_no'] = costing.cs_invoice_num if costing.cs_invoice_num else ''
        
        # HSN Code from linked Need Assessment dimensions if possible
        if costing.cs_assessment_num:
            from ..models import Nadimension
            hsn = Nadimension.objects.filter(na_assessment_num=costing.cs_assessment_num).values_list('na_hsn_code', flat=True).first()
            data['hsn_code'] = hsn if hsn else ''

        # Also return the full PO list for this customer
        po_qs = PkpurchaseorderInfo.objects.filter(po_customer_name=customer_id)
        data['po_list_id'] = list(po_qs.values_list('id', flat=True))
        data['po_list_name'] = list(po_qs.values_list('po_num', flat=True))
        
    return JsonResponse(data)