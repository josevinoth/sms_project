from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Max


from ..sub_forms.maintenance_form import MaintenanceForm
from ..sub_models.maintenance_mod import MaintenanceInfo
from ..sub_models.vehiclemaster_mod import VehiclemasterInfo

from django.views.decorators.http import require_POST
from django.contrib import messages


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

            # ===============================
            # SET VEHICLE
            # ===============================
            reg_no = request.POST.get("registration_no")
            try:
                vehicle = VehiclemasterInfo.objects.get(
                    vm_registrationnumber=reg_no
                )
            except VehiclemasterInfo.DoesNotExist:
                messages.error(request, "Selected vehicle not found.")
                return redirect('maintenance_add')

            obj.vehicle = vehicle

            # ===============================
            # JOB CARD CREATOR & TIME
            # ===============================
            obj.job_card_creator = (
                request.user.get_full_name() or request.user.username
            )
            obj.job_card_created_on = timezone.now()

            # ensure approval_status has the model default (defensive)
            try:
                obj.approval_status = (
                    MaintenanceInfo._meta.get_field('approval_status').default
                )
            except Exception:
                obj.approval_status = 1

            # ===============================
            # AUTO GENERATE JOB CARD NUMBER
            # FORMAT: WJ/25/0001
            # ===============================
            current_year = timezone.now().year % 100  # 2025 -> 25
            year_prefix = f"WJ/{current_year:02d}"

            last_job_card = (
                MaintenanceInfo.objects
                .filter(job_card_no__startswith=year_prefix)
                .aggregate(Max("job_card_no"))
                .get("job_card_no__max")
            )

            if last_job_card:
                last_number = int(last_job_card.split("/")[-1])
                new_number = last_number + 1
            else:
                new_number = 1

            obj.job_card_no = f"{year_prefix}/{new_number:04d}"

            # ===============================
            # SAVE RECORD
            # ===============================
            obj.save()

            messages.success(request, "Maintenance job card created and awaiting manager approval.")
            return redirect('maintenance_list')

    else:
        form = MaintenanceForm()

    # compute approval status label for a new form (model default)
    try:
        field = MaintenanceInfo._meta.get_field('approval_status')
        default_val = field.default
        approval_status_label = next((label for val, label in field.choices if val == default_val), str(default_val))
    except Exception:
        approval_status_label = ''

    return render(
        request,
        "asset_mgt_app/maintenance.html",
        {
            "form": form,
            "first_name": first_name,
            "job_creator": request.user.get_full_name() or request.user.username,
            "created_on": timezone.now(),
            "approval_status_label": approval_status_label,
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
        form = MaintenanceForm(
            instance=record,
            initial={
                "registration_no": record.vehicle
            }
        )

        if form.is_valid():
            obj = form.save(commit=False)

            # 🔥 CRITICAL: update vehicle from registration_no
            obj.vehicle = form.cleaned_data["registration_no"]

            obj.save()
            messages.success(request, "Maintenance record updated.")
            return redirect('maintenance_list')

    else:
        form = MaintenanceForm(instance=record)

    # approval label from instance
    approval_status_label = (getattr(record, 'get_approval_status_display', lambda: '')() if record else '')

    return render(
        request,
        "asset_mgt_app/maintenance.html",
        {
            "form": form,
            "job_creator": record.job_card_creator,
            "created_on": record.job_card_created_on,
            "approval_status_label": approval_status_label,
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
        messages.success(request, "Maintenance record deleted.")
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


from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from xhtml2pdf import pisa
from django.conf import settings
import os


@login_required(login_url='login_page')
def maintenance_pdf(request, id):
    maintenance = get_object_or_404(MaintenanceInfo, id=id)

    # ===============================
    # FETCH LAST SERVICED DATE
    # ===============================
    last_service = (
        MaintenanceInfo.objects
        .filter(
            vehicle=maintenance.vehicle,
            complaint=maintenance.complaint,
            job_card_created_on__lt=maintenance.job_card_created_on
        )
        .order_by('-job_card_created_on')
        .first()
    )

    last_serviced_date = (
        last_service.job_card_created_on if last_service else None
    )
    vehicle_type = (
        maintenance.vehicle.vm_vehicletype.vt_vehicletype
        if maintenance.vehicle and maintenance.vehicle.vm_vehicletype
        else None
    )

    template = get_template("asset_mgt_app/maintenance_pdf.html")

    logo_path = os.path.join(settings.MEDIA_ROOT, "Company_Logo.png")

    context = {
        "maintenance": maintenance,
        "company_logo": logo_path,
        "last_serviced_date": last_serviced_date,
        "vehicle_type": vehicle_type,
    }

    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="JOB_CARD_{maintenance.job_card_no}.pdf"'
    )

    pisa_status = pisa.CreatePDF(
        src=html,
        dest=response,
        encoding="UTF-8"
    )

    if pisa_status.err:
        return HttpResponse("PDF generation failed", status=500)

    return response
@login_required(login_url='login_page')
def manager_approval_list(request):
    # Show only records awaiting manager approval (approval_status == 1)
    records = MaintenanceInfo.objects.filter(approval_status=1).order_by('-job_card_created_on')

    return render(
        request,
        "asset_mgt_app/maintenance_approval_manager.html",
        {"records": records}
    )



@login_required(login_url='login_page')
@require_POST
def manager_approve(request, id):
    record = get_object_or_404(MaintenanceInfo, id=id)

    if record.approval_status == 1:
        record.approval_status = 2
        record.save()

        messages.success(
            request,
            f"Job card {record.job_card_no} approved by manager and moved to finance."
        )
    else:
        messages.warning(request, "Record is not pending manager approval.")

    return redirect('manager_approval_list')

@login_required(login_url='login_page')
def finance_approval_list(request):
    records = MaintenanceInfo.objects.filter(
        approval_status=2
    ).order_by('-job_card_created_on')

    return render(
        request,
        "asset_mgt_app/maintenance_approval_finance.html",
        {"records": records}
    )



@login_required(login_url='login_page')
@require_POST
def finance_approve(request, id):
    record = get_object_or_404(MaintenanceInfo, id=id)

    if record.approval_status == 2:
        record.approval_status = 3  # Finance Approved
        record.save()
        messages.success(request, f"Job card {record.job_card_no} finance approved.")
    else:
        messages.warning(request, "Record is not pending finance approval.")

    # Redirect back to the finance approval list so the user remains on the same page
    return redirect('finance_approval_list')
