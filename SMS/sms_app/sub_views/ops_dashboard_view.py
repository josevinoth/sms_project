import calendar
from datetime import datetime, date, timedelta
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone

from ..models import (
    Vehicle_allotmentInfo,
    EnquirynoteInfo,
    Enquirynotevehicle,
    CustomerInfo,
    TransInvoiceInfo,
    TripdetailInfo,
    Location_info,
    User_extInfo,
    Vendor_info,
    MyUser
)
from .general_utils import is_tms_manager


def ops_dashboard(request):
    """
    Main entry point for Transport Operations (Ops) Dashboard.
    Placed below CS Dashboard in Home Page navigation.
    """
    first_name = request.session.get('first_name', 'Admin')
    user_id = request.session.get('ses_userID')

    default_branch_id = 'all'
    try:
        bvm_maa_loc = Location_info.objects.filter(loc_name='BVM MAA').first()
        if bvm_maa_loc:
            default_branch_id = str(bvm_maa_loc.id)
    except Exception as e:
        print(f"OPS EMPLOYEES EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

    if user_id:
        try:
            current_user_ext = User_extInfo.objects.get(user_id=user_id)
            if current_user_ext.emp_branch_id:
                default_branch_id = str(current_user_ext.emp_branch_id)
        except Exception:
            pass

    branches = Location_info.objects.all().order_by('loc_name')
    today_dt = timezone.localtime(timezone.now()).date()

    # Operations department representatives ONLY (BVM Trans Solutions pvt ltd desk/allotment staff, excluding Drivers)
    ops_employees = []
    try:
        ops_ext_qs = User_extInfo.objects.filter(
            department__dept_name='Operations',
            emp_organisation__bvm_business__icontains='Trans',
            user__is_active=True,
            is_approved=True
        ).exclude(
            emp_designation__des_designation_name='Driver'
        ).select_related('user', 'emp_branch').order_by('user__first_name')

        for ue in ops_ext_qs:
            u = ue.user
            b_id = ue.emp_branch_id if ue.emp_branch else ''
            b_name = ue.emp_branch.loc_name if ue.emp_branch else ''
            full_name = u.get_full_name() or u.first_name
            ops_employees.append({
                'id': u.id,
                'name': full_name,
                'branch_id': b_id,
                'branch_name': b_name,
            })
    except Exception as e:
        print(f"OPS EMPLOYEES EXCEPTION: {e}")

    # Default to Last 30 Days so active operational transactions appear immediately
    default_from_date = today_dt - timedelta(days=30)
    default_to_date = today_dt

    month_start = today_dt.replace(day=1)
    start_of_week = today_dt - timedelta(days=today_dt.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    last_60_start = today_dt - timedelta(days=60)

    iso_year, iso_week, _ = today_dt.isocalendar()

    current_user_id = user_id if user_id else (request.user.id if request.user.is_authenticated else None)

    context = {
        'first_name': first_name,
        'current_user_id': current_user_id,
        'branches': branches,
        'ops_employees': ops_employees,
        'default_branch_id': default_branch_id,
        'today_date': today_dt.strftime('%Y-%m-%d'),
        'default_from_date': default_from_date.strftime('%Y-%m-%d'),
        'default_to_date': default_to_date.strftime('%Y-%m-%d'),
        'current_week_start': start_of_week.strftime('%Y-%m-%d'),
        'current_week_end': end_of_week.strftime('%Y-%m-%d'),
        'month_start_date': month_start.strftime('%Y-%m-%d'),
        'last_30_start_date': default_from_date.strftime('%Y-%m-%d'),
        'last_60_start_date': last_60_start.strftime('%Y-%m-%d'),
        'current_week_number': iso_week,
        'current_month_name': today_dt.strftime('%B %Y'),
    }
    return render(request, "asset_mgt_app/ops_dashboard.html", context)


def get_ops_dashboard_data(request):
    """
    API returning allotment department data and visual insights for the Ops Transport Dashboard:
    1. Top summary KPI insight cards (Single line of 10 cards)
    2. Allotment department particulars data matrix (Takes full left column, AR strictly excluded)
    3. Multi-dimensional visual charts: Fleet Sourcing mix, Funnel dropoff, Vendor utilization
    4. Top vendors breakdown (Shared side-by-side with market logistics)
    5. Lost Customer: Number of vendors who gave vehicles in the past month from selected filter but none in current period
    """
    today_dt = timezone.localtime(timezone.now()).date()

    branch_id = request.GET.get('branch_id', 'all')
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    scale = request.GET.get('scale', 'branch')
    ops_user_id = request.GET.get('ops_user_id', 'all')

    target_ops_id = None
    if ops_user_id and ops_user_id != 'all':
        try:
            target_ops_id = int(ops_user_id)
        except ValueError:
            target_ops_id = None
    elif scale == 'personal':
        ses_uid = request.session.get('ses_userID') or (request.user.id if request.user.is_authenticated else None)
        if ses_uid:
            try:
                target_ops_id = int(ses_uid)
            except ValueError:
                target_ops_id = None

    # Selected period range (default to last 30 days)
    if from_date_str and to_date_str:
        try:
            period_start = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            period_end = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        except Exception:
            period_start = today_dt - timedelta(days=30)
            period_end = today_dt
    else:
        period_start = today_dt - timedelta(days=30)
        period_end = today_dt

    # Month-till-Date (MTD) definition
    if period_start.year == today_dt.year and period_start.month == today_dt.month:
        mtd_start = date(today_dt.year, today_dt.month, 1)
        mtd_end = today_dt
    else:
        mtd_year = period_start.year
        mtd_month = period_start.month
        mtd_start = date(mtd_year, mtd_month, 1)
        _, last_day_of_month = calendar.monthrange(mtd_year, mtd_month)
        mtd_end = date(mtd_year, mtd_month, last_day_of_month)

    iso_year, iso_week, _ = period_end.isocalendar()

    # Branch filters
    branch_user_ids = []
    branch_code = None
    if branch_id and branch_id != 'all':
        branch_loc = Location_info.objects.filter(id=branch_id).first()
        if branch_loc and branch_loc.loc_name:
            branch_code = branch_loc.loc_name.split()[-1]
        branch_user_ids = list(User_extInfo.objects.filter(
            emp_branch_id=branch_id,
            user__is_active=True
        ).values_list('user_id', flat=True))

    def filter_allots(start_d, end_d):
        date_q = (
            Q(va_created_at__date__gte=start_d, va_created_at__date__lte=end_d) |
            Q(va_enquirynumber__en_created_at__date__gte=start_d, va_enquirynumber__en_created_at__date__lte=end_d)
        )
        qs = Vehicle_allotmentInfo.objects.filter(date_q).exclude(va_status_id__in=[2, 4])
        if branch_id and branch_id != 'all':
            b_q = Q(va_enquirynumber__en_assignedto_id__in=branch_user_ids)
            if branch_code:
                b_q |= Q(va_enquirynumber__en_enquirynumber__icontains=branch_code)
            qs = qs.filter(b_q)
        if target_ops_id:
            qs = qs.filter(va_updated_by_id=target_ops_id)
        return qs

    def filter_enquiries(start_d, end_d, linked_allots=None):
        date_q = Q(en_created_at__date__gte=start_d, en_created_at__date__lte=end_d)
        if linked_allots is not None:
            linked_enq_ids = linked_allots.values_list('va_enquirynumber_id', flat=True)
            date_q |= Q(id__in=linked_enq_ids)

        qs = EnquirynoteInfo.objects.filter(date_q)
        if branch_id and branch_id != 'all':
            b_q = Q(en_assignedto_id__in=branch_user_ids)
            if branch_code:
                b_q |= Q(en_enquirynumber__icontains=branch_code)
            qs = qs.filter(b_q)
        if target_ops_id:
            if linked_allots is not None:
                qs = qs.filter(Q(id__in=linked_allots.values_list('va_enquirynumber_id', flat=True)) | Q(en_assignedto_id=target_ops_id))
            else:
                qs = qs.filter(Q(vehicle_allotmentinfo__va_updated_by_id=target_ops_id) | Q(en_assignedto_id=target_ops_id)).distinct()
        return qs

    # 1. Selected Period Data
    p_allots = filter_allots(period_start, period_end)
    p_enquiries = filter_enquiries(period_start, period_end, linked_allots=p_allots)

    # Booking (Demanded)
    p_booking = Enquirynotevehicle.objects.filter(
        env_enquirynumber__in=p_enquiries
    ).aggregate(total=Sum('env_quantity'))['total']
    if p_booking is None or p_booking == 0:
        p_booking = p_enquiries.count()

    p_placed = p_allots.count()
    p_unplaced = max(p_booking - p_placed, 0)
    p_booking_placed_pct = round((p_placed / p_booking) * 100, 1) if p_booking > 0 else 0.0

    # Invoiced trips linked to period enquiries/allotments
    p_trips = TripdetailInfo.objects.filter(tr_enquirynumber__in=p_enquiries)
    p_invoiced = TransInvoiceInfo.objects.filter(
        Q(ti_trip__in=p_trips) | Q(ti_consignment__co_enquirynumber__in=p_enquiries)
    ).values('ti_trip_id').distinct().count()
    p_ready_inv = p_trips.filter(tc_financestatus_id=9).count()
    p_total_invoiced_or_ready = max(p_invoiced, p_ready_inv)
    p_pending_billing = max(p_placed - p_total_invoiced_or_ready, 0)
    p_placed_invoiced_pct = round((p_total_invoiced_or_ready / p_placed) * 100, 1) if p_placed > 0 else 0.0

    # Fleet source breakdowns (OWN, ATTC, MKT Local, MKT OS)
    p_placed_own = p_allots.filter(va_vehiclesource_id=1).count()
    p_placed_attc = p_allots.filter(va_vehiclesource_id=2).count()
    p_placed_mkt_local = p_allots.filter(va_vehiclesource_id=3, va_enquirynumber__en_trip_type_id=1).count()
    p_placed_mkt_os = p_allots.filter(va_vehiclesource_id=3, va_enquirynumber__en_trip_type_id=2).count()

    p_own_share = round((p_placed_own / p_placed) * 100, 1) if p_placed > 0 else 0.0
    p_attc_share = round((p_placed_attc / p_placed) * 100, 1) if p_placed > 0 else 0.0
    p_mkt_local_share = round((p_placed_mkt_local / p_placed) * 100, 1) if p_placed > 0 else 0.0
    p_mkt_os_share = round((p_placed_mkt_os / p_placed) * 100, 1) if p_placed > 0 else 0.0

    # Distinct vendors used
    p_vendors_mkt_local = p_allots.filter(
        va_vehiclesource_id=3,
        va_enquirynumber__en_trip_type_id=1,
        va_vendor__isnull=False
    ).values('va_vendor').distinct().count()

    p_vendors_mkt_os = p_allots.filter(
        va_vehiclesource_id=3,
        va_enquirynumber__en_trip_type_id=2,
        va_vendor__isnull=False
    ).values('va_vendor').distinct().count()

    p_avg_local_per_vendor = round(p_placed_mkt_local / p_vendors_mkt_local, 1) if p_vendors_mkt_local > 0 else 0.0
    p_avg_os_per_vendor = round(p_placed_mkt_os / p_vendors_mkt_os, 1) if p_vendors_mkt_os > 0 else 0.0

    # Customer dynamics: New Customers
    if target_ops_id:
        p_cust_qs = CustomerInfo.objects.filter(
            id__in=p_enquiries.values_list('en_customername_id', flat=True),
            cu_created_at__date__gte=period_start,
            cu_created_at__date__lte=period_end
        )
    else:
        p_cust_qs = CustomerInfo.objects.filter(
            cu_created_at__date__gte=period_start,
            cu_created_at__date__lte=period_end
        )
    p_new_cust = p_cust_qs.count()

    # Lost Customer: Defined strictly as the number of vendors who gave vehicles in the past month from selected filter,
    # but did not provide any vehicles in the current selected filter period
    past_month_start = period_start - timedelta(days=30)
    past_month_end = period_start - timedelta(days=1)

    past_month_allots = filter_allots(past_month_start, past_month_end).filter(va_vendor__isnull=False)
    past_month_vendors = set(past_month_allots.values_list('va_vendor_id', flat=True))

    current_period_allots = p_allots.filter(va_vendor__isnull=False)
    current_period_vendors = set(current_period_allots.values_list('va_vendor_id', flat=True))

    lost_vendor_ids = past_month_vendors - current_period_vendors
    p_lost_cust = len(lost_vendor_ids)
    lost_vendor_names = list(Vendor_info.objects.filter(id__in=lost_vendor_ids).values_list('vend_name', flat=True)[:10])

    # 2. Month-till-Date (MTD) Data
    m_allots = filter_allots(mtd_start, mtd_end)
    m_enquiries = filter_enquiries(mtd_start, mtd_end, linked_allots=m_allots)

    m_booking = Enquirynotevehicle.objects.filter(
        env_enquirynumber__in=m_enquiries
    ).aggregate(total=Sum('env_quantity'))['total']
    if m_booking is None or m_booking == 0:
        m_booking = m_enquiries.count()

    m_placed = m_allots.count()
    m_booking_placed_pct = round((m_placed / m_booking) * 100, 1) if m_booking > 0 else 0.0

    m_trips = TripdetailInfo.objects.filter(tr_enquirynumber__in=m_enquiries)
    m_invoiced = TransInvoiceInfo.objects.filter(
        Q(ti_trip__in=m_trips) | Q(ti_consignment__co_enquirynumber__in=m_enquiries)
    ).values('ti_trip_id').distinct().count()
    m_ready_inv = m_trips.filter(tc_financestatus_id=9).count()
    m_total_invoiced_or_ready = max(m_invoiced, m_ready_inv)
    m_placed_invoiced_pct = round((m_total_invoiced_or_ready / m_placed) * 100, 1) if m_placed > 0 else 0.0

    m_placed_own = m_allots.filter(va_vehiclesource_id=1).count()
    m_placed_attc = m_allots.filter(va_vehiclesource_id=2).count()
    m_placed_mkt_local = m_allots.filter(va_vehiclesource_id=3, va_enquirynumber__en_trip_type_id=1).count()
    m_placed_mkt_os = m_allots.filter(va_vehiclesource_id=3, va_enquirynumber__en_trip_type_id=2).count()

    m_own_share = round((m_placed_own / m_placed) * 100, 1) if m_placed > 0 else 0.0
    m_attc_share = round((m_placed_attc / m_placed) * 100, 1) if m_placed > 0 else 0.0
    m_mkt_local_share = round((m_placed_mkt_local / m_placed) * 100, 1) if m_placed > 0 else 0.0
    m_mkt_os_share = round((m_placed_mkt_os / m_placed) * 100, 1) if m_placed > 0 else 0.0

    m_vendors_mkt_local = m_allots.filter(
        va_vehiclesource_id=3,
        va_enquirynumber__en_trip_type_id=1,
        va_vendor__isnull=False
    ).values('va_vendor').distinct().count()

    m_vendors_mkt_os = m_allots.filter(
        va_vehiclesource_id=3,
        va_enquirynumber__en_trip_type_id=2,
        va_vendor__isnull=False
    ).values('va_vendor').distinct().count()

    if target_ops_id:
        m_new_cust = CustomerInfo.objects.filter(
            id__in=m_enquiries.values_list('en_customername_id', flat=True),
            cu_created_at__date__gte=mtd_start,
            cu_created_at__date__lte=mtd_end
        ).count()
    else:
        m_new_cust = CustomerInfo.objects.filter(
            cu_created_at__date__gte=mtd_start,
            cu_created_at__date__lte=mtd_end
        ).count()

    # MTD Lost Customer (vendors from month prior to mtd_start not active in MTD)
    m_past_month_start = mtd_start - timedelta(days=30)
    m_past_month_end = mtd_start - timedelta(days=1)
    m_past_vends = set(filter_allots(m_past_month_start, m_past_month_end).filter(va_vendor__isnull=False).values_list('va_vendor_id', flat=True))
    m_curr_vends = set(m_allots.filter(va_vendor__isnull=False).values_list('va_vendor_id', flat=True))
    m_lost_cust = len(m_past_vends - m_curr_vends)

    # 3. Top Market Vendors Utilized (Insight Ranking)
    top_vendors_qs = p_allots.filter(
        va_vehiclesource_id=3,
        va_vendor__isnull=False
    ).values('va_vendor__vend_name').annotate(
        total_trips=Count('id'),
        local_trips=Count('id', filter=Q(va_enquirynumber__en_trip_type_id=1)),
        os_trips=Count('id', filter=Q(va_enquirynumber__en_trip_type_id=2))
    ).order_by('-total_trips')[:8]

    top_vendors_list = []
    top_vendors_chart_names = []
    top_vendors_chart_counts = []
    for tv in top_vendors_qs:
        v_name = tv['va_vendor__vend_name'] or 'Unknown Vendor'
        top_vendors_list.append({
            'name': v_name,
            'total': tv['total_trips'],
            'local': tv['local_trips'],
            'os': tv['os_trips'],
            'share_pct': f"{round((tv['total_trips'] / (p_placed_mkt_local + p_placed_mkt_os)) * 100, 1)}%" if (p_placed_mkt_local + p_placed_mkt_os) > 0 else "0.0%"
        })
        top_vendors_chart_names.append(v_name[:15])
        top_vendors_chart_counts.append(tv['total_trips'])

    # 4. Particulars Matrix (The 10 core allotment department items, AR strictly excluded!)
    particulars_table = [
        {
            'name': 'New Customer On-board',
            'icon': 'fas fa-user-plus',
            'icon_color': '#38bdf8',
            'period_val': str(p_new_cust),
            'mtd_val': str(m_new_cust),
            'insight': f"+{p_new_cust} New Accounts",
            'badge_color': '#38bdf8',
            'badge_bg': 'rgba(56, 189, 248, 0.15)',
            'subtext': 'Direct onboardings'
        },
        {
            'name': 'Lost Customer',
            'icon': 'fas fa-user-minus',
            'icon_color': '#f87171',
            'period_val': str(p_lost_cust),
            'mtd_val': str(m_lost_cust),
            'insight': f"{p_lost_cust} Inactive Vendors",
            'badge_color': '#f87171' if p_lost_cust > 0 else '#10b981',
            'badge_bg': 'rgba(239, 68, 68, 0.15)' if p_lost_cust > 0 else 'rgba(16, 185, 129, 0.15)',
            'subtext': 'Zero vehicles from past month'
        },
        # AR is strictly EXCLUDED as requested
        {
            'name': 'Booking Vs Placed',
            'icon': 'fas fa-truck-loading',
            'icon_color': '#60a5fa',
            'period_val': f"{p_booking_placed_pct:.1f}%",
            'mtd_val': f"{m_booking_placed_pct:.1f}%",
            'insight': f"{p_placed} Placed / {p_booking} Demanded",
            'badge_color': '#10b981' if p_booking_placed_pct >= 90 else '#f59e0b',
            'badge_bg': 'rgba(16, 185, 129, 0.15)' if p_booking_placed_pct >= 90 else 'rgba(245, 158, 11, 0.15)',
            'subtext': f"{p_unplaced} Demands unfulfilled"
        },
        {
            'name': 'Placed Vs Invoiced',
            'icon': 'fas fa-file-invoice-dollar',
            'icon_color': '#34d399',
            'period_val': f"{p_placed_invoiced_pct:.1f}%",
            'mtd_val': f"{m_placed_invoiced_pct:.1f}%",
            'insight': f"{p_total_invoiced_or_ready} Invoiced / {p_placed} Placed",
            'badge_color': '#10b981' if p_placed_invoiced_pct >= 80 else '#f59e0b',
            'badge_bg': 'rgba(16, 185, 129, 0.15)' if p_placed_invoiced_pct >= 80 else 'rgba(245, 158, 11, 0.15)',
            'subtext': f"{p_pending_billing} Pending invoicing"
        },
        {
            'name': 'Placed OWN',
            'icon': 'fas fa-truck-moving',
            'icon_color': '#3b82f6',
            'period_val': f"{p_placed_own} ({p_own_share}%)",
            'mtd_val': f"{m_placed_own} ({m_own_share}%)",
            'insight': f"{p_own_share}% Fleet Share",
            'badge_color': '#3b82f6',
            'badge_bg': 'rgba(59, 130, 246, 0.15)',
            'subtext': 'Company owned assets'
        },
        {
            'name': 'Placed ATTC',
            'icon': 'fas fa-link',
            'icon_color': '#f59e0b',
            'period_val': f"{p_placed_attc} ({p_attc_share}%)",
            'mtd_val': f"{m_placed_attc} ({m_attc_share}%)",
            'insight': f"{p_attc_share}% Fleet Share",
            'badge_color': '#f59e0b',
            'badge_bg': 'rgba(245, 158, 11, 0.15)',
            'subtext': 'Contract attached fleet'
        },
        {
            'name': 'Placed MKT (Local)',
            'icon': 'fas fa-city',
            'icon_color': '#10b981',
            'period_val': f"{p_placed_mkt_local} ({p_mkt_local_share}%)",
            'mtd_val': f"{m_placed_mkt_local} ({m_mkt_local_share}%)",
            'insight': f"{p_mkt_local_share}% Fleet Share",
            'badge_color': '#10b981',
            'badge_bg': 'rgba(16, 185, 129, 0.15)',
            'subtext': f"{p_avg_local_per_vendor} trips/vendor"
        },
        {
            'name': 'Placed MKT (OS)',
            'icon': 'fas fa-road',
            'icon_color': '#a855f7',
            'period_val': f"{p_placed_mkt_os} ({p_mkt_os_share}%)",
            'mtd_val': f"{m_placed_mkt_os} ({m_mkt_os_share}%)",
            'insight': f"{p_mkt_os_share}% Fleet Share",
            'badge_color': '#a855f7',
            'badge_bg': 'rgba(168, 85, 247, 0.15)',
            'subtext': f"{p_avg_os_per_vendor} trips/vendor"
        },
        {
            'name': 'MKT (Local) No of vendors used',
            'icon': 'fas fa-store-alt',
            'icon_color': '#14b8a6',
            'period_val': str(p_vendors_mkt_local),
            'mtd_val': str(m_vendors_mkt_local),
            'insight': f"{p_vendors_mkt_local} Distinct Vendors",
            'badge_color': '#2dd4bf',
            'badge_bg': 'rgba(20, 184, 166, 0.15)',
            'subtext': f"{p_avg_local_per_vendor} avg load/vendor"
        },
        {
            'name': 'MKT (OS) No of vendors used',
            'icon': 'fas fa-warehouse',
            'icon_color': '#0ea5e9',
            'period_val': str(p_vendors_mkt_os),
            'mtd_val': str(m_vendors_mkt_os),
            'insight': f"{p_vendors_mkt_os} Distinct Vendors",
            'badge_color': '#38bdf8',
            'badge_bg': 'rgba(14, 165, 233, 0.15)',
            'subtext': f"{p_avg_os_per_vendor} avg load/vendor"
        },
    ]

    # Top highlight cards: Display the OVERALL values of the particulars (independent of date filter)
    o_allots_qs = Vehicle_allotmentInfo.objects.exclude(va_status_id__in=[2, 4])
    if branch_id and branch_id != 'all':
        b_q = Q(va_enquirynumber__en_assignedto_id__in=branch_user_ids)
        if branch_code:
            b_q |= Q(va_enquirynumber__en_enquirynumber__icontains=branch_code)
        o_allots_qs = o_allots_qs.filter(b_q)
    if target_ops_id:
        o_allots_qs = o_allots_qs.filter(va_updated_by_id=target_ops_id)

    o_placed = o_allots_qs.count()

    o_enq_qs = EnquirynoteInfo.objects.all()
    if branch_id and branch_id != 'all':
        b_q = Q(en_assignedto_id__in=branch_user_ids)
        if branch_code:
            b_q |= Q(en_enquirynumber__icontains=branch_code)
        o_enq_qs = o_enq_qs.filter(b_q)
    if target_ops_id:
        o_enq_qs = o_enq_qs.filter(Q(vehicle_allotmentinfo__va_updated_by_id=target_ops_id) | Q(en_assignedto_id=target_ops_id)).distinct()

    o_booking = Enquirynotevehicle.objects.filter(
        env_enquirynumber__in=o_enq_qs
    ).aggregate(total=Sum('env_quantity'))['total']
    if o_booking is None or o_booking == 0:
        o_booking = o_enq_qs.count()

    o_booking_placed_pct = round((o_placed / o_booking) * 100, 1) if o_booking > 0 else 0.0

    o_trips = TripdetailInfo.objects.filter(tr_enquirynumber__in=o_enq_qs)
    o_invoiced = TransInvoiceInfo.objects.filter(
        Q(ti_trip__in=o_trips) | Q(ti_consignment__co_enquirynumber__in=o_enq_qs)
    ).values('ti_trip_id').distinct().count()
    o_ready_inv = o_trips.filter(tc_financestatus_id=9).count()
    o_total_invoiced = max(o_invoiced, o_ready_inv)
    o_placed_invoiced_pct = round((o_total_invoiced / o_placed) * 100, 1) if o_placed > 0 else 0.0

    o_placed_own = o_allots_qs.filter(va_vehiclesource_id=1).count()
    o_placed_attc = o_allots_qs.filter(va_vehiclesource_id=2).count()
    o_placed_mkt_local = o_allots_qs.filter(va_vehiclesource_id=3, va_enquirynumber__en_trip_type_id=1).count()
    o_placed_mkt_os = o_allots_qs.filter(va_vehiclesource_id=3, va_enquirynumber__en_trip_type_id=2).count()

    o_own_share = round((o_placed_own / o_placed) * 100, 1) if o_placed > 0 else 0.0
    o_attc_share = round((o_placed_attc / o_placed) * 100, 1) if o_placed > 0 else 0.0
    o_mkt_local_share = round((o_placed_mkt_local / o_placed) * 100, 1) if o_placed > 0 else 0.0
    o_mkt_os_share = round((o_placed_mkt_os / o_placed) * 100, 1) if o_placed > 0 else 0.0

    o_vendors_mkt_local = o_allots_qs.filter(
        va_vehiclesource_id=3,
        va_enquirynumber__en_trip_type_id=1,
        va_vendor__isnull=False
    ).values('va_vendor').distinct().count()

    o_vendors_mkt_os = o_allots_qs.filter(
        va_vehiclesource_id=3,
        va_enquirynumber__en_trip_type_id=2,
        va_vendor__isnull=False
    ).values('va_vendor').distinct().count()

    if target_ops_id:
        o_new_cust = CustomerInfo.objects.filter(
            id__in=o_enq_qs.values_list('en_customername_id', flat=True)
        ).count()
    else:
        o_new_cust = CustomerInfo.objects.count()

    recent_30_vends = set(Vehicle_allotmentInfo.objects.filter(
        va_created_at__date__gte=today_dt - timedelta(days=30),
        va_created_at__date__lte=today_dt,
        va_vendor__isnull=False
    ).values_list('va_vendor_id', flat=True))
    all_branch_vends = set(o_allots_qs.filter(va_vendor__isnull=False).values_list('va_vendor_id', flat=True))
    o_lost_cust = len(all_branch_vends - recent_30_vends)

    # Top highlight cards: Display the OVERALL values of the particulars
    top_cards = {
        'booking_placed_rate': f"{o_booking_placed_pct:.1f}%",
        'booking_placed_sub': f"{o_placed} Placed / {o_booking} Demanded",
        'placed_invoiced_rate': f"{o_placed_invoiced_pct:.1f}%",
        'placed_invoiced_sub': f"{o_total_invoiced} Invoiced / {o_placed} Placed",
        'placed_own': o_placed_own,
        'placed_own_pct': f"{o_own_share}%",
        'placed_attc': o_placed_attc,
        'placed_attc_pct': f"{o_attc_share}%",
        'placed_mkt_local': o_placed_mkt_local,
        'placed_mkt_local_pct': f"{o_mkt_local_share}%",
        'placed_mkt_os': o_placed_mkt_os,
        'placed_mkt_os_pct': f"{o_mkt_os_share}%",
        'vendors_mkt_local': o_vendors_mkt_local,
        'vendors_mkt_os': o_vendors_mkt_os,
        'new_customers': o_new_cust,
        'lost_customers': o_lost_cust,
        'total_placed': o_placed,
        'total_demanded': o_booking,
    }

    # Chart 1: Fleet Sourcing Breakdown (Completely Distinct Colors: Blue, Amber, Green, Purple)
    chart_sourcing = {
        'labels': ['Placed OWN', 'Placed ATTC', 'Placed MKT (Local)', 'Placed MKT (OS)'],
        'data': [p_placed_own, p_placed_attc, p_placed_mkt_local, p_placed_mkt_os],
        'colors': ['rgba(59, 130, 246, 0.90)', 'rgba(245, 158, 11, 0.90)', 'rgba(16, 185, 129, 0.90)', 'rgba(168, 85, 247, 0.90)'],
    }

    # Chart 2: Fulfillment & Invoicing Multi-stage Conversion Funnel
    chart_funnel = {
        'labels': ['1. Demanded Bookings', '2. Placed Allotments', '3. Invoiced / Ready'],
        'data': [p_booking, p_placed, p_total_invoiced_or_ready],
        'colors': ['rgba(59, 130, 246, 0.85)', 'rgba(16, 185, 129, 0.85)', 'rgba(217, 119, 6, 0.85)'],
        'fulfillment_pct': p_booking_placed_pct,
        'invoicing_pct': p_placed_invoiced_pct
    }

    # Chart 3: Market Logistics Local vs OS Comparison
    chart_market_comp = {
        'labels': ['Market Local', 'Market Outstation (OS)'],
        'placed': [p_placed_mkt_local, p_placed_mkt_os],
        'vendors': [p_vendors_mkt_local, p_vendors_mkt_os],
        'avg_per_vendor': [p_avg_local_per_vendor, p_avg_os_per_vendor]
    }

    # Chart 4: Top Vendors Breakdown
    chart_top_vendors = {
        'labels': top_vendors_chart_names,
        'data': top_vendors_chart_counts
    }

    period_hdr = f"Selected Period ({period_start.strftime('%d %b')} - {period_end.strftime('%d %b %Y')})"
    mtd_hdr = f"Month till Date ({mtd_start.strftime('%d %b')} - {mtd_end.strftime('%d %b %Y')})"

    return JsonResponse({
        'status': 'success',
        'period_header': period_hdr,
        'mtd_header': mtd_hdr,
        'week_number': iso_week,
        'top_cards': top_cards,
        'particulars_table': particulars_table,
        'chart_sourcing': chart_sourcing,
        'chart_funnel': chart_funnel,
        'chart_market_comp': chart_market_comp,
        'chart_top_vendors': chart_top_vendors,
        'top_vendors_list': top_vendors_list,
        'lost_vendors_list': lost_vendor_names
    })
