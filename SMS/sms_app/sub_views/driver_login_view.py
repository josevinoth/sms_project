from django.shortcuts import render, redirect
from django.contrib import messages
from ..sub_models.tripdetail_mod import TripdetailInfo
from django.db.models import Q

def driver_login(request):
    if request.method == 'POST':
        # ── Clear any stale session from a previous driver ──
        # The WebView app shares one session, so an old driver_trip_id
        # would persist and show the wrong vehicle for a new phone number.
        if 'driver_trip_id' in request.session:
            del request.session['driver_trip_id']

        mobile_no = request.POST.get('mobile_number', '').strip()
        
        if not mobile_no:
            messages.error(request, "Please enter Mobile Number.")
            return render(request, 'driver_app/driver_login.html')
        
        # Step 1: Find the LATEST trip for this mobile number
        trip = TripdetailInfo.objects.filter(
            tr_drivernumber=mobile_no
        ).order_by('-id').first()
        
        if trip:
            # Step 2: Check if the latest trip is active.
            # If it's Closed (2), Cancelled (3), or Delivered (7), do not show it.
            if trip.tc_financestatus_id in [2, 3, 7]:
                messages.error(request, "No active trip found (The latest trip is already closed).")
                return render(request, 'driver_app/driver_login.html')
            
            # Success: Log in to the latest active trip
            request.session['driver_trip_id'] = trip.id
            return redirect('driver_dashboard')
        else:
            messages.error(request, "No trip found for this mobile number.")
            return render(request, 'driver_app/driver_login.html')
            
    return render(request, 'driver_app/driver_login.html')

def driver_logout(request):
    if 'driver_trip_id' in request.session:
        del request.session['driver_trip_id']
    return redirect('driver_login')
