from datetime import datetime, date
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q
from ..sub_models.enquirynote_mod import EnquirynoteInfo
from ..sub_models.customer_mod import CustomerInfo
from ..sub_models.user_ext_mod import User_extInfo
from ..sub_models.tripdetail_mod import TripdetailInfo, Trip_closure_files_Info
from ..sub_models.consignmentdetail_mod import ConsignmentdetailInfo
from ..sub_models.enquirynote_vehicle_mod import Enquirynotevehicle
from ..models import Location_info, StatusList, MyUser, CustomerdepartmentInfo, Places, VehiclecategoryInfo, VehicletypeInfo, VehiclemasterInfo
from .general_utils import get_financial_year, generate_next_number

def get_customer_context(request):
    """Helper to get the linked customer, department, and LP status for the portal.
    Handles _lp suffix logic for AISATS collaboration users.
    Returns: (customer, department, is_lp, agent_name)
    """
    user = request.user
    customer = None
    department = None
    is_lp = False
    agent_name = ""
    
    try:
        user_ext = User_extInfo.objects.get(user=user)
        is_lp = user_ext.is_lp_customer
        
        username = user.username.lower()
        if username.endswith('_lp'):
            # AISATS Collaboration logic: aisats_lp -> AISATS customer
            prefix = username[:-3]
            customer = CustomerInfo.objects.filter(
                Q(cu_customercode__iexact=prefix) | 
                Q(cu_nameshort__iexact=prefix) | 
                Q(cu_name__iexact=prefix)
            ).first()
            
            if user_ext.linked_customer:
                agent_name = user_ext.linked_customer.cu_nameshort or user_ext.linked_customer.cu_name
        else:
            # Check for Agent Mode override first
            agent_cust_id = request.session.get('agent_selected_customer_id')
            if agent_cust_id:
                customer = CustomerInfo.objects.filter(id=agent_cust_id).first()
                agent_name = user_ext.linked_customer.cu_nameshort or user_ext.linked_customer.cu_name if user_ext.linked_customer else ""
            else:
                # Regular Customer logic
                customer = user_ext.linked_customer

        # Check for department override in session
        dept_id = request.session.get('ses_customer_dept_id')
        if dept_id:
            department = CustomerdepartmentInfo.objects.filter(id=dept_id).first()
        
        if not department and user_ext.department:
             department = CustomerdepartmentInfo.objects.filter(ct_customerdepartment__iexact=user_ext.department.dept_name).first()
             
    except User_extInfo.DoesNotExist:
        pass
        
    return customer, department, is_lp, agent_name


def get_portal_role_context(request):
    """Return Parent-Child, Agent Account, and Brandix Dual-Login role metadata for the current portal user."""
    portal_role = 'STANDARD'
    agent_account = ''
    assigned_plant = ''
    linked_customer = None
    bill_to_customer = None

    try:
        user_ext = User_extInfo.objects.select_related('linked_customer', 'linked_customer__cu_parent_customer').get(user=request.user)
        portal_role = user_ext.portal_role or 'STANDARD'
        agent_account = user_ext.agent_account or ''
        assigned_plant = user_ext.assigned_plant or ''
        linked_customer = user_ext.linked_customer
        if linked_customer:
            bill_to_customer = linked_customer.cu_parent_customer or linked_customer
    except User_extInfo.DoesNotExist:
        pass

    return {
        'portal_role': portal_role,
        'agent_account': agent_account,
        'assigned_plant': assigned_plant,
        'linked_customer': linked_customer,
        'bill_to_customer': bill_to_customer,
        'is_factory': portal_role == 'FACTORY',
        'is_logistics': portal_role == 'LOGISTICS',
        'is_parent': portal_role == 'PARENT',
        'hide_commercials': portal_role == 'FACTORY',
    }


def get_portal_enquiry_queryset(customer, portal_ctx):
    """Return the scoped EnquirynoteInfo queryset based on Parent/Child/Agent/Factory/Logistics role."""
    role = portal_ctx.get('portal_role', 'STANDARD')
    agent_account = portal_ctx.get('agent_account', '')
    if role == 'PARENT':
        return EnquirynoteInfo.objects.filter(
            Q(en_customername=customer) | Q(en_sub_customer__cu_parent_customer=customer)
        )
    if role in ('FACTORY', 'LOGISTICS'):
        qs = EnquirynoteInfo.objects.filter(
            Q(en_sub_customer=customer) | Q(en_customername=customer)
        )
        if agent_account:
            qs = qs.filter(en_agent_name__iexact=agent_account)
        if role == 'FACTORY' and portal_ctx.get('assigned_plant'):
            qs = qs.filter(en_plant_code__iexact=portal_ctx['assigned_plant'])
        return qs
    return EnquirynoteInfo.objects.filter(en_customername=customer)


def get_portal_trip_queryset(customer, portal_ctx):
    """Return the scoped TripdetailInfo queryset based on Parent/Child/Agent/Factory/Logistics role."""
    role = portal_ctx.get('portal_role', 'STANDARD')
    agent_account = portal_ctx.get('agent_account', '')
    if role == 'PARENT':
        return TripdetailInfo.objects.filter(
            Q(tr_enquirynumber__en_customername=customer) |
            Q(tr_enquirynumber__en_sub_customer__cu_parent_customer=customer)
        )
    if role in ('FACTORY', 'LOGISTICS'):
        qs = TripdetailInfo.objects.filter(
            Q(tr_enquirynumber__en_sub_customer=customer) |
            Q(tr_enquirynumber__en_customername=customer)
        )
        if agent_account:
            qs = qs.filter(tr_enquirynumber__en_agent_name__iexact=agent_account)
        if role == 'FACTORY' and portal_ctx.get('assigned_plant'):
            qs = qs.filter(tr_enquirynumber__en_plant_code__iexact=portal_ctx['assigned_plant'])
        return qs
    return TripdetailInfo.objects.filter(tr_enquirynumber__en_customername=customer)


def _ensure_aware(dt):
    if dt and timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


def compute_brandix_kpis(enq, trip=None):
    """
    Auto-calculate Brandix SLA & Turnaround KPIs from enquiry & trip timestamps:
    - Late Booking (48-hr rule)
    - Placement Status, On-Time Placement (OTP), On-Time Delivery (OTD), Same Day Delivery
    - Spent at PP Hrs / %, Spent at DP Hrs / %, Transit Time Hrs / %
    """
    kpis = {
        'late_booking': '-',
        'placement_status': 'Not Placed',
        'on_time_placement': '-',
        'on_time_delivery': '-',
        'same_day_delivery': '-',
        'spent_at_pp_hrs': None,
        'spent_at_dp_hrs': None,
        'transit_time_hrs': None,
        'spent_at_pp_pct': None,
        'spent_at_dp_pct': None,
        'transit_time_pct': None,
    }
    if not enq:
        return kpis

    req_arr = _ensure_aware(enq.en_requested_arrival_time)
    req_del = _ensure_aware(enq.en_requested_delivery_time)
    created_at = _ensure_aware(enq.en_created_at)

    # 1. Late Booking (< 48 hours prior to requested arrival time)
    if req_arr and created_at:
        try:
            diff_hrs = (req_arr - created_at).total_seconds() / 3600.0
            kpis['late_booking'] = 'Yes' if diff_hrs < 48.0 else 'No'
        except Exception:
            pass

    if not trip:
        return kpis

    # 2. Placement Status
    arrived_pp = _ensure_aware(trip.tr_reporteddate_pickup or trip.tr_dock_in_time)
    departed_pp = _ensure_aware(trip.tr_departeddate_pickup or trip.tr_dock_out_time)
    arrived_dp = _ensure_aware(trip.tr_reporteddate_delivery)
    departed_dp = _ensure_aware(trip.tr_departeddate_delivery)

    if arrived_pp or (trip.tr_vehiclenumber and trip.tr_vehiclenumber != '-'):
        kpis['placement_status'] = 'Placed'

    # 3. On-Time Placement (OTP)
    if arrived_pp and req_arr:
        try:
            kpis['on_time_placement'] = 'Yes' if arrived_pp <= req_arr else 'No'
        except Exception:
            pass

    # 4. On-Time Delivery (OTD)
    if arrived_dp and req_del:
        try:
            kpis['on_time_delivery'] = 'Yes' if arrived_dp <= req_del else 'No'
        except Exception:
            pass

    # 5. Same Day Delivery
    if arrived_pp and arrived_dp:
        try:
            kpis['same_day_delivery'] = 'Yes' if arrived_dp.date() == arrived_pp.date() else 'No'
        except Exception:
            pass

    # 6. Dwell & Transit Hours
    pp_hrs = dp_hrs = transit_hrs = None
    if arrived_pp and departed_pp and departed_pp >= arrived_pp:
        pp_hrs = round((departed_pp - arrived_pp).total_seconds() / 3600.0, 2)
    if arrived_dp and departed_dp and departed_dp >= arrived_dp:
        dp_hrs = round((departed_dp - arrived_dp).total_seconds() / 3600.0, 2)
    if departed_pp and arrived_dp and arrived_dp >= departed_pp:
        transit_hrs = round((arrived_dp - departed_pp).total_seconds() / 3600.0, 2)

    kpis['spent_at_pp_hrs'] = pp_hrs
    kpis['spent_at_dp_hrs'] = dp_hrs
    kpis['transit_time_hrs'] = transit_hrs

    total_hrs = sum(h for h in (pp_hrs, dp_hrs, transit_hrs) if h is not None)
    if total_hrs > 0:
        if pp_hrs is not None:
            kpis['spent_at_pp_pct'] = round((pp_hrs / total_hrs) * 100.0, 1)
        if dp_hrs is not None:
            kpis['spent_at_dp_pct'] = round((dp_hrs / total_hrs) * 100.0, 1)
        if transit_hrs is not None:
            kpis['transit_time_pct'] = round((transit_hrs / total_hrs) * 100.0, 1)

    return kpis

@login_required
def ajax_get_vehicle_types(request):
    """AJAX view to return all vehicle types (unfiltered)."""
    types = VehicletypeInfo.objects.all().order_by('vt_vehicletype').values('id', 'vt_vehicletype')
    return JsonResponse(list(types), safe=False)


def compute_shipment_flow(enq=None, trip=None, va=None, is_delivered=False, pod_trip_id=None, track_link=''):
    """
    Computes comprehensive 12-step operational shipment lifecycle flow:
    Phase 1: Order Placement & Allotment
      1. Indent Placed (Booking received & registered)
      2. Vehicle Allotted (Vehicle & Driver assigned)
    Phase 2: Origin Loading Bay Operations
      3. Reported at Loading Point (Vehicle arrived at pickup location gate)
      4. Loading Dock-In (Positioned at loading dock/bay)
      5. Cargo Loading (Cargo loaded and secured inside vehicle container)
      6. Loading Dock-Out (Loading completed, dock released & gate clearance)
    Phase 3: Highway Transit Operations
      7. Trip Started (In-Transit) (Dispatched from origin & moving on transit corridor)
    Phase 4: Destination Unloading Bay Operations
      8. Reported at Unloading Point (Vehicle arrived at delivery destination gate)
      9. Unloading Dock-In (Positioned at unloading bay/dock)
      10. Cargo Unloading (Cargo unloaded, verified & count checked by consignee)
      11. Unloading Dock-Out (Unloading completed, dock cleared & exit gate pass)
    Phase 5: Delivery & POD Verification
      12. Trip Completed & POD Verified (Trip officially closed & POD document uploaded)
    """
    if va is None and enq and hasattr(enq, 'vehicle_allotmentinfo_set'):
        va = enq.vehicle_allotmentinfo_set.first()

    has_vehicle = bool(
        (trip and trip.tr_vehiclenumber and trip.tr_vehiclenumber != '-') or
        (va and (va.va_vehiclenumber or va.va_vehiclenumber_mkt))
    )

    veh_no = '-'
    if trip and trip.tr_vehiclenumber and trip.tr_vehiclenumber != '-':
        veh_no = trip.tr_vehiclenumber
    elif va:
        if va.va_vehiclenumber:
            veh_no = str(va.va_vehiclenumber)
        elif va.va_vehiclenumber_mkt:
            veh_no = va.va_vehiclenumber_mkt

    driver_name = ''
    driver_phone = ''
    if trip and (trip.tr_drivername or trip.tr_drivernumber):
        driver_name = trip.tr_drivername or ''
        driver_phone = trip.tr_drivernumber or ''
    elif va and (va.va_drivername or va.va_drivernumber):
        driver_name = va.va_drivername or ''
        driver_phone = va.va_drivernumber or ''
    if driver_name:
        import re as _re
        driver_name = _re.sub(r'\s*\(\d+\)\s*$', '', str(driver_name)).strip()

    # Check delivery status
    if not is_delivered and trip:
        if trip.tc_financestatus_id in [2, 3, 4, 5, 6, 7, 9, 10, 11]:
            is_delivered = True

    from_loc_name = enq.en_fromlocaion.place_name if (enq and enq.en_fromlocaion) else (trip.tr_departedlocation.place_name if (trip and trip.tr_departedlocation) else 'Origin')
    to_loc_name = enq.en_tolocation.place_name if (enq and enq.en_tolocation) else (trip.tr_reportedlocation.place_name if (trip and trip.tr_reportedlocation) else 'Destination')

    # Step 1: Indent Placed
    t1_done = True
    t1_time = enq.en_created_at if enq else (trip.tr_created_at if trip else None)

    # Step 2: Vehicle Allotted
    t2_done = has_vehicle
    t2_time = (va.va_created_at if va and hasattr(va, 'va_created_at') and va.va_created_at else None) or (trip.tr_created_at if trip else None)

    # Step 3: Reported at Loading Point (Pickup arrival)
    t3_done = bool(trip and (trip.tr_reporteddate_pickup or trip.tr_departeddate_pickup or trip.tr_dock_in_time or trip.tr_loading_time or trip.tr_dock_out_time or trip.tr_departeddate or is_delivered))
    t3_time = (trip.tr_reporteddate_pickup or trip.tr_departeddate_pickup or trip.tr_dock_in_time or trip.tr_loading_time) if trip else None

    # Step 4: Loading Dock-In
    t4_done = bool(trip and (trip.tr_dock_in_time or trip.tr_loading_time or trip.tr_dock_out_time or trip.tr_departeddate or is_delivered))
    t4_time = (trip.tr_dock_in_time or trip.tr_loading_time) if trip else None

    # Step 5: Cargo Loading
    t5_done = bool(trip and (trip.tr_loading_time or trip.tr_dock_out_time or trip.tr_departeddate or is_delivered))
    t5_time = (trip.tr_loading_time or trip.tr_dock_out_time) if trip else None

    # Step 6: Loading Dock-Out
    t6_done = bool(trip and (trip.tr_dock_out_time or trip.tr_departeddate or is_delivered))
    t6_time = (trip.tr_dock_out_time or trip.tr_departeddate) if trip else None

    # Step 7: Trip Started / Departed (In-Transit)
    t7_done = bool(trip and (is_delivered or trip.tc_financestatus_id in [2, 7, 9] or trip.tr_reporteddate or trip.tr_reporteddate_delivery or trip.tr_unloading_time or trip.tr_departeddate_delivery))
    t7_active = bool(trip and not is_delivered and (trip.tc_financestatus_id == 1 or trip.tr_departeddate or (t6_done and not (trip.tr_reporteddate or trip.tr_reporteddate_delivery))))
    t7_time = (trip.tr_departeddate or trip.tr_dock_out_time) if trip else None

    # Step 8: Reported at Unloading Point (Destination arrival)
    t8_done = bool(trip and (trip.tr_reporteddate_delivery or trip.tr_reporteddate or trip.tr_departeddate_delivery or trip.tr_unloading_time or is_delivered))
    t8_time = (trip.tr_reporteddate or trip.tr_reporteddate_delivery or trip.tr_unloading_time) if trip else None

    # Step 9: Unloading Dock-In
    t9_done = bool(trip and (trip.tr_departeddate_delivery or trip.tr_unloading_time or is_delivered))
    t9_time = (trip.tr_departeddate_delivery or trip.tr_reporteddate or trip.tr_unloading_time) if trip else None

    # Step 10: Cargo Unloading
    t10_done = bool(trip and (trip.tr_unloading_time or is_delivered))
    t10_time = (trip.tr_unloading_time or trip.tr_reporteddate) if trip else None

    # Step 11: Unloading Dock-Out
    t11_done = bool(trip and (trip.tr_departeddate_delivery or trip.tr_reporteddate_delivery or is_delivered))
    t11_time = (trip.tr_departeddate_delivery or trip.tr_reporteddate_delivery or trip.tr_unloading_time) if trip else None

    # Step 12: Trip Completed & POD Verified
    t12_done = is_delivered
    t12_time = (trip.tr_reporteddate_delivery or trip.tr_unloading_time or trip.tr_reporteddate or trip.tr_updated_at) if (trip and is_delivered) else None

    # Determine current step (1 to 12)
    if enq and enq.en_status_id == 8:
        current_step = 1
        stage_label = 'Cancelled'
        stage_class = 'cancelled'
        stage_color = '#ef4444'
        stage_icon = 'fa-ban'
    elif t12_done:
        current_step = 12
        stage_label = 'Trip Completed & POD Verified'
        stage_class = 'completed'
        stage_color = '#10b981'
        stage_icon = 'fa-check-circle'
    elif t11_done:
        current_step = 11
        stage_label = 'Unloading Dock-Out'
        stage_class = 'unloading'
        stage_color = '#38bdf8'
        stage_icon = 'fa-door-open'
    elif t10_done:
        current_step = 10
        stage_label = 'Cargo Unloaded'
        stage_class = 'unloading'
        stage_color = '#38bdf8'
        stage_icon = 'fa-dolly'
    elif t9_done:
        current_step = 9
        stage_label = 'Unloading Dock-In'
        stage_class = 'unloading'
        stage_color = '#38bdf8'
        stage_icon = 'fa-warehouse'
    elif t8_done:
        current_step = 8
        stage_label = 'Reported at Destination'
        stage_class = 'unloading'
        stage_color = '#38bdf8'
        stage_icon = 'fa-location-dot'
    elif t7_active:
        current_step = 7
        stage_label = 'In-Transit (Highway Movement)'
        stage_class = 'transit'
        stage_color = '#00f2fe'
        stage_icon = 'fa-truck-fast'
    elif t6_done:
        current_step = 6
        stage_label = 'Loading Dock-Out'
        stage_class = 'loading'
        stage_color = '#f59e0b'
        stage_icon = 'fa-door-open'
    elif t5_done:
        current_step = 5
        stage_label = 'Cargo Loaded'
        stage_class = 'loading'
        stage_color = '#f59e0b'
        stage_icon = 'fa-boxes-packing'
    elif t4_done:
        current_step = 4
        stage_label = 'Loading Dock-In'
        stage_class = 'loading'
        stage_color = '#f59e0b'
        stage_icon = 'fa-warehouse'
    elif t3_done:
        current_step = 3
        stage_label = 'Reported at Loading'
        stage_class = 'loading'
        stage_color = '#f59e0b'
        stage_icon = 'fa-location-dot'
    elif t2_done:
        current_step = 2
        stage_label = 'Vehicle Allotted'
        stage_class = 'allotted'
        stage_color = '#a855f7'
        stage_icon = 'fa-truck-front'
    else:
        current_step = 1
        if enq and not enq.en_is_approved:
            stage_label = 'Pending Logistics Approval'
            stage_class = 'indent'
            stage_color = '#f59e0b'
            stage_icon = 'fa-hourglass-half'
        else:
            stage_label = 'Indent Placed'
            stage_class = 'indent'
            stage_color = '#38bdf8'
            stage_icon = 'fa-file-invoice'

    def get_step_status(step_num):
        if t12_done:
            return 'done'
        if step_num < current_step:
            return 'done'
        if step_num == current_step:
            return 'current'
        return 'pending'

    steps = [
        {
            'step': 1,
            'phase_group': 'Phase 1: Order Placement & Vehicle Allotment',
            'phase_badge': 'Order Placement',
            'phase_icon': 'fa-clipboard-check',
            'phase_color': '#38bdf8',
            'title': 'Indent Placed',
            'desc': f"Movement Request ({from_loc_name} -> {to_loc_name})" if enq else "Indent Placed",
            'sub': f"Route: {from_loc_name} → {to_loc_name}",
            'time': t1_time,
            'status': get_step_status(1),
            'icon': 'fa-file-invoice',
        },
        {
            'step': 2,
            'phase_group': 'Phase 1: Order Placement & Vehicle Allotment',
            'phase_badge': 'Vehicle Allotment',
            'phase_icon': 'fa-truck-front',
            'phase_color': '#a855f7',
            'title': 'Vehicle Allotted',
            'desc': f"Vehicle: {veh_no}" if veh_no and veh_no != '-' else "Awaiting Allotment",
            'sub': f"Driver: {driver_name} {f'({driver_phone})' if driver_phone else ''}".strip() or 'Driver assignment in progress',
            'time': t2_time,
            'status': get_step_status(2),
            'icon': 'fa-truck-front',
        },
        {
            'step': 3,
            'phase_group': f'Phase 2: Origin Loading Bay Operations ({from_loc_name})',
            'phase_badge': 'Loading Point',
            'phase_icon': 'fa-warehouse',
            'phase_color': '#f59e0b',
            'title': 'Reported at Loading Point',
            'desc': f"Vehicle arrived at origin: {from_loc_name}",
            'sub': 'Vehicle reported at loading gate' if (t3_done or current_step >= 3) else 'Awaiting arrival at loading point',
            'time': t3_time,
            'status': get_step_status(3),
            'icon': 'fa-location-dot',
        },
        {
            'step': 4,
            'phase_group': f'Phase 2: Origin Loading Bay Operations ({from_loc_name})',
            'phase_badge': 'Loading Point',
            'phase_icon': 'fa-warehouse',
            'phase_color': '#f59e0b',
            'title': 'Loading Dock-In',
            'desc': f"Placed at {from_loc_name} loading bay",
            'sub': 'Docked at loading platform' if (t4_done or current_step >= 4) else 'Dock-in pending',
            'time': t4_time,
            'status': get_step_status(4),
            'icon': 'fa-warehouse',
        },
        {
            'step': 5,
            'phase_group': f'Phase 2: Origin Loading Bay Operations ({from_loc_name})',
            'phase_badge': 'Loading Point',
            'phase_icon': 'fa-boxes-packing',
            'phase_color': '#f59e0b',
            'title': 'Cargo Loading',
            'desc': 'Cargo loaded & secured inside vehicle container',
            'sub': 'Loading activity completed' if (t5_done or current_step >= 5) else 'Loading operation in progress',
            'time': t5_time,
            'status': get_step_status(5),
            'icon': 'fa-boxes-packing',
        },
        {
            'step': 6,
            'phase_group': f'Phase 2: Origin Loading Bay Operations ({from_loc_name})',
            'phase_badge': 'Loading Point',
            'phase_icon': 'fa-door-open',
            'phase_color': '#f59e0b',
            'title': 'Loading Dock-Out',
            'desc': f"Vehicle cleared from {from_loc_name} loading bay",
            'sub': 'Dock released & cleared for dispatch' if (t6_done or current_step >= 6) else 'Dock-out release pending',
            'time': t6_time,
            'status': get_step_status(6),
            'icon': 'fa-door-open',
        },
        {
            'step': 7,
            'phase_group': 'Phase 3: Highway Transit Operations',
            'phase_badge': 'In-Transit',
            'phase_icon': 'fa-truck-fast',
            'phase_color': '#00f2fe',
            'title': 'Trip Started (In-Transit)',
            'desc': f"Dispatched from {from_loc_name} • Highway movement",
            'sub': f'Moving towards {to_loc_name}' if (t7_active or t7_done or current_step >= 7) else 'Awaiting transit dispatch',
            'track_link': track_link,
            'time': t7_time,
            'status': get_step_status(7),
            'icon': 'fa-truck-fast',
        },
        {
            'step': 8,
            'phase_group': f'Phase 4: Destination Unloading Bay Operations ({to_loc_name})',
            'phase_badge': 'Unloading Point',
            'phase_icon': 'fa-warehouse',
            'phase_color': '#38bdf8',
            'title': 'Reported at Unloading Point',
            'desc': f"Vehicle arrived at destination: {to_loc_name}",
            'sub': 'Reported at delivery receiving gate' if (t8_done or current_step >= 8) else 'En route to delivery point',
            'time': t8_time,
            'status': get_step_status(8),
            'icon': 'fa-location-crosshairs',
        },
        {
            'step': 9,
            'phase_group': f'Phase 4: Destination Unloading Bay Operations ({to_loc_name})',
            'phase_badge': 'Unloading Point',
            'phase_icon': 'fa-warehouse',
            'phase_color': '#38bdf8',
            'title': 'Unloading Dock-In',
            'desc': f"Positioned at {to_loc_name} receiving bay",
            'sub': 'Vehicle docked at unloading platform' if (t9_done or current_step >= 9) else 'Scheduled for receiving dock',
            'time': t9_time,
            'status': get_step_status(9),
            'icon': 'fa-warehouse',
        },
        {
            'step': 10,
            'phase_group': f'Phase 4: Destination Unloading Bay Operations ({to_loc_name})',
            'phase_badge': 'Unloading Point',
            'phase_icon': 'fa-dolly',
            'phase_color': '#38bdf8',
            'title': 'Cargo Unloading',
            'desc': 'Cargo unloaded & received at destination bay',
            'sub': 'Material unloaded & quality inspection done' if (t10_done or current_step >= 10) else 'Awaiting unloading activity',
            'time': t10_time,
            'status': get_step_status(10),
            'icon': 'fa-dolly',
        },
        {
            'step': 11,
            'phase_group': f'Phase 4: Destination Unloading Bay Operations ({to_loc_name})',
            'phase_badge': 'Unloading Point',
            'phase_icon': 'fa-door-open',
            'phase_color': '#38bdf8',
            'title': 'Unloading Dock-Out',
            'desc': f"Vehicle cleared from {to_loc_name} unloading dock",
            'sub': 'Receiving bay released & gate pass cleared' if (t11_done or current_step >= 11) else 'Unloading dock-out pending',
            'time': t11_time,
            'status': get_step_status(11),
            'icon': 'fa-door-open',
        },
        {
            'step': 12,
            'phase_group': 'Phase 5: Delivery & POD Verification',
            'phase_badge': 'Trip Completed',
            'phase_icon': 'fa-circle-check',
            'phase_color': '#10b981',
            'title': 'Trip Completed & POD Verified',
            'desc': f"Delivered safely to {to_loc_name}",
            'sub': 'Consignment delivered, verified & POD uploaded' if t12_done else 'Trip completion pending',
            'time': t12_time,
            'pod_trip_id': pod_trip_id,
            'status': 'done' if t12_done else 'pending',
            'icon': 'fa-circle-check',
        },
    ]

    progress_percent = int(round((current_step / 12) * 100))

    return {
        'current_stage': current_step,
        'total_stages': 12,
        'progress_percent': progress_percent,
        'stage_label': stage_label,
        'stage_class': stage_class,
        'stage_color': stage_color,
        'stage_icon': stage_icon,
        'vehicle_no': veh_no,
        'driver_name': driver_name,
        'driver_phone': driver_phone,
        'from_loc': from_loc_name,
        'to_loc': to_loc_name,
        'steps': steps,
    }

@login_required(login_url='/SMS/customer_login/2/')
def customer_dashboard(request):
    """
    Premium dashboard for customers showing summary stats and recent shipments.
    """
    customer, department, is_lp, agent_name = get_customer_context(request)
    
    if not customer:
        messages.error(request, 'Your account is not linked to a Customer Profile. Please contact support.')
        if request.user.is_staff or request.user.is_superuser:
            return redirect('home_page')
        return redirect('login_page')

    portal_ctx = get_portal_role_context(request)

    # Base queryset for enquiries
    enquiry_qs = get_portal_enquiry_queryset(customer, portal_ctx)
    if department:
        enquiry_qs = enquiry_qs.filter(en_customerdepartment=department)

    # All trips for this customer
    all_trips = get_portal_trip_queryset(customer, portal_ctx)
    if department:
        all_trips = all_trips.filter(tr_enquirynumber__en_customerdepartment=department)

    from ..sub_models.vehicle_allotment_mod import Vehicle_allotmentInfo
    from datetime import timedelta

    # BUSINESS trips only (tr_category_id=1) — exclude empty runs
    business_trips = all_trips.filter(tr_category_id=1)

    # Current Month MTD Delivered trips & current month filter
    first_day_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # In-Transit = enquiries with a business trip in status 1 (trip started/running in current month)
    in_transit_enq_ids = business_trips.filter(
        tc_financestatus_id=1,
        tr_created_at__gte=first_day_of_month
    ).values_list('tr_enquirynumber_id', flat=True).distinct()
    in_transit = enquiry_qs.filter(id__in=in_transit_enq_ids).count()
    from sms_app.models import Trip_closure_files_Info
    closed_trip_numbers = Trip_closure_files_Info.objects.exclude(
        Q(tcf_pod__isnull=True) | Q(tcf_pod='')
    ).values_list('tcf_tripnumber', flat=True)
    
    active_trip_enq_ids = list(business_trips.filter(
        tc_financestatus_id__in=[1, 8]
    ).values_list('tr_enquirynumber_id', flat=True).distinct())

    all_closed_via_closure_enq_ids = business_trips.filter(
        tr_tripnumber__in=closed_trip_numbers
    ).values_list('tr_enquirynumber_id', flat=True).distinct()

    all_delivered_enq_ids = list(set(
        list(business_trips.filter(
            tc_financestatus_id__in=[2, 7, 9]
        ).values_list('tr_enquirynumber_id', flat=True).distinct()) +
        list(all_closed_via_closure_enq_ids)
    ) - set(active_trip_enq_ids))

    closed_via_closure_enq_ids = business_trips.filter(
        tr_tripnumber__in=closed_trip_numbers,
        tr_created_at__gte=first_day_of_month
    ).values_list('tr_enquirynumber_id', flat=True).distinct()

    delivered_enq_ids = list(set(
        list(business_trips.filter(
            tc_financestatus_id__in=[2, 7, 9],
            tr_created_at__gte=first_day_of_month
        ).values_list('tr_enquirynumber_id', flat=True).distinct()) +
        list(closed_via_closure_enq_ids)
    ) - set(active_trip_enq_ids))
    delivered = enquiry_qs.filter(id__in=delivered_enq_ids).count()

    # Vehicle Allotted = enquiries created in current month that have a vehicle allotted
    # but NO business trip started (not in-transit, not delivered)
    allotted_trip_enq_ids = business_trips.filter(
        tr_vehiclenumber__isnull=False,
        tr_enquirynumber__en_created_at__gte=first_day_of_month
    ).exclude(
        tr_vehiclenumber=''
    ).values_list('tr_enquirynumber_id', flat=True).distinct()

    allotted_va_ids = Vehicle_allotmentInfo.objects.filter(
        va_enquirynumber__in=enquiry_qs,
        va_enquirynumber__en_created_at__gte=first_day_of_month
    ).filter(
        ~Q(va_vehiclenumber__isnull=True) | (~Q(va_vehiclenumber_mkt='') & ~Q(va_vehiclenumber_mkt__isnull=True))
    ).values_list('va_enquirynumber_id', flat=True).distinct()

    allotted_all_ids = list(set(list(allotted_trip_enq_ids) + list(allotted_va_ids)))

    # Exclude explicitly dead/cancelled/completed enquiries (status 5 = Completed, 8 = Cancelled)
    dead_enq_ids = list(enquiry_qs.filter(en_status_id__in=[5, 8]).values_list('id', flat=True))
    cancelled_trip_enq_ids = list(all_trips.filter(
        Q(tc_financestatus_id__in=[10, 11]) |
        Q(tc_financestatus__status__icontains='Cancellation') |
        Q(tc_financestatus__status__icontains='Cancelled') |
        Q(tr_remarks__icontains='Cancelled')
    ).values_list('tr_enquirynumber_id', flat=True).distinct())
    dead_enq_ids = list(set(dead_enq_ids + cancelled_trip_enq_ids))

    # Exclude enquiries where ALL trips are closed or cancelled (no active trips, but has trips)
    active_trips_enq_ids = all_trips.exclude(tc_financestatus_id__in=[2, 3, 4, 5, 7, 9, 10, 11]).values_list('tr_enquirynumber_id', flat=True).distinct()
    any_trip_enq_ids = all_trips.values_list('tr_enquirynumber_id', flat=True).distinct()
    fully_closed_enq_ids = list(set(any_trip_enq_ids) - set(active_trips_enq_ids))

    # Allotted: count total allotted vehicles on enquiries created in current month with no active/closed trip
    allotted_enq_ids = list(enquiry_qs.filter(
        id__in=allotted_all_ids,
        en_created_at__gte=first_day_of_month
    ).exclude(
        id__in=in_transit_enq_ids
    ).exclude(
        id__in=all_delivered_enq_ids
    ).exclude(
        id__in=dead_enq_ids
    ).exclude(
        id__in=fully_closed_enq_ids
    ).values_list('id', flat=True))

    allotted = 0
    for eid in allotted_enq_ids:
        va_count = Vehicle_allotmentInfo.objects.filter(va_enquirynumber_id=eid).filter(
            ~Q(va_vehiclenumber__isnull=True) | (~Q(va_vehiclenumber_mkt='') & ~Q(va_vehiclenumber_mkt__isnull=True))
        ).count()
        tr_count = business_trips.filter(tr_enquirynumber_id=eid, tr_vehiclenumber__isnull=False).exclude(tr_vehiclenumber='').count()
        allotted += max(va_count, tr_count, 1)

    # Active = enquiries with NO vehicle allotted yet (recent 3 days)
    recent_limit = timezone.now() - timedelta(days=3)
    active_enquiries = enquiry_qs.filter(
        en_created_at__gte=recent_limit
    ).exclude(
        id__in=allotted_all_ids
    ).exclude(
        id__in=dead_enq_ids
    ).exclude(
        id__in=fully_closed_enq_ids
    ).count()

    # Recent Shipments — include driver and consignment info
    recent_shipments = all_trips.select_related(
        'tr_enquirynumber', 'tc_financestatus', 'tr_consignmentnumber'
    ).order_by('-tr_created_at')[:5]

    for trip in recent_shipments:
        is_deliv = (trip.tc_financestatus_id in [2, 3, 4, 5, 6, 7, 9, 10, 11] or (trip.tr_tripnumber and trip.tr_tripnumber in closed_trip_numbers))
        track_link = f'/SMS/SMS/customer_track_vehicle/?vehicle={trip.tr_vehiclenumber}&trip_id={trip.id}' if trip.tr_vehiclenumber and not is_deliv else ''
        trip.flow = compute_shipment_flow(trip.tr_enquirynumber, trip, is_delivered=is_deliv, track_link=track_link)

    pending_approvals_count = enquiry_qs.filter(en_is_approved=False).count()

    return render(request, 'asset_mgt_app/customer_portal_dashboard.html', {
        'customer': customer,
        'department': department,
        'active_enquiries': active_enquiries,
        'in_transit': in_transit,
        'delivered': delivered,
        'allotted': allotted,
        'recent_shipments': recent_shipments,
        'portal_ctx': portal_ctx,
        'pending_approvals_count': pending_approvals_count,
    })

@login_required(login_url='/SMS/customer_login/2/')
def customer_enquiry_add(request):
    """
    Simplified enquiry submission form for logged-in customers.
    Supports Standard, Parent, Brandix Factory (request without vehicle sizing),
    and Brandix Logistics (full booking) roles.
    """
    customer, department, is_lp, agent_name = get_customer_context(request)
    portal_ctx = get_portal_role_context(request)
    is_factory = portal_ctx['is_factory']
    is_logistics = portal_ctx['is_logistics']
    
    from ..sub_models.tr_triptype_mod import Tr_triptype_Info
    places = Places.objects.all().order_by('place_name')
    categories = VehiclecategoryInfo.objects.all().order_by('vc_vehiclecategory')
    types = VehicletypeInfo.objects.all().order_by('vt_vehicletype')
    departments = CustomerdepartmentInfo.objects.all().order_by('ct_customerdepartment')
    trip_types = Tr_triptype_Info.objects.all().order_by('tr_trip_type')

    if request.method == 'POST':
        from_loc_id = request.POST.get('from_location')
        to_loc_id = request.POST.get('to_location')
        category_id = request.POST.get('vehicle_category')
        type_id = request.POST.get('vehicle_type')
        cargo_details = request.POST.get('cargo_details', '')
        
        pickup_datetime_str = request.POST.get('pickup_datetime', '')
        req_arrival_str = request.POST.get('requested_arrival_time', '')
        if is_factory and not pickup_datetime_str and req_arrival_str:
            pickup_datetime_str = req_arrival_str

        pickup_date = None
        req_time = None
        if pickup_datetime_str:
            try:
                parts = pickup_datetime_str.split('T')
                pickup_date = parts[0]
                req_time = parts[1] if len(parts) > 1 else None
            except Exception:
                pickup_date = pickup_datetime_str
        
        if not pickup_date:
            pickup_date = request.POST.get('pickup_date')
        if not req_time:
            req_time = request.POST.get('req_time')
        
        dept_id = request.POST.get('customer_department')
        trip_type_id = request.POST.get('trip_type')
        agent_name = request.POST.get('agent_name') or portal_ctx.get('agent_account') or agent_name
        no_of_veh = request.POST.get('no_of_veh', '')
        no_of_pcs = request.POST.get('no_of_pcs', 0)
        weight = request.POST.get('weight')
        dimensions = request.POST.get('dimensions')
        cbm = request.POST.get('cbm')
        
        pickup_contact_name = request.POST.get('pickup_contact_name')
        pickup_contact_mobile = request.POST.get('pickup_contact_mobile')
        delivery_contact_name = request.POST.get('delivery_contact_name')
        delivery_contact_mobile = request.POST.get('delivery_contact_mobile')

        # Brandix / Child Portal fields
        plant_code = request.POST.get('plant_code') or portal_ctx.get('assigned_plant') or ''
        buyer_name = request.POST.get('buyer_name') or ''
        po_numbers = request.POST.get('po_numbers') or ''
        req_delivery_str = request.POST.get('requested_delivery_time') or None
        otd_cutoff_str = request.POST.get('otd_cutoff') or None
        shipment_type = request.POST.get('shipment_type') or ''
        vessel_name = request.POST.get('vessel_name') or ''
        voyage_no = request.POST.get('voyage_no') or ''
        bl_cutoff_str = request.POST.get('bl_cutoff') or None
        special_instructions = request.POST.get('special_instructions') or ''
        
        if not customer:
            messages.error(request, 'Account link missing.')
            return redirect('customer_dashboard')
            
        try:
            # Resolve objects
            selected_dept = CustomerdepartmentInfo.objects.filter(id=dept_id).first() if dept_id else department
            trip_type_obj = Tr_triptype_Info.objects.filter(id=trip_type_id).first() if trip_type_id else None
            from_loc = Places.objects.filter(id=from_loc_id).first() if from_loc_id else None
            to_loc = Places.objects.filter(id=to_loc_id).first() if to_loc_id else None
            vc_obj = VehiclecategoryInfo.objects.filter(id=category_id).first() if category_id else None
            vt_obj = VehicletypeInfo.objects.filter(id=type_id).first() if type_id else None

            # Validate mandatory fields
            errors = []
            if not selected_dept:
                errors.append('Please select a Department.')
            if not trip_type_obj:
                errors.append('Please select a Trip Type.')
            if not pickup_datetime_str and not pickup_date:
                errors.append('Please select Requested Arrival Date & Time.' if is_factory else 'Please select Vehicle Required Date & Time.')
            if not from_loc:
                errors.append('Please select an Origin.')
            if not to_loc:
                errors.append('Please select a Destination.')

            veh_count = 0
            if not is_factory:
                if not vc_obj:
                    errors.append('Please select a Vehicle Category.')
                if not vt_obj:
                    errors.append('Please select a Vehicle Type.')
                try:
                    veh_count = int(no_of_veh)
                    if veh_count < 1:
                        errors.append('Please enter Number of Vehicles (minimum 1).')
                except (ValueError, TypeError):
                    errors.append('Please enter Number of Vehicles (minimum 1).')

            if errors:
                for err in errors:
                    messages.error(request, err)
                return render(request, 'asset_mgt_app/customer_enquiry_add.html', {
                    'customer': customer,
                    'department': selected_dept or department,
                    'departments': departments,
                    'places': places,
                    'categories': categories,
                    'types': types,
                    'trip_types': trip_types,
                    'is_lp': is_lp,
                    'default_agent_name': agent_name,
                    'portal_ctx': portal_ctx,
                })

            category_name = vc_obj.vc_vehiclecategory if vc_obj else ""
            if not cargo_details and vt_obj:
                cargo_details = vt_obj.vt_vehicletype

            assigned_user = MyUser.objects.filter(is_superuser=True).first() or request.user
            if customer and "EIPL" in customer.cu_name:
                ajay_user = MyUser.objects.filter(first_name__icontains='Ajay', last_name__icontains='R').first()
                if not ajay_user:
                    ajay_user = MyUser.objects.filter(first_name__icontains='Ajay').first()
                if ajay_user:
                    assigned_user = ajay_user

            # Parent-Child billing binding
            bill_to_cust = portal_ctx['bill_to_customer'] or customer
            sub_cust = customer if (customer != bill_to_cust or is_factory or is_logistics) else None

            # Strict Approval Gate: Factory indents require Logistics approval before BVM dispatch
            is_approved_flag = False if is_factory else True
            approved_by_val = (request.user.get_full_name() or request.user.username) if is_logistics else None
            approved_date_val = timezone.now() if is_logistics else None

            enquiry = EnquirynoteInfo(
                en_customername=bill_to_cust,
                en_sub_customer=sub_cust,
                en_customerdepartment=selected_dept,
                en_assignedto=assigned_user,
                en_status=StatusList.objects.filter(id=6).first(),
                en_trip_type=trip_type_obj,
                en_consignmentdetails=cargo_details,
                en_vehicledetails=category_name,
                en_pickupdatetime=pickup_datetime_str if pickup_datetime_str else timezone.now(),
                en_fromlocaion=from_loc,
                en_tolocation=to_loc,
                en_created_at=timezone.now(),
                en_agent_name=agent_name,
                en_vehicle_req_time=req_time if req_time else None,
                en_no_of_vehicles=veh_count,
                en_no_of_pcs=int(no_of_pcs) if no_of_pcs else 0,
                en_weight=weight,
                en_dimensions=dimensions,
                en_cbm=cbm,
                en_pickup_contact_name=pickup_contact_name,
                en_pickup_contact_mobile=pickup_contact_mobile,
                en_delivery_contact_name=delivery_contact_name,
                en_delivery_contact_mobile=delivery_contact_mobile,
                en_plant_code=plant_code or None,
                en_is_approved=is_approved_flag,
                en_approved_by=approved_by_val,
                en_approved_date=approved_date_val,
                en_requested_arrival_time=req_arrival_str or (pickup_datetime_str if is_factory else None),
                en_requested_delivery_time=req_delivery_str,
                en_otd_cutoff=otd_cutoff_str,
                en_buyer_name=buyer_name or None,
                en_po_numbers=po_numbers or None,
                en_shipment_type=shipment_type or None,
                en_vessel_name=vessel_name or None,
                en_voyage_no=voyage_no or None,
                en_bl_cutoff=bl_cutoff_str,
                en_special_instructions=special_instructions or None,
                en_requestor=request.user.get_full_name() or request.user.username,
            )
            enquiry.save()
            
            current_fy = get_financial_year()
            prefix = f"{current_fy}_WEB_EN_"
            enquiry.en_enquirynumber = generate_next_number(EnquirynoteInfo, 'en_enquirynumber', prefix, 6)
            enquiry.save(update_fields=['en_enquirynumber'])
            
            if vc_obj and vt_obj and veh_count > 0:
                try:
                    Enquirynotevehicle.objects.create(
                        env_enquirynumber=enquiry,
                        env_vehiclecategory=vc_obj,
                        env_vehicletype=vt_obj,
                        env_quantity=veh_count,
                        env_updated_by=request.user
                    )
                except Exception as inner_e:
                     print(f"Failed to create vehicle detail: {inner_e}")
            
            if is_factory:
                messages.success(request, f'Movement request ({from_loc.place_name} → {to_loc.place_name}) submitted to Logistics for vehicle sizing & approval!')
            else:
                messages.success(request, f'Booking ({from_loc.place_name} → {to_loc.place_name}) submitted successfully!')
            return redirect('customer_enquiry_list')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'asset_mgt_app/customer_enquiry_add.html', {
        'customer': customer,
        'department': department,
        'departments': departments,
        'places': places,
        'categories': categories,
        'types': types,
        'trip_types': trip_types,
        'is_lp': is_lp,
        'default_agent_name': agent_name,
        'portal_ctx': portal_ctx,
    })


@login_required(login_url='/SMS/customer_login/2/')
def customer_enquiry_approve(request, enquiry_id):
    """
    Brandix Logistics Approval & Vehicle Sizing view.
    Reviews a Factory indent, assigns Vehicle Category/Type/Count + Export Shipping details,
    and unlocks the booking for BVM Dispatch.
    """
    customer, department, is_lp, agent_name = get_customer_context(request)
    portal_ctx = get_portal_role_context(request)
    if not customer:
        return redirect('customer_dashboard')

    if not portal_ctx['is_logistics'] and not request.user.is_superuser:
        messages.error(request, 'Only Logistics Officers can approve and size vehicle requests.')
        return redirect('customer_enquiry_list')

    enquiry = get_object_or_404(
        get_portal_enquiry_queryset(customer, portal_ctx),
        id=enquiry_id
    )

    if enquiry.en_status_id == 8:
        messages.error(request, 'Cancelled bookings cannot be approved.')
        return redirect('customer_enquiry_list')

    categories = VehiclecategoryInfo.objects.all().order_by('vc_vehiclecategory')
    types = VehicletypeInfo.objects.all().order_by('vt_vehicletype')

    if request.method == 'POST':
        category_id = request.POST.get('vehicle_category')
        type_id = request.POST.get('vehicle_type')
        no_of_veh = request.POST.get('no_of_veh', '')

        vc_obj = VehiclecategoryInfo.objects.filter(id=category_id).first() if category_id else None
        vt_obj = VehicletypeInfo.objects.filter(id=type_id).first() if type_id else None

        errors = []
        if not vc_obj:
            errors.append('Please select a Vehicle Category.')
        if not vt_obj:
            errors.append('Please select a Vehicle Type.')
        try:
            veh_count = int(no_of_veh)
            if veh_count < 1:
                errors.append('Please enter Number of Vehicles (minimum 1).')
        except (ValueError, TypeError):
            veh_count = 0
            errors.append('Please enter Number of Vehicles (minimum 1).')

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'asset_mgt_app/customer_enquiry_approve.html', {
                'customer': customer,
                'enquiry': enquiry,
                'categories': categories,
                'types': types,
                'portal_ctx': portal_ctx,
            })

        enquiry.en_vehicledetails = vc_obj.vc_vehiclecategory
        enquiry.en_no_of_vehicles = veh_count
        if not enquiry.en_consignmentdetails and vt_obj:
            enquiry.en_consignmentdetails = vt_obj.vt_vehicletype

        enquiry.en_shipment_type = request.POST.get('shipment_type') or enquiry.en_shipment_type
        enquiry.en_vessel_name = request.POST.get('vessel_name') or enquiry.en_vessel_name
        enquiry.en_voyage_no = request.POST.get('voyage_no') or enquiry.en_voyage_no
        bl_cutoff_val = request.POST.get('bl_cutoff')
        if bl_cutoff_val:
            enquiry.en_bl_cutoff = bl_cutoff_val
        special_instr = request.POST.get('special_instructions')
        if special_instr is not None:
            enquiry.en_special_instructions = special_instr

        enquiry.en_is_approved = True
        enquiry.en_approved_by = request.user.get_full_name() or request.user.username
        enquiry.en_approved_date = timezone.now()
        enquiry.save()

        Enquirynotevehicle.objects.update_or_create(
            env_enquirynumber=enquiry,
            defaults={
                'env_vehiclecategory': vc_obj,
                'env_vehicletype': vt_obj,
                'env_quantity': veh_count,
                'env_updated_by': request.user,
            }
        )

        route_label = f"{enquiry.en_fromlocaion.place_name} → {enquiry.en_tolocation.place_name}" if enquiry.en_fromlocaion and enquiry.en_tolocation else "Shipment"
        messages.success(request, f'{route_label} approved and sent to BVM Dispatch!')
        return redirect('customer_enquiry_list')

    env = Enquirynotevehicle.objects.filter(env_enquirynumber=enquiry).first()
    return render(request, 'asset_mgt_app/customer_enquiry_approve.html', {
        'customer': customer,
        'enquiry': enquiry,
        'env': env,
        'categories': categories,
        'types': types,
        'portal_ctx': portal_ctx,
    })

@login_required(login_url='/SMS/customer_login/2/')
def customer_enquiry_edit(request, enquiry_id):
    """Edit an existing customer enquiry."""
    from ..sub_models.tr_triptype_mod import Tr_triptype_Info
    customer, department, is_lp, agent_name = get_customer_context(request)
    if not customer:
        return redirect('customer_dashboard')

    portal_ctx = get_portal_role_context(request)
    is_factory = portal_ctx['is_factory']
    is_logistics = portal_ctx['is_logistics']

    enquiry = get_object_or_404(get_portal_enquiry_queryset(customer, portal_ctx), id=enquiry_id)

    if enquiry.en_status_id == 8:
        messages.error(request, 'Cancelled bookings cannot be edited.')
        return redirect('customer_enquiry_list')

    if is_factory and enquiry.en_is_approved:
        messages.error(request, 'Approved bookings cannot be edited by Factory. Please contact Logistics.')
        return redirect('customer_enquiry_list')

    # If Logistics clicks edit on an unapproved Factory request, send them to the Approval & Sizing screen
    if is_logistics and not enquiry.en_is_approved:
        return redirect('customer_enquiry_approve', enquiry_id=enquiry.id)

    if request.method == 'POST':
        from_loc_id = request.POST.get('from_location')
        to_loc_id = request.POST.get('to_location')
        category_id = request.POST.get('vehicle_category')
        type_id = request.POST.get('vehicle_type')
        cargo_details = request.POST.get('cargo_details', '')
        
        pickup_datetime_str = request.POST.get('pickup_datetime', '')
        req_arrival_str = request.POST.get('requested_arrival_time', '')
        if is_factory and not pickup_datetime_str and req_arrival_str:
            pickup_datetime_str = req_arrival_str

        req_time = None
        if pickup_datetime_str:
            try:
                parts = pickup_datetime_str.split('T')
                req_time = parts[1] if len(parts) > 1 else None
            except Exception:
                pass
        
        dept_id = request.POST.get('customer_department')
        trip_type_id = request.POST.get('trip_type')
        no_veh_val = request.POST.get('no_of_veh')

        # Resolve objects
        selected_dept = CustomerdepartmentInfo.objects.filter(id=dept_id).first() if dept_id else enquiry.en_customerdepartment
        tt_obj = Tr_triptype_Info.objects.filter(id=trip_type_id).first() if trip_type_id else enquiry.en_trip_type
        from_loc = Places.objects.filter(id=from_loc_id).first() if from_loc_id else enquiry.en_fromlocaion
        to_loc = Places.objects.filter(id=to_loc_id).first() if to_loc_id else enquiry.en_tolocation
        vc_obj = VehiclecategoryInfo.objects.filter(id=category_id).first() if category_id else None
        vt_obj = VehicletypeInfo.objects.filter(id=type_id).first() if type_id else None

        veh_count = enquiry.en_no_of_vehicles or 0
        if not is_factory:
            try:
                veh_count = int(no_veh_val)
                if veh_count < 1:
                    veh_count = None
            except (ValueError, TypeError):
                veh_count = None

        errors = []
        if not selected_dept:
            errors.append('Please select a Department.')
        if not tt_obj:
            errors.append('Please select a Trip Type.')
        if not pickup_datetime_str and not enquiry.en_pickupdatetime:
            errors.append('Please select Requested Arrival Date & Time.' if is_factory else 'Please select Vehicle Required Date & Time.')
        if not from_loc:
            errors.append('Please select an Origin.')
        if not to_loc:
            errors.append('Please select a Destination.')
        if not is_factory:
            if not vc_obj:
                errors.append('Please select a Vehicle Category.')
            if not vt_obj:
                errors.append('Please select a Vehicle Type.')
            if not veh_count:
                errors.append('Please enter Number of Vehicles (minimum 1).')

        if errors:
            for err in errors:
                messages.error(request, err)
            places = Places.objects.all().order_by('place_name')
            categories = VehiclecategoryInfo.objects.all().order_by('vc_vehiclecategory')
            types = VehicletypeInfo.objects.all().order_by('vt_vehicletype')
            departments = CustomerdepartmentInfo.objects.all().order_by('ct_customerdepartment')
            trip_types = Tr_triptype_Info.objects.all().order_by('tr_trip_type')
            env = Enquirynotevehicle.objects.filter(env_enquirynumber=enquiry).first()
            return render(request, 'asset_mgt_app/customer_enquiry_add.html', {
                'customer': customer,
                'department': selected_dept,
                'departments': departments,
                'places': places,
                'categories': categories,
                'types': types,
                'trip_types': trip_types,
                'is_lp': is_lp,
                'enquiry': enquiry,
                'env': env,
                'edit_mode': True,
                'default_agent_name': agent_name,
                'portal_ctx': portal_ctx,
            })

        # Update enquiry fields
        enquiry.en_trip_type = tt_obj
        enquiry.en_customerdepartment = selected_dept
        enquiry.en_fromlocaion = from_loc
        enquiry.en_tolocation = to_loc
        if vc_obj:
            enquiry.en_vehicledetails = vc_obj.vc_vehiclecategory

        if pickup_datetime_str:
            enquiry.en_pickupdatetime = pickup_datetime_str
        if req_time:
            enquiry.en_vehicle_req_time = req_time

        if cargo_details:
            enquiry.en_consignmentdetails = cargo_details
        elif vt_obj:
            enquiry.en_consignmentdetails = vt_obj.vt_vehicletype

        enquiry.en_agent_name = request.POST.get('agent_name') or portal_ctx.get('agent_account') or enquiry.en_agent_name
        if not is_factory and veh_count is not None:
            enquiry.en_no_of_vehicles = veh_count

        if is_factory or is_logistics:
            enquiry.en_plant_code = request.POST.get('plant_code') or enquiry.en_plant_code
            enquiry.en_buyer_name = request.POST.get('buyer_name') or enquiry.en_buyer_name
            enquiry.en_po_numbers = request.POST.get('po_numbers') or enquiry.en_po_numbers
            if req_arrival_str:
                enquiry.en_requested_arrival_time = req_arrival_str
            req_del_str = request.POST.get('requested_delivery_time')
            if req_del_str:
                enquiry.en_requested_delivery_time = req_del_str
            otd_str = request.POST.get('otd_cutoff')
            if otd_str:
                enquiry.en_otd_cutoff = otd_str

        if is_logistics:
            enquiry.en_shipment_type = request.POST.get('shipment_type') or enquiry.en_shipment_type
            enquiry.en_vessel_name = request.POST.get('vessel_name') or enquiry.en_vessel_name
            enquiry.en_voyage_no = request.POST.get('voyage_no') or enquiry.en_voyage_no
            bl_str = request.POST.get('bl_cutoff')
            if bl_str:
                enquiry.en_bl_cutoff = bl_str

        no_pcs_val = request.POST.get('no_of_pcs')
        if no_pcs_val not in (None, ''):
            try:
                enquiry.en_no_of_pcs = int(no_pcs_val)
            except (ValueError, TypeError):
                pass

        enquiry.en_weight = request.POST.get('weight', enquiry.en_weight)
        enquiry.en_dimensions = request.POST.get('dimensions', enquiry.en_dimensions)
        enquiry.en_cbm = request.POST.get('cbm', enquiry.en_cbm)
        enquiry.en_pickup_contact_name = request.POST.get('pickup_contact_name', enquiry.en_pickup_contact_name)
        enquiry.en_pickup_contact_mobile = request.POST.get('pickup_contact_mobile', enquiry.en_pickup_contact_mobile)
        enquiry.en_delivery_contact_name = request.POST.get('delivery_contact_name', enquiry.en_delivery_contact_name)
        enquiry.en_delivery_contact_mobile = request.POST.get('delivery_contact_mobile', enquiry.en_delivery_contact_mobile)

        enquiry.save()

        if not is_factory and vc_obj and vt_obj:
            Enquirynotevehicle.objects.update_or_create(
                env_enquirynumber=enquiry,
                defaults={
                    'env_vehiclecategory': vc_obj,
                    'env_vehicletype': vt_obj,
                    'env_quantity': enquiry.en_no_of_vehicles or 1,
                    'env_updated_by': request.user
                }
            )

        messages.success(request, f'Booking ({from_loc.place_name} → {to_loc.place_name}) updated successfully!')
        return redirect('customer_enquiry_list')

    places = Places.objects.all().order_by('place_name')
    categories = VehiclecategoryInfo.objects.all().order_by('vc_vehiclecategory')
    types = VehicletypeInfo.objects.all().order_by('vt_vehicletype')
    departments = CustomerdepartmentInfo.objects.all().order_by('ct_customerdepartment')
    trip_types = Tr_triptype_Info.objects.all().order_by('tr_trip_type')

    # Get current vehicle detail for pre-selection
    env = Enquirynotevehicle.objects.filter(env_enquirynumber=enquiry).first()

    return render(request, 'asset_mgt_app/customer_enquiry_add.html', {
        'customer': customer,
        'department': enquiry.en_customerdepartment,
        'departments': departments,
        'places': places,
        'categories': categories,
        'types': types,
        'trip_types': trip_types,
        'is_lp': is_lp,
        'enquiry': enquiry,
        'env': env,
        'edit_mode': True,
        'default_agent_name': enquiry.en_agent_name or agent_name,
        'portal_ctx': portal_ctx,
    })

@login_required(login_url='/SMS/customer_login/2/')
def customer_enquiry_list(request):
    """
    List previous enquiries and current shipments for the customer.
    """
    customer, _, is_lp, agent_name = get_customer_context(request)
    if not customer:
        return redirect('customer_dashboard')

    portal_ctx = get_portal_role_context(request)
    search_query = request.GET.get('q', '')
    approval_filter = request.GET.get('approval', '')
    
    # Get enquiries scoped by role (Standard, Parent, Factory, Logistics)
    base_qs = get_portal_enquiry_queryset(customer, portal_ctx)
    pending_approvals_count = base_qs.filter(en_is_approved=False).count()

    enquiries_qs = base_qs.select_related(
        'en_customername',
        'en_sub_customer',
        'en_fromlocaion',
        'en_tolocation',
        'en_customerdepartment'
    ).prefetch_related(
        'tripdetailinfo_set',
        'vehicle_allotmentinfo_set',
        'consignmentdetailinfo_set'
    )

    if approval_filter == 'pending':
        enquiries_qs = enquiries_qs.filter(en_is_approved=False)
    
    if search_query:
        enquiries_qs = enquiries_qs.filter(
            Q(en_enquirynumber__icontains=search_query) |
            Q(en_fromlocaion__place_name__icontains=search_query) |
            Q(en_tolocation__place_name__icontains=search_query) |
            Q(tripdetailinfo__tr_tripnumber__icontains=search_query) |
            Q(tripdetailinfo__tr_vehiclenumber__icontains=search_query) |
            Q(vehicle_allotmentinfo__va_vehiclenumber__vm_registrationnumber__icontains=search_query) |
            Q(vehicle_allotmentinfo__va_vehiclenumber_mkt__icontains=search_query) |
            Q(tripdetailinfo__tr_consignmentnumber__co_consignmentnumber__icontains=search_query) |
            Q(en_customerdepartment__ct_customerdepartment__icontains=search_query)
        ).distinct()

    # Status filter from dashboard cards
    status_filter = request.GET.get('status', '')
    from ..sub_models.vehicle_allotment_mod import Vehicle_allotmentInfo
    from datetime import timedelta

    first_day_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Pre-compute allotted IDs needed for 'active' and 'allotted' filters (current month only)
    _business_trips = TripdetailInfo.objects.filter(
        tr_enquirynumber__en_customername=customer,
        tr_category_id=1
    )
    _allotted_trip_enq_ids = _business_trips.filter(
        tr_vehiclenumber__isnull=False,
        tr_enquirynumber__en_created_at__gte=first_day_of_month
    ).exclude(
        tr_vehiclenumber=''
    ).values_list('tr_enquirynumber_id', flat=True).distinct()

    _allotted_va_ids = Vehicle_allotmentInfo.objects.filter(
        va_enquirynumber__en_customername=customer,
        va_enquirynumber__en_created_at__gte=first_day_of_month
    ).filter(
        ~Q(va_vehiclenumber__isnull=True) | (~Q(va_vehiclenumber_mkt='') & ~Q(va_vehiclenumber_mkt__isnull=True))
    ).values_list('va_enquirynumber_id', flat=True).distinct()

    _allotted_all_ids = list(set(list(_allotted_trip_enq_ids) + list(_allotted_va_ids)))

    _in_transit_enq_ids = _business_trips.filter(
        tc_financestatus_id=1,
        tr_created_at__gte=first_day_of_month
    ).values_list('tr_enquirynumber_id', flat=True).distinct()

    _active_trip_enq_ids = list(_business_trips.filter(
        tc_financestatus_id__in=[1, 8]
    ).values_list('tr_enquirynumber_id', flat=True).distinct())

    from sms_app.models import Trip_closure_files_Info
    _closed_trip_numbers = Trip_closure_files_Info.objects.exclude(
        Q(tcf_pod__isnull=True) | Q(tcf_pod='')
    ).values_list('tcf_tripnumber', flat=True)
    _all_closed_via_closure_enq_ids = _business_trips.filter(
        tr_tripnumber__in=_closed_trip_numbers
    ).values_list('tr_enquirynumber_id', flat=True).distinct()

    _all_delivered_enq_ids = list(set(
        list(_business_trips.filter(
            tc_financestatus_id__in=[2, 7, 9]
        ).values_list('tr_enquirynumber_id', flat=True).distinct()) +
        list(_all_closed_via_closure_enq_ids)
    ) - set(_active_trip_enq_ids))

    first_day_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    _closed_via_closure_enq_ids = _business_trips.filter(
        tr_tripnumber__in=_closed_trip_numbers,
        tr_created_at__gte=first_day_of_month
    ).values_list('tr_enquirynumber_id', flat=True).distinct()

    _delivered_enq_ids = list(set(
        list(_business_trips.filter(
            tc_financestatus_id__in=[2, 7, 9],
            tr_created_at__gte=first_day_of_month
        ).values_list('tr_enquirynumber_id', flat=True).distinct()) +
        list(_closed_via_closure_enq_ids)
    ) - set(_active_trip_enq_ids))

    # Exclusions for dead/closed/cancelled enquiries
    _all_trips = TripdetailInfo.objects.filter(tr_enquirynumber__en_customername=customer)
    _dead_enq_ids = list(enquiries_qs.filter(en_status_id__in=[5, 8]).values_list('id', flat=True))
    _cancelled_trip_enq_ids = list(_all_trips.filter(
        Q(tc_financestatus_id__in=[10, 11]) |
        Q(tc_financestatus__status__icontains='Cancellation') |
        Q(tc_financestatus__status__icontains='Cancelled') |
        Q(tr_remarks__icontains='Cancelled')
    ).values_list('tr_enquirynumber_id', flat=True).distinct())
    _dead_enq_ids = list(set(_dead_enq_ids + _cancelled_trip_enq_ids))

    _active_trips_enq_ids = _all_trips.exclude(tc_financestatus_id__in=[2, 3, 4, 5, 7, 9, 10, 11]).values_list('tr_enquirynumber_id', flat=True).distinct()
    _any_trip_enq_ids = _all_trips.values_list('tr_enquirynumber_id', flat=True).distinct()
    _fully_closed_enq_ids = list(set(_any_trip_enq_ids) - set(_active_trips_enq_ids))

    if status_filter == 'active':
        # Active = enquiries with NO vehicle allotted, recent 3 days, not dead
        recent_limit = timezone.now() - timedelta(days=3)
        enquiries_qs = enquiries_qs.filter(
            en_created_at__gte=recent_limit
        ).exclude(
            id__in=_allotted_all_ids
        ).exclude(
            id__in=_dead_enq_ids
        ).exclude(
            id__in=_fully_closed_enq_ids
        )
    elif status_filter == 'transit':
        # In-Transit = business trips with status 1
        enquiries_qs = enquiries_qs.filter(id__in=_in_transit_enq_ids)
    elif status_filter == 'delivered':
        # Delivered = business trips with status 2 or 7 (closed/settled)
        enquiries_qs = enquiries_qs.filter(id__in=_delivered_enq_ids)
    elif status_filter == 'cancelled':
        enquiries_qs = enquiries_qs.filter(id__in=_dead_enq_ids)
    elif status_filter == 'allotted':
        # Allotted = has vehicle, created or allotted in current month, but NOT yet in-transit or delivered, and NOT dead
        enquiries_qs = enquiries_qs.filter(
            id__in=_allotted_all_ids,
            en_created_at__gte=first_day_of_month
        ).exclude(
            id__in=_in_transit_enq_ids
        ).exclude(
            id__in=_all_delivered_enq_ids
        ).exclude(
            id__in=_dead_enq_ids
        ).exclude(
            id__in=_fully_closed_enq_ids
        ).exclude(
            id__in=_in_transit_enq_ids
        ).exclude(
            id__in=_all_delivered_enq_ids
        ).exclude(
            id__in=_dead_enq_ids
        ).exclude(
            id__in=_fully_closed_enq_ids
        )
    else:
        # Default (My Bookings list with no status filter): filter by current month
        enquiries_qs = enquiries_qs.filter(en_created_at__gte=first_day_of_month)

    enquiries_qs = enquiries_qs.order_by('-en_created_at')

    # Pagination - 50 items per page
    from django.core.paginator import Paginator
    paginator = Paginator(enquiries_qs, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Build enriched data for template (1 row per enquiry, with per-vehicle flows & modals)
    enquiry_list = []
    flow_modals = []
    for row_idx, enq in enumerate(page_obj, start=1):
        cn = enq.consignmentdetailinfo_set.first()

        if status_filter == 'transit':
            trips_qs = list(enq.tripdetailinfo_set.filter(tc_financestatus_id=1, tr_category_id=1))
            vas_qs = []
        elif status_filter == 'delivered':
            trips_qs = list(enq.tripdetailinfo_set.filter(
                Q(tc_financestatus_id__in=[2, 7, 9]) | Q(tr_tripnumber__in=_closed_trip_numbers),
                tr_category_id=1
            ))
            vas_qs = []
        elif status_filter == 'allotted':
            trips_qs = list(enq.tripdetailinfo_set.filter(tr_category_id=1).exclude(
                tc_financestatus_id__in=[1, 2, 3, 7, 9]
            ).exclude(
                tr_tripnumber__in=_closed_trip_numbers
            ))
            vas_qs = list(enq.vehicle_allotmentinfo_set.all())
        elif status_filter == 'active':
            trips_qs = []
            vas_qs = []
        else:
            trips_qs = list(enq.tripdetailinfo_set.filter(tr_category_id=1))
            vas_qs = list(enq.vehicle_allotmentinfo_set.all())

        pairs = []
        covered_vehicles = set()
        for t in trips_qs:
            t_veh = (t.tr_vehiclenumber or '').strip().upper()
            if t_veh:
                covered_vehicles.add(t_veh)
            matched_va = None
            for v in vas_qs:
                v_veh = (str(v.va_vehiclenumber) if v.va_vehiclenumber else (v.va_vehiclenumber_mkt or '')).strip().upper()
                if v_veh and v_veh == t_veh:
                    matched_va = v
                    break
            pairs.append((t, matched_va))

        for v in vas_qs:
            v_veh = (str(v.va_vehiclenumber) if v.va_vehiclenumber else (v.va_vehiclenumber_mkt or '')).strip().upper()
            if v_veh and v_veh in covered_vehicles:
                continue
            if v_veh:
                covered_vehicles.add(v_veh)
            pairs.append((None, v))

        import re
        vehicles = []
        for trip, va in pairs:
            vehicle_no = '-'
            if trip and trip.tr_vehiclenumber:
                vehicle_no = trip.tr_vehiclenumber
            elif va:
                if va.va_vehiclenumber:
                    vehicle_no = str(va.va_vehiclenumber)
                elif va.va_vehiclenumber_mkt:
                    vehicle_no = va.va_vehiclenumber_mkt

            driver_name = None
            if trip and trip.tr_drivername:
                driver_name = trip.tr_drivername
            elif va and va.va_drivername:
                driver_name = va.va_drivername
            if driver_name:
                driver_name = re.sub(r'\s*\(\d+\)\s*$', '', str(driver_name)).strip()

            driver_number = None
            if trip and trip.tr_drivernumber:
                driver_number = trip.tr_drivernumber
            elif va and va.va_drivernumber:
                driver_number = va.va_drivernumber

            is_delivered = False
            if trip and (trip.tc_financestatus_id in [2, 3, 4, 5, 6, 7, 9, 10, 11] or (trip.tr_tripnumber and trip.tr_tripnumber in _closed_trip_numbers)):
                is_delivered = True

            track_link = ''
            if not is_delivered and vehicle_no and vehicle_no != '-':
                track_link = f'/SMS/SMS/customer_track_vehicle/?vehicle={vehicle_no}'
                if trip:
                    track_link += f'&trip_id={trip.id}'

            pod_trip_id = None
            if trip and is_delivered:
                closure = Trip_closure_files_Info.objects.filter(tcf_tripnumber=trip.tr_tripnumber).first()
                if closure and closure.tcf_pod:
                    pod_trip_id = trip.id
                if not pod_trip_id and trip.tc_pod_attachment:
                    pod_trip_id = trip.id

            if vehicle_no != '-' or driver_name or driver_number:
                v_flow = compute_shipment_flow(
                    enq=enq,
                    trip=trip,
                    va=va,
                    is_delivered=is_delivered,
                    pod_trip_id=pod_trip_id,
                    track_link=track_link
                )
                v_cn = trip.tr_consignmentnumber if (trip and trip.tr_consignmentnumber) else cn
                seal_no = (
                    (v_cn.co_seal_number if v_cn else None)
                    or (trip.tr_seal_number if trip else None)
                    or ''
                ).strip()
                has_seals = bool(
                    seal_no
                    or (v_cn and (v_cn.co_eseal_number or v_cn.co_dan_aod_no or v_cn.co_client_invoice_no))
                    or (trip and (trip.tr_eseal_number or trip.tr_dan_aod_no or trip.tr_client_invoice_no or trip.tr_return_job))
                )
                vehicles.append({
                    'trip_id': trip.id if trip else None,
                    'vehicle_no': vehicle_no,
                    'driver_name': driver_name,
                    'driver_number': driver_number,
                    'track_link': track_link,
                    'pod_trip_id': pod_trip_id,
                    'is_delivered': is_delivered,
                    'has_seals': has_seals,
                    'seal_no': seal_no,
                    'flow': v_flow,
                })

        # Primary trip / va for enquiry-level summary & flow modal
        primary_trip, primary_va = pairs[0] if pairs else (None, None)
        primary_veh = vehicles[0]['vehicle_no'] if vehicles else '-'
        primary_driver_name = vehicles[0]['driver_name'] if vehicles else None
        primary_driver_number = vehicles[0]['driver_number'] if vehicles else None
        primary_track_link = vehicles[0]['track_link'] if vehicles else ''
        primary_pod_trip_id = vehicles[0]['pod_trip_id'] if vehicles else None
        primary_is_delivered = vehicles[0]['is_delivered'] if vehicles else False

        customer_ref = enq.en_enquirynumber
        if primary_trip and primary_trip.tr_customerref:
            customer_ref = primary_trip.tr_customerref

        cnote = '-'
        if primary_trip and primary_trip.tr_consignmentnumber and primary_trip.tr_consignmentnumber.co_consignmentnumber:
            cnote = primary_trip.tr_consignmentnumber.co_consignmentnumber
        elif cn and cn.co_consignmentnumber:
            cnote = cn.co_consignmentnumber
        elif primary_trip and primary_trip.tr_tripnumber:
            cnote = primary_trip.tr_tripnumber

        consignment_id = None
        cus_ref_num = None
        if primary_trip and primary_trip.tr_consignmentnumber:
            consignment_id = primary_trip.tr_consignmentnumber.id
            cus_ref_num = primary_trip.tr_consignmentnumber.co_cusrefnum
        elif cn:
            consignment_id = cn.id
            cus_ref_num = cn.co_cusrefnum

        flow = compute_shipment_flow(
            enq=enq,
            trip=primary_trip,
            va=primary_va,
            is_delivered=primary_is_delivered,
            pod_trip_id=primary_pod_trip_id,
            track_link=primary_track_link
        )

        if vehicles:
            for v_idx, v in enumerate(vehicles, start=1):
                m_id = f"flow-modal-{row_idx}-{v_idx}"
                v['modal_id'] = m_id
                flow_modals.append({'modal_id': m_id, 'enq': enq, 'flow': v['flow']})
        elif flow:
            m_id = f"flow-modal-{row_idx}"
            flow_modals.append({'modal_id': m_id, 'enq': enq, 'flow': flow})

        has_gate_or_beyond = any(v['flow'].get('current_stage', 1) >= 3 for v in vehicles)
        can_cancel = (
            enq.en_status_id not in (5, 8)
            and not has_gate_or_beyond
            and not portal_ctx.get('is_parent')
        )

        enquiry_list.append({
            'enq': enq,
            'vehicles': vehicles,
            'can_cancel': can_cancel,
            'vehicle_no': primary_veh,
            'customer_ref': customer_ref,
            'cnote': cnote,
            'track_link': primary_track_link,
            'pod_trip_id': primary_pod_trip_id,
            'consignment_id': consignment_id,
            'cus_ref_num': cus_ref_num,
            'driver_name': primary_driver_name,
            'driver_number': primary_driver_number,
            'is_delivered': primary_is_delivered,
            'flow': flow,
        })
    
    return render(request, 'asset_mgt_app/customer_enquiry_list.html', {
        'enquiry_list': enquiry_list,
        'flow_modals': flow_modals,
        'search_query': search_query,
        'page_obj': page_obj,
        'status_filter': status_filter,
        'approval_filter': approval_filter,
        'pending_approvals_count': pending_approvals_count,
        'portal_ctx': portal_ctx,
    })

@login_required
def customer_track_vehicle(request):
    """Customer-facing vehicle tracking page with clean UI and trip lifecycle integration."""
    raw_vehicle = request.GET.get('vehicle', '').strip()
    vehicle_number = raw_vehicle.upper().replace(' ', '').replace('-', '')
    trip_id = request.GET.get('trip_id')
    trip = None
    is_closed = False
    assigned_time = None
    closed_time = None
    trip_number = None
    trip_status = None
    origin = None
    destination = None

    if trip_id:
        trip = TripdetailInfo.objects.filter(id=trip_id).select_related(
            'tr_departedlocation', 'tr_reportedlocation', 'tc_financestatus', 'tr_enquirynumber',
            'tr_enquirynumber__en_fromlocaion', 'tr_enquirynumber__en_tolocation'
        ).first()
    elif vehicle_number:
        trip = TripdetailInfo.objects.filter(
            Q(tr_vehiclenumber__iexact=raw_vehicle) |
            Q(tr_vehiclenumber__iexact=vehicle_number) |
            Q(tr_vehiclenumber__icontains=vehicle_number)
        ).select_related(
            'tr_departedlocation', 'tr_reportedlocation', 'tc_financestatus', 'tr_enquirynumber',
            'tr_enquirynumber__en_fromlocaion', 'tr_enquirynumber__en_tolocation'
        ).order_by('-id').first()

    if trip:
        if not vehicle_number and trip.tr_vehiclenumber:
            vehicle_number = trip.tr_vehiclenumber.upper().replace(' ', '').replace('-', '')
            raw_vehicle = trip.tr_vehiclenumber
        trip_number = trip.tr_tripnumber
        trip_status = str(trip.tc_financestatus) if trip.tc_financestatus else 'Trip Started'
        closed_status_ids = [2, 3, 4, 5, 6, 7, 9, 10, 11]
        closed_keywords = ['closed', 'settled', 'cancel', 'invoice', 'approved', 'clarification', 'awaiting trip settlement']
        if trip.tc_financestatus_id in closed_status_ids or any(k in trip_status.lower() for k in closed_keywords):
            is_closed = True

        assigned_time = trip.tr_departeddate or trip.tr_created_at
        closed_time = trip.tr_reporteddate or trip.tr_updated_at if is_closed else None
        origin = trip.tr_departedlocation.place_name if trip.tr_departedlocation else (
            str(trip.tr_enquirynumber.en_fromlocaion) if trip.tr_enquirynumber and trip.tr_enquirynumber.en_fromlocaion else ''
        )
        destination = trip.tr_reportedlocation.place_name if trip.tr_reportedlocation else (
            str(trip.tr_enquirynumber.en_tolocation) if trip.tr_enquirynumber and trip.tr_enquirynumber.en_tolocation else ''
        )

    return render(request, 'asset_mgt_app/customer_track_vehicle.html', {
        'vehicle_number': vehicle_number,
        'display_vehicle_number': raw_vehicle or vehicle_number,
        'trip': trip,
        'trip_number': trip_number,
        'trip_status': trip_status,
        'is_closed': is_closed,
        'assigned_time': assigned_time,
        'closed_time': closed_time,
        'origin': origin,
        'destination': destination,
    })


@login_required
def customer_shipment_tracking(request, trip_id):
    """
    Real-time tracking view for a specific shipment.
    """
    customer, _, is_lp, agent_name = get_customer_context(request)
    trip = get_object_or_404(TripdetailInfo, id=trip_id, tr_enquirynumber__en_customername=customer)
    
    enq = trip.tr_enquirynumber
    va = enq.vehicle_allotmentinfo_set.first() if enq else None
    closure = Trip_closure_files_Info.objects.filter(tcf_tripnumber=trip.tr_tripnumber).first()
    is_delivered = (trip.tc_financestatus_id in [2, 3, 4, 5, 6, 7, 9, 10, 11] or bool(closure))
    pod_trip_id = trip.id if ((closure and closure.tcf_pod) or trip.tc_pod_attachment) else None
    track_link = f'/SMS/SMS/customer_track_vehicle/?vehicle={trip.tr_vehiclenumber}&trip_id={trip.id}' if trip.tr_vehiclenumber and not is_delivered else ''
    flow = compute_shipment_flow(enq, trip, va, is_delivered=is_delivered, pod_trip_id=pod_trip_id, track_link=track_link)

    return render(request, 'asset_mgt_app/customer_shipment_tracking.html', {
        'trip': trip,
        'customer': customer,
        'flow': flow,
    })

@login_required
def download_pod(request, trip_id):
    """View POD inline — combines all uploaded attachment pages into a single multi-page PDF."""
    import os
    from django.conf import settings
    from django.http import HttpResponse
    from sms_app.sub_views.tripdetail_add_view import generate_combined_pod_pdf

    customer, _, is_lp, agent_name = get_customer_context(request)
    trip = get_object_or_404(TripdetailInfo, id=trip_id, tr_enquirynumber__en_customername=customer)

    # Generate combined PDF of all uploaded attachment pages/files
    pdf_buf = generate_combined_pod_pdf(trip.tr_tripnumber)
    if pdf_buf:
        filename = str(trip.tr_tripnumber)
        if trip and trip.tr_consignmentnumber:
            filename = str(trip.tr_consignmentnumber.co_consignmentnumber)
        filename = filename.replace(" ", "_").replace("/", "_")

        response = HttpResponse(pdf_buf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{filename}.pdf"'
        return response

    file_url = None
    file_name = None
    is_pdf = False

    # Try closure files first
    closure = Trip_closure_files_Info.objects.filter(tcf_tripnumber=trip.tr_tripnumber).first()
    if closure and closure.tcf_pod:
        fp = os.path.join(settings.MEDIA_ROOT, str(closure.tcf_pod))
        if os.path.exists(fp):
            file_url = closure.tcf_pod.url
            file_name = os.path.basename(str(closure.tcf_pod))
            is_pdf = file_name.lower().endswith('.pdf')

    # Fallback to trip attachment
    if not file_url and trip.tc_pod_attachment:
        fp = os.path.join(settings.MEDIA_ROOT, str(trip.tc_pod_attachment))
        if os.path.exists(fp):
            file_url = trip.tc_pod_attachment.url
            file_name = os.path.basename(str(trip.tc_pod_attachment))
            is_pdf = file_name.lower().endswith('.pdf')

    if not file_url:
        messages.error(request, "POD document not found for this shipment.")
        return redirect(request.META.get('HTTP_REFERER', 'customer_dashboard'))

    return render(request, 'asset_mgt_app/view_pod.html', {
        'file_url': file_url,
        'file_name': file_name,
        'is_pdf': is_pdf,
        'trip_number': trip.tr_tripnumber,
    })

@login_required
def download_dmr(request, trip_id):
    """Generate and download a single-trip DMR report as Excel."""
    from .dmr_report_view import build_dmr_excel_workbook
    from django.http import HttpResponse
    from io import BytesIO


    customer, _, is_lp, agent_name = get_customer_context(request)
    trip = get_object_or_404(TripdetailInfo, id=trip_id, tr_enquirynumber__en_customername=customer)
    
    # Use existing DMR logic
    dept_id = trip.tr_enquirynumber.en_customerdepartment_id if trip.tr_enquirynumber.en_customerdepartment else None
    dept_name = trip.tr_enquirynumber.en_customerdepartment.dept_name if trip.tr_enquirynumber.en_customerdepartment else "Transport"
    wb, _ = build_dmr_excel_workbook(
        customer_obj=customer,
        dept_id=dept_id,
        dept_name=dept_name,
        from_loc=trip.tr_departedlocation_id,
        to_loc=trip.tr_reportedlocation_id,
        trips=[trip]
    )

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="DMR_{trip.tr_tripnumber}.xlsx"'
    return response

@login_required(login_url='/SMS/customer_login/2/')
def customer_documents(request):
    """Documents page showing all PODs and documents for the customer."""
    customer, department, is_lp, agent_name = get_customer_context(request)
    if not customer:
        return redirect('customer_dashboard')

    portal_ctx = get_portal_role_context(request)
    
    from django.core.paginator import Paginator
    from django.db.models import Prefetch

    # Get trip numbers that have a POD in the closure table
    closure_trip_numbers = list(Trip_closure_files_Info.objects.exclude(
        tcf_pod__isnull=True
    ).exclude(
        tcf_pod=''
    ).values_list('tcf_tripnumber', flat=True))

    # Get all trips scoped by role (Factory / Logistics / Parent / Standard) that have a POD
    trips_qs = get_portal_trip_queryset(customer, portal_ctx).filter(
        Q(tc_pod_attachment__isnull=False, tc_pod_attachment__gt='') |
        Q(tr_tripnumber__in=closure_trip_numbers)
    ).select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_fromlocaion',
        'tr_enquirynumber__en_tolocation',
        'tc_financestatus'
    ).order_by('-tr_created_at')

    if department:
        trips_qs = trips_qs.filter(tr_enquirynumber__en_customerdepartment=department)
    
    # Paginate results (25 per page)
    paginator = Paginator(trips_qs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Build document list for current page
    import os
    from django.conf import settings
    
    # Batch fetch closure files for the current page to avoid N+1 queries
    trip_numbers = [t.tr_tripnumber for t in page_obj if t.tr_tripnumber]
    closures = Trip_closure_files_Info.objects.filter(tcf_tripnumber__in=trip_numbers).only('tcf_tripnumber', 'tcf_pod')
    closure_map = {c.tcf_tripnumber: c for c in closures}
    
    documents = []
    for trip in page_obj:
        closure = closure_map.get(trip.tr_tripnumber)
        has_pod = False
        pod_source = ''
        
        if closure and closure.tcf_pod:
            has_pod = True
            pod_source = 'closure'
            file_url = closure.tcf_pod.url
        if not has_pod and trip.tc_pod_attachment:
            has_pod = True
            pod_source = 'trip'
            file_url = trip.tc_pod_attachment.url
        
        if has_pod:
            file_name = os.path.basename(file_url) if file_url else f"POD_{trip.tr_tripnumber}"
            documents.append({
                'trip': trip,
                'trip_number': trip.tr_tripnumber,
                'from_location': trip.tr_enquirynumber.en_fromlocaion.place_name if trip.tr_enquirynumber.en_fromlocaion else '-',
                'to_location': trip.tr_enquirynumber.en_tolocation.place_name if trip.tr_enquirynumber.en_tolocation else '-',
                'vehicle_no': trip.tr_vehiclenumber or '-',
                'status': trip.tc_financestatus.status if trip.tc_financestatus else '-',
                'date': trip.tr_created_at,
                'doc_type': 'POD',
                'pod_source': pod_source,
            })
    
    return render(request, 'asset_mgt_app/customer_documents.html', {
        'customer': customer,
        'department': department,
        'documents': documents,
        'page_obj': page_obj,
    })

@login_required(login_url='/SMS/customer_login/2/')
def customer_profile(request):
    """View to display customer user profile."""
    customer, department, is_lp, agent_name = get_customer_context(request)
    if not customer:
        return redirect('customer_dashboard')
    
    return render(request, 'asset_mgt_app/customer_profile.html', {
        'customer': customer,
        'department': department,
        'is_lp': is_lp,
        'agent_name': agent_name,
        'user': request.user
    })

@login_required(login_url='/SMS/customer_login/2/')
def customer_support(request):
    """View to display support contact information."""
    customer, department, is_lp, agent_name = get_customer_context(request)
    if not customer:
        return redirect('customer_dashboard')
        
    return render(request, 'asset_mgt_app/customer_support.html', {
        'customer': customer,
        'department': department,
        'is_lp': is_lp
    })


@login_required(login_url='/SMS/customer_login/2/')
def customer_gate_update(request, enquiry_id):
    """
    Allows Brandix Factory / Logistics (or Customer Portal users) to update Gate Sealing,
    Export Invoice, DAN/AOD, Demurrage Reason, and Return Job fields.
    """
    customer, _, _, _ = get_customer_context(request)
    portal_ctx = get_portal_role_context(request)
    if not customer:
        return redirect('customer_dashboard')

    if not portal_ctx['is_factory'] and not request.user.is_superuser:
        messages.error(request, 'Only Factory users can update Gate & Sealing details.')
        return redirect('customer_enquiry_list')

    enquiry = get_object_or_404(get_portal_enquiry_queryset(customer, portal_ctx), id=enquiry_id)
    vehicle_no = (request.GET.get('vehicle') or request.POST.get('vehicle') or '').strip()
    trip_id = (request.GET.get('trip_id') or request.POST.get('trip_id') or '').strip()

    if trip_id and trip_id.isdigit():
        trip = enquiry.tripdetailinfo_set.filter(id=int(trip_id)).first()
    elif vehicle_no:
        trip = enquiry.tripdetailinfo_set.filter(tr_vehiclenumber__iexact=vehicle_no).first()
    else:
        trip = enquiry.tripdetailinfo_set.first()

    if trip and trip.tr_consignmentnumber:
        cn = trip.tr_consignmentnumber
    elif vehicle_no:
        cn = enquiry.consignmentdetailinfo_set.filter(co_vehicelnumber__iexact=vehicle_no).first() or enquiry.consignmentdetailinfo_set.first()
    else:
        cn = enquiry.consignmentdetailinfo_set.first()

    target_vehicle = vehicle_no or (trip.tr_vehiclenumber if trip else '')

    if not trip:
        messages.warning(request, 'Gate & Seals are available once a trip is created and the vehicle reports at the loading gate.')
        return redirect('customer_enquiry_list')

    gate_flow = compute_shipment_flow(enq=enquiry, trip=trip)
    if gate_flow.get('current_stage', 1) < 3:
        messages.warning(request, f'Vehicle {target_vehicle or ""} is still en route. Gate & Seals unlock once it reports at the loading gate.')
        return redirect('customer_enquiry_list')

    if request.method == 'POST':
        seal_no = request.POST.get('co_seal_number', '').strip()
        eseal_no = request.POST.get('co_eseal_number', '').strip()
        dan_no = request.POST.get('co_dan_aod_no', '').strip()
        inv_no = request.POST.get('co_client_invoice_no', '').strip()
        inv_date = request.POST.get('co_client_invoice_date') or None

        trip.tr_seal_number = seal_no or None
        trip.tr_eseal_number = eseal_no or None
        trip.tr_dan_aod_no = dan_no or None
        trip.tr_client_invoice_no = inv_no or None
        if inv_date:
            trip.tr_client_invoice_date = inv_date
        trip.tr_demurrage_reason = request.POST.get('tr_demurrage_reason', trip.tr_demurrage_reason)
        trip.tr_return_job = (request.POST.get('tr_return_job') == 'on')
        trip.save()

        if cn:
            cn.co_seal_number = seal_no or cn.co_seal_number
            cn.co_eseal_number = eseal_no or cn.co_eseal_number
            cn.co_smart_lock_number = eseal_no or cn.co_smart_lock_number
            cn.co_dan_aod_no = dan_no or cn.co_dan_aod_no
            cn.co_client_invoice_no = inv_no or cn.co_client_invoice_no
            if inv_date:
                cn.co_client_invoice_date = inv_date
            cn.save()

        label = f"Vehicle {target_vehicle}" if target_vehicle else "Shipment"
        messages.success(request, f'Gate & Sealing details updated for {label}.')
        return redirect('customer_enquiry_list')

    return render(request, 'asset_mgt_app/customer_gate_update.html', {
        'customer': customer,
        'enquiry': enquiry,
        'cn': cn,
        'trip': trip,
        'vehicle_no': target_vehicle,
        'trip_id': trip.id,
        'portal_ctx': portal_ctx,
    })


@login_required(login_url='/SMS/customer_login/2/')
def customer_enquiry_cancel(request, enquiry_id):
    """Cancel a booking before any vehicle reaches the loading gate (Stage < 3)."""
    customer, _, _, _ = get_customer_context(request)
    portal_ctx = get_portal_role_context(request)
    if not customer:
        return redirect('customer_dashboard')

    if portal_ctx['is_parent']:
        messages.error(request, 'Parent account has read-only access.')
        return redirect('customer_enquiry_list')

    enquiry = get_portal_enquiry_queryset(customer, portal_ctx).filter(id=enquiry_id).first()
    if not enquiry:
        messages.error(request, 'Booking not found or access denied.')
        return redirect('customer_enquiry_list')

    if enquiry.en_status_id == 8:
        messages.info(request, 'Booking is already cancelled.')
        return redirect('customer_enquiry_list')

    trips = enquiry.tripdetailinfo_set.filter(tr_category_id=1)
    for t in trips:
        if compute_shipment_flow(enq=enquiry, trip=t).get('current_stage', 1) >= 3:
            messages.warning(request, 'Cannot cancel after a vehicle has reached the loading gate. Use Gate & Seals -> Return The Job instead.')
            return redirect('customer_enquiry_list')

    if request.method == 'POST':
        reason = (request.POST.get('cancel_reason') or '').strip()
        note = f"[CANCELLED by {request.user.username}]" + (f" {reason}" if reason else "")
        existing_req = (enquiry.en_special_instructions or '').strip()
        enquiry.en_special_instructions = f"{existing_req}\n{note}".strip() if existing_req else note
        enquiry.en_status_id = 8
        enquiry.save(update_fields=['en_status', 'en_special_instructions'])
        route_label = f"{enquiry.en_fromlocaion.place_name} → {enquiry.en_tolocation.place_name}" if enquiry.en_fromlocaion and enquiry.en_tolocation else "Shipment"
        messages.success(request, f'Booking ({route_label}) has been cancelled.')

    return redirect('customer_enquiry_list')


def build_brandix_dmr_data(trips, hide_commercials=False):
    """
    Build Brandix OKI/DOKI DMR headers and rows with auto-calculated SLA & Turnaround KPIs.
    Masks commercial charges when hide_commercials=True (Factory Login).
    """
    headers = [
        'S.No', 'Request Id', 'Job No', 'Plant / Shipper', 'Created By', 'Created Date',
        'Approved By', 'Approved Date', 'Vehicle No', 'Driver', 'Attended By',
        'Pickup', 'Delivery', 'Requested Arrival', 'Arrived at Pickup', 'Departed Pickup',
        'Requested Delivery', 'Arrived at Delivery', 'Departed Delivery',
        'Late Booking', 'Placement Status', 'OTP (On-Time Placement)', 'OTD (On-Time Delivery)',
        'Same Day Delivery', 'Spent at PP (Hrs)', 'Spent at DP (Hrs)', 'Transit Time (Hrs)',
        'Buyer', 'Reference PO No', 'Shipment Type', 'Vessel', 'Voyage', 'BL Cutoff',
        'Security Seal', 'E-Seal No', 'DAN/AOD No', 'Export Invoice No',
        'Demurrage Reason', 'Demurrage Hrs', 'Return Job', 'Current Status'
    ]
    if not hide_commercials:
        headers.extend(['Transport Charge', 'Demurrage Charge', 'Total Charge'])

    rows = []
    for idx, trip in enumerate(trips, start=1):
        enq = trip.tr_enquirynumber
        cn = trip.tr_consignmentnumber or (enq.consignmentdetailinfo_set.first() if enq else None)
        kpis = compute_brandix_kpis(enq, trip)

        arrived_pp = trip.tr_reporteddate_pickup or trip.tr_dock_in_time
        departed_pp = trip.tr_departeddate_pickup or trip.tr_dock_out_time

        cg_inv = None
        if cn:
            from ..sub_models.consignmentgoods_mod import ConsignmentgoodsInfo
            cg_first = ConsignmentgoodsInfo.objects.filter(
                cg_consignmentnumber=cn.id,
                cg_consignerinvoice__isnull=False
            ).exclude(cg_consignerinvoice='').first()
            if cg_first:
                cg_inv = cg_first.cg_consignerinvoice
        row = [
            idx,
            enq.en_enquirynumber if enq else '-',
            (cn.co_consignmentnumber if cn else None) or trip.tr_tripnumber or '-',
            (enq.en_plant_code if enq and enq.en_plant_code else None) or (enq.en_sub_customer.cu_name if enq and enq.en_sub_customer else '-'),
            (enq.en_requestor if enq else None) or '-',
            enq.en_created_at.strftime('%d-%m-%Y %H:%M') if enq and enq.en_created_at else '-',
            (enq.en_approved_by if enq else None) or '-',
            enq.en_approved_date.strftime('%d-%m-%Y %H:%M') if enq and enq.en_approved_date else '-',
            trip.tr_vehiclenumber or '-',
            trip.tr_drivername or '-',
            trip.tr_attended_by or '-',
            enq.en_fromlocaion.place_name if enq and enq.en_fromlocaion else '-',
            enq.en_tolocation.place_name if enq and enq.en_tolocation else '-',
            enq.en_requested_arrival_time.strftime('%d-%m-%Y %H:%M') if enq and enq.en_requested_arrival_time else '-',
            arrived_pp.strftime('%d-%m-%Y %H:%M') if arrived_pp else '-',
            departed_pp.strftime('%d-%m-%Y %H:%M') if departed_pp else '-',
            enq.en_requested_delivery_time.strftime('%d-%m-%Y %H:%M') if enq and enq.en_requested_delivery_time else '-',
            trip.tr_reporteddate_delivery.strftime('%d-%m-%Y %H:%M') if trip.tr_reporteddate_delivery else '-',
            trip.tr_departeddate_delivery.strftime('%d-%m-%Y %H:%M') if trip.tr_departeddate_delivery else '-',
            kpis['late_booking'],
            kpis['placement_status'],
            kpis['on_time_placement'],
            kpis['on_time_delivery'],
            kpis['same_day_delivery'],
            kpis['spent_at_pp_hrs'] if kpis['spent_at_pp_hrs'] is not None else '-',
            kpis['spent_at_dp_hrs'] if kpis['spent_at_dp_hrs'] is not None else '-',
            kpis['transit_time_hrs'] if kpis['transit_time_hrs'] is not None else '-',
            (enq.en_buyer_name if enq else None) or '-',
            (enq.en_po_numbers if enq else None) or '-',
            (enq.en_shipment_type if enq else None) or '-',
            (enq.en_vessel_name if enq else None) or '-',
            (enq.en_voyage_no if enq else None) or '-',
            enq.en_bl_cutoff.strftime('%d-%m-%Y %H:%M') if enq and enq.en_bl_cutoff else '-',
            (cn.co_seal_number if cn else None) or trip.tr_seal_number or '-',
            (cn.co_smart_lock_number if cn else None) or (cn.co_eseal_number if cn else None) or trip.tr_eseal_number or '-',
            (cn.co_dan_aod_no if cn else None) or trip.tr_dan_aod_no or '-',
            cg_inv or (cn.co_client_invoice_no if cn else None) or trip.tr_client_invoice_no or '-',
            trip.tr_demurrage_reason or '-',
            str(trip.tr_demurrage_hours) if trip.tr_demurrage_hours else '0',
            'Yes' if trip.tr_return_job else 'No',
            trip.tc_financestatus.status if trip.tc_financestatus else 'Active',
        ]
        if not hide_commercials:
            t_cost = float(trip.tc_tripcost or 0)
            d_cost = float(trip.tc_total_halting_cost or trip.tc_haltingcost or 0)
            row.extend([t_cost, d_cost, t_cost + d_cost])
        rows.append(row)
    return headers, rows


@login_required(login_url='/SMS/customer_login/2/')
def customer_dmr_report(request):
    """
    Daily Movement Report (DMR) strictly scoped to the logged-in customer.
    Supports Date Range, Month/Year, Department filters, Search, Brandix SLA KPIs, and Excel Export.
    """
    customer, department, is_lp, agent_name = get_customer_context(request)
    if not customer:
        messages.error(request, 'Your account is not linked to a Customer Profile. Please contact support.')
        return redirect('customer_dashboard')

    portal_ctx = get_portal_role_context(request)

    from .dmr_report_view import (
        BASE_DMR_Q, apply_dmr_date_filter, build_dmr_search_filter,
        get_dmr_headers, get_dmr_rows
    )
    from django.core.paginator import Paginator

    today_dt = date.today()
    from_date = request.GET.get('from_date', '').strip()
    to_date = request.GET.get('to_date', '').strip()
    selected_month = request.GET.get('month', '')
    selected_year = request.GET.get('year', '')
    search_query = request.GET.get('q', '').strip()
    dept_id = request.GET.get('customer_department', '')

    # Base trips scoped by Parent/Child/Factory/Logistics role
    trips = get_portal_trip_queryset(customer, portal_ctx).filter(
        BASE_DMR_Q
    ).select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_enquirynumber__en_sub_customer',
        'tr_enquirynumber__en_customerdepartment',
        'tr_enquirynumber__en_fromlocaion',
        'tr_enquirynumber__en_tolocation',
        'tr_consignmentnumber',
        'tr_departedlocation',
        'tr_reportedlocation',
        'tc_financestatus'
    )

    # Department scoping
    dept_name = ""
    if department:
        trips = trips.filter(tr_enquirynumber__en_customerdepartment=department)
        dept_name = department.ct_customerdepartment
        dept_id = str(department.id)
    elif dept_id:
        trips = trips.filter(tr_enquirynumber__en_customerdepartment_id=dept_id)
        try:
            dept_name = CustomerdepartmentInfo.objects.get(id=dept_id).ct_customerdepartment
        except:
            dept_name = ""

    # Apply date filters
    trips = apply_dmr_date_filter(trips, from_date, to_date, selected_month, selected_year)

    # Search filter
    if search_query:
        trips = trips.filter(build_dmr_search_filter(search_query))

    trips = trips.order_by('-effective_dmr_date', '-id').distinct()

    total_records = trips.count()

    # KPI counts for customer summary
    in_transit_count = trips.filter(tc_financestatus_id=1).count()
    delivered_count = trips.filter(tc_financestatus_id__in=[2, 7, 9]).count()

    # Pagination
    paginator = Paginator(trips, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Headers & dynamic rows
    use_brandix_dmr = portal_ctx['is_factory'] or portal_ctx['is_logistics'] or ('brandix' in (customer.cu_name or '').lower())
    if use_brandix_dmr:
        headers, data_rows = build_brandix_dmr_data(page_obj, hide_commercials=portal_ctx['hide_commercials'])
    else:
        headers, template_key = get_dmr_headers(
            customer.cu_name, dept_name, None, None,
            customer_id=customer.id, dept_id=int(dept_id) if dept_id and str(dept_id).isdigit() else None
        )
        data_rows = get_dmr_rows(page_obj, headers, template_key, customer.cu_name, start_idx=page_obj.start_index())

    # Available departments for filter dropdown
    available_departments = CustomerdepartmentInfo.objects.filter(
        enquirynoteinfo__in=get_portal_enquiry_queryset(customer, portal_ctx)
    ).distinct().order_by('ct_customerdepartment')

    current_year = today_dt.year
    current_month = today_dt.month

    return render(request, 'asset_mgt_app/customer_dmr_report.html', {
        'customer': customer,
        'department': department,
        'dept_id': str(dept_id or ''),
        'available_departments': available_departments,
        'headers': headers,
        'data_rows': data_rows,
        'page_obj': page_obj,
        'total_records': total_records,
        'in_transit_count': in_transit_count,
        'delivered_count': delivered_count,
        'from_date': from_date,
        'to_date': to_date,
        'selected_month': int(selected_month) if (selected_month and str(selected_month).isdigit()) else current_month,
        'selected_year': int(selected_year) if (selected_year and str(selected_year).isdigit()) else current_year,
        'years': range(current_year - 5, current_year + 1),
        'search_query': search_query,
        'portal_ctx': portal_ctx,
    })


@login_required(login_url='/SMS/customer_login/2/')
def customer_dmr_export_excel(request):
    """Export DMR Excel for the logged-in customer."""
    customer, department, is_lp, agent_name = get_customer_context(request)
    if not customer:
        messages.error(request, 'Customer context not found.')
        return redirect('customer_dashboard')

    portal_ctx = get_portal_role_context(request)

    from .dmr_report_view import (
        BASE_DMR_Q, apply_dmr_date_filter, build_dmr_search_filter,
        build_dmr_excel_workbook
    )

    today_dt = date.today()
    from_date = request.GET.get('from_date', '').strip()
    to_date = request.GET.get('to_date', '').strip()
    selected_month = request.GET.get('month', '')
    selected_year = request.GET.get('year', '')
    search_query = request.GET.get('q', '').strip()
    dept_id = request.GET.get('customer_department', '')

    trips = get_portal_trip_queryset(customer, portal_ctx).filter(
        BASE_DMR_Q
    ).select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_enquirynumber__en_sub_customer',
        'tr_enquirynumber__en_customerdepartment',
        'tr_enquirynumber__en_fromlocaion',
        'tr_enquirynumber__en_tolocation',
        'tr_consignmentnumber',
        'tr_departedlocation',
        'tr_reportedlocation',
        'tc_financestatus'
    )

    dept_name = ""
    if department:
        trips = trips.filter(tr_enquirynumber__en_customerdepartment=department)
        dept_name = department.ct_customerdepartment
        dept_id = department.id
    elif dept_id:
        trips = trips.filter(tr_enquirynumber__en_customerdepartment_id=dept_id)
        try:
            dept_name = CustomerdepartmentInfo.objects.get(id=dept_id).ct_customerdepartment
        except:
            dept_name = ""

    trips = apply_dmr_date_filter(trips, from_date, to_date, selected_month, selected_year)
    if search_query:
        trips = trips.filter(build_dmr_search_filter(search_query))

    trips = trips.order_by('-effective_dmr_date', '-id').distinct()

    use_brandix_dmr = portal_ctx['is_factory'] or portal_ctx['is_logistics'] or ('brandix' in (customer.cu_name or '').lower())
    if use_brandix_dmr:
        import openpyxl
        from openpyxl.styles import Font, PatternFill
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Brandix DMR"
        headers, rows = build_brandix_dmr_data(list(trips), hide_commercials=portal_ctx['hide_commercials'])
        ws.append(headers)
        header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True)
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
        for r in rows:
            ws.append(r)
    else:
        wb, _ = build_dmr_excel_workbook(
            customer_obj=customer,
            dept_id=int(dept_id) if dept_id and str(dept_id).isdigit() else None,
            dept_name=dept_name or "Logistics",
            from_loc=None,
            to_loc=None,
            trips=list(trips)
        )

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    cust_clean = (customer.cu_nameshort or customer.cu_name or "Customer").replace(" ", "_").replace("/", "_")
    filename = f"DMR_{cust_clean}_{today_dt.strftime('%Y%m%d')}.xlsx"
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
