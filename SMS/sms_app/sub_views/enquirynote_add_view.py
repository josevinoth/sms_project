from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.http import JsonResponse

from ..forms import ConsignmentdetailaddForm,EnquirynoteaddForm,EnquirynotevehicleForm
from ..models import Vehicle_allotmentInfo,User_extInfo,TripdetailInfo,ConsignmentdetailInfo,EnquirynoteInfo,Enquirynotevehicle,VehiclemasterInfo
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from ..sub_models.customer_mod import CustomerInfo
from ..sub_models.location_info_mod import Location_info


@login_required(login_url='login_page')
def enquirynote_nav(request,enquirynote_id=0,enquirynotevehicle_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if enquirynote_id == 0:
        print("I am inside Get add Enquirynote")
        form = EnquirynoteaddForm()
        enquiryvechicle_form = EnquirynotevehicleForm()
        context = {
            'user_id': user_id,
            'form': form,
            'enquiryvechicle_form': enquiryvechicle_form,
            'first_name': first_name,
        }
    else:
        print("I am inside get edit Enuirynote")
        enquirynote = EnquirynoteInfo.objects.get(pk=enquirynote_id)
        form = EnquirynoteaddForm(instance=enquirynote)
        enquiryvechicle_form = EnquirynotevehicleForm()
        enquirynotevehicle_list = Enquirynotevehicle.objects.filter(env_enquirynumber=enquirynote_id)
        context = {
            'user_id': user_id,
            'form': form,
            'enquiryvechicle_form': enquiryvechicle_form,
            'first_name': first_name,
            'enquirynotevehicle_list': enquirynotevehicle_list,
            'enquirynote_id': enquirynote_id,
        }
    return render(request, "asset_mgt_app/enquirynote_add.html", context)
@login_required(login_url='login_page')
def enquirynote_add(request,enquirynote_id=0,enquirynotevehicle_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if enquirynote_id == 0:
            print("I am inside Get add Enquirynote")
            form = EnquirynoteaddForm()
            enquiryvechicle_form = EnquirynotevehicleForm()
            context = {
                'user_id': user_id,
                'form': form,
                'enquiryvechicle_form': enquiryvechicle_form,
                'first_name': first_name,
            }
        else:
            print("I am inside get edit Enuirynote")
            enquirynote=EnquirynoteInfo.objects.get(pk=enquirynote_id)
            enquiry_num_id = EnquirynoteInfo.objects.get(pk=enquirynote_id).id
            request.session['enquiry_num_id'] = enquiry_num_id
            tr_enqiury_id = EnquirynoteInfo.objects.get(pk=enquirynote_id).en_enquirynumber
            request.session['ses_enqiury_id'] = tr_enqiury_id
            form = EnquirynoteaddForm(instance=enquirynote)
            # enquirynotevehicle = Enquirynotevehicle.objects.get(pk=enquirynotevehicle_id)
            enquiryvechicle_form = EnquirynotevehicleForm()
            enquirynotevehicle_list=Enquirynotevehicle.objects.filter(env_enquirynumber=enquirynote_id)
            context={
                'user_id': user_id,
                'form': form,
                'enquiryvechicle_form': enquiryvechicle_form,
                'first_name': first_name,
                'enquirynotevehicle_list': enquirynotevehicle_list,
                'enquiry_num_id': enquiry_num_id,
            }
        return render(request, "asset_mgt_app/enquirynote_add.html",context)
    else:
        if enquirynote_id == 0:
            print("I am inside post add Enuirynote")
            form = EnquirynoteaddForm(request.POST)
            if form.is_valid():
                # Save form but do not commit immediately
                instance = form.save(commit=False)
                instance.save()  # ID is generated after this

                # Determine branch prefix
                user_branch = User_extInfo.objects.get(user_id=user_id).emp_branch
                branch_id = Location_info.objects.get(loc_name=user_branch).id

                if branch_id == 1:
                    branch_prefix = "BLR_"
                elif branch_id == 2:
                    branch_prefix = "MAA_"
                elif branch_id == 3:
                    branch_prefix = "PNY_"
                else:
                    branch_prefix = "HYD_"

                # Generate enquiry number with branch prefix
                enquiry_num_next = f"{branch_prefix}EN_{1000000 + instance.id}"

                # Update the enquiry number and save
                instance.en_enquirynumber = enquiry_num_next
                instance.save(update_fields=['en_enquirynumber'])

                print("Enquiry Main Form Saved")
                messages.success(request, 'Record Updated Successfully')

                return redirect(f'/SMS/enquirynote_update/{instance.id}')
            else:
                print("Enquiry Main Form not Saved")
                print(form.errors)
                messages.error(request, f'Record Not Saved: {form.errors}')
                
                # Re-render with errors
                enquiryvechicle_form = EnquirynotevehicleForm()
                context = {
                    'user_id': user_id,
                    'form': form,
                    'enquiryvechicle_form': enquiryvechicle_form,
                    'first_name': first_name,
                }
                return render(request, "asset_mgt_app/enquirynote_add.html", context)
        else:
            print("I am inside post edit Enquirynote")
            enquirynote = EnquirynoteInfo.objects.get(pk=enquirynote_id)
            form = EnquirynoteaddForm(request.POST,instance=enquirynote)
            if form.is_valid():
                form.save()
                print("Enquiry Main Form Saved")
                messages.success(request, 'Record Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
            else:
                print("Enquiry Main Form not Saved")
                print(form.errors)
                messages.error(request, f'Record Not Saved: {form.errors}')
                
                # Re-render with errors
                enquiryvechicle_form = EnquirynotevehicleForm()
                enquirynotevehicle_list=Enquirynotevehicle.objects.filter(env_enquirynumber=enquirynote_id)
                enquiry_num_id = EnquirynoteInfo.objects.get(pk=enquirynote_id).id
                
                context={
                    'user_id': user_id,
                    'form': form,
                    'enquiryvechicle_form': enquiryvechicle_form,
                    'first_name': first_name,
                    'enquirynotevehicle_list': enquirynotevehicle_list,
                    'enquiry_num_id': enquiry_num_id,
                    'enquirynote_id': enquirynote_id,
                }
                return render(request, "asset_mgt_app/enquirynote_add.html", context)
            # return redirect('/SMS/enquirynote_list')

from django.db.models import Q

@login_required(login_url='login_page')
def enquirynote_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    user_role = User_extInfo.objects.get(user_id=user_id).emp_role

    enquiry_number = request.GET.get('enquiry_number', '')
    consignment_number = request.GET.get('consignment_number', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    select_all = request.GET.get('select_all', '')

    # Use select_related for foreign keys to reduce queries
    enquirynote_queryset = EnquirynoteInfo.objects.select_related(
        'en_customername', 'en_fromlocaion', 'en_tolocation', 'en_assignedto', 'en_status'
    )

    # Filter by enquiry no.
    if enquiry_number:
        enquirynote_queryset = enquirynote_queryset.filter(
            en_enquirynumber__icontains=enquiry_number
        )

    # Filter by consignment
    if consignment_number:
        enquirynote_queryset = enquirynote_queryset.filter(
            consignmentdetailinfo__co_consignmentnumber__icontains=consignment_number
        ).distinct()

    # Date filters
    if date_from:
        enquirynote_queryset = enquirynote_queryset.filter(
            en_created_at__date__gte=date_from
        )
    if date_to:
        enquirynote_queryset = enquirynote_queryset.filter(
            en_created_at__date__lte=date_to
        )

    user_ext = User_extInfo.objects.get(user_id=user_id)
    user_role_obj = user_ext.emp_role  # This is RoleInfo object

    # Extract actual role name safely
    role_name = str(user_role_obj).lower()
    if role_name not in ["admin", "super user", "superuser"]:
        enquirynote_queryset = enquirynote_queryset.filter(
            en_assignedto=user_id
        )

    enquirynote_queryset = enquirynote_queryset.order_by('-id')

    select_all = request.GET.get('select_all', '')

    if select_all == "true":
        # Load records with a sensible limit (500 max for performance)
        page_obj = list(enquirynote_queryset[:500])
    else:
        # Normal pagination
        paginator = Paginator(enquirynote_queryset, 75)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number if page_number and page_number.isdigit() else 1)

    # Efficiently get enquiry IDs
    enquiry_ids = [enq.id for enq in page_obj]

    # Fetch related data
    consignment_data = ConsignmentdetailInfo.objects.filter(co_enquirynumber_id__in=enquiry_ids)
    vehicle_data = Vehicle_allotmentInfo.objects.filter(
        va_enquirynumber__in=enquiry_ids
    ).values_list('va_enquirynumber', 'va_vehiclenumber__vm_registrationnumber', 'va_vehiclenumber_mkt')


    trip_data = TripdetailInfo.objects.filter(
        tr_enquirynumber_id__in=enquiry_ids
    ).values_list(
        'tr_enquirynumber',
        'tr_consignmentnumber__co_consignmentnumber',
        'tr_tripnumber',
        'tc_financestatus__status',
        'tc_financestatus',
        'tr_category__category'
    )

    # Pre-build consignment dict to avoid N+1 queries
    consignment_dict = {}
    for consignment in consignment_data:
        consignment_dict.setdefault(consignment.co_enquirynumber_id, []).append(consignment)
    
    # Pre-build consignment count dict for limit checking
    consignment_count_dict = {enq_id: len(cons_list) for enq_id, cons_list in consignment_dict.items()}

    # Vehicle dict
    vehicle_dict = {}
    for enq_id, reg_num, mkt_num in vehicle_data:
        valid_numbers = [num for num in (reg_num, mkt_num) if num]
        vehicle_dict.setdefault(enq_id, []).extend(valid_numbers or ["No Vehicle"])

    # Trip dict
    trip_dict = {}
    for enq_id, trip_cons, trip_num, trip_status, trip_status_id, trip_category in trip_data:
        # Check category safely
        cat_lower = trip_category.strip().lower() if trip_category else ""
        
        # If category is "Business", show consignment number; otherwise show category name
        # Added "bussiness" to handle potential typos in the database
        if cat_lower in ["business", "bussiness"]:
            display_text = trip_cons if trip_cons else "No Consignment"
        else:
            display_text = trip_category if trip_category else "No Category"
        
        trip_dict.setdefault(enq_id, []).append(
            (display_text, trip_num or "No Trip", trip_status or "", trip_status_id)
        )

    # Vehicle limits
    vehicle_limits = (
        Enquirynotevehicle.objects.filter(env_enquirynumber__in=enquiry_ids)
        .values('env_enquirynumber')
        .annotate(total_allowed=Sum('env_quantity'))
    )
    vehicle_limit_dict = {v['env_enquirynumber']: v['total_allowed'] for v in vehicle_limits}

    vehicle_allotted = (
        Vehicle_allotmentInfo.objects.filter(va_enquirynumber__in=enquiry_ids)
        .values('va_enquirynumber')
        .annotate(total_allotted=Count('id'))
    )
    vehicle_allotted_dict = {v['va_enquirynumber']: v['total_allotted'] for v in vehicle_allotted}

    # Build final data
    enquiry_data = []
    for enquiry in page_obj:
        vehicles = vehicle_dict.get(enquiry.id, [])
        consignments = consignment_dict.get(enquiry.id, [])

        total_allowed = vehicle_limit_dict.get(enquiry.id, 0)
        total_allotted = vehicle_allotted_dict.get(enquiry.id, 0)
        limit_reached = total_allotted >= total_allowed if total_allowed > 0 else False

        # Consignment limit logic - use pre-computed count
        consignment_count = consignment_count_dict.get(enquiry.id, 0)
        if vehicles and total_allowed > 0:
            consignment_limit_reached = consignment_count >= total_allowed
        else:
            consignment_limit_reached = True

        enquiry_data.append({
            'enquiry': enquiry,
            'consignments': consignments,
            'trips': trip_dict.get(enquiry.id, []),
            'vehicles': vehicles,
            'vehicle_limit': total_allowed,
            'vehicle_allotted': total_allotted,
            'limit_reached': limit_reached,
            'consignment_limit_reached': consignment_limit_reached,
        })

    # Vehicle count summary (Own and Attached)
    vehicles = VehiclemasterInfo.objects.filter(vm_ownership__ow_ownership__icontains='own') | \
               VehiclemasterInfo.objects.filter(vm_ownership__ow_ownership__icontains='attached')
    
    vehicles = vehicles.select_related('vm_vehicletype', 'vm_ownership')
    
    # Get the latest trip status for each vehicle using Max aggregation
    from django.db.models import Max
    
    latest_trip_ids = (
        TripdetailInfo.objects
        .values('tr_vehiclenumber')
        .annotate(latest_id=Max('id'))
        .values_list('latest_id', flat=True)
    )
    
    latest_trips = {
        t['tr_vehiclenumber']: t['tc_financestatus_id']
        for t in TripdetailInfo.objects.filter(id__in=latest_trip_ids)
        .values('tr_vehiclenumber', 'tc_financestatus_id')
    }

    # Structure: {'Own': {'total': X, 'branches': {'MAA': {'total': Y, 'types': {...}}, ...}}, ...}
    vehicle_summary = {
        'Own': {'total': 0, 'branches': {}},
        'Attached': {'total': 0, 'branches': {}}
    }
    IN_TRIP_STATUS_IDS = [1, 8]

    for v in vehicles:
        reg = v.vm_registrationnumber.strip().upper() if v.vm_registrationnumber else ""
        if not reg: continue
        
        # Determine ownership key
        ownership_name = v.vm_ownership.ow_ownership.lower() if v.vm_ownership else ""
        if 'own' in ownership_name:
            owner_key = 'Own'
        elif 'attached' in ownership_name:
            owner_key = 'Attached'
        else:
            continue

        # Determine branch key
        if reg.startswith('TN'): branch_key = 'MAA'
        elif reg.startswith('KA'): branch_key = 'BLR'
        else: branch_key = 'OTH'
            
        v_vt = v.vm_vehicletype.vt_vehicletype if v.vm_vehicletype else "Unknown"
        status_id = latest_trips.get(reg)
        is_in_trip = status_id in IN_TRIP_STATUS_IDS
        
        # Increment total for ownership group
        vehicle_summary[owner_key]['total'] += 1
        
        # Initialize branch in group if not exists
        if branch_key not in vehicle_summary[owner_key]['branches']:
            vehicle_summary[owner_key]['branches'][branch_key] = {'total': 0, 'types': {}}
        
        branch_ref = vehicle_summary[owner_key]['branches'][branch_key]
        branch_ref['total'] += 1

        # Initialize vehicle type in branch if not exists
        if v_vt not in branch_ref['types']:
            branch_ref['types'][v_vt] = {'total': 0, 'avail': 0, 'trip': 0}
        
        # Increment counts per vehicle type
        branch_ref['types'][v_vt]['total'] += 1
        if is_in_trip:
            branch_ref['types'][v_vt]['trip'] += 1
        else:
            branch_ref['types'][v_vt]['avail'] += 1

    context = {
        'page_obj': page_obj,
        'first_name': first_name,
        'role': user_role,
        'enquiry_data': enquiry_data,
        'enquiry_number': enquiry_number,
        'vehicle_summary': vehicle_summary,
    }
    return render(request, "asset_mgt_app/enquirynote_list.html", context)

# Connect to consignemnt Note
@login_required(login_url='login_page')
def consignment_note_connect(request,enquirynote_id):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    enquiry_num=EnquirynoteInfo.objects.get(pk=enquirynote_id).en_enquirynumber
    request.session['ses_enquiry_note']=enquiry_num
    try:
        consignment_num=ConsignmentdetailInfo.objects.get(co_enquirynumber=enquiry_num).co_consignmentnumber
    except ObjectDoesNotExist:
        consignment_num=None

    if request.method == "GET":
        if consignment_num==None:
            print("I am inside Get add consignmentdetails")
            con_det_form = ConsignmentdetailaddForm()
        else:
            print("I am inside get edit consignmentdetails")
            try:
                consignmentdetail = ConsignmentdetailInfo.objects.get(co_consignmentnumber=consignment_num)
            except ObjectDoesNotExist:
                consignmentdetail = None
            con_det_form = ConsignmentdetailaddForm(instance=consignmentdetail)
        context = {
            'first_name': first_name,
            'con_det_form': con_det_form,
            'enquiry_num': enquiry_num,
            'user_id': user_id,
            'consignmentdetail_list': ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num),
        }
        return render(request, "asset_mgt_app/consignmentdetail_add.html", context)
    else:
        if consignment_num==None:
            print("I am inside post add consignmentdetails")
            con_det_form = ConsignmentdetailaddForm(request.POST)
        else:
            print("I am inside post edit consignmentdetails")
            try:
                consignmentdetail = ConsignmentdetailInfo.objects.get(co_consignmentnumber=consignment_num)
            except ObjectDoesNotExist:
                consignmentdetail = None
            con_det_form = ConsignmentdetailaddForm(request.POST, instance=consignmentdetail)
        if con_det_form.is_valid():
            con_det_form.save()
            print("con_det_form Main Form is Valid")
        else:
            print("con_det_form Form is not Valid")

        return redirect('/SMS/enquirynote_list')
#Delete enquirynote
@login_required(login_url='login_page')
def enquirynote_delete(request,enquirynote_id):
    enquiry_num = EnquirynoteInfo.objects.get(pk=enquirynote_id).en_enquirynumber
    enquiry_num_id = EnquirynoteInfo.objects.get(pk=enquirynote_id).id
    consignment_num_list = list(ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id).values_list('co_consignmentnumber',flat=True))
    tripdetails_list=list(TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num_id).values_list('tr_tripnumber',flat=True))
    for i in consignment_num_list:
        consignment_note=ConsignmentdetailInfo.objects.get(co_consignmentnumber=i)
        consignment_note.delete()
    for j in tripdetails_list:
        tripdetails_note=TripdetailInfo.objects.get(tr_tripnumber=j)
        tripdetails_note.delete()
    enquirynote = EnquirynoteInfo.objects.get(pk=enquirynote_id)
    enquirynote.delete()
    return redirect('/SMS/enquirynote_list')

@login_required(login_url='login_page')
def get_customer_details(request):
    customer_id = request.GET.get('customer_id')
    try:
        customer = CustomerInfo.objects.get(id=customer_id)
        data = {
            'customer_contact': customer.cu_contactno,
            'customer_email': customer.cu_email,
            'customer_businessmodel_id': customer.cu_businessmodel.id if customer.cu_businessmodel else None,
            'customer_businessmodel_name': str(customer.cu_businessmodel) if customer.cu_businessmodel else "",
        }
        return JsonResponse(data)
    except CustomerInfo.DoesNotExist:
        return JsonResponse({'error': 'Customer not found'}, status=404)
@login_required(login_url='login_page')
def fetch_enquiry_locations(request):
    enquiry_number = request.GET.get('enquiry_number', '').strip()
    if not enquiry_number:
        return JsonResponse({'error': 'Missing enquiry number'}, status=400)

    try:
        enquiry = EnquirynoteInfo.objects.select_related('en_fromlocaion', 'en_tolocation').get(id=enquiry_number)
        data = {
            'from_location_id': enquiry.en_fromlocaion.id if enquiry.en_fromlocaion else None,
            'to_location_id': enquiry.en_tolocation.id if enquiry.en_tolocation else None,
        }
        return JsonResponse(data)
    except EnquirynoteInfo.DoesNotExist:
        return JsonResponse({'error': 'Enquiry not found'}, status=404)
