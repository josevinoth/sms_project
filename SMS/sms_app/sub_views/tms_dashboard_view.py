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
import json

class Abs(Func):
    function = 'ABS'

def tms_dashboard(request):
    first_name = request.session.get('first_name')
    cs_dept = Department_info.objects.filter(Q(dept_name__icontains="CS") | Q(dept_name__icontains="Customer Service")).first()
    cs_employees = []
    if cs_dept:
        cs_employees = User_extInfo.objects.filter(department=cs_dept, user__is_active=True).select_related('user')
    else:
        cs_employees = User_extInfo.objects.filter(user__is_active=True).select_related('user')
        
    context = {
        'first_name': first_name,
        'cs_employees': cs_employees,
    }
    return render(request, "asset_mgt_app/tms_dashboard.html", context)

def get_tms_dashboard_data(request):
    employee_id = request.GET.get('employee_id')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    def apply_enquiry_date_filter(qs, field_prefix=''):
        """Filter by enquiry created date (en_created_at is a DateTimeField, use __date__ lookup)."""
        date_field = f"{field_prefix}en_created_at" if not field_prefix else f"{field_prefix}en_created_at"
        if from_date:
            qs = qs.filter(**{f"{date_field}__date__gte": from_date})
        if to_date:
            qs = qs.filter(**{f"{date_field}__date__lte": to_date})
        return qs

    def calculate_metrics(user_id=None):
        # All querysets filtered by Enquiry Created Date
        en_qs = apply_enquiry_date_filter(EnquirynoteInfo.objects.all(), '')
        cn_qs = apply_enquiry_date_filter(ConsignmentdetailInfo.objects.all(), 'co_enquirynumber__')
        tr_qs = apply_enquiry_date_filter(TripdetailInfo.objects.all(), 'tr_enquirynumber__')
        ti_qs = apply_enquiry_date_filter(TransInvoiceInfo.objects.all(), 'ti_trip__tr_enquirynumber__')

        if user_id and user_id != 'all':
            en_qs = en_qs.filter(en_assignedto_id=user_id)
            cn_qs = cn_qs.filter(co_enquirynumber__en_assignedto_id=user_id)
            tr_qs = tr_qs.filter(tr_enquirynumber__en_assignedto_id=user_id)
            ti_qs = ti_qs.filter(ti_trip__tr_enquirynumber__en_assignedto_id=user_id)

        vehicles_count = tr_qs.count()
        cnotes_count = cn_qs.count()

        metrics = {
            'enquiries': vehicles_count,
            'cnotes': cnotes_count,
            'missed': max(0, vehicles_count - cnotes_count),
            'settled': tr_qs.filter(tc_financestatus__status__icontains="Settle").count(),
            'ready': tr_qs.filter(tc_financestatus__status__icontains="Settle").exclude(transinvoiceinfo__isnull=False).count(),
            'invoiced': ti_qs.count(),
        }
        return metrics

    totals = calculate_metrics('all')
    employee_metrics = calculate_metrics(employee_id)
    
    # Chart Data: Business Trip Distribution — filtered by Enquiry Created Date
    business_qs = apply_enquiry_date_filter(
        TripdetailInfo.objects.filter(tr_category__category__icontains="Business"),
        'tr_enquirynumber__'
    )
    if employee_id and employee_id != 'all':
        business_qs = business_qs.filter(tr_enquirynumber__en_assignedto_id=employee_id)

    if not business_qs.exists():
        business_qs = apply_enquiry_date_filter(TripdetailInfo.objects.all(), 'tr_enquirynumber__')
        if employee_id and employee_id != 'all':
            business_qs = business_qs.filter(tr_enquirynumber__en_assignedto_id=employee_id)

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
        return qs.count()

    sources = ['Own', 'Market', 'Attached']
    bar_chart_data = {
        'labels': ['Own', 'Market', 'Attached', 'Total'],
        'local': [get_trip_count(s, local_type) for s in sources] + [get_trip_count('Total', local_type)],
        'outstation': [get_trip_count(s, outstation_type) for s in sources] + [get_trip_count('Total', outstation_type)]
    }
    
    # Donut Charts (Mileage Breakdown) — filtered by Enquiry Created Date
    def get_km_details(ownership_type):
        db_source = ownership_type
        if ownership_type == 'Own': db_source = 'OWN'

        qs = apply_enquiry_date_filter(
            TripdetailInfo.objects.filter(tr_vehiclesource__ow_ownership__icontains=db_source),
            'tr_enquirynumber__'
        )
        if employee_id and employee_id != 'all':
            qs = qs.filter(tr_enquirynumber__en_assignedto_id=employee_id)
            
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
        'donut_own': get_km_details('Own'),
        'donut_attached': get_km_details('Attached'),
        'progress_chart': {
            'labels': progress_labels,
            'counts': progress_counts,
            'breakdowns': progress_breakdowns,
            'month_name': month_name
        }
    })
