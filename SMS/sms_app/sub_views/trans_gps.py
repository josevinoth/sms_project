from django.shortcuts import render
from django.http import JsonResponse
import xml.etree.ElementTree as ET
import requests

from ..models import TripdetailInfo, Tripstatusinfo
from django.db.models import Q

import urllib3
from django.conf import settings

if settings.DEBUG:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def track_vehicle_position(request):
    vehicle_number = request.GET.get('vehicle', '').upper().replace(' ', '').replace('-', '')
    return render(request, "asset_mgt_app/trans_gps.html", {'vehicle_number': vehicle_number})

def get_vehicle_data(request):
    api_url = (
        "https://track.trackmyvehicle.in/events/data.xml"
        "?account=Bvm%20Storage%20Solutions%20Pvt%20ltd"
        "&user=apilink"
        "&password=pass@123"
        "&group=all"
        "&limit=1"
    )

    def normalize(num):
        return num.strip().upper().replace(" ", "").replace("-", "") if num else ""

    # Fetch status IDs dynamically to be robust
    in_trip_status_ids = list(Tripstatusinfo.objects.filter(
        status__in=['Trip Started', 'Open', 'Started', 'Loading Reported', 'Unloading Reported']
    ).values_list('id', flat=True))
    
    workshop_status_ids = list(Tripstatusinfo.objects.filter(
        status__in=['Workshop', 'Maintenance']
    ).values_list('id', flat=True))

    # Vehicles are "In Trip" if they have an active trip status OR if approved (legacy check)
    in_trip_qs = TripdetailInfo.objects.filter(
        Q(tc_financestatus__in=in_trip_status_ids) | Q(tr_approval=1)
    ).values_list('tr_vehiclenumber', flat=True)
    in_trip_numbers = set(map(normalize, in_trip_qs))

    # Vehicles are "Workshop" if status is Workshop OR legacy approval=8
    workshop_qs = TripdetailInfo.objects.filter(
        Q(tc_financestatus__in=workshop_status_ids) | Q(tr_approval=8)
    ).values_list('tr_vehiclenumber', flat=True)
    workshop_numbers = set(map(normalize, workshop_qs))
    
    # Available is the default, so we don't strictly need a set for it if logic is else-if, 
    # but we can fetch legacy available just in case.
    # available_numbers = set(map(normalize, TripdetailInfo.objects.filter(tr_approval=2).values_list('tr_vehiclenumber', flat=True)))

    vehicle_data = []
    in_trip_list = []
    available_list = []
    workshop_list = []

    try:
        response = requests.get(api_url, verify=False, timeout=15)
        if response.status_code == 200:
            root = ET.fromstring(response.content)

            for device in root.findall(".//Device"):
                raw_number = device.findtext("Description", "").strip()
                normalized_number = normalize(raw_number)

                # Get the LAST EventData element (most recent)
                events = device.findall("EventData")
                if not events:
                    continue
                event = events[-1]

                lat = event.findtext("GPSPoint_lat", "").strip()
                lon = event.findtext("GPSPoint_lon", "").strip()
                speed = event.findtext("Speed", "").strip()
                Odometer = event.findtext("Odometer", "").strip()
                status_code = event.findtext("StatusCode", "").strip()
                timestamp = event.findtext("Timestamp", "").strip()
                address = event.findtext("Address", "").strip()

                running_status = "Stopped"
                status_lower = status_code.lower()
                if status_lower == "moving":
                    running_status = "Moving"
                elif status_lower == "idle":
                    running_status = "Idle"
                elif status_lower in ("stop", "stopped"):
                    running_status = "Stopped"
                elif status_lower == "arrive":
                    running_status = "Stopped"
                elif status_lower == "depart":
                    running_status = "Moving"

                if normalized_number in in_trip_numbers:
                    trip_status = "in_trip"
                elif normalized_number in workshop_numbers:
                    trip_status = "workshop"
                else:
                    trip_status = "available"

                vehicle_info = {
                    "number": raw_number,
                    "lat": lat,
                    "lon": lon,
                    "speed": speed,
                    "Odometer": Odometer,
                    "status": trip_status,
                    "running_status": running_status,
                    "timestamp": timestamp,
                    "address": address,
                }

                vehicle_data.append(vehicle_info)

                # Categorize into separate lists
                if trip_status == "in_trip":
                    in_trip_list.append(vehicle_info)
                elif trip_status == "available":
                    available_list.append(vehicle_info)
                elif trip_status == "workshop":
                    workshop_list.append(vehicle_info)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    resp = JsonResponse({
        "all_data": vehicle_data,
        "in_trip": in_trip_list,
        "available": available_list,
        "workshop": workshop_list
    }, safe=False)
    resp["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp["Pragma"] = "no-cache"
    resp["Expires"] = "0"
    return resp
