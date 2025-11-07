import base64
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.core.files.base import ContentFile
from django.db.models import Q
from django.utils.timezone import make_aware

from .send_department_email import send_department_email
from ..forms import TripclosurefilesForm,TripdetailaddForm
from ..models import Vehicle_allotmentInfo,ConsignmentdetailInfo,Tripstatusinfo,Trip_closure_files_Info,EnquirynoteInfo,TripdetailInfo,VehiclemasterInfo,TripHighvalueInfo
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
import json
@login_required(login_url='login_page')
def tripdetail_enquiry(request, enquiry_id, trip_num):
    # Fetch the enquiry object (optional - only needed if you want to verify or log it)
    enquiry = get_object_or_404(EnquirynoteInfo, pk=enquiry_id)

    # If no trip is associated, store enquiry ID in session and redirect to insert
    if trip_num == 'none' or trip_num == '':
        request.session['ses_enqiury_id'] = enquiry_id
        return redirect('tripdetail_insert')  # Define this URL in urls.py
    else:
        trip_id = TripdetailInfo.objects.get(tr_tripnumber=trip_num).id
        print('trip_id:', trip_id)
        # If trip_id is provided, redirect to update
        return redirect('tripdetail_update', tripdetail_id=trip_id)  # tripdetail_id is a keyword argument in the URL

@login_required(login_url='login_page')
def tripdetail_nav(request,tripdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print("I am inside Get add tripetails")
    trip_det_form = TripdetailaddForm()
    tripclosurefiles_form = TripclosurefilesForm()
    enquiry_num_id = tripdetail_id
    request.session['ses_enqiury_id'] = enquiry_num_id
    tripdetail_list=TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num_id)
    status_list = Tripstatusinfo.objects.filter(id__in=[1, 2, 3,8])
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
    user_id = request.session.get('ses_userID')
    enquiry_num_id = request.session.get('ses_enqiury_id')

    if request.method == "GET":
        if tripdetail_id == 0:
            print("I am inside Get add tripdetails")
            vehicle_allotment_id = request.GET.get('vehicle_allotment_id')

            initial_data = {}
            if vehicle_allotment_id:
                try:
                    va = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id)
                    initial_data = {
                        'tr_vehiclenumber': va.va_vehiclenumber,
                        'tr_drivername': va.va_drivername,
                        'tr_vehicletype': va.va_vehicletype,
                        'tr_vehiclesource': va.va_vehiclesource,
                        'tr_vehicletype_placed': va.va_vehicletype_placed,
                        'tr_drivernumber': va.va_drivernumber,
                        'tr_driver_lic': va.va_driver_lic,
                        'tr_category': 2,
                    }
                except Vehicle_allotmentInfo.DoesNotExist:
                    pass

            trip_det_form = TripdetailaddForm(initial=initial_data)
            if vehicle_allotment_id:
                trip_det_form.fields['tr_category'].widget.attrs['readonly'] = True

            previous_trip = TripdetailInfo.objects.filter(
                tr_enquirynumber_id=enquiry_num_id
            ).order_by('-tr_created_at').first()
            if previous_trip and previous_trip.tr_reportedlocation:
                trip_det_form.fields['tr_departedlocation'].initial = previous_trip.tr_reportedlocation
            else:
                print("No previous trip or reported location found.")

            tripclosurefiles_form = TripclosurefilesForm()
            enquiry_num_id = request.session.get('ses_enqiury_id')
            trip_list = TripdetailInfo.objects.select_related(
                'tr_approval', 'tr_approval__ta_approval_status'
            ).filter(tr_enquirynumber=enquiry_num_id)
            status_list = Tripstatusinfo.objects.filter(id__in=[1, 2, 3, 8])

            # ✅ Exclude already-used consignments for this enquiry
            used_consignments = TripdetailInfo.objects.filter(
                tr_enquirynumber=enquiry_num_id
            ).exclude(tr_consignmentnumber__isnull=True).values_list('tr_consignmentnumber_id', flat=True)

            consignment_list = ConsignmentdetailInfo.objects.filter(
                co_enquirynumber=enquiry_num_id
            ).exclude(id__in=used_consignments)

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
                'status_selected': 8,
            }

        else:
            trip_num = TripdetailInfo.objects.get(pk=tripdetail_id).tr_tripnumber
            enquiry_num = TripdetailInfo.objects.get(pk=tripdetail_id).tr_enquirynumber
            enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
            tripdetail = TripdetailInfo.objects.get(pk=tripdetail_id)
            request.session['ses_tripdetail_id'] = tripdetail_id

            trip_det_form = TripdetailaddForm(instance=tripdetail)
            tripclosure_files = Trip_closure_files_Info.objects.filter(tcf_tripnumber=trip_num).first()
            tripclosurefiles_form = TripclosurefilesForm(instance=tripclosure_files)
            trip_list = TripdetailInfo.objects.select_related(
                'tr_approval', 'tr_approval__ta_approval_status'
            ).filter(tr_enquirynumber=enquiry_num_id)
            status_list = Tripstatusinfo.objects.filter(id__in=[1, 2, 3, 8])

            trip_instance = TripdetailInfo.objects.get(pk=tripdetail_id)
            try:
                status_selected = trip_instance.tc_financestatus.id if trip_instance.tc_financestatus else 8
                print('status_selected', status_selected)
            except ObjectDoesNotExist:
                status_selected = None

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

            # ⚠️ Fixed missing newline before this line
            checklist = TripHighvalueInfo.objects.filter(
                thc_tripnumber=trip_instance.id,
                thc_enquirynumber=enquiry_num_id
            ).order_by('-id').first()

            trip_approvallist = (
                trip_instance.tr_approval and trip_instance.tr_approval.ta_approval_status_id == 1
            )

            context = {
                'first_name': first_name,
                'user_id': user_id,
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
            }

        return render(request, "asset_mgt_app/tripdetail_add.html", context)

    else:
        if tripdetail_id == 0:
            print("I am inside post add tripdetails")
            trip_det_form = TripdetailaddForm(request.POST, request.FILES)
            vehicle_allotment_id = request.POST.get('vehicle_allotment_id')
            tripclosurefiles_form = TripclosurefilesForm(request.POST, request.FILES)
            enquiry_num = request.session.get('ses_enqiury_id')
            cosnignment_number = request.POST.get('tr_consignmentnumber')
            vehicle_number = request.POST.get('tr_vehiclenumber')

            # ✅ Prevent using same consignment again (backend check)
            if cosnignment_number and TripdetailInfo.objects.filter(
                tr_consignmentnumber=cosnignment_number
            ).exists():
                messages.error(request, 'This consignment number is already used in another trip.')
                return redirect(request.META['HTTP_REFERER'])

            if vehicle_allotment_id:
                va = Vehicle_allotmentInfo.objects.get(pk=vehicle_allotment_id)

            if trip_det_form.is_valid():
                trip_status_list = TripdetailInfo.objects.filter(
                    tr_enquirynumber=enquiry_num, tr_vehiclenumber=vehicle_number
                )
                if cosnignment_number:
                    trip_status_list = trip_status_list.filter(tr_consignmentnumber=cosnignment_number)

                for trip in trip_status_list:
                    if trip.tc_financestatus and trip.tc_financestatus.id == 1:
                        messages.error(
                            request,
                            'A trip for this vehicle is still open. Please close it before creating a new one.'
                        )
                        return redirect(request.META['HTTP_REFERER'])

                # SAFELY GENERATE trip_num_next
                trip_num_next = 'TN_1000000'
                latest_trip = TripdetailInfo.objects.exclude(
                    tr_tripnumber__isnull=True
                ).exclude(tr_tripnumber='').order_by('-id').first()

                if latest_trip and latest_trip.tr_tripnumber and latest_trip.tr_tripnumber.startswith('TN_'):
                    try:
                        last_number = int(latest_trip.tr_tripnumber.replace('TN_', ''))
                        trip_num_next = f'TN_{last_number + 1}'
                    except (ValueError, TypeError):
                        pass

                trip = trip_det_form.save(commit=False)
                trip.tc_financestatus_id = 8

                # ✅ Process POD signature
                pod_data = request.POST.get('pod_signature_data')
                if pod_data:
                    format, imgstr = pod_data.split(';base64,')
                    ext = format.split('/')[-1]
                    data = ContentFile(base64.b64decode(imgstr), name=f'pod_signature.{ext}')
                    trip.td_pod = data

                trip.save()
                tripclosurefiles_form.save()

                print("Main Form is Valid")
                last_id = TripdetailInfo.objects.latest('id').id
                last_id_files = Trip_closure_files_Info.objects.latest('id').id
                TripdetailInfo.objects.filter(id=last_id).update(tr_tripnumber=trip_num_next)
                Trip_closure_files_Info.objects.filter(id=last_id_files).update(tcf_tripnumber=trip_num_next)

                tripdetail_list = TripdetailInfo.objects.filter(
                    tr_enquirynumber=enquiry_num
                ).values_list('tr_tripnumber', flat=True)
                EnquirynoteInfo.objects.filter(
                    en_enquirynumber=enquiry_num
                ).update(en_tripdetails=list(tripdetail_list))
                messages.success(request, 'Record Updated Successfully')

            else:
                print("Main Form is not Valid")
                messages.error(request, 'Record Not Saved. Please Enter All Required Fields')

        else:
            print("I am inside post edit tripdetails")
            trip_num = TripdetailInfo.objects.get(pk=tripdetail_id).tr_tripnumber
            tripdetail = TripdetailInfo.objects.get(pk=tripdetail_id)
            trip_det_form = TripdetailaddForm(request.POST, request.FILES, instance=tripdetail)
            tripclosure_files = Trip_closure_files_Info.objects.filter(tcf_tripnumber=trip_num).first()
            tripclosurefiles_form = TripclosurefilesForm(request.POST, request.FILES, instance=tripclosure_files)
            enquiry_num = tripdetail.tr_enquirynumber.id

            if trip_det_form.is_valid():
                trip = trip_det_form.save(commit=False)

                # ✅ Save POD Signature if available
                pod_data = request.POST.get("pod_signature_data", None)
                if pod_data:
                    format, imgstr = pod_data.split(';base64,')
                    ext = format.split('/')[-1]
                    data = ContentFile(base64.b64decode(imgstr), name=f"{trip_num}_pod_signature.{ext}")
                    trip.td_pod = data

                trip.save()
                tripclosurefiles_form.save()

                print("Main Form is Valid")
                tripdetail_list = TripdetailInfo.objects.filter(
                    tr_enquirynumber=enquiry_num
                ).values_list('tr_tripnumber', flat=True)
                EnquirynoteInfo.objects.filter(pk=enquiry_num).update(en_tripdetails=list(tripdetail_list))
                messages.success(request, 'Record Updated Successfully')

            else:
                for field, errors in trip_det_form.errors.items():
                    for error in errors:
                        print(f"Error in {field}: {error}")
                        messages.error(request, f"Error in {field}: {error}")
                print("Trip Details Main Form is not Valid")
                messages.error(request, 'Record Not Saved. Please Enter All Required Fields')

    return redirect(request.META['HTTP_REFERER'])
# List tripdetail
@login_required(login_url='login_page')
def tripdetail_list(request):
    first_name = request.session.get('first_name')
    context = {'tripdetail_list' : TripdetailInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/tripdetail_list.html",context)

#Delete tripdetail
@login_required(login_url='login_page')
def tripdetail_delete(request,tripdetail_id):
    tripdetail = TripdetailInfo.objects.get(pk=tripdetail_id)
    enquiry_num = TripdetailInfo.objects.get(pk=tripdetail_id).tr_enquirynumber
    trip_num = TripdetailInfo.objects.get(pk=tripdetail_id).tr_tripnumber
    tripdetail.delete()
    try:
        tripdetail_list = TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num).values_list('tr_tripnumber',flat=True)
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_tripdetails=list(tripdetail_list))
    except ObjectDoesNotExist:
        tripdetail_list = []
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_tripdetails=list(tripdetail_list))
    trip_closure_files=list(Trip_closure_files_Info.objects.filter(tcf_tripnumber=trip_num).values_list('tcf_tripnumber',flat=True))
    for i in trip_closure_files:
        trip_files = Trip_closure_files_Info.objects.get(tcf_tripnumber=i)
        trip_files.delete()
    # return redirect('/SMS/tripdetail_list')
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def load_vehicle_details(request):
    enquiry_number = request.GET.get('enquiry_number')
    consignment_number = request.GET.get('consignment_number')
    count=0
    trip_number=list(TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_number,tr_consignmentnumber=consignment_number,tc_financestatus=1).values_list('tr_tripnumber',flat=True))
    if len(trip_number)>0:
        count=count+1
    if count<1:
        vehicle_type_requested=list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,va_consignmentnumber=consignment_number).values_list('va_vehicletype',flat=True))
        vehicle_type_placed=list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,va_consignmentnumber=consignment_number).values_list('va_vehicletype_placed',flat=True))
        vehicletype_source = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,va_consignmentnumber=consignment_number).values_list('va_vehiclesource', flat=True))
        vehicletype_number = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,va_consignmentnumber=consignment_number).values_list('va_vehiclenumber', flat=True))
        driver_name = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,va_consignmentnumber=consignment_number).values_list('va_drivername', flat=True))
        driver_number = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,va_consignmentnumber=consignment_number).values_list('va_driver_lic', flat=True))
        driver_license = list(Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number,va_consignmentnumber=consignment_number).values_list('va_drivernumber', flat=True))
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
        count_val=count
        data = {
            'count_val':count_val,
        }
    return HttpResponse(json.dumps(data))

@login_required(login_url='login_page')
def trip_email(request):
    recipient = request.POST.get('recipient')
    tripdetail_id = request.session.get('ses_tripdetail_id')

    if not tripdetail_id:
        messages.error(request, "Trip detail ID is missing. Please try again.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

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

    def format_datetime(value):
        if not value:
            return ""
        try:
            if isinstance(value, str):
                value = datetime.fromisoformat(value.replace('Z', '').split('+')[0].strip())
            return value.strftime("%Y-%m-%d %H:%M")  # 👈 no seconds
        except Exception:
            return str(value)

    # ---- Parse date fields ----
    departed_date = parse_dt(trip.tr_departeddate)
    loading_time = parse_dt(trip.tr_loading_time)
    unloading_time = parse_dt(trip.tr_unloading_time)
    reported_date = parse_dt(trip.tr_reporteddate)

    # ---- Date validation ----
    invalid_dates = []
    if departed_date and loading_time and departed_date > loading_time:
        invalid_dates.append("Loading Time cannot be before Departed Date.")
    if loading_time and unloading_time and loading_time > unloading_time:
        invalid_dates.append("Unloading Time cannot be before Loading Time.")
    if departed_date and reported_date and departed_date > reported_date:
        invalid_dates.append("Reported Date cannot be before Departed Date.")

    if invalid_dates:
        messages.error(request, "⚠️ Date format or order issue:\n" + "\n".join(invalid_dates))
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # ---- Email text ----
    status_map = {'trip started': 'started', 'trip closed': 'closed'}
    trip_status_text = f"Trip has been {status_map.get(trip.tc_financestatus, trip.tc_financestatus)}"

    recipient_list = [email.strip() for email in recipient.split(',')]
    subject = f"Trip {trip.tr_tripnumber} - Update"

    # ---- Build HTML Email ----
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
                    }}
                    th, td {{
                        border: 1px solid black;
                        padding: 8px;
                    }}
                    th {{
                        background-color: #f4f4f4;
                        text-align: left;
                    }}
                    td {{
                        vertical-align: top;
                    }}
                    .remarks div {{
                        margin-bottom: 5px;
                    }}
               </style>
            </head>
            <body>
                <p>Dear Team,</p>
                <p>{trip_status_text}</p>
                <p>Please find below the trip details:</p>
                <table>
                    <tr><th>Trip Number</th><td>{trip.tr_tripnumber}</td></tr>
                    <tr><th>Enquiry Number</th><td>{trip.tr_enquirynumber}</td></tr>
                    <tr><th>Consignment Number</th><td>{trip.tr_consignmentnumber}</td></tr>
                    <tr><th>Vehicle Type</th><td>{trip.tr_vehicletype}</td></tr>
                    <tr><th>Vehicle Type Placed</th><td>{trip.tr_vehicletype_placed}</td></tr>
                    <tr><th>Vehicle Number</th><td>{trip.tr_vehiclenumber}</td></tr>
                    <tr><th>Driver Name</th><td>{trip.tr_drivername}</td></tr>
                    <tr><th>Driver Number</th><td>{trip.tr_drivernumber}</td></tr>
                    <tr><th>Trip Category</th><td>{trip.tr_category}</td></tr>
                    <tr><th>Departed Location</th><td>{trip.tr_departedlocation}</td></tr>
                    <tr><th>Departed KM</th><td>{trip.tr_departedkm}</td></tr>
                    <tr><th>Departed Date</th><td>{format_datetime(trip.tr_departeddate)}</td></tr>
                    <tr><th>Loading Time</th><td>{format_datetime(trip.tr_loading_time)}</td></tr>
                    <tr><th>Un-Loading Time</th><td>{format_datetime(trip.tr_unloading_time)}</td></tr>
                    <tr><th>Reported Location</th><td>{trip.tr_reportedlocation}</td></tr>
                    <tr><th>Reported KM</th><td>{trip.tr_reportedkm}</td></tr>
                    <tr><th>Reported Date</th><td>{format_datetime(trip.tr_reporteddate)}</td></tr>
                    <tr><th>Trip Status</th><td>{trip.tc_financestatus}</td></tr>
                    <tr><th>POD Number</th><td>{trip.tc_pod}</td></tr>
                    <tr><th>Updated By</th><td>{trip.tr_updated_by}</td></tr>
                    <tr>
                        <th>Remarks</th>
                        <td class="remarks">
                            {''.join(f'<div>{remark}</div>' for remark in (trip.tr_remarks or '').splitlines())}
                        </td>
                    </tr>
                </table>
                <p>Regards,<br>Transport Admin</p>
            </body>
        </html>
    """

    # ---- Attachment Handling ----
    attachment_path = trip.tc_pod_attachment.path if trip.tc_pod_attachment else None
    attachment_file = open(attachment_path, 'rb') if attachment_path else None
    file_name = trip.tc_pod_attachment.name.split("/")[-1] if trip.tc_pod_attachment else None

    # ---- Send Email ----
    send_department_email(
        department='itadmin',
        subject=subject,
        message=email_body,
        recipient_list=recipient_list,
        attachment=attachment_file,
        attachment_type="application/octet-stream" if attachment_file else None,
        file_name=file_name,
        email_type=1
    )

    messages.success(request, "Trip email sent successfully with attachment.")
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required(login_url='login_page')
def load_truck_details(request):
    consignment_number = request.GET.get("consignment_number")
    enquiry_number = request.GET.get("enquiry_number")
    filtered_records = Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry_number)

    try:
        # Fetch truck number from ConsignmentdetailInfo

        truck_number = ConsignmentdetailInfo.objects.get(pk=consignment_number).co_vehicelnumber

        # Fetch vehicle details from Vehicle_allotmentInfo (search in both fields)
        vehicle_info = filtered_records.filter(
            Q(va_vehiclenumber__vm_registrationnumber=truck_number) | Q(va_vehiclenumber_mkt=truck_number)
        ).first()  # Get first matching record

        if vehicle_info:
            data = {
                "truck_number": truck_number,
                "va_drivername": vehicle_info.va_drivername,
                "va_drivernumber": vehicle_info.va_drivernumber,
                "va_vehiclesource": vehicle_info.va_vehiclesource.id if vehicle_info.va_vehiclesource else None,
                "va_vehicletype_placed": vehicle_info.va_vehicletype_placed.id if vehicle_info.va_vehicletype_placed else None,
                "va_vehicletype": vehicle_info.va_vehicletype.id if vehicle_info.va_vehicletype else None,
                "va_driver_lic": vehicle_info.va_driver_lic,
            }
        else:
            data = {"error": "No vehicle allotment details found for this Consignment number"}

    except ObjectDoesNotExist:
        data = {"error": "Consignment number not found"}

    return JsonResponse(data)


def fleet_management_view(request):
    vehicles = VehiclemasterInfo.objects.all()
    vehicle_status_list = []

    for vehicle in vehicles:
        trip = TripdetailInfo.objects.filter(tr_vehiclenumber=vehicle.vm_registrationnumber).order_by(
            '-tr_created_at').first()

        if trip:
            status = {
                'registration_number': vehicle.vm_registrationnumber,
                'driver_name': trip.tr_drivername,
                'from_location': trip.tr_departedlocation.place_name if trip.tr_departedlocation else None,
                'to_location': trip.tr_reportedlocation.place_name if trip.tr_reportedlocation else None,
                'vehicle_type': trip.tr_vehicletype_placed.vt_vehicletype if trip.tr_vehicletype_placed else None,
                'vehicle_source': trip.tr_vehiclesource.ow_ownership if trip.tr_vehiclesource else None,
                'departed_date': trip.tr_departeddate,
                'reported_date': trip.tr_reporteddate,
                'trip_status': trip.tc_financestatus.status if trip.tc_financestatus else 'Unknown',
                'trip_number': trip.tr_tripnumber,
                'status': 'In Trip'
            }
        else:
            status = {
                'registration_number': vehicle.vm_registrationnumber,
                'driver_name': '',
                'from_location': '',
                'to_location': '',
                'trip_status': '',
                'trip_number': '',
                'vehicle_type': '',
                'vehicle_source': '',
                'departed_date': '',
                'reported_date': '',
                'status': 'Available'
            }

        vehicle_status_list.append(status)

    return render(request, "asset_mgt_app/fleet_management.html", {'vehicle_status_list': vehicle_status_list})

@login_required(login_url='login_page')
def get_sim_tracking_data(request):
    trip_details = TripdetailInfo.objects.filter(tr_vehiclesource=3,tc_financestatus=1).values(
        'tr_vehiclenumber', 'tr_drivername', 'tr_drivernumber', 'tr_track_link','tc_financestatus'
    )

    sim_data = []
    for trip in trip_details:
        sim_data.append({
            'sim_number': trip['tr_drivernumber'] or 'NA',
            'imei': trip['tr_vehiclenumber'],
            'status': trip['tc_financestatus'],
            'track_url': trip['tr_track_link'] ,
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