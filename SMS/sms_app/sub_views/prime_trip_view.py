from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime

from ..models import PrimeVehicleAllotmentInfo, PrimeTripInfo, MyUser, Places, TripdetailInfo

@login_required(login_url='login_page')
def prime_trip_add(request, allotment_id):
    # Ensure session has user details
    user_id = request.session.get('ses_userID')
    if not user_id:
        return redirect('login_page')

    # Get the vehicle allotment
    allotment = get_object_or_404(PrimeVehicleAllotmentInfo, pk=allotment_id)
    enquiry = allotment.pva_enquirynumber

    # Check if a trip already exists for this allotment (get the latest one)
    trip = PrimeTripInfo.objects.filter(pt_allotment=allotment).order_by('-id').first()
    if trip and (trip.pt_to_place or trip.pt_to_km or trip.pt_to_date):
        trip = None

    if request.method == 'POST':
        try:
            if trip:
                # Update Mode: only update To Details and Conditional Shipment fields
                trip.pt_to_date = request.POST.get('pt_to_date') or None
                trip.pt_to_time = request.POST.get('pt_to_time') or None
                trip.pt_to_km = request.POST.get('pt_to_km') or None
                trip.pt_to_place = request.POST.get('pt_to_place') or None
                trip.pt_updated_by_id = user_id
                
                # Check empty / shipment
                pt_empty_shipment = request.POST.get('pt_empty_shipment')
                if pt_empty_shipment:
                    trip.pt_empty_shipment = pt_empty_shipment
                
                # Update other conditional shipment fields if it's shipment and editable
                if trip.pt_empty_shipment != 'Empty':
                    # Consignment details
                    trip.pt_cnote_date = request.POST.get('pt_cnote_date') or None
                    trip.pt_consigner = request.POST.get('pt_consigner') or None
                    trip.pt_consignee = request.POST.get('pt_consignee') or None
                    # Shipment Info
                    trip.pt_shipment_weight = request.POST.get('pt_shipment_weight') or None
                    trip.pt_no_of_pcs = request.POST.get('pt_no_of_pcs') or None
                    trip.pt_shipment_value_inr = request.POST.get('pt_shipment_value_inr') or None
                    trip.pt_customer_ref_name = request.POST.get('pt_customer_ref_name') or None
                    trip.pt_customer_ref_no = request.POST.get('pt_customer_ref_no') or None
                    trip.pt_ewb_no = request.POST.get('pt_ewb_no') or None
                    trip.pt_ewb_validity_date = request.POST.get('pt_ewb_validity_date') or None

                trip.save()
                messages.success(request, f"Prime Trip {trip.pt_prime_trip_no} Updated/Closed Successfully!")
            else:
                # Create Mode
                # Generate Prime Trip Number (e.g. 26-27_MAA_PTR_000001)
                # Find last prime trip no and increment
                last_trip = PrimeTripInfo.objects.all().order_by('-id').first()
                if last_trip and last_trip.pt_prime_trip_no:
                    parts = last_trip.pt_prime_trip_no.split('_')
                    if len(parts) == 4:
                        num = int(parts[-1]) + 1
                        prime_trip_no = f"{parts[0]}_{parts[1]}_{parts[2]}_{num:06d}"
                    else:
                        prime_trip_no = "26-27_MAA_PTR_000001"
                else:
                    prime_trip_no = "26-27_MAA_PTR_000001"

                # Generate C-Note Number
                trip_type = request.POST.get('pt_empty_shipment') or 'Shipment'
                cnote_no = None
                if trip_type != 'Empty':
                    last_shipment = PrimeTripInfo.objects.filter(pt_cnote_number__isnull=False).exclude(pt_cnote_number='').order_by('-id').first()
                    if last_shipment and last_shipment.pt_cnote_number:
                        parts = last_shipment.pt_cnote_number.split('_')
                        if len(parts) == 3 and parts[1] == 'PCON':
                            try:
                                num = int(parts[-1]) + 1
                                cnote_no = f"MAA_PCON_{num:06d}"
                            except ValueError:
                                cnote_no = "MAA_PCON_100001"
                        else:
                            cnote_no = "MAA_PCON_100001"
                    else:
                        cnote_no = "MAA_PCON_100001"

                # Create trip
                trip_obj = PrimeTripInfo(
                    pt_allotment=allotment,
                    pt_prime_trip_no=prime_trip_no,
                    pt_from_date=request.POST.get('pt_from_date') or None,
                    pt_from_time=request.POST.get('pt_from_time') or None,
                    pt_from_km=request.POST.get('pt_from_km') or None,
                    pt_from_place=request.POST.get('pt_from_place') or None,
                    pt_empty_shipment=trip_type,
                    pt_cnote_number=cnote_no,
                    pt_cnote_date=request.POST.get('pt_cnote_date') if trip_type != 'Empty' else None,
                    pt_consigner=request.POST.get('pt_consigner') if trip_type != 'Empty' else None,
                    pt_consignee=request.POST.get('pt_consignee') if trip_type != 'Empty' else None,
                    pt_shipment_weight=request.POST.get('pt_shipment_weight') if trip_type != 'Empty' else None,
                    pt_no_of_pcs=request.POST.get('pt_no_of_pcs') if trip_type != 'Empty' else None,
                    pt_shipment_value_inr=request.POST.get('pt_shipment_value_inr') if trip_type != 'Empty' else None,
                    pt_customer_ref_name=request.POST.get('pt_customer_ref_name') if trip_type != 'Empty' else None,
                    pt_customer_ref_no=request.POST.get('pt_customer_ref_no') if trip_type != 'Empty' else None,
                    pt_ewb_no=request.POST.get('pt_ewb_no') if trip_type != 'Empty' else None,
                    pt_ewb_validity_date=request.POST.get('pt_ewb_validity_date') if trip_type != 'Empty' else None,
                    pt_created_by_id=user_id,
                    pt_updated_by_id=user_id
                )
                trip_obj.save()
                messages.success(request, f"Prime Trip {prime_trip_no} Created Successfully!")
            return redirect('prime_trip_list')

        except Exception as e:
            messages.error(request, f"Error saving trip: {str(e)}")
            return redirect('prime_trip_add', allotment_id=allotment_id)

    # For GET request, render the form
    if trip:
        expected_trip_no = trip.pt_prime_trip_no
        expected_cnote_no = trip.pt_cnote_number or ""
    else:
        last_trip = PrimeTripInfo.objects.all().order_by('-id').first()
        if last_trip and last_trip.pt_prime_trip_no:
            parts = last_trip.pt_prime_trip_no.split('_')
            if len(parts) == 4:
                num = int(parts[-1]) + 1
                expected_trip_no = f"{parts[0]}_{parts[1]}_{parts[2]}_{num:06d}"
            else:
                expected_trip_no = "26-27_MAA_PTR_000001"
        else:
            expected_trip_no = "26-27_MAA_PTR_000001"

        last_shipment = PrimeTripInfo.objects.filter(pt_cnote_number__isnull=False).exclude(pt_cnote_number='').order_by('-id').first()
        if last_shipment and last_shipment.pt_cnote_number:
            parts = last_shipment.pt_cnote_number.split('_')
            if len(parts) == 3 and parts[1] == 'PCON':
                try:
                    num = int(parts[-1]) + 1
                    expected_cnote_no = f"MAA_PCON_{num:06d}"
                except ValueError:
                    expected_cnote_no = "MAA_PCON_100001"
            else:
                expected_cnote_no = "MAA_PCON_100001"
        else:
            expected_cnote_no = "MAA_PCON_100001"

    # Find the registration number of the vehicle
    registration_number = ""
    if allotment.pva_vehiclesource_id == 3:
        registration_number = allotment.pva_vehiclenumber_mkt.strip() if allotment.pva_vehiclenumber_mkt else ""
    elif allotment.pva_vehiclenumber:
        registration_number = allotment.pva_vehiclenumber.vm_registrationnumber.strip() if allotment.pva_vehiclenumber.vm_registrationnumber else ""

    last_reported_place = ""
    last_reported_km = ""

    if registration_number:
        from django.db.models import Q
        # Check TripdetailInfo (TMS trips) for the latest trip of this vehicle
        last_tms_trip = (
            TripdetailInfo.objects
            .filter(tr_vehiclenumber=registration_number)
            .exclude(tr_reportedkm__isnull=True)
            .exclude(tr_reportedkm=0)
            .order_by('-tr_created_at')
            .first()
        )
        
        # Check PrimeTripInfo (Prime trips) for the latest trip of this vehicle
        last_prime_trip = (
            PrimeTripInfo.objects
            .filter(
                Q(pt_allotment__pva_vehiclenumber__vm_registrationnumber=registration_number) |
                Q(pt_allotment__pva_vehiclenumber_mkt=registration_number)
            )
            .exclude(pt_to_km__isnull=True)
            .exclude(pt_to_km=0)
            .order_by('-pt_created_at')
            .first()
        )

        # Compare to find the most recent trip globally for this vehicle
        tms_time = last_tms_trip.tr_created_at if last_tms_trip else None
        prime_time = last_prime_trip.pt_created_at if last_prime_trip else None

        if tms_time and prime_time:
            if tms_time > prime_time:
                last_reported_km = last_tms_trip.tr_reportedkm
                last_reported_place = last_tms_trip.tr_reportedlocation.place_name if last_tms_trip.tr_reportedlocation else ""
            else:
                last_reported_km = last_prime_trip.pt_to_km
                last_reported_place = last_prime_trip.pt_to_place or ""
        elif tms_time:
            last_reported_km = last_tms_trip.tr_reportedkm
            last_reported_place = last_tms_trip.tr_reportedlocation.place_name if last_tms_trip.tr_reportedlocation else ""
        elif prime_time:
            last_reported_km = last_prime_trip.pt_to_km
            last_reported_place = last_prime_trip.pt_to_place or ""

    places = Places.objects.all().order_by('place_name')

    context = {
        'allotment': allotment,
        'enquiry': enquiry,
        'expected_trip_no': expected_trip_no,
        'expected_cnote_no': expected_cnote_no,
        'places': places,
        'last_reported_place': last_reported_place,
        'last_reported_km': last_reported_km,
        'trip': trip,
    }
    return render(request, 'asset_mgt_app/prime_trip_add.html', context)


from collections import defaultdict
from django.utils import timezone

@login_required(login_url='login_page')
def prime_trip_list(request):
    trips = PrimeTripInfo.objects.all().select_related(
        'pt_allotment',
        'pt_allotment__pva_vehiclenumber',
        'pt_allotment__pva_enquirynumber'
    ).order_by('-pt_from_date', '-pt_from_time')
    
    # Filter by search terms if present
    trip_number = request.GET.get('trip_number')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if trip_number:
        trips = trips.filter(pt_prime_trip_no__icontains=trip_number)
    if date_from:
        trips = trips.filter(pt_from_date__gte=date_from)
    if date_to:
        trips = trips.filter(pt_from_date__lte=date_to)

    # Pre-calculate allotment cumulative run
    allotment_cumulatives = {}
    for t in PrimeTripInfo.objects.all():
        allotment_id = t.pt_allotment_id
        if allotment_id not in allotment_cumulatives:
            allotment_cumulatives[allotment_id] = 0.0
        if t.pt_to_km is not None and t.pt_from_km is not None:
            allotment_cumulatives[allotment_id] += float(t.pt_to_km - t.pt_from_km)

    # Group trips by (allotment_id, date)
    grouped_data = defaultdict(list)
    for trip in trips:
        # Pre-calculate individual trip distance
        if trip.pt_to_km is not None and trip.pt_from_km is not None:
            trip.trip_distance = float(trip.pt_to_km - trip.pt_from_km)
        else:
            trip.trip_distance = None
            
        date_key = trip.pt_from_date or (trip.pt_created_at.date() if trip.pt_created_at else timezone.now().date())
        
        # Determine active vehicle, replacement reason, and vehicle source for this specific trip
        allotment = trip.pt_allotment
        vehicle_no = allotment.pva_vehiclenumber.vm_registrationnumber if allotment.pva_vehiclenumber else (allotment.pva_vehiclenumber_mkt or "-")
        vehicle_source = allotment.pva_vehiclesource_id
        replacement_reason = allotment.pva_replacement_reason
        
        # Determine trip start datetime
        trip_time = trip.pt_from_time or datetime.min.time()
        trip_dt = datetime.combine(date_key, trip_time)
        
        if allotment.pva_replacement_reason and allotment.pva_replacement_date:
            local_repl_dt = timezone.localtime(allotment.pva_replacement_date)
            repl_naive = timezone.make_naive(local_repl_dt) if timezone.is_aware(local_repl_dt) else local_repl_dt
            
            if trip_dt < repl_naive:
                # Before replacement: use original vehicle
                if allotment.pva_original_vehiclenumber:
                    vehicle_no = allotment.pva_original_vehiclenumber.vm_registrationnumber
                else:
                    vehicle_no = allotment.pva_original_vehiclenumber_mkt or "-"
                replacement_reason = None
                vehicle_source = 1  # Assume own/attached for original
        elif allotment.pva_replacement_reason:
            # Legacy fallback: compare trip date with today's date
            today_date = timezone.localtime(timezone.now()).date()
            if date_key < today_date:
                if allotment.pva_original_vehiclenumber:
                    vehicle_no = allotment.pva_original_vehiclenumber.vm_registrationnumber
                else:
                    vehicle_no = allotment.pva_original_vehiclenumber_mkt or "-"
                replacement_reason = None
                vehicle_source = 1

        # Determine color coding style for this trip's vehicle badge
        badge_style = "background: var(--bg-page); border: 1.5px solid var(--border-light); color: var(--text-main);"
        if replacement_reason:
            if 'Vehicle:' in replacement_reason:
                badge_style = "background: var(--accent-pink); color: white; border: none;"
            elif 'Driver:' in replacement_reason:
                badge_style = "background: var(--accent-orange); color: white; border: none;"
            elif 'Both:' in replacement_reason:
                badge_style = "background: var(--accent-purple); color: white; border: none;"
        else:
            if vehicle_source == 3:
                badge_style = "background: var(--accent-orange); color: white; border: none;"
            else:
                badge_style = "background: var(--accent-blue); color: white; border: none;"

        trip.active_vehicle_no = vehicle_no
        trip.active_badge_style = badge_style

        grouped_data[(trip.pt_allotment_id, date_key)].append(trip)
    
    daily_summaries = []
    for (allotment_id, date_val), day_trips in grouped_data.items():
        day_trips_sorted = sorted(day_trips, key=lambda x: x.pt_from_time or datetime.min.time())
        
        first_trip = day_trips_sorted[0]
        
        # Get unique active vehicles on this day
        vehicles_on_day = []
        seen_vehicles = set()
        for t in day_trips_sorted:
            if t.active_vehicle_no not in seen_vehicles:
                seen_vehicles.add(t.active_vehicle_no)
                vehicles_on_day.append({
                    'no': t.active_vehicle_no,
                    'style': t.active_badge_style
                })
        
        # Get start/end kms
        from_kms = [t.pt_from_km for t in day_trips if t.pt_from_km is not None]
        to_kms = [t.pt_to_km for t in day_trips if t.pt_to_km is not None]
        
        start_km = min(from_kms) if from_kms else None
        end_km = max(to_kms) if to_kms else None
        
        # If single vehicle, distance_run can be calculated by end-start, otherwise sum the trips distance
        if len(seen_vehicles) == 1:
            distance_run = (end_km - start_km) if (start_km is not None and end_km is not None) else 0.0
            range_label = f"Range: {start_km} - {end_km}" if (start_km is not None and end_km is not None) else None
        else:
            distance_run = sum(t.trip_distance for t in day_trips if t.trip_distance is not None)
            range_label = "Range: Multi-Vehicle"
        
        # Get start/end times
        from_times = [t.pt_from_time for t in day_trips if t.pt_from_time is not None]
        to_times = [t.pt_to_time for t in day_trips if t.pt_to_time is not None]
        
        start_time = min(from_times) if from_times else None
        end_time = max(to_times) if to_times else None
        
        active_hours = None
        is_outside_window = False
        if start_time and end_time:
            dt_start = datetime.combine(datetime.min, start_time)
            dt_end = datetime.combine(datetime.min, end_time)
            duration = dt_end - dt_start
            duration_hours = duration.total_seconds() / 3600.0
            active_hours = f"{duration_hours:.1f} Hrs"
            
            # Check 9AM - 9PM window (9:00 to 21:00)
            if start_time.hour < 9 or end_time.hour >= 21 or (end_time.hour == 21 and end_time.minute > 0):
                is_outside_window = True
        
        allotment = first_trip.pt_allotment

        # Fetch Agreed Monthly Km from the Booking Note
        agreed_km = allotment.pva_enquirynumber.pen_agreed_km or 0.0
            
        cum_km = allotment_cumulatives.get(allotment_id, 0.0)
        
        daily_summaries.append({
            'allotment': allotment,
            'date': date_val,
            'vehicles': vehicles_on_day,
            'range_label': range_label,
            'distance_run': distance_run,
            'active_hours': active_hours,
            'is_outside_window': is_outside_window,
            'trips_count': len(day_trips),
            'agreed_km': agreed_km,
            'cumulative_km': cum_km,
            'trips': day_trips_sorted
        })
        
    # Sort summaries by date descending
    daily_summaries = sorted(daily_summaries, key=lambda x: x['date'], reverse=True)

    context = {
        'daily_summaries': daily_summaries
    }
    return render(request, 'asset_mgt_app/prime_trip_list.html', context)
