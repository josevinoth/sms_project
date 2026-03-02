from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from ..sub_models.maintenance_bill_mod import MaintenanceBillInfo
from ..sub_forms.maintenance_bill_form import MaintenanceBillForm
from ..sub_models.maintenance_mod import MaintenanceInfo
from ..sub_models.vehiclemaster_mod import VehiclemasterInfo

@login_required(login_url='login_page')
def maintenance_bill_add(request, id=None):
    instance = get_object_or_404(MaintenanceBillInfo, id=id) if id else None
    
    if request.method == "POST":
        form = MaintenanceBillForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            msg = "Maintenance Bill updated successfully." if id else "Maintenance Bill added successfully."
            messages.success(request, msg)
            return redirect('maintenance_bill_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = MaintenanceBillForm(instance=instance)
    
    # Fetch only maintenance records that are "Finance Approved" (3) 
    # and have NOT been billed yet (bills_v1__isnull=True)
    pending_maintenance = MaintenanceInfo.objects.filter(
        mi_approval_status_id=3,
        bills_v1__isnull=True
    ).order_by('-mi_created_at')

    # Fetch vehicles that have records in the pending_maintenance above (unbilled ones)
    vehicles = VehiclemasterInfo.objects.filter(
        maintenance_records__mi_approval_status_id=3,
        maintenance_records__bills_v1__isnull=True
    ).distinct().order_by('vm_registrationnumber')
    
    return render(request, "asset_mgt_app/maintenance_bill_add.html", {
        "form": form, 
        "pending_maintenance": pending_maintenance,
        "vehicles": vehicles,
        "is_edit": True if id else False,
        "instance": instance
    })

@login_required(login_url='login_page')
def maintenance_bill_edit(request, id):
    return maintenance_bill_add(request, id=id)

@login_required(login_url='login_page')
def maintenance_bill_delete(request, id):
    bill = get_object_or_404(MaintenanceBillInfo, id=id)
    bill.delete()
    messages.success(request, "Maintenance Bill deleted successfully.")
    return redirect('maintenance_bill_list')

@login_required(login_url='login_page')
def maintenance_bill_list(request):
    bills = MaintenanceBillInfo.objects.all().order_by('-mnb_created_at')
    return render(request, "asset_mgt_app/maintenance_bill_list.html", {"bills": bills})

@login_required(login_url='login_page')
def fetch_maintenance_bill_details(request):
    maintenance_id = request.GET.get('maintenance_id')
    try:
        maintenance = MaintenanceInfo.objects.get(id=maintenance_id)
        data = {
            "vehicle_no": maintenance.mi_vehicle.vm_registrationnumber,
            "vehicle_type": maintenance.mi_vehicle.vm_vehicletype.vt_vehicletype if maintenance.mi_vehicle.vm_vehicletype else "N/A",
            "service_type": maintenance.mi_service_type,
            "estimated_amount": float(maintenance.mi_estimated_amount) if maintenance.mi_estimated_amount else 0,
            "vendor_name": maintenance.mi_vehicle.vm_vendor.vend_name if maintenance.mi_vehicle.vm_vendor else "N/A",
            "technician": maintenance.mi_technician,
        }
        return JsonResponse(data)
    except MaintenanceInfo.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

@login_required(login_url='login_page')
def get_maintenance_records_by_vehicle(request):
    vehicle_id = request.GET.get('vehicle_id')
    # Match the unbilled records with status 3 (Finance Approved)
    records = MaintenanceInfo.objects.filter(
        mi_vehicle_id=vehicle_id, 
        mi_approval_status_id=3,
        bills_v1__isnull=True
    ).order_by('-mi_created_at')
    
    data = []
    for r in records:
        data.append({
            "id": r.id,
            "job_card_no": r.mi_job_card_no or f"JC-{r.id}",
            "service_type": r.mi_service_type,
            "estimated_amount": str(r.mi_estimated_amount),
            "created_at": r.mi_created_at.strftime('%Y-%m-%d'),
            "status": str(r.mi_approval_status) if r.mi_approval_status else "N/A"
        })
    
    return JsonResponse({"records": data})
