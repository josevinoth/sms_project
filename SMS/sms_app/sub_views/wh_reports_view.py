from django.shortcuts import render
import json
from django.db.models import Count, Q,Sum,Case,ExpressionWrapper, When, Value, CharField, Min,FloatField, F,IntegerField
from django.db.models import F, Subquery, OuterRef
from django.db.models.functions import Coalesce,Round
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime
from ..models import Warehouse_goods_info,ExpenseExtinfo,BayInfo,Location_info,UnitInfo,Business_Sol_info,TrbusinesstypeInfo,CustomerInfo,DamagereportInfo,DamageInfo,LocationmasterInfo,Gatein_info


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
    selected_branch = request.session.get('branch','')
    selected_unit = request.session.get('unit','')
    selected_bay = request.session.get('bay','')
    selected_businessmodel = request.session.get('businessmodel','')

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
    ).order_by("lm_wh_location__loc_name", "lm_wh_unit__unit_name").order_by("-occupied_area")  # Ensure correct ordering

    # Get branch-unit with max occupied area
    max_occupied_unit = unit_summary.first()
    max_occupied_area = max_occupied_unit["occupied_area"] if max_occupied_unit else 0
    max_occupied_branch_unit = f"{max_occupied_unit['lm_wh_location__loc_name']} - {max_occupied_unit['lm_wh_unit__unit_name']}" if max_occupied_unit else "N/A"

    branch_labels = []
    total_areas = []
    occupied_areas = []
    available_areas = []
    total_volumes = []
    occupied_volumes = []
    available_volumes = []
    available_area_percentages = []

    for branch in branch_summary:
        branch_labels.append(branch["lm_wh_location__loc_name"])
        total_areas.append(branch["total_area"])
        occupied_areas.append(branch["occupied_area"])
        available_areas.append(branch["available_area"])
        total_volumes.append(branch["total_volume"])
        occupied_volumes.append(branch["occupied_volume"])
        available_volumes.append(branch["available_volume"])
        available_area_percentages.append(branch["available_area_percent"])

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
        'branch_labels': branch_labels,
        'total_areas': total_areas,
        'occupied_areas': occupied_areas,
        'available_areas': available_areas,
        'total_volumes': total_volumes,
        'occupied_volumes': occupied_volumes,
        'available_volumes': available_volumes,
        'available_area_percentages': available_area_percentages,
        'max_occupied_area': max_occupied_area,
        'max_occupied_branch_unit': max_occupied_branch_unit,
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

    # **Subqueries for Branch-wise Occupied Area and Volume**
    occupied_area_branch_subquery = Warehouse_goods_info.objects.filter(
        wh_branch=OuterRef("lm_wh_location")
    ).values("wh_branch").annotate(
        total_occupied_area=Sum("wh_goods_area")
    ).values("total_occupied_area")[:1]

    occupied_volume_branch_subquery = Warehouse_goods_info.objects.filter(
        wh_branch=OuterRef("lm_wh_location")
    ).values("wh_branch").annotate(
        total_occupied_volume=Sum("wh_goods_volume_weight")
    ).values("total_occupied_volume")[:1]

    # **Subqueries for Unit-wise Occupied Area and Volume**
    occupied_area_unit_subquery = Warehouse_goods_info.objects.filter(
        wh_branch=OuterRef("lm_wh_location"),
        wh_unit=OuterRef("lm_wh_unit")
    ).values("wh_branch", "wh_unit").annotate(
        total_occupied_area=Sum("wh_goods_area")
    ).values("total_occupied_area")[:1]

    occupied_volume_unit_subquery = Warehouse_goods_info.objects.filter(
        wh_branch=OuterRef("lm_wh_location"),
        wh_unit=OuterRef("lm_wh_unit")
    ).values("wh_branch", "wh_unit").annotate(
        total_occupied_volume=Sum("wh_goods_volume_weight")
    ).values("total_occupied_volume")[:1]

    # **Branch-Level Summary**
    branch_summary = utilization_summary.values("lm_wh_location__loc_name").annotate(
        total_area=Sum(F("lm_size")),
        occupied_area=Subquery(occupied_area_branch_subquery, output_field=FloatField()),
        occupied_volume=Subquery(occupied_volume_branch_subquery, output_field=FloatField()),
        available_area=ExpressionWrapper(
            Sum(F("lm_size")) - Subquery(occupied_area_branch_subquery, output_field=FloatField()),
            output_field=FloatField()
        ),
        total_volume=Sum(F("lm_total_volume")),
        available_volume=ExpressionWrapper(
            Sum(F("lm_total_volume")) - Subquery(occupied_volume_branch_subquery, output_field=FloatField()),
            output_field=FloatField()
        ),

        occupied_area_percentage=ExpressionWrapper(
            (Subquery(occupied_area_branch_subquery, output_field=FloatField()) * 100.0) / Sum(F("lm_size")),
            output_field=FloatField()
        ),

        available_area_percentage=ExpressionWrapper(
            ((Sum(F("lm_size")) - Subquery(occupied_area_branch_subquery, output_field=FloatField())) * 100.0) / Sum(
                F("lm_size")),
            output_field=FloatField()
        ),
    )

    # **Unit-Level Summary**
    unit_summary = utilization_summary.values("lm_wh_location__loc_name", "lm_wh_unit__unit_name").annotate(
        total_area=Sum(F("lm_size")),
        occupied_area=Subquery(occupied_area_unit_subquery, output_field=FloatField()),
        occupied_volume=Subquery(occupied_volume_unit_subquery, output_field=FloatField()),
        available_area=ExpressionWrapper(
            Sum(F("lm_size")) - Subquery(occupied_area_unit_subquery, output_field=FloatField()),
            output_field=FloatField()
        ),
        total_volume=Sum(F("lm_total_volume")),
        available_volume=ExpressionWrapper(
            Sum(F("lm_total_volume")) - Subquery(occupied_volume_unit_subquery, output_field=FloatField()),
            output_field=FloatField()
        ),

        occupied_area_percentage=ExpressionWrapper(
            (Subquery(occupied_area_unit_subquery, output_field=FloatField()) * 100.0) / Sum(F("lm_size")),
            output_field=FloatField()
        ),

        available_area_percentage=ExpressionWrapper(
            ((Sum(F("lm_size")) - Subquery(occupied_area_unit_subquery, output_field=FloatField())) * 100.0) / Sum(
                F("lm_size")),
            output_field=FloatField()
        ),
    )

    branch_labels = []
    total_areas = []
    occupied_areas = []
    available_areas = []
    total_volumes = []
    occupied_volumes = []
    available_volumes = []


    for branch in branch_summary:
        branch_labels.append(branch["lm_wh_location__loc_name"])
        total_areas.append(branch["total_area"])
        occupied_areas.append(branch["occupied_area"])
        available_areas.append(branch["available_area"])
        total_volumes.append(branch["total_volume"])
        occupied_volumes.append(branch["occupied_volume"])
        available_volumes.append(branch["available_volume"])

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
        'branch_labels': branch_labels,
        'total_areas': total_areas,
        'occupied_areas': occupied_areas,
        'available_areas': available_areas,
        'total_volumes': total_volumes,
        'occupied_volumes': occupied_volumes,
        'available_volumes': available_volumes,
    }

    return render(request, "asset_mgt_app/WH_space_utilization_report.html", context)

def warehouse_dashboard(request):
    first_name = request.session.get('first_name')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    selected_branch = request.GET.get('branch')
    selected_unit = request.GET.get('unit')

    # Get all branches and units
    branches = Location_info.objects.all()
    units = UnitInfo.objects.all()

    # Filter units if branch is selected
    if selected_branch:
        units = units.filter(ui_branch_name__loc_name=selected_branch)

    # Build a common filter for Warehouse_goods_info
    filters = {}
    if from_date:
        filters["wh_checkin_time__gte"] = timezone.make_aware(datetime.strptime(from_date, "%Y-%m-%d"))
    if to_date:
        filters["wh_checkin_time__lte"] = timezone.make_aware(datetime.strptime(to_date, "%Y-%m-%d"))
    if selected_branch:
        filters["wh_unit__ui_branch_name__loc_name"] = selected_branch
    if selected_unit:
        filters["wh_unit__unit_name"] = selected_unit

    # KPI Counts
    total_branches = Location_info.objects.count()
    total_units = units.count()
    total_bays = BayInfo.objects.filter(**({"bay_branch_name__loc_name": selected_branch} if selected_branch else {})).count()
    total_customers = Gatein_info.objects.values("gatein_customer").distinct().count()
    vehicle_count = Gatein_info.objects.values("gatein_truck_number").distinct().count()

    # Space Utilization
    space_filter = {}
    if selected_branch:
        space_filter["lm_wh_location__loc_name"] = selected_branch
    if selected_unit:
        space_filter["lm_wh_unit__unit_name"] = selected_unit

    space_summary = LocationmasterInfo.objects.filter(**space_filter).aggregate(
        total_area=Sum("lm_size"),
        occupied_area=Sum("lm_area_occupied"),
        available_area=Sum("lm_available_area"),
        total_volume=Sum("lm_total_volume"),
        occupied_volume=Sum("lm_volume_occupied"),
        available_volume=Sum("lm_available_volume"),
    )

    space_utilization_percent = (
        (space_summary["occupied_area"] / space_summary["total_area"] * 100) if space_summary["total_area"] else 0
    )

    # Revenue and Top Customers
    revenue_summary = Warehouse_goods_info.objects.filter(**filters).aggregate(
        total_invoice_amount=Sum("wh_invoice_amount_inr"),
        total_tonnage=Sum("wh_goods_weight"),
        total_revenue=Sum("wh_total_invoice_cost")
    )

    top_customers = (
        Warehouse_goods_info.objects.filter(**filters)
        .values("wh_customer_name__cu_nameshort")
        .annotate(total_revenue=Sum("wh_total_invoice_cost"))
        .order_by("-total_revenue")[:10]
    )
    least_customers = (
        Warehouse_goods_info.objects.filter(**filters)
        .values("wh_customer_name__cu_nameshort")
        .annotate(total_revenue=Sum("wh_total_invoice_cost"))
        .order_by("total_revenue")[:10]
    )

    top_customers_json = json.dumps(list(top_customers), default=str)

    # Branch-wise area utilization
    branch_area = LocationmasterInfo.objects.filter(**space_filter).values("lm_wh_location__loc_name").annotate(
        occupied=Sum("lm_area_occupied"),
        available=Sum("lm_available_area")
    )

    # Unit-wise area utilization
    unit_area = LocationmasterInfo.objects.filter(**space_filter).values("lm_wh_unit__unit_name").annotate(
        occupied=Sum("lm_area_occupied"),
        available=Sum("lm_available_area")
    )

    context = {
        "first_name": first_name,
        "branches": branches,
        "units": units,
        "selected_branch": selected_branch,
        "selected_unit": selected_unit,
        "from_date": from_date,
        "to_date": to_date,

        "total_branches": total_branches,
        "total_units": total_units,
        "total_bays": total_bays,
        "total_customers": total_customers,
        "vehicle_count": vehicle_count,

        "space_summary": space_summary,
        "space_summary_json": json.dumps(space_summary, default=str),
        "space_utilization_percent": round(space_utilization_percent, 2),

        "revenue_summary": revenue_summary,
        "top_customers": top_customers,
        "top_customers_json": top_customers_json,
        "least_customers": least_customers,

        "branch_area_json": json.dumps(list(branch_area), default=str),
        "unit_area_json": json.dumps(list(unit_area), default=str),
    }

    return render(request, "asset_mgt_app/warehouse_dashboard.html", context)

