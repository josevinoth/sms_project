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

    # Only redirect for cancelled trips (status 3)
    if trip.tc_financestatus_id == 3:
        messages.info(request, "This trip has been cancelled.")
        del request.session['driver_trip_id']
        return redirect('driver_login')

    # Flag for closed trips (read-only mode)
    is_closed = trip.tc_financestatus_id in [2, 7]

    if request.method == 'POST':
        action = request.POST.get('action')
        raw_km = request.POST.get('hidden_km', '')

        # ===== DEBUG: Print everything received from driver form =====
        print("=" * 60)
        print("DRIVER DASHBOARD POST DATA:")
        print(f"  Action: '{action}'")
        print(f"  Raw KM: '{raw_km}'")
        print(f"  All POST keys: {list(request.POST.keys())}")
        print(f"  Trip ID: {trip.id} | Trip#: {trip.tr_tripnumber}")
        print("=" * 60)

        # Clean KM value (remove commas, spaces)
        km_value = raw_km.strip().replace(',', '').replace(' ', '') if raw_km else ''

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

        # 0. Vehicle Reported (At Origin) -> tr_departeddate_pickup & tr_reportedkm_pickup
        if action == 'vehicle_reported':
            if not trip.tr_departeddate_pickup:
                if km_value and km_value.isdigit():
                    val_km = int(km_value)
                    # No previous trip KM to check against here usually, but let's be safe
                    trip.tr_departedkm = val_km
                    print(f"  >> SAVED tr_departedkm = {val_km}")
                else:
                    print(f"  >> KM NOT SAVED (invalid: '{km_value}')")
                trip.tr_departeddate_pickup = timezone.now()
                trip.save()
                messages.success(request, f"Vehicle Reported Time & KM: {km_value or 'N/A'}")
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

        # 3. Vehicle Started (Departing Origin) -> tr_departeddate & tr_departedkm
        elif action == 'vehicle_started':
            if not trip.tr_departeddate:
                if km_value and km_value.isdigit():
                    val_km = int(km_value)
                    prev_km = trip.tr_departedkm or 0
                    if val_km < prev_km:
                        messages.error(request, f"KM Reading ({val_km}) cannot be less than previous reading ({prev_km}).")
                        return redirect('driver_dashboard')
                    trip.tr_reportedkm_pickup = val_km
                    print(f"  >> SAVED tr_reportedkm_pickup = {val_km}")
                else:
                    print(f"  >> KM NOT SAVED (invalid: '{km_value}')")
                trip.tr_departeddate = timezone.now()
                trip.save()
                messages.success(request, f"Vehicle Started Time & KM: {km_value or 'N/A'}")
                trigger_alert(trip_send_trip_started_mail, "Trip Started")

        # 4. Vehicle Reported (At Destination/Unloading) -> tr_reporteddate & tr_reportedkm
        elif action == 'vehicle_reported_unloading':
            if not trip.tr_reporteddate:
                if km_value and km_value.isdigit():
                    val_km = int(km_value)
                    prev_km = trip.tr_reportedkm_pickup or trip.tr_departedkm or 0
                    if val_km < prev_km:
                        messages.error(request, f"KM Reading ({val_km}) cannot be less than previous reading ({prev_km}).")
                        return redirect('driver_dashboard')
                    trip.tr_reportedkm = val_km
                    print(f"  >> SAVED tr_reportedkm = {val_km}")
                else:
                    print(f"  >> KM NOT SAVED (invalid: '{km_value}')")
                trip.tr_reporteddate = timezone.now()
                trip.save()
                messages.success(request, f"Vehicle Arrived & KM: {km_value or 'N/A'}")
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

        # 7. Vehicle Started (Return/Trip Close) -> tr_reporteddate_delivery & tr_reportedkm_delivery
        elif action == 'vehicle_started_unloading':
            if not trip.tr_reporteddate_delivery:
                if km_value and km_value.isdigit():
                    val_km = int(km_value)
                    prev_km = trip.tr_reportedkm or trip.tr_reportedkm_pickup or 0
                    if val_km < prev_km:
                        messages.error(request, f"KM Reading ({val_km}) cannot be less than previous reading ({prev_km}).")
                        return redirect('driver_dashboard')
                    trip.tr_reportedkm_delivery = val_km
                    print(f"  >> SAVED tr_reportedkm_delivery = {val_km}")
                else:
                    print(f"  >> KM NOT SAVED (invalid: '{km_value}')")
                now = timezone.now()
                trip.tr_reporteddate_delivery = now
                trip.tr_reporteddate_pickup = now  # Also save for admin display
                trip.save()
                messages.success(request, f"Vehicle Released & KM: {km_value or 'N/A'}")
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

    return render(request, 'driver_app/driver_dashboard.html', {'trip': trip, 'is_closed': is_closed})
