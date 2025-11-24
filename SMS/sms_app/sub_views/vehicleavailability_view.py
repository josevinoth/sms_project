from django.utils.timezone import now
from django.shortcuts import render
from ..models import VehiclemasterInfo, TripdetailInfo

def vehicle_availability_list(request):
    vehicles = VehiclemasterInfo.objects.all()
    vehicle_data = []

    AVAILABLE_STATUS_IDS = [2, 3, 4, 6, 7]   # <-- new rule

    for vehicle in vehicles:

        latest_trip = TripdetailInfo.objects.filter(
            tr_vehiclenumber=vehicle.vm_registrationnumber
        ).order_by('-tr_created_at').first()

        availability = "No"
        trip_status = "No Trip Data"
        location = "N/A"
        date_time = "N/A"

        if latest_trip:
            status_id = latest_trip.tc_financestatus.id if latest_trip.tc_financestatus else None

            # 🔥 Check availability by status list
            if status_id in AVAILABLE_STATUS_IDS:
                availability = "Yes"
            else:
                availability = "No"

            trip_status = latest_trip.tc_financestatus.status if latest_trip.tc_financestatus else "Unknown"
            location = latest_trip.tr_reportedlocation.place_name if latest_trip.tr_reportedlocation else "N/A"
            date_time = latest_trip.tr_reporteddate if latest_trip.tr_reporteddate else "N/A"

        vehicle_data.append({
            'vehicle_number': vehicle.vm_registrationnumber,
            'vehicle_type': vehicle.vm_vehicletype,
            'manufacturer': vehicle.vm_vehiclemanufacturer,
            'model': vehicle.vm_vehiclemodel,
            'ownership': vehicle.vm_ownership,
            'location': location,
            'date_time': date_time,
            'trip_status': trip_status,
            'availability': availability,
        })

    return render(request, 'asset_mgt_app/vehicleavailability_list.html', {'vehicle_data': vehicle_data})
