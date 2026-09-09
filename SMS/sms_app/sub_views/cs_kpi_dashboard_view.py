from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Sum, Q, F
from django.utils import timezone
from datetime import datetime, date, timedelta

from ..sub_models.tripdetail_mod import TripdetailInfo, TripAttachmentInfo
from ..sub_models.enquirynote_mod import EnquirynoteInfo
from ..sub_models.enquirynote_vehicle_mod import Enquirynotevehicle
from ..sub_models.vehicle_allotment_mod import Vehicle_allotmentInfo
from ..sub_models.consignmentdetail_mod import ConsignmentdetailInfo
from ..sub_models.trans_invoice_mod import TransInvoiceInfo
from ..sub_models.trans_customer_claims_mod import TransCustomerClaimsInfo
from ..sub_models.user_ext_mod import User_extInfo
from ..sub_models.location_info_mod import Location_info
from ..sub_models.my_user_mod import MyUser
from .general_utils import is_tms_manager
from .trans_invoice_view import calculate_trip_invoice_total
from .invoice_documents_view import get_enquiry_special_sell, get_enquiry_standard_sell
from .tripclosure_add_view import get_allotment_sale_rate
from ..sub_models.consignmentgoods_mod import ConsignmentgoodsInfo
from collections import defaultdict

CS_DEPARTMENT_ID = 4


def get_color_code(percentage):
    """
    Color coding rules:
    Red: 0% - 35%
    Orange: 36% - 70%
    Green: 71% - 100%
    Blue: > 100%
    """
    if percentage <= 35:
        return 'red', '#ef4444', 'Red'
    elif percentage <= 70:
        return 'orange', '#f59e0b', 'Orange'
    elif percentage <= 100:
        return 'green', '#10b981', 'Green'
    else:
        return 'blue', '#3b82f6', 'Blue'


def cs_kpi_dashboard(request):
    first_name = request.session.get('first_name', 'Admin')
    user_id = request.session.get('ses_userID')

    current_user_ext = None
    user_role_id = None
    current_user_id = None
    dropdown_disabled = False
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
            user_role_id = current_user_ext.emp_role_id if current_user_ext.emp_role else None
            current_user_id = user_id
            if current_user_ext.emp_branch_id:
                default_branch_id = str(current_user_ext.emp_branch_id)
        except Exception:
            pass

    is_cs_user = (current_user_ext and current_user_ext.department_id == CS_DEPARTMENT_ID)
    _is_tms_mgr = is_tms_manager(user_id)

    if user_role_id in [1, 3] or _is_tms_mgr or not user_id:
        dropdown_disabled = False
        default_employee_id = 'all'
    elif is_cs_user:
        dropdown_disabled = True
        default_employee_id = str(current_user_id)
    else:
        dropdown_disabled = False
        default_employee_id = 'all'

    # Customer Service representatives
    cs_employees_data = []
    try:
        cs_qs = User_extInfo.objects.filter(
            department_id=CS_DEPARTMENT_ID,
            user__is_active=True
        ).only('id', 'user_id', 'department_id', 'emp_branch_id', 'emp_role_id').select_related('user', 'emp_branch').order_by('user__first_name')
        for emp in cs_qs:
            cs_employees_data.append({
                'id': emp.user.id,
                'name': emp.user.first_name or emp.user.username,
                'branch_id': str(emp.emp_branch_id) if emp.emp_branch_id else '',
                'branch_name': emp.emp_branch.loc_name if emp.emp_branch else 'General'
            })
    except Exception:
        pass

    if not cs_employees_data:
        try:
            users = MyUser.objects.filter(is_active=True).order_by('first_name')
            for u in users:
                cs_employees_data.append({
                    'id': u.id,
                    'name': u.first_name or u.username,
                    'branch_name': 'General'
                })
        except Exception:
            pass

    # Branches
    branches = Location_info.objects.all().order_by('loc_name')

    today_str = timezone.localtime(timezone.now()).strftime('%Y-%m-%d')

    context = {
        'first_name': first_name,
        'cs_employees': cs_employees_data,
        'dropdown_disabled': dropdown_disabled,
        'default_employee_id': default_employee_id,
        'default_branch_id': default_branch_id,
        'user_role_id': user_role_id,
        'current_user_id': current_user_id,
        'branches': branches,
        'today_date': today_str,
    }
    return render(request, "asset_mgt_app/cs_kpi_dashboard.html", context)


def get_cs_kpi_dashboard_data(request):
    user_id = request.session.get('ses_userID')
    user_role_id = None
    current_user_ext = None
    enforce_user_filter = False

    if user_id:
        try:
            current_user_ext = User_extInfo.objects.get(user_id=user_id)
            user_role_id = current_user_ext.emp_role_id if current_user_ext.emp_role else None
        except Exception:
            pass

    is_cs_user = (current_user_ext and current_user_ext.department_id == CS_DEPARTMENT_ID)
    _is_tms_mgr = is_tms_manager(user_id)

    employee_id = request.GET.get('employee_id')
    if user_role_id in [1, 3] or _is_tms_mgr or not user_id:
        pass
    elif is_cs_user:
        enforce_user_filter = True
        employee_id = str(user_id)
    else:
        if employee_id and employee_id != 'all':
            employee_id = 'all'

    if enforce_user_filter and (employee_id == 'all' or not employee_id):
        employee_id = str(user_id)

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    branch_id = request.GET.get('branch_id')

    # Determine the count of CS representatives for scaling targets
    if employee_id and employee_id != 'all':
        cs_count = 1
    else:
        if branch_id and branch_id != 'all':
            cs_count = User_extInfo.objects.filter(
                department_id=CS_DEPARTMENT_ID,
                user__is_active=True,
                emp_branch_id=branch_id
            ).count()
        else:
            cs_count = User_extInfo.objects.filter(
                department_id=CS_DEPARTMENT_ID,
                user__is_active=True
            ).count()
        if cs_count == 0:
            cs_count = 1

    # Determine the count of working days in the selected date range
    # (Matching BVM operational policy: except Sunday all are working days)
    working_days_count = 1
    if from_date and to_date:
        try:
            d_start = datetime.strptime(from_date, '%Y-%m-%d').date()
            d_end = datetime.strptime(to_date, '%Y-%m-%d').date()
            if d_start <= d_end:
                w_count = 0
                cur_d = d_start
                while cur_d <= d_end:
                    if cur_d.weekday() != 6:  # Exclude Sunday (6)
                        w_count += 1
                    cur_d += timedelta(days=1)
                working_days_count = max(w_count, 1)
        except Exception:
            working_days_count = 1

    # Base targets (per single CS representative per working day) scaled by CS count and working days
    base_cnote_target = int(request.GET.get('cnote_target', 30) or 30)
    base_invoice_target = int(request.GET.get('invoice_target', 30) or 30)
    base_pod_target = int(request.GET.get('pod_target', 30) or 30)
    base_sow_target = int(request.GET.get('sow_target', 30) or 30)
    base_appreciation_target = int(request.GET.get('appreciation_target', 1) or 1)
    base_complaint_target = int(request.GET.get('complaint_target', 1) or 1)

    multiplier = cs_count * working_days_count

    cnote_target = base_cnote_target * multiplier
    invoice_target_total = base_invoice_target * multiplier
    pod_target_total = base_pod_target * multiplier
    sow_target = base_sow_target * multiplier
    appreciation_target = base_appreciation_target * multiplier
    complaint_target = base_complaint_target * multiplier

    # Base QuerySets
    enquiries_qs = EnquirynoteInfo.objects.all()
    if from_date:
        enquiries_qs = enquiries_qs.filter(en_created_at__date__gte=from_date)
    if to_date:
        enquiries_qs = enquiries_qs.filter(en_created_at__date__lte=to_date)

    branch_user_ids = []
    if branch_id and branch_id != 'all':
        branch_user_ids = list(User_extInfo.objects.filter(
            emp_branch_id=branch_id,
            user__is_active=True
        ).values_list('user_id', flat=True))
        enquiries_qs = enquiries_qs.filter(
            Q(en_assignedto_id__in=branch_user_ids) |
            Q(en_fromlocaion_id=branch_id)
        )

    if employee_id and employee_id != 'all':
        enquiries_qs = enquiries_qs.filter(en_assignedto_id=employee_id)

    # 1. Operational Funnel: Left Table Metrics
    # Veh Requested — sum of env_quantity from Enquirynotevehicle
    # (verified: env_quantity is correctly populated; using enquiry count as fallback was inaccurate)
    veh_requested = Enquirynotevehicle.objects.filter(
        env_enquirynumber__in=enquiries_qs
    ).aggregate(total=Sum('env_quantity'))['total'] or 0

    # Veh Allotted (Exclude cancelled status 4 and replaced status 2 so replacement vehicles are not double-counted)
    allotment_qs = Vehicle_allotmentInfo.objects.filter(va_enquirynumber__in=enquiries_qs).exclude(va_status_id__in=[2, 4])
    veh_allotted = allotment_qs.count()

    # Veh Not Allotted (Demands without vehicle placed)
    veh_not_allotted = max(veh_requested - veh_allotted, 0)

    # C-Notes Created — strictly based on the filtered vehicle requests / enquiries
    cnotes_qs = ConsignmentdetailInfo.objects.filter(
        co_enquirynumber__in=enquiries_qs
    ).distinct()

    cnotes_created = cnotes_qs.count()

    # Trips linked to these C-Notes
    trips_qs = TripdetailInfo.objects.filter(
        tr_consignmentnumber__in=cnotes_qs
    ).distinct()

    # C-Notes associated with at least one trip
    cnotes_with_trip_ids = set(
        trips_qs.values_list('tr_consignmentnumber_id', flat=True)
    )

    # Breakdown Categories:
    # 1. Not Associated with Trip
    not_associated_with_trip = cnotes_qs.exclude(id__in=cnotes_with_trip_ids).count()

    # 2. Awaiting Trip Approval (tc_financestatus_id = 8)
    awaiting_trip_approval = trips_qs.filter(tc_financestatus_id=8).count()

    # 3. Trip Started (tc_financestatus_id = 1 or tr_operational_status_id = 1)
    trip_started = trips_qs.filter(Q(tc_financestatus_id=1) | Q(tr_operational_status_id=1)).count()

    # 4. Trip Closed (tc_financestatus_id = 2 or tr_operational_status_id = 2)
    trip_closed = trips_qs.filter(Q(tc_financestatus_id=2) | Q(tr_operational_status_id=2)).count()

    # 5. Awaiting Trip Settlement (tc_financestatus_id = 4)
    awaiting_trip_settlement = trips_qs.filter(tc_financestatus_id=4).count()

    # 6. Trip Settled (tc_financestatus_id = 7)
    trip_settled = trips_qs.filter(tc_financestatus_id=7).count()

    # 7. Cancellation without Billing (tc_financestatus_id = 11)
    cancellation_without_billing = trips_qs.filter(tc_financestatus_id=11).count()

    # 8. Cancellation with Billing (tc_financestatus_id = 10)
    cancellation_with_billing = trips_qs.filter(tc_financestatus_id=10).count()

    # Collect all invoiced IDs matching Invoice Pending Report logic
    invoiced_trip_ids = list(TransInvoiceInfo.objects.filter(
        ti_trip__isnull=False
    ).values_list('ti_trip_id', flat=True))

    invoiced_cons_ids = TransInvoiceInfo.objects.filter(
        ti_consignment__isnull=False
    ).values_list('ti_consignment_id', flat=True)

    trips_from_cons = TripdetailInfo.objects.filter(
        tr_consignmentnumber_id__in=invoiced_cons_ids
    ).values_list('id', flat=True)

    invoiced_goods_ids = TransInvoiceInfo.objects.filter(
        ti_goods__isnull=False
    ).values_list('ti_goods_id', flat=True)

    cons_from_goods = ConsignmentgoodsInfo.objects.filter(
        id__in=invoiced_goods_ids
    ).values_list('cg_consignmentnumber_id', flat=True)

    trips_from_goods = TripdetailInfo.objects.filter(
        tr_consignmentnumber_id__in=cons_from_goods
    ).values_list('id', flat=True)

    all_invoiced_ids = set(invoiced_trip_ids) | set(trips_from_cons) | set(trips_from_goods)

    # 9. Ready For Invoice (tc_financestatus_id = 9 and not invoiced)
    ready_for_invoice = trips_qs.filter(
        tc_financestatus_id=9
    ).exclude(id__in=all_invoiced_ids).count()

    # 10. Invoice Completed (Trips with TransInvoiceInfo or linked invoice)
    invoiced_trips = trips_qs.filter(id__in=all_invoiced_ids).count()

    # Only return demo sample data if explicitly requested via query parameter ?is_sample=1
    is_sample_requested = (request.GET.get('is_sample') == '1')
    if is_sample_requested:
        # Default matching exact image values for demo
        veh_requested = 35
        veh_not_allotted = 1
        veh_allotted = 34
        cnotes_created = 32
        not_associated_with_trip = 2
        awaiting_trip_approval = 2
        trip_started = 15
        trip_closed = 5
        awaiting_trip_settlement = 2
        trip_settled = 2
        cancellation_without_billing = 0
        cancellation_with_billing = 0
        ready_for_invoice = 4
        invoiced_trips = 0

    reconciliation_total = (
        not_associated_with_trip +
        awaiting_trip_approval +
        trip_started +
        trip_closed +
        awaiting_trip_settlement +
        trip_settled +
        cancellation_without_billing +
        cancellation_with_billing +
        ready_for_invoice +
        invoiced_trips
    )

    # 2. Performance Targets & Achievements (Middle/Right Table)
    # KPI 1: No. of C-Notes for the day
    cnote_achieved = 25 if is_sample_requested else (cnotes_created if cnotes_created > 0 else 0)
    cnote_pct = round((cnote_achieved / cnote_target) * 100) if cnote_target > 0 else 0
    cnote_code_key, cnote_code_color, cnote_code_label = get_color_code(cnote_pct)

    # KPI 2: Invoice Submitted (Current date data with 3-working-days SLA tracking)
    def add_n_working_days(start_d, n_days=3):
        d = start_d
        count = 0
        while count < n_days:
            d = d + timedelta(days=1)
            if d.weekday() != 6:  # Exclude Sunday
                count += 1
        return d

    curr_date_obj = None
    if from_date:
        try:
            curr_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
        except Exception:
            curr_date_obj = timezone.now().date()
    else:
        curr_date_obj = timezone.now().date()

    # Calculate 3-working-days SLA deadline for this selected date
    sla_due_date = add_n_working_days(curr_date_obj, 3)
    sla_due_date_str = sla_due_date.strftime('%d-%m-%Y')
    today_date_obj = timezone.localtime(timezone.now()).date()

    # Current date's trips and invoice achievements
    current_day_total_trips = trips_qs.count()
    invoice_achieved_num = 26 if is_sample_requested else (ready_for_invoice + invoiced_trips)
    # The percentage is calculated directly against the day's C-Notes count (cnotes_created)
    invoice_base_cnotes = cnotes_created if cnotes_created > 0 else current_day_total_trips
    invoice_pct = round((invoice_achieved_num / invoice_base_cnotes) * 100) if invoice_base_cnotes > 0 else 0
    inv_code_key, inv_code_color, inv_code_label = get_color_code(invoice_pct)

    pending_trips_for_sla = max(current_day_total_trips - invoice_achieved_num, 0)

    if current_day_total_trips > 0 and pending_trips_for_sla == 0:
        sla_status = 'met'
        sla_badge_text = '✅ 100% SLA Met<br><span style="font-size:0.63rem; opacity:0.9;">(Within 3 Days)</span>'
        sla_badge_color = '#10b981'
    elif today_date_obj > sla_due_date and pending_trips_for_sla > 0:
        sla_status = 'overdue'
        sla_badge_text = f'⚠️ Overdue: {pending_trips_for_sla} Pending<br><span style="font-size:0.63rem; opacity:0.9;">(>3 Days SLA)</span>'
        sla_badge_color = '#ef4444'
    else:
        d_temp = today_date_obj
        days_left = 0
        while d_temp < sla_due_date:
            d_temp += timedelta(days=1)
            if d_temp.weekday() != 6:
                days_left += 1
        sla_status = 'in_progress'
        days_text = f"{days_left} Day{'s' if days_left != 1 else ''} Left"
        sla_badge_text = f'⏳ SLA Due: {sla_due_date_str}<br><span style="font-size:0.63rem; opacity:0.9;">({days_text})</span>'
        sla_badge_color = '#38bdf8'

    # KPI 3: POD SCAN
    pod_scanned_count = trips_qs.filter(
        Q(tc_pod_attachment__isnull=False) | Q(td_pod__isnull=False)
    ).exclude(tc_pod_attachment='', td_pod='').count()
    if is_sample_requested:
        pod_scanned_count = 26

    pod_target_display = str(pod_target_total)
    pod_achieved_display = str(pod_scanned_count)
    pod_pct = round((pod_scanned_count / pod_target_total) * 100) if pod_target_total > 0 else 0
    pod_code_key, pod_code_color, pod_code_label = get_color_code(pod_pct)

    # KPI 4: SOW, SOP, Ratesheet
    sow_achieved = 10 if is_sample_requested else TransInvoiceInfo.objects.filter(ti_trip__in=trips_qs, ti_sow__isnull=False).count()
    sow_pct = round((sow_achieved / sow_target) * 100) if sow_target > 0 else 0
    sow_code_key, sow_code_color, sow_code_label = get_color_code(sow_pct)

    # KPI 5: Customer -Appreciations
    appreciation_achieved = 0
    appreciation_pct = round((appreciation_achieved / appreciation_target) * 100) if appreciation_target > 0 else 0
    appr_code_key, appr_code_color, appr_code_label = get_color_code(appreciation_pct)

    # KPI 6: Customer -Complaints
    complaints_count = TransCustomerClaimsInfo.objects.filter(
        (Q(tcc_trip_date__gte=from_date) if from_date else Q()) &
        (Q(tcc_trip_date__lte=to_date) if to_date else Q())
    ).count()
    complaints_achieved = 0 if is_sample_requested else complaints_count
    complaints_pct = round((complaints_achieved / complaint_target) * 100) if complaint_target > 0 else 0
    comp_code_key, comp_code_color, comp_code_label = get_color_code(complaints_pct)

    kpi_rows = [
        {
            'name': 'C-Notes Created',
            'target': str(cnote_target),
            'achieved': str(cnote_achieved),
            'pct': f"{cnote_pct}%",
            'code_color': cnote_code_color,
            'code_label': cnote_code_label,
            'cs_count': cs_count,
            'days_count': working_days_count,
            'is_header': False
        },
        {
            'name': 'Invoice Submitted',
            'target': str(invoice_base_cnotes),
            'cnotes_count': invoice_base_cnotes,
            'achieved': str(invoice_achieved_num),
            'pct': f"{invoice_pct}%",
            'code_color': inv_code_color,
            'code_label': inv_code_label,
            'sla_status': sla_status,
            'sla_badge_text': sla_badge_text,
            'sla_badge_color': sla_badge_color,
            'sla_due_date': sla_due_date_str,
            'cs_count': cs_count,
            'days_count': working_days_count,
            'is_header': False
        },
        {
            'name': 'POD SCAN',
            'target': pod_target_display,
            'achieved': pod_achieved_display,
            'pct': f"{pod_pct}%",
            'code_color': pod_code_color,
            'code_label': pod_code_label,
            'cs_count': cs_count,
            'days_count': working_days_count,
            'is_header': False
        },
        {
            'name': 'SOW, SOP, Ratesheet',
            'target': str(sow_target),
            'achieved': str(sow_achieved),
            'pct': f"{sow_pct}%",
            'code_color': sow_code_color,
            'code_label': sow_code_label,
            'cs_count': cs_count,
            'days_count': working_days_count,
            'is_header': False
        },
        {
            'name': 'Customer -Appreciations',
            'target': str(appreciation_target),
            'achieved': str(appreciation_achieved),
            'pct': f"{appreciation_pct}%",
            'code_color': appr_code_color,
            'code_label': appr_code_label,
            'cs_count': cs_count,
            'days_count': working_days_count,
            'is_header': False
        },
        {
            'name': 'Customer -Complaints',
            'target': str(complaint_target),
            'achieved': str(complaints_achieved),
            'pct': f"{complaints_pct}%",
            'code_color': comp_code_color,
            'code_label': comp_code_label,
            'cs_count': cs_count,
            'days_count': working_days_count,
            'is_header': False
        }
    ]

    funnel_metrics = {
        'veh_requested': veh_requested,
        'veh_not_allotted': veh_not_allotted,
        'veh_allotted': veh_allotted,
        'cnotes_created': cnotes_created,
        'not_associated_with_trip': not_associated_with_trip,
        'awaiting_trip_approval': awaiting_trip_approval,
        'trip_started': trip_started,
        'trip_closed': trip_closed,
        'awaiting_trip_settlement': awaiting_trip_settlement,
        'trip_settled': trip_settled,
        'cancellation_without_billing': cancellation_without_billing,
        'cancellation_with_billing': cancellation_with_billing,
        'ready_for_invoice': ready_for_invoice,
        'invoice_completed': invoiced_trips,
        'pod_scanned': pod_scanned_count,
        'reconciliation_total': reconciliation_total,
    }

    allotment_pct = round((veh_allotted / veh_requested) * 100, 1) if veh_requested > 0 else 0
    cnote_conv_pct = round((cnotes_created / veh_allotted) * 100, 1) if veh_allotted > 0 else 0
    trip_start_pct = round((trip_started / cnotes_created) * 100, 1) if cnotes_created > 0 else 0
    pod_comp_pct = round((pod_scanned_count / pod_target_total) * 100, 1) if pod_target_total > 0 else 0

    conversion_metrics = {
        'allotment_pct': f"{allotment_pct}%",
        'cnote_conv_pct': f"{cnote_conv_pct}%",
        'trip_start_pct': f"{trip_start_pct}%",
        'pod_comp_pct': f"{pod_comp_pct}%",
    }

    # 3. Revenue & Billing Calculation (Total Revenue, Total Value Billed, Value Unbilled)
    # Value Unbilled is strictly calculated using the official Invoice Pending Report logic
    # Total Value Billed fetches the total charges invoiced for the cohort C-Notes/trips
    if is_sample_requested:
        total_revenue = 450000.0
        total_billed = 180000.0
        total_unbilled = 270000.0
    else:
        def safe_num(val):
            if val is None or val == '':
                return 0.0
            try:
                return float(val)
            except (ValueError, TypeError):
                return 0.0

        # Invoices map for billed trips / C-Notes
        invoices_by_trip = dict(
            TransInvoiceInfo.objects.filter(ti_trip__in=trips_qs)
            .values_list('ti_trip_id', 'ti_total')
        )
        invoices_by_cons = dict(
            TransInvoiceInfo.objects.filter(ti_consignment__in=cnotes_qs)
            .exclude(ti_total=0).values_list('ti_consignment_id', 'ti_total')
        )

        total_billed = 0.0
        for trip in trips_qs.filter(id__in=all_invoiced_ids):
            inv_amt = invoices_by_trip.get(trip.id)
            if inv_amt is None and trip.tr_consignmentnumber_id:
                inv_amt = invoices_by_cons.get(trip.tr_consignmentnumber_id)

            if inv_amt is not None and safe_num(inv_amt) > 0:
                val = safe_num(inv_amt)
            else:
                val = calculate_trip_invoice_total(trip) or safe_num(trip.tc_tripcost)
            total_billed += val

        # Value Unbilled: Calculated inline using the SAME logic as Invoice Pending Report
        # (no import from transport_reports_view needed - logic is self-contained here)
        unbilled_trips_qs = trips_qs.exclude(id__in=all_invoiced_ids)

        # Bulk-fetch allotments for unbilled trips
        unbilled_enquiry_ids = set(unbilled_trips_qs.values_list('tr_enquirynumber_id', flat=True))
        cnote_enquiry_ids = set(cnotes_qs.values_list('co_enquirynumber_id', flat=True))
        all_enquiry_ids = unbilled_enquiry_ids | cnote_enquiry_ids

        allotments_qs = Vehicle_allotmentInfo.objects.filter(
            va_enquirynumber_id__in=all_enquiry_ids
        ).select_related('va_vehicletype', 'va_vehicletype_placed', 'va_vehiclenumber')

        allotment_map = defaultdict(list)
        for a in allotments_qs:
            allotment_map[a.va_enquirynumber_id].append(a)

        total_unbilled = 0.0

        for trip in unbilled_trips_qs:
            # Resolve allotment for this trip
            allotment = None
            if trip.tr_enquirynumber_id in allotment_map:
                al_list = allotment_map[trip.tr_enquirynumber_id]
                if trip.tr_vehiclenumber:
                    clean_veh = str(trip.tr_vehiclenumber).replace(' ', '').upper()
                    for a in al_list:
                        a_veh = ''
                        if a.va_vehiclenumber:
                            a_veh = str(a.va_vehiclenumber.vm_registrationnumber)
                        elif a.va_vehiclenumber_mkt:
                            a_veh = str(a.va_vehiclenumber_mkt)
                        if a_veh.replace(' ', '').upper() == clean_veh:
                            allotment = a
                            break
                    if not allotment and al_list:
                        allotment = al_list[0]
                elif al_list:
                    allotment = al_list[0]

            # Halting charge
            halting_days = safe_num(trip.tc_no_of_days_halting)
            if halting_days <= 0:
                halting_days = 1.0
            tc_tot_cost = safe_num(trip.tc_total_halting_cost)
            tc_day_cost = safe_num(trip.tc_haltingcost)
            tc_total_check = getattr(trip, 'tc_total_halting_cost_check', False)
            tc_day_check = getattr(trip, 'tc_haltingcost_check', False)
            if tc_total_check or tc_day_check:
                if tc_tot_cost > 0:
                    halting_val = tc_tot_cost
                elif tc_day_cost > 0:
                    halting_val = tc_day_cost * halting_days
                else:
                    halting_val = 0.0
            else:
                halting_val = 0.0

            # Transport charge — same priority hierarchy as Invoice Pending Report
            is_settled = trip.tc_financestatus_id in [7, 9]
            is_special_sell_check = getattr(trip, 'tc_special_sell_check', False)
            is_tripcost_check = getattr(trip, 'tc_tripcost_check', False)

            if is_settled:
                if is_special_sell_check:
                    transport_val = safe_num(trip.tc_special_sell)
                    if transport_val <= 0 and allotment and safe_num(allotment.va_special_sale) > 0:
                        transport_val = safe_num(allotment.va_special_sale)
                    if transport_val <= 0:
                        transport_val = safe_num(get_enquiry_special_sell(trip))
                elif is_tripcost_check:
                    transport_val = safe_num(trip.tc_tripcost)
                    if transport_val <= 0 and allotment and safe_num(allotment.va_sale) > 0:
                        transport_val = safe_num(allotment.va_sale)
                    if transport_val <= 0:
                        transport_val = safe_num(get_enquiry_standard_sell(trip))
                else:
                    transport_val = 0.0
            else:
                if is_special_sell_check:
                    transport_val = safe_num(trip.tc_special_sell)
                    if transport_val <= 0 and allotment and safe_num(allotment.va_special_sale) > 0:
                        transport_val = safe_num(allotment.va_special_sale)
                    if transport_val <= 0:
                        transport_val = safe_num(get_enquiry_special_sell(trip))
                elif is_tripcost_check and safe_num(trip.tc_tripcost) > 0:
                    transport_val = safe_num(trip.tc_tripcost)
                else:
                    if allotment and allotment.va_special_sale is not None and safe_num(allotment.va_special_sale) > 0:
                        transport_val = safe_num(allotment.va_special_sale)
                    elif allotment and allotment.va_sale is not None and safe_num(allotment.va_sale) > 0:
                        transport_val = safe_num(allotment.va_sale)
                    else:
                        transport_val = safe_num(get_enquiry_special_sell(trip)) or safe_num(get_allotment_sale_rate(trip))

            row_total = (
                safe_num(transport_val) +
                (safe_num(trip.tc_tollcost) if trip.tc_tollcost_check else 0) +
                (safe_num(trip.tc_parkingcost) if trip.tc_parkingcost_check else 0) +
                (safe_num(trip.tc_loadingcost) if trip.tc_loadingcost_check else 0) +
                (safe_num(trip.tc_unloadingcost) if trip.tc_unloadingcost_check else 0) +
                halting_val +
                (safe_num(trip.tc_rtocost) if trip.tc_rtocost_check else 0) +
                (safe_num(trip.tc_weighmentcost) if trip.tc_weighmentcost_check else 0) +
                (safe_num(trip.tc_handlingcost) if trip.tc_handlingcost_check else 0) +
                (safe_num(trip.tc_cancellation) if trip.tc_cancellation_check else 0)
            )
            if row_total <= 0:
                row_total = safe_num(trip.tc_tripcost)
            total_unbilled += row_total

        # Include C-Notes without any trips (rate from allotment)
        trips_cnote_ids = set(trips_qs.values_list('tr_consignmentnumber_id', flat=True))
        cnotes_without_trip = cnotes_qs.exclude(id__in=trips_cnote_ids)
        for cn in cnotes_without_trip:
            al_list = allotment_map.get(cn.co_enquirynumber_id, [])
            if al_list:
                al = al_list[0]
                rate = safe_num(al.va_special_sale) or safe_num(al.va_sale)
                total_unbilled += rate

        total_revenue = total_billed + total_unbilled


    billed_share_pct = round((total_billed / total_revenue) * 100, 1) if total_revenue > 0 else 0.0
    unbilled_share_pct = round((total_unbilled / total_revenue) * 100, 1) if total_revenue > 0 else 0.0

    revenue_metrics = {
        'total_revenue': round(total_revenue, 2),
        'total_billed': round(total_billed, 2),
        'value_unbilled': round(total_unbilled, 2),
        'total_revenue_formatted': f"₹ {total_revenue:,.2f}",
        'total_billed_formatted': f"₹ {total_billed:,.2f}",
        'value_unbilled_formatted': f"₹ {total_unbilled:,.2f}",
        'billed_share_pct': f"{billed_share_pct}%",
        'unbilled_share_pct': f"{unbilled_share_pct}%",
    }

    # Monthly Calendar Map
    import calendar as py_calendar
    cal_year = int(request.GET.get('cal_year', from_date[:4] if from_date else timezone.now().strftime('%Y')))
    cal_month = int(request.GET.get('cal_month', from_date[5:7] if from_date else timezone.now().strftime('%m')))

    _, num_days = py_calendar.monthrange(cal_year, cal_month)
    month_start = date(cal_year, cal_month, 1)
    month_end = date(cal_year, cal_month, num_days)

    # Query enquiries in the month strictly matching cohort filters
    month_enquiries = EnquirynoteInfo.objects.filter(
        en_created_at__date__gte=month_start,
        en_created_at__date__lte=month_end
    )
    if branch_id and branch_id != 'all':
        month_enquiries = month_enquiries.filter(
            Q(en_assignedto_id__in=branch_user_ids) |
            Q(en_fromlocaion_id=branch_id)
        )
    if employee_id and employee_id != 'all':
        month_enquiries = month_enquiries.filter(en_assignedto_id=employee_id)

    # Vehicles Allotted for those enquiries (grouped by enquiry creation date)
    month_allotments = Vehicle_allotmentInfo.objects.filter(
        va_enquirynumber__in=month_enquiries
    ).exclude(va_status_id__in=[2, 4])

    allotment_by_date = dict(
        month_allotments.values('va_enquirynumber__en_created_at__date').annotate(cnt=Count('id')).values_list('va_enquirynumber__en_created_at__date', 'cnt')
    )

    # C-Notes and Trips for those enquiries (grouped by enquiry creation date)
    month_cnotes = ConsignmentdetailInfo.objects.filter(
        co_enquirynumber__in=month_enquiries
    )
    month_trips = TripdetailInfo.objects.filter(
        tr_consignmentnumber__in=month_cnotes
    )

    trips_by_date = dict(
        month_trips.values('tr_consignmentnumber__co_enquirynumber__en_created_at__date').annotate(cnt=Count('id')).values_list('tr_consignmentnumber__co_enquirynumber__en_created_at__date', 'cnt')
    )
    ready_only_by_date = dict(
        month_trips.filter(tc_financestatus_id=9).exclude(transinvoiceinfo__isnull=False).values('tr_consignmentnumber__co_enquirynumber__en_created_at__date').annotate(cnt=Count('id')).values_list('tr_consignmentnumber__co_enquirynumber__en_created_at__date', 'cnt')
    )
    invoiced_by_date = dict(
        month_trips.filter(transinvoiceinfo__isnull=False).values('tr_consignmentnumber__co_enquirynumber__en_created_at__date').annotate(cnt=Count('id')).values_list('tr_consignmentnumber__co_enquirynumber__en_created_at__date', 'cnt')
    )

    calendar_map = {}
    for day in range(1, num_days + 1):
        d = date(cal_year, cal_month, day)
        d_str = d.strftime('%Y-%m-%d')
        allotted = max(allotment_by_date.get(d, 0), trips_by_date.get(d, 0))
        ready = ready_only_by_date.get(d, 0)
        invoiced = invoiced_by_date.get(d, 0)

        # If zero trips in DB for this date and it's sample/demo date (e.g. 24th/28th Aug 2026), provide realistic reference
        if allotted == 0 and is_sample_requested:
            if day in [6, 12, 18, 21, 24]:
                allotted = 34 if day == 24 else (20 + day % 7)
                ready = 4 if day == 24 else (12 if day == 21 else 0)
                invoiced = 30 if day == 24 else (15 if day in [21, 12] else 0)

        total_done = ready + invoiced
        if allotted > 0:
            status = 'green' if total_done >= allotted else 'red'
        else:
            status = 'none'

        calendar_map[d_str] = {
            'day': day,
            'allotted': allotted,
            'ready': ready,
            'invoiced': invoiced,
            'status': status
        }


    return JsonResponse({
        'status': 'success',
        'funnel': funnel_metrics,
        'kpi_rows': kpi_rows,
        'revenue_metrics': revenue_metrics,
        'conversion': conversion_metrics,
        'calendar_data': calendar_map,
        'thresholds': {
            'red': '<= 35%',
            'orange': '36% - 70%',
            'green': '71% - 100%',
            'blue': '> 100%'
        }
    })


