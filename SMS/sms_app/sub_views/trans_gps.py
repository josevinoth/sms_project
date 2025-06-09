import xml.etree.ElementTree as ET
import requests
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def track_vehicle_position(request):
    # The TrackMyVehicle XML endpoint (account/user/password/group/limit in query params)
    api_url = (
        "https://track.trackmyvehicle.in/events/data.xml"
        "?account=Bvm%20Storage%20Solutions%20Pvt%20ltd"
        "&user=apilink"
        "&password=pass@123"
        "&group=all"
        "&limit=50"
    )

    vehicle_data = []
    selected_data = None
    selected_number = request.POST.get("vehicle_number") if request.method == "POST" else None

    try:
        response = requests.get(api_url, verify=False, timeout=10)
        if response.status_code == 200:
            root = ET.fromstring(response.content)

            # Iterate over each <Device> in the XML
            for device in root.findall(".//Device"):
                number = device.findtext("Description", "").strip()
                event = device.find("EventData")
                if event is not None:
                    lat = event.findtext("GPSPoint_lat", "").strip()
                    lon = event.findtext("GPSPoint_lon", "").strip()
                    speed = event.findtext("Speed", "").strip()
                    status = event.findtext("StatusCode", "").strip()
                    timestamp = event.findtext("Timestamp", "").strip()

                    # Only include this device if it actually has lat/lon
                    if lat and lon:
                        data = {
                            "number": number,
                            "lat": lat,
                            "lon": lon,
                            "speed": speed,
                            "status": status,
                            "timestamp": timestamp,
                        }
                        vehicle_data.append(data)

                        # If this device matches the vehicle_number submitted, save it
                        if selected_number and number == selected_number:
                            selected_data = data

    except Exception as e:
        # If anything goes wrong (network/XML parsing), render template with an "error" context
        return render(
            request,
            "asset_mgt_app/trans_gps.html",
            {"error": str(e), "vehicle_data": vehicle_data},
        )

    return render(
        request,
        "asset_mgt_app/trans_gps.html",
        {
            "vehicle_data": vehicle_data,
            "selected_data": selected_data,
            "selected_number": selected_number,
        },
    )
