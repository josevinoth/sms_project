from django.shortcuts import render
import json
from django.db.models import Count, Q,Sum,Case,ExpressionWrapper, When, Value, CharField, Min,FloatField, F,IntegerField
from django.db.models import F, Subquery, OuterRef
from django.db.models.functions import Coalesce,Round
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime
from ..models import Warehouse_goods_info,ExpenseExtinfo,BayInfo,Location_info,UnitInfo,Business_Sol_info,TrbusinesstypeInfo,CustomerInfo,DamagereportInfo,DamageInfo,LocationmasterInfo


def wh_damage_report(request):
    first_name = request.session.get('first_name')
    branches = Location_info.objects.all()
    units =UnitInfo.objects.all()
    selected_branch = request.GET.get('branch', '')
    selected_unit= request.GET.get('unit', '')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if selected_branch:
        units = units.filter(ui_branch_name__loc_name=selected_branch)

    damage_summary = DamagereportInfo.objects.exclude(dam_damage_type=6)

    if selected_branch:
        damage_summary = damage_summary.filter(
            wh_Dam_rep_job_num_id__wh_unit__ui_branch_name__loc_name=selected_branch
        )

    if selected_unit:
        damage_summary = damage_summary.filter(
            wh_Dam_rep_job_num_id__wh_unit__unit_name=selected_unit
        )

    if from_date:
        from_date_obj = timezone.make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
        damage_summary = damage_summary.filter(wh_Dam_rep_job_num_id__wh_checkin_time__gte=from_date_obj)

    if to_date:
        to_date_obj = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))
        damage_summary = damage_summary.filter(wh_Dam_rep_job_num_id__wh_checkin_time__lte=to_date_obj)

    damage_summary = (
        damage_summary
        .values("dam_damage_type__damage_name")
        .annotate(
            damage_count=Count("wh_Dam_rep_job_num_id"),
        )
        .order_by("-damage_count")
    )

    # Convert to lists for Chart.js
    damage_types = [item["dam_damage_type__damage_name"] for item in damage_summary]
    damage_counts = [item["damage_count"] for item in damage_summary]

    context = {
        "damage_summary": damage_summary,
        "first_name": first_name,
        "damage_types": damage_types,
        "damage_counts": damage_counts,
        'branches': branches,
        'units': units,
        'selected_branch': selected_branch,
        'selected_unit': selected_unit,
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request,"asset_mgt_app/WH_damage_report.html",context)


def wh_stock_report(request):
    first_name = request.session.get('first_name')
    branches = Location_info.objects.all()
    units = UnitInfo.objects.all()
    selected_branch = request.GET.get('branch', '')
    selected_unit = request.GET.get('unit', '')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    stock_summary = Warehouse_goods_info.objects.all()

    if selected_branch:
        units = units.filter(ui_branch_name__loc_name=selected_branch)

    filters = {}
    if selected_branch:
        filters["wh_unit__ui_branch_name__loc_name"] = selected_branch

    if selected_unit:
        filters["wh_unit___unit_name"] = selected_unit
    if from_date:
        filters["wh_checkin_time__gte"] = timezone.make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
    if to_date:
        filters["wh_checkin_time__lte"] = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))

    if filters:
        stock_summary = stock_summary.filter(**filters)

    stock_summary = (
        stock_summary
        .values("wh_check_in_out__check_in_out_name")  # Correct field name
        .annotate(
            count=Count("wh_job_no"),
            total_goods_weight=Sum("wh_goods_weight"),
            total_quantity=Sum("wh_total_qty"),
            total_invoice_amount=Sum("wh_invoice_amount_inr")
        )
    )

    stock_summary_json = json.dumps(list(stock_summary))

    context = {
        "stock_summary": stock_summary,
        "stock_summary_json": stock_summary_json,
        "first_name": first_name,
        'branches': branches,
        'units': units,
        'selected_branch': selected_branch,
        'selected_unit': selected_unit,
        'from_date': from_date,
        'to_date': to_date,
    }

    return render(request, "asset_mgt_app/WH_stock_report.html", context)


def wh_space_availability_report(request):
    first_name = request.session.get('first_name')
    selected_branch = request.session.get('branch')
    selected_unit = request.session.get('unit')
    selected_bay = request.session.get('bay')
    selected_businessmodel = request.session.get('businessmodel')

    branches = Location_info.objects.all()
    units = UnitInfo.objects.all()
    bays = BayInfo.objects.all()
    businessmodels = TrbusinesstypeInfo.objects.all()

    utilization_summary = LocationmasterInfo.objects.all()

    # Apply filters dynamically
    filters = {}
    if selected_branch:
        filters["lm_wh_unit__ui_branch_name__loc_name"] = selected_branch
    if selected_unit:
        filters["lm_wh_unit__unit_name"] = selected_unit
    if selected_bay:
        filters["lm_wh_areaside__bay_bayname"] = selected_bay
    if selected_businessmodel:
        filters["lm_customer_model__tb_trbusinesstype"] = selected_businessmodel

    if filters:
        utilization_summary = utilization_summary.filter(**filters)

    # Grouped Summary for Branches (Summed values)
    branch_summary = utilization_summary.values("lm_wh_location__loc_name").annotate(
        total_area=Sum("lm_size"),
        occupied_area=Sum("lm_area_occupied"),
        available_area=Sum("lm_available_area"),
        total_volume=Sum("lm_total_volume"),
        occupied_volume=Sum("lm_volume_occupied"),
        available_volume=Sum("lm_available_volume"),
        available_area_percent=ExpressionWrapper(
            (F("available_area") * 100.0) / F("total_area"),
            output_field=FloatField()
        )
    )

    # 🔹 FIX: Group Units Within Each Branch Separately
    unit_summary = utilization_summary.values("lm_wh_location__loc_name", "lm_wh_unit__unit_name").annotate(
        total_area=Sum("lm_size"),
        occupied_area=Sum("lm_area_occupied"),
        available_area=Sum("lm_available_area"),
        total_volume=Sum("lm_total_volume"),
        occupied_volume=Sum("lm_volume_occupied"),
        available_volume=Sum("lm_available_volume"),
        available_area_percent=ExpressionWrapper(
            (F("available_area") * 100.0) / F("total_area"),
            output_field=FloatField()
        )
    ).order_by("lm_wh_location__loc_name", "lm_wh_unit__unit_name")  # Ensure correct ordering

    context = {
        'utilization_summary': utilization_summary,
        'branch_summary': branch_summary,
        'unit_summary': unit_summary,
        'first_name': first_name,
        'branches': branches,
        'units': units,
        'bays': bays,
        'businessmodels': businessmodels,
        'selected_branch': selected_branch,
        'selected_unit': selected_unit,
        'selected_bay': selected_bay,
        'selected_businessmodel': selected_businessmodel,
    }
    return render(request, "asset_mgt_app/WH_space_availability_report.html", context)


def wh_space_utilization_report(request):
    first_name = request.session.get('first_name')
    selected_branch = request.session.get('branch')
    selected_unit = request.session.get('unit')
    selected_bay = request.session.get('bay')
    selected_businessmodel = request.session.get('businessmodel')

    branches = Location_info.objects.all()
    units = UnitInfo.objects.all()
    bays = BayInfo.objects.all()
    businessmodels = TrbusinesstypeInfo.objects.all()

    utilization_summary = LocationmasterInfo.objects.all()

    # Apply filters dynamically
    filters = {}
    if selected_branch:
        filters["lm_wh_unit__ui_branch_name__loc_name"] = selected_branch
    if selected_unit:
        filters["lm_wh_unit__unit_name"] = selected_unit
    if selected_bay:
        filters["lm_wh_areaside__bay_bayname"] = selected_bay
    if selected_businessmodel:
        filters["lm_customer_model__tb_trbusinesstype"] = selected_businessmodel

    if filters:
        utilization_summary = utilization_summary.filter(**filters)

    # Grouped Summary for Branches (Summed values)
    branch_summary = utilization_summary.values("lm_wh_location__loc_name").annotate(
        total_area=Sum(F("lm_size"), distinct=True),
        occupied_area=Sum(F("lm_wh_location__warehouse_goods_info__wh_goods_area"), distinct=True),  # From WH table
        occupied_volume=Sum(F("lm_wh_location__warehouse_goods_info__wh_goods_volume_weight"), distinct=True),  # From WH table
        available_area=ExpressionWrapper(
            Sum(F("lm_size"), distinct=True) -Sum(F("lm_wh_location__warehouse_goods_info__wh_goods_area"), distinct=True),
            output_field=FloatField()
        ),
        total_volume=Sum(F("lm_total_volume"), distinct=True),
        available_volume=ExpressionWrapper(
            Sum(F("lm_total_volume"), distinct=True) - Sum(F("lm_wh_location__warehouse_goods_info__wh_goods_volume_weight"), distinct=True),
            output_field=FloatField()
        ),

    )

    # 🔹 FIX: Group Units Within Each Branch Separately
    unit_summary = utilization_summary.values("lm_wh_location__loc_name", "lm_wh_unit__unit_name").annotate(
        total_area=Sum(F("lm_size"), distinct=True),
        occupied_area=Sum(F("lm_wh_location__warehouse_goods_info__wh_goods_area"), distinct=True),  # From WH table
        occupied_volume=Sum(F("lm_wh_location__warehouse_goods_info__wh_goods_volume_weight"), distinct=True),
        # From WH table
        available_area=ExpressionWrapper(
            Sum(F("lm_size"), distinct=True) - Sum(F("lm_wh_location__warehouse_goods_info__wh_goods_area"),
                                                   distinct=True),
            output_field=FloatField()
        ),
        total_volume=Sum(F("lm_total_volume"), distinct=True),
        available_volume=ExpressionWrapper(
            Sum(F("lm_total_volume"), distinct=True) - Sum(
                F("lm_wh_location__warehouse_goods_info__wh_goods_volume_weight"), distinct=True),
            output_field=FloatField()
        ),
    )
    context = {
        'utilization_summary': utilization_summary,
        'branch_summary': branch_summary,
        'unit_summary': unit_summary,
        'first_name': first_name,
        'branches': branches,
        'units': units,
        'bays': bays,
        'businessmodels': businessmodels,
        'selected_branch': selected_branch,
        'selected_unit': selected_unit,
        'selected_bay': selected_bay,
        'selected_businessmodel': selected_businessmodel,
    }
    return render(request, "asset_mgt_app/WH_space_utilization_report.html", context)
