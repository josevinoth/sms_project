from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Sum, Q

from ..sub_forms.attached_bill_form import AttachedBillForm
from ..sub_models.attached_bill_mod import AttachedBillInfo
from ..sub_models.vehiclemaster_mod import VehiclemasterInfo
from ..sub_models.tripdetail_mod import TripdetailInfo


# ==================================================
# ADD ATTACHED BILL
# ==================================================
@login_required(login_url='login_page')
def attached_bill_add(request):
    if request.method == "POST":
        form = AttachedBillForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.ab_created_by = request.user
            obj.save()
            messages.success(request, "Attached Bill saved successfully.")
            return redirect('attached_bill_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AttachedBillForm()

    return render(
        request,
        "asset_mgt_app/attached_bill_add.html",
        {
            "form": form,
            "title": "Add Attached Bill"
        }
    )


# ==================================================
# LIST ATTACHED BILLS
# ==================================================
@login_required(login_url='login_page')
def attached_bill_list(request):
    bills = AttachedBillInfo.objects.all().order_by('-ab_created_at')
    return render(
        request,
        "asset_mgt_app/attached_bill_list.html",
        {
            "bills": bills
        }
    )


# ==================================================
# EDIT ATTACHED BILL
# ==================================================
@login_required(login_url='login_page')
def attached_bill_edit(request, id):
    record = get_object_or_404(AttachedBillInfo, id=id)
    if request.method == "POST":
        form = AttachedBillForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.ab_updated_by = request.user
            obj.save()
            messages.success(request, "Attached Bill updated successfully.")
            return redirect('attached_bill_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AttachedBillForm(instance=record)

    return render(
        request,
        "asset_mgt_app/attached_bill_add.html",
        {
            "form": form,
            "record": record,
            "title": "Edit Attached Bill"
        }
    )


# ==================================================
# DELETE ATTACHED BILL
# ==================================================
@login_required(login_url='login_page')
def attached_bill_delete(request, id):
    record = get_object_or_404(AttachedBillInfo, id=id)
    if request.method == "POST":
        record.delete()
        messages.success(request, "Attached Bill deleted successfully.")
    return redirect('attached_bill_list')


# ==================================================
# QUICK MEDIA UPLOAD
# ==================================================
@login_required(login_url='login_page')
def attached_bill_upload(request, id):
    record = get_object_or_404(AttachedBillInfo, id=id)
    if request.method == "POST" and request.FILES.get('ab_bill_upload'):
        record.ab_bill_upload = request.FILES.get('ab_bill_upload')
        record.save()
        messages.success(request, "File uploaded successfully.")
    return redirect('attached_bill_list')


# ==================================================
# AJAX: GET VEHICLE DETAILS & KM RUN
# ==================================================
@login_required(login_url='login_page')
def get_attached_vehicle_details(request):
    vendor_id = request.GET.get('vendor_id')
    vehicle_id = request.GET.get('vehicle_id')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    data = {'trips': []}

    if vehicle_id:
        vehicle = get_object_or_404(VehiclemasterInfo, id=vehicle_id)
        data.update({
            'vehicle_type': str(vehicle.vm_vehicletype) if vehicle.vm_vehicletype else "",
            'buy_cost': float(vehicle.vm_buycost) if vehicle.vm_buycost and vehicle.vm_buycost.replace('.','',1).isdigit() else 0.0,
            'agreed_km': float(vehicle.vm_agreedkm) if vehicle.vm_agreedkm and vehicle.vm_agreedkm.replace('.','',1).isdigit() else 0.0,
            'extra_km_rate': float(vehicle.vm_extrakm) if vehicle.vm_extrakm and vehicle.vm_extrakm.replace('.','',1).isdigit() else 0.0,
        })
    elif vendor_id:
        # Just vendor selected, we don't have vehicle specific details yet but we can still fetch trips
        pass

    # Filter trips
    filters = Q()
    if vehicle_id:
        vehicle = VehiclemasterInfo.objects.get(id=vehicle_id)
        filters &= Q(tr_vehiclenumber=vehicle.vm_registrationnumber)
    elif vendor_id:
        # Get all vehicles for this vendor and filter trips by those registration numbers
        vehicle_reg_nos = VehiclemasterInfo.objects.filter(vm_vendor_id=vendor_id).values_list('vm_registrationnumber', flat=True)
        filters &= Q(tr_vehiclenumber__in=vehicle_reg_nos)
    
    if from_date and to_date:
        filters &= Q(tr_departeddate__date__range=[from_date, to_date])

    if filters:
        # Get all billed trip numbers to exclude them
        bill_id = request.GET.get('bill_id')
        billed_trips_query = AttachedBillInfo.objects.all()
        if bill_id:
            billed_trips_query = billed_trips_query.exclude(id=bill_id)
        
        already_billed = []
        for b_trips in billed_trips_query.values_list('ab_selected_trips', flat=True):
            if b_trips:
                already_billed.extend([t.strip() for t in b_trips.split(',') if t.strip()])
        
        # Apply exclusion
        if already_billed:
            filters &= ~Q(tr_tripnumber__in=already_billed)

        trips = TripdetailInfo.objects.filter(filters).order_by('-tr_departeddate')
        total_km_run = 0
        trip_dates = set()  # Unique departure dates (days vehicle made at least one trip)

        for trip in trips:
            km = (trip.tr_reportedkm or 0) - (trip.tr_departedkm or 0)
            if km < 0: km = 0
            total_km_run += km

            # Track unique departure dates
            if trip.tr_departeddate:
                trip_dates.add(trip.tr_departeddate.date())

            # Use Enquirynote data for customer name
            customer_name = trip.tr_enquirynumber.en_customername.cu_name if trip.tr_enquirynumber and trip.tr_enquirynumber.en_customername else "N/A"

            data['trips'].append({
                'trip_date': trip.tr_departeddate.strftime('%d-%m-%Y') if trip.tr_departeddate else "",
                'cnote': trip.tr_tripnumber or "",
                'customer': customer_name,
                'from': str(trip.tr_departedlocation) if trip.tr_departedlocation else "",
                'to': str(trip.tr_reportedlocation) if trip.tr_reportedlocation else "",
                'trip_km': km,
                'buy_cost': float(trip.tc_tripcost or 0),
                'parking_cost': float(trip.tc_parkingcost or 0),
                'toll_cost': float(trip.tc_tollcost or 0),
                'total_buy_cost': float((trip.tc_tripcost or 0) + (trip.tc_parkingcost or 0) + (trip.tc_tollcost or 0))
            })

        data['total_km_run'] = total_km_run

        # Leave days = (Total Non-Sunday days in period) - (Non-Sunday days with trips)
        if from_date and to_date:
            from datetime import date as dt_date, timedelta
            start_dt = dt_date.fromisoformat(from_date)
            end_dt = dt_date.fromisoformat(to_date)
            
            leave_days_count = 0
            curr = start_dt
            while curr <= end_dt:
                if curr.weekday() != 6: # 6 is Sunday
                    if curr not in trip_dates:
                        leave_days_count += 1
                curr += timedelta(days=1)
                
            data['leave_days'] = leave_days_count
        else:
            data['leave_days'] = 0
    else:
        data['total_km_run'] = 0
        data['leave_days'] = 0

    return JsonResponse(data)


@login_required(login_url='login_page')
def get_vehicles_by_vendor(request):
    vendor_id = request.GET.get('vendor_id')
    if not vendor_id:
        return JsonResponse({'vehicles': []})
    
    # Ownership ID 2 = ATTACHED
    vehicles = VehiclemasterInfo.objects.filter(vm_vendor_id=vendor_id, vm_ownership_id=2).order_by('vm_registrationnumber')
    
    veh_list = []
    for v in vehicles:
        veh_list.append({
            'id': v.id,
            'reg_no': v.vm_registrationnumber
        })
    
    return JsonResponse({'vehicles': veh_list})
