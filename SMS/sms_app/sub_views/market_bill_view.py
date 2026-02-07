from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages

from ..sub_forms.market_bill_form import MarketBillForm
from ..sub_models.market_bill_mod import MarketBillInfo
from ..sub_models.vendor_info_mod import Vendor_info
from ..sub_models.vehiclemaster_mod import VehiclemasterInfo
from ..sub_models.tripdetail_mod import TripdetailInfo
from ..sub_models.vehicle_allotment_mod import Vehicle_allotmentInfo
from ..sub_models.haltingcharges_mod import Haltingcharges


# ==================================================
# ADD MARKET BILL
# ==================================================
@login_required(login_url='login_page')
def market_bill_add(request):
    if request.method == "POST":
        form = MarketBillForm(request.POST)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.mb_created_by = request.user
            obj.save()
            messages.success(request, "Market Bill saved successfully.")
            return redirect('market_bill_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = MarketBillForm()

    return render(
        request,
        "asset_mgt_app/market_bill.html",
        {
            "form": form,
        }
    )


# ==================================================
# LIST MARKET BILLS
# ==================================================
@login_required(login_url='login_page')
def market_bill_list(request):
    bills = MarketBillInfo.objects.all().order_by('-mb_created_at')

    return render(
        request,
        "asset_mgt_app/market_bill_list.html",
        {
            "bills": bills
        }
    )


# ==================================================
# EDIT MARKET BILL
# ==================================================
@login_required(login_url='login_page')
def market_bill_edit(request, id):
    record = get_object_or_404(MarketBillInfo, id=id)

    if request.method == "POST":
        form = MarketBillForm(request.POST, instance=record)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.mb_updated_by = request.user
            obj.save()
            messages.success(request, "Market Bill updated successfully.")
            return redirect('market_bill_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        # Robust fetch for vehicle type if missing in record but number exists
        if record.mb_vehicle_number and not record.mb_vehicle_type:
            # Check Vehicle Master
            v_master = VehiclemasterInfo.objects.filter(vm_registrationnumber__iexact=record.mb_vehicle_number).first()
            if v_master and v_master.vm_vehicletype:
                record.mb_vehicle_type = str(v_master.vm_vehicletype)
            # Check recent trips with a non-null type
            v_trip = TripdetailInfo.objects.filter(
                tr_vehiclenumber__iexact=record.mb_vehicle_number
            ).exclude(tr_vehicletype__isnull=True).order_by('-tr_created_at').first()
            if v_trip and v_trip.tr_vehicletype:
                record.mb_vehicle_type = str(v_trip.tr_vehicletype)
        
        form = MarketBillForm(instance=record)

    # Fetch selected trips data for the edit page table
    selected_trips_data = []
    if record.mb_selected_trips:
        trip_ids = [int(tid) for tid in record.mb_selected_trips.split(',') if tid.strip()]
        selected_trips = TripdetailInfo.objects.filter(id__in=trip_ids).select_related('tr_enquirynumber', 'tr_consignmentnumber')
        
        for trip in selected_trips:
            from_location = ''
            to_location = ''
            if trip.tr_enquirynumber:
                if trip.tr_enquirynumber.en_fromlocaion:
                    from_location = str(trip.tr_enquirynumber.en_fromlocaion)
                if trip.tr_enquirynumber.en_tolocation:
                    to_location = str(trip.tr_enquirynumber.en_tolocation)

            trip_date = ''
            if trip.tr_departeddate:
                trip_date = trip.tr_departeddate.strftime('%d-%m-%Y')
            elif trip.tr_created_at:
                trip_date = trip.tr_created_at.strftime('%d-%m-%Y')

            # Fetch vehicle type
            # Robust fetch for vehicle type
            v_master = VehiclemasterInfo.objects.filter(vm_registrationnumber__iexact=trip.tr_vehiclenumber).first()
            if v_master and v_master.vm_vehicletype:
                vehicle_type = str(v_master.vm_vehicletype)
            elif trip.tr_vehicletype:
                vehicle_type = str(trip.tr_vehicletype)
            else:
                vehicle_type = ''

            selected_trips_data.append({
                'id': trip.id,
                'trip_number': (trip.tr_consignmentnumber.co_consignmentnumber if trip.tr_consignmentnumber and trip.tr_consignmentnumber.co_consignmentnumber else (trip.tr_tripnumber or '')),
                'vehicle_number': trip.tr_vehiclenumber or '',
                'vehicle_type': vehicle_type,
                'from_location': from_location,
                'to_location': to_location,
                'trip_date': trip_date,
                'trip_cost': float(trip.tc_tripcost or 0),
                'parking_cost': float(trip.tc_parkingcost or 0),
                'halting_days': int(trip.tc_no_of_days_halting or 0),
                'halting_cost': float(trip.tc_haltingcost or 0),
            })

    return render(
        request,
        "asset_mgt_app/market_bill.html",
        {
            "form": form,
            "record": record,
            "selected_trips_data": selected_trips_data,
        }
    )


# ==================================================
# DELETE MARKET BILL
# ==================================================
@login_required(login_url='login_page')
def market_bill_delete(request, id):
    record = get_object_or_404(MarketBillInfo, id=id)

    if request.method == "POST":
        record.delete()
        messages.success(request, "Market Bill deleted successfully.")
        return redirect('market_bill_list')

    return redirect('market_bill_list')


# ==================================================
# AJAX: GET VEHICLES BY VENDOR
# ==================================================
@login_required(login_url='login_page')
def get_vehicles_by_vendor(request):
    vendor_id = request.GET.get('vendor_id')

    if not vendor_id:
        return JsonResponse({'vehicles': []})

    vehicles = VehiclemasterInfo.objects.filter(
        vm_vendor_id=vendor_id
    ).values_list('vm_registrationnumber', flat=True)

    vehicle_list = [{'id': v, 'text': v} for v in vehicles if v]

    return JsonResponse({'vehicles': vehicle_list})


# ==================================================
# AJAX: GET TRIPS BY VEHICLE
# ==================================================
@login_required(login_url='login_page')
def get_trips_by_vehicle(request):
    vehicle_number = request.GET.get('vehicle_number')

    if not vehicle_number:
        return JsonResponse({'trips': []})

    # Get all already billed trip IDs from all MarketBillInfo records
    billed_trip_ids = set()
    all_bills = MarketBillInfo.objects.exclude(mb_selected_trips__isnull=True).exclude(mb_selected_trips='')
    for bill in all_bills:
        ids = [tid.strip() for tid in bill.mb_selected_trips.split(',') if tid.strip()]
        billed_trip_ids.update(ids)

    # Filter trips that are not in billed_trip_ids
    trips = TripdetailInfo.objects.filter(
        tr_vehiclenumber=vehicle_number
    ).exclude(id__in=list(billed_trip_ids)).select_related('tr_enquirynumber', 'tr_consignmentnumber')

    trip_list = []
    for trip in trips:
        # Get from/to locations from enquiry
        from_location = ''
        to_location = ''
        if trip.tr_enquirynumber:
            if trip.tr_enquirynumber.en_fromlocaion:
                from_location = str(trip.tr_enquirynumber.en_fromlocaion)
            if trip.tr_enquirynumber.en_tolocation:
                to_location = str(trip.tr_enquirynumber.en_tolocation)

        # Get trip date
        trip_date = ''
        if trip.tr_departeddate:
            trip_date = trip.tr_departeddate.strftime('%d-%m-%Y')
        elif trip.tr_created_at:
            trip_date = trip.tr_created_at.strftime('%d-%m-%Y')

        # --- Trip Cost Logic ---
        # Fetch va_specialbuy or va_standardbuy from allotment
        trip_cost = 0
        allotment = Vehicle_allotmentInfo.objects.filter(va_enquirynumber=trip.tr_enquirynumber).first()
        if allotment:
            trip_cost = allotment.va_specialbuy if allotment.va_specialbuy else allotment.va_standardbuy
        
        if not trip_cost:
            trip_cost = trip.tc_tripcost or 0

        # --- Halting Cost Logic ---
        # Fetch halting rate based on customer and trip type
        halting_days = int(trip.tc_no_of_days_halting or 0)
        halting_rate = 0
        if trip.tr_enquirynumber:
            enquiry = trip.tr_enquirynumber
            try:
                halting_obj = Haltingcharges.objects.filter(
                    hc_Customer_name=enquiry.en_customername,
                    hc_trip_type=enquiry.en_trip_type
                ).first()
                if halting_obj:
                    halting_rate = halting_obj.hc_charges
            except:
                pass
        
        halting_cost = halting_rate * halting_days

        # Fetch vehicle type for this trip
        vehicle = VehiclemasterInfo.objects.filter(vm_registrationnumber=trip.tr_vehiclenumber).first()
        vehicle_type = str(vehicle.vm_vehicletype) if vehicle and vehicle.vm_vehicletype else ''

        trip_list.append({
            'id': trip.id,
            'trip_number': (trip.tr_consignmentnumber.co_consignmentnumber if trip.tr_consignmentnumber and trip.tr_consignmentnumber.co_consignmentnumber else (trip.tr_tripnumber or '')),
            'vehicle_number': trip.tr_vehiclenumber or '',
            'vehicle_type': vehicle_type,
            'from_location': from_location,
            'to_location': to_location,
            'trip_date': trip_date,
            'trip_cost': float(trip_cost),
            'parking_cost': float(trip.tc_parkingcost or 0),
            'halting_days': halting_days,
            'halting_cost': float(halting_cost),
        })

    return JsonResponse({'trips': trip_list})


# ==================================================
# AJAX: GET VEHICLE DETAILS (TYPE)
# ==================================================
@login_required(login_url='login_page')
def get_vehicle_details(request):
    vehicle_number = request.GET.get('vehicle_number')

    if not vehicle_number:
        return JsonResponse({'vehicle_type': ''})

    # Try Vehiclemaster first (case-insensitive)
    v_master = VehiclemasterInfo.objects.filter(vm_registrationnumber__iexact=vehicle_number).first()
    if v_master and v_master.vm_vehicletype:
        vehicle_type = str(v_master.vm_vehicletype)
    else:
        # Fallback: check TripdetailInfo for this vehicle number - specifically find one with a type
        v_trip = TripdetailInfo.objects.filter(
            tr_vehiclenumber__iexact=vehicle_number
        ).exclude(tr_vehicletype__isnull=True).order_by('-tr_created_at').first()
        vehicle_type = str(v_trip.tr_vehicletype) if v_trip and v_trip.tr_vehicletype else ''

    return JsonResponse({'vehicle_type': vehicle_type})
