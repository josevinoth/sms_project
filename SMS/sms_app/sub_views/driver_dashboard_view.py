from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from ..sub_models.tripdetail_mod import TripdetailInfo
from .tripdetail_add_view import (
    trip_send_loading_report_mail, 
    trip_send_trip_started_mail, 
    trip_send_unloading_report_mail,
    trip_send_trip_closed_mail,
    get_auto_recipients
)
import json

def driver_dashboard(request):
    trip_id = request.session.get('driver_trip_id')
    if not trip_id:
        return redirect('driver_login')
    
    trip = get_object_or_404(TripdetailInfo, id=trip_id)
    
    # Check if trip is closed/cancelled
    # status 2=Closed, 3=Cancelled, 7=Delivered(Closed)
    if trip.tc_financestatus_id in [2, 3, 7]: 
         messages.info(request, "This trip is completed/closed.")
         del request.session['driver_trip_id']
         return redirect('driver_login')

    if request.method == 'POST':
        action = request.POST.get('action')
        
        # Helper to Trigger Alerts
        def trigger_alert(alert_func, label):
            # Only send for Category 1 (Normal Trips)
            if trip.tr_category_id != 1:
                return

            try:
                request.session['ses_tripdetail_id'] = trip.id
                
                # Fetch recipients
                recipients = get_auto_recipients(trip)
                
                if not recipients:
                    # Silent warning or log
                    print(f"Alert Skipped: {label} - No recipients found.")
                    return

                response = alert_func(request)
                
                # Parse Response
                try:
                    data = json.loads(response.content.decode('utf-8'))
                    if data.get('success'):
                        messages.info(request, f"✓ Email Alert Sent: {label}")
                    else:
                        print(f"Alert skipped: {label} ({data.get('msg')})")
                except:
                    messages.info(request, f"✓ Email Alert Sent: {label}")
            except Exception as e:
                print(f"Alert trigger error ({label}): {e}")

        # 0. Vehicle Reported (At Origin) -> tr_departeddate_pickup
        if action == 'vehicle_reported':
            if not trip.tr_departeddate_pickup:
                trip.tr_departeddate_pickup = timezone.now()
                trip.save()
                messages.success(request, "Vehicle Reported Time Recorded!")
                trigger_alert(trip_send_loading_report_mail, "Loading Reported")

        # 1. Loading Dock In
        elif action == 'loading_dock_in':
            if not trip.tr_loading_time:
                trip.tr_loading_time = timezone.now()
                trip.save()
                messages.success(request, "Loading Dock In Reported!")
                
        # 2. Loading Dock Out (Mapped to tr_dock_in_time)
        elif action == 'loading_dock_out':
            if not trip.tr_dock_in_time: 
                trip.tr_dock_in_time = timezone.now()
                trip.save()
                messages.success(request, "Loading Dock Out Reported!")

        # 3. Vehicle Started (Departing Origin) -> tr_departeddate
        elif action == 'vehicle_started':
            if not trip.tr_departeddate:
                trip.tr_departeddate = timezone.now()
                trip.save()
                messages.success(request, "Vehicle Started Time Recorded!")
                trigger_alert(trip_send_trip_started_mail, "Trip Started")

        # 4. Vehicle Reported (At Destination/Unloading) -> tr_reporteddate
        elif action == 'vehicle_reported_unloading':
            if not trip.tr_reporteddate:
                trip.tr_reporteddate = timezone.now()
                trip.save()
                messages.success(request, "Vehicle Arrival at Destination Recorded!")
                trigger_alert(trip_send_unloading_report_mail, "Unloading Reported")

        # 5. Unloading Dock In (Mapped to tr_departeddate_delivery)
        elif action == 'unloading_dock_in':
            if not trip.tr_departeddate_delivery: 
                trip.tr_departeddate_delivery = timezone.now()
                trip.save()
                messages.success(request, "Unloading Dock In Reported!")

        # 6. Unloading Dock Out (Mapped to tr_unloading_time)
        elif action == 'unloading_dock_out':
            if not trip.tr_unloading_time: 
                trip.tr_unloading_time = timezone.now()
                trip.save()
                messages.success(request, "Unloading Dock Out Reported!")

        # 7. Vehicle Started (Return/Trip Close) -> tr_reporteddate_delivery
        elif action == 'vehicle_started_unloading':
            if not trip.tr_reporteddate_delivery:
                trip.tr_reporteddate_delivery = timezone.now()
                trip.save()
                messages.success(request, "Vehicle Released/Started from Destination!")
                trigger_alert(trip_send_trip_closed_mail, "Trip Closed")

        # 8. POD Upload
        elif action == 'upload_pod':
            if 'pod_file' in request.FILES:
                trip.tc_pod_attachment = request.FILES['pod_file']
                trip.save()
                messages.success(request, "POD Uploaded Successfully!")
            else:
                messages.error(request, "No file selected for POD.")
                
        # 7. Logout
        elif action == 'logout':
            del request.session['driver_trip_id']
            return redirect('driver_login')

        return redirect('driver_dashboard')

    return render(request, 'driver_app/driver_dashboard.html', {'trip': trip})
