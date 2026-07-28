import json
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from ..forms import PrimeVehicleAllotmentForm
from ..models import (
    VehiclemasterInfo, PrimeEnquirynoteInfo, PrimeVehicleAllotmentInfo, VehicletypeInfo,
    PrimeEnquiryVehicle
)
from ..sub_models.vendor_info_mod import Vendor_info
from .vehicle_allotment_view import get_va_auto_recipients, va_send_allotment_email
from .general_utils import generate_next_number, get_financial_year, get_branch_code, get_session_branch_id


def _generate_prime_job_number(request):
    """Auto-generate the next Prime Job Number like: 26-27_MAA_PJB_000001"""
    fy = get_financial_year()
    branch_id = get_session_branch_id(request)
    branch_code = get_branch_code(branch_id)
    prefix = f"{fy}_{branch_code}_PJB_"
    job_num = generate_next_number(PrimeVehicleAllotmentInfo, 'pva_prime_job_number', prefix, 6)
    return job_num


@login_required(login_url='login_page')
def prime_vehicle_allotment_add(request, pev_id=None, vehicle_allotment_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    # If updating an existing allotment
    if vehicle_allotment_id != 0:
        va = get_object_or_404(PrimeVehicleAllotmentInfo, pk=vehicle_allotment_id)
        pev_id = va.pva_prime_enquiry_vehicle_id
        enquiry_id = va.pva_enquirynumber_id
    elif pev_id:
        pev = get_object_or_404(PrimeEnquiryVehicle, pk=pev_id)
        enquiry_id = pev.pev_enquirynumber_id
        va = None
    else:
        messages.error(request, "Invalid Prime Vehicle Request ID")
        return redirect('prime_enquiry_vehicle_insert')

    enquiry = get_object_or_404(PrimeEnquirynoteInfo, id=enquiry_id)
    pev = get_object_or_404(PrimeEnquiryVehicle, pk=pev_id)

    if request.method == "GET":
        if vehicle_allotment_id == 0:
            form = PrimeVehicleAllotmentForm(initial={'pva_vehicletype': pev.pev_vehicletype_id})
            # Generate next prime job number for display (not saved yet)
            next_job_number = _generate_prime_job_number(request)
        else:
            form = PrimeVehicleAllotmentForm(instance=va)
            next_job_number = va.pva_prime_job_number or _generate_prime_job_number(request)

        context = {
            'first_name': first_name,
            'user_id': user_id,
            'vehicle_allotment_form': form,
            'va': va,
            'pev_id': pev_id,
            'enquiry_num_id': enquiry_id,
            'vehicle_allotment_list': PrimeVehicleAllotmentInfo.objects.filter(pva_prime_enquiry_vehicle_id=pev_id),
            'vehicles_data': VehiclemasterInfo.objects.all(),
            'customer_name': enquiry.pen_customername.cu_name if enquiry.pen_customername else "",
            'from_location': enquiry.pen_fromlocaion.place_name if enquiry.pen_fromlocaion else "",
            'to_location': enquiry.pen_tolocation.place_name if enquiry.pen_tolocation else "",
            'all_vehicletypes': VehicletypeInfo.objects.all(),
            'all_vendors': Vendor_info.objects.all(),
            'pev': pev,
            'enquiry': enquiry,
            'next_job_number': next_job_number,
        }
        return render(request, "asset_mgt_app/prime_vehicle_allotment_add.html", context)

    # POST SAVE (ADD + UPDATE)
    if request.method == "POST":
        if vehicle_allotment_id == 0:
            form = PrimeVehicleAllotmentForm(request.POST)
        else:
            form = PrimeVehicleAllotmentForm(request.POST, instance=va)

        if not form.is_valid():
            error_msgs = "; ".join([f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()])
            messages.error(request, f"Invalid form data: {error_msgs}")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        obj = form.save(commit=False)
        obj.pva_enquirynumber_id = enquiry_id
        obj.pva_prime_enquiry_vehicle_id = pev_id

        # Ensure status is updated from POST if provided
        status_id = request.POST.get('pva_status')
        if status_id:
            obj.pva_status_id = status_id

        # Save Prime-specific fields
        obj.pva_prime_trip_no = request.POST.get('va_prime_trip_no', '').strip() or None
        obj.pva_prime_from_date = request.POST.get('va_prime_from_date') or None
        obj.pva_prime_from_time = request.POST.get('va_prime_from_time') or None
        obj.pva_prime_from_km = request.POST.get('va_prime_from_km') or None

        # Auto-generate job number ONLY on new record
        if vehicle_allotment_id == 0:
            # Duplicate check
            vehicle_source = obj.pva_vehiclesource_id
            duplicate_qs = PrimeVehicleAllotmentInfo.objects.filter(pva_prime_enquiry_vehicle_id=pev_id)

            if vehicle_source in [1, 2] and obj.pva_vehiclenumber:
                duplicate_qs = duplicate_qs.filter(pva_vehiclenumber=obj.pva_vehiclenumber)
            elif vehicle_source == 3 and obj.pva_vehiclenumber_mkt:
                duplicate_qs = duplicate_qs.filter(pva_vehiclenumber_mkt__iexact=obj.pva_vehiclenumber_mkt.strip())

            if duplicate_qs.exists():
                messages.error(request, "This vehicle number is already allotted for this vehicle request.")
                return redirect(request.META.get('HTTP_REFERER', '/'))

            # Assign auto job number
            obj.pva_prime_job_number = _generate_prime_job_number(request)

        obj.save()

        # Email Trigger
        submit_and_email = request.POST.get('submit_and_email')
        if submit_and_email:
            try:
                enquiry_full = PrimeEnquirynoteInfo.objects.select_related(
                    'pen_customername', 'pen_customerdepartment', 'pen_fromlocaion', 'pen_tolocation'
                ).get(id=enquiry_id)
                customer_id = enquiry_full.pen_customername_id if enquiry_full.pen_customername else None
                department_id = enquiry_full.pen_customerdepartment_id if enquiry_full.pen_customerdepartment else None
                recipients = get_va_auto_recipients(customer_id, department_id)

                if recipients:
                    success, result = va_send_allotment_email(obj, enquiry_full, recipients)
                    if success:
                        obj.pva_email_sent = True
                        obj.save(update_fields=['va_email_sent'])
                        messages.success(request, f"Vehicle Allotment Saved. Alert sent to: {', '.join(recipients)}")
                    else:
                        messages.success(request, "Vehicle Allotment Saved. Email failed to send.")
                else:
                    messages.warning(request, "Vehicle Allotment Saved. No email ID found for this customer.")
            except Exception as e:
                messages.success(request, "Vehicle Allotment Saved Successfully")
        else:
            messages.success(request, "Vehicle Allotment Saved Successfully")

        return redirect('prime_vehicle_allotment_update', vehicle_allotment_id=obj.id)


@login_required(login_url='login_page')
def prime_vehicle_allotment_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    enquiry_number = request.GET.get('enquiry_number', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    select_all = request.GET.get('select_all', '')

    # Fetch vehicle allotments linked to Prime Enquiries
    vehicle_allotment_queryset = PrimeVehicleAllotmentInfo.objects.filter(
        pva_enquirynumber__pen_enquirynumber__icontains='_ENP_'
    ).select_related('pva_enquirynumber', 'pva_vehicletype', 'pva_vehicletype_placed', 'pva_vehiclesource', 'pva_vendor', 'pva_status').order_by('-id')

    # Apply search filters
    if enquiry_number:
        vehicle_allotment_queryset = vehicle_allotment_queryset.filter(
            pva_enquirynumber__pen_enquirynumber__icontains=enquiry_number
        )

    if date_from:
        vehicle_allotment_queryset = vehicle_allotment_queryset.filter(
            pva_created_at__date__gte=date_from
        )

    if date_to:
        vehicle_allotment_queryset = vehicle_allotment_queryset.filter(
            pva_created_at__date__lte=date_to
        )

    return render(request, "asset_mgt_app/prime_vehicle_allotment_list.html", {
        'first_name': first_name,
        'user_id': user_id,
        'vehicle_allotment_list': vehicle_allotment_queryset,
        'select_all': select_all,
        'vehicles_data': VehiclemasterInfo.objects.all(),
    })






@login_required(login_url='login_page')
def prime_vehicle_revert_replace(request):
    if request.method == 'POST':
        try:
            allotment_id = request.POST.get('allotment_id')
            va = PrimeVehicleAllotmentInfo.objects.get(id=allotment_id)
            
            if va.pva_replacement_reason:
                # Restore original values
                va.pva_vehiclenumber = va.pva_original_vehiclenumber
                va.pva_vehiclenumber_mkt = va.pva_original_vehiclenumber_mkt
                va.pva_drivername = va.pva_original_drivername
                va.pva_drivernumber = va.pva_original_drivernumber
                va.pva_driver_lic = va.pva_original_driver_lic
                va.pva_driver_lic_expiry = va.pva_original_driver_lic_expiry
                
                # Clear original backups
                va.pva_original_vehiclenumber = None
                va.pva_original_vehiclenumber_mkt = None
                va.pva_original_drivername = None
                va.pva_original_drivernumber = None
                va.pva_original_driver_lic = None
                va.pva_original_driver_lic_expiry = None
                
                # Clear replacement status
                va.pva_replacement_reason = None
                va.pva_replacement_date = None
                va.pva_status_id = 1 # Back to standard Allotted status
                va.pva_updated_by_id = request.session.get('ses_userID')
                va.save()
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'message': 'Not a replaced vehicle'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


@login_required(login_url='login_page')
def prime_vehicle_simplified_replace(request):
    if request.method == 'POST':
        try:
            allotment_id = request.POST.get('allotment_id')
            replace_type = request.POST.get('replace_type') # 'vehicle' or 'driver'
            reason = request.POST.get('reason')
            
            va = PrimeVehicleAllotmentInfo.objects.get(id=allotment_id)
            
            # Backup original fields if this is the first replacement
            if not va.pva_replacement_reason:
                va.pva_original_vehiclenumber = va.pva_vehiclenumber
                va.pva_original_vehiclenumber_mkt = va.pva_vehiclenumber_mkt
                va.pva_original_drivername = va.pva_drivername
                va.pva_original_drivernumber = va.pva_drivernumber
                va.pva_original_driver_lic = va.pva_driver_lic
                va.pva_original_driver_lic_expiry = va.pva_driver_lic_expiry

            if replace_type == 'vehicle':
                if va.pva_replacement_reason and 'Driver:' in va.pva_replacement_reason:
                    va.pva_status_id = 5 # Both Replaced
                    va.pva_replacement_reason = 'Both: ' + va.pva_replacement_reason.replace('Driver:', '').strip() + ' & ' + reason
                else:
                    va.pva_status_id = 4 # Vehicle Replaced
                    va.pva_replacement_reason = 'Vehicle: ' + reason
                
                new_vehicle = request.POST.get('new_vehicle_number')
                if new_vehicle:
                    va.pva_vehiclenumber_mkt = new_vehicle
                    va.pva_vehiclenumber = None  # Clear own vehicle ID to prevent conflicts
                    
            elif replace_type == 'driver':
                if va.pva_replacement_reason and 'Vehicle:' in va.pva_replacement_reason:
                    va.pva_status_id = 5 # Both Replaced
                    va.pva_replacement_reason = 'Both: ' + va.pva_replacement_reason.replace('Vehicle:', '').strip() + ' & ' + reason
                else:
                    va.pva_status_id = 3 # Driver Replaced
                    va.pva_replacement_reason = 'Driver: ' + reason
                    
                new_driver = request.POST.get('new_driver_name')
                new_driver_num = request.POST.get('new_driver_number')
                new_driver_lic = request.POST.get('new_driver_lic')
                new_driver_lic_expiry = request.POST.get('new_driver_lic_expiry')
                
                if new_driver:
                    va.pva_drivername = new_driver
                if new_driver_num:
                    va.pva_drivernumber = new_driver_num
                if new_driver_lic:
                    va.pva_driver_lic = new_driver_lic
                if new_driver_lic_expiry:
                    va.pva_driver_lic_expiry = new_driver_lic_expiry
            
            elif replace_type == 'both':
                va.pva_status_id = 5 # Both Replaced
                va.pva_replacement_reason = 'Both: ' + reason
                new_vehicle = request.POST.get('new_vehicle_number')
                if new_vehicle:
                    va.pva_vehiclenumber_mkt = new_vehicle
                    va.pva_vehiclenumber = None
                
                new_driver = request.POST.get('new_driver_name')
                new_driver_num = request.POST.get('new_driver_number')
                new_driver_lic = request.POST.get('new_driver_lic')
                new_driver_lic_expiry = request.POST.get('new_driver_lic_expiry')
                
                if new_driver:
                    va.pva_drivername = new_driver
                if new_driver_num:
                    va.pva_drivernumber = new_driver_num
                if new_driver_lic:
                    va.pva_driver_lic = new_driver_lic
                if new_driver_lic_expiry:
                    va.pva_driver_lic_expiry = new_driver_lic_expiry
            
            va.pva_replacement_date = timezone.now()
            va.pva_updated_by_id = request.session.get('ses_userID')
            va.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request'})
