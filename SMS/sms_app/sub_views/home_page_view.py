from django.contrib.auth.decorators import login_required
from django.contrib.messages.context_processors import messages
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.utils import timezone
from django.db.models.functions import Coalesce, TruncMonth
from ..models import Customerattach,PkcostingInfo,RequirementsInfo,Pregateintruckinfo,PkstockpurchasesInfo,Loadingbay_Info,TrbusinesstypeInfo,User_extInfo,Warehouse_goods_info,AssetInfo,Vendor_info,Location_info,Product_info,User,Service_Info,TripdetailInfo,TripHighvalueInfo,UnitInfo,BayInfo
from django.shortcuts import render, redirect
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
from collections import defaultdict
import json
from .general_utils import is_tms_manager

from ..sub_models.DG_cargo_checklist_mod import DGcargovalueInfo
from ..sub_models.maintenance_mod import MaintenanceInfo
from ..sub_models.pk_needassessment_mod import PkneedassessmentInfo
from ..sub_models.wh_highvaluecheck_info_mod import HighvalueInfo
from ..sub_models.vehicle_allotment_mod import Vehicle_allotmentInfo


@login_required(login_url='login_page')
def home_page(request):
    first_name=request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    user_ext = User_extInfo.objects.get(user=user_id)
    role=User_extInfo.objects.get(user=user_id).emp_role
    department=User_extInfo.objects.get(user=user_id).department
    bussiness_solution=User_extInfo.objects.get(user=user_id).emp_organisation
    ses_username = request.session.get('ses_username', request.POST.get('username'))
    case_to_case=str(TrbusinesstypeInfo.objects.get(id=1))
    exlcusive=str(TrbusinesstypeInfo.objects.get(id=2))
    dedicated=str(TrbusinesstypeInfo.objects.get(id=3))
    house_hold=str(TrbusinesstypeInfo.objects.get(id=4))
    case_to_case_list=list(Warehouse_goods_info.objects.filter(wh_voucher_num=None,wh_check_in_out=2,wh_customer_type=1).values_list('wh_job_no',flat=True).distinct())
    dedicated_list=list(Warehouse_goods_info.objects.filter(wh_voucher_num=None,wh_check_in_out=2,wh_customer_type=3).values_list('wh_job_no',flat=True).distinct())
    exclusive_list=list(Warehouse_goods_info.objects.filter(wh_voucher_num=None,wh_check_in_out=1,wh_customer_type=2).values_list('wh_job_no',flat=True).distinct())
    wh_check_in_jobs_1 = (Warehouse_goods_info.objects.filter(wh_check_in_out=1).values('wh_job_no')).distinct()
    wh_check_in_jobs_2 = (Loadingbay_Info.objects.filter(lb_validity_date__lte=(timezone.now())+timedelta(days=1),lb_job_no__in=wh_check_in_jobs_1)).distinct()
    wh_job_count=len(wh_check_in_jobs_2)
    open_requirements=len(RequirementsInfo.objects.filter(Q(req_status=2) | Q(req_status=6)))
    count_return=len(PkcostingInfo.objects.filter(ct_excess_status=1))
    excess_count=len(PkcostingInfo.objects.filter(ct_excess_status=3))
    count_retrival=len(PkcostingInfo.objects.filter(ct_cost_type=8,ct_stock_status__in=[1, 3]))
    count_acceptance=len(PkcostingInfo.objects.filter(ct_cost_type=8,ct_stock_status=2))
    customer_rate_due_count = len(Customerattach.objects.filter(ca_contract_due_days__lte=30,ca_category_id=4,ca_status=1))
    DG_cargo_count = len(DGcargovalueInfo.objects.filter(DG_wh_approval_status__id=2))
    total_dues = customer_rate_due_count
    approval_count = TripdetailInfo.objects.filter(
        Q(tr_category=1),
        Q(tr_departeddate__isnull=False),
        Q(tc_financestatus_id=8) | Q(tr_approval__ta_approval_status__id=3)
    ).exclude(
        tr_approval__ta_approval_status__id=1
    ).count()
    approval_count_wms1 = HighvalueInfo.objects.filter( ( Q(hc_commodity__id__gte=11, hc_commodity__id__lte=14) |
        Q(hc_value__gt=2500000) ) & Q(hc_approval_status__id=2)
    ).count()
    approval_count_wms2 = HighvalueInfo.objects.filter( ( Q(hc_commodity__id__gte=11, hc_commodity__id__lte=14) |
        Q(hc_value__gt=2500000) ) & Q(hc_approval_status__id=3)
    ).count()
    checklist_count = TripHighvalueInfo.objects.filter(thc_approval_status=2).count()
    manager_listcount =MaintenanceInfo.objects.filter(mi_approval_status_id=1).count()
    finance_listcount =MaintenanceInfo.objects.filter(mi_approval_status_id=2).count()
    need_assessment_count= PkneedassessmentInfo.objects.filter(na_status_id=5).count()
    sell_rate_approval_count = Vehicle_allotmentInfo.objects.filter(va_status_id=6).count()

    # Last 6 months labels used across monthly warehouse charts.
    now = timezone.now()
    month_starts = []
    for index in range(5, -1, -1):
        month = now.month - index
        year = now.year
        while month <= 0:
            month += 12
            year -= 1
        month_starts.append(datetime(year, month, 1, tzinfo=now.tzinfo))

    month_labels = [month.strftime('%b %Y') for month in month_starts]
    month_keys = [month.strftime('%Y-%m') for month in month_starts]
    filter_start_date = month_starts[0]

    selected_branch_id = request.GET.get('branch_id', '').strip()
    selected_unit_id = request.GET.get('unit_id', '').strip()
    selected_bay_id = request.GET.get('bay_id', '').strip()

    branch_filter_list = Location_info.objects.filter(loc_status=1).order_by('loc_name')
    unit_filter_list = UnitInfo.objects.all().order_by('unit_name')
    bay_filter_list = BayInfo.objects.all().order_by('bay_bayname')

    if selected_branch_id:
        unit_filter_list = unit_filter_list.filter(ui_branch_name_id=selected_branch_id)

    if selected_unit_id and not unit_filter_list.filter(id=selected_unit_id).exists():
        selected_unit_id = ''
        selected_bay_id = ''

    if selected_unit_id:
        bay_filter_list = bay_filter_list.filter(Bay_unit_name_id=selected_unit_id)
    elif selected_branch_id:
        bay_filter_list = bay_filter_list.filter(bay_branch_name_id=selected_branch_id)

    if selected_bay_id and not bay_filter_list.filter(id=selected_bay_id).exists():
        selected_bay_id = ''

    usage_filters = {
        'wh_checkin_time__isnull': False,
        'wh_checkin_time__gte': filter_start_date,
    }
    if selected_branch_id:
        usage_filters['wh_branch_id'] = selected_branch_id
    if selected_unit_id:
        usage_filters['wh_unit_id'] = selected_unit_id
    if selected_bay_id:
        usage_filters['wh_bay_id'] = selected_bay_id

    usage_qs = (
        Warehouse_goods_info.objects
        .filter(**usage_filters)
        .annotate(month=TruncMonth('wh_checkin_time'))
        .values('month')
        .annotate(
            total_area=Coalesce(Sum('wh_goods_area'), 0.0),
            total_volume=Coalesce(Sum('wh_goods_volume_weight'), 0.0),
        )
        .order_by('month')
    )
    usage_area_map = {
        item['month'].strftime('%Y-%m'): float(item['total_area'] or 0.0)
        for item in usage_qs if item.get('month')
    }
    usage_volume_map = {
        item['month'].strftime('%Y-%m'): float(item['total_volume'] or 0.0)
        for item in usage_qs if item.get('month')
    }
    monthly_warehouse_area = [round(usage_area_map.get(key, 0.0), 2) for key in month_keys]
    monthly_warehouse_volume = [round(usage_volume_map.get(key, 0.0), 2) for key in month_keys]

    department_qs = (
        User_extInfo.objects
        .values('department__dept_name')
        .annotate(total=Count('id'))
        .order_by('-total')
    )
    team_department_labels = []
    team_department_values = []
    for item in department_qs:
        team_department_labels.append(item.get('department__dept_name') or 'Unassigned')
        team_department_values.append(item.get('total') or 0)

    if not team_department_labels:
        team_department_labels = ['No Data']
        team_department_values = [0]

    region_totals_qs = (
        Warehouse_goods_info.objects
        .filter(wh_checkin_time__isnull=False, wh_checkin_time__gte=filter_start_date)
        .values('wh_branch__loc_city__city_name')
        .annotate(total=Coalesce(Sum('wh_goods_volume_weight'), 0.0))
        .order_by('-total')
    )

    top_regions = []
    for item in region_totals_qs:
        region_name = item.get('wh_branch__loc_city__city_name') or 'Unknown Region'
        if region_name not in top_regions:
            top_regions.append(region_name)
        if len(top_regions) == 4:
            break

    region_month_map = defaultdict(dict)
    if top_regions:
        region_month_qs = (
            Warehouse_goods_info.objects
            .filter(
                wh_checkin_time__isnull=False,
                wh_checkin_time__gte=filter_start_date,
                wh_branch__loc_city__city_name__in=top_regions,
            )
            .annotate(month=TruncMonth('wh_checkin_time'))
            .values('month', 'wh_branch__loc_city__city_name')
            .annotate(total=Coalesce(Sum('wh_goods_volume_weight'), 0.0))
            .order_by('month')
        )

        for item in region_month_qs:
            region_name = item.get('wh_branch__loc_city__city_name') or 'Unknown Region'
            month_obj = item.get('month')
            if not month_obj:
                continue
            region_month_map[region_name][month_obj.strftime('%Y-%m')] = float(item.get('total') or 0.0)

    region_month_datasets = []
    for region in top_regions:
        region_month_datasets.append({
            'label': region,
            'data': [round(region_month_map.get(region, {}).get(key, 0.0), 2) for key in month_keys],
        })

    if not region_month_datasets:
        region_month_datasets = [{'label': 'No Region', 'data': [0 for _ in month_keys]}]
    context = {'count_asset': AssetInfo.objects.all().count(),
               'count_vendors': Vendor_info.objects.filter(vend_status=1).count(),
               'count_ass_asset': AssetInfo.objects.filter(asset_assignedto__isnull=False).count(),
               'count_unass_asset': AssetInfo.objects.filter(asset_assignedto__isnull=True).count(),
               'count_location': Location_info.objects.filter(loc_status=1).count(),
               'count_product': Product_info.objects.all().count(),
               'count_employee': User.objects.all().count(),
               'sum_ass_cost': AssetInfo.objects.aggregate(sum=Sum('asset_cost'))['sum'] or 0.00,
               'sum_service_cost':Service_Info.objects.aggregate(sum=Sum('ser_cost'))['sum'] or 0.00,
               'ses_username': ses_username,
               'first_name': first_name,
               'case_to_case_list': len(case_to_case_list),
               'dedicated_list': len(dedicated_list),
               'exclusive_list': len(exclusive_list),
               'role': role,
               'user_id': user_id,
               'department': department,
               'bussiness_solution': bussiness_solution,
               'bussiness_solution_id': user_ext.emp_organisation.id,
               'wh_job_count': wh_job_count,
               'wh_check_in_jobs_2': wh_check_in_jobs_2,
               'open_requirements': open_requirements,
               'count_return': count_return,
               'excess_count': excess_count,
               'manager_listcount': manager_listcount,
               'finance_listcount': finance_listcount,
               'sell_rate_approval_count': sell_rate_approval_count,
               'count_retrival': count_retrival,
               'count_acceptance': count_acceptance,
               'customer_rate_due_count': customer_rate_due_count,
               'total_dues': total_dues,
               'approval_count':approval_count,
               'checklist_count':checklist_count,
               'approval_count_wms1':approval_count_wms1,
               'approval_count_wms2':approval_count_wms2,
               'DG_cargo_count':DG_cargo_count,
               'need_assessment_count': need_assessment_count,
               'warehouse_month_labels_json': json.dumps(month_labels),
               'monthly_warehouse_area_json': json.dumps(monthly_warehouse_area),
               'monthly_warehouse_volume_json': json.dumps(monthly_warehouse_volume),
               'team_department_labels_json': json.dumps(team_department_labels),
               'team_department_values_json': json.dumps(team_department_values),
               'region_month_labels_json': json.dumps(month_labels),
               'region_month_datasets_json': json.dumps(region_month_datasets),
               'branch_filter_list': branch_filter_list,
               'unit_filter_list': unit_filter_list,
               'bay_filter_list': bay_filter_list,
               'selected_branch_id': selected_branch_id,
               'selected_unit_id': selected_unit_id,
               'selected_bay_id': selected_bay_id,
               # TMS-only flag: hides all non-TMS sidebar sections for BVM Trans Managers
               'is_tms_only': is_tms_manager(user_id),
               }
    return render(request, 'asset_mgt_app/home_page.html', context)

@login_required(login_url='login_page')
def wh_e_way_bill_list(request):
    wh_check_in_jobs_1 = (Warehouse_goods_info.objects.filter(wh_check_in_out=1).values('wh_job_no')).distinct()
    wh_check_in_jobs_2 = (Loadingbay_Info.objects.filter(lb_validity_date__lte=(timezone.now())+timedelta(days=1),lb_job_no__in=wh_check_in_jobs_1)).distinct()
    first_name = request.session.get('first_name')
    context = {
                'wh_check_in_jobs_2' : wh_check_in_jobs_2,
                'first_name': first_name
            }
    return render(request,"asset_mgt_app/wh_e_way_bill_list.html",context)
@login_required(login_url='login_page')
def edit_wh_e_way_bill_list(request,wh_job_id):
    # wh_job_list_id=Loadingbay_Info.objects.get(pk=wh_job_id)
    # job_id = Gatein_info.objects.get(gatein_job_no=wh_job_num_next).id
    url = 'loadingbay_update/' + str(wh_job_id)
    return redirect(url)

@login_required(login_url='login_page')
def open_requirements_list(request):
    first_name = request.session.get('first_name')
    requirements_list = RequirementsInfo.objects.filter(Q(req_status=2) | Q(req_status=6)).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(requirements_list, 10000)
    page_obj = paginator.get_page(page_number)
    context = {
        'requirements_list': requirements_list,
        'first_name': first_name,
        'page_obj': page_obj,
    }
    return render(request, "asset_mgt_app/requirements_list.html", context)


@login_required(login_url='login_page')
def customer_contract_rate_due_days(request):
    first_name = request.session.get('first_name')
    customer_attach_list = Customerattach.objects.all()

    for i in customer_attach_list:
        customer_attach_id = i.id

        ca_contract_end_date_val = i.ca_contract_end_date
        ca_rate_end_date_val = i.ca_rate_end_date
        ca_sop_end_date_val = i.ca_sop_end_date
        ca_kyc_end_date_val = i.ca_kyc_end_date

        if ca_contract_end_date_val:
            try:
                ca_contract_due_days = (ca_contract_end_date_val - timezone.now().date()).days
                Customerattach.objects.filter(pk=customer_attach_id).update(
                    ca_contract_due_days=ca_contract_due_days
                )
            except Exception as e:
                print("Error calculating ca_contract_due_days:", e)

        if ca_rate_end_date_val:
            try:
                ca_rate_due_days = (ca_rate_end_date_val - timezone.now().date()).days
                Customerattach.objects.filter(pk=customer_attach_id).update(
                    ca_rate_due_days=ca_rate_due_days
                )
            except Exception as e:
                print("Error calculating ca_rate_due_days:", e)

        if ca_sop_end_date_val:
            try:
                ca_sop_due_days = (ca_sop_end_date_val - timezone.now().date()).days
                Customerattach.objects.filter(pk=customer_attach_id).update(
                    ca_sop_due_days=ca_sop_due_days
                )
            except Exception as e:
                print("Error calculating ca_sop_due_days:", e)

        if ca_kyc_end_date_val:
            try:
                ca_kyc_due_days = (ca_kyc_end_date_val - timezone.now().date()).days
                Customerattach.objects.filter(pk=customer_attach_id).update(
                    ca_kyc_due_days=ca_kyc_due_days
                )
            except Exception as e:
                print("Error calculating ca_kyc_due_days:", e)

    return HttpResponse(status=204)


@login_required(login_url='login_page')
def customer_contract_rate_dues_list(request):
    first_name = request.session.get('first_name')

    # Group attachments by customer
    customer_dict = {}
    attachments = Customerattach.objects.all().select_related('ca_customer_name', 'ca_category')

    for attach in attachments:
        if attach.ca_customer_name is None or attach.ca_category is None:
            continue

        cust_id = attach.ca_customer_name.id
        if cust_id not in customer_dict:
            customer_dict[cust_id] = {
                'customer_name': attach.ca_customer_name,
                'contract': '',
                'rate_sheet': '',
                'sop': '',
                'kyc': '',
            }

        due_days = attach.ca_contract_due_days or ''  # Convert None to empty string

        if attach.ca_category.id == 2:  # Contract/SOW
            customer_dict[cust_id]['contract'] = due_days
        elif attach.ca_category.id == 4:  # Rate Sheet
            customer_dict[cust_id]['rate_sheet'] = due_days
        elif attach.ca_category.id == 3:  # SOP
            customer_dict[cust_id]['sop'] = due_days
        elif attach.ca_category.id == 1:  # KYC
            customer_dict[cust_id]['kyc'] = due_days

    context = {
        'customer_list': customer_dict.values(),
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/customer_contract_rate_due_days_list.html", context)

