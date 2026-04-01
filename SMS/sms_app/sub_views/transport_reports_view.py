from datetime import datetime
from django.http import JsonResponse

from datetime import date
import calendar
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q, F, Sum, Value, FloatField, Case, When
from django.db.models.functions import Coalesce, Trim, Upper
from django.utils.safestring import mark_safe
from ..models import TripdetailInfo, ConsignmentdetailInfo, CustomerInfo, CustomerdepartmentInfo, ConsignmentgoodsInfo, Places, VehiclemasterInfo, Driverexpense, Vehicle_allotmentInfo, VendorratemasterInfo1, Vendor_info, OwnershipInfo, CustomerClaimsInfo
from ..sub_models.trans_customer_claims_mod import TransCustomerClaimsInfo
from ..sub_forms.dmr_report_form import DmrForm
from ..sub_models.location_info_mod import Location_info
from ..models import VehiclemasterInfo

# -------------------------
# HEADERS
# -------------------------

VEHICLE_LOG_HEADERS = [
    "SNo", "Date", "Trip Sheet No.", "Vehicle No.", "Starting Time", "Closing Time",
    "Start Km.", "Closing Km.", "Used Km.", "Starting Place", "Closing Place",
    "Cnote No", "Customer", "Shipper", "Trip Category", "Driver Name"
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
    "Branch", "Customer Short Name", "Planning Date", "Cnote No", "From", "To", "Dept",
    "Veh No", "Veh Type", "Consignee", "Reference No", "HAWB No", "No. of Pcs", "Weight",
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
    "S No", "Date", "Vehicle No", 
    "Toll charges", "AAI charges", "Loading charges", "Unloading Charges", 
    "Weighment charges", "Halting Charges", "Handling Charges", "Selling", 
    "Toll Expenses", "Depreciation", "Permit", "FC", "Road tax"
]

WHATSAPP_DELIVERY_STATUS_HEADERS = [
    "S No", "Branch", "Customer Name", "Department", "C-Note No",
    "Consignment Date", "Trip Code", "Vehicle Type", "From", "To",
    "Vehicle No", "Start Date", "End Date", "Driver",
    "Whatsapp Delivered time", "Delivered Status"
]

HALTING_REPORT_HEADERS = [
    "SNo", "Branch", "Date", "VehicleNo", "VehicleType", "Customer", "Department", "Vertical",
    "Consignor", "Consignee", "C-Note",
    "Halting Start", "Halting End", "Halting Days",
    "Halting Charges (Paid to Vendor)", "Halting Charges (Billed to Customer)", "Difference",
    "Pickup Start", "Pickup End", "Pickup Hrs",
    "Delivery Start", "Delivery End", "Delivery Hrs"
]

CLAIM_PENDING_HEADERS = [
    "SNo", "Cnote No", "Trip Date", "From", "To", "Veh No", "Driver Name", "Shipper Ref", "Damage Remarks", "Reason For Claim", "Amount"
]


VENDOR_PL_ATTACHED_HEADERS = [
    "S No", "Date", "Cnote", "From", "To", "Customer", "Veh No", "Veh Type",
    "Trip Charges", "Toll charges", "AAI charges", "Loading charges", "Unloading Charges",
    "Weighment charges", "Halting Charges", "Handling Charges", "Selling",
    "Vendor Name", "Bill No", "Buy cost", "Toll Cost", "Parking Cost",
    "Loading cost", "Unloading cost", "Weighment cost", "Handling cost",
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
    "Sno", "Branch", "Date", "VehicleNo", "VehicleType", "Mileage Fixed",
    "Leased To Customer", "Km Run", "Diesel Expenses", "Revenue",
    "Diesel vs Revenue %", "Actual Mileage"
]

OWN_VS_MARKET_SALES_HEADERS = [
    "SNo", "Date", "Branch", "Customer Name", "Department",
    "Own Vehicle Sales", "No of Vehicle Used - Own", "No of Jobs - Own", "No of Drivers - Own", "Trip Index - Own",
    "Market Vehicle Sales", "No of Vehicle Used - Market", "No of Jobs - Market", "No of Drivers - Market", "Trip Index - Market",
    "Market Buy Rate", "No of Trips - Local", "No of Trips - OutStation"
]

ENQUIRY_PENDING_HEADERS = [
    "SNo", "Date", "Enquiry No", "From", "To", "Vehicle Requested", "Unassigned Vehicles", "Vehicle Type", "Customer Name", "Reason"
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

# -------------------------
# VIEWS
# -------------------------
@login_required(login_url='login_page')
def vehicle_log_report_view(request):
    first_name = request.session.get('first_name')
    select_all = request.POST.get('select_all') or request.GET.get('select_all')

    if request.method == "POST":
        form = DmrForm(request.POST)
        vehicle_number = request.POST.get('vehicle_number')
        selected_month = request.POST.get('month')
        selected_year = request.POST.get('year')
        from_loc_id = request.POST.get('from_location')
        to_loc_id = request.POST.get('to_location')
        branch_id = request.POST.get('branch')
    else:
        form = DmrForm()
        vehicle_number = ""
        selected_month = '0'
        selected_year = '0'
        from_loc_id = ""
        to_loc_id = ""
        branch_id = ""

    trips = TripdetailInfo.objects.select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_category',
        'tr_consignmentnumber',
        'tr_departedlocation',
        'tr_reportedlocation'
    )

    # Filters
    if vehicle_number:
        trips = trips.filter(tr_vehiclenumber__icontains=vehicle_number)
    
    if selected_month and selected_month != '0' and selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__month=selected_month, tr_loading_time__year=selected_year) |
            Q(tr_departeddate__month=selected_month, tr_departeddate__year=selected_year) |
            Q(tr_departeddate_pickup__month=selected_month, tr_departeddate_pickup__year=selected_year) |
            Q(tr_reporteddate__month=selected_month, tr_reporteddate__year=selected_year) |
            Q(tr_reporteddate_pickup__month=selected_month, tr_reporteddate_pickup__year=selected_year) |
            Q(tr_unloading_time__month=selected_month, tr_unloading_time__year=selected_year)
        )

    if from_loc_id:
        trips = trips.filter(tr_departedlocation_id=from_loc_id)
    if to_loc_id:
        trips = trips.filter(tr_reportedlocation_id=to_loc_id)

    if branch_id:
        try:
            b_id = int(branch_id)
            if b_id == 1: # BLR
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='BLR')
            elif b_id == 2: # MAA
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='MAA')
            elif b_id == 3: # PNY
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='PNY')
            elif b_id == 4: # HYD
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='HYD')
            else:
                loc = Location_info.objects.get(id=b_id)
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains=loc.loc_name)
        except (ValueError, Location_info.DoesNotExist):
            pass

    trips = trips.order_by('-tr_created_at') # Order by created_at for consistency if loading_time is missing

    # Performance Optimization: Limit results
    if select_all == 'true':
        trips = trips[:2000] # Safe upper limit for report
    else:
        # Default view or filtered view: reasonable limit for fast load
        if not (vehicle_number or (selected_month and selected_month != '0') or from_loc_id or to_loc_id or branch_id):
            trips = trips[:100] # Very fast initial load
        else:
            trips = trips[:1000] # Fast filtered load

    trip_cons_ids = [t.tr_consignmentnumber_id for t in trips if t.tr_consignmentnumber_id]

    goods_map = {
        g.cg_consignmentnumber_id: g
        for g in ConsignmentgoodsInfo.objects.filter(
            cg_consignmentnumber_id__in=trip_cons_ids
        ).select_related('cg_consigner')
    }

    data_rows = []
    for idx, trip in enumerate(trips, start=1):
        cons_goods = goods_map.get(trip.tr_consignmentnumber_id)

        # Fallback date for display
        display_date = trip.tr_loading_time or trip.tr_departeddate or trip.tr_departeddate_pickup or trip.tr_reporteddate or trip.tr_reporteddate_pickup or trip.tr_created_at

        data_rows.append([
            idx,
            display_date.strftime("%d-%m-%Y") if display_date else "",
            safe_str(trip.tr_tripnumber),
            safe_str(trip.tr_vehiclenumber),
            trip.tr_departeddate.strftime("%H:%M") if trip.tr_departeddate else "",
            trip.tr_reporteddate.strftime("%H:%M") if trip.tr_reporteddate else "",
            safe_str(trip.tr_departedkm),
            safe_str(trip.tr_reportedkm),
            max(0, (trip.tr_reportedkm_delivery or trip.tr_reportedkm or 0) - (trip.tr_departedkm or 0)),
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_str(trip.tr_consignmentnumber.co_consignmentnumber) if trip.tr_consignmentnumber else "",
            safe_str(trip.tr_enquirynumber.en_customername),
            safe_str(cons_goods.cg_consigner) if cons_goods else "",
            safe_str(trip.tr_category),
            safe_str(trip.tr_drivername),
        ])

    all_vehicles = VehiclemasterInfo.objects.filter(
        vm_ownership_id__in=[1, 2]
    ).order_by('vm_registrationnumber')

    return render(request, "asset_mgt_app/vehicle_log_report.html", {
        'first_name': first_name,
        'form': form,
        'headers': VEHICLE_LOG_HEADERS,
        'data_rows': data_rows,
        'vehicle_number': vehicle_number,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'from_location': from_loc_id,
        'to_location': to_loc_id,
        'branch_id': branch_id,
        'select_all': select_all,
        'all_vehicles': all_vehicles,
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
        trips = trips.filter(tr_category_id=trip_category_id)

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
            if b_id == 1: # BLR
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='BLR')
            elif b_id == 2: # MAA
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='MAA')
            elif b_id == 3: # PNY
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='PNY')
            elif b_id == 4: # HYD
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
            trip.tr_departeddate.strftime("%d-%m-%Y %H:%M") if trip.tr_departeddate else "",
            trip.tr_reporteddate.strftime("%d-%m-%Y %H:%M") if trip.tr_reporteddate else "",
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype),
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
        .filter(vm_ownership_id__in=[1, 2]) # OWN, ATTACHED
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
                vehicles = vehicles.filter(Q(vm_vendor__vend_branch_id=4) | Q(vm_registrationnumber__istartswith='TS') | Q(vm_registrationnumber__istartswith='AP'))
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
        
        utilized_days_set = set() # Using a set of dates to avoid double counting overlapping trips

        for trip in veh_trips:
            # Multi-field fallback for start and end
            t_start_dt = trip['tr_departeddate'] or trip['tr_loading_time'] or trip['tr_departeddate_pickup'] or trip['tr_reporteddate']
            t_end_dt = trip['tr_reporteddate'] or trip['tr_reporteddate_pickup'] or trip['tr_unloading_time']
            
            if not t_start_dt and not t_end_dt:
                continue # Skip drafts with no activity dates

            t_start = t_start_dt.date() if t_start_dt else month_start
            # If trip is unclosed, don't count until today; count as 1 day (the start date)
            t_end = t_end_dt.date() if t_end_dt else t_start
            
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
            if veh_no_clean.startswith('TN'): branch_name = "MAA"
            elif veh_no_clean.startswith('KA'): branch_name = "BLR"
            elif veh_no_clean.startswith('PY'): branch_name = "PNY"
            elif veh_no_clean.startswith('TS') or veh_no_clean.startswith('AP'): branch_name = "HYD"
            else: branch_name = "Other"

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
            trip.tr_departeddate.strftime("%d-%m-%Y %H:%M") if trip.tr_departeddate else "",
            trip.tr_reporteddate.strftime("%d-%m-%Y %H:%M") if trip.tr_reporteddate else "",
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype),
            safe_str(trip.tr_vehiclesource),
            safe_num(trip.tc_tripcost) if trip.tc_tripcost_check else 0, # Trip Charges
            safe_num(trip.tc_tollcost) if trip.tc_tollcost_check else 0, # Toll charges
            safe_num(trip.tc_supervisorcost) if trip.tc_supervisorcost_check else 0, # AAI charges
            safe_num(trip.tc_loadingcost) if trip.tc_loadingcost_check else 0, # Loading charges
            safe_num(trip.tc_unloadingcost) if trip.tc_unloadingcost_check else 0, # Unloading Charges
            safe_num(trip.tc_weighmentcost) if trip.tc_weighmentcost_check else 0, # Weighment charges
            (safe_num(trip.tc_haltingcost) if trip.tc_haltingcost_check else 0) + (safe_num(trip.tc_total_halting_cost) if trip.tc_total_halting_cost_check else 0), # Halting Charges
            safe_num(trip.tc_handlingcost) if trip.tc_handlingcost_check else 0, # Handling Charges
            total_selling                       # Selling (Total)
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
        'all_vehicles': VehiclemasterInfo.objects.filter(vm_ownership_id__in=[1, 2, 3]).order_by('vm_registrationnumber'),
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
            advance.de_date.strftime("%d-%m-%Y") if advance.de_date else "",
            safe_str(advance.de_expense_type.expense_type if advance.de_expense_type else ""),  # Type (Advance/Expense)
            safe_str(advance.driver_name.dm_id if advance.driver_name else ""),  # Employee ID
            safe_str(advance.driver_name.dm_name if advance.driver_name else ""),  # Driver name
            advance.de_date.strftime("%d-%m-%Y") if advance.de_date and advance.de_expense_type_id == 1 else "",  # Advance Date
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
    from ..models import TransInvoiceInfo

    if request.method == "POST":
        form = DmrForm(request.POST)
    else:
        form = DmrForm()

    customer_id = request.POST.get('dmr_customer')
    dept_id = request.POST.get('customer_department')
    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')
    from_loc_id = request.POST.get('from_location')
    to_loc_id = request.POST.get('to_location')

    # -----------------------------
    # Trips already invoiced
    # -----------------------------
    from ..models import ConsignmentgoodsInfo

    # 1. Direct trip link
    invoiced_trip_ids = list(TransInvoiceInfo.objects.filter(
        ti_trip__isnull=False
    ).values_list('ti_trip_id', flat=True))

    # 2. Via Consignment link
    invoiced_cons_ids = TransInvoiceInfo.objects.filter(
        ti_consignment__isnull=False
    ).values_list('ti_consignment_id', flat=True)

    trips_from_cons = TripdetailInfo.objects.filter(
        tr_consignmentnumber_id__in=invoiced_cons_ids
    ).values_list('id', flat=True)

    # 3. Via Goods link
    invoiced_goods_ids = TransInvoiceInfo.objects.filter(
        ti_goods__isnull=False
    ).values_list('ti_goods_id', flat=True)

    cons_from_goods = ConsignmentgoodsInfo.objects.filter(
        id__in=invoiced_goods_ids
    ).values_list('cg_consignmentnumber_id', flat=True)

    trips_from_goods = TripdetailInfo.objects.filter(
        tr_consignmentnumber_id__in=cons_from_goods
    ).values_list('id', flat=True)

    # Combine all
    all_invoiced_ids = set(invoiced_trip_ids) | set(trips_from_cons) | set(trips_from_goods)

    # -----------------------------
    # Base queryset
    # -----------------------------
    trips = TripdetailInfo.objects.filter(
        tr_category_id=1,
        tc_financestatus_id=7
    ).exclude(
        tr_consignmentnumber__isnull=True
    ).exclude(
        id__in=all_invoiced_ids
    ).select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_enquirynumber__en_customerdepartment',
        'tr_consignmentnumber',
        'tr_vehicletype',
        'tr_vehiclesource',
        'tr_departedlocation',
        'tr_reportedlocation'
    ).prefetch_related(
        'tr_consignmentnumber__cg_consignmentnumber'
    ).annotate(
        trip_total=(
            Case(When(tc_tripcost_check=True, then=F('tc_tripcost')), default=0.0, output_field=FloatField()) +
            Case(When(tc_tollcost_check=True, then=F('tc_tollcost')), default=0.0, output_field=FloatField()) +
            Case(When(tc_parkingcost_check=True, then=F('tc_parkingcost')), default=0.0, output_field=FloatField()) +
            Case(When(tc_loadingcost_check=True, then=F('tc_loadingcost')), default=0.0, output_field=FloatField()) +
            Case(When(tc_unloadingcost_check=True, then=F('tc_unloadingcost')), default=0.0, output_field=FloatField()) +
            Case(When(tc_haltingcost_check=True, then=F('tc_haltingcost')), default=0.0, output_field=FloatField()) +
            Case(When(tc_rtocost_check=True, then=F('tc_rtocost')), default=0.0, output_field=FloatField()) +
            Case(When(tc_weighmentcost_check=True, then=F('tc_weighmentcost')), default=0.0, output_field=FloatField()) +
            Case(When(tc_handlingcost_check=True, then=F('tc_handlingcost')), default=0.0, output_field=FloatField()) +
            Case(When(tc_supervisorcost_check=True, then=F('tc_supervisorcost')), default=0.0, output_field=FloatField()) +
            Case(When(tc_betacost_check=True, then=F('tc_betacost')), default=0.0, output_field=FloatField()) +
            Case(When(tc_total_halting_cost_check=True, then=F('tc_total_halting_cost')), default=0.0, output_field=FloatField()) +
            Case(When(tc_cancellation_check=True, then=F('tc_cancellation')), default=0.0, output_field=FloatField())
        )
    )

    # -----------------------------
    # Filters
    # -----------------------------
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

    trips = trips.order_by('-tr_created_at')

    # -----------------------------
    # Build table rows
    # -----------------------------
    data_rows = []

    for idx, trip in enumerate(trips, start=1):
        cons = trip.tr_consignmentnumber
        goods = cons.cg_consignmentnumber.first() if cons else None

        row = [
            # 1. Branch (maps to Dept in Master List)
            safe_str(trip.tr_enquirynumber.en_customerdepartment),
            # 2. Customer Short Name
            safe_str(trip.tr_enquirynumber.en_customername),
            # 3. Date
            (lambda: (
                # Prefer date matching the filter
                next((d for d in [
                    trip.tr_loading_time, trip.tr_departeddate, trip.tr_departeddate_pickup,
                    trip.tr_departeddate_delivery, trip.tr_reporteddate, trip.tr_reporteddate_pickup,
                    trip.tr_reporteddate_delivery, trip.tr_unloading_time, trip.tr_dock_in_time,
                    trip.tr_dock_out_time, trip.tr_created_at
                ] if d and (not selected_month or selected_month == '0' or d.month == int(selected_month)) and 
                  (not selected_year or selected_year == '0' or d.year == int(selected_year))), 
                # Fallback to first available date
                next((d for d in [
                    trip.tr_loading_time, trip.tr_departeddate, trip.tr_departeddate_pickup,
                    trip.tr_departeddate_delivery, trip.tr_reporteddate, trip.tr_reporteddate_pickup,
                    trip.tr_reporteddate_delivery, trip.tr_unloading_time, trip.tr_dock_in_time,
                    trip.tr_dock_out_time, trip.tr_created_at
                ] if d), None)
            )))().strftime("%d-%m-%Y") if any([
                trip.tr_loading_time, trip.tr_departeddate, trip.tr_departeddate_pickup,
                trip.tr_departeddate_delivery, trip.tr_reporteddate, trip.tr_reporteddate_pickup,
                trip.tr_reporteddate_delivery, trip.tr_unloading_time, trip.tr_dock_in_time,
                trip.tr_dock_out_time, trip.tr_created_at
            ]) else "",
            # 4. Cnote No
            safe_str(cons.co_consignmentnumber) if cons else "",
            # 5. From
            safe_str(trip.tr_departedlocation),
            # 6. To
            safe_str(trip.tr_reportedlocation),
            # 7. Dept
            safe_str(trip.tr_enquirynumber.en_customerdepartment),
            # 8. Veh No
            safe_str(trip.tr_vehiclenumber),
            # 9. Veh Type
            safe_str(trip.tr_vehicletype),
            # 10. Consignee
            safe_str(goods.cg_consignee) if goods else "",
            # 11. Reference No
            safe_str(cons.co_cusrefnum) if cons else "",
            # 12. HAWB No
            safe_str(goods.cg_hawbno) if goods else "",
            # 13. No. of Pcs
            safe_num(goods.cg_qty) if goods else 0,
            # 14. Weight
            safe_num(goods.cg_weight) if goods else 0.0,
            # 15. Transportation Charges
            safe_num(trip.tc_tripcost) if trip.tc_tripcost_check else 0,
            # 16. Toll Charges
            safe_num(trip.tc_tollcost) if trip.tc_tollcost_check else 0,
            # 17. Parking Charges
            safe_num(trip.tc_parkingcost) if trip.tc_parkingcost_check else 0,
            # 18. Loading Charges
            safe_num(trip.tc_loadingcost) if trip.tc_loadingcost_check else 0,
            # 19. Unloading Charges
            safe_num(trip.tc_unloadingcost) if trip.tc_unloadingcost_check else 0,
            # 20. Halting Charges
            (safe_num(trip.tc_haltingcost) if trip.tc_haltingcost_check else 0) + (safe_num(trip.tc_total_halting_cost) if trip.tc_total_halting_cost_check else 0),
            # 21. Docket Charges (Mapped to tc_rtocost in WOH list)
            safe_num(trip.tc_rtocost) if trip.tc_rtocost_check else 0,
            # 22. Weighment Charges
            safe_num(trip.tc_weighmentcost) if trip.tc_weighmentcost_check else 0,
            # 23. Handling Charges
            safe_num(trip.tc_handlingcost) if trip.tc_handlingcost_check else 0,
            # 24. Cancellation Charges
            safe_num(trip.tc_cancellation) if trip.tc_cancellation_check else 0,
            # 25. TOTAL
            round(safe_num(trip.trip_total), 2)
        ]

        data_rows.append(row)

    # -----------------------------
    # Context
    # -----------------------------
    context = {
        'first_name': first_name,
        'form': form,
        'headers': INVOICE_PENDING_HEADERS,
        'data_rows': data_rows,
        'customer_id': customer_id,
        'dept_id': dept_id,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'from_location': from_loc_id,
        'to_location': to_loc_id,
    }

    return render(request, "asset_mgt_app/invoice_pending_report.html", context)


@login_required(login_url='login_page')
def vendor_p_l_mkt_report_view(request):
    first_name = request.session.get('first_name')

    from ..models import Vehicle_allotmentInfo, TransInvoiceInfo, Driverexpense, VehiclemasterInfo, VehicletypeInfo, MarketBillInfo, ConsignmentgoodsInfo, TripdetailInfo

    if request.method == "POST":
        form = DmrForm(request.POST)
    else:
        form = DmrForm()


    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')
    from_loc_id = request.POST.get('from_location')
    to_loc_id = request.POST.get('to_location')
    branch = request.POST.get('branch', '').strip()
    vendor_id = request.POST.get('vendor_id', '').strip()
    veh_no = (request.POST.get('veh_no') or request.GET.get('veh_no', '')).strip()

    # Identifty all invoiced trip IDs (Linked directly or via consignment/goods)
    invoiced_trip_ids = list(TransInvoiceInfo.objects.filter(ti_trip__isnull=False).values_list('ti_trip_id', flat=True))
    invoiced_cons_ids = TransInvoiceInfo.objects.filter(ti_consignment__isnull=False).values_list('ti_consignment_id', flat=True)
    invoiced_goods_ids = TransInvoiceInfo.objects.filter(ti_goods__isnull=False).values_list('ti_goods_id', flat=True)

    # Trips from consignment links
    trips_from_cons = list(TripdetailInfo.objects.filter(tr_consignmentnumber_id__in=invoiced_cons_ids).values_list('id', flat=True))

    # Trips from goods links
    from ..models import ConsignmentgoodsInfo
    cons_from_goods = ConsignmentgoodsInfo.objects.filter(id__in=invoiced_goods_ids).values_list('cg_consignmentnumber_id', flat=True)
    trips_from_goods = list(TripdetailInfo.objects.filter(tr_consignmentnumber_id__in=cons_from_goods).values_list('id', flat=True))
    
    # Combined set of all invoiced trip IDs
    all_invoiced_ids = set(invoiced_trip_ids + trips_from_cons + trips_from_goods)

    # BASE TRIPS
    # ------------------------------------------------
    trips = TripdetailInfo.objects.filter(
        id__in=all_invoiced_ids,
        tc_financestatus_id__in=[2, 7],
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

    # ------------------------------------------------
    # FILTERS
    # ------------------------------------------------


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

    if branch == 'MAA':
        trips = trips.filter(
            tr_consignmentnumber__co_consignmentnumber__istartswith='MAA'
        )
    elif branch == 'BLR':
        trips = trips.filter(
            tr_consignmentnumber__co_consignmentnumber__istartswith='BLR'
        )

    if vendor_id:
        valid_enquiries = Vehicle_allotmentInfo.objects.filter(va_vendor_id=vendor_id).values_list('va_enquirynumber_id', flat=True)
        trips = trips.filter(tr_enquirynumber_id__in=valid_enquiries)

    if veh_no:
        trips = trips.filter(tr_vehiclenumber__icontains=veh_no)

    trips = trips.order_by('-tr_created_at')

    # ------------------------------------------------
    # PRE-FETCH RELATED DATA (NO PAGINATION)
    # ------------------------------------------------
    trips_list = list(trips)
    trip_ids = [t.id for t in trips_list]
    trip_enquiries = [t.tr_enquirynumber_id for t in trips_list]

    allotments = Vehicle_allotmentInfo.objects.filter(
        va_enquirynumber_id__in=trip_enquiries
    ).select_related('va_vendor')

    invoices = TransInvoiceInfo.objects.filter(
        ti_trip_id__in=trip_ids
    )

    expenses = Driverexpense.objects.filter(
        trip_number__in=trip_ids
    )

    # ------------------------------------------------
    # MAPS
    # ------------------------------------------------
    allotment_map = {}
    for a in allotments:
        key = (
            a.va_enquirynumber_id,
            str(a.va_vehiclenumber) if a.va_vehiclenumber else a.va_vehiclenumber_mkt
        )
        allotment_map[key] = a

    invoice_obj_map = {i.ti_trip_id: i for i in invoices}
    invoice_map = {i.ti_trip_id: i.ti_inv_no for i in invoices}

    expense_map = {}
    for e in expenses:
        if e.trip_number and str(e.trip_number).isdigit():
            expense_map.setdefault(int(e.trip_number), []).append(e)

    # VENDOR BILLS (MARKET BILLS)
    from ..models import MarketBillInfo
    all_bills = MarketBillInfo.objects.all().only('mb_bill_no', 'mb_selected_trips')
    bill_no_map = {}
    for b in all_bills:
        if b.mb_selected_trips:
            ids = [tid.strip() for tid in b.mb_selected_trips.split(',') if tid.strip()]
            for tid in ids:
                try:
                    bill_no_map[int(tid)] = b.mb_bill_no
                except: pass

    # PRE-FETCH VENDOR RATES (SPEED UP)
    # ------------------------------------------------
    # Filter rates by the vendors and locations present in the trips (optional but safer)
    vendor_ids = set(a.va_vendor_id for a in allotments if a.va_vendor_id)
    rates = VendorratemasterInfo1.objects.filter(
        vr1_vendor_id__in=vendor_ids
    ).values('vr1_fromlocation_id', 'vr1_tolocation_id', 'vr1_vehicletype_id', 'vr1_vendor_id', 'vr1_rate')
    
    rate_map = {
        (r['vr1_fromlocation_id'], r['vr1_tolocation_id'], r['vr1_vehicletype_id'], r['vr1_vendor_id']): r['vr1_rate']
        for r in rates
    }

    # ------------------------------------------------
    # BUILD TABLE
    # ------------------------------------------------
    data_rows = []

    for idx, trip in enumerate(trips_list, start=1):

        # ---------------- SELLING ----------------
        # For MARKET vehicles: Prioritize Invoice charges over Trip detail fields
        # because the trip detail fields (tc_loadingcost, etc.) are often overwritten
        # with BUYING costs during the Market Bill entry process.
        inv = invoice_obj_map.get(trip.id)

        selling_trip = (safe_num(inv.ti_transportation_charges) if inv else (safe_num(trip.tc_tripcost) if trip.tc_tripcost_check else 0.0))
        
        if trip.tr_vehiclesource_id == 3: # 3 = MARKET
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

        # ---------------- BUYING ----------------
        # Try to find allotment with more flexible vehicle number matching
        allotment = allotment_map.get((trip.tr_enquirynumber_id, trip.tr_vehiclenumber))
        if not allotment and trip.tr_vehiclenumber:
            # Fallback: search for allotment with normalized vehicle number
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
            
            # LOOKUP PRE-FETCHED RATES
            if allotment.va_vendor:
                # Fallback for vehicle type ID (market vehicles sometimes use placed_id)
                v_type_id = trip.tr_vehicletype_id or (trip.tr_vehicletype_placed_id if hasattr(trip, 'tr_vehicletype_placed_id') else None)
                
                key = (
                    trip.tr_departedlocation_id,
                    trip.tr_reportedlocation_id,
                    v_type_id,
                    allotment.va_vendor_id
                )
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
            # Direct field mapping
            buying_loading += safe_num(e.de_loadingcost)
            buying_unloading += safe_num(e.de_unloadingcost)
            buying_weighment += safe_num(e.de_weighmentcost)
            buying_aai += safe_num(e.de_supervisorcost)
            buying_parking += safe_num(e.de_parkingcost)
            buying_rto += safe_num(e.de_rtocost)
            buying_batta += safe_num(e.de_battacost)

            # Categorize based on expense type for types without specific fields
            exp_type_str = str(e.de_expense_type).lower() if e.de_expense_type else ""
            if "toll" in exp_type_str:
                buying_toll += safe_num(e.de_total_cost)
            elif "halting" in exp_type_str:
                buying_halting += safe_num(e.de_total_cost)
            elif "handling" in exp_type_str:
                buying_handling += safe_num(e.de_total_cost)

        # MARKET vehicles: Include costs from Market Bill saved in Tripdetail fields
        # (Since Market Bill view updates these instead of creating separate Driverexpenses)
        if trip.tr_vehiclesource_id == 3: # MARKET
            buying_loading += safe_num(trip.tc_loadingcost)
            buying_unloading += safe_num(trip.tc_unloadingcost)
            buying_weighment += safe_num(trip.tc_weighmentcost)
            buying_aai += safe_num(trip.tc_supervisorcost)
            buying_parking += safe_num(trip.tc_parkingcost)
            buying_halting += (safe_num(trip.tc_haltingcost))
            buying_handling += safe_num(trip.tc_handlingcost)

        total_buying = (
            buying_trip_cost +
            buying_loading +
            buying_unloading +
            buying_weighment +
            buying_toll +
            buying_halting +
            buying_handling +
            buying_parking +
            buying_rto +
            buying_batta
        )

        profit = total_selling - total_buying

        profit_pct_selling = (profit / total_selling * 100) if total_selling > 0 else 0
        profit_pct_buying = (profit / total_buying * 100) if total_buying > 0 else 0

        row = [
            idx,
            # Efficient date selection
            (lambda: (
                next((d for d in [
                    trip.tr_loading_time, trip.tr_departeddate, trip.tr_departeddate_pickup,
                    trip.tr_departeddate_delivery, trip.tr_reporteddate, trip.tr_reporteddate_pickup,
                    trip.tr_reporteddate_delivery, trip.tr_unloading_time, trip.tr_dock_in_time,
                    trip.tr_dock_out_time, trip.tr_created_at
                ] if d and (not selected_month or selected_month == '0' or d.month == int(selected_month)) and 
                  (not selected_year or selected_year == '0' or d.year == int(selected_year))), 
                next((d for d in [
                    trip.tr_loading_time, trip.tr_departeddate, trip.tr_departeddate_pickup,
                    trip.tr_departeddate_delivery, trip.tr_reporteddate, trip.tr_reporteddate_pickup,
                    trip.tr_reporteddate_delivery, trip.tr_unloading_time, trip.tr_dock_in_time,
                    trip.tr_dock_out_time, trip.tr_created_at
                ] if d), None))
            ))().strftime("%d-%m-%Y") if any([
                trip.tr_loading_time, trip.tr_departeddate, trip.tr_departeddate_pickup,
                trip.tr_departeddate_delivery, trip.tr_reporteddate, trip.tr_reporteddate_pickup,
                trip.tr_reporteddate_delivery, trip.tr_unloading_time, trip.tr_dock_in_time,
                trip.tr_dock_out_time, trip.tr_created_at
            ]) else "",

            safe_str(trip.tr_consignmentnumber),
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_str(trip.tr_enquirynumber.en_customername),
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype),

            # SELLING
            selling_trip,
            selling_toll,
            selling_loading,
            selling_unloading,
            selling_weighment,
            selling_halting,
            selling_handling,
            selling_parking,
            total_selling,

            # REFERENCES
            invoice_map.get(trip.id, ""),
            vendor_name,
            bill_no_map.get(trip.id, ""),

            # BUYING
            buying_trip_cost,
            buying_toll,
            buying_loading,
            buying_unloading,
            buying_weighment,
            buying_halting,
            buying_handling,
            buying_parking,
            total_buying,

            # PROFIT
            round(profit, 2),
            f"{round(profit_pct_selling, 2)}%",
            f"{round(profit_pct_buying, 2)}%",
        ]

        data_rows.append(row)

    # Fetch only vendors that have been used in MARKET vehicle allotments (source 3)
    # or have MARKET vehicles in master (ownership 3)
    market_vendor_ids_allotment = Vehicle_allotmentInfo.objects.filter(
        va_vehiclesource_id=3, # MARKET
        va_vendor__isnull=False
    ).values_list('va_vendor_id', flat=True).distinct()
    
    market_vendor_ids_master = VehiclemasterInfo.objects.filter(
        vm_ownership_id=3, # MARKET
        vm_vendor__isnull=False
    ).values_list('vm_vendor_id', flat=True).distinct()
    
    all_vendors = Vendor_info.objects.filter(
        id__in=set(list(market_vendor_ids_allotment) + list(market_vendor_ids_master))
    ).order_by('vend_name')

    # Get vehicle numbers for the selected vendor
    vehicle_numbers = []
    if vendor_id:
        # 1. Market field in allotments (source 3)
        va_mkt_veh = Vehicle_allotmentInfo.objects.filter(
            va_vendor_id=vendor_id,
            va_vehiclesource_id=3,
            va_vehiclenumber_mkt__isnull=False
        ).exclude(va_vehiclenumber_mkt="").values_list('va_vehiclenumber_mkt', flat=True).distinct()
        
        # 2. Master field in allotments (source 3)
        va_mast_veh = Vehicle_allotmentInfo.objects.filter(
            va_vendor_id=vendor_id,
            va_vehiclesource_id=3,
            va_vehiclenumber__isnull=False
        ).values_list('va_vehiclenumber__vm_registrationnumber', flat=True).distinct()
        
        # 3. Dedicated Market vehicles in master (ownership 3)
        vm_mast_veh = VehiclemasterInfo.objects.filter(
            vm_vendor_id=vendor_id,
            vm_ownership_id=3
        ).exclude(vm_registrationnumber__isnull=True).exclude(vm_registrationnumber="").values_list('vm_registrationnumber', flat=True).distinct()

        vehicle_numbers = sorted(set(va_mkt_veh) | set(va_mast_veh) | set(vm_mast_veh))
    else:
        # If no vendor, show all vehicles currently in the filtered trips table
        vehicle_numbers = sorted(trips.values_list('tr_vehiclenumber', flat=True).distinct())

    return render(request, "asset_mgt_app/vendor_p_l_mkt_report.html", {
        'first_name': first_name,
        'form': form,
        'headers': VENDOR_PL_MKT_MKT_HEADERS,
        'data_rows': data_rows,

        'selected_month': selected_month,
        'selected_year': selected_year,
        'from_location': from_loc_id,
        'to_location': to_loc_id,
        'branch': branch,
        'vendor_id': int(vendor_id) if vendor_id else None,
        'veh_no': veh_no,
        'all_vendors': all_vendors,
        'vehicle_numbers': vehicle_numbers,
    })



@login_required(login_url='login_page')
def vendor_p_l_attached_report_view(request):
    first_name = request.session.get('first_name')

    from ..models import Vehicle_allotmentInfo, TransInvoiceInfo, Driverexpense, VehiclemasterInfo, VehicletypeInfo, MarketBillInfo, ConsignmentgoodsInfo

    if request.method == "POST":
        form = DmrForm(request.POST)
    else:
        form = DmrForm()


    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')
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

    # Identifty all invoiced trip IDs (Linked directly or via consignment/goods)
    invoiced_trip_ids = list(TransInvoiceInfo.objects.filter(ti_trip__isnull=False).values_list('ti_trip_id', flat=True))
    invoiced_cons_ids = TransInvoiceInfo.objects.filter(ti_consignment__isnull=False).values_list('ti_consignment_id', flat=True)
    invoiced_goods_ids = TransInvoiceInfo.objects.filter(ti_goods__isnull=False).values_list('ti_goods_id', flat=True)

    # Trips from consignment links
    trips_from_cons = list(TripdetailInfo.objects.filter(tr_consignmentnumber_id__in=invoiced_cons_ids).values_list('id', flat=True))

    # Trips from goods links
    cons_from_goods = ConsignmentgoodsInfo.objects.filter(id__in=invoiced_goods_ids).values_list('cg_consignmentnumber_id', flat=True)
    trips_from_goods = list(TripdetailInfo.objects.filter(tr_consignmentnumber_id__in=cons_from_goods).values_list('id', flat=True))
    
    # Combined set of all invoiced trip IDs
    all_invoiced_ids = set(invoiced_trip_ids + trips_from_cons + trips_from_goods)

    # BASE TRIPS
    # ------------------------------------------------
    trips = TripdetailInfo.objects.filter(
        id__in=all_invoiced_ids,
        tc_financestatus_id__in=[2, 7],
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

    # ------------------------------------------------
    # FILTERS
    # ------------------------------------------------


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

    if vehicle_type_id:
        trips = trips.filter(tr_vehicletype_id=vehicle_type_id)

    if vendor_id:
        # Filter trips by vehicles belonging to the selected vendor
        vendor_vehicles = VehiclemasterInfo.objects.filter(vm_vendor_id=vendor_id).values_list('vm_registrationnumber', flat=True)
        trips = trips.filter(tr_vehiclenumber__in=vendor_vehicles)

    if veh_no:
        trips = trips.filter(tr_vehiclenumber__icontains=veh_no)

    trips = trips.order_by('-tr_created_at')

    # ------------------------------------------------
    # PRE-FETCH RELATED DATA (FULL DATA)
    # ------------------------------------------------
    trips_list = list(trips)
    trip_ids = [t.id for t in trips_list]
    trip_enquiries = [t.tr_enquirynumber_id for t in trips_list]

    va_map = {
        va.va_enquirynumber_id: va
        for va in Vehicle_allotmentInfo.objects.filter(
            va_enquirynumber_id__in=trip_enquiries
        ).select_related('va_vendor')
    }

    inv_map = {
        inv.ti_trip_id: inv
        for inv in TransInvoiceInfo.objects.filter(
            ti_trip_id__in=trip_ids
        )
    }

    driver_expense_map = {}
    trip_numbers = [t.tr_tripnumber for t in trips_list if t.tr_tripnumber]
    expenses = Driverexpense.objects.filter(trip_number__in=trip_numbers)
    # Build two lookups: by trip number string AND by trip ID (for safety)
    trip_id_by_tripnum = {t.tr_tripnumber: t.id for t in trips_list if t.tr_tripnumber}
    for exp in expenses:
        trip_str = exp.trip_number
        if trip_str and trip_str in trip_id_by_tripnum:
            t_id = trip_id_by_tripnum[trip_str]
            driver_expense_map.setdefault(t_id, []).append(exp)

    # VENDOR BILLS (MARKET & ATTACHED BILLS)
    bill_no_map = {}
    
    # Market Bills
    all_market_bills = MarketBillInfo.objects.all().only('mb_bill_no', 'mb_selected_trips')
    for b in all_market_bills:
        if b.mb_selected_trips:
            ids = [tid.strip() for tid in b.mb_selected_trips.split(',') if tid.strip()]
            for tid in ids:
                try:
                    # Try as ID first
                    bill_no_map[int(tid)] = b.mb_bill_no
                except:
                    # Fallback to Trip Number string
                    bill_no_map[tid] = b.mb_bill_no

    # Attached Bills
    attached_bill_map = {}
    from ..models import AttachedBillInfo
    all_attached_bills = AttachedBillInfo.objects.all().only('ab_bill_no', 'ab_selected_trips', 'ab_buy_cost', 'ab_total_km_run')
    for b in all_attached_bills:
        if b.ab_selected_trips:
            ids = [tid.strip() for tid in b.ab_selected_trips.split(',') if tid.strip()]
            for tid in ids:
                try:
                    # Try as ID first
                    bill_no_map[int(tid)] = b.ab_bill_no
                    attached_bill_map[int(tid)] = b
                except:
                    # Fallback to Trip Number string
                    bill_no_map[tid] = b.ab_bill_no
                    attached_bill_map[tid] = b

    # Vehicle Vendor Map (Fallback for Attached)
    veh_nos = [t.tr_vehiclenumber for t in trips_list if t.tr_vehiclenumber]
    
    # Use stripped keys for robustness
    veh_vendor_map = {}
    veh_objs = VehiclemasterInfo.objects.filter(vm_registrationnumber__in=veh_nos).select_related('vm_vendor')
    for v in veh_objs:
        if v.vm_registrationnumber:
            veh_vendor_map[v.vm_registrationnumber.strip()] = v.vm_vendor

    # ------------------------------------------------
    # BUILD REPORT
    # ------------------------------------------------
    data_rows = []

    for idx, trip in enumerate(trips_list, start=1):

        # ---------------- SELLING ----------------
        # Fallback to Invoice charges if trip record is missing them
        inv = inv_map.get(trip.id)

        selling_trip = (safe_num(inv.ti_transportation_charges) if inv else (safe_num(trip.tc_tripcost) if trip.tc_tripcost_check else 0.0))
        selling_toll = (safe_num(inv.ti_toll_charges) if inv else (safe_num(trip.tc_tollcost) if trip.tc_tollcost_check else 0.0))
        selling_aai = (safe_num(inv.ti_docket_charges) if inv else (safe_num(trip.tc_supervisorcost) if trip.tc_supervisorcost_check else 0.0))
        selling_loading = (safe_num(inv.ti_loading_charges) if inv else (safe_num(trip.tc_loadingcost) if trip.tc_loadingcost_check else 0.0))
        selling_unloading = (safe_num(inv.ti_unloading_charges) if inv else (safe_num(trip.tc_unloadingcost) if trip.tc_unloadingcost_check else 0.0))
        selling_weighment = (safe_num(inv.ti_weighment_charges) if inv else (safe_num(trip.tc_weighmentcost) if trip.tc_weighmentcost_check else 0.0))
        selling_halting = (safe_num(inv.ti_halting_charges) if inv else ((safe_num(trip.tc_haltingcost) if trip.tc_haltingcost_check else 0) + (safe_num(trip.tc_total_halting_cost) if trip.tc_total_halting_cost_check else 0)))
        selling_handling = (safe_num(inv.ti_handling_charges) if inv else (safe_num(trip.tc_handlingcost) if trip.tc_handlingcost_check else 0.0))

        selling_parking = (safe_num(inv.ti_parking_charges) if inv else (safe_num(trip.tc_parkingcost) if trip.tc_parkingcost_check else 0.0))
        selling_rto = safe_num(trip.tc_rtocost) if trip.tc_rtocost_check else 0.0
        selling_beta = safe_num(trip.tc_betacost) if trip.tc_betacost_check else 0.0
        selling_cancellation = safe_num(trip.tc_cancellation) if trip.tc_cancellation_check else 0.0

        total_selling = (
            selling_trip + selling_toll + selling_aai +
            selling_loading + selling_unloading +
            selling_weighment + selling_halting +
            selling_handling +
            selling_parking + selling_rto + selling_beta + selling_cancellation
        )

        # ---------------- BUYING ----------------
        va_info = va_map.get(trip.tr_enquirynumber_id)

        vendor_name = ""
        if va_info and va_info.va_vendor:
            vendor_name = str(va_info.va_vendor)
        else:
            # Fallback to Vehicle Master
            v_key = trip.tr_vehiclenumber.strip() if trip.tr_vehiclenumber else ""
            v_obj = veh_vendor_map.get(v_key)
            if v_obj:
                vendor_name = str(v_obj)

        reported_km = safe_num(trip.tr_reportedkm_delivery or trip.tr_reportedkm)
        departed_km = safe_num(trip.tr_departedkm)
        km_run = reported_km - departed_km if reported_km and departed_km else 0

        ab_bill = attached_bill_map.get(trip.id) or attached_bill_map.get(trip.tr_tripnumber)

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

        trip_expenses = driver_expense_map.get(trip.id, [])

        buy_loading = buy_unloading = buy_weighment = buy_aai = 0.0
        buy_toll = safe_num(trip.tc_tollcost)
        buy_halting = buy_handling = buy_parking = buy_rto = buy_batta = 0.0

        for e in trip_expenses:
            buy_loading += safe_num(e.de_loadingcost)
            buy_unloading += safe_num(e.de_unloadingcost)
            buy_weighment += safe_num(e.de_weighmentcost)
            buy_handling += safe_num(e.de_supervisorcost)  # Handling cost = supervisor cost
            buy_parking += safe_num(e.de_parkingcost)
            buy_rto += safe_num(e.de_rtocost)
            buy_batta += safe_num(e.de_battacost)

            # Categorize based on expense type for halting
            exp_type_str = str(e.de_expense_type).lower() if e.de_expense_type else ""
            if "toll" in exp_type_str and not ab_bill:
                buy_toll += safe_num(e.de_total_cost)
            elif "halting" in exp_type_str:
                buy_halting += safe_num(e.de_total_cost)

        total_buying = (
            buying_trip_cost +
            buy_loading +
            buy_unloading +
            buy_weighment +
            buy_toll +
            buy_halting +
            buy_handling +
            buy_parking +
            buy_rto +
            buy_batta
        )

        # KM & PROFIT ----------------

        buy_rate_per_km = (total_buying / km_run) if km_run > 0 else 0

        profit = total_selling - total_buying
        profit_pct = (profit / total_selling * 100) if total_selling > 0 else 0

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

        row = [
            idx,
            display_date,

            safe_str(trip.tr_consignmentnumber),
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_str(trip.tr_enquirynumber.en_customername),
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype),

            selling_trip,
            selling_toll,
            selling_parking, # AAI column shows ONLY Parking charges as requested
            selling_loading,
            selling_unloading,
            selling_weighment,
            selling_halting,
            selling_handling,
            total_selling,
            
            vendor_name,
            bill_no_map.get(trip.id) or bill_no_map.get(trip.tr_tripnumber, ""),

            # BUYING BREAKDOWN
            buying_trip_cost,
            buy_toll,
            buy_parking,
            buy_loading,
            buy_unloading,
            buy_weighment,
            buy_handling,
            
            round(total_buying, 2),

            round(profit, 2),
            f"{round(profit_pct, 2)}%"
        ]

        data_rows.append(row)

    # Fetch only vendors that have been used in ATTACHED vehicle allotments (source 2)
    # or have ATTACHED vehicles in master (ownership 2)
    attached_vendor_ids_allotment = Vehicle_allotmentInfo.objects.filter(
        va_vehiclesource_id=2, # ATTACHED
        va_vendor__isnull=False
    ).values_list('va_vendor_id', flat=True).distinct()
    
    attached_vendor_ids_master = VehiclemasterInfo.objects.filter(
        vm_ownership_id=2, # ATTACHED
        vm_vendor__isnull=False
    ).values_list('vm_vendor_id', flat=True).distinct()
    
    all_vendors = Vendor_info.objects.filter(
        id__in=set(list(attached_vendor_ids_allotment) + list(attached_vendor_ids_master))
    ).order_by('vend_name')

    # Get vehicle numbers for the selected vendor from both sources
    vehicle_numbers = []

    if vendor_id:

        # Source 1: Allotments (Strictly Attached)
        va_veh_qs = Vehicle_allotmentInfo.objects.filter(
            va_vendor_id=vendor_id,
            va_vehiclesource_id=2, # ATTACHED
            va_vehiclenumber__isnull=False
        ).values_list(
            'va_vehiclenumber__vm_registrationnumber',
            flat=True
        ).distinct()

        # Source 2: Master (Strictly Attached)
        vm_veh_qs = VehiclemasterInfo.objects.filter(
            vm_vendor_id=vendor_id,
            vm_ownership_id=2 # ATTACHED
        ).exclude(
            vm_registrationnumber__isnull=True
        ).exclude(
            vm_registrationnumber=""
        ).values_list(
            'vm_registrationnumber',
            flat=True
        ).distinct()

        vehicle_numbers = sorted(
            set(va_veh_qs) | set(vm_veh_qs)
        )
    else:
        # If no vendor, show all vehicles currently in the filtered trips table
        vehicle_numbers = sorted(trips.values_list('tr_vehiclenumber', flat=True).distinct())


    print("Selected Vendor ID:", vendor_id)
    print("Vehicle Numbers Found:", vehicle_numbers)
    print("Vendor ID:", vendor_id)
    print("VA Vehicles:", list(va_veh_qs) if vendor_id else "No vendor")
    print("VM Vehicles:", list(vm_veh_qs) if vendor_id else "No vendor")
    print("Final Vehicle Numbers:", vehicle_numbers)
    return render(request, "asset_mgt_app/vendor_p_l_attached_report.html", {
        'first_name': first_name,
        'form': form,
        'headers': VENDOR_PL_ATTACHED_HEADERS,
        'data_rows': data_rows,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'from_location': from_loc_id,
        'to_location': to_loc_id,
        'vendor_id': int(vendor_id) if vendor_id else None,
        'vehicle_type_id': int(vehicle_type_id) if vehicle_type_id else None,
        'veh_no': veh_no,
        'all_vendors': all_vendors,
        'vehicle_types': VehicletypeInfo.objects.all().order_by('vt_vehicletype'),
        'vehicle_numbers': vehicle_numbers,
    })
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from ..models import VehiclemasterInfo

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
            if b_id == 1: # BLR
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='BLR')
            elif b_id == 2: # MAA
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='MAA')
        except (ValueError, TypeError):
            pass

    if vehicle_source_id:
        trips = trips.filter(tr_vehiclesource_id=vehicle_source_id)

    trips = trips.order_by('-tr_created_at')

    select_all = request.POST.get('select_all') or request.GET.get('select_all')

    # Performance Optimization: Limit results
    if select_all == 'true':
        trips = trips[:2000] # Safe upper limit
    else:
        # Default view or filtered view: reasonable limit for fast load
        if not (vehicle_search or customer_id or dept_id or (selected_month and selected_month != '0') or branch_id or vehicle_source_id):
            trips = trips[:150] # Very fast initial load
        else:
            trips = trips[:1000] # Fast filtered load

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
            safe_str(trip.tr_vehicletype),
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_str(trip.tr_vehiclenumber),
            trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else "",
            trip.tr_reporteddate.strftime("%d-%m-%Y") if trip.tr_reporteddate else "",
            safe_str(trip.tr_drivername),
            "", # Whatsapp Delivered time
            "", # Delivered Status
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
            if b_id == 1: # BLR
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='BLR')
            elif b_id == 2: # MAA
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='MAA')
            elif b_id == 3: # PNY
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='PNY')
            elif b_id == 4: # HYD
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='HYD')
        except: pass

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
                'vehicle_type': safe_str(trip.tr_vehicletype),
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
    first_name = request.session.get('first_name')

    # -------------------------------
    # FILTER FORM (GET)
    # -------------------------------
    form = DmrForm(request.GET or None)

    vehicle_number = request.GET.get('vehicle_search')
    selected_month = request.GET.get('month')
    selected_year = request.GET.get('year')

    # -------------------------------
    # BASE QUERY – OWN VEHICLES ONLY
    # -------------------------------
    trips = TripdetailInfo.objects.filter(
        tc_financestatus_id__in=[2, 7],     # Closed / Settled
        tr_vehiclesource_id__in=[1, 2]      # Own vehicles
    ).select_related(
        'tr_vehicletype',
        'tr_departedlocation',
        'tr_reportedlocation'
    )

    # -------------------------------
    # FILTERS
    # -------------------------------
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

    if vehicle_number:
        trips = trips.filter(tr_vehiclenumber=vehicle_number)

    trips_list = list(trips.order_by('-tr_created_at'))
    trip_ids = [str(t.id) for t in trips_list]

    # -------------------------------
    # PREFETCH EXPENSES (TOLL)
    # -------------------------------
    expenses = (
        Driverexpense.objects
        .filter(trip_number__in=trip_ids)
        .select_related('de_expense_type')
    )

    expense_map = {}
    for e in expenses:
        if e.trip_number and str(e.trip_number).isdigit():
            expense_map.setdefault(int(e.trip_number), []).append(e)

    # -------------------------------
    # VEHICLE MASTER (FIXED COSTS)
    # -------------------------------
    vehicle_map = {
        v.vm_registrationnumber: v
        for v in VehiclemasterInfo.objects.all()
    }

    # -------------------------------
    # BUILD TABLE
    # -------------------------------
    data_rows = []

    for idx, trip in enumerate(trips_list, start=1):

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
        date_val = trip_date.strftime("%d-%m-%Y") if trip_date else ""

        # -------- SELLING -------- - Respecting checkboxes
        selling_total = (
            (safe_num(trip.tc_tripcost) if trip.tc_tripcost_check else 0) +
            (safe_num(trip.tc_tollcost) if trip.tc_tollcost_check else 0) +
            (safe_num(trip.tc_supervisorcost) if trip.tc_supervisorcost_check else 0) +
            (safe_num(trip.tc_loadingcost) if trip.tc_loadingcost_check else 0) +
            (safe_num(trip.tc_unloadingcost) if trip.tc_unloadingcost_check else 0) +
            (safe_num(trip.tc_weighmentcost) if trip.tc_weighmentcost_check else 0) +
            (safe_num(trip.tc_haltingcost) if trip.tc_haltingcost_check else 0) +
            (safe_num(trip.tc_total_halting_cost) if trip.tc_total_halting_cost_check else 0) +
            (safe_num(trip.tc_handlingcost) if trip.tc_handlingcost_check else 0) +
            (safe_num(trip.tc_parkingcost) if trip.tc_parkingcost_check else 0) +
            (safe_num(trip.tc_rtocost) if trip.tc_rtocost_check else 0) +
            (safe_num(trip.tc_betacost) if trip.tc_betacost_check else 0) +
            (safe_num(trip.tc_cancellation) if trip.tc_cancellation_check else 0)
        )

        # -------- TOLL EXPENSE --------
        toll_expense = 0.0
        for e in expense_map.get(trip.id, []):
            if e.de_expense_type and 'toll' in str(e.de_expense_type).lower():
                toll_expense += safe_num(e.de_total_cost)

        # -------- FIXED VEHICLE COSTS (REFERENCE) --------
        vm = vehicle_map.get(trip.tr_vehiclenumber)

        depreciation = safe_num(vm.vm_yearofdepreciation) if vm else 0
        permit = safe_num(vm.vm_permitamount) if vm else 0
        fc = safe_num(vm.vm_fcamount) if vm else 0
        road_tax = safe_num(vm.vm_roadtaxamount) if vm else 0

        row = [
            idx,
            date_val,
            safe_str(trip.tr_vehiclenumber),
            safe_num(trip.tc_tollcost) if trip.tc_tollcost_check else 0,
            safe_num(trip.tc_supervisorcost) if trip.tc_supervisorcost_check else 0,
            safe_num(trip.tc_loadingcost) if trip.tc_loadingcost_check else 0,
            safe_num(trip.tc_unloadingcost) if trip.tc_unloadingcost_check else 0,
            safe_num(trip.tc_weighmentcost) if trip.tc_weighmentcost_check else 0,
            (safe_num(trip.tc_haltingcost) if trip.tc_haltingcost_check else 0) + (safe_num(trip.tc_total_halting_cost) if trip.tc_total_halting_cost_check else 0),
            safe_num(trip.tc_handlingcost) if trip.tc_handlingcost_check else 0,
            selling_total,
            toll_expense,
            depreciation,
            permit,
            fc,
            road_tax,
        ]

        data_rows.append(row)

    # -------------------------------
    # CONTEXT
    # -------------------------------
    context = {
        'first_name': first_name,
        'form': form,
        'headers': OWN_VEHICLE_PL_HEADERS,
        'data_rows': data_rows,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'vehicle_number': vehicle_number,
        'all_vehicles': VehiclemasterInfo.objects.filter(vm_ownership_id__in=[1,2,3])
    }

    return render(request, "asset_mgt_app/own_vehicle_pl_report.html", context)


@login_required(login_url='login_page')
def claim_pending_report_view(request):
    first_name = request.session.get('first_name')

    # Fetch all vehicles present in TransCustomerClaimsInfo for the dropdown
    claim_vehicles = TransCustomerClaimsInfo.objects.values_list('tcc_veh_no', flat=True).distinct().order_by('tcc_veh_no')
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
        branch = "Chennai" if cust_name_upper.endswith("MAA") else ("Bangalore" if cust_name_upper.endswith("BLR") else "")

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
            safe_num(claim.tcc_claim_amount)
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

    
    if request.method == "POST":
        form = DmrForm(request.POST)
    else:
        form = DmrForm()
    
    customer_id = request.POST.get('dmr_customer')
    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')
    branch_id = request.POST.get('branch')
    vehicle_source_id = request.POST.get('vehicle_source')
    
    # Base Query
    trips = TripdetailInfo.objects.all().select_related(
        'tr_enquirynumber', 'tr_enquirynumber__en_customername', 'tr_enquirynumber__en_customerdepartment',
        'tr_vehicletype', 'tr_departedlocation', 'tr_reportedlocation',
        'tr_consignmentnumber', 'tr_vehiclesource'
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

    if branch_id:
        trips = trips.filter(tr_enquirynumber__en_branch_id=branch_id)

    if vehicle_source_id:
        trips = trips.filter(tr_vehiclesource_id=vehicle_source_id)
    else:
        # Default to Attached & Own only
        trips = trips.filter(tr_vehiclesource_id__in=[1, 2])

    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) |
            Q(tr_departeddate__year=selected_year) |
            Q(tr_departeddate_pickup__year=selected_year) |
            Q(tr_reporteddate__year=selected_year) |
            Q(tr_unloading_time__year=selected_year) |
            Q(tr_created_at__year=selected_year)
        )
            
    trips = trips.order_by('-tr_created_at')
    
    paginator = Paginator(trips, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    trip_ids = [t.id for t in page_obj]
    # Filter valid consignment IDs (not None)
    consignment_ids = [t.tr_consignmentnumber.id for t in page_obj if t.tr_consignmentnumber]

    # Fetch Expenses for "Buying Halting"
    expenses = Driverexpense.objects.filter(trip_number__in=trip_ids).select_related('de_expense_type')
    expense_map = {}
    
    for e in expenses:
        if e.trip_number and str(e.trip_number).isdigit():
            exp_trip_id = int(e.trip_number)
            if exp_trip_id not in expense_map:
                expense_map[exp_trip_id] = 0.0
            
            # Check if expense is related to Halting
            if e.de_expense_type and 'halting' in str(e.de_expense_type).lower():
                expense_map[exp_trip_id] += safe_num(e.de_total_cost)
            
    # Fetch Consignment Goods for Consignor/Consignee
    goods = ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber_id__in=consignment_ids).select_related(
        'cg_consigner', 'cg_consignee'
    ).order_by('id')
    
    goods_map = {}
    for g in goods:
        cid = g.cg_consignmentnumber_id
        if cid not in goods_map:
            goods_map[cid] = {"consignors": set(), "consignees": set()}
            
        if g.cg_consigner:
            goods_map[cid]["consignors"].add(str(g.cg_consigner).strip())
        if g.cg_consignee:
            goods_map[cid]["consignees"].add(str(g.cg_consignee).strip())

    data_rows = []
    
    for idx, trip in enumerate(page_obj, start=(page_obj.start_index() if hasattr(page_obj, 'start_index') else 1)):
        
        # --- Basic Details ---
        branch = safe_str(trip.tr_enquirynumber.en_branch if hasattr(trip.tr_enquirynumber, 'en_branch') else '') 
        
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
        date_val = trip_date.strftime("%d-%m-%Y") if trip_date else ""
        veh_no = safe_str(trip.tr_vehiclenumber)
        veh_type = safe_str(trip.tr_vehicletype)
        customer = safe_str(trip.tr_enquirynumber.en_customername)
        dept = safe_str(trip.tr_enquirynumber.en_customerdepartment)
        vertical = safe_str(trip.tr_enquirynumber.en_unit if hasattr(trip.tr_enquirynumber, 'en_unit') else '')
        
        consignor = ""
        consignee = ""
        cnote = ""
        
        if trip.tr_consignmentnumber:
            cnote = safe_str(trip.tr_consignmentnumber.co_consignmentnumber)
            # Lookup from goods map
            if trip.tr_consignmentnumber.id in goods_map:
                m = goods_map[trip.tr_consignmentnumber.id]
                consignor = ", ".join(sorted(list(m["consignors"])))
                consignee = ", ".join(sorted(list(m["consignees"])))
            
            # Fallback to Enquiry locations if party names are still empty
            if not consignor and trip.tr_enquirynumber:
                consignor = safe_str(trip.tr_enquirynumber.en_fromlocaion)
            if not consignee and trip.tr_enquirynumber:
                consignee = safe_str(trip.tr_enquirynumber.en_tolocation)

            cust_name = safe_str(trip.tr_enquirynumber.en_customername).strip().upper()
            branch = "Chennai" if cust_name.endswith("MAA") else ("Bangalore" if cust_name.endswith("BLR") else "")
            
        # --- Halting ---
        # Halting Start: Vehicle Reported at Loading (tr_departeddate_pickup)
        # Halting End: Dock-In at Loading (tr_loading_time)
        h_start = trip.tr_departeddate_pickup
        h_end = trip.tr_loading_time
        halting_start_str = h_start.strftime("%d-%m-%Y %H:%M") if h_start else ""
        halting_end_str = h_end.strftime("%d-%m-%Y %H:%M") if h_end else ""
        halting_days = safe_num(trip.tc_no_of_days_halting)

        buying_halting = expense_map.get(trip.id, 0.0)
        selling_halting = (safe_num(trip.tc_haltingcost) if trip.tc_haltingcost_check else 0) + (safe_num(trip.tc_total_halting_cost) if trip.tc_total_halting_cost_check else 0)
        diff = selling_halting - buying_halting

        # --- Pickup ---
        # Pickup Start: Dock-In at Loading (tr_loading_time)
        # Pickup End: Dock-Out at Loading (tr_dock_out_time)
        p_start = trip.tr_loading_time
        p_end = trip.tr_dock_out_time
        p_hrs = "0.0"
        p_start_str = ""
        p_end_str = ""

        if p_start and p_end:
            p_start_str = p_start.strftime("%d-%m-%Y %H:%M")
            p_end_str = p_end.strftime("%d-%m-%Y %H:%M")
            delta = p_end - p_start
            p_hrs = f"{round(delta.total_seconds() / 3600, 2)}"
        elif p_start:
            p_start_str = p_start.strftime("%d-%m-%Y %H:%M")

        # --- Delivery ---
        # Delivery Start: Dock-In at Delivery (tr_departeddate_delivery)
        # Delivery End: Dock-Out at Delivery (tr_unloading_time)
        d_start = trip.tr_departeddate_delivery
        d_end = trip.tr_unloading_time
        d_hrs = "0.0"
        d_start_str = ""
        d_end_str = ""

        if d_start and d_end:
            d_start_str = d_start.strftime("%d-%m-%Y %H:%M")
            d_end_str = d_end.strftime("%d-%m-%Y %H:%M")
            delta = d_end - d_start
            d_hrs = f"{round(delta.total_seconds() / 3600, 2)}"
        elif d_start:
             d_start_str = d_start.strftime("%d-%m-%Y %H:%M")

        row = [
            idx, branch, date_val, veh_no, veh_type, customer, dept, vertical,
            consignor, consignee, cnote,
            halting_start_str, halting_end_str, halting_days,
            buying_halting, selling_halting, diff,
            p_start_str, p_end_str, p_hrs,
            d_start_str, d_end_str, d_hrs
        ]
        data_rows.append(row)
        
    context = {
        'first_name': first_name,
        'form': form,
        'headers': HALTING_REPORT_HEADERS,
        'data_rows': data_rows,
        'page_obj': page_obj,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'customer_id': customer_id,
        'selected_branch': int(branch_id) if branch_id else None,
        'selected_source': int(vehicle_source_id) if vehicle_source_id else None,
        'all_branches': Location_info.objects.filter(id__in=[1, 2]).order_by('loc_name'),
        'vehicle_sources': OwnershipInfo.objects.filter(id__in=[1, 2]),
    }
    
    return render(request, "asset_mgt_app/halting_report.html", context)




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
            vehicle_type = safe_str(rec.mi_vehicle.vm_vehicletype) if rec.mi_vehicle and rec.mi_vehicle.vm_vehicletype else ""
        except:
            vehicle_no = ""
            vehicle_type = ""
            
        make = safe_str(rec.mi_make_model)
        
        branch_display = ""
        if rec.mi_location:
            branch_display = str(rec.mi_location.branch)
        
        job_card_no = rec.id # fallback
        prev_job_card_date = prev_rec.mi_created_at.strftime("%d-%m-%Y") if prev_rec and prev_rec.mi_created_at else ""
        prev_job_card_no = prev_rec.id if prev_rec else ""
        
        bills = rec.bills_v1.all()
        bill_nos = ", ".join([b.mnb_bill_no for b in bills if b.mnb_bill_no])

        row = [
            counter,
            branch_display,
            rec.mi_created_at.strftime("%d-%m-%Y") if rec.mi_created_at else "", # Date
            vehicle_no, # Vehicle No
            vehicle_type, # Vehicle Type
            safe_str(rec.mi_service_type), # Service Type
            rec.mi_total_km_run, # KM
            safe_num(rec.mi_budget), # PO Amount
            safe_num(rec.mi_estimated_amount), # Actual Amount
            safe_str(rec.mi_technician),  # Vendor Name logic
            safe_str(rec.mi_job_card_no), # JC No
            bill_nos # Bill No
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
            counter,                                # 1 S.No
            branch_name,                            # 2 Branch
            safe_str(rec.ins_vendor),               # 3 Vendor
            safe_str(rec.ins_name),                 # 4 Insurance Company
            safe_str(rec.ins_vehicle_no),           # 5 Vehicle No
            vehicle_type,                           # 6 Vehicle Type
            safe_str(rec.ins_type),                 # 7 Insurance Type
            expiry_date.strftime("%d-%m-%Y") if expiry_date else "",  # 8 Renewal Date
            safe_num(rec.ins_premium_amount),        # 9 Premium Amount
            safe_num(rec.ins_sum_assured),           # 10 IDV Value
            elapsed_days,                           # 11 Elapsed Days
            ds_status                               # 12 Status
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
        'all_companies': Insurance_Info.objects.filter(ins_status_id=1).values_list('ins_name', flat=True).distinct().order_by('ins_name'),
    }

    return render(
        request,
        "asset_mgt_app/insurance_renewal_report.html",
        context
    )



@login_required(login_url='login_page')
def diesel_vs_revenue_report_view(request):
    first_name = request.session.get('first_name')
    from ..models import TripdetailInfo, Fuelfillinginfo, VehiclemasterInfo, Location_info
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

    # Base Query for Trips
    trips = TripdetailInfo.objects.all().select_related(
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
                trips = trips.filter(Q(tr_enquirynumber__en_customername__cu_name__icontains='MAA') | Q(tr_consignmentnumber__co_consignmentnumber__istartswith='MAA'))
            elif "BLR" in branch_name:
                trips = trips.filter(Q(tr_enquirynumber__en_customername__cu_name__icontains='BLR') | Q(tr_consignmentnumber__co_consignmentnumber__istartswith='BLR'))
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
    trips = trips.order_by('-tr_loading_time', '-tr_created_at')

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

    # Total KM aggregation per vehicle from trips for the selected period
    km_stats_q = Q(tr_vehiclenumber__in=vehicle_numbers)
    if q_date:
        km_stats_q &= q_date
        
    v_km_map = {}
    vehicle_trips_data = TripdetailInfo.objects.filter(km_stats_q).values('tr_vehiclenumber', 'tr_reportedkm', 'tr_departedkm')
    for vtr in vehicle_trips_data:
        vno = vtr['tr_vehiclenumber']
        vkm = max(0, safe_num(vtr['tr_reportedkm']) - safe_num(vtr['tr_departedkm']))
        v_km_map[vno] = v_km_map.get(vno, 0) + vkm

    # Vehicle Master for fixed mileage
    vehicles = VehiclemasterInfo.objects.filter(vm_registrationnumber__in=vehicle_numbers).select_related('vm_vehiclemanufacturer', 'vm_vehiclemodel')
    vehicle_master_map = {v.vm_registrationnumber: v for v in vehicles}

    # Fetch Invoices and Rates for Revenue fallback
    from ..sub_models.trans_invoice_mod import TransInvoiceInfo
    from ..sub_models.rtratemaster_mod import RtratemasterInfo
    
    invoices = TransInvoiceInfo.objects.filter(ti_trip_id__in=[t.id for t in trips])
    invoice_map = {inv.ti_trip_id: inv for inv in invoices}
    
    # Standard Customer Rates Fallback
    rates = RtratemasterInfo.objects.all().values(
        'ro_customer_id', 'ro_customerdepartment_id', 'ro_fromlocation_id', 'ro_tolocation_id', 'ro_vehicletype_id', 'ro_rate'
    )
    cust_rate_map = {
        (r['ro_customer_id'], r['ro_customerdepartment_id'], r['ro_fromlocation_id'], r['ro_tolocation_id'], r['ro_vehicletype_id']): r['ro_rate']
        for r in rates
    }

    processed_rows = []
    counter = 1

    for trip in trips:
        cust_name = safe_str(trip.tr_enquirynumber.en_customername).strip().upper() if trip.tr_enquirynumber else ""
        row_branch = "Chennai" if "MAA" in cust_name or (trip.tr_consignmentnumber and "MAA" in str(trip.tr_consignmentnumber)) else \
                     ("Bangalore" if "BLR" in cust_name or (trip.tr_consignmentnumber and "BLR" in str(trip.tr_consignmentnumber)) else "")
        
        # Date selection
        dates = [trip.tr_loading_time, trip.tr_departeddate, trip.tr_created_at]
        display_date = next((d for d in dates if d), None)
        trip_date_str = display_date.strftime("%d-%m-%Y") if display_date else ""
        
        # Revenue calculation (Multi-level fallback)
        inv = invoice_map.get(trip.id)
        cons = trip.tr_consignmentnumber
        
        rev_trip = (safe_num(inv.ti_transportation_charges) if inv else (safe_num(trip.tc_tripcost) if trip.tc_tripcost_check else 0.0))
        if rev_trip == 0 and not (inv or trip.tc_tripcost_check):
            if cons and cons.co_freight_amount:
                 try:
                     # Strip non-numeric and parse
                     f_str = "".join(c for c in str(cons.co_freight_amount) if c.isdigit() or c == '.')
                     if f_str: rev_trip = float(f_str)
                 except: pass
            
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

        rev_toll = (safe_num(inv.ti_toll_charges) if inv else (safe_num(trip.tc_tollcost) if trip.tc_tollcost_check else 0.0))
        rev_aai = (safe_num(inv.ti_docket_charges) if inv else (safe_num(trip.tc_supervisorcost) if trip.tc_supervisorcost_check else 0.0))
        rev_loading = (safe_num(inv.ti_loading_charges) if inv else (safe_num(trip.tc_loadingcost) if trip.tc_loadingcost_check else 0.0))
        rev_unloading = (safe_num(inv.ti_unloading_charges) if inv else (safe_num(trip.tc_unloadingcost) if trip.tc_unloadingcost_check else 0.0))
        rev_weighment = (safe_num(inv.ti_weighment_charges) if inv else (safe_num(trip.tc_weighmentcost) if trip.tc_weighmentcost_check else 0.0))
        rev_halting = (safe_num(inv.ti_halting_charges) if inv else ((safe_num(trip.tc_haltingcost) if trip.tc_haltingcost_check else 0) + (safe_num(trip.tc_total_halting_cost) if trip.tc_total_halting_cost_check else 0)))
        rev_handling = (safe_num(inv.ti_handling_charges) if inv else (safe_num(trip.tc_handlingcost) if trip.tc_handlingcost_check else 0.0))
        rev_parking = (safe_num(inv.ti_parking_charges) if inv else (safe_num(trip.tc_parkingcost) if trip.tc_parkingcost_check else 0.0))
        rev_rto = safe_num(trip.tc_rtocost) if trip.tc_rtocost_check else 0.0
        rev_batta = safe_num(trip.tc_betacost) if trip.tc_betacost_check else 0.0
        rev_cancellation = (safe_num(inv.ti_cancellation_charges) if inv else (safe_num(trip.tc_cancellation) if trip.tc_cancellation_check else 0.0))

        revenue = rev_trip + rev_toll + rev_aai + rev_loading + rev_unloading + \
                  rev_weighment + rev_halting + rev_handling + rev_parking + \
                  rev_rto + rev_batta + rev_cancellation


        # Trip KM
        trip_km = max(0, safe_num(trip.tr_reportedkm) - safe_num(trip.tr_departedkm))

        # Stats for this vehicle in period
        v_fuel = fuel_map.get(trip.tr_vehiclenumber, {'total_cost': 0, 'total_ltr': 0})
        v_total_fuel_cost = safe_num(v_fuel['total_cost'])
        v_total_ltr = safe_num(v_fuel['total_ltr'])
        v_total_km = v_km_map.get(trip.tr_vehiclenumber, 0)

        # Formula: Diesel Expenses = Total Diesel expenses / Total KM run * trip run KM
        if v_total_km > 0:
            assigned_diesel_expense = (v_total_fuel_cost / v_total_km) * trip_km
        else:
            assigned_diesel_expense = 0

        # Formula: Actual Mileage = Total KM / Total Ltr (for the month)
        # Note: mileage is usually identical for all trips of the same vehicle in that period
        if v_total_ltr > 0:
            actual_mileage = v_total_km / v_total_ltr
        else:
            actual_mileage = 0

        diesel_vs_revenue_pct = (assigned_diesel_expense / revenue * 100) if revenue > 0 else 0

        vm = vehicle_master_map.get(trip.tr_vehiclenumber)
        mileage_fixed = safe_str(vm.vm_millage) if vm else ""
        leased_to = safe_str(trip.tr_enquirynumber.en_customername) if trip.tr_enquirynumber else ""

        processed_rows.append([
            counter,
            row_branch,
            trip_date_str,
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype),
            mileage_fixed,
            leased_to,
            trip_km,
            round(assigned_diesel_expense, 2),
            round(revenue, 2),
            f"{diesel_vs_revenue_pct:.2f}%",
            f"{actual_mileage:.2f}"
        ])
        counter += 1

    paginator = Paginator(processed_rows, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    all_vehicles = VehiclemasterInfo.objects.filter(vm_ownership_id__in=[1, 2, 3]).order_by('vm_registrationnumber')

    context = {
        'first_name': first_name,
        'form': form,
        'headers': DIESEL_VS_REVENUE_HEADERS,
        'data_rows': page_obj.object_list,
        'page_obj': page_obj,
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
        
        is_own = trip.tr_vehiclesource_id in [2] # 1=OWN, 2=ATTACHED/OWN
        
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
        enquiries = enquiries.filter(en_enquirynumber__istartswith="BLR")
    elif branch == "Chennai":
        enquiries = enquiries.filter(en_enquirynumber__istartswith="MAA")

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
    allotments = Vehicle_allotmentInfo.objects.filter(va_enquirynumber_id__in=enquiry_ids).select_related(
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
                safe_str(enq.en_created_at.strftime('%d-%m-%Y')) if enq.en_created_at else "",
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
        Q(tr_reporteddate__isnull=False) | Q(tr_unloading_time__isnull=False),
        tc_financestatus_id=7
    )

    # Apply Custom Filters
    if from_date:
        trips = trips.filter(Q(tr_reporteddate__date__gte=from_date) | Q(tr_unloading_time__date__gte=from_date))
    if to_date:
        trips = trips.filter(Q(tr_reporteddate__date__lte=to_date) | Q(tr_unloading_time__date__lte=to_date))

    if branch_id:
        try:
            b_id = int(branch_id)
            if b_id == 1: # BLR
                trips = trips.filter(tr_enquirynumber__en_customername__cu_name__icontains='BLR')
            elif b_id == 2: # MAA
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
            start_date.strftime("%d-%m-%Y") if start_date else "",
            end_date.strftime("%d-%m-%Y") if end_date else "",
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

    # Base Query: Pending Enquiries (Status 6)
    enquiries = EnquirynoteInfo.objects.filter(en_status_id=6)

    # Filter out enquiries where unassigned vehicles <= 0
    pending_ids = list(enquiries.values_list('id', flat=True))
    
    reqs = Enquirynotevehicle.objects.filter(env_enquirynumber_id__in=pending_ids).values('env_enquirynumber_id').annotate(tot=Sum('env_quantity'))
    req_map = {r['env_enquirynumber_id']: r['tot'] or 0 for r in reqs}

    allots = Vehicle_allotmentInfo.objects.filter(va_enquirynumber_id__in=pending_ids).values('va_enquirynumber_id').annotate(tot=Count('id'))
    allots_map = {a['va_enquirynumber_id']: a['tot'] or 0 for a in allots}

    valid_ids = [eid for eid in pending_ids if req_map.get(eid, 0) > allots_map.get(eid, 0)]
    
    enquiries = enquiries.filter(id__in=valid_ids).select_related(
        'en_customername', 'en_fromlocaion', 'en_tolocation'
    )

    records_total = enquiries.count()

    # Apply Filters
    if branch == "Bengaluru":
        enquiries = enquiries.filter(en_enquirynumber__istartswith="BLR")
    elif branch == "Chennai":
        enquiries = enquiries.filter(en_enquirynumber__istartswith="MAA")

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
        8: 'en_customername__cu_name',
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
    vehicle_requests = Enquirynotevehicle.objects.filter(env_enquirynumber_id__in=enquiry_ids).select_related('env_vehicletype')
    req_map = {}
    total_req_qty = {}
    for vr in vehicle_requests:
        req_map.setdefault(vr.env_enquirynumber_id, []).append(f"{vr.env_quantity} x {vr.env_vehicletype}")
        qty = vr.env_quantity or 0
        total_req_qty[vr.env_enquirynumber_id] = total_req_qty.get(vr.env_enquirynumber_id, 0) + qty

    # Fetch allotments
    allotments = Vehicle_allotmentInfo.objects.filter(va_enquirynumber_id__in=enquiry_ids)
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
            enq.en_created_at.strftime('%d-%m-%Y') if enq.en_created_at else "",
            enq.en_enquirynumber,
            safe_str(enq.en_fromlocaion),
            safe_str(enq.en_tolocation),
            veh_req_str,
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


