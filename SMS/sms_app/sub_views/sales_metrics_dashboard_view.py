import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime, date, timedelta
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q
from django.utils import timezone

from ..models import (
    MyUser,
    User_extInfo,
    SalesInfo,
    Sales_Comments_Info,
    Sales_target_info,
    BusinessrevenueInfo,
    Business_Sol_info,
    Calltype,
    Callnature,
    Location_info,
    YesNoInfo
)

SALES_DEPARTMENT_ID = 5


def get_color_code(percentage):
    """
    Color coding rules matching CS Dashboard scale:
    Red: 0% - 35%
    Orange: 36% - 70%
    Green: 71% - 100%
    Purple/Blue: > 100%
    """
    if percentage <= 35:
        return 'red', '#ef4444', 'Red'
    elif percentage <= 70:
        return 'orange', '#f59e0b', 'Orange'
    elif percentage <= 100:
        return 'green', '#10b981', 'Green'
    else:
        return 'blue', '#8b5cf6', 'Purple'


def _get_short_company(user, target=None):
    """
    Returns clean short company code: PACK, TRANS, STORAGE, EXPRESS, TOURS, etc.
    """
    if target and target.st_company:
        name = str(target.st_company.bvm_business).upper()
        if 'PACK' in name:
            return 'PACK'
        if 'TRANS' in name:
            return 'TRANS'
        if 'STORAGE' in name:
            return 'STORAGE'
        if 'EXPRESS' in name:
            return 'EXPRESS'
        if 'TOURS' in name:
            return 'TOURS'
        return name[:12]

    if hasattr(user, 'user_extinfo') and user.user_extinfo and user.user_extinfo.emp_organisation:
        name = str(user.user_extinfo.emp_organisation).upper()
        if 'PACK' in name:
            return 'PACK'
        if 'TRANS' in name:
            return 'TRANS'
        if 'STORAGE' in name:
            return 'STORAGE'
        if 'EXPRESS' in name:
            return 'EXPRESS'
        if 'TOURS' in name:
            return 'TOURS'
        return name[:12]

    return 'PACK'


def _get_active_sales_rep_ids():
    """
    Returns the set of user IDs that have recorded sales activities
    (calls, targets, sales records, or revenue entries).
    """
    return set(Sales_Comments_Info.objects.values_list('sc_updated_by_id', flat=True)) | \
           set(Sales_target_info.objects.values_list('st_sales_person_id', flat=True)) | \
           set(SalesInfo.objects.values_list('s_updated_by_id', flat=True)) | \
           set(BusinessrevenueInfo.objects.values_list('br_sale_person_id', flat=True))


def _build_metrics_rows(branch_id=None, employee_id=None, from_date=None, to_date=None):
    """
    Computes all 26 metrics + performance indicators across active sales executives.
    Uses branch_id (Location_info) and employee_id (User_extInfo / MyUser) identical to CS Dashboard.
    """
    active_ids = _get_active_sales_rep_ids()

    users_query = MyUser.objects.filter(
        user_extinfo__department_id=SALES_DEPARTMENT_ID,
        is_active=True,
        id__in=active_ids
    ).distinct().select_related('user_extinfo', 'user_extinfo__emp_branch')

    if branch_id and branch_id != 'all':
        users_query = users_query.filter(user_extinfo__emp_branch_id=branch_id)

    if employee_id and employee_id != 'all':
        users_query = users_query.filter(id=employee_id)

    # Standardize all metric filtering on Date of Call (sc_date_of_call)
    call_filter = Q()
    revenue_filter = Q()
    target_filter = Q()

    if from_date:
        call_filter &= Q(sc_date_of_call__gte=from_date)
        revenue_filter &= Q(br_to_date__gte=from_date)
        target_filter &= Q(st_end_date__gte=from_date)
    if to_date:
        call_filter &= Q(sc_date_of_call__lte=to_date)
        revenue_filter &= Q(br_from_date__lte=to_date)
        target_filter &= Q(st_start_date__lte=to_date)

    rows = []

    for u in users_query:
        # Targets (Option A: Targets strictly apply to a selected period; in All-Time mode targets are 0)
        if from_date or to_date:
            t_qs = Sales_target_info.objects.filter(st_sales_person=u).filter(target_filter).order_by('-id')
            target = t_qs.first()
        else:
            target = None

        company = _get_short_company(u, target)

        # Calls
        calls = Sales_Comments_Info.objects.filter(sc_updated_by=u).filter(call_filter)
        total_calls = calls.count()

        # If user has zero calls and zero targets and no single employee filter, skip
        if (not employee_id or employee_id == 'all') and total_calls == 0 and not target:
            continue

        # CALL TYPE counts (4 columns)
        c_email = calls.filter(sc_call_type__call_type__icontains='mail').count()
        c_inperson = calls.filter(sc_call_type__call_type__icontains='person').count()
        c_teams = calls.filter(sc_call_type__call_type__icontains='team').count()
        c_tele = calls.filter(sc_call_type__call_type__icontains='tele').count()

        # CALL NATURE counts (Pipeline Stages - 7 columns)
        n_suspect = calls.filter(sc_call_nature__call_nature__icontains='suspect').count()
        n_prospect = calls.filter(sc_call_nature__call_nature__icontains='prospect').count()
        n_rfq = calls.filter(
            Q(sc_call_nature__call_nature__icontains='rfq') |
            Q(sc_call_nature__call_nature__icontains='rfp') |
            Q(sc_call_nature__call_nature__icontains='rfi')
        ).count()
        n_negotiation = calls.filter(sc_call_nature__call_nature__icontains='negotiat').count()
        n_contract = calls.filter(
            Q(sc_call_nature__call_nature__icontains='signed') |
            Q(sc_call_nature__call_nature__icontains='contract')
        ).count()
        n_implementation = calls.filter(sc_call_nature__call_nature__icontains='implement').count()
        n_transaction = calls.filter(sc_call_nature__call_nature__icontains='transaction').count()

        # TARGET (In-Person / Period - 6 columns)
        if target:
            tgt_rev_exist = float(target.st_target_revenue_existing or 0.0)
            tgt_rev_new = float(target.st_target_revenue_new or 0.0)
            if tgt_rev_exist == 0 and tgt_rev_new == 0 and (target.st_target_revenue or 0) > 0:
                tgt_rev_exist = round(float(target.st_target_revenue) / 100000.0, 2)

            tgt_cust_total = int(target.st_target_customer or 0)
            tgt_cust_new = int(target.st_target_customers_new or 0)
            tgt_cust_exist = int(target.st_target_customers_existing or 0)
            tgt_cust_onboard = int(target.st_target_customers_onboard or 0)
            tgt_calls = int(target.st_target_calls or 0)
        else:
            tgt_rev_exist = 0.0
            tgt_rev_new = 0.0
            tgt_cust_total = 0
            tgt_cust_new = 0
            tgt_cust_exist = 0
            tgt_cust_onboard = 0
            tgt_calls = 0

        if tgt_cust_total == 0 and (tgt_cust_new > 0 or tgt_cust_exist > 0):
            tgt_cust_total = tgt_cust_new + tgt_cust_exist

        tgt_rev_total = round(tgt_rev_exist + tgt_rev_new, 2)

        # ACTUALS (In-Person / Period - 6 columns)
        # All customer metrics are unified with calls on the filtered Date of Call
        inperson_calls = calls.filter(sc_call_type__call_type__icontains='person')
        inperson_sales_ids = inperson_calls.values_list('sc_sales_number_id', flat=True).distinct()
        inperson_sales = SalesInfo.objects.filter(id__in=inperson_sales_ids)

        # Existing customers visited in-person by this rep
        act_cust_exist = inperson_sales.exclude(s_customer_name_id=210).filter(s_customer_name__isnull=False).values('s_customer_name_id').distinct().count()

        # New customer accounts visited in-person by this rep
        act_cust_new = inperson_sales.filter(Q(s_customer_name_id=210) | Q(s_customer_new_name__isnull=False)).values('s_customer_new_name').distinct().count()

        # Total accounts visited in person
        act_cust_total = act_cust_exist + act_cust_new
        if act_cust_total == 0 and total_calls > 0:
            act_cust_total = calls.values('sc_sales_number').distinct().count()

        # Newly onboarded clients with Business Won: Yes (excluding Customer Response Pending)
        won_base = SalesInfo.objects.filter(
            s_updated_by=u,
            s_bus_won_not__yesno_name='Yes'
        ).exclude(s_status__status='Customer Response Pending')

        if from_date or to_date:
            date_q = Q()
            if from_date:
                date_q &= Q(s_yesdate_business__gte=from_date)
            if to_date:
                date_q &= Q(s_yesdate_business__lte=to_date)
            act_cust_onboard = won_base.filter(date_q).count()
        else:
            act_cust_onboard = won_base.count()

        # Revenue
        rev_qs = BusinessrevenueInfo.objects.filter(br_sale_person=u).filter(revenue_filter)
        total_rev_inr = rev_qs.aggregate(tot=Sum('br_revenue_1'))['tot'] or 0

        rev_exist_inr = rev_qs.filter(
            ~Q(br_customer_name_id=210)
        ).aggregate(tot=Sum('br_revenue_1'))['tot'] or 0

        rev_new_inr = rev_qs.filter(
            Q(br_customer_name_id=210)
        ).aggregate(tot=Sum('br_revenue_1'))['tot'] or 0

        if rev_new_inr == 0 and total_rev_inr > 0 and rev_exist_inr == 0:
            rev_exist_inr = total_rev_inr

        act_rev_exist = round(rev_exist_inr / 100000.0, 2)
        act_rev_new = round(rev_new_inr / 100000.0, 2)
        act_rev_total = round(total_rev_inr / 100000.0, 2)

        rev_achieve_pct = round((act_rev_total / tgt_rev_total * 100), 1) if tgt_rev_total > 0 else 0
        cust_achieve_pct = round((act_cust_exist / tgt_cust_exist * 100), 1) if tgt_cust_exist > 0 else 0
        onboard_achieve_pct = round((act_cust_onboard / tgt_cust_onboard * 100), 1) if tgt_cust_onboard > 0 else 0
        calls_achieve_pct = round((c_inperson / tgt_calls * 100), 1) if tgt_calls > 0 else 0

        rows.append({
            'salesperson_id': u.id,
            'salesperson': u.first_name,
            'salesperson_full': f"{u.first_name} {u.last_name or ''}".strip(),
            'company': company,
            'branch_name': u.user_extinfo.emp_branch.loc_name if (hasattr(u, 'user_extinfo') and u.user_extinfo and u.user_extinfo.emp_branch) else 'BVM MAA',
            'no_of_calls': total_calls,
            'target_calls': tgt_calls,
            # Call Type
            'email': c_email,
            'in_person': c_inperson,
            'ms_teams': c_teams,
            'tele_call': c_tele,
            # Call Nature
            'suspect': n_suspect,
            'prospect': n_prospect,
            'rfq': n_rfq,
            'negotiation': n_negotiation,
            'contract_signed': n_contract,
            'implementation': n_implementation,
            'transaction': n_transaction,
            # Targets (In-Person)
            'target_rev_exist': tgt_rev_exist,
            'target_rev_new': tgt_rev_new,
            'target_rev_total': tgt_rev_total,
            'target_cust_total': tgt_cust_total,
            'target_cust_new': tgt_cust_new,
            'target_cust_exist': tgt_cust_exist,
            'target_cust_onboard': tgt_cust_onboard,
            # Actuals (In-Person)
            'actual_rev_exist': act_rev_exist,
            'actual_rev_new': act_rev_new,
            'actual_rev_total': act_rev_total,
            'actual_cust_total': act_cust_total,
            'actual_cust_new': act_cust_new,
            'actual_cust_exist': act_cust_exist,
            'actual_cust_onboard': act_cust_onboard,
            # Achievements
            'rev_achieve_pct': rev_achieve_pct,
            'cust_achieve_pct': cust_achieve_pct,
            'onboard_achieve_pct': onboard_achieve_pct,
            'calls_achieve_pct': calls_achieve_pct
        })

    rows.sort(key=lambda x: (x['no_of_calls'], x['actual_rev_total']), reverse=True)
    return rows


@login_required(login_url='login_page')
def sales_metrics_dashboard(request):
    """
    Renders the modern Executive Cockpit Sales Metrics Dashboard matching cs_kpi_dashboard styling.
    Uses identical branch and representative dropdown structures.
    """
    first_name = request.session.get('first_name', 'Admin')
    user_id = request.session.get('ses_userID')

    current_user_ext = None
    default_branch_id = 'all'
    default_employee_id = 'all'

    try:
        bvm_maa_loc = Location_info.objects.filter(loc_name='BVM MAA').first()
        if bvm_maa_loc:
            default_branch_id = str(bvm_maa_loc.id)
    except Exception:
        pass

    if user_id:
        try:
            current_user_ext = User_extInfo.objects.get(user_id=user_id)
            if current_user_ext.emp_branch_id:
                default_branch_id = str(current_user_ext.emp_branch_id)
        except Exception:
            pass

    # Active Sales representatives with branch mapping (strictly active reps with recorded activity)
    sales_employees_data = []
    try:
        active_ids = _get_active_sales_rep_ids()
        sales_qs = User_extInfo.objects.filter(
            department_id=SALES_DEPARTMENT_ID,
            user__is_active=True,
            user_id__in=active_ids
        ).only('id', 'user_id', 'department_id', 'emp_branch_id', 'emp_role_id').select_related('user', 'emp_branch').order_by('user__first_name')

        for emp in sales_qs:
            full_name = f"{emp.user.first_name or ''} {emp.user.last_name or ''}".strip() or emp.user.username
            sales_employees_data.append({
                'id': emp.user.id,
                'name': full_name,
                'branch_id': str(emp.emp_branch_id) if emp.emp_branch_id else '',
                'branch_name': emp.emp_branch.loc_name if emp.emp_branch else 'BVM MAA'
            })
    except Exception:
        pass

    # Branches (identical to cs_kpi_dashboard)
    branches = Location_info.objects.all().order_by('loc_name')

    today_str = timezone.localtime(timezone.now()).strftime('%Y-%m-%d')

    context = {
        'first_name': first_name,
        'branches': branches,
        'sales_employees': sales_employees_data,
        'default_branch_id': default_branch_id,
        'default_employee_id': default_employee_id,
        'today_date': today_str,
        'default_from_date': '',
        'default_to_date': '',
    }
    return render(request, "asset_mgt_app/sales_metrics_dashboard.html", context)


@login_required(login_url='login_page')
def get_sales_metrics_dashboard_data(request):
    """
    JSON API feeding the executive sales performance dashboard.
    Returns summary cards, channel distribution, pipeline funnel, target achievement gauges,
    and the full 26-metric salesperson data grid with totals.
    """
    branch_id = request.GET.get('branch_id', '').strip()
    employee_id = request.GET.get('employee_id', '').strip()
    from_date = request.GET.get('from_date', '').strip()
    to_date = request.GET.get('to_date', '').strip()

    rows = _build_metrics_rows(branch_id, employee_id, from_date, to_date)

    total_calls = sum(r['no_of_calls'] for r in rows)
    total_in_person = sum(r['in_person'] for r in rows)
    total_tele_call = sum(r['tele_call'] for r in rows)
    total_email = sum(r['email'] for r in rows)
    total_teams = sum(r['ms_teams'] for r in rows)

    total_suspect = sum(r['suspect'] for r in rows)
    total_prospect = sum(r['prospect'] for r in rows)
    total_rfq = sum(r['rfq'] for r in rows)
    total_negotiation = sum(r['negotiation'] for r in rows)
    total_contract_signed = sum(r['contract_signed'] for r in rows)
    total_implementation = sum(r['implementation'] for r in rows)
    total_transaction = sum(r['transaction'] for r in rows)

    total_target_calls = sum(r['target_calls'] for r in rows)
    total_target_rev = round(sum(r['target_rev_total'] for r in rows), 2)
    total_target_rev_ex = round(sum(r['target_rev_exist'] for r in rows), 2)
    total_target_rev_new = round(sum(r['target_rev_new'] for r in rows), 2)

    total_actual_rev = round(sum(r['actual_rev_total'] for r in rows), 2)
    total_actual_rev_ex = round(sum(r['actual_rev_exist'] for r in rows), 2)
    total_actual_rev_new = round(sum(r['actual_rev_new'] for r in rows), 2)

    total_target_cust = sum(r['target_cust_total'] for r in rows)
    total_target_cust_new = sum(r['target_cust_new'] for r in rows)
    total_target_cust_ex = sum(r['target_cust_exist'] for r in rows)
    total_target_onboard = sum(r['target_cust_onboard'] for r in rows)

    # 1. Existing Customers Visited In-Person (Scoped to selected branch/rep/date)
    rep_ids = [r['salesperson_id'] for r in rows]
    inperson_calls_scope = Sales_Comments_Info.objects.filter(sc_updated_by_id__in=rep_ids, sc_call_type__call_type__icontains='person')

    if from_date:
        inperson_calls_scope = inperson_calls_scope.filter(sc_date_of_call__gte=from_date)
    if to_date:
        inperson_calls_scope = inperson_calls_scope.filter(sc_date_of_call__lte=to_date)

    inperson_sales_ids = inperson_calls_scope.values_list('sc_sales_number_id', flat=True).distinct()
    distinct_exist_inperson_count = SalesInfo.objects.filter(
        id__in=inperson_sales_ids
    ).exclude(s_customer_name_id=210).filter(s_customer_name__isnull=False).values('s_customer_name_id').distinct().count()

    total_actual_cust_ex = distinct_exist_inperson_count
    total_actual_cust_new = sum(r['actual_cust_new'] for r in rows)
    total_actual_cust = total_actual_cust_ex + total_actual_cust_new

    # 2. Newly Onboarded / Won Customers (Business Won Status = Yes, excluding Customer Response Pending)
    won_qs = SalesInfo.objects.filter(
        s_bus_won_not__yesno_name='Yes',
        s_updated_by_id__in=rep_ids
    ).exclude(s_status__status='Customer Response Pending')

    if from_date or to_date:
        date_q = Q()
        if from_date:
            date_q &= Q(s_yesdate_business__gte=from_date)
        if to_date:
            date_q &= Q(s_yesdate_business__lte=to_date)
        won_qs = won_qs.filter(date_q)

    won_qs = won_qs.select_related('s_updated_by', 's_status', 's_customer_name')
    won_customers_list = []
    for s in won_qs.order_by('-s_yesdate_business', '-id'):
        cname = (s.s_customer_new_name or '').strip()
        if not cname or cname.lower() == 'new customer':
            if s.s_customer_name and s.s_customer_name.cu_name and s.s_customer_name.cu_name.lower() != 'new customer':
                cname = s.s_customer_name.cu_name.strip()
            else:
                cname = f"Client #{s.id}"
        last = s.s_updated_by.last_name or '' if s.s_updated_by else ''
        first = s.s_updated_by.first_name if s.s_updated_by else 'Unknown'
        rep = (first + ' ' + last).strip()
        st = s.s_status.status if s.s_status else 'Won'
        won_d = s.s_yesdate_business.strftime('%d-%b-%Y') if s.s_yesdate_business else 'N/A'
        won_customers_list.append({
            'id': s.id,
            'customer_name': cname,
            'bus_won_status': 'Yes',
            'sales_rep': rep,
            'status': st,
            'won_date': won_d,
            'revenue': float(s.s_expected_revenue or 0)
        })

    total_actual_onboard = len(won_customers_list)

    overall_rev_pct = round((total_actual_rev / total_target_rev * 100), 1) if total_target_rev > 0 else 0
    overall_cust_exist_pct = round((total_actual_cust_ex / total_target_cust_ex * 100), 1) if total_target_cust_ex > 0 else 0
    overall_onboard_pct = round((total_actual_onboard / total_target_onboard * 100), 1) if total_target_onboard > 0 else 0
    in_person_rate = round((total_in_person / total_calls * 100), 1) if total_calls > 0 else 0
    tele_rate = round((total_tele_call / total_calls * 100), 1) if total_calls > 0 else 0
    digital_rate = round(((total_email + total_teams) / total_calls * 100), 1) if total_calls > 0 else 0
    win_rate = round((total_actual_onboard / total_actual_cust * 100), 1) if total_actual_cust > 0 else 0

    rev_code, rev_hex, rev_status = get_color_code(overall_rev_pct)
    cust_code, cust_hex, cust_status = get_color_code(overall_cust_exist_pct)
    onboard_code, onboard_hex, onboard_status = get_color_code(overall_onboard_pct)

    # 1. Top 8 KPI Cards
    cards = {
        'total_calls': {
            'val': f"{total_calls:,}",
            'sub': f"{len(rows)} Executives",
            'badge': "Calls Logged",
            'icon': "fa-phone-volume"
        },
        'in_person': {
            'val': f"{total_in_person:,}",
            'sub': f"{in_person_rate}% of Calls",
            'badge': "In-Person",
            'icon': "fa-user-friends"
        },
        'tele_calls': {
            'val': f"{total_tele_call:,}",
            'sub': f"{tele_rate}% of Calls",
            'badge': "Tele-Calls",
            'icon': "fa-headset"
        },
        'email_teams': {
            'val': f"{total_email + total_teams:,}",
            'sub': f"Mail: {total_email} · Teams: {total_teams}",
            'badge': "Digital Outreach",
            'icon': "fa-envelope-open-text"
        },
        'target_rev': {
            'val': f"₹ {total_target_rev:,.2f} L",
            'sub': f"Ex: ₹{total_target_rev_ex:.1f}L · Nw: ₹{total_target_rev_new:.1f}L",
            'badge': "Target Rev",
            'icon': "fa-bullseye"
        },
        'actual_rev': {
            'val': f"₹ {total_actual_rev:,.2f} L",
            'sub': f"{overall_rev_pct}% Achieved",
            'badge': f"Ex: ₹{total_actual_rev_ex:.1f}L",
            'icon': "fa-coins"
        },
        'target_cust': {
            'val': f"{total_actual_cust_ex:,}",
            'sub': f"Target: {total_target_cust_ex} ({overall_cust_exist_pct}%)",
            'badge': "Existing In-Person",
            'icon': "fa-users"
        },
        'new_onboard': {
            'val': f"{total_actual_onboard:,}",
            'sub': f"Business Won: Yes (Tgt: {total_target_onboard})",
            'badge': "Won / Onboarded",
            'icon': "fa-trophy"
        }
    }

    # 2. Call Channel Distribution (middle card 1)
    call_channels = [
        {'name': "In-Person Meetings", 'count': total_in_person, 'pct': in_person_rate, 'color': '#3b82f6', 'icon': 'fa-user-friends'},
        {'name': "Tele-Calls (Phone)", 'count': total_tele_call, 'pct': tele_rate, 'color': '#10b981', 'icon': 'fa-headset'},
        {'name': "E-Mail Outreach", 'count': total_email, 'pct': round((total_email / total_calls * 100), 1) if total_calls > 0 else 0, 'color': '#a855f7', 'icon': 'fa-envelope'},
        {'name': "MS-Teams Calls", 'count': total_teams, 'pct': round((total_teams / total_calls * 100), 1) if total_calls > 0 else 0, 'color': '#f59e0b', 'icon': 'fa-video'},
    ]

    # 3. Pipeline Funnel (middle card 2)
    pipeline_stages = [
        {'name': "Suspect", 'count': total_suspect, 'pct': round((total_suspect / total_calls * 100), 1) if total_calls > 0 else 0, 'color': '#94a3b8', 'icon': 'fa-search'},
        {'name': "Prospect", 'count': total_prospect, 'pct': round((total_prospect / total_calls * 100), 1) if total_calls > 0 else 0, 'color': '#60a5fa', 'icon': 'fa-binoculars'},
        {'name': "RFQ / RFP", 'count': total_rfq, 'pct': round((total_rfq / total_calls * 100), 1) if total_calls > 0 else 0, 'color': '#eab308', 'icon': 'fa-file-invoice'},
        {'name': "Negotiation", 'count': total_negotiation, 'pct': round((total_negotiation / total_calls * 100), 1) if total_calls > 0 else 0, 'color': '#fb923c', 'icon': 'fa-handshake'},
        {'name': "Contract Won", 'count': total_contract_signed, 'pct': round((total_contract_signed / total_calls * 100), 1) if total_calls > 0 else 0, 'color': '#22c55e', 'icon': 'fa-file-signature'},
        {'name': "Implementation", 'count': total_implementation, 'pct': round((total_implementation / total_calls * 100), 1) if total_calls > 0 else 0, 'color': '#818cf8', 'icon': 'fa-cogs'},
        {'name': "Transaction", 'count': total_transaction, 'pct': round((total_transaction / total_calls * 100), 1) if total_calls > 0 else 0, 'color': '#c084fc', 'icon': 'fa-exchange-alt'},
    ]

    # 4. Target Achievement Gauges & Sector Meters (CS Semicircular Gauge Format)
    rev_ex_pct = round((total_actual_rev_ex / total_target_rev_ex * 100), 1) if total_target_rev_ex > 0 else 0
    rev_new_pct = round((total_actual_rev_new / total_target_rev_new * 100), 1) if total_target_rev_new > 0 else 0
    calls_achieve_pct = round((total_in_person / total_target_calls * 100), 1) if total_target_calls > 0 else 0

    revenue_meters = [
        {
            'title': "EXISTING REV",
            'target': f"₹{total_target_rev_ex:.1f}L",
            'done': f"₹{total_actual_rev_ex:.1f}L",
            'pct': rev_ex_pct,
            'color': get_color_code(rev_ex_pct)[1],
            'status': get_color_code(rev_ex_pct)[2],
            'badge': f"Target: ₹{total_target_rev_ex:.1f}L · Done: ₹{total_actual_rev_ex:.1f}L"
        },
        {
            'title': "NEW CLIENT REV",
            'target': f"₹{total_target_rev_new:.1f}L",
            'done': f"₹{total_actual_rev_new:.1f}L",
            'pct': rev_new_pct,
            'color': get_color_code(rev_new_pct)[1],
            'status': get_color_code(rev_new_pct)[2],
            'badge': f"Target: ₹{total_target_rev_new:.1f}L · Done: ₹{total_actual_rev_new:.1f}L"
        },
        {
            'title': "TOTAL REVENUE",
            'target': f"₹{total_target_rev:.1f}L",
            'done': f"₹{total_actual_rev:.1f}L",
            'pct': overall_rev_pct,
            'color': rev_hex,
            'status': rev_status,
            'badge': f"⚡ {overall_rev_pct}% Overall Achieved"
        }
    ]

    customer_meters = [
        {
            'title': "EXISTING CUST (IN-PERSON)",
            'target': f"{total_target_cust_ex}",
            'done': f"{total_actual_cust_ex}",
            'pct': overall_cust_exist_pct,
            'color': cust_hex,
            'status': cust_status,
            'badge': f"👥 {total_actual_cust_ex} Visited In-Person",
            'is_exist': True
        },
        {
            'title': "NEW ONBOARDED (WON)",
            'target': f"{total_target_onboard}",
            'done': f"{total_actual_onboard}",
            'pct': overall_onboard_pct,
            'color': onboard_hex,
            'status': onboard_status,
            'badge': f"🏆 {total_actual_onboard} Won (Business Won: Yes)",
            'is_onboard': True,
            'latest_won_name': won_customers_list[0]['customer_name'] if won_customers_list else 'No Won Clients',
            'won_preview': [w['customer_name'] for w in won_customers_list[:10]],
            'won_count': total_actual_onboard
        },
        {
            'title': "IN-PERSON CALLS",
            'target': f"{total_target_calls}",
            'done': f"{total_in_person}",
            'pct': calls_achieve_pct,
            'color': get_color_code(calls_achieve_pct)[1],
            'status': get_color_code(calls_achieve_pct)[2],
            'badge': f"⚡ {total_in_person} Client Meetings"
        }
    ]

    gauges = [
        {
            'name': "REVENUE ACHIEVEMENT",
            'target': total_target_rev,
            'done': total_actual_rev,
            'unit': "₹ Lak",
            'pct': overall_rev_pct,
            'color': rev_hex,
            'status': rev_status,
            'sub': f"Target: ₹{total_target_rev:.1f}L | Achieved: ₹{total_actual_rev:.1f}L"
        },
        {
            'name': "EXISTING CUSTOMERS (IN-PERSON)",
            'target': total_target_cust_ex,
            'done': total_actual_cust_ex,
            'unit': "Nos",
            'pct': overall_cust_exist_pct,
            'color': cust_hex,
            'status': cust_status,
            'sub': f"Target: {total_target_cust_ex} Nos | Visited: {total_actual_cust_ex} Nos"
        },
        {
            'name': "NEW ONBOARDING (WON)",
            'target': total_target_onboard,
            'done': total_actual_onboard,
            'unit': "Nos",
            'pct': overall_onboard_pct,
            'color': onboard_hex,
            'status': onboard_status,
            'sub': f"Target: {total_target_onboard} Nos | Won: {total_actual_onboard} Nos"
        }
    ]

    # 5. Row color helper for template
    for r in rows:
        r['rev_color_class'] = get_color_code(r['rev_achieve_pct'])[0]
        r['cust_color_class'] = get_color_code(r['cust_achieve_pct'])[0]
        r['onboard_color_class'] = get_color_code(r['onboard_achieve_pct'])[0]

    # 6. Totals row
    totals = {
        'no_of_calls': total_calls,
        'email': total_email,
        'in_person': total_in_person,
        'ms_teams': total_teams,
        'tele_call': total_tele_call,
        'suspect': total_suspect,
        'prospect': total_prospect,
        'rfq': total_rfq,
        'negotiation': total_negotiation,
        'contract_signed': total_contract_signed,
        'implementation': total_implementation,
        'transaction': total_transaction,
        'target_rev_exist': total_target_rev_ex,
        'target_rev_new': total_target_rev_new,
        'target_rev_total': total_target_rev,
        'target_cust_total': total_target_cust,
        'target_cust_new': total_target_cust_new,
        'target_cust_exist': total_target_cust_ex,
        'target_cust_onboard': total_target_onboard,
        'actual_rev_exist': total_actual_rev_ex,
        'actual_rev_new': total_actual_rev_new,
        'actual_rev_total': total_actual_rev,
        'actual_cust_total': total_actual_cust,
        'actual_cust_new': total_actual_cust_new,
        'actual_cust_exist': total_actual_cust_ex,
        'actual_cust_onboard': total_actual_onboard,
        'rev_achieve_pct': overall_rev_pct,
        'cust_achieve_pct': overall_cust_exist_pct,
        'onboard_achieve_pct': overall_onboard_pct,
    }

    data = {
        'cards': cards,
        'call_channels': call_channels,
        'pipeline_stages': pipeline_stages,
        'gauges': gauges,
        'revenue_meters': revenue_meters,
        'customer_meters': customer_meters,
        'won_customers': won_customers_list,
        'rows': rows,
        'totals': totals,
        'count': len(rows),
    }
    return JsonResponse(data)


@login_required(login_url='login_page')
def sales_metrics_export_excel(request):
    """
    Exports the exact 26-column metrics extracted directly from the dashboard data into an Excel spreadsheet.
    Triggered via the 'Export Excel' button on the dashboard itself.
    """
    branch_id = request.GET.get('branch_id', '').strip()
    employee_id = request.GET.get('employee_id', '').strip()
    from_date = request.GET.get('from_date', '').strip()
    to_date = request.GET.get('to_date', '').strip()

    rows = _build_metrics_rows(branch_id, employee_id, from_date, to_date)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sales Metrics Export"
    ws.views.sheetView[0].showGridLines = True

    font_group = Font(name='Calibri', size=11, bold=True, color='FFFFFF')
    font_sub = Font(name='Calibri', size=10, bold=True, color='1E293B')
    font_data = Font(name='Calibri', size=10)
    font_total = Font(name='Calibri', size=10, bold=True, color='000000')

    fill_group_call_type = PatternFill(start_color='1E3A8A', end_color='1E3A8A', fill_type='solid')
    fill_group_call_nature = PatternFill(start_color='0D9488', end_color='0D9488', fill_type='solid')
    fill_group_target = PatternFill(start_color='C2410C', end_color='C2410C', fill_type='solid')
    fill_group_actual = PatternFill(start_color='15803D', end_color='15803D', fill_type='solid')
    fill_sub_header = PatternFill(start_color='F1F5F9', end_color='F1F5F9', fill_type='solid')
    fill_total = PatternFill(start_color='E2E8F0', end_color='E2E8F0', fill_type='solid')

    border_thin = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    align_center = Alignment(horizontal='center', vertical='center', wrap_text=True)
    align_left = Alignment(horizontal='left', vertical='center')
    align_right = Alignment(horizontal='right', vertical='center')

    # Row 1: Merged Group Headers (Exact 26-column format from user template)
    ws.merge_cells('D1:G1')
    ws['D1'] = 'CALL TYPE'
    ws['D1'].fill = fill_group_call_type
    ws['D1'].font = font_group
    ws['D1'].alignment = align_center

    ws.merge_cells('H1:N1')
    ws['H1'] = 'CALL NATURE'
    ws['H1'].fill = fill_group_call_nature
    ws['H1'].font = font_group
    ws['H1'].alignment = align_center

    ws.merge_cells('O1:T1')
    ws['O1'] = 'TARGET (In-Person)'
    ws['O1'].fill = fill_group_target
    ws['O1'].font = font_group
    ws['O1'].alignment = align_center

    ws.merge_cells('U1:Z1')
    ws['U1'] = 'ACTUAL  (In-Person)'
    ws['U1'].fill = fill_group_actual
    ws['U1'].font = font_group
    ws['U1'].alignment = align_center

    for col in range(1, 27):
        cell = ws.cell(row=1, column=col)
        cell.border = border_thin
        if col in range(4, 8):
            cell.fill = fill_group_call_type
        elif col in range(8, 15):
            cell.fill = fill_group_call_nature
        elif col in range(15, 21):
            cell.fill = fill_group_target
        elif col in range(21, 27):
            cell.fill = fill_group_actual

    ws.row_dimensions[1].height = 26

    # Row 2: Sub-headers matching exact user template
    headers = [
        'Sales', 'Company', 'No of Calls',
        'E-Mail', 'In-Person', 'MS-Teams', 'Tele-Call',
        'Suspect', 'Prospect', 'RFQ', 'Negotiation', 'Contract Signed', 'Implemenetaion', 'Transaction',
        'Target Revenue Existing Customer (Lak)', 'Target Revenue New Customer (Lak)',
        'Target No of Customers (Nos)', 'Target No of New Customer s(Nos)',
        'Target No of Existing Customers (Nos)', 'Target No of New Customers Onboard (Nos)',
        'Actual Revenue Existing Customer (Lak)', 'Actual Revenue New Customer (Lak)',
        'Actual No of Customers (Nos)', 'Actual No of New Customers (Nos)',
        'Actual No of Existing Customers (Nos)', 'Actual No of New Customers Onboard (Nos)'
    ]

    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=2, column=col_idx, value=h)
        cell.font = font_sub
        cell.fill = fill_sub_header
        cell.alignment = align_center
        cell.border = border_thin

    ws.row_dimensions[2].height = 42

    current_row = 3
    for r in rows:
        row_values = [
            r['salesperson'],
            r['company'],
            r['no_of_calls'],
            r['email'] or '',
            r['in_person'] or '',
            r['ms_teams'] or '',
            r['tele_call'] or '',
            r['suspect'] or '',
            r['prospect'] or '',
            r['rfq'] or '',
            r['negotiation'] or '',
            r['contract_signed'] or '',
            r['implementation'] or '',
            r['transaction'] or '',
            r['target_rev_exist'] if r['target_rev_exist'] > 0 else '',
            r['target_rev_new'] if r['target_rev_new'] > 0 else '',
            r['target_cust_total'] if r['target_cust_total'] > 0 else '',
            r['target_cust_new'] if r['target_cust_new'] > 0 else '',
            r['target_cust_exist'] if r['target_cust_exist'] > 0 else '',
            r['target_cust_onboard'] if r['target_cust_onboard'] > 0 else '',
            r['actual_rev_exist'] if r['actual_rev_exist'] > 0 else '',
            r['actual_rev_new'] if r['actual_rev_new'] > 0 else '',
            r['actual_cust_total'] if r['actual_cust_total'] > 0 else '',
            r['actual_cust_new'] if r['actual_cust_new'] > 0 else '',
            r['actual_cust_exist'] if r['actual_cust_exist'] > 0 else '',
            r['actual_cust_onboard'] if r['actual_cust_onboard'] > 0 else '',
        ]

        for col_idx, val in enumerate(row_values, 1):
            cell = ws.cell(row=current_row, column=col_idx, value=val)
            cell.font = font_data
            cell.border = border_thin
            if col_idx in [1, 2]:
                cell.alignment = align_left
            elif col_idx in [15, 16, 21, 22]:
                cell.alignment = align_right
                if isinstance(val, (int, float)):
                    cell.number_format = '#,##0.00'
            else:
                cell.alignment = align_center

        ws.row_dimensions[current_row].height = 20
        current_row += 1

    # Totals Row
    total_row_values = [
        'TOTAL', '',
        sum(r['no_of_calls'] for r in rows),
        sum(r['email'] for r in rows),
        sum(r['in_person'] for r in rows),
        sum(r['ms_teams'] for r in rows),
        sum(r['tele_call'] for r in rows),
        sum(r['suspect'] for r in rows),
        sum(r['prospect'] for r in rows),
        sum(r['rfq'] for r in rows),
        sum(r['negotiation'] for r in rows),
        sum(r['contract_signed'] for r in rows),
        sum(r['implementation'] for r in rows),
        sum(r['transaction'] for r in rows),
        round(sum(r['target_rev_exist'] for r in rows), 2),
        round(sum(r['target_rev_new'] for r in rows), 2),
        sum(r['target_cust_total'] for r in rows),
        sum(r['target_cust_new'] for r in rows),
        sum(r['target_cust_exist'] for r in rows),
        sum(r['target_cust_onboard'] for r in rows),
        round(sum(r['actual_rev_exist'] for r in rows), 2),
        round(sum(r['actual_rev_new'] for r in rows), 2),
        sum(r['actual_cust_total'] for r in rows),
        sum(r['actual_cust_new'] for r in rows),
        sum(r['actual_cust_exist'] for r in rows),
        sum(r['actual_cust_onboard'] for r in rows),
    ]

    for col_idx, val in enumerate(total_row_values, 1):
        cell = ws.cell(row=current_row, column=col_idx, value=val)
        cell.font = font_total
        cell.fill = fill_total
        cell.border = border_thin
        if col_idx in [1, 2]:
            cell.alignment = align_left
        elif col_idx in [15, 16, 21, 22]:
            cell.alignment = align_right
            if isinstance(val, (int, float)):
                cell.number_format = '#,##0.00'
        else:
            cell.alignment = align_center

    ws.row_dimensions[current_row].height = 22

    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            v_str = str(cell.value or '')
            if len(v_str) > max_len:
                max_len = len(v_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="SMS_Sales_Metrics_{timestamp}.xlsx"'
    wb.save(response)
    return response


# Keep for backward compatibility if ever called
def sales_metrics_report(request):
    return redirect('sales_metrics_dashboard')


def sales_metrics_import_excel(request):
    """
    Imports sales targets from the uploaded Excel template if needed.
    """
    if request.method != "POST" or not request.FILES.get('excel_file'):
        messages.error(request, "Please select an Excel file (.xlsx) to upload.")
        return redirect('sales_metrics_dashboard')

    excel_file = request.FILES['excel_file']
    try:
        wb = openpyxl.load_workbook(excel_file, data_only=True)
        ws = wb.active

        imported_count = 0
        user_id = request.session.get('ses_userID')
        updater = MyUser.objects.filter(id=user_id).first() if user_id else None

        for row in ws.iter_rows(min_row=3, values_only=True):
            if not row or not row[0]:
                continue

            sales_name = str(row[0]).strip()
            company_str = str(row[1]).strip() if len(row) > 1 and row[1] else ''

            user = MyUser.objects.filter(
                first_name__iexact=sales_name,
                user_extinfo__department_id=SALES_DEPARTMENT_ID
            ).first()

            if not user:
                user = MyUser.objects.filter(
                    first_name__icontains=sales_name,
                    user_extinfo__department_id=SALES_DEPARTMENT_ID
                ).first()

            if not user:
                continue

            company_obj = None
            if company_str:
                company_obj = Business_Sol_info.objects.filter(
                    bvm_business__icontains=company_str
                ).first()

            target_calls = int(row[2]) if len(row) > 2 and row[2] else 0
            tgt_rev_exist = float(row[14]) if len(row) > 14 and row[14] else 0.0
            tgt_rev_new = float(row[15]) if len(row) > 15 and row[15] else 0.0
            tgt_cust_total = int(row[16]) if len(row) > 16 and row[16] else 0
            tgt_cust_new = int(row[17]) if len(row) > 17 and row[17] else 0
            tgt_cust_exist = int(row[18]) if len(row) > 18 and row[18] else 0
            tgt_cust_onboard = int(row[19]) if len(row) > 19 and row[19] else 0

            target = Sales_target_info.objects.filter(st_sales_person=user).order_by('-id').first()
            if not target:
                now = timezone.now().date()
                target = Sales_target_info(
                    st_sales_person=user,
                    st_start_date=now.replace(day=1),
                    st_end_date=now
                )

            if company_obj:
                target.st_company = company_obj
            target.st_target_calls = target_calls
            target.st_target_revenue_existing = tgt_rev_exist
            target.st_target_revenue_new = tgt_rev_new
            target.st_target_revenue = (tgt_rev_exist + tgt_rev_new) * 100000.0
            target.st_target_customer = tgt_cust_total or (tgt_cust_new + tgt_cust_exist)
            target.st_target_customers_new = tgt_cust_new
            target.st_target_customers_existing = tgt_cust_exist
            target.st_target_customers_onboard = tgt_cust_onboard
            if updater:
                target.st_updated_by = updater
            target.save()
            imported_count += 1

        messages.success(request, f"Successfully imported targets for {imported_count} sales executives.")
    except Exception as e:
        messages.error(request, f"Error importing Excel file: {str(e)}")

    return redirect('sales_metrics_dashboard')
