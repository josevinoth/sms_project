from django.utils.timezone import now, timedelta
from django.shortcuts import render
from ..models import VehiclemasterInfo, TripdetailInfo

def vehicle_availability_list(request):
    vehicles = VehiclemasterInfo.objects.all()
    vehicle_data = []

    for vehicle in vehicles:
        # Get the most recent trip where the vehicle was closed
        latest_closed_trip = TripdetailInfo.objects.filter(
            tr_vehiclenumber=vehicle,
            tc_financestatus__id=2  # Assuming status ID 2 means "Closed"
        ).order_by('-tr_reporteddate').first()

        trip_status = "No Trip Data"
        availability = "Yes"
        location = "N/A"
        date_time = "N/A"

        if latest_closed_trip:
            trip_status = latest_closed_trip.tc_financestatus.status
            location = latest_closed_trip.tr_reportedlocation.place_name if latest_closed_trip.tr_reportedlocation else "N/A"
            date_time = latest_closed_trip.tr_reporteddate


            if latest_closed_trip.tr_reporteddate:

                if latest_closed_trip.tr_reporteddate.date() < now().date():
                    availability = "No"
                else:
                    availability = "Yes"
            else:
                availability = "No"

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
