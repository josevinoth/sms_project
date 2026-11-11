import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from datetime import datetime
from django.utils import timezone
from ..sub_models.tms_petty_cash_mod import TMSPettyCashInfo
from ..sub_models.tms_expense_type_mod import TMSExpenseTypeInfo
from ..sub_models.tripdetail_mod import TripdetailInfo
from ..sub_models.credit_ledger_mod import CreditLedgerInfo
from ..models import Business_Sol_info, Location_info
from ..sub_forms.tms_petty_cash_form import TMSPettyCashForm
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


def generate_tms_petty_cash_number(model_class, field_name, branch_obj=None, voucher_date=None):
    """
    Generates [BranchCode]_T_26-27_yy_xxx strictly based on voucher_date.
    No fallback date is permitted.
    """
    if not voucher_date:
        raise ValueError("Voucher Date is strictly required to generate TMS voucher number. No fallback date is permitted.")

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

    fy = get_financial_year(v_date) # returns e.g. "26-27"
    month_str = f"{v_date.month:02d}"
    
    branch_prefix = "M"
    if branch_obj and branch_obj.loc_name:
        loc_name_lower = branch_obj.loc_name.lower()
        if "blr" in loc_name_lower or "bengaluru" in loc_name_lower or "bangalore" in loc_name_lower:
            branch_prefix = "B"
            
    prefix = f"{branch_prefix}_T_{fy}_{month_str}_"
    
    # fetch all existing numbers with this prefix to get the maximum sequence
    existing_nums = model_class.objects.filter(**{f"{field_name}__startswith": prefix}).values_list(field_name, flat=True)
    max_seq = 0
    for num_str in existing_nums:
        if num_str:
            try:
                seq = int(num_str.split('_')[-1])
                if seq > max_seq:
                    max_seq = seq
            except (ValueError, IndexError):
                pass
    new_seq = max_seq + 1
    new_num = f"{prefix}{str(new_seq).zfill(3)}"

    while model_class.objects.filter(**{field_name: new_num}).exists():
        new_seq += 1
        new_num = f"{prefix}{str(new_seq).zfill(3)}"

    return new_num

def tms_petty_cash_add(request, tpc_id=0):
    initial_data = {}
    if tpc_id == 0:
        # Default Business
        bvm_trans = Business_Sol_info.objects.filter(bvm_business__icontains='bvm trans solutions').first()
        if bvm_trans:
            initial_data['tpc_business'] = bvm_trans.id
            
        # Default Expense Category to Cash Expense
        from ..models import ExpenseCategoryInfo
        cash_cat = ExpenseCategoryInfo.objects.filter(exp_category_name__icontains='Cash').first()
        if cash_cat:
            initial_data['tpc_category'] = cash_cat.id

        # Default Branch based on session
        branch_id = get_session_branch_id(request)
        if branch_id:
            initial_data['tpc_branch'] = branch_id
            
            # Default Credit Ledger based on branch name
            branch_obj = Location_info.objects.filter(id=branch_id).first()
            if branch_obj:
                branch_code = branch_obj.loc_name.split()[-1] # e.g. "MAA" or "BLR"
                ledger = CreditLedgerInfo.objects.filter(
                    ledger_name__icontains='Trans Petty Cash'
                ).filter(
                    ledger_name__icontains=branch_code
                ).exclude(
                    ledger_name__icontains='Admin'
                ).first()
                if not ledger:
                    ledger = CreditLedgerInfo.objects.filter(
                        ledger_name__icontains='Trans'
                    ).filter(
                        ledger_name__icontains=branch_code
                    ).first()
                if ledger:
                    initial_data['tpc_credit_ledger'] = ledger.id
                    
        form = TMSPettyCashForm(initial=initial_data, request=request)
    else:
        tpc = get_object_or_404(TMSPettyCashInfo, pk=tpc_id)
        form = TMSPettyCashForm(instance=tpc, request=request)
        
    if request.method == 'POST':
        post_data = request.POST.copy()
        
        # Handle vehicle number: if selected from master (digit), link to master.
        # If entered manually or from a trip where vehicle is not in master,
        # DO NOT add to Vehicle Master; store in tpc_vehicle_number_manual.
        if post_data.get('tpc_vehicle_number'):
            veh_input = str(post_data['tpc_vehicle_number']).strip()
            if not veh_input.isdigit():
                from ..models import VehiclemasterInfo
                veh = VehiclemasterInfo.objects.filter(vm_registrationnumber__iexact=veh_input).first()
                if veh:
                    post_data['tpc_vehicle_number'] = str(veh.id)
                    post_data['tpc_vehicle_number_manual'] = ''
                else:
                    post_data['tpc_vehicle_number'] = ''
                    post_data['tpc_vehicle_number_manual'] = veh_input.upper()
            else:
                post_data['tpc_vehicle_number_manual'] = ''
        else:
            post_data['tpc_vehicle_number_manual'] = ''

        # Handle driver name: if selected from master (digit), link to master.
        # If entered manually, DO NOT add to Driver Master; store in tpc_driver_name_manual.
        if post_data.get('tpc_driver_name'):
            drv_input = str(post_data['tpc_driver_name']).strip()
            if not drv_input.isdigit():
                from ..models import DrivermasterInfo
                drv = DrivermasterInfo.objects.filter(dm_name__iexact=drv_input).first()
                if drv:
                    post_data['tpc_driver_name'] = str(drv.id)
                    post_data['tpc_driver_name_manual'] = ''
                else:
                    post_data['tpc_driver_name'] = ''
                    post_data['tpc_driver_name_manual'] = drv_input
            else:
                post_data['tpc_driver_name_manual'] = ''
        else:
            post_data['tpc_driver_name_manual'] = ''

        if post_data.get('tpc_to'):
            if not str(post_data['tpc_to']).isdigit():
                post_data['tpc_to_manual'] = str(post_data['tpc_to']).strip()
                post_data['tpc_to'] = ''
            else:
                post_data['tpc_to_manual'] = ''
        else:
            post_data['tpc_to_manual'] = ''

        if tpc_id == 0:
            form = TMSPettyCashForm(post_data, request=request)
        else:
            tpc = get_object_or_404(TMSPettyCashInfo, pk=tpc_id)
            form = TMSPettyCashForm(post_data, instance=tpc, request=request)
            
        from_location = ""
        to_location = ""
        job_lookup = post_data.get('tpc_job_no') if tpc_id == 0 else tpc.tpc_job_no
        if job_lookup:
            trip = TripdetailInfo.objects.filter(
                Q(tr_consignmentnumber__co_consignmentnumber=job_lookup) | 
                Q(tr_tripnumber=job_lookup)
            ).first()
            if trip:
                from_location = trip.tr_departedlocation.place_name if trip.tr_departedlocation else ""
                to_location = trip.tr_reportedlocation.place_name if trip.tr_reportedlocation else ""

        context = {
            'form': form,
            'tpc_id': tpc_id,
            'from_location': from_location,
            'to_location': to_location,
        }

        if form.is_valid():
            saved_tpc = form.save(commit=False)
            voucher_date = saved_tpc.tpc_transaction_date
            if not voucher_date:
                messages.error(request, "Voucher Date is strictly required to generate voucher number.")
                return render(request, "asset_mgt_app/tms_petty_cash_add.html", context)

            branch_prefix = "M"
            if saved_tpc.tpc_branch and saved_tpc.tpc_branch.loc_name:
                loc_lower = saved_tpc.tpc_branch.loc_name.lower()
                if "blr" in loc_lower or "bengaluru" in loc_lower or "bangalore" in loc_lower:
                    branch_prefix = "B"

            v_fy = get_financial_year(voucher_date)
            v_month = f"{voucher_date.month:02d}"
            expected_prefix = f"{branch_prefix}_T_{v_fy}_{v_month}_"

            created_user = request.user if (request.user and request.user.is_authenticated) else None
            if not created_user and request.session.get('ses_userID'):
                from django.contrib.auth.models import User
                try:
                    created_user = User.objects.get(id=request.session['ses_userID'])
                except User.DoesNotExist:
                    pass

            if tpc_id == 0:
                saved_tpc.tpc_number = generate_tms_petty_cash_number(TMSPettyCashInfo, 'tpc_number', saved_tpc.tpc_branch, voucher_date=voucher_date)
                saved_tpc.tpc_created_by = created_user
            else:
                if not saved_tpc.tpc_number or not saved_tpc.tpc_number.startswith(expected_prefix):
                    saved_tpc.tpc_number = generate_tms_petty_cash_number(TMSPettyCashInfo, 'tpc_number', saved_tpc.tpc_branch, voucher_date=voucher_date)
                if not saved_tpc.tpc_created_by and created_user:
                    saved_tpc.tpc_created_by = created_user
            saved_tpc.tpc_updated_by = created_user
            saved_tpc.save()
            messages.success(request, "Petty Cash saved successfully.")
            return redirect('tms_petty_cash_list')
        else:
            messages.error(request, "Please correct the errors below.")
            
    else:
        from_location = ""
        to_location = ""
        if tpc_id != 0:
            trip = TripdetailInfo.objects.filter(
                Q(tr_consignmentnumber__co_consignmentnumber=tpc.tpc_job_no) | 
                Q(tr_tripnumber=tpc.tpc_job_no)
            ).first()
            if trip:
                from_location = trip.tr_departedlocation.place_name if trip.tr_departedlocation else ""
                to_location = trip.tr_reportedlocation.place_name if trip.tr_reportedlocation else ""

        context = {
            'form': form,
            'tpc_id': tpc_id,
            'from_location': from_location,
            'to_location': to_location,
        }
    return render(request, "asset_mgt_app/tms_petty_cash_add.html", context)


def tms_petty_cash_list(request):
    tpc_number = request.GET.get('tpc_number', "").strip()
    search_date = request.GET.get('search_date', "").strip()
    from_date = request.GET.get('from_date', "").strip()
    to_date = request.GET.get('to_date', "").strip()
    search_vehicle = request.GET.get('search_vehicle', "").strip()
    search_branch = request.GET.get('search_branch', "").strip()
    search_user = request.GET.get('search_user', "").strip()
    
    filters = Q()
    if tpc_number:
        filters &= Q(tpc_number__icontains=tpc_number)
    if search_date:
        filters &= Q(tpc_trip_date=search_date)
    if from_date:
        filters &= Q(tpc_transaction_date__gte=from_date)
    if to_date:
        filters &= Q(tpc_transaction_date__lte=to_date)
    if search_vehicle:
        filters &= (Q(tpc_vehicle_number__vm_registrationnumber__icontains=search_vehicle) | Q(tpc_vehicle_number_manual__icontains=search_vehicle))
        
    is_admin_or_supervisor = is_admin_or_supervisor_user(request)

    if not is_admin_or_supervisor:
        user_branch_code = get_user_branch_code(request)
        if user_branch_code == 'BLR':
            filters &= (Q(tpc_branch__loc_name__icontains='BLR') | Q(tpc_branch__loc_name__icontains='Bangalore') | Q(tpc_branch__loc_name__icontains='Bengaluru'))
        elif user_branch_code == 'MAA':
            filters &= (Q(tpc_branch__loc_name__icontains='MAA') | Q(tpc_branch__loc_name__icontains='Chennai'))
        elif user_branch_code:
            filters &= Q(tpc_branch__loc_name__icontains=user_branch_code)
    else:
        if search_branch:
            if search_branch == 'BLR':
                filters &= (Q(tpc_branch__loc_name__icontains='BLR') | Q(tpc_branch__loc_name__icontains='Bangalore') | Q(tpc_branch__loc_name__icontains='Bengaluru'))
            elif search_branch == 'MAA':
                filters &= (Q(tpc_branch__loc_name__icontains='MAA') | Q(tpc_branch__loc_name__icontains='Chennai'))
            else:
                filters &= Q(tpc_branch__loc_name__icontains=search_branch)
        if search_user:
            filters &= Q(tpc_created_by_id=search_user)
            
    tpc_list = TMSPettyCashInfo.objects.filter(filters).select_related(
        'tpc_business', 'tpc_branch', 'tpc_vehicle_number', 'tpc_created_by', 'tpc_updated_by'
    ).order_by('-id')

    if request.GET.get('draw'):
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '').strip()
        
        records_total = tpc_list.count()
        
        if search_value:
            search_filters = (
                Q(tpc_number__icontains=search_value) |
                Q(tpc_business__bvm_business__icontains=search_value) |
                Q(tpc_branch__loc_name__icontains=search_value) |
                Q(tpc_vehicle_number__vm_registrationnumber__icontains=search_value) |
                Q(tpc_vehicle_number_manual__icontains=search_value) |
                Q(tpc_created_by__first_name__icontains=search_value) |
                Q(tpc_created_by__username__icontains=search_value)
            )
            tpc_list = tpc_list.filter(search_filters)

        # Check column-specific searches from header inputs
        for col_idx in range(13):
            col_search = request.GET.get(f'columns[{col_idx}][search][value]', '').strip()
            if col_search:
                if col_idx == 1:
                    tpc_list = tpc_list.filter(tpc_number__icontains=col_search)
                elif col_idx == 2:
                    tpc_list = tpc_list.filter(tpc_transaction_date__icontains=col_search)
                elif col_idx == 3:
                    tpc_list = tpc_list.filter(tpc_business__bvm_business__icontains=col_search)
                elif col_idx == 4:
                    tpc_list = tpc_list.filter(tpc_branch__loc_name__icontains=col_search)
                elif col_idx == 5:
                    try:
                        amt_val = float(col_search)
                        tpc_list = tpc_list.filter(tpc_amount=amt_val)
                    except ValueError:
                        tpc_list = tpc_list.filter(tpc_amount__icontains=col_search)
                elif col_idx == 6:
                    matching_trips = TripdetailInfo.objects.filter(
                        Q(tr_departedlocation__place_name__icontains=col_search) |
                        Q(tr_reportedlocation__place_name__icontains=col_search)
                    ).values_list('tr_consignmentnumber__co_consignmentnumber', 'tr_tripnumber')
                    trip_numbers = set()
                    for c_no, t_no in matching_trips:
                        if c_no: trip_numbers.add(c_no)
                        if t_no: trip_numbers.add(t_no)
                    tpc_list = tpc_list.filter(Q(tpc_job_no__icontains=col_search) | Q(tpc_job_no__in=trip_numbers))
                elif col_idx == 7:
                    tpc_list = tpc_list.filter(
                        Q(tpc_vehicle_number__vm_registrationnumber__icontains=col_search) |
                        Q(tpc_vehicle_number_manual__icontains=col_search)
                    )
                elif col_idx == 8:
                    tpc_list = tpc_list.filter(tpc_created_on__icontains=col_search)
                elif col_idx == 9:
                    tpc_list = tpc_list.filter(
                        Q(tpc_created_by__first_name__icontains=col_search) |
                        Q(tpc_created_by__username__icontains=col_search)
                    )
                elif col_idx == 10:
                    tpc_list = tpc_list.filter(
                        Q(tpc_updated_by__first_name__icontains=col_search) |
                        Q(tpc_updated_by__username__icontains=col_search)
                    )
                elif col_idx == 11:
                    tpc_list = tpc_list.filter(tpc_updated_at__icontains=col_search)
            
        records_filtered = tpc_list.count()
        
        if length > 0:
            tpc_page = tpc_list[start:start+length]
        else:
            tpc_page = tpc_list
            
        data = []
        for i, tpc in enumerate(tpc_page):
            from_to_location = ""
            if tpc.tpc_job_no:
                try:
                    trip = TripdetailInfo.objects.filter(
                        Q(tr_consignmentnumber__co_consignmentnumber=tpc.tpc_job_no) | 
                        Q(tr_tripnumber=tpc.tpc_job_no)
                    ).first()
                    if trip:
                        fr = trip.tr_departedlocation.place_name if trip.tr_departedlocation else ""
                        to = trip.tr_reportedlocation.place_name if trip.tr_reportedlocation else ""
                        if fr or to:
                            from_to_location = f"{fr} - {to}"
                except Exception:
                    pass
            
            created_by = tpc.tpc_created_by.first_name if tpc.tpc_created_by and tpc.tpc_created_by.first_name else (tpc.tpc_created_by.username if tpc.tpc_created_by else "-")
            updated_by = tpc.tpc_updated_by.first_name if tpc.tpc_updated_by and tpc.tpc_updated_by.first_name else (tpc.tpc_updated_by.username if tpc.tpc_updated_by else "-")
            veh_no = tpc.tpc_vehicle_number.vm_registrationnumber if tpc.tpc_vehicle_number else (tpc.tpc_vehicle_number_manual or "")
            if not veh_no and tpc.tpc_job_no:
                try:
                    trip_obj = TripdetailInfo.objects.filter(
                        Q(tr_consignmentnumber__co_consignmentnumber=tpc.tpc_job_no) | 
                        Q(tr_tripnumber=tpc.tpc_job_no)
                    ).first()
                    if trip_obj and trip_obj.tr_vehiclenumber:
                        veh_no = trip_obj.tr_vehiclenumber
                except Exception:
                    pass
            
            edit_url = f"/SMS/petty_cash_insert/{tpc.id}/"
            if tpc.tpc_source_driver_expense_id:
                edit_url = f"/SMS/driver_expense_add/{tpc.tpc_source_driver_expense_id}/"
            elif tpc.tpc_remarks and "Auto-generated from Driver Settlement Expense ID: " in tpc.tpc_remarks:
                try:
                    driver_expense_id = int(tpc.tpc_remarks.split("Auto-generated from Driver Settlement Expense ID: ")[1].strip())
                    edit_url = f"/SMS/driver_expense_add/{driver_expense_id}/"
                except ValueError:
                    pass

            row = [
                start + i + 1,
                tpc.tpc_number or "",
                tpc.tpc_transaction_date.strftime("%Y-%m-%d") if tpc.tpc_transaction_date else "",
                tpc.tpc_business.bvm_business if tpc.tpc_business else "",
                tpc.tpc_branch.loc_name if tpc.tpc_branch else "",
                str(tpc.tpc_amount) if tpc.tpc_amount else "0.0",
                from_to_location,
                veh_no,
                timezone.localtime(tpc.tpc_created_on).strftime("%Y-%m-%d %H:%M") if tpc.tpc_created_on else "-",
                created_by,
                updated_by,
                timezone.localtime(tpc.tpc_updated_at).strftime("%Y-%m-%d %H:%M") if tpc.tpc_updated_at else "-",
                f'''<div class="d-flex justify-content-center" style="gap: 5px;">
                    <a href="/SMS/tms_petty_cash_voucher_print/{tpc.id}/" target="_blank" class="btn-modern py-1 px-2" style="min-width:auto; display:inline-flex; align-items:center; background-color: #0dcaf0; color: white; border-color: #0dcaf0;" title="Print Voucher">
                        <i class="fas fa-print"></i>
                    </a>
                    <a href="{edit_url}" class="btn-modern btn-submit py-1 px-2" style="min-width:auto; display:inline-flex; align-items:center;">
                        <i class="far fa-edit"></i>
                    </a>
                    <form action="/SMS/tms_petty_cash_delete/{tpc.id}/" method="post" onsubmit="return confirm('Are you sure you want to delete this record?');" style="display:inline-flex;">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get('CSRF_COOKIE', '')}">
                        <button type="submit" class="btn-modern btn-cancel py-1 px-2" style="min-width:auto; display:inline-flex; align-items:center;">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    </form>
                </div>'''
            ]
            data.append(row)
            
        return JsonResponse({
            'draw': draw,
            'recordsTotal': records_total,
            'recordsFiltered': records_filtered,
            'data': data
        })
        
    user_list = []
    if is_admin_or_supervisor:
        from django.contrib.auth.models import User
        creator_ids = TMSPettyCashInfo.objects.filter(tpc_created_by__isnull=False).values_list('tpc_created_by_id', flat=True).distinct()
        user_list = User.objects.filter(id__in=creator_ids).order_by('first_name', 'username')

    context = {
        'search_tpc_number': tpc_number,
        'search_date': search_date,
        'from_date': from_date,
        'to_date': to_date,
        'search_vehicle': search_vehicle,
        'search_branch': search_branch,
        'search_user': search_user,
        'user_list': user_list,
        'is_admin_or_supervisor': is_admin_or_supervisor,
    }
    return render(request, "asset_mgt_app/tms_petty_cash_list.html", context)


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

def tms_petty_cash_voucher_print(request, tpc_id):
    tpc = get_object_or_404(TMSPettyCashInfo, pk=tpc_id)
    amount_in_words = number_to_words(tpc.tpc_amount or 0)
    
    # Determine the 'Payment to' value based on available fields
    payment_to = ''
    if tpc.tpc_to_manual:
        payment_to = tpc.tpc_to_manual
    elif tpc.tpc_driver_name:
        payment_to = tpc.tpc_driver_name.dm_name
    elif tpc.tpc_driver_name_manual:
        payment_to = tpc.tpc_driver_name_manual
    elif tpc.tpc_to:
        payment_to = tpc.tpc_to.first_name or tpc.tpc_to.username
        
    # Clean remarks for printing
    clean_remarks = tpc.tpc_remarks or ''
    if 'Auto-generated' in clean_remarks:
        clean_remarks = re.sub(r'\s*\[?Auto-generated.*', '', clean_remarks).strip()

    context = {
        'tpc': tpc,
        'amount_in_words': amount_in_words,
        'payment_to': payment_to,
        'clean_remarks': clean_remarks,
    }
    return render(request, 'asset_mgt_app/tms_petty_cash_voucher.html', context)

def tms_petty_cash_delete(request, tpc_id):
    tpc = get_object_or_404(TMSPettyCashInfo, pk=tpc_id)
    tpc.delete()
    messages.success(request, "Petty Cash deleted successfully.")
    return redirect('tms_petty_cash_list')

def get_tms_trips_by_date(request):
    trip_date = request.GET.get('trip_date')
    if not trip_date:
        return JsonResponse({'status': 'error', 'message': 'No date provided'})
        
    try:
        from datetime import datetime
        # Check if format is DD-MM-YYYY
        if len(trip_date.split('-')[0]) == 2:
            parsed_date = datetime.strptime(trip_date, "%d-%m-%Y").date()
            trip_date = parsed_date.strftime("%Y-%m-%d")
    except Exception:
        pass
        
    trips = TripdetailInfo.objects.filter(tr_departeddate__date=trip_date).exclude(tr_category__category__icontains='empty')
    
    trip_data = []
    for t in trips:
        customer_name = ""
        cnote_no = ""
        customer_id = ""
        
        if t.tr_consignmentnumber:
            cnote_no = t.tr_consignmentnumber.co_consignmentnumber or ""
            if t.tr_consignmentnumber.co_customer:
                customer_name = t.tr_consignmentnumber.co_customer.cu_name or ""
                customer_id = t.tr_consignmentnumber.co_customer.id
                
        trip_data.append({
            'trip_id': t.id,
            'cnote_no': cnote_no,
            'customer_id': customer_id,
            'customer_name': customer_name,
            'vehicle_source_id': t.tr_vehiclesource.id if t.tr_vehiclesource else "",
            'vehicle_source_name': t.tr_vehiclesource.ow_ownership if t.tr_vehiclesource else "",
            'vehicle_number': t.tr_vehiclenumber or "",
            'driver_name': t.tr_drivername or "",
            'from_location': t.tr_departedlocation.place_name if t.tr_departedlocation else "",
            'to_location': t.tr_reportedlocation.place_name if t.tr_reportedlocation else ""
        })
        
    return JsonResponse({'status': 'success', 'data': trip_data})

def tms_petty_cash_export_tally(request):
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from django.http import HttpResponse
    
    tpc_number = request.GET.get('tpc_number', "").strip()
    search_date = request.GET.get('search_date', "").strip()
    from_date = request.GET.get('from_date', "").strip()
    to_date = request.GET.get('to_date', "").strip()
    search_vehicle = request.GET.get('search_vehicle', "").strip()
    search_branch = request.GET.get('search_branch', "").strip()
    search_user = request.GET.get('search_user', "").strip()
    
    filters = Q()
    if tpc_number:
        filters &= Q(tpc_number__icontains=tpc_number)
    if search_date:
        filters &= Q(tpc_trip_date=search_date)
    if from_date:
        filters &= Q(tpc_transaction_date__gte=from_date)
    if to_date:
        filters &= Q(tpc_transaction_date__lte=to_date)
    if search_vehicle:
        filters &= (Q(tpc_vehicle_number__vm_registrationnumber__icontains=search_vehicle) | Q(tpc_vehicle_number_manual__icontains=search_vehicle))

    is_admin_or_supervisor = is_admin_or_supervisor_user(request)

    if not is_admin_or_supervisor:
        user_branch_code = get_user_branch_code(request)
        if user_branch_code == 'BLR':
            filters &= (Q(tpc_branch__loc_name__icontains='BLR') | Q(tpc_branch__loc_name__icontains='Bangalore') | Q(tpc_branch__loc_name__icontains='Bengaluru'))
        elif user_branch_code == 'MAA':
            filters &= (Q(tpc_branch__loc_name__icontains='MAA') | Q(tpc_branch__loc_name__icontains='Chennai'))
        elif user_branch_code:
            filters &= Q(tpc_branch__loc_name__icontains=user_branch_code)
    else:
        if search_branch:
            if search_branch == 'BLR':
                filters &= (Q(tpc_branch__loc_name__icontains='BLR') | Q(tpc_branch__loc_name__icontains='Bangalore') | Q(tpc_branch__loc_name__icontains='Bengaluru'))
            elif search_branch == 'MAA':
                filters &= (Q(tpc_branch__loc_name__icontains='MAA') | Q(tpc_branch__loc_name__icontains='Chennai'))
            else:
                filters &= Q(tpc_branch__loc_name__icontains=search_branch)
        if search_user:
            filters &= Q(tpc_created_by_id=search_user)
        
    tpc_list = TMSPettyCashInfo.objects.filter(filters).order_by('-id').select_related(
        'tpc_expense_type', 'tpc_credit_ledger', 'tpc_branch', 'tpc_customer', 
        'tpc_vehicle_source', 'tpc_vehicle_number', 'tpc_driver_name', 'tpc_created_by'
    )
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Tally Export"
    
    headers = [
        "DATE", "VOU. NO.", "DEBIT", "CREDIT", "PRIMARY COST CATEGORY", 
        "CUSTOMER", "JOB NO", "VEH.NO.", "AMOUNT", "DRIVER NAME", 
        "TRN DATE", "REMARKS"
    ]
    ws.append(headers)
    
    # Style Header: Yellow Background (#FFFF00), Bold, Center alignment
    header_font = Font(bold=True)
    header_fill = PatternFill("solid", fgColor="FFFF00")
    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")
        
    # Process and append data rows
    for tpc in tpc_list:
        date_str = tpc.tpc_transaction_date.strftime("%d-%m-%Y") if tpc.tpc_transaction_date else ""
        vou_no = tpc.tpc_number or ""
        debit = tpc.tpc_expense_type.tms_exp_type_name if tpc.tpc_expense_type else ""
        credit = tpc.tpc_credit_ledger.ledger_name if tpc.tpc_credit_ledger else ""
        
        # Primary Cost Category
        branch_code = ""
        if tpc.tpc_branch:
            loc_name_upper = tpc.tpc_branch.loc_name.upper()
            if "MAA" in loc_name_upper:
                branch_code = "Maa"
            elif "BLR" in loc_name_upper:
                branch_code = "Blr"
            else:
                branch_code = tpc.tpc_branch.loc_name.split()[-1].title()
                
        source_code = ""
        if tpc.tpc_vehicle_source:
            source_name = tpc.tpc_vehicle_source.ow_ownership.lower()
            if "market" in source_name:
                source_code = "Mkt"
            elif "attached" in source_name:
                source_code = "Att"
            elif "own" in source_name:
                source_code = "Own"
            else:
                source_code = tpc.tpc_vehicle_source.ow_ownership[:3].title()
        elif tpc.tpc_unit:
            source_code = tpc.tpc_unit
            
        primary_cost_cat = f"{branch_code}-{source_code}" if (branch_code and source_code) else (branch_code or source_code or "")
        
        # Customer
        customer = tpc.tpc_customer.cu_name if tpc.tpc_customer else ""
        
        # Job No
        job_no = tpc.tpc_job_no or ""
        
        # Veh. No: "Mkt" constant for market vehicles, else the registration number
        veh_no = ""
        if tpc.tpc_vehicle_source and "market" in tpc.tpc_vehicle_source.ow_ownership.lower():
            veh_no = "Mkt"
        elif tpc.tpc_vehicle_number:
            reg_num = tpc.tpc_vehicle_number.vm_registrationnumber or ""
            if tpc.tpc_vehicle_source and "attached" in tpc.tpc_vehicle_source.ow_ownership.lower():
                veh_no = f"{reg_num}(A)"
            else:
                veh_no = reg_num
        elif tpc.tpc_vehicle_number_manual:
            veh_no = tpc.tpc_vehicle_number_manual
            
        # Amount
        amount = tpc.tpc_amount or 0.0
        
        # Driver Name
        driver_name = (tpc.tpc_driver_name.dm_name if tpc.tpc_driver_name else tpc.tpc_driver_name_manual) or ""
        
        # Trn Date (DD-MMM, e.g. 28-Jul)
        trn_date = tpc.tpc_trip_date.strftime("%d-%b") if tpc.tpc_trip_date else ""
        
        # Remarks: Route string from trip if available, else tpc_remarks
        remarks = tpc.tpc_remarks or ""
        if job_no:
            trip = TripdetailInfo.objects.filter(
                Q(tr_consignmentnumber__co_consignmentnumber=job_no) | 
                Q(tr_tripnumber=job_no)
            ).first()
            if trip:
                from_loc = trip.tr_departedlocation.place_name if trip.tr_departedlocation else ""
                to_loc = trip.tr_reportedlocation.place_name if trip.tr_reportedlocation else ""
                if from_loc or to_loc:
                    remarks = f"{from_loc}-{to_loc}"
                    
        ws.append([
            date_str, vou_no, debit, credit, primary_cost_cat,
            customer, job_no, veh_no, amount, driver_name,
            trn_date, remarks
        ])
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="TMS_Petty_Cash_Tally_Export.xlsx"'
    wb.save(response)
    return response


def get_ledger_balance(request):
    ledger_id = request.GET.get('ledger_id')
    if not ledger_id:
        return JsonResponse({'status': 'error', 'message': 'No ledger ID provided'})
    
    from django.db.models import Sum
    from ..models import iou_info
    from ..sub_models.pms_petty_cash_mod import PMSPettyCashInfo
    from ..sub_models.wms_petty_cash_mod import WMSPettyCashInfo
    
    total_iou = iou_info.objects.filter(iou_credit_ledger_id=ledger_id).aggregate(Sum('amount'))['amount__sum'] or 0.0
    
    total_tms_spent = TMSPettyCashInfo.objects.filter(tpc_credit_ledger_id=ledger_id).aggregate(Sum('tpc_amount'))['tpc_amount__sum'] or 0.0
    total_pms_spent = PMSPettyCashInfo.objects.filter(ppc_credit_ledger_id=ledger_id).aggregate(Sum('ppc_amount'))['ppc_amount__sum'] or 0.0
    total_wms_spent = WMSPettyCashInfo.objects.filter(wpc_credit_ledger_id=ledger_id).aggregate(Sum('wpc_total_amount'))['wpc_total_amount__sum'] or 0.0
    
    total_spent = total_tms_spent + total_pms_spent + total_wms_spent
    balance = total_iou - total_spent
    
    return JsonResponse({
        'status': 'success',
        'balance': f"{balance:.2f}"
    })


@csrf_exempt
def add_tms_expense_type(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if not name:
            return JsonResponse({"success": False, "error": "Expense type name cannot be empty."})

        existing = TMSExpenseTypeInfo.objects.filter(tms_exp_type_name__iexact=name).first()
        if existing:
            if not existing.tms_exp_type_status:
                existing.tms_exp_type_status = True
                existing.save()
            return JsonResponse({
                "success": True,
                "id": existing.id,
                "name": existing.tms_exp_type_name,
                "message": "Expense type already exists."
            })

        from django.db.models import Max
        from django.db import connection
        try:
            new_obj = TMSExpenseTypeInfo.objects.create(tms_exp_type_name=name, tms_exp_type_status=True)
        except Exception:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT setval(pg_get_serial_sequence('sms_app_tmsexpensetypeinfo', 'id'), (SELECT COALESCE(MAX(id), 1) FROM sms_app_tmsexpensetypeinfo));")
                new_obj = TMSExpenseTypeInfo.objects.create(tms_exp_type_name=name, tms_exp_type_status=True)
            except Exception:
                max_id = TMSExpenseTypeInfo.objects.aggregate(Max('id'))['id__max'] or 0
                new_obj = TMSExpenseTypeInfo.objects.create(id=max_id + 1, tms_exp_type_name=name, tms_exp_type_status=True)

        return JsonResponse({
            "success": True,
            "id": new_obj.id,
            "name": new_obj.tms_exp_type_name
        })
    return JsonResponse({"success": False, "error": "Invalid request method."})

