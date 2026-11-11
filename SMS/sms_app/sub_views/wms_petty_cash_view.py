import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import JsonResponse, HttpResponse
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

from ..sub_models.wms_petty_cash_mod import WMSPettyCashInfo
from ..sub_models.wms_expense_type_mod import WMSExpenseTypeInfo
from ..sub_models.gatein_mod import Gatein_info
from ..sub_models.credit_ledger_mod import CreditLedgerInfo
from ..models import Business_Sol_info, Location_info, ExpenseCategoryInfo, iou_info, CustomerInfo, Warehouse_goods_info, UnitInfo
from ..sub_forms.wms_petty_cash_form import WMSPettyCashForm
from .general_utils import get_financial_year, get_session_branch_id
from django.views.decorators.csrf import csrf_exempt


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


def generate_wms_petty_cash_number(model_class, field_name, branch_obj=None, voucher_date=None):
    """
    Generates Voucher Number format in UPPERCASE: [BranchCode]-WH-[MM]-[FY]-[Seq]
    strictly based on voucher_date. No fallback date is permitted.
    """
    if not voucher_date:
        raise ValueError("Voucher Date is strictly required to generate WMS voucher number. No fallback date is permitted.")

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

    prefix = f"{branch_code}-WH-{month_str}-{fy_slash}-"

    # fetch all existing numbers for this prefix to get the maximum sequence
    existing_nums = model_class.objects.filter(
        Q(**{f"{field_name}__istartswith": prefix}) | Q(**{f"{field_name}__istartswith": f"{branch_code.title()}-Wh-{month_str}-{fy_slash}-"})
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


def wms_petty_cash_add(request, wpc_id=0):
    initial_data = {}
    if wpc_id == 0:
        # Default Business
        bvm_storage = Business_Sol_info.objects.filter(bvm_business__icontains='Storage').first()
        if bvm_storage:
            initial_data['wpc_business'] = bvm_storage.id

        # Default Expense Category to Cash Expense
        cash_cat = ExpenseCategoryInfo.objects.filter(exp_category_name__icontains='Cash').first()
        if cash_cat:
            initial_data['wpc_category'] = cash_cat.id

        # Default Branch based on session
        branch_id = get_session_branch_id(request)
        if branch_id:
            initial_data['wpc_branch'] = branch_id

            # Default Credit Ledger based on branch name
            branch_obj = Location_info.objects.filter(id=branch_id).first()
            if branch_obj:
                branch_code = branch_obj.loc_name.split()[-1]
                ledger = CreditLedgerInfo.objects.filter(
                    ledger_name__icontains='WH Petty Cash'
                ).filter(
                    ledger_name__icontains=branch_code
                ).exclude(
                    ledger_name__icontains='Admin'
                ).first()
                if not ledger:
                    ledger = CreditLedgerInfo.objects.filter(
                        ledger_name__icontains='WH'
                    ).filter(
                        ledger_name__icontains=branch_code
                    ).first()
                if ledger:
                    initial_data['wpc_credit_ledger'] = ledger.id

        form = WMSPettyCashForm(initial=initial_data, request=request)
    else:
        wpc = get_object_or_404(WMSPettyCashInfo, pk=wpc_id)
        form = WMSPettyCashForm(instance=wpc, request=request)

    if request.method == 'POST':
        post_data = request.POST.copy()

        # Handle 'To Person' text vs User ForeignKey
        if post_data.get('wpc_to'):
            if not str(post_data['wpc_to']).isdigit():
                post_data['wpc_to_manual'] = str(post_data['wpc_to']).strip()
                post_data['wpc_to'] = ''
            else:
                post_data['wpc_to_manual'] = ''
        else:
            post_data['wpc_to_manual'] = ''

        # Auto-calculate amounts in backend
        try:
            bill_amt = float(post_data.get('wpc_bill_amount') or 0.0)
            gst_pct = float(post_data.get('wpc_gst_percentage') or 0.0)
            gst_amt = round((bill_amt * gst_pct) / 100.0, 2)
            total_amt = round(bill_amt + gst_amt, 2)
            post_data['wpc_gst_amount'] = str(gst_amt)
            post_data['wpc_total_amount'] = str(total_amt)
        except Exception:
            pass

        if wpc_id == 0:
            form = WMSPettyCashForm(post_data, request.FILES, request=request)
        else:
            wpc = get_object_or_404(WMSPettyCashInfo, pk=wpc_id)
            form = WMSPettyCashForm(post_data, request.FILES, instance=wpc, request=request)

        if form.is_valid():
            saved_wpc = form.save(commit=False)
            if post_data.get('wpc_bill_attachment-clear') in ['on', '1', 'true']:
                saved_wpc.wpc_bill_attachment = None
            voucher_date = saved_wpc.wpc_date
            if not voucher_date:
                messages.error(request, "Voucher Date is strictly required to generate voucher number.")
                return render(request, "asset_mgt_app/wms_petty_cash_add.html", context)

            expected_branch_code = "MAA"
            if saved_wpc.wpc_branch and saved_wpc.wpc_branch.loc_name:
                loc_upper = saved_wpc.wpc_branch.loc_name.upper()
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
                    expected_branch_code = saved_wpc.wpc_branch.loc_name.split()[-1].upper()

            v_fy = get_financial_year(voucher_date).replace('-', '/')
            v_month = f"{voucher_date.month:02d}"
            expected_prefix = f"{expected_branch_code}-WH-{v_month}-{v_fy}-"

            created_user = request.user if (request.user and request.user.is_authenticated) else None
            if not created_user and request.session.get('ses_userID'):
                from django.contrib.auth.models import User
                try:
                    created_user = User.objects.get(id=request.session['ses_userID'])
                except User.DoesNotExist:
                    pass

            if wpc_id == 0:
                saved_wpc.wpc_number = generate_wms_petty_cash_number(WMSPettyCashInfo, 'wpc_number', saved_wpc.wpc_branch, voucher_date=voucher_date)
                saved_wpc.wpc_created_by = created_user
            else:
                if not saved_wpc.wpc_number or not saved_wpc.wpc_number.upper().startswith(expected_prefix):
                    saved_wpc.wpc_number = generate_wms_petty_cash_number(WMSPettyCashInfo, 'wpc_number', saved_wpc.wpc_branch, voucher_date=voucher_date)
                if not saved_wpc.wpc_created_by and created_user:
                    saved_wpc.wpc_created_by = created_user
            saved_wpc.wpc_updated_by = created_user
            saved_wpc.save()
            messages.success(request, "WMS Petty Cash saved successfully.")
            return redirect('wms_petty_cash_list')
        else:
            messages.error(request, "Please correct the errors below.")

    import os
    bill_filename = ""
    if form.instance and form.instance.wpc_bill_attachment:
        bill_filename = os.path.basename(form.instance.wpc_bill_attachment.name)

    context = {
        'form': form,
        'wpc_id': wpc_id,
        'bill_filename': bill_filename,
    }
    return render(request, "asset_mgt_app/wms_petty_cash_add.html", context)


def wms_petty_cash_list(request):
    wpc_number = request.GET.get('wpc_number', "").strip()
    search_date = request.GET.get('search_date', "").strip()
    from_date = request.GET.get('from_date', "").strip()
    to_date = request.GET.get('to_date', "").strip()
    search_unit = request.GET.get('search_unit', "").strip()
    search_branch = request.GET.get('search_branch', "").strip()

    filters = Q()
    if wpc_number:
        filters &= Q(wpc_number__icontains=wpc_number)
    if search_date:
        filters &= Q(wpc_date=search_date)
    if from_date:
        filters &= Q(wpc_date__gte=from_date)
    if to_date:
        filters &= Q(wpc_date__lte=to_date)
    if search_unit:
        filters &= Q(wpc_unit__icontains=search_unit)

    search_user = request.GET.get('search_user', "").strip()

    is_admin_or_supervisor = is_admin_or_supervisor_user(request)

    if not is_admin_or_supervisor:
        user_branch_code = get_user_branch_code(request)
        if user_branch_code == 'BLR':
            filters &= (Q(wpc_branch__loc_name__icontains='BLR') | Q(wpc_branch__loc_name__icontains='Bangalore') | Q(wpc_branch__loc_name__icontains='Bengaluru'))
        elif user_branch_code == 'MAA':
            filters &= (Q(wpc_branch__loc_name__icontains='MAA') | Q(wpc_branch__loc_name__icontains='Chennai'))
        elif user_branch_code:
            filters &= Q(wpc_branch__loc_name__icontains=user_branch_code)
    else:
        if search_branch:
            if search_branch == 'BLR':
                filters &= (Q(wpc_branch__loc_name__icontains='BLR') | Q(wpc_branch__loc_name__icontains='Bangalore') | Q(wpc_branch__loc_name__icontains='Bengaluru'))
            elif search_branch == 'MAA':
                filters &= (Q(wpc_branch__loc_name__icontains='MAA') | Q(wpc_branch__loc_name__icontains='Chennai'))
            else:
                filters &= Q(wpc_branch__loc_name__icontains=search_branch)
        if search_user:
            filters &= Q(wpc_created_by_id=search_user)

    wpc_list = WMSPettyCashInfo.objects.filter(filters).select_related(
        'wpc_business', 'wpc_branch', 'wpc_category', 'wpc_expense_type',
        'wpc_credit_ledger', 'wpc_to', 'wpc_customer', 'wpc_business_model',
        'wpc_created_by', 'wpc_updated_by'
    ).order_by('-id')

    paginator = Paginator(wpc_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    from ..sub_models.wms_petty_cash_mod import UNIT_CHOICES
    unit_list = [choice[0] for choice in UNIT_CHOICES]

    user_list = []
    if is_admin_or_supervisor:
        from django.contrib.auth.models import User
        creator_ids = WMSPettyCashInfo.objects.filter(wpc_created_by__isnull=False).values_list('wpc_created_by_id', flat=True).distinct()
        user_list = User.objects.filter(id__in=creator_ids).order_by('first_name', 'username')

    context = {
        'wpc_list': wpc_list,
        'page_obj': page_obj,
        'search_wpc_number': wpc_number,
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
    return render(request, "asset_mgt_app/wms_petty_cash_list.html", context)


def wms_petty_cash_delete(request, wpc_id):
    wpc = get_object_or_404(WMSPettyCashInfo, pk=wpc_id)
    wpc.delete()
    messages.success(request, "WMS Petty Cash deleted successfully.")
    return redirect('wms_petty_cash_list')


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


def wms_petty_cash_voucher_print(request, wpc_id):
    wpc = get_object_or_404(WMSPettyCashInfo, pk=wpc_id)
    total_val = wpc.wpc_total_amount if (wpc.wpc_total_amount and wpc.wpc_total_amount > 0) else (wpc.wpc_bill_amount or 0)
    amount_in_words = number_to_words(total_val)

    # Determine the 'Payment to' value based on available fields
    payment_to = ''
    if wpc.wpc_to_manual:
        payment_to = wpc.wpc_to_manual
    elif wpc.wpc_to:
        payment_to = wpc.wpc_to.first_name or wpc.wpc_to.username

    # Clean remarks for printing
    clean_remarks = wpc.wpc_remarks or ''
    if 'Auto-generated' in clean_remarks:
        clean_remarks = re.sub(r'\s*\[?Auto-generated.*', '', clean_remarks).strip()

    context = {
        'wpc': wpc,
        'amount_in_words': amount_in_words,
        'payment_to': payment_to,
        'clean_remarks': clean_remarks,
    }
    return render(request, 'asset_mgt_app/wms_petty_cash_voucher.html', context)


def get_wms_customers_by_unit(request):
    """
    Fetch distinct customers for the selected Unit from Warehouse_goods_info.
    If unit is empty or has no specific customers, return all active storage customers.
    """
    unit_name = request.GET.get('unit', '').strip()
    customers_data = []

    if unit_name:
        cust_ids = Warehouse_goods_info.objects.filter(
            wh_unit__unit_name__iexact=unit_name,
            wh_customer_name__isnull=False
        ).values_list('wh_customer_name_id', flat=True).distinct()

        if cust_ids:
            customers = CustomerInfo.objects.filter(id__in=cust_ids).order_by('cu_name')
            customers_data = [{'id': c.id, 'name': c.cu_name} for c in customers]

    # If no customers found specifically for unit, fallback to all storage customers
    if not customers_data:
        customers = CustomerInfo.objects.filter(cu_business_sol__bvm_business__icontains='Storage').order_by('cu_name')
        if not customers.exists():
            customers = CustomerInfo.objects.all().order_by('cu_name')
        customers_data = [{'id': c.id, 'name': c.cu_name} for c in customers]

    return JsonResponse({'status': 'success', 'customers': customers_data})


def get_wms_jobs_by_customer(request):
    """
    Fetch distinct Job Numbers for the selected Unit and Customer from Warehouse_goods_info and Gatein_info.
    """
    unit_name = request.GET.get('unit', '').strip()
    customer_id = request.GET.get('customer_id', '').strip()

    if not customer_id:
        return JsonResponse({'status': 'success', 'jobs': []})

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


def get_wms_job_details(request):
    """
    AJAX endpoint to fetch full warehouse job details from Warehouse_goods_info / Gatein_info
    """
    job_no = request.GET.get('job_no', '').strip()
    if not job_no:
        return JsonResponse({'status': 'error', 'message': 'No job number provided'})

    # 1. First check Warehouse_goods_info
    wh_good = Warehouse_goods_info.objects.filter(
        wh_job_no__iexact=job_no
    ).select_related('wh_customer_name', 'wh_customer_type', 'wh_unit', 'wh_branch').first()

    # Also lookup gatein for truck/driver if available
    gatein = Gatein_info.objects.filter(gatein_job_no__iexact=job_no).first()

    if wh_good:
        checkin_date_str = wh_good.wh_checkin_time.strftime("%d-%m-%Y") if wh_good.wh_checkin_time else (gatein.gatein_arrival_date.strftime("%d-%m-%Y") if gatein and gatein.gatein_arrival_date else "")
        return JsonResponse({
            'status': 'success',
            'job_no': wh_good.wh_job_no,
            'customer_id': wh_good.wh_customer_name.id if wh_good.wh_customer_name else None,
            'customer_name': wh_good.wh_customer_name.cu_name if wh_good.wh_customer_name else '',
            'business_model_id': wh_good.wh_customer_type.id if wh_good.wh_customer_type else None,
            'business_model_name': wh_good.wh_customer_type.tb_trbusinesstype if wh_good.wh_customer_type else '',
            'unit_name': wh_good.wh_unit.unit_name if wh_good.wh_unit else '',
            'invoice_no': wh_good.wh_goods_invoice or (gatein.gatein_invoice if gatein else ''),
            'truck_no': gatein.gatein_truck_number if gatein else (wh_good.wh_truck_type.veh_type_name if wh_good.wh_truck_type else ''),
            'driver_name': gatein.gatein_driver if gatein else '',
            'shipper': wh_good.wh_consigner or (gatein.gatein_shipper if gatein else ''),
            'consignee': wh_good.wh_consignee or (gatein.gatein_consignee if gatein else ''),
            'qty': wh_good.wh_total_qty or (gatein.gatein_no_of_pkg if gatein else 0),
            'weight': wh_good.wh_gross_weight or (gatein.gatein_actual_weight if gatein else 0.0),
            'cbm': wh_good.wh_cbm or 0.0,
            'date': checkin_date_str,
            'invoice_amount': wh_good.wh_invoice_amount_inr or wh_good.wh_invoice_value or 0.0,
            'handling_cost': wh_good.wh_handling_cost or 0.0,
            'loading_cost': wh_good.wh_total_loading_cost or wh_good.wh_unloading_cost or 0.0,
            'storage_cost': wh_good.wh_storage_cost_total or 0.0,
            'total_cost': wh_good.wh_total_invoice_cost or 0.0,
        })

    # 2. Fallback to Gatein_info
    gatein = Gatein_info.objects.filter(
        Q(gatein_job_no__iexact=job_no) | Q(gatein_invoice__iexact=job_no)
    ).select_related('gatein_customer', 'gatein_customer_type').first()

    if gatein:
        arrival_date_str = gatein.gatein_arrival_date.strftime("%d-%m-%Y") if gatein.gatein_arrival_date else ""
        return JsonResponse({
            'status': 'success',
            'job_no': gatein.gatein_job_no,
            'customer_id': gatein.gatein_customer.id if gatein.gatein_customer else None,
            'customer_name': gatein.gatein_customer.cu_name if gatein.gatein_customer else '',
            'business_model_id': gatein.gatein_customer_type.id if gatein.gatein_customer_type else None,
            'business_model_name': gatein.gatein_customer_type.tb_trbusinesstype if gatein.gatein_customer_type else '',
            'unit_name': '',
            'invoice_no': gatein.gatein_invoice or '',
            'truck_no': gatein.gatein_truck_number or '',
            'driver_name': gatein.gatein_driver or '',
            'shipper': gatein.gatein_shipper or '',
            'consignee': gatein.gatein_consignee or '',
            'qty': gatein.gatein_no_of_pkg or 0,
            'weight': gatein.gatein_actual_weight or 0.0,
            'cbm': 0.0,
            'date': arrival_date_str,
            'invoice_amount': 0.0,
            'handling_cost': 0.0,
            'loading_cost': 0.0,
            'storage_cost': 0.0,
            'total_cost': 0.0,
        })
    else:
        return JsonResponse({'status': 'not_found', 'message': 'Job number not found'})



def wms_petty_cash_export_tally(request):
    wpc_number = request.GET.get('wpc_number', "").strip()
    search_date = request.GET.get('search_date', "").strip()
    from_date = request.GET.get('from_date', "").strip()
    to_date = request.GET.get('to_date', "").strip()
    search_unit = request.GET.get('search_unit', "").strip()
    search_branch = request.GET.get('search_branch', "").strip()

    filters = Q()
    if wpc_number:
        filters &= Q(wpc_number__icontains=wpc_number)
    if search_date:
        filters &= Q(wpc_date=search_date)
    if from_date:
        filters &= Q(wpc_date__gte=from_date)
    if to_date:
        filters &= Q(wpc_date__lte=to_date)
    if search_unit:
        filters &= Q(wpc_unit__icontains=search_unit)

    search_user = request.GET.get('search_user', "").strip()

    is_admin_or_supervisor = is_admin_or_supervisor_user(request)

    if not is_admin_or_supervisor:
        user_branch_code = get_user_branch_code(request)
        if user_branch_code == 'BLR':
            filters &= (Q(wpc_branch__loc_name__icontains='BLR') | Q(wpc_branch__loc_name__icontains='Bangalore') | Q(wpc_branch__loc_name__icontains='Bengaluru'))
        elif user_branch_code == 'MAA':
            filters &= (Q(wpc_branch__loc_name__icontains='MAA') | Q(wpc_branch__loc_name__icontains='Chennai'))
        elif user_branch_code:
            filters &= Q(wpc_branch__loc_name__icontains=user_branch_code)
    else:
        if search_branch:
            if search_branch == 'BLR':
                filters &= (Q(wpc_branch__loc_name__icontains='BLR') | Q(wpc_branch__loc_name__icontains='Bangalore') | Q(wpc_branch__loc_name__icontains='Bengaluru'))
            elif search_branch == 'MAA':
                filters &= (Q(wpc_branch__loc_name__icontains='MAA') | Q(wpc_branch__loc_name__icontains='Chennai'))
            else:
                filters &= Q(wpc_branch__loc_name__icontains=search_branch)
        if search_user:
            filters &= Q(wpc_created_by_id=search_user)

    wpc_list = WMSPettyCashInfo.objects.filter(filters).select_related(
        'wpc_business', 'wpc_branch', 'wpc_category', 'wpc_expense_type',
        'wpc_credit_ledger', 'wpc_to', 'wpc_customer', 'wpc_business_model',
        'wpc_created_by'
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

    for wpc in wpc_list:
        tally_date = wpc.wpc_date
        date_str = tally_date.strftime("%d-%m-%Y") if tally_date else ""
        vou_no = wpc.wpc_number or ""
        debit = wpc.wpc_expense_type.wms_exp_type_name if wpc.wpc_expense_type else ""
        credit = wpc.wpc_credit_ledger.ledger_name if wpc.wpc_credit_ledger else ""
        primary_cost_cat = wpc.wpc_unit or ""
        customer = wpc.wpc_customer.cu_name if wpc.wpc_customer else ""
        job_no = wpc.wpc_job_no or ""

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

        amount = wpc.wpc_total_amount or wpc.wpc_bill_amount or 0.0
        to_person = wpc.wpc_to.first_name if wpc.wpc_to else (wpc.wpc_to_manual or "")
        trn_date = wpc.wpc_transaction_date.strftime("%d-%b") if wpc.wpc_transaction_date else ""
        remarks = wpc.wpc_remarks or ""

        ws.append([
            date_str, vou_no, debit, credit, primary_cost_cat,
            customer, job_no, veh_no, amount, to_person, trn_date, remarks
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="WMS_Petty_Cash_Tally_Export.xlsx"'
    wb.save(response)
    return response


@csrf_exempt
def add_wms_expense_type(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if not name:
            return JsonResponse({"success": False, "error": "Expense type name cannot be empty."})

        existing = WMSExpenseTypeInfo.objects.filter(wms_exp_type_name__iexact=name).first()
        if existing:
            if not existing.wms_exp_type_status:
                existing.wms_exp_type_status = True
                existing.save()
            return JsonResponse({
                "success": True,
                "id": existing.id,
                "name": existing.wms_exp_type_name,
                "message": "Expense type already exists."
            })

        from django.db.models import Max
        from django.db import connection
        try:
            new_obj = WMSExpenseTypeInfo.objects.create(wms_exp_type_name=name, wms_exp_type_status=True)
        except Exception:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT setval(pg_get_serial_sequence('sms_app_wmsexpensetypeinfo', 'id'), (SELECT COALESCE(MAX(id), 1) FROM sms_app_wmsexpensetypeinfo));")
                new_obj = WMSExpenseTypeInfo.objects.create(wms_exp_type_name=name, wms_exp_type_status=True)
            except Exception:
                max_id = WMSExpenseTypeInfo.objects.aggregate(Max('id'))['id__max'] or 0
                new_obj = WMSExpenseTypeInfo.objects.create(id=max_id + 1, wms_exp_type_name=name, wms_exp_type_status=True)

        return JsonResponse({
            "success": True,
            "id": new_obj.id,
            "name": new_obj.wms_exp_type_name
        })
    return JsonResponse({"success": False, "error": "Invalid request method."})


def wms_petty_cash_combined_pdf(request, wpc_id):
    wpc = get_object_or_404(WMSPettyCashInfo, pk=wpc_id)
    from ..utils.petty_cash_pdf_utils import generate_petty_cash_combined_pdf
    pdf_bytes = generate_petty_cash_combined_pdf(wpc, pc_type='WMS')
    safe_name = re.sub(r'[\\/*?:"<>|]', '_', wpc.wpc_number or f'WMS_{wpc.id}')
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{safe_name}_combined.pdf"'
    return response


def wms_petty_cash_export_zip(request):
    wpc_number = request.GET.get('wpc_number', "").strip()
    search_date = request.GET.get('search_date', "").strip()
    from_date = request.GET.get('from_date', "").strip()
    to_date = request.GET.get('to_date', "").strip()
    search_unit = request.GET.get('search_unit', "").strip()
    search_branch = request.GET.get('search_branch', "").strip()

    filters = Q()
    if wpc_number:
        filters &= Q(wpc_number__icontains=wpc_number)
    if search_date:
        filters &= Q(wpc_transaction_date=search_date)
    if from_date:
        filters &= Q(wpc_date__gte=from_date)
    if to_date:
        filters &= Q(wpc_date__lte=to_date)
    if search_unit:
        filters &= Q(wpc_unit__icontains=search_unit)

    is_admin_or_supervisor = is_admin_or_supervisor_user(request)
    if not is_admin_or_supervisor:
        user_branch = get_user_branch_code(request)
        if user_branch:
            filters &= (Q(wpc_branch__loc_name__icontains=user_branch) | Q(wpc_number__istartswith=f"{user_branch}-"))
    else:
        if search_branch:
            filters &= (Q(wpc_branch__loc_name__icontains=search_branch) | Q(wpc_number__istartswith=f"{search_branch}-"))

    wpc_list = WMSPettyCashInfo.objects.filter(filters).order_by('-id').select_related(
        'wpc_business', 'wpc_branch', 'wpc_category', 'wpc_expense_type',
        'wpc_credit_ledger', 'wpc_to', 'wpc_customer', 'wpc_created_by', 'wpc_updated_by'
    )
    from ..utils.petty_cash_pdf_utils import export_petty_cash_zip
    return export_petty_cash_zip(wpc_list, pc_type='WMS', zip_filename='WMS_Petty_Cash_Attachments.zip')


