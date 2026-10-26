from django.shortcuts import render, redirect
from django.contrib import messages
from ..sub_models.tripdetail_mod import TripdetailInfo
from django.db.models import Q
import os
from django.conf import settings
from datetime import date
from django.http import FileResponse, Http404

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
        
        # Step 1: Find the LATEST ACTIVE Business trip (Category 1) for this mobile number
        # Drivers should ONLY see trips that are actively ongoing:
        # 12: Work In Progress (or None), 8: Awaiting Trip Approval, 1: Trip Started
        active_trip = TripdetailInfo.objects.filter(
            tr_drivernumber=mobile_no,
            tr_category_id=1
        ).filter(
            Q(tc_financestatus_id__in=[1, 8, 12]) | Q(tc_financestatus__isnull=True)
        ).order_by('-id').first()

        if active_trip:
            # Success: Log in to the active trip
            request.session['driver_trip_id'] = active_trip.id
            return redirect('driver_dashboard')

        # Step 2: If no active trip, check if any completed/settlement/closed trip exists
        past_trip = TripdetailInfo.objects.filter(
            tr_drivernumber=mobile_no,
            tr_category_id=1
        ).order_by('-id').first()

        if past_trip:
            messages.error(request, "No active trip found (The latest trip is already closed).")
            return render(request, 'driver_app/driver_login.html')
        else:
            messages.error(request, "No active trip found for this mobile number.")
            return render(request, 'driver_app/driver_login.html')
            
    return render(request, 'driver_app/driver_login.html')

def driver_logout(request):
    if 'driver_trip_id' in request.session:
        del request.session['driver_trip_id']
    return redirect('driver_login')


def driver_download_app(request):
    """Public page for drivers to download the BVM Driver APK."""
    apk_path = os.path.join(settings.MEDIA_ROOT, 'apk', 'BVM_Driver.apk')
    file_size = "—"
    updated_on = "—"
    version = "1.1"

    if os.path.exists(apk_path):
        size_bytes = os.path.getsize(apk_path)
        size_mb = round(size_bytes / (1024 * 1024), 1)
        file_size = f"{size_mb} MB"
        mtime = os.path.getmtime(apk_path)
        from datetime import datetime
        updated_on = datetime.fromtimestamp(mtime).strftime("%d %b %Y")

    context = {
        'version': version,
        'file_size': file_size,
        'updated_on': updated_on,
        'year': date.today().year,
    }
    return render(request, 'driver_app/download_app.html', context)


def driver_download_apk_file(request):
    """Direct APK file download endpoint with proper MIME type and binary streaming."""
    apk_path = os.path.join(settings.MEDIA_ROOT, 'apk', 'BVM_Driver.apk')
    if not os.path.exists(apk_path):
        # Fallback check
        alt_path = os.path.join(settings.BASE_DIR, 'media', 'apk', 'BVM_Driver.apk')
        if os.path.exists(alt_path):
            apk_path = alt_path
        else:
            raise Http404("APK file not found on server.")

    response = FileResponse(open(apk_path, 'rb'), content_type='application/vnd.android.package-archive')
    response['Content-Disposition'] = 'attachment; filename="BVM_Driver.apk"'
    response['Content-Length'] = os.path.getsize(apk_path)
    return response

