from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Sum, Q
import calendar
from datetime import date as dt_date, timedelta

from ..sub_forms.attached_bill_form import AttachedBillForm
from ..sub_models.attached_bill_mod import AttachedBillInfo
from ..sub_models.vehiclemaster_mod import VehiclemasterInfo
from ..sub_models.tripdetail_mod import TripdetailInfo


# ==================================================
# ADD ATTACHED BILL
# ==================================================
@login_required(login_url='login_page')
def attached_bill_add(request):
    if request.method == "POST":
        form = AttachedBillForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.ab_created_by = request.user
            obj.save()
            messages.success(request, "Attached Bill saved successfully.")
            return redirect('attached_bill_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AttachedBillForm()

    return render(
        request,
        "asset_mgt_app/attached_bill_add.html",
        {
            "form": form,
            "title": "Add Attached Bill"
        }
    )


# ==================================================
# LIST ATTACHED BILLS
# ==================================================
@login_required(login_url='login_page')
def attached_bill_list(request):
    bills = AttachedBillInfo.objects.all().order_by('-ab_created_at')
    return render(
        request,
        "asset_mgt_app/attached_bill_list.html",
        {
            "bills": bills
        }
    )


# ==================================================
# EDIT ATTACHED BILL
# ==================================================
@login_required(login_url='login_page')
def attached_bill_edit(request, id):
    record = get_object_or_404(AttachedBillInfo, id=id)
    if request.method == "POST":
        form = AttachedBillForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.ab_updated_by = request.user
            obj.save()
            messages.success(request, "Attached Bill updated successfully.")
            return redirect('attached_bill_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AttachedBillForm(instance=record)

    return render(
        request,
        "asset_mgt_app/attached_bill_add.html",
        {
            "form": form,
            "record": record,
            "title": "Edit Attached Bill"
        }
    )


# ==================================================
# DELETE ATTACHED BILL
# ==================================================
@login_required(login_url='login_page')
def attached_bill_delete(request, id):
    record = get_object_or_404(AttachedBillInfo, id=id)
    if request.method == "POST":
        record.delete()
        messages.success(request, "Attached Bill deleted successfully.")
    return redirect('attached_bill_list')


# ==================================================
# QUICK MEDIA UPLOAD
# ==================================================
@login_required(login_url='login_page')
def attached_bill_upload(request, id):
    record = get_object_or_404(AttachedBillInfo, id=id)
    if request.method == "POST" and request.FILES.get('ab_bill_upload'):
        record.ab_bill_upload = request.FILES.get('ab_bill_upload')
        record.save()
        messages.success(request, "File uploaded successfully.")
    return redirect('attached_bill_list')


# ==================================================
# AJAX: GET VEHICLE DETAILS & KM RUN
# ==================================================
@login_required(login_url='login_page')
def get_attached_vehicle_details(request):
    vendor_id = request.GET.get('vendor_id')
    vehicle_id = request.GET.get('vehicle_id')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    data = {'trips': []}

    if vehicle_id:
        vehicle = get_object_or_404(VehiclemasterInfo, id=vehicle_id)
        data.update({
            'vehicle_type': str(vehicle.vm_vehicletype) if vehicle.vm_vehicletype else "",
            'buy_cost': float(vehicle.vm_buycost) if vehicle.vm_buycost and vehicle.vm_buycost.replace('.','',1).isdigit() else 0.0,
            'agreed_km': float(vehicle.vm_agreedkm) if vehicle.vm_agreedkm and vehicle.vm_agreedkm.replace('.','',1).isdigit() else 0.0,
            'extra_km_rate': float(vehicle.vm_extrakm) if vehicle.vm_extrakm and vehicle.vm_extrakm.replace('.','',1).isdigit() else 0.0,
        })
    elif vendor_id:
        # Just vendor selected, we don't have vehicle specific details yet but we can still fetch trips
        pass

    # Filter trips
    filters = Q()
    if vehicle_id:
        vehicle = VehiclemasterInfo.objects.get(id=vehicle_id)
        filters &= Q(tr_vehiclenumber=vehicle.vm_registrationnumber)
    elif vendor_id:
        # Get all vehicles for this vendor and filter trips by those registration numbers
        vehicle_reg_nos = VehiclemasterInfo.objects.filter(vm_vendor_id=vendor_id).values_list('vm_registrationnumber', flat=True)
        filters &= Q(tr_vehiclenumber__in=vehicle_reg_nos)
    
    if from_date and to_date:
        filters &= Q(tr_departeddate__date__range=[from_date, to_date])

    if filters:
        # Get all billed trip numbers to exclude them
        bill_id = request.GET.get('bill_id')
        billed_trips_query = AttachedBillInfo.objects.all()
        if bill_id:
            billed_trips_query = billed_trips_query.exclude(id=bill_id)
        
        already_billed = []
        for b_trips in billed_trips_query.values_list('ab_selected_trips', flat=True):
            if b_trips:
                already_billed.extend([t.strip() for t in b_trips.split(',') if t.strip()])
        
        # Apply exclusion
        if already_billed:
            filters &= ~Q(tr_tripnumber__in=already_billed)

        trips = TripdetailInfo.objects.filter(filters).order_by('-tr_departeddate')
        total_km_run = 0
        trip_dates = set()  # Unique departure dates (days vehicle made at least one trip)

        for trip in trips:
            km = (trip.tr_reportedkm or 0) - (trip.tr_departedkm or 0)
            if km < 0: km = 0
            total_km_run += km

            # Track unique departure dates
            if trip.tr_departeddate:
                trip_dates.add(trip.tr_departeddate.date())

            # Use Enquirynote data for customer name
            customer_name = trip.tr_enquirynumber.en_customername.cu_name if trip.tr_enquirynumber and trip.tr_enquirynumber.en_customername else "N/A"

            data['trips'].append({
                'trip_date': trip.tr_departeddate.strftime('%d-%m-%Y') if trip.tr_departeddate else "",
                'trip_no': trip.tr_tripnumber or "",
                'cnote': trip.tr_consignmentnumber.co_consignmentnumber if trip.tr_consignmentnumber else "",
                'customer': customer_name,
                'from': str(trip.tr_departedlocation) if trip.tr_departedlocation else "",
                'to': str(trip.tr_reportedlocation) if trip.tr_reportedlocation else "",
                'trip_km': km,
                'buy_cost': float(trip.tc_tripcost or 0),
                'parking_cost': float(trip.tc_parkingcost or 0),
                'toll_cost': float(trip.tc_tollcost or 0),
                'total_buy_cost': float((trip.tc_tripcost or 0) + (trip.tc_parkingcost or 0) + (trip.tc_tollcost or 0))
            })

        data['total_km_run'] = total_km_run

        # Leave days calculation:
        # A day is a leave day if it had no trips.
        # Sundays are normally excluded — BUT if both the Saturday before AND
        # the Monday after are leave days (no trips), that Sunday counts as leave too.
        if from_date and to_date:
            from datetime import date as dt_date, timedelta
            start_dt = dt_date.fromisoformat(from_date)
            end_dt = dt_date.fromisoformat(to_date)

            # Build set of leave days (non-Sunday days with no trips)
            leave_set = set()
            curr = start_dt
            while curr <= end_dt:
                if curr.weekday() != 6:  # skip Sundays for now
                    if curr not in trip_dates:
                        leave_set.add(curr)
                curr += timedelta(days=1)

            # Now check every Sunday in the period:
            # If Saturday (day before) AND Monday (day after) are both in leave_set,
            # count that Sunday as leave too.
            leave_days_count = len(leave_set)
            curr = start_dt
            while curr <= end_dt:
                if curr.weekday() == 6:  # It's a Sunday
                    saturday = curr - timedelta(days=1)
                    monday   = curr + timedelta(days=1)
                    # Both bounding days must be within the period and be leave days
                    if saturday >= start_dt and monday <= end_dt:
                        if saturday in leave_set and monday in leave_set:
                            leave_days_count += 1
                curr += timedelta(days=1)

            data['leave_days'] = leave_days_count
        else:
            data['leave_days'] = 0
    else:
        data['total_km_run'] = 0
        data['leave_days'] = 0

    return JsonResponse(data)


@login_required(login_url='login_page')
def attached_bill_summary(request, id):
    """Return structured summary data for the bill summary modal."""
    bill = get_object_or_404(AttachedBillInfo, id=id)
    vehicle = bill.ab_vehicle_number
    vendor = bill.ab_vendor

    # --- Period info ---
    from_date = bill.ab_from_date
    to_date = bill.ab_to_date
    days_in_month = 0
    working_days = 0
    if from_date and to_date:
        days_in_month = (to_date - from_date).days + 1
        curr = from_date
        while curr <= to_date:
            if curr.weekday() != 6:  # not Sunday
                working_days += 1
            curr += timedelta(days=1)

    # --- Use SAVED bill fields for reliable values ---
    contract_amount = float(bill.ab_buy_cost or 0)
    leave_days     = int(bill.ab_leave_days or 0)
    leave_per_day  = (contract_amount / days_in_month) if days_in_month > 0 else 0
    leave_amount   = float(bill.ab_leave_amount or 0)
    agreed_km      = float(bill.ab_agreed_km or 0)
    total_km_saved = float(bill.ab_total_km_run or 0)   # saved total KM from ADD/EDIT
    extra_km       = float(bill.ab_extra_km_run or 0)
    extra_km_amount = float(bill.ab_extra_km_amount or 0)
    actual_amount  = float(bill.ab_bill_amount or 0)

    # --- Fetch selected trips ONLY ---
    selected_trip_numbers = [t.strip() for t in (bill.ab_selected_trips or '').split(',') if t.strip()]
    total_trips = len(selected_trip_numbers)

    trips = []
    if selected_trip_numbers:
        trip_filters = Q(tr_tripnumber__in=selected_trip_numbers)
        # Optional: verify vehicle and date range for data integrity
        if vehicle:
            trip_filters &= Q(tr_vehiclenumber=vehicle.vm_registrationnumber)
        
        trips = list(TripdetailInfo.objects.filter(trip_filters).select_related(
            'tr_departedlocation', 'tr_reportedlocation', 'tr_enquirynumber'
        ))

    # Use fetched trips for KM/Selling calculation (these ARE the billed trips)
    trip_km_run = 0
    trip_days   = set()
    for t in trips:
        trip_km_run += max(0, (t.tr_reportedkm or 0) - (t.tr_departedkm or 0))
        if t.tr_departeddate:
            trip_days.add(t.tr_departeddate.date())

    # Use saved total_km_run when trips still can't be fetched
    display_total_km = trip_km_run if trips else total_km_saved

    days_run   = len(trip_days)
    trip_index = f"{total_trips} TRIPS / {days_run} DAYS RUN" if days_run else f"{total_trips} TRIPS"

    # --- Empty KM = Agreed KM − Total KM Run ---
    empty_km           = max(0.0, agreed_km - display_total_km)
    per_km_amount      = (actual_amount / total_km_saved) if total_km_saved > 0 else 0
    empty_km_buy_cost  = per_km_amount * empty_km
    business_empty_km          = empty_km
    business_empty_km_buy_cost = empty_km_buy_cost

    # --- Selling = sum of all trip charges billed to customer ---
    selling = 0.0
    for t in trips:
        selling += (float(t.tc_tripcost or 0) + float(t.tc_tollcost or 0) +
                    float(t.tc_supervisorcost or 0) + float(t.tc_loadingcost or 0) +
                    float(t.tc_unloadingcost or 0) + float(t.tc_weighmentcost or 0) +
                    float(t.tc_haltingcost or 0) + float(t.tc_handlingcost or 0))

    # --- Buying = actual bill amount paid to vendor ---
    buying = actual_amount

    # --- Profit / % ---
    profit   = selling - buying
    sell_pct = round((profit / selling) * 100, 2) if selling > 0 else 0
    buy_pct  = round((profit / buying)  * 100, 2) if buying  > 0 else 0

    # --- Title ---
    vendor_name  = vendor.vend_name if vendor else "N/A"
    period_label = from_date.strftime("%b %Y").upper() if from_date else ""
    title        = f"{vendor_name} - {period_label}"

    return JsonResponse({
        'title': title,
        'vehicle_no':   vehicle.vm_registrationnumber if vehicle else '',
        'vehicle_type': str(vehicle.vm_vehicletype) if vehicle and vehicle.vm_vehicletype else '',
        'days_in_month': days_in_month,
        'working_days':  working_days,
        'leave_days':    leave_days,
        'contract_amount': round(contract_amount, 2),
        'leave_per_day':   round(leave_per_day, 2),
        'leave_amount':    round(leave_amount, 2),
        'extra_km':        round(extra_km, 2),
        'extra_km_amount': round(extra_km_amount, 2),
        'actual_amount':   round(actual_amount, 2),
        'total_trips': total_trips,
        'trip_index':  trip_index,
        'total_km':    round(display_total_km, 2),
        'agreed_km':   round(agreed_km, 2),
        'empty_km':              round(empty_km, 2),
        'per_km_amount':         round(per_km_amount, 2),
        'empty_km_buy_cost':     round(empty_km_buy_cost, 2),
        'business_empty_km':          round(business_empty_km, 2),
        'business_empty_km_buy_cost': round(business_empty_km_buy_cost, 2),
        'selling': round(selling, 2),
        'buying':  round(buying, 2),
        'profit':  round(profit, 2),
        'sell_pct': sell_pct,
        'buy_pct':  buy_pct,
    })


@login_required(login_url='login_page')
def get_vehicles_by_vendor(request):
    vendor_id = request.GET.get('vendor_id')
    if not vendor_id:
        return JsonResponse({'vehicles': []})
    
    # Ownership ID 2 = ATTACHED
    vehicles = VehiclemasterInfo.objects.filter(vm_vendor_id=vendor_id, vm_ownership_id=2).order_by('vm_registrationnumber')
    
    veh_list = []
    for v in vehicles:
        veh_list.append({
            'id': v.id,
            'reg_no': v.vm_registrationnumber
        })
    
    return JsonResponse({'vehicles': veh_list})
