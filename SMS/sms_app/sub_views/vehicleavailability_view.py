from django.utils.timezone import now
from django.shortcuts import render
from ..models import VehiclemasterInfo, TripdetailInfo, Vehicle_allotmentInfo, EnquirynoteInfo

def vehicle_availability_list(request):
    vehicles = VehiclemasterInfo.objects.all().select_related('vm_vehicletype', 'vm_vehiclemanufacturer', 'vm_vehiclemodel', 'vm_ownership')
    vehicle_data = []

    # Statuses where trip is completed / settled / cancelled
    COMPLETED_STATUS_IDS = [2, 3, 4, 5, 6, 7, 9, 10]

    total_count = 0
    available_count = 0
    busy_count = 0
    allotted_count = 0

    for vehicle in vehicles:
        reg_num = vehicle.vm_registrationnumber
        
        # Latest trip across all enquiries
        latest_trip = TripdetailInfo.objects.filter(
            tr_vehiclenumber=reg_num
        ).order_by('-tr_created_at', '-id').first()

        # Find latest allotment for this vehicle
        latest_allotment = Vehicle_allotmentInfo.objects.filter(
            va_vehiclenumber=vehicle
        ).order_by('-id').first()

        availability = "Yes"
        badge_class = "success"
        trip_status = "Available (No Trip Data)"
        location = "N/A"
        date_time = "N/A"

        if latest_trip:
            status_id = latest_trip.tc_financestatus.id if latest_trip.tc_financestatus else None
            trip_status = latest_trip.tc_financestatus.status if latest_trip.tc_financestatus else "Unknown"
            location = latest_trip.tr_reportedlocation.place_name if latest_trip.tr_reportedlocation else "N/A"
            date_time = latest_trip.tr_reporteddate if latest_trip.tr_reporteddate else "N/A"

            if status_id in COMPLETED_STATUS_IDS:
                # Latest trip is finished/closed/settled.
                # Check if vehicle has been ALLOTTED to a newer enquiry where trip hasn't started yet!
                if latest_allotment and latest_allotment.va_enquirynumber_id != latest_trip.tr_enquirynumber_id:
                    # Verify if this newer enquiry's trip is NOT completed
                    newer_trip = TripdetailInfo.objects.filter(
                        tr_enquirynumber=latest_allotment.va_enquirynumber,
                        tr_vehiclenumber=reg_num
                    ).first()
                    
                    if not newer_trip or (newer_trip.tc_financestatus_id not in COMPLETED_STATUS_IDS):
                        availability = "Allotted"
                        badge_class = "warning"
                        trip_status = f"Allotted ({latest_allotment.va_enquirynumber.en_enquirynumber})"
                        allotted_count += 1
                    else:
                        availability = "Yes"
                        badge_class = "success"
                        available_count += 1
                else:
                    availability = "Yes"
                    badge_class = "success"
                    available_count += 1
            else:
                # Trip is currently ACTIVE (e.g. Trip Started, Awaiting Trip Approval, etc.)
                availability = "No"
                badge_class = "danger"
                busy_count += 1
        else:
            # No trip history exists yet
            if latest_allotment:
                availability = "Allotted"
                badge_class = "warning"
                trip_status = f"Allotted ({latest_allotment.va_enquirynumber.en_enquirynumber})"
                allotted_count += 1
            else:
                availability = "Yes"
                badge_class = "success"
                trip_status = "Available"
                available_count += 1

        total_count += 1

        vehicle_data.append({
            'vehicle_number': reg_num,
            'vehicle_type': vehicle.vm_vehicletype,
            'manufacturer': vehicle.vm_vehiclemanufacturer,
            'model': vehicle.vm_vehiclemodel,
            'ownership': vehicle.vm_ownership,
            'location': location,
            'date_time': date_time,
            'trip_status': trip_status,
            'availability': availability,
            'badge_class': badge_class,
        })

    context = {
        'vehicle_data': vehicle_data,
        'total_count': total_count,
        'available_count': available_count,
        'busy_count': busy_count,
        'allotted_count': allotted_count,
    }

    return render(request, 'asset_mgt_app/vehicleavailability_list.html', context)
