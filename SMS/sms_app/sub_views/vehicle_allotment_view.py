import json
from datetime import datetime
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Sum, Q, Count
from ..forms import VehicleallotmentForm
from ..models import Enquirynotevehicle, TripdetailInfo, OwnershipInfo, User_extInfo, ConsignmentdetailInfo, ConsignmentgoodsInfo, \
    VehiclemasterInfo, EnquirynoteInfo, Vehicle_allotmentInfo, VendorratemasterInfo1, RtratemasterInfo, VehicletypeInfo, DeletionLog, \
    Trip_approval_info, approval_status_info
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from .send_department_email import send_department_email
from .general_utils import get_branch_code, get_session_branch_id

import re
from ..sub_models.vendor_info_mod import Vendor_info
from ..sub_models.emailmaster_mod import Emailmaster
from ..sub_models.emailtype_mod import Email_type
from ..sub_models.trans_invoice_mod import TransInvoiceInfo
from ..sub_models.vehicle_replacement_status_mod import Replacementstatus


VEHICLE_NUMBER_REGEX = re.compile(r'^[A-Za-z]{2}[0-9]{2}[A-Za-z]{0,2}[0-9]{4}$')

def sync_allotment_rate_to_trips(allotment_obj):
    """
    Syncs the effective sell rate from Vehicle_allotmentInfo to related TripdetailInfo records.
    Special Sell takes priority if > 0, otherwise falls back to Standard Sell.
    """
    if not allotment_obj or not allotment_obj.va_enquirynumber_id:
        return

    effective_rate = 0.0
    if allotment_obj.va_special_sale is not None and float(allotment_obj.va_special_sale) > 0:
        effective_rate = float(allotment_obj.va_special_sale)
    elif allotment_obj.va_sale is not None and float(allotment_obj.va_sale) > 0:
        effective_rate = float(allotment_obj.va_sale)

    if effective_rate <= 0:
        return

    veh_no = ''
    if allotment_obj.va_vehiclenumber and getattr(allotment_obj.va_vehiclenumber, 'vm_registrationnumber', None):
        veh_no = allotment_obj.va_vehiclenumber.vm_registrationnumber.strip()
    elif allotment_obj.va_vehiclenumber_mkt:
        veh_no = allotment_obj.va_vehiclenumber_mkt.strip()

    trips = TripdetailInfo.objects.filter(tr_enquirynumber_id=allotment_obj.va_enquirynumber_id)
    if veh_no:
        clean_veh = veh_no.replace(' ', '').replace('-', '').upper()
        for t in trips:
            t_veh = (t.tr_vehiclenumber or '').replace(' ', '').replace('-', '').upper()
            if not t_veh or t_veh == clean_veh or trips.count() == 1:
                t.tc_tripcost = effective_rate
                t.save(update_fields=['tc_tripcost'])
    else:
        trips.update(tc_tripcost=effective_rate)

def validate_vehicle_number_format(veh_num):
    """
    Validates strict vehicle registration format:
    - First 2 chars: Alphabets only (e.g. TN)
    - Next 2 chars: Digits only (e.g. 22)
    - Next 1-2 chars: Alphabets optional (e.g. AB or A)
    - Final 4 chars: Digits only (e.g. 4916)
    - No spaces or special characters.
    """
    if not veh_num:
        return False
    return bool(VEHICLE_NUMBER_REGEX.match(str(veh_num).strip()))


def is_license_expired(lic_expiry_val):
    """
    Returns True if lic_expiry_val is a valid date string and is before today's date.
    """
    if not lic_expiry_val:
        return False
    try:
        if isinstance(lic_expiry_val, datetime):
            exp_date = lic_expiry_val.date()
        elif hasattr(lic_expiry_val, 'strftime'):
            exp_date = lic_expiry_val
        else:
            exp_str = str(lic_expiry_val).strip().split('T')[0]
            exp_date = datetime.strptime(exp_str, '%Y-%m-%d').date()
        return exp_date < timezone.now().date()
    except (ValueError, TypeError):
        return False


# ===== HELPER: Get recipients from Emailmaster =====
def get_va_auto_recipients(customer_id, department_id, requestor=None):
    """
    Fetch email recipients from Emailmaster for vehicle allotment alerts.
    Uses Email Type 2 (For alert), matching by Customer + Department.
    Falls back to Customer-only match if no department-specific entry exists.
    """
    if not customer_id:
        return None

    try:
        # Base query for this customer and alert type
        email_qs = Emailmaster.objects.filter(
            Q(em_emailtype_id=2) | Q(em_emailtype__email_type__iexact='For alert'),
            em_Customer_name_id=customer_id
        )

        # Filter by Requestor if provided and matches exist
        if requestor:
            req_qs = email_qs.filter(em_user__iexact=requestor)
            if req_qs.exists():
                email_qs = req_qs

        # Try matching Customer + Department first
        email_entry = email_qs.filter(em_customerdepartment_id=department_id).first()

        # Fallback to Customer-only match
        if not email_entry:
            email_entry = email_qs.filter(em_customerdepartment__isnull=True).first()

        if email_entry:
            to_emails = [e.strip() for e in (email_entry.em_to_names or '').split(',') if e.strip()]
            cc_emails = [e.strip() for e in (email_entry.em_cc_names or '').split(',') if e.strip()]
            return to_emails + cc_emails

        return None
    except Exception:
        return None


# ===== HELPER: Send Vehicle Allotment Email =====
def va_send_allotment_email(va, enquiry, recipients):
    """
    Send automated Vehicle Allotment email with dark blue styling.
    """
    customer_name = enquiry.en_customername.cu_name if enquiry.en_customername else "N/A"
    department_name = enquiry.en_customerdepartment.ct_customerdepartment if enquiry.en_customerdepartment else "N/A"
    from_location = enquiry.en_fromlocaion.place_name if enquiry.en_fromlocaion else "N/A"
    to_location = enquiry.en_tolocation.place_name if enquiry.en_tolocation else "N/A"

    # Get vehicle number (own/attached or market)
    vehicle_number = str(va.va_vehiclenumber) if va.va_vehiclenumber else (va.va_vehiclenumber_mkt or "N/A")

    subject = f"Vehicle Allotment - {vehicle_number}"

    email_body = f"""
        <html>
            <head>
                <style>
                    table {{
                        width: 70%;
                        border-collapse: collapse;
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                        border: 1px solid black;
                        margin-left: auto;
                        margin-right: auto;
                    }}
                    th, td {{
                        border: 1px solid black;
                        padding: 10px;
                    }}
                    th {{
                        background-color: #f4f4f4;
                        color: #333;
                        text-align: left;
                        width: 40%;
                    }}
                    td {{
                        vertical-align: top;
                    }}
                </style>
            </head>
            <body>
                <p>Dear Customer,</p>
                <p>Thank you for your business. Below are the vehicle allotment details for your reference:</p>
                <table>
                    <tr>
                        <th colspan="2" style="background-color: #003366; color: white; padding: 10px; text-align: center; font-size: 18px;">
                            Vehicle Allotment
                        </th>
                    </tr>
                    <tr><th>Customer Name</th><td>{customer_name}</td></tr>
                    <tr><th>Department</th><td>{department_name}</td></tr>
                    <tr><th>From Location</th><td>{from_location}</td></tr>
                    <tr><th>To Location</th><td>{to_location}</td></tr>
                    <tr><th>Vehicle Type</th><td>{va.va_vehicletype}</td></tr>
                    <tr><th>Vehicle Number</th><td>{vehicle_number}</td></tr>
                    <tr><th>Driver Name</th><td>{va.va_drivername or 'N/A'}</td></tr>
                    <tr><th>Driver Mobile</th><td>{va.va_drivernumber or 'N/A'}</td></tr>
                </table>
                <p>Regards,<br>BVM Transport Team</p>
            </body>
        </html>
    """

    try:
        send_department_email(
            department='itadmin',
            subject=subject,
            message=email_body,
            recipient_list=recipients,
            email_type=1
        )
        return True, recipients
    except Exception as e:
        return False, str(e)


@login_required(login_url='login_page')
def vehicle_allotment_enquiry(request, enquiry_id, vehicle_number):
    request.session['ses_enquiry_id'] = enquiry_id  # ADD THIS

    if vehicle_number == "0" or vehicle_number == 0:
        return redirect('vehicle_allotment_insert', enquiry_id=enquiry_id)

    enquiry = get_object_or_404(EnquirynoteInfo, pk=enquiry_id)

    # find vehicle ID if exists
    try:
        vehicle_number_id = VehiclemasterInfo.objects.get(
            vm_registrationnumber=vehicle_number
        ).id
    except VehiclemasterInfo.DoesNotExist:
        vehicle_number_id = None

    # check if allotment exists already
    vehicle_allotment = Vehicle_allotmentInfo.objects.filter(
        va_enquirynumber=enquiry
    ).filter(
        Q(va_vehiclenumber_mkt=vehicle_number) |
        Q(va_vehiclenumber=vehicle_number_id)
    ).last()  # Pick the LATEST one (for replacements)

    if vehicle_allotment:
        return redirect('vehicle_allotment_update',
                        vehicle_allotment_id=vehicle_allotment.id)

    # if no allotment → go to ADD PAGE with that enquiry_id
    return redirect('vehicle_allotment_insert', enquiry_id=enquiry_id)


@login_required(login_url='login_page')
def vehicle_allotment_nav(request, vehicle_allotment_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    request.session['ses_enqiury_id'] = vehicle_allotment_id
    print("I am inside Get add tripetails")
    vehicle_allotment_form = VehicleallotmentForm()
    vehicle_allotment_list = Vehicle_allotmentInfo.objects.filter(va_enquirynumber=vehicle_allotment_id)
    context = {
        'vehicle_allotment_list': Vehicle_allotmentInfo.objects.all(),
        'first_name': first_name,
        'user_id': user_id,
        'vehicle_allotment_form': vehicle_allotment_form,
        'vehicle_allotment_list': vehicle_allotment_list,
    }
    return render(request, "asset_mgt_app/vehicle_allotment_add.html", context)


@login_required(login_url='login_page')
def vehicle_allotment_add(request, enquiry_id=None, vehicle_allotment_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    # ---------- ADD MODE (GET) ----------
    if request.method == "GET" and vehicle_allotment_id == 0:
        form = VehicleallotmentForm()

        # Store enquiry ID in session for POST usage
        request.session['ses_enquiry_id'] = enquiry_id
        enquiry = EnquirynoteInfo.objects.get(id=enquiry_id)  # ⬅ Fetch enquiry

        return render(request, "asset_mgt_app/vehicle_allotment_add.html", {
            'first_name': first_name,
            'user_id': user_id,
            'vehicle_allotment_form': form,
            'enquiry_num_id': enquiry_id,
            'vehicle_allotment_list': Vehicle_allotmentInfo.objects.filter(
                va_enquirynumber=enquiry_id
            ).order_by('-id'),
            'vehicles_data': VehiclemasterInfo.objects.only('id', 'vm_registrationnumber').order_by('vm_registrationnumber'),
            'customer_name': enquiry.en_customername.cu_name if enquiry.en_customername else "",
            'from_location': enquiry.en_fromlocaion.place_name if enquiry.en_fromlocaion else "",
            'to_location': enquiry.en_tolocation.place_name if enquiry.en_tolocation else "",
            'all_vehicletypes': VehicletypeInfo.objects.all(),
            'all_vendors': Vendor_info.objects.all(),
        })

    # ---------- UPDATE MODE (GET) ----------
    if request.method == "GET" and vehicle_allotment_id != 0:
        va = Vehicle_allotmentInfo.objects.select_related(
            'va_enquirynumber', 'va_enquirynumber__en_customername',
            'va_enquirynumber__en_fromlocaion', 'va_enquirynumber__en_tolocation',
            'va_status'
        ).get(pk=vehicle_allotment_id)
        enquiry_id = va.va_enquirynumber.id

        # Store correct enquiry ID in session
        request.session['ses_enquiry_id'] = enquiry_id
        enquiry = va.va_enquirynumber  # ⬅ Fetch enquiry

        form = VehicleallotmentForm(instance=va)

        return render(request, "asset_mgt_app/vehicle_allotment_add.html", {
            'first_name': first_name,
            'user_id': user_id,
            'vehicle_allotment_form': form,
            'va': va,
            'enquiry_num_id': enquiry_id,
            'vehicle_allotment_list': Vehicle_allotmentInfo.objects.filter(
                va_enquirynumber=enquiry_id
            ).select_related('va_status', 'va_vehicletype', 'va_vehicletype_placed', 'va_vendor', 'va_vehiclesource').order_by('-id'),
            'vehicles_data': VehiclemasterInfo.objects.only('id', 'vm_registrationnumber').order_by('vm_registrationnumber'),
            'customer_name': enquiry.en_customername.cu_name if enquiry.en_customername else "",
            'from_location': enquiry.en_fromlocaion.place_name if enquiry.en_fromlocaion else "",
            'to_location': enquiry.en_tolocation.place_name if enquiry.en_tolocation else "",
            'all_vehicletypes': VehicletypeInfo.objects.all(),
            'all_vendors': Vendor_info.objects.all(),
        })

    # ---------- POST SAVE (ADD + UPDATE) ----------
    # ---------- POST SAVE (ADD + UPDATE) ----------
    if request.method == "POST":

        if vehicle_allotment_id != 0:
            try:
                va_existing = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id)
                enquiry_id = va_existing.va_enquirynumber_id
            except Vehicle_allotmentInfo.DoesNotExist:
                enquiry_id = None
        else:
            enquiry_id = request.POST.get('enquiry_num_id') or enquiry_id or request.session.get('ses_enquiry_id')

        if not enquiry_id:
            messages.error(request, "Enquiry ID missing. Please try again.")
            referer = request.META.get('HTTP_REFERER')
            return redirect(referer if referer else 'enquirynote_list')

        # ------------------
        # ADD MODE
        # ------------------
        if vehicle_allotment_id == 0:
            form = VehicleallotmentForm(request.POST)

            if not form.is_valid():
                messages.error(request, "Invalid form data")
                referer = request.META.get('HTTP_REFERER')
                return redirect(referer if referer else request.path)

            obj = form.save(commit=False)
            obj.va_enquirynumber_id = enquiry_id
            if request.user and request.user.is_authenticated:
                obj.va_created_by = request.user
                obj.va_updated_by = request.user

            # Explicitly ensure status is updated from POST if provided
            status_id = request.POST.get('va_status')
            if status_id:
                obj.va_status_id = status_id

            # 🚫 MANDATORY DRIVER & LICENSE EXPIRY CHECK FOR OWN/ATTACHED VEHICLES
            vehicle_source = obj.va_vehiclesource_id
            if vehicle_source in [1, 2]:
                if not obj.va_drivername or not str(obj.va_drivername).strip():
                    messages.error(request, "Driver Name is mandatory for OWN and ATTACHED vehicles.")
                    referer = request.META.get('HTTP_REFERER')
                    return redirect(referer if referer else request.path)
                if not obj.va_driver_lic_expiry or not str(obj.va_driver_lic_expiry).strip():
                    messages.error(request, "Driver License Expiry Date is mandatory for OWN and ATTACHED vehicles.")
                    referer = request.META.get('HTTP_REFERER')
                    return redirect(referer if referer else request.path)
            
            # 🚫 EXPIRED LICENSE CHECK FOR ALL DRIVERS
            if obj.va_driver_lic_expiry and is_license_expired(obj.va_driver_lic_expiry):
                messages.error(request, f"🚫 Cannot submit form: Driver license expired on {obj.va_driver_lic_expiry}! Please assign a driver with a valid license.")
                referer = request.META.get('HTTP_REFERER')
                return redirect(referer if referer else request.path)

            # 🚫 VEHICLE REGISTRATION FORMAT CHECK FOR MARKET VEHICLES (Temporarily commented out)
            # if vehicle_source == 3 and obj.va_vehiclenumber_mkt:
            #     mkt_num = str(obj.va_vehiclenumber_mkt).strip()
            #     if not validate_vehicle_number_format(mkt_num):
            #         messages.error(
            #             request,
            #             f"Invalid vehicle number format '{mkt_num}'. Format must strictly follow e.g. TN22AB4916 (First 2 letters, next 2 digits, optional 1-2 letters, and final 4 digits)."
            #         )
            #         referer = request.META.get('HTTP_REFERER')
            #         return redirect(referer if referer else request.path)

            # 🚫 VEHICLE TYPE & QUANTITY VALIDATION AGAINST ENQUIRY NOTE
            requested_entries = Enquirynotevehicle.objects.filter(env_enquirynumber_id=enquiry_id)
            if requested_entries.exists():
                requested_vt_ids = list(requested_entries.values_list('env_vehicletype_id', flat=True))
                if obj.va_vehicletype_id not in requested_vt_ids:
                    requested_vt_names = ", ".join(list(requested_entries.values_list('env_vehicletype__vt_vehicletype', flat=True)))
                    messages.error(
                        request,
                        f"🚫 Vehicle type '{obj.va_vehicletype}' was not requested in this Enquiry Note. Requested type(s): {requested_vt_names}."
                    )
                    referer = request.META.get('HTTP_REFERER')
                    return redirect(referer if referer else request.path)

                total_requested_for_type = requested_entries.filter(
                    env_vehicletype_id=obj.va_vehicletype_id
                ).aggregate(total=Sum('env_quantity'))['total'] or 0

                already_allotted_count = Vehicle_allotmentInfo.objects.filter(
                    va_enquirynumber_id=enquiry_id,
                    va_vehicletype_id=obj.va_vehicletype_id
                ).count()

                if already_allotted_count >= total_requested_for_type:
                    messages.error(
                        request,
                        f"🚫 Cannot allot vehicle: Total requested quantity of '{obj.va_vehicletype}' ({total_requested_for_type}) has already been allotted ({already_allotted_count} allotted)."
                    )
                    referer = request.META.get('HTTP_REFERER')
                    return redirect(referer if referer else request.path)

            duplicate_qs = Vehicle_allotmentInfo.objects.filter(
                va_enquirynumber_id=enquiry_id
            )
            allotments_to_check = Vehicle_allotmentInfo.objects.none()

            # OWN / ATTACHED
            if vehicle_source in [1, 2] and obj.va_vehiclenumber:
                duplicate_qs = duplicate_qs.filter(
                    va_vehiclenumber=obj.va_vehiclenumber
                )
                allotments_to_check = Vehicle_allotmentInfo.objects.filter(va_vehiclenumber=obj.va_vehiclenumber)

            # MARKET
            elif vehicle_source == 3 and obj.va_vehiclenumber_mkt:
                duplicate_qs = duplicate_qs.filter(
                    va_vehiclenumber_mkt__iexact=obj.va_vehiclenumber_mkt.strip()
                )
                allotments_to_check = Vehicle_allotmentInfo.objects.filter(va_vehiclenumber_mkt__iexact=obj.va_vehiclenumber_mkt.strip())

            # Filter active checks to only allotments/enquiries created on/after 2026-08-01
            allotments_to_check = allotments_to_check.filter(
                Q(va_created_at__date__gte='2026-08-01') | Q(va_enquirynumber__en_created_at__date__gte='2026-08-01')
            )

            if duplicate_qs.exists():
                messages.error(
                    request,
                    "This vehicle number is already allotted for this enquiry."
                )
                referer = request.META.get('HTTP_REFERER')
                return redirect(referer if referer else request.path)

            # 🚫 ACTIVE TRIP CHECK FOR THIS VEHICLE (Global - August 1, 2026 onwards)
            is_busy = False
            busy_enquiry = ""
            closed_status_ids = [2, 3, 4, 5, 7, 9, 10, 11]

            reg_no = obj.va_vehiclenumber.vm_registrationnumber if (vehicle_source in [1, 2] and obj.va_vehiclenumber) else (obj.va_vehiclenumber_mkt if vehicle_source == 3 else None)

            if reg_no:
                reg_no_clean = str(reg_no).strip()
                other_trips = TripdetailInfo.objects.filter(
                    Q(tr_created_at__date__gte='2026-08-01') | Q(tr_enquirynumber__en_created_at__date__gte='2026-08-01'),
                    tr_vehiclenumber__iexact=reg_no_clean
                ).exclude(tr_enquirynumber_id=enquiry_id).select_related('tr_enquirynumber')

                for trip_item in other_trips:
                    enq_status_str = str(trip_item.tr_enquirynumber.en_status) if (trip_item.tr_enquirynumber and trip_item.tr_enquirynumber.en_status) else ""
                    if "Completed" in enq_status_str or "Cancel" in enq_status_str or "Closed" in enq_status_str:
                        continue

                    op_closed = (trip_item.tr_operational_status_id in closed_status_ids) if trip_item.tr_operational_status_id else False
                    fin_closed = (trip_item.tc_financestatus_id in closed_status_ids) if trip_item.tc_financestatus_id else False
                    if not (op_closed or fin_closed):
                        is_busy = True
                        busy_enquiry = trip_item.tr_enquirynumber.en_enquirynumber if trip_item.tr_enquirynumber else str(trip_item.tr_enquirynumber_id)
                        break

            # 🚫 DOUBLE-SUBMISSION / RACE CONDITION GUARD (Last 15 seconds check)
            from datetime import timedelta
            from django.utils import timezone

            fifteen_sec_ago = timezone.now() - timedelta(seconds=15)
            recent_duplicate = Vehicle_allotmentInfo.objects.filter(
                va_enquirynumber_id=enquiry_id,
                va_created_at__gte=fifteen_sec_ago
            )
            if vehicle_source in [1, 2] and obj.va_vehiclenumber:
                recent_duplicate = recent_duplicate.filter(va_vehiclenumber=obj.va_vehiclenumber)
            elif vehicle_source == 3 and obj.va_vehiclenumber_mkt:
                recent_duplicate = recent_duplicate.filter(va_vehiclenumber_mkt__iexact=obj.va_vehiclenumber_mkt.strip())

            if recent_duplicate.exists():
                messages.warning(
                    request,
                    "⚠️ Duplicate submission detected. Vehicle allotment was already processed."
                )
                referer = request.META.get('HTTP_REFERER')
                return redirect(referer if referer else request.path)

            # Reset Buy Rates for non-market vehicles (Own & Attached)
            if vehicle_source in [1, 2]:
                obj.va_standardbuy = None
                obj.va_specialbuy = None

            # Auto-fill va_sale from RtratemasterInfo if left blank or 0
            if not obj.va_sale or float(obj.va_sale) == 0:
                enquiry_obj = obj.va_enquirynumber
                vt_id = obj.va_vehicletype_placed_id or obj.va_vehicletype_id
                if enquiry_obj and vt_id:
                    rm = RtratemasterInfo.objects.filter(
                        ro_customer=enquiry_obj.en_customername,
                        ro_customerdepartment=enquiry_obj.en_customerdepartment,
                        ro_fromlocation=enquiry_obj.en_fromlocaion,
                        ro_tolocation=enquiry_obj.en_tolocation,
                        ro_vehicletype_id=vt_id
                    ).first()
                    if not rm:
                        rm = RtratemasterInfo.objects.filter(
                            ro_customer=enquiry_obj.en_customername,
                            ro_fromlocation=enquiry_obj.en_fromlocaion,
                            ro_tolocation=enquiry_obj.en_tolocation,
                            ro_vehicletype_id=vt_id
                        ).first()
                    if rm and rm.ro_rate:
                        obj.va_sale = float(rm.ro_rate)

            # Auto-fill va_special_sale from va_sale if left blank or 0
            if not obj.va_special_sale or float(obj.va_special_sale) == 0:
                if obj.va_sale and float(obj.va_sale) > 0:
                    obj.va_special_sale = float(obj.va_sale)

            # Check for rate approval
            if float(obj.va_special_sale or 0) < float(obj.va_sale or 0):
                rate_approval_status = Replacementstatus.objects.filter(id=6).first()
                if rate_approval_status:
                    obj.va_status = rate_approval_status
            
            # ✅ SAVE
            obj.save()
            sync_allotment_rate_to_trips(obj)


            # ===== AUTO EMAIL TRIGGER (only if Submit & Email clicked) =====
            submit_and_email = request.POST.get('submit_and_email')
            if submit_and_email:
                try:
                    enquiry = EnquirynoteInfo.objects.select_related(
                        'en_customername', 'en_customerdepartment', 'en_fromlocaion', 'en_tolocation'
                    ).get(id=enquiry_id)

                    customer_id = enquiry.en_customername_id if enquiry.en_customername else None
                    department_id = enquiry.en_customerdepartment_id if enquiry.en_customerdepartment else None

                    recipients = get_va_auto_recipients(customer_id, department_id, requestor=enquiry.en_requestor)

                    if recipients:
                        success, result = va_send_allotment_email(obj, enquiry, recipients)
                        if success:
                            obj.va_email_sent = True
                            obj.save(update_fields=['va_email_sent'])
                            messages.success(request,
                                             f"Vehicle Allotment Saved. Alert sent to: {', '.join(recipients)}")
                        else:
                            messages.error(request, f"Vehicle Allotment Saved. Email failed to send: {result}")
                    else:
                        messages.warning(request,
                                         "Vehicle Allotment Saved. No email ID found for this customer in the email master.")
                except Exception as e:
                    messages.success(request, "Vehicle Allotment Saved Successfully")
            else:
                messages.success(request, "Vehicle Allotment Saved Successfully")

            return redirect('vehicle_allotment_update', vehicle_allotment_id=obj.id)

        # ------------------
        # UPDATE MODE
        # ------------------
        else:
            va = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id)
            orig_enquiry_id = va.va_enquirynumber_id
            form = VehicleallotmentForm(request.POST, instance=va)

            if not form.is_valid():
                # Show actual form errors for debugging
                error_msgs = "; ".join([f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()])
                messages.error(request, f"Invalid form data: {error_msgs}")
                referer = request.META.get('HTTP_REFERER')
                return redirect(referer if referer else request.path)

            obj = form.save(commit=False)
            obj.va_enquirynumber_id = orig_enquiry_id

            # 🔒 FREEZE PROTECTION: Always preserve original allotment & driver details on update.
            # Driver/Vehicle replacement MUST be done via the Replace Vehicle / Replace Driver modals.
            obj.va_vehiclesource = va.va_vehiclesource
            obj.va_vehiclenumber = va.va_vehiclenumber
            obj.va_vehiclenumber_mkt = va.va_vehiclenumber_mkt
            obj.va_vendor = va.va_vendor
            obj.va_drivername = va.va_drivername
            obj.va_drivernumber = va.va_drivernumber
            obj.va_driver_lic = va.va_driver_lic
            obj.va_driver_lic_expiry = va.va_driver_lic_expiry
            obj.va_driver_master_id = va.va_driver_master_id
            obj.va_created_at = va.va_created_at

            if request.user and request.user.is_authenticated:
                obj.va_updated_by = request.user

            # Explicitly ensure status is updated from POST if provided
            status_id = request.POST.get('va_status')
            if status_id:
                obj.va_status_id = status_id

            vehicle_source = obj.va_vehiclesource_id
            allotments_to_check = Vehicle_allotmentInfo.objects.none()
            if vehicle_source in [1, 2] and obj.va_vehiclenumber:
                allotments_to_check = Vehicle_allotmentInfo.objects.filter(va_vehiclenumber=obj.va_vehiclenumber)
            elif vehicle_source == 3 and obj.va_vehiclenumber_mkt:
                allotments_to_check = Vehicle_allotmentInfo.objects.filter(va_vehiclenumber_mkt__iexact=obj.va_vehiclenumber_mkt.strip())

            # Filter active checks to only allotments/enquiries created on/after 2026-08-01
            allotments_to_check = allotments_to_check.filter(
                Q(va_created_at__date__gte='2026-08-01') | Q(va_enquirynumber__en_created_at__date__gte='2026-08-01')
            )

            # 🚫 ACTIVE TRIP CHECK FOR THIS VEHICLE (Global - August 1, 2026 onwards)
            is_busy = False
            busy_enquiry = ""
            closed_status_ids = [2, 3, 4, 5, 7, 9, 10, 11]

            reg_no = obj.va_vehiclenumber.vm_registrationnumber if (vehicle_source in [1, 2] and obj.va_vehiclenumber) else (obj.va_vehiclenumber_mkt if vehicle_source == 3 else None)

            if reg_no:
                reg_no_clean = str(reg_no).strip()
                other_trips = TripdetailInfo.objects.filter(
                    Q(tr_created_at__date__gte='2026-08-01') | Q(tr_enquirynumber__en_created_at__date__gte='2026-08-01'),
                    tr_vehiclenumber__iexact=reg_no_clean
                ).exclude(tr_enquirynumber_id=obj.va_enquirynumber_id).select_related('tr_enquirynumber')

                for trip_item in other_trips:
                    enq_status_str = str(trip_item.tr_enquirynumber.en_status) if (trip_item.tr_enquirynumber and trip_item.tr_enquirynumber.en_status) else ""
                    if "Completed" in enq_status_str or "Cancel" in enq_status_str or "Closed" in enq_status_str:
                        continue

                    op_closed = (trip_item.tr_operational_status_id in closed_status_ids) if trip_item.tr_operational_status_id else False
                    fin_closed = (trip_item.tc_financestatus_id in closed_status_ids) if trip_item.tc_financestatus_id else False
                    if not (op_closed or fin_closed):
                        is_busy = True
                        busy_enquiry = trip_item.tr_enquirynumber.en_enquirynumber if trip_item.tr_enquirynumber else str(trip_item.tr_enquirynumber_id)
                        break

            # For UPDATE mode of an already assigned vehicle allotment, allow updating commercial fields (Special Buy, Standard Buy, Sell, Remarks)
            if is_busy and vehicle_allotment_id == 0:
                messages.error(
                    request,
                    f"This vehicle is currently allotted to another active trip/enquiry ({busy_enquiry}) and the trip has not been closed."
                )
                referer = request.META.get('HTTP_REFERER')
                return redirect(referer if referer else request.path)

            # Reset Buy Rates for non-market vehicles (Own & Attached)
            if vehicle_source in [1, 2]:
                obj.va_standardbuy = None
                obj.va_specialbuy = None

            # Auto-fill va_special_sale from va_sale if left blank or 0
            if not obj.va_special_sale or float(obj.va_special_sale) == 0:
                if obj.va_sale and float(obj.va_sale) > 0:
                    obj.va_special_sale = float(obj.va_sale)

            # Check for rate approval
            if float(obj.va_special_sale or 0) < float(obj.va_sale or 0):
                rate_approval_status = Replacementstatus.objects.filter(id=6).first()
                if rate_approval_status:
                    obj.va_status = rate_approval_status

            obj.save()
            sync_allotment_rate_to_trips(obj)

            # Touch the parent enquiry's updated timestamp
            from django.utils import timezone
            en_user = request.user if (request.user and request.user.is_authenticated) else None
            EnquirynoteInfo.objects.filter(id=enquiry_id).update(
                en_updatedon=timezone.now(),
                en_updated_by=en_user
            )

            # ===== AUTO EMAIL TRIGGER (only if Submit & Email clicked) =====
            submit_and_email = request.POST.get('submit_and_email')
            if submit_and_email:
                try:
                    enquiry = EnquirynoteInfo.objects.select_related(
                        'en_customername', 'en_customerdepartment', 'en_fromlocaion', 'en_tolocation'
                    ).get(id=obj.va_enquirynumber_id)

                    customer_id = enquiry.en_customername_id if enquiry.en_customername else None
                    department_id = enquiry.en_customerdepartment_id if enquiry.en_customerdepartment else None

                    recipients = get_va_auto_recipients(customer_id, department_id, requestor=enquiry.en_requestor)

                    if recipients:
                        success, result = va_send_allotment_email(obj, enquiry, recipients)
                        if success:
                            obj.va_email_sent = True
                            obj.save(update_fields=['va_email_sent'])
                            messages.success(request,
                                             f"Vehicle Allotment Updated. Alert sent to: {', '.join(recipients)}")
                        else:
                            messages.error(request, f"Vehicle Allotment Updated. Email failed to send: {result}")
                    else:
                        messages.warning(request,
                                         "Vehicle Allotment Updated. No email ID found for this customer in the email master.")
                except Exception as e:
                    messages.success(request, "Vehicle Allotment Updated Successfully")
            else:
                messages.success(request, "Vehicle Allotment Updated Successfully")

            return redirect('vehicle_allotment_update', vehicle_allotment_id=obj.id)

    # fallback return
    return redirect('enquirynote_list')


# List vehicle_allotment
@login_required(login_url='login_page')
def vehicle_allotment_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    user_ext = User_extInfo.objects.get(user_id=user_id)
    user_role = user_ext.emp_role  # Role object
    user_branch_obj = user_ext.emp_branch  # Location_info object

    # Defensive: Handle missing branch or role
    # Standardized branch code retrieval
    branch_id = get_session_branch_id(request)
    branch_code = get_branch_code(branch_id)

    # Filters from HTML
    enquiry_number = request.GET.get('enquiry_number', '')
    vehicle_number = request.GET.get('vehicle_number', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    select_all = request.GET.get('select_all', '')

    # -----------------------------
    # BASE QUERYSET
    # -----------------------------
    enquirynote_queryset = EnquirynoteInfo.objects.all()

    from datetime import datetime, timedelta

    # Filter by branch if user is not Admin/Superuser and has a branch
    if user_role and user_role.id != 1 and branch_code:
        # Filter by branch
        enquirynote_queryset = enquirynote_queryset.filter(
            en_customername__cu_name__icontains=branch_code
        )

    # -----------------------------
    # Apply search filters
    # -----------------------------
    if enquiry_number:
        enquirynote_queryset = enquirynote_queryset.filter(
            en_enquirynumber__icontains=enquiry_number
        )

    if vehicle_number:
        enquirynote_queryset = enquirynote_queryset.filter(
            Q(vehicle_allotmentinfo__va_vehiclenumber__vm_registrationnumber__icontains=vehicle_number) |
            Q(vehicle_allotmentinfo__va_vehiclenumber_mkt__icontains=vehicle_number) |
            Q(tripdetailinfo__tr_vehiclenumber__icontains=vehicle_number)
        ).distinct()

    if date_from:
        enquirynote_queryset = enquirynote_queryset.filter(
            en_created_at__date__gte=date_from
        )

    if date_to:
        enquirynote_queryset = enquirynote_queryset.filter(
            en_created_at__date__lte=date_to
        )

    # -----------------------------
    # SELECT ALL / FILTERED – No limit
    # -----------------------------
    if select_all == "true" or enquiry_number or vehicle_number or date_from or date_to:
        page_obj = list(enquirynote_queryset.order_by('-en_created_at', '-id'))
    else:
        paginator = Paginator(enquirynote_queryset.order_by('-en_created_at', '-id'), 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number if page_number and page_number.isdigit() else 1)

    enquiry_ids = [enq.id for enq in page_obj]

    # -----------------------------
    # RELATED DATA
    # -----------------------------
    consignment_data = ConsignmentdetailInfo.objects.filter(
        co_enquirynumber_id__in=enquiry_ids
    )

    vehicle_data = Vehicle_allotmentInfo.objects.filter(
        va_enquirynumber__in=enquiry_ids
    ).values_list(
        'va_enquirynumber',
        'va_vehiclenumber__vm_registrationnumber',
        'va_vehiclenumber_mkt',
        'va_status_id',
        'id',
        'va_replaced_allotment_id'
    )

    trip_data = TripdetailInfo.objects.filter(
        tr_enquirynumber_id__in=enquiry_ids
    ).values_list(
        'id',
        'tr_enquirynumber',
        'tr_consignmentnumber__co_consignmentnumber',
        'tr_tripnumber',
        'tc_financestatus__status',
        'tc_financestatus',
        'tr_category__category',
        'tr_vehiclenumber'
    )

    # Find which trips already have a completed invoice
    all_page_trip_ids = [row[0] for row in trip_data]
    invoiced_trip_ids = set(
        TransInvoiceInfo.objects.filter(
            ti_trip_id__in=all_page_trip_ids,
            is_woh=True
        ).values_list('ti_trip_id', flat=True)
    )

    # -----------------------------
    # BUILD VEHICLE DICT (with deduplication)
    # -----------------------------
    # First pass: collect all IDs that have been replaced (i.e., they appear as va_replaced_allotment_id)
    replaced_ids = set()
    for enq_id, reg_num, mkt_num, status_id, va_id, replaced_va_id in vehicle_data:
        if replaced_va_id:
            replaced_ids.add(replaced_va_id)

    vehicle_dict = {}
    for enq_id, reg_num, mkt_num, status_id, va_id, replaced_va_id in vehicle_data:
        v_num = reg_num if reg_num else mkt_num
        if v_num:
            if va_id in replaced_ids:
                display_num = f"{v_num} (replaced)"
            else:
                display_num = v_num

            vehicle_dict.setdefault(enq_id, [])
            # Avoid duplicates: skip if this vehicle number already exists in the list
            if not any(v['number'] == display_num or v['number'] == v_num for v in vehicle_dict[enq_id]):
                vehicle_dict[enq_id].append({
                    'id': va_id,
                    'number': display_num
                })
        else:
            vehicle_dict.setdefault(enq_id, []).append({
                'id': va_id,
                'number': 'None'
            })

    # -----------------------------
    # BUILD TRIP DICT
    # -----------------------------
    trip_dict = {}
    for trip_id, enq_id, trip_cons, trip_num, trip_status, trip_status_id, trip_category, trip_veh_num in trip_data:
        cat_lower = trip_category.strip().lower() if trip_category else ""
        if cat_lower in ["business", "bussiness"]:
            display_text = trip_cons if trip_cons else "No Consignment"
        else:
            display_text = trip_category if trip_category else "No Category"

        display_veh_num = trip_veh_num if trip_veh_num else (trip_num or "No Trip")
        is_invoiced = trip_id in invoiced_trip_ids

        trip_dict.setdefault(enq_id, []).append(
            (display_text, trip_num or "No Trip", trip_status or "", trip_status_id, display_veh_num, is_invoiced)
        )

    # -----------------------------
    # FIND VEHICLE LIMITS
    # -----------------------------
    vehicle_limits = Enquirynotevehicle.objects.filter(
        env_enquirynumber__in=enquiry_ids
    ).values('env_enquirynumber').annotate(total_allowed=Sum('env_quantity'))

    vehicle_limit_dict = {
        v['env_enquirynumber']: v['total_allowed'] for v in vehicle_limits
    }

    vehicle_allotted = Vehicle_allotmentInfo.objects.filter(
        va_enquirynumber__in=enquiry_ids
    ).values('va_enquirynumber').annotate(total_allotted=Count('id'))

    vehicle_allotted_dict = {
        v['va_enquirynumber']: v['total_allotted'] for v in vehicle_allotted
    }

    # -----------------------------
    # FINAL DATA BUILD
    # -----------------------------
    enquiry_data = []
    for enquiry in page_obj:
        vehicles = vehicle_dict.get(enquiry.id, [])
        consignments = consignment_data.filter(co_enquirynumber_id=enquiry.id)

        total_allowed = vehicle_limit_dict.get(enquiry.id, 0)
        total_allotted = vehicle_allotted_dict.get(enquiry.id, 0)
        limit_reached = total_allotted >= total_allowed if total_allowed > 0 else False

        vehicles_with_cons = consignments.values_list('co_vehicelnumber', flat=True).distinct()
        cons_limit_reached = len(vehicles_with_cons) >= len(vehicles) if vehicles else False

        enquiry_data.append({
            'enquiry': enquiry,
            'consignments': consignments,
            'trips': trip_dict.get(enquiry.id, []),
            'vehicles': vehicles,
            'vehicle_limit': total_allowed,
            'vehicle_allotted': total_allotted,
            'limit_reached': limit_reached,
            'consignment_limit_reached': cons_limit_reached,
        })

    return render(
        request,
        "asset_mgt_app/vehicle_allotment_list.html",
        {
            'page_obj': page_obj,
            'first_name': first_name,
            'role': user_role,
            'enquiry_data': enquiry_data,
            'enquiry_number': enquiry_number,
            'vehicle_number': vehicle_number,
            'date_from': date_from,
            'date_to': date_to,
        }
    )


@login_required(login_url='login_page')
def vehicle_allotment_delete(request, vehicle_allotment_id):
    vehicle_allotment = get_object_or_404(Vehicle_allotmentInfo, pk=vehicle_allotment_id)
    enquiry_num = vehicle_allotment.va_enquirynumber

    # Find vehicle registration / identifier
    veh_reg = vehicle_allotment.va_vehiclenumber.vm_registrationnumber if vehicle_allotment.va_vehiclenumber else vehicle_allotment.va_vehiclenumber_mkt

    # 🚫 Check if any trips exist for this enquiry and vehicle
    trips = TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num)
    if veh_reg:
        v_trips = trips.filter(tr_vehiclenumber__iexact=veh_reg)
        if v_trips.exists():
            trips = v_trips

    if trips.exists():
        existing_trip = trips.first()
        trip_no = existing_trip.tr_tripnumber or f"ID {existing_trip.id}"
        messages.error(
            request,
            f"Cannot delete vehicle allotment ({veh_reg or 'Vehicle'}) because trip ({trip_no}) exists. Please delete or cancel the trip first."
        )
        referer = request.META.get('HTTP_REFERER')
        return redirect(referer if referer else '/SMS/vehicle_allotment_list/')

    # ✅ Safe to delete when no trip exists
    reason = request.POST.get('deletion_reason', 'No reason provided')
    identifier = veh_reg or str(vehicle_allotment_id)

    DeletionLog.objects.create(
        dl_model_name='Vehicle_allotmentInfo',
        dl_record_id=vehicle_allotment_id,
        dl_record_identifier=identifier,
        dl_deleted_by=request.user,
        dl_reason=reason
    )

    vehicle_allotment.delete()
    messages.success(request, f"Vehicle allotment ({identifier}) deleted successfully.")
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer if referer else '/SMS/vehicle_allotment_list/')


@login_required(login_url='login_page')
def load_vehicle_source(request):
    vehicletype_placed = request.GET.get('vehicletype_placed')
    print('vehicletype_placed', vehicletype_placed)
    if not vehicletype_placed:
        return HttpResponse(json.dumps({'error': 'Vehicle type not provided'}), status=400)

    vehicle_source_name_list = []
    vehicle_source_id_list = []

    # Fetch vehicles allotted in a trip
    vehicle_allotted_list = list(
        TripdetailInfo.objects.filter(tr_vehiclesource__in=[1, 2], tc_financestatus=1).values_list('tr_vehiclenumber',
                                                                                                   flat=True)
    )

    # Fetch all vehicle master records, avoiding repetitive queries
    vehicle_master_queryset = VehiclemasterInfo.objects.exclude(
        vm_registrationnumber__in=vehicle_allotted_list).select_related('vm_vehicletype', 'vm_ownership')

    # Filter available vehicles by vehicle type
    matching_vehicles = [
        vehicle for vehicle in vehicle_master_queryset
        if vehicle.vm_vehicletype and vehicle.vm_vehicletype.id == int(vehicletype_placed)
    ]

    # Prepare ownership information
    ownership_cache = {}  # Cache ownership info to avoid duplicate queries
    for vehicle in matching_vehicles:
        ownership = vehicle.vm_ownership
        if ownership:
            if ownership.id not in ownership_cache:
                ownership_cache[ownership.id] = ownership.ow_ownership
            if ownership.id not in vehicle_source_id_list:
                vehicle_source_id_list.append(ownership.id)
            if ownership_cache[ownership.id] not in vehicle_source_name_list:
                vehicle_source_name_list.append(ownership_cache[ownership.id])

    # Handle case when no matching vehicles are found
    if not matching_vehicles:
        fallback_ownership = OwnershipInfo.objects.filter(pk=3).first()
        if fallback_ownership:
            if fallback_ownership.id not in vehicle_source_id_list:
                vehicle_source_id_list.append(fallback_ownership.id)
            if fallback_ownership.ow_ownership not in vehicle_source_name_list:
                vehicle_source_name_list.append(fallback_ownership.ow_ownership)

    # Prepare and return response
    data = {
        'vehicle_source_name': vehicle_source_name_list,
        'vehicle_source_id': vehicle_source_id_list,
    }
    return HttpResponse(json.dumps(data))


@login_required(login_url='login_page')
def load_vehicle_number(request):
    vehicletype_placed = request.GET.get('vehicletype_placed')
    vehicletype_source = request.GET.get('vehicletype_source')
    enquiry_id = request.GET.get('enquiry_id')
    current_vehicle_id = request.GET.get('current_vehicle_id')

    # basic validation
    if not vehicletype_placed or not vehicletype_source:
        return JsonResponse({'vehicle_number_list': [], 'vehicle_number_list_id': []})

    # 1) Find all enquiries that have closed/cancelled trips
    closed_status_ids = [2, 3, 4, 5, 7, 9, 10, 11]
    free_enquiry_ids = TripdetailInfo.objects.filter(
        Q(tr_operational_status_id__in=closed_status_ids) | Q(tc_financestatus_id__in=closed_status_ids)
    ).values_list('tr_enquirynumber_id', flat=True)

    # Cutoff date: only allotments created on/after 2026-08-01 are considered for busy status
    from datetime import datetime
    from django.utils.timezone import make_aware
    cutoff_date = make_aware(datetime(2026, 8, 1))

    # 2) Busy allotments are active allotments created on/after cutoff date whose enquiry is NOT in free_enquiry_ids
    # Exclude cancelled (4), replaced (2), completed (5) allotments and dead/cancelled enquiries (5, 8)
    busy_allotments_qs = Vehicle_allotmentInfo.objects.filter(
        va_created_at__gte=cutoff_date
    ).exclude(
        va_enquirynumber_id__in=free_enquiry_ids
    ).exclude(
        va_status_id__in=[2, 4, 5]
    ).exclude(
        va_enquirynumber__en_status_id__in=[5, 8]
    ).exclude(va_vehiclenumber__isnull=True)

    enquiry_veh_ids = set()
    if enquiry_id:
        enquiry_veh_ids = set(Vehicle_allotmentInfo.objects.filter(
            va_enquirynumber_id=enquiry_id,
            va_vehiclenumber__isnull=False
        ).values_list('va_vehiclenumber_id', flat=True))
        busy_allotments_qs = busy_allotments_qs.exclude(va_enquirynumber_id=enquiry_id)

    busy_vehicle_ids = set(busy_allotments_qs.values_list('va_vehiclenumber_id', flat=True)) - enquiry_veh_ids

    if current_vehicle_id:
        try:
            busy_vehicle_ids.discard(int(current_vehicle_id))
        except (ValueError, TypeError):
            pass

    # 3) Get vehicles matching type+ownership (Active only)
    candidate_qs = VehiclemasterInfo.objects.filter(
        Q(vm_status_id=1) | Q(vm_status__isnull=True),
        vm_vehicletype=vehicletype_placed,
        vm_ownership=vehicletype_source
    )
    if current_vehicle_id:
        try:
            curr_vid = int(current_vehicle_id)
            candidate_qs = VehiclemasterInfo.objects.filter(
                (Q(vm_status_id=1) | Q(vm_status__isnull=True) | Q(pk=curr_vid)),
                vm_vehicletype=vehicletype_placed,
                vm_ownership=vehicletype_source
            )
        except (ValueError, TypeError):
            pass

    candidate_qs = candidate_qs.exclude(id__in=busy_vehicle_ids).values_list('id', 'vm_registrationnumber')

    vehicle_data = []
    seen_regs = set()

    for vid, reg in candidate_qs:
        # skip duplicates
        if reg in seen_regs:
            continue

        vehicle_data.append({'id': vid, 'number': reg})
        seen_regs.add(reg)

    return JsonResponse({
        'vehicle_number_list': [v['number'] for v in vehicle_data],
        'vehicle_number_list_id': [v['id'] for v in vehicle_data]
    })


@login_required(login_url='login_page')
def load_driver_details(request):
    vehicle_number = request.GET.get('vehicle_number')

    if not vehicle_number:
        data = {
            'driver_name': [],
            'driver_number': [],
            'driver_license': [],
            'driver_license_exp_date': [],
        }
        return HttpResponse(json.dumps(data))

    driver_name = list(
        VehiclemasterInfo.objects.filter(pk=vehicle_number).values_list('vm_primarydrivername', flat=True))
    driver_number = list(
        VehiclemasterInfo.objects.filter(pk=vehicle_number).values_list('vm_primarydrivermob', flat=True))
    driver_license = list(
        VehiclemasterInfo.objects.filter(pk=vehicle_number).values_list('vm_primarydriver_license', flat=True))

    # Use string conversion to avoid json serialization issues with dates
    driver_license_exp_date = list(
        VehiclemasterInfo.objects.filter(pk=vehicle_number).values_list('vm_primarydriver_license_exp_date', flat=True))
    vendor_id = list(
        VehiclemasterInfo.objects.filter(pk=vehicle_number).values_list('vm_vendor_id', flat=True))

    driver_license_exp_date = [str(d) if d else '' for d in driver_license_exp_date]

    data = {
        'driver_name': driver_name,
        'driver_number': driver_number,
        'driver_license': driver_license,
        'driver_license_exp_date': driver_license_exp_date,
        'vendor_id': vendor_id,
    }
    return HttpResponse(json.dumps(data))


def vehicle_type_counts(request):
    print("I am a vehicle type")
    enquiry_number = request.GET.get('enquiry_number')
    print('Enquiry Number:', enquiry_number)

    # Get sum of env_quantity for each vehicle type
    vehicle_counts = Enquirynotevehicle.objects.filter(env_enquirynumber=enquiry_number).values(
        'env_vehicletype').annotate(total_quantity=Sum('env_quantity'))

    print('Vehicle Counts:', vehicle_counts)

    count_dict = {item['env_vehicletype']: item['total_quantity'] for item in vehicle_counts}
    print('count_dict :', count_dict)
    return JsonResponse({'vehicle_counts': count_dict})


@login_required(login_url='login_page')
def vehicle_requested(request):
    enquiry_number = request.GET.get('enquiry_number')

    requested_vehicles = Enquirynotevehicle.objects.filter(env_enquirynumber=enquiry_number) \
        .values('env_vehicletype__id', 'env_vehicletype__vt_vehicletype', 'env_vehiclecategory__id', 'env_vehiclecategory__vc_vehiclecategory') \
        .annotate(requested_qty=Sum('env_quantity'))

    vehicle_list = []

    for rv in requested_vehicles:
        vehicle_type_id = rv['env_vehicletype__id']
        vehicle_type_name = rv['env_vehicletype__vt_vehicletype']
        vehicle_category_id = rv.get('env_vehiclecategory__id', '')
        vehicle_category_name = rv.get('env_vehiclecategory__vc_vehiclecategory', '')
        requested_qty = rv['requested_qty']

        # FIXED: Use va_enquirynumber_id instead of nested lookup
        allotted_qty = Vehicle_allotmentInfo.objects.filter(
            va_enquirynumber_id=enquiry_number,
            va_vehicletype_id=vehicle_type_id
        ).count()

        remaining = requested_qty - allotted_qty

        if remaining > 0:
            vehicle_list.append({
                'id': vehicle_type_id,
                'name': vehicle_type_name,
                'category_id': vehicle_category_id,
                'category_name': vehicle_category_name,
                'remaining': remaining
            })

    return JsonResponse({'vehicles': vehicle_list})


def get_remaining_quantity(request, enquiry_id, vehicle_type_id):
    enquiry_number = request.GET.get('enquiry_number')
    try:
        # Total requested
        requested = Enquirynotevehicle.objects.filter(
            env_enquirynumber_id=enquiry_id,
            env_vehicletype_id=vehicle_type_id
        ).aggregate(total=Sum('env_quantity'))['total'] or 0

        # Count of allotted vehicles of the same type
        allotted = Vehicle_allotmentInfo.objects.filter(
            va_enquirynumber_id=enquiry_id,
            va_vehicletype_id=vehicle_type_id
        ).count()

        remaining = requested - allotted
        return JsonResponse({'remaining': max(remaining, 0)})

    except Exception as e:
        return JsonResponse({'remaining': 0, 'error': str(e)})


@login_required(login_url='login_page')
def get_vendor_buy_rate(request):
    vehicle_id = request.GET.get('vehicle_id')  # This is actually a vehicle type ID, not the Vehicle_allotmentInfo ID
    vendor_id = request.GET.get('vendor_id')
    enquiry_id = request.GET.get('enquiry_id')  # ✅ NO SESSION
    vehicle_category_id = request.GET.get('vehicle_category_id')

    print("vehicle_id:", vehicle_id)
    print("vendor_id:", vendor_id)
    print("enquiry_id:", enquiry_id)

    enquiry = EnquirynoteInfo.objects.get(id=enquiry_id)

    # Filter for the matching vendor rate
    filter_kwargs = {
        'vr1_vendor_id': vendor_id,
        'vr1_fromlocation': enquiry.en_fromlocaion,
        'vr1_tolocation': enquiry.en_tolocation,
        'vr1_vehicletype': vehicle_id,  # This is likely a ForeignKey ID
        'vr1_touchpoint': enquiry.en_touchpoint,
        'vr1_touchpoint2': enquiry.en_touchpoint2,
        'vr1_touchpoint3': enquiry.en_touchpoint3,
        'vr1_touchpoint4': enquiry.en_touchpoint4
    }
    if vehicle_category_id:
        filter_kwargs['vr1_vehiclecategory_id'] = vehicle_category_id

    rate = VendorratemasterInfo1.objects.filter(**filter_kwargs).first()

    buy_rate = str(rate.vr1_rate) if rate else "0"
    print("Buy Rate:", buy_rate)

    data = {
        'buy_rate': buy_rate,
    }
    return JsonResponse(data)


@login_required(login_url='login_page')
def get_vendor_sale_rate(request):
    checkbox_id = request.GET.get('checkbox_id')  # 'chk_requested' or 'chk_placed'
    vehicle_requested = request.GET.get('vehicle_requested')
    vehicle_placed = request.GET.get('vehicle_placed')
    vendor_id = request.GET.get('vendor_id')
    enquiry_id = request.GET.get('enquiry_id')  # ✅ NO SESSION
    vehicle_category_id = request.GET.get('vehicle_category_id')

    if not enquiry_id:
        return JsonResponse({'sale_rate': "0", 'special_sale_rate': "0"})

    try:
        enquiry = EnquirynoteInfo.objects.get(id=enquiry_id)
    except EnquirynoteInfo.DoesNotExist:
        return JsonResponse({'sale_rate': "0", 'special_sale_rate': "0"})

    # Determine which vehicle type to use based on the checkbox
    if checkbox_id == 'chk_requested':
        vehicle_id = vehicle_requested
    elif checkbox_id == 'chk_placed':
        vehicle_id = vehicle_placed
    else:
        vehicle_id = vehicle_requested or vehicle_placed or request.GET.get('vehicle_id') or request.GET.get('vehicle_type_id')

    if not vehicle_id:
        return JsonResponse({'sale_rate': "0", 'special_sale_rate': "0"})

    # Filter for the matching vendor rate
    filter_kwargs = {
        'ro_customer': enquiry.en_customername,
        'ro_fromlocation': enquiry.en_fromlocaion,
        'ro_tolocation': enquiry.en_tolocation,
        'ro_vehicletype': vehicle_id,  # ForeignKey to vehicle type
        'ro_touchpoint': enquiry.en_touchpoint,
        'ro_touchpoint2': enquiry.en_touchpoint2,
        'ro_touchpoint3': enquiry.en_touchpoint3,
        'ro_touchpoint4': enquiry.en_touchpoint4
    }
    if enquiry.en_customerdepartment:
        filter_kwargs['ro_customerdepartment'] = enquiry.en_customerdepartment
    if vehicle_category_id:
        filter_kwargs['ro_vehiclecategory_id'] = vehicle_category_id

    rate = RtratemasterInfo.objects.filter(**filter_kwargs).first()
    if not rate and enquiry.en_customerdepartment:
        filter_without_dept = {k: v for k, v in filter_kwargs.items() if k != 'ro_customerdepartment'}
        rate = RtratemasterInfo.objects.filter(**filter_without_dept).first()
    master_rate = str(rate.ro_rate) if rate and rate.ro_rate else "0"

    fetch_master_rate = request.GET.get('fetch_master_rate') == '1'

    # Check if Enquirynotevehicle has standard sell & special sale configured for this enquiry
    env_match = Enquirynotevehicle.objects.filter(
        env_enquirynumber=enquiry,
        env_vehicletype_id=vehicle_id
    )
    if vehicle_category_id:
        env_match_cat = env_match.filter(env_vehiclecategory_id=vehicle_category_id)
        if env_match_cat.exists():
            env_match = env_match_cat
    env_obj = env_match.first()

    if not fetch_master_rate and env_obj and env_obj.env_sale is not None and float(env_obj.env_sale) > 0:
        sale_rate = str(env_obj.env_sale)
    else:
        sale_rate = master_rate

    if not fetch_master_rate and env_obj and env_obj.env_special_sale is not None and float(env_obj.env_special_sale) > 0:
        special_sale_rate = str(env_obj.env_special_sale)
    else:
        special_sale_rate = sale_rate

    return JsonResponse({
        'master_rate': master_rate,
        'sale_rate': sale_rate,
        'special_sale_rate': special_sale_rate
    })


@login_required(login_url='login_page')
def vendor_filter(request):
    enquiry_num = request.GET.get('enquiry_num')

    try:
        enquiry = EnquirynoteInfo.objects.get(id=enquiry_num)
        from_location = enquiry.en_fromlocaion
        to_location = enquiry.en_tolocation

        vendors = VendorratemasterInfo1.objects.filter(
            vr1_fromlocation=from_location,
            vr1_tolocation=to_location
        ).select_related('vr1_vendor').values(
            'vr1_vendor__id',
            'vr1_vendor__vend_name'
        ).distinct()

        vendor_list = [
            {'id': v['vr1_vendor__id'], 'name': v['vr1_vendor__vend_name']}
            for v in vendors
        ]

        return JsonResponse({'vendor_filter': vendor_list})

    except EnquirynoteInfo.DoesNotExist:
        return JsonResponse({'vendor_filter': [], 'error': 'Invalid Enquiry Number'}, status=400)
    except EnquirynoteInfo.DoesNotExist:
        return JsonResponse({'vendor_filter': [], 'error': 'Invalid Enquiry Number'}, status=400)


@login_required(login_url='login_page')
def vehicle_allotment_email(request):
    recipient = request.POST.get('recipient')
    va_id = request.POST.get('va_id')

    if not va_id:
        messages.error(request, "Vehicle Allotment ID is missing. Please try again.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        va = Vehicle_allotmentInfo.objects.get(pk=va_id)
    except Vehicle_allotmentInfo.DoesNotExist:
        messages.error(request, "Vehicle allotment record not found.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    # Fetch Enquiry details based on enquiry number
    try:
        enquiry = EnquirynoteInfo.objects.select_related(
            'en_customername',
            'en_customerdepartment',
            'en_fromlocaion',
            'en_tolocation'
        ).get(en_enquirynumber=va.va_enquirynumber)
    except EnquirynoteInfo.DoesNotExist:
        enquiry = None

    customer_name = enquiry.en_customername.cu_name if enquiry else "N/A"
    department_name = enquiry.en_customerdepartment.ct_customerdepartment if enquiry else "N/A"
    from_location = enquiry.en_fromlocaion.place_name if enquiry and enquiry.en_fromlocaion else "N/A"
    to_location = enquiry.en_tolocation.place_name if enquiry and enquiry.en_tolocation else "N/A"

    # Convert recipient string to list
    recipient_list = [email.strip() for email in recipient.split(',') if email.strip()]

    subject = f"Vehicle Allotment Update - {va.va_vehiclenumber}"

    email_body = f"""
        <html>
            <head>
                <style>
                    table {{
                        width: 70%;
                        border-collapse: collapse;
                        font-family: Arial, sans-serif;
                        font-size: 14px;
                        border: 1px solid black;
                        margin-left: auto;
                        margin-right: auto;
                    }}
                    th, td {{
                        border: 1px solid black;
                        padding: 10px;
                    }}
                    th {{
                        background-color: #f4f4f4;
                        color: #333;
                        text-align: left;
                        width: 40%;
                    }}
                    td {{
                        vertical-align: top;
                    }}
                    .remarks div {{
                        margin-bottom: 10px;
                    }}
                </style>
            </head>
            <body>
                <p>Dear Customer,</p>
                <p>Thank you for your business. Below are the booking details for your reference:</p>
                <table>
                    <tr>
                        <th colspan="2" style="background-color: #003366; color: white; padding: 10px; text-align: center; font-size: 18px;">
                            Vehicle Allotment
                        </th>
                    </tr>
                    <tr><th>Customer Name</th><td>{customer_name}</td></tr>
                    <tr><th>Department</th><td>{department_name}</td></tr>
                    <tr><th>From Location</th><td>{from_location}</td></tr>
                    <tr><th>To Location</th><td>{to_location}</td></tr>
                    <tr><th>Vehicle Type</th><td>{va.va_vehicletype}</td></tr>
                    <tr><th>Vehicle Number</th><td>{va.va_vehiclenumber}</td></tr>
                    <tr><th>Driver Name</th><td>{va.va_drivername or 'N/A'}</td></tr>
                    <tr><th>Driver Mobile</th><td>{va.va_drivernumber or 'N/A'}</td></tr>
                    <tr>
                        <th>Remarks</th>
                        <td class="remarks">
                            {''.join(f'<div>{remark}</div>' for remark in (va.va_remarks or '').splitlines()) or 'N/A'}
                        </td>
                    </tr>
                </table>
                <p>Regards,<br>BVM Transport Team</p>
            </body>
        </html>
    """

    # Send email (no attachment for allotment email)
    send_department_email(
        department='itadmin',
        subject=subject,
        message=email_body,
        recipient_list=recipient_list,
        email_type=1
    )

    messages.success(request, "Vehicle Allotment email sent successfully.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='login_page')
def get_vendor_buy_rate(request):
    vendor_id = request.GET.get('vendor_id')
    vehicle_type_id = request.GET.get('vehicle_id')
    enquiry_id = request.GET.get('enquiry_id') or request.session.get('ses_enquiry_id') or request.session.get('enquiry_num_id') or request.session.get('ses_enqiury_id')

    if not vendor_id or not vehicle_type_id or not enquiry_id:
        return JsonResponse({'standard_buy': 0, 'special_buy': 0})

    try:
        enquiry = EnquirynoteInfo.objects.get(id=enquiry_id)
    except EnquirynoteInfo.DoesNotExist:
        return JsonResponse({'standard_buy': 0, 'special_buy': 0})

    rate_obj = VendorratemasterInfo1.objects.filter(
        vr1_vendor_id=vendor_id,
        vr1_fromlocation=enquiry.en_fromlocaion,
        vr1_tolocation=enquiry.en_tolocation,
        vr1_vehicletype_id=vehicle_type_id,
        vr1_touchpoint=enquiry.en_touchpoint,
        vr1_touchpoint2=enquiry.en_touchpoint2,
        vr1_touchpoint3=enquiry.en_touchpoint3,
        vr1_touchpoint4=enquiry.en_touchpoint4
    ).first()

    if not rate_obj:
        return JsonResponse({'standard_buy': 0, 'special_buy': 0})

    rate = float(rate_obj.vr1_rate)

    return JsonResponse({
        'standard_buy': rate,
        'special_buy': rate
    })


@login_required(login_url='login_page')
def get_vendor_by_vehicle(request):
    vehicle_id = request.GET.get('vehicle_id')

    if not vehicle_id:
        return JsonResponse({'vendor_id': '', 'vendor_name': ''})

    try:
        vehicle = VehiclemasterInfo.objects.select_related('vm_vendor').get(id=vehicle_id)

        if vehicle.vm_vendor:
            return JsonResponse({
                'vendor_id': vehicle.vm_vendor.id,
                'vendor_name': vehicle.vm_vendor.vend_name
            })

        return JsonResponse({'vendor_id': '', 'vendor_name': ''})

    except VehiclemasterInfo.DoesNotExist:
        return JsonResponse({'vendor_id': '', 'vendor_name': ''})


def get_decimal(val, default=0):
    try:
        return float(val) if val else default
    except (ValueError, TypeError):
        return default


@login_required(login_url='login_page')
def vehicle_allotment_replace(request, allotment_id):
    """
    Handle full vehicle replacement.
    Creates a new allotment record and marks old as 'Vehicle Replaced'.
    """
    if request.method == "POST":
        try:
            with transaction.atomic():
                old_va = Vehicle_allotmentInfo.objects.select_for_update().get(id=allotment_id)

                existing_replacement = old_va.replacement_chain.order_by('-id').first()
                if old_va.va_status_id == 2 and existing_replacement:
                    return JsonResponse({'success': True, 'new_id': existing_replacement.id})

                old_vehicle_num_check = str(old_va.va_vehiclenumber) if old_va.va_vehiclenumber else (old_va.va_vehiclenumber_mkt or '')
                restricted_trips = TripdetailInfo.objects.filter(
                    tr_enquirynumber=old_va.va_enquirynumber,
                    tc_financestatus_id__in=[4, 5, 7, 9]
                )
                if old_vehicle_num_check:
                    restricted_trips = restricted_trips.filter(tr_vehiclenumber=old_vehicle_num_check)
                if restricted_trips.exists():
                    blocked_trip = restricted_trips.first()
                    status_name = blocked_trip.tc_financestatus.status if blocked_trip.tc_financestatus else "Financial Settlement/Invoicing"
                    return JsonResponse({
                        'success': False,
                        'message': f"🚫 REPLACEMENT BLOCKED: Trip '{blocked_trip.tr_tripnumber or blocked_trip.id}' is currently in '{status_name}'. Vehicle replacement is not permitted after finance processing has started."
                    })

                # Get new details from POST
                new_vehicle_source_id = request.POST.get('va_vehiclesource')
                new_vehicle_id = request.POST.get('va_vehiclenumber')
                new_vehicle_mkt = (request.POST.get('va_vehiclenumber_mkt') or '').strip()
                new_vehicletype_placed_id = request.POST.get('va_vehicletype_placed')
                new_driver_name = request.POST.get('va_drivername')
                new_driver_number = request.POST.get('va_drivernumber')
                new_driver_lic = request.POST.get('va_driver_lic')
                new_driver_lic_expiry = request.POST.get('va_driver_lic_expiry')
                new_driver_master_id = request.POST.get('va_driver_master_id')
                if not new_driver_master_id or not str(new_driver_master_id).strip():
                    new_driver_master_id = None
                new_vendor_id = request.POST.get('va_vendor')
                reason = request.POST.get('reason', '')

                if not reason:
                    return JsonResponse({'success': False, 'message': 'Reason for replacement is required.'})

                # Validate Mandatory Driver License Expiry Date for Own and Attached vehicles
                if str(new_vehicle_source_id) in ['1', '2']:
                    if not new_driver_lic_expiry or not str(new_driver_lic_expiry).strip():
                        return JsonResponse({
                            'success': False,
                            'message': 'Driver License Expiry Date is mandatory for OWN and ATTACHED vehicles.'
                        })

                # Validate Expired License for all drivers
                if new_driver_lic_expiry and is_license_expired(new_driver_lic_expiry):
                    return JsonResponse({
                        'success': False,
                        'message': f"🚫 Cannot complete replacement: Selected driver license expired on {new_driver_lic_expiry}! Please select a driver with a valid license."
                    })

                # Validate vehicle registration format for market vehicles (Temporarily commented out)
                # if str(new_vehicle_source_id) == '3' or new_vehicle_mkt:
                #     if not validate_vehicle_number_format(new_vehicle_mkt):
                #         return JsonResponse({
                #             'success': False,
                #             'message': f"Invalid vehicle number format '{new_vehicle_mkt}'. Format must strictly follow e.g. TN22AB4916 (First 2 letters, next 2 digits, optional 1-2 letters, and final 4 digits)."
                #         })

                # Step 1: Create New Allotment
                new_va = Vehicle_allotmentInfo.objects.create(
                    va_enquirynumber=old_va.va_enquirynumber,
                    va_vehiclesource_id=new_vehicle_source_id,
                    va_vehicletype_id=request.POST.get('va_vehicletype') or old_va.va_vehicletype_id,
                    va_vehicletype_placed_id=new_vehicletype_placed_id if new_vehicletype_placed_id else old_va.va_vehicletype_placed_id,
                    va_vehicletype_selection_requested=True if request.POST.get(
                        'va_vehicletype_selection_requested') == 'on' else False,
                    va_vehicletype_selection_placed=True if request.POST.get(
                        'va_vehicletype_selection_placed') == 'on' else False,
                    va_vehiclenumber_id=new_vehicle_id if new_vehicle_id else None,
                    va_vehiclenumber_mkt=new_vehicle_mkt,
                    va_drivername=new_driver_name,
                    va_drivernumber=new_driver_number,
                    va_driver_lic=new_driver_lic,
                    va_driver_lic_expiry=new_driver_lic_expiry,
                    va_driver_master_id=new_driver_master_id,
                    va_status_id=1,  # Vehicle Assigned (new active allotment)
                    va_replaced_allotment=old_va,
                    va_replacement_reason=reason,
                    va_replacement_date=timezone.now(),
                    va_updated_by_id=request.session.get('ses_userID'),
                    va_vendor_id=new_vendor_id if new_vendor_id else old_va.va_vendor_id,
                    va_sale=get_decimal(request.POST.get('va_sale'), old_va.va_sale),
                    va_special_sale=get_decimal(request.POST.get('va_special_sale'), getattr(old_va, 'va_special_sale', None)) or get_decimal(request.POST.get('va_sale'), old_va.va_sale),
                    va_standardbuy=get_decimal(request.POST.get('va_standardbuy'), old_va.va_standardbuy) if str(new_vehicle_source_id) == '3' else None,
                    va_specialbuy=get_decimal(request.POST.get('va_specialbuy'), old_va.va_specialbuy) if str(new_vehicle_source_id) == '3' else None,
                    va_profit_percentage=get_decimal(request.POST.get('va_profit_percentage'), old_va.va_profit_percentage)
                )

                # Step 2: Mark Old Allotment as Replaced
                old_va.va_status_id = 2  # Vehicle Replaced
                old_va.va_updated_by_id = request.session.get('ses_userID')
                old_va.save()

            # Step 3: Update Active / Linked Trip if exists
            old_vehicle_num = str(old_va.va_vehiclenumber) if old_va.va_vehiclenumber else (old_va.va_vehiclenumber_mkt or '')
            new_vehicle_num = str(new_va.va_vehiclenumber) if new_va.va_vehiclenumber else (new_va.va_vehiclenumber_mkt or '')

            trips = TripdetailInfo.objects.filter(
                tr_enquirynumber=old_va.va_enquirynumber,
                tr_vehiclenumber=old_vehicle_num
            )
            for active_trip in trips:
                active_trip.tr_vehiclenumber = new_vehicle_num
                active_trip.tr_drivername = new_va.va_drivername
                active_trip.tr_drivernumber = new_va.va_drivernumber
                active_trip.tr_driver_master_id = new_va.va_driver_master_id
                current_remarks = active_trip.tr_remarks or ""
                replacement_note = f"\n[AUTO-NOTE] Vehicle replaced from {old_vehicle_num} to {new_vehicle_num} on {timezone.now().strftime('%Y-%m-%d %H:%M')} due to: {reason}"
                active_trip.tr_remarks = (current_remarks + replacement_note)[:250]
                active_trip.save()
            sync_allotment_rate_to_trips(new_va)

            # Step 4: Update Consignment Details if exists & check for E-Way Bill numbers
            consignments = ConsignmentdetailInfo.objects.filter(
                co_enquirynumber=old_va.va_enquirynumber
            ).filter(
                Q(co_vehicelnumber=old_vehicle_num) | Q(co_vehicelnumber__isnull=True) | Q(co_vehicelnumber='')
            )
            
            ewaybill_alert = False
            affected_consignments = []
            if consignments.exists():
                for cons in consignments:
                    has_ebill = ConsignmentgoodsInfo.objects.filter(
                        cg_consignmentnumber=cons,
                        cg_ebillno__isnull=False
                    ).exclude(cg_ebillno='').exists()
                    if has_ebill:
                        ewaybill_alert = True
                        affected_consignments.append(cons.co_consignmentnumber or str(cons.id))
                
                consignments.update(co_vehicelnumber=new_vehicle_num)

                # Reset approval status for linked trips so trip MUST be re-approved after vehicle replacement
                linked_trips = TripdetailInfo.objects.filter(tr_consignmentnumber__in=consignments)
                if linked_trips.exists():
                    pending_status = approval_status_info.objects.filter(pk=2).first() or approval_status_info.objects.first()
                    for t in linked_trips:
                        if t.tr_approval:
                            t.tr_approval.ta_approval_status = pending_status
                            t.tr_approval.save()
                        t.tc_financestatus_id = 8  # Reset finance status to pending approval

            alert_msg = ""
            if ewaybill_alert:
                cons_str = ", ".join(affected_consignments)
                alert_msg = f"⚠️ VEHICLE REPLACED SUCCESSFULLY!\n\nIMPORTANT NOTICE: Consignment(s) [{cons_str}] have existing E-Way Bill details.\nSince the vehicle number changed from {old_vehicle_num} to {new_vehicle_num}, Part-B of the E-Way Bill MUST be updated and re-approved with the revised PDF before departure!"

            return JsonResponse({'success': True, 'new_id': new_va.id, 'ewaybill_alert': ewaybill_alert, 'alert_msg': alert_msg})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


@login_required(login_url='login_page')
def vehicle_allotment_driver_replace(request, allotment_id):
    """
    Handle driver-only replacement.
    """
    if request.method == "POST":
        try:
            with transaction.atomic():
                old_va = Vehicle_allotmentInfo.objects.select_for_update().get(id=allotment_id)

                existing_replacement = old_va.replacement_chain.order_by('-id').first()
                if old_va.va_status_id == 3 and existing_replacement:
                    return JsonResponse({'success': True, 'new_id': existing_replacement.id})

                old_vehicle_num_check = str(old_va.va_vehiclenumber) if old_va.va_vehiclenumber else (old_va.va_vehiclenumber_mkt or '')
                restricted_trips = TripdetailInfo.objects.filter(
                    tr_enquirynumber=old_va.va_enquirynumber,
                    tc_financestatus_id__in=[4, 5, 7, 9]
                )
                if old_vehicle_num_check:
                    restricted_trips = restricted_trips.filter(tr_vehiclenumber=old_vehicle_num_check)
                if restricted_trips.exists():
                    blocked_trip = restricted_trips.first()
                    status_name = blocked_trip.tc_financestatus.status if blocked_trip.tc_financestatus else "Financial Settlement/Invoicing"
                    return JsonResponse({
                        'success': False,
                        'message': f"🚫 REPLACEMENT BLOCKED: Trip '{blocked_trip.tr_tripnumber or blocked_trip.id}' is currently in '{status_name}'. Driver replacement is not permitted after finance processing has started."
                    })

                # Get new details
                new_driver_name = request.POST.get('va_drivername')
                new_driver_number = request.POST.get('va_drivernumber')
                new_driver_lic = request.POST.get('va_driver_lic')
                new_driver_lic_expiry = request.POST.get('va_driver_lic_expiry')
                new_driver_master_id = request.POST.get('va_driver_master_id')
                if not new_driver_master_id or not str(new_driver_master_id).strip():
                    new_driver_master_id = None
                reason = request.POST.get('reason', '')

                if not reason or not new_driver_name:
                    return JsonResponse({'success': False, 'message': 'Reason and New Driver Name are required.'})

                # Validate Mandatory Driver License Expiry Date for Own and Attached vehicles
                if old_va.va_vehiclesource_id in [1, 2]:
                    if not new_driver_lic_expiry or not str(new_driver_lic_expiry).strip():
                        return JsonResponse({
                            'success': False,
                            'message': 'Driver License Expiry Date is mandatory for OWN and ATTACHED vehicles.'
                        })

                # Validate Expired License for all drivers
                if new_driver_lic_expiry and is_license_expired(new_driver_lic_expiry):
                    return JsonResponse({
                        'success': False,
                        'message': f"🚫 Cannot complete driver replacement: Selected driver license expired on {new_driver_lic_expiry}! Please select a driver with a valid license."
                    })

                # Step 1: Create New Allotment Record (new active allotment with Vehicle Assigned status = 1)
                new_va = Vehicle_allotmentInfo.objects.create(
                    va_enquirynumber=old_va.va_enquirynumber,
                    va_vehiclesource=old_va.va_vehiclesource,
                    va_vehicletype=old_va.va_vehicletype,
                    va_vehicletype_placed=old_va.va_vehicletype_placed,
                    va_vehicletype_selection_requested=old_va.va_vehicletype_selection_requested,
                    va_vehicletype_selection_placed=old_va.va_vehicletype_selection_placed,
                    va_vehiclenumber=old_va.va_vehiclenumber,
                    va_vehiclenumber_mkt=old_va.va_vehiclenumber_mkt,
                    va_drivername=new_driver_name,
                    va_drivernumber=new_driver_number,
                    va_driver_lic=new_driver_lic,
                    va_driver_lic_expiry=new_driver_lic_expiry,
                    va_driver_master_id=new_driver_master_id,
                    va_status_id=1,  # Vehicle Assigned (new active record)
                    va_replaced_allotment=old_va,
                    va_replacement_reason=reason,
                    va_replacement_date=timezone.now(),
                    va_updated_by_id=request.session.get('ses_userID'),
                    va_vendor=old_va.va_vendor,
                    va_sale=old_va.va_sale,
                    va_standardbuy=old_va.va_standardbuy,
                    va_specialbuy=old_va.va_specialbuy,
                    va_profit_percentage=old_va.va_profit_percentage
                )

                # Step 2: Mark Old Allotment as Driver Replaced (Status ID 3)
                old_va.va_status_id = 3
                old_va.va_updated_by_id = request.session.get('ses_userID')
                old_va.save()

                # Step 3: Update Active Trip if exists
                vehicle_num = str(old_va.va_vehiclenumber) if old_va.va_vehiclenumber else old_va.va_vehiclenumber_mkt

                active_trip = TripdetailInfo.objects.filter(
                    tr_enquirynumber=old_va.va_enquirynumber,
                    tr_vehiclenumber=vehicle_num,
                    tc_financestatus_id__in=[1, 8]  # Open or Awaiting Approval
                ).first()

                if active_trip:
                    active_trip.tr_drivername = new_driver_name
                    active_trip.tr_drivernumber = new_driver_number
                    active_trip.tr_driver_lic = new_driver_lic
                    active_trip.tr_driver_master_id = new_va.va_driver_master_id
                    active_trip.save()

                return JsonResponse({'success': True, 'new_id': new_va.id})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

@login_required(login_url='login_page')
def sell_rate_approval_list(request):
    allotments = Vehicle_allotmentInfo.objects.filter(va_status_id=6).select_related(
        'va_enquirynumber',
        'va_enquirynumber__en_customername',
        'va_enquirynumber__en_fromlocaion',
        'va_enquirynumber__en_tolocation',
        'va_vehiclenumber'
    ).order_by('-id')
    return render(request, 'asset_mgt_app/sell_rate_approval_list.html', {'vehicle_allotment_list': allotments})

@login_required(login_url='login_page')
def approve_sell_rate(request, va_id):
    va = get_object_or_404(Vehicle_allotmentInfo, pk=va_id)
    approved_status = Replacementstatus.objects.filter(id=1).first()
    if approved_status:
        va.va_status = approved_status
        va.save(update_fields=['va_status'])
        messages.success(request, 'Rate approved successfully and vehicle assigned.')
    else:
        messages.error(request, 'Status "Vehicle Assigned" not found.')
    return redirect('sell_rate_approval_list')
