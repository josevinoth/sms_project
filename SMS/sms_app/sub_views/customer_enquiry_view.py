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
    if t12_done:
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
            'desc': f"Booking #{enq.en_enquirynumber}" if enq else "Indent Placed",
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

    # Base queryset for enquiries
    enquiry_qs = EnquirynoteInfo.objects.filter(en_customername=customer)
    if department:
        enquiry_qs = enquiry_qs.filter(en_customerdepartment=department)

    # All trips for this customer
    all_trips = TripdetailInfo.objects.filter(tr_enquirynumber__en_customername=customer)
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
    closed_trip_numbers = Trip_closure_files_Info.objects.values_list('tcf_tripnumber', flat=True)
    
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
        va_enquirynumber__en_customername=customer,
        va_enquirynumber__en_created_at__gte=first_day_of_month
    ).filter(
        ~Q(va_vehiclenumber__isnull=True) | (~Q(va_vehiclenumber_mkt='') & ~Q(va_vehiclenumber_mkt__isnull=True))
    ).values_list('va_enquirynumber_id', flat=True).distinct()

    allotted_all_ids = list(set(list(allotted_trip_enq_ids) + list(allotted_va_ids)))

    # Exclude explicitly dead/cancelled/completed enquiries (status 5 = Cancelled/Dead)
    dead_enq_ids = list(enquiry_qs.filter(en_status_id__in=[5]).values_list('id', flat=True))
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

    # Allotted: has vehicle, created in current month, but no business trip running or closed yet
    allotted = enquiry_qs.filter(
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
    ).count()

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

    return render(request, 'asset_mgt_app/customer_portal_dashboard.html', {
        'customer': customer,
        'department': department,
        'active_enquiries': active_enquiries,
        'in_transit': in_transit,
        'delivered': delivered,
        'allotted': allotted,
        'recent_shipments': recent_shipments
    })

@login_required(login_url='/SMS/customer_login/2/')
def customer_enquiry_add(request):
    """
    Simplified enquiry submission form for logged-in customers.
    """
    customer, department, is_lp, agent_name = get_customer_context(request)
    
    if request.method == 'POST':
        from_loc_id = request.POST.get('from_location')
        to_loc_id = request.POST.get('to_location')
        # New structured vehicle fields
        category_id = request.POST.get('vehicle_category')
        type_id = request.POST.get('vehicle_type')
        
        cargo_details = request.POST.get('cargo_details', '') # Still capture for fallback/legacy
        
        # Combined datetime-local field
        pickup_datetime_str = request.POST.get('pickup_datetime', '')
        pickup_date = None
        req_time = None
        if pickup_datetime_str:
            try:
                # datetime-local format: "2026-02-22T10:30"
                parts = pickup_datetime_str.split('T')
                pickup_date = parts[0]
                req_time = parts[1] if len(parts) > 1 else None
            except Exception:
                pickup_date = pickup_datetime_str
        
        # Fallback: check old separate fields
        if not pickup_date:
            pickup_date = request.POST.get('pickup_date')
        if not req_time:
            req_time = request.POST.get('req_time')
        
        # New fields for LP/Agent
        agent_name = request.POST.get('agent_name')
        no_of_veh = request.POST.get('no_of_veh', 0)
        no_of_pcs = request.POST.get('no_of_pcs', 0)
        weight = request.POST.get('weight')
        dimensions = request.POST.get('dimensions')
        cbm = request.POST.get('cbm')
        
        pickup_contact_name = request.POST.get('pickup_contact_name')
        pickup_contact_mobile = request.POST.get('pickup_contact_mobile')
        delivery_contact_name = request.POST.get('delivery_contact_name')
        delivery_contact_mobile = request.POST.get('delivery_contact_mobile')
        
        if not customer:
            messages.error(request, 'Account link missing.')
            return redirect('customer_dashboard')
            
        try:
            from_loc = Places.objects.get(id=from_loc_id) if from_loc_id else None
            to_loc = Places.objects.get(id=to_loc_id) if to_loc_id else None
            
            # Get objects for structured storage and string names
            category_name = ""
            vc_obj = None
            if category_id:
                vc_obj = VehiclecategoryInfo.objects.filter(id=category_id).first()
                if vc_obj:
                    category_name = vc_obj.vc_vehiclecategory

            vt_obj = None
            if type_id:
                vt_obj = VehicletypeInfo.objects.filter(id=type_id).first()
                # ONLY use vehicle type if cargo_details is explicitly empty
                if not cargo_details and vt_obj:
                    cargo_details = vt_obj.vt_vehicletype

            # Department: use form selection, fallback to session
            dept_id = request.POST.get('customer_department')
            selected_dept = None
            if dept_id:
                selected_dept = CustomerdepartmentInfo.objects.filter(id=dept_id).first()
            if not selected_dept:
                selected_dept = department

            # Custom logic for assigning to Ajay R for EIPL
            assigned_user = MyUser.objects.filter(is_superuser=True).first() or request.user
            if customer and "EIPL" in customer.cu_name:
                ajay_user = MyUser.objects.filter(first_name__icontains='Ajay', last_name__icontains='R').first()
                if not ajay_user:
                    ajay_user = MyUser.objects.filter(first_name__icontains='Ajay').first()
                if ajay_user:
                    assigned_user = ajay_user

            from ..sub_models.tr_triptype_mod import Tr_triptype_Info
            trip_type_id = request.POST.get('trip_type')
            trip_type_obj = None
            if trip_type_id:
                trip_type_obj = Tr_triptype_Info.objects.filter(id=trip_type_id).first()
            if not trip_type_obj:
                messages.error(request, 'Please select a Trip Type.')
                places = Places.objects.all().order_by('place_name')
                categories = VehiclecategoryInfo.objects.all().order_by('vc_vehiclecategory')
                types = VehicletypeInfo.objects.all().order_by('vt_vehicletype')
                departments = CustomerdepartmentInfo.objects.all().order_by('ct_customerdepartment')
                trip_types = Tr_triptype_Info.objects.all().order_by('tr_trip_type')
                return render(request, 'asset_mgt_app/customer_enquiry_add.html', {
                    'customer': customer,
                    'department': department,
                    'departments': departments,
                    'places': places,
                    'categories': categories,
                    'types': types,
                    'trip_types': trip_types,
                    'is_lp': is_lp,
                    'default_agent_name': agent_name
                })

            enquiry = EnquirynoteInfo(
                en_customername=customer,
                en_customerdepartment=selected_dept,
                en_assignedto=assigned_user,
                en_status=StatusList.objects.filter(id=6).first(),
                en_trip_type=trip_type_obj,
                en_consignmentdetails=cargo_details,
                en_vehicledetails=category_name, # Save category here as string
                en_pickupdatetime=pickup_datetime_str if pickup_datetime_str else timezone.now(),
                en_fromlocaion=from_loc,
                en_tolocation=to_loc,
                en_created_at=timezone.now(),
                
                # New fields
                en_agent_name=agent_name,
                en_vehicle_req_time=req_time if req_time else None,
                en_no_of_vehicles=int(no_of_veh) if no_of_veh else 0,
                en_no_of_pcs=int(no_of_pcs) if no_of_pcs else 0,
                en_weight=weight,
                en_dimensions=dimensions,
                en_cbm=cbm,
                en_pickup_contact_name=pickup_contact_name,
                en_pickup_contact_mobile=pickup_contact_mobile,
                en_delivery_contact_name=delivery_contact_name,
                en_delivery_contact_mobile=delivery_contact_mobile
            )
            enquiry.save() # Save first to get ID
            
            # Generate number based on ID to match internal pattern
            # Example format: 26-27_WEB_EN_000001
            current_fy = get_financial_year()
            prefix = f"{current_fy}_WEB_EN_"
            enquiry.en_enquirynumber = generate_next_number(EnquirynoteInfo, 'en_enquirynumber', prefix, 6)
            enquiry.save(update_fields=['en_enquirynumber'])
            
            # Save structured vehicle info for internal view sync using fetched objects
            if vc_obj and vt_obj:
                try:
                    Enquirynotevehicle.objects.create(
                        env_enquirynumber=enquiry,
                        env_vehiclecategory=vc_obj,
                        env_vehicletype=vt_obj,
                        env_quantity=int(no_of_veh) if no_of_veh else 1,
                        env_updated_by=request.user
                    )
                except Exception as inner_e:
                     print(f"Failed to create vehicle detail: {inner_e}")
            
            messages.success(request, f'Booking {enquiry.en_enquirynumber} submitted successfully!')
            return redirect('customer_enquiry_list')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            
    from ..sub_models.tr_triptype_mod import Tr_triptype_Info
    places = Places.objects.all().order_by('place_name')
    categories = VehiclecategoryInfo.objects.all().order_by('vc_vehiclecategory')
    types = VehicletypeInfo.objects.all().order_by('vt_vehicletype')
    departments = CustomerdepartmentInfo.objects.all().order_by('ct_customerdepartment')
    trip_types = Tr_triptype_Info.objects.all().order_by('tr_trip_type')

    return render(request, 'asset_mgt_app/customer_enquiry_add.html', {
        'customer': customer,
        'department': department,
        'departments': departments,
        'places': places,
        'categories': categories,
        'types': types,
        'trip_types': trip_types,
        'is_lp': is_lp,
        'default_agent_name': agent_name
    })

@login_required(login_url='/SMS/customer_login/2/')
def customer_enquiry_edit(request, enquiry_id):
    """Edit an existing customer enquiry."""
    from ..sub_models.tr_triptype_mod import Tr_triptype_Info
    customer, department, is_lp, agent_name = get_customer_context(request)
    if not customer:
        return redirect('customer_dashboard')

    enquiry = get_object_or_404(EnquirynoteInfo, id=enquiry_id, en_customername=customer)

    if request.method == 'POST':
        from_loc_id = request.POST.get('from_location')
        to_loc_id = request.POST.get('to_location')
        category_id = request.POST.get('vehicle_category')
        type_id = request.POST.get('vehicle_type')
        cargo_details = request.POST.get('cargo_details', '')
        
        pickup_datetime_str = request.POST.get('pickup_datetime', '')
        req_time = None
        if pickup_datetime_str:
            try:
                parts = pickup_datetime_str.split('T')
                req_time = parts[1] if len(parts) > 1 else None
            except Exception:
                pass
        
        # Trip type update
        trip_type_id = request.POST.get('trip_type')
        if trip_type_id:
            tt_obj = Tr_triptype_Info.objects.filter(id=trip_type_id).first()
            if tt_obj:
                enquiry.en_trip_type = tt_obj
        
        dept_id = request.POST.get('customer_department')
        if dept_id:
            selected_dept = CustomerdepartmentInfo.objects.filter(id=dept_id).first()
            if selected_dept:
                enquiry.en_customerdepartment = selected_dept

        if from_loc_id:
            enquiry.en_fromlocaion = Places.objects.filter(id=from_loc_id).first()
        if to_loc_id:
            enquiry.en_tolocation = Places.objects.filter(id=to_loc_id).first()

        if pickup_datetime_str:
            enquiry.en_pickupdatetime = pickup_datetime_str
        if req_time:
            enquiry.en_vehicle_req_time = req_time

        if cargo_details:
            enquiry.en_consignmentdetails = cargo_details

        enquiry.en_agent_name = request.POST.get('agent_name', enquiry.en_agent_name)
        
        no_veh_val = request.POST.get('no_of_veh')
        if no_veh_val not in (None, ''):
            try:
                enquiry.en_no_of_vehicles = int(no_veh_val)
            except (ValueError, TypeError):
                pass

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

        # Update structured vehicle detail
        vc_obj = VehiclecategoryInfo.objects.filter(id=category_id).first() if category_id else None
        vt_obj = VehicletypeInfo.objects.filter(id=type_id).first() if type_id else None
        if vc_obj and vt_obj:
            Enquirynotevehicle.objects.update_or_create(
                env_enquirynumber=enquiry,
                defaults={
                    'env_vehiclecategory': vc_obj,
                    'env_vehicletype': vt_obj,
                    'env_quantity': enquiry.en_no_of_vehicles or 1,
                    'env_updated_by': request.user
                }
            )

        messages.success(request, f'Booking {enquiry.en_enquirynumber} updated successfully!')
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
        'default_agent_name': enquiry.en_agent_name or agent_name
    })

@login_required(login_url='/SMS/customer_login/2/')
def customer_enquiry_list(request):
    """
    List previous enquiries and current shipments for the customer.
    """
    customer, _, is_lp, agent_name = get_customer_context(request)
    if not customer:
        return redirect('customer_dashboard')

    search_query = request.GET.get('q', '')
    
    # Get enquiries with optimized queries using select_related
    enquiries_qs = EnquirynoteInfo.objects.filter(
        en_customername=customer
    ).select_related(
        'en_customername',
        'en_fromlocaion',
        'en_tolocation',
        'en_customerdepartment'
    ).prefetch_related(
        'tripdetailinfo_set',
        'vehicle_allotmentinfo_set',
        'consignmentdetailinfo_set'
    )
    
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
    _closed_trip_numbers = Trip_closure_files_Info.objects.values_list('tcf_tripnumber', flat=True)
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
    _dead_enq_ids = list(enquiries_qs.filter(en_status_id__in=[5]).values_list('id', flat=True))
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

    # Build enriched data for template
    enquiry_list = []
    for enq in page_obj:
        # When status filter is active, pick the matching trip
        if status_filter == 'transit':
            trip = enq.tripdetailinfo_set.filter(tc_financestatus_id=1, tr_category_id=1).first()
        elif status_filter == 'delivered':
            trip = enq.tripdetailinfo_set.filter(
                Q(tc_financestatus_id__in=[2, 7, 9]) | Q(tr_tripnumber__in=_closed_trip_numbers),
                tr_category_id=1
            ).first()
        elif status_filter == 'allotted':
            # Allotted: business trip exists but not in-transit or delivered
            trip = enq.tripdetailinfo_set.filter(tr_category_id=1).exclude(
                tc_financestatus_id__in=[1, 2, 3, 7, 9]
            ).exclude(
                tr_tripnumber__in=_closed_trip_numbers
            ).first()
        elif status_filter == 'active':
            trip = None  # Active enquiries have no trips yet
        else:
            trip = enq.tripdetailinfo_set.filter(tr_category_id=1).first()
        va = enq.vehicle_allotmentinfo_set.first()
        cn = enq.consignmentdetailinfo_set.first()

        # If a search query is active, try to find a trip that matches it to display relevant info
        if search_query:
            matched_trip = enq.tripdetailinfo_set.filter(
                Q(tr_vehiclenumber__icontains=search_query) | Q(tr_tripnumber__icontains=search_query)
            ).first()
            if matched_trip:
                trip = matched_trip

        # Vehicle number: trip > allotment (own) > allotment (market)
        vehicle_no = '-'
        if trip and trip.tr_vehiclenumber:
            vehicle_no = trip.tr_vehiclenumber
        elif va:
            if va.va_vehiclenumber:
                vehicle_no = str(va.va_vehiclenumber)
            elif va.va_vehiclenumber_mkt:
                vehicle_no = va.va_vehiclenumber_mkt
        
        # If the search query matched a secondary allotment not captured above, display it
        if search_query and search_query.upper() not in vehicle_no.upper():
            matched_va = enq.vehicle_allotmentinfo_set.filter(
                Q(va_vehiclenumber__vm_registrationnumber__icontains=search_query) |
                Q(va_vehiclenumber_mkt__icontains=search_query)
            ).first()
            if matched_va:
                if matched_va.va_vehiclenumber:
                    vehicle_no = str(matched_va.va_vehiclenumber)
                elif matched_va.va_vehiclenumber_mkt:
                    vehicle_no = matched_va.va_vehiclenumber_mkt

        # Customer reference
        customer_ref = enq.en_enquirynumber
        if trip and trip.tr_customerref:
            customer_ref = trip.tr_customerref

        # Consignment number: trip > direct consignment > trip number
        cnote = '-'
        if trip and trip.tr_consignmentnumber and trip.tr_consignmentnumber.co_consignmentnumber:
            cnote = trip.tr_consignmentnumber.co_consignmentnumber
        elif cn and cn.co_consignmentnumber:
            cnote = cn.co_consignmentnumber
        elif trip and trip.tr_tripnumber:
            cnote = trip.tr_tripnumber

        # Is Delivered?
        is_delivered = False
        if trip and (trip.tc_financestatus_id in [2, 3, 4, 5, 6, 7, 9, 10, 11] or (trip.tr_tripnumber and trip.tr_tripnumber in _closed_trip_numbers)):
            is_delivered = True

        # Tracking link - generate from vehicle number using Trans GPS (only if NOT delivered)
        track_link = ''
        if not is_delivered and vehicle_no and vehicle_no != '-':
            track_link = f'/SMS/SMS/customer_track_vehicle/?vehicle={vehicle_no}'
            if trip:
                track_link += f'&trip_id={trip.id}'

        # POD download - only show if file actually exists
        import os
        from django.conf import settings
        pod_trip_id = None
        if trip and is_delivered:
            # Check closure files
            closure = Trip_closure_files_Info.objects.filter(tcf_tripnumber=trip.tr_tripnumber).first()
            if closure and closure.tcf_pod:
                pod_trip_id = trip.id
            
            # Check trip attachment
            if not pod_trip_id and trip.tc_pod_attachment:
                pod_trip_id = trip.id

        # Consignment ID for PDF link
        consignment_id = None
        cus_ref_num = None
        if trip and trip.tr_consignmentnumber:
            consignment_id = trip.tr_consignmentnumber.id
            cus_ref_num = trip.tr_consignmentnumber.co_cusrefnum
        elif cn:
            consignment_id = cn.id
            cus_ref_num = cn.co_cusrefnum

        # Driver number
        driver_number = None
        if trip and trip.tr_drivernumber:
            driver_number = trip.tr_drivernumber

        # Compute status flow
        flow = compute_shipment_flow(
            enq=enq,
            trip=trip,
            va=va,
            is_delivered=is_delivered,
            pod_trip_id=pod_trip_id,
            track_link=track_link
        )

        enquiry_list.append({
            'enq': enq,
            'vehicle_no': vehicle_no,
            'customer_ref': customer_ref,
            'cnote': cnote,
            'track_link': track_link,
            'pod_trip_id': pod_trip_id,
            'consignment_id': consignment_id,
            'cus_ref_num': cus_ref_num,
            'driver_number': driver_number,
            'is_delivered': is_delivered,
            'flow': flow,
        })
    
    return render(request, 'asset_mgt_app/customer_enquiry_list.html', {
        'enquiry_list': enquiry_list,
        'search_query': search_query,
        'page_obj': page_obj,
        'status_filter': status_filter,
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
    
    from django.core.paginator import Paginator
    from django.db.models import Prefetch

    # Get trip numbers that have a POD in the closure table
    closure_trip_numbers = list(Trip_closure_files_Info.objects.exclude(
        tcf_pod__isnull=True
    ).exclude(
        tcf_pod=''
    ).values_list('tcf_tripnumber', flat=True))

    # Get all trips for this customer that have a POD
    trips_qs = TripdetailInfo.objects.filter(
        tr_enquirynumber__en_customername=customer
    ).filter(
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
def customer_dmr_report(request):
    """
    Daily Movement Report (DMR) strictly scoped to the logged-in customer.
    Supports Date Range, Month/Year, Department filters, Search, and Excel Export.
    """
    customer, department, is_lp, agent_name = get_customer_context(request)
    if not customer:
        messages.error(request, 'Your account is not linked to a Customer Profile. Please contact support.')
        return redirect('customer_dashboard')

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

    # Base trips for this customer
    trips = TripdetailInfo.objects.filter(
        BASE_DMR_Q,
        tr_enquirynumber__en_customername=customer
    ).select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
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
    headers, template_key = get_dmr_headers(
        customer.cu_name, dept_name, None, None,
        customer_id=customer.id, dept_id=int(dept_id) if dept_id and str(dept_id).isdigit() else None
    )
    data_rows = get_dmr_rows(page_obj, headers, template_key, customer.cu_name, start_idx=page_obj.start_index())

    # Available departments for filter dropdown
    available_departments = CustomerdepartmentInfo.objects.filter(
        enquirynoteinfo__en_customername=customer
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
    })


@login_required(login_url='/SMS/customer_login/2/')
def customer_dmr_export_excel(request):
    """Export DMR Excel for the logged-in customer."""
    customer, department, is_lp, agent_name = get_customer_context(request)
    if not customer:
        messages.error(request, 'Customer context not found.')
        return redirect('customer_dashboard')

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

    trips = TripdetailInfo.objects.filter(
        BASE_DMR_Q,
        tr_enquirynumber__en_customername=customer
    ).select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
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
