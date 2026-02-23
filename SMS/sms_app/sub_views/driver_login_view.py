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
            
        # Find active trip matching credentials
        trip = TripdetailInfo.objects.filter(
            tr_drivernumber=mobile_no
        ).exclude(
            tc_financestatus_id__in=[2, 3, 7] # Assuming 2=Closed, 3=Cancelled, 7=Delivered(Closed)
        ).order_by('-id').first()
        
        if trip:
            # Login successful
            request.session['driver_trip_id'] = trip.id
            return redirect('driver_dashboard')
        else:
            messages.error(request, "No active trip found for these details.")
            return render(request, 'driver_app/driver_login.html')
            
    return render(request, 'driver_app/driver_login.html')

def driver_logout(request):
    if 'driver_trip_id' in request.session:
        del request.session['driver_trip_id']
    return redirect('driver_login')
