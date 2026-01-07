from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone

from ..sub_forms.maintenance_form import MaintenanceForm
from ..sub_models.maintenance_mod import MaintenanceInfo
from ..sub_models.vehiclemaster_mod import VehiclemasterInfo


# ==================================================
# ADD MAINTENANCE
# ==================================================
@login_required(login_url='login_page')
def maintenance_add(request):
    first_name = request.session.get('first_name')

    if request.method == "POST":
        form = MaintenanceForm(request.POST)

        if form.is_valid():
            obj = form.save(commit=False)

            # 🔹 FIX: SET VEHICLE PROPERLY
            reg_no = request.POST.get("registration_no")
            vehicle = VehiclemasterInfo.objects.get(
                vm_registrationnumber=reg_no
            )
            obj.vehicle = vehicle   # ✅ REQUIRED

            # 🔹 auto job card fields
            obj.job_card_creator = (
                request.user.get_full_name() or request.user.username
            )
            obj.job_card_created_on = timezone.now()

            obj.save()

            return redirect('maintenance_list')

    else:
        form = MaintenanceForm()

    return render(
        request,
        "asset_mgt_app/maintenance.html",
        {
            "form": form,
            "first_name": first_name,
            "job_creator": request.user.get_full_name() or request.user.username,
            "created_on": timezone.now(),
        }
    )

# ==================================================
# LIST MAINTENANCE
# ==================================================
@login_required(login_url='login_page')
def maintenance_list(request):
    maintenance_list = MaintenanceInfo.objects.all().order_by('-job_card_created_on')

    return render(
        request,
        "asset_mgt_app/maintenance_list.html",
        {
            "maintenance_list": maintenance_list
        }
    )


# ==================================================
# EDIT MAINTENANCE
# ==================================================
@login_required(login_url='login_page')
def maintenance_edit(request, id):
    record = get_object_or_404(MaintenanceInfo, id=id)

    if request.method == "POST":
        form = MaintenanceForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect('maintenance_list')
    else:
        form = MaintenanceForm(instance=record)

    return render(
        request,
        "asset_mgt_app/maintenance.html",
        {
            "form": form,
            "job_creator": record.job_card_creator,
            "created_on": record.job_card_created_on,
        }
    )


# ==================================================
# DELETE MAINTENANCE
# ==================================================
@login_required(login_url='login_page')
def maintenance_delete(request, id):
    record = get_object_or_404(MaintenanceInfo, id=id)

    if request.method == "POST":
        record.delete()
        return redirect('maintenance_list')


# ==================================================
# FETCH VEHICLE DETAILS (AJAX)
# ==================================================
@login_required(login_url='login_page')
def fetch_vehicle_details(request):
    reg_no = request.GET.get('reg_no')

    vehicle = VehiclemasterInfo.objects.filter(
        vm_registrationnumber=reg_no
    ).first()

    if not vehicle:
        return JsonResponse({}, status=404)

    return JsonResponse({
        "make_model": f"{vehicle.vm_vehiclemanufacturer} - {vehicle.vm_vehiclemodel}",
        "registration_date": vehicle.vm_registrationdate,
        "chassis_no": vehicle.vm_chassisnumber,
        "engine_no": vehicle.vm_enginenumber,
    })
