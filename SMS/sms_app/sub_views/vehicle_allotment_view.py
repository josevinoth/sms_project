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
from ..models import Enquirynotevehicle, TripdetailInfo, OwnershipInfo, User_extInfo, ConsignmentdetailInfo, \
    VehiclemasterInfo, EnquirynoteInfo, Vehicle_allotmentInfo, VendorratemasterInfo1, RtratemasterInfo, VehicletypeInfo
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .send_department_email import send_department_email
from .general_utils import get_branch_code, get_session_branch_id

from ..sub_models.vendor_info_mod import Vendor_info
from ..sub_models.emailmaster_mod import Emailmaster
from ..sub_models.emailtype_mod import Email_type


# ===== HELPER: Get recipients from Emailmaster =====
def get_va_auto_recipients(customer_id, department_id):
    """
    Fetch email recipients from Emailmaster for vehicle allotment alerts.
    Uses Email Type 2 (For alert), matching by Customer + Department.
    Falls back to Customer-only match if no department-specific entry exists.
    """
    if not customer_id:
        return None

    try:
        # Try matching Customer + Department first
        email_entry = Emailmaster.objects.filter(
            Q(em_emailtype_id=2) | Q(em_emailtype__email_type__iexact='For alert'),
            em_Customer_name_id=customer_id,
            em_customerdepartment_id=department_id
        ).first()

        # Fallback to Customer-only match
        if not email_entry:
            email_entry = Emailmaster.objects.filter(
                Q(em_emailtype_id=2) | Q(em_emailtype__email_type__iexact='For alert'),
                em_Customer_name_id=customer_id,
                em_customerdepartment__isnull=True
            ).first()

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
            ),
            'vehicles_data': VehiclemasterInfo.objects.all(),
            'customer_name': enquiry.en_customername.cu_name,
            'from_location': enquiry.en_fromlocaion.place_name if enquiry.en_fromlocaion else "",
            'to_location': enquiry.en_tolocation.place_name if enquiry.en_tolocation else "",
            'all_vehicletypes': VehicletypeInfo.objects.all(),
            'all_vendors': Vendor_info.objects.all(),
        })

    # ---------- UPDATE MODE (GET) ----------
    if request.method == "GET" and vehicle_allotment_id != 0:
        va = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id)
        enquiry_id = va.va_enquirynumber.id

        # Store correct enquiry ID in session
        request.session['ses_enquiry_id'] = enquiry_id
        enquiry = EnquirynoteInfo.objects.get(id=enquiry_id)  # ⬅ Fetch enquiry

        form = VehicleallotmentForm(instance=va)

        return render(request, "asset_mgt_app/vehicle_allotment_add.html", {
            'first_name': first_name,
            'user_id': user_id,
            'vehicle_allotment_form': form,
            'va': va,
            'enquiry_num_id': enquiry_id,
            'vehicle_allotment_list': Vehicle_allotmentInfo.objects.filter(
                va_enquirynumber=enquiry_id
            ),
            'vehicles_data': VehiclemasterInfo.objects.all(),
            'customer_name': enquiry.en_customername.cu_name,
            'from_location': enquiry.en_fromlocaion.place_name if enquiry.en_fromlocaion else "",
            'to_location': enquiry.en_tolocation.place_name if enquiry.en_tolocation else "",
            'all_vehicletypes': VehicletypeInfo.objects.all(),
            'all_vendors': Vendor_info.objects.all(),
        })

    # ---------- POST SAVE (ADD + UPDATE) ----------
    # ---------- POST SAVE (ADD + UPDATE) ----------
    if request.method == "POST":

        enquiry_id = request.session.get('ses_enquiry_id')

        if not enquiry_id:
            messages.error(request, "Enquiry ID missing. Please try again.")
            return redirect(request.META.get('HTTP_REFERER'))

        # ------------------
        # ADD MODE
        # ------------------
        if vehicle_allotment_id == 0:
            form = VehicleallotmentForm(request.POST)

            if not form.is_valid():
                messages.error(request, "Invalid form data")
                return redirect(request.META.get('HTTP_REFERER'))

            obj = form.save(commit=False)
            obj.va_enquirynumber_id = enquiry_id

            # Explicitly ensure status is updated from POST if provided
            status_id = request.POST.get('va_status')
            if status_id:
                obj.va_status_id = status_id

            # 🚫 DUPLICATE VEHICLE CHECK (✅ CORRECT PLACE)
            vehicle_source = obj.va_vehiclesource_id

            duplicate_qs = Vehicle_allotmentInfo.objects.filter(
                va_enquirynumber_id=enquiry_id
            )

            # OWN / ATTACHED
            if vehicle_source in [1, 2] and obj.va_vehiclenumber:
                duplicate_qs = duplicate_qs.filter(
                    va_vehiclenumber=obj.va_vehiclenumber
                )

            # MARKET
            elif vehicle_source == 3 and obj.va_vehiclenumber_mkt:
                duplicate_qs = duplicate_qs.filter(
                    va_vehiclenumber_mkt__iexact=obj.va_vehiclenumber_mkt.strip()
                )

            if duplicate_qs.exists():
                messages.error(
                    request,
                    "This vehicle number is already allotted for this enquiry."
                )
                return redirect(request.META.get('HTTP_REFERER'))

            # ✅ SAVE
            obj.save()

            # ===== AUTO EMAIL TRIGGER (only if Submit & Email clicked) =====
            submit_and_email = request.POST.get('submit_and_email')
            if submit_and_email:
                try:
                    enquiry = EnquirynoteInfo.objects.select_related(
                        'en_customername', 'en_customerdepartment', 'en_fromlocaion', 'en_tolocation'
                    ).get(id=enquiry_id)

                    customer_id = enquiry.en_customername_id if enquiry.en_customername else None
                    department_id = enquiry.en_customerdepartment_id if enquiry.en_customerdepartment else None

                    recipients = get_va_auto_recipients(customer_id, department_id)

                    if recipients:
                        success, result = va_send_allotment_email(obj, enquiry, recipients)
                        if success:
                            obj.va_email_sent = True
                            obj.save(update_fields=['va_email_sent'])
                            messages.success(request,
                                             f"Vehicle Allotment Saved. Alert sent to: {', '.join(recipients)}")
                        else:
                            messages.success(request, "Vehicle Allotment Saved. Email failed to send.")
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
            form = VehicleallotmentForm(request.POST, instance=va)

            if not form.is_valid():
                # Show actual form errors for debugging
                error_msgs = "; ".join([f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()])
                messages.error(request, f"Invalid form data: {error_msgs}")
                return redirect(request.META.get('HTTP_REFERER'))

            obj = form.save(commit=False)

            # Explicitly ensure status is updated from POST if provided
            status_id = request.POST.get('va_status')
            if status_id:
                obj.va_status_id = status_id

            obj.va_enquirynumber = va.va_enquirynumber
            obj.save()

            # ===== AUTO EMAIL TRIGGER (only if Submit & Email clicked) =====
            submit_and_email = request.POST.get('submit_and_email')
            if submit_and_email:
                try:
                    enquiry = EnquirynoteInfo.objects.select_related(
                        'en_customername', 'en_customerdepartment', 'en_fromlocaion', 'en_tolocation'
                    ).get(id=obj.va_enquirynumber_id)

                    customer_id = enquiry.en_customername_id if enquiry.en_customername else None
                    department_id = enquiry.en_customerdepartment_id if enquiry.en_customerdepartment else None

                    recipients = get_va_auto_recipients(customer_id, department_id)

                    if recipients:
                        success, result = va_send_allotment_email(obj, enquiry, recipients)
                        if success:
                            obj.va_email_sent = True
                            obj.save(update_fields=['va_email_sent'])
                            messages.success(request,
                                             f"Vehicle Allotment Updated. Alert sent to: {', '.join(recipients)}")
                        else:
                            messages.success(request, "Vehicle Allotment Updated. Email failed to send.")
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

        # Filter last 30 days only
        today = datetime.today().date()
        last_days = today - timedelta(days=30)

        enquirynote_queryset = enquirynote_queryset.filter(
            en_created_at__date__gte=last_days,
            en_created_at__date__lte=today
        )

    # -----------------------------
    # Apply search filters
    # -----------------------------
    if enquiry_number:
        enquirynote_queryset = enquirynote_queryset.filter(
            en_enquirynumber__icontains=enquiry_number
        )

    if date_from:
        enquirynote_queryset = enquirynote_queryset.filter(
            en_created_at__date__gte=date_from
        )

    if date_to:
        enquirynote_queryset = enquirynote_queryset.filter(
            en_created_at__date__lte=date_to
        )

    # -----------------------------
    # SELECT ALL – No pagination
    # -----------------------------
    if select_all == "true" or date_from or date_to:
        page_obj = enquirynote_queryset.order_by('-en_created_at', '-id')
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
        'id'
    )

    trip_data = TripdetailInfo.objects.filter(
        tr_enquirynumber_id__in=enquiry_ids
    ).values_list(
        'tr_enquirynumber',
        'tr_consignmentnumber__co_consignmentnumber',
        'tr_tripnumber',
        'tc_financestatus__status',
        'tc_financestatus',
        'tr_category__category',
        'tr_vehiclenumber'
    )

    # -----------------------------
    # BUILD VEHICLE DICT
    # -----------------------------
    vehicle_dict = {}
    for enq_id, reg_num, mkt_num, va_id in vehicle_data:
        display_num = reg_num or mkt_num or "None"
        vehicle_dict.setdefault(enq_id, []).append({
            'id': va_id,
            'number': display_num
        })

    # -----------------------------
    # BUILD TRIP DICT
    # -----------------------------
    trip_dict = {}
    for enq_id, trip_cons, trip_num, trip_status, trip_status_id, trip_category, trip_veh_num in trip_data:
        cat_lower = trip_category.strip().lower() if trip_category else ""
        if cat_lower in ["business", "bussiness"]:
            display_text = trip_cons if trip_cons else "No Consignment"
        else:
            display_text = trip_category if trip_category else "No Category"

        display_veh_num = trip_veh_num if trip_veh_num else (trip_num or "No Trip")

        trip_dict.setdefault(enq_id, []).append(
            (display_text, trip_num or "No Trip", trip_status or "", trip_status_id, display_veh_num)
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
            'date_from': date_from,
            'date_to': date_to,
        }
    )


# Delete vehicle_allotment
@login_required(login_url='login_page')
def vehicle_allotment_delete(request, vehicle_allotment_id):
    vehicle_allotment = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id)
    enquiry_num = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id).va_enquirynumber
    enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
    vehicle_allotment.delete()
    # vehicle_allotment_list = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_num_id).values_list('va_vehiclenumber',flat=True))
    # vehicle_numbers = []
    # for i in vehicle_allotment_list:
    #     vehicle_numbers.append(str(VehiclemasterInfo.objects.get(id=i).vm_registrationnumber))
    # try:
    #     EnquirynoteInfo.objects.filter(id=enquiry_num_id).update(en_vehicle_allotment=vehicle_numbers)
    # except ObjectDoesNotExist:
    #     EnquirynoteInfo.objects.filter(id=enquiry_num_id).update(en_vehicle_allotment=vehicle_numbers)

    # return redirect('/SMS/vehicle_allotment_list')
    return redirect(request.META['HTTP_REFERER'])


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

    # basic validation
    if not vehicletype_placed or not vehicletype_source:
        return JsonResponse({'vehicle_number_list': [], 'vehicle_number_list_id': []})

    # 1) registration numbers that are in closed (2) or settled (7) trips for the given type+source
    inactive_regs = TripdetailInfo.objects.filter(
        tc_financestatus_id__in=[2, 3, 4, 6, 7],
        tr_vehicletype_placed=vehicletype_placed,
        tr_vehiclesource=vehicletype_source,
        tr_vehiclenumber__isnull=False
    ).values_list('tr_vehiclenumber', flat=True).distinct()
    inactive_regs = list(inactive_regs)

    # 2) registration numbers that are currently active (exclude these, EXCEPT for the current enquiry)
    active_regs_qs = TripdetailInfo.objects.filter(
        tc_financestatus_id=1,
        tr_vehiclenumber__isnull=False
    )
    if enquiry_id:
        active_regs_qs = active_regs_qs.exclude(tr_enquirynumber_id=enquiry_id)

    active_regs = list(active_regs_qs.values_list('tr_vehiclenumber', flat=True))

    # 3) Get vehicles matching type+ownership
    candidate_qs = VehiclemasterInfo.objects.filter(
        vm_vehicletype=vehicletype_placed,
        vm_ownership=vehicletype_source
    ).values_list('id', 'vm_registrationnumber')

    vehicle_data = []
    seen_regs = set()

    for vid, reg in candidate_qs:
        # skip duplicates
        if reg in seen_regs:
            continue

        # Skip vehicles that are currently active in a trip
        if reg in active_regs:
            continue

        # Add hint if it was in closed/settled trips
        label = reg
        if reg in inactive_regs:
            label = f"{reg}"

        vehicle_data.append({'id': vid, 'number': label})
        seen_regs.add(reg)

    return JsonResponse({
        'vehicle_number_list': [v['number'] for v in vehicle_data],
        'vehicle_number_list_id': [v['id'] for v in vehicle_data]
    })


@login_required(login_url='login_page')
def load_driver_details(request):
    vehicle_number = request.GET.get('vehicle_number')
    driver_name = list(
        VehiclemasterInfo.objects.filter(pk=vehicle_number).values_list('vm_primarydrivername', flat=True))
    driver_number = list(
        VehiclemasterInfo.objects.filter(pk=vehicle_number).values_list('vm_primarydrivermob', flat=True))
    driver_license = list(
        VehiclemasterInfo.objects.filter(pk=vehicle_number).values_list('vm_primarydriver_license', flat=True))
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
        .values('env_vehicletype__id', 'env_vehicletype__vt_vehicletype') \
        .annotate(requested_qty=Sum('env_quantity'))

    vehicle_list = []

    for rv in requested_vehicles:
        vehicle_type_id = rv['env_vehicletype__id']
        vehicle_type_name = rv['env_vehicletype__vt_vehicletype']
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

    print("vehicle_id:", vehicle_id)
    print("vendor_id:", vendor_id)
    print("enquiry_id:", enquiry_id)

    enquiry = EnquirynoteInfo.objects.get(id=enquiry_id)

    # Filter for the matching vendor rate
    rate = VendorratemasterInfo1.objects.filter(
        vr1_vendor_id=vendor_id,
        vr1_fromlocation=enquiry.en_fromlocaion,
        vr1_tolocation=enquiry.en_tolocation,
        vr1_vehicletype=vehicle_id  # This is likely a ForeignKey ID
    ).first()

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

    if not enquiry_id:
        return JsonResponse({'sale_rate': "0"})

    enquiry = EnquirynoteInfo.objects.get(id=enquiry_id)

    # Determine which vehicle type to use based on the checkbox
    if checkbox_id == 'chk_requested':
        vehicle_id = vehicle_requested
    elif checkbox_id == 'chk_placed':
        vehicle_id = vehicle_placed
    else:
        return JsonResponse({'sale_rate': "0"})

    if not vehicle_id:
        return JsonResponse({'sale_rate': "0"})

    # Filter for the matching vendor rate
    rate = RtratemasterInfo.objects.filter(
        ro_customer=enquiry.en_customername,
        ro_fromlocation=enquiry.en_fromlocaion,
        ro_tolocation=enquiry.en_tolocation,
        ro_vehicletype=vehicle_id  # ForeignKey to vehicle type
    ).first()

    sale_rate = str(rate.ro_rate) if rate else "0"

    return JsonResponse({'sale_rate': sale_rate})


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
    enquiry_id = request.session.get('ses_enquiry_id')

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
        vr1_vehicletype_id=vehicle_type_id
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

                # Get new details from POST
                new_vehicle_source_id = request.POST.get('va_vehiclesource')
                new_vehicle_id = request.POST.get('va_vehiclenumber')
                new_vehicle_mkt = request.POST.get('va_vehiclenumber_mkt')
                new_vehicletype_placed_id = request.POST.get('va_vehicletype_placed')
                new_driver_name = request.POST.get('va_drivername')
                new_driver_number = request.POST.get('va_drivernumber')
                new_driver_lic = request.POST.get('va_driver_lic')
                new_driver_lic_expiry = request.POST.get('va_driver_lic_expiry')
                new_vendor_id = request.POST.get('va_vendor')
                reason = request.POST.get('reason', '')

                if not reason:
                    return JsonResponse({'success': False, 'message': 'Reason for replacement is required.'})

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
                    va_status_id=2,  # Vehicle Replaced
                    va_replaced_allotment=old_va,
                    va_replacement_reason=reason,
                    va_replacement_date=timezone.now(),
                    va_updated_by_id=request.session.get('ses_userID'),
                    va_vendor=old_va.va_vendor,
                    va_sale=get_decimal(request.POST.get('va_sale'), old_va.va_sale),
                    va_standardbuy=get_decimal(request.POST.get('va_standardbuy'), old_va.va_standardbuy),
                    va_specialbuy=get_decimal(request.POST.get('va_specialbuy'), old_va.va_specialbuy),
                    va_profit_percentage=get_decimal(request.POST.get('va_profit_percentage'), old_va.va_profit_percentage)
                )

                # Step 2: Mark Old Allotment as Replaced
                old_va.va_status_id = 2  # Vehicle Replaced
                old_va.save()

            # Step 3: Update Active Trip if exists
            old_vehicle_num = str(old_va.va_vehiclenumber) if old_va.va_vehiclenumber else old_va.va_vehiclenumber_mkt
            new_vehicle_num = str(new_va.va_vehiclenumber) if new_va.va_vehiclenumber else new_va.va_vehiclenumber_mkt

            active_trip = TripdetailInfo.objects.filter(
                tr_enquirynumber=old_va.va_enquirynumber,
                tr_vehiclenumber=old_vehicle_num,
                tc_financestatus_id__in=[1, 8]  # Open or Awaiting Approval
            ).first()

            if active_trip:
                active_trip.tr_vehiclenumber = new_vehicle_num
                active_trip.tr_drivername = new_va.va_drivername
                active_trip.tr_drivernumber = new_va.va_drivernumber

                # Update remarks to reflect replacement
                current_remarks = active_trip.tr_remarks or ""
                replacement_note = f"\n[AUTO-NOTE] Vehicle replaced from {old_vehicle_num} to {new_vehicle_num} on {timezone.now().strftime('%Y-%m-%d %H:%M')} due to: {reason}"
                active_trip.tr_remarks = (current_remarks + replacement_note)[:250]
                active_trip.save()

            # Step 4: Update Consignment Details if exists
            ConsignmentdetailInfo.objects.filter(
                co_enquirynumber=old_va.va_enquirynumber,
                co_vehicelnumber=old_vehicle_num
            ).update(co_vehicelnumber=new_vehicle_num)

            return JsonResponse({'success': True, 'new_id': new_va.id})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})


@login_required(login_url='login_page')
def vehicle_allotment_driver_replace(request, allotment_id):
    """
    Handle driver-only replacement.
    """
    if request.method == "POST":
        try:
            old_va = Vehicle_allotmentInfo.objects.get(id=allotment_id)

            # Get new details
            new_driver_name = request.POST.get('va_drivername')
            new_driver_number = request.POST.get('va_drivernumber')
            new_driver_lic = request.POST.get('va_driver_lic')
            new_driver_lic_expiry = request.POST.get('va_driver_lic_expiry')
            reason = request.POST.get('reason', '')

            if not reason or not new_driver_name:
                return JsonResponse({'success': False, 'message': 'Reason and New Driver Name are required.'})

            # Step 1: Create New Allotment Record (cloning old details but with new driver)
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
                va_status_id=3,  # Driver Replaced
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
                active_trip.save()

            return JsonResponse({'success': True, 'new_id': new_va.id})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
