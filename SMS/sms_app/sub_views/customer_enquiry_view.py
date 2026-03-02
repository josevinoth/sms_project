from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Q
from ..sub_models.enquirynote_mod import EnquirynoteInfo
from ..sub_models.customer_mod import CustomerInfo
from ..sub_models.user_ext_mod import User_extInfo
from ..sub_models.tripdetail_mod import TripdetailInfo, Trip_closure_files_Info
from ..sub_models.consignmentdetail_mod import ConsignmentdetailInfo
from ..sub_models.enquirynote_vehicle_mod import Enquirynotevehicle
from ..models import Location_info, StatusList, MyUser, CustomerdepartmentInfo, Places, VehiclecategoryInfo, VehicletypeInfo, VehiclemasterInfo

def get_customer_context(request):
    """Helper to get the linked customer, department, and LP status for the portal."""
    user = request.user
    customer = None
    department = None
    is_lp = False
    
    try:
        user_ext = User_extInfo.objects.get(user=user)
        customer = user_ext.linked_customer
        is_lp = user_ext.is_lp_customer
        
        # Check for department override in session (selected at login for regular users)
        dept_id = request.session.get('ses_customer_dept_id')
        if dept_id:
            department = CustomerdepartmentInfo.objects.filter(id=dept_id).first()
        
        # Fallback to name-based match if no session ID (e.g. legacy login or direct link)
        if not department and user_ext.department:
             department = CustomerdepartmentInfo.objects.filter(ct_customerdepartment__iexact=user_ext.department.dept_name).first()
             
    except User_extInfo.DoesNotExist:
        pass
        
    return customer, department, is_lp

@login_required
def ajax_get_vehicle_types(request):
    """AJAX view to return all vehicle types (unfiltered)."""
    types = VehicletypeInfo.objects.all().order_by('vt_vehicletype').values('id', 'vt_vehicletype')
    return JsonResponse(list(types), safe=False)

@login_required
def customer_dashboard(request):
    """
    Premium dashboard for customers showing summary stats and recent shipments.
    """
    customer, department, is_lp = get_customer_context(request)
    
    if not customer:
        messages.error(request, 'Your account is not linked to a Customer Profile. Please contact support.')
        return render(request, 'asset_mgt_app/customer_portal_dashboard.html', {'error': True})

    # Base queryset for enquiries
    enquiry_qs = EnquirynoteInfo.objects.filter(en_customername=customer)
    if department:
        enquiry_qs = enquiry_qs.filter(en_customerdepartment=department)

    # All trips for this customer
    all_trips = TripdetailInfo.objects.filter(tr_enquirynumber__en_customername=customer)
    if department:
        all_trips = all_trips.filter(tr_enquirynumber__en_customerdepartment=department)

    completed_statuses = [2, 3, 4, 5, 7, 9]

    # Count DISTINCT ENQUIRIES (not individual trips) so numbers match the list pages
    # In-Transit = distinct enquiries with at least one in-transit trip (status 1)
    in_transit = enquiry_qs.filter(
        tripdetailinfo__tc_financestatus_id=1
    ).distinct().count()

    # Active = distinct enquiries with a trip that has a vehicle BUT NOT yet started AND NOT completed
    active_enquiries = enquiry_qs.filter(
        id__in=all_trips.filter(
            tr_vehiclenumber__isnull=False
        ).exclude(
            tr_vehiclenumber=''
        ).exclude(
            tc_financestatus_id__in=completed_statuses + [1]
        ).values_list('tr_enquirynumber_id', flat=True).distinct()
    ).count()

    # Delivered = distinct enquiries with a completed trip this year
    delivered = enquiry_qs.filter(
        tripdetailinfo__tc_financestatus_id__in=[2, 7]
    ).distinct().count()

    # Cancelled = distinct enquiries with a cancelled trip
    cancelled = enquiry_qs.filter(
        tripdetailinfo__tc_financestatus_id=3
    ).distinct().count()

    # Recent Shipments — include driver and consignment info
    recent_shipments = all_trips.select_related(
        'tr_enquirynumber', 'tc_financestatus', 'tr_consignmentnumber'
    ).order_by('-tr_created_at')[:5]

    return render(request, 'asset_mgt_app/customer_portal_dashboard.html', {
        'customer': customer,
        'department': department,
        'active_enquiries': active_enquiries,
        'in_transit': in_transit,
        'delivered': delivered,
        'cancelled': cancelled,
        'recent_shipments': recent_shipments,
    })

@login_required
def customer_enquiry_add(request):
    """
    Simplified enquiry submission form for logged-in customers.
    """
    customer, department, is_lp = get_customer_context(request)
    
    if request.method == 'POST':
        from_loc_id = request.POST.get('from_location')
        to_loc_id = request.POST.get('to_location')
        # New structured vehicle fields
        category_id = request.POST.get('vehicle_category')
        type_id = request.POST.get('vehicle_type')
        
        cargo_details = request.POST.get('cargo_details', '') # Still capture for fallback/legacy
        
        # Combined datetime-local field
        pickup_datetime_str = request.POST.get('pickup_datetime', '')
        pickup_date = None
        req_time = None
        if pickup_datetime_str:
            try:
                # datetime-local format: "2026-02-22T10:30"
                parts = pickup_datetime_str.split('T')
                pickup_date = parts[0]
                req_time = parts[1] if len(parts) > 1 else None
            except Exception:
                pickup_date = pickup_datetime_str
        
        # Fallback: check old separate fields
        if not pickup_date:
            pickup_date = request.POST.get('pickup_date')
        if not req_time:
            req_time = request.POST.get('req_time')
        
        # New fields for LP/Agent
        agent_name = request.POST.get('agent_name')
        no_of_veh = request.POST.get('no_of_veh', 0)
        no_of_pcs = request.POST.get('no_of_pcs', 0)
        weight = request.POST.get('weight')
        dimensions = request.POST.get('dimensions')
        cbm = request.POST.get('cbm')
        
        if not customer:
            messages.error(request, 'Account link missing.')
            return redirect('customer_dashboard')
            
        try:
            from_loc = Places.objects.get(id=from_loc_id) if from_loc_id else None
            to_loc = Places.objects.get(id=to_loc_id) if to_loc_id else None
            
            # Get objects for structured storage and string names
            category_name = ""
            vc_obj = None
            if category_id:
                vc_obj = VehiclecategoryInfo.objects.filter(id=category_id).first()
                if vc_obj:
                    category_name = vc_obj.vc_vehiclecategory

            vt_obj = None
            if type_id:
                vt_obj = VehicletypeInfo.objects.filter(id=type_id).first()
                if vt_obj:
                    # User requested Type to be saved in en_consignmentdetails
                    cargo_details = vt_obj.vt_vehicletype

            # Department: use form selection, fallback to session
            dept_id = request.POST.get('customer_department')
            selected_dept = None
            if dept_id:
                selected_dept = CustomerdepartmentInfo.objects.filter(id=dept_id).first()
            if not selected_dept:
                selected_dept = department

            enquiry = EnquirynoteInfo(
                en_customername=customer,
                en_customerdepartment=selected_dept,
                en_assignedto=MyUser.objects.filter(is_superuser=True).first() or request.user,
                en_status=StatusList.objects.filter(id=6).first(),
                en_consignmentdetails=cargo_details,
                en_vehicledetails=category_name, # Save category here as string
                en_pickupdatetime=pickup_date if pickup_date else timezone.now(),
                en_fromlocaion=from_loc,
                en_tolocation=to_loc,
                en_created_at=timezone.now(),
                
                # New fields
                en_agent_name=agent_name,
                en_vehicle_req_time=req_time if req_time else None,
                en_no_of_vehicles=int(no_of_veh) if no_of_veh else 0,
                en_no_of_pcs=int(no_of_pcs) if no_of_pcs else 0,
                en_weight=weight,
                en_dimensions=dimensions,
                en_cbm=cbm
            )
            enquiry.save() # Save first to get ID
            
            # Generate number based on ID to match internal pattern
            enquiry.en_enquirynumber = f"WEB_EN_{1000000 + enquiry.id}"
            enquiry.save(update_fields=['en_enquirynumber'])
            
            # Save structured vehicle info for internal view sync using fetched objects
            if vc_obj and vt_obj:
                try:
                    Enquirynotevehicle.objects.create(
                        env_enquirynumber=enquiry,
                        env_vehiclecategory=vc_obj,
                        env_vehicletype=vt_obj,
                        env_quantity=int(no_of_veh) if no_of_veh else 1,
                        env_updated_by=request.user
                    )
                except Exception as inner_e:
                     print(f"Failed to create vehicle detail: {inner_e}")
            
            messages.success(request, f'Enquiry {enquiry.en_enquirynumber} submitted successfully!')
            return redirect('customer_enquiry_list')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            
    places = Places.objects.all().order_by('place_name')
    categories = VehiclecategoryInfo.objects.all().order_by('vc_vehiclecategory')
    types = VehicletypeInfo.objects.all().order_by('vt_vehicletype')
    departments = CustomerdepartmentInfo.objects.all().order_by('ct_customerdepartment')

    return render(request, 'asset_mgt_app/customer_enquiry_add.html', {
        'customer': customer,
        'department': department,
        'departments': departments,
        'places': places,
        'categories': categories,
        'types': types,
        'is_lp': is_lp
    })

@login_required
def customer_enquiry_edit(request, enquiry_id):
    """Edit an existing customer enquiry."""
    customer, department, is_lp = get_customer_context(request)
    if not customer:
        return redirect('customer_dashboard')

    enquiry = get_object_or_404(EnquirynoteInfo, id=enquiry_id, en_customername=customer)

    if request.method == 'POST':
        from_loc_id = request.POST.get('from_location')
        to_loc_id = request.POST.get('to_location')
        category_id = request.POST.get('vehicle_category')
        type_id = request.POST.get('vehicle_type')
        cargo_details = request.POST.get('cargo_details', '')
        pickup_date = request.POST.get('pickup_date')
        agent_name = request.POST.get('agent_name')
        req_time = request.POST.get('req_time')
        no_of_veh = request.POST.get('no_of_veh', 0)
        no_of_pcs = request.POST.get('no_of_pcs', 0)
        weight = request.POST.get('weight')
        dimensions = request.POST.get('dimensions')
        cbm = request.POST.get('cbm')

        try:
            from_loc = Places.objects.get(id=from_loc_id) if from_loc_id else None
            to_loc = Places.objects.get(id=to_loc_id) if to_loc_id else None

            category_name = ""
            vc_obj = None
            if category_id:
                vc_obj = VehiclecategoryInfo.objects.filter(id=category_id).first()
                if vc_obj:
                    category_name = vc_obj.vc_vehiclecategory

            vt_obj = None
            if type_id:
                vt_obj = VehicletypeInfo.objects.filter(id=type_id).first()
                if vt_obj:
                    cargo_details = vt_obj.vt_vehicletype

            # Department
            dept_id = request.POST.get('customer_department')
            selected_dept = None
            if dept_id:
                selected_dept = CustomerdepartmentInfo.objects.filter(id=dept_id).first()
            if not selected_dept:
                selected_dept = department

            enquiry.en_customerdepartment = selected_dept
            enquiry.en_consignmentdetails = cargo_details
            enquiry.en_vehicledetails = category_name
            enquiry.en_pickupdatetime = pickup_date if pickup_date else enquiry.en_pickupdatetime
            enquiry.en_fromlocaion = from_loc
            enquiry.en_tolocation = to_loc
            enquiry.en_agent_name = agent_name
            enquiry.en_vehicle_req_time = req_time if req_time else None
            enquiry.en_no_of_vehicles = int(no_of_veh) if no_of_veh else 0
            enquiry.en_no_of_pcs = int(no_of_pcs) if no_of_pcs else 0
            enquiry.en_weight = weight
            enquiry.en_dimensions = dimensions
            enquiry.en_cbm = cbm
            enquiry.save()

            # Update vehicle detail record
            if vc_obj and vt_obj:
                env = Enquirynotevehicle.objects.filter(env_enquirynumber=enquiry).first()
                if env:
                    env.env_vehiclecategory = vc_obj
                    env.env_vehicletype = vt_obj
                    env.env_quantity = int(no_of_veh) if no_of_veh else 1
                    env.env_updated_by = request.user
                    env.save()
                else:
                    Enquirynotevehicle.objects.create(
                        env_enquirynumber=enquiry,
                        env_vehiclecategory=vc_obj,
                        env_vehicletype=vt_obj,
                        env_quantity=int(no_of_veh) if no_of_veh else 1,
                        env_updated_by=request.user
                    )

            messages.success(request, f'Enquiry {enquiry.en_enquirynumber} updated successfully!')
            return redirect('customer_enquiry_list')

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    places = Places.objects.all().order_by('place_name')
    categories = VehiclecategoryInfo.objects.all().order_by('vc_vehiclecategory')
    types = VehicletypeInfo.objects.all().order_by('vt_vehicletype')
    departments = CustomerdepartmentInfo.objects.all().order_by('ct_customerdepartment')

    # Get current vehicle detail for pre-selection
    env = Enquirynotevehicle.objects.filter(env_enquirynumber=enquiry).first()

    return render(request, 'asset_mgt_app/customer_enquiry_add.html', {
        'customer': customer,
        'department': enquiry.en_customerdepartment,
        'departments': departments,
        'places': places,
        'categories': categories,
        'types': types,
        'is_lp': is_lp,
        'enquiry': enquiry,
        'env': env,
        'edit_mode': True,
    })

@login_required
def customer_enquiry_list(request):
    """
    List previous enquiries and current shipments for the customer.
    """
    customer, _, is_lp = get_customer_context(request)
    if not customer:
        return redirect('customer_dashboard')

    search_query = request.GET.get('q', '')
    
    # Get enquiries with optimized queries using select_related
    enquiries_qs = EnquirynoteInfo.objects.filter(
        en_customername=customer
    ).select_related(
        'en_customername',
        'en_fromlocaion',
        'en_tolocation',
        'en_customerdepartment'
    ).prefetch_related(
        'tripdetailinfo_set',
        'vehicle_allotmentinfo_set',
        'consignmentdetailinfo_set'
    )
    
    if search_query:
        enquiries_qs = enquiries_qs.filter(
            Q(en_enquirynumber__icontains=search_query) |
            Q(en_fromlocaion__place_name__icontains=search_query) |
            Q(en_tolocation__place_name__icontains=search_query) |
            Q(tripdetailinfo__tr_tripnumber__icontains=search_query)
        ).distinct()

    # Status filter from dashboard cards
    status_filter = request.GET.get('status', '')
    _completed = [2, 3, 4, 5, 7, 9]
    if status_filter == 'active':
        # Active = enquiries with a trip that has a vehicle, NOT yet started AND NOT completed
        active_trip_enq_ids = TripdetailInfo.objects.filter(
            tr_enquirynumber__en_customername=customer
        ).filter(
            tr_vehiclenumber__isnull=False
        ).exclude(
            tr_vehiclenumber=''
        ).exclude(
            tc_financestatus_id__in=_completed + [1]
        ).values_list('tr_enquirynumber_id', flat=True).distinct()
        enquiries_qs = enquiries_qs.filter(id__in=active_trip_enq_ids)
    elif status_filter == 'transit':
        enquiries_qs = enquiries_qs.filter(tripdetailinfo__tc_financestatus_id=1).distinct()
    elif status_filter == 'delivered':
        enquiries_qs = enquiries_qs.filter(tripdetailinfo__tc_financestatus_id__in=[2, 7]).distinct()
    elif status_filter == 'cancelled':
        enquiries_qs = enquiries_qs.filter(tripdetailinfo__tc_financestatus_id=3).distinct()

    enquiries_qs = enquiries_qs.order_by('-en_created_at')

    # Pagination - 50 items per page
    from django.core.paginator import Paginator
    paginator = Paginator(enquiries_qs, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Build enriched data for template
    enquiry_list = []
    for enq in page_obj:
        # When status filter is active, pick the matching trip
        if status_filter == 'transit':
            trip = enq.tripdetailinfo_set.filter(tc_financestatus_id=1).first()
        elif status_filter == 'delivered':
            trip = enq.tripdetailinfo_set.filter(tc_financestatus_id__in=[2, 7]).first()
        elif status_filter == 'cancelled':
            trip = enq.tripdetailinfo_set.filter(tc_financestatus_id=3).first()
        elif status_filter == 'active':
            trip = None  # Active enquiries have no trips yet
        else:
            trip = enq.tripdetailinfo_set.first()
        va = enq.vehicle_allotmentinfo_set.first()
        cn = enq.consignmentdetailinfo_set.first()

        # Vehicle number: trip > allotment (own) > allotment (market)
        vehicle_no = '-'
        if trip and trip.tr_vehiclenumber:
            vehicle_no = trip.tr_vehiclenumber
        elif va:
            if va.va_vehiclenumber:
                vehicle_no = str(va.va_vehiclenumber)
            elif va.va_vehiclenumber_mkt:
                vehicle_no = va.va_vehiclenumber_mkt

        # Customer reference
        customer_ref = enq.en_enquirynumber
        if trip and trip.tr_customerref:
            customer_ref = trip.tr_customerref

        # Consignment number: trip > direct consignment
        cnote = '-'
        if trip and trip.tr_consignmentnumber:
            cnote = trip.tr_consignmentnumber.co_consignmentnumber
        elif cn:
            cnote = cn.co_consignmentnumber

        # Tracking link - generate from vehicle number using Trans GPS
        track_link = ''
        if vehicle_no and vehicle_no != '-':
            track_link = f'/SMS/SMS/customer_track_vehicle/?vehicle={vehicle_no}'

        # POD download - only show if file actually exists
        import os
        from django.conf import settings
        pod_trip_id = None
        if trip and trip.tc_financestatus_id in [2, 7]:
            # Check closure files
            closure = Trip_closure_files_Info.objects.filter(tcf_tripnumber=trip.tr_tripnumber).first()
            if closure and closure.tcf_pod:
                fpath = os.path.join(settings.MEDIA_ROOT, str(closure.tcf_pod))
                if os.path.exists(fpath):
                    pod_trip_id = trip.id
            # Check trip attachment
            if not pod_trip_id and trip.tc_pod_attachment:
                fpath = os.path.join(settings.MEDIA_ROOT, str(trip.tc_pod_attachment))
                if os.path.exists(fpath):
                    pod_trip_id = trip.id

        # Consignment ID for PDF link
        consignment_id = None
        cus_ref_num = None
        if trip and trip.tr_consignmentnumber:
            consignment_id = trip.tr_consignmentnumber.id
            cus_ref_num = trip.tr_consignmentnumber.co_cusrefnum
        elif cn:
            consignment_id = cn.id
            cus_ref_num = cn.co_cusrefnum

        # Driver number
        driver_number = None
        if trip and trip.tr_drivernumber:
            driver_number = trip.tr_drivernumber

        enquiry_list.append({
            'enq': enq,
            'vehicle_no': vehicle_no,
            'customer_ref': customer_ref,
            'cnote': cnote,
            'track_link': track_link,
            'pod_trip_id': pod_trip_id,
            'consignment_id': consignment_id,
            'cus_ref_num': cus_ref_num,
            'driver_number': driver_number,
        })
    
    return render(request, 'asset_mgt_app/customer_enquiry_list.html', {
        'enquiry_list': enquiry_list,
        'search_query': search_query,
        'page_obj': page_obj,
        'status_filter': status_filter,
    })

@login_required
def customer_track_vehicle(request):
    """Customer-facing vehicle tracking page with clean UI."""
    vehicle_number = request.GET.get('vehicle', '').upper().replace(' ', '').replace('-', '')
    return render(request, 'asset_mgt_app/customer_track_vehicle.html', {
        'vehicle_number': vehicle_number,
    })


@login_required
def customer_shipment_tracking(request, trip_id):
    """
    Real-time tracking view for a specific shipment.
    """
    customer, _, is_lp = get_customer_context(request)
    trip = get_object_or_404(TripdetailInfo, id=trip_id, tr_enquirynumber__en_customername=customer)
    
    return render(request, 'asset_mgt_app/customer_shipment_tracking.html', {
        'trip': trip,
        'customer': customer
    })

@login_required
def download_pod(request, trip_id):
    """View POD inline — works in both WebView and desktop browsers."""
    import os
    from django.conf import settings

    customer, _, is_lp = get_customer_context(request)
    trip = get_object_or_404(TripdetailInfo, id=trip_id, tr_enquirynumber__en_customername=customer)

    file_url = None
    file_name = None
    is_pdf = False

    # Try closure files first
    closure = Trip_closure_files_Info.objects.filter(tcf_tripnumber=trip.tr_tripnumber).first()
    if closure and closure.tcf_pod:
        fp = os.path.join(settings.MEDIA_ROOT, str(closure.tcf_pod))
        if os.path.exists(fp):
            file_url = closure.tcf_pod.url
            file_name = os.path.basename(str(closure.tcf_pod))
            is_pdf = file_name.lower().endswith('.pdf')

    # Fallback to trip attachment
    if not file_url and trip.tc_pod_attachment:
        fp = os.path.join(settings.MEDIA_ROOT, str(trip.tc_pod_attachment))
        if os.path.exists(fp):
            file_url = trip.tc_pod_attachment.url
            file_name = os.path.basename(str(trip.tc_pod_attachment))
            is_pdf = file_name.lower().endswith('.pdf')

    if not file_url:
        messages.error(request, "POD document not found for this shipment.")
        return redirect(request.META.get('HTTP_REFERER', 'customer_dashboard'))

    return render(request, 'asset_mgt_app/view_pod.html', {
        'file_url': file_url,
        'file_name': file_name,
        'is_pdf': is_pdf,
        'trip_number': trip.tr_tripnumber,
    })

@login_required
def download_dmr(request, trip_id):
    """Generate and download a single-trip DMR report as Excel."""
    from .dmr_report_view import get_dmr_headers, get_dmr_rows
    from django.http import HttpResponse
    from io import BytesIO
    from openpyxl import Workbook

    customer, _, is_lp = get_customer_context(request)
    trip = get_object_or_404(TripdetailInfo, id=trip_id, tr_enquirynumber__en_customername=customer)
    
    # Use existing DMR logic
    dept_name = trip.tr_enquirynumber.en_customerdepartment.dept_name if trip.tr_enquirynumber.en_customerdepartment else "Transport"
    headers, template_key = get_dmr_headers(customer.cu_name, dept_name, trip.tr_departedlocation_id, trip.tr_reportedlocation_id)
    rows = get_dmr_rows([trip], headers, template_key, customer.cu_name)

    wb = Workbook()
    ws = wb.active
    ws.title = "DMR Report"
    ws.append(headers)
    for row in rows:
        ws.append(row)

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="DMR_{trip.tr_tripnumber}.xlsx"'
    return response

@login_required
def customer_documents(request):
    """Documents page showing all PODs and documents for the customer."""
    customer, department, is_lp = get_customer_context(request)
    if not customer:
        return redirect('customer_dashboard')
    
    # Get all trips for this customer
    trips_qs = TripdetailInfo.objects.filter(
        tr_enquirynumber__en_customername=customer
    ).select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_fromlocaion',
        'tr_enquirynumber__en_tolocation',
        'tc_financestatus'
    )
    if department:
        trips_qs = trips_qs.filter(tr_enquirynumber__en_customerdepartment=department)
    
    trips_qs = trips_qs.order_by('-tr_created_at')
    
    # Build document list
    import os
    from django.conf import settings
    documents = []
    for trip in trips_qs:
        # Check closure files for POD
        closure = Trip_closure_files_Info.objects.filter(tcf_tripnumber=trip.tr_tripnumber).first()
        has_pod = False
        pod_source = ''
        
        if closure and closure.tcf_pod:
            file_path = os.path.join(settings.MEDIA_ROOT, str(closure.tcf_pod))
            if os.path.exists(file_path):
                has_pod = True
                pod_source = 'closure'
        if not has_pod and trip.tc_pod_attachment:
            file_path = os.path.join(settings.MEDIA_ROOT, str(trip.tc_pod_attachment))
            if os.path.exists(file_path):
                has_pod = True
                pod_source = 'trip'
        
        if has_pod:
            documents.append({
                'trip': trip,
                'trip_number': trip.tr_tripnumber,
                'from_location': trip.tr_enquirynumber.en_fromlocaion.place_name if trip.tr_enquirynumber.en_fromlocaion else '-',
                'to_location': trip.tr_enquirynumber.en_tolocation.place_name if trip.tr_enquirynumber.en_tolocation else '-',
                'vehicle_no': trip.tr_vehiclenumber or '-',
                'status': trip.tc_financestatus.status if trip.tc_financestatus else '-',
                'date': trip.tr_created_at,
                'doc_type': 'POD',
                'pod_source': pod_source,
            })
    
    return render(request, 'asset_mgt_app/customer_documents.html', {
        'customer': customer,
        'department': department,
        'documents': documents,
    })
