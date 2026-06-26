from datetime import datetime, date
from django.utils import timezone
from django.http import JsonResponse
import calendar
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q, F, Sum, Value, FloatField, Case, When, ExpressionWrapper
from django.db.models.functions import Coalesce, Trim, Upper
from django.utils.safestring import mark_safe
from ..models import TripdetailInfo, ConsignmentdetailInfo, CustomerInfo, CustomerdepartmentInfo, ConsignmentgoodsInfo, \
    Places, VehiclemasterInfo, Driverexpense, Vehicle_allotmentInfo, VendorratemasterInfo1, Vendor_info, OwnershipInfo, \
    CustomerClaimsInfo, VehicletypeInfo, TransInvoiceInfo, MarketBillInfo, AttachedBillInfo, BudgetInfo, \
    Business_Sol_info, UnitInfo, ExpenseExtinfo, Fuelfillinginfo
from ..sub_models.trans_customer_claims_mod import TransCustomerClaimsInfo
from ..sub_forms.dmr_report_form import DmrForm
from ..sub_models.location_info_mod import Location_info
from ..models import VehiclemasterInfo


def safe_num(val):
    if val is None or val == "":
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def safe_str(val):
    return str(val) if val is not None else ""


def safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def calculate_own_vehicle_fuel_and_salary(trips_list, date_from=None, date_to=None):
    from ..models import TripdetailInfo, DrivermasterInfo, DriverSalaryInfo, Fuelfillinginfo
    from django.db.models import Q
    from django.db.models.functions import Coalesce
    import calendar
    from datetime import date as date_cls
    import re

    driver_month_pairs = set()
    for t in trips_list:
        if t.tr_vehiclesource_id != 1: continue
        d_id = None
        if t.tr_driver_master_id:
            d_id = t.tr_driver_master_id
        elif t.tr_drivername:
            m_id = re.search(r'\((\d+)\)', t.tr_drivername)
            if m_id:
                dm = DrivermasterInfo.objects.filter(dm_id=m_id.group(1)).first()
                if dm: d_id = dm.id
        if d_id:
            d = getattr(t, 'resolved_date', None)
            if not d:
                d = t.tr_departeddate_pickup or t.tr_loading_time or t.tr_departeddate or t.tr_created_at
            if d:
                driver_month_pairs.add((d_id, d.month, d.year))

    salary_lookup_raw = {}
    for d_id, m, y in driver_month_pairs:
        q_filter = Q(tr_driver_master_id=d_id)
        driver_obj = DrivermasterInfo.objects.filter(id=d_id).first()
        if driver_obj and driver_obj.dm_id:
            q_filter |= Q(tr_drivername__icontains=f"({driver_obj.dm_id})")

        total_trips = TripdetailInfo.objects.annotate(
            resolved_date=Coalesce('tr_departeddate_pickup', 'tr_loading_time', 'tr_departeddate', 'tr_created_at')
        ).filter(
            q_filter,
            resolved_date__month=m,
            resolved_date__year=y,
            tr_category_id__in=[1, 2, 3]
        ).count()

        salary_rec = DriverSalaryInfo.objects.filter(
            ds_driverid_id=d_id,
            ds_month__month=m,
            ds_month__year=y
        ).first()

        if salary_rec and total_trips > 0:
            salary_lookup_raw[(d_id, m, y)] = safe_num(salary_rec.ds_monthly_salary) / total_trips
        else:
            salary_lookup_raw[(d_id, m, y)] = 0.0

    salary_lookup = {}
    for t in trips_list:
        if t.tr_vehiclesource_id != 1: continue
        d_id = None
        if t.tr_driver_master_id:
            d_id = t.tr_driver_master_id
        elif t.tr_drivername:
            m_id = re.search(r'\((\d+)\)', t.tr_drivername)
            if m_id:
                dm = DrivermasterInfo.objects.filter(dm_id=m_id.group(1)).first()
                if dm: d_id = dm.id
        if d_id:
            d = getattr(t, 'resolved_date', None)
            if not d:
                d = t.tr_departeddate_pickup or t.tr_loading_time or t.tr_departeddate or t.tr_created_at
            if d:
                salary_lookup[t.id] = salary_lookup_raw.get((d_id, d.month, d.year), 0.0)

    fuel_lookup = {}
    fuel_interval_cache = {}

    def _trip_period_bounds(trip):
        if date_from and date_to:
            try:
                return date_cls.fromisoformat(date_from), date_cls.fromisoformat(date_to)
            except:
                pass
        if date_from:
            try:
                return date_cls.fromisoformat(date_from), date_cls.fromisoformat(date_from)
            except:
                pass
        if date_to:
            try:
                return date_cls.fromisoformat(date_to), date_cls.fromisoformat(date_to)
            except:
                pass

        d = getattr(trip, 'resolved_date', None)
        if not d:
            d = trip.tr_departeddate_pickup or trip.tr_loading_time or trip.tr_departeddate or trip.tr_created_at
        if not d:
            return None, None
        d = d.date() if hasattr(d, 'date') else d
        month_start = date_cls(d.year, d.month, 1)
        month_end = date_cls(d.year, d.month, calendar.monthrange(d.year, d.month)[1])
        return month_start, month_end

    def _trip_report_date(trip):
        d = getattr(trip, 'resolved_date', None)
        if not d:
            d = trip.tr_departeddate_pickup or trip.tr_loading_time or trip.tr_departeddate or trip.tr_created_at
        return d.date() if hasattr(d, 'date') else d

    def _vehicle_fuel_intervals(veh_no, period_start, period_end):
        cache_key = (veh_no, period_start, period_end)
        if cache_key in fuel_interval_cache:
            return fuel_interval_cache[cache_key]

        previous_fill = (
            Fuelfillinginfo.objects.filter(
                ff_vehicle_num__vm_registrationnumber__iexact=veh_no,
                ff_date__lt=period_start,
            )
            .order_by('-ff_date', '-ff_odometer_reading', '-id')
            .first()
        )
        fuel_records = list(
            Fuelfillinginfo.objects.filter(
                ff_vehicle_num__vm_registrationnumber__iexact=veh_no,
                ff_date__gte=period_start,
                ff_date__lte=period_end,
            )
            .order_by('ff_date', 'ff_odometer_reading', 'id')
        )
        if previous_fill:
            fuel_records.insert(0, previous_fill)

        if not fuel_records:
            fuel_interval_cache[cache_key] = []
            return []

        intervals = []
        for idx, fuel_rec in enumerate(fuel_records):
            interval_start = fuel_rec.ff_date
            next_fuel_rec = fuel_records[idx + 1] if idx + 1 < len(fuel_records) else None
            interval_end = next_fuel_rec.ff_date if next_fuel_rec else period_end
            include_end = next_fuel_rec is None

            if interval_end < period_start or interval_start > period_end:
                continue

            period_trips = TripdetailInfo.objects.filter(
                tr_vehiclenumber__iexact=veh_no,
                tr_category_id__in=[1, 2, 3],
            ).annotate(
                resolved_date=Coalesce('tr_loading_time', 'tr_departeddate', 'tr_created_at')
            ).filter(
                resolved_date__date__gte=interval_start,
                **{'resolved_date__date__lte' if include_end else 'resolved_date__date__lt': interval_end}
            )

            total_km = sum(vehicle_log_used_km(pt) for pt in period_trips)
            per_km_cost = (safe_num(fuel_rec.ff_fuel_price) / total_km) if total_km > 0 else 0.0

            intervals.append({
                'start': interval_start,
                'end': interval_end,
                'include_end': include_end,
                'per_km_cost': per_km_cost,
            })

        fuel_interval_cache[cache_key] = intervals
        return intervals

    for t in trips_list:
        if t.tr_vehiclesource_id != 1: continue
        veh_no = str(t.tr_vehiclenumber).strip() if t.tr_vehiclenumber else None
        if not veh_no:
            fuel_lookup[t.id] = 0.0
            continue

        period_start, period_end = _trip_period_bounds(t)
        if not period_start:
            fuel_lookup[t.id] = 0.0
            continue

        used_km = vehicle_log_used_km(t)
        trip_date = _trip_report_date(t)
        trip_fuel_cost = 0.0

        if trip_date and used_km > 0:
            for interval in _vehicle_fuel_intervals(veh_no, period_start, period_end):
                starts_inside = trip_date >= interval['start']
                ends_inside = (
                    trip_date <= interval['end']
                    if interval['include_end']
                    else trip_date < interval['end']
                )
                if starts_inside and ends_inside:
                    trip_fuel_cost = used_km * interval['per_km_cost']
                    break

        fuel_lookup[t.id] = round(trip_fuel_cost, 2)

    return fuel_lookup, salary_lookup


def get_trip_pl_data(trip, inv, trip_expenses, va_info, ab_bill, mb_bill, prorated_fuel=None, prorated_salary=None):
    """
    Consolidated logic to calculate P&L data for a single trip.
    Returns: (total_selling, total_buying, profit, profit_pct, display_date)
    """
    # --- Revenue (Harmonized) ---
    # Prioritize Trip Settlement fields (tc_...) if they are non-zero/checked,
    # then fallback to Invoice (ti_...) if available.
    tc_tripcost = (safe_num(trip.tc_tripcost) if (
            getattr(trip, 'tc_tripcost_check', True) and safe_num(trip.tc_tripcost) > 0) else (
        safe_num(inv.ti_transportation_charges) if inv else 0.0))
    tc_tollcost = (safe_num(trip.tc_tollcost) if (
            getattr(trip, 'tc_tollcost_check', True) and safe_num(trip.tc_tollcost) > 0) else (
        safe_num(inv.ti_toll_charges) if inv else 0.0))
    tc_supervisorcost = (safe_num(trip.tc_supervisorcost) if (
            getattr(trip, 'tc_supervisorcost_check', True) and safe_num(trip.tc_supervisorcost) > 0) else (
        safe_num(inv.ti_docket_charges) if inv else 0.0))
    tc_loadingcost = (safe_num(trip.tc_loadingcost) if (
            getattr(trip, 'tc_loadingcost_check', True) and safe_num(trip.tc_loadingcost) > 0) else (
        safe_num(inv.ti_loading_charges) if inv else 0.0))
    tc_unloadingcost = (safe_num(trip.tc_unloadingcost) if (
            getattr(trip, 'tc_unloadingcost_check', True) and safe_num(trip.tc_unloadingcost) > 0) else (
        safe_num(inv.ti_unloading_charges) if inv else 0.0))
    tc_weighmentcost = (safe_num(trip.tc_weighmentcost) if (
            getattr(trip, 'tc_weighmentcost_check', True) and safe_num(trip.tc_weighmentcost) > 0) else (
        safe_num(inv.ti_weighment_charges) if inv else 0.0))

    # Halting Logic
    halting_days = safe_num(trip.tc_no_of_days_halting)
    if getattr(trip, 'tc_total_halting_cost_check', False) and safe_num(trip.tc_total_halting_cost) > 0:
        tc_haltingcost = safe_num(trip.tc_total_halting_cost)
    elif getattr(trip, 'tc_haltingcost_check', False) and safe_num(trip.tc_haltingcost) > 0:
        tc_haltingcost = safe_num(trip.tc_haltingcost) * halting_days
    elif inv:
        tc_haltingcost = safe_num(inv.ti_halting_charges)
    else:
        tc_haltingcost = 0.0

    tc_handlingcost = (safe_num(trip.tc_handlingcost) if (
            getattr(trip, 'tc_handlingcost_check', True) and safe_num(trip.tc_handlingcost) > 0) else (
        safe_num(inv.ti_handling_charges) if inv else 0.0))
    tc_parkingcost = (safe_num(trip.tc_parkingcost) if (
            getattr(trip, 'tc_parkingcost_check', True) and safe_num(trip.tc_parkingcost) > 0) else (
        safe_num(inv.ti_parking_charges) if inv else 0.0))
    tc_rtocost = safe_num(trip.tc_rtocost) if getattr(trip, 'tc_rtocost_check', True) else 0.0
    tc_betacost = safe_num(trip.tc_betacost) if getattr(trip, 'tc_betacost_check', True) else 0.0
    tc_cancellation = safe_num(trip.tc_cancellation) if getattr(trip, 'tc_cancellation_check', True) else 0.0

    total_selling = (tc_tripcost + tc_tollcost + tc_supervisorcost + tc_loadingcost + tc_unloadingcost +
                     tc_weighmentcost + tc_haltingcost + tc_handlingcost + tc_parkingcost +
                     tc_rtocost + tc_betacost + tc_cancellation)

    # --- Expenses (Harmonized) ---
    total_buying = 0.0
    v_source = trip.tr_vehiclesource_id

    if v_source == 1:  # OWN
        fuel = salary = acting = bata = toll = parking = loading = unloading = weighment = handling = hire = other = 0.0
        if prorated_fuel is not None:
            fuel = prorated_fuel
        if prorated_salary is not None:
            salary = prorated_salary

        for e in trip_expenses:
            et = str(e.de_expense_type).lower() if e.de_expense_type else ""
            cv = safe_num(e.de_total_cost)
            if any(k in et for k in ['fuel', 'diesel']):
                if prorated_fuel is None:
                    fuel += cv
            elif 'salary' in et:
                salary += cv
            elif 'acting' in et:
                acting += cv
            elif any(k in et for k in ['bata', 'batta']):
                bata += cv
            elif 'toll' in et:
                toll += cv
            elif 'parking' in et:
                parking += cv
            elif 'loading' in et:
                loading += cv
            elif 'unloading' in et:
                unloading += cv
            elif 'weighment' in et:
                weighment += cv
            elif any(k in et for k in ['handling', 'supervisor']):
                handling += cv
            elif any(k in et for k in ['hire', 'freight']):
                hire += cv
            else:
                other += cv
        total_buying = (
                fuel + salary + acting + bata + toll + parking + loading + unloading + weighment + handling + hire + other)

    elif v_source == 2:  # ATTACHED
        if ab_bill:
            km_run = max(0, safe_num(trip.tr_reportedkm_delivery or trip.tr_reportedkm) - safe_num(trip.tr_departedkm))
            ab_buy_cost = safe_num(ab_bill.ab_buy_cost)
            ab_total_km = safe_num(ab_bill.ab_total_km_run)
            if 0 < km_run < 5000:
                ab_rate = (ab_buy_cost / ab_total_km) if ab_total_km > 0 else 0
                total_buying = round(ab_rate * km_run, 2)
            else:
                num_trips = 1
                if ab_bill.ab_selected_trips:
                    num_trips = len([it.strip() for it in ab_bill.ab_selected_trips.split(',') if it.strip()])
                if num_trips < 1: num_trips = 1
                total_buying = round(ab_buy_cost / num_trips, 2)
        else:
            total_buying = 0.0

    elif v_source == 3:  # MARKET
        if mb_bill:
            total_buying = safe_num(mb_bill.mb_total_cost)

    profit = total_selling - total_buying
    profit_pct = (profit / total_selling * 100) if total_selling > 0 else 0

    # Date Logic
    dates = [trip.tr_departeddate_pickup, trip.tr_loading_time, trip.tr_departeddate, trip.tr_created_at]
    trip_date = next((d for d in dates if d), None)
    display_date = _fmt_dt(trip_date, date_only=True)

    return total_selling, total_buying, profit, profit_pct, display_date


# -------------------------
# HEADERS
# -------------------------

VEHICLE_LOG_HEADERS = [
    "SNo", "Date", "Trip Sheet No.", "Vehicle No.", "Start Date", "End Date", "Starting Time", "Closing Time",
    "Start Km.", "Closing Km.", "Used Km.", "Starting Place", "Closing Place",
    "Cnote No", "Customer", "Shipper", "Driver Name"
]

TRIP_CANCELLATION_HEADERS = [
    "SNo", "Date", "Customer Name", "C-Note", "Trip Code", "Trip Category", "Department",
    "Start DateTime", "End DateTime", "From", "To", "Veh No", "Veh Type",
    "Veh Source", "Cancellation Charges as per Rate Sheet", "Cancellation Charges as per Billing", "Reason"
]

REF_NO_PENDING_HEADERS = [
    "SNo", "Date", "Branch", "Customer Name", "C-Note", "Trip Code", "Department",
    "Start DateTime", "End DateTime", "From", "To", "Veh No", "Truck Type",
    "Veh Source", "Trip Charges", "Toll charges", "AAI charges", "Loading charges",
    "Unloading Charges", "Weighment charges", "Halting Charges", "Handling Charges",
    "Selling (total)"
]

VEHICLE_UTILIZATION_HEADERS = [
    "SNo", "Vehicle Number", "Vehicle Type", "Utilized Days", "Non-Utilized Days", "Non-Utilized Dates"
]

DRIVERS_ADVANCE_HEADERS = [
    "SNo", "Branch", "Date", "Type", "Emp Id", "Driver Name", "Advance Date", "Advance Amount", "No of Days Due"
]

INVOICE_PENDING_HEADERS = [
    "SNo", "Branch", "Customer Short Name", "Planning Date", "Cnote No", "From", "To", "Dept",
    "Veh No", "Veh Type", "Veh Source", "Consignee", "No. of Pcs", "Weight", "Trip Status",
    "Transportation Charges", "Toll Charges", "Parking Charges", "Loading Charges", "Unloading Charges",
    "Halting Charges", "Docket Charges", "Weighment Charges", "Handling Charges", "Cancellation Charges",
    "TOTAL"
]

VENDOR_PL_HEADERS = [
    "S No", "Date", "Cnote", "From", "To", "Customer", "Veh No", "Veh Type",
    "Trip Charges", "Toll charges", "AAI charges", "Loading charges", "Unloading Charges",
    "Weighment charges", "Halting Charges", "Handling Charges", "Selling",
    "Vendor Name", "Bill No", "Buy cost", "Toll Cost", "Parking Cost",
    "Loading cost", "Unloading cost", "Weighment cost", "Handling cost",
    "Total Buying", "Profit", "Profit %"
]

VENDOR_PL_MKT_MKT_HEADERS = [
    "S No", "Date", "Cnote", "From", "To", "Customer", "Veh No", "Veh Type",
    "Trip Charges", "Toll charges", "Loading charges",
    "Unloading Charges", "Weighment charges", "Halting Charges", "Handling Charges", "Parking Charges",
    "Selling", "BVM Inv no.", "Vendor Name", "Bill No", "Trip Cost",
    "Toll Expenses", "Loading Expenses", "Unloading Expenses",
    "Weighment Expenses", "Halting Expenses", "Handling Expenses", "Parking Expenses",
    "Buying", "Profit", "Profit % with Selling", "Profit % with Buying"
]

OWN_VEHICLE_PL_HEADERS = [
    "S No", "Trip date", "Vehicle No", "Cnote No", "Trip Category", "Customer Name", "From", "To",
    "Trip Charges", "Toll Charges", "Parking Charges", "Loading Charges", "Unloading Charges",
    "Weighment Charges", "Handling charges", "Halting Charges", "Revenue",
    "Driver Salary", "Fuel Cost", "Acting Driver", "Driver Bata", "Toll Cost",
    "Parking Cost", "Loading Cost", "Unloading Cost", "Weighment Cost", "Handling Cost", "Vehicle Hire", "Total Expense"
]

WHATSAPP_DELIVERY_STATUS_HEADERS = [
    "S No", "Branch", "Customer Name", "Department", "C-Note No",
    "Consignment Date", "Trip Code", "Vehicle Type", "From", "To",
    "Vehicle No", "Start Date", "End Date", "Driver",
    "Whatsapp Delivered time", "Delivered Status"
]

HALTING_REPORT_HEADERS = [
    "S.No", "Branch", "Date", "Vehicle No", "Veh Type", "Customer Name", "Dept", "Consignor", "Consignee", "Cnote No",
    "Vehicle reported date& time at loading point", "Vehicle started date & time at Unloading Point", "Time Taken",
    "Halting days as per billing", "Halting Charges as per Billing", "Remarks"
]

CLAIM_PENDING_HEADERS = [
    "SNo", "Cnote No", "Trip Date", "From", "To", "Veh No", "Driver Name", "Shipper Ref", "Damage Remarks",
    "Reason For Claim", "Amount",
    "CAPA Issued Date", "CAPA Closed Date", "Status"
]

# -------------------------
# TIME ANALYSIS
# -------------------------
# MIS REPORT MAPPINGS
# -------------------------

TRANSPORT_INCOME_CATEGORIES = {
    "Halting Charges": "bf_Halting_Charges",
    "Halting Charges (SEZ)": "bf_Halting_Charges_SEZ",
    "Loading Charges": "bf_Loading_Charges",
    "Parking Charges": "bf_Parking_Charges",
    "Parking Charges(SEZ)": "bf_Parking_Charges_SEZ",
    "Toll Charges": "bf_Toll_Charges",
    "Transportation Charges": "bf_Transportation_Charges",
    "Transportation Charges - Interstate": "bf_Transportation_Charges_Interstate",
    "Transportation Charges(SEZ)": "bf_Transportation_Charges_SEZ",
    "Transportation Handling Charges": "bf_Transportation_Handling_Charges",
    "Transportation Handling Charges(SEZ)": "bf_Transportation_Handling_Charges_SEZ",
    "Unloading Charges": "bf_Unloading_Charges",
    "Weighment Charges": "bf_Weighment_Charges",
}

TRANSPORT_INVOICE_FIELD_MAPPING = {
    "Halting Charges": "ti_halting_charges",
    "Halting Charges (SEZ)": None,
    "Loading Charges": "ti_loading_charges",
    "Parking Charges": "ti_parking_charges",
    "Parking Charges(SEZ)": None,
    "Toll Charges": "ti_toll_charges",
    "Transportation Charges": "ti_transportation_charges",
    "Transportation Charges - Interstate": None,
    "Transportation Charges(SEZ)": None,
    "Transportation Handling Charges": "ti_handling_charges",
    "Transportation Handling Charges(SEZ)": None,
    "Unloading Charges": "ti_unloading_charges",
    "Weighment Charges": "ti_weighment_charges",
}

TRANSPORT_OPERATIONAL_EXPENSES_FIXED = {
    "GPRS Access & Service": "bf_gprs_access_service",
    "Insurance-Vehicles": "bf_insurance_vehicles",
    "Vehicle-Hire": "bf_vehicle_hire",
}

TRANSPORT_OPERATIONAL_EXPENSES_VARIABLE = {
    "Acting Driver": "bf_acting_driver",
    "CNG": "bf_cng",
    "Diesel-Vehicle": "bf_diesel_vehicle",
    "Driver Betta": "bf_driver_betta",
    "Extra Hrs": "bf_extra_hrs",
    "Extra KM": "bf_extra_km",
    "Halting": "bf_halting",
    "Loading": "bf_loading",
    "Parking": "bf_parking",
    "Rates & Taxes": "bf_rates_taxes",
    "Toll": "bf_toll",
    "Transportation": "bf_transportation",
    "Unloading": "bf_unloading",
    "Vehicle Maintenance": "bf_vehicle_maintenance",
    "Weighment": "bf_weighment",
}

TRANSPORT_NON_OPERATIONAL_EXPENSES_FIXED = {
    "AMC": "bf_amc",
    "Depreciation": "bf_depreciation",
    "Internet & Data Card": "bf_internet_data_card_expenses",
    "Rent-Plant & Machinery": "bf_rent_plant_machinery",
    "Software AMC": "bf_software_AMC_charges",
}

TRANSPORT_NON_OPERATIONAL_EXPENSES_VARIABLE = {
    "CGST Ineligible ITC": "bf_CGST_ineligible_ITC",
    "Conveyance Expenses": "bf_conveyance_expenses",
    "Handling Expenses": "bf_handling_expenses",
    "Hotel, Boarding & Lodging": "bf_hotel_boarding_lodging_expenses",
    "IGST Ineligible ITC": "bf_IGST_ineligible_ITC",
    "Postage & Courier": "bf_postage_courier",
    "Printing & Stationery": "bf_printing_stationery",
    "SGST Ineligible ITC": "bf_SGST_ineligible_ITC",
    "Staff Welfare": "bf_staff_welfare_staff",
    "Supplies & General": "bf_office_supplies_general_expenses",
    "Telephone & Mobile": "bf_telephone_mobile_expenses",
    "Training": "bf_training_expenses",
    "Travelling": "bf_travelling_expenses",
    "Power and Fuel Expenses": "bf_power_fuel",
}

TRANSPORT_EMPLOYEE_BENEFITS_CATEGORIES = {
    "Corp Staff": "bf_corp_staff",
    "Bonus-Corp Staff": "bf_bonus_corp_staff",
    "EDLI Contribution-Corp Staff": "bf_EDLI_contribution_corp_staff",
    "Employer Contribution to ESI-Corp Staff": "bf_employer_contribution_to_ESI_corp_staff",
    "Employer Contribution to PF-Corp Staff": "bf_employer_contribution_to_PF_corp_staff",
    "EPF Admin-Corp Staff": "bf_EPF_admin_charges_corp_staff",
    "Ex-Gratia-Corp Staff": "bf_exgratia_corp_staff",
    "Gratuity-Corp Staff": "bf_gratuity_corp_staff",
    "Incentive-Corp Staff": "bf_incentive_corp_staff",
    "Insurance-Corp Staff": "bf_insurance_corp_staff",
    "LWF-Corp Staff": "bf_lwf_corp_staff",
    "Salaries & Wages-Corp Staff": "bf_salaries_wages_corp_staff",

    "Dept Staff": "bf_dept_staff",
    "Bonus-Staff": "bf_bonus_staff",
    "EDLI Contribution-Staff": "bf_EDLI_contribution_staff",
    "Employer Contribution to ESI-Staff": "bf_employer_contribution_to_ESI_staff",
    "Employer Contribution to PF-Staff": "bf_employer_contribution_to_PF_staff",
    "EPF Admin-Staff": "bf_EPF_admin_charges_staff",
    "Ex-Gratia-Staff": "bf_exgratia_dept_staff",
    "Gratuity-Staff": "bf_gratuity_staff",
    "Incentive-Staff": "bf_incentive_dept_staff",
    "Insurance-Staff": "bf_insurance_staff",
    "LWF-Staff": "bf_lwf_dept_staff",
    "Salaries & Wages-Staff": "bf_salaries_wages_staff",

    "Drivers": "bf_driver_staff",
    "Bonus-Drivers": "bf_bonus_drivers",
    "EDLI Contribution-Drivers": "bf_EDLI_contribution_drivers",
    "Employer Contribution to ESI-Drivers": "bf_employer_contribution_to_ESI_drivers",
    "Employer Contribution to PF-Drivers": "bf_employer_contribution_to_PF_drivers",
    "EPF Admin-Drivers": "bf_EPF_admin_charges_drivers",
    "Ex-Gratia-Drivers": "bf_exgratia_drivers",
    "Gratuity-Drivers": "bf_gratuity_drivers",
    "Incentive-Drivers": "bf_incentive_drivers",
    "Insurance-Drivers": "bf_insurance_drivers",
    "LWF-Drivers": "bf_lwf_drivers",
    "Salaries & Wages-Drivers": "bf_salaries_wages_drivers",
}

TRANSPORT_DEPARTMENT_EXPENSES_CATEGORIES = {
    "Advertisement & Business Promotion": "bf_advertisement_business_promotion",
    "Bank Charges": "bf_bank_charges",
    "Consultancy": "bf_consultancy_charges",
    "Celebration": "bf_celebration_expenses",
    "Directors Remuneration": "bf_directors_remuneration",
    "Interest On Statutory Dues": "bf_interest_on_statutory_dues",
    "Office Repairs & Maintenance": "bf_office_repairs_maintenance",
    "Professional & Legal": "bf_professional_legal_charges",
    "Rent-Furniture & Fittings": "bf_rent_furniture_fittings",
    "Rent-Office": "bf_rent_office",
    "Subscription & Membership": "bf_subscription_membership",
}

TRANSPORT_INTEREST_EXPENSES_CATEGORIES = {
    "Interest on Borrowings": "bf_interest_on_borrowings",
    "Interest on vehicle loan": "bf_interest_on_vehicle_loan",
}

TRANSPORT_BUDGET_FIELD_MAPPING = {
    **TRANSPORT_INCOME_CATEGORIES,
    **TRANSPORT_OPERATIONAL_EXPENSES_FIXED,
    **TRANSPORT_OPERATIONAL_EXPENSES_VARIABLE,
    **TRANSPORT_NON_OPERATIONAL_EXPENSES_FIXED,
    **TRANSPORT_NON_OPERATIONAL_EXPENSES_VARIABLE,
    **TRANSPORT_EMPLOYEE_BENEFITS_CATEGORIES,
    **TRANSPORT_DEPARTMENT_EXPENSES_CATEGORIES,
    **TRANSPORT_INTEREST_EXPENSES_CATEGORIES,
}


# -------------------------
# CLAIM PENDING REPORT HELPERS
# -------------------------

def _fmt_dt(dt, date_only=False):
    """Format a datetime object to IST 'DD-MM-YYYY HH:MM' or 'DD-MM-YYYY'."""
    if dt:
        from datetime import datetime, date
        # If it's a naive date object, localize only if it has time info
        # timezone.localtime() works on aware datetimes.
        try:
            loc_dt = timezone.localtime(dt)
        except Exception:
            # Fallback for date objects or cases where localization isn't possible
            loc_dt = dt

        if date_only:
            return loc_dt.strftime("%d-%m-%Y")
        return loc_dt.strftime("%d-%m-%Y %H:%M")
    return ""


def _duration_str(start, end, round_to_minute=True):
    """Return human-readable duration like '2 hrs 15 mins' between two datetimes.
    Ensures both are converted to local time for consistent delta calculation."""
    if not start or not end:
        return ""

    # Ensure comparison is done on aware localized objects
    st_loc = timezone.localtime(start)
    ed_loc = timezone.localtime(end)

    if round_to_minute:
        st_loc = st_loc.replace(second=0, microsecond=0)
        ed_loc = ed_loc.replace(second=0, microsecond=0)

    delta = ed_loc - st_loc
    total_seconds = int(delta.total_seconds())

    # If the difference is negative, show as "Backward" or return 0 mins?
    # Usually in logistics, 'Pickup' requested before 'Enquiry Created' might happen.
    is_neg = False
    if total_seconds < 0:
        is_neg = True
        total_seconds = abs(total_seconds)

    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60

    res = f"{hours:02d}:{minutes:02d}"
    return f"-{res}" if is_neg else res


TIME_ANALYSIS_HEADERS = [
    "SNo", "Enquiry No", "Cnote No", "Customer Name", "Vehicle No", "Vehicle Type",
    "Enquiry Created Date & Time", "Pickup Date & Time",
    "Vehicle Allotted Date & Time", "Time Taken for Veh Allotment",
    "Cnote Created Date & Time", "Time Taken for Cnote Entry",
    "Trip Created Date & Time", "Time Taken for Trip Entry",
    "Vehicle Reported Date & Time at Loading Point",
    "Dock-In Date & Time at Loading Point", "Idle Time at Loading",
    "Dock-Out Date & Time at Loading Point", "Loading Time",
    "Vehicle Started Date & Time at Loading Point",
    "Vehicle Reported Date & Time at Unloading Point",
    "Dock-In Date & Time at Unloading Point", "Idle Time at Unloading",
    "Dock-Out Date & Time at Unloading Point", "Unloading Time",
    "Vehicle Started Date & Time at Unloading Point",
]

VENDOR_PL_ATTACHED_HEADERS = [
    "S No", "Date", "Cnote", "From", "To", "Customer", "Veh No", "Veh Type",
    "Trip Charges", "Toll charges", "AAI charges", "Loading charges", "Unloading Charges",
    "Weighment charges", "Halting Charges", "Handling Charges", "Selling",
    "Vendor Name", "Bill No", "Buy cost", "Toll Cost", "Parking Cost",
    "Loading cost", "Unloading cost", "Weighment cost", "Handling cost",
    "Halting cost", "RTO cost", "Batta cost",
    "Total Buying", "Profit", "Profit %"
]

DAILY_TRIP_COUNT_HEADERS = [
    "S.No", "Branch", "Date", "Vehicle No", "Vehicle Type",
    "Active Trips For the Day", "OWN/Market/Attached"
]

MAINTENANCE_REPORT_HEADERS = [
    "S.No", "Branch", "Date", "Vehicle No", "Vehicle Type", "Service Type", "KM", "PO Amount",
    "Actual Amount", "Vendor name", "JC No", "Bill No"
]

INSURANCE_RENEWAL_HEADERS = [
    "S No", "Branch", "Vendor Name", "Company Name", "Vehicle No", "Vehicle Type",
    "Insurance", "Renewal Date", "Premium Amount", "IDV Value", "Elapsed (Days)", "DS Status"
]

DIESEL_VS_REVENUE_HEADERS = [
    "Sno", "Branch", "Date", "CNote No", "VehicleNo", "VehicleType", "Mileage Fixed",
    "Leased To Customer", "Km Run", "Diesel Expenses", "Revenue",
    "Diesel vs Revenue %", "Actual Mileage"
]

OWN_VS_MARKET_SALES_HEADERS = [
    "SNo", "Date", "Branch", "Customer Name", "Department",
    "Own Vehicle Sales", "No of Vehicle Used - Own", "No of Jobs - Own", "No of Drivers - Own", "Trip Index - Own",
    "Market Vehicle Sales", "No of Vehicle Used - Market", "No of Jobs - Market", "No of Drivers - Market",
    "Trip Index - Market",
    "Market Buy Rate", "No of Trips - Local", "No of Trips - OutStation"
]

ENQUIRY_PENDING_HEADERS = [
    "SNo", "Date", "Enquiry No", "From", "To", "Vehicle Requested", "Assigned Vehicles", "Unassigned Vehicles",
    "Vehicle Type",
    "Customer Name", "Reason"
]

DRIVER_BALANCE_HEADERS = ["S.No", "Driver Id", "Branch", "Driver name", "Balance"]

POD_PENDING_REPORT_HEADERS = [
    "S.No", "Trip Start Date", "Trip End Date", "Cnote", "Customer Name", "From", "To",
    "Department", "Vehicle No", "Trip Type", "Vehicle Source", "Shipper Name", "Revenue", "Pending Days", "Remarks"
]


# -------------------------
# HELPERS
# -------------------------

def safe_str(v):
    return "" if v is None else str(v)


def safe_num(v):
    try:
        return float(v) if v not in ("", None, "None") else 0
    except:
        return 0


def vehicle_log_used_km(trip):
    """Used km — same logic as Vehicle Log Report (Start Km / Closing Km)."""
    start_km = trip.tr_reportedkm_pickup if trip.tr_reportedkm_pickup else (trip.tr_departedkm or 0)
    closing_km = trip.tr_reportedkm_delivery if trip.tr_reportedkm_delivery else (trip.tr_reportedkm or 0)
    if closing_km and start_km:
        used_km = closing_km - start_km
        if 0 < used_km < 15000:
            return used_km
    return 0


def default_mileage_for_vehicle_type(trip):
    """Default km/litre by vehicle type (Diesel vs Revenue report)."""
    vt_str = str(getattr(trip, 'tr_vehicletype_placed', None) or trip.tr_vehicletype or '').upper()
    if "ACE" in vt_str:
        return 14.0
    if "407" in vt_str:
        return 9.0
    if "10FT" in vt_str:
        return 8.0
    if "14FT" in vt_str:
        return 7.0
    if "17FT" in vt_str:
        return 6.0
    if "19FT" in vt_str:
        return 5.5
    if "20FT" in vt_str:
        return 4.5
    if "22FT" in vt_str:
        return 4.0
    if "24FT" in vt_str:
        return 4.0
    if "32FT" in vt_str:
        return 3.5
    return 4.5


def effective_mileage_km_per_litre(trip, vehicle_master, actual_mileage):
    """Pick km/litre: actual → vehicle master → type default (2.5–18 km/l realistic range)."""
    fixed_mileage = safe_num(vehicle_master.vm_millage) if vehicle_master else 0
    default_mileage = default_mileage_for_vehicle_type(trip)
    if 2.5 <= actual_mileage <= 18.0:
        return actual_mileage
    if fixed_mileage > 0:
        return fixed_mileage
    return default_mileage


def trip_fuel_cost_from_mileage(trip_km, price_per_ltr, eff_mileage):
    """
    Fuel cost per trip (Diesel vs Revenue report):
    litres = trip_km / mileage; cost = litres × rate per litre.
    """
    if trip_km <= 0 or price_per_ltr <= 0 or eff_mileage <= 0:
        return 0.0
    return (price_per_ltr / eff_mileage) * trip_km


def trip_fuel_cost_from_period(used_km, total_fuel_price, total_km, total_litres, eff_mileage=10.0):
    """
    Own Vehicle P/L fuel (Vehicle Log used km + period fuel fills):
    - Per-litre price = total fuel ÷ total litres (date range).
    - If period km is trustworthy (mileage 2.5–18 km/l): trip fuel = used km × (fuel ÷ km).
    - If odometer km is missing on many trips (unrealistic mileage): trip fuel =
      (used km ÷ vehicle mileage) × per-litre price.
    """
    if used_km <= 0 or total_fuel_price <= 0:
        return 0.0

    price_per_ltr = (total_fuel_price / total_litres) if total_litres > 0 else 0
    period_mileage = (total_km / total_litres) if total_litres > 0 else 0

    if total_km > 0 and total_litres > 0 and 2.5 <= period_mileage <= 18.0:
        return used_km * (total_fuel_price / total_km)

    if price_per_ltr <= 0:
        return 0.0
    mileage = eff_mileage if eff_mileage > 0 else 10.0
    return trip_fuel_cost_from_mileage(used_km, price_per_ltr, mileage)


# -------------------------
# VIEWS
# -------------------------
@login_required(login_url='login_page')
def vehicle_log_report_view(request):
    first_name = request.session.get('first_name')
    
    if request.method == "POST":
        form = DmrForm(request.POST)
        vehicle_number = request.POST.get('vehicle_number', '')
        from_location = request.POST.get('from_location', '')
        to_location = request.POST.get('to_location', '')
        branch_id = request.POST.get('branch', '')
        from_date = request.POST.get('from_date', '')
        to_date = request.POST.get('to_date', '')
    else:
        form = DmrForm()
        vehicle_number = ''
        from_location = ''
        to_location = ''
        branch_id = ''
        from_date = ''
        to_date = ''

    all_vehicles = VehiclemasterInfo.objects.filter(
        vm_ownership_id__in=[1, 2]
    ).order_by('vm_registrationnumber')

    return render(request, "asset_mgt_app/vehicle_log_report.html", {
        'first_name': first_name,
        'form': form,
        'headers': VEHICLE_LOG_HEADERS,
        'data_rows': [],
        'all_vehicles': all_vehicles,
        'vehicle_number': vehicle_number,
        'from_location': from_location,
        'to_location': to_location,
        'branch_id': branch_id,
        'from_date': from_date,
        'to_date': to_date,
    })


def vehicle_log_report_ajax_view(request):
    from django.http import JsonResponse
    from django.db.models import Q
    from ..models import Location_info, ConsignmentgoodsInfo, TripdetailInfo

    draw = safe_int(request.GET.get('draw'), 1)
    start = safe_int(request.GET.get('start'), 0)
    length = safe_int(request.GET.get('length'), 10)

    vehicle_number = request.GET.get('vehicle_number', '')
    from_loc_id = request.GET.get('from_location', '')
    to_loc_id = request.GET.get('to_location', '')
    branch_id = request.GET.get('branch', '')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    search_value = request.GET.get('search[value]', '').strip()

    trips = TripdetailInfo.objects.select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_category',
        'tr_consignmentnumber',
        'tr_departedlocation',
        'tr_reportedlocation'
    ).filter(tr_vehiclesource_id__in=[1, 2])

    if vehicle_number:
        trips = trips.filter(tr_vehiclenumber__icontains=vehicle_number)



    if from_date and to_date:
        trips = trips.filter(
            (Q(tr_loading_time__date__gte=from_date) & Q(tr_loading_time__date__lte=to_date)) |
            (Q(tr_departeddate__date__gte=from_date) & Q(tr_departeddate__date__lte=to_date)) |
            (Q(tr_departeddate_pickup__date__gte=from_date) & Q(tr_departeddate_pickup__date__lte=to_date)) |
            (Q(tr_reporteddate__date__gte=from_date) & Q(tr_reporteddate__date__lte=to_date)) |
            (Q(tr_reporteddate_pickup__date__gte=from_date) & Q(tr_reporteddate_pickup__date__lte=to_date)) |
            (Q(tr_unloading_time__date__gte=from_date) & Q(tr_unloading_time__date__lte=to_date))
        )
    elif from_date:
        trips = trips.filter(
            Q(tr_loading_time__date__gte=from_date) |
            Q(tr_departeddate__date__gte=from_date) |
            Q(tr_departeddate_pickup__date__gte=from_date) |
            Q(tr_reporteddate__date__gte=from_date) |
            Q(tr_reporteddate_pickup__date__gte=from_date) |
            Q(tr_unloading_time__date__gte=from_date)
        )
    elif to_date:
        trips = trips.filter(
            Q(tr_loading_time__date__lte=to_date) |
            Q(tr_departeddate__date__lte=to_date) |
            Q(tr_departeddate_pickup__date__lte=to_date) |
            Q(tr_reporteddate__date__lte=to_date) |
            Q(tr_reporteddate_pickup__date__lte=to_date) |
            Q(tr_unloading_time__date__lte=to_date)
        )

    if from_loc_id:
        trips = trips.filter(tr_departedlocation_id=from_loc_id)
    if to_loc_id:
        trips = trips.filter(tr_reportedlocation_id=to_loc_id)

    if branch_id:
        try:
            b_id = int(branch_id)
            if b_id == 1:
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='BLR')
            elif b_id == 2:
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='MAA')
            elif b_id == 3:
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='PNY')
            elif b_id == 4:
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='HYD')
            else:
                loc = Location_info.objects.get(id=b_id)
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains=loc.loc_name)
        except (ValueError, Location_info.DoesNotExist):
            pass

    if search_value:
        trips = trips.filter(
            Q(tr_vehiclenumber__icontains=search_value) |
            Q(tr_consignmentnumber__co_consignmentnumber__icontains=search_value) |
            Q(tr_enquirynumber__en_customername__cu_name__icontains=search_value) |
            Q(tr_drivername__icontains=search_value)
        )

    records_total = trips.order_by().values('id').count()
    records_filtered = records_total

    order_column_idx = safe_int(request.GET.get('order[0][column]'), -1)
    order_dir = request.GET.get('order[0][dir]', 'asc')

    order_map = {
        1: 'tr_created_at',
        2: 'tr_tripnumber',
        3: 'tr_vehiclenumber',
        9: 'tr_departedlocation__place_name',
        10: 'tr_reportedlocation__place_name',
        11: 'tr_consignmentnumber__co_consignmentnumber',
        12: 'tr_enquirynumber__en_customername__cu_name',
        14: 'tr_drivername',
    }

    sort_field = order_map.get(order_column_idx)
    if sort_field:
        if order_dir == 'desc':
            sort_field = '-' + sort_field
        trips = trips.order_by(sort_field)
    else:
        trips = trips.order_by('-tr_created_at')

    if length != -1:
        paginated_trips = trips[start:start + length]
    else:
        paginated_trips = trips[start:]

    all_matching_trips = list(paginated_trips)

    trip_cons_ids = [t.tr_consignmentnumber_id for t in all_matching_trips if t.tr_consignmentnumber_id]

    goods_map = {
        g.cg_consignmentnumber_id: g
        for g in ConsignmentgoodsInfo.objects.filter(
            cg_consignmentnumber_id__in=trip_cons_ids
        ).select_related('cg_consigner')
    }

    data_rows = []
    for idx, trip in enumerate(all_matching_trips, start=start + 1):
        cons_goods = goods_map.get(trip.tr_consignmentnumber_id)

        display_date = trip.tr_loading_time or trip.tr_departeddate or trip.tr_departeddate_pickup or trip.tr_reporteddate or trip.tr_reporteddate_pickup or trip.tr_created_at

        start_km = trip.tr_reportedkm_pickup if trip.tr_reportedkm_pickup else (trip.tr_departedkm or 0)
        closing_km = trip.tr_reportedkm_delivery if trip.tr_reportedkm_delivery else (trip.tr_reportedkm or 0)
        used_km = vehicle_log_used_km(trip)

        from_date_display = _fmt_dt(trip.tr_departeddate, date_only=True) if trip.tr_departeddate else (
            _fmt_dt(trip.tr_departeddate_pickup, date_only=True) if trip.tr_departeddate_pickup else ""
        )
        to_date_display = _fmt_dt(trip.tr_reporteddate_delivery, date_only=True) if trip.tr_reporteddate_delivery else (
            _fmt_dt(trip.tr_reporteddate, date_only=True) if trip.tr_reporteddate else ""
        )

        data_rows.append([
            idx,
            _fmt_dt(display_date, date_only=True),
            safe_str(trip.tr_tripnumber),
            safe_str(trip.tr_vehiclenumber),
            from_date_display,
            to_date_display,
            _fmt_dt(trip.tr_departeddate)[11:] if trip.tr_departeddate else "",
            _fmt_dt(trip.tr_reporteddate)[11:] if trip.tr_reporteddate else "",
            safe_str(start_km),
            safe_str(closing_km),
            safe_str(used_km),
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_str(trip.tr_consignmentnumber.co_consignmentnumber) if trip.tr_consignmentnumber else safe_str(
                trip.tr_category),
            safe_str(trip.tr_enquirynumber.en_customername) if trip.tr_enquirynumber else "",
            safe_str(cons_goods.cg_consigner) if cons_goods else "",
            safe_str(trip.tr_drivername),
        ])

    return JsonResponse({
        "draw": draw,
        "recordsTotal": records_total,
        "recordsFiltered": records_filtered,
        "data": data_rows
    })


@login_required(login_url='login_page')
def trip_cancellation_report_view(request):
    first_name = request.session.get('first_name')

    if request.method == "POST":
        form = DmrForm(request.POST)
    else:
        form = DmrForm()

    customer_id = request.POST.get('dmr_customer')
    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')
    from_loc_id = request.POST.get('from_location')
    to_loc_id = request.POST.get('to_location')
    trip_category_id = request.POST.get('trip_category')
    branch_id = request.POST.get('branch')
    vehicle_search = request.POST.get('vehicle_search', '').strip()

    trips = TripdetailInfo.objects.filter(
        Q(tc_financestatus_id=3)
    ).select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_enquirynumber__en_customerdepartment',
        'tr_consignmentnumber',
        'tr_vehicletype',
        'tr_vehiclesource',
        'tr_departedlocation',
        'tr_reportedlocation',
        'tr_category',
        'tr_vehicletype_placed',
    )

    if vehicle_search:
        trips = trips.filter(tr_vehiclenumber__icontains=vehicle_search)

    if customer_id:
        trips = trips.filter(tr_enquirynumber__en_customername_id=customer_id)

    if trip_category_id:
        trips = trips.filter(tr_enquirynumber__en_trip_type_id=trip_category_id)

    if selected_month and selected_month != '0':
        trips = trips.filter(
            Q(tr_loading_time__month=selected_month) |
            Q(tr_departeddate__month=selected_month) |
            Q(tr_departeddate_pickup__month=selected_month) |
            Q(tr_reporteddate__month=selected_month) |
            Q(tr_unloading_time__month=selected_month) |
            Q(tr_created_at__month=selected_month)
        )

    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) |
            Q(tr_departeddate__year=selected_year) |
            Q(tr_departeddate_pickup__year=selected_year) |
            Q(tr_reporteddate__year=selected_year) |
            Q(tr_unloading_time__year=selected_year) |
            Q(tr_created_at__year=selected_year)
        )

    if from_loc_id:
        trips = trips.filter(tr_departedlocation_id=from_loc_id)

    if to_loc_id:
        trips = trips.filter(tr_reportedlocation_id=to_loc_id)

    if branch_id:
        try:
            b_id = int(branch_id)
            if b_id == 1:  # BLR
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='BLR')
            elif b_id == 2:  # MAA
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='MAA')
            elif b_id == 3:  # PNY
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='PNY')
            elif b_id == 4:  # HYD
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='HYD')
            else:
                loc = Location_info.objects.get(id=b_id)
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains=loc.loc_name)
        except (ValueError, Location_info.DoesNotExist):
            pass

    trips = trips.order_by('-tr_created_at')

    paginator = Paginator(trips, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    data_rows = []

    for idx, trip in enumerate(page_obj, start=(page_obj.start_index() if hasattr(page_obj, 'start_index') else 1)):

        cons_no = safe_str(trip.tr_consignmentnumber.co_consignmentnumber) if trip.tr_consignmentnumber else ""

        cust_name = safe_str(trip.tr_enquirynumber.en_customername).strip().upper()
        branch = "MAA" if cust_name.endswith("MAA") else (
            "BLR" if cust_name.endswith("BLR") else ""
        )

        # Filter-aware date selection
        dates = [
            trip.tr_loading_time, trip.tr_departeddate, trip.tr_departeddate_pickup,
            trip.tr_departeddate_delivery, trip.tr_reporteddate, trip.tr_reporteddate_pickup,
            trip.tr_reporteddate_delivery, trip.tr_unloading_time, trip.tr_dock_in_time,
            trip.tr_dock_out_time, trip.tr_created_at
        ]
        target_month = int(selected_month) if selected_month and selected_month != '0' else None
        target_year = int(selected_year) if selected_year and selected_year != '0' else None

        trip_date = None
        for d in dates:
            if d:
                month_match = (not target_month or d.month == target_month)
                year_match = (not target_year or d.year == target_year)
                if month_match and year_match:
                    trip_date = d
                    break
        if not trip_date:
            trip_date = next((d for d in dates if d), None)
        display_date = trip_date.strftime("%d-%m-%Y") if trip_date else ""

        trip_category = str(trip.tr_category) if trip.tr_category else ""

        # Look up cancellation charge from Charge Master
        from ..sub_models.charge_master_mod import ChargeMasterInfo
        rate_sheet_charge = 0
        try:
            customer_id = trip.tr_enquirynumber.en_customername_id if trip.tr_enquirynumber else None
            vehicle_type_id = trip.tr_vehicletype_placed_id or (trip.tr_vehicletype_id if trip.tr_vehicletype else None)
            if customer_id and vehicle_type_id:
                cm = ChargeMasterInfo.objects.get(
                    cm_customer_id=customer_id,
                    cm_vehicle_type_id=vehicle_type_id,
                    cm_charge_type_id=1
                )
                rate_sheet_charge = cm.cm_amount
        except Exception:
            rate_sheet_charge = 0

        data_rows.append([
            idx,
            display_date,
            safe_str(trip.tr_enquirynumber.en_customername),
            cons_no,
            safe_str(trip.tr_tripnumber),
            trip_category,
            safe_str(trip.tr_enquirynumber.en_customerdepartment),
            _fmt_dt(trip.tr_departeddate),
            _fmt_dt(trip.tr_reporteddate),
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype_placed or trip.tr_vehicletype),
            safe_str(trip.tr_vehiclesource),
            rate_sheet_charge,
            trip.tc_cancellation,
            safe_str(trip.tr_remarks),
        ])
    from ..models import Location_info, VehiclemasterInfo
    return render(request, "asset_mgt_app/trip_cancellation_report.html", {
        'first_name': first_name,
        'form': form,
        'headers': TRIP_CANCELLATION_HEADERS,
        'data_rows': data_rows,
        'page_obj': page_obj,
        'customer_id': int(customer_id) if customer_id else None,
        'selected_month': int(selected_month) if selected_month else None,
        'selected_year': int(selected_year) if selected_year else None,
        'from_location': int(from_loc_id) if from_loc_id else None,
        'to_location': int(to_loc_id) if to_loc_id else None,
        'trip_category_id': int(trip_category_id) if trip_category_id else None,
        'branch_id': int(branch_id) if branch_id else None,
        'vehicle_search': vehicle_search,
        'all_vehicles': VehiclemasterInfo.objects.filter(vm_ownership_id__in=[1, 2]).order_by('vm_registrationnumber'),
        'all_branches': Location_info.objects.filter(id__in=[1, 2]).order_by('loc_name'),
    })


from datetime import date, datetime
from django.contrib.auth.decorators import login_required


@login_required(login_url='login_page')
def vehicle_utilization_report_view(request):
    first_name = request.session.get('first_name')
    from django.utils import timezone
    import calendar

    # -----------------------------
    # GET FILTERS
    # -----------------------------
    if request.method == "POST":
        form = DmrForm(request.POST)
        vehicle_search = request.POST.get('vehicle_search') or ""
        selected_month = request.POST.get('month') or "0"
        selected_year = request.POST.get('year') or "0"
        branch_id = request.POST.get('branch') or ""
        vehicle_source = request.POST.get('vehicle_source') or ""
    else:
        form = DmrForm(request.GET or None)

        vehicle_search = request.GET.get('vehicle_search', '').strip()
        selected_month = request.GET.get('month', str(date.today().month))
        selected_year = request.GET.get('year', str(date.today().year))
        branch_id = request.GET.get('branch', '')
        vehicle_source = request.GET.get('vehicle_source', '')

    # Convert month/year to integers for calculation
    try:
        month_int = int(selected_month)
        year_int = int(selected_year)
    except (ValueError, TypeError):
        month_int = date.today().month
        year_int = date.today().year

    if month_int == 0:
        month_int = date.today().month
    if year_int == 0:
        year_int = date.today().year

    # Calculate month boundaries
    month_start = date(year_int, month_int, 1)
    last_day = calendar.monthrange(year_int, month_int)[1]
    month_end = date(year_int, month_int, last_day)
    total_days_in_month = last_day

    # -----------------------------
    # FETCH VEHICLES
    # -----------------------------
    vehicles = (
        VehiclemasterInfo.objects
        .annotate(
            veh_no_clean=Upper(Trim('vm_registrationnumber'))
        )
        .select_related('vm_vehicletype', 'vm_vendor', 'vm_vendor__vend_branch')
        .filter(vm_ownership_id__in=[1, 2])  # OWN, ATTACHED
    )

    if vehicle_search:
        vehicles = vehicles.filter(vm_registrationnumber__icontains=vehicle_search)

    if vehicle_source:
        vehicles = vehicles.filter(vm_ownership_id=vehicle_source)

    if branch_id and branch_id != 'None':
        try:
            b_id = int(branch_id)
            # Branch IDs: 1: BLR (KA), 2: MAA (TN), 3: PNY (PY), 4: HYD (TS/AP)
            if b_id == 1:
                vehicles = vehicles.filter(Q(vm_vendor__vend_branch_id=1) | Q(vm_registrationnumber__istartswith='KA'))
            elif b_id == 2:
                vehicles = vehicles.filter(Q(vm_vendor__vend_branch_id=2) | Q(vm_registrationnumber__istartswith='TN'))
            elif b_id == 3:
                vehicles = vehicles.filter(Q(vm_vendor__vend_branch_id=3) | Q(vm_registrationnumber__istartswith='PY'))
            elif b_id == 4:
                vehicles = vehicles.filter(
                    Q(vm_vendor__vend_branch_id=4) | Q(vm_registrationnumber__istartswith='TS') | Q(
                        vm_registrationnumber__istartswith='AP'))
            else:
                vehicles = vehicles.filter(vm_vendor__vend_branch_id=b_id)
        except ValueError:
            pass

    vehicles = vehicles.order_by('vm_registrationnumber')

    # -----------------------------
    # FETCH TRIPS OVERLAPPING THE MONTH
    # -----------------------------
    # Overlap criteria: trip_start <= month_end AND (trip_end >= month_start OR trip_end IS NULL)
    overlapping_trips = TripdetailInfo.objects.filter(
        Q(tr_loading_time__date__lte=month_end) |
        Q(tr_departeddate__date__lte=month_end) |
        Q(tr_departeddate_pickup__date__lte=month_end) |
        Q(tr_reporteddate__date__lte=month_end)
    ).filter(
        Q(tr_loading_time__date__gte=month_start) |
        Q(tr_departeddate__date__gte=month_start) |
        Q(tr_departeddate_pickup__date__gte=month_start) |
        Q(tr_reporteddate__date__gte=month_start) |
        Q(tr_reporteddate__isnull=True)
    ).values(
        'tr_vehiclenumber', 'tr_departeddate', 'tr_reporteddate', 'tr_loading_time',
        'tr_departeddate_pickup', 'tr_reporteddate_pickup', 'tr_unloading_time',
        'tc_no_of_days_halting'
    )

    # Group trips by vehicle (normalized registration number)
    trip_map = {}
    for trip in overlapping_trips:
        veh_no = trip['tr_vehiclenumber'].strip().upper() if trip['tr_vehiclenumber'] else ""
        if veh_no:
            trip_map.setdefault(veh_no, []).append(trip)

    # -----------------------------
    # BUILD TABLE
    # -----------------------------
    data_rows = []
    counter = 1
    today_dt = date.today()

    for vehicle in vehicles:
        veh_no_clean = vehicle.vm_registrationnumber.strip().upper()
        veh_trips = trip_map.get(veh_no_clean, [])

        utilized_days_set = set()  # Using a set of dates to avoid double counting overlapping trips

        for trip in veh_trips:
            # Multi-field fallback for start and end
            t_start_dt = trip['tr_departeddate'] or trip['tr_loading_time'] or trip['tr_departeddate_pickup'] or trip[
                'tr_reporteddate']
            t_end_dt = trip['tr_reporteddate'] or trip['tr_reporteddate_pickup'] or trip['tr_unloading_time']

            if not t_start_dt and not t_end_dt:
                continue  # Skip drafts with no activity dates

            t_start = timezone.localtime(t_start_dt).date() if t_start_dt else month_start
            # If trip is unclosed, don't count until today; count as 1 day (the start date)
            t_end = timezone.localtime(t_end_dt).date() if t_end_dt else t_start

            # Effective overlap within the selected month (Base trip period)
            eff_start = max(t_start, month_start)
            eff_end = min(t_end, month_end)

            if eff_start <= eff_end:
                # Add all dates in this movement range to the set
                curr = eff_start
                while curr <= eff_end:
                    utilized_days_set.add(curr)
                    curr += timezone.timedelta(days=1)

            # Add Halting Days as additional utilized dates following the end date
            halting_days = trip.get('tc_no_of_days_halting') or 0
            if halting_days > 0:
                # Start adding halting dates from the day after t_end
                curr_h = t_end + timezone.timedelta(days=1)
                for _ in range(halting_days):
                    if month_start <= curr_h <= month_end:
                        utilized_days_set.add(curr_h)
                    curr_h += timezone.timedelta(days=1)

        utilized_days_count = len(utilized_days_set)

        # Sort dates and format as comma-separated string of day numbers
        sorted_dates = sorted(list(utilized_days_set))
        dates_used_str = ", ".join([d.strftime('%d') for d in sorted_dates])

        # Calculate Non-Utilized Days
        all_month_days = set(month_start + timezone.timedelta(days=i) for i in range(total_days_in_month))
        # Filter all_month_days to only include days up to today if the month is current
        if year_int == today_dt.year and month_int == today_dt.month:
            all_month_days = {d for d in all_month_days if d <= today_dt}

        non_utilized_days_set = all_month_days - utilized_days_set
        non_utilized_days_count = len(non_utilized_days_set)

        sorted_non_utilized_dates = sorted(list(non_utilized_days_set))

        # Highlight Sundays in red
        non_utilized_dates_list = []
        for d in sorted_non_utilized_dates:
            day_str = d.strftime('%d')
            if d.weekday() == 6:  # Sunday
                non_utilized_dates_list.append(f'<span style="color: red; font-weight: bold;">{day_str}</span>')
            else:
                non_utilized_dates_list.append(day_str)
        non_utilized_dates_str = mark_safe(", ".join(non_utilized_dates_list))

        # Branch Logic for row display
        branch_name = ""
        if vehicle.vm_vendor and vehicle.vm_vendor.vend_branch:
            branch_name = str(vehicle.vm_vendor.vend_branch)
        else:
            if veh_no_clean.startswith('TN'):
                branch_name = "MAA"
            elif veh_no_clean.startswith('KA'):
                branch_name = "BLR"
            elif veh_no_clean.startswith('PY'):
                branch_name = "PNY"
            elif veh_no_clean.startswith('TS') or veh_no_clean.startswith('AP'):
                branch_name = "HYD"
            else:
                branch_name = "Other"

        data_rows.append([
            counter,
            vehicle.vm_registrationnumber,
            safe_str(vehicle.vm_vehicletype),
            utilized_days_count,
            non_utilized_days_count,
            non_utilized_dates_str
        ])
        counter += 1

    all_vehicles = VehiclemasterInfo.objects.filter(
        vm_ownership_id__in=[1, 2]
    ).order_by('vm_registrationnumber')

    context = {
        'first_name': first_name,
        'form': form,
        'headers': VEHICLE_UTILIZATION_HEADERS,
        'data_rows': data_rows,
        'selected_month': str(month_int),
        'selected_year': str(year_int),
        'all_vehicles': all_vehicles,
        'vehicle_search': vehicle_search,
        'selected_branch': branch_id,
        'selected_source': vehicle_source,
    }

    return render(
        request,
        "asset_mgt_app/vehicle_utilization_report.html",
        context
    )


@login_required(login_url='login_page')
def ref_no_pending_report_view(request):
    first_name = request.session.get('first_name')
    if request.method == "POST":
        form = DmrForm(request.POST)
    else:
        form = DmrForm()

    customer_id = request.POST.get('dmr_customer')
    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')
    from_loc_id = request.POST.get('from_location')
    to_loc_id = request.POST.get('to_location')
    vehicle_search = request.POST.get('vehicle_search', '').strip()

    # Filter trips where customer reference is missing OR pending in BOTH Trip and Consignment
    trips = (
        TripdetailInfo.objects
        .annotate(
            ref_clean=Trim('tr_customerref'),
            cons_ref_clean=Trim('tr_consignmentnumber__co_cusrefnum')
        )
        .filter(
            (Q(ref_clean__isnull=True) | Q(ref_clean__exact='') | Q(ref_clean='0')) &
            (Q(cons_ref_clean__isnull=True) | Q(cons_ref_clean__exact='') | Q(cons_ref_clean='0')),
            tr_category_id=1
        )
        .select_related(
            'tr_enquirynumber',
            'tr_enquirynumber__en_customername',
            'tr_enquirynumber__en_customerdepartment',
            'tr_consignmentnumber',
            'tr_vehicletype',
            'tr_vehiclesource',
            'tr_departedlocation',
            'tr_reportedlocation'
        )
    )

    if customer_id:
        trips = trips.filter(tr_enquirynumber__en_customername_id=customer_id)
    if selected_month and selected_month != '0':
        trips = trips.filter(
            Q(tr_loading_time__month=selected_month) |
            Q(tr_departeddate__month=selected_month) |
            Q(tr_departeddate_pickup__month=selected_month) |
            Q(tr_reporteddate__month=selected_month) |
            Q(tr_unloading_time__month=selected_month) |
            Q(tr_created_at__month=selected_month)
        )

    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) |
            Q(tr_departeddate__year=selected_year) |
            Q(tr_departeddate_pickup__year=selected_year) |
            Q(tr_reporteddate__year=selected_year) |
            Q(tr_unloading_time__year=selected_year) |
            Q(tr_created_at__year=selected_year)
        )
    if from_loc_id:
        trips = trips.filter(tr_departedlocation_id=from_loc_id)
    if to_loc_id:
        trips = trips.filter(tr_reportedlocation_id=to_loc_id)
    if vehicle_search:
        trips = trips.filter(tr_vehiclenumber__icontains=vehicle_search)

    trips = trips.order_by('-tr_created_at')

    paginator = Paginator(trips, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    data_rows = []
    for idx, trip in enumerate(page_obj, start=(page_obj.start_index() if hasattr(page_obj, 'start_index') else 1)):
        cons_no = safe_str(trip.tr_consignmentnumber.co_consignmentnumber) if trip.tr_consignmentnumber else ""
        cust_name = safe_str(trip.tr_enquirynumber.en_customername).strip().upper()
        branch = "MAA" if cust_name.endswith("MAA") else ("BLR" if cust_name.endswith("BLR") else "")
        # Filter-aware date selection
        dates = [
            trip.tr_loading_time, trip.tr_departeddate, trip.tr_departeddate_pickup,
            trip.tr_departeddate_delivery, trip.tr_reporteddate, trip.tr_reporteddate_pickup,
            trip.tr_reporteddate_delivery, trip.tr_unloading_time, trip.tr_dock_in_time,
            trip.tr_dock_out_time, trip.tr_created_at
        ]
        target_month = int(selected_month) if selected_month and selected_month != '0' else None
        target_year = int(selected_year) if selected_year and selected_year != '0' else None

        trip_date = None
        for d in dates:
            if d:
                month_match = (not target_month or d.month == target_month)
                year_match = (not target_year or d.year == target_year)
                if month_match and year_match:
                    trip_date = d
                    break
        if not trip_date:
            trip_date = next((d for d in dates if d), None)
        display_date = trip_date.strftime("%d-%m-%Y") if trip_date else ""

        # Calculate Total Selling (sum of charges) - Respecting checkboxes
        total_selling = (safe_num(trip.tc_tripcost) if trip.tc_tripcost_check else 0) + \
                        (safe_num(trip.tc_tollcost) if trip.tc_tollcost_check else 0) + \
                        (safe_num(trip.tc_supervisorcost) if trip.tc_supervisorcost_check else 0) + \
                        (safe_num(trip.tc_loadingcost) if trip.tc_loadingcost_check else 0) + \
                        (safe_num(trip.tc_unloadingcost) if trip.tc_unloadingcost_check else 0) + \
                        (safe_num(trip.tc_weighmentcost) if trip.tc_weighmentcost_check else 0) + \
                        (safe_num(trip.tc_haltingcost) if trip.tc_haltingcost_check else 0) + \
                        (safe_num(trip.tc_total_halting_cost) if trip.tc_total_halting_cost_check else 0) + \
                        (safe_num(trip.tc_handlingcost) if trip.tc_handlingcost_check else 0) + \
                        (safe_num(trip.tc_cancellation) if trip.tc_cancellation_check else 0) + \
                        (safe_num(trip.tc_rtocost) if trip.tc_rtocost_check else 0) + \
                        (safe_num(trip.tc_betacost) if trip.tc_betacost_check else 0)

        row = [
            idx,
            display_date,
            branch,
            safe_str(trip.tr_enquirynumber.en_customername),
            cons_no,
            safe_str(trip.tr_tripnumber),
            safe_str(trip.tr_enquirynumber.en_customerdepartment),
            _fmt_dt(trip.tr_departeddate),
            _fmt_dt(trip.tr_reporteddate),
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype_placed or trip.tr_vehicletype),
            safe_str(trip.tr_vehiclesource),
            safe_num(trip.tc_tripcost) if trip.tc_tripcost_check else 0,  # Trip Charges
            safe_num(trip.tc_tollcost) if trip.tc_tollcost_check else 0,  # Toll charges
            safe_num(trip.tc_supervisorcost) if trip.tc_supervisorcost_check else 0,  # AAI charges
            safe_num(trip.tc_loadingcost) if trip.tc_loadingcost_check else 0,  # Loading charges
            safe_num(trip.tc_unloadingcost) if trip.tc_unloadingcost_check else 0,  # Unloading Charges
            safe_num(trip.tc_weighmentcost) if trip.tc_weighmentcost_check else 0,  # Weighment charges
            (safe_num(trip.tc_haltingcost) if trip.tc_haltingcost_check else 0) + (
                safe_num(trip.tc_total_halting_cost) if trip.tc_total_halting_cost_check else 0),  # Halting Charges
            safe_num(trip.tc_handlingcost) if trip.tc_handlingcost_check else 0,  # Handling Charges
            total_selling  # Selling (Total)
        ]
        data_rows.append(row)

    context = {
        'first_name': first_name,
        'form': form,
        'headers': REF_NO_PENDING_HEADERS,
        'data_rows': data_rows,
        'page_obj': page_obj,
        'customer_id': customer_id,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'from_location': from_loc_id,
        'to_location': to_loc_id,
        'vehicle_search': vehicle_search,
        'all_vehicles': VehiclemasterInfo.objects.filter(vm_ownership_id__in=[1, 2, 3]).order_by(
            'vm_registrationnumber'),
    }
    return render(request, "asset_mgt_app/ref_no_pending_report.html", context)


@login_required(login_url='login_page')
def drivers_advance_report_view(request):
    first_name = request.session.get('first_name')
    from ..models import Driverexpense, User_extInfo, DrivermasterInfo
    from datetime import datetime

    # Get filter parameters
    driver_id = request.POST.get('driver_name') or request.GET.get('driver_name')
    from_date = request.POST.get('from_date') or request.GET.get('from_date')
    to_date = request.POST.get('to_date') or request.GET.get('to_date')

    # Fetch only driver advances (expense_type=1)
    advances = Driverexpense.objects.filter(
        de_expense_type__id=1
    ).select_related(
        'driver_name', 'de_driver_id', 'de_expense_type'
    )

    # If driver_id is provided, try to find the name for display
    selected_driver_id = None

    if driver_id:
        advances = advances.filter(driver_name_id=driver_id)
        try:
            selected_driver_id = int(driver_id)
        except (ValueError, TypeError):
            selected_driver_id = None

    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, "%Y-%m-%d")
            advances = advances.filter(de_date__gte=from_date_obj)
        except:
            pass

    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, "%Y-%m-%d")
            advances = advances.filter(de_date__lte=to_date_obj)
        except:
            pass

    advances = advances.order_by('-de_date')

    data_rows = []
    for idx, advance in enumerate(advances, start=1):
        # Get branch from driver's user account if available
        branch = ""
        if advance.driver_name and advance.driver_name.dm_user_id:
            try:
                user_ext = User_extInfo.objects.get(user=advance.driver_name.dm_user_id)
                if user_ext.emp_branch and user_ext.emp_branch.loc_name:
                    # Extract "MAA" / "BLR" from "BVM MAA"
                    branch = user_ext.emp_branch.loc_name.split()[-1]
                else:
                    branch = str(user_ext.emp_branch) if user_ext.emp_branch else ""
            except:
                pass

        # Calculate days due from expense date to today
        days_due = 0
        if advance.de_date:
            days_due = (datetime.now().date() - advance.de_date.date()).days

        row = [
            idx,
            branch,
            _fmt_dt(advance.de_date, date_only=True),
            safe_str(advance.de_expense_type.expense_type if advance.de_expense_type else ""),  # Type (Advance/Expense)
            safe_str(advance.driver_name.dm_id if advance.driver_name else ""),  # Employee ID
            safe_str(advance.driver_name.dm_name if advance.driver_name else ""),  # Driver name
            _fmt_dt(advance.de_date, date_only=True) if advance.de_date and advance.de_expense_type_id == 1 else "",
            # Advance Date
            safe_num(advance.de_total_cost if advance.de_expense_type_id == 1 else 0),  # Advance Amount
            days_due
        ]
        data_rows.append(row)

    # Get all drivers for dropdown
    drivers = DrivermasterInfo.objects.all().order_by('dm_name')

    context = {
        'first_name': first_name,
        'headers': DRIVERS_ADVANCE_HEADERS,
        'data_rows': data_rows,
        'drivers': drivers,
        'selected_driver_id': selected_driver_id,
        'from_date': from_date or '',
        'to_date': to_date or '',
    }
    return render(request, "asset_mgt_app/drivers_advance_report.html", context)


@login_required(login_url='login_page')
def invoice_pending_report_view(request):
    first_name = request.session.get('first_name')

    # Always use GET — filters are applied via AJAX in the DataTable
    # (Synced and re-applied)
    form = DmrForm()

    from ..models import Location_info, OwnershipInfo
    from ..sub_models.trip_status_mod import Tripstatusinfo

    context = {
        'first_name': first_name,
        'form': form,
        'headers': INVOICE_PENDING_HEADERS,
        'all_branches': Location_info.objects.filter(id__in=[1, 2]).order_by('loc_name'),
        'all_vehiclesources': OwnershipInfo.objects.all(),
        'all_tripstatuses': Tripstatusinfo.objects.all().order_by('status'),
    }

    return render(request, "asset_mgt_app/invoice_pending_report.html", context)


@login_required(login_url='login_page')
def invoice_pending_report_ajax_view(request):
    """Server-side DataTables AJAX endpoint for Invoice Pending Report (Synced)."""
    from ..models import TransInvoiceInfo, ConsignmentgoodsInfo
    from ..sub_models.invoice_document_mod import InvoiceDocumentInfo
    from django.http import JsonResponse

    # DataTables params
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 50))
    search_value = request.GET.get('search[value]', '').strip()

    # Custom filter params (passed via AJAX data function)
    customer_id = request.GET.get('dmr_customer', '').strip()
    dept_id = request.GET.get('customer_department', '').strip()
    from_date = request.GET.get('from_date', '').strip()
    to_date = request.GET.get('to_date', '').strip()
    from_loc_id = request.GET.get('from_location', '').strip()
    to_loc_id = request.GET.get('to_location', '').strip()
    branch_id = request.GET.get('branch', '').strip()
    vehicle_source_id = request.GET.get('vehicle_source', '').strip()
    trip_status_id = request.GET.get('trip_status', '').strip()

    # -------------------------
    # Collect all invoiced IDs (same logic as the main view)
    # -------------------------
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

    # -------------------------
    # Base queryset
    # -------------------------
    trips = TripdetailInfo.objects.filter(
        tr_category_id=1
    ).filter(
        Q(tr_enquirynumber__en_customername__cu_name__icontains='MAA') |
        Q(tr_enquirynumber__en_customername__cu_name__icontains='BLR')
    ).exclude(
        tr_consignmentnumber__isnull=True
    ).select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_enquirynumber__en_customerdepartment',
        'tr_consignmentnumber',
        'tr_vehicletype',
        'tr_vehiclesource',
        'tr_departedlocation',
        'tr_reportedlocation',
        'tc_financestatus',
    ).annotate(
        trip_total=(
                Case(When(tc_tripcost_check=True, then=F('tc_tripcost')), default=0.0, output_field=FloatField()) +
                Case(When(tc_tollcost_check=True, then=F('tc_tollcost')), default=0.0, output_field=FloatField()) +
                Case(When(tc_parkingcost_check=True, then=F('tc_parkingcost')), default=0.0,
                     output_field=FloatField()) +
                Case(When(tc_loadingcost_check=True, then=F('tc_loadingcost')), default=0.0,
                     output_field=FloatField()) +
                Case(When(tc_unloadingcost_check=True, then=F('tc_unloadingcost')), default=0.0,
                     output_field=FloatField()) +
                Case(When(tc_haltingcost_check=True, then=F('tc_haltingcost')), default=0.0,
                     output_field=FloatField()) +
                Case(When(tc_rtocost_check=True, then=F('tc_rtocost')), default=0.0, output_field=FloatField()) +
                Case(When(tc_weighmentcost_check=True, then=F('tc_weighmentcost')), default=0.0,
                     output_field=FloatField()) +
                Case(When(tc_handlingcost_check=True, then=F('tc_handlingcost')), default=0.0,
                     output_field=FloatField()) +
                Case(When(tc_supervisorcost_check=True, then=F('tc_supervisorcost')), default=0.0,
                     output_field=FloatField()) +
                Case(When(tc_betacost_check=True, then=F('tc_betacost')), default=0.0, output_field=FloatField()) +
                Case(When(tc_total_halting_cost_check=True, then=F('tc_total_halting_cost')), default=0.0,
                     output_field=FloatField()) +
                Case(When(tc_cancellation_check=True, then=F('tc_cancellation')), default=0.0,
                     output_field=FloatField())
        )
    )

    # -------------------------
    # Apply custom filters
    # -------------------------
    if customer_id:
        trips = trips.filter(tr_enquirynumber__en_customername_id=customer_id)

    if dept_id:
        trips = trips.filter(tr_enquirynumber__en_customerdepartment_id=dept_id)

    if from_date:
        trips = trips.filter(tr_departeddate_pickup__date__gte=from_date)

    if to_date:
        trips = trips.filter(tr_departeddate_pickup__date__lte=to_date)

    if from_loc_id:
        trips = trips.filter(tr_departedlocation_id=from_loc_id)

    if to_loc_id:
        trips = trips.filter(tr_reportedlocation_id=to_loc_id)

    if branch_id:
        try:
            b_id = int(branch_id)
            if b_id == 2:  # MAA
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='MAA')
            elif b_id == 1:  # BLR
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='BLR')
        except (ValueError, TypeError):
            pass

    if vehicle_source_id:
        trips = trips.filter(tr_vehiclesource_id=vehicle_source_id)

    if trip_status_id:
        try:
            ts_id = int(trip_status_id)
            trips = trips.filter(tc_financestatus_id=ts_id)
        except (ValueError, TypeError):
            pass

    # Total before global search
    records_total = trips.count()

    if search_value:
        matching_invoice_trip_numbers = list(InvoiceDocumentInfo.objects.filter(
            id_status__status__icontains=search_value
        ).exclude(
            id_tripnumber__isnull=True
        ).exclude(
            id_tripnumber__exact=''
        ).values_list('id_tripnumber', flat=True))

        q_objects = (
                Q(tr_vehiclenumber__icontains=search_value) |
                Q(tr_enquirynumber__en_customername__cu_name__icontains=search_value) |
                Q(tr_consignmentnumber__co_consignmentnumber__icontains=search_value) |
                Q(tr_departedlocation__place_name__icontains=search_value) |
                Q(tr_reportedlocation__place_name__icontains=search_value) |
                Q(tr_enquirynumber__en_customerdepartment__ct_customerdepartment__icontains=search_value) |
                Q(tr_tripnumber__icontains=search_value) |
                Q(tc_financestatus__status__icontains=search_value)
        )

        if matching_invoice_trip_numbers:
            q_objects |= Q(tr_tripnumber__in=matching_invoice_trip_numbers)

        trips = trips.filter(q_objects)

    records_filtered = trips.count()

    # -------------------------
    # Ordering
    # -------------------------
    order_col = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'desc')
    col_map = {
        0: 'id',
        1: 'tr_enquirynumber__en_customername__cu_name',
        3: 'tr_created_at',
        4: 'tr_consignmentnumber__co_consignmentnumber',
        5: 'tr_departedlocation__place_name',
        6: 'tr_reportedlocation__place_name',
        8: 'tr_vehiclenumber',
        24: 'trip_total',
    }
    order_field = col_map.get(order_col, 'tr_created_at')
    if order_dir == 'desc' and not order_field.startswith('-'):
        order_field = '-' + order_field
    trips = trips.order_by(order_field)

    # -------------------------
    # Slicing for pagination
    # -------------------------
    if length != -1:
        trips_slice = trips[start:start + length]
    else:
        trips_slice = trips[start:]

    # Bulk-fetch consignment goods for current page only
    trip_cons_ids = [t.tr_consignmentnumber_id for t in trips_slice if t.tr_consignmentnumber_id]
    goods_map = {
        g.cg_consignmentnumber_id: g
        for g in ConsignmentgoodsInfo.objects.filter(
            cg_consignmentnumber_id__in=trip_cons_ids
        )
    }

    # Bulk-fetch invoice documents for current page only
    trip_numbers = [t.tr_tripnumber for t in trips_slice if t.tr_tripnumber]
    invoice_docs = InvoiceDocumentInfo.objects.filter(id_tripnumber__in=trip_numbers).select_related('id_status')
    invoice_doc_map = {doc.id_tripnumber: doc.id_status.status for doc in invoice_docs if doc.id_status}

    # -------------------------
    # Build data rows
    # -------------------------
    data = []
    for idx, trip in enumerate(trips_slice, start=start + 1):
        cons = trip.tr_consignmentnumber
        goods = goods_map.get(trip.tr_consignmentnumber_id) if trip.tr_consignmentnumber_id else None
        inv_status = invoice_doc_map.get(trip.tr_tripnumber, "-") if trip.tr_tripnumber else "-"

        # Branch
        branch_name = "OTH"
        cu_name = str(trip.tr_enquirynumber.en_customername if trip.tr_enquirynumber else "").upper()
        if 'MAA' in cu_name:
            branch_name = 'MAA'
        elif 'BLR' in cu_name:
            branch_name = 'BLR'
        elif 'HYD' in cu_name:
            branch_name = 'HYD'
        elif 'PNY' in cu_name:
            branch_name = 'PNY'
        elif 'CJB' in cu_name:
            branch_name = 'CJB'

        # Date selection logic (strictly using tr_departeddate_pickup as the planning date)
        display_date = trip.tr_departeddate_pickup.strftime("%d-%m-%Y") if trip.tr_departeddate_pickup else ""

        if trip.id in all_invoiced_ids:
            trip_status_display = "Invoice Completed"
        elif inv_status != "-":
            trip_status_display = inv_status
        else:
            trip_status_display = safe_str(trip.tc_financestatus) if trip.tc_financestatus else ""

        data.append([
            idx,
            branch_name,
            safe_str(trip.tr_enquirynumber.en_customername) if trip.tr_enquirynumber else "",
            display_date,
            safe_str(cons.co_consignmentnumber) if cons else "",
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_str(trip.tr_enquirynumber.en_customerdepartment) if trip.tr_enquirynumber else "",
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype_placed or trip.tr_vehicletype),
            safe_str(trip.tr_vehiclesource.ow_ownership) if trip.tr_vehiclesource else "",
            safe_str(goods.cg_consignee) if goods else "",
            safe_num(goods.cg_qty) if goods else 0,
            safe_num(goods.cg_weight) if goods else 0.0,
            trip_status_display,
            safe_num(trip.tc_tripcost) if trip.tc_tripcost_check else 0,
            safe_num(trip.tc_tollcost) if trip.tc_tollcost_check else 0,
            safe_num(trip.tc_parkingcost) if trip.tc_parkingcost_check else 0,
            safe_num(trip.tc_loadingcost) if trip.tc_loadingcost_check else 0,
            safe_num(trip.tc_unloadingcost) if trip.tc_unloadingcost_check else 0,
            (safe_num(trip.tc_haltingcost) if trip.tc_haltingcost_check else 0) +
            (safe_num(trip.tc_total_halting_cost) if trip.tc_total_halting_cost_check else 0),
            safe_num(trip.tc_rtocost) if trip.tc_rtocost_check else 0,
            safe_num(trip.tc_weighmentcost) if trip.tc_weighmentcost_check else 0,
            safe_num(trip.tc_handlingcost) if trip.tc_handlingcost_check else 0,
            safe_num(trip.tc_cancellation) if trip.tc_cancellation_check else 0,
            round(safe_num(trip.trip_total), 2),
        ])

    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data,
    })


@login_required(login_url='login_page')
def vendor_p_l_mkt_report_view(request):
    first_name = request.session.get('first_name')

    from ..models import Vehicle_allotmentInfo, VehiclemasterInfo
    from ..sub_models.vendor_info_mod import Vendor_info

    if request.method == "POST":
        form = DmrForm(request.POST)
    else:
        form = DmrForm()

    date_from = (request.POST.get('date_from') or request.GET.get('date_from', '')).strip()
    date_to = (request.POST.get('date_to') or request.GET.get('date_to', '')).strip()
    from_loc_id = request.POST.get('from_location')
    to_loc_id = request.POST.get('to_location')
    branch = request.POST.get('branch', '').strip()
    vendor_id = request.POST.get('vendor_id', '').strip()
    veh_no = (request.POST.get('veh_no') or request.GET.get('veh_no', '')).strip()

    # Fetch only vendors that have been used in MARKET vehicle allotments (source 3)
    # or have MARKET vehicles in master (ownership 3)
    market_vendor_ids_allotment = Vehicle_allotmentInfo.objects.filter(
        va_vehiclesource_id=3,  # MARKET
        va_vendor__isnull=False
    ).values_list('va_vendor_id', flat=True).distinct()

    market_vendor_ids_master = VehiclemasterInfo.objects.filter(
        vm_ownership_id=3,  # MARKET
        vm_vendor__isnull=False
    ).values_list('vm_vendor_id', flat=True).distinct()

    all_vendors = Vendor_info.objects.filter(
        id__in=set(list(market_vendor_ids_allotment) + list(market_vendor_ids_master))
    ).order_by('vend_name')

    # Get vehicle numbers for the selected vendor
    vehicle_numbers = []
    if vendor_id:
        va_mkt_veh = Vehicle_allotmentInfo.objects.filter(
            va_vendor_id=vendor_id,
            va_vehiclesource_id=3,
            va_vehiclenumber_mkt__isnull=False
        ).exclude(va_vehiclenumber_mkt="").values_list('va_vehiclenumber_mkt', flat=True).distinct()

        va_mast_veh = Vehicle_allotmentInfo.objects.filter(
            va_vendor_id=vendor_id,
            va_vehiclesource_id=3,
            va_vehiclenumber__isnull=False
        ).values_list('va_vehiclenumber__vm_registrationnumber', flat=True).distinct()

        vm_mast_veh = VehiclemasterInfo.objects.filter(
            vm_vendor_id=vendor_id,
            vm_ownership_id=3
        ).exclude(vm_registrationnumber__isnull=True).exclude(vm_registrationnumber="").values_list(
            'vm_registrationnumber', flat=True).distinct()

        vehicle_numbers = sorted({
            v.strip().upper() for v in list(va_mkt_veh) + list(va_mast_veh) + list(vm_mast_veh)
            if v and str(v).strip()
        })

    return render(request, "asset_mgt_app/vendor_p_l_mkt_report.html", {
        'first_name': first_name,
        'form': form,
        'headers': VENDOR_PL_MKT_MKT_HEADERS,
        'date_from': date_from,
        'date_to': date_to,
        'from_location': from_loc_id,
        'to_location': to_loc_id,
        'branch': branch,
        'vendor_id': int(vendor_id) if vendor_id else None,
        'veh_no': veh_no,
        'all_vendors': all_vendors,
        'vehicle_numbers': vehicle_numbers,
    })


@login_required(login_url='login_page')
def vendor_p_l_mkt_report_ajax_view(request):
    from django.http import JsonResponse
    from ..models import Vehicle_allotmentInfo, TransInvoiceInfo, Driverexpense, VehiclemasterInfo, VehicletypeInfo,         MarketBillInfo, ConsignmentgoodsInfo, TripdetailInfo
    from ..sub_models.vendor_info_mod import Vendor_info
    from ..sub_models.vendorratemaster1_mod import VendorratemasterInfo1

    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '').strip()

    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    from_loc_id = request.GET.get('from_location', '').strip()
    to_loc_id = request.GET.get('to_location', '').strip()
    branch = request.GET.get('branch', '').strip()
    vendor_id = request.GET.get('vendor_id', '').strip()
    veh_no = request.GET.get('veh_no', '').strip()

    # Identifty all invoiced trip IDs
    invoiced_trip_ids = list(TransInvoiceInfo.objects.filter(ti_trip__isnull=False).values_list('ti_trip_id', flat=True))
    invoiced_cons_ids = TransInvoiceInfo.objects.filter(ti_consignment__isnull=False).values_list('ti_consignment_id', flat=True)
    invoiced_goods_ids = TransInvoiceInfo.objects.filter(ti_goods__isnull=False).values_list('ti_goods_id', flat=True)

    trips_from_cons = list(TripdetailInfo.objects.filter(tr_consignmentnumber_id__in=invoiced_cons_ids).values_list('id', flat=True))
    cons_from_goods = ConsignmentgoodsInfo.objects.filter(id__in=invoiced_goods_ids).values_list('cg_consignmentnumber_id', flat=True)
    trips_from_goods = list(TripdetailInfo.objects.filter(tr_consignmentnumber_id__in=cons_from_goods).values_list('id', flat=True))

    all_invoiced_ids = set(invoiced_trip_ids + trips_from_cons + trips_from_goods)

    # BASE TRIPS
    trips = TripdetailInfo.objects.filter(
        tc_financestatus_id__in=[2, 7, 9],
        tr_vehiclesource_id=3  # 3 = MARKET
    ).select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_enquirynumber__en_customerdepartment',
        'tr_consignmentnumber',
        'tr_vehicletype',
        'tr_vehiclesource',
        'tr_departedlocation',
        'tr_reportedlocation'
    )

    if date_from:
        trips = trips.filter(
            Q(tr_departeddate_pickup__date__gte=date_from) |
            Q(tr_departeddate__date__gte=date_from) |
            Q(tr_loading_time__date__gte=date_from)
        )

    if date_to:
        trips = trips.filter(
            Q(tr_departeddate_pickup__date__lte=date_to) |
            Q(tr_departeddate__date__lte=date_to) |
            Q(tr_loading_time__date__lte=date_to)
        )

    if from_loc_id:
        trips = trips.filter(tr_departedlocation_id=from_loc_id)

    if to_loc_id:
        trips = trips.filter(tr_reportedlocation_id=to_loc_id)

    if branch == 'MAA':
        trips = trips.filter(tr_consignmentnumber__co_consignmentnumber__icontains='MAA')
    elif branch == 'BLR':
        trips = trips.filter(tr_consignmentnumber__co_consignmentnumber__icontains='BLR')

    if vendor_id:
        valid_enquiries = Vehicle_allotmentInfo.objects.filter(va_vendor_id=vendor_id).values_list('va_enquirynumber_id', flat=True)
        trips = trips.filter(tr_enquirynumber_id__in=valid_enquiries)

    if veh_no:
        trips = trips.filter(tr_vehiclenumber__icontains=veh_no)

    records_total = trips.count()

    if search_value:
        q_objects = (
            Q(tr_vehiclenumber__icontains=search_value) |
            Q(tr_enquirynumber__en_customername__cu_name__icontains=search_value) |
            Q(tr_consignmentnumber__co_consignmentnumber__icontains=search_value) |
            Q(tr_departedlocation__place_name__icontains=search_value) |
            Q(tr_reportedlocation__place_name__icontains=search_value) |
            Q(tr_tripnumber__icontains=search_value)
        )
        trips = trips.filter(q_objects)

    # Ordering based on tr_created_at
    order_dir = request.GET.get('order[0][dir]', 'desc')
    order_field = '-tr_created_at' if order_dir == 'desc' else 'tr_created_at'
    trips = trips.order_by(order_field)

    if vendor_id:
        v_id = int(vendor_id)
        trips_all = list(trips)
        trip_enquiries_all = [t.tr_enquirynumber_id for t in trips_all]
        allotments_all = Vehicle_allotmentInfo.objects.filter(va_enquirynumber_id__in=trip_enquiries_all, va_vendor_id=v_id)
        valid_trips = []
        for trip in trips_all:
            if not trip.tr_vehiclenumber:
                continue
            clean_veh = str(trip.tr_vehiclenumber).replace(" ", "").upper()
            matched = False
            for a in allotments_all:
                if a.va_enquirynumber_id == trip.tr_enquirynumber_id:
                    a_veh = str(a.va_vehiclenumber) if a.va_vehiclenumber else (a.va_vehiclenumber_mkt or "")
                    if a_veh.replace(" ", "").upper() == clean_veh:
                        matched = True
                        break
            if matched:
                valid_trips.append(trip)
        records_filtered = len(valid_trips)
        if length != -1:
            trips_list = valid_trips[start:start + length]
        else:
            trips_list = valid_trips[start:]
    else:
        records_filtered = trips.count()
        if length != -1:
            trips_list = list(trips[start:start + length])
        else:
            trips_list = list(trips[start:])
    trip_ids = [t.id for t in trips_list]
    trip_enquiries = [t.tr_enquirynumber_id for t in trips_list]

    allotments = Vehicle_allotmentInfo.objects.filter(va_enquirynumber_id__in=trip_enquiries).select_related('va_vendor')
    invoices = TransInvoiceInfo.objects.filter(ti_trip_id__in=trip_ids)

    trip_id_to_pk = {t.id: t.id for t in trips_list}
    trip_num_to_pk = {t.tr_tripnumber: t.id for t in trips_list if t.tr_tripnumber}
    all_query_ids = [str(t.id) for t in trips_list] + [t.tr_tripnumber for t in trips_list if t.tr_tripnumber]

    expenses = Driverexpense.objects.filter(trip_number__in=all_query_ids)

    allotment_map = {}
    for a in allotments:
        key = (a.va_enquirynumber_id, str(a.va_vehiclenumber) if a.va_vehiclenumber else a.va_vehiclenumber_mkt)
        allotment_map[key] = a

    invoice_obj_map = {i.ti_trip_id: i for i in invoices}
    invoice_map = {i.ti_trip_id: i.ti_inv_no for i in invoices}

    expense_map = {}
    for e in expenses:
        t_id = None
        search_key = str(e.trip_number).strip().upper() if e.trip_number else ""
        if search_key in trip_num_to_pk:
            t_id = trip_num_to_pk[search_key]
        elif search_key.isdigit():
            t_id = int(search_key)
        if t_id and t_id in trip_id_to_pk:
            expense_map.setdefault(t_id, []).append(e)

    all_bills = MarketBillInfo.objects.all().only('mb_bill_no', 'mb_selected_trips')
    bill_no_map = {}
    for b in all_bills:
        if b.mb_selected_trips:
            ids = [tid.strip() for tid in b.mb_selected_trips.split(',') if tid.strip()]
            for tid in ids:
                try:
                    bill_no_map[int(tid)] = b.mb_bill_no
                except:
                    pass

    vendor_ids = set(a.va_vendor_id for a in allotments if a.va_vendor_id)
    rates = VendorratemasterInfo1.objects.filter(
        vr1_vendor_id__in=vendor_ids
    ).values('vr1_fromlocation_id', 'vr1_tolocation_id', 'vr1_vehicletype_id', 'vr1_vendor_id', 'vr1_rate')

    rate_map = {
        (r['vr1_fromlocation_id'], r['vr1_tolocation_id'], r['vr1_vehicletype_id'], r['vr1_vendor_id']): r['vr1_rate']
        for r in rates
    }

    data = []
    
    # We need to maintain a global running counter or use the relative index + start
    # We will use start + idx for serial number
    for idx, trip in enumerate(trips_list, start=1):
        inv = invoice_obj_map.get(trip.id)
        selling_trip = (safe_num(inv.ti_transportation_charges) if inv else (safe_num(trip.tc_tripcost) if trip.tc_tripcost_check else 0.0))

        if trip.tr_vehiclesource_id == 3:  # MARKET
            selling_toll = (safe_num(inv.ti_toll_charges) if inv else (safe_num(trip.tc_tollcost) if trip.tc_tollcost_check else 0.0))
            selling_aai = (safe_num(inv.ti_docket_charges) if inv else (safe_num(trip.tc_supervisorcost) if trip.tc_supervisorcost_check else 0.0))
            selling_loading = (safe_num(inv.ti_loading_charges) if inv else (safe_num(trip.tc_loadingcost) if trip.tc_loadingcost_check else 0.0))
            selling_unloading = (safe_num(inv.ti_unloading_charges) if inv else (safe_num(trip.tc_unloadingcost) if trip.tc_unloadingcost_check else 0.0))
            selling_weighment = (safe_num(inv.ti_weighment_charges) if inv else (safe_num(trip.tc_weighmentcost) if trip.tc_weighmentcost_check else 0.0))
            selling_halting = (safe_num(inv.ti_halting_charges) if inv else ((safe_num(trip.tc_haltingcost) if trip.tc_haltingcost_check else 0) + (safe_num(trip.tc_total_halting_cost) if trip.tc_total_halting_cost_check else 0)))
            selling_handling = (safe_num(inv.ti_handling_charges) if inv else (safe_num(trip.tc_handlingcost) if trip.tc_handlingcost_check else 0.0))
            selling_parking = (safe_num(inv.ti_parking_charges) if inv else (safe_num(trip.tc_parkingcost) if trip.tc_parkingcost_check else 0.0))
        else:
            selling_toll = (safe_num(inv.ti_toll_charges) if inv else (safe_num(trip.tc_tollcost) if trip.tc_tollcost_check else 0.0))
            selling_aai = (safe_num(inv.ti_docket_charges) if inv else (safe_num(trip.tc_supervisorcost) if trip.tc_supervisorcost_check else 0.0))
            selling_loading = (safe_num(inv.ti_loading_charges) if inv else (safe_num(trip.tc_loadingcost) if trip.tc_loadingcost_check else 0.0))
            selling_unloading = (safe_num(inv.ti_unloading_charges) if inv else (safe_num(trip.tc_unloadingcost) if trip.tc_unloadingcost_check else 0.0))
            selling_weighment = (safe_num(inv.ti_weighment_charges) if inv else (safe_num(trip.tc_weighmentcost) if trip.tc_weighmentcost_check else 0.0))
            selling_halting = (safe_num(inv.ti_halting_charges) if inv else ((safe_num(trip.tc_haltingcost) if trip.tc_haltingcost_check else 0) + (safe_num(trip.tc_total_halting_cost) if trip.tc_total_halting_cost_check else 0)))
            selling_handling = (safe_num(inv.ti_handling_charges) if inv else (safe_num(trip.tc_handlingcost) if trip.tc_handlingcost_check else 0.0))
            selling_parking = (safe_num(inv.ti_parking_charges) if inv else (safe_num(trip.tc_parkingcost) if trip.tc_parkingcost_check else 0.0))

        total_selling = (
                selling_trip + selling_toll +
                selling_loading + selling_unloading +
                selling_weighment + selling_halting +
                selling_handling + selling_parking +
                (safe_num(trip.tc_rtocost) if trip.tc_rtocost_check else 0.0) +
                (safe_num(trip.tc_betacost) if trip.tc_betacost_check else 0.0) +
                (safe_num(trip.tc_cancellation) if trip.tc_cancellation_check else 0.0)
        )

        allotment = allotment_map.get((trip.tr_enquirynumber_id, trip.tr_vehiclenumber))
        if not allotment and trip.tr_vehiclenumber:
            clean_veh = trip.tr_vehiclenumber.replace(" ", "").upper()
            for a in allotments:
                if a.va_enquirynumber_id == trip.tr_enquirynumber_id:
                    a_veh_no = (str(a.va_vehiclenumber) if a.va_vehiclenumber else a.va_vehiclenumber_mkt or "")
                    if a_veh_no.replace(" ", "").upper() == clean_veh:
                        allotment = a
                        break

        vendor_name = ""
        buying_trip_cost = 0.0

        if allotment:
            vendor_name = safe_str(allotment.va_vendor) if allotment.va_vendor else "Market"
        else:
            vendor_name = "Market"



        if allotment:
            if allotment.va_vendor:
                v_type_id = trip.tr_vehicletype_id or (trip.tr_vehicletype_placed_id if hasattr(trip, 'tr_vehicletype_placed_id') else None)
                key = (trip.tr_departedlocation_id, trip.tr_reportedlocation_id, v_type_id, allotment.va_vendor_id)
                rate_val = rate_map.get(key)
                if rate_val is not None:
                    buying_trip_cost = safe_num(rate_val)
                else:
                    buying_trip_cost = safe_num(allotment.va_specialbuy) or safe_num(allotment.va_standardbuy)
            else:
                buying_trip_cost = safe_num(allotment.va_specialbuy) or safe_num(allotment.va_standardbuy)
        else:
            vendor_name = "Market"

        trip_expenses = expense_map.get(trip.id, [])

        buying_loading = buying_unloading = buying_weighment = buying_aai = 0.0
        buying_toll = buying_halting = buying_handling = buying_parking = buying_rto = buying_batta = 0.0

        for e in trip_expenses:
            buying_loading += safe_num(e.de_loadingcost)
            buying_unloading += safe_num(e.de_unloadingcost)
            buying_weighment += safe_num(e.de_weighmentcost)
            buying_aai += safe_num(e.de_supervisorcost)
            buying_parking += safe_num(e.de_parkingcost)
            buying_rto += safe_num(e.de_rtocost)
            buying_batta += safe_num(e.de_battacost)

            exp_type_str = str(e.de_expense_type).lower() if e.de_expense_type else ""
            cost_val = safe_num(e.de_total_cost)

            if "toll" in exp_type_str:
                if not e.de_rtocost: buying_toll += cost_val
            elif "halting" in exp_type_str:
                buying_halting += cost_val
            elif "handling" in exp_type_str or "supervisor" in exp_type_str:
                if not e.de_supervisorcost: buying_handling += cost_val
            elif "parking" in exp_type_str:
                if not e.de_parkingcost: buying_parking += cost_val
            elif "loading" in exp_type_str:
                if not e.de_loadingcost: buying_loading += cost_val
            elif "unloading" in exp_type_str:
                if not e.de_unloadingcost: buying_unloading += cost_val
            elif "weighment" in exp_type_str:
                if not e.de_weighmentcost: buying_weighment += cost_val
            elif "bata" in exp_type_str or "batta" in exp_type_str:
                if not e.de_battacost: buying_batta += cost_val

        if trip.tr_vehiclesource_id == 3:  # MARKET
            buying_loading += safe_num(trip.tc_loadingcost)
            buying_unloading += safe_num(trip.tc_unloadingcost)
            buying_weighment += safe_num(trip.tc_weighmentcost)
            buying_aai += safe_num(trip.tc_supervisorcost)
            buying_parking += safe_num(trip.tc_parkingcost)
            buying_halting += (safe_num(trip.tc_haltingcost))
            buying_handling += safe_num(trip.tc_handlingcost)

        total_buying = (
                buying_trip_cost + buying_loading + buying_unloading +
                buying_weighment + buying_toll + buying_halting +
                buying_handling + buying_parking + buying_rto + buying_batta
        )

        profit = total_selling - total_buying
        profit_pct_selling = (profit / total_selling * 100) if total_selling > 0 else 0
        profit_pct_buying = (profit / total_buying * 100) if total_buying > 0 else 0

        date_val = (lambda: (next((d for d in [
            trip.tr_departeddate_pickup, trip.tr_departeddate, trip.tr_loading_time,
            trip.tr_reporteddate, trip.tr_reporteddate_pickup, trip.tr_reporteddate_delivery,
            trip.tr_unloading_time, trip.tr_dock_in_time, trip.tr_dock_out_time, trip.tr_created_at
        ] if d), None)))()
        date_str = date_val.strftime("%d-%m-%Y") if date_val else ""

        row = [
            start + len(data) + 1,
            date_str,
            safe_str(trip.tr_consignmentnumber),
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_str(trip.tr_enquirynumber.en_customername),
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype_placed or trip.tr_vehicletype),
            selling_trip,
            selling_toll,
            selling_loading,
            selling_unloading,
            selling_weighment,
            selling_halting,
            selling_handling,
            selling_parking,
            total_selling,
            invoice_map.get(trip.id, ""),
            vendor_name,
            bill_no_map.get(trip.id, ""),
            buying_trip_cost,
            buying_toll,
            buying_loading,
            buying_unloading,
            buying_weighment,
            buying_halting,
            buying_handling,
            buying_parking,
            total_buying,
            round(profit, 2),
            f"{round(profit_pct_selling, 2)}%",
            f"{round(profit_pct_buying, 2)}%",
        ]
        data.append(row)

    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data
    })
@login_required(login_url='login_page')
def vendor_p_l_attached_report_view(request):
    first_name = request.session.get('first_name')

    from ..models import Vehicle_allotmentInfo, VehiclemasterInfo
    from ..sub_models.vendor_info_mod import Vendor_info

    if request.method == "POST":
        form = DmrForm(request.POST)
    else:
        form = DmrForm()

    date_from = (request.POST.get('date_from') or request.GET.get('date_from', '')).strip()
    date_to = (request.POST.get('date_to') or request.GET.get('date_to', '')).strip()
    from_loc_id = request.POST.get('from_location')
    to_loc_id = request.POST.get('to_location')
    vendor_id = request.POST.get('vendor_id') or request.GET.get('vendor_id')

    if vendor_id:
        try:
            vendor_id = int(vendor_id)
        except ValueError:
            vendor_id = None
    else:
        vendor_id = None

    vehicle_type_id = request.POST.get('vehicle_type') or request.GET.get('vehicle_type')
    veh_no = (request.POST.get('veh_no') or request.GET.get('veh_no', '')).strip()

    attached_vendor_ids_allotment = Vehicle_allotmentInfo.objects.filter(
        va_vehiclesource_id=2,  # ATTACHED
        va_vendor__isnull=False
    ).values_list('va_vendor_id', flat=True).distinct()

    attached_vendor_ids_master = VehiclemasterInfo.objects.filter(
        vm_ownership_id=2,  # ATTACHED
        vm_vendor__isnull=False
    ).values_list('vm_vendor_id', flat=True).distinct()

    all_vendors = Vendor_info.objects.filter(
        id__in=set(list(attached_vendor_ids_allotment) + list(attached_vendor_ids_master))
    ).order_by('vend_name')

    vehicle_numbers = []
    if vendor_id:
        va_att_veh = Vehicle_allotmentInfo.objects.filter(
            va_vendor_id=vendor_id, va_vehiclesource_id=2, va_vehiclenumber_mkt__isnull=False
        ).exclude(va_vehiclenumber_mkt="").values_list('va_vehiclenumber_mkt', flat=True).distinct()

        va_mast_veh = Vehicle_allotmentInfo.objects.filter(
            va_vendor_id=vendor_id, va_vehiclesource_id=2, va_vehiclenumber__isnull=False
        ).values_list('va_vehiclenumber__vm_registrationnumber', flat=True).distinct()

        vm_mast_veh = VehiclemasterInfo.objects.filter(
            vm_vendor_id=vendor_id, vm_ownership_id=2
        ).exclude(vm_registrationnumber__isnull=True).exclude(vm_registrationnumber="").values_list(
            'vm_registrationnumber', flat=True).distinct()

        vehicle_numbers = sorted({
            v.strip().upper() for v in list(va_att_veh) + list(va_mast_veh) + list(vm_mast_veh)
            if v and str(v).strip()
        })

    return render(request, "asset_mgt_app/vendor_p_l_attached_report.html", {
        'first_name': first_name,
        'form': form,
        'headers': VENDOR_PL_ATTACHED_HEADERS,
        'date_from': date_from,
        'date_to': date_to,
        'from_location': from_loc_id,
        'to_location': to_loc_id,
        'vehicle_type': vehicle_type_id,
        'vendor_id': vendor_id,
        'veh_no': veh_no,
        'all_vendors': all_vendors,
        'vehicle_numbers': vehicle_numbers,
    })


@login_required(login_url='login_page')
def vendor_p_l_attached_report_ajax_view(request):
    from django.http import JsonResponse
    from ..models import Vehicle_allotmentInfo, TransInvoiceInfo, Driverexpense, VehiclemasterInfo, VehicletypeInfo,         MarketBillInfo, ConsignmentgoodsInfo, TripdetailInfo
    from ..sub_models.vendor_info_mod import Vendor_info

    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '').strip()

    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    from_loc_id = request.GET.get('from_location', '').strip()
    to_loc_id = request.GET.get('to_location', '').strip()
    vendor_id = request.GET.get('vendor_id', '').strip()
    
    if vendor_id:
        try:
            vendor_id = int(vendor_id)
        except ValueError:
            vendor_id = None
    else:
        vendor_id = None
        
    vehicle_type_id = request.GET.get('vehicle_type', '').strip()
    veh_no = request.GET.get('veh_no', '').strip()

    invoiced_trip_ids = list(TransInvoiceInfo.objects.filter(ti_trip__isnull=False).values_list('ti_trip_id', flat=True))
    invoiced_cons_ids = TransInvoiceInfo.objects.filter(ti_consignment__isnull=False).values_list('ti_consignment_id', flat=True)
    invoiced_goods_ids = TransInvoiceInfo.objects.filter(ti_goods__isnull=False).values_list('ti_goods_id', flat=True)

    trips_from_cons = list(TripdetailInfo.objects.filter(tr_consignmentnumber_id__in=invoiced_cons_ids).values_list('id', flat=True))
    cons_from_goods = ConsignmentgoodsInfo.objects.filter(id__in=invoiced_goods_ids).values_list('cg_consignmentnumber_id', flat=True)
    trips_from_goods = list(TripdetailInfo.objects.filter(tr_consignmentnumber_id__in=cons_from_goods).values_list('id', flat=True))

    all_invoiced_ids = set(invoiced_trip_ids + trips_from_cons + trips_from_goods)

    trips = TripdetailInfo.objects.filter(
        tc_financestatus_id__in=[2, 7, 9],
        tr_vehiclesource_id=2  # 2 = ATTACHED
    ).select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_enquirynumber__en_customerdepartment',
        'tr_consignmentnumber',
        'tr_vehicletype',
        'tr_vehiclesource',
        'tr_departedlocation',
        'tr_reportedlocation'
    )

    if date_from:
        trips = trips.filter(
            Q(tr_departeddate_pickup__date__gte=date_from) |
            Q(tr_departeddate__date__gte=date_from) |
            Q(tr_loading_time__date__gte=date_from)
        )

    if date_to:
        trips = trips.filter(
            Q(tr_departeddate_pickup__date__lte=date_to) |
            Q(tr_departeddate__date__lte=date_to) |
            Q(tr_loading_time__date__lte=date_to)
        )

    if from_loc_id:
        trips = trips.filter(tr_departedlocation_id=from_loc_id)

    if to_loc_id:
        trips = trips.filter(tr_reportedlocation_id=to_loc_id)

    if vehicle_type_id:
        trips = trips.filter(tr_vehicletype_id=vehicle_type_id)

    if vendor_id:
        enquiries_with_vendor = Vehicle_allotmentInfo.objects.filter(va_vendor__isnull=False).values_list('va_enquirynumber_id', flat=True)
        enquiries_for_this_vendor = Vehicle_allotmentInfo.objects.filter(va_vendor_id=vendor_id).values_list('va_enquirynumber_id', flat=True)
        vendor_vehicles = VehiclemasterInfo.objects.filter(vm_vendor_id=vendor_id).values_list('vm_registrationnumber', flat=True)

        trips = trips.filter(
            Q(tr_enquirynumber_id__in=enquiries_for_this_vendor) |
            (~Q(tr_enquirynumber_id__in=enquiries_with_vendor) & Q(tr_vehiclenumber__in=vendor_vehicles))
        )

    if veh_no:
        trips = trips.filter(tr_vehiclenumber__icontains=veh_no)

    records_total = trips.count()

    if search_value:
        q_objects = (
            Q(tr_vehiclenumber__icontains=search_value) |
            Q(tr_enquirynumber__en_customername__cu_name__icontains=search_value) |
            Q(tr_consignmentnumber__co_consignmentnumber__icontains=search_value) |
            Q(tr_departedlocation__place_name__icontains=search_value) |
            Q(tr_reportedlocation__place_name__icontains=search_value) |
            Q(tr_tripnumber__icontains=search_value)
        )
        trips = trips.filter(q_objects)

    records_filtered = trips.count()

    order_dir = request.GET.get('order[0][dir]', 'desc')
    order_field = '-tr_created_at' if order_dir == 'desc' else 'tr_created_at'
    trips = trips.order_by(order_field)

    if length != -1:
        trips_slice = trips[start:start + length]
    else:
        trips_slice = trips[start:]

    trips_list = list(trips_slice)
    trip_ids = [t.id for t in trips_list]
    trip_enquiries = [t.tr_enquirynumber_id for t in trips_list]

    va_map = {}
    for va in Vehicle_allotmentInfo.objects.filter(va_enquirynumber_id__in=trip_enquiries).select_related('va_vendor'):
        if va.va_enquirynumber_id not in va_map:
            va_map[va.va_enquirynumber_id] = va
        elif va.va_vendor:
            va_map[va.va_enquirynumber_id] = va

    inv_map = {inv.ti_trip_id: inv for inv in TransInvoiceInfo.objects.filter(ti_trip_id__in=trip_ids)}

    trip_id_to_pk = {t.id: t.id for t in trips_list}
    trip_num_to_pk = {str(t.tr_tripnumber).strip(): t.id for t in trips_list if t.tr_tripnumber}
    cnote_to_pk = {str(t.tr_consignmentnumber.co_consignmentnumber).strip(): t.id for t in trips_list if t.tr_consignmentnumber and t.tr_consignmentnumber.co_consignmentnumber}

    all_query_ids = [str(t.id) for t in trips_list]
    for t in trips_list:
        if t.tr_tripnumber: all_query_ids.append(str(t.tr_tripnumber).strip())
        if t.tr_consignmentnumber and t.tr_consignmentnumber.co_consignmentnumber:
            all_query_ids.append(str(t.tr_consignmentnumber.co_consignmentnumber).strip())
    all_query_ids = list(set(all_query_ids))

    driver_expense_map = {}
    expenses = Driverexpense.objects.filter(trip_number__in=all_query_ids)
    for exp in expenses:
        t_id = None
        s_key = str(exp.trip_number).strip() if exp.trip_number else ""
        if s_key in trip_num_to_pk:
            t_id = trip_num_to_pk[s_key]
        elif s_key in cnote_to_pk:
            t_id = cnote_to_pk[s_key]
        elif s_key.isdigit():
            t_id = int(s_key)
        if t_id and t_id in trip_id_to_pk:
            driver_expense_map.setdefault(t_id, []).append(exp)

    bill_no_map = {}
    all_market_bills = MarketBillInfo.objects.all().only('mb_bill_no', 'mb_selected_trips')
    for b in all_market_bills:
        if b.mb_selected_trips:
            ids = [tid.strip() for tid in b.mb_selected_trips.split(',') if tid.strip()]
            for tid in ids:
                try:
                    bill_no_map[int(tid)] = b.mb_bill_no
                except:
                    bill_no_map[tid] = b.mb_bill_no

    attached_bill_map = {}
    from ..models import AttachedBillInfo
    ab_bills = AttachedBillInfo.objects.all().only(
        'ab_bill_no', 'ab_selected_trips', 'ab_buy_cost', 'ab_total_km_run',
        'ab_from_date', 'ab_to_date', 'ab_vehicle_number_id'
    ).select_related('ab_vehicle_number')

    for b in ab_bills:
        if b.ab_selected_trips:
            ids = [tid.strip() for tid in b.ab_selected_trips.split(',') if tid.strip()]
            for tid in ids:
                try:
                    t_id_int = int(tid)
                    bill_no_map[t_id_int] = b.ab_bill_no
                    attached_bill_map[t_id_int] = b
                except:
                    bill_no_map[tid] = b.ab_bill_no

    from ..models import VehiclemasterInfo
    vehicles = VehiclemasterInfo.objects.filter(vm_ownership_id=2).select_related('vm_vendor')
    veh_map = {v.vm_registrationnumber.replace(" ","").upper(): v for v in vehicles if v.vm_registrationnumber}

    data = []

    for idx, trip in enumerate(trips_list, start=1):
        inv = inv_map.get(trip.id)
        allotment = va_map.get(trip.tr_enquirynumber_id)
        trip_expenses = driver_expense_map.get(trip.id, [])

        clean_veh_no = trip.tr_vehiclenumber.replace(" ", "").upper() if trip.tr_vehiclenumber else ""
        veh_master = veh_map.get(clean_veh_no)

        if allotment and allotment.va_vendor:
            vendor_name = safe_str(allotment.va_vendor)
            v_id = allotment.va_vendor_id
        elif veh_master and veh_master.vm_vendor:
            vendor_name = safe_str(veh_master.vm_vendor)
            v_id = veh_master.vm_vendor_id
        else:
            vendor_name = "Attached"
            v_id = None

        if vendor_id and v_id != vendor_id:
            continue

        selling_trip = safe_num(inv.ti_transportation_charges) if inv else (safe_num(trip.tc_tripcost) if trip.tc_tripcost_check else 0.0)
        selling_toll = safe_num(inv.ti_toll_charges) if inv else (safe_num(trip.tc_tollcost) if trip.tc_tollcost_check else 0.0)
        selling_aai = safe_num(inv.ti_docket_charges) if inv else (safe_num(trip.tc_supervisorcost) if trip.tc_supervisorcost_check else 0.0)
        selling_loading = safe_num(inv.ti_loading_charges) if inv else (safe_num(trip.tc_loadingcost) if trip.tc_loadingcost_check else 0.0)
        selling_unloading = safe_num(inv.ti_unloading_charges) if inv else (safe_num(trip.tc_unloadingcost) if trip.tc_unloadingcost_check else 0.0)
        selling_weighment = safe_num(inv.ti_weighment_charges) if inv else (safe_num(trip.tc_weighmentcost) if trip.tc_weighmentcost_check else 0.0)
        selling_halting = safe_num(inv.ti_halting_charges) if inv else ((safe_num(trip.tc_haltingcost) if trip.tc_haltingcost_check else 0) + (safe_num(trip.tc_total_halting_cost) if trip.tc_total_halting_cost_check else 0))
        selling_handling = safe_num(inv.ti_handling_charges) if inv else (safe_num(trip.tc_handlingcost) if trip.tc_handlingcost_check else 0.0)
        selling_parking = safe_num(inv.ti_parking_charges) if inv else (safe_num(trip.tc_parkingcost) if trip.tc_parkingcost_check else 0.0)

        total_selling = (
                selling_trip + selling_toll + selling_aai + selling_loading + selling_unloading +
                selling_weighment + selling_halting + selling_handling + selling_parking +
                (safe_num(trip.tc_rtocost) if trip.tc_rtocost_check else 0.0) +
                (safe_num(trip.tc_betacost) if trip.tc_betacost_check else 0.0) +
                (safe_num(trip.tc_cancellation) if trip.tc_cancellation_check else 0.0)
        )

        buying_trip_cost = 0.0
        km_run_val = ""

        att_bill = attached_bill_map.get(trip.id)
        if att_bill:
            total_trips = len([t for t in str(att_bill.ab_selected_trips).split(',') if t.strip()])
            if total_trips > 0:
                buying_trip_cost = safe_num(att_bill.ab_buy_cost) / total_trips
            km_run_val = safe_num(att_bill.ab_total_km_run)

        buying_loading = buying_unloading = buying_weighment = buying_aai = 0.0
        buying_toll = buying_halting = buying_handling = buying_parking = buying_rto = buying_batta = 0.0

        for e in trip_expenses:
            buying_loading += safe_num(e.de_loadingcost)
            buying_unloading += safe_num(e.de_unloadingcost)
            buying_weighment += safe_num(e.de_weighmentcost)
            buying_aai += safe_num(e.de_supervisorcost)
            buying_parking += safe_num(e.de_parkingcost)
            buying_rto += safe_num(e.de_rtocost)
            buying_batta += safe_num(e.de_battacost)

            exp_type_str = str(e.de_expense_type).lower() if e.de_expense_type else ""
            cost_val = safe_num(e.de_total_cost)

            if "toll" in exp_type_str:
                if not e.de_rtocost: buying_toll += cost_val
            elif "halting" in exp_type_str:
                buying_halting += cost_val
            elif "handling" in exp_type_str or "supervisor" in exp_type_str:
                if not e.de_supervisorcost: buying_handling += cost_val
            elif "parking" in exp_type_str:
                if not e.de_parkingcost: buying_parking += cost_val
            elif "loading" in exp_type_str:
                if not e.de_loadingcost: buying_loading += cost_val
            elif "unloading" in exp_type_str:
                if not e.de_unloadingcost: buying_unloading += cost_val
            elif "weighment" in exp_type_str:
                if not e.de_weighmentcost: buying_weighment += cost_val
            elif "bata" in exp_type_str or "batta" in exp_type_str:
                if not e.de_battacost: buying_batta += cost_val

        total_buying = (
                buying_trip_cost + buying_loading + buying_unloading +
                buying_weighment + buying_toll + buying_halting +
                buying_handling + buying_parking + buying_rto + buying_batta
        )

        profit = total_selling - total_buying
        profit_pct_selling = (profit / total_selling * 100) if total_selling > 0 else 0
        profit_pct_buying = (profit / total_buying * 100) if total_buying > 0 else 0

        date_val = (lambda: (next((d for d in [
            trip.tr_departeddate_pickup, trip.tr_departeddate, trip.tr_loading_time,
            trip.tr_reporteddate, trip.tr_reporteddate_pickup, trip.tr_reporteddate_delivery,
            trip.tr_unloading_time, trip.tr_dock_in_time, trip.tr_dock_out_time, trip.tr_created_at
        ] if d), None)))()
        date_str = date_val.strftime("%d-%m-%Y") if date_val else ""

        b_no = bill_no_map.get(trip.id)
        if not b_no:
            b_no = bill_no_map.get(trip.tr_tripnumber)
            if not b_no and trip.tr_consignmentnumber:
                b_no = bill_no_map.get(trip.tr_consignmentnumber.co_consignmentnumber)
        b_no = b_no or ""

        row = [
            start + len(data) + 1,
            date_str,
            safe_str(trip.tr_consignmentnumber),
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_str(trip.tr_enquirynumber.en_customername),
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype_placed or trip.tr_vehicletype),
            selling_trip,
            selling_toll,
            selling_aai,
            selling_loading,
            selling_unloading,
            selling_weighment,
            selling_halting,
            selling_handling,
            total_selling,
            vendor_name,
            b_no,
            buying_trip_cost,
            buying_toll,
            buying_parking,
            buying_loading,
            buying_unloading,
            buying_weighment,
            buying_handling,
            buying_halting,
            buying_rto,
            buying_batta,
            total_buying,
            round(profit, 2),
            f"{round(profit_pct_selling, 2)}%",
        ]
        data.append(row)

    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data
    })


@login_required(login_url='login_page')
def get_vehicles_by_vendor(request):
    from ..models import Vehicle_allotmentInfo
    vendor_id = request.GET.get('vendor_id', '').strip()

    if not vendor_id:
        return JsonResponse([], safe=False)

    # Primary source: Vehicle_allotmentInfo links vendors to vehicle numbers
    va_qs = Vehicle_allotmentInfo.objects.filter(
        va_vendor_id=vendor_id,
        va_vehiclenumber__isnull=False
    ).select_related('va_vehiclenumber').values_list(
        'va_vehiclenumber__vm_registrationnumber', flat=True
    ).distinct()

    vehicle_list = sorted(set(
        v for v in va_qs
        if v and v.strip() and v.strip().lower() != 'null'
    ))

    # Fallback: also check VehiclemasterInfo.vm_vendor if nothing found above
    if not vehicle_list:
        vm_qs = VehiclemasterInfo.objects.filter(
            vm_vendor_id=vendor_id
        ).exclude(
            vm_registrationnumber__isnull=True
        ).exclude(
            vm_registrationnumber=""
        ).exclude(
            vm_registrationnumber="Null"
        ).values_list('vm_registrationnumber', flat=True).distinct()
        vehicle_list = sorted(set(vm_qs))

    return JsonResponse(vehicle_list, safe=False)


@login_required(login_url='login_page')
def whatsapp_delivery_status_report_view(request):
    first_name = request.session.get('first_name')

    if request.method == "POST":
        form = DmrForm(request.POST)
        customer_id = request.POST.get('dmr_customer')
        dept_id = request.POST.get('customer_department')
        selected_month = request.POST.get('month')
        selected_year = request.POST.get('year')
        from_loc_id = request.POST.get('from_location')
        to_loc_id = request.POST.get('to_location')
        branch_id = request.POST.get('branch')
        vehicle_source_id = request.POST.get('vehicle_source')
        vehicle_search = request.POST.get('vehicle_search', '').strip()
    else:
        form = DmrForm()
        customer_id = None
        dept_id = None
        selected_month = '0'
        selected_year = str(datetime.now().year)
        from_loc_id = None
        to_loc_id = None
        branch_id = None
        vehicle_source_id = None
        vehicle_search = ""

    # ------------------------------------------------
    # BASE QUERY - Remove tr_category_id=1 to show all trips
    # ------------------------------------------------
    trips = TripdetailInfo.objects.all().select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_enquirynumber__en_customerdepartment',
        'tr_consignmentnumber',
        'tr_vehicletype',
        'tr_departedlocation',
        'tr_reportedlocation',
        'tr_vehiclesource'
    )

    if vehicle_search:
        trips = trips.filter(tr_vehiclenumber__icontains=vehicle_search)

    # ------------------------------------------------
    # FILTERS
    # ------------------------------------------------
    if customer_id:
        trips = trips.filter(tr_enquirynumber__en_customername_id=customer_id)

    if dept_id:
        trips = trips.filter(tr_enquirynumber__en_customerdepartment_id=dept_id)

    if selected_month and selected_month != '0':
        trips = trips.filter(
            Q(tr_loading_time__month=selected_month) |
            Q(tr_departeddate__month=selected_month) |
            Q(tr_departeddate_pickup__month=selected_month) |
            Q(tr_reporteddate__month=selected_month) |
            Q(tr_unloading_time__month=selected_month) |
            Q(tr_created_at__month=selected_month)
        )

    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) |
            Q(tr_departeddate__year=selected_year) |
            Q(tr_departeddate_pickup__year=selected_year) |
            Q(tr_reporteddate__year=selected_year) |
            Q(tr_unloading_time__year=selected_year) |
            Q(tr_created_at__year=selected_year)
        )

    if from_loc_id:
        trips = trips.filter(tr_departedlocation_id=from_loc_id)

    if to_loc_id:
        trips = trips.filter(tr_reportedlocation_id=to_loc_id)

    if branch_id:
        try:
            b_id = int(branch_id)
            if b_id == 1:  # BLR
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='BLR')
            elif b_id == 2:  # MAA
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='MAA')
        except (ValueError, TypeError):
            pass

    if vehicle_source_id:
        trips = trips.filter(tr_vehiclesource_id=vehicle_source_id)

    trips = trips.order_by('-tr_created_at')

    select_all = request.POST.get('select_all') or request.GET.get('select_all')

    # Performance Optimization: Limit results
    if select_all == 'true':
        trips = trips[:2000]  # Safe upper limit
    else:
        # Default view or filtered view: reasonable limit for fast load
        if not (vehicle_search or customer_id or dept_id or (
                selected_month and selected_month != '0') or branch_id or vehicle_source_id):
            trips = trips[:150]  # Very fast initial load
        else:
            trips = trips[:1000]  # Fast filtered load

    # ------------------------------------------------
    # BUILD REPORT (NO PAGINATION)
    # ------------------------------------------------
    data_rows = []

    for idx, trip in enumerate(trips, start=1):

        customer_name = safe_str(trip.tr_enquirynumber.en_customername)
        department = safe_str(trip.tr_enquirynumber.en_customerdepartment)
        cnote_no = safe_str(trip.tr_consignmentnumber)

        cust_name = customer_name.strip().upper()
        branch_name = (
            "Chennai" if cust_name.endswith("MAA")
            else "Bangalore" if cust_name.endswith("BLR")
            else ""
        )

        # Filter-aware date selection logic
        dates = [
            trip.tr_loading_time, trip.tr_departeddate, trip.tr_departeddate_pickup,
            trip.tr_departeddate_delivery, trip.tr_reporteddate, trip.tr_reporteddate_pickup,
            trip.tr_reporteddate_delivery, trip.tr_unloading_time, trip.tr_dock_in_time,
            trip.tr_dock_out_time, trip.tr_created_at
        ]
        target_month = int(selected_month) if selected_month and selected_month != '0' else None
        target_year = int(selected_year) if selected_year and selected_year != '0' else None

        trip_date = None
        for d in dates:
            if d:
                month_match = (not target_month or d.month == target_month)
                year_match = (not target_year or d.year == target_year)
                if month_match and year_match:
                    trip_date = d
                    break
        if not trip_date:
            trip_date = next((d for d in dates if d), None)

        consignment_date = (
            trip.tr_consignmentnumber.co_consignmentdate.strftime("%d-%m-%Y")
            if trip.tr_consignmentnumber and trip.tr_consignmentnumber.co_consignmentdate
            else (trip_date.strftime("%d-%m-%Y") if trip_date else "")
        )

        row = [
            idx,
            branch_name,
            customer_name,
            department,
            cnote_no,
            consignment_date,
            safe_str(trip.tr_tripnumber),
            safe_str(trip.tr_vehicletype_placed or trip.tr_vehicletype),
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_str(trip.tr_vehiclenumber),
            trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else "",
            trip.tr_reporteddate.strftime("%d-%m-%Y") if trip.tr_reporteddate else "",
            safe_str(trip.tr_drivername),
            "",  # Whatsapp Delivered time
            "",  # Delivered Status
        ]
        data_rows.append(row)

    from ..models import OwnershipInfo, Location_info, VehiclemasterInfo
    return render(request, "asset_mgt_app/whatsapp_delivery_status_report.html", {
        'first_name': first_name,
        'form': form,
        'headers': WHATSAPP_DELIVERY_STATUS_HEADERS,
        'data_rows': data_rows,
        'customer_id': int(customer_id) if customer_id else None,
        'dept_id': int(dept_id) if dept_id else None,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'selected_branch': int(branch_id) if branch_id else None,
        'selected_source': int(vehicle_source_id) if vehicle_source_id else None,
        'vehicle_search': vehicle_search,
        'all_vehicles': VehiclemasterInfo.objects.filter(vm_ownership_id__in=[1, 2]).order_by('vm_registrationnumber'),
        'all_branches': Location_info.objects.filter(id__in=[1, 2]).order_by('loc_name'),
        'vehicle_sources': OwnershipInfo.objects.filter(id__in=[1, 2]),
        'select_all': select_all,
    })


@login_required(login_url='login_page')
def daily_trip_count_report_view(request):
    first_name = request.session.get('first_name')

    if request.method == "POST":
        form = DmrForm(request.POST)
    else:
        form = DmrForm()

    customer_id = request.POST.get('dmr_customer')
    dept_id = request.POST.get('customer_department')
    selected_month = request.POST.get('month', '0')
    selected_year = request.POST.get('year', '0')
    from_loc_id = request.POST.get('from_location')
    to_loc_id = request.POST.get('to_location')
    branch_id = request.POST.get('branch')
    vehicle_source_id = request.POST.get('vehicle_source')
    vehicle_filter = request.POST.get('vehicle_number')
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')

    trips = TripdetailInfo.objects.filter(
        tr_vehiclesource_id__in=[1, 2],
    ).select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_enquirynumber__en_customerdepartment',
        'tr_vehicletype',
        'tr_departedlocation',
        'tr_reportedlocation',
        'tr_vehiclesource',
        'tr_category',
        'tr_consignmentnumber'
    )

    # ------------------------------------------------
    # FILTERS
    # ------------------------------------------------
    if customer_id:
        trips = trips.filter(tr_enquirynumber__en_customername_id=customer_id)

    if dept_id:
        trips = trips.filter(tr_enquirynumber__en_customerdepartment_id=dept_id)

    if from_date:
        trips = trips.filter(
            Q(tr_loading_time__date__gte=from_date) |
            Q(tr_departeddate__date__gte=from_date) |
            Q(tr_departeddate_pickup__date__gte=from_date) |
            Q(tr_reporteddate__date__gte=from_date) |
            Q(tr_unloading_time__date__gte=from_date) |
            Q(tr_created_at__date__gte=from_date)
        )

    if to_date:
        trips = trips.filter(
            Q(tr_loading_time__date__lte=to_date) |
            Q(tr_departeddate__date__lte=to_date) |
            Q(tr_departeddate_pickup__date__lte=to_date) |
            Q(tr_reporteddate__date__lte=to_date) |
            Q(tr_unloading_time__date__lte=to_date) |
            Q(tr_created_at__date__lte=to_date)
        )

    if selected_month and selected_month != '0':
        trips = trips.filter(
            Q(tr_loading_time__month=selected_month) |
            Q(tr_departeddate__month=selected_month) |
            Q(tr_departeddate_pickup__month=selected_month) |
            Q(tr_reporteddate__month=selected_month) |
            Q(tr_unloading_time__month=selected_month) |
            Q(tr_created_at__month=selected_month)
        )

    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) |
            Q(tr_departeddate__year=selected_year) |
            Q(tr_departeddate_pickup__year=selected_year) |
            Q(tr_reporteddate__year=selected_year) |
            Q(tr_unloading_time__year=selected_year) |
            Q(tr_created_at__year=selected_year)
        )

    if from_loc_id:
        trips = trips.filter(tr_departedlocation_id=from_loc_id)

    if to_loc_id:
        trips = trips.filter(tr_reportedlocation_id=to_loc_id)

    if vehicle_filter:
        trips = trips.filter(tr_vehiclenumber__icontains=vehicle_filter)

    if branch_id:
        try:
            b_id = int(branch_id)
            if b_id == 1:  # BLR
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='BLR')
            elif b_id == 2:  # MAA
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='MAA')
            elif b_id == 3:  # PNY
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='PNY')
            elif b_id == 4:  # HYD
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='HYD')
        except:
            pass

    if vehicle_source_id:
        trips = trips.filter(tr_vehiclesource_id=vehicle_source_id)

    trips = trips.order_by('-tr_created_at')

    # ------------------------------------------------
    # AGGREGATION
    # ------------------------------------------------
    aggregated_data = {}

    for trip in trips:

        # Determine the "Operational Day" for this trip count
        # Priority: Actual Loading -> Enquiry Date (Intended Day) -> Actual Departure -> Creation
        full_date = (
                trip.tr_loading_time or
                (trip.tr_enquirynumber.en_created_at if trip.tr_enquirynumber else None) or
                trip.tr_departeddate or
                trip.tr_created_at
        )

        if not full_date:
            continue
        trip_date = full_date.date() if hasattr(full_date, 'date') else full_date

        date_str = trip_date.strftime("%d-%m-%Y")
        vehicle_no = safe_str(trip.tr_vehiclenumber)

        cust_name = safe_str(trip.tr_enquirynumber.en_customername).upper().strip()

        branch_name = (
            "Chennai" if cust_name.endswith("MAA")
            else "Bangalore" if cust_name.endswith("BLR")
            else ""
        )

        key = (date_str, vehicle_no, branch_name)

        if key not in aggregated_data:
            aggregated_data[key] = {
                'branch': branch_name,
                'date': date_str,
                'vehicle_no': vehicle_no,
                'vehicle_type': safe_str(trip.tr_vehicletype_placed or trip.tr_vehicletype),
                'ownership': safe_str(trip.tr_vehiclesource),
                'active_trips': 0,
                'empty_trips': 0,
                'km_business': 0.0,
                'km_empty': 0.0
            }

        # KM calculation
        km_run = safe_num(trip.tr_reportedkm) - safe_num(trip.tr_departedkm)

        if trip.tr_category_id == 1:
            aggregated_data[key]['active_trips'] += 1
            aggregated_data[key]['km_business'] += km_run
        elif trip.tr_category_id in [2, 3]:
            aggregated_data[key]['empty_trips'] += 1
            aggregated_data[key]['km_empty'] += km_run

    # ------------------------------------------------
    # BUILD TABLE
    # ------------------------------------------------
    data_rows = []

    sorted_keys = sorted(
        aggregated_data.keys(),
        key=lambda x: datetime.strptime(x[0], "%d-%m-%Y"),
        reverse=True
    )

    for idx, key in enumerate(sorted_keys, start=1):
        item = aggregated_data[key]

        row = [
            idx,
            item['branch'],
            item['date'],
            item['vehicle_no'],
            item['vehicle_type'],
            item['active_trips'],
            item['ownership']
        ]

        data_rows.append(row)

    all_vehicles = VehiclemasterInfo.objects.filter(
        vm_ownership_id__in=[1, 2]
    ).order_by('vm_registrationnumber')

    # Pagination for groups (dates)
    paginator = Paginator(data_rows, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    from ..models import OwnershipInfo, Location_info
    return render(request, "asset_mgt_app/daily_trip_count_report.html", {
        'first_name': first_name,
        'form': form,
        'headers': DAILY_TRIP_COUNT_HEADERS,
        'data_rows': page_obj,
        'page_obj': page_obj,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'from_date': from_date,
        'to_date': to_date,
        'vehicle_filter': vehicle_filter,
        'selected_branch': int(branch_id) if branch_id else None,
        'selected_source': int(vehicle_source_id) if vehicle_source_id else None,
        'all_vehicles': all_vehicles,
        'all_branches': Location_info.objects.filter(id__in=[1, 2]).order_by('loc_name'),
        'vehicle_sources': OwnershipInfo.objects.filter(id__in=[1, 2]),
    })


@login_required(login_url='login_page')
def own_vehicle_pl_report_view(request):
    from ..models import (
        TripdetailInfo, Driverexpense, MarketBillInfo, AttachedBillInfo,
        Vehicle_allotmentInfo, VendorratemasterInfo1, TransInvoiceInfo,
        DriverSalaryInfo, DrivermasterInfo
    )
    first_name = request.session.get('first_name')

    # -------------------------------
    # FILTER FORM (GET)
    # -------------------------------
    form = DmrForm(request.GET or None)

    vehicle_number = request.GET.get('vehicle_search')
    branch_id = request.GET.get('branch', '').strip()
    vehicletype_id = request.GET.get('vehicletype', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    # -------------------------------
    # BASE QUERY – OWN VEHICLES ONLY
    # -------------------------------
    trips = TripdetailInfo.objects.filter(
        tr_vehiclesource_id=1,  # BVM - OWN only
    ).filter(
        Q(tr_category_id=1, tc_financestatus_id__in=[7, 9]) |
        Q(tr_category_id__in=[2, 3])
    ).select_related(
        'tr_vehicletype',
        'tr_category',
        'tr_departedlocation',
        'tr_reportedlocation',
        'tr_enquirynumber__en_customername',
        'tr_consignmentnumber'
    )

    # -------------------------------
    # FILTERS
    # -------------------------------
    if branch_id:
        if branch_id == '1':  # BLR
            trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='BLR')
        elif branch_id == '2':  # MAA
            trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='MAA')

    if vehicle_number:
        trips = trips.filter(tr_vehiclenumber__icontains=vehicle_number)

    if vehicletype_id:
        trips = trips.filter(tr_vehicletype_id=vehicletype_id)

    from django.db.models.functions import Coalesce
    trips = trips.annotate(
        resolved_date=Coalesce('tr_loading_time', 'tr_departeddate', 'tr_created_at')
    )

    if date_from and date_to:
        trips = trips.filter(resolved_date__date__range=[date_from, date_to])
    elif date_from:
        trips = trips.filter(resolved_date__date__gte=date_from)
    elif date_to:
        trips = trips.filter(resolved_date__date__lte=date_to)

    trips_list = list(trips.order_by('-tr_created_at'))
    trip_ids = [t.id for t in trips_list]

    from ..models import TransInvoiceInfo
    invoices = TransInvoiceInfo.objects.filter(ti_trip_id__in=trip_ids)
    invoice_obj_map = {i.ti_trip_id: i for i in invoices}

    # Create mappings to connect string identifiers to internal IDs (Robust matching)
    trip_id_to_pk = {t.id: t.id for t in trips_list}
    trip_num_to_pk = {str(t.tr_tripnumber).strip().upper(): t.id for t in trips_list if t.tr_tripnumber}

    # Collect all possible search strings (IDs and Trip Numbers - including upper for robust matching)
    all_query_ids = [str(t.id) for t in trips_list] + [str(t.tr_tripnumber).strip() for t in trips_list if
                                                       t.tr_tripnumber] + \
                    [str(t.tr_tripnumber).strip().upper() for t in trips_list if t.tr_tripnumber]

    # -------------------------------
    # PRE-CALCULATE PRORATED DRIVER SALARY
    # -------------------------------
    salary_lookup = {}
    driver_month_pairs = set()

    # Cache for name-to-ID resolution to avoid redundant master lookups
    name_id_to_pk = {}

    # -------------------------------
    # PREFETCH EXPENSES
    # -------------------------------
    expenses = (
        Driverexpense.objects
        .filter(trip_number__in=all_query_ids)
        .select_related('de_expense_type')
    )

    expense_map = {}
    for e in expenses:
        t_id = None
        search_key = str(e.trip_number).strip().upper() if e.trip_number else ""

        # 1. Try matching by trip number string (Case-insensitive, stripped)
        if search_key in trip_num_to_pk:
            t_id = trip_num_to_pk[search_key]
        # 2. Try matching by digit ID
        elif search_key.isdigit():
            t_id = int(search_key)

        # Add to map if resolved ID exists in the current trips list
        if t_id and t_id in trip_id_to_pk:
            expense_map.setdefault(t_id, []).append(e)

    # -------------------------------
    # VEHICLE MASTER (FIXED COSTS)
    # -------------------------------
    vehicle_map = {
        v.vm_registrationnumber: v
        for v in VehiclemasterInfo.objects.all()
    }

    # -------------------------------
    # FUEL & SALARY COST PER TRIP (Calculated via helper)
    # -------------------------------
    fuel_lookup, salary_lookup = calculate_own_vehicle_fuel_and_salary(trips_list, date_from=date_from, date_to=date_to)

    # -------------------------------
    # BUILD TABLE
    # -------------------------------
    data_rows = []
    filtered_trips_list = []
    current_idx = 1

    for trip in trips_list:

        # Filter-aware date selection
        dates = [
            trip.tr_loading_time, trip.tr_departeddate, trip.tr_departeddate_pickup,
            trip.tr_departeddate_delivery, trip.tr_reporteddate, trip.tr_reporteddate_pickup,
            trip.tr_reporteddate_delivery, trip.tr_unloading_time, trip.tr_dock_in_time,
            trip.tr_dock_out_time, trip.tr_created_at
        ]
        target_month = None
        target_year = None

        trip_date = None
        for d in dates:
            if d:
                month_match = (not target_month or d.month == target_month)
                year_match = (not target_year or d.year == target_year)
                if month_match and year_match:
                    trip_date = d
                    break
        if not trip_date:
            trip_date = next((d for d in dates if d), None)
        date_val = trip_date.strftime("%d-%m-%Y") if trip_date else ""

        # -------- SELLING (Now respecting Bill to Customer Checkboxes) --------
        # Prioritize Trip Settlement fields (tc_...) if they are non-zero/checked,
        # then fallback to Invoice (ti_...) if available.
        inv = invoice_obj_map.get(trip.id)

        selling_trip = (safe_num(trip.tc_tripcost) if (
                getattr(trip, 'tc_tripcost_check', True) and safe_num(trip.tc_tripcost) > 0) else (
            safe_num(inv.ti_transportation_charges) if inv else 0.0))
        selling_toll = (safe_num(trip.tc_tollcost) if (
                getattr(trip, 'tc_tollcost_check', True) and safe_num(trip.tc_tollcost) > 0) else (
            safe_num(inv.ti_toll_charges) if inv else 0.0))
        selling_parking = (safe_num(trip.tc_parkingcost) if (
                getattr(trip, 'tc_parkingcost_check', True) and safe_num(trip.tc_parkingcost) > 0) else (
            safe_num(inv.ti_parking_charges) if inv else 0.0))
        selling_loading = (safe_num(trip.tc_loadingcost) if (
                getattr(trip, 'tc_loadingcost_check', True) and safe_num(trip.tc_loadingcost) > 0) else (
            safe_num(inv.ti_loading_charges) if inv else 0.0))
        selling_unloading = (safe_num(trip.tc_unloadingcost) if (
                getattr(trip, 'tc_unloadingcost_check', True) and safe_num(trip.tc_unloadingcost) > 0) else (
            safe_num(inv.ti_unloading_charges) if inv else 0.0))
        selling_weighment = (safe_num(trip.tc_weighmentcost) if (
                getattr(trip, 'tc_weighmentcost_check', True) and safe_num(trip.tc_weighmentcost) > 0) else (
            safe_num(inv.ti_weighment_charges) if inv else 0.0))
        selling_handling = (safe_num(trip.tc_handlingcost) if (
                getattr(trip, 'tc_handlingcost_check', True) and safe_num(trip.tc_handlingcost) > 0) else (
            safe_num(inv.ti_handling_charges) if inv else 0.0))

        # Halting Logic
        halting_days = safe_num(trip.tc_no_of_days_halting)
        if getattr(trip, 'tc_total_halting_cost_check', False) and safe_num(trip.tc_total_halting_cost) > 0:
            selling_halting = safe_num(trip.tc_total_halting_cost)
        elif getattr(trip, 'tc_haltingcost_check', False) and safe_num(trip.tc_haltingcost) > 0:
            selling_halting = safe_num(trip.tc_haltingcost) * halting_days
        elif inv:
            selling_halting = safe_num(inv.ti_halting_charges)
        else:
            selling_halting = 0.0

        selling_supervisor = (safe_num(trip.tc_supervisorcost) if (
                getattr(trip, 'tc_supervisorcost_check', True) and safe_num(trip.tc_supervisorcost) > 0) else (
            safe_num(inv.ti_docket_charges) if inv else 0.0))
        selling_rto = (safe_num(trip.tc_rtocost) if getattr(trip, 'tc_rtocost_check', True) else 0.0)
        selling_beta = (safe_num(trip.tc_betacost) if getattr(trip, 'tc_betacost_check', True) else 0.0)
        selling_cancellation = (safe_num(trip.tc_cancellation) if (
                getattr(trip, 'tc_cancellation_check', True) and safe_num(trip.tc_cancellation) > 0) else (
            safe_num(inv.ti_cancellation_charges) if inv else 0.0))

        selling_total = (
                selling_trip + selling_toll + selling_parking + selling_loading +
                selling_unloading + selling_weighment + selling_handling +
                selling_halting + selling_supervisor + selling_rto +
                selling_beta + selling_cancellation
        )

        # -------- EXPENSES --------
        toll_expense = 0.0
        fuel_expense = 0.0

        # Pull Driver Salary from pre-calculated lookup (if available)
        driver_salary = round(salary_lookup.get(trip.id, 0.0), 2)

        acting_driver = 0.0
        driver_bata = 0.0
        parking_expense = 0.0
        loading_expense = 0.0
        unloading_expense = 0.0
        weighment_expense = 0.0
        handling_expense = 0.0
        vehicle_hire = 0.0

        for e in expense_map.get(trip.id, []):
            extype = str(e.de_expense_type).lower()

            # --- 1. Aggregating Dedicated Fields (Robust to Generic "Expense" Types) ---
            parking_val = safe_num(e.de_parkingcost)
            loading_val = safe_num(e.de_loadingcost)
            unloading_val = safe_num(e.de_unloadingcost)
            weighment_val = safe_num(e.de_weighmentcost)
            handling_val = safe_num(e.de_supervisorcost)
            toll_val = safe_num(e.de_rtocost)
            bata_val = safe_num(e.de_battacost)

            parking_expense += parking_val
            loading_expense += loading_val
            unloading_expense += unloading_val
            weighment_expense += weighment_val
            handling_expense += handling_val
            toll_expense += toll_val
            driver_bata += bata_val

            # --- 2. Aggregating Category-Based Bulk Costs (from de_total_cost) ---
            cost = safe_num(e.de_total_cost)

            if 'fuel' in extype or 'diesel' in extype:
                # Fuel cost is always pulled directly from Fuelfillinginfo database to prevent double counting
                pass
            elif 'salary' in extype:
                # If we already have a salary from DriverSalaryInfo, we might want to ignore manual 'salary' expenses
                # or add them? The user said "take value from driver salary page".
                # Usually, this means replace. Let's ONLY add if driver_salary is still 0.
                if driver_salary == 0.0:
                    driver_salary += cost
            elif 'acting' in extype:
                acting_driver += cost
            elif 'hire' in extype or 'freight' in extype:
                vehicle_hire += cost

            # For categories that have dedicated fields, only add de_total_cost if those fields are 0
            # to avoid double-counting in specific category records (e.g., a "Fuel" record vs "General Expense").
            elif 'toll' in extype:
                if not toll_val: toll_expense += cost
            elif 'parking' in extype:
                if not parking_val: parking_expense += cost
            elif 'loading' in extype:
                if not loading_val: loading_expense += cost
            elif 'unloading' in extype:
                if not unloading_val: unloading_expense += cost
            elif 'weighment' in extype:
                if not weighment_val: weighment_expense += cost
            elif 'bata' in extype or 'batta' in extype:
                if not bata_val: driver_bata += cost
            elif 'handling' in extype:
                if not handling_val: handling_expense += cost

        # --- 3. Fuel Cost: prorated from Fuelfillinginfo (pre-calculated above) ---
        fuel_expense = round(fuel_lookup.get(trip.id, 0.0), 2)

        total_expense = (
                driver_salary + fuel_expense + acting_driver + driver_bata +
                toll_expense + parking_expense + loading_expense + unloading_expense +
                weighment_expense + handling_expense + vehicle_hire
        )

        row = [
            current_idx,
            date_val,
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_consignmentnumber),
            safe_str(trip.tr_category),
            safe_str(trip.tr_enquirynumber.en_customername) if trip.tr_enquirynumber else "",
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_num(trip.tc_tripcost),
            safe_num(trip.tc_tollcost),
            safe_num(trip.tc_parkingcost),
            safe_num(trip.tc_loadingcost),
            safe_num(trip.tc_unloadingcost),
            safe_num(trip.tc_weighmentcost),
            safe_num(trip.tc_handlingcost),
            safe_num(trip.tc_haltingcost) * safe_num(trip.tc_no_of_days_halting),

            selling_total,
            driver_salary,
            fuel_expense,
            acting_driver,
            driver_bata,
            toll_expense,
            parking_expense,
            loading_expense,
            unloading_expense,
            weighment_expense,
            handling_expense,
            vehicle_hire,
            total_expense,
        ]

        data_rows.append(row)
        filtered_trips_list.append(trip)
        current_idx += 1

    trips_list = filtered_trips_list

    # -------------------------------
    # SUMMARY AGGREGATION
    # -------------------------------
    total_trips = len(trips_list)
    working_days_set = set()
    total_km = 0.0
    empty_km_val = 0.0
    business_empty_km_val = 0.0
    total_revenue = 0.0
    total_operational_expense = 0.0
    revenue_idx = OWN_VEHICLE_PL_HEADERS.index("Revenue")
    total_expense_idx = OWN_VEHICLE_PL_HEADERS.index("Total Expense")

    # Calculate months for Prorated Fixed Costs
    months_count = 1
    if date_from and date_to:
        try:
            d_from = datetime.strptime(date_from, "%Y-%m-%d")
            d_to = datetime.strptime(date_to, "%Y-%m-%d")
            days_diff = max(1, (d_to - d_from).days)
            months_count = max(1.0, days_diff / 30.0)
        except:
            months_count = 1
    elif date_from or date_to:
        months_count = 1
    else:
        # If no dates restricted, default to 1 for generic visualization
        months_count = 1

    total_days_in_period = int(30 * months_count)

    for trip, row in zip(trips_list, data_rows):
        if trip.tr_departeddate:
            working_days_set.add(trip.tr_departeddate.date())

        km_diff = vehicle_log_used_km(trip)
        total_km += km_diff

        # Category 2 = Empty, Category 3 = Business Empty
        if trip.tr_category_id == 2:
            empty_km_val += km_diff
        elif trip.tr_category_id == 3:
            business_empty_km_val += km_diff

        total_revenue += row[revenue_idx]
        total_operational_expense += row[total_expense_idx]

    num_days_working = len(working_days_set)
    num_idle_days = max(0, total_days_in_period - num_days_working)
    if not vehicle_number and total_trips > 0:
        # Scale idle days by distinct vehicles effectively
        unique_veh_count = len(set(t.tr_vehiclenumber for t in trips_list if t.tr_vehiclenumber))
        num_idle_days = max(0, (total_days_in_period * unique_veh_count) - num_days_working)

    insurance = 0.0
    road_tax = 0.0
    permit = 0.0
    maintenance_cost = 0.0

    summary_vehicle_no = vehicle_number if vehicle_number else "All Vehicles"
    summary_vehicle_type = "Mixed"

    # Needs Maintenance Bill info
    from ..sub_models.maintenance_bill_mod import MaintenanceBillInfo

    if vehicle_number:
        if trips_list:
            summary_vehicle_type = safe_str(trips_list[0].tr_vehicletype)
        v_obj = vehicle_map.get(vehicle_number)
        if v_obj:
            insurance = safe_num(v_obj.vm_premium) / 12.0 * months_count
            road_tax = safe_num(v_obj.vm_roadtaxamount) / 12.0 * months_count
            permit = safe_num(v_obj.vm_permitamount) / 12.0 * months_count

        m_bills = MaintenanceBillInfo.objects.filter(mnb_maintenance__mi_vehicle__vm_registrationnumber=vehicle_number)
        if date_from: m_bills = m_bills.filter(mnb_bill_date__gte=date_from)
        if date_to: m_bills = m_bills.filter(mnb_bill_date__lte=date_to)
        for mb in m_bills:
            maintenance_cost += safe_num(mb.mnb_total_amount)
    else:
        unique_veh_nos = set(trip.tr_vehiclenumber for trip in trips_list if trip.tr_vehiclenumber)
        for vno in unique_veh_nos:
            v_obj = vehicle_map.get(vno)
            if v_obj:
                insurance += safe_num(v_obj.vm_premium) / 12.0 * months_count
                road_tax += safe_num(v_obj.vm_roadtaxamount) / 12.0 * months_count
                permit += safe_num(v_obj.vm_permitamount) / 12.0 * months_count

        m_bills = MaintenanceBillInfo.objects.filter(
            mnb_maintenance__mi_vehicle__vm_registrationnumber__in=unique_veh_nos)
        if date_from: m_bills = m_bills.filter(mnb_bill_date__gte=date_from)
        if date_to: m_bills = m_bills.filter(mnb_bill_date__lte=date_to)
        for mb in m_bills:
            maintenance_cost += safe_num(mb.mnb_total_amount)

    total_fixed_expenses = insurance + road_tax + permit + maintenance_cost
    base_expenses = total_operational_expense + total_fixed_expenses

    empty_km_cost = 0.0
    business_empty_km_cost = 0.0
    if total_km > 0:
        cost_per_km = base_expenses / total_km
        empty_km_cost = empty_km_val * cost_per_km
        business_empty_km_cost = business_empty_km_val * cost_per_km

    total_expenses_all = base_expenses + empty_km_cost + business_empty_km_cost

    profit = total_revenue - total_expenses_all
    profit_pct = (profit / total_revenue * 100) if total_revenue > 0 else 0

    def format_dmy(d_str):
        if not d_str: return ""
        try:
            return datetime.strptime(d_str, "%Y-%m-%d").strftime("%d-%m-%Y")
        except:
            return d_str

    month_str = "All Time"
    df_f = format_dmy(date_from)
    dt_f = format_dmy(date_to)
    if df_f and dt_f:
        month_str = f"{df_f} to {dt_f}"
    elif df_f:
        month_str = f"From {df_f}"
    elif dt_f:
        month_str = f"Up to {dt_f}"

    summary_data = {
        'month': month_str,
        'vehicle_no': summary_vehicle_no,
        'vehicle_type': summary_vehicle_type,
        'days_working': num_days_working,
        'idle_days': num_idle_days,
        'total_trips': total_trips,
        'trip_index': round(total_trips / max(1, num_days_working), 2),
        'total_km': round(total_km, 2),
        'empty_km': round(empty_km_val, 2),
        'business_empty_km': round(business_empty_km_val, 2),
        'revenue': round(total_revenue, 2),
        'operational_expenses': round(total_operational_expense, 2),
        'maintenance_cost': round(maintenance_cost, 2),
        'insurance': round(insurance, 2),
        'road_tax': round(road_tax, 2),
        'permit': round(permit, 2),
        'empty_km_cost': round(empty_km_cost, 2),
        'business_empty_km_cost': round(business_empty_km_cost, 2),
        'total_expenses': round(total_expenses_all, 2),
        'profit': round(profit, 2),
        'profit_pct': round(profit_pct, 2),
    }

    # -------------------------------
    # CONTEXT
    # -------------------------------
    context = {
        'first_name': first_name,
        'form': form,
        'headers': OWN_VEHICLE_PL_HEADERS,
        'data_rows': data_rows,
        'summary_data': summary_data,
        'date_from': date_from,
        'date_to': date_to,
        'branch_id': branch_id,
        'vehicletype_id': vehicletype_id,
        'vehicle_number': vehicle_number,
        'all_vehicles': VehiclemasterInfo.objects.filter(vm_ownership_id=1),
        'all_branches': [
            {'id': b.id, 'name': b.loc_name.replace('BVM ', '').strip()}
            for b in Location_info.objects.filter(id__in=[1, 2]).order_by('loc_name')
        ],
        'all_vehicletypes': VehicletypeInfo.objects.all(),
    }

    return render(request, "asset_mgt_app/own_vehicle_pl_report.html", context)


@login_required(login_url='login_page')
def claim_pending_report_view(request):
    first_name = request.session.get('first_name')

    # Fetch all vehicles present in TransCustomerClaimsInfo for the dropdown
    claim_vehicles = TransCustomerClaimsInfo.objects.values_list('tcc_veh_no', flat=True).distinct().order_by(
        'tcc_veh_no')
    claim_vehicles = [v for v in claim_vehicles if v]

    # Initialize Filter Form
    if request.method == "POST":
        form = DmrForm(request.POST)
    else:
        form = DmrForm()

    # Get Filter Parameters
    vehicle_no = request.POST.get('vehicle_number')
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')

    # Base Query: Fetch All Claims from TransCustomerClaimsInfo
    claims = TransCustomerClaimsInfo.objects.all().select_related(
        'tcc_cnote',
        'tcc_cnote__co_customer',
        'tcc_cnote__co_enquirynumber',
        'tcc_cnote__co_enquirynumber__en_customerdepartment',
        'tcc_current_status',
        'tcc_mgmt_approval'
    )

    if vehicle_no:
        claims = claims.filter(tcc_veh_no=vehicle_no)

    if from_date:
        claims = claims.filter(tcc_trip_date__gte=from_date)

    if to_date:
        claims = claims.filter(tcc_trip_date__lte=to_date)

    claims = claims.order_by('-tcc_updated_on')

    # Pagination
    paginator = Paginator(claims, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Fetch related Trips for the current page
    cnote_ids = [c.tcc_cnote_id for c in page_obj if c.tcc_cnote_id]
    trips_by_cnote = TripdetailInfo.objects.filter(tr_consignmentnumber_id__in=cnote_ids).select_related(
        'tr_vehicletype', 'tr_departedlocation', 'tr_reportedlocation'
    )
    trip_map = {t.tr_consignmentnumber_id: t for t in trips_by_cnote}

    data_rows = []

    for idx, claim in enumerate(page_obj, start=(page_obj.start_index() if hasattr(page_obj, 'start_index') else 1)):
        # Look up trip details
        trip = trip_map.get(claim.tcc_cnote_id)

        trip_code = "N/A"
        trip_date = claim.tcc_trip_date.strftime("%d-%m-%Y") if claim.tcc_trip_date else ""
        truck_no = safe_str(claim.tcc_veh_no)
        veh_type = safe_str(claim.tcc_veh_type)
        loc_from = safe_str(claim.tcc_from)
        loc_to = safe_str(claim.tcc_to)
        driver = safe_str(claim.tcc_driver_name)
        department = ""
        cnote = ""
        cust_name_str = "N/A"

        if trip:
            trip_code = safe_str(trip.tr_tripnumber)

        if claim.tcc_cnote:
            cnote = safe_str(claim.tcc_cnote.co_consignmentnumber)
            if claim.tcc_cnote.co_enquirynumber:
                department = safe_str(claim.tcc_cnote.co_enquirynumber.en_customerdepartment)
            cust_name_str = safe_str(claim.tcc_cnote.co_customer)

        cust_name_upper = cust_name_str.strip().upper()
        branch = "Chennai" if cust_name_upper.endswith("MAA") else (
            "Bangalore" if cust_name_upper.endswith("BLR") else "")

        capa_issue_date = claim.tcc_capa_issued_date.strftime("%d-%m-%Y") if claim.tcc_capa_issued_date else ""
        capa_closed_date = claim.tcc_capa_closed_date.strftime("%d-%m-%Y") if claim.tcc_capa_closed_date else ""
        status_name = safe_str(claim.tcc_current_status.status_title) if claim.tcc_current_status else ""

        row = [
            idx,
            cnote,
            trip_date,
            loc_from,
            loc_to,
            truck_no,
            driver,
            safe_str(claim.tcc_shipper_ref_no),
            safe_str(claim.tcc_damage_remarks),
            safe_str(claim.tcc_reason_for_claim),
            safe_num(claim.tcc_claim_amount),
            capa_issue_date,
            capa_closed_date,
            status_name
        ]
        data_rows.append(row)

    context = {
        'first_name': first_name,
        'form': form,
        'headers': CLAIM_PENDING_HEADERS,
        'data_rows': data_rows,
        'page_obj': page_obj,
        'vehicle_no': vehicle_no,
        'all_vehicles': claim_vehicles,
        'from_date': from_date,
        'to_date': to_date,
    }

    return render(request, "asset_mgt_app/claim_pending_report.html", context)


@login_required(login_url='login_page')
def halting_report_view(request):
    first_name = request.session.get('first_name')
    from ..models import Location_info, OwnershipInfo
    from ..sub_forms.dmr_report_form import DmrForm
    from datetime import datetime

    if request.method == "POST":
        form = DmrForm(request.POST)
        selected_month = request.POST.get('month', '0')
        selected_year = request.POST.get('year', str(datetime.now().year))
        branch_id = request.POST.get('branch')
        vehicle_source_id = request.POST.get('vehicle_source')
    else:
        form = DmrForm()
        selected_month = '0'
        selected_year = str(datetime.now().year)
        branch_id = None
        vehicle_source_id = None

    context = {
        'first_name': first_name,
        'form': form,
        'headers': HALTING_REPORT_HEADERS,
        'data_rows': [],  # AJAX populated
        'selected_month': selected_month,
        'selected_year': selected_year,
        'selected_branch': int(branch_id) if branch_id else None,
        'selected_source': int(vehicle_source_id) if vehicle_source_id else None,
        'all_branches': [
            {'id': b.id, 'name': b.loc_name.replace('BVM ', '').strip()}
            for b in Location_info.objects.filter(id__in=[1, 2]).order_by('loc_name')
        ],
        'vehicle_sources': OwnershipInfo.objects.all(),
    }
    return render(request, "asset_mgt_app/halting_report.html", context)


def halting_report_ajax_view(request):
    from django.http import JsonResponse
    from ..models import TripdetailInfo, Driverexpense, ConsignmentgoodsInfo

    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))

    customer_id = request.GET.get('customer')
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')
    branch_id = request.GET.get('branch')
    vehicle_source_id = request.GET.get('vehicle_source')

    trips = get_filtered_trips(branch_id, None, vehicle_source_id, None, None, selected_year, customer_id=customer_id,
                               selected_month=selected_month)
    trips = trips.filter(tr_category_id=1)  # Business trips only
    records_total = trips.count()

    search_value = request.GET.get('search[value]', '').strip()
    if search_value:
        trips = trips.filter(
            Q(tr_vehiclenumber__icontains=search_value) |
            Q(tr_consignmentnumber__co_consignmentnumber__icontains=search_value) |
            Q(tr_enquirynumber__en_customername__cu_name__icontains=search_value)
        )

    records_filtered = trips.count()

    if length == -1:
        page_trips = list(trips[start:])
    else:
        page_trips = list(trips[start:start + length])

    # --- PRE-FETCH Logic ---
    trip_id_to_pk = {t.id: t.id for t in page_trips}
    trip_num_to_pk = {str(t.tr_tripnumber).strip().upper(): t.id for t in page_trips if t.tr_tripnumber}
    all_query_ids = [str(t.id) for t in page_trips] + [str(t.tr_tripnumber).strip() for t in page_trips if
                                                       t.tr_tripnumber]

    expenses = Driverexpense.objects.filter(trip_number__in=all_query_ids).select_related('de_expense_type').only(
        'trip_number', 'de_expense_type__expense_type', 'de_total_cost'
    )
    expense_map = {}
    for e in expenses:
        t_id = None
        s_key = str(e.trip_number).strip().upper() if e.trip_number else ""
        if s_key in trip_num_to_pk:
            t_id = trip_num_to_pk[s_key]
        elif s_key.isdigit():
            try:
                t_id = int(s_key)
            except:
                pass
        if t_id and t_id in trip_id_to_pk:
            if e.de_expense_type and 'halting' in str(e.de_expense_type).lower():
                expense_map[t_id] = expense_map.get(t_id, 0.0) + safe_num(e.de_total_cost)

    consignment_ids = [t.tr_consignmentnumber.id for t in page_trips if t.tr_consignmentnumber]
    goods = ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber_id__in=consignment_ids).select_related(
        'cg_consigner', 'cg_consignee'
    ).only('cg_consignmentnumber_id', 'cg_consigner__consigner_name', 'cg_consignee__consignee_name')

    goods_map = {}
    for g in goods:
        cid = g.cg_consignmentnumber_id
        m = goods_map.setdefault(cid, {"consignors": set(), "consignees": set()})
        if g.cg_consigner: m["consignors"].add(str(g.cg_consigner).strip())
        if g.cg_consignee: m["consignees"].add(str(g.cg_consignee).strip())

    data_rows = []
    for idx, trip in enumerate(page_trips, start=start + 1):
        # Optimized Logic
        dates = [
            trip.tr_loading_time, trip.tr_departeddate, trip.tr_departeddate_pickup,
            trip.tr_departeddate_delivery, trip.tr_reporteddate, trip.tr_reporteddate_pickup,
            trip.tr_reporteddate_delivery, trip.tr_unloading_time, trip.tr_dock_in_time,
            trip.tr_dock_out_time, trip.tr_created_at
        ]
        target_month = int(selected_month) if selected_month and selected_month != '0' else None
        target_year = int(selected_year) if selected_year and selected_year != '0' else None

        trip_date = None
        for d in dates:
            if d:
                month_match = (not target_month or d.month == target_month)
                year_match = (not target_year or d.year == target_year)
                if month_match and year_match:
                    trip_date = d
                    break
        if not trip_date: trip_date = next((d for d in dates if d), None)
        date_val = _fmt_dt(trip_date, date_only=True)

        consignor = ""
        consignee = ""
        if trip.tr_consignmentnumber:
            if trip.tr_consignmentnumber.id in goods_map:
                m = goods_map[trip.tr_consignmentnumber.id]
                consignor = ", ".join(sorted(list(m["consignors"])))
                consignee = ", ".join(sorted(list(m["consignees"])))
            if not consignor and trip.tr_enquirynumber: consignor = safe_str(trip.tr_enquirynumber.en_fromlocaion)
            if not consignee and trip.tr_enquirynumber: consignee = safe_str(trip.tr_enquirynumber.en_tolocation)

        cust_name = safe_str(trip.tr_enquirynumber.en_customername).strip().upper()
        branch = "Chennai" if cust_name.endswith("MAA") else ("Bangalore" if cust_name.endswith("BLR") else "")

        veh_reported_loading = trip.tr_departeddate_pickup
        veh_started_unloading = trip.tr_reporteddate_pickup
        time_taken = _duration_str(veh_reported_loading, veh_started_unloading)

        halting_days = int(safe_num(trip.tc_no_of_days_halting))
        selling_halting = 0
        if trip.tc_haltingcost_check or trip.tc_total_halting_cost_check:
            selling_halting = safe_num(trip.tc_haltingcost) * halting_days

        data_rows.append([
            idx, branch, date_val, safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype_placed or trip.tr_vehicletype),
            safe_str(trip.tr_enquirynumber.en_customername), safe_str(trip.tr_enquirynumber.en_customerdepartment),
            consignor, consignee,
            safe_str(trip.tr_consignmentnumber.co_consignmentnumber) if trip.tr_consignmentnumber else "",
            _fmt_dt(veh_reported_loading),
            _fmt_dt(veh_started_unloading),
            time_taken, halting_days, selling_halting, safe_str(trip.tr_remarks)
        ])

    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data_rows,
    })


@login_required(login_url='login_page')
def maintenance_report_view(request):
    first_name = request.session.get('first_name')
    from ..models import MaintenanceInfo, VehiclemasterInfo
    from ..sub_models.branch_mod import Branch
    from datetime import datetime

    if request.method == "POST":
        form = DmrForm(request.POST)
        vehicle_search = request.POST.get('vehicle_search', '')
        from_date = request.POST.get('from_date', '')
        to_date = request.POST.get('to_date', '')
        branch_id = request.POST.get('branch', '')
    else:
        form = DmrForm()
        vehicle_search = ""
        from_date = ""
        to_date = ""

        branch_id = ""

    # Base Query
    maintenance_records = MaintenanceInfo.objects.filter(
        mi_vehicle__vm_ownership_id__in=[1],
        bills_v1__isnull=False
    ).select_related(
        'mi_vehicle', 'mi_vehicle__vm_vehicletype', 'mi_vehicle__vm_vehiclemanufacturer', 'mi_vehicle__vm_vendor'
    ).prefetch_related('bills_v1').distinct().order_by('mi_vehicle__vm_registrationnumber', '-mi_created_at')

    # Filters
    if vehicle_search:
        maintenance_records = maintenance_records.filter(mi_vehicle__vm_registrationnumber__icontains=vehicle_search)

    if from_date:
        maintenance_records = maintenance_records.filter(mi_created_at__date__gte=from_date)
    if to_date:
        maintenance_records = maintenance_records.filter(mi_created_at__date__lte=to_date)
    if branch_id:
        maintenance_records = maintenance_records.filter(mi_location_id=branch_id)
    #
    #     if selected_month and selected_month != '0':
    #         maintenance_records = maintenance_records.filter(created_at__month=selected_month)
    #
    #     if selected_year and selected_year != '0':
    #         maintenance_records = maintenance_records.filter(created_at__year=selected_year)
    #
    #     # We need to process records to find "Previous Job Card" info.
    #     # Since we ordered by vehicle and desc created_at, the "next" record in the list
    #     # for the SAME vehicle is the previous job card.

    records_list = list(maintenance_records)
    processed_rows = []

    # Helper to find previous record
    # We can pre-group by vehicle to make this faster
    vehicle_groups = {}
    for rec in records_list:
        v_id = rec.mi_vehicle_id
        if v_id not in vehicle_groups:
            vehicle_groups[v_id] = []
        vehicle_groups[v_id].append(rec)

    # Now build rows
    counter = 1

    # We want to show the filtered range.
    for rec in records_list:
        # Find previous in the group
        group = vehicle_groups.get(rec.mi_vehicle_id, [])
        # group is ordered desc by created_at. rec is in group.
        # Find index of rec
        try:
            curr_idx = group.index(rec)
            prev_rec = group[curr_idx + 1] if curr_idx + 1 < len(group) else None
        except ValueError:
            prev_rec = None

        # Safely access vehicle fields
        try:
            vehicle_no = safe_str(rec.mi_vehicle.vm_registrationnumber) if rec.mi_vehicle else ""
            vehicle_type = safe_str(
                rec.mi_vehicle.vm_vehicletype) if rec.mi_vehicle and rec.mi_vehicle.vm_vehicletype else ""
        except:
            vehicle_no = ""
            vehicle_type = ""

        make = safe_str(rec.mi_make_model)

        branch_display = ""
        if rec.mi_location:
            branch_display = str(rec.mi_location.branch)

        job_card_no = rec.id  # fallback
        prev_job_card_date = _fmt_dt(prev_rec.mi_created_at, date_only=True) if prev_rec else ""
        prev_job_card_no = prev_rec.id if prev_rec else ""

        bills = rec.bills_v1.all()
        bill_nos = ", ".join([b.mnb_bill_no for b in bills if b.mnb_bill_no])
        actual_amount = sum([safe_num(b.mnb_total_amount) for b in bills])

        row = [
            counter,
            branch_display,
            _fmt_dt(rec.mi_created_at, date_only=True),  # Date
            vehicle_no,  # Vehicle No
            vehicle_type,  # Vehicle Type
            safe_str(rec.mi_service_type),  # Service Type
            rec.mi_total_km_run,  # KM
            safe_num(rec.mi_estimated_amount),  # PO Amount
            safe_num(actual_amount),  # Actual Amount
            safe_str(rec.mi_technician),  # Vendor Name logic
            safe_str(rec.mi_job_card_no),  # JC No
            bill_nos  # Bill No
        ]
        processed_rows.append(row)
        counter += 1

    data_rows = processed_rows
    all_vehicles = VehiclemasterInfo.objects.filter(vm_ownership_id=1).order_by('vm_registrationnumber')
    all_branches = Branch.objects.all().order_by('branch')

    context = {
        'first_name': first_name,
        'form': form,
        'headers': MAINTENANCE_REPORT_HEADERS,
        'data_rows': data_rows,
        'vehicle_search': vehicle_search,
        'from_date': from_date,
        'to_date': to_date,
        'selected_branch_id': branch_id,
        'all_vehicles': all_vehicles,
        'all_branches': all_branches,
    }

    return render(request, "asset_mgt_app/maintenance_report.html", context)


from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Upper, Trim

from ..models import Insurance_Info, VehiclemasterInfo, Location_info


@login_required(login_url='login_page')
def insurance_renewal_report_view(request):
    first_name = request.session.get('first_name')

    # -------------------------
    # READ FILTER (POST only – matches HTML)
    # -------------------------
    vehicle_search = request.POST.get('vehicle_search', '').strip()
    branch_search = request.POST.get('branch_search', '').strip()
    company_search = request.POST.get('company_search', '').strip()

    # -------------------------
    # BASE QUERY (normalize vehicle no)
    # -------------------------
    insurance_records = (
        Insurance_Info.objects
        .filter(ins_status_id=1)
        .select_related('ins_branch', 'ins_vendor', 'ins_type')
        .annotate(
            veh_no_clean=Upper(Trim('ins_vehicle_no'))
        )
        .order_by('ins_expiry_date')
    )

    # -------------------------
    # FILTERS
    # -------------------------
    if vehicle_search:
        insurance_records = insurance_records.filter(
            veh_no_clean=vehicle_search.strip().upper()
        )

    if branch_search:
        insurance_records = insurance_records.filter(ins_branch_id=branch_search)

    if company_search:
        insurance_records = insurance_records.filter(ins_name__icontains=company_search)

    import re
    def normalize_veh(v):
        if not v: return ""
        return re.sub(r'[^A-Z0-9]', '', str(v).upper())

    # -------------------------
    # VEHICLE MASTER (for dropdown + type lookup)
    # -------------------------
    vehicles = (
        VehiclemasterInfo.objects
        .select_related('vm_vehicletype')
        .order_by('vm_registrationnumber')
    )

    vehicle_map = {
        normalize_veh(v.vm_registrationnumber): v
        for v in vehicles
    }

    # -------------------------
    # PROCESS ROWS
    # -------------------------
    today = datetime.now().date()
    processed_rows = []
    counter = 1

    for rec in insurance_records:
        v_raw = str(rec.ins_vehicle_no).upper()
        v_clean = normalize_veh(v_raw)

        # Priority 1: Exact cleaned match
        vehicle = vehicle_map.get(v_clean)

        # Priority 2: Fuzzy match (any master reg is a part of this string)
        if not vehicle and v_clean:
            # Sort keys by length descending to match the longest (most specific) sub-string first
            sorted_mk = sorted(vehicle_map.keys(), key=len, reverse=True)
            for mk in sorted_mk:
                if mk and (mk in v_clean):
                    vehicle = vehicle_map[mk]
                    break

        vehicle_type = safe_str(vehicle.vm_vehicletype) if vehicle else ""

        expiry_date = rec.ins_expiry_date
        elapsed_days = (expiry_date - today).days if expiry_date else 0

        # Status logic
        if expiry_date:
            if elapsed_days < 0:
                ds_status = "Expired"
            elif elapsed_days <= 30:
                ds_status = "Renewal Due"
            else:
                ds_status = "Active"
        else:
            ds_status = ""

        # Branch Logic: Priority to Insurance Branch -> Vehicle Branch
        branch_name = safe_str(rec.ins_branch)
        if not branch_name and vehicle and vehicle.vm_branch:
            branch_name = safe_str(vehicle.vm_branch)

        processed_rows.append([
            counter,  # 1 S.No
            branch_name,  # 2 Branch
            safe_str(rec.ins_vendor),  # 3 Vendor
            safe_str(rec.ins_name),  # 4 Insurance Company
            safe_str(rec.ins_vehicle_no),  # 5 Vehicle No
            vehicle_type,  # 6 Vehicle Type
            safe_str(rec.ins_type),  # 7 Insurance Type
            _fmt_dt(expiry_date, date_only=True),  # 8 Renewal Date
            safe_num(rec.ins_premium_amount),  # 9 Premium Amount
            safe_num(rec.ins_sum_assured),  # 10 IDV Value
            elapsed_days,  # 11 Elapsed Days
            ds_status  # 12 Status
        ])

        counter += 1

    # -------------------------
    # CONTEXT (NO paginator – DataTables handles it)
    # -------------------------
    context = {
        'first_name': first_name,
        'headers': INSURANCE_RENEWAL_HEADERS,
        'data_rows': processed_rows,
        'vehicle_search': vehicle_search,
        'branch_search': int(branch_search) if branch_search else None,
        'company_search': company_search,
        'all_vehicles': vehicles,
        'all_branches': Location_info.objects.filter(id__in=[1, 2]).order_by('loc_name'),
        'all_companies': Insurance_Info.objects.filter(ins_status_id=1).values_list('ins_name',
                                                                                    flat=True).distinct().order_by(
            'ins_name'),
    }

    return render(
        request,
        "asset_mgt_app/insurance_renewal_report.html",
        context
    )


@login_required(login_url='login_page')
def diesel_vs_revenue_report_view(request):
    first_name = request.session.get('first_name')
    from ..models import TripdetailInfo, Fuelfillinginfo, VehiclemasterInfo, Location_info, ConsignmentdetailInfo
    from django.db.models import Sum, Q

    if request.method == "POST":
        form = DmrForm(request.POST)
        vehicle_search = request.POST.get('vehicle_search', '')
        selected_month = request.POST.get('month', '0')
        selected_year = request.POST.get('year', '0')
        branch_id = request.POST.get('branch', '')
    else:
        form = DmrForm()
        vehicle_search = ""
        selected_month = '0'
        selected_year = '0'
        branch_id = ""

    # Base Query for Trips (Own vehicles only & Business trips only)
    trips = TripdetailInfo.objects.filter(
        tr_vehiclesource_id=1,
        tr_category__category__icontains='business'
    ).select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_consignmentnumber',
        'tr_vehicletype'
    )

    # Branch Filter
    branch_name = ""
    if branch_id:
        try:
            branch_obj = Location_info.objects.get(id=branch_id)
            branch_name = branch_obj.loc_name.upper()
            if "MAA" in branch_name:
                trips = trips.filter(Q(tr_enquirynumber__en_customername__cu_name__icontains='MAA') | Q(
                    tr_consignmentnumber__co_consignmentnumber__icontains='MAA'))
            elif "BLR" in branch_name:
                trips = trips.filter(Q(tr_enquirynumber__en_customername__cu_name__icontains='BLR') | Q(
                    tr_consignmentnumber__co_consignmentnumber__icontains='BLR'))
        except Location_info.DoesNotExist:
            pass

    if vehicle_search:
        trips = trips.filter(tr_vehiclenumber__icontains=vehicle_search)

    # Date Filters
    q_date = Q()
    if selected_month and selected_month != '0':
        q_date &= (
                Q(tr_loading_time__month=selected_month) |
                Q(tr_departeddate__month=selected_month) |
                Q(tr_departeddate_pickup__month=selected_month) |
                Q(tr_reporteddate__month=selected_month) |
                Q(tr_unloading_time__month=selected_month) |
                Q(tr_created_at__month=selected_month)
        )
    if selected_year and selected_year != '0':
        q_date &= (
                Q(tr_loading_time__year=selected_year) |
                Q(tr_departeddate__year=selected_year) |
                Q(tr_departeddate_pickup__year=selected_year) |
                Q(tr_reporteddate__year=selected_year) |
                Q(tr_unloading_time__year=selected_year) |
                Q(tr_created_at__year=selected_year)
        )

    if q_date:
        trips = trips.filter(q_date)

    # Sort
    trip_ids = list(trips.order_by('-tr_loading_time', '-tr_created_at').values_list('id', flat=True))
    trips = TripdetailInfo.objects.filter(id__in=trip_ids).select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_consignmentnumber',
        'tr_vehicletype'
    ).order_by('-tr_loading_time', '-tr_created_at')

    # Get all vehicles from filtered trips to optimize fuel lookup
    vehicle_numbers = trips.values_list('tr_vehiclenumber', flat=True).distinct()

    # Fuel Aggregation per Vehicle for the selected period
    fuel_q = Q(ff_vehicle_num__vm_registrationnumber__in=vehicle_numbers)
    if selected_month and selected_month != '0':
        fuel_q &= Q(ff_date__month=selected_month)
    if selected_year and selected_year != '0':
        fuel_q &= Q(ff_date__year=selected_year)

    fuel_stats = Fuelfillinginfo.objects.filter(fuel_q).values('ff_vehicle_num__vm_registrationnumber').annotate(
        total_cost=Sum('ff_fuel_price'),
        total_ltr=Sum('ff_filled_ltr')
    )
    fuel_map = {item['ff_vehicle_num__vm_registrationnumber']: item for item in fuel_stats}

    # Total KM and Total LTR aggregation per vehicle from trips for the selected period
    km_stats_q = Q(tr_vehiclenumber__in=vehicle_numbers)
    if q_date:
        km_stats_q &= q_date

    v_km_map = {}
    v_ltr_map = {}
    vehicle_trips_data = TripdetailInfo.objects.filter(km_stats_q).values('tr_vehiclenumber', 'tr_reportedkm',
                                                                          'tr_reportedkm_delivery', 'tr_departedkm')
    for vtr in vehicle_trips_data:
        vno = vtr['tr_vehiclenumber']
        rep_km = safe_num(vtr['tr_reportedkm_delivery'] if vtr['tr_reportedkm_delivery'] else vtr['tr_reportedkm'])
        dep_km = safe_num(vtr['tr_departedkm'])
        vkm = max(0, rep_km - dep_km)
        # Extreme bad data sanitization
        if vkm > 15000:
            continue
        v_km_map[vno] = v_km_map.get(vno, 0) + vkm

    # Fleet-wide statistics for fallback
    total_fleet_cost = sum(item['total_cost'] for item in fuel_map.values() if item['total_cost'])
    total_fleet_ltr = sum(item['total_ltr'] for item in fuel_map.values() if item['total_ltr'])
    fleet_avg_price = (
            total_fleet_cost / total_fleet_ltr) if total_fleet_ltr > 0 else 96.0  # Fallback to 96 if no fleet data

    # Vehicle Master for fixed mileage
    vehicles = VehiclemasterInfo.objects.filter(vm_registrationnumber__in=vehicle_numbers).select_related(
        'vm_vehiclemanufacturer', 'vm_vehiclemodel')
    vehicle_master_map = {v.vm_registrationnumber: v for v in vehicles}

    # Fetch Invoices and Rates for Revenue fallback
    from ..sub_models.trans_invoice_mod import TransInvoiceInfo
    from ..sub_models.rtratemaster_mod import RtratemasterInfo

    invoices = TransInvoiceInfo.objects.filter(ti_trip_id__in=[t.id for t in trips])
    invoice_map = {inv.ti_trip_id: inv for inv in invoices}

    # Fetch Consignments for fallback mapping (Matching by Enquiry + Vehicle)
    enquiry_ids = [t.tr_enquirynumber_id for t in trips if t.tr_enquirynumber_id]
    cons_fallback_qs = ConsignmentdetailInfo.objects.filter(
        co_enquirynumber_id__in=enquiry_ids
    ).values('co_enquirynumber_id', 'co_vehicelnumber', 'co_consignmentnumber')

    cons_fallback_map = {
        (c['co_enquirynumber_id'], safe_str(c['co_vehicelnumber']).strip().upper()): c['co_consignmentnumber']
        for c in cons_fallback_qs
    }

    # Standard Customer Rates Fallback
    rates = RtratemasterInfo.objects.all().values(
        'ro_customer_id', 'ro_customerdepartment_id', 'ro_fromlocation_id', 'ro_tolocation_id', 'ro_vehicletype_id',
        'ro_rate'
    )
    cust_rate_map = {
        (r['ro_customer_id'], r['ro_customerdepartment_id'], r['ro_fromlocation_id'], r['ro_tolocation_id'],
         r['ro_vehicletype_id']): r['ro_rate']
        for r in rates
    }

    processed_rows = []
    counter = 1

    for trip in trips:
        cust_name = safe_str(trip.tr_enquirynumber.en_customername).strip().upper() if trip.tr_enquirynumber else ""
        row_branch = "Chennai" if "MAA" in cust_name or (
                trip.tr_consignmentnumber and "MAA" in str(trip.tr_consignmentnumber)) else \
            ("Bangalore" if "BLR" in cust_name or (
                    trip.tr_consignmentnumber and "BLR" in str(trip.tr_consignmentnumber)) else "")

        # Date selection
        dates = [trip.tr_loading_time, trip.tr_departeddate, trip.tr_created_at]
        display_date = next((d for d in dates if d), None)
        trip_date_str = display_date.strftime("%d-%m-%Y") if display_date else ""

        # Revenue calculation (Multi-level fallback)
        inv = invoice_map.get(trip.id)
        cons = trip.tr_consignmentnumber

        rev_trip = (safe_num(inv.ti_transportation_charges) if inv else (
            safe_num(trip.tc_tripcost) if trip.tc_tripcost_check else 0.0))
        if rev_trip == 0 and not (inv or trip.tc_tripcost_check):
            if cons and cons.co_freight_amount:
                try:
                    # Strip non-numeric and parse
                    f_str = "".join(c for c in str(cons.co_freight_amount) if c.isdigit() or c == '.')
                    if f_str: rev_trip = float(f_str)
                except:
                    pass

            if rev_trip == 0 and trip.tr_enquirynumber:
                # Try Standard Rate Master
                key = (
                    trip.tr_enquirynumber.en_customername_id,
                    trip.tr_enquirynumber.en_customerdepartment_id,
                    trip.tr_departedlocation_id,
                    trip.tr_reportedlocation_id,
                    trip.tr_vehicletype_id
                )
                rev_trip = safe_num(cust_rate_map.get(key, 0.0))

        rev_toll = (
            safe_num(inv.ti_toll_charges) if inv else (safe_num(trip.tc_tollcost) if trip.tc_tollcost_check else 0.0))
        rev_aai = (safe_num(inv.ti_docket_charges) if inv else (
            safe_num(trip.tc_supervisorcost) if trip.tc_supervisorcost_check else 0.0))
        rev_loading = (safe_num(inv.ti_loading_charges) if inv else (
            safe_num(trip.tc_loadingcost) if trip.tc_loadingcost_check else 0.0))
        rev_unloading = (safe_num(inv.ti_unloading_charges) if inv else (
            safe_num(trip.tc_unloadingcost) if trip.tc_unloadingcost_check else 0.0))
        rev_weighment = (safe_num(inv.ti_weighment_charges) if inv else (
            safe_num(trip.tc_weighmentcost) if trip.tc_weighmentcost_check else 0.0))
        rev_halting = (safe_num(inv.ti_halting_charges) if inv else (
                (safe_num(trip.tc_haltingcost) if trip.tc_haltingcost_check else 0) + (
            safe_num(trip.tc_total_halting_cost) if trip.tc_total_halting_cost_check else 0)))
        rev_handling = (safe_num(inv.ti_handling_charges) if inv else (
            safe_num(trip.tc_handlingcost) if trip.tc_handlingcost_check else 0.0))
        rev_parking = (safe_num(inv.ti_parking_charges) if inv else (
            safe_num(trip.tc_parkingcost) if trip.tc_parkingcost_check else 0.0))
        rev_rto = safe_num(trip.tc_rtocost) if trip.tc_rtocost_check else 0.0
        rev_batta = safe_num(trip.tc_betacost) if trip.tc_betacost_check else 0.0
        rev_cancellation = (safe_num(inv.ti_cancellation_charges) if inv else (
            safe_num(trip.tc_cancellation) if trip.tc_cancellation_check else 0.0))

        revenue = rev_trip + rev_toll + rev_aai + rev_loading + rev_unloading + \
                  rev_weighment + rev_halting + rev_handling + rev_parking + \
                  rev_rto + rev_batta + rev_cancellation

        # Trip KM (Aligned with Vehicle Log Report logic)
        reported_km_val = trip.tr_reportedkm_delivery if trip.tr_reportedkm_delivery else trip.tr_reportedkm
        trip_km = max(0, safe_num(reported_km_val) - safe_num(trip.tr_departedkm))

        # --- Enhanced Diesel Calculation with Robust Fallbacks ---
        v_fuel = fuel_map.get(trip.tr_vehiclenumber, {'total_cost': 0, 'total_ltr': 0})
        v_total_fuel_cost = safe_num(v_fuel['total_cost'])
        v_total_ltr = safe_num(v_fuel['total_ltr'])
        v_total_km = v_km_map.get(trip.tr_vehiclenumber, 0)

        # 1. Price per Ltr (Vehicle specific -> Fleet avg)
        price_per_ltr = (v_total_fuel_cost / v_total_ltr) if v_total_ltr > 0 else fleet_avg_price

        # 2. Mileage Determination (Actual -> Fixed -> Default Type-based)
        actual_mileage = (v_total_km / v_total_ltr) if v_total_ltr > 0 else 0
        vm = vehicle_master_map.get(trip.tr_vehiclenumber)
        fixed_mileage = safe_num(vm.vm_millage) if vm else 0

        # Default mileage by vehicle type (fallback of fallbacks)
        vt_str = str(trip.tr_vehicletype_placed or trip.tr_vehicletype).upper()
        default_mileage = 4.5  # Default for unknown heavy trucks
        if "ACE" in vt_str:
            default_mileage = 14.0
        elif "407" in vt_str:
            default_mileage = 9.0
        elif "10FT" in vt_str:
            default_mileage = 8.0
        elif "14FT" in vt_str:
            default_mileage = 7.0
        elif "17FT" in vt_str:
            default_mileage = 6.0
        elif "19FT" in vt_str:
            default_mileage = 5.5
        elif "20FT" in vt_str:
            default_mileage = 4.5
        elif "22FT" in vt_str:
            default_mileage = 4.0
        elif "24FT" in vt_str:
            default_mileage = 4.0
        elif "32FT" in vt_str:
            default_mileage = 3.5

        # Logic: Use actual if realistic, else fixed, else default
        # Realistic range for trucks/commercial vehicles: 2.5 to 18 km/ltr
        if 2.5 <= actual_mileage <= 18.0:
            eff_mileage = actual_mileage
        elif fixed_mileage > 0:
            eff_mileage = fixed_mileage
        else:
            eff_mileage = default_mileage

        assigned_diesel_expense = (price_per_ltr / eff_mileage) * trip_km
        actual_mileage_display = actual_mileage if actual_mileage > 0 else eff_mileage

        diesel_vs_revenue_pct = (assigned_diesel_expense / revenue * 100) if revenue > 0 else 0

        vm = vehicle_master_map.get(trip.tr_vehiclenumber)
        mileage_fixed = safe_str(vm.vm_millage) if vm else ""
        leased_to = safe_str(trip.tr_enquirynumber.en_customername) if trip.tr_enquirynumber else ""
        cnote_str = safe_str(trip.tr_consignmentnumber.co_consignmentnumber) if trip.tr_consignmentnumber else ""
        if not cnote_str and trip.tr_enquirynumber:
            # Fallback: Find linked CNote via Enquiry + Vehicle Number
            v_key = (trip.tr_enquirynumber_id, safe_str(trip.tr_vehiclenumber).strip().upper())
            cnote_str = safe_str(cons_fallback_map.get(v_key, ""))

        processed_rows.append([
            counter,
            row_branch,
            trip_date_str,
            cnote_str,
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype_placed or trip.tr_vehicletype),
            mileage_fixed,
            leased_to,
            trip_km,
            round(assigned_diesel_expense, 2),
            round(revenue, 2),
            f"{diesel_vs_revenue_pct:.2f}%",
            f"{actual_mileage_display:.2f}"
        ])
        counter += 1

    all_vehicles = VehiclemasterInfo.objects.filter(vm_ownership_id__in=[1]).order_by('vm_registrationnumber')

    context = {
        'first_name': first_name,
        'form': form,
        'headers': DIESEL_VS_REVENUE_HEADERS,
        'data_rows': processed_rows,
        'vehicle_search': vehicle_search,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'all_vehicles': all_vehicles,
    }
    return render(request, "asset_mgt_app/diesel_vs_revenue_report.html", context)


@login_required(login_url='login_page')
def own_vs_market_sales_report_view(request):
    first_name = request.session.get('first_name')
    from ..models import TripdetailInfo, Vehicle_allotmentInfo
    from datetime import datetime

    if request.method == "POST":
        form = DmrForm(request.POST)
        selected_month = request.POST.get('month', '0')
        selected_year = request.POST.get('year', '0')
        customer_id = request.POST.get('dmr_customer')
        dept_id = request.POST.get('customer_department')
    else:
        form = DmrForm()
        selected_month = '0'
        selected_year = '0'
        customer_id = None
        dept_id = None

    # Base Query
    trips = TripdetailInfo.objects.all().select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_enquirynumber__en_customerdepartment',
        'tr_enquirynumber__en_trip_type',
        'tr_consignmentnumber'
    )

    if customer_id:
        trips = trips.filter(tr_enquirynumber__en_customername_id=customer_id)
    if dept_id:
        trips = trips.filter(tr_enquirynumber__en_customerdepartment_id=dept_id)
    if selected_month and selected_month != '0':
        trips = trips.filter(
            Q(tr_loading_time__month=selected_month) |
            Q(tr_departeddate__month=selected_month) |
            Q(tr_departeddate_pickup__month=selected_month) |
            Q(tr_reporteddate__month=selected_month) |
            Q(tr_unloading_time__month=selected_month) |
            Q(tr_created_at__month=selected_month)
        )

    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) |
            Q(tr_departeddate__year=selected_year) |
            Q(tr_departeddate_pickup__year=selected_year) |
            Q(tr_reporteddate__year=selected_year) |
            Q(tr_unloading_time__year=selected_year) |
            Q(tr_created_at__year=selected_year)
        )

    # Prefetch Vehicle Allotment for Market Buy Rate
    enquiry_ids = [t.tr_enquirynumber_id for t in trips]
    va_data = Vehicle_allotmentInfo.objects.filter(va_enquirynumber_id__in=enquiry_ids)
    va_map = {v.va_enquirynumber_id: v for v in va_data}

    aggregated_data = {}

    for trip in trips:
        # Determine Date
        # Filter-aware date selection
        dates = [
            trip.tr_loading_time, trip.tr_departeddate, trip.tr_departeddate_pickup,
            trip.tr_departeddate_delivery, trip.tr_reporteddate, trip.tr_reporteddate_pickup,
            trip.tr_reporteddate_delivery, trip.tr_unloading_time, trip.tr_dock_in_time,
            trip.tr_dock_out_time, trip.tr_created_at
        ]
        target_month = int(selected_month) if selected_month and selected_month != '0' else None
        target_year = int(selected_year) if selected_year and selected_year != '0' else None

        full_date = None
        for d in dates:
            if d:
                month_match = (not target_month or d.month == target_month)
                year_match = (not target_year or d.year == target_year)
                if month_match and year_match:
                    full_date = d
                    break
        if not full_date:
            full_date = next((d for d in dates if d), None)
        if not full_date:
            continue
        trip_date = full_date.date()

        date_str = trip_date.strftime("%d-%m-%Y")

        cust_name = safe_str(trip.tr_enquirynumber.en_customername).strip().upper()
        branch = "Chennai" if cust_name.endswith("MAA") else ("Bangalore" if cust_name.endswith("BLR") else "")

        customer = safe_str(trip.tr_enquirynumber.en_customername)
        dept = safe_str(trip.tr_enquirynumber.en_customerdepartment)

        key = (date_str, branch, customer, dept)

        if key not in aggregated_data:
            aggregated_data[key] = {
                'date': date_str,
                'branch': branch,
                'customer': customer,
                'dept': dept,
                'own_sales': 0.0,
                'own_vehs': set(),
                'own_jobs': 0,
                'own_drivers': set(),
                'mkt_sales': 0.0,
                'mkt_vehs': set(),
                'mkt_jobs': 0,
                'mkt_drivers': set(),
                'mkt_buy_rate': 0.0,
                'local_trips': 0,
                'outstation_trips': 0
            }

        data = aggregated_data[key]

        # Revenue Calculation - Respecting checkboxes
        revenue = (safe_num(trip.tc_tripcost) if trip.tc_tripcost_check else 0) + \
                  (safe_num(trip.tc_rtocost) if trip.tc_rtocost_check else 0) + \
                  (safe_num(trip.tc_betacost) if trip.tc_betacost_check else 0) + \
                  (safe_num(trip.tc_parkingcost) if trip.tc_parkingcost_check else 0) + \
                  (safe_num(trip.tc_tollcost) if trip.tc_tollcost_check else 0) + \
                  (safe_num(trip.tc_loadingcost) if trip.tc_loadingcost_check else 0) + \
                  (safe_num(trip.tc_unloadingcost) if trip.tc_unloadingcost_check else 0) + \
                  (safe_num(trip.tc_weighmentcost) if trip.tc_weighmentcost_check else 0) + \
                  (safe_num(trip.tc_handlingcost) if trip.tc_handlingcost_check else 0) + \
                  (safe_num(trip.tc_haltingcost) if trip.tc_haltingcost_check else 0) + \
                  (safe_num(trip.tc_total_halting_cost) if trip.tc_total_halting_cost_check else 0) + \
                  (safe_num(trip.tc_supervisorcost) if trip.tc_supervisorcost_check else 0) + \
                  (safe_num(trip.tc_cancellation) if trip.tc_cancellation_check else 0)

        is_own = trip.tr_vehiclesource_id in [2]  # 1=OWN, 2=ATTACHED/OWN

        if is_own:
            data['own_sales'] += revenue
            data['own_jobs'] += 1
            if trip.tr_vehiclenumber:
                data['own_vehs'].add(trip.tr_vehiclenumber)
            if trip.tr_drivername:
                data['own_drivers'].add(trip.tr_drivername)
        else:
            data['mkt_sales'] += revenue
            data['mkt_jobs'] += 1
            if trip.tr_vehiclenumber:
                data['mkt_vehs'].add(trip.tr_vehiclenumber)
            if trip.tr_drivername:
                data['mkt_drivers'].add(trip.tr_drivername)

            # Market Buy Rate from Allotment
            va = va_map.get(trip.tr_enquirynumber_id)
            if va:
                data['mkt_buy_rate'] += safe_num(va.va_specialbuy) or safe_num(va.va_standardbuy)

        # Local vs Outstation
        trip_type = safe_str(trip.tr_enquirynumber.en_trip_type).lower()
        if "local" in trip_type:
            data['local_trips'] += 1
        elif "outstation" in trip_type:
            data['outstation_trips'] += 1

    # Convert to rows
    processed_rows = []
    # Sort by date desc
    sorted_keys = sorted(aggregated_data.keys(), key=lambda x: datetime.strptime(x[0], "%d-%m-%Y"), reverse=True)

    for idx, key in enumerate(sorted_keys, start=1):
        d = aggregated_data[key]

        own_index = (d['own_sales'] / d['own_jobs']) if d['own_jobs'] > 0 else 0
        mkt_index = (d['mkt_sales'] / d['mkt_jobs']) if d['mkt_jobs'] > 0 else 0

        row = [
            idx,
            d['date'],
            d['branch'],
            d['customer'],
            d['dept'],
            d['own_sales'],
            len(d['own_vehs']),
            d['own_jobs'],
            len(d['own_drivers']),
            round(own_index, 2),
            d['mkt_sales'],
            len(d['mkt_vehs']),
            d['mkt_jobs'],
            len(d['mkt_drivers']),
            round(mkt_index, 2),
            d['mkt_buy_rate'],
            d['local_trips'],
            d['outstation_trips']
        ]
        processed_rows.append(row)

    paginator = Paginator(processed_rows, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'first_name': first_name,
        'form': form,
        'headers': OWN_VS_MARKET_SALES_HEADERS,
        'data_rows': page_obj.object_list,
        'page_obj': page_obj,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'customer_id': customer_id,
        'dept_id': dept_id,
    }
    return render(request, "asset_mgt_app/own_vs_market_sales_report.html", context)


@login_required(login_url='login_page')
def enquiry_pending_report_view(request):
    from ..models import EnquirynoteInfo, Enquirynotevehicle, Vehicle_allotmentInfo, StatusList
    first_name = request.session.get('first_name')

    if request.method == "POST":
        form = DmrForm(request.POST)
    else:
        form = DmrForm()

    customer_id = request.POST.get('dmr_customer')
    from_loc_id = request.POST.get('from_location')
    to_loc_id = request.POST.get('to_location')
    from_date = request.POST.get('date_from')
    to_date = request.POST.get('date_to')
    branch = request.POST.get('branch')

    # Status 6 = Pending
    enquiries = EnquirynoteInfo.objects.filter(en_status_id=6).select_related(
        'en_customername', 'en_customerdepartment', 'en_fromlocaion', 'en_tolocation'
    )

    if branch == "Bengaluru":
        enquiries = enquiries.filter(en_enquirynumber__icontains="BLR")
    elif branch == "Chennai":
        enquiries = enquiries.filter(en_enquirynumber__icontains="MAA")

    if customer_id:
        enquiries = enquiries.filter(en_customername_id=customer_id)
    if from_loc_id:
        enquiries = enquiries.filter(en_fromlocaion_id=from_loc_id)
    if to_loc_id:
        enquiries = enquiries.filter(en_tolocation_id=to_loc_id)
    if from_date:
        enquiries = enquiries.filter(en_created_at__date__gte=from_date)
    if to_date:
        enquiries = enquiries.filter(en_created_at__date__lte=to_date)

    enquiries = enquiries.order_by('-en_created_at')

    # Prefetch data for efficiency
    enquiry_ids = [enq.id for enq in enquiries]

    # Vehicle Requests mapping
    vehicle_requests = Enquirynotevehicle.objects.filter(env_enquirynumber_id__in=enquiry_ids).select_related(
        'env_vehicletype')
    req_map = {}
    total_req_qty = {}
    for vr in vehicle_requests:
        req_map.setdefault(vr.env_enquirynumber_id, []).append(f"{vr.env_quantity} x {vr.env_vehicletype}")
        qty = vr.env_quantity or 0
        total_req_qty[vr.env_enquirynumber_id] = total_req_qty.get(vr.env_enquirynumber_id, 0) + qty

    # Vehicle Allotments mapping
    allotments = Vehicle_allotmentInfo.objects.filter(va_enquirynumber_id__in=enquiry_ids,
                                                      va_status_id__in=[1, 4, 5]).select_related(
        'va_vehiclenumber')
    allot_map = {}
    for va in allotments:
        reg_no = va.va_vehiclenumber.vm_registrationnumber if va.va_vehiclenumber else va.va_vehiclenumber_mkt
        if reg_no:
            allot_map.setdefault(va.va_enquirynumber_id, []).append(str(reg_no))

    data_rows = []
    for idx, enq in enumerate(enquiries, start=1):
        # Vehicle Requested
        req_list = req_map.get(enq.id, [])
        veh_req_str = str(total_req_qty.get(enq.id, 0))

        # Vehicle Type
        # Extract unique types from req_list
        veh_types = ", ".join(list(set([r.split(" x ")[-1] for r in req_list])))

        # Vehicle Unplaced count
        total_req = total_req_qty.get(enq.id, 0)
        total_placed = len(allot_map.get(enq.id, []))
        unplaced_count = max(0, total_req - total_placed)
        places_str = str(unplaced_count)

        if unplaced_count > 0:
            row = [
                idx,
                _fmt_dt(enq.en_created_at, date_only=True),
                safe_str(enq.en_enquirynumber),
                safe_str(enq.en_fromlocaion),
                safe_str(enq.en_tolocation),
                veh_req_str,
                places_str,
                veh_types,
                safe_str(enq.en_customername),
                safe_str(" ")  # Reason field as requested by user
            ]
            data_rows.append(row)

    context = {
        'first_name': first_name,
        'form': form,
        'headers': ENQUIRY_PENDING_HEADERS,
        'data_rows': data_rows,
        'customer_id': customer_id,
        'from_location': from_loc_id,
        'to_location': to_loc_id,
        'date_from': from_date,
        'date_to': to_date,
        'selected_branch': branch,
    }
    return render(request, "asset_mgt_app/enquiry_pending_report.html", context)


@login_required(login_url='login_page')
def driver_balance_report_view(request):
    """
    Displays S.No, Driver Id, Branch, Driver name, and Balance.
    """
    from ..models import DrivermasterInfo, driver_settlement_info, User_extInfo, Location_info
    from django.db.models import Sum

    first_name = request.session.get('first_name')

    # Filters
    driver_id = request.POST.get('driver_name') or request.GET.get('driver_name')
    branch_id = request.POST.get('branch') or request.GET.get('branch')
    from_date = request.POST.get('from_date') or request.GET.get('from_date')
    to_date = request.POST.get('to_date') or request.GET.get('to_date')

    # Base queryset for drivers - Restricted to BVM MAA and BVM BLR branches as per user request
    drivers_qs = DrivermasterInfo.objects.filter(
        dm_user_id__user_extinfo__emp_branch__loc_name__in=['BVM MAA', 'BVM BLR']
    ).select_related('dm_user_id')

    if driver_id:
        drivers_qs = drivers_qs.filter(id=driver_id)

    # We might need to filter by branch. Branch info is in User_extInfo
    if branch_id:
        drivers_qs = drivers_qs.filter(dm_user_id__user_extinfo__emp_branch_id=branch_id)

    data_rows = []
    for idx, driver in enumerate(drivers_qs.order_by('dm_name'), start=1):
        # Calculate Balance: Advance - Expense from Driverexpense within the date range
        from ..models import Driverexpense

        expenses_qs = Driverexpense.objects.filter(de_driver_id__driver=driver)

        if from_date:
            expenses_qs = expenses_qs.filter(de_date__date__gte=from_date)
        if to_date:
            expenses_qs = expenses_qs.filter(de_date__date__lte=to_date)

        advances_total = expenses_qs.filter(de_expense_type_id=1).aggregate(total=Sum('de_total_cost'))['total'] or 0
        expenses_total = expenses_qs.filter(de_expense_type_id=2).aggregate(total=Sum('de_total_cost'))['total'] or 0

        balance = advances_total - expenses_total

        # Get Branch
        branch_name = ""
        try:
            if driver.dm_user_id:
                user_ext = User_extInfo.objects.get(user=driver.dm_user_id)
                if user_ext.emp_branch:
                    branch_name = user_ext.emp_branch.loc_name.replace('BVM ', '')
        except User_extInfo.DoesNotExist:
            pass

        data_rows.append([
            idx,
            driver.dm_id or "",
            branch_name,
            driver.dm_name or "",
            round(balance, 2)
        ])

    # For dropdowns - Restricted to BVM MAA and BVM BLR drivers and branches
    all_drivers = DrivermasterInfo.objects.filter(
        dm_user_id__user_extinfo__emp_branch__loc_name__in=['BVM MAA', 'BVM BLR']
    ).order_by('dm_name')

    raw_branches = Location_info.objects.filter(loc_name__in=['BVM MAA', 'BVM BLR']).order_by('loc_name')
    all_branches = [{'id': b.id, 'loc_name': b.loc_name.replace('BVM ', '')} for b in raw_branches]

    # Convert select_driver_id and selected_branch_id to safe types for template comparison
    safe_driver_id = None
    if driver_id:
        try:
            safe_driver_id = int(driver_id)
        except (ValueError, TypeError):
            pass

    safe_branch_id = None
    if branch_id:
        try:
            safe_branch_id = int(branch_id)
        except (ValueError, TypeError):
            pass

    context = {
        'first_name': first_name,
        'headers': DRIVER_BALANCE_HEADERS,
        'data_rows': data_rows,
        'drivers': all_drivers,
        'branches': all_branches,
        'selected_driver_id': safe_driver_id,
        'selected_branch_id': safe_branch_id,
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, "asset_mgt_app/driver_balance_report.html", context)


@login_required(login_url='login_page')
def pod_pending_report_view(request):
    first_name = request.session.get('first_name')

    from ..models import Location_info, OwnershipInfo, Tr_triptype_Info
    return render(request, "asset_mgt_app/pod_pending_report.html", {
        'first_name': first_name,
        'headers': POD_PENDING_REPORT_HEADERS,
        'all_vehiclesources': OwnershipInfo.objects.all(),
        'all_triptypes': Tr_triptype_Info.objects.all(),
        'all_branches': [
            {'id': b.id, 'name': b.loc_name.replace('BVM ', '').strip()}
            for b in Location_info.objects.filter(id__in=[1, 2]).order_by('loc_name')
        ],
    })


@login_required(login_url='login_page')
def pod_pending_report_ajax_view(request):
    """Server-side DataTables AJAX endpoint for POD Pending Report."""
    from django.db.models import Q
    from datetime import date
    from django.http import JsonResponse

    # DataTables params
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 50))
    search_value = request.GET.get('search[value]', '').strip()

    # Custom Filter params
    from_date = request.GET.get('from_date', '').strip()
    to_date = request.GET.get('to_date', '').strip()
    branch_id = request.GET.get('branch', '').strip()
    vehiclesource_id = request.GET.get('vehiclesource', '').strip()
    triptype_id = request.GET.get('triptype', '').strip()

    trips = TripdetailInfo.objects.select_related(
        'tr_enquirynumber', 'tr_enquirynumber__en_customername',
        'tr_enquirynumber__en_customerdepartment', 'tr_consignmentnumber',
        'tr_vehiclesource', 'tr_enquirynumber__en_trip_type',
        'tr_departedlocation', 'tr_reportedlocation'
    ).filter(
        Q(tr_reporteddate__isnull=False) | Q(tr_unloading_time__isnull=False) | Q(tr_reporteddate_pickup__isnull=False),
        tc_financestatus_id__in=[2, 4, 5, 6, 7, 9],
        tr_category_id=1  # Business trips only
    )

    # Apply Custom Filters
    if from_date:
        trips = trips.filter(tr_departeddate__date__gte=from_date)
    if to_date:
        trips = trips.filter(tr_departeddate__date__lte=to_date)

    if branch_id:
        try:
            b_id = int(branch_id)
            if b_id == 1:  # BLR
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='BLR')
            elif b_id == 2:  # MAA
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='MAA')
        except:
            pass

    if vehiclesource_id:
        trips = trips.filter(tr_vehiclesource_id=vehiclesource_id)

    if triptype_id:
        trips = trips.filter(tr_enquirynumber__en_trip_type_id=triptype_id)

    records_total = trips.count()

    # Apply Global Search
    if search_value:
        trips = trips.filter(
            Q(tr_tripnumber__icontains=search_value) |
            Q(tr_vehiclenumber__icontains=search_value) |
            Q(tr_enquirynumber__en_customername__cu_name__icontains=search_value) |
            Q(tr_enquirynumber__en_customerdepartment__ct_customerdepartment__icontains=search_value) |
            Q(tr_consignmentnumber__co_consignmentnumber__icontains=search_value) |
            Q(tr_departedlocation__place_name__icontains=search_value) |
            Q(tr_reportedlocation__place_name__icontains=search_value)
        )

    records_filtered = trips.count()

    # Ordering
    order_col = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'desc')
    col_map = {
        0: 'id',
        1: 'tr_departeddate',
        2: 'tr_reporteddate',
        3: 'tr_consignmentnumber__co_consignmentnumber',
        4: 'tr_enquirynumber__en_customername__cu_name',
        5: 'tr_departedlocation__place_name',
        6: 'tr_reportedlocation__place_name',
        7: 'tr_enquirynumber__en_customerdepartment__ct_customerdepartment',
        8: 'tr_vehiclenumber',
        9: 'tr_enquirynumber__en_trip_type__tr_trip_type',
        10: 'tr_vehiclesource__ow_ownership',
        12: 'tc_tripcost',
    }
    order_field = col_map.get(order_col, '-tr_created_at')
    if order_dir == 'desc' and not order_field.startswith('-'):
        order_field = '-' + order_field
    trips = trips.order_by(order_field)

    # Slicing for Pagination
    if length != -1:
        trips_slice = trips[start:start + length]
    else:
        trips_slice = trips[start:]

    # Fetch Consignment Goods in Bulk for current page
    trip_cons_ids = [t.tr_consignmentnumber_id for t in trips_slice if t.tr_consignmentnumber_id]
    goods_map = {
        g.cg_consignmentnumber_id: g
        for g in ConsignmentgoodsInfo.objects.filter(
            cg_consignmentnumber_id__in=trip_cons_ids
        ).select_related('cg_consigner')
    }

    data = []
    today = date.today()
    for idx, trip in enumerate(trips_slice, start=start + 1):
        cons_goods = goods_map.get(trip.tr_consignmentnumber_id)

        start_date = trip.tr_departeddate or trip.tr_loading_time
        # Trip Closed Date = tr_reporteddate_pickup, fallback to unloading_time or reporteddate
        end_date = trip.tr_reporteddate_pickup or trip.tr_unloading_time or trip.tr_reporteddate

        pending_days = ""
        if not trip.tc_pod_attachment and end_date:
            diff = today - end_date.date()
            pending_days = max(0, diff.days)

        data.append([
            idx,
            _fmt_dt(start_date, date_only=True),
            _fmt_dt(end_date, date_only=True),
            safe_str(trip.tr_consignmentnumber.co_consignmentnumber) if trip.tr_consignmentnumber else "",
            safe_str(trip.tr_enquirynumber.en_customername),
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_str(trip.tr_enquirynumber.en_customerdepartment),
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_enquirynumber.en_trip_type if trip.tr_enquirynumber else ""),
            safe_str(trip.tr_vehiclesource),
            safe_str(cons_goods.cg_consigner) if cons_goods else "",
            safe_num(trip.tc_tripcost) if trip.tc_tripcost_check else 0,
            pending_days,
            safe_str(trip.tr_remarks),
        ])

    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data,
    })


@login_required(login_url='login_page')
def enquiry_pending_report_ajax_view(request):
    from ..models import EnquirynoteInfo, Enquirynotevehicle, Vehicle_allotmentInfo
    from django.db.models import Sum, Count, Q
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')

    # Filters
    branch = request.GET.get('branch', '')
    customer_id = request.GET.get('dmr_customer', '')
    from_loc_id = request.GET.get('from_location', '')
    to_loc_id = request.GET.get('to_location', '')
    from_date = request.GET.get('date_from', '')
    to_date = request.GET.get('date_to', '')

    # Base Query: All Enquiries (except cancelled ones, as requested)
    enquiries = EnquirynoteInfo.objects.exclude(
        Q(en_status_id=8) | Q(tripdetailinfo__tc_financestatus_id=3)
    )

    # Filter out enquiries where unassigned vehicles <= 0
    pending_ids = list(enquiries.values_list('id', flat=True))

    reqs = Enquirynotevehicle.objects.filter(env_enquirynumber_id__in=pending_ids).values(
        'env_enquirynumber_id').annotate(tot=Sum('env_quantity'))
    req_map = {r['env_enquirynumber_id']: r['tot'] or 0 for r in reqs}

    allots = Vehicle_allotmentInfo.objects.filter(va_enquirynumber_id__in=pending_ids,
                                                  va_status_id__in=[1, 4, 5]).values(
        'va_enquirynumber_id').annotate(tot=Count('id'))
    allots_map = {a['va_enquirynumber_id']: a['tot'] or 0 for a in allots}

    # We show all enquiries here as requested, no longer filtering out those where unassigned <= 0
    enquiries = enquiries.select_related(
        'en_customername', 'en_fromlocaion', 'en_tolocation'
    )

    records_total = enquiries.count()

    # Apply Filters
    if branch == "Bengaluru":
        enquiries = enquiries.filter(en_enquirynumber__icontains="BLR")
    elif branch == "Chennai":
        enquiries = enquiries.filter(en_enquirynumber__icontains="MAA")

    if customer_id:
        enquiries = enquiries.filter(en_customername_id=customer_id)
    if from_loc_id:
        enquiries = enquiries.filter(en_fromlocaion_id=from_loc_id)
    if to_loc_id:
        enquiries = enquiries.filter(en_tolocation_id=to_loc_id)
    if from_date:
        enquiries = enquiries.filter(en_created_at__date__gte=from_date)
    if to_date:
        enquiries = enquiries.filter(en_created_at__date__lte=to_date)

    if search_value:
        enquiries = enquiries.filter(
            Q(en_enquirynumber__icontains=search_value) |
            Q(en_customername__cu_name__icontains=search_value)
        )

    records_filtered = enquiries.count()

    # Order By
    order_col = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'desc')
    col_map = {
        0: 'id',
        1: 'en_created_at',
        2: 'en_enquirynumber',
        3: 'en_fromlocaion__place_name',
        4: 'en_tolocation__place_name',
        9: 'en_customername__cu_name',
    }
    order_field = col_map.get(order_col, '-en_created_at')
    if order_dir == 'desc' and not order_field.startswith('-'):
        order_field = '-' + order_field
    enquiries = enquiries.order_by(order_field)

    # Slicing
    if length != -1:
        enquiries_slice = enquiries[start:start + length]
    else:
        enquiries_slice = enquiries[start:]

    enquiry_ids = [enq.id for enq in enquiries_slice]

    # Fetch vehicle requests
    vehicle_requests = Enquirynotevehicle.objects.filter(env_enquirynumber_id__in=enquiry_ids).select_related(
        'env_vehicletype')
    req_map = {}
    total_req_qty = {}
    for vr in vehicle_requests:
        req_map.setdefault(vr.env_enquirynumber_id, []).append(f"{vr.env_quantity} x {vr.env_vehicletype}")
        qty = vr.env_quantity or 0
        total_req_qty[vr.env_enquirynumber_id] = total_req_qty.get(vr.env_enquirynumber_id, 0) + qty

    # Fetch allotments
    allotments = Vehicle_allotmentInfo.objects.filter(va_enquirynumber_id__in=enquiry_ids, va_status_id__in=[1, 4, 5])
    allot_map = {}
    for va in allotments:
        allot_map.setdefault(va.va_enquirynumber_id, []).append(va.id)

    def safe_str(val):
        return str(val) if val else ""

    data = []
    for idx, enq in enumerate(enquiries_slice, start=start + 1):
        req_list = req_map.get(enq.id, [])
        veh_req_str = str(total_req_qty.get(enq.id, 0))
        veh_types = ", ".join(list(set([r.split(" x ")[-1] for r in req_list])))
        total_req = total_req_qty.get(enq.id, 0)
        total_placed = len(allot_map.get(enq.id, []))
        unplaced_count = max(0, total_req - total_placed)

        data.append([
            idx,
            _fmt_dt(enq.en_created_at, date_only=True),
            enq.en_enquirynumber,
            safe_str(enq.en_fromlocaion),
            safe_str(enq.en_tolocation),
            veh_req_str,
            str(total_placed),
            str(unplaced_count),
            veh_types,
            safe_str(enq.en_customername),
            " "
        ])

    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data,
    })


def get_filtered_trips(branch_id, trip_category_id, vehicle_source_id, from_date, to_date, selected_year,
                       customer_id=None, selected_month=None):
    from ..models import TripdetailInfo, Location_info
    from django.db.models import Q

    # Sanitize all inputs to handle 'None' strings or empty values
    branch_id = branch_id if branch_id not in [None, 'None', '', '0'] else None
    trip_category_id = trip_category_id if trip_category_id not in [None, 'None', '', '0'] else None
    vehicle_source_id = vehicle_source_id if vehicle_source_id not in [None, 'None', '', '0'] else None
    customer_id = customer_id if customer_id not in [None, 'None', '', '0'] else None
    selected_year = selected_year if selected_year not in [None, 'None', '', '0'] else None
    selected_month = selected_month if selected_month not in [None, 'None', '', '0'] else None

    trips = TripdetailInfo.objects.filter(
        Q(tc_financestatus_id__in=[1, 2, 3, 4, 7, 9])
    ).select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_enquirynumber__en_customerdepartment',
        'tr_consignmentnumber',
        'tr_vehicletype',
        'tr_vehiclesource',
        'tr_departedlocation',
        'tr_reportedlocation'
    )

    if trip_category_id:
        trips = trips.filter(tr_enquirynumber__en_trip_type_id=trip_category_id)

    if vehicle_source_id:
        trips = trips.filter(tr_vehiclesource_id=vehicle_source_id)

    if customer_id:
        trips = trips.filter(tr_enquirynumber__en_customername_id=customer_id)

    from django.db.models.functions import Coalesce
    trips = trips.annotate(
        resolved_date=Coalesce('tr_departeddate_pickup', 'tr_loading_time', 'tr_departeddate', 'tr_created_at')
    )

    if from_date or to_date or (selected_year and selected_year != '0') or (selected_month and selected_month != '0'):

        if from_date:
            trips = trips.filter(resolved_date__date__gte=from_date)

        if to_date:
            trips = trips.filter(resolved_date__date__lte=to_date)

        if selected_year and selected_year != '0':
            trips = trips.filter(resolved_date__year=selected_year)

        if selected_month and selected_month != '0':
            trips = trips.filter(resolved_date__month=selected_month)

    if branch_id:
        try:
            b_id = int(branch_id)
            if b_id == 1:  # BLR
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='BLR')
            elif b_id == 2:  # MAA
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='MAA')
            elif b_id == 3:  # PNY
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='PNY')
            elif b_id == 4:  # HYD
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='HYD')
            else:
                loc = Location_info.objects.get(id=b_id)
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains=loc.loc_name)
        except (ValueError, Location_info.DoesNotExist):
            pass

    return trips.order_by('-tr_created_at')


@login_required(login_url='login_page')
def movementwise_pl_report_view(request):
    from sms_app.sub_models.tr_triptype_mod import Tr_triptype_Info
    from ..models import Driverexpense, MarketBillInfo, Vehicle_allotmentInfo, TransInvoiceInfo, AttachedBillInfo, \
        VendorratemasterInfo1

    first_name = request.session.get('first_name')
    if request.method == "POST":
        form = DmrForm(request.POST)
    else:
        form = DmrForm()

    branch_id = request.POST.get('branch')
    trip_category_id = request.POST.get('trip_category')
    vehicle_source_id = request.POST.get('vehicle_source')
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    selected_year = request.POST.get('year')

    headers = [
        "SNo", "Trip Date", "Cnote", "Customer Name", "From", "To",
        "Vehicle Source", "Vehicle No", "Veh Type", "Revenue",
        "Expenses", "Profit", "Profit %"
    ]

    from ..models import Location_info, OwnershipInfo, Tr_triptype_Info
    return render(request, "asset_mgt_app/movementwise_pl_report.html", {
        'first_name': first_name,
        'headers': headers,
        'data_rows': [],  # AJAX populated
        'all_branches': [
            {'id': b.id, 'name': b.loc_name.replace('BVM ', '').strip()}
            for b in Location_info.objects.filter(id__in=[1, 2]).order_by('loc_name')
        ],

        'all_trip_categories': Tr_triptype_Info.objects.all(),
        'all_vehicle_sources': OwnershipInfo.objects.all(),
        'branch_id': int(branch_id) if branch_id else None,
        'trip_category_id': int(trip_category_id) if trip_category_id else None,
        'vehicle_source_id': int(vehicle_source_id) if vehicle_source_id else None,
        'from_date': from_date,
        'to_date': to_date,
        'selected_year': selected_year,
        'form': form,
    })


def movementwise_pl_report_ajax_view(request):
    try:
        from django.http import JsonResponse
        from django.db.models import Q
        from ..models import Location_info, OwnershipInfo, Driverexpense, TransInvoiceInfo, MarketBillInfo, \
            AttachedBillInfo, Vehicle_allotmentInfo, VendorratemasterInfo1

        draw = safe_int(request.GET.get('draw'), 1)
        start = safe_int(request.GET.get('start'), 0)
        length = safe_int(request.GET.get('length'), 10)

        branch_id = request.GET.get('branch')
        trip_category_id = request.GET.get('trip_category')
        vehicle_source_id = request.GET.get('vehicle_source')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        selected_year = request.GET.get('year')
        search_value = request.GET.get('search[value]', '').strip()

        # Base queryset
        base_trips = get_filtered_trips(branch_id, trip_category_id, vehicle_source_id, from_date, to_date,
                                        selected_year)
        base_trips = base_trips.filter(tr_category_id=1, tc_financestatus_id__in=[7, 9])
        trips = base_trips

        records_total = trips.order_by().values('id').count()

        # Ordering
        order_column_idx = safe_int(request.GET.get('order[0][column]'), 0)
        order_dir = request.GET.get('order[0][dir]', 'asc')

        order_map = {
            1: 'resolved_date',
            2: 'tr_consignmentnumber__co_consignmentnumber',
            3: 'tr_enquirynumber__en_customername__cu_name',
            4: 'tr_departedlocation__place_name',
            5: 'tr_reportedlocation__place_name',
            6: 'tr_vehiclesource__ow_ownership',
            7: 'tr_vehiclenumber',
            8: 'tr_vehicletype_placed__vt_typename',
        }

        sort_field = order_map.get(order_column_idx)
        if sort_field:
            if order_dir == 'desc':
                sort_field = '-' + sort_field
            trips = trips.order_by(sort_field)
        else:
            trips = trips.order_by('-tr_created_at')

        # Search filter in DB
        if search_value:
            trips = trips.filter(
                Q(tr_consignmentnumber__co_consignmentnumber__icontains=search_value) |
                Q(tr_enquirynumber__en_customername__cu_name__icontains=search_value) |
                Q(tr_vehiclenumber__icontains=search_value)
            )

        records_filtered = trips.order_by().values('id').count()

        # Pagination in DB
        if length != -1:
            paginated_trips = trips[start:start + length]
        else:
            paginated_trips = trips[start:]

        all_matching_trips = list(paginated_trips)

        # --- PRE-FETCH Logic (Scoped to Current Page) ---
        trip_id_to_pk = {t.id: t.id for t in all_matching_trips}
        trip_num_to_pk = {str(t.tr_tripnumber).strip().upper(): t.id for t in all_matching_trips if t.tr_tripnumber}
        all_query_ids = [str(t.id) for t in all_matching_trips] + [str(t.tr_tripnumber).strip() for t in
                                                                   all_matching_trips if t.tr_tripnumber]

        invoices = TransInvoiceInfo.objects.filter(
            Q(ti_trip_id__in=trip_id_to_pk.keys()) |
            Q(ti_consignment_id__in=[t.tr_consignmentnumber_id for t in all_matching_trips if
                                     t.tr_consignmentnumber_id])
        ).select_related('ti_trip', 'ti_consignment')

        invoice_obj_map = {}
        for i in invoices:
            if i.ti_trip_id:
                invoice_obj_map[i.ti_trip_id] = i
            elif i.ti_consignment_id:
                matching_trips = [t.id for t in all_matching_trips if t.tr_consignmentnumber_id == i.ti_consignment_id]
                for mt_id in matching_trips:
                    if mt_id not in invoice_obj_map:
                        invoice_obj_map[mt_id] = i

        expenses = Driverexpense.objects.filter(trip_number__in=all_query_ids).select_related('de_expense_type')
        expense_map = {}
        for e in expenses:
            t_id = None
            s_key = str(e.trip_number).strip().upper() if e.trip_number else ""
            if s_key in trip_num_to_pk:
                t_id = trip_num_to_pk[s_key]
            elif s_key.isdigit():
                t_id = int(s_key)
            if t_id and t_id in trip_id_to_pk: expense_map.setdefault(t_id, []).append(e)

        va_map = {va.va_enquirynumber_id: va for va in Vehicle_allotmentInfo.objects.filter(
            va_enquirynumber_id__in=[t.tr_enquirynumber_id for t in all_matching_trips if
                                     t.tr_enquirynumber_id]).select_related('va_vendor')}
        vendor_ids = set(a.va_vendor_id for a in va_map.values() if a.va_vendor_id)

        bill_no_map = {}
        for b in MarketBillInfo.objects.all().only('mb_bill_no', 'mb_selected_trips', 'mb_total_cost'):
            if b.mb_selected_trips:
                for tid in [tid.strip() for tid in b.mb_selected_trips.split(',') if tid.strip()]:
                    try:
                        bill_no_map[int(tid)] = b
                    except:
                        pass
                    bill_no_map[str(tid).strip().upper()] = b

        attached_bill_map = {}
        for b in AttachedBillInfo.objects.all().only('ab_bill_no', 'ab_selected_trips', 'ab_buy_cost',
                                                     'ab_total_km_run'):
            if b.ab_selected_trips:
                for tid in [tid.strip() for tid in b.ab_selected_trips.split(',') if tid.strip()]:
                    try:
                        attached_bill_map[int(tid)] = b
                    except:
                        pass
                    attached_bill_map[str(tid).strip().upper()] = b

        # --- Calculate Fuel Proration and Salary for OWN vehicles on this page ---
        fuel_lookup, salary_lookup = calculate_own_vehicle_fuel_and_salary(
            all_matching_trips, date_from=from_date, date_to=to_date
        )

        final_data_rows = []
        for idx, trip in enumerate(all_matching_trips, start=start + 1):
            inv = invoice_obj_map.get(trip.id)
            trip_expenses = expense_map.get(trip.id, [])
            va_info = va_map.get(trip.tr_enquirynumber_id)
            ab_bill = attached_bill_map.get(trip.id) or (
                attached_bill_map.get(str(trip.tr_tripnumber).strip().upper()) if trip.tr_tripnumber else None)
            mb_bill = bill_no_map.get(trip.id) or (
                bill_no_map.get(str(trip.tr_tripnumber).strip().upper()) if trip.tr_tripnumber else None)

            try:
                prorated_fuel_val = fuel_lookup.get(trip.id, None)
                prorated_salary_val = salary_lookup.get(trip.id, None)
                selling, buying, profit, profit_pct, disp_date = get_trip_pl_data(
                    trip, inv, trip_expenses, va_info, ab_bill, mb_bill,
                    prorated_fuel=prorated_fuel_val, prorated_salary=prorated_salary_val
                )
            except Exception as e:
                print(f"Error calculating P&L for trip {trip.id}: {e}")
                selling = buying = profit = profit_pct = 0.0
                disp_date = ""

            final_data_rows.append([
                idx,
                disp_date,
                safe_str(trip.tr_consignmentnumber.co_consignmentnumber) if trip.tr_consignmentnumber else "",
                safe_str(trip.tr_enquirynumber.en_customername) if trip.tr_enquirynumber else "",
                safe_str(trip.tr_departedlocation),
                safe_str(trip.tr_reportedlocation),
                safe_str(trip.tr_vehiclesource),
                safe_str(trip.tr_vehiclenumber),
                safe_str(trip.tr_vehicletype_placed or trip.tr_vehicletype),
                round(selling, 2),
                round(buying, 2),
                round(profit, 2),
                f"{round(profit_pct, 2)}%"
            ])

        return JsonResponse({
            'draw': draw,
            'recordsTotal': records_total,
            'recordsFiltered': records_filtered,
            'data': final_data_rows,
        })
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(error_msg)
        return JsonResponse({
            'error': str(e),
            'traceback': error_msg,
            'draw': safe_int(request.GET.get('draw'), 1),
            'recordsTotal': 0,
            'recordsFiltered': 0,
            'data': [],
        }, status=200)


def customerwise_pl_report_ajax_view(request):
    try:
        from django.http import JsonResponse
        from django.db.models import Q
        from ..models import TripdetailInfo, Location_info, OwnershipInfo, Driverexpense, MarketBillInfo, \
            AttachedBillInfo, Vehicle_allotmentInfo, TransInvoiceInfo

        draw = safe_int(request.GET.get('draw'), 1)
        start = safe_int(request.GET.get('start'), 0)
        length = safe_int(request.GET.get('length'), 10)

        branch_id = request.GET.get('branch')
        trip_category_id = request.GET.get('trip_category')
        customer_id = request.GET.get('customer')
        vehicle_source_id = request.GET.get('vehicle_source')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        selected_year = request.GET.get('year')
        search_value = request.GET.get('search[value]', '').strip()

        # Base queryset
        base_trips = get_filtered_trips(branch_id, trip_category_id, vehicle_source_id, from_date, to_date,
                                        selected_year,
                                        customer_id=customer_id)
        base_trips = base_trips.filter(tr_category_id=1, tc_financestatus_id__in=[7, 9])
        trips = base_trips

        records_total = trips.order_by().values('id').count()

        # Ordering
        order_column_idx = safe_int(request.GET.get('order[0][column]'), 0)
        order_dir = request.GET.get('order[0][dir]', 'asc')

        order_map = {
            1: 'resolved_date',
            2: 'tr_consignmentnumber__co_consignmentnumber',
            3: 'tr_enquirynumber__en_customername__cu_name',
            4: 'tr_departedlocation__place_name',
            5: 'tr_reportedlocation__place_name',
            6: 'tr_vehiclesource__ow_ownership',
            7: 'tr_vehiclenumber',
            8: 'tr_vehicletype_placed__vt_typename',
        }

        sort_field = order_map.get(order_column_idx)
        if sort_field:
            if order_dir == 'desc':
                sort_field = '-' + sort_field
            trips = trips.order_by(sort_field)
        else:
            trips = trips.order_by('-tr_created_at')

        # Search filter in DB
        if search_value:
            trips = trips.filter(
                Q(tr_consignmentnumber__co_consignmentnumber__icontains=search_value) |
                Q(tr_enquirynumber__en_customername__cu_name__icontains=search_value) |
                Q(tr_vehiclenumber__icontains=search_value)
            )

        records_filtered = trips.order_by().values('id').count()

        # Pagination in DB
        if length != -1:
            paginated_trips = trips[start:start + length]
        else:
            paginated_trips = trips[start:]

        all_matching_trips = list(paginated_trips)

        # Scoped Pre-fetch
        trip_id_to_pk = {t.id: t.id for t in all_matching_trips}
        trip_num_to_pk = {str(t.tr_tripnumber).strip().upper(): t.id for t in all_matching_trips if t.tr_tripnumber}
        all_query_ids = [str(t.id) for t in all_matching_trips] + [str(t.tr_tripnumber).strip() for t in
                                                                   all_matching_trips if t.tr_tripnumber]

        invoices = TransInvoiceInfo.objects.filter(
            Q(ti_trip_id__in=trip_id_to_pk.keys()) |
            Q(ti_consignment_id__in=[t.tr_consignmentnumber_id for t in all_matching_trips if
                                     t.tr_consignmentnumber_id])
        ).select_related('ti_trip', 'ti_consignment')

        invoice_obj_map = {}
        for i in invoices:
            if i.ti_trip_id:
                invoice_obj_map[i.ti_trip_id] = i
            elif i.ti_consignment_id:
                matching_trips = [t.id for t in all_matching_trips if t.tr_consignmentnumber_id == i.ti_consignment_id]
                for mt_id in matching_trips:
                    if mt_id not in invoice_obj_map:
                        invoice_obj_map[mt_id] = i

        expenses = Driverexpense.objects.filter(trip_number__in=all_query_ids).select_related('de_expense_type')
        expense_map = {}
        for e in expenses:
            t_id = None
            s_key = str(e.trip_number).strip().upper() if e.trip_number else ""
            if s_key in trip_num_to_pk:
                t_id = trip_num_to_pk[s_key]
            elif s_key.isdigit():
                t_id = int(s_key)
            if t_id and t_id in trip_id_to_pk: expense_map.setdefault(t_id, []).append(e)

        va_map = {va.va_enquirynumber_id: va for va in Vehicle_allotmentInfo.objects.filter(
            va_enquirynumber_id__in=[t.tr_enquirynumber_id for t in all_matching_trips if
                                     t.tr_enquirynumber_id]).select_related('va_vendor')}
        vendor_ids = set(a.va_vendor_id for a in va_map.values() if a.va_vendor_id)

        bill_no_map = {}
        for b in MarketBillInfo.objects.all().only('mb_bill_no', 'mb_selected_trips', 'mb_total_cost'):
            if b.mb_selected_trips:
                for tid in [tid.strip() for tid in b.mb_selected_trips.split(',') if tid.strip()]:
                    try:
                        bill_no_map[int(tid)] = b
                    except:
                        pass
                    bill_no_map[str(tid).strip().upper()] = b

        attached_bill_map = {}
        for b in AttachedBillInfo.objects.all().only('ab_bill_no', 'ab_selected_trips', 'ab_buy_cost',
                                                     'ab_total_km_run'):
            if b.ab_selected_trips:
                for tid in [tid.strip() for tid in b.ab_selected_trips.split(',') if tid.strip()]:
                    try:
                        attached_bill_map[int(tid)] = b
                    except:
                        pass
                    attached_bill_map[str(tid).strip().upper()] = b

        # --- Calculate Fuel Proration and Salary for OWN vehicles on this page ---
        fuel_lookup, salary_lookup = calculate_own_vehicle_fuel_and_salary(
            all_matching_trips, date_from=from_date, date_to=to_date
        )

        # Calculate P&L for current page
        final_data_rows = []
        for idx, trip in enumerate(all_matching_trips, start=start + 1):
            inv = invoice_obj_map.get(trip.id)
            trip_expenses = expense_map.get(trip.id, [])
            va_info = va_map.get(trip.tr_enquirynumber_id)
            ab_bill = attached_bill_map.get(trip.id) or (
                attached_bill_map.get(str(trip.tr_tripnumber).strip().upper()) if trip.tr_tripnumber else None)
            mb_bill = bill_no_map.get(trip.id) or (
                bill_no_map.get(str(trip.tr_tripnumber).strip().upper()) if trip.tr_tripnumber else None)

            try:
                # Use None as default so get_trip_pl_data falls back to expense records
                # when no prorated fuel is available (non-OWN vehicles etc.)
                prorated_fuel_val = fuel_lookup.get(trip.id, None)
                prorated_salary_val = salary_lookup.get(trip.id, None)
                selling, buying, profit, profit_pct, disp_date = get_trip_pl_data(
                    trip, inv, trip_expenses, va_info, ab_bill, mb_bill,
                    prorated_fuel=prorated_fuel_val, prorated_salary=prorated_salary_val
                )
            except Exception as e:
                print(f"Error calculating P&L for trip {trip.id}: {e}")
                selling = buying = profit = profit_pct = 0.0
                disp_date = ""

            final_data_rows.append([
                idx,
                disp_date,
                safe_str(trip.tr_consignmentnumber.co_consignmentnumber) if trip.tr_consignmentnumber else "",
                safe_str(trip.tr_enquirynumber.en_customername) if trip.tr_enquirynumber else "",
                safe_str(trip.tr_departedlocation),
                safe_str(trip.tr_reportedlocation),
                safe_str(trip.tr_vehiclesource),
                safe_str(trip.tr_vehiclenumber),
                safe_str(trip.tr_vehicletype_placed or trip.tr_vehicletype),
                round(selling, 2),
                round(buying, 2),
                round(profit, 2),
                f"{round(profit_pct, 2)}%"
            ])

        return JsonResponse({
            'draw': draw,
            'recordsTotal': records_total,
            'recordsFiltered': records_filtered,
            'data': final_data_rows,
        })
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(error_msg)
        return JsonResponse({
            'error': str(e),
            'traceback': error_msg,
            'draw': safe_int(request.GET.get('draw'), 1),
            'recordsTotal': 0,
            'recordsFiltered': 0,
            'data': [],
        }, status=200)


@login_required(login_url='/')
def customerwise_pl_report_view(request):
    first_name = request.session.get('first_name')
    if request.method == "POST":
        form = DmrForm(request.POST)
    else:
        form = DmrForm()

    branch_id = request.POST.get('branch')
    trip_category_id = request.POST.get('trip_category')
    customer_id = request.POST.get('customer')
    vehicle_source_id = request.POST.get('vehicle_source')
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')
    selected_year = request.POST.get('year')

    from ..models import (
        TripdetailInfo, Location_info, OwnershipInfo, Trip_category_info,
        Tr_triptype_Info, CustomerInfo, Driverexpense, MarketBillInfo,
        Vehicle_allotmentInfo, TransInvoiceInfo, AttachedBillInfo, VendorratemasterInfo1
    )
    from django.db.models import Q

    headers = [
        "SNo", "Trip Date", "Cnote", "Customer Name", "From", "To",
        "Vehicle Source", "Vehicle No", "Veh Type", "Revenue",
        "Expenses", "Profit", "Profit %"
    ]

    all_customers = CustomerInfo.objects.filter(cu_name__icontains='(T)').order_by('cu_name')

    return render(request, "asset_mgt_app/customerwise_pl_report.html", {
        'first_name': first_name,
        'form': form,
        'headers': headers,
        'data_rows': [],  # AJAX populated
        'branch_id': int(branch_id) if branch_id else None,
        'trip_category_id': int(trip_category_id) if trip_category_id else None,
        'customer_id': int(customer_id) if customer_id else None,
        'vehicle_source_id': int(vehicle_source_id) if vehicle_source_id else None,
        'from_date': from_date,
        'to_date': to_date,
        'selected_year': selected_year,
        'all_trip_categories': Tr_triptype_Info.objects.all().order_by('tr_trip_type'),
        'all_branches': [
            {'id': b.id, 'name': b.loc_name.replace('BVM ', '').strip()}
            for b in Location_info.objects.filter(id__in=[1, 2]).order_by('loc_name')
        ],

        'all_customers': all_customers,
        'all_vehicle_sources': OwnershipInfo.objects.all(),
    })


@login_required(login_url='login_page')
def location_pl_report_view(request):
    first_name = request.session.get('first_name')
    from ..models import TripdetailInfo, TransInvoiceInfo, Driverexpense, VehiclemasterInfo, VehicletypeInfo, \
        MarketBillInfo, ConsignmentgoodsInfo, Vehicle_allotmentInfo, Location_info, VendorratemasterInfo1, \
        AttachedBillInfo
    from ..forms import DmrForm

    form = DmrForm(request.GET or None)

    branch_id = request.GET.get('branch', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    branch_name = 'All Branches'
    if branch_id:
        try:
            branch_obj = Location_info.objects.get(id=branch_id)
            branch_name = branch_obj.loc_name.replace('BVM ', '').strip()
        except:
            pass

    trips = TripdetailInfo.objects.filter(
        tc_financestatus_id__in=[7, 9]
    ).select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_consignmentnumber'
    )

    if branch_id:
        if branch_id == '1':  # BLR
            trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='BLR')
        elif branch_id == '2':  # MAA
            trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='MAA')

    if date_from and date_to:
        trips = trips.filter(tr_departeddate__date__range=[date_from, date_to])
    elif date_from:
        trips = trips.filter(tr_departeddate__date__gte=date_from)
    elif date_to:
        trips = trips.filter(tr_departeddate__date__lte=date_to)

    trips_list = list(trips)
    trip_ids = [t.id for t in trips_list]
    trip_enquiries = [t.tr_enquirynumber_id for t in trips_list]

    invoices = TransInvoiceInfo.objects.filter(ti_trip_id__in=trip_ids)
    invoice_obj_map = {i.ti_trip_id: i for i in invoices}

    trip_id_to_pk = {t.id: t.id for t in trips_list}
    trip_num_to_pk = {str(t.tr_tripnumber).strip().upper(): t.id for t in trips_list if t.tr_tripnumber}
    # Collect all possible search strings (IDs and Trip Numbers - including raw and upper for robust matching)
    all_query_ids = [str(t.id) for t in trips_list] + [str(t.tr_tripnumber).strip() for t in trips_list if
                                                       t.tr_tripnumber] + \
                    [str(t.tr_tripnumber).strip().upper() for t in trips_list if t.tr_tripnumber]

    expenses = Driverexpense.objects.filter(trip_number__in=all_query_ids).select_related('de_expense_type')
    expense_map = {}
    for e in expenses:
        t_id = None
        search_key = str(e.trip_number).strip().upper() if e.trip_number else ""
        if search_key in trip_num_to_pk:
            t_id = trip_num_to_pk[search_key]
        elif search_key.isdigit():
            t_id = int(search_key)
        if t_id and t_id in trip_id_to_pk:
            expense_map.setdefault(t_id, []).append(e)

    # VENDOR BILLS (MARKET & ATTACHED)
    all_bills = MarketBillInfo.objects.all().only('mb_bill_no', 'mb_selected_trips', 'mb_total_cost')
    bill_no_map = {}
    for b in all_bills:
        if b.mb_selected_trips:
            ids = [tid.strip() for tid in b.mb_selected_trips.split(',') if tid.strip()]
            for tid in ids:
                try:
                    bill_no_map[int(tid)] = b
                except:
                    pass

    attached_bill_map = {}
    all_attached_bills = AttachedBillInfo.objects.all().only('ab_bill_no', 'ab_selected_trips', 'ab_buy_cost',
                                                             'ab_total_km_run')
    for b in all_attached_bills:
        if b.ab_selected_trips:
            ids = [tid.strip() for tid in b.ab_selected_trips.split(',') if tid.strip()]
            for tid in ids:
                try:
                    attached_bill_map[int(tid)] = b
                except ValueError:
                    attached_bill_map[tid] = b

    # ALLOTMENTS & RATES
    va_map = {
        va.va_enquirynumber_id: va
        for va in
        Vehicle_allotmentInfo.objects.filter(va_enquirynumber_id__in=trip_enquiries).select_related('va_vendor')
    }

    vendor_ids = set(a.va_vendor_id for a in va_map.values() if a.va_vendor_id)
    rates = VendorratemasterInfo1.objects.filter(vr1_vendor_id__in=vendor_ids).values(
        'vr1_fromlocation_id', 'vr1_tolocation_id', 'vr1_vehicletype_id', 'vr1_vendor_id', 'vr1_rate'
    )
    rate_map = {
        (r['vr1_fromlocation_id'], r['vr1_tolocation_id'], r['vr1_vehicletype_id'], r['vr1_vendor_id']): r['vr1_rate']
        for r in rates
    }

    veh_nos = [t.tr_vehiclenumber for t in trips_list if t.tr_vehiclenumber]
    veh_vendor_map = {
        v.vm_registrationnumber.strip(): v.vm_vendor
        for v in VehiclemasterInfo.objects.filter(vm_registrationnumber__in=veh_nos).select_related('vm_vendor')
        if v.vm_registrationnumber
    }

    own_rev = 0.0
    att_rev = 0.0
    mkt_rev = 0.0

    own_op_exp = 0.0
    att_op_exp = 0.0
    mkt_op_exp = 0.0

    def safe_num(val):
        try:
            if val is None: return 0.0
            return float(val)
        except:
            return 0.0

    # -------------------------------
    # PRE-CALCULATE PRORATED FUEL COST PER TRIP
    # Logic: For each vehicle, get all fuel fills ordered by date.
    # Between consecutive fills, count how many trips ran in that period.
    # Prorate: fuel_fill_cost / trips_in_period -> each trip in that period.
    # -------------------------------
    from ..models import Fuelfillinginfo
    from django.db.models import Sum
    import datetime

    # Group trips by vehicle number
    vehicle_trips_map = {}  # {veh_no: [trip, ...]}
    for t in trips_list:
        veh = str(t.tr_vehiclenumber).strip() if t.tr_vehiclenumber else None
        if veh:
            vehicle_trips_map.setdefault(veh, []).append(t)

    fuel_lookup = {}  # {trip.id: prorated_fuel_cost}

    for veh_no, veh_trips in vehicle_trips_map.items():
        if not veh_trips:
            continue

        # Determine the date range of the trips shown in this report
        trip_dates = []
        for t in veh_trips:
            d = t.tr_departeddate or t.tr_created_at
            if d:
                trip_dates.append(d.date())

        if trip_dates:
            min_date = min(trip_dates)
            max_date = max(trip_dates)

            fuel_records = Fuelfillinginfo.objects.filter(
                ff_vehicle_num__vm_registrationnumber__iexact=veh_no,
                ff_date__gte=min_date,
                ff_date__lte=max_date
            ).aggregate(total_fuel=Sum('ff_fuel_price'))

            total_fuel = safe_num(fuel_records.get('total_fuel'))
        else:
            total_fuel = 0.0

        if len(veh_trips) > 0 and total_fuel > 0:
            prorated = total_fuel / len(veh_trips)
            for t in veh_trips:
                fuel_lookup[t.id] = prorated

    for trip in trips_list:
        v_source = trip.tr_vehiclesource_id
        inv = invoice_obj_map.get(trip.id)

        if v_source == 1:
            selling_trip = (safe_num(inv.ti_transportation_charges) if inv else (
                safe_num(trip.tc_tripcost) if getattr(trip, 'tc_tripcost_check', True) else 0.0))
            selling_toll = (safe_num(inv.ti_toll_charges) if inv else (
                safe_num(trip.tc_tollcost) if getattr(trip, 'tc_tollcost_check', True) else 0.0))
            selling_parking = (safe_num(inv.ti_parking_charges) if inv else (
                safe_num(trip.tc_parkingcost) if getattr(trip, 'tc_parkingcost_check', True) else 0.0))
            selling_loading = (safe_num(inv.ti_loading_charges) if inv else (
                safe_num(trip.tc_loadingcost) if getattr(trip, 'tc_loadingcost_check', True) else 0.0))
            selling_unloading = (safe_num(inv.ti_unloading_charges) if inv else (
                safe_num(trip.tc_unloadingcost) if getattr(trip, 'tc_unloadingcost_check', True) else 0.0))
            selling_weighment = (safe_num(inv.ti_weighment_charges) if inv else (
                safe_num(trip.tc_weighmentcost) if getattr(trip, 'tc_weighmentcost_check', True) else 0.0))
            selling_handling = (safe_num(inv.ti_handling_charges) if inv else (
                safe_num(trip.tc_handlingcost) if getattr(trip, 'tc_handlingcost_check', True) else 0.0))
            halting_days = safe_num(trip.tc_no_of_days_halting)
            if inv:
                selling_halting = safe_num(inv.ti_halting_charges)
            elif getattr(trip, 'tc_haltingcost_check', False) or getattr(trip, 'tc_total_halting_cost_check', False):
                selling_halting = safe_num(trip.tc_haltingcost) * halting_days
            else:
                selling_halting = 0.0

            selling_supervisor = (
                safe_num(trip.tc_supervisorcost) if getattr(trip, 'tc_supervisorcost_check', True) else 0.0)
            selling_rto = (safe_num(trip.tc_rtocost) if getattr(trip, 'tc_rtocost_check', True) else 0.0)
            selling_beta = (safe_num(trip.tc_betacost) if getattr(trip, 'tc_betacost_check', True) else 0.0)
            selling_cancellation = (safe_num(inv.ti_cancellation_charges) if inv else (
                safe_num(trip.tc_cancellation) if getattr(trip, 'tc_cancellation_check', True) else 0.0))

            selling_total = (
                    selling_trip + selling_toll + selling_parking + selling_loading +
                    selling_unloading + selling_weighment + selling_handling +
                    selling_halting + selling_supervisor + selling_rto +
                    selling_beta + selling_cancellation
            )
            own_rev += selling_total
        elif v_source in [2, 3]:
            selling_trip = (safe_num(inv.ti_transportation_charges) if inv else (
                safe_num(trip.tc_tripcost) if getattr(trip, 'tc_tripcost_check', True) else 0.0))
            selling_toll = (safe_num(inv.ti_toll_charges) if inv else (
                safe_num(trip.tc_tollcost) if getattr(trip, 'tc_tollcost_check', True) else 0.0))
            selling_parking = (safe_num(inv.ti_parking_charges) if inv else (
                safe_num(trip.tc_parkingcost) if getattr(trip, 'tc_parkingcost_check', True) else 0.0))
            selling_loading = (safe_num(inv.ti_loading_charges) if inv else (
                safe_num(trip.tc_loadingcost) if getattr(trip, 'tc_loadingcost_check', True) else 0.0))
            selling_unloading = (safe_num(inv.ti_unloading_charges) if inv else (
                safe_num(trip.tc_unloadingcost) if getattr(trip, 'tc_unloadingcost_check', True) else 0.0))
            selling_weighment = (safe_num(inv.ti_weighment_charges) if inv else (
                safe_num(trip.tc_weighmentcost) if getattr(trip, 'tc_weighmentcost_check', True) else 0.0))
            selling_handling = (safe_num(inv.ti_handling_charges) if inv else (
                safe_num(trip.tc_handlingcost) if getattr(trip, 'tc_handlingcost_check', True) else 0.0))
            halting_days = safe_num(trip.tc_no_of_days_halting)
            if inv:
                selling_halting = safe_num(inv.ti_halting_charges)
            elif getattr(trip, 'tc_haltingcost_check', False) or getattr(trip, 'tc_total_halting_cost_check', False):
                selling_halting = safe_num(trip.tc_haltingcost) * halting_days
            else:
                selling_halting = 0.0

            selling_supervisor = (
                safe_num(trip.tc_supervisorcost) if getattr(trip, 'tc_supervisorcost_check', True) else 0.0)
            selling_rto = (safe_num(trip.tc_rtocost) if getattr(trip, 'tc_rtocost_check', True) else 0.0)
            selling_beta = (safe_num(trip.tc_betacost) if getattr(trip, 'tc_betacost_check', True) else 0.0)
            selling_cancellation = (safe_num(inv.ti_cancellation_charges) if inv else (
                safe_num(trip.tc_cancellation) if getattr(trip, 'tc_cancellation_check', True) else 0.0))

            selling_total = (
                    selling_trip + selling_toll + selling_parking + selling_loading +
                    selling_unloading + selling_weighment + selling_handling +
                    selling_halting + selling_supervisor + selling_rto +
                    selling_beta + selling_cancellation
            )

            if v_source == 2:
                att_rev += selling_total
            else:
                mkt_rev += selling_total

        if v_source == 1:
            t_exp = 0.0
            toll_expense, fuel_expense, driver_salary, acting_driver, driver_bata, parking_expense, loading_expense, unloading_expense, weighment_expense, handling_expense, vehicle_hire = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
            for e in expense_map.get(trip.id, []):
                extype = str(e.de_expense_type).lower()
                parking_val = safe_num(e.de_parkingcost)
                loading_val = safe_num(e.de_loadingcost)
                unloading_val = safe_num(e.de_unloadingcost)
                weighment_val = safe_num(e.de_weighmentcost)
                handling_val = safe_num(e.de_supervisorcost)
                toll_val = safe_num(e.de_rtocost)
                bata_val = safe_num(e.de_battacost)

                parking_expense += parking_val
                loading_expense += loading_val
                unloading_expense += unloading_val
                weighment_expense += weighment_val
                handling_expense += handling_val
                toll_expense += toll_val
                driver_bata += bata_val

                cost = safe_num(e.de_total_cost)
                if 'fuel' in extype or 'diesel' in extype:
                    # Fuel cost is always pulled directly from Fuelfillinginfo database to prevent double counting
                    pass
                elif 'salary' in extype:
                    driver_salary += cost
                elif 'acting' in extype:
                    acting_driver += cost
                elif 'hire' in extype or 'freight' in extype:
                    vehicle_hire += cost
                elif 'toll' in extype:
                    if not toll_val: toll_expense += cost
                elif 'parking' in extype:
                    if not parking_val: parking_expense += cost
                elif 'loading' in extype:
                    if not loading_val: loading_expense += cost
                elif 'unloading' in extype:
                    if not unloading_val: unloading_expense += cost
                elif 'weighment' in extype:
                    if not weighment_val: weighment_expense += cost
                elif 'bata' in extype or 'batta' in extype:
                    if not bata_val: driver_bata += cost
                elif 'handling' in extype:
                    if not handling_val: handling_expense += cost

            # --- Fuel Cost: prorated from Fuelfillinginfo (pre-calculated above) ---
            fuel_expense = round(fuel_lookup.get(trip.id, 0.0), 2)

            t_exp = (driver_salary + fuel_expense + acting_driver + driver_bata + toll_expense + parking_expense +
                     loading_expense + unloading_expense + weighment_expense + handling_expense + vehicle_hire)
            own_op_exp += t_exp

        elif v_source == 2:  # ATTACHED
            # 1. Base Trip Cost (Pro-rated from Bill or Allotment)
            va_info = va_map.get(trip.tr_enquirynumber_id)
            reported_km = safe_num(trip.tr_reportedkm_delivery or trip.tr_reportedkm)
            departed_km = safe_num(trip.tr_departedkm)
            km_run = max(0, reported_km - departed_km)

            ab_bill = attached_bill_map.get(trip.id) or (
                attached_bill_map.get(str(trip.tr_tripnumber).strip()) if trip.tr_tripnumber else None)
            if ab_bill:
                ab_buy_cost = safe_num(ab_bill.ab_buy_cost)
                ab_total_km = safe_num(ab_bill.ab_total_km_run)
                ab_rate = (ab_buy_cost / ab_total_km) if ab_total_km > 0 else 0
                buying_trip_cost = round(ab_rate * km_run, 2)
            else:
                buying_trip_cost = (
                    safe_num(getattr(va_info, 'va_specialbuy', 0)) or
                    safe_num(getattr(va_info, 'va_standardbuy', 0))
                    if va_info else 0
                )

            # 2. Driver Settlement Expenses
            buy_loading = buy_unloading = buy_weighment = buy_aai = 0.0
            buy_toll = safe_num(trip.tc_tollcost)
            buy_halting = buy_handling = buy_parking = buy_rto = buy_batta = 0.0

            for e in expense_map.get(trip.id, []):
                buy_loading += safe_num(e.de_loadingcost)
                buy_unloading += safe_num(e.de_unloadingcost)
                buy_weighment += safe_num(e.de_weighmentcost)
                buy_handling += safe_num(e.de_supervisorcost)
                buy_parking += safe_num(e.de_parkingcost)
                buy_rto += safe_num(e.de_rtocost)
                buy_batta += safe_num(e.de_battacost)

                exp_type_str = str(e.de_expense_type).lower() if e.de_expense_type else ""
                cost_val = safe_num(e.de_total_cost)

                if "toll" in exp_type_str and not ab_bill:
                    if not e.de_rtocost: buy_toll += cost_val
                elif "halting" in exp_type_str:
                    buy_halting += cost_val
                elif "parking" in exp_type_str and not e.de_parkingcost:
                    buy_parking += cost_val
                elif "loading" in exp_type_str and not e.de_loadingcost:
                    buy_loading += cost_val
                elif "unloading" in exp_type_str and not e.de_unloadingcost:
                    buy_unloading += cost_val
                elif "weighment" in exp_type_str and not e.de_weighmentcost:
                    buy_weighment += cost_val
                elif ("bata" in exp_type_str or "batta" in exp_type_str) and not e.de_battacost:
                    buy_batta += cost_val

            buying_total = (
                    buying_trip_cost + buy_toll + buy_loading + buy_unloading +
                    buy_weighment + buy_halting + buy_handling + buy_parking +
                    buy_rto + buy_batta
            )
            att_op_exp += buying_total

        elif v_source == 3:  # MARKET - use actual Market Bill total as expense
            mb_obj = bill_no_map.get(trip.id)
            if mb_obj:
                buying_total = safe_num(mb_obj.mb_total_cost)
                mkt_op_exp += buying_total

    months_count = 1
    if date_from and date_to:
        from datetime import datetime
        try:
            d_from = datetime.strptime(date_from, "%Y-%m-%d")
            d_to = datetime.strptime(date_to, "%Y-%m-%d")
            days_diff = max(1, (d_to - d_from).days)
            months_count = max(1.0, days_diff / 30.0)
        except:
            months_count = 1

    own_trips = [t for t in trips_list if t.tr_vehiclesource_id == 1]
    unique_veh_nos = set(trip.tr_vehiclenumber for trip in own_trips if trip.tr_vehiclenumber)

    vehicle_map = {v.vm_registrationnumber: v for v in VehiclemasterInfo.objects.all()}
    insurance = 0.0
    road_tax = 0.0
    permit = 0.0
    maintenance_cost = 0.0

    for vno in unique_veh_nos:
        v_obj = vehicle_map.get(vno)
        if v_obj:
            insurance += safe_num(v_obj.vm_premium) / 12.0 * months_count
            road_tax += safe_num(v_obj.vm_roadtaxamount) / 12.0 * months_count
            permit += safe_num(v_obj.vm_permitamount) / 12.0 * months_count

    from ..sub_models.maintenance_bill_mod import MaintenanceBillInfo
    m_bills = MaintenanceBillInfo.objects.filter(mnb_maintenance__mi_vehicle__vm_registrationnumber__in=unique_veh_nos)
    if date_from: m_bills = m_bills.filter(mnb_bill_date__gte=date_from)
    if date_to: m_bills = m_bills.filter(mnb_bill_date__lte=date_to)
    for mb in m_bills:
        maintenance_cost += safe_num(mb.mnb_total_amount)

    non_op_exp = insurance + road_tax + permit + maintenance_cost

    total_revenue = own_rev + att_rev + mkt_rev
    total_op_exp = own_op_exp + att_op_exp + mkt_op_exp
    gross_profit = total_revenue - total_op_exp
    gross_profit_pct = (gross_profit / total_revenue * 100.0) if total_revenue > 0 else 0.0

    net_profit = gross_profit - non_op_exp
    net_profit_pct = (net_profit / total_revenue * 100.0) if total_revenue > 0 else 0.0

    branch_name = None
    if branch_id:
        try:
            branch_name = Location_info.objects.get(id=branch_id).loc_name
        except:
            pass

    context = {
        'first_name': first_name,
        'form': form,
        'branch_id': branch_id,
        'branch_name': branch_name,
        'date_from': date_from,
        'date_to': date_to,
        'all_branches': [
            {'id': b.id, 'name': b.loc_name.replace('BVM ', '').strip()}
            for b in Location_info.objects.filter(id__in=[1, 2]).order_by('loc_name')
        ],
        'own_rev': round(own_rev, 2),
        'att_rev': round(att_rev, 2),
        'mkt_rev': round(mkt_rev, 2),
        'total_revenue': round(total_revenue, 2),
        'own_op_exp': round(own_op_exp, 2),
        'att_op_exp': round(att_op_exp, 2),
        'mkt_op_exp': round(mkt_op_exp, 2),
        'total_op_exp': round(total_op_exp, 2),
        'gross_profit': round(gross_profit, 2),
        'gross_profit_pct': round(gross_profit_pct, 2),
        'non_op_exp': round(non_op_exp, 2),
        'net_profit': round(net_profit, 2),
        'net_profit_pct': round(net_profit_pct, 2),
    }

    return render(request, "asset_mgt_app/location_pl_report.html", context)


# -------------------------
# TIME ANALYSIS REPORT
# -------------------------

# Helpers are now defined at the top of the file under TIME ANALYSIS REPORT HELPERS.


@login_required(login_url='login_page')
def time_analysis_report_view(request):
    first_name = request.session.get('first_name')

    if request.method == "POST":
        form = DmrForm(request.POST)
        customer_id = request.POST.get('dmr_customer')
        selected_month = request.POST.get('month')
        selected_year = request.POST.get('year')
        branch_id = request.POST.get('branch')
        vehicle_search = request.POST.get('vehicle_search', '').strip()
    else:
        form = DmrForm()
        customer_id = None
        # Default to current month and year for better performance
        today = timezone.localtime(timezone.now())
        selected_month = today.month
        selected_year = today.year
        branch_id = ''
        vehicle_search = ''

    # Initialize form with defaults if it's a GET request
    if request.method == "GET":
        form.fields['month'].initial = selected_month
        form.fields['year'].initial = selected_year

    # Ensure they are strings for the string-based comparisons below if needed,
    # but the filter logic works with both.
    # Actually, request.POST.get returns strings, so we normalize to strings for logic.
    selected_month = str(selected_month)
    selected_year = str(selected_year)

    trips = TripdetailInfo.objects.filter(tr_category_id=1).select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_consignmentnumber',
        'tr_vehicletype',
    ).only(
        'tr_vehiclenumber', 'tr_vehicletype__vt_vehicletype', 'tr_created_at', 'tr_departeddate', 'tr_loading_time',
        'tr_dock_in_time', 'tr_dock_out_time', 'tr_reporteddate', 'tr_departeddate_delivery',
        'tr_unloading_time', 'tr_reporteddate_pickup', 'tr_departeddate_pickup',
        'tr_enquirynumber__en_enquirynumber', 'tr_enquirynumber__en_customername__cu_name',
        'tr_enquirynumber__en_created_at', 'tr_enquirynumber__en_pickupdatetime',
        'tr_consignmentnumber__co_consignmentnumber', 'tr_consignmentnumber__co_created_at'
    )

    if customer_id:
        trips = trips.filter(tr_enquirynumber__en_customername_id=customer_id)

    if vehicle_search:
        trips = trips.filter(tr_vehiclenumber__icontains=vehicle_search)

    if selected_month and selected_month != '0':
        trips = trips.filter(
            Q(tr_created_at__month=selected_month) |
            Q(tr_departeddate__month=selected_month) |
            Q(tr_loading_time__month=selected_month)
        )

    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_created_at__year=selected_year) |
            Q(tr_departeddate__year=selected_year) |
            Q(tr_loading_time__year=selected_year)
        )

    if branch_id:
        try:
            b_id = int(branch_id)
            if b_id == 1:
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='BLR')
            elif b_id == 2:
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='MAA')
            elif b_id == 3:
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='PNY')
            elif b_id == 4:
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='HYD')
            else:
                loc = Location_info.objects.get(id=b_id)
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains=loc.loc_name)
        except (ValueError, Location_info.DoesNotExist):
            pass

    trips = trips.order_by('-tr_created_at')

    # Fetch vehicle allotment info for all related enquiries
    enquiry_ids = trips.values_list('tr_enquirynumber_id', flat=True).distinct()
    allotment_map = {}

    # Optimized allotment fetching
    allotments_qs = Vehicle_allotmentInfo.objects.filter(
        va_enquirynumber_id__in=enquiry_ids
    ).select_related('va_vehiclenumber').only(
        'va_enquirynumber_id', 'va_created_at', 'va_vehiclenumber_mkt',
        'va_vehiclenumber__vm_registrationnumber'
    )

    for va in allotments_qs:
        allotment_map.setdefault(va.va_enquirynumber_id, []).append(va)

    data_rows = []
    for idx, trip in enumerate(trips, start=1):
        enquiry = trip.tr_enquirynumber
        cons = trip.tr_consignmentnumber

        # Enquiry fields
        enquiry_no = safe_str(enquiry.en_enquirynumber) if enquiry else ""
        customer_name = safe_str(enquiry.en_customername) if enquiry else ""
        enquiry_created = enquiry.en_created_at if enquiry else None
        pickup_dt = enquiry.en_pickupdatetime if enquiry else None

        # Cnote fields
        cnote_no = safe_str(cons.co_consignmentnumber) if cons else ""
        cnote_created = cons.co_created_at if cons else None

        # Vehicle Allotment – Match with the specific vehicle for this trip
        veh_allotted_dt = None
        if enquiry:
            allotments = allotment_map.get(enquiry.id, [])
            trip_veh = safe_str(trip.tr_vehiclenumber).strip().upper()

            # Find the allotment that matches this trip's vehicle
            match_va = None
            for a in allotments:
                va_num = ""
                if a.va_vehiclenumber:
                    va_num = safe_str(a.va_vehiclenumber.vm_registrationnumber)
                else:
                    va_num = safe_str(a.va_vehiclenumber_mkt)

                if va_num.strip().upper() == trip_veh:
                    match_va = a
                    break

            if not match_va and allotments:
                # Fallback to first if only one allotment exists, or if no match found
                match_va = allotments[0]

            if match_va:
                veh_allotted_dt = match_va.va_created_at

        # ---- CALCULATIONS ----
        # 1. Booking Delay (How long after the requested pickup time was the enquiry actually created?)
        # Or Booking Lead Time? Usually, if enquiry is 12:01 and pickup is 12:00, delay is 1 min.
        booking_delay = _duration_str(pickup_dt, enquiry_created)

        # 2. Time taken for allotment = allotted dt - enquiry created dt
        time_for_allotment = _duration_str(enquiry_created, veh_allotted_dt)

        # 3. Time Taken for Cnote Entry = cnote created - veh allotted dt
        time_for_cnote = _duration_str(veh_allotted_dt, cnote_created)

        # 4. Trip Sheet Entry Time = trip created - veh allotted dt
        trip_created = trip.tr_created_at
        time_for_trip = _duration_str(veh_allotted_dt, trip_created)

        # ---- LOADING POINT TIMINGS ----
        veh_reported_loading = trip.tr_departeddate_pickup
        dock_in_loading = trip.tr_loading_time
        idle_loading = _duration_str(veh_reported_loading, dock_in_loading)
        dock_out_loading = trip.tr_dock_out_time
        loading_time = _duration_str(dock_in_loading, dock_out_loading)
        veh_started_loading = trip.tr_departeddate

        # ---- UNLOADING POINT TIMINGS ----
        veh_reported_unloading = trip.tr_reporteddate
        dock_in_unloading = trip.tr_departeddate_delivery
        idle_unloading = _duration_str(veh_reported_unloading, dock_in_unloading)
        dock_out_unloading = trip.tr_unloading_time
        unloading_time = _duration_str(dock_in_unloading, dock_out_unloading)
        veh_started_unloading = trip.tr_reporteddate_pickup

        data_rows.append([
            idx,
            enquiry_no,
            cnote_no,
            customer_name,
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype),
            _fmt_dt(enquiry_created),
            _fmt_dt(pickup_dt),
            _fmt_dt(veh_allotted_dt),
            time_for_allotment,
            _fmt_dt(cnote_created),
            time_for_cnote,
            _fmt_dt(trip_created),
            time_for_trip,
            _fmt_dt(veh_reported_loading),
            _fmt_dt(dock_in_loading),
            idle_loading,
            _fmt_dt(dock_out_loading),
            loading_time,
            _fmt_dt(veh_started_loading),
            _fmt_dt(veh_reported_unloading),
            _fmt_dt(dock_in_unloading),
            idle_unloading,
            _fmt_dt(dock_out_unloading),
            unloading_time,
            _fmt_dt(veh_started_unloading),
        ])

    all_vehicles = VehiclemasterInfo.objects.filter(
        vm_ownership_id__in=[1, 2]
    ).order_by('vm_registrationnumber')

    return render(request, "asset_mgt_app/time_analysis_report.html", {
        'first_name': first_name,
        'form': form,
        'headers': TIME_ANALYSIS_HEADERS,
        'data_rows': data_rows,
        'customer_id': int(customer_id) if customer_id else None,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'branch_id': branch_id,
        'vehicle_search': vehicle_search,
        'all_vehicles': all_vehicles,
    })


@login_required(login_url='/')
def mileage_report_view(request):
    first_name = request.session.get('first_name')
    if request.method == "POST":
        form = DmrForm(request.POST)
    else:
        form = DmrForm()

    branch_id = request.POST.get('branch')
    from_date = request.POST.get('from_date')
    to_date = request.POST.get('to_date')

    from ..models import VehiclemasterInfo, OwnershipInfo, Location_info
    from ..sub_models.fuelfilling_mod import Fuelfillinginfo
    from django.db.models import Q, Max, Min, Sum

    # Only show Own vehicles (vm_ownership_id=1)
    vehicles = VehiclemasterInfo.objects.filter(vm_ownership_id=1)

    # Filter by Branch based on registration number prefix
    if branch_id:
        try:
            b_id = int(branch_id)
            if b_id == 1:  # BLR -> KA
                vehicles = vehicles.filter(vm_registrationnumber__icontains='KA')
            elif b_id == 2:  # MAA -> TN
                vehicles = vehicles.filter(vm_registrationnumber__icontains='TN')
        except (ValueError, Location_info.DoesNotExist):
            pass

    data_rows = []
    idx = 1
    for vehicle in vehicles:
        v_fuel_records = Fuelfillinginfo.objects.filter(ff_vehicle_num=vehicle.id)
        if from_date:
            v_fuel_records = v_fuel_records.filter(ff_date__gte=from_date)
        if to_date:
            v_fuel_records = v_fuel_records.filter(ff_date__lte=to_date)

        v_fuel_records = v_fuel_records.order_by('ff_date', 'ff_odometer_reading')

        if not v_fuel_records.exists():
            continue

        first_rec = v_fuel_records.first()
        last_rec = v_fuel_records.last()

        km_start = first_rec.ff_odometer_reading or 0
        km_end = last_rec.ff_odometer_reading or 0
        total_km = km_end - km_start

        # total_ltrs = sum of all liters in range EXCEPT the last record's liters
        # as the last record's fuel is consumed AFTER the last odometer reading in this range.
        total_ltrs = 0.0
        if v_fuel_records.count() > 1:
            all_but_last = v_fuel_records.exclude(id=last_rec.id)
            total_ltrs = all_but_last.aggregate(Sum('ff_filled_ltr'))['ff_filled_ltr__sum'] or 0.0
        else:
            # If only one record, we can't calculate mileage, so we show the fill but 0 km
            total_ltrs = 0.0  # Or potentially first_rec.ff_filled_ltr if we want to show it, but mileage will be 0.
            # Usually for a period report, distance and fuel should correspond to a valid delta.

        std_mileage = safe_num(vehicle.vm_millage)
        actual_mileage = (total_km / total_ltrs) if total_ltrs > 0 else 0

        data_rows.append([
            idx,
            vehicle.vm_registrationnumber,
            safe_str(vehicle.vm_vehicletype),
            km_start,
            km_end,
            total_km,
            round(total_ltrs, 2),
            round(std_mileage, 2),
            round(actual_mileage, 2)
        ])
        idx += 1

    headers = [
        "SNo", "Vehicle No", "Vehicle Type", "KM Start", "KM End",
        "Total KM", "Fuel Ltrs", "Standard Mileage", "Actual Mileage"
    ]

    return render(request, "asset_mgt_app/mileage_report.html", {
        'first_name': first_name,
        'form': form,
        'headers': headers,
        'data_rows': data_rows,
        'branch_id': int(branch_id) if branch_id else None,
        'from_date': from_date,
        'to_date': to_date,
        'all_branches': Location_info.objects.filter(id__in=[1, 2]).order_by('loc_name'),
    })


from ..sub_models.maintenance_mod import MaintenanceInfo
from ..sub_models.branch_mod import Branch


@login_required(login_url='login_page')
def vendor_bills_pending_maintenance_report_view(request):
    first_name = request.user.first_name

    branch_id = ""
    from_date = ""
    to_date = ""
    vendor_name = ""

    if request.method == "POST":
        branch_id = request.POST.get('branch', '')
        from_date = request.POST.get('from_date', '')
        to_date = request.POST.get('to_date', '')
        vendor_name = request.POST.get('vendor_name', '')

    all_branches = Branch.objects.all().order_by('branch')

    # Get distinct vendor names (technicians) that are already present in pending bills
    all_vendors = MaintenanceInfo.objects.filter(mi_technician__isnull=False).exclude(
        mi_technician__exact='').values_list('mi_technician', flat=True).distinct().order_by('mi_technician')

    # Base query: Finance Approved (3) but have no associated bill
    maintenance_records = MaintenanceInfo.objects.filter(
        mi_approval_status_id=3,
        bills_v1__isnull=True
    ).select_related('mi_vehicle', 'mi_vehicle__vm_vehicletype').order_by('-mi_est_delivery', '-mi_created_at')

    # Apply Filters
    if branch_id:
        maintenance_records = maintenance_records.filter(mi_location_id=branch_id)
    if from_date:
        maintenance_records = maintenance_records.filter(mi_created_at__date__gte=from_date)
    if to_date:
        maintenance_records = maintenance_records.filter(mi_created_at__date__lte=to_date)
    if vendor_name:
        maintenance_records = maintenance_records.filter(mi_technician__icontains=vendor_name)

    data_rows = []

    for idx, record in enumerate(maintenance_records, start=1):
        vehicle = record.mi_vehicle
        vehicle_no = vehicle.vm_registrationnumber if vehicle else ""
        veh_type = vehicle.vm_vehicletype.vt_vehicletype if vehicle and vehicle.vm_vehicletype else ""

        data_rows.append({
            's_no': idx,
            'job_card_no': record.mi_job_card_no,
            'vehicle_no': vehicle_no,
            'veh_type': veh_type,
            'service_type': record.mi_service_type,
            'est_delivery': record.mi_est_delivery,
            'vendor_name': record.mi_technician
        })

    return render(request, "asset_mgt_app/vendor_bills_pending_maintenance_report.html", {
        'first_name': first_name,
        'data_rows': data_rows,
        'all_branches': all_branches,
        'selected_branch_id': branch_id,
        'from_date': from_date,
        'to_date': to_date,
        'vendor_name': vendor_name,
        'all_vendors': all_vendors,
    })


from ..sub_models.tripdetail_mod import TripdetailInfo
from ..sub_models.vehicle_allotment_mod import Vehicle_allotmentInfo
from ..sub_models.market_bill_mod import MarketBillInfo
from ..sub_models.vendor_info_mod import Vendor_info
from ..sub_models.location_info_mod import Location_info


@login_required(login_url='login_page')
def vendor_bills_pending_mkt_att_report_view(request):
    title = "Vendor Bills Pending Report MKT/ATT"
    branch_param = request.GET.get('branch', '')
    from_date_param = request.GET.get('from_date', '')
    to_date_param = request.GET.get('to_date', '')
    vendor_param = request.GET.get('vendor_name', '')
    veh_source_param = request.GET.get('veh_source', '')

    # Settle finance status ID and Market ownership ID
    settled_status_id = 7
    market_ownership_id = 3

    trip_filters = Q(tc_financestatus_id=settled_status_id)

    # Branch filter based on user's branch
    if branch_param:
        trip_filters &= Q(tr_updated_by__user_extinfo__emp_branch_id=branch_param)

    # Date filter on Trip Date (Departed Date)
    if from_date_param:
        from_date_obj = datetime.strptime(from_date_param, '%Y-%m-%d').date()
        trip_filters &= Q(tr_departeddate__date__gte=from_date_obj)
    if to_date_param:
        to_date_obj = datetime.strptime(to_date_param, '%Y-%m-%d').date()
        trip_filters &= Q(tr_departeddate__date__lte=to_date_obj)

    # Vendor filter - via Allotment
    if vendor_param:
        vendor_enquiries = Vehicle_allotmentInfo.objects.filter(va_vendor_id=vendor_param).values_list(
            'va_enquirynumber_id', flat=True)
        trip_filters &= Q(tr_enquirynumber_id__in=list(vendor_enquiries))

    if veh_source_param:
        trip_filters &= Q(tr_vehiclesource_id=veh_source_param)
    else:
        # By default, only show Market and Attached pending trips
        trip_filters &= Q(tr_vehiclesource_id__in=[2, 3])

    # Exclude already billed trips — market trips via MarketBillInfo, attached trips via AttachedBillInfo
    # Robustly collect market billed trip info (mb_selected_trips usually has IDs, but handle trip numbers variant too)
    market_billed_trip_ids = set()
    market_billed_trip_numbers = set()
    for bill in MarketBillInfo.objects.exclude(mb_selected_trips__isnull=True).exclude(mb_selected_trips=''):
        for tid in bill.mb_selected_trips.split(','):
            tid = tid.strip()
            if not tid: continue
            if tid.isdigit():
                market_billed_trip_ids.add(int(tid))
            else:
                market_billed_trip_numbers.add(tid)

    if market_billed_trip_numbers:
        resolved_market_ids = set(
            TripdetailInfo.objects.filter(
                tr_tripnumber__in=market_billed_trip_numbers
            ).values_list('id', flat=True)
        )
        market_billed_trip_ids.update(resolved_market_ids)

    # Collect billed attached trip numbers (ab_selected_trips stores trip numbers, NOT integer IDs)
    attached_billed_trip_numbers = set()
    for bill in AttachedBillInfo.objects.exclude(ab_selected_trips__isnull=True).exclude(ab_selected_trips=''):
        for tno in bill.ab_selected_trips.split(','):
            tno = tno.strip()
            if tno:
                attached_billed_trip_numbers.add(tno)

    # Resolve trip numbers to integer IDs for fast exclusion
    attached_billed_trip_ids = set(
        TripdetailInfo.objects.filter(
            tr_tripnumber__in=attached_billed_trip_numbers
        ).values_list('id', flat=True)
    )

    trips = list(TripdetailInfo.objects.filter(trip_filters).select_related(
        'tr_enquirynumber', 'tr_enquirynumber__en_customername', 'tr_enquirynumber__en_fromlocaion',
        'tr_enquirynumber__en_tolocation',
        'tr_consignmentnumber', 'tr_departedlocation', 'tr_reportedlocation',
        'tr_vehicletype', 'tr_vehiclesource',
        'tr_updated_by', 'tr_updated_by__user_extinfo__emp_branch'
    ))

    # Filter per source: market trips excluded via market bills, attached trips excluded via attached bills
    def is_billed(trip):
        src = trip.tr_vehiclesource_id
        if src == 3:  # Market
            return trip.id in market_billed_trip_ids
        elif src == 2:  # Attached
            return trip.id in attached_billed_trip_ids
        return False

    trips = [t for t in trips if not is_billed(t)]

    # Pre-fetch all relevant vehicle allotments in one query
    enquiry_ids = [t.tr_enquirynumber_id for t in trips if t.tr_enquirynumber_id]
    allotments = Vehicle_allotmentInfo.objects.filter(
        va_enquirynumber_id__in=enquiry_ids
    ).select_related('va_vendor', 'va_vehiclenumber')

    allotment_map = {}
    for a in allotments:
        veh_no = (a.va_vehiclenumber.vm_registrationnumber if a.va_vehiclenumber else (
                a.va_vehiclenumber_mkt or "")).lower().strip()
        key = (a.va_enquirynumber_id, veh_no)
        # Store first matched allotment for enquiry+vehicle pair
        if key not in allotment_map:
            allotment_map[key] = a

    # Fallback vendor map from VehiclemasterInfo.vm_vendor (used for attached vehicles)
    all_veh_nos = [t.tr_vehiclenumber for t in trips if t.tr_vehiclenumber]
    veh_vendor_map = {
        v.vm_registrationnumber.strip().lower(): v.vm_vendor
        for v in VehiclemasterInfo.objects.filter(
            vm_registrationnumber__in=all_veh_nos
        ).select_related('vm_vendor')
        if v.vm_vendor
    }

    data_rows = []

    for i, trip in enumerate(trips, start=1):
        veh_no_lower = (trip.tr_vehiclenumber or "").lower().strip()
        key = (trip.tr_enquirynumber_id, veh_no_lower)
        allotment = allotment_map.get(key)

        vendor_name = ""
        buy_cost = 0.0

        if allotment:
            vendor_name = allotment.va_vendor.vend_name if allotment.va_vendor else ""
            buy_cost = float(allotment.va_specialbuy) if allotment.va_specialbuy else float(
                allotment.va_standardbuy or 0.0)

        # Fallback: for attached vehicles, pull vendor from VehiclemasterInfo.vm_vendor
        if not vendor_name:
            v_vendor = veh_vendor_map.get(veh_no_lower)
            if v_vendor:
                vendor_name = v_vendor.vend_name

        # Apply vendor filter again in Python space as a strict safety check
        if vendor_param:
            allotment_vendor_id = str(allotment.va_vendor_id) if allotment and allotment.va_vendor else ""
            vm_vendor_obj = veh_vendor_map.get(veh_no_lower)
            vm_vendor_id = str(vm_vendor_obj.id) if vm_vendor_obj else ""
            if allotment_vendor_id != str(vendor_param) and vm_vendor_id != str(vendor_param):
                continue

        trip_date = trip.tr_departeddate.strftime('%Y-%m-%d') if trip.tr_departeddate else ""
        cnote = trip.tr_consignmentnumber.co_consignmentnumber if trip.tr_consignmentnumber else ""
        from_loc = str(trip.tr_departedlocation) if trip.tr_departedlocation else (
            str(trip.tr_enquirynumber.en_fromlocaion) if trip.tr_enquirynumber and trip.tr_enquirynumber.en_fromlocaion else "")
        to_loc = str(trip.tr_reportedlocation) if trip.tr_reportedlocation else (
            str(trip.tr_enquirynumber.en_tolocation) if trip.tr_enquirynumber and trip.tr_enquirynumber.en_tolocation else "")
        customer = str(
            trip.tr_enquirynumber.en_customername) if trip.tr_enquirynumber and trip.tr_enquirynumber.en_customername else ""
        veh_no = trip.tr_vehiclenumber if trip.tr_vehiclenumber else ""
        veh_type = str(trip.tr_vehicletype) if trip.tr_vehicletype else ""
        branch = ""
        if hasattr(trip.tr_updated_by, 'user_extinfo') and trip.tr_updated_by.user_extinfo.emp_branch:
            branch = trip.tr_updated_by.user_extinfo.emp_branch.loc_name
        veh_source = str(trip.tr_vehiclesource.ow_ownership) if trip.tr_vehiclesource else ""

        data_rows.append({
            's_no': i,
            'branch': branch,
            'veh_source': veh_source,
            'trip_date': trip_date,
            'cnote': cnote,
            'from_loc': from_loc,
            'to_loc': to_loc,
            'customer': customer,
            'veh_no': veh_no,
            'veh_type': veh_type,
            'vendor_name': vendor_name,
            'buy_cost': buy_cost
        })

    branches = Location_info.objects.filter(loc_name__in=['BVM MAA', 'BVM BLR']).order_by('loc_name')
    vendors = Vendor_info.objects.all().order_by('vend_name')

    context = {
        'title': title,
        'data_rows': data_rows,
        'branch_param': branch_param,
        'from_date_param': from_date_param,
        'to_date_param': to_date_param,
        'vendor_param': vendor_param,
        'veh_source_param': veh_source_param,
        'branches': branches,
        'vendors': vendors,
    }

    return render(request, "asset_mgt_app/vendor_bills_pending_mkt_att_report.html", context)


@login_required(login_url='login_page')
def transport_mis(request):
    first_name = request.session.get("first_name")
    selected_branch = request.GET.get("branch")
    selected_unit = request.GET.get("unit")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    selected_year = request.GET.get("year")
    selected_vehicle_source = request.GET.get("vehicle_source")

    if selected_year and selected_year != 'None':
        try:
            selected_year = int(selected_year)
        except ValueError:
            selected_year = date.today().year
    else:
        selected_year = date.today().year

    years = list(
        ExpenseExtinfo.objects.dates('exp_ext_expense_number__exp_service_start_date', 'year').values_list(
            'exp_ext_expense_number__exp_service_start_date__year', flat=True)
        .distinct()
    )

    branches = Location_info.objects.all()
    vehicle_sources = OwnershipInfo.objects.all()

    if selected_branch:
        units = UnitInfo.objects.filter(ui_branch_name__loc_name=selected_branch).values_list("unit_name",
                                                                                              flat=True).distinct()

    # BVM Trans ID is 2
    expenses_filter = {"exp_ext_expense_number__exp_business_id": 2}
    budget_filter = {"bf_company_id": 2}
    income_filter = {"ti_customer__cu_business_sol_id": 2}

    if selected_year:
        expenses_filter["exp_ext_expense_number__exp_service_start_date__year"] = selected_year
        budget_filter["bf_start_date_year__year"] = selected_year
        income_filter["ti_inv_date__year"] = selected_year

    if selected_branch:
        expenses_filter["exp_ext_branch__loc_name"] = selected_branch
        budget_filter["bf_location__loc_name"] = selected_branch
        income_filter["ti_trip__tr_updated_by__user_extinfo__emp_branch__loc_name"] = selected_branch

    if selected_unit:
        expenses_filter["exp_ext_unit__unit_name"] = selected_unit
        budget_filter["bf_unit_reference__unit_name"] = selected_unit

    if selected_vehicle_source:
        budget_filter["bf_vehicle_source__ow_ownership"] = selected_vehicle_source
        income_filter["ti_trip__tr_vehiclesource__ow_ownership"] = selected_vehicle_source

    if from_date:
        try:
            from_date_dt = datetime.strptime(from_date, "%Y-%m-%d")
            expenses_filter["exp_ext_expense_number__exp_service_start_date__gte"] = from_date_dt
            budget_filter["bf_start_date_year__gte"] = from_date_dt
            income_filter["ti_inv_date__gte"] = from_date_dt
        except ValueError:
            pass

    if to_date:
        try:
            to_date_dt = datetime.strptime(to_date, "%Y-%m-%d")
            expenses_filter["exp_ext_expense_number__exp_service_start_date__lte"] = to_date_dt
            budget_filter["bf_start_date_year__lte"] = to_date_dt
            income_filter["ti_inv_date__lte"] = to_date_dt
        except ValueError:
            pass

    # Dynamic months calculation
    import calendar
    if from_date and to_date:
        try:
            f_dt = datetime.strptime(from_date, "%Y-%m-%d")
            t_dt = datetime.strptime(to_date, "%Y-%m-%d")

            display_months_indices = []
            # Simplified logic for months within the range (assumes same year or range of months)
            start_month = f_dt.month
            end_month = t_dt.month
            if f_dt.year == t_dt.year:
                display_months_indices = list(range(start_month, end_month + 1))
            else:
                # Handle multi-year if needed, but for MIS usually within a year/fiscal period
                display_months_indices = list(range(1, 13))
        except ValueError:
            display_months_indices = list(range(1, 13))
    else:
        display_months_indices = list(range(1, 13))

    month_names_display = {i: calendar.month_name[i][:3] for i in display_months_indices}

    expense_summary = (
        ExpenseExtinfo.objects.filter(**expenses_filter)
        .exclude(exp_ext_expense_number__exp_service_start_date__isnull=True)
        .values("exp_ext_expense_number__exp_expense_type__exp_type_name",
                "exp_ext_expense_number__exp_service_start_date__month")
        .annotate(total_expense=Sum(F('exp_ext_amount') * F('exp_ext_expense_number__exp_quantity')))
    )

    expense_dict = {}
    for item in expense_summary:
        cat = item["exp_ext_expense_number__exp_expense_type__exp_type_name"]
        month = item["exp_ext_expense_number__exp_service_start_date__month"]
        if month in display_months_indices:
            expense_dict.setdefault(cat, {i: 0 for i in display_months_indices})
            expense_dict[cat][month] += item["total_expense"]

    # --- Add Attached Bill totals to "Transportation" Actual ---
    from ..sub_models.attached_bill_mod import AttachedBillInfo
    attached_bill_filter = {}
    if selected_year:
        attached_bill_filter["ab_from_date__year"] = selected_year
    if selected_branch:
        attached_bill_filter["ab_vendor__vend_branch__loc_name"] = selected_branch
    if from_date:
        attached_bill_filter["ab_from_date__gte"] = from_date
    if to_date:
        attached_bill_filter["ab_from_date__lte"] = to_date

    # Apply vehicle source filter if selected (Attached is usually ID 2)
    if selected_vehicle_source:
        attached_bill_filter["ab_vehicle_number__vm_ownership__ow_ownership"] = selected_vehicle_source
    else:
        # Default to only Attached vehicles if no filter is set?
        # The user said "if vehicle source = attached", so we filter by it.
        attached_bill_filter["ab_vehicle_number__vm_ownership_id"] = 2

    attached_summary = (
        AttachedBillInfo.objects.filter(**attached_bill_filter)
        .values("ab_from_date__month")
        .annotate(
            total_attached=Sum(
                Coalesce(F('ab_bill_amount'), Value(0.0)) -
                Coalesce(F('ab_extra_km_amount'), Value(0.0)) -
                Coalesce(F('ab_toll_cost'), Value(0.0)),
                output_field=FloatField()
            ),
            total_toll=Sum(Coalesce(F('ab_toll_cost'), Value(0.0)), output_field=FloatField()),
            total_extra_km=Sum(Coalesce(F('ab_extra_km_amount'), Value(0.0)), output_field=FloatField())
        )
    )

    trans_cat = "Transportation"
    toll_cat = "Toll"
    extra_km_cat = "Extra KM"
    for cat in [trans_cat, toll_cat, extra_km_cat]:
        if cat not in expense_dict:
            expense_dict[cat] = {i: 0 for i in display_months_indices}

    for item in attached_summary:
        month = item["ab_from_date__month"]
        if month in display_months_indices:
            expense_dict[trans_cat][month] += float(item["total_attached"] or 0)
            expense_dict[toll_cat][month] += float(item["total_toll"] or 0)
            expense_dict[extra_km_cat][month] += float(item["total_extra_km"] or 0)

    # --- Add Trip Closure/Driver Settlement charges to Actuals ---
    from ..sub_models.tripdetail_mod import TripdetailInfo
    trip_filter = {}
    if selected_year:
        trip_filter["tr_departeddate__year"] = selected_year
    if selected_branch:
        trip_filter["tr_updated_by__user_extinfo__emp_branch__loc_name"] = selected_branch
    if from_date:
        trip_filter["tr_departeddate__gte"] = from_date
    if to_date:
        trip_filter["tr_departeddate__lte"] = to_date

    if selected_vehicle_source:
        trip_filter["tr_vehiclesource__ow_ownership"] = selected_vehicle_source
    else:
        trip_filter["tr_vehiclesource_id__in"] = [1, 2, 3]  # OWN, ATTACHED, and MARKET

    trip_summary = (
        TripdetailInfo.objects.filter(**trip_filter)
        .exclude(tr_departeddate__isnull=True)
        .values("tr_departeddate__month")
        .annotate(
            total_halting=Sum('tc_haltingcost'),
            total_loading=Sum('tc_loadingcost'),
            total_parking=Sum('tc_parkingcost'),
            total_betta=Sum('tc_betacost'),
            total_handling=Sum('tc_handlingcost'),
            # Sum Toll from Trip Closure if it's an OWN or MARKET vehicle

            total_toll_trip_closure=Sum(Case(
                When(tr_vehiclesource_id__in=[1, 3], then=F('tc_tollcost')),
                default=Value(0.0),
                output_field=FloatField()
            ))

        )
    )

    halting_cat = "Halting"
    loading_cat = "Loading"
    parking_cat = "Parking"
    toll_cat = "Toll"
    betta_cat = "Driver Betta"
    handling_exp_cat = "Handling Expenses"

    for cat in [halting_cat, loading_cat, parking_cat, toll_cat, betta_cat, handling_exp_cat]:
        if cat not in expense_dict:
            expense_dict[cat] = {i: 0 for i in display_months_indices}

    for item in trip_summary:
        month = item["tr_departeddate__month"]
        if month in display_months_indices:
            expense_dict[halting_cat][month] += float(item["total_halting"] or 0)
            expense_dict[loading_cat][month] += float(item["total_loading"] or 0)
            expense_dict[parking_cat][month] += float(item["total_parking"] or 0)
            expense_dict[betta_cat][month] += float(item["total_betta"] or 0)
            expense_dict[handling_exp_cat][month] += float(item["total_handling"] or 0)
            expense_dict[toll_cat][month] += float(item["total_toll_trip_closure"] or 0)

    # --- Add Driver Salary actuals to "Driver Betta" ---
    from ..sub_models.driver_salary_mod import DriverSalaryInfo
    salary_filter = {}
    if selected_year:
        salary_filter["ds_month__year"] = selected_year
    if selected_branch:
        salary_filter["ds_branch__loc_name"] = selected_branch
    if from_date:
        salary_filter["ds_month__gte"] = from_date
    if to_date:
        salary_filter["ds_month__lte"] = to_date

    salary_summary = (
        DriverSalaryInfo.objects.filter(**salary_filter)
        .values("ds_month__month")
        .annotate(total_salary=Sum('ds_monthly_salary'))
    )

    for item in salary_summary:
        month = item["ds_month__month"]
        if month in display_months_indices:
            expense_dict[betta_cat][month] += float(item["total_salary"] or 0)

    # --- Add Market Bill charges to Actuals ---
    from ..sub_models.market_bill_mod import MarketBillInfo
    market_bill_filter = {}
    if selected_year:
        market_bill_filter["mb_bill_date__year"] = selected_year
    if selected_branch:
        market_bill_filter["mb_vendor__vend_branch__loc_name"] = selected_branch
    if from_date:
        market_bill_filter["mb_bill_date__gte"] = from_date
    if to_date:
        market_bill_filter["mb_bill_date__lte"] = to_date

    # Only include Market Bills if MARKET is selected or if no specific source is selected
    if selected_vehicle_source and selected_vehicle_source != "MARKET":
        market_summary = []
    else:
        market_summary = (
            MarketBillInfo.objects.filter(**market_bill_filter)
            .exclude(mb_bill_date__isnull=True)
            .values("mb_bill_date__month")
            .annotate(
                total_transportation=Sum('mb_trip_cost'),
                total_loading=Sum('mb_loading_cost'),
                total_unloading=Sum('mb_unloading_cost'),
                total_parking=Sum('mb_parking_cost'),
                total_halting=Sum('mb_halting_cost')
            )
        )

    unloading_cat = "Unloading"
    if unloading_cat not in expense_dict:
        expense_dict[unloading_cat] = {i: 0 for i in display_months_indices}

    for item in market_summary:
        month = item["mb_bill_date__month"]
        if month in display_months_indices:
            expense_dict[trans_cat][month] += float(item["total_transportation"] or 0)
            expense_dict[loading_cat][month] += float(item["total_loading"] or 0)
            expense_dict[unloading_cat][month] += float(item["total_unloading"] or 0)
            expense_dict[parking_cat][month] += float(item["total_parking"] or 0)
            expense_dict[halting_cat][month] += float(item["total_halting"] or 0)

    # --- Add Fuel Filling charges to "Diesel-Vehicle" Actual ---
    fuel_filter = {}
    if selected_year:
        fuel_filter["ff_date__year"] = selected_year
    if selected_branch:
        fuel_filter["ff_updated_by__user_extinfo__emp_branch__loc_name"] = selected_branch
    if from_date:
        fuel_filter["ff_date__gte"] = from_date
    if to_date:
        fuel_filter["ff_date__lte"] = to_date

    fuel_summary = (
        Fuelfillinginfo.objects.filter(**fuel_filter)
        .values("ff_date__month")
        .annotate(total_fuel=Sum('ff_fuel_price'))
    )

    diesel_cat = "Diesel-Vehicle"
    # Overwrite Diesel-Vehicle with Fuel Filling data
    expense_dict[diesel_cat] = {i: 0 for i in display_months_indices}

    for item in fuel_summary:
        month = item["ff_date__month"]
        if month in display_months_indices:
            expense_dict[diesel_cat][month] += float(item["total_fuel"] or 0)

    income_actual_summary = (
        TransInvoiceInfo.objects.filter(**income_filter)
        .exclude(ti_inv_date__isnull=True)
        .values("ti_inv_date__month")
        .annotate(**{
            cat.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_"): Sum(field)
            for cat, field in TRANSPORT_INVOICE_FIELD_MAPPING.items() if field is not None
        })
    )

    income_actual_dict = {cat: {i: 0 for i in display_months_indices} for cat in TRANSPORT_INCOME_CATEGORIES.keys()}
    for item in income_actual_summary:
        month = item["ti_inv_date__month"]
        if month in display_months_indices:
            for cat, field in TRANSPORT_INVOICE_FIELD_MAPPING.items():
                if field:
                    safe_key = cat.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
                    income_actual_dict[cat][month] += item.get(safe_key, 0.0)

    halting_inc_cat = "Halting Charges"
    loading_inc_cat = "Loading Charges"
    handling_inc_cat = "Transportation Handling Charges"
    trans_inc_cat = "Transportation Charges"
    parking_inc_cat = "Parking Charges"
    extra_km_cat = "Extra KM"

    # 1. Pull from TripdetailInfo (all vehicle sources)
    trip_income_summary = (
        TripdetailInfo.objects.filter(**trip_filter)
        .exclude(tr_departeddate__isnull=True)
        .values("tr_departeddate__month")
        .annotate(
            total_halting=Sum(Case(When(tc_haltingcost_check=True, then=F('tc_haltingcost')), default=Value(0.0),
                                   output_field=FloatField())),
            total_loading=Sum(Case(When(tc_loadingcost_check=True, then=F('tc_loadingcost')), default=Value(0.0),
                                   output_field=FloatField())),
            total_handling=Sum(Case(When(tc_handlingcost_check=True, then=F('tc_handlingcost')), default=Value(0.0),
                                    output_field=FloatField())),
            total_transportation=Sum(Case(When(tc_tripcost_check=True, then=F('tc_tripcost')), default=Value(0.0),
                                          output_field=FloatField())),
            total_parking=Sum(Case(When(tc_parkingcost_check=True, then=F('tc_parkingcost')), default=Value(0.0),
                                   output_field=FloatField())),
            total_toll=Sum(Case(When(tc_tollcost_check=True, then=F('tc_tollcost')), default=Value(0.0),
                                output_field=FloatField()))
        )
    )
    for item in trip_income_summary:
        month = item["tr_departeddate__month"]
        if month in display_months_indices:
            income_actual_dict[halting_inc_cat][month] += float(item["total_halting"] or 0)
            income_actual_dict[loading_inc_cat][month] += float(item["total_loading"] or 0)
            income_actual_dict[handling_inc_cat][month] += float(item["total_handling"] or 0)
            income_actual_dict[trans_inc_cat][month] += float(item["total_transportation"] or 0)
            income_actual_dict[parking_inc_cat][month] += float(item["total_parking"] or 0)
            income_actual_dict["Toll Charges"][month] += float(item["total_toll"] or 0)

    # 2. Pull from AttachedBillInfo (for Attached vehicles)
    if not (selected_vehicle_source and selected_vehicle_source != "ATTACHED"):
        attached_income_summary = (
            AttachedBillInfo.objects.filter(**attached_bill_filter)
            .exclude(ab_from_date__isnull=True)
            .values("ab_from_date__month")
            .annotate(
                total_transportation=Sum(
                    Coalesce(F('ab_bill_amount'), Value(0.0)) -
                    Coalesce(F('ab_extra_km_amount'), Value(0.0)) -
                    Coalesce(F('ab_toll_cost'), Value(0.0)),
                    output_field=FloatField()
                ),
                total_extra_km=Sum(Coalesce(F('ab_extra_km_amount'), Value(0.0)), output_field=FloatField()),
                total_toll=Sum(Coalesce(F('ab_toll_cost'), Value(0.0)), output_field=FloatField())
            )
        )
        for item in attached_income_summary:
            month = item["ab_from_date__month"]
            if month in display_months_indices:
                income_actual_dict[trans_inc_cat][month] += float(item["total_transportation"] or 0)
                if extra_km_cat in income_actual_dict:  # If there's an Extra KM income category
                    income_actual_dict[extra_km_cat][month] += float(item["total_extra_km"] or 0)
                income_actual_dict["Toll Charges"][month] += float(item["total_toll"] or 0)

    # 3. Pull from MarketBillInfo (for Market vehicles)
    if not (selected_vehicle_source and selected_vehicle_source != "MARKET"):
        market_income_summary = (
            MarketBillInfo.objects.filter(**market_bill_filter)
            .exclude(mb_bill_date__isnull=True)
            .values("mb_bill_date__month")
            .annotate(
                total_halting=Sum(Coalesce(F('mb_halting_cost'), Value(0.0)), output_field=FloatField()),
                total_loading=Sum(Coalesce(F('mb_loading_cost'), Value(0.0)), output_field=FloatField()),
                total_transportation=Sum(Coalesce(F('mb_trip_cost'), Value(0.0)), output_field=FloatField()),
                total_parking=Sum(Coalesce(F('mb_parking_cost'), Value(0.0)), output_field=FloatField())
            )
        )
        for item in market_income_summary:
            month = item["mb_bill_date__month"]
            if month in display_months_indices:
                income_actual_dict[halting_inc_cat][month] += float(item["total_halting"] or 0)
                income_actual_dict[loading_inc_cat][month] += float(item["total_loading"] or 0)
                income_actual_dict[trans_inc_cat][month] += float(item["total_transportation"] or 0)
                income_actual_dict[parking_inc_cat][month] += float(item["total_parking"] or 0)

    budget_summary = (
        BudgetInfo.objects.filter(**budget_filter)
        .values("bf_start_date_year__month")
        .annotate(**{field: Sum(field) for field in TRANSPORT_BUDGET_FIELD_MAPPING.values() if field is not None})
    )

    budget_dict_by_month = {}
    for item in budget_summary:
        month = item["bf_start_date_year__month"]
        if month in display_months_indices:
            for cat, field in TRANSPORT_BUDGET_FIELD_MAPPING.items():
                if field:
                    budget_dict_by_month.setdefault(cat, {i: 0 for i in display_months_indices})
                    budget_dict_by_month[cat][month] = item.get(field, 0.0)

    def get_category_summary(category_mapping, category_name, actual_dict, is_income=False):
        summary = []
        grand_monthly_expenses = {i: 0 for i in display_months_indices}
        grand_monthly_budgets = {i: 0 for i in display_months_indices}
        grand_total_expense = 0
        grand_total_budget = 0

        for category, field in category_mapping.items():
            monthly_expenses = actual_dict.get(category, {i: 0 for i in display_months_indices})
            monthly_budgets = budget_dict_by_month.get(category, {i: 0 for i in display_months_indices})
            # Variance calculation:
            # For Income: Actual - Budget (Positive = Over-performance)
            # For Expenses: Budget - Actual (Positive = Saving)
            if is_income:
                monthly_variance = {month: monthly_expenses[month] - monthly_budgets[month] for month in
                                    display_months_indices}
            else:
                monthly_variance = {month: monthly_budgets[month] - monthly_expenses[month] for month in
                                    display_months_indices}

            total_expense = sum(monthly_expenses.values())
            total_budget = sum(monthly_budgets.values())

            if is_income:
                total_variance = total_expense - total_budget
            else:
                total_variance = total_budget - total_expense

            pl_percentage = (total_variance / total_budget * 100) if total_budget > 0 else 0.0

            for month in display_months_indices:
                grand_monthly_expenses[month] += monthly_expenses[month]
                grand_monthly_budgets[month] += monthly_budgets[month]

            grand_total_expense += total_expense
            grand_total_budget += total_budget

            summary.append({
                "expense_type": category,
                "monthly_expenses": monthly_expenses,
                "monthly_budgets": monthly_budgets,
                "monthly_variance": monthly_variance,
                "total_expense": total_expense,
                "total_budget": total_budget,
                "total_variance": total_variance,
                "pl_percentage": pl_percentage,
            })

        if is_income:
            grand_monthly_variance = {month: grand_monthly_expenses[month] - grand_monthly_budgets[month] for month in
                                      display_months_indices}
            grand_total_variance = grand_total_expense - grand_total_budget
        else:
            grand_monthly_variance = {month: grand_monthly_budgets[month] - grand_monthly_expenses[month] for month in
                                      display_months_indices}
            grand_total_variance = grand_total_budget - grand_total_expense

        grand_pl_percentage = (grand_total_variance / grand_total_budget * 100) if grand_total_budget > 0 else 0.0

        summary.append({
            "expense_type": f"Total {category_name}",
            "monthly_expenses": grand_monthly_expenses,
            "monthly_budgets": grand_monthly_budgets,
            "monthly_variance": grand_monthly_variance,
            "total_expense": grand_total_expense,
            "total_budget": grand_total_budget,
            "total_variance": grand_total_variance,
            "pl_percentage": grand_pl_percentage,
            "is_total": True,
        })
        return summary

    income_summary = get_category_summary(TRANSPORT_INCOME_CATEGORIES, "Income", income_actual_dict, is_income=True)
    op_fixed_summary = get_category_summary(TRANSPORT_OPERATIONAL_EXPENSES_FIXED, "Operational Fixed", expense_dict)
    op_variable_summary = get_category_summary(TRANSPORT_OPERATIONAL_EXPENSES_VARIABLE, "Operational Variable",
                                               expense_dict)
    non_op_fixed_summary = get_category_summary(TRANSPORT_NON_OPERATIONAL_EXPENSES_FIXED, "Non-Operational Fixed",
                                                expense_dict)
    non_op_variable_summary = get_category_summary(TRANSPORT_NON_OPERATIONAL_EXPENSES_VARIABLE,
                                                   "Non-Operational Variable", expense_dict)
    employee_benefits_summary = get_category_summary(TRANSPORT_EMPLOYEE_BENEFITS_CATEGORIES, "Employee Benefits",
                                                     expense_dict)
    dept_expenses_summary = get_category_summary(TRANSPORT_DEPARTMENT_EXPENSES_CATEGORIES, "Department Expenses",
                                                 expense_dict)
    interest_summary = get_category_summary(TRANSPORT_INTEREST_EXPENSES_CATEGORIES, "Interest Expenses", expense_dict)

    # Net Profit Calculation
    net_monthly_budget = {i: 0 for i in display_months_indices}
    net_monthly_actual = {i: 0 for i in display_months_indices}

    for month in display_months_indices:
        net_monthly_budget[month] = income_summary[-1]["monthly_budgets"][month] - (
                op_fixed_summary[-1]["monthly_budgets"][month] + op_variable_summary[-1]["monthly_budgets"][month] +
                non_op_fixed_summary[-1]["monthly_budgets"][month] + non_op_variable_summary[-1]["monthly_budgets"][
                    month] +
                employee_benefits_summary[-1]["monthly_budgets"][month] + dept_expenses_summary[-1]["monthly_budgets"][
                    month] +
                interest_summary[-1]["monthly_budgets"][month]
        )
        net_monthly_actual[month] = income_summary[-1]["monthly_expenses"][month] - (
                op_fixed_summary[-1]["monthly_expenses"][month] + op_variable_summary[-1]["monthly_expenses"][month] +
                non_op_fixed_summary[-1]["monthly_expenses"][month] + non_op_variable_summary[-1]["monthly_expenses"][
                    month] +
                employee_benefits_summary[-1]["monthly_expenses"][month] +
                dept_expenses_summary[-1]["monthly_expenses"][month] +
                interest_summary[-1]["monthly_expenses"][month]
        )

    net_monthly_variance = {month: net_monthly_actual[month] - net_monthly_budget[month] for month in
                            display_months_indices}
    net_monthly_pl_percentage = {
        month: (net_monthly_variance[month] / net_monthly_budget[month] * 100) if net_monthly_budget[
                                                                                      month] != 0 else 0.0
        for month in display_months_indices
    }
    total_net_budget = sum(net_monthly_budget.values())
    total_net_actual = sum(net_monthly_actual.values())
    total_net_variance = total_net_actual - total_net_budget
    total_net_pl_percentage = (total_net_variance / total_net_budget * 100) if total_net_budget != 0 else 0.0

    net_summary = {
        "monthly_budget": net_monthly_budget,
        "monthly_actual": net_monthly_actual,
        "monthly_variance": net_monthly_variance,
        "monthly_pl_percentage": net_monthly_pl_percentage,
        "total_budget": total_net_budget,
        "total_actual": total_net_actual,
        "total_variance": total_net_variance,
        "pl_percentage": total_net_pl_percentage,
    }

    import calendar
    month_names = [calendar.month_name[i] for i in range(1, 13)]

    return render(request, "asset_mgt_app/trans_mis.html", {
        "first_name": first_name,
        "income_summary": income_summary,
        "op_fixed_summary": op_fixed_summary,
        "op_variable_summary": op_variable_summary,
        "non_op_fixed_summary": non_op_fixed_summary,
        "non_op_variable_summary": non_op_variable_summary,
        "employee_benefits_summary": employee_benefits_summary,
        "dept_expenses_summary": dept_expenses_summary,
        "interest_summary": interest_summary,
        "net_summary": net_summary,
        "month_names_display": month_names_display,
        "months": display_months_indices,
        "years": years,
        "branches": branches,
        "vehicle_sources": vehicle_sources,
        "selected_year": selected_year,
        "selected_branch": selected_branch,
        "selected_vehicle_source": selected_vehicle_source,
        "from_date": from_date,
        "to_date": to_date,
    })

