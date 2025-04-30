import xml.etree.ElementTree as ET

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
import requests
import certifi

@login_required(login_url='login_page')
def get_vehicle_position(request, vehicle_number):
    print(f"Requesting position for vehicle: {vehicle_number}")  # Debugging line

    url = "https://track.trackmyvehicle.in/events/data.xml"
    params = {
        'account': 'Bvm Storage Solutions Pvt ltd',
        'user': 'apilink',
        'password': 'pass@123',
        'vehicle': vehicle_number,  # Pass the vehicle number
        'limit': 1
    }

    try:
        response = requests.get(url, params=params, verify=False)

        print(f"Response Status Code: {response.status_code}")  # Debugging line
        print(f"Response Content: {response.content.decode('utf-8')}")  # Debugging line

        if response.status_code == 200:
            root = ET.fromstring(response.content)
            vehicle_data = []

            for child in root.findall(".//event"):
                vehicle_info = {
                    'latitude': child.find('latitude').text if child.find('latitude') is not None else '',
                    'longitude': child.find('longitude').text if child.find('longitude') is not None else '',
                    'speed': child.find('speed').text if child.find('speed') is not None else '',
                    'timestamp': child.find('timestamp').text if child.find('timestamp') is not None else '',
                }
                vehicle_data.append(vehicle_info)

            return render(request, 'asset_mgt_app/trans_gps.html', {'vehicle_data': vehicle_data})

        else:
            return render(request, 'error.html', {'error_message': 'Failed to retrieve data from the API'})

    except requests.exceptions.SSLError as e:
        return HttpResponse(f"SSL Error: {str(e)}", status=500)
    except Exception as e:
        return HttpResponse(f"Unexpected Error: {str(e)}", status=500)