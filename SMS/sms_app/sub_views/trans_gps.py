import xml.etree.ElementTree as ET
import requests
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def track_vehicle_position(request):
    api_url = (
        "https://track.trackmyvehicle.in/events/data.xml"
        "?account=Bvm%20Storage%20Solutions%20Pvt%20ltd"
        "&user=apilink"
        "&password=pass@123"
        "&group=all"
        "&limit=50"
    )

    try:
        response = requests.get(api_url, verify=False)
        vehicle_data = []

        if response.status_code == 200:
            root = ET.fromstring(response.content)

            for device in root.findall(".//Device"):
                number = device.findtext("Description", "").strip()
                event = device.find("EventData")
                if event is not None:
                    lat = event.findtext("GPSPoint_lat")
                    lon = event.findtext("GPSPoint_lon")
                    speed = event.findtext("Speed")
                    status = event.findtext("StatusCode")
                    timestamp = event.findtext("Timestamp")

                    if lat and lon:
                        vehicle_data.append({
                            'number': number,
                            'lat': lat,
                            'lon': lon,
                            'speed': speed,
                            'status': status,
                            'timestamp': timestamp
                        })

        return render(request, "asset_mgt_app/trans_gps.html", {"vehicle_data": vehicle_data})

    except Exception as e:
        return render(request, "asset_mgt_app/trans_gps.html", {"error": str(e)})
