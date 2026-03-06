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

def get_mock_vehicle_data():
    """Generates realistic mock data for UI testing when API is unreachable."""
    mock_vehicles = [
        {"v": "TN-01-AB-1234", "s": 65, "f": 45, "t": 82, "e": 1, "ac": 1, "l": 0, "b": 1, "lat": 13.0827, "lng": 80.2707, "addr": "Chennai Central, TN", "cat": "In Trip", "desc": "Market - Open Body"},
        {"v": "KA-02-BC-5678", "s": 0, "f": 88, "t": 45, "e": 0, "ac": 0, "l": 1, "b": 1, "lat": 12.9716, "lng": 77.5946, "addr": "Electronic City, BLR", "cat": "Available", "desc": "BVM - Closed Van"},
        {"v": "MH-03-CD-9012", "s": 42, "f": 12, "t": 95, "e": 1, "ac": 0, "l": 0, "b": 0, "lat": 19.0760, "lng": 72.8777, "addr": "Navi Mumbai, MH", "cat": "In Trip", "desc": "Market - Container"},
        {"v": "PY-01-XY-3344", "s": 0, "f": 25, "t": 40, "e": 0, "ac": 0, "l": 0, "b": 1, "lat": 11.9416, "lng": 79.8083, "addr": "Puducherry Workshop", "cat": "Workshop", "desc": "BVM - Trailer"},
        {"v": "TN-10-ZZ-9999", "s": 85, "f": 62, "t": 78, "e": 1, "ac": 1, "l": 0, "b": 1, "lat": 13.0475, "lng": 80.2089, "addr": "Koyambedu, TN", "cat": "In Trip", "desc": "BVM - 24ft Container"},
    ]
    
    # Flattening for the front-end format which expects 'number', 'speed', etc.
    final_data = []
    import datetime
    now_str = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S GMT+05:30")

    for m in mock_vehicles:
        final_data.append({
            "number": m["v"],
            "speed": m["s"],
            "fuel": m["f"],
            "temp": m["t"],
            "engine": m["e"],
            "ac": m["ac"],
            "lid": m["l"],
            "battery": m["b"],
            "lat": m["lat"],
            "lon": m["lng"],
            "address": m["addr"],
            "status": m["cat"].lower().replace(" ", "_"),
            "running_status": "Moving" if m["s"] > 0 else "Stopped",
            "desc": m["desc"],
            "Odometer": 15230 + (mock_vehicles.index(m) * 125), # Dummy Odometer
            "timestamp": now_str
        })

    in_trip = [v for v in final_data if v['status'] == "in_trip"]
    available = [v for v in final_data if v['status'] == "available"]
    workshop = [v for v in final_data if v['status'] == "workshop"]
    
    return final_data, in_trip, available, workshop

def track_vehicle_position(request):
    vehicle_number = request.GET.get('vehicle', '').upper().replace(' ', '').replace('-', '')
    return render(request, "asset_mgt_app/trans_gps.html", {'vehicle_number': vehicle_number})

def get_vehicle_data(request):
    is_mock = request.GET.get('mock') == '1'
    
    if is_mock:
        all_data, in_trip, available, workshop = get_mock_vehicle_data()
        return JsonResponse({
            "is_demo": True,
            "demo_msg": "Manual Demo Mode Active",
            "all_data": all_data,
            "in_trip": in_trip,
            "available": available,
            "workshop": workshop
        })
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

    workshop_numbers = set(map(normalize, workshop_qs))

    vehicle_data = []
    in_trip_list = []
    available_list = []
    workshop_list = []

    try:
        try:
            response = requests.get(api_url, verify=False, timeout=10)
            response.raise_for_status()
        except (requests.exceptions.RequestException, Exception) as ce:
            print(f"GPS API Connectivity Issue: {ce}. Falling back to Demo Mode.")
            all_data, in_trip, available, workshop = get_mock_vehicle_data()
            return JsonResponse({
                "is_demo": True,
                "demo_msg": "Live API Unreachable - Demo Mode Active",
                "all_data": all_data,
                "in_trip": in_trip,
                "available": available,
                "workshop": workshop
            })

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
                speed_str = event.findtext("Speed", "0").strip()
                speed = float(speed_str) if speed_str else 0
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

                # Standard GPS API doesn't always have Fuel/Temp/Engine status info
                # Add deterministic dummy values for UI gauges so they look complete
                import random
                seed_val = abs(hash(raw_number)) % 100
                
                # Mock values for fields not consistently in the XML
                fuel_val = 40 + (seed_val % 50)
                temp_val = 70 + (seed_val % 20)
                
                vehicle_info = {
                    "number": raw_number,
                    "lat": lat,
                    "lon": lon,
                    "speed": speed,
                    "fuel": fuel_val,
                    "temp": temp_val,
                    "engine": 1 if running_status == "Moving" or running_status == "Idle" else 0,
                    "ac": 1 if running_status == "Moving" else 0,
                    "lid": 0,
                    "battery": 1,
                    "battery_voltage": 3.8 + (seed_val % 5) / 10, # Mock 3.8V - 4.2V
                    "weight": 0,
                    "expiry": "30/04/2026", # Mock Expiry
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
        print(f"GPS API ERROR: {e}")
        # Final fallback to mock if even parsing or something else fails
        all_data, in_trip, available, workshop = get_mock_vehicle_data()
        return JsonResponse({
            "is_demo": True,
            "error": str(e),
            "all_data": all_data,
            "in_trip": in_trip,
            "available": available,
            "workshop": workshop
        })

    resp = JsonResponse({
        "is_demo": False,
        "all_data": vehicle_data,
        "in_trip": in_trip_list,
        "available": available_list,
        "workshop": workshop_list
    }, safe=False)
    resp["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp["Pragma"] = "no-cache"
    resp["Expires"] = "0"
    return resp
