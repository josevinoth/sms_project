from django.shortcuts import render, redirect
from django.contrib import messages
from ..sub_models.tripdetail_mod import TripdetailInfo
from django.db.models import Q

def driver_login(request):
    if request.method == 'POST':
        mobile_no = request.POST.get('mobile_number', '').strip()
        
        if not mobile_no:
            messages.error(request, "Please enter Mobile Number.")
            return render(request, 'driver_app/driver_login.html')
        
        # Step 1: Try to find the LATEST ACTIVE trip (not closed/cancelled)
        trip = TripdetailInfo.objects.filter(
            tr_drivernumber=mobile_no
        ).exclude(
            tc_financestatus_id__in=[2, 3, 7]  # 2=Closed, 3=Cancelled, 7=Delivered
        ).order_by('-id').first()
        
        # Step 2: If no active trip, show the LATEST trip (even if closed)
        #         Only skip cancelled trips (status 3)
        if not trip:
            trip = TripdetailInfo.objects.filter(
                tr_drivernumber=mobile_no
            ).exclude(
                tc_financestatus_id=3  # Only exclude cancelled
            ).order_by('-id').first()
        
        if trip:
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
