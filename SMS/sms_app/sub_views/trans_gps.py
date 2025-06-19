from django.shortcuts import render
from django.http import JsonResponse
import xml.etree.ElementTree as ET
import requests

from ..models import TripdetailInfo

import urllib3
from django.conf import settings

if settings.DEBUG:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def track_vehicle_position(request):
    return render(request, "asset_mgt_app/trans_gps.html")


def get_vehicle_data(request):
    api_url = (
        "https://track.trackmyvehicle.in/events/data.xml"
        "?account=Bvm%20Storage%20Solutions%20Pvt%20ltd"
        "&user=apilink"
        "&password=pass@123"
        "&group=all"
        "&limit=50"
    )

    def normalize(num):
        return num.strip().upper().replace(" ", "").replace("-", "") if num else ""

    in_trip_numbers = set(map(normalize, TripdetailInfo.objects.filter(tr_approval=1).values_list('tr_vehiclenumber', flat=True)))
    available_numbers = set(map(normalize, TripdetailInfo.objects.filter(tr_approval=2).values_list('tr_vehiclenumber', flat=True)))
    workshop_number = set(map(normalize, TripdetailInfo.objects.filter(tr_approval=8).values_list('tr_vehiclenumber', flat=True)))

    vehicle_data = []
    try:
        response = requests.get(api_url, verify=False, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)

            for device in root.findall(".//Device"):
                raw_number = device.findtext("Description", "").strip()
                normalized_number = normalize(raw_number)

                event = device.find("EventData")
                if not event:
                    continue

                lat = event.findtext("GPSPoint_lat", "").strip()
                lon = event.findtext("GPSPoint_lon", "").strip()
                speed = event.findtext("Speed", "").strip()
                status_code = event.findtext("StatusCode", "").strip()
                timestamp = event.findtext("Timestamp", "").strip()

                running_status = "Stopped"
                if status_code.lower() == "moving":
                    running_status = "Moving"
                elif status_code.lower() == "idle":
                    running_status = "Idle"

                if normalized_number in in_trip_numbers:
                    trip_status = "in_trip"
                elif normalized_number in workshop_number:
                    trip_status = "workshop"
                else:
                    trip_status = "available"

                if lat and lon:
                    vehicle_data.append({
                        "number": raw_number,
                        "lat": lat,
                        "lon": lon,
                        "speed": speed,
                        "status": trip_status,
                        "running_status": running_status,
                        "timestamp": timestamp,
                    })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse(vehicle_data, safe=False)
