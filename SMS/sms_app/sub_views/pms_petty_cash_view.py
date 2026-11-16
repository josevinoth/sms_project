import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from ..sub_models.pms_petty_cash_mod import PMSPettyCashInfo
from ..sub_models.pms_expense_type_mod import PMSExpenseTypeInfo
from ..sub_models.pms_vehicle_mod import PMSVehicleInfo
from django.views.decorators.csrf import csrf_exempt
from ..sub_models.gatein_mod import Gatein_info
from ..sub_models.credit_ledger_mod import CreditLedgerInfo
from ..models import Business_Sol_info, Location_info, ExpenseCategoryInfo, iou_info, CustomerInfo, Warehouse_goods_info, UnitInfo
from ..sub_forms.pms_petty_cash_form import PMSPettyCashForm
from .general_utils import get_financial_year, get_session_branch_id


def is_admin_or_supervisor_user(request):
    """
    Returns True if current user is admin, superuser, staff, or has supervisor/manager/admin role or designation.
    """
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        ses_user_id = request.session.get('ses_userID')
        if not ses_user_id:
            return False
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(id=ses_user_id)
        except User.DoesNotExist:
            return False

    if user.is_superuser or user.is_staff:
        return True

    user_role = (request.session.get('ses_role') or '').lower()
    if user_role in ['admin', 'super user', 'superuser']:
        return True

    try:
        from ..sub_models.user_ext_mod import User_extInfo
        user_ext = User_extInfo.objects.select_related('emp_designation', 'emp_role').get(user_id=user.id)
        desig = str(user_ext.emp_designation).lower() if user_ext.emp_designation else ''
        role = str(user_ext.emp_role).lower() if user_ext.emp_role else ''
        if 'supervisor' in desig or 'admin' in role or 'super' in role:
            return True
    except Exception:
        pass
    return False


def get_user_branch_code(request):
    """
    Determines the user's branch code: 'MAA', 'BLR', etc.
    Checks User_extInfo.emp_branch, falling back to session ses_branch_id.
    """
    user = getattr(request, 'user', None)
    user_id = user.id if (user and user.is_authenticated) else request.session.get('ses_userID')
    branch_name = ''

    if user_id:
        try:
            from ..sub_models.user_ext_mod import User_extInfo
            user_ext = User_extInfo.objects.select_related('emp_branch').get(user_id=user_id)
            if user_ext.emp_branch and user_ext.emp_branch.loc_name:
                branch_name = user_ext.emp_branch.loc_name
        except Exception:
            pass

    if not branch_name:
        branch_id = request.session.get('ses_branch_id')
        if branch_id:
            try:
                from ..models import Location_info
                loc = Location_info.objects.get(id=branch_id)
                branch_name = loc.loc_name or ''
            except Exception:
                pass

    name_upper = branch_name.upper()
    if 'BLR' in name_upper or 'BANGALORE' in name_upper or 'BENGALURU' in name_upper:
        return 'BLR'
    elif 'MAA' in name_upper or 'CHENNAI' in name_upper:
        return 'MAA'
    elif 'PNY' in name_upper or 'PONDICHERRY' in name_upper:
        return 'PNY'
    elif 'HYD' in name_upper or 'HYDERABAD' in name_upper:
        return 'HYD'
    elif 'CJB' in name_upper or 'COIMBATORE' in name_upper:
        return 'CJB'
    elif branch_name:
        return branch_name.split()[-1].upper()
    return ''


def generate_pms_petty_cash_number(model_class, field_name, branch_obj=None, voucher_date=None):
    """
    Generates Voucher Number format in UPPERCASE: [BranchCode]-PKG-[MM]-[FY]-[Seq]
    strictly based on voucher_date. No fallback date is permitted.
    """
    if not voucher_date:
        raise ValueError("Voucher Date is strictly required to generate PMS voucher number. No fallback date is permitted.")

    if isinstance(voucher_date, str):
        try:
            v_date = datetime.strptime(voucher_date[:10], "%Y-%m-%d").date()
        except Exception:
            raise ValueError(f"Invalid voucher_date format: {voucher_date}")
    elif isinstance(voucher_date, datetime):
        v_date = voucher_date.date()
    elif hasattr(voucher_date, 'month') and hasattr(voucher_date, 'year'):
        v_date = voucher_date
    else:
        raise ValueError(f"Invalid voucher_date: {voucher_date}")

    fy = get_financial_year(v_date) # e.g. "26-27"
    fy_slash = fy.replace('-', '/') # "26/27"
    month_str = f"{v_date.month:02d}"

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

    # fetch all existing numbers for this prefix to get the maximum sequence
    existing_nums = model_class.objects.filter(
        Q(**{f"{field_name}__istartswith": prefix}) | Q(**{f"{field_name}__istartswith": f"{branch_code.title()}-PKG-{month_str}-{fy_slash}-"})
    ).values_list(field_name, flat=True)

    max_seq = 0
    for num_str in existing_nums:
        if num_str:
            try:
                seq = int(num_str.split('-')[-1])
                if seq > max_seq:
                    max_seq = seq
            except (ValueError, IndexError):
                pass
    new_seq = max_seq + 1
    new_num = f"{prefix}{str(new_seq).zfill(2)}"

    while model_class.objects.filter(Q(**{f"{field_name}__iexact": new_num})).exists():
        new_seq += 1
        new_num = f"{prefix}{str(new_seq).zfill(2)}"

    return new_num


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
            if post_data.get('ppc_bill_attachment-clear') in ['on', '1', 'true']:
                saved_wpc.ppc_bill_attachment = None
            voucher_date = saved_wpc.ppc_date
            if not voucher_date:
                messages.error(request, "Voucher Date is strictly required to generate voucher number.")
                return render(request, "asset_mgt_app/pms_petty_cash_add.html", context)

            expected_branch_code = "MAA"
            if saved_wpc.ppc_branch and saved_wpc.ppc_branch.loc_name:
                loc_upper = saved_wpc.ppc_branch.loc_name.upper()
                if "BLR" in loc_upper or "BANGALORE" in loc_upper or "BENGALURU" in loc_upper:
                    expected_branch_code = "BLR"
                elif "MAA" in loc_upper or "CHENNAI" in loc_upper:
                    expected_branch_code = "MAA"
                elif "PNY" in loc_upper or "PONDICHERRY" in loc_upper:
                    expected_branch_code = "PNY"
                elif "HYD" in loc_upper or "HYDERABAD" in loc_upper:
                    expected_branch_code = "HYD"
                elif "CBE" in loc_upper or "COIMBATORE" in loc_upper:
                    expected_branch_code = "CBE"
                else:
                    expected_branch_code = saved_wpc.ppc_branch.loc_name.split()[-1].upper()

            v_fy = get_financial_year(voucher_date).replace('-', '/')
            v_month = f"{voucher_date.month:02d}"
            expected_prefix = f"{expected_branch_code}-PKG-{v_month}-{v_fy}-"

            created_user = request.user if (request.user and request.user.is_authenticated) else None
            if not created_user and request.session.get('ses_userID'):
                from django.contrib.auth.models import User
                try:
                    created_user = User.objects.get(id=request.session['ses_userID'])
                except User.DoesNotExist:
                    pass

            if ppc_id == 0:
                saved_wpc.ppc_number = generate_pms_petty_cash_number(PMSPettyCashInfo, 'ppc_number', saved_wpc.ppc_branch, voucher_date=voucher_date)
                saved_wpc.ppc_created_by = created_user
            else:
                if not saved_wpc.ppc_number or not saved_wpc.ppc_number.upper().startswith(expected_prefix):
                    saved_wpc.ppc_number = generate_pms_petty_cash_number(PMSPettyCashInfo, 'ppc_number', saved_wpc.ppc_branch, voucher_date=voucher_date)
                if not saved_wpc.ppc_created_by and created_user:
                    saved_wpc.ppc_created_by = created_user
            saved_wpc.ppc_updated_by = created_user
            saved_wpc.save()
            messages.success(request, "PMS Petty Cash saved successfully.")
            return redirect('pms_petty_cash_list')
        else:
            messages.error(request, "Please correct the errors below.")

    import os
    bill_filename = ""
    if form.instance and form.instance.ppc_bill_attachment:
        bill_filename = os.path.basename(form.instance.ppc_bill_attachment.name)

    context = {
        'form': form,
        'ppc_id': ppc_id,
        'bill_filename': bill_filename,
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
        filters &= Q(ppc_date=search_date)
    if from_date:
        filters &= Q(ppc_date__gte=from_date)
    if to_date:
        filters &= Q(ppc_date__lte=to_date)
    if search_unit:
        filters &= Q(ppc_unit__icontains=search_unit)

    search_user = request.GET.get('search_user', "").strip()

    is_admin_or_supervisor = is_admin_or_supervisor_user(request)

    if not is_admin_or_supervisor:
        user_branch_code = get_user_branch_code(request)
        if user_branch_code == 'BLR':
            filters &= (Q(ppc_branch__loc_name__icontains='BLR') | Q(ppc_branch__loc_name__icontains='Bangalore') | Q(ppc_branch__loc_name__icontains='Bengaluru'))
        elif user_branch_code == 'MAA':
            filters &= (Q(ppc_branch__loc_name__icontains='MAA') | Q(ppc_branch__loc_name__icontains='Chennai'))
        elif user_branch_code:
            filters &= Q(ppc_branch__loc_name__icontains=user_branch_code)
    else:
        if search_branch:
            if search_branch == 'BLR':
                filters &= (Q(ppc_branch__loc_name__icontains='BLR') | Q(ppc_branch__loc_name__icontains='Bangalore') | Q(ppc_branch__loc_name__icontains='Bengaluru'))
            elif search_branch == 'MAA':
                filters &= (Q(ppc_branch__loc_name__icontains='MAA') | Q(ppc_branch__loc_name__icontains='Chennai'))
            else:
                filters &= Q(ppc_branch__loc_name__icontains=search_branch)
        if search_user:
            filters &= Q(ppc_created_by_id=search_user)

    ppc_list = PMSPettyCashInfo.objects.filter(filters).select_related(
        'ppc_business', 'ppc_branch', 'ppc_category', 'ppc_expense_type',
        'ppc_credit_ledger', 'ppc_to', 'ppc_customer', 'ppc_vehicle_number', 
        'ppc_created_by', 'ppc_updated_by'
    ).order_by('-id')

    paginator = Paginator(ppc_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    from ..sub_models.pms_petty_cash_mod import UNIT_CHOICES
    unit_list = [choice[0] for choice in UNIT_CHOICES]

    user_list = []
    if is_admin_or_supervisor:
        from django.contrib.auth.models import User
        creator_ids = PMSPettyCashInfo.objects.filter(ppc_created_by__isnull=False).values_list('ppc_created_by_id', flat=True).distinct()
        user_list = User.objects.filter(id__in=creator_ids).order_by('first_name', 'username')

    context = {
        'ppc_list': ppc_list,
        'page_obj': page_obj,
        'search_ppc_number': ppc_number,
        'search_date': search_date,
        'from_date': from_date,
        'to_date': to_date,
        'search_unit': search_unit,
        'search_branch': search_branch,
        'search_user': search_user,
        'user_list': user_list,
        'unit_list': unit_list,
        'is_admin_or_supervisor': is_admin_or_supervisor,
    }
    return render(request, "asset_mgt_app/pms_petty_cash_list.html", context)


def pms_petty_cash_delete(request, ppc_id):
    wpc = get_object_or_404(PMSPettyCashInfo, pk=ppc_id)
    wpc.delete()
    messages.success(request, "PMS Petty Cash deleted successfully.")
    return redirect('pms_petty_cash_list')


def number_to_words(n):
    if n == 0 or n is None: return 'Zero'
    ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
    tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
    def _convert(num):
        if num < 20: return ones[num]
        elif num < 100: return tens[num // 10] + ('' if num % 10 == 0 else ' ' + ones[num % 10])
        elif num < 1000: return ones[num // 100] + ' Hundred' + ('' if num % 100 == 0 else ' ' + _convert(num % 100))
        elif num < 100000: return _convert(num // 1000) + ' Thousand' + ('' if num % 1000 == 0 else ' ' + _convert(num % 1000))
        elif num < 10000000: return _convert(num // 100000) + ' Lakh' + ('' if num % 100000 == 0 else ' ' + _convert(num % 100000))
        else: return _convert(num // 10000000) + ' Crore' + ('' if num % 10000000 == 0 else ' ' + _convert(num % 10000000))
    try:
        n_int = int(n)
        return _convert(n_int) + ' Only'
    except:
        return ''


def pms_petty_cash_voucher_print(request, ppc_id):
    ppc = get_object_or_404(PMSPettyCashInfo, pk=ppc_id)
    total_val = ppc.ppc_total_amount if (ppc.ppc_total_amount and ppc.ppc_total_amount > 0) else (ppc.ppc_bill_amount or ppc.ppc_amount or 0)
    amount_in_words = number_to_words(total_val)

    # Determine the 'Payment to' value based on available fields
    payment_to = ''
    if ppc.ppc_to_manual:
        payment_to = ppc.ppc_to_manual
    elif ppc.ppc_to:
        payment_to = ppc.ppc_to.first_name or ppc.ppc_to.username

    # Clean remarks for printing
    clean_remarks = ppc.ppc_remarks or ''
    if 'Auto-generated' in clean_remarks:
        clean_remarks = re.sub(r'\s*\[?Auto-generated.*', '', clean_remarks).strip()

    context = {
        'ppc': ppc,
        'amount_in_words': amount_in_words,
        'payment_to': payment_to,
        'clean_remarks': clean_remarks,
    }
    return render(request, 'asset_mgt_app/pms_petty_cash_voucher.html', context)


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
    from ..sub_models.packing_jobs_mod import Packingjobs
    from ..sub_models.pk_costing_summary_mod import PkcostingsummaryInfo
    from ..sub_models.na_dimension_mod import Nadimension
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
    search_user = request.GET.get('search_user', "").strip()

    filters = Q()
    if ppc_number:
        filters &= Q(ppc_number__icontains=ppc_number)
    if search_date:
        filters &= Q(ppc_date=search_date)
    if from_date:
        filters &= Q(ppc_date__gte=from_date)
    if to_date:
        filters &= Q(ppc_date__lte=to_date)
    if search_unit:
        filters &= Q(ppc_unit__icontains=search_unit)

    is_admin_or_supervisor = is_admin_or_supervisor_user(request)

    if not is_admin_or_supervisor:
        user_branch_code = get_user_branch_code(request)
        if user_branch_code == 'BLR':
            filters &= (Q(ppc_branch__loc_name__icontains='BLR') | Q(ppc_branch__loc_name__icontains='Bangalore') | Q(ppc_branch__loc_name__icontains='Bengaluru'))
        elif user_branch_code == 'MAA':
            filters &= (Q(ppc_branch__loc_name__icontains='MAA') | Q(ppc_branch__loc_name__icontains='Chennai'))
        elif user_branch_code:
            filters &= Q(ppc_branch__loc_name__icontains=user_branch_code)
    else:
        if search_branch:
            if search_branch == 'BLR':
                filters &= (Q(ppc_branch__loc_name__icontains='BLR') | Q(ppc_branch__loc_name__icontains='Bangalore') | Q(ppc_branch__loc_name__icontains='Bengaluru'))
            elif search_branch == 'MAA':
                filters &= (Q(ppc_branch__loc_name__icontains='MAA') | Q(ppc_branch__loc_name__icontains='Chennai'))
            else:
                filters &= Q(ppc_branch__loc_name__icontains=search_branch)
        if search_user:
            filters &= Q(ppc_created_by_id=search_user)

    ppc_list = PMSPettyCashInfo.objects.filter(filters).select_related(
        'ppc_business', 'ppc_branch', 'ppc_category', 'ppc_expense_type',
        'ppc_credit_ledger', 'ppc_to', 'ppc_customer', 'ppc_vehicle_number', 
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
        tally_date = wpc.ppc_date
        date_str = tally_date.strftime("%d-%m-%Y") if tally_date else ""
        vou_no = wpc.ppc_number or ""
        debit = wpc.ppc_expense_type.pms_exp_type_name if wpc.ppc_expense_type else ""
        credit = wpc.ppc_credit_ledger.ledger_name if wpc.ppc_credit_ledger else ""
        primary_cost_cat = wpc.ppc_unit or ""
        customer = wpc.ppc_customer.cu_name if wpc.ppc_customer else ""
        job_no = wpc.ppc_job_no or ""

        # Lookup vehicle number if available from Gatein or Goods
        veh_no = "N/A(V)"
        if getattr(wpc, "ppc_vehicle_number", None):
            veh_no = wpc.ppc_vehicle_number.pc_vehicle_no
        elif job_no:
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


@csrf_exempt
def add_pms_vehicle(request):
    if request.method == "POST":
        vehicle_num = request.POST.get("vehicle_number", "").strip().upper()
        if not vehicle_num:
            return JsonResponse({"success": False, "error": "Vehicle number cannot be empty."})

        existing = PMSVehicleInfo.objects.filter(pc_vehicle_no__iexact=vehicle_num).first()
        if existing:
            if not existing.pc_is_active:
                existing.pc_is_active = True
                existing.save()
            return JsonResponse({
                "success": True,
                "id": existing.id,
                "vehicle_number": existing.pc_vehicle_no,
                "pc_vehicle_no": existing.pc_vehicle_no,
                "message": "Vehicle already exists."
            })

        new_veh = PMSVehicleInfo.objects.create(pc_vehicle_no=vehicle_num)
        return JsonResponse({
            "success": True,
            "id": new_veh.id,
            "vehicle_number": new_veh.pc_vehicle_no,
            "pc_vehicle_no": new_veh.pc_vehicle_no
        })
    return JsonResponse({"success": False, "error": "Invalid request method."})


@csrf_exempt
def add_pms_expense_type(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if not name:
            return JsonResponse({"success": False, "error": "Expense type name cannot be empty."})

        existing = PMSExpenseTypeInfo.objects.filter(pms_exp_type_name__iexact=name).first()
        if existing:
            if not existing.pms_exp_type_status:
                existing.pms_exp_type_status = True
                existing.save()
            return JsonResponse({
                "success": True,
                "id": existing.id,
                "name": existing.pms_exp_type_name,
                "message": "Expense type already exists."
            })

        from django.db.models import Max
        from django.db import connection
        try:
            new_obj = PMSExpenseTypeInfo.objects.create(pms_exp_type_name=name, pms_exp_type_status=True)
        except Exception:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT setval(pg_get_serial_sequence('sms_app_pmsexpensetypeinfo', 'id'), (SELECT COALESCE(MAX(id), 1) FROM sms_app_pmsexpensetypeinfo));")
                new_obj = PMSExpenseTypeInfo.objects.create(pms_exp_type_name=name, pms_exp_type_status=True)
            except Exception:
                max_id = PMSExpenseTypeInfo.objects.aggregate(Max('id'))['id__max'] or 0
                new_obj = PMSExpenseTypeInfo.objects.create(id=max_id + 1, pms_exp_type_name=name, pms_exp_type_status=True)

        return JsonResponse({
            "success": True,
            "id": new_obj.id,
            "name": new_obj.pms_exp_type_name
        })
    return JsonResponse({"success": False, "error": "Invalid request method."})


def pms_petty_cash_combined_pdf(request, ppc_id):
    ppc = get_object_or_404(PMSPettyCashInfo, pk=ppc_id)
    from ..utils.petty_cash_pdf_utils import generate_petty_cash_combined_pdf
    pdf_bytes = generate_petty_cash_combined_pdf(ppc, pc_type='PMS')
    safe_name = re.sub(r'[\\/*?:"<>|]', '_', ppc.ppc_number or f'PMS_{ppc.id}')
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{safe_name}_combined.pdf"'
    return response


def pms_petty_cash_export_zip(request):
    ppc_number = request.GET.get('ppc_number', "").strip()
    search_date = request.GET.get('search_date', "").strip()
    from_date = request.GET.get('from_date', "").strip()
    to_date = request.GET.get('to_date', "").strip()
    search_unit = request.GET.get('search_unit', "").strip()
    search_branch = request.GET.get('search_branch', "").strip()
    search_user = request.GET.get('search_user', "").strip()

    filters = Q()
    if ppc_number:
        filters &= Q(ppc_number__icontains=ppc_number)
    if search_date:
        filters &= (Q(ppc_date=search_date) | Q(ppc_transaction_date=search_date))
    if from_date:
        filters &= Q(ppc_date__gte=from_date)
    if to_date:
        filters &= Q(ppc_date__lte=to_date)
    if search_unit:
        filters &= Q(ppc_unit__icontains=search_unit)

    is_admin_or_supervisor = is_admin_or_supervisor_user(request)
    if not is_admin_or_supervisor:
        user_branch_code = get_user_branch_code(request)
        if user_branch_code == 'BLR':
            filters &= (Q(ppc_branch__loc_name__icontains='BLR') | Q(ppc_branch__loc_name__icontains='Bangalore') | Q(ppc_branch__loc_name__icontains='Bengaluru'))
        elif user_branch_code == 'MAA':
            filters &= (Q(ppc_branch__loc_name__icontains='MAA') | Q(ppc_branch__loc_name__icontains='Chennai'))
        elif user_branch_code:
            filters &= Q(ppc_branch__loc_name__icontains=user_branch_code)
    else:
        if search_branch:
            if search_branch == 'BLR':
                filters &= (Q(ppc_branch__loc_name__icontains='BLR') | Q(ppc_branch__loc_name__icontains='Bangalore') | Q(ppc_branch__loc_name__icontains='Bengaluru'))
            elif search_branch == 'MAA':
                filters &= (Q(ppc_branch__loc_name__icontains='MAA') | Q(ppc_branch__loc_name__icontains='Chennai'))
            else:
                filters &= Q(ppc_branch__loc_name__icontains=search_branch)
        if search_user:
            filters &= Q(ppc_created_by_id=search_user)

    ppc_list = PMSPettyCashInfo.objects.filter(filters).order_by('-id').select_related(
        'ppc_business', 'ppc_branch', 'ppc_category', 'ppc_expense_type',
        'ppc_credit_ledger', 'ppc_to', 'ppc_customer', 'ppc_vehicle_number',
        'ppc_created_by', 'ppc_updated_by'
    )
    from ..utils.petty_cash_pdf_utils import export_petty_cash_zip
    return export_petty_cash_zip(ppc_list, pc_type='PMS', zip_filename='PMS_Petty_Cash_Attachments.zip')


