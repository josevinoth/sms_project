from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from ..models import TripdetailInfo, ConsignmentdetailInfo, CustomerInfo, CustomerdepartmentInfo, ConsignmentgoodsInfo, Places
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
    else:
        form = DmrForm()

    customer_id = request.POST.get('dmr_customer')
    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')
    from_loc_id = request.POST.get('from_location')
    to_loc_id = request.POST.get('to_location')

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
    if customer_id:
        trips = trips.filter(tr_enquirynumber__en_customername_id=customer_id)
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
        'customer_id': customer_id,
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
