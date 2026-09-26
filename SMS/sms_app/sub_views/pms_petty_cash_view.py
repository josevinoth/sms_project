from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from ..sub_models.pms_petty_cash_mod import PMSPettyCashInfo
from ..sub_models.gatein_mod import Gatein_info
from ..sub_models.credit_ledger_mod import CreditLedgerInfo
from ..models import Business_Sol_info, Location_info, ExpenseCategoryInfo, iou_info, CustomerInfo, Warehouse_goods_info, UnitInfo
from ..sub_forms.pms_petty_cash_form import PMSPettyCashForm
from .general_utils import get_financial_year, get_session_branch_id


def generate_pms_petty_cash_number(model_class, field_name, branch_obj=None):
    """
    Generates Voucher Number format in UPPERCASE: [BranchCode]-Pkg-[MM]-[FY]-[Seq]
    Example: MAA-Pkg-09-26/27-01 or BLR-Pkg-09-26/27-01
    """
    fy = get_financial_year() # e.g. "26-27"
    fy_slash = fy.replace('-', '/') # "26/27"
    today = datetime.now()
    month_str = today.strftime("%m") # "09"

    branch_code = "MAA"
    if branch_obj and branch_obj.loc_name:
        loc_name_upper = branch_obj.loc_name.upper()
        if "MAA" in loc_name_upper or "CHENNAI" in loc_name_upper:
            branch_code = "MAA"
        elif "BLR" in loc_name_upper or "BANGALORE" in loc_name_upper or "BENGALURU" in loc_name_upper:
            branch_code = "BLR"
        elif "PNY" in loc_name_upper or "PONDICHERRY" in loc_name_upper:
            branch_code = "PNY"
        elif "HYD" in loc_name_upper or "HYDERABAD" in loc_name_upper:
            branch_code = "HYD"
        elif "CBE" in loc_name_upper or "COIMBATORE" in loc_name_upper:
            branch_code = "CBE"
        else:
            branch_code = branch_obj.loc_name.split()[-1].upper()

    prefix = f"{branch_code}-PKG-{month_str}-{fy_slash}-"

    # fetch latest for this prefix (case-insensitive check)
    latest_obj = model_class.objects.filter(
        Q(**{f"{field_name}__istartswith": prefix}) | Q(**{f"{field_name}__istartswith": f"{branch_code.title()}-PKG-{month_str}-{fy_slash}-"})
    ).order_by('-id').first()

    if latest_obj:
        latest_num_str = getattr(latest_obj, field_name)
        try:
            seq = int(latest_num_str.split('-')[-1])
            new_seq = seq + 1
        except ValueError:
            new_seq = 1
    else:
        new_seq = 1

    return f"{prefix}{str(new_seq).zfill(2)}"


def pms_petty_cash_add(request, ppc_id=0):
    initial_data = {}
    if ppc_id == 0:
        # Default Business
        bvm_pack = Business_Sol_info.objects.filter(bvm_business__icontains='Pack').first()
        if bvm_pack:
            initial_data['ppc_business'] = bvm_pack.id

        # Default Expense Category to Cash Expense
        cash_cat = ExpenseCategoryInfo.objects.filter(exp_category_name__icontains='Cash').first()
        if cash_cat:
            initial_data['ppc_category'] = cash_cat.id

        # Default Branch based on session
        branch_id = get_session_branch_id(request)
        if branch_id:
            initial_data['ppc_branch'] = branch_id

            # Default Credit Ledger based on branch name
            branch_obj = Location_info.objects.filter(id=branch_id).first()
            if branch_obj:
                branch_code = branch_obj.loc_name.split()[-1]
                ledger = CreditLedgerInfo.objects.filter(
                    ledger_name__icontains='PACK Petty cash'
                ).filter(
                    ledger_name__icontains=branch_code
                ).exclude(
                    ledger_name__icontains='Admin'
                ).first()
                if not ledger:
                    ledger = CreditLedgerInfo.objects.filter(
                        ledger_name__icontains='PACK'
                    ).filter(
                        ledger_name__icontains=branch_code
                    ).first()
                if ledger:
                    initial_data['ppc_credit_ledger'] = ledger.id

        form = PMSPettyCashForm(initial=initial_data, request=request)
    else:
        wpc = get_object_or_404(PMSPettyCashInfo, pk=ppc_id)
        form = PMSPettyCashForm(instance=wpc, request=request)

    if request.method == 'POST':
        post_data = request.POST.copy()

        # Handle 'To Person' text vs User ForeignKey
        if post_data.get('ppc_to'):
            if not str(post_data['ppc_to']).isdigit():
                post_data['ppc_to_manual'] = str(post_data['ppc_to']).strip()
                post_data['ppc_to'] = ''
            else:
                post_data['ppc_to_manual'] = ''
        else:
            post_data['ppc_to_manual'] = ''

        # Auto-calculate amounts in backend
        try:
            bill_amt = float(post_data.get('ppc_bill_amount') or 0.0)
            gst_pct = float(post_data.get('ppc_gst_percentage') or 0.0)
            gst_amt = round((bill_amt * gst_pct) / 100.0, 2)
            total_amt = round(bill_amt + gst_amt, 2)
            post_data['ppc_gst_amount'] = str(gst_amt)
            post_data['ppc_total_amount'] = str(total_amt)
            post_data['ppc_amount'] = str(total_amt) # Map to Tally's field
        except Exception:
            pass

        if ppc_id == 0:
            form = PMSPettyCashForm(post_data, request.FILES, request=request)
        else:
            wpc = get_object_or_404(PMSPettyCashInfo, pk=ppc_id)
            form = PMSPettyCashForm(post_data, request.FILES, instance=wpc, request=request)

        if form.is_valid():
            saved_wpc = form.save(commit=False)
            if ppc_id == 0:
                saved_wpc.ppc_number = generate_pms_petty_cash_number(PMSPettyCashInfo, 'ppc_number', saved_wpc.ppc_branch)
                saved_wpc.ppc_created_by = request.user
            saved_wpc.ppc_updated_by = request.user
            saved_wpc.save()
            messages.success(request, "PMS Petty Cash saved successfully.")
            return redirect('pms_petty_cash_list')
        else:
            messages.error(request, "Please correct the errors below.")

    context = {
        'form': form,
        'ppc_id': ppc_id,
    }
    return render(request, "asset_mgt_app/pms_petty_cash_add.html", context)


def pms_petty_cash_list(request):
    ppc_number = request.GET.get('ppc_number', "").strip()
    search_date = request.GET.get('search_date', "").strip()
    from_date = request.GET.get('from_date', "").strip()
    to_date = request.GET.get('to_date', "").strip()
    search_unit = request.GET.get('search_unit', "").strip()
    search_branch = request.GET.get('search_branch', "").strip()

    filters = Q()
    if ppc_number:
        filters &= Q(ppc_number__icontains=ppc_number)
    if search_date:
        filters &= Q(ppc_transaction_date=search_date)
    if from_date:
        filters &= Q(ppc_transaction_date__gte=from_date)
    if to_date:
        filters &= Q(ppc_transaction_date__lte=to_date)
    if search_unit:
        filters &= Q(ppc_unit__icontains=search_unit)

    user = request.user
    is_admin_or_supervisor = user.is_superuser
    if not is_admin_or_supervisor:
        try:
            from ..sub_models.user_ext_mod import User_extInfo
            user_ext = User_extInfo.objects.select_related('emp_designation', 'emp_role').get(user_id=user.id)
            desig = str(user_ext.emp_designation).lower() if user_ext.emp_designation else ''
            role = str(user_ext.emp_role).lower() if user_ext.emp_role else ''
            if 'supervisor' in desig or 'admin' in role:
                is_admin_or_supervisor = True
        except Exception:
            pass

    if not is_admin_or_supervisor:
        branch_id = get_session_branch_id(request)
        if branch_id:
            filters &= Q(ppc_branch_id=branch_id)
    else:
        if search_branch:
            filters &= Q(ppc_branch__loc_name__icontains=search_branch)

    ppc_list = PMSPettyCashInfo.objects.filter(filters).select_related(
        'ppc_business', 'ppc_branch', 'ppc_category', 'ppc_expense_type',
        'ppc_credit_ledger', 'ppc_to', 'ppc_customer', 
        'ppc_created_by', 'ppc_updated_by'
    ).order_by('-id')

    paginator = Paginator(ppc_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    from ..sub_models.pms_petty_cash_mod import UNIT_CHOICES
    unit_list = [choice[0] for choice in UNIT_CHOICES]

    context = {
        'ppc_list': page_obj,
        'search_ppc_number': ppc_number,
        'search_date': search_date,
        'from_date': from_date,
        'to_date': to_date,
        'search_unit': search_unit,
        'search_branch': search_branch,
        'unit_list': unit_list,
        'is_admin_or_supervisor': is_admin_or_supervisor,
    }
    return render(request, "asset_mgt_app/pms_petty_cash_list.html", context)


def pms_petty_cash_delete(request, ppc_id):
    wpc = get_object_or_404(PMSPettyCashInfo, pk=ppc_id)
    wpc.delete()
    messages.success(request, "PMS Petty Cash deleted successfully.")
    return redirect('pms_petty_cash_list')


def get_pms_customers_by_unit(request):
    """
    Fetch Pack customers.
    """
    customers = CustomerInfo.objects.filter(cu_business_sol__bvm_business__icontains='Pack').order_by('cu_name')
    if not customers.exists():
        customers = CustomerInfo.objects.all().order_by('cu_name')
    customers_data = [{'id': c.id, 'name': c.cu_name} for c in customers]

    return JsonResponse({'status': 'success', 'customers': customers_data})


def get_pms_jobs_by_customer(request):
    """
    Fetch distinct Job Numbers for the selected Customer from Packingjobs.
    """
    customer_id = request.GET.get('customer_id', '').strip()
    
    if not customer_id:
        return JsonResponse({'status': 'success', 'jobs': []})

    try:
        from sms_app.sub_models.packing_jobs_mod import Packingjobs
        
        customer = CustomerInfo.objects.get(id=customer_id)
        cust_name = customer.cu_name
        
        jobs = list(
            Packingjobs.objects.filter(pj_customer__iexact=cust_name)
            .exclude(pj_job_no__isnull=True)
            .exclude(pj_job_no__exact='')
            .values_list('pj_job_no', flat=True)
            .distinct()
            .order_by('-pj_job_no')[:200]
        )
        
        jobs_data = [{'job_no': j} for j in jobs]
        return JsonResponse({'status': 'success', 'jobs': jobs_data})
    except Exception as e:
        return JsonResponse({'status': 'error', 'jobs': []})

    filters = Q(wh_customer_name_id=customer_id)
    if unit_name:
        filters &= Q(wh_unit__unit_name__iexact=unit_name)

    jobs = list(
        Warehouse_goods_info.objects.filter(filters)
        .exclude(wh_job_no__isnull=True)
        .exclude(wh_job_no__exact='')
        .values_list('wh_job_no', flat=True)
        .distinct()
        .order_by('-wh_job_no')[:200]
    )

    # Fallback to Gatein_info if no jobs in Warehouse_goods_info
    if not jobs:
        jobs = list(
            Gatein_info.objects.filter(gatein_customer_id=customer_id)
            .exclude(gatein_job_no__isnull=True)
            .exclude(gatein_job_no__exact='')
            .values_list('gatein_job_no', flat=True)
            .distinct()
            .order_by('-gatein_job_no')[:200]
        )

    return JsonResponse({'status': 'success', 'jobs': jobs})


def get_pms_job_details(request):
    """
    AJAX endpoint to fetch full package job details from Packingjobs and PkcostingsummaryInfo
    """
    from sms_app.sub_models.packing_jobs_mod import Packingjobs
    from sms_app.sub_models.pk_costing_summary_mod import PkcostingsummaryInfo
    from sms_app.sub_models.na_dimension_mod import Nadimension
    from django.db.models import Sum

    job_no = request.GET.get('job_no', '').strip()
    if not job_no:
        return JsonResponse({'status': 'error', 'message': 'No job number provided'})

    pack_job = Packingjobs.objects.filter(pj_job_no__iexact=job_no).first()
    costing_summary = PkcostingsummaryInfo.objects.filter(cs_job_no__iexact=job_no).first()

    if pack_job:
        # Fallbacks to Costing Summary if Packingjobs is empty
        bill_amount = pack_job.pj_bill_amount
        if (not bill_amount or str(bill_amount) == '0' or str(bill_amount) == '0.0') and costing_summary:
            bill_amount = costing_summary.cs_total_cost_wm
            
        reference = pack_job.pj_reference
        if not reference and costing_summary:
            if costing_summary.cs_customer_po:
                reference = str(costing_summary.cs_customer_po)
            else:
                reference = costing_summary.cs_invoice_num

        date = pack_job.pj_date
        if not date and costing_summary and costing_summary.cs_created_at:
            date = costing_summary.cs_created_at.strftime('%d-%m-%Y')

        no_box = pack_job.pj_no_box
        if (not no_box or str(no_box) == '0' or str(no_box) == '0.0') and costing_summary and costing_summary.cs_assessment_num:
            # sum nad_quantity
            total_qty = Nadimension.objects.filter(nad_assess_num=costing_summary.cs_assessment_num).aggregate(Sum('nad_quantity'))['nad_quantity__sum']
            if total_qty:
                no_box = total_qty

        return JsonResponse({
            'status': 'success',
            'job_no': pack_job.pj_job_no,
            'date': date or '',
            'customer': pack_job.pj_customer,
            'pack_type': pack_job.pj_pack_type,
            'no_box': no_box or '-',
            'reference': reference or '-',
            'bill_amount': bill_amount or '-',
            'expense': pack_job.pj_expense or '-',
            'prod_status': pack_job.pj_production_completed_flag or '-',
            'qc_status': pack_job.pj_qc_completed_flag or '-'
        })
    else:
        return JsonResponse({'status': 'error', 'message': 'Job details not found'})

def pms_petty_cash_export_tally(request):
    ppc_number = request.GET.get('ppc_number', "").strip()
    search_date = request.GET.get('search_date', "").strip()
    from_date = request.GET.get('from_date', "").strip()
    to_date = request.GET.get('to_date', "").strip()
    search_unit = request.GET.get('search_unit', "").strip()
    search_branch = request.GET.get('search_branch', "").strip()

    filters = Q()
    if ppc_number:
        filters &= Q(ppc_number__icontains=ppc_number)
    if search_date:
        filters &= Q(ppc_transaction_date=search_date)
    if from_date:
        filters &= Q(ppc_transaction_date__gte=from_date)
    if to_date:
        filters &= Q(ppc_transaction_date__lte=to_date)
    if search_unit:
        filters &= Q(ppc_unit__icontains=search_unit)

    user = request.user
    is_admin_or_supervisor = user.is_superuser
    if not is_admin_or_supervisor:
        try:
            from ..sub_models.user_ext_mod import User_extInfo
            user_ext = User_extInfo.objects.select_related('emp_designation', 'emp_role').get(user_id=user.id)
            desig = str(user_ext.emp_designation).lower() if user_ext.emp_designation else ''
            role = str(user_ext.emp_role).lower() if user_ext.emp_role else ''
            if 'supervisor' in desig or 'admin' in role:
                is_admin_or_supervisor = True
        except Exception:
            pass

    if not is_admin_or_supervisor:
        branch_id = get_session_branch_id(request)
        if branch_id:
            filters &= Q(ppc_branch_id=branch_id)
    else:
        if search_branch:
            filters &= Q(ppc_branch__loc_name__icontains=search_branch)

    ppc_list = PMSPettyCashInfo.objects.filter(filters).select_related(
        'ppc_business', 'ppc_branch', 'ppc_category', 'ppc_expense_type',
        'ppc_credit_ledger', 'ppc_to', 'ppc_customer', 
    ).order_by('-id')

    wb = Workbook()
    ws = wb.active
    ws.title = "Tally Export"

    headers = [
        "DATE", "VOU. NO.", "DEBIT", "CREDIT", "PRIMARY COST CATEGORY", 
        "CUSTOMER", "JOB NO", "VEH.NO.", "AMOUNT", "TO", "TRN DATE", "REMARKS"
    ]
    ws.append(headers)

    header_font = Font(bold=True)
    header_fill = PatternFill("solid", fgColor="FFFF00")
    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    for wpc in ppc_list:
        date_str = wpc.ppc_transaction_date.strftime("%d-%m-%Y") if wpc.ppc_transaction_date else ""
        vou_no = wpc.ppc_number or ""
        debit = wpc.ppc_expense_type.pms_exp_type_name if wpc.ppc_expense_type else ""
        credit = wpc.ppc_credit_ledger.ledger_name if wpc.ppc_credit_ledger else ""
        primary_cost_cat = wpc.ppc_unit or ""
        customer = wpc.ppc_customer.cu_name if wpc.ppc_customer else ""
        job_no = wpc.ppc_job_no or ""

        # Lookup vehicle number if available from Gatein or Goods
        veh_no = "N/A(V)"
        if job_no:
            gatein = Gatein_info.objects.filter(gatein_job_no__iexact=job_no).first()
            if gatein and gatein.gatein_truck_number:
                veh_no = gatein.gatein_truck_number
            else:
                wh_good = Warehouse_goods_info.objects.filter(wh_job_no__iexact=job_no).select_related('wh_truck_type').first()
                if wh_good and wh_good.wh_truck_type:
                    veh_no = wh_good.wh_truck_type.veh_type_name

        amount = wpc.ppc_total_amount or wpc.ppc_bill_amount or 0.0
        to_person = wpc.ppc_to.first_name if wpc.ppc_to else (wpc.ppc_to_manual or "")
        trn_date = wpc.ppc_transaction_date.strftime("%d-%b") if wpc.ppc_transaction_date else ""
        remarks = wpc.ppc_remarks or ""

        ws.append([
            date_str, vou_no, debit, credit, primary_cost_cat,
            customer, job_no, veh_no, amount, to_person, trn_date, remarks
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="PMS_Petty_Cash_Tally_Export.xlsx"'
    wb.save(response)
    return response
