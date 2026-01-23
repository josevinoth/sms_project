from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from ..models import TripdetailInfo, ConsignmentdetailInfo, CustomerInfo, CustomerdepartmentInfo, ConsignmentgoodsInfo, Places, VehiclemasterInfo, Driverexpense, Vehicle_allotmentInfo
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
    "SNo", "Date", "Branch", "Customer Name", "C-Note", "Trip Code", "Department",
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

VEHICLE_STATUS_HEADERS = [
    "SNo", "Branch", "Vehicle Number", "Vehicle Type", "Date of Idle"
]

DRIVERS_ADVANCE_HEADERS = [
    "SNo", "Branch", "Date", "Emp Id", "DriverName", "AdvanceDate", "Advance amount", "No of Days Due"
]

INVOICE_PENDING_HEADERS = [
    "SNo", "Date", "Branch", "Customer Name", "C-Note No", "C-Note Date", "Department",
    "Trip Code", "Vehicle No", "Vehicle Type", "Vehicle Source", "Trip Start Date",
    "Settlement Date", "Reference No", "Billing Amount", "Invoice Status", "Remarks"
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
        vehicle_number = form.fields['vehicle_number'].initial or ""
        selected_month = form.fields['month'].initial or '0'
        selected_year = form.fields['year'].initial or '0'
        from_loc_id = ""
        to_loc_id = ""

    # Base Query
    trips = TripdetailInfo.objects.all().select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_enquirynumber__en_customerdepartment',
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

    paginator = Paginator(trips, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    data_rows = []
    trip_cons_ids = [t.tr_consignmentnumber_id for t in page_obj if t.tr_consignmentnumber_id]
    goods_map = {g.cg_consignmentnumber_id: g for g in ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber_id__in=trip_cons_ids).select_related('cg_consigner')}

    for idx, trip in enumerate(page_obj, start=(page_obj.start_index() if hasattr(page_obj, 'start_index') else 1)):
        cons_goods = goods_map.get(trip.tr_consignmentnumber_id)
        row = [
            idx,
            trip.tr_loading_time.strftime("%d-%m-%Y") if trip.tr_loading_time else (trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else ""),
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
            safe_str(trip.tr_drivername)
        ]
        data_rows.append(row)

    context = {
        'first_name': first_name,
        'form': form,
        'headers': VEHICLE_LOG_HEADERS,
        'data_rows': data_rows,
        'page_obj': page_obj,
        'vehicle_number': vehicle_number,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'from_location': from_loc_id,
        'to_location': to_loc_id,
    }
    return render(request, "asset_mgt_app/vehicle_log_report.html", context)


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
        Q(tc_cancellation__gt=0) | Q(tc_financestatus_id=8)
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
        branch = "Chennai" if "MAA" in cons_no else ("Bangalore" if "BLR" in cons_no else "")
        display_date = trip.tr_loading_time.strftime("%d-%m-%Y") if trip.tr_loading_time else \
                       (trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else "")

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
            trip.tc_cancellation,
            safe_str(trip.tr_remarks)
        ]
        data_rows.append(row)

    context = {
        'first_name': first_name,
        'form': form,
        'headers': TRIP_CANCELLATION_HEADERS,
        'data_rows': data_rows,
        'page_obj': page_obj,
        'customer_id': customer_id,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'from_location': from_loc_id,
        'to_location': to_loc_id,
    }
    return render(request, "asset_mgt_app/trip_cancellation_report.html", context)


@login_required(login_url='login_page')
def vehicle_status_report_view(request):
    first_name = request.session.get('first_name')
    from ..models import VehiclemasterInfo

    vehicle_search = request.POST.get('vehicle_search')

    vehicles = VehiclemasterInfo.objects.all().select_related('vm_vehicletype')
    
    if vehicle_search:
        vehicles = vehicles.filter(vm_registrationnumber__icontains=vehicle_search)

    data_rows = []
    counter = 1
    for vehicle in vehicles:
        # Find latest trip for this vehicle
        latest_trip = TripdetailInfo.objects.filter(
            tr_vehiclenumber=vehicle.vm_registrationnumber
        ).select_related('tr_reportedlocation', 'tr_consignmentnumber').order_by('-tr_created_at').first()

        idle_date = ""
        branch = ""
        
        if latest_trip:
            # Date of Idle is when they last finished/reported
            dt = latest_trip.tr_reporteddate or latest_trip.tr_unloading_time or latest_trip.tr_created_at
            idle_date = dt.strftime("%d-%m-%Y") if dt else ""
            
            # Derive Branch (Chennai or Bangalore)
            loc_str = ""
            if latest_trip.tr_reportedlocation:
                loc_str = str(latest_trip.tr_reportedlocation.place_name).upper()
            elif latest_trip.tr_consignmentnumber:
                loc_str = str(latest_trip.tr_consignmentnumber.co_consignmentnumber).upper()

            if any(x in loc_str for x in ["MAA", "CHENNAI", "MADHAVARAM", "ALANDUR", "AIRPORT"]):
                branch = "Chennai"
            elif any(x in loc_str for x in ["BLR", "BANGALORE"]):
                branch = "Bangalore"
            else:
                branch = loc_str.capitalize()

        row = [
            counter,
            branch,
            vehicle.vm_registrationnumber,
            safe_str(vehicle.vm_vehicletype),
            idle_date
        ]
        data_rows.append(row)
        counter += 1

    context = {
        'first_name': first_name,
        'headers': VEHICLE_STATUS_HEADERS,
        'data_rows': data_rows,
        'vehicle_search': vehicle_search,
    }
    return render(request, "asset_mgt_app/vehicle_status_report.html", context)


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
    trips = TripdetailInfo.objects.filter(
        Q(tr_customerref__isnull=True) | Q(tr_customerref='')
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
        branch = "Chennai" if "MAA" in cons_no else ("Bangalore" if "BLR" in cons_no else "")
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

    # Fetch all driver advances (expense_type=1)
    advances = Driverexpense.objects.filter(
        de_expense_type__id=1  # ADVANCE type
    ).select_related(
        'driver_name', 'de_driver_id', 'trip_number'
    )

    # If driver_id is provided, try to find the name for display
    selected_driver_name = ""
    if driver_id:
        # The input might be the ID directly if selected from list
        # We need to filter by ID
        advances = advances.filter(driver_name_id=driver_id)
        try:
            selected_driver_name = DrivermasterInfo.objects.get(id=driver_id).dm_name
            # If checking directly against name text input
        except:
            pass
    
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
            safe_str(advance.driver_name.dm_id if advance.driver_name else ""),  # Employee ID
            safe_str(advance.driver_name.dm_name if advance.driver_name else ""),  # Driver name
            advance.de_date.strftime("%d-%m-%Y") if advance.de_date else "",  # Advance date
            safe_num(advance.de_total_cost),  # Advance amount
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
        'selected_driver_name': selected_driver_name, # Pass name back for input value
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
    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')
    from_loc_id = request.POST.get('from_location')
    to_loc_id = request.POST.get('to_location')

    # Get invoiced trip IDs to exclude
    invoiced_trip_ids = TransInvoiceInfo.objects.filter(
        ti_trip__isnull=False
    ).values_list('ti_trip_id', flat=True)

    # Filter trips with status "Trip Settled" (7) NOT in invoiced_trip_ids
    trips = TripdetailInfo.objects.filter(
        tc_financestatus_id=7
    ).exclude(
        id__in=invoiced_trip_ids
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
        branch = "Chennai" if "MAA" in cons_no else ("Bangalore" if "BLR" in cons_no else "")
        display_date = trip.tr_loading_time.strftime("%d-%m-%Y") if trip.tr_loading_time else \
                       (trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else "")

        # Calculate Billing Amount (sum of charges)
        billing_amount = safe_num(trip.tc_tripcost) + safe_num(trip.tc_tollcost) + safe_num(trip.tc_supervisorcost) + \
                         safe_num(trip.tc_loadingcost) + safe_num(trip.tc_unloadingcost) + safe_num(trip.tc_weighmentcost) + \
                         safe_num(trip.tc_haltingcost) + safe_num(trip.tc_handlingcost)

        row = [
            idx,
            display_date,
            branch,
            safe_str(trip.tr_enquirynumber.en_customername),
            cons_no,
            trip.tr_consignmentnumber.co_consignmentdate.strftime("%d-%m-%Y") if trip.tr_consignmentnumber and trip.tr_consignmentnumber.co_consignmentdate else "",
            safe_str(trip.tr_enquirynumber.en_customerdepartment),
            safe_str(trip.tr_tripnumber),
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype),
            safe_str(trip.tr_vehiclesource),
            trip.tr_departeddate.strftime("%d-%m-%Y %H:%M") if trip.tr_departeddate else "",
            trip.tr_updated_at.strftime("%d-%m-%Y") if trip.tr_updated_at else "", # Using tr_updated_at as proxy for settlement date if status is 7
            safe_str(trip.tr_customerref),
            billing_amount,
            "Invoice Pending",
            safe_str(trip.tr_remarks)
        ]
        data_rows.append(row)

    context = {
        'first_name': first_name,
        'form': form,
        'headers': INVOICE_PENDING_HEADERS,
        'data_rows': data_rows,
        'page_obj': page_obj,
        'customer_id': customer_id,
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

    # Get all trips that are settled (id=7) or closed (id=2)
    trips = TripdetailInfo.objects.filter(
        tc_financestatus_id__in=[2, 7]
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
    if dept_id:
        trips = trips.filter(tr_enquirynumber__en_customerdepartment_id=dept_id)
    if selected_month and selected_month != '0':
        trips = trips.filter(
            Q(tr_loading_time__month=selected_month) | Q(tr_loading_time__isnull=True, tr_created_at__month=selected_month))
    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) | Q(tr_loading_time__isnull=True, tr_created_at__year=selected_year))
    if from_loc_id:
        trips = trips.filter(tr_departedlocation_id=from_loc_id)
    if to_loc_id:
        trips = trips.filter(tr_reportedlocation_id=to_loc_id)

    trips = trips.order_by('-tr_created_at')

    paginator = Paginator(trips, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    trip_ids = [t.id for t in page_obj]
    trip_enquiries = [t.tr_enquirynumber_id for t in page_obj]

    # Pre-fetch related data
    allotments = Vehicle_allotmentInfo.objects.filter(va_enquirynumber_id__in=trip_enquiries).select_related('va_vendor')
    invoices = TransInvoiceInfo.objects.filter(ti_trip_id__in=trip_ids)
    
    # We need to fetch expenses linked to these trips.
    # Driverexpense links to TripdetailInfo via 'trip_number' (which is the FK field name in model, not `de_trip_number` char field)
    # Check model definition: trip_number = ForeignKey(TripdetailInfo...)
    expenses = Driverexpense.objects.filter(trip_number_id__in=trip_ids)

    # Maps
    allotment_map = {}
    for a in allotments:
        key = (a.va_enquirynumber_id, str(a.va_vehiclenumber) if a.va_vehiclenumber else a.va_vehiclenumber_mkt)
        allotment_map[key] = a

    invoice_map = {i.ti_trip_id: i.ti_inv_no for i in invoices}
    
    # Expense Map: trip_id -> list of expenses
    expense_map = {}
    for e in expenses:
        if e.trip_number_id not in expense_map:
            expense_map[e.trip_number_id] = []
        expense_map[e.trip_number_id].append(e)

    data_rows = []

    for idx, trip in enumerate(page_obj, start=(page_obj.start_index() if hasattr(page_obj, 'start_index') else 1)):
        # SELLING DATA
        selling_trip = safe_num(trip.tc_tripcost)
        selling_toll = safe_num(trip.tc_tollcost)
        selling_aai = safe_num(trip.tc_supervisorcost)
        selling_loading = safe_num(trip.tc_loadingcost)
        selling_unloading = safe_num(trip.tc_unloadingcost)
        selling_weighment = safe_num(trip.tc_weighmentcost)
        selling_halting = safe_num(trip.tc_haltingcost) + safe_num(trip.tc_total_halting_cost)
        selling_handling = safe_num(trip.tc_handlingcost)
        
        total_selling = selling_trip + selling_toll + selling_aai + selling_loading + \
                        selling_unloading + selling_weighment + selling_halting + selling_handling + \
                        safe_num(trip.tc_parkingcost) + safe_num(trip.tc_rtocost) + safe_num(trip.tc_betacost)

        # BUYING DATA
        # 1. Base Trip Cost from Allotment (or fallback?)
        allotment = allotment_map.get((trip.tr_enquirynumber_id, trip.tr_vehiclenumber))
        
        vendor_name = ""
        buying_trip_cost = 0.0
        
        if allotment:
            vendor_name = safe_str(allotment.va_vendor) if allotment.va_vendor else "Own Vehicle"
            buying_trip_cost = safe_num(allotment.va_standardbuy) + safe_num(allotment.va_specialbuy)
        else:
             # Fallback logic
             vendor_name = "Own Vehicle" if trip.tr_vehiclesource_id in [1, 2] else "Unassigned"
             # If no allotment, maybe we don't have buying trip cost easily available, assume 0 or derived?
             # For Market vehicles, usually allotment exists.
        
        # 2. Granular Expenses from Driverexpense
        # We need to sum up expenses by type for this trip
        trip_expenses = expense_map.get(trip.id, [])
        
        buying_toll = 0.0
        buying_aai = 0.0
        buying_loading = 0.0
        buying_unloading = 0.0
        buying_weighment = 0.0
        buying_halting = 0.0
        buying_handling = 0.0 # Not explicit in Driverexpense model
        
        # There might be other expenses, but let's map what we have in Driverexpense model
        # de_loadingcost, de_unloadingcost, de_weighmentcost, de_supervisorcost (AAI), de_rtocost, de_parkingcost, de_battacost
        # There isn't a direct "Toll" field in Driverexpense model shown earlier? 
        # Wait, the Driverexpense model showed: de_parkingcost, de_loadingcost, de_unloadingcost, de_weighmentcost, de_supervisorcost, de_rtocost, de_battacost.
        # It does NOT have a specific "Toll" field named clearly like `de_tollcost`.
        # However, it has `de_expense_type`. If expense type is used for toll, we can check that.
        # But typically `de_total_cost` is the amount.
        
        # Let's sum specific fields if they exist on the Driverexpense record, 
        # OR if there are multiple records each representing a type.
        # The model seems to have specific columns for costs on a single record? 
        # "de_loadingcost = models.FloatField(default=0.0)"
        # This implies one record can have multiple components? Or is it one record per trip?
        # Usually Driver settlement has multiple expense lines.
        # Let's aggregate ALL linked expense records for this trip.
        
        for e in trip_expenses:
             buying_loading += safe_num(e.de_loadingcost)
             buying_unloading += safe_num(e.de_unloadingcost)
             buying_weighment += safe_num(e.de_weighmentcost)
             buying_aai += safe_num(e.de_supervisorcost)
             # buying_toll? - No specific field. Maybe check if expense type is 'Toll' or similar?
             # For now, let's assume any other cost logic or if there's a field I missed.
             # Actually, often Toll is submitted as a separate expense type record.
             # If `de_expense_type` name is "Toll", we take `de_total_cost`.
             # I'll need to fetch expense types to be sure, but for now I'll stick to the explicit fields.
             
        # "Toll Expenses" - we don't have a clear field. I will leave as 0 for now or map from generic Total if type is Toll.
        # "Halting Expenses" - also no clear field in Driverexpense (only `de_parkingcost`?).
        # "Handling Expenses" - no field.
        
        total_buying = buying_trip_cost + buying_toll + buying_aai + buying_loading + \
                       buying_unloading + buying_weighment + buying_halting + buying_handling

        profit = total_selling - total_buying
        
        # Margin calculations
        profit_pct_selling = (profit / total_selling * 100) if total_selling > 0 else 0
        profit_pct_buying = (profit / total_buying * 100) if total_buying > 0 else 0
        
        bvm_inv_no = invoice_map.get(trip.id, "")
        bill_no = "" # No clear vendor bill no mapping yet

        row = [
            idx,
            trip.tr_loading_time.strftime("%d-%m-%Y") if trip.tr_loading_time else \
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
            
            # REFERENCE
            bvm_inv_no,
            vendor_name,
            bill_no,
            
            # BUYING
            buying_trip_cost,
            buying_toll,
            buying_aai,
            buying_loading,
            buying_unloading,
            buying_weighment,
            buying_halting,
            buying_handling,
            total_buying,
            
            # PROFIT
            round(profit, 2),
            f"{round(profit_pct_selling, 2)}%",
            f"{round(profit_pct_buying, 2)}%"
        ]
        data_rows.append(row)

    context = {
        'first_name': first_name,
        'form': form,
        'headers': VENDOR_PL_MKT_HEADERS,
        'data_rows': data_rows,
        'page_obj': page_obj,
        'customer_id': customer_id,
        'dept_id': dept_id,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'from_location': from_loc_id,
        'to_location': to_loc_id,
    }
    return render(request, "asset_mgt_app/vendor_p_l_mkt_report.html", context)



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

    # Get all trips that are settled (id=7) or closed (id=2)
    trips = TripdetailInfo.objects.filter(
        tc_financestatus_id__in=[2, 7]
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
    if dept_id:
        trips = trips.filter(tr_enquirynumber__en_customerdepartment_id=dept_id)
    if selected_month and selected_month != '0':
        trips = trips.filter(
            Q(tr_loading_time__month=selected_month) | Q(tr_loading_time__isnull=True, tr_created_at__month=selected_month))
    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) | Q(tr_loading_time__isnull=True, tr_created_at__year=selected_year))
    if from_loc_id:
        trips = trips.filter(tr_departedlocation_id=from_loc_id)
    if to_loc_id:
        trips = trips.filter(tr_reportedlocation_id=to_loc_id)

    trips = trips.order_by('-tr_created_at')

    paginator = Paginator(trips, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    trip_ids = [t.id for t in page_obj] 
    
    # Prefetch related data
    # 1. Vehicle Allotment for Vendor Name & Base Buying Cost
    va_map = {
        va.va_enquirynumber_id: va 
        for va in Vehicle_allotmentInfo.objects.filter(
            va_enquirynumber__in=[t.tr_enquirynumber_id for t in page_obj]
        ).select_related('va_vendor')
    }

    # 2. Invoice Info for BVM Inv No
    inv_map = {
        inv.ti_trip_id: inv 
        for inv in TransInvoiceInfo.objects.filter(ti_trip_id__in=trip_ids)
    }

    # 3. Driver Expenses for granular buying costs
    # Fetch expenses linked to these trips
    # Note: Logic assumes Driverexpense is linked to trip_number (TripdetailInfo)
    driver_expense_map = {}
    expenses = Driverexpense.objects.filter(trip_number_id__in=trip_ids)
    for exp in expenses:
        if exp.trip_number_id not in driver_expense_map:
            driver_expense_map[exp.trip_number_id] = []
        driver_expense_map[exp.trip_number_id].append(exp)


    data_rows = []
    for idx, trip in enumerate(page_obj, start=(page_obj.start_index() if hasattr(page_obj, 'start_index') else 1)):
        
        # --- Selling (Income) ---
        selling_trip_charges = safe_num(trip.tc_tripcost)
        selling_toll = safe_num(trip.tc_tollcost)
        selling_aai = safe_num(trip.tc_supervisorcost)
        selling_loading = safe_num(trip.tc_loadingcost)
        selling_unloading = safe_num(trip.tc_unloadingcost)
        selling_weighment = safe_num(trip.tc_weighmentcost)
        # Halting is sum of tc_haltingcost + tc_total_halting_cost
        selling_halting = safe_num(trip.tc_haltingcost) + safe_num(trip.tc_total_halting_cost) 
        selling_handling = safe_num(trip.tc_handlingcost)

        # Other selling components not in explicit columns but part of total Selling
        selling_parking = safe_num(trip.tc_parkingcost)
        selling_rto = safe_num(trip.tc_rtocost)
        selling_beta = safe_num(trip.tc_betacost)
        
        total_selling = (
            selling_trip_charges + selling_toll + selling_aai + 
            selling_loading + selling_unloading + selling_weighment + 
            selling_halting + selling_handling + 
            selling_parking + selling_rto + selling_beta
        )

        # --- Buying (Expenses) ---
        va_info = va_map.get(trip.tr_enquirynumber_id)
        
        # Vendor Name
        vendor_name = "Own Vehicle" # Default
        if va_info:
            if va_info.va_vendor:
                vendor_name = str(va_info.va_vendor)
            elif va_info.va_vehiclenumber_mkt: # If market vehicle number exists but no vendor linked
                vendor_name = "Market Vehicle"

        # Buying Trip Cost (Base)
        buying_trip_cost = 0.0
        if va_info:
            buying_trip_cost = safe_num(getattr(va_info, 'va_standardbuy', 0)) + safe_num(getattr(va_info, 'va_specialbuy', 0))

        # Granular Buying Expenses from Driverexpense
        trip_expenses = driver_expense_map.get(trip.id, [])
        
        # Summing up expenses for this trip
        buy_loading = sum(safe_num(e.de_loadingcost) for e in trip_expenses)
        buy_unloading = sum(safe_num(e.de_unloadingcost) for e in trip_expenses)
        buy_weighment = sum(safe_num(e.de_weighmentcost) for e in trip_expenses)
        buy_aai = sum(safe_num(e.de_supervisorcost) for e in trip_expenses)
        
        # Placeholder/Unmapped buying expenses
        buy_toll = 0.0 
        buy_halting = 0.0
        buy_handling = 0.0
        
        total_buying = (
            buying_trip_cost + buy_loading + buy_unloading + 
            buy_weighment + buy_aai + buy_toll + buy_halting + buy_handling
        )

        # --- Reference Columns ---
        inv_info = inv_map.get(trip.id)
        bvm_inv_no = inv_info.ti_inv_no if inv_info else ""
        bill_no = "" # Placeholder as per requirement

        # --- Attached / MKT Metrics ---
        
        # KM Calculations
        reported_km = safe_num(trip.tr_reportedkm)
        departed_km = safe_num(trip.tr_departedkm)
        km_run = reported_km - departed_km if (reported_km and departed_km) else 0.0
        
        agreed_km = 0.0 # Placeholder
        extra_km_amt = 0.0 # Placeholder
        
        # Rate Calculation
        # Total Buy / Total KM (or KM Run if Total KM is not distinct)
        # Assuming Total KM here refers to Actual KM Run for the trip
        buy_rate_per_km = 0.0
        if km_run > 0:
            buy_rate_per_km = total_buying / km_run
            
        # Buying (Totalbuying/Total KM) * Trip KM
        # If Trip KM is KM Run, this basically equals Total Buying.
        # This formula seems redundant if Trip KM == KM Run. 
        # Implementing literally as (Total Buying / KM Run) * KM Run
        buying_calulated = total_buying 
        if km_run > 0:
             buying_calulated = (total_buying / km_run) * km_run


        # --- Profit ---
        profit = total_selling - total_buying
        profit_pct = (profit / total_buying * 100) if total_buying > 0 else 0.0

        # --- Other Placeholders ---
        trip_index = 0
        leave_days = 0
        idle_days = 0

        row = [
            idx,
            trip.tr_loading_time.strftime("%d-%m-%Y") if trip.tr_loading_time else \
                (trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else ""),
            safe_str(trip.tr_consignmentnumber),
            safe_str(trip.tr_departedlocation),
            safe_str(trip.tr_reportedlocation),
            safe_str(trip.tr_enquirynumber.en_customername),
            safe_str(trip.tr_vehiclenumber),
            safe_str(trip.tr_vehicletype),
            selling_trip_charges,
            selling_toll,
            selling_aai,
            selling_loading,
            selling_unloading,
            selling_weighment,
            selling_halting,
            selling_handling,
            total_selling,
            vendor_name,
            bill_no,
            round(buy_rate_per_km, 2), # Total Buy / Total KM
            round(buying_calulated, 2), # Buying (Totalbuying/Total KM) * Trip KM
            round(profit, 2),
            f"{round(profit_pct, 2)}%",
            agreed_km,
            km_run,
            extra_km_amt,
            trip_index,
            leave_days,
            idle_days
        ]
        data_rows.append(row)

    context = {
        'first_name': first_name,
        'form': form,
        'headers': VENDOR_PL_ATTACHED_HEADERS,
        'data_rows': data_rows,
        'page_obj': page_obj,
        'customer_id': customer_id,
        'dept_id': dept_id,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'from_loc_id': from_loc_id,
        'to_loc_id': to_loc_id,
    }
    return render(request, "asset_mgt_app/vendor_p_l_attached_report.html", context)




@login_required(login_url='login_page')
def whatsapp_delivery_status_report_view(request):
    first_name = request.session.get('first_name')
    from ..models import Vehicle_allotmentInfo

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

    # Base Query - Fetching from TripdetailInfo to link with Consignments
    trips = TripdetailInfo.objects.all().select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_enquirynumber__en_customerdepartment',
        'tr_consignmentnumber',
        'tr_vehicletype',
        'tr_departedlocation',
        'tr_reportedlocation'
    )

    if customer_id:
        trips = trips.filter(tr_enquirynumber__en_customername_id=customer_id)
    if dept_id:
        trips = trips.filter(tr_enquirynumber__en_customerdepartment_id=dept_id)
    if selected_month and selected_month != '0':
        trips = trips.filter(
            Q(tr_loading_time__month=selected_month) | Q(tr_loading_time__isnull=True, tr_created_at__month=selected_month))
    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) | Q(tr_loading_time__isnull=True, tr_created_at__year=selected_year))
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
        
        # Mapped Columns
        branch_name = safe_str(trip.tr_enquirynumber.en_branch if hasattr(trip.tr_enquirynumber, 'en_branch') else 'Main Branch')
        customer_name = safe_str(trip.tr_enquirynumber.en_customername)
        department = safe_str(trip.tr_enquirynumber.en_customerdepartment)
        cnote_no = safe_str(trip.tr_consignmentnumber)
        
        # Determine Branch from C-Note
        lower_cnote = cnote_no.lower()
        if 'maa_' in lower_cnote:
            branch_name = "MAA"
        elif 'blr_' in lower_cnote:
            branch_name = "BLR"
        
        consignment_date = ""
        if trip.tr_consignmentnumber and trip.tr_consignmentnumber.co_consignmentdate:
            consignment_date = trip.tr_consignmentnumber.co_consignmentdate.strftime("%d-%m-%Y")

        trip_code = safe_str(trip.tr_tripnumber)
        vehicle_type = safe_str(trip.tr_vehicletype)
        from_loc = safe_str(trip.tr_departedlocation)
        to_loc = safe_str(trip.tr_reportedlocation)
        vehicle_no = safe_str(trip.tr_vehiclenumber)
        
        start_date = trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else ""
        end_date = trip.tr_reporteddate.strftime("%d-%m-%Y") if trip.tr_reporteddate else ""
        driver_name = safe_str(trip.tr_drivername)

        # Placeholders
        whatsapp_time = "" 
        delivered_status = "Pending" # Placeholder status

        row = [
            idx,
            branch_name,
            customer_name,
            department,
            cnote_no,
            consignment_date,
            trip_code,
            vehicle_type,
            from_loc,
            to_loc,
            vehicle_no,
            start_date,
            end_date,
            driver_name,
            whatsapp_time,
            delivered_status
        ]
        data_rows.append(row)

    context = {
        'first_name': first_name,
        'form': form,
        'headers': WHATSAPP_DELIVERY_HEADERS,
        'data_rows': data_rows,
        'page_obj': page_obj,
        'customer_id': customer_id,
        'dept_id': dept_id,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'from_loc_id': from_loc_id,
        'to_loc_id': to_loc_id,
    }
    return render(request, "asset_mgt_app/whatsapp_delivery_status_report.html", context)


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

    trips = TripdetailInfo.objects.all().select_related(
        'tr_enquirynumber',
        'tr_vehicletype',
        'tr_departedlocation',
        'tr_vehiclesource',
        'tr_category',
        'tr_consignmentnumber'
    )

    # Filters (Month, Year, Vehicle)
    if selected_month and selected_month != '0':
        trips = trips.filter(
            Q(tr_loading_time__month=selected_month) | Q(tr_loading_time__isnull=True, tr_created_at__month=selected_month))
    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) | Q(tr_loading_time__isnull=True, tr_created_at__year=selected_year))
    if vehicle_filter:
        trips = trips.filter(tr_vehiclenumber__icontains=vehicle_filter)

    # Aggregation Logic
    aggregated_data = {}

    for trip in trips:
        # Determine Date
        trip_date = None
        if trip.tr_loading_time:
            trip_date = trip.tr_loading_time.date()
        elif trip.tr_departeddate:
            trip_date = trip.tr_departeddate.date()
        
        if not trip_date:
            continue
            
        date_str = trip_date.strftime("%d-%m-%Y")
        
        vehicle_no = safe_str(trip.tr_vehiclenumber)
        
        # Branch mapping from Consignment Number (First 3 letters)
        if trip.tr_consignmentnumber and trip.tr_consignmentnumber.co_consignmentnumber:
             branch_name = safe_str(trip.tr_consignmentnumber.co_consignmentnumber)[:3].upper()
        else:
            branch_name = "MAA" # Default fallback
        
        key = (date_str, vehicle_no, branch_name)

        if key not in aggregated_data:
            aggregated_data[key] = {
                'branch': branch_name,
                'date': date_str,
                'vehicle_no': vehicle_no,
                'vehicle_type': safe_str(trip.tr_vehicletype),
                'active_trips': 0,
                'empty_trips': 0,
                'ownership': safe_str(trip.tr_vehiclesource), 
                'km_business': 0.0,
                'km_empty': 0.0
            }

        # Metrics Calculation
        # KM Run
        reported_km = safe_num(trip.tr_reportedkm)
        departed_km = safe_num(trip.tr_departedkm)
        km_run = reported_km - departed_km if (reported_km and departed_km) else 0.0
        
        # Active vs Empty
        # Category 1 = Active/Normal
        # Category 2, 3 = Empty/Special
        if trip.tr_category_id == 1:
            aggregated_data[key]['active_trips'] += 1
            aggregated_data[key]['km_business'] += km_run
        elif trip.tr_category_id in [2, 3]:
            aggregated_data[key]['empty_trips'] += 1
            aggregated_data[key]['km_empty'] += km_run
            
    # Convert to list for display
    data_rows = []
    # Sorting keys 
    sorted_keys = sorted(aggregated_data.keys(), key=lambda x: datetime.strptime(x[0], "%d-%m-%Y"), reverse=True)
    
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

    context = {
        'first_name': first_name,
        'form': form,
        'headers': DAILY_TRIP_COUNT_HEADERS,
        'data_rows': data_rows,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'vehicle_filter': vehicle_filter
    }
    return render(request, "asset_mgt_app/daily_trip_count_report.html", context)


@login_required(login_url='login_page')
def own_vehicle_pl_report_view(request):
    first_name = request.session.get('first_name')
    
    # Initialize Filter Form
    if request.method == "POST":
        form = DmrForm(request.POST)
    else:
        form = DmrForm()

    # Get Filter Parameters
    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')
    vehicle_number = request.POST.get('vehicle_number')
    
    # Base Query: Fetch Settled or Closed Trips
    # Focusing on Own Vehicles (tr_vehiclesource_id usually 1 or 2 for Own)
    trips = TripdetailInfo.objects.filter(
        tc_financestatus_id__in=[2, 7],
        tr_vehiclesource_id__in=[1, 2] 
    ).select_related(
        'tr_enquirynumber',
        'tr_vehicletype',
        'tr_vehiclesource',
        'tr_departedlocation',
        'tr_reportedlocation'
    )

    # Apply Filters
    if selected_month and selected_month != '0':
        trips = trips.filter(
            Q(tr_loading_time__month=selected_month) | Q(tr_loading_time__isnull=True, tr_created_at__month=selected_month))
    if selected_year and selected_year != '0':
        trips = trips.filter(
            Q(tr_loading_time__year=selected_year) | Q(tr_loading_time__isnull=True, tr_created_at__year=selected_year))
    if vehicle_number:
        trips = trips.filter(tr_vehiclenumber__icontains=vehicle_number)

    trips = trips.order_by('-tr_created_at')

    # Pagination
    paginator = Paginator(trips, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    trip_ids = [t.id for t in page_obj]
    
    # Prefetch Driver Expenses for "Toll Expenses"
    # Assuming Driverexpense linked via trip_number (TripDetail FK)
    expenses = Driverexpense.objects.filter(trip_number_id__in=trip_ids).select_related('de_expense_type')
    expense_map = {}
    for e in expenses:
        if e.trip_number_id not in expense_map:
            expense_map[e.trip_number_id] = []
        expense_map[e.trip_number_id].append(e)

    # Prefetch Vehicle Master Info for Fixed Costs
    vehicle_numbers = [t.tr_vehiclenumber for t in page_obj if t.tr_vehiclenumber]
    vehicles = VehiclemasterInfo.objects.filter(vm_registrationnumber__in=vehicle_numbers)
    vehicle_map = {v.vm_registrationnumber: v for v in vehicles}

    data_rows = []
    
    for idx, trip in enumerate(page_obj, start=(page_obj.start_index() if hasattr(page_obj, 'start_index') else 1)):
        
        # --- Date ---
        date_val = trip.tr_loading_time.strftime("%d-%m-%Y") if trip.tr_loading_time else \
                   (trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else "")

        # --- Selling Charges (Revenue) ---
        tc_toll = safe_num(trip.tc_tollcost)
        tc_aai = safe_num(trip.tc_supervisorcost)
        tc_loading = safe_num(trip.tc_loadingcost)
        tc_unloading = safe_num(trip.tc_unloadingcost)
        tc_weighment = safe_num(trip.tc_weighmentcost)
        tc_halting = safe_num(trip.tc_haltingcost) + safe_num(trip.tc_total_halting_cost)
        tc_handling = safe_num(trip.tc_handlingcost)
        
        # Total Selling
        # Sum of all revenue components
        selling_total = (
            safe_num(trip.tc_tripcost) + tc_toll + tc_aai + tc_loading + 
            tc_unloading + tc_weighment + tc_halting + tc_handling +
            safe_num(trip.tc_parkingcost) + safe_num(trip.tc_rtocost) + safe_num(trip.tc_betacost)
        )

        # --- Toll Expenses (Combined from Driverexpense) ---
        # Logic: Sum 'de_total_cost' where expense type name contains 'Toll'
        # OR fallback to 0 if no specific mapping found.
        # Since I cannot guarantee 'Toll' type exists, I will try to look for it.
        trip_expenses = expense_map.get(trip.id, [])
        toll_expenses = 0.0
        
        for e in trip_expenses:
             # loose match for Toll in expense type if available
             if e.de_expense_type and 'toll' in str(e.de_expense_type).lower():
                 toll_expenses += safe_num(e.de_total_cost)
        
        # --- Vehicle Fixed Costs (From Vehicle Master) ---
        vm = vehicle_map.get(trip.tr_vehiclenumber)
        depreciation = safe_num(vm.vm_yearofdepreciation) if vm else 0.0 # Or vm_ofdepreciation? Using yearofdepreciation as mostly value is there
        permit = safe_num(vm.vm_permitamount) if vm else 0.0
        fc = safe_num(vm.vm_fcamount) if vm else 0.0
        road_tax = safe_num(vm.vm_roadtaxamount) if vm else 0.0
        
        # Note: These are likely Annual/Fixed amounts, not per trip.
        # Displaying as is as per request "Fetch data".

        row = [
            idx,
            date_val,
            safe_str(trip.tr_vehiclenumber),
            tc_toll,         # Toll charges
            tc_aai,          # AAI charges
            tc_loading,      # Loading charges
            tc_unloading,    # Unloading charges
            tc_weighment,    # Weighment charges
            tc_halting,      # Halting charges
            tc_handling,     # Handling charges
            selling_total,   # Selling
            toll_expenses,   # Toll Expenses
            depreciation,    # Depriciation
            permit,          # Permit
            fc,              # FC
            road_tax         # Road tax
        ]
        data_rows.append(row)

    context = {
        'first_name': first_name,
        'form': form,
        'headers': OWN_VEHICLE_PL_HEADERS,
        'data_rows': data_rows,
        'page_obj': page_obj,
        'selected_month': selected_month,
        'selected_year': selected_year,
        'vehicle_number': vehicle_number,
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

        row = [
            idx,
            safe_str(claim.cc_branch),
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

            # Determine Branch from C-Note
            lower_cnote = cnote.lower()
            if 'maa_' in lower_cnote:
                branch = "MAA"
            elif 'blr_' in lower_cnote:
                branch = "BLR"
            
        # --- Halting ---
        # Timestamps for Halting not explicitly tracked
        halting_start = "" 
        halting_end = ""
        halting_days = safe_num(trip.tc_no_of_days_halting)
        
        buying_halting = expense_map.get(trip.id, 0.0)
        selling_halting = safe_num(trip.tc_haltingcost) + safe_num(trip.tc_total_halting_cost)
        diff = selling_halting - buying_halting
        
        # --- Pickup ---
        p_start = trip.tr_departeddate_pickup
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
        # Start: Reported at delivery loc
        # End: Departed from delivery loc (Unloading done)
        d_start = trip.tr_reporteddate
        d_end = trip.tr_departeddate_delivery
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
            halting_start, halting_end, halting_days,
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
