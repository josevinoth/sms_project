from datetime import datetime
from datetime import date
import calendar
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q, F, Sum, Value, FloatField
from django.db.models.functions import Coalesce, Trim, Upper
from ..models import TripdetailInfo, ConsignmentdetailInfo, CustomerInfo, CustomerdepartmentInfo, ConsignmentgoodsInfo, Places, VehiclemasterInfo, Driverexpense, Vehicle_allotmentInfo, VendorratemasterInfo1, Vendor_info
from ..sub_forms.dmr_report_form import DmrForm

# -------------------------
# HEADERS
# -------------------------

VEHICLE_LOG_HEADERS = [
    "SNo", "Date", "Trip Sheet No.", "Vehicle No.", "Starting Time", "Closing Time",
    "Start Km.", "Closing Km.", "Used Km.", "Starting Place", "Closing Place",
    "Cnote No", "Customer", "Shipper", "Trip Category", "Driver Name"
]

TRIP_CANCELLATION_HEADERS = [
    "SNo", "Date", "Branch", "Customer Name", "C-Note", "Trip Code", "Trip Category", "Department",
    "Start DateTime", "End DateTime", "From", "To", "Veh No", "Veh Type",
    "Veh Source", "Cancellation Charges", "Reason"
]

REF_NO_PENDING_HEADERS = [
    "SNo", "Date", "Branch", "Customer Name", "C-Note", "Trip Code", "Department",
    "Start DateTime", "End DateTime", "From", "To", "Veh No", "Truck Type",
    "Veh Source", "Trip Charges", "Toll charges", "AAI charges", "Loading charges",
    "Unloading Charges", "Weighment charges", "Halting Charges", "Handling Charges",
    "Selling (total)"
]

VEHICLE_UTILIZATION_HEADERS = [
    "SNo", "Vehicle Number", "Vehicle Type", "Utilized Days"
]

DRIVERS_ADVANCE_HEADERS = [
    "SNo", "Branch", "Date", "Type", "Emp Id", "DriverName", "AdvanceDate", "Advance amount", "Balance amount", "No of Days Due"
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
    "Trip Charges", "Toll charges", "AAI charges", "Loading charges",
    "Unloading Charges", "Weighment charges", "Halting Charges", "Handling Charges",
    "Total Selling", "Vendor Name", "KM Run", "Agreed KM", "Total Buying", "Profit", "Profit %"
]

VENDOR_PL_MKT_HEADERS = [
    "S No", "Date", "Cnote", "From", "To", "Customer", "Veh No", "Veh Type",
    "Trip Charges", "Toll charges", "AAI charges", "Loading charges",
    "Unloading Charges", "Weighment charges", "Halting Charges", "Handling Charges",
    "Selling", "BVM Inv no.", "Vendor Name", "Bill No", "Trip Cost",
    "Toll Expenses", "AAI Expenses", "Loading Expenses", "Unloading Expenses",
    "Weighment Expenses", "Halting Expenses", "Handling Expenses",
    "Buying", "Profit", "Profit % with Selling", "Profit % with Buying"
]

OWN_VEHICLE_PL_HEADERS = [
    "S No", "Date", "Vehicle No", 
    "Toll charges", "AAI charges", "Loading charges", "Unloading Charges", 
    "Weighment charges", "Halting Charges", "Handling Charges", "Selling", 
    "Toll Expenses", "Depreciation", "Permit", "FC", "Road tax"
]

WHATSAPP_DELIVERY_HEADERS = [
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
    "SNo", "Branch", "CustomerName", "Department", "CNotes", "Reason", "Vertical",
    "TripCode", "TripDate", "TruckNo", "VehicleType", "From", "To", "Driver",
    "Liability", "ClaimAmount", "Claim Status"
]


VENDOR_PL_ATTACHED_HEADERS = [
    "S No", "Date", "Cnote", "From", "To", "Customer", "Veh No", "Veh Type",
    "Trip Charges", "Toll charges", "AAI charges", "Loading charges", "Unloading Charges",
    "Weighment charges", "Halting Charges", "Handling Charges", "Selling",
    "Vendor Name", "Bill No", "Total Buy / Total KM",
    "Buying (Totalbuying/Total KM) * Trip KM",
    "Profit", "Profit %", "Agreed KM", "KM Run", "Extra Km amt",
    "Trip Index", "Leave Days", "Idle Days"
]

DAILY_TRIP_COUNT_HEADERS = [
    "S.No", "Branch", "Date", "Vehicle No", "Vehicle Type",
    "Active Trips For the Day", "Empty Trips For the Day",
    "OWN/Market/Attached", "KM Business", "KM Empty"
]

MAINTENANCE_REPORT_HEADERS = [
    "SNo", "Branch", "VehicleNo", "VehicleType", "Make", "PO Date",
    "ServiceType", "Job Card No", "Previous Job Card Date", "Previous Job Card No",
    "Expected Date Of delivery", "Expected Amount", "Vendor Name", "Assigned Date",
    "Bill Amount Date", "Estimated Amount", "Total KM", "Delivery Date",
    "Bill Amount", "Bill Date"
]

INSURANCE_RENEWAL_HEADERS = [
    "S No", "Vendor Name", "Company Name", "Vehicle No", "Vehicle Type",
    "Insurance", "Renewal Date", "IDV Value", "Elapsed (Days)", "DS Status"
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
    "SNo", "Date", "Enquiry No", "From", "To", "Vehicle Requested", "Vehicle Placed", "Vehicle Type", "Customer Name", "Reason"
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

    if request.method == "POST":
        form = DmrForm(request.POST)
        vehicle_number = request.POST.get('vehicle_number')
        selected_month = request.POST.get('month')
        selected_year = request.POST.get('year')
        from_loc_id = request.POST.get('from_location')
        to_loc_id = request.POST.get('to_location')
    else:
        form = DmrForm()
        vehicle_number = ""
        selected_month = '0'
        selected_year = '0'
        from_loc_id = ""
        to_loc_id = ""

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
    if selected_month and selected_month != '0':
        trips = trips.filter(tr_loading_time__month=selected_month)
    if selected_year and selected_year != '0':
        trips = trips.filter(tr_loading_time__year=selected_year)
    if from_loc_id:
        trips = trips.filter(tr_departedlocation_id=from_loc_id)
    if to_loc_id:
        trips = trips.filter(tr_reportedlocation_id=to_loc_id)

    trips = trips.order_by('-tr_loading_time')

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

        data_rows.append([
            idx,
            trip.tr_loading_time.strftime("%d-%m-%Y") if trip.tr_loading_time else "",
            safe_str(trip.tr_tripnumber),
            safe_str(trip.tr_vehiclenumber),
            trip.tr_departeddate.strftime("%H:%M") if trip.tr_departeddate else "",
            trip.tr_reporteddate.strftime("%H:%M") if trip.tr_reporteddate else "",
            safe_str(trip.tr_departedkm),
            safe_str(trip.tr_reportedkm),
            max(0, (trip.tr_reportedkm or 0) - (trip.tr_departedkm or 0)),
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
        'tr_reportedlocation'
    )

    if customer_id:
        trips = trips.filter(tr_enquirynumber__en_customername_id=customer_id)

    if selected_month and selected_month != '0':
        trips = trips.filter(
            Q(tr_loading_time__month=selected_month) |
            Q(tr_loading_time__isnull=True, tr_created_at__month=selected_month)
        )

    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) |
            Q(tr_loading_time__isnull=True, tr_created_at__year=selected_year)
        )

    if from_loc_id:
        trips = trips.filter(tr_departedlocation_id=from_loc_id)

    if to_loc_id:
        trips = trips.filter(tr_reportedlocation_id=to_loc_id)

    trips = trips.order_by('-tr_created_at')

    data_rows = []

    for idx, trip in enumerate(trips, start=1):

        cons_no = safe_str(trip.tr_consignmentnumber.co_consignmentnumber) if trip.tr_consignmentnumber else ""

        cust_name = safe_str(trip.tr_enquirynumber.en_customername).strip().upper()
        branch = "Chennai" if cust_name.endswith("MAA") else (
            "Bangalore" if cust_name.endswith("BLR") else ""
        )

        display_date = (
            trip.tr_loading_time.strftime("%d-%m-%Y")
            if trip.tr_loading_time else
            (trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else "")
        )

        category_id = trip.tr_category_id
        trip_category = "Business" if category_id == 1 else ("Empty" if category_id in [2, 3] else "")

        data_rows.append([
            idx,
            display_date,
            branch,
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
            trip.tc_cancellation,
            safe_str(trip.tr_remarks),
        ])

    return render(request, "asset_mgt_app/trip_cancellation_report.html", {
        'first_name': first_name,
        'form': form,
        'headers': TRIP_CANCELLATION_HEADERS,
        'data_rows': data_rows,
        'customer_id': customer_id,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'from_location': from_loc_id,
        'to_location': to_loc_id,
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
    else:
        form = DmrForm(request.GET or None)

        vehicle_search = request.GET.get('vehicle_search', '').strip()
        selected_month = request.GET.get('month', str(date.today().month))
        selected_year = request.GET.get('year', str(date.today().year))

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
        .select_related('vm_vehicletype')
        .filter(vm_ownership_id__in=[1, 2, 3]) # OWN, MARKET, ATTACHED as per logic elsewhere
    )

    if vehicle_search:
        vehicles = vehicles.filter(vm_registrationnumber__icontains=vehicle_search)
    
    vehicles = vehicles.order_by('vm_registrationnumber')

    # -----------------------------
    # FETCH TRIPS OVERLAPPING THE MONTH
    # -----------------------------
    # Overlap criteria: trip_start <= month_end AND (trip_end >= month_start OR trip_end IS NULL)
    overlapping_trips = TripdetailInfo.objects.filter(
        tr_departeddate__date__lte=month_end
    ).filter(
        Q(tr_reporteddate__date__gte=month_start) | Q(tr_reporteddate__isnull=True)
    ).values('tr_vehiclenumber', 'tr_departeddate', 'tr_reporteddate')

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
            t_start = trip['tr_departeddate'].date() if trip['tr_departeddate'] else month_start
            t_end = trip['tr_reporteddate'].date() if trip['tr_reporteddate'] else today_dt
            
            # Effective overlap within the selected month
            eff_start = max(t_start, month_start)
            eff_end = min(t_end, month_end)
            
            if eff_start <= eff_end:
                # Add all dates in this range to the set
                curr = eff_start
                while curr <= eff_end:
                    utilized_days_set.add(curr)
                    curr += timezone.timedelta(days=1)

        utilized_days_count = len(utilized_days_set)

        data_rows.append([
            counter,
            vehicle.vm_registrationnumber,
            safe_str(vehicle.vm_vehicletype),
            utilized_days_count
        ])
        counter += 1

    all_vehicles = VehiclemasterInfo.objects.filter(
        vm_ownership_id__in=[1, 2]
    ).order_by('vm_registrationnumber')

    context = {
        'first_name': first_name,
        'form': form,
        'headers': VEH_UTILIZATION_HEADERS if 'VEH_UTILIZATION_HEADERS' in locals() else VEHICLE_UTILIZATION_HEADERS,
        'data_rows': data_rows,
        'selected_month': str(month_int),
        'selected_year': str(year_int),
        'all_vehicles': all_vehicles,
        'vehicle_search': vehicle_search,
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

    # Filter trips where customer reference is missing OR pending
    trips = (
        TripdetailInfo.objects
        .annotate(ref_clean=Trim('tr_customerref'))
        .filter(
            Q(ref_clean__isnull=True) |
            Q(ref_clean__exact='') |
            Q(ref_clean='0')
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
        trips = trips.filter(Q(tr_loading_time__month=selected_month) | Q(tr_loading_time__isnull=True, tr_created_at__month=selected_month))
    if selected_year and selected_year != '0':
        trips = trips.filter(Q(tr_loading_time__year=selected_year) | Q(tr_loading_time__isnull=True, tr_created_at__year=selected_year))
    if from_loc_id:
        trips = trips.filter(tr_departedlocation_id=from_loc_id)
    if to_loc_id:
        trips = trips.filter(tr_reportedlocation_id=to_loc_id)

    trips = trips.order_by('-tr_created_at')

    paginator = Paginator(trips, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    data_rows = []
    for idx, trip in enumerate(page_obj, start=(page_obj.start_index() if hasattr(page_obj, 'start_index') else 1)):
        cons_no = safe_str(trip.tr_consignmentnumber.co_consignmentnumber) if trip.tr_consignmentnumber else ""
        cust_name = safe_str(trip.tr_enquirynumber.en_customername).strip().upper()
        branch = "Chennai" if cust_name.endswith("MAA") else ("Bangalore" if cust_name.endswith("BLR") else "")
        display_date = trip.tr_loading_time.strftime("%d-%m-%Y") if trip.tr_loading_time else \
                       (trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else "")

        # Calculate Total Selling (sum of charges)
        total_selling = safe_num(trip.tc_tripcost) + safe_num(trip.tc_tollcost) + safe_num(trip.tc_supervisorcost) + \
                        safe_num(trip.tc_loadingcost) + safe_num(trip.tc_unloadingcost) + safe_num(trip.tc_weighmentcost) + \
                        safe_num(trip.tc_haltingcost) + safe_num(trip.tc_handlingcost)

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
            safe_num(trip.tc_tripcost),         # Trip Charges
            safe_num(trip.tc_tollcost),         # Toll charges
            safe_num(trip.tc_supervisorcost),   # AAI charges
            safe_num(trip.tc_loadingcost),      # Loading charges
            safe_num(trip.tc_unloadingcost),    # Unloading Charges
            safe_num(trip.tc_weighmentcost),    # Weighment charges
            safe_num(trip.tc_haltingcost),      # Halting Charges
            safe_num(trip.tc_handlingcost),     # Handling Charges
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

    # Fetch all driver advances (expense_type=1) and expenses (expense_type=2)
    advances = Driverexpense.objects.filter(
        de_expense_type__id__in=[1, 2]
    ).select_related(
        'driver_name', 'de_driver_id', 'trip_number', 'de_expense_type'
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
                if user_ext.emp_branch:
                    branch = str(user_ext.emp_branch)
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
            advance.de_date.strftime("%d-%m-%Y") if advance.de_date else "",  # Advance date
            safe_num(advance.de_total_cost),  # Advance amount
            safe_num(advance.de_driver_id.ds_balance if advance.de_driver_id else 0), # Balance amount
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
    trips = TripdetailInfo.objects.all().exclude(
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
        trip_total=Coalesce(F('tc_tripcost'), 0.0, output_field=FloatField()) +
                   Coalesce(F('tc_tollcost'), 0.0, output_field=FloatField()) +
                   Coalesce(F('tc_parkingcost'), 0.0, output_field=FloatField()) +
                   Coalesce(F('tc_loadingcost'), 0.0, output_field=FloatField()) +
                   Coalesce(F('tc_unloadingcost'), 0.0, output_field=FloatField()) +
                   Coalesce(F('tc_haltingcost'), 0.0, output_field=FloatField()) +
                   Coalesce(F('tc_rtocost'), 0.0, output_field=FloatField()) +
                   Coalesce(F('tc_weighmentcost'), 0.0, output_field=FloatField()) +
                   Coalesce(F('tc_handlingcost'), 0.0, output_field=FloatField()) +
                   Coalesce(F('tc_cancellation'), 0.0, output_field=FloatField())
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
            Q(tr_loading_time__isnull=True, tr_created_at__month=selected_month)
        )

    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) |
            Q(tr_loading_time__isnull=True, tr_created_at__year=selected_year)
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
            # 3. Planning Date
            trip.tr_created_at.strftime("%Y-%m-%d") if trip.tr_created_at else "",
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
            safe_num(trip.tc_tripcost),
            # 16. Toll Charges
            safe_num(trip.tc_tollcost),
            # 17. Parking Charges
            safe_num(trip.tc_parkingcost),
            # 18. Loading Charges
            safe_num(trip.tc_loadingcost),
            # 19. Unloading Charges
            safe_num(trip.tc_unloadingcost),
            # 20. Halting Charges
            safe_num(trip.tc_haltingcost),
            # 21. Docket Charges (Mapped to tc_rtocost in WOH list)
            safe_num(trip.tc_rtocost),
            # 22. Weighment Charges
            safe_num(trip.tc_weighmentcost),
            # 23. Handling Charges
            safe_num(trip.tc_handlingcost),
            # 24. Cancellation Charges
            safe_num(trip.tc_cancellation),
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

    from ..models import Vehicle_allotmentInfo, TransInvoiceInfo, Driverexpense

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
    branch = request.POST.get('branch', '').strip()
    vendor_id = request.POST.get('vendor_id', '').strip()

    # BASE TRIPS
    # ------------------------------------------------
    trips = TripdetailInfo.objects.filter(
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
    if customer_id:
        trips = trips.filter(tr_enquirynumber__en_customername_id=customer_id)

    if dept_id:
        trips = trips.filter(tr_enquirynumber__en_customerdepartment_id=dept_id)

    if selected_month and selected_month != '0':
        trips = trips.filter(
            Q(tr_loading_time__month=selected_month) |
            Q(tr_loading_time__isnull=True, tr_created_at__month=selected_month)
        )

    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) |
            Q(tr_loading_time__isnull=True, tr_created_at__year=selected_year)
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

    trips = trips.order_by('-tr_created_at')

    # ------------------------------------------------
    # PRE-FETCH RELATED DATA (NO PAGINATION)
    # ------------------------------------------------
    trip_ids = list(trips.values_list('id', flat=True))
    trip_enquiries = list(trips.values_list('tr_enquirynumber_id', flat=True))

    allotments = Vehicle_allotmentInfo.objects.filter(
        va_enquirynumber_id__in=trip_enquiries
    ).select_related('va_vendor')

    invoices = TransInvoiceInfo.objects.filter(
        ti_trip_id__in=trip_ids
    )

    expenses = Driverexpense.objects.filter(
        trip_number_id__in=trip_ids
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

    invoice_map = {i.ti_trip_id: i.ti_inv_no for i in invoices}

    expense_map = {}
    for e in expenses:
        expense_map.setdefault(e.trip_number_id, []).append(e)

    # ------------------------------------------------
    # BUILD TABLE
    # ------------------------------------------------
    data_rows = []

    for idx, trip in enumerate(trips, start=1):

        # ---------------- SELLING ----------------
        selling_trip = safe_num(trip.tc_tripcost)
        selling_toll = safe_num(trip.tc_tollcost)
        selling_aai = safe_num(trip.tc_supervisorcost)
        selling_loading = safe_num(trip.tc_loadingcost)
        selling_unloading = safe_num(trip.tc_unloadingcost)
        selling_weighment = safe_num(trip.tc_weighmentcost)
        selling_halting = safe_num(trip.tc_haltingcost) + safe_num(trip.tc_total_halting_cost)
        selling_handling = safe_num(trip.tc_handlingcost)

        total_selling = (
            selling_trip + selling_toll + selling_aai +
            selling_loading + selling_unloading +
            selling_weighment + selling_halting +
            selling_handling +
            safe_num(trip.tc_parkingcost) +
            safe_num(trip.tc_rtocost) +
            safe_num(trip.tc_betacost)
        )

        # ---------------- BUYING ----------------
        allotment = allotment_map.get(
            (trip.tr_enquirynumber_id, trip.tr_vehiclenumber)
        )

        vendor_name = ""
        buying_trip_cost = 0.0

        if allotment:
            vendor_name = safe_str(allotment.va_vendor) if allotment.va_vendor else "Market"
            
            # Fetch from Vendor Rate Master if vendor is present
            if allotment.va_vendor:
                rate_lookup = VendorratemasterInfo1.objects.filter(
                    vr1_fromlocation=trip.tr_departedlocation,
                    vr1_tolocation=trip.tr_reportedlocation,
                    vr1_vehicletype=trip.tr_vehicletype,
                    vr1_vendor=allotment.va_vendor
                ).first()
                if rate_lookup:
                    buying_trip_cost = safe_num(rate_lookup.vr1_rate)
                else:
                    buying_trip_cost = safe_num(allotment.va_standardbuy) + safe_num(allotment.va_specialbuy)
            else:
                buying_trip_cost = safe_num(allotment.va_standardbuy) + safe_num(allotment.va_specialbuy)
        else:
            vendor_name = "Market"

        trip_expenses = expense_map.get(trip.id, [])

        buying_loading = buying_unloading = buying_weighment = buying_aai = 0.0

        for e in trip_expenses:
            buying_loading += safe_num(e.de_loadingcost)
            buying_unloading += safe_num(e.de_unloadingcost)
            buying_weighment += safe_num(e.de_weighmentcost)
            buying_aai += safe_num(e.de_supervisorcost)

        total_buying = (
            buying_trip_cost +
            buying_loading +
            buying_unloading +
            buying_weighment +
            buying_aai
        )

        profit = total_selling - total_buying

        profit_pct_selling = (profit / total_selling * 100) if total_selling > 0 else 0
        profit_pct_buying = (profit / total_buying * 100) if total_buying > 0 else 0

        row = [
            idx,
            trip.tr_loading_time.strftime("%d-%m-%Y") if trip.tr_loading_time else
            (trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else ""),

            safe_str(trip.tr_consignmentnumber),
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_str(trip.tr_enquirynumber.en_customername),
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype),

            # SELLING
            selling_trip,
            selling_toll,
            selling_aai,
            selling_loading,
            selling_unloading,
            selling_weighment,
            selling_halting,
            selling_handling,
            total_selling,

            # REFERENCES
            invoice_map.get(trip.id, ""),
            vendor_name,
            "",

            # BUYING
            buying_trip_cost,
            0,
            buying_aai,
            buying_loading,
            buying_unloading,
            buying_weighment,
            0,
            0,
            total_buying,

            # PROFIT
            round(profit, 2),
            f"{round(profit_pct_selling, 2)}%",
            f"{round(profit_pct_buying, 2)}%",
        ]

        data_rows.append(row)

    return render(request, "asset_mgt_app/vendor_p_l_mkt_report.html", {
        'first_name': first_name,
        'form': form,
        'headers': VENDOR_PL_MKT_HEADERS,
        'data_rows': data_rows,
        'customer_id': customer_id,
        'dept_id': dept_id,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'from_location': from_loc_id,
        'to_location': to_loc_id,
        'branch': branch,
        'vendor_id': int(vendor_id) if vendor_id else None,
        'all_vendors': Vendor_info.objects.all().order_by('vend_name'),
    })



@login_required(login_url='login_page')
def vendor_p_l_attached_report_view(request):
    first_name = request.session.get('first_name')

    from ..models import Vehicle_allotmentInfo, TransInvoiceInfo, Driverexpense

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

    # BASE TRIPS
    # ------------------------------------------------
    trips = TripdetailInfo.objects.filter(
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
    if customer_id:
        trips = trips.filter(tr_enquirynumber__en_customername_id=customer_id)

    if dept_id:
        trips = trips.filter(tr_enquirynumber__en_customerdepartment_id=dept_id)

    if selected_month and selected_month != '0':
        trips = trips.filter(
            Q(tr_loading_time__month=selected_month) |
            Q(tr_loading_time__isnull=True, tr_created_at__month=selected_month)
        )

    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) |
            Q(tr_loading_time__isnull=True, tr_created_at__year=selected_year)
        )

    if from_loc_id:
        trips = trips.filter(tr_departedlocation_id=from_loc_id)

    if to_loc_id:
        trips = trips.filter(tr_reportedlocation_id=to_loc_id)

    trips = trips.order_by('-tr_created_at')

    # ------------------------------------------------
    # PRE-FETCH RELATED DATA (FULL DATA)
    # ------------------------------------------------
    trip_ids = list(trips.values_list('id', flat=True))
    trip_enquiries = list(trips.values_list('tr_enquirynumber_id', flat=True))

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
    expenses = Driverexpense.objects.filter(trip_number_id__in=trip_ids)
    for exp in expenses:
        driver_expense_map.setdefault(exp.trip_number_id, []).append(exp)

    # ------------------------------------------------
    # BUILD REPORT
    # ------------------------------------------------
    data_rows = []

    for idx, trip in enumerate(trips, start=1):

        # ---------------- SELLING ----------------
        selling_trip = safe_num(trip.tc_tripcost)
        selling_toll = safe_num(trip.tc_tollcost)
        selling_aai = safe_num(trip.tc_supervisorcost)
        selling_loading = safe_num(trip.tc_loadingcost)
        selling_unloading = safe_num(trip.tc_unloadingcost)
        selling_weighment = safe_num(trip.tc_weighmentcost)
        selling_halting = safe_num(trip.tc_haltingcost) + safe_num(trip.tc_total_halting_cost)
        selling_handling = safe_num(trip.tc_handlingcost)

        selling_parking = safe_num(trip.tc_parkingcost)
        selling_rto = safe_num(trip.tc_rtocost)
        selling_beta = safe_num(trip.tc_betacost)

        total_selling = (
            selling_trip + selling_toll + selling_aai +
            selling_loading + selling_unloading +
            selling_weighment + selling_halting +
            selling_handling +
            selling_parking + selling_rto + selling_beta
        )

        # ---------------- BUYING ----------------
        va_info = va_map.get(trip.tr_enquirynumber_id)

        vendor_name = "Attached"
        if va_info:
            if va_info.va_vendor:
                vendor_name = str(va_info.va_vendor)
            elif va_info.va_vehiclenumber_mkt:
                vendor_name = "Market Vehicle"

        buying_trip_cost = (
            safe_num(getattr(va_info, 'va_standardbuy', 0)) +
            safe_num(getattr(va_info, 'va_specialbuy', 0))
            if va_info else 0
        )

        trip_expenses = driver_expense_map.get(trip.id, [])

        buy_loading = sum(safe_num(e.de_loadingcost) for e in trip_expenses)
        buy_unloading = sum(safe_num(e.de_unloadingcost) for e in trip_expenses)
        buy_weighment = sum(safe_num(e.de_weighmentcost) for e in trip_expenses)
        buy_aai = sum(safe_num(e.de_supervisorcost) for e in trip_expenses)

        total_buying = buying_trip_cost + buy_loading + buy_unloading + buy_weighment + buy_aai

        # ---------------- KM & PROFIT ----------------
        reported_km = safe_num(trip.tr_reportedkm)
        departed_km = safe_num(trip.tr_departedkm)
        km_run = reported_km - departed_km if reported_km and departed_km else 0

        buy_rate_per_km = (total_buying / km_run) if km_run > 0 else 0

        profit = total_selling - total_buying
        profit_pct = (profit / total_buying * 100) if total_buying > 0 else 0

        row = [
            idx,
            trip.tr_loading_time.strftime("%d-%m-%Y") if trip.tr_loading_time else
            (trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else ""),

            safe_str(trip.tr_consignmentnumber),
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_str(trip.tr_enquirynumber.en_customername),
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype),

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
            "",

            round(buy_rate_per_km, 2),
            round(total_buying, 2),

            round(profit, 2),
            f"{round(profit_pct, 2)}%",

            0,
            km_run,
            0,
            0,
            0,
            0
        ]

        data_rows.append(row)

    return render(request, "asset_mgt_app/vendor_p_l_attached_report.html", {
        'first_name': first_name,
        'form': form,
        'headers': VENDOR_PL_ATTACHED_HEADERS,
        'data_rows': data_rows,
        'customer_id': customer_id,
        'dept_id': dept_id,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'from_location': from_loc_id,
        'to_location': to_loc_id,
    })



@login_required(login_url='login_page')
def whatsapp_delivery_status_report_view(request):
    first_name = request.session.get('first_name')

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

    # ------------------------------------------------
    # BASE QUERY
    # ------------------------------------------------
    trips = TripdetailInfo.objects.select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_enquirynumber__en_customerdepartment',
        'tr_consignmentnumber',
        'tr_vehicletype',
        'tr_departedlocation',
        'tr_reportedlocation'
    )

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
            Q(tr_loading_time__isnull=True, tr_created_at__month=selected_month)
        )

    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) |
            Q(tr_loading_time__isnull=True, tr_created_at__year=selected_year)
        )

    if from_loc_id:
        trips = trips.filter(tr_departedlocation_id=from_loc_id)

    if to_loc_id:
        trips = trips.filter(tr_reportedlocation_id=to_loc_id)

    trips = trips.order_by('-tr_created_at')

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

        consignment_date = (
            trip.tr_consignmentnumber.co_consignmentdate.strftime("%d-%m-%Y")
            if trip.tr_consignmentnumber and trip.tr_consignmentnumber.co_consignmentdate
            else ""
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
            "",                 # WhatsApp Time (future)
            "Pending"           # Delivery Status (future)
        ]

        data_rows.append(row)

    return render(request, "asset_mgt_app/whatsapp_delivery_status_report.html", {
        'first_name': first_name,
        'form': form,
        'headers': WHATSAPP_DELIVERY_HEADERS,
        'data_rows': data_rows,
        'customer_id': customer_id,
        'dept_id': dept_id,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'from_loc_id': from_loc_id,
        'to_loc_id': to_loc_id,
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
    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')
    from_loc_id = request.POST.get('from_location')
    to_loc_id = request.POST.get('to_location')
    vehicle_filter = request.POST.get('vehicle_number')

    # ------------------------------------------------
    # BASE QUERY
    # ------------------------------------------------
    trips = TripdetailInfo.objects.select_related(
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

    if selected_month and selected_month != '0':
        trips = trips.filter(
            Q(tr_loading_time__month=selected_month) |
            Q(tr_loading_time__isnull=True, tr_created_at__month=selected_month)
        )

    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) |
            Q(tr_loading_time__isnull=True, tr_created_at__year=selected_year)
        )

    if from_loc_id:
        trips = trips.filter(tr_departedlocation_id=from_loc_id)

    if to_loc_id:
        trips = trips.filter(tr_reportedlocation_id=to_loc_id)

    if vehicle_filter:
        trips = trips.filter(tr_vehiclenumber__icontains=vehicle_filter)

    trips = trips.order_by('-tr_created_at')

    # ------------------------------------------------
    # AGGREGATION
    # ------------------------------------------------
    aggregated_data = {}

    for trip in trips:

        # Determine trip date
        trip_date = (
            trip.tr_loading_time.date() if trip.tr_loading_time
            else trip.tr_departeddate.date() if trip.tr_departeddate
            else None
        )

        if not trip_date:
            continue

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
            item['empty_trips'],
            item['ownership'],
            round(item['km_business'], 2),
            round(item['km_empty'], 2)
        ]

        data_rows.append(row)

    all_vehicles = VehiclemasterInfo.objects.filter(
        vm_ownership_id__in=[1, 2 , 3]
    ).order_by('vm_registrationnumber')

    return render(request, "asset_mgt_app/daily_trip_count_report.html", {
        'first_name': first_name,
        'form': form,
        'headers': DAILY_TRIP_COUNT_HEADERS,
        'data_rows': data_rows,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'vehicle_filter': vehicle_filter,
        'all_vehicles': all_vehicles
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
            Q(tr_loading_time__isnull=True, tr_created_at__month=selected_month)
        )

    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) |
            Q(tr_loading_time__isnull=True, tr_created_at__year=selected_year)
        )

    if vehicle_number:
        trips = trips.filter(tr_vehiclenumber=vehicle_number)

    trips = trips.order_by('-tr_created_at')

    # -------------------------------
    # PREFETCH EXPENSES (TOLL)
    # -------------------------------
    expenses = (
        Driverexpense.objects
        .filter(trip_number_id__in=trips.values_list('id', flat=True))
        .select_related('de_expense_type')
    )

    expense_map = {}
    for e in expenses:
        expense_map.setdefault(e.trip_number_id, []).append(e)

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

    for idx, trip in enumerate(trips, start=1):

        date_val = (
            trip.tr_loading_time.strftime("%d-%m-%Y")
            if trip.tr_loading_time else
            (trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else "")
        )

        # -------- SELLING --------
        selling_total = (
            safe_num(trip.tc_tripcost) +
            safe_num(trip.tc_tollcost) +
            safe_num(trip.tc_supervisorcost) +
            safe_num(trip.tc_loadingcost) +
            safe_num(trip.tc_unloadingcost) +
            safe_num(trip.tc_weighmentcost) +
            safe_num(trip.tc_haltingcost) +
            safe_num(trip.tc_total_halting_cost) +
            safe_num(trip.tc_handlingcost) +
            safe_num(trip.tc_parkingcost) +
            safe_num(trip.tc_rtocost) +
            safe_num(trip.tc_betacost)
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
            safe_num(trip.tc_tollcost),
            safe_num(trip.tc_supervisorcost),
            safe_num(trip.tc_loadingcost),
            safe_num(trip.tc_unloadingcost),
            safe_num(trip.tc_weighmentcost),
            safe_num(trip.tc_haltingcost) + safe_num(trip.tc_total_halting_cost),
            safe_num(trip.tc_handlingcost),
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
    from ..models import CustomerClaimsInfo
    
    # Initialize Filter Form
    if request.method == "POST":
        form = DmrForm(request.POST)
    else:
        form = DmrForm()

    # Get Filter Parameters
    customer_id = request.POST.get('dmr_customer')
    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')

    # Base Query: Fetch All Claims
    # We need to join with Customer, Branch, Unit, and Trip
    claims = CustomerClaimsInfo.objects.all().select_related(
        'cc_branch',
        'cc_unit',
        'cc_customer',
        'cc_status',
    )

    if customer_id:
        claims = claims.filter(cc_customer_id=customer_id)
    if selected_month and selected_month != '0':
         # Using cc_CAPA_issueddate or cc_updated_on for date filtering?
         # Assuming updated_on is more relevant for general tracking if date field ambiguous
         claims = claims.filter(cc_updated_on__month=selected_month)
    if selected_year and selected_year != '0':
         claims = claims.filter(cc_updated_on__year=selected_year)
    
    claims = claims.order_by('-cc_updated_on')

    # Pagination
    paginator = Paginator(claims, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Fetch related Trips for the current page
    # cc_job_ref is the link. It could contain Trip Number OR CNote Number.
    job_refs = [c.cc_job_ref for c in page_obj if c.cc_job_ref]
    
    # Try to find trips matching tr_tripnumber
    trips_by_no = TripdetailInfo.objects.filter(tr_tripnumber__in=job_refs).select_related(
        'tr_vehicletype', 'tr_departedlocation', 'tr_reportedlocation'
    )
    trip_map = {t.tr_tripnumber: t for t in trips_by_no}

    # Try to find trips matching tr_consignmentnumber__co_consignmentnumber for unmapped ones
    # This requires a second query or careful OR logic.
    # Simpler to do a second lookup for remaining refs
    remaining_refs = [r for r in job_refs if r not in trip_map]
    if remaining_refs:
        trips_by_cnote = TripdetailInfo.objects.filter(
            tr_consignmentnumber__co_consignmentnumber__in=remaining_refs
        ).select_related(
            'tr_vehicletype', 'tr_departedlocation', 'tr_reportedlocation', 'tr_consignmentnumber'
        )
        for t in trips_by_cnote:
            # Map by CNote so we can lookup later
            if t.tr_consignmentnumber:
                trip_map[t.tr_consignmentnumber.co_consignmentnumber] = t

    data_rows = []
    
    for idx, claim in enumerate(page_obj, start=(page_obj.start_index() if hasattr(page_obj, 'start_index') else 1)):
        
        # Look up trip details
        trip = trip_map.get(claim.cc_job_ref)
        
        trip_code = claim.cc_job_ref
        trip_date = ""
        truck_no = ""
        veh_type = ""
        loc_from = ""
        loc_to = ""
        driver = ""
        department = "" # From trip or customer?
        cnote = claim.cc_job_ref # Default to ref

        if trip:
            trip_code = safe_str(trip.tr_tripnumber)
            trip_date = trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else ""
            truck_no = safe_str(trip.tr_vehiclenumber)
            veh_type = safe_str(trip.tr_vehicletype)
            loc_from = safe_str(trip.tr_departedlocation)
            loc_to = safe_str(trip.tr_reportedlocation)
            driver = safe_str(trip.tr_drivername)
            if trip.tr_consignmentnumber:
                cnote = safe_str(trip.tr_consignmentnumber.co_consignmentnumber)
            
            # Try to get dept from trip enquiry if available, else standard customer dept
            if trip.tr_enquirynumber and trip.tr_enquirynumber.en_customerdepartment:
                 department = safe_str(trip.tr_enquirynumber.en_customerdepartment)

            cust_name = safe_str(trip.tr_enquirynumber.en_customername).strip().upper()
            branch = "Chennai" if cust_name.endswith("MAA") else ("Bangalore" if cust_name.endswith("BLR") else "")
        else:
            cust_name = safe_str(claim.cc_customer).strip().upper()
            branch = "Chennai" if cust_name.endswith("MAA") else ("Bangalore" if cust_name.endswith("BLR") else "")

        row = [
            idx,
            branch,
            safe_str(claim.cc_customer),
            department,
            cnote,
            safe_str(claim.cc_claim_reason),
            safe_str(claim.cc_unit), # Vertical? Assuming UnitInfo maps to vertical/business unit
            trip_code,
            trip_date,
            truck_no,
            veh_type,
            loc_from,
            loc_to,
            driver,
            "N/A", # Liability - Field missing in model
            safe_num(claim.cc_amount),
            safe_str(claim.cc_status)
        ]
        data_rows.append(row)

    context = {
        'first_name': first_name,
        'form': form,
        'headers': CLAIM_PENDING_HEADERS,
        'data_rows': data_rows,
        'page_obj': page_obj,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'customer_id': customer_id,
    }
    
    return render(request, "asset_mgt_app/claim_pending_report.html", context)




@login_required(login_url='login_page')
def halting_report_view(request):
    first_name = request.session.get('first_name')
    from ..models import TripdetailInfo, Driverexpense, ConsignmentgoodsInfo
    
    if request.method == "POST":
        form = DmrForm(request.POST)
    else:
        form = DmrForm()
    
    customer_id = request.POST.get('dmr_customer')
    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')
    
    # Base Query
    trips = TripdetailInfo.objects.all().select_related(
        'tr_enquirynumber', 'tr_enquirynumber__en_customername', 'tr_enquirynumber__en_customerdepartment',
        'tr_vehicletype', 'tr_departedlocation', 'tr_reportedlocation',
        'tr_consignmentnumber'
    )
    
    if customer_id:
        trips = trips.filter(tr_enquirynumber__en_customername_id=customer_id)
    if selected_month and selected_month != '0':
        trips = trips.filter(
            Q(tr_loading_time__month=selected_month) | Q(tr_loading_time__isnull=True, tr_created_at__month=selected_month))
    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) | Q(tr_loading_time__isnull=True, tr_created_at__year=selected_year))
            
    trips = trips.order_by('-tr_created_at')
    
    paginator = Paginator(trips, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    trip_ids = [t.id for t in page_obj]
    # Filter valid consignment IDs (not None)
    consignment_ids = [t.tr_consignmentnumber.id for t in page_obj if t.tr_consignmentnumber]

    # Fetch Expenses for "Buying Halting"
    expenses = Driverexpense.objects.filter(trip_number_id__in=trip_ids).select_related('de_expense_type')
    expense_map = {}
    
    for e in expenses:
        if e.trip_number_id not in expense_map:
            expense_map[e.trip_number_id] = 0.0
        
        # Check if expense is related to Halting
        if e.de_expense_type and 'halting' in str(e.de_expense_type).lower():
            expense_map[e.trip_number_id] += safe_num(e.de_total_cost)
            
    # Fetch Consignment Goods for Consignor/Consignee
    goods = ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber_id__in=consignment_ids).select_related(
        'cg_consigner', 'cg_consignee'
    )
    
    goods_map = {}
    for g in goods:
        # Use simple mapping: ConsignmentID -> (ConsignorName, ConsigneeName)
        # If multiple goods exist, this takes the last one processed. Usually sufficient for reports.
        consigner = g.cg_consigner.consigner_name if g.cg_consigner else ""
        consignee = g.cg_consignee.consignee_name if g.cg_consignee else ""
        goods_map[g.cg_consignmentnumber_id] = (consigner, consignee)

    data_rows = []
    
    for idx, trip in enumerate(page_obj, start=(page_obj.start_index() if hasattr(page_obj, 'start_index') else 1)):
        
        # --- Basic Details ---
        branch = safe_str(trip.tr_enquirynumber.en_branch if hasattr(trip.tr_enquirynumber, 'en_branch') else '') 
        
        date_val = trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else ""
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
                consignor, consignee = goods_map[trip.tr_consignmentnumber.id]

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
        selling_halting = safe_num(trip.tc_haltingcost) + safe_num(trip.tc_total_halting_cost)
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
    }
    
    return render(request, "asset_mgt_app/halting_report.html", context)




@login_required(login_url='login_page')
def maintenance_report_view(request):
    first_name = request.session.get('first_name')
    from ..models import MaintenanceInfo, VehiclemasterInfo
    from datetime import datetime

    if request.method == "POST":
        form = DmrForm(request.POST)
        vehicle_search = request.POST.get('vehicle_search', '')
        selected_month = request.POST.get('month', '')
        selected_year = request.POST.get('year', '')
    else:
        form = DmrForm()
        vehicle_search = ""
        selected_month = ""
        selected_year = ""

    # Base Query
    maintenance_records = MaintenanceInfo.objects.all().select_related(
        'vehicle', 'vehicle__vm_vehicletype', 'vehicle__vm_vehiclemanufacturer'
    ).order_by('vehicle__vm_registrationnumber', '-created_at')

    # Filters
    if vehicle_search:
        maintenance_records = maintenance_records.filter(vehicle__vm_registrationnumber__icontains=vehicle_search)
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
        v_id = rec.vehicle_id
        if v_id not in vehicle_groups:
            vehicle_groups[v_id] = []
        vehicle_groups[v_id].append(rec)

    # Now build rows
    counter = 1

    # We want to show the filtered range.
    for rec in records_list:
        # Find previous in the group
        group = vehicle_groups.get(rec.vehicle_id, [])
        # group is ordered desc by created_at. rec is in group.
        # Find index of rec
        try:
            curr_idx = group.index(rec)
            prev_rec = group[curr_idx + 1] if curr_idx + 1 < len(group) else None
        except ValueError:
            prev_rec = None
        
        # Safely access vehicle fields
        try:
            vehicle_no = safe_str(rec.vehicle.vm_registrationnumber) if rec.vehicle else ""
            vehicle_type = safe_str(rec.vehicle.vm_vehicletype) if rec.vehicle and rec.vehicle.vm_vehicletype else ""
        except:
            vehicle_no = ""
            vehicle_type = ""
            
        make = safe_str(rec.make_model)
        
        # Branch - Logic similar to other reports if possible, but MaintenanceInfo doesn't have location directly usually.
        # We can try to infer from user or just leave blank/dash for now as it wasn't in model
        branch = "" 
        
        job_card_no = rec.id # fallback
        prev_job_card_date = prev_rec.created_at.strftime("%d-%m-%Y") if prev_rec and prev_rec.created_at else ""
        prev_job_card_no = prev_rec.id if prev_rec else ""
        
        row = [
            counter,
            branch,
            vehicle_no,
            vehicle_type,
            make,
            "", # PO Date (Not available)
            safe_str(rec.service_type),
            job_card_no,
            prev_job_card_date,
            prev_job_card_no,
            rec.est_delivery.strftime("%d-%m-%Y %H:%M") if rec.est_delivery else "",
            "", # Expected Amount (Is this estimated_amount?)
            safe_str(rec.technician), # Using Technician as Vendor Name? Or driver? Requirement says "Vendor Name". Maintenance info has technician.
            rec.job_card_created_on.strftime("%d-%m-%Y") if rec.job_card_created_on else "", # Assigned Date -> job_card_created_on
            "", # Bill Amount Date
            safe_num(rec.estimated_amount),
            rec.total_km_run,
            rec.est_delivery.strftime("%d-%m-%Y") if rec.est_delivery else "", # Delivery Date -> Est Delivery?
            "", # Bill Amount
            ""  # Bill Date
        ]
        processed_rows.append(row)
        counter += 1

    paginator = Paginator(processed_rows, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    all_vehicles = VehiclemasterInfo.objects.filter(vm_ownership_id__in=[1, 2 ,3]).order_by('vm_registrationnumber')

    context = {
        'first_name': first_name,
        'form': form,
        'headers': MAINTENANCE_REPORT_HEADERS,
        'data_rows': page_obj.object_list, # Paginator pages list of rows
        'page_obj': page_obj,
        'vehicle_search': vehicle_search,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'all_vehicles': all_vehicles,
    }
    return render(request, "asset_mgt_app/maintenance_report.html", context)

from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.db.models.functions import Upper, Trim

from ..models import Insurance_Info, VehiclemasterInfo


@login_required(login_url='login_page')
def insurance_renewal_report_view(request):
    first_name = request.session.get('first_name')

    # -------------------------
    # READ FILTER (POST only – matches HTML)
    # -------------------------
    vehicle_search = request.POST.get('vehicle_search', '').strip()

    # -------------------------
    # BASE QUERY (normalize vehicle no)
    # -------------------------
    insurance_records = (
        Insurance_Info.objects
        .annotate(
            veh_no_clean=Upper(Trim('ins_vehicle_no'))
        )
        .order_by('ins_expiry_date')
    )

    # -------------------------
    # VEHICLE FILTER
    # -------------------------
    if vehicle_search:
        insurance_records = insurance_records.filter(
            veh_no_clean=vehicle_search.strip().upper()
        )

    # -------------------------
    # VEHICLE MASTER (for dropdown + type lookup)
    # -------------------------
    vehicles = (
        VehiclemasterInfo.objects
        .annotate(
            veh_no_clean=Upper(Trim('vm_registrationnumber'))
        )
        .select_related('vm_vehicletype')
        .order_by('vm_registrationnumber')
    )

    vehicle_map = {
        v.veh_no_clean: v
        for v in vehicles
    }

    # -------------------------
    # PROCESS ROWS
    # -------------------------
    today = datetime.now().date()
    processed_rows = []
    counter = 1

    for rec in insurance_records:
        vehicle = vehicle_map.get(rec.veh_no_clean)
        vehicle_type = safe_str(vehicle.vm_vehicletype) if vehicle else ""

        expiry_date = rec.ins_expiry_date
        elapsed_days = (expiry_date - today).days if expiry_date else 0

        if expiry_date:
            if elapsed_days < 0:
                ds_status = "Expired"
            elif elapsed_days <= 30:
                ds_status = "Renewal Due"
            else:
                ds_status = "Active"
        else:
            ds_status = ""

        processed_rows.append([
            counter,                                # 1 S.No
            safe_str(rec.ins_vendor),               # 2 Vendor
            safe_str(rec.ins_name),                 # 3 Policy Name
            safe_str(rec.ins_vehicle_no),           # 4 Vehicle No
            vehicle_type,                           # 5 Vehicle Type
            safe_str(rec.ins_type),                 # 6 Insurance Type
            expiry_date.strftime("%d-%m-%Y") if expiry_date else "",  # 7 Expiry Date
            safe_num(rec.ins_sum_assured),           # 8 Sum Assured
            elapsed_days,                           # 9 Elapsed Days
            ds_status                               # 10 Status (badge column)
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
        'all_vehicles': vehicles,   # dropdown
    }

    return render(
        request,
        "asset_mgt_app/insurance_renewal_report.html",
        context
    )



@login_required(login_url='login_page')
def diesel_vs_revenue_report_view(request):
    first_name = request.session.get('first_name')
    from ..models import TripdetailInfo, Fuelfillinginfo, VehiclemasterInfo, ConsignmentdetailInfo
    from datetime import datetime
    from django.db.models import Sum

    if request.method == "POST":
        form = DmrForm(request.POST)
        vehicle_search = request.POST.get('vehicle_search', '')
        selected_month = request.POST.get('month', '0')
        selected_year = request.POST.get('year', '0')
    else:
        form = DmrForm()
        vehicle_search = ""
        selected_month = '0'
        selected_year = '0'

    # Base Query for Trips
    trips = TripdetailInfo.objects.all().select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_consignmentnumber',
        'tr_vehicletype'
    )

    if vehicle_search:
        trips = trips.filter(tr_vehiclenumber__icontains=vehicle_search)
    if selected_month and selected_month != '0':
        trips = trips.filter(tr_loading_time__month=selected_month)
    if selected_year and selected_year != '0':
        trips = trips.filter(tr_loading_time__year=selected_year)

    trips = trips.order_by('-tr_loading_time')

    # Get Vehicle Master Data for Mileage Fixed
    vehicles = VehiclemasterInfo.objects.all()
    vehicle_map = {v.vm_registrationnumber: v for v in vehicles}

    processed_rows = []
    counter = 1

    for trip in trips:
        cust_name = safe_str(trip.tr_enquirynumber.en_customername).strip().upper()
        branch = "Chennai" if cust_name.endswith("MAA") else ("Bangalore" if cust_name.endswith("BLR") else "")
        
        trip_date = trip.tr_loading_time.date() if trip.tr_loading_time else (trip.tr_departeddate.date() if trip.tr_departeddate else None)
        
        # Revenue calculation (Sum of selling components)
        revenue = safe_num(trip.tc_tripcost) + safe_num(trip.tc_rtocost) + safe_num(trip.tc_betacost) + \
                  safe_num(trip.tc_parkingcost) + safe_num(trip.tc_tollcost) + safe_num(trip.tc_loadingcost) + \
                  safe_num(trip.tc_unloadingcost) + safe_num(trip.tc_weighmentcost) + safe_num(trip.tc_handlingcost) + \
                  safe_num(trip.tc_haltingcost) + safe_num(trip.tc_total_halting_cost) + safe_num(trip.tc_supervisorcost)

        # KM Run
        km_run = max(0, safe_num(trip.tr_reportedkm) - safe_num(trip.tr_departedkm))

        # Fuel Expenses for this vehicle on this date
        fuel_data = Fuelfillinginfo.objects.filter(
            ff_vehicle_num__vm_registrationnumber=trip.tr_vehiclenumber,
            ff_date=trip_date
        ).aggregate(total_cost=Sum('ff_fuel_price'), total_ltr=Sum('ff_filled_ltr'))

        diesel_expenses = safe_num(fuel_data['total_cost'])
        filled_ltr = safe_num(fuel_data['total_ltr'])

        # Calculations
        diesel_vs_revenue_pct = (diesel_expenses / revenue * 100) if revenue > 0 else 0
        actual_mileage = (km_run / filled_ltr) if filled_ltr > 0 else 0

        # Vehicle master details
        vm = vehicle_map.get(trip.tr_vehiclenumber)
        mileage_fixed = safe_str(vm.vm_millage) if vm else ""
        leased_to = safe_str(trip.tr_enquirynumber.en_customername) if trip.tr_enquirynumber else ""

        row = [
            counter,
            branch,
            trip_date.strftime("%d-%m-%Y") if trip_date else "",
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype),
            mileage_fixed,
            leased_to,
            km_run,
            diesel_expenses,
            revenue,
            f"{diesel_vs_revenue_pct:.2f}%",
            f"{actual_mileage:.2f}"
        ]
        processed_rows.append(row)
        counter += 1

    paginator = Paginator(processed_rows, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    all_vehicles = VehiclemasterInfo.objects.filter(vm_ownership_id__in=[1, 2 ,3]).order_by('vm_registrationnumber')

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
        trips = trips.filter(tr_loading_time__month=selected_month)
    if selected_year and selected_year != '0':
        trips = trips.filter(tr_loading_time__year=selected_year)

    # Prefetch Vehicle Allotment for Market Buy Rate
    enquiry_ids = [t.tr_enquirynumber_id for t in trips]
    va_data = Vehicle_allotmentInfo.objects.filter(va_enquirynumber_id__in=enquiry_ids)
    va_map = {v.va_enquirynumber_id: v for v in va_data}

    aggregated_data = {}

    for trip in trips:
        # Determine Date
        trip_date = trip.tr_loading_time.date() if trip.tr_loading_time else (trip.tr_departeddate.date() if trip.tr_departeddate else None)
        if not trip_date:
            continue
        
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
        
        # Revenue Calculation
        revenue = safe_num(trip.tc_tripcost) + safe_num(trip.tc_rtocost) + safe_num(trip.tc_betacost) + \
                  safe_num(trip.tc_parkingcost) + safe_num(trip.tc_tollcost) + safe_num(trip.tc_loadingcost) + \
                  safe_num(trip.tc_unloadingcost) + safe_num(trip.tc_weighmentcost) + safe_num(trip.tc_handlingcost) + \
                  safe_num(trip.tc_haltingcost) + safe_num(trip.tc_total_halting_cost) + safe_num(trip.tc_supervisorcost)
        
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
                data['mkt_buy_rate'] += safe_num(va.va_standardbuy) + safe_num(va.va_specialbuy)

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
    vehicle_requests = Enquirynotevehicle.objects.filter(env_enquirynumber_id__in=enquiry_ids).select_related('env_vehicletype')
    req_map = {}
    for vr in vehicle_requests:
        req_map.setdefault(vr.env_enquirynumber_id, []).append(f"{vr.env_quantity} x {vr.env_vehicletype}")
    
    # Vehicle Allotments mapping
    allotments = Vehicle_allotmentInfo.objects.filter(va_enquirynumber_id__in=enquiry_ids).select_related('va_vehiclenumber')
    allot_map = {}
    for va in allotments:
        reg_no = va.va_vehiclenumber.vm_registrationnumber if va.va_vehiclenumber else va.va_vehiclenumber_mkt
        if reg_no:
            allot_map.setdefault(va.va_enquirynumber_id, []).append(str(reg_no))

    data_rows = []
    for idx, enq in enumerate(enquiries, start=1):
        # Vehicle Requested
        req_list = req_map.get(enq.id, [])
        veh_req_str = ", ".join(req_list)
        
        # Vehicle Type
        # Extract unique types from req_list
        veh_types = ", ".join(list(set([r.split(" x ")[-1] for r in req_list])))

        # Vehicle Placed
        places_list = allot_map.get(enq.id, [])
        places_str = ", ".join(places_list) if places_list else "0"

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
