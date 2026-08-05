from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.http import JsonResponse

from ..forms import ConsignmentdetailaddForm, EnquirynoteaddForm, EnquirynotevehicleForm
from ..models import Vehicle_allotmentInfo, User_extInfo, TripdetailInfo, ConsignmentdetailInfo, EnquirynoteInfo, \
    Enquirynotevehicle, VehiclemasterInfo, Tripstatusinfo, DeletionLog
from ..sub_models.trans_invoice_mod import TransInvoiceInfo
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from ..sub_models.customer_mod import CustomerInfo
from ..sub_models.location_info_mod import Location_info
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id, is_tms_manager


@login_required(login_url='login_page')
def enquirynote_nav(request, enquirynote_id=0, enquirynotevehicle_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if enquirynote_id == 0:
        print("I am inside Get add Enquirynote")
        form = EnquirynoteaddForm(initial={'en_assignedto': user_id})
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
def enquirynote_add(request, enquirynote_id=0, enquirynotevehicle_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if enquirynote_id == 0:
            print("I am inside Get add Enquirynote")
            form = EnquirynoteaddForm(initial={'en_assignedto': user_id})

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
            enquiry_num_id = enquirynote.id
            request.session['enquiry_num_id'] = enquiry_num_id
            tr_enqiury_id = enquirynote.en_enquirynumber
            request.session['ses_enqiury_id'] = tr_enqiury_id  # Keep for backward compat if needed
            form = EnquirynoteaddForm(instance=enquirynote)

            # enquirynotevehicle = Enquirynotevehicle.objects.get(pk=enquirynotevehicle_id)
            enquiryvechicle_form = EnquirynotevehicleForm()
            enquirynotevehicle_list = Enquirynotevehicle.objects.filter(env_enquirynumber=enquirynote_id)
            context = {
                'user_id': user_id,
                'form': form,
                'enquiryvechicle_form': enquiryvechicle_form,
                'first_name': first_name,
                'enquirynotevehicle_list': enquirynotevehicle_list,
                'enquiry_num_id': enquiry_num_id,
            }
        return render(request, "asset_mgt_app/enquirynote_add.html", context)
    else:
        if enquirynote_id == 0:
            print("I am inside post add Enuirynote")
            form = EnquirynoteaddForm(request.POST)
            if form.is_valid():
                # Save form but do not commit immediately
                instance = form.save(commit=False)
                instance.save()  # ID is generated after this

                # Determine branch prefix using centralized utility
                branch_id = get_session_branch_id(request)
                branch_code = get_branch_code(branch_id)
                branch_prefix = f"{branch_code}_"

                # Generate enquiry number with financial year and branch prefix
                # Example format: 26-27_MAA_EN_000001
                current_fy = get_financial_year()
                prefix = f"{current_fy}_{branch_prefix}EN_"
                enquiry_num_next = generate_next_number(EnquirynoteInfo, 'en_enquirynumber', prefix, 6)

                # Update the enquiry number and save
                instance.en_enquirynumber = enquiry_num_next
                instance.save(update_fields=['en_enquirynumber'])

                print("Enquiry Main Form Saved")
                messages.success(request, 'Record Updated Successfully')

                return redirect(f'/SMS/enquirynote_update/{instance.id}')
            else:
                print("Enquiry Main Form not Saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
                return redirect(request.META.get('HTTP_REFERER', '/SMS/enquirynote_list/'))
        else:
            print("I am inside post edit Enquirynote")
            enquirynote = EnquirynoteInfo.objects.get(pk=enquirynote_id)
            form = EnquirynoteaddForm(request.POST, instance=enquirynote)
            if form.is_valid():
                form.save()
                print("Enquiry Main Form Saved")
                messages.success(request, 'Record Updated Successfully')
                return redirect(request.META.get('HTTP_REFERER', f'/SMS/enquirynote_update/{enquirynote_id}'))
            else:
                print("Enquiry Main Form not Saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
                return redirect(request.META.get('HTTP_REFERER', f'/SMS/enquirynote_update/{enquirynote_id}'))
            # return redirect('/SMS/enquirynote_list')


from django.db.models import Q


@login_required(login_url='login_page')
def enquirynote_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    user_role = User_extInfo.objects.get(user_id=user_id).emp_role

    enquiry_number = request.GET.get('enquiry_number', '')
    consignment_number = request.GET.get('consignment_number', '')
    vehicle_number = request.GET.get('vehicle_number', '')
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

    # Filter by vehicle number
    if vehicle_number:
        enquirynote_queryset = enquirynote_queryset.filter(
            Q(vehicle_allotmentinfo__va_vehiclenumber__vm_registrationnumber__icontains=vehicle_number) |
            Q(vehicle_allotmentinfo__va_vehiclenumber_mkt__icontains=vehicle_number) |
            Q(tripdetailinfo__tr_vehiclenumber__icontains=vehicle_number)
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
    # Admin, Super User, and TMS Managers (BVM Trans + Manager + User role) see ALL enquiries
    if role_name not in ["admin", "super user", "superuser"] and not is_tms_manager(user_id):
        enquirynote_queryset = enquirynote_queryset.filter(
            en_assignedto=user_id
        )

    enquirynote_queryset = enquirynote_queryset.order_by('-id')

    select_all = request.GET.get('select_all', '')

    if select_all == "true":
        # Load records with a sensible limit (1000 max for performance) when "Show All" is clicked
        page_obj = list(enquirynote_queryset[:1000])
    elif date_from or date_to or enquiry_number or consignment_number or vehicle_number:
        # Load records with a larger limit (5000 max) when specific filters/search terms are applied
        page_obj = list(enquirynote_queryset[:5000])
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
    ).values_list('va_enquirynumber', 'va_vehiclenumber__vm_registrationnumber', 'va_vehiclenumber_mkt', 'va_status_id',
                  'id', 'va_replaced_allotment_id')

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
        'tr_vehiclenumber',
        'tc_cancellation_check'
    )

    # Find which trips already have a completed invoice
    all_page_trip_ids = [row[0] for row in trip_data]
    invoiced_trip_ids = set(
        TransInvoiceInfo.objects.filter(
            ti_trip_id__in=all_page_trip_ids,
            is_woh=True
        ).values_list('ti_trip_id', flat=True)
    )

    # Pre-build consignment dict to avoid N+1 queries
    consignment_dict = {}
    for consignment in consignment_data:
        consignment_dict.setdefault(consignment.co_enquirynumber_id, []).append(consignment)

    # Pre-build consignment count dict for limit checking
    consignment_count_dict = {enq_id: len(cons_list) for enq_id, cons_list in consignment_dict.items()}

    # Identify allotment replacement statuses
    vehicle_replaced_ids = set()
    driver_replaced_ids = set()
    va_status_map = {row[4]: row[3] for row in vehicle_data}  # va_id -> status_id

    for enq_id, reg_num, mkt_num, status_id, va_id, replaced_va_id in vehicle_data:
        if status_id == 2 or (replaced_va_id and va_status_map.get(replaced_va_id) == 2):
            vehicle_replaced_ids.add(replaced_va_id if replaced_va_id else va_id)
        if status_id == 3 or (replaced_va_id and va_status_map.get(replaced_va_id) == 3):
            driver_replaced_ids.add(replaced_va_id if replaced_va_id else va_id)

    # Vehicle dict
    vehicle_dict = {}
    for enq_id, reg_num, mkt_num, status_id, va_id, replaced_va_id in vehicle_data:
        v_num = reg_num if reg_num else mkt_num
        if v_num:
            if va_id in vehicle_replaced_ids or status_id == 2:
                display_num = f"{v_num} (replaced)"
            elif va_id in driver_replaced_ids or status_id == 3:
                display_num = f"{v_num} (driver replaced)"
            else:
                display_num = v_num

            if enq_id not in vehicle_dict:
                vehicle_dict[enq_id] = []

            # Deduplicate by raw vehicle number so driver replacements for the same vehicle do not create duplicate badges
            existing_entry = next((v for v in vehicle_dict[enq_id] if v['raw_num'] == v_num), None)
            if not existing_entry:
                vehicle_dict[enq_id].append({
                    'id': va_id,
                    'number': display_num,
                    'raw_num': v_num
                })
            else:
                # Priority: (replaced) > (driver replaced) > plain
                if "(replaced)" in display_num or ("(driver replaced)" in display_num and "(replaced)" not in existing_entry['number']):
                    existing_entry['number'] = display_num
                    existing_entry['id'] = va_id
        else:
            if enq_id not in vehicle_dict:
                vehicle_dict[enq_id] = []
            vehicle_dict[enq_id].append({
                'id': va_id,
                'number': "None",
                'raw_num': ""
            })

    # Trip dict
    trip_dict = {}
    for trip_id, enq_id, trip_cons, trip_num, trip_status, trip_status_id, trip_category, trip_veh_num, tc_cancellation_check in trip_data:
        # Check category safely
        cat_lower = trip_category.strip().lower() if trip_category else ""

        # If category is "Business", show consignment number; otherwise show category name
        # Added "bussiness" to handle potential typos in the database
        if tc_cancellation_check or trip_status_id in [10, 11]:
            display_text = "Cancelled Trip"
        elif cat_lower in ["business", "bussiness"]:
            display_text = trip_cons if trip_cons else "No Consignment"
        else:
            display_text = trip_category if trip_category else "No Category"

        display_veh_num = trip_veh_num if trip_veh_num else (trip_num or "No Trip")
        is_invoiced = trip_id in invoiced_trip_ids

        trip_dict.setdefault(enq_id, []).append(
            (display_text, trip_num or "No Trip", trip_status or "", trip_status_id, display_veh_num, is_invoiced)
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

    docked_out_enquiry_ids = set(
        TripdetailInfo.objects.filter(
            tr_enquirynumber_id__in=enquiry_ids,
            tr_dock_out_time__isnull=False
        ).values_list('tr_enquirynumber_id', flat=True)
    )

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
            'has_docked_out_trip': (enquiry.id in docked_out_enquiry_ids),
        })

    # -----------------------------
    # LIVE FLEET SUMMARY CALCULATION
    # -----------------------------
    in_trip_status_ids = list(Tripstatusinfo.objects.filter(
        status__in=['Trip Started', 'Open', 'Started', 'Loading Reported', 'Unloading Reported']
    ).values_list('id', flat=True))

    def normalize_reg(num):
        return num.strip().upper().replace(" ", "").replace("-", "") if num else ""

    active_trips_reg_nums = set(
        normalize_reg(num) for num in TripdetailInfo.objects.filter(
            tc_financestatus_id__in=in_trip_status_ids
        ).values_list('tr_vehiclenumber', flat=True)
    )

    all_v = VehiclemasterInfo.objects.select_related(
        'vm_ownership', 'vm_vehicletype', 'vm_vendor__vend_branch'
    )

    vehicle_summary = {
        'Own': {'total': 0, 'branches': {}},
        'Attached': {'total': 0, 'branches': {}}
    }

    for v in all_v:
        # Categorize: Own vs Attached
        ownership_str = str(v.vm_ownership).lower()
        cat = 'Own' if 'own' in ownership_str else 'Attached'

        # Branch determination logic to match user request:
        # Own -> MAA, BLR
        # Attached -> MAA
        raw_branch = "GENERAL"
        if v.vm_vendor and v.vm_vendor.vend_branch:
            raw_branch = v.vm_vendor.vend_branch.loc_name

        branch = None
        reg = (v.vm_registrationnumber or "").upper().strip()

        if cat == 'Own':
            if 'MAA' in raw_branch:
                branch = 'MAA'
            elif 'BLR' in raw_branch:
                branch = 'BLR'
            elif raw_branch == 'HO':
                branch = 'MAA'
            else:
                # Fallback to registration number prefix for Own vehicles
                if reg.startswith('TN'):
                    branch = 'MAA'
                elif reg.startswith('KA'):
                    branch = 'BLR'
        else:  # Attached
            if 'MAA' in raw_branch:
                branch = 'MAA'
            elif reg.startswith('TN'):  # Fallback for attached too
                branch = 'MAA'

        # If the branch doesn't match the required filters for the category, skip it.
        if not branch:
            continue

        v_type = str(v.vm_vehicletype) or "Unknown"
        reg_norm = normalize_reg(v.vm_registrationnumber)

        # Structure init
        if branch not in vehicle_summary[cat]['branches']:
            # Create a safe slug for HTML IDs
            branch_slug = branch.replace(" ", "_").replace("-", "_").replace(".", "_").replace("/", "_")
            vehicle_summary[cat]['branches'][branch] = {
                'total': 0,
                'types': {},
                'slug': branch_slug
            }

        if v_type not in vehicle_summary[cat]['branches'][branch]['types']:
            vehicle_summary[cat]['branches'][branch]['types'][v_type] = {'total': 0, 'avail': 0, 'trip': 0}

        # Counters
        vehicle_summary[cat]['total'] += 1
        vehicle_summary[cat]['branches'][branch]['total'] += 1
        vehicle_summary[cat]['branches'][branch]['types'][v_type]['total'] += 1

        if reg_norm and reg_norm in active_trips_reg_nums:
            vehicle_summary[cat]['branches'][branch]['types'][v_type]['trip'] += 1
        else:
            vehicle_summary[cat]['branches'][branch]['types'][v_type]['avail'] += 1

    # Sort branches for consistent display
    for cat in ['Own', 'Attached']:
        vehicle_summary[cat]['branches'] = dict(sorted(vehicle_summary[cat]['branches'].items()))

    context = {
        'page_obj': page_obj,
        'first_name': first_name,
        'role': user_role,
        'enquiry_data': enquiry_data,
        'enquiry_number': enquiry_number,
        'consignment_number': consignment_number,
        'vehicle_number': vehicle_number,
        'date_from': date_from,
        'date_to': date_to,
        'vehicle_summary': vehicle_summary,
    }
    return render(request, "asset_mgt_app/enquirynote_list.html", context)


@login_required(login_url='login_page')
def search_vehicle_numbers(request):
    term = request.GET.get('term', '').strip()
    if len(term) < 2:
        return JsonResponse({'results': []})

    # Search in VehiclemasterInfo (registered vehicles)
    vm_regs = list(VehiclemasterInfo.objects.filter(
        vm_registrationnumber__icontains=term
    ).values_list('vm_registrationnumber', flat=True).distinct()[:200])

    # Search in Vehicle_allotmentInfo (own & market vehicles)
    own_regs = list(Vehicle_allotmentInfo.objects.filter(
        va_vehiclenumber__vm_registrationnumber__icontains=term
    ).values_list('va_vehiclenumber__vm_registrationnumber', flat=True).distinct()[:200])

    mkt_regs = list(Vehicle_allotmentInfo.objects.filter(
        va_vehiclenumber_mkt__icontains=term
    ).values_list('va_vehiclenumber_mkt', flat=True).distinct()[:200])

    # Search in TripdetailInfo
    trip_regs = list(TripdetailInfo.objects.filter(
        tr_vehiclenumber__icontains=term
    ).values_list('tr_vehiclenumber', flat=True).distinct()[:200])

    combined = []
    seen = set()

    for r in (vm_regs + own_regs + mkt_regs + trip_regs):
        if r and r.strip():
            clean_r = r.strip()
            if clean_r.upper() not in seen:
                seen.add(clean_r.upper())
                combined.append(clean_r)
                if len(combined) >= 200:
                    break

    return JsonResponse({'results': combined})


# Connect to consignemnt Note
@login_required(login_url='login_page')
def consignment_note_connect(request, enquirynote_id):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    enquiry_num = EnquirynoteInfo.objects.get(pk=enquirynote_id).en_enquirynumber
    request.session['ses_enquiry_note'] = enquiry_num
    try:
        consignment_num = ConsignmentdetailInfo.objects.get(co_enquirynumber=enquiry_num).co_consignmentnumber
    except ObjectDoesNotExist:
        consignment_num = None

    if request.method == "GET":
        if consignment_num == None:
            print("I am inside Get add consignmentdetails")
            try:
                enquiry = EnquirynoteInfo.objects.get(pk=enquirynote_id)
                customer = enquiry.en_customername
                customer_obj = CustomerInfo.objects.filter(cu_name=customer).first()
                cust_id = customer_obj.id if customer_obj else None
            except Exception:
                cust_id = None
            con_det_form = ConsignmentdetailaddForm(initial={'co_enquirynumber': enquirynote_id, 'co_customer': cust_id})
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
        if consignment_num == None:
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


# Delete enquirynote
@login_required(login_url='login_page')
def enquirynote_delete(request, enquirynote_id):
    enquirynote = EnquirynoteInfo.objects.get(pk=enquirynote_id)
    enquiry_num = enquirynote.en_enquirynumber
    reason = request.POST.get('deletion_reason', 'No reason provided')

    # Create deletion log
    DeletionLog.objects.create(
        dl_model_name='EnquirynoteInfo',
        dl_record_id=enquirynote_id,
        dl_record_identifier=enquiry_num,
        dl_deleted_by=request.user,
        dl_reason=reason
    )

    # Perform cascading deletes manually as required by the existing logic
    consignment_num_list = list(
        ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquirynote_id).values_list('co_consignmentnumber',
                                                                                          flat=True))
    tripdetails_list = list(
        TripdetailInfo.objects.filter(tr_enquirynumber=enquirynote_id).values_list('tr_tripnumber', flat=True))

    for i in consignment_num_list:
        consignment_note = ConsignmentdetailInfo.objects.get(co_consignmentnumber=i)
        DeletionLog.objects.create(
            dl_model_name='ConsignmentdetailInfo',
            dl_record_id=consignment_note.id,
            dl_record_identifier=i,
            dl_deleted_by=request.user,
            dl_reason=f"Cascaded delete from Enquiry {enquiry_num}. Reason: {reason}"
        )
        consignment_note.delete()

    # Cascade delete Enquirynotevehicle
    env_list = Enquirynotevehicle.objects.filter(env_enquirynumber=enquirynote_id)
    for env in env_list:
        DeletionLog.objects.create(
            dl_model_name='Enquirynotevehicle',
            dl_record_id=env.id,
            dl_record_identifier=str(env.id),
            dl_deleted_by=request.user,
            dl_reason=f"Cascaded delete from Enquiry {enquiry_num}. Reason: {reason}"
        )
        env.delete()

    # Cascade delete Vehicle_allotmentInfo
    va_list = Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquirynote_id)
    for va in va_list:
        DeletionLog.objects.create(
            dl_model_name='Vehicle_allotmentInfo',
            dl_record_id=va.id,
            dl_record_identifier=str(va.id),
            dl_deleted_by=request.user,
            dl_reason=f"Cascaded delete from Enquiry {enquiry_num}. Reason: {reason}"
        )
        va.delete()

    for j in tripdetails_list:
        tripdetails_note = TripdetailInfo.objects.get(tr_tripnumber=j)
        DeletionLog.objects.create(
            dl_model_name='TripdetailInfo',
            dl_record_id=tripdetails_note.id,
            dl_record_identifier=j,
            dl_deleted_by=request.user,
            dl_reason=f"Cascaded delete from Enquiry {enquiry_num}. Reason: {reason}"
        )
        tripdetails_note.delete()

    enquirynote.delete()
    messages.success(request, f"Enquiry {enquiry_num} deleted and logged successfully.")
    return redirect('/SMS/enquirynote_list')


@login_required(login_url='login_page')
def get_customer_details(request):
    customer_id = request.GET.get('customer_id')
    department_id = request.GET.get('department_id')
    try:
        customer = CustomerInfo.objects.get(id=customer_id)
        
        from ..sub_models.emailmaster_mod import Emailmaster
        qs = Emailmaster.objects.filter(em_Customer_name_id=customer_id)
        if department_id:
            dept_qs = qs.filter(Q(em_customerdepartment_id=department_id) | Q(em_customerdepartment__isnull=True))
            if dept_qs.exists():
                qs = dept_qs

        users = list(qs.exclude(em_user__isnull=True).exclude(em_user='')
                     .values_list('em_user', flat=True).distinct())

        data = {
            'customer_contact': customer.cu_contactno,
            'customer_email': customer.cu_email,
            'customer_businessmodel_id': customer.cu_businessmodel.id if customer.cu_businessmodel else None,
            'customer_businessmodel_name': str(customer.cu_businessmodel) if customer.cu_businessmodel else "",
            'users': users,
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
