import base64
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.core.files.base import ContentFile
from django.db.models import Q
from django.utils.timezone import make_aware
from django.utils import timezone

from .send_department_email import send_department_email
from ..forms import TripclosurefilesForm, TripdetailaddForm
from ..models import Vehicle_allotmentInfo, ConsignmentdetailInfo, ConsignmentgoodsInfo, Tripstatusinfo, Trip_closure_files_Info, \
    EnquirynoteInfo, TripdetailInfo, VehiclemasterInfo, TripHighvalueInfo, Emailmaster, Email_type, User_extInfo, TransInvoiceInfo, DeletionLog
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
import json
from .general_utils import get_financial_year, get_branch_code, generate_next_number, get_session_branch_id


def format_email_date(dt):
    if not dt:
        return ""

    try:
        # Convert to local timezone (IST)
        local_dt = timezone.localtime(dt)
        return local_dt.strftime("%d-%m-%Y %H:%M")
    except Exception:
        return str(dt)


@login_required(login_url='login_page')
def tripdetail_enquiry(request, enquiry_id, trip_num):
    # Fetch the enquiry object (optional - only needed if you want to verify or log it)
    enquiry = get_object_or_404(EnquirynoteInfo, pk=enquiry_id)

    # If no trip is associated, store enquiry ID in session and redirect to insert
    if trip_num == 'none' or trip_num == '':
        request.session['enquiry_num_id'] = enquiry_id
        return redirect(f"{reverse('tripdetail_insert')}?enq_id={enquiry_id}")
    else:
        trip = TripdetailInfo.objects.filter(
            tr_enquirynumber=enquiry,
            tr_tripnumber=trip_num,
        ).order_by('-tr_consignmentnumber_id', '-id').first()
        if not trip:
            request.session['enquiry_num_id'] = enquiry_id
            messages.warning(request,
                             "Trip number was not found for this enquiry. Please create or select the trip again.")
            return redirect(f"{reverse('tripdetail_insert')}?enq_id={enquiry_id}")

        trip_id = trip.id
        print('trip_id:', trip_id)
        # If trip_id is provided, redirect to update
        return redirect('tripdetail_update', tripdetail_id=trip_id)  # tripdetail_id is a keyword argument in the URL


@login_required(login_url='login_page')
def tripdetail_nav(request, tripdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print("I am inside Get add tripetails")
    trip_det_form = TripdetailaddForm()
    tripclosurefiles_form = TripclosurefilesForm()
    enquiry_num_id = tripdetail_id
    request.session['enquiry_num_id'] = enquiry_num_id
    tripdetail_list = TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num_id)
    status_list = Tripstatusinfo.objects.filter(id__in=[1, 2, 8])
    consignment_list = ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id)
    context = {
        'first_name': first_name,
        'user_id': user_id,
        'trip_det_form': trip_det_form,
        'tripclosurefiles_form': tripclosurefiles_form,
        'enquiry_num_id': enquiry_num_id,
        'tripdetail_list': tripdetail_list,
        'status_list': status_list,
        'consignment_list': consignment_list,
    }
    return render(request, "asset_mgt_app/tripdetail_add.html", context)


@login_required(login_url='login_page')
def tripdetail_add(request, tripdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID') or (request.user.id if request.user.is_authenticated else '')

    enq_id_param = request.GET.get('enq_id') or request.GET.get('enquiry_num_id')
    if enq_id_param:
        try:
            enquiry_num_id = int(enq_id_param)
        except (ValueError, TypeError):
            enquiry_num_id = None
        if enquiry_num_id:
            request.session['enquiry_num_id'] = enquiry_num_id
            request.session['ses_enqiury_id'] = enquiry_num_id
            try:
                enquiry = EnquirynoteInfo.objects.get(pk=enquiry_num_id)
                request.session['ses_enqiury_num'] = enquiry.en_enquirynumber
            except ObjectDoesNotExist:
                pass
    else:
        enquiry_num_id = request.session.get('enquiry_num_id')

    # Fallback to string-based session key if needed (though we should avoid this)
    if not enquiry_num_id:
        string_enq_num = request.session.get('ses_enqiury_id')
        if string_enq_num:
            enq_obj = EnquirynoteInfo.objects.filter(en_enquirynumber=string_enq_num).first()
            if enq_obj:
                enquiry_num_id = enq_obj.id

    # ✅ Always refresh session with current enquiry_num_id for consistency
    if enquiry_num_id:
        request.session['enquiry_num_id'] = enquiry_num_id
    else:
        # If no enquiry ID is found, inform the user and redirect to the list.
        # This message will now be displayed and cleared once on the next page.
        messages.warning(request, "No enquiry number found in session. Please select an enquiry from the list first.")
        return redirect('enquirynote_list')

    if request.method == "GET":
        if tripdetail_id == 0:
            print("I am inside Get add tripdetails")
            vehicle_allotment_id = request.GET.get('vehicle_allotment_id')

            selected_vehicle_number = None
            initial_data = {'tr_high_value': 2}
            if vehicle_allotment_id:
                try:
                    va = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id)
                    # Choose correct vehicle registration string
                    selected_vehicle_number = va.va_vehiclenumber_mkt if va.va_vehiclesource_id == 3 else (va.va_vehiclenumber.vm_registrationnumber if va.va_vehiclenumber else '')

                    initial_data.update({
                        'tr_vehiclenumber': selected_vehicle_number,
                        'tr_drivername': va.va_drivername,
                        'tr_driver_master_id': va.va_driver_master_id,
                        'tr_vehicletype': va.va_vehicletype,
                        'tr_vehiclesource': va.va_vehiclesource,
                        'tr_vehicletype_placed': va.va_vehicletype_placed,
                        'tr_drivernumber': va.va_drivernumber,
                        'tr_driver_lic': va.va_driver_lic,
                        'tr_category': 1 if va.va_vehiclesource_id == 3 else 2,
                    })
                except Vehicle_allotmentInfo.DoesNotExist:
                    pass

            # Fetch latest reported KM for this vehicle from its last completed trip
            search_vehicle_num = selected_vehicle_number
            last_trip_km = None
            if search_vehicle_num:
                last_trip_km = TripdetailInfo.objects.filter(
                    tr_vehiclenumber=search_vehicle_num
                ).filter(
                    Q(tr_reportedkm__isnull=False) | Q(tr_reportedkm_delivery__isnull=False)
                ).order_by('-id').first()

            if last_trip_km:
                latest_km = last_trip_km.tr_reportedkm or last_trip_km.tr_reportedkm_delivery
                if latest_km:
                    initial_data['tr_reportedkm_pickup'] = latest_km
                    initial_data['tr_departedkm'] = latest_km

            trip_det_form = TripdetailaddForm(initial=initial_data)
            if vehicle_allotment_id and va.va_vehiclesource_id != 3:
                trip_det_form.fields['tr_category'].widget.attrs['readonly'] = True

            # Ensure departed location matches the vehicle's last reported location
            location_locked = False
            if vehicle_allotment_id and selected_vehicle_number and va.va_vehiclesource_id != 3:
                last_trip_loc = TripdetailInfo.objects.filter(
                    tr_vehiclenumber=search_vehicle_num
                ).exclude(tr_reportedlocation__isnull=True).order_by('-tr_created_at').first()

                if last_trip_loc:
                    trip_det_form.fields['tr_departedlocation'].initial = last_trip_loc.tr_reportedlocation
                    trip_det_form.fields['tr_departedlocation'].widget.attrs.update({
                        'style': 'pointer-events: none; background-color: #e9ecef;',
                        'onmousedown': 'return false;',
                        'onkeydown': 'return false;',
                        'readonly': 'readonly'
                    })
                    location_locked = True
                else:
                    previous_trip = TripdetailInfo.objects.filter(
                        tr_enquirynumber_id=enquiry_num_id
                    ).order_by('-tr_created_at').first()
                    if previous_trip and previous_trip.tr_reportedlocation:
                        trip_det_form.fields['tr_departedlocation'].initial = previous_trip.tr_reportedlocation
            else:
                previous_trip = TripdetailInfo.objects.filter(
                    tr_enquirynumber_id=enquiry_num_id
                ).order_by('-tr_created_at').first()
                if previous_trip and previous_trip.tr_reportedlocation:
                    trip_det_form.fields['tr_departedlocation'].initial = previous_trip.tr_reportedlocation

            tripclosurefiles_form = TripclosurefilesForm()
            trip_list = TripdetailInfo.objects.select_related(
                'tr_approval', 'tr_approval__ta_approval_status'
            ).filter(tr_enquirynumber=enquiry_num_id)
            status_list = Tripstatusinfo.objects.filter(id__in=[1, 2, 8, 10, 11])

            # ✅ Exclude already-used consignments for this enquiry
            used_consignments = TripdetailInfo.objects.filter(
                tr_enquirynumber=enquiry_num_id
            ).exclude(tr_consignmentnumber__isnull=True).values_list('tr_consignmentnumber_id', flat=True)

            consignment_list = ConsignmentdetailInfo.objects.filter(
                co_enquirynumber=enquiry_num_id
            ).exclude(id__in=used_consignments)

            trip_det_form.fields['tr_enquirynumber'].queryset = EnquirynoteInfo.objects.filter(id=enquiry_num_id)
            trip_det_form.fields['tr_consignmentnumber'].queryset = consignment_list

            # Build allotted vehicle list for Enquiry
            allotted_vas = Vehicle_allotmentInfo.objects.filter(
                va_enquirynumber=enquiry_num_id,
                va_status_id__in=[1, 2, 3]
            ).select_related('va_vehiclenumber', 'va_vehiclesource', 'va_vehicletype', 'va_vehicletype_placed')

            # Find vehicles that have a cancelled trip for this enquiry so they cannot create another trip
            cancelled_vehicles = set(
                TripdetailInfo.objects.filter(
                    tr_enquirynumber=enquiry_num_id
                ).filter(
                    Q(tc_cancellation_check=True) | Q(tc_financestatus_id__in=[10, 11]) | Q(tr_operational_status_id__in=[10, 11])
                ).values_list('tr_vehiclenumber', flat=True)
            )

            # Find vehicles that ALREADY have an active/existing Business trip for this enquiry
            # Category 1 = Business trip
            assigned_business_vehicles = set(
                TripdetailInfo.objects.filter(
                    tr_enquirynumber=enquiry_num_id,
                    tr_category_id=1
                ).exclude(
                    tc_cancellation_check=True
                ).exclude(
                    tc_financestatus_id__in=[10, 11]
                ).values_list('tr_vehiclenumber', flat=True)
            )

            allotted_vehicle_list = []
            allotted_vehicle_map = {}
            for va_item in allotted_vas:
                reg_num = va_item.va_vehiclenumber_mkt if va_item.va_vehiclesource_id == 3 else (va_item.va_vehiclenumber.vm_registrationnumber if va_item.va_vehiclenumber else '')
                # Exclude vehicle if it was cancelled or already has an active Business trip
                if reg_num and reg_num not in allotted_vehicle_map:
                    if reg_num in cancelled_vehicles and reg_num != selected_vehicle_number:
                        continue
                    if reg_num in assigned_business_vehicles and reg_num != selected_vehicle_number:
                        continue

                    item_info = {
                        'reg_number': reg_num,
                        'is_mkt': va_item.va_vehiclesource_id == 3,
                        'vehiclesource_id': va_item.va_vehiclesource_id,
                        'vehiclesource_name': str(va_item.va_vehiclesource) if va_item.va_vehiclesource else '',
                        'vehicletype_id': va_item.va_vehicletype_id if va_item.va_vehicletype else None,
                        'vehicletype_placed_id': va_item.va_vehicletype_placed_id if va_item.va_vehicletype_placed else None,
                        'driver_name': va_item.va_drivername or '',
                        'driver_number': va_item.va_drivernumber or '',
                        'driver_lic': va_item.va_driver_lic or '',
                        'driver_master_id': va_item.va_driver_master_id
                    }
                    allotted_vehicle_list.append(item_info)
                    allotted_vehicle_map[reg_num] = item_info

            import json
            allotted_vehicle_map_json = json.dumps(allotted_vehicle_map)

            context = {
                'first_name': first_name,
                'user_id': user_id,
                'trip_det_form': trip_det_form,
                'tripclosurefiles_form': tripclosurefiles_form,
                'enquiry_num_id': enquiry_num_id,
                'trip_list': trip_list,
                'status_list': status_list,
                'consignment_list': consignment_list,
                'tripdetail_list': TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num_id),
                'status_selected': 1 if initial_data.get('tr_category') in [2, 3] else 8,
                'location_locked': location_locked,
                'allotted_vehicle_list': allotted_vehicle_list,
                'allotted_vehicle_map_json': allotted_vehicle_map_json,
                'selected_vehicle_number': selected_vehicle_number,
                'vehicle_allotment_id': vehicle_allotment_id,
            }

        else:
            trip_num = TripdetailInfo.objects.get(pk=tripdetail_id).tr_tripnumber
            enquiry_num = TripdetailInfo.objects.get(pk=tripdetail_id).tr_enquirynumber
            enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
            tripdetail = TripdetailInfo.objects.get(pk=tripdetail_id)

            # ✅ Sync Driver/Vehicle info with LATEST Allotment if trip is not closed
            # (Statuses: 1: Open/Started, 8: Awaiting Approval)
            if tripdetail.tc_financestatus_id in [1, 8] and tripdetail.tr_consignmentnumber:
                truck_number = tripdetail.tr_consignmentnumber.co_vehicelnumber
                if truck_number:
                    latest_allotment = Vehicle_allotmentInfo.objects.filter(
                        va_enquirynumber=enquiry_num_id
                    ).filter(
                        Q(va_vehiclenumber__vm_registrationnumber=truck_number.strip()) | Q(
                            va_vehiclenumber_mkt=truck_number.strip())
                    ).last()

                    if latest_allotment:
                        needs_save = False
                        if tripdetail.tr_drivername != latest_allotment.va_drivername:
                            tripdetail.tr_drivername = latest_allotment.va_drivername
                            needs_save = True
                        if tripdetail.tr_drivernumber != latest_allotment.va_drivernumber:
                            tripdetail.tr_drivernumber = latest_allotment.va_drivernumber
                            needs_save = True
                        if tripdetail.tr_driver_lic != latest_allotment.va_driver_lic:
                            tripdetail.tr_driver_lic = latest_allotment.va_driver_lic
                            needs_save = True
                        if tripdetail.tr_vehiclenumber != truck_number:
                            tripdetail.tr_vehiclenumber = truck_number
                            needs_save = True
                        if tripdetail.tr_vehiclesource != latest_allotment.va_vehiclesource:
                            tripdetail.tr_vehiclesource = latest_allotment.va_vehiclesource
                            needs_save = True
                        if tripdetail.tr_vehicletype != latest_allotment.va_vehicletype:
                            tripdetail.tr_vehicletype = latest_allotment.va_vehicletype
                            needs_save = True
                        if tripdetail.tr_vehicletype_placed != latest_allotment.va_vehicletype_placed:
                            tripdetail.tr_vehicletype_placed = latest_allotment.va_vehicletype_placed
                            needs_save = True

                        if needs_save:
                            tripdetail.save()
                            en_user = request.user if (request.user and request.user.is_authenticated) else None
                            EnquirynoteInfo.objects.filter(id=tripdetail.tr_enquirynumber_id).update(
                                en_updatedon=timezone.now(),
                                en_updated_by=en_user
                            )

            request.session['ses_tripdetail_id'] = tripdetail_id

            trip_det_form = TripdetailaddForm(instance=tripdetail)
            tripclosure_files = Trip_closure_files_Info.objects.filter(tcf_tripnumber=trip_num).first()
            tripclosurefiles_form = TripclosurefilesForm(instance=tripclosure_files)
            trip_list = TripdetailInfo.objects.select_related(
                'tr_approval', 'tr_approval__ta_approval_status'
            ).filter(tr_enquirynumber=enquiry_num_id)
            trip_instance = TripdetailInfo.objects.get(pk=tripdetail_id)
            try:
                if trip_instance.tr_operational_status:
                    status_selected = trip_instance.tr_operational_status.id
                else:
                    status_selected = trip_instance.tc_financestatus.id if trip_instance.tc_financestatus else 8
                    # Fallback mapping for older records
                    if status_selected in [4, 5, 6, 7, 9]:
                        status_selected = 2

                # Auto-progress logic for Open/Started trips
                if status_selected == 1:
                    if trip_instance.tr_reporteddate_pickup:
                        status_selected = 2  # Trip Closed

                print('status_selected (auto)', status_selected)
            except ObjectDoesNotExist:
                status_selected = None
            if status_selected == 8:
                allowed_statuses = [8, 10, 11]
            else:
                allowed_statuses = [1, 2, 8, 10, 11]
            if status_selected and status_selected not in allowed_statuses:
                allowed_statuses.append(status_selected)

            status_list = Tripstatusinfo.objects.filter(id__in=allowed_statuses)

            consignment_selected = trip_instance.tr_consignmentnumber.id if trip_instance.tr_consignmentnumber else None

            # ✅ Exclude already-used consignments, but keep current one visible
            used_consignments = TripdetailInfo.objects.filter(
                tr_enquirynumber=enquiry_num_id
            ).exclude(tr_consignmentnumber__isnull=True).exclude(
                tr_consignmentnumber=trip_instance.tr_consignmentnumber
            ).values_list('tr_consignmentnumber_id', flat=True)

            consignment_list = ConsignmentdetailInfo.objects.filter(
                co_enquirynumber=enquiry_num_id
            ).exclude(id__in=used_consignments)

            trip_det_form.fields['tr_enquirynumber'].queryset = EnquirynoteInfo.objects.filter(id=enquiry_num_id)
            trip_det_form.fields['tr_consignmentnumber'].queryset = consignment_list

            # ⚠️ Fixed missing newline before this line
            checklist = TripHighvalueInfo.objects.filter(
                thc_tripnumber=trip_instance.id,
                thc_enquirynumber=enquiry_num_id
            ).order_by('-id').first()

            trip_approvallist = (
                trip_instance.tr_approval and trip_instance.tr_approval.ta_approval_status_id == 1
            )

            # Check user role and invoice status
            user_ext = User_extInfo.objects.filter(user_id=user_id).first()
            user_role = user_ext.emp_role.role_name if user_ext and user_ext.emp_role else "User"
            is_invoiced = TransInvoiceInfo.objects.filter(ti_trip=trip_instance).exists()

            # Gating flags for workflow controls
            has_dock_out = bool(trip_instance.tr_dock_out_time)
            has_consignment = bool(trip_instance.tr_consignmentnumber)
            has_consignment_goods = False
            if trip_instance.tr_consignmentnumber:
                has_consignment_goods = ConsignmentgoodsInfo.objects.filter(
                    cg_consignmentnumber=trip_instance.tr_consignmentnumber_id
                ).exists()
            has_vehicle_started = bool(trip_instance.tr_departeddate)

            # Build allotted vehicle list for Enquiry
            allotted_vas = Vehicle_allotmentInfo.objects.filter(
                va_enquirynumber=enquiry_num_id,
                va_status_id__in=[1, 2, 3]
            ).select_related('va_vehiclenumber', 'va_vehiclesource', 'va_vehicletype', 'va_vehicletype_placed')

            allotted_vehicle_list = []
            allotted_vehicle_map = {}
            for va in allotted_vas:
                reg_num = va.va_vehiclenumber_mkt if va.va_vehiclesource_id == 3 else (va.va_vehiclenumber.vm_registrationnumber if va.va_vehiclenumber else '')
                if reg_num and reg_num not in allotted_vehicle_map:
                    item_info = {
                        'reg_number': reg_num,
                        'is_mkt': va.va_vehiclesource_id == 3,
                        'vehiclesource_id': va.va_vehiclesource_id,
                        'vehiclesource_name': str(va.va_vehiclesource) if va.va_vehiclesource else '',
                        'vehicletype_id': va.va_vehicletype_id if va.va_vehicletype else None,
                        'vehicletype_placed_id': va.va_vehicletype_placed_id if va.va_vehicletype_placed else None,
                        'driver_name': va.va_drivername or '',
                        'driver_number': va.va_drivernumber or '',
                        'driver_lic': va.va_driver_lic or '',
                        'driver_master_id': va.va_driver_master_id
                    }
                    allotted_vehicle_list.append(item_info)
                    allotted_vehicle_map[reg_num] = item_info

            import json
            allotted_vehicle_map_json = json.dumps(allotted_vehicle_map)

            context = {
                'first_name': first_name,
                'user_id': user_id,
                'user_role': user_role,
                'is_invoiced': is_invoiced,
                'trip_det_form': trip_det_form,
                'tripclosurefiles_form': tripclosurefiles_form,
                'enquiry_num_id': enquiry_num_id,
                'trip_list': trip_list,
                'status_list': status_list,
                'status_selected': status_selected,
                'consignment_selected': consignment_selected,
                'consignment_list': consignment_list,
                'tripdetail_list': TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num_id),
                'checklist': checklist,
                'trip_approvallist': trip_approvallist,
                'trip_instance': trip_instance,
                'location_locked': False,
                'has_dock_out': has_dock_out,
                'has_consignment': has_consignment,
                'has_consignment_goods': has_consignment_goods,
                'has_vehicle_started': has_vehicle_started,
                'allotted_vehicle_list': allotted_vehicle_list,
                'allotted_vehicle_map_json': allotted_vehicle_map_json,
            }

        return render(request, "asset_mgt_app/tripdetail_add.html", context)

    else:
        if tripdetail_id == 0:
            print("I am inside post add tripdetails")
            post_data = request.POST.copy()
            if not post_data.get('tr_high_value'):
                post_data['tr_high_value'] = '2'
            fk_fields = [
                'tr_enquirynumber', 'tr_consignmentnumber', 'tr_vehiclesource', 
                'tr_vehicletype', 'tr_vehicletype_placed', 'tr_departedlocation', 
                'tr_reportedlocation', 'tc_financestatus', 'tr_updated_by', 'tr_category'
            ]
            for fk in fk_fields:
                val = post_data.get(fk)
                if val is not None and val != '' and not str(val).isdigit():
                    if fk == 'tr_updated_by' and request.user.is_authenticated:
                        post_data['tr_updated_by'] = str(request.user.id)
                    else:
                        post_data.pop(fk, None)

            trip_det_form = TripdetailaddForm(post_data, request.FILES)
            vehicle_allotment_id = post_data.get('vehicle_allotment_id')
            tripclosurefiles_form = TripclosurefilesForm(post_data, request.FILES)
            enquiry_num = enquiry_num_id
            cosnignment_number = post_data.get('tr_consignmentnumber')
            vehicle_number = post_data.get('tr_vehiclenumber')
            status_list = Tripstatusinfo.objects.filter(id__in=[1, 2, 8, 10, 11])
            consignment_list = ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id)
            trip_det_form.fields['tr_enquirynumber'].queryset = EnquirynoteInfo.objects.filter(id=enquiry_num_id)
            trip_det_form.fields['tr_consignmentnumber'].queryset = consignment_list

            # ✅ Prevent using same consignment again (backend check)
            if cosnignment_number and TripdetailInfo.objects.filter(
                    tr_consignmentnumber=cosnignment_number
            ).exists():
                messages.error(request, 'This consignment number is already used in another trip.')
                return render(request, "asset_mgt_app/tripdetail_add.html", {
                    'first_name': first_name,
                    'user_id': user_id,
                    'trip_det_form': trip_det_form,
                    'tripclosurefiles_form': tripclosurefiles_form,
                    'enquiry_num_id': enquiry_num_id,
                    'status_list': status_list,
                    'consignment_list': consignment_list,
                    'tripdetail_list': TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num_id),
                    'status_selected': request.POST.get('tc_financestatus') or 8,
                })

            if vehicle_allotment_id:
                va = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id)

            if trip_det_form.is_valid():
                # ✅ FIX 1: Open trip check is now GLOBAL across ALL enquiries for this vehicle
                # Prevents users from creating a new trip for a vehicle that is already open in a different enquiry
                open_trip_global = TripdetailInfo.objects.filter(
                    tr_vehiclenumber=vehicle_number,
                    tc_financestatus_id=1  # Open / Started
                ).first()
                if open_trip_global:
                    messages.error(
                        request,
                        f'Vehicle {vehicle_number} already has an open trip '
                        f'(Trip No: {open_trip_global.tr_tripnumber}). '
                        f'Please close it before creating a new one.'
                    )
                    return redirect(request.META['HTTP_REFERER'])

                # ✅ NEW LOCATION MATCHING VALIDATION HERE
                # Skip for Market Vehicles (Source 3)
                v_source_id = request.POST.get('tr_vehiclesource')
                if vehicle_number and str(v_source_id) != "3":
                    last_trip_for_loc = TripdetailInfo.objects.filter(
                        tr_vehiclenumber=vehicle_number
                    ).exclude(tr_reportedlocation__isnull=True).order_by('-tr_created_at').first()

                    if last_trip_for_loc:
                        departed_loc_id = request.POST.get('tr_departedlocation')
                        last_loc_name = last_trip_for_loc.tr_reportedlocation.place_name if hasattr(
                            last_trip_for_loc.tr_reportedlocation, 'place_name') else str(
                            last_trip_for_loc.tr_reportedlocation)

                        # ✅ FIX 2: Block if departed location is EMPTY or does NOT match last reported location
                        if not departed_loc_id:
                            messages.error(
                                request,
                                f"Departed location is required. Vehicle's last destination was '{last_loc_name}'."
                            )
                            return redirect(request.META.get('HTTP_REFERER', 'tripdetail_list'))

                        if str(departed_loc_id) != str(last_trip_for_loc.tr_reportedlocation.id):
                            messages.error(
                                request,
                                f"Warning: Vehicle's last destination was '{last_loc_name}'. Please create an 'Empty Trip' or 'Business Empty Trip' from '{last_loc_name}' first."
                            )
                            return redirect(request.META.get('HTTP_REFERER', 'tripdetail_list'))

                # Generate trip number with financial year (Branch specific)
                # Example format: 26-27_MAA_TN_0000001
                current_fy = get_financial_year()
                branch_id = get_session_branch_id(request)
                branch_code = get_branch_code(branch_id)
                prefix = f"{current_fy}_{branch_code}_TN_"
                trip_num_next = generate_next_number(TripdetailInfo, 'tr_tripnumber', prefix, 7)

                trip = trip_det_form.save(commit=False)
                trip.tr_tripnumber = trip_num_next

                # ✅ Synchronize KM fields for reports
                # tr_departedkm is the 'canonical' Starting KM used in reports.
                if not trip.tr_departedkm and trip.tr_reportedkm_pickup:
                    trip.tr_departedkm = trip.tr_reportedkm_pickup

                # tr_reportedkm is the 'canonical' Ending KM used in reports.
                if not trip.tr_reportedkm and trip.tr_reportedkm_delivery:
                    trip.tr_reportedkm = trip.tr_reportedkm_delivery

                # KM Validation: Ensure closing KM >= opening KM
                closing_km = trip.tr_reportedkm or 0
                opening_km = trip.tr_reportedkm_pickup or 0
                if closing_km > 0 and closing_km < opening_km:
                    messages.error(request,
                                   f"Error: Closing KM ({closing_km}) cannot be less than Opening KM ({opening_km})")
                    return redirect(request.META.get('HTTP_REFERER', 'tripdetail_list'))

                # ✅ Robust Status Matching
                status_open = Tripstatusinfo.objects.filter(
                    Q(status__iexact='Open') | Q(status__iexact='Started')).first()
                status_closed = Tripstatusinfo.objects.filter(
                    Q(status__iexact='Closed') | Q(status__iexact='Trip Closed')).first()
                status_pending = Tripstatusinfo.objects.filter(status__iexact='Pending Approval').first()

                # Manual capture of status from POST
                manual_status_id = request.POST.get('tc_financestatus')
                if manual_status_id:
                    trip.tc_financestatus_id = int(manual_status_id)
                    trip.tr_operational_status_id = int(manual_status_id)  # Keep both fields in sync
                else:
                    if trip.tr_category_id in [2, 3]:
                        if status_open:
                            trip.tc_financestatus_id = status_open.id
                            trip.tr_operational_status_id = status_open.id  # Keep both fields in sync
                    else:
                        if status_pending:
                            trip.tc_financestatus_id = status_pending.id
                            trip.tr_operational_status_id = status_pending.id  # Keep both fields in sync

                if vehicle_allotment_id:
                    trip.tr_driver_master_id = va.va_driver_master_id

                pod_data = request.POST.get('pod_signature_data')
                if pod_data:
                    format, imgstr = pod_data.split(';base64,')
                    ext = format.split('/')[-1]
                    data = ContentFile(base64.b64decode(imgstr), name=f'pod_signature.{ext}')
                    trip.td_pod = data

                trip.save()
                en_user = request.user if (request.user and request.user.is_authenticated) else None
                EnquirynoteInfo.objects.filter(id=trip.tr_enquirynumber_id).update(
                    en_updatedon=timezone.now(),
                    en_updated_by=en_user
                )

                # Removed auto-advance logic to strictly require trip approval

                # ✅ AUTOMATED EMAIL TRIGGERS
                def trigger_alert(alert_func, label):
                    try:
                        import json
                        request.session['ses_tripdetail_id'] = trip.id

                        # Fetch recipients
                        recipients = get_auto_recipients(trip)

                        if not recipients:
                            if label == "Trip Started":
                                messages.error(request, "This customer don't have mail please add mail to start the trip.")
                                # Revert to Awaiting Trip Approval so unloading details stay frozen
                                # Keep BOTH status fields in sync to avoid vehicle showing as busy
                                trip.tc_financestatus_id = 8
                                trip.tr_operational_status_id = 8
                                trip.save(update_fields=['tc_financestatus', 'tr_operational_status'])
                            else:
                                display_label = "starting trip" if label == "Loading Reported" else label
                                messages.error(request, f"This customer don't have mail please add mail for {display_label}.")
                            return

                        response = alert_func(request)
                        rec_str = ", ".join(recipients)

                        # Inspect JsonResponse
                        try:
                            data = json.loads(response.content.decode('utf-8'))
                            if data.get('success'):
                                messages.info(request, f"Automated Alert Sent: {label} (To: {rec_str})")
                            else:
                                messages.warning(request, f"Alert skipped: {label} ({data.get('msg')})")
                        except:
                            messages.info(request, f"Automated Alert Sent: {label} (To: {rec_str})")
                    except Exception as e:
                        print(f"Alert trigger error ({label}): {e}")
                        messages.error(request, f"Alert Failed: {label} (Email Server Error)")
                        # Even if SMTP fails, mark flag as True so fields unlock
                        flag_map = {
                            "Loading Reported": "tr_loading_report_mail_sent",
                            "Trip Started": "tr_trip_started_mail_sent",
                            "Unloading Reported": "tr_unloading_report_mail_sent",
                            "Trip Closed": "tr_trip_closed_mail_sent",
                        }
                        flag_field = flag_map.get(label)
                        if flag_field and not getattr(trip, flag_field, True):
                            setattr(trip, flag_field, True)
                            trip.save(update_fields=[flag_field])

                is_open = status_open and trip.tc_financestatus_id == status_open.id
                is_closed = status_closed and trip.tc_financestatus_id == status_closed.id

                # ✅ Send email alerts ONLY for Business Trips (Category 1)
                is_business_trip = (trip.tr_category_id == 1) or (trip.tr_category and trip.tr_category.category.strip().lower() == 'business')
                if is_business_trip:
                    # 1. Loading Reported
                    if trip.tr_departedlocation and trip.tr_departeddate_pickup and not trip.tr_loading_report_mail_sent:
                        trigger_alert(trip_send_loading_report_mail, "Loading Reported")

                    # 2. Trip Started
                    if is_open and not trip.tr_trip_started_mail_sent:
                        trigger_alert(trip_send_trip_started_mail, "Trip Started")

                    # 3. Unloading Reported
                    if trip.tr_reportedlocation and trip.tr_reporteddate and not trip.tr_unloading_report_mail_sent:
                        trigger_alert(trip_send_unloading_report_mail, "Unloading Reported")

                    # 4. Trip Closed
                    if is_closed and not trip.tr_trip_closed_mail_sent:
                        trigger_alert(trip_send_trip_closed_mail, "Trip Closed")

                print("Main Form is Valid")
                last_id = TripdetailInfo.objects.latest('id').id
                last_id_files = Trip_closure_files_Info.objects.latest('id').id
                TripdetailInfo.objects.filter(id=last_id).update(tr_tripnumber=trip_num_next)
                Trip_closure_files_Info.objects.filter(id=last_id_files).update(tcf_tripnumber=trip_num_next)

                tripdetail_list = TripdetailInfo.objects.filter(
                    tr_enquirynumber=enquiry_num
                ).values_list('tr_tripnumber', flat=True)
                EnquirynoteInfo.objects.filter(
                    pk=enquiry_num
                ).update(en_tripdetails=list(tripdetail_list))
                messages.success(request, "Record Updated Successfully")

                return redirect('tripdetail_update', tripdetail_id=trip.id)

            else:
                print("Main Form is not Valid")
                for field, errors in trip_det_form.errors.items():
                    field_label = trip_det_form.fields[field].label if field in trip_det_form.fields else field
                    for error in errors:
                        print(f"Error in {field}: {error}")
                        messages.error(request, f"{field_label}: {error}")
                messages.error(request, 'Record Not Saved. Please Enter All Required Fields')
                status_list = Tripstatusinfo.objects.filter(id__in=[1, 2, 8, 10, 11])
                consignment_list = ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id)
                trip_det_form.fields['tr_enquirynumber'].queryset = EnquirynoteInfo.objects.filter(id=enquiry_num_id)
                trip_det_form.fields['tr_consignmentnumber'].queryset = consignment_list
                return render(request, "asset_mgt_app/tripdetail_add.html", {
                    'first_name': first_name,
                    'user_id': user_id,
                    'trip_det_form': trip_det_form,
                    'tripclosurefiles_form': tripclosurefiles_form,
                    'enquiry_num_id': enquiry_num_id,
                    'status_list': status_list,
                    'consignment_list': consignment_list,
                    'tripdetail_list': TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num_id),
                    'status_selected': request.POST.get('tc_financestatus') or 8,
                })

        else:
            print("I am inside post edit tripdetails")
            trip_num = TripdetailInfo.objects.get(pk=tripdetail_id).tr_tripnumber
            tripdetail = TripdetailInfo.objects.get(pk=tripdetail_id)

            post_data = request.POST.copy()
            fk_fields = [
                'tr_enquirynumber', 'tr_consignmentnumber', 'tr_vehiclesource', 
                'tr_vehicletype', 'tr_vehicletype_placed', 'tr_departedlocation', 
                'tr_reportedlocation', 'tc_financestatus', 'tr_updated_by', 'tr_category'
            ]
            for fk in fk_fields:
                val = post_data.get(fk)
                if val is not None and val != '' and not str(val).isdigit():
                    if fk == 'tr_updated_by' and request.user.is_authenticated:
                        post_data['tr_updated_by'] = str(request.user.id)
                    else:
                        post_data.pop(fk, None)

            trip_det_form = TripdetailaddForm(post_data, request.FILES, instance=tripdetail)
            tripclosure_files = Trip_closure_files_Info.objects.filter(tcf_tripnumber=trip_num).first()
            tripclosurefiles_form = TripclosurefilesForm(post_data, request.FILES, instance=tripclosure_files)
            enquiry_num = tripdetail.tr_enquirynumber.id

            if trip_det_form.is_valid():
                trip = trip_det_form.save(commit=False)

                # ✅ PROTECT already-saved fields from being wiped by disabled HTML inputs.
                # Disabled fields are not submitted in POST, so Django sees them as blank/None
                # and would overwrite the DB value. We restore from the DB instance instead.
                protected_fields = [
                    'tr_reportedkm', 'tr_reporteddate', 'tr_unloading_time',
                    'tr_reporteddate_pickup', 'tr_reportedkm_delivery',
                    'tr_departeddate_delivery', 'tr_reportedkm_pickup',
                    'tr_departeddate', 'tr_departedkm',
                    'tr_loading_time', 'tr_dock_in_time', 'tr_dock_out_time',
                ]
                for field in protected_fields:
                    new_val = getattr(trip, field, None)
                    old_val = getattr(tripdetail, field, None)
                    if not new_val and old_val:
                        setattr(trip, field, old_val)

                # ✅ Synchronize KM fields for reports
                # tr_departedkm is the 'canonical' Starting KM used in reports.
                if not trip.tr_departedkm and trip.tr_reportedkm_pickup:
                    trip.tr_departedkm = trip.tr_reportedkm_pickup

                # tr_reportedkm is the 'canonical' Ending KM used in reports.
                if not trip.tr_reportedkm and trip.tr_reportedkm_delivery:
                    trip.tr_reportedkm = trip.tr_reportedkm_delivery

                # KM Validation: Ensure closing KM >= opening KM
                closing_km = trip.tr_reportedkm or 0
                opening_km = trip.tr_reportedkm_pickup or 0
                if closing_km > 0 and closing_km < opening_km:
                    messages.error(request,
                                   f"Error: Closing KM ({closing_km}) cannot be less than Opening KM ({opening_km})")
                    return redirect(request.META.get('HTTP_REFERER', 'tripdetail_list'))

                # ✅ Robust Status Matching Lookups
                status_open = Tripstatusinfo.objects.filter(
                    Q(status__iexact='Open') | Q(status__iexact='Started')).first()
                status_closed = Tripstatusinfo.objects.filter(
                    Q(status__iexact='Closed') | Q(status__iexact='Trip Closed')).first()

                # Manual capture since it's a raw select tag in HTML
                manual_status_id = request.POST.get('tc_financestatus')
                if manual_status_id:
                    manual_status_id = int(manual_status_id)
                    trip.tr_operational_status_id = manual_status_id
                    # Prevent reverting advanced finance statuses back to Trip Closed (2)
                    if manual_status_id == 2 and trip.tc_financestatus_id in [4, 5, 6, 7, 9]:
                        pass  # keep the advanced status
                    else:
                        trip.tc_financestatus_id = manual_status_id
                
                # Fallback: Sync operational status if missing or if manual_status_id was disabled in UI
                if not trip.tr_operational_status_id and trip.tc_financestatus_id:
                    trip.tr_operational_status_id = trip.tc_financestatus_id
                # Special case: Awaiting Trip Approval (8) should always be synced
                elif trip.tc_financestatus_id == 8 and trip.tr_operational_status_id != 8:
                    trip.tr_operational_status_id = 8

                pod_data = request.POST.get("pod_signature_data", None)
                if pod_data:
                    format, imgstr = pod_data.split(';base64,')
                    ext = format.split('/')[-1]
                    data = ContentFile(base64.b64decode(imgstr), name=f"{trip_num}_pod_signature.{ext}")
                    trip.td_pod = data

                trip.save()
                en_user = request.user if (request.user and request.user.is_authenticated) else None
                EnquirynoteInfo.objects.filter(id=trip.tr_enquirynumber_id).update(
                    en_updatedon=timezone.now(),
                    en_updated_by=en_user
                )
                if tripclosurefiles_form.is_valid():
                    tripclosurefiles_form.save()
                else:
                    for field, errors in tripclosurefiles_form.errors.items():
                        for error in errors:
                            messages.warning(request, f"Attachment not saved - {field}: {error}")

                # ✅ AUTOMATED EMAIL TRIGGERS
                def trigger_alert(alert_func, label):
                    try:
                        import json
                        request.session['ses_tripdetail_id'] = trip.id

                        # Fetch recipients
                        recipients = get_auto_recipients(trip)

                        if not recipients:
                            if label == "Trip Started":
                                messages.error(request, "This customer don't have mail please add mail to start the trip.")
                                # Revert to Trip Open so unloading details stay frozen
                                trip.tc_financestatus_id = 8
                                trip.save(update_fields=['tc_financestatus'])
                            else:
                                display_label = "starting trip" if label == "Loading Reported" else label
                                messages.error(request, f"This customer don't have mail please add mail for {display_label}.")
                            return

                        response = alert_func(request)
                        rec_str = ", ".join(recipients)

                        # Inspect JsonResponse
                        try:
                            data = json.loads(response.content.decode('utf-8'))
                            if data.get('success'):
                                messages.info(request, f"Automated Alert Sent: {label} (To: {rec_str})")
                            else:
                                messages.warning(request, f"Alert skipped: {label} ({data.get('msg')})")
                        except:
                            messages.info(request, f"Automated Alert Sent: {label} (To: {rec_str})")
                    except Exception as e:
                        print(f"Alert trigger error ({label}): {e}")
                        messages.error(request, f"Alert Failed: {label} (Email Server Error)")
                        # Even if SMTP fails, mark flag as True so fields unlock
                        flag_map = {
                            "Loading Reported": "tr_loading_report_mail_sent",
                            "Trip Started": "tr_trip_started_mail_sent",
                            "Unloading Reported": "tr_unloading_report_mail_sent",
                            "Trip Closed": "tr_trip_closed_mail_sent",
                        }
                        flag_field = flag_map.get(label)
                        if flag_field and not getattr(trip, flag_field, True):
                            setattr(trip, flag_field, True)
                            trip.save(update_fields=[flag_field])

                # Boolean checks for status
                # Fallback to IDs 1/2 if name lookup fails, but prioritize names
                is_open = (status_open and trip.tc_financestatus_id == status_open.id) or (
                        not status_open and trip.tc_financestatus_id == 1)
                is_closed = (status_closed and trip.tc_financestatus_id == status_closed.id) or (
                        not status_closed and trip.tc_financestatus_id == 2)

                # ✅ Send email alerts ONLY for Business Trips (Category 1)
                is_business_trip = (trip.tr_category_id == 1) or (trip.tr_category and trip.tr_category.category.strip().lower() == 'business')
                if is_business_trip:
                    # 1. Loading Reported
                    if trip.tr_departedlocation and trip.tr_departeddate_pickup and not trip.tr_loading_report_mail_sent:
                        trigger_alert(trip_send_loading_report_mail, "Loading Reported")

                    # 2. Trip Started
                    if is_open and not trip.tr_trip_started_mail_sent:
                        trigger_alert(trip_send_trip_started_mail, "Trip Started")

                    # 3. Unloading Reported
                    if trip.tr_reportedlocation and trip.tr_reporteddate and not trip.tr_unloading_report_mail_sent:
                        trigger_alert(trip_send_unloading_report_mail, "Unloading Reported")

                    # 4. Trip Closed
                    if is_closed and not trip.tr_trip_closed_mail_sent:
                        trigger_alert(trip_send_trip_closed_mail, "Trip Closed")

                print("Main Form is Valid")
                tripdetail_list = TripdetailInfo.objects.filter(
                    tr_enquirynumber=enquiry_num
                ).values_list('tr_tripnumber', flat=True)
                EnquirynoteInfo.objects.filter(pk=enquiry_num).update(en_tripdetails=list(tripdetail_list))
                messages.success(request, 'Record Updated Successfully')

                return redirect('tripdetail_update', tripdetail_id=tripdetail_id)


            else:
                for field, errors in trip_det_form.errors.items():
                    for error in errors:
                        print(f"Error in {field}: {error}")
                        messages.error(request, f"Error in {field}: {error}")
                print("Trip Details Main Form is not Valid")
                messages.error(request, 'Record Not Saved. Please Enter All Required Fields')

    return redirect('tripdetail_insert')


# List tripdetail
@login_required(login_url='login_page')
def tripdetail_list(request):
    first_name = request.session.get('first_name')
    branch = request.GET.get('branch', '').strip()
    selected_status_id = request.GET.get('trip_status', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    status_list = Tripstatusinfo.objects.filter(id__in=[1, 2, 8])

    context = {
        'first_name': first_name,
        'branch': branch,
        'status_list': status_list,
        'selected_status': int(selected_status_id) if selected_status_id else None,
        'date_from': date_from,
        'date_to': date_to,
    }

    return render(request, "asset_mgt_app/tripdetail_list.html", context)


@login_required(login_url='login_page')
def tripdetail_list_ajax(request):
    """Server-side DataTables AJAX endpoint for Trip Detail List."""
    from django.db.models import Q

    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 50))
    search_value = request.GET.get('search[value]', '').strip()

    # Filters from query params
    branch = request.GET.get('branch', '').strip()
    selected_status_id = request.GET.get('trip_status', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    qs = TripdetailInfo.objects.select_related(
        'tr_enquirynumber', 'tr_consignmentnumber',
        'tr_departedlocation', 'tr_reportedlocation',
        'tc_financestatus'
    ).all()

    # Branch filter
    if branch == 'MAA':
        qs = qs.filter(tr_consignmentnumber__co_consignmentnumber__icontains='MAA')
    elif branch == 'BLR':
        qs = qs.filter(tr_consignmentnumber__co_consignmentnumber__icontains='BLR')

    # Status filter
    if selected_status_id:
        qs = qs.filter(tc_financestatus_id=selected_status_id)

    # Date filters
    if date_from:
        qs = qs.filter(tr_created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(tr_created_at__date__lte=date_to)

    records_total = qs.count()

    # Global search
    if search_value:
        qs = qs.filter(
            Q(tr_tripnumber__icontains=search_value) |
            Q(tr_vehiclenumber__icontains=search_value) |
            Q(tr_enquirynumber__en_enquirynumber__icontains=search_value) |
            Q(tr_consignmentnumber__co_consignmentnumber__icontains=search_value) |
            Q(tr_departedlocation__place_name__icontains=search_value) |
            Q(tr_reportedlocation__place_name__icontains=search_value) |
            Q(tc_financestatus__status__icontains=search_value) |
            Q(tr_updated_by__first_name__icontains=search_value) |
            Q(tr_updated_by__username__icontains=search_value)
        )

    records_filtered = qs.count()

    # Ordering
    order_col = int(request.GET.get('order[0][column]', 0))
    order_dir = request.GET.get('order[0][dir]', 'desc')
    col_map = {
        0: 'tr_created_at',
        1: 'tr_enquirynumber__en_enquirynumber',
        2: 'tr_consignmentnumber__co_consignmentnumber',
        3: 'tr_tripnumber',
        4: 'tr_vehiclenumber',
        5: 'tr_departedlocation__place_name',
        6: 'tr_departedkm',
        7: 'tr_departeddate',
        8: 'tr_reportedlocation__place_name',
        9: 'tr_reportedkm',
        10: 'tr_reporteddate',
        11: 'id',  # Placeholder for Track
        12: 'tc_financestatus__status',
        13: 'tr_updated_by__first_name',
        14: 'tr_updated_at',
    }
    order_field = col_map.get(order_col, 'tr_created_at')
    if order_dir == 'desc':
        order_field = '-' + order_field
    qs = qs.order_by(order_field)

    # Slice for pagination
    if length != -1:
        qs = qs[start:start + length]
    else:
        qs = qs[start:]

    data = []
    for t in qs:
        # Format Dates (remove seconds and +00:00)
        departed_dt = timezone.localtime(t.tr_departeddate).strftime('%Y-%m-%d %H:%M') if t.tr_departeddate else ''
        reported_dt = timezone.localtime(t.tr_reporteddate).strftime('%Y-%m-%d %H:%M') if t.tr_reporteddate else ''
        updated_at = timezone.localtime(t.tr_updated_at).strftime('%Y-%m-%d %H:%M') if t.tr_updated_at else ''

        data.append([
            t.tr_created_at.strftime('%Y-%m-%d') if t.tr_created_at else '',
            str(t.tr_enquirynumber) if t.tr_enquirynumber else '',
            str(t.tr_consignmentnumber) if t.tr_consignmentnumber else '',
            t.tr_tripnumber or '',
            t.tr_vehiclenumber or '',
            str(t.tr_departedlocation) if t.tr_departedlocation else '',
            str(t.tr_departedkm) if t.tr_departedkm is not None else '0',
            departed_dt,
            str(t.tr_reportedlocation) if t.tr_reportedlocation else '',
            str(t.tr_reportedkm) if t.tr_reportedkm is not None else '0',
            reported_dt,
            t.tr_track_link or '',
            str(t.tc_financestatus) if t.tc_financestatus else '',
            str(t.tr_updated_by) if t.tr_updated_by else '',
            updated_at,
            t.id,  # for edit URL (index 15)
            t.id,  # for delete URL (index 16)
        ])

    return JsonResponse({
        'draw': draw,
        'recordsTotal': records_total,
        'recordsFiltered': records_filtered,
        'data': data,
    })


# Delete tripdetail
@login_required(login_url='login_page')
def tripdetail_delete(request, tripdetail_id):
    tripdetail = TripdetailInfo.objects.get(pk=tripdetail_id)
    enquiry_num = tripdetail.tr_enquirynumber
    trip_num = tripdetail.tr_tripnumber
    
    reason = request.POST.get('deletion_reason', 'No reason provided')
    identifier = trip_num
    
    DeletionLog.objects.create(
        dl_model_name='TripdetailInfo',
        dl_record_id=tripdetail_id,
        dl_record_identifier=identifier,
        dl_deleted_by=request.user,
        dl_reason=reason
    )
    
    tripdetail.delete()
    try:
        tripdetail_list = TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num).values_list('tr_tripnumber',
                                                                                                  flat=True)
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_tripdetails=list(tripdetail_list))
    except ObjectDoesNotExist:
        tripdetail_list = []
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_tripdetails=list(tripdetail_list))
    trip_closure_files = Trip_closure_files_Info.objects.filter(tcf_tripnumber=trip_num)
    for trip_file in trip_closure_files:
        trip_file.delete()
    return redirect(request.META.get('HTTP_REFERER', '/SMS/tripdetail_list'))


@login_required(login_url='login_page')
def load_vehicle_details(request):
    enquiry_number = request.GET.get('enquiry_number')
    consignment_number = request.GET.get('consignment_number')
    count = 0
    trip_number = list(
        TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_number, tr_consignmentnumber=consignment_number,
                                      tc_financestatus=1).values_list('tr_tripnumber', flat=True))
    if len(trip_number) > 0:
        count = count + 1
    if count < 1:
        vehicle_type_requested = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,
                                                                           va_consignmentnumber=consignment_number).values_list(
            'va_vehicletype', flat=True))
        vehicle_type_placed = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,
                                                                        va_consignmentnumber=consignment_number).values_list(
            'va_vehicletype_placed', flat=True))
        vehicletype_source = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,
                                                                       va_consignmentnumber=consignment_number).values_list(
            'va_vehiclesource', flat=True))
        vehicletype_number = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,
                                                                       va_consignmentnumber=consignment_number).values_list(
            'va_vehiclenumber', flat=True))
        driver_name = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,
                                                                va_consignmentnumber=consignment_number).values_list(
            'va_drivername', flat=True))
        driver_number = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,
                                                                  va_consignmentnumber=consignment_number).values_list(
            'va_driver_lic', flat=True))
        driver_license = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,
                                                                   va_consignmentnumber=consignment_number).values_list(
            'va_drivernumber', flat=True))
        count_val = count
        data = {
            'vehicle_type_requested': vehicle_type_requested,
            'vehicle_type_placed': vehicle_type_placed,
            'vehicletype_source': vehicletype_source,
            'vehicletype_number': vehicletype_number,
            'driver_name': driver_name,
            'driver_number': driver_number,
            'driver_license': driver_license,
            'count_val': count_val,
        }
    else:
        count_val = count
        data = {
            'count_val': count_val,
        }
    return HttpResponse(json.dumps(data))


@login_required(login_url='login_page')
def trip_email(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "msg": "Invalid request method"})

    recipient = request.POST.get('recipient')
    message_from_user = request.POST.get('message', '')
    alert_type = request.POST.get('alert_type', '')
    tripdetail_id = request.session.get('ses_tripdetail_id')

    # Save manual recipient to session
    request.session["trip_manual_recipient"] = recipient

    if not tripdetail_id:
        return JsonResponse({"success": False, "msg": "Trip detail ID is missing."})

    trip = TripdetailInfo.objects.get(pk=tripdetail_id)

    # ---- Helper function: parse and format date ----
    def parse_dt(value):
        if not value:
            return None
        try:
            if isinstance(value, datetime):
                return value
            return make_aware(datetime.strptime(str(value).split('+')[0].strip(), "%Y-%m-%d %H:%M:%S"))
        except Exception:
            return None

    try:
        enquiry = EnquirynoteInfo.objects.select_related('en_customername', 'en_customerdepartment').get(
            en_enquirynumber=trip.tr_enquirynumber)
    except EnquirynoteInfo.DoesNotExist:
        enquiry = None

    customer_name = enquiry.en_customername.cu_name if enquiry and enquiry.en_customername else "N/A"

    # Common Data Points
    from_location = trip.tr_departedlocation.place_name if trip.tr_departedlocation else "N/A"
    reported_dt = format_email_date(trip.tr_departeddate_pickup)
    consignment = trip.tr_consignmentnumber.co_consignmentnumber if trip.tr_consignmentnumber else "N/A"
    started_dt = format_email_date(trip.tr_departeddate)
    to_location = trip.tr_reportedlocation.place_name if trip.tr_reportedlocation else "N/A"
    unloading_reported_dt = format_email_date(trip.tr_reporteddate)

    # New Fields Requested
    vehicle_number = trip.tr_vehiclenumber or "N/A"
    driver_name = trip.tr_drivername or "N/A"
    driver_number = trip.tr_drivernumber or "N/A"

    subject = f"{alert_type if alert_type else 'Trip Update'} - {trip.tr_tripnumber}"
    recipient_list = [email.strip() for email in recipient.split(',') if email.strip()]

    email_content = ""

    # Mail 1: Loading Reported
    if "Loading Reported" in alert_type:
        email_content = f"""
        <table style="border-collapse: collapse; width: 100%; border: 1px solid #ddd; font-family: Arial, sans-serif;">
            <thead>
                <tr style="background-color: #007bff; color: white;">
                    <th colspan="2" style="padding: 10px; text-align: center;">Loading Reported Details</th>
                </tr>
            </thead>
            <tbody>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Customer Name</b></td><td style="padding: 8px; border: 1px solid #ddd;">{customer_name}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>vehicle number</b></td><td style="padding: 8px; border: 1px solid #ddd;">{vehicle_number}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>driver name</b></td><td style="padding: 8px; border: 1px solid #ddd;">{driver_name}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>mobile number</b></td><td style="padding: 8px; border: 1px solid #ddd;">{driver_number}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>From Location</b></td><td style="padding: 8px; border: 1px solid #ddd;">{from_location}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Vehicle Reported Date & Time</b></td><td style="padding: 8px; border: 1px solid #ddd;">{reported_dt}</td></tr>
            </tbody>
        </table>
        """

    # Mail 2: Trip Started
    elif "Trip Started" in alert_type:
        email_content = f"""
        <table style="border-collapse: collapse; width: 100%; border: 1px solid #ddd; font-family: Arial, sans-serif;">
            <thead>
                <tr style="background-color: #007bff; color: white;">
                    <th colspan="2" style="padding: 10px; text-align: center;">Trip Started Details</th>
                </tr>
            </thead>
            <tbody>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Customer Name</b></td><td style="padding: 8px; border: 1px solid #ddd;">{customer_name}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>vehicle number</b></td><td style="padding: 8px; border: 1px solid #ddd;">{vehicle_number}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>driver name</b></td><td style="padding: 8px; border: 1px solid #ddd;">{driver_name}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>mobile number</b></td><td style="padding: 8px; border: 1px solid #ddd;">{driver_number}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>From Location</b></td><td style="padding: 8px; border: 1px solid #ddd;">{from_location}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Vehicle Reported Date & Time</b></td><td style="padding: 8px; border: 1px solid #ddd;">{reported_dt}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Consignment Number</b></td><td style="padding: 8px; border: 1px solid #ddd;">{consignment}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Vehicle Started Date & Time</b></td><td style="padding: 8px; border: 1px solid #ddd;">{started_dt}</td></tr>
            </tbody>
        </table>
        """

    # Mail 3: Unloading Reported
    elif "Unloading Reported" in alert_type:
        email_content = f"""
         <table style="border-collapse: collapse; width: 100%; border: 1px solid #ddd; font-family: Arial, sans-serif;">
            <thead>
                <tr style="background-color: #007bff; color: white;">
                    <th colspan="2" style="padding: 10px; text-align: center;">Unloading Reported Details</th>
                </tr>
            </thead>
            <tbody>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Customer Name</b></td><td style="padding: 8px; border: 1px solid #ddd;">{customer_name}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>vehicle number</b></td><td style="padding: 8px; border: 1px solid #ddd;">{vehicle_number}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>driver name</b></td><td style="padding: 8px; border: 1px solid #ddd;">{driver_name}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>mobile number</b></td><td style="padding: 8px; border: 1px solid #ddd;">{driver_number}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>From Location</b></td><td style="padding: 8px; border: 1px solid #ddd;">{from_location}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Reported Date (Loading)</b></td><td style="padding: 8px; border: 1px solid #ddd;">{reported_dt}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Consignment #</b></td><td style="padding: 8px; border: 1px solid #ddd;">{consignment}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Started Date</b></td><td style="padding: 8px; border: 1px solid #ddd;">{started_dt}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>To Location</b></td><td style="padding: 8px; border: 1px solid #ddd;">{to_location}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Reported Date (Unloading)</b></td><td style="padding: 8px; border: 1px solid #ddd;">{unloading_reported_dt}</td></tr>
            </tbody>
        </table>
        """

    # Mail 4: Trip Closed
    elif "Trip Closed" in alert_type:
        email_content = f"""
        <table style="border-collapse: collapse; width: 100%; border: 1px solid #ddd; font-family: Arial, sans-serif;">
            <thead>
                <tr style="background-color: #007bff; color: white;">
                    <th colspan="2" style="padding: 10px; text-align: center;">Trip Closed Details</th>
                </tr>
            </thead>
            <tbody>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Customer Name</b></td><td style="padding: 8px; border: 1px solid #ddd;">{customer_name}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Trip Number</b></td><td style="padding: 8px; border: 1px solid #ddd;">{trip.tr_tripnumber}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>vehicle number</b></td><td style="padding: 8px; border: 1px solid #ddd;">{vehicle_number}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>driver name</b></td><td style="padding: 8px; border: 1px solid #ddd;">{driver_name}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>mobile number</b></td><td style="padding: 8px; border: 1px solid #ddd;">{driver_number}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Reported Date (Loading)</b></td><td style="padding: 8px; border: 1px solid #ddd;">{reported_dt}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Consignment #</b></td><td style="padding: 8px; border: 1px solid #ddd;">{consignment}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Started Date</b></td><td style="padding: 8px; border: 1px solid #ddd;">{started_dt}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>To Location</b></td><td style="padding: 8px; border: 1px solid #ddd;">{to_location}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Vehicle Closed Date & Time</b></td><td style="padding: 8px; border: 1px solid #ddd;">{unloading_reported_dt}</td></tr>
                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Status</b></td><td style="padding: 8px; border: 1px solid #ddd;">Trip Closed</td></tr>
            </tbody>
        </table>
        """

    # Fallback / Default Format
    else:
        email_content = f"""
        <p>Please find below the trip details.</p>
        <p><b>Customer:</b> {customer_name}</p>
        <p><b>Vehicle Number:</b> {vehicle_number}</p>
        <p><b>Driver Name:</b> {driver_name}</p>
        <p><b>Driver Mobile Number:</b> {driver_number}</p>
        <p><b>Trip:</b> {trip.tr_tripnumber}</p>
        """

    full_email_body = f"""
    <html>
    <body>
        <p>Dear Customer,</p>
        <p>Status Update: {alert_type if alert_type else 'General Update'}.</p>
        {email_content}
        <br>
        {"<p><b>Message:</b> " + message_from_user + "</p>" if message_from_user else ""}
        <p>Regards,<br>BVM Warehouse Team</p>
    </body>
    </html>
    """

    # ---- Handle Flags ----
    if "Loading Reported" in alert_type:
        trip.tr_loading_report_mail_sent = True
        trip.save(update_fields=["tr_loading_report_mail_sent"])
    elif "Trip Started" in alert_type:
        trip.tr_trip_started_mail_sent = True
        trip.save(update_fields=["tr_trip_started_mail_sent"])
    elif "Unloading Reported" in alert_type:
        trip.tr_unloading_report_mail_sent = True
        trip.save(update_fields=["tr_unloading_report_mail_sent"])
    elif "Trip Closed" in alert_type:
        trip.tr_trip_closed_mail_sent = True
        trip.save(update_fields=["tr_trip_closed_mail_sent"])

    # ---- Attachment Handling ----
    attachment_path = trip.tc_pod_attachment.path if trip.tc_pod_attachment else None
    attachment_file = open(attachment_path, 'rb') if attachment_path else None
    file_name = trip.tc_pod_attachment.name.split("/")[-1] if trip.tc_pod_attachment else None

    # ---- Send Email ----
    try:
        send_department_email(
            department='itadmin',
            subject=subject,
            message=full_email_body,
            recipient_list=recipient_list,
            attachment=attachment_file,
            attachment_type="application/octet-stream" if attachment_file else None,
            file_name=file_name,
            email_type=1
        )
        return JsonResponse({"success": True, "msg": "Email sent successfully."})
    except Exception as e:
        return JsonResponse({"success": False, "msg": f"Error sending email: {str(e)}"})


@login_required(login_url='login_page')
def load_truck_details(request):
    consignment_number = request.GET.get("consignment_number")
    enquiry_number = request.GET.get("enquiry_number")
    filtered_records = Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number)

    try:
        # Fetch truck number from ConsignmentdetailInfo
        consignment_obj = ConsignmentdetailInfo.objects.get(pk=consignment_number)
        truck_number = consignment_obj.co_vehicelnumber.strip() if consignment_obj.co_vehicelnumber else ""

        # Fetch vehicle details from Vehicle_allotmentInfo (search in both fields)
        vehicle_info = filtered_records.filter(
            Q(va_vehiclenumber__vm_registrationnumber=truck_number) | Q(va_vehiclenumber_mkt=truck_number)
        ).last()  # Fix: Get LATEST matching record (for replacements)

        if vehicle_info:
            data = {
                "truck_number": truck_number,
                "va_drivername": vehicle_info.va_drivername,
                "va_drivernumber": vehicle_info.va_drivernumber,
                "va_vehiclesource": vehicle_info.va_vehiclesource.id if vehicle_info.va_vehiclesource else None,
                "va_vehicletype_placed": vehicle_info.va_vehicletype_placed.id if vehicle_info.va_vehicletype_placed else None,
                "va_vehicletype": vehicle_info.va_vehicletype.id if vehicle_info.va_vehicletype else None,
                "va_driver_lic": vehicle_info.va_driver_lic,
                "va_sale": vehicle_info.va_sale,
            }
        else:
            data = {"error": "No vehicle allotment details found for vehicle: " + truck_number}

    except ObjectDoesNotExist:
        data = {"error": "Consignment number not found"}

    return JsonResponse(data)


def fleet_management_view(request):
    vehicles = VehiclemasterInfo.objects.all().select_related('vm_vehicletype', 'vm_vehiclemanufacturer', 'vm_vehiclemodel', 'vm_ownership')
    vehicle_status_list = []

    COMPLETED_STATUS_IDS = [2, 3, 4, 5, 6, 7, 9, 10]   # Settled, Closed, Cancelled, etc.

    total_count = 0
    in_trip_count = 0
    available_count = 0

    for vehicle in vehicles:
        reg_num = vehicle.vm_registrationnumber

        trip = TripdetailInfo.objects.filter(
            tr_vehiclenumber=reg_num
        ).select_related(
            'tr_enquirynumber__en_customername',
            'tr_departedlocation',
            'tr_reportedlocation',
            'tr_vehicletype_placed',
            'tr_vehicletype',
            'tr_vehiclesource',
            'tc_financestatus'
        ).order_by('-tr_created_at', '-id').first()

        master_vtype = vehicle.vm_vehicletype.vt_vehicletype if vehicle.vm_vehicletype else ''
        master_vsrc = vehicle.vm_ownership.ow_ownership if vehicle.vm_ownership else ''

        if trip:
            enquiry = trip.tr_enquirynumber
            customer = enquiry.en_customername if enquiry else None

            from_loc = getattr(trip, 'tr_departedlocation', None)
            to_loc = getattr(trip, 'tr_reportedlocation', None)
            v_placed = getattr(trip, 'tr_vehicletype_placed', None)
            v_req = getattr(trip, 'tr_vehicletype', None)
            v_src = getattr(trip, 'tr_vehiclesource', None)
            fin_status = getattr(trip, 'tc_financestatus', None)

            status_id = fin_status.id if fin_status else None
            is_active_trip = status_id not in COMPLETED_STATUS_IDS if status_id else False

            if is_active_trip:
                operational_status = 'In Trip'
                in_trip_count += 1
            else:
                operational_status = 'Available'
                available_count += 1

            consignment_obj = getattr(trip, 'tr_consignmentnumber', None)

            status = {
                'registration_number': reg_num,
                'customer_name': customer.cu_name if customer else '',
                'driver_name': trip.tr_drivername or '',
                'from_location': from_loc.place_name if from_loc else '',
                'to_location': to_loc.place_name if to_loc else '',
                'vehicle_type': v_placed.vt_vehicletype if v_placed else (v_req.vt_vehicletype if v_req else master_vtype),
                'vehicle_source': v_src.ow_ownership if v_src else master_vsrc,
                'departed_date': trip.tr_departeddate,
                'reported_date': trip.tr_reporteddate,
                'trip_status': fin_status.status if fin_status else 'Unknown',
                'trip_number': trip.tr_tripnumber or '',
                'consignment_number': consignment_obj.co_consignmentnumber if consignment_obj else '',
                'status': operational_status
            }
        else:
            available_count += 1
            status = {
                'registration_number': reg_num,
                'customer_name': '',
                'driver_name': '',
                'from_location': '',
                'to_location': '',
                'trip_status': 'No Trip Data',
                'trip_number': '',
                'consignment_number': '',
                'vehicle_type': master_vtype,
                'vehicle_source': master_vsrc,
                'departed_date': '',
                'reported_date': '',
                'status': 'Available'
            }

        total_count += 1
        vehicle_status_list.append(status)

    context = {
        'vehicle_status_list': vehicle_status_list,
        'total_count': total_count,
        'in_trip_count': in_trip_count,
        'available_count': available_count,
    }

    return render(request, "asset_mgt_app/fleet_management.html", context)


@login_required(login_url='login_page')
def get_sim_tracking_data(request):
    trip_details = TripdetailInfo.objects.filter(tr_vehiclesource=3, tc_financestatus=1).values(
        'tr_vehiclenumber', 'tr_drivername', 'tr_drivernumber', 'tr_track_link', 'tc_financestatus'
    )

    sim_data = []
    for trip in trip_details:
        sim_data.append({
            'sim_number': trip['tr_drivernumber'] or 'NA',
            'imei': trip['tr_vehiclenumber'],
            'status': trip['tc_financestatus'],
            'track_url': trip['tr_track_link'],
            'driver_name': trip['tr_drivername'] or 'NA'
        })

    return JsonResponse(sim_data, safe=False)


@login_required(login_url='login_page')
def get_customer_ref(request):
    consignment_id = request.GET.get('consignment_id')
    try:
        consignment = ConsignmentdetailInfo.objects.get(id=consignment_id)
        data = {'customer_ref': consignment.co_cusrefnum}
    except ConsignmentdetailInfo.DoesNotExist:
        data = {'customer_ref': ''}
    return JsonResponse(data)


@login_required(login_url='login_page')
def get_last_reported_km(request):
    vehicle = request.GET.get("vehicle")
    enquiry_id = request.GET.get("enquiry_id")

    last_trip = None
    if vehicle:
        if enquiry_id:
            last_trip = (
                TripdetailInfo.objects
                .filter(tr_enquirynumber_id=enquiry_id, tr_vehiclenumber=vehicle, tr_category_id__in=[2, 3])
                .filter(Q(tr_reporteddate__isnull=False) | Q(tr_reportedkm__isnull=False))
                .order_by('-tr_reporteddate', '-id')
                .first()
            )

        if not last_trip:
            last_trip = (
                TripdetailInfo.objects
                .filter(tr_vehiclenumber=vehicle)
                .filter(Q(tr_reporteddate__isnull=False) | Q(tr_reportedkm__isnull=False))
                .order_by('-tr_reporteddate', '-id')
                .first()
            )

    reported_dt_str = None
    if last_trip and last_trip.tr_reporteddate:
        local_dt = timezone.localtime(last_trip.tr_reporteddate)
        reported_dt_str = local_dt.strftime('%Y-%m-%dT%H:%M')

    return JsonResponse({
        "reported_km": last_trip.tr_reportedkm if last_trip else None,
        "reported_date": reported_dt_str
    })


def get_auto_recipients(trip):
    """
    Automatically fetches recipients from Emailmaster.
    Prioritizes Email Type 2 or 'For alert'.
    """
    try:
        # Refresh trip to ensure relationships are up to date
        trip.refresh_from_db()
        enquiry = EnquirynoteInfo.objects.select_related('en_customername', 'en_customerdepartment').get(
            id=trip.tr_enquirynumber_id)

        customer = enquiry.en_customername
        department = enquiry.en_customerdepartment

        # 1. Filtered Search: Type 2 (Alerts) or 'For alert' by name
        type_obj = Email_type.objects.filter(Q(id=2) | Q(email_type__iexact='For alert')).first()
        tid = type_obj.id if type_obj else 2

        email_qs = Emailmaster.objects.filter(
            Q(em_Customer_name_id=customer.id) &
            (Q(em_emailtype_id=tid) | Q(em_emailtype__email_type__iexact='For alert'))
        )

        if enquiry.en_requestor:
            req_qs = email_qs.filter(em_user__iexact=enquiry.en_requestor)
            if req_qs.exists():
                email_qs = req_qs

        if department:
            dept_qs = email_qs.filter(em_customerdepartment_id=department.id)
            if dept_qs.exists():
                email_obj = dept_qs.first()
            else:
                email_obj = email_qs.first()
        else:
            email_obj = email_qs.first()

        if email_obj:
            to = email_obj.em_to_names or ""
            cc = email_obj.em_cc_names or ""
            recipients = [x.strip() for x in to.split(",") if x.strip()]
            if cc:
                recipients.extend([x.strip() for x in cc.split(",") if x.strip()])

            return recipients

    except Exception as e:
        print(f"Error fetching auto recipients: {e}")

    return None


def get_trip_recipients(request, trip):
    recipients = get_auto_recipients(trip)
    return recipients or []


def get_manual_recipients_backup(request):
    recipient = request.session.get("trip_manual_recipient")
    if not recipient:
        return ["itadmin@bvm.com"]
    return [x.strip() for x in recipient.split(",") if x.strip()]


@login_required(login_url='login_page')
def trip_send_loading_report_mail(request):
    trip_id = request.session.get("ses_tripdetail_id")

    if not trip_id:
        return JsonResponse({"success": False, "msg": "Trip ID missing"})

    trip = TripdetailInfo.objects.select_related("tr_enquirynumber").get(id=trip_id)

    if trip.tr_loading_report_mail_sent:
        return JsonResponse({"success": False, "msg": "Loading report mail already sent"})

    recipients = get_trip_recipients(request, trip)

    enquiry = EnquirynoteInfo.objects.select_related("en_customername").get(id=trip.tr_enquirynumber_id)

    customer_name = enquiry.en_customername.cu_name if enquiry.en_customername else "N/A"
    from_location = trip.tr_departedlocation.place_name if trip.tr_departedlocation else "N/A"
    reported_dt = format_email_date(trip.tr_departeddate_pickup)
    vehicle_number = trip.tr_vehiclenumber or "N/A"

    subject = f"Trip Loading Reported - {vehicle_number}"

    email_body = f"""
    <html>
    <body>
        <p>Dear Customer,</p>
        <p>Status Update: Loading Reported Alert.</p>
        <table style="border-collapse: collapse; width: 70%; border: 1px solid #ddd; font-family: Arial, sans-serif; margin-left: auto; margin-right: auto;">
            <thead>
                <tr style="background-color: #003366; color: white;">
                    <th colspan="2" style="padding: 10px; text-align: center;">Loading Reported Details</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Customer Name</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{customer_name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Vehicle Number</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{vehicle_number}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>From Location</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{from_location}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Vehicle Reported Date & Time</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{reported_dt}</td>
                </tr>
            </tbody>
        </table>
        <p>Regards,<br>BVM Transport Team</p>
    </body>
    </html>
    """

    send_department_email(
        department="itadmin",
        subject=subject,
        message=email_body,
        recipient_list=recipients,
        email_type=1
    )

    trip.tr_loading_report_mail_sent = True
    trip.save(update_fields=["tr_loading_report_mail_sent"])

    return JsonResponse({"success": True})


@login_required(login_url='login_page')
def trip_send_trip_started_mail(request):
    trip_id = request.session.get("ses_tripdetail_id")

    if not trip_id:
        return JsonResponse({"success": False, "msg": "Trip ID missing"})

    trip = TripdetailInfo.objects.select_related("tr_enquirynumber").get(id=trip_id)

    if trip.tr_trip_started_mail_sent:
        return JsonResponse({"success": False, "msg": "Trip started mail already sent"})

    recipients = get_trip_recipients(request, trip)

    enquiry = EnquirynoteInfo.objects.select_related("en_customername").get(id=trip.tr_enquirynumber_id)

    customer_name = enquiry.en_customername.cu_name if enquiry.en_customername else "N/A"
    from_location = trip.tr_departedlocation.place_name if trip.tr_departedlocation else "N/A"
    reported_dt = format_email_date(trip.tr_departeddate_pickup)
    consignment = trip.tr_consignmentnumber.co_consignmentnumber if trip.tr_consignmentnumber else "N/A"
    started_dt = format_email_date(trip.tr_departeddate)
    vehicle_number = trip.tr_vehiclenumber or "N/A"

    subject = f"Trip Started - {vehicle_number}"

    email_body = f"""
    <html>
    <body>
        <p>Dear Customer,</p>
        <p>Status Update: Trip Started Alert.</p>
        <table style="border-collapse: collapse; width: 70%; border: 1px solid #ddd; font-family: Arial, sans-serif; margin-left: auto; margin-right: auto;">
            <thead>
                <tr style="background-color: #003366; color: white;">
                    <th colspan="2" style="padding: 10px; text-align: center;">Trip Started Details</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Customer Name</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{customer_name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Vehicle Number</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{vehicle_number}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>From Location</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{from_location}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Vehicle Reported Date & Time</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{reported_dt}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Consignment Number</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{consignment}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Vehicle Started Date & Time</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{started_dt}</td>
                </tr>
            </tbody>
        </table>
        <p>Regards,<br>BVM Transport Team</p>
    </body>
    </html>
    """

    send_department_email(
        department="itadmin",
        subject=subject,
        message=email_body,
        recipient_list=recipients,
        email_type=1
    )

    # --- ADD WHATSAPP TRIGGER ---
    try:
        from ..utils.whatsapp_utils import send_whatsapp_consignment_details
        send_whatsapp_consignment_details(trip)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"WhatsApp Error: {e}")

    trip.tr_trip_started_mail_sent = True
    trip.save(update_fields=["tr_trip_started_mail_sent"])

    return JsonResponse({"success": True})


@login_required(login_url='login_page')
def trip_send_unloading_report_mail(request):
    trip_id = request.session.get("ses_tripdetail_id")

    if not trip_id:
        return JsonResponse({"success": False, "msg": "Trip ID missing"})

    trip = TripdetailInfo.objects.select_related("tr_enquirynumber").get(id=trip_id)

    if trip.tr_unloading_report_mail_sent:
        return JsonResponse({"success": False, "msg": "Unloading report mail already sent"})

    recipients = get_trip_recipients(request, trip)

    enquiry = EnquirynoteInfo.objects.select_related("en_customername").get(id=trip.tr_enquirynumber_id)

    customer_name = enquiry.en_customername.cu_name if enquiry.en_customername else "N/A"
    from_location = trip.tr_departedlocation.place_name if trip.tr_departedlocation else "N/A"
    loading_reported_dt = format_email_date(trip.tr_departeddate_pickup)
    consignment = trip.tr_consignmentnumber.co_consignmentnumber if trip.tr_consignmentnumber else "N/A"
    started_dt = format_email_date(trip.tr_departeddate)
    to_location = trip.tr_reportedlocation.place_name if trip.tr_reportedlocation else "N/A"
    unloading_reported_dt = format_email_date(trip.tr_reporteddate)
    vehicle_number = trip.tr_vehiclenumber or "N/A"

    subject = f"Trip Unloading Reported - {vehicle_number}"

    email_body = f"""
    <html>
    <body>
        <p>Dear Customer,</p>
        <p>Status Update: Unloading Reported Alert.</p>
        <table style="border-collapse: collapse; width: 70%; border: 1px solid #ddd; font-family: Arial, sans-serif; margin-left: auto; margin-right: auto;">
            <thead>
                <tr style="background-color: #003366; color: white;">
                    <th colspan="2" style="padding: 10px; text-align: center;">Unloading Reported Details</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Customer Name</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{customer_name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Vehicle Number</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{vehicle_number}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Consignment Number</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{consignment}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>To Location</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{to_location}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Vehicle Reported Date & Time (Unloading)</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{unloading_reported_dt}</td>
                </tr>
            </tbody>
        </table>
        <p>Regards,<br>BVM Transport Team</p>
    </body>
    </html>
    """

    send_department_email(
        department="itadmin",
        subject=subject,
        message=email_body,
        recipient_list=recipients,
        email_type=1
    )

    trip.tr_unloading_report_mail_sent = True
    trip.save(update_fields=["tr_unloading_report_mail_sent"])

    return JsonResponse({"success": True})


@login_required(login_url='login_page')
def trip_send_trip_closed_mail(request):
    trip_id = request.session.get("ses_tripdetail_id")

    if not trip_id:
        return JsonResponse({"success": False, "msg": "Trip ID missing"})

    trip = TripdetailInfo.objects.select_related("tr_enquirynumber").get(id=trip_id)

    if trip.tr_trip_closed_mail_sent:
        return JsonResponse({"success": False, "msg": "Trip closed mail already sent"})

    recipients = get_trip_recipients(request, trip)

    enquiry = EnquirynoteInfo.objects.select_related("en_customername").get(id=trip.tr_enquirynumber_id)

    customer_name = enquiry.en_customername.cu_name if enquiry.en_customername else "N/A"
    vehicle_number = trip.tr_vehiclenumber or "N/A"
    from_location = trip.tr_departedlocation.place_name if trip.tr_departedlocation else "N/A"
    to_location = trip.tr_reportedlocation.place_name if trip.tr_reportedlocation else "N/A"
    consignment = trip.tr_consignmentnumber.co_consignmentnumber if trip.tr_consignmentnumber else "N/A"
    started_dt = format_email_date(trip.tr_departeddate) or "N/A"
    reported_dt = format_email_date(trip.tr_reporteddate) or "N/A"

    # POD Status Logic - Check both file attachment and signature
    pod_status = "POD Received" if (trip.tc_pod_attachment or trip.td_pod) else "POD Not Received"

    subject = f"Trip Closed - {vehicle_number}"

    email_body = f"""
    <html>
    <body>
        <p>Dear Customer,</p>
        <p>Status Update: Trip Closed Alert.</p>
        <table style="border-collapse: collapse; width: 70%; border: 1px solid #ddd; font-family: Arial, sans-serif; margin-left: auto; margin-right: auto;">
            <thead>
                <tr style="background-color: #003366; color: white;">
                    <th colspan="2" style="padding: 10px; text-align: center;">Trip Closed Details</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Customer Name</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{customer_name}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Vehicle Number</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{vehicle_number}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>From Location</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{from_location}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Consignment Number</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{consignment}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Vehicle Started Date & Time</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{started_dt}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>To Location</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{to_location}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Vehicle Closed Date & Time</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{reported_dt}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>POD Status</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>{pod_status}</b></td>
                </tr>
            </tbody>
        </table>
        <p>Regards,<br>BVM Transport Team</p>
    </body>
    </html>
    """

    send_department_email(
        department="itadmin",
        subject=subject,
        message=email_body,
        recipient_list=recipients,
        email_type=1
    )

    # --- ADD WHATSAPP TRIGGER ---
    try:
        from ..utils.whatsapp_utils import send_whatsapp_consignment_details
        send_whatsapp_consignment_details(trip)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"WhatsApp Error: {e}")

    trip.tr_trip_closed_mail_sent = True
    trip.save(update_fields=["tr_trip_closed_mail_sent"])

    return JsonResponse({"success": True})


@login_required(login_url='login_page')
def get_trip_email_recipients(request):
    enquiry_id = request.GET.get("enquiry_id")
    if not enquiry_id:
        return JsonResponse({"success": False, "msg": "Enquiry ID missing"})

    try:
        enquiry = EnquirynoteInfo.objects.select_related("en_customername", "en_customerdepartment").get(id=enquiry_id)
        customer = enquiry.en_customername
        department = enquiry.en_customerdepartment

        # ✅ Optimized lookup using the same logic as automated triggers
        email_type_obj = Email_type.objects.filter(Q(id=2) | Q(email_type__iexact='For alert')).first()
        tid = email_type_obj.id if email_type_obj else 2

        email_qs = Emailmaster.objects.filter(em_Customer_name=customer, em_emailtype_id=tid)

        if enquiry.en_requestor:
            req_qs = email_qs.filter(em_user__iexact=enquiry.en_requestor)
            if req_qs.exists():
                email_qs = req_qs

        if department:
            dept_qs = email_qs.filter(em_customerdepartment=department)
            if dept_qs.exists():
                email_obj = dept_qs.first()
            else:
                email_obj = email_qs.first()
        else:
            email_obj = email_qs.first()

        if email_obj:
            to = email_obj.em_to_names or ""

            cc = email_obj.em_cc_names or ""
            recipients = to
            if cc:
                if recipients:
                    recipients += ", " + cc
                else:
                    recipients = cc
            return JsonResponse({"success": True, "recipients": recipients})
        else:
            # Fallback for UI consistency
            return JsonResponse(
                {"success": True, "recipients": "itadmin@bvm.com", "msg": f"No alert contact found for {customer}"})

    except Exception as e:
        return JsonResponse({"success": False, "msg": str(e)})
