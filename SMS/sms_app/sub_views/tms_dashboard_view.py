from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Sum, Q, F, Value, FloatField, Func
from django.utils import timezone
from datetime import datetime
from ..sub_models.tripdetail_mod import TripdetailInfo, Trip_closure_files_Info, Trip_category_info
from ..sub_models.enquirynote_mod import EnquirynoteInfo
from ..sub_models.user_ext_mod import User_extInfo
from ..sub_models.department_info_mod import Department_info
from ..sub_models.ownership_mod import OwnershipInfo
from ..sub_models.tr_triptype_mod import Tr_triptype_Info
from ..sub_models.vehiclemaster_mod import VehiclemasterInfo
from ..sub_models.my_user_mod import MyUser
from ..sub_models.vehicle_allotment_mod import Vehicle_allotmentInfo
from ..sub_models.consignmentdetail_mod import ConsignmentdetailInfo
from ..sub_models.trans_invoice_mod import TransInvoiceInfo
from ..sub_models.tr_businesstype_mod import Tr_businesstype_Info
from ..sub_models.location_info_mod import Location_info
import json

# Customer Service department ID
CS_DEPARTMENT_ID = 4

class Abs(Func):
    function = 'ABS'

def tms_dashboard(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    # Get current user's role and details
    current_user_ext = None
    user_role_id = None
    current_user_id = None
    dropdown_disabled = False
    default_employee_id = 'all'

    if user_id:
        try:
            current_user_ext = User_extInfo.objects.get(user_id=user_id)
            user_role_id = current_user_ext.emp_role_id if current_user_ext.emp_role else None
            current_user_id = user_id
        except User_extInfo.DoesNotExist:
            pass

    # Determine dropdown behavior based on role
    # Role IDs: 1=Admin, 3=Super User, 2=General User
    # Department ID 4 = "Customer Service"
    is_cs_user = (current_user_ext and
                  current_user_ext.department_id == CS_DEPARTMENT_ID)

    if user_role_id in [1, 3]:  # Admin & Super User
        dropdown_disabled = False
        default_employee_id = 'all'
    elif is_cs_user:  # Customer Service Department
        dropdown_disabled = True
        default_employee_id = str(current_user_id)
    else:  # General User or Other roles
        dropdown_disabled = True
        default_employee_id = 'all'

    # Get employees to display in dropdown
    # Always show employees from the Customer Service department (ID=4)
    cs_employees = User_extInfo.objects.filter(
        department_id=CS_DEPARTMENT_ID,
        user__is_active=True
    ).select_related('user')

    # Get own and attached vehicle numbers
    own_vehicles = VehiclemasterInfo.objects.filter(
        vm_ownership__ow_ownership__icontains='OWN'
    ).values_list('vm_registrationnumber', flat=True).order_by('vm_registrationnumber')

    attached_vehicles = VehiclemasterInfo.objects.filter(
        vm_ownership__ow_ownership__icontains='Attached'
    ).values_list('vm_registrationnumber', flat=True).order_by('vm_registrationnumber')

    # Get all branches (Location_info) that have at least one CS employee
    branches = Location_info.objects.filter(
        user_extinfo__department_id=CS_DEPARTMENT_ID,
        user_extinfo__user__is_active=True
    ).distinct().order_by('loc_name')

    context = {
        'first_name': first_name,
        'cs_employees': cs_employees,
        'dropdown_disabled': dropdown_disabled,
        'default_employee_id': default_employee_id,
        'user_role_id': user_role_id,
        'current_user_id': current_user_id,
        'own_vehicles': own_vehicles,
        'attached_vehicles': attached_vehicles,
        'branches': branches,
    }
    return render(request, "asset_mgt_app/tms_dashboard.html", context)

def get_tms_dashboard_data(request):
    # Get current user's role and department to enforce data filtering
    user_id = request.session.get('ses_userID')
    user_role_id = None
    current_user_ext = None
    enforce_user_filter = False

    if user_id:
        try:
            current_user_ext = User_extInfo.objects.get(user_id=user_id)
            user_role_id = current_user_ext.emp_role_id if current_user_ext.emp_role else None
        except User_extInfo.DoesNotExist:
            pass

    # Check if the user belongs to the "Customer Service" department (ID=4)
    is_cs_user = (current_user_ext and
                  current_user_ext.department_id == CS_DEPARTMENT_ID)

    # Determine filtering enforcement based on role and department
    # Role IDs: 1=Admin, 3=Super User (can view all)
    # Users from "Customer Service" department (ID=4): forced to see only their own data
    # Other users: can only see 'all' (aggregate) data
    employee_id = request.GET.get('employee_id')

    if user_role_id in [1, 3]:  # Admin & Super User - can view all
        pass  # employee_id stays as selected by user
    elif is_cs_user:  # Customer Service department - force to their own data
        enforce_user_filter = True
        employee_id = str(user_id)
    else:  # Other roles/departments - only allow 'all' selection
        if employee_id and employee_id != 'all':
            employee_id = 'all'

    # If employee_id is 'all' but user is enforced, override to their ID
    if enforce_user_filter and (employee_id == 'all' or not employee_id):
        employee_id = str(user_id)

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    branch_id = request.GET.get('branch_id')

    # Get the enquiries filtered by the date range
    enquiries_base_qs = EnquirynoteInfo.objects.all()
    if from_date:
        enquiries_base_qs = enquiries_base_qs.filter(en_created_at__date__gte=from_date)
    if to_date:
        enquiries_base_qs = enquiries_base_qs.filter(en_created_at__date__lte=to_date)

    # Apply branch filter — restrict to enquiries assigned to CS users in that branch
    if branch_id and branch_id != 'all':
        branch_user_ids = User_extInfo.objects.filter(
            emp_branch_id=branch_id,
            department_id=CS_DEPARTMENT_ID,
            user__is_active=True
        ).values_list('user_id', flat=True)
        enquiries_base_qs = enquiries_base_qs.filter(en_assignedto_id__in=branch_user_ids)

    def calculate_metrics(user_id=None):
        en_qs = enquiries_base_qs
        if user_id and user_id != 'all':
            en_qs = en_qs.filter(en_assignedto_id=user_id)

        # Base querysets
        cn_qs = ConsignmentdetailInfo.objects.filter(co_enquirynumber__in=en_qs)
        tr_qs = TripdetailInfo.objects.filter(tr_enquirynumber__in=en_qs)
        ti_qs = TransInvoiceInfo.objects.filter(ti_trip__tr_enquirynumber__in=en_qs)

        # --- Vehicle Requested: sum of env_quantity in Enquirynotevehicle for these enquiries ---
        from ..sub_models.enquirynote_vehicle_mod import Enquirynotevehicle
        total_enquiries = Enquirynotevehicle.objects.filter(env_enquirynumber__in=en_qs).aggregate(total=Sum('env_quantity'))['total'] or 0

        # --- C-Notes: count of individual C-Note records (representing billed trips) ---
        en_ids_with_cnote = set(
            cn_qs.exclude(co_enquirynumber__isnull=True)
                 .values_list('co_enquirynumber_id', flat=True)
                 .distinct()
        )
        cnotes_count = cn_qs.exclude(co_enquirynumber__isnull=True).count()

        # --- Enquiry IDs that do NOT yet have a C-Note ---
        en_ids_without_cnote = list(
            en_qs.exclude(id__in=en_ids_with_cnote)
                 .values_list('id', flat=True)
        )

        # --- Enquiries Cancelled: enquiries directly cancelled OR with a cancelled trip,
        #     but excluding enquiries already counted in C-Notes ---
        en_ids_cancelled_trips = set(
            TripdetailInfo.objects.filter(
                tr_enquirynumber_id__in=en_qs,
                tc_financestatus_id=3
            ).values_list('tr_enquirynumber_id', flat=True).distinct()
        )
        en_ids_cancelled_direct = set(
            en_qs.filter(en_status_id=8).values_list('id', flat=True)
        )
        # Enquiries Cancelled = (trip-cancelled + direct-cancelled) minus those already with C-Notes
        en_ids_enquiries_cancelled = en_ids_cancelled_trips.union(en_ids_cancelled_direct) - en_ids_with_cnote
        enquiries_cancelled_count = Enquirynotevehicle.objects.filter(
            env_enquirynumber_id__in=en_ids_enquiries_cancelled
        ).aggregate(total=Sum('env_quantity'))['total'] or 0

        # --- Trips Cancelled: actual count of TripdetailInfo records with cancelled finance status,
        #     ONLY for enquiries that HAVE a C-Note. PLUS any cancelled C-Notes.
        base_trips_cancelled = TripdetailInfo.objects.filter(
            tr_enquirynumber_id__in=en_ids_with_cnote,
            tc_financestatus_id=3
        ).count()
        
        cancelled_cnotes_count = cn_qs.filter(co_status_id=8).count()
        
        overlap = TripdetailInfo.objects.filter(
            tr_enquirynumber_id__in=en_ids_with_cnote,
            tc_financestatus_id=3,
            tr_consignmentnumber__co_status_id=8
        ).count()
        
        trips_cancelled_count = base_trips_cancelled + cancelled_cnotes_count - overlap

        # --- Missed (Vehicles Missed): unallotted vehicle quantity for non-cancelled, non-cnote enquiries ---
        from django.db.models import Count
        req_totals = {
            r['env_enquirynumber_id']: r['tot'] or 0
            for r in Enquirynotevehicle.objects.filter(env_enquirynumber__in=en_qs)
            .values('env_enquirynumber_id')
            .annotate(tot=Sum('env_quantity'))
        }
        allot_totals = {
            a['va_enquirynumber_id']: a['tot'] or 0
            for a in Vehicle_allotmentInfo.objects.filter(va_enquirynumber__in=en_qs)
            .values('va_enquirynumber_id')
            .annotate(tot=Count('id'))
        }

        missed_count = 0
        for enq in en_qs:
            if enq.id in en_ids_enquiries_cancelled:
                continue  # skip ONLY cancelled enquiries

            req_qty = req_totals.get(enq.id, 0)
            allot_qty = allot_totals.get(enq.id, 0)
            if req_qty > allot_qty:
                missed_count += (req_qty - allot_qty)

        metrics = {
            'enquiries': total_enquiries,
            'cnotes': cnotes_count,
            'missed': missed_count,
            'enquiries_cancelled': enquiries_cancelled_count,
            'trips_cancelled': trips_cancelled_count,
            'settled': tr_qs.filter(tc_financestatus_id=7).count(),
            'ready': tr_qs.filter(tc_financestatus_id=9).exclude(transinvoiceinfo__isnull=False).count(),
            'invoiced': ti_qs.count(),
        }
        return metrics

    totals = calculate_metrics('all')
    employee_metrics = calculate_metrics(employee_id)
    
    # Chart Data: Business Trip Distribution — filtered by the same active enquiries
    active_en_qs = enquiries_base_qs
    if employee_id and employee_id != 'all':
        active_en_qs = active_en_qs.filter(en_assignedto_id=employee_id)

    business_qs = TripdetailInfo.objects.filter(
        tr_category__category__iexact="Business",
        tr_enquirynumber__in=active_en_qs
    )

    if not business_qs.exists():
        business_qs = TripdetailInfo.objects.filter(tr_enquirynumber__in=active_en_qs)

    trip_types = Tr_triptype_Info.objects.all()
    local_type = trip_types.filter(tr_trip_type__icontains="Local").first()
    outstation_type = trip_types.filter(tr_trip_type__icontains="Outstation").first()
    
    def get_trip_count(source_name, trip_type_obj):
        qs = business_qs
        if source_name != 'Total':
            db_source = source_name
            if source_name == 'Own': db_source = 'OWN'
            qs = qs.filter(tr_vehiclesource__ow_ownership__icontains=db_source)
        if trip_type_obj:
            qs = qs.filter(tr_enquirynumber__en_trip_type=trip_type_obj)
            
        from ..sub_models.enquirynote_vehicle_mod import Enquirynotevehicle
        enq_ids = qs.values_list('tr_enquirynumber_id', flat=True).distinct()
        total_qty = Enquirynotevehicle.objects.filter(
            env_enquirynumber_id__in=enq_ids
        ).aggregate(total=Sum('env_quantity'))['total'] or 0
        return total_qty

    sources = ['Own', 'Market', 'Attached']
    bar_chart_data = {
        'labels': ['Own', 'Market', 'Attached', 'Total'],
        'local': [get_trip_count(s, local_type) for s in sources] + [get_trip_count('Total', local_type)],
        'outstation': [get_trip_count(s, outstation_type) for s in sources] + [get_trip_count('Total', outstation_type)]
    }

    # C-Note Count done by CS representatives
    cs_users = User_extInfo.objects.filter(
        department_id=CS_DEPARTMENT_ID,
        user__is_active=True
    ).select_related('user')
    cs_labels = []
    cs_cnotes_counts = []
    for emp in cs_users:
        emp_en_qs = enquiries_base_qs.filter(en_assignedto_id=emp.user.id)
        emp_cnotes_count = ConsignmentdetailInfo.objects.filter(co_enquirynumber__in=emp_en_qs).count()
        cs_labels.append(emp.user.first_name)
        cs_cnotes_counts.append(emp_cnotes_count)
    
    cs_cnote_chart = {
        'labels': cs_labels,
        'counts': cs_cnotes_counts
    }
    
    # Donut Charts (Mileage Breakdown) — filtered by the same active enquiries
    own_vehicle_num = request.GET.get('own_vehicle_number')
    attached_vehicle_num = request.GET.get('attached_vehicle_number')

    def get_km_details(ownership_type):
        db_source = ownership_type
        if ownership_type == 'Own': db_source = 'OWN'

        qs = TripdetailInfo.objects.filter(
            tr_vehiclesource__ow_ownership__icontains=db_source,
            tr_enquirynumber__in=active_en_qs
        )

        if ownership_type == 'Own' and own_vehicle_num and own_vehicle_num != 'all':
            qs = qs.filter(tr_vehiclenumber__iexact=own_vehicle_num)
        elif ownership_type == 'Attached' and attached_vehicle_num and attached_vehicle_num != 'all':
            qs = qs.filter(tr_vehiclenumber__iexact=attached_vehicle_num)
            
        def sum_km(filter_q):
            # Use Abs to prevent negative values from data entry errors
            res = qs.filter(filter_q).aggregate(val=Sum(Abs(F('tr_reportedkm') - F('tr_departedkm')), output_field=FloatField()))
            return res['val'] or 0

        business = sum_km(Q(tr_category__category__iexact="Business"))
        empty = sum_km(Q(tr_category__category__iexact="Empty"))
        # Using icontains for Business Empty to handle potential leading spaces or variations
        business_empty = sum_km(Q(tr_category__category__icontains="Business") & Q(tr_category__category__icontains="Empty"))
        
        # Fallback if categories aren't populated yet
        if business == 0 and empty == 0 and business_empty == 0:
            total = sum_km(Q())
            business = total
            
        return [business, empty, business_empty]

    progress_month_str = request.GET.get('progress_month')

    local_now = timezone.localtime(timezone.now())
    current_year = local_now.year
    current_month = local_now.month
    
    if progress_month_str:
        try:
            dt = datetime.strptime(progress_month_str, '%Y-%m')
            current_year = dt.year
            current_month = dt.month
        except ValueError:
            pass

    own_attached_ids = list(
        OwnershipInfo.objects.filter(
            Q(ow_ownership__icontains='OWN') |
            Q(ow_ownership__icontains='Attached')
        ).values_list('id', flat=True)
    )

    progress_qs = TripdetailInfo.objects.filter(
        tr_category__category__icontains="Business",
        tr_enquirynumber__en_created_at__year=current_year,
        tr_enquirynumber__en_created_at__month=current_month,
        tr_vehiclesource_id__in=own_attached_ids,
    )
    if employee_id and employee_id != 'all':
        progress_qs = progress_qs.filter(tr_enquirynumber__en_assignedto_id=employee_id)

    trips_by_vehicle = progress_qs.values(
        'tr_vehicletype__vt_vehicletype',
        'tr_vehiclenumber'
    ).annotate(
        trip_count=Count('id')
    )

    # Initialize buckets/ranges for trip counts
    buckets = ["30-42", "20-30", "10-20", "0-10"]
    progress_breakdowns = {b: [] for b in buckets}

    for item in trips_by_vehicle:
        vt_name = str(item['tr_vehicletype__vt_vehicletype'] or 'Unknown').strip()
        veh_num = str(item['tr_vehiclenumber'] or 'N/A').strip()
        count = item['trip_count']
        
        # Categorize vehicle based on trip count
        if count >= 30:
            b_key = "30-42"
        elif count >= 20:
            b_key = "20-30"
        elif count >= 10:
            b_key = "10-20"
        else:
            b_key = "0-10"
            
        progress_breakdowns[b_key].append({
            'vehicle_number': veh_num,
            'trip_count': count,
            'vehicle_type': vt_name
        })

    # Sort each bucket's vehicles by trip count descending
    for b_key in progress_breakdowns:
        progress_breakdowns[b_key] = sorted(
            progress_breakdowns[b_key],
            key=lambda x: x['trip_count'],
            reverse=True
        )

    # Build chart data format
    progress_labels = buckets
    progress_counts = [len(progress_breakdowns[b]) for b in buckets]

    month_name = datetime(current_year, current_month, 1).strftime('%B %Y')

    return JsonResponse({
        'totals': totals,
        'employee': employee_metrics,
        'bar_chart': bar_chart_data,
        'cs_cnote_chart': cs_cnote_chart,
        'donut_own': get_km_details('Own'),
        'donut_attached': get_km_details('Attached'),
        'progress_chart': {
            'labels': progress_labels,
            'counts': progress_counts,
            'breakdowns': progress_breakdowns,
            'month_name': month_name
        }
    })
