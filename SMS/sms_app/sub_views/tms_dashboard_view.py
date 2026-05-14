from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Sum, Q, F, Value, FloatField, Func
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
        cs_employees = User_extInfo.objects.filter(department=cs_dept).select_related('user')
    else:
        cs_employees = User_extInfo.objects.all().select_related('user')
        
    context = {
        'first_name': first_name,
        'cs_employees': cs_employees,
    }
    return render(request, "asset_mgt_app/tms_dashboard.html", context)

def get_tms_dashboard_data(request):
    employee_id = request.GET.get('employee_id')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    def apply_date_filter(qs, date_field):
        if from_date:
            qs = qs.filter(**{f"{date_field}__gte": from_date})
        if to_date:
            qs = qs.filter(**{f"{date_field}__lte": to_date})
        return qs
    
    def calculate_metrics(user_id=None):
        en_qs = apply_date_filter(EnquirynoteInfo.objects.all(), 'en_created_at')
        cn_qs = apply_date_filter(ConsignmentdetailInfo.objects.all(), 'co_consignmentdate')
        tr_qs = apply_date_filter(TripdetailInfo.objects.all(), 'tr_departeddate')
        ti_qs = apply_date_filter(TransInvoiceInfo.objects.all(), 'ti_inv_date')

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
    
    # Chart Data: Business Trip Distribution
    business_qs = apply_date_filter(TripdetailInfo.objects.filter(tr_category__category__icontains="Business"), 'tr_departeddate')
    if employee_id and employee_id != 'all':
        business_qs = business_qs.filter(tr_enquirynumber__en_assignedto_id=employee_id)

    if not business_qs.exists():
        business_qs = apply_date_filter(TripdetailInfo.objects.all(), 'tr_departeddate')
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
    
    # Donut Charts (Mileage Breakdown)
    def get_km_details(ownership_type):
        db_source = ownership_type
        if ownership_type == 'Own': db_source = 'OWN'
        
        qs = apply_date_filter(TripdetailInfo.objects.filter(tr_vehiclesource__ow_ownership__icontains=db_source), 'tr_departeddate')
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

    return JsonResponse({
        'totals': totals,
        'employee': employee_metrics,
        'bar_chart': bar_chart_data,
        'donut_own': get_km_details('Own'),
        'donut_attached': get_km_details('Attached')
    })
