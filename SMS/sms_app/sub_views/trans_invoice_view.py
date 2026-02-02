from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from openpyxl import Workbook
from django.http import HttpResponse

from ..sub_forms.trans_invoice_Form import TransInvoiceForm
from ..sub_models.trans_invoice_mod import TransInvoiceInfo
from ..sub_models.customer_mod import CustomerInfo
from ..sub_models.tripdetail_mod import TripdetailInfo
from ..sub_models.consignmentdetail_mod import ConsignmentdetailInfo
from ..sub_models.consignmentgoods_mod import ConsignmentgoodsInfo



# ==================================================
# ADD / EDIT TRANS INVOICE
# ==================================================
@login_required(login_url='login_page')
def trans_invoice_add(request):
    first_name = request.session.get('first_name')
    invoice = None
    saved = False

    if request.method == "POST":
        form = TransInvoiceForm(request.POST)

        if form.is_valid():
            invoice = form.save(commit=False)

            # calculate total
            invoice.ti_total = (
                (invoice.ti_transportation_charges or 0) +
                (invoice.ti_toll_charges or 0) +
                (invoice.ti_parking_charges or 0) +
                (invoice.ti_loading_charges or 0) +
                (invoice.ti_unloading_charges or 0) +
                (invoice.ti_halting_charges or 0) +
                (invoice.ti_docket_charges or 0) +
                (invoice.ti_weighment_charges or 0) +
                (invoice.ti_handling_charges or 0) +
                (invoice.ti_cancellation_charges or 0)
            )

            # ==================================================
            # ATTACH CONSIGNMENT / TRIP / GOODS
            # ==================================================

            cons = (
                ConsignmentdetailInfo.objects
                .filter(co_customer=invoice.ti_customer)
                .exclude(co_consignmentnumber__isnull=True)
                .exclude(co_consignmentnumber__exact='')
                .order_by('-id')
                .first()
            )

            if cons:
                invoice.ti_consignment = cons
            else:
                messages.info(
                    request,
                    "No consignment found for selected customer — invoice will be saved without consignment"
                )

            trip = None
            if cons:
                trip = (
                    TripdetailInfo.objects
                    .filter(tr_consignmentnumber=cons)
                    .order_by('-id')
                    .first()
                )
                if trip:
                    invoice.ti_trip = trip

            goods = None
            if cons:
                goods = (
                    ConsignmentgoodsInfo.objects
                    .filter(cg_consignmentnumber=cons)
                    .order_by('-id')
                    .first()
                )
                if goods:
                    invoice.ti_goods = goods

            department = ""
            if trip and getattr(trip, 'tr_enquirynumber', None):
                department = (
                    getattr(trip.tr_enquirynumber, 'en_customerdepartment', "") or ""
                )
            invoice.ti_department = department

            cust = invoice.ti_customer
            customer_name = str(cust).upper() if cust else ""

            if cust:
                invoice.ti_gst_in = getattr(cust, 'cu_gst', '') or invoice.ti_gst_in
                invoice.ti_pincode = getattr(cust, 'cu_pincode', '') or invoice.ti_pincode
                invoice.ti_customer_short_name = (
                    getattr(cust, 'cu_nameshort', '') or invoice.ti_customer_short_name
                )

            if "MAA" in customer_name:
                invoice.ti_branch = "Chennai"
                invoice.ti_state = "Tamil Nadu"
            elif "BLR" in customer_name:
                invoice.ti_branch = "Bangalore"
                invoice.ti_state = "Karnataka"
            else:
                invoice.ti_branch = invoice.ti_branch or ""
                invoice.ti_state = invoice.ti_state or ""

            invoice.save()
            saved = True

        else:
            messages.error(
                request,
                "Invoice not saved. Please correct the errors below."
            )

    else:
        form = TransInvoiceForm()

    invoice_list = TransInvoiceInfo.objects.none()

    return render(
        request,
        "asset_mgt_app/trans_invoice_Add.html",
        {
            "form": form,
            "invoice_list": invoice_list,
            "first_name": first_name,
            "saved": saved,
        }
    )



from django.db.models import Sum, F, Value, FloatField
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages


@login_required(login_url='login_page')
def trans_invoice_edit(request, invoice_id):
    first_name = request.session.get('first_name')

    invoice = get_object_or_404(TransInvoiceInfo, id=invoice_id)
    customer = invoice.ti_customer  # current customer

    # ==================================================
    # FETCH LIST SHOWN BELOW (USED FOR TOTAL CALCULATION)
    # ==================================================
    invoice_list = (
        TransInvoiceInfo.objects
        .filter(
            ti_customer=customer,
            is_woh=True
        )
        .annotate(
            trip_total=Coalesce(F('ti_trip__tc_tripcost'), 0.0) +
                       Coalesce(F('ti_trip__tc_tollcost'), 0.0) +
                       Coalesce(F('ti_trip__tc_parkingcost'), 0.0) +
                       Coalesce(F('ti_trip__tc_loadingcost'), 0.0) +
                       Coalesce(F('ti_trip__tc_unloadingcost'), 0.0) +
                       Coalesce(F('ti_trip__tc_haltingcost'), 0.0) +
                       Coalesce(F('ti_trip__tc_rtocost'), 0.0) +
                       Coalesce(F('ti_trip__tc_weighmentcost'), 0.0) +
                       Coalesce(F('ti_trip__tc_handlingcost'), 0.0) +
                       Coalesce(F('ti_trip__tc_cancellation'), 0.0)
        )
    )

    # ==================================================
    # AGGREGATE CHARGES FROM LIST
    # ==================================================
    # ==================================================
    # AGGREGATE CHARGES FROM LIST
    # ==================================================
    totals = invoice_list.aggregate(
        transport=Sum('ti_trip__tc_tripcost'),
        toll=Sum('ti_trip__tc_tollcost'),
        parking=Sum('ti_trip__tc_parkingcost'),
        loading=Sum('ti_trip__tc_loadingcost'),
        unloading=Sum('ti_trip__tc_unloadingcost'),
        halting=Sum('ti_trip__tc_haltingcost'),
        docket=Sum('ti_docket_charges'), # Docket charges might not be in Trip, creating ambiguity, checking model... keeping as is for safety if not in trip? Wait, earlier I used ti_docket_charges from invoice. Let's check trip model.
        weighment=Sum('ti_trip__tc_weighmentcost'),
        handling=Sum('ti_trip__tc_handlingcost'),
        cancellation=Sum('ti_trip__tc_cancellation'),
    )

    # Replace None with 0
    for key in totals:
        totals[key] = totals[key] or 0

    # ==================================================
    # POST REQUEST (SAVE)
    # ==================================================
    if request.method == "POST":
        form = TransInvoiceForm(request.POST, instance=invoice)

        if form.is_valid():
            invoice = form.save(commit=False)

            # TOTAL = SUM OF ALL CHARGES
            invoice.ti_total = (
                invoice.ti_transportation_charges +
                invoice.ti_toll_charges +
                invoice.ti_parking_charges +
                invoice.ti_loading_charges +
                invoice.ti_unloading_charges +
                invoice.ti_halting_charges +
                invoice.ti_docket_charges +
                invoice.ti_weighment_charges +
                invoice.ti_handling_charges +
                invoice.ti_cancellation_charges
            )

            # BRANCH / STATE LOGIC
            customer_name = str(invoice.ti_customer).upper()

            if "MAA" in customer_name:
                invoice.ti_branch = "Chennai"
                invoice.ti_state = "Tamil Nadu"
            elif "BLR" in customer_name:
                invoice.ti_branch = "Bangalore"
                invoice.ti_state = "Karnataka"
            else:
                invoice.ti_branch = ""
                invoice.ti_state = ""

            invoice.save()
            messages.success(request, "Transportation Invoice Updated Successfully!")
            return redirect("trans_invoice_list")

        else:
            messages.error(request, "Please fix the errors below")

    # ==================================================
    # GET REQUEST (EDIT PAGE LOAD)
    # 👉 PRE-FILL FORM WITH AGGREGATED TOTALS
    # ==================================================
    else:
        invoice.ti_transportation_charges = totals['transport']
        invoice.ti_toll_charges = totals['toll']
        invoice.ti_parking_charges = totals['parking']
        invoice.ti_loading_charges = totals['loading']
        invoice.ti_unloading_charges = totals['unloading']
        invoice.ti_halting_charges = totals['halting']
        invoice.ti_docket_charges = totals['docket']
        invoice.ti_weighment_charges = totals['weighment']
        invoice.ti_handling_charges = totals['handling']
        invoice.ti_cancellation_charges = totals['cancellation']

        invoice.ti_total = sum(totals.values())

        form = TransInvoiceForm(instance=invoice)

    return render(
        request,
        "asset_mgt_app/trans_invoice_Add.html",
        {
            'total_charges': invoice.ti_total,
            'form': form,
            'first_name': first_name,
            'invoice': invoice,
            'is_edit': True,
            'invoice_list': invoice_list.select_related(
                "ti_customer",
                "ti_trip",
                "ti_consignment",
                "ti_goods"
            ).order_by("-id"),
        }
    )

# ==================================================
# LIST TRANS INVOICE
# ==================================================
@login_required(login_url='login_page')
def trans_invoice_list(request):
    first_name = request.session.get('first_name')

    return render(
        request,
        "asset_mgt_app/trans_invoice_list.html",
        {
            'trans_invoice_list': TransInvoiceInfo.objects.all().order_by('-id'),
            'first_name': first_name,
        }
    )


# ==================================================
# DELETE TRANS INVOICE
# ==================================================
@login_required(login_url='login_page')
def trans_invoice_delete(request, invoice_id):
    invoice = get_object_or_404(TransInvoiceInfo, pk=invoice_id)
    invoice.delete()
    messages.success(request, "Transportation Invoice Deleted Successfully!")
    return redirect('trans_invoice_list')


# ==================================================
# AJAX – FETCH CUSTOMER DETAILS
# ==================================================
@login_required(login_url='login_page')
def fetch_customer_details(request):
    customer_id = request.GET.get('customer_id')
    customer = CustomerInfo.objects.filter(id=customer_id).first()

    if not customer:
        return JsonResponse({
            'gstin': '',
            'customer_short_name': '',
            'branch': '',
            'state': '',
        })

    customer_name = str(customer).upper()

    branch = ""
    state = ""

    if "MAA" in customer_name:
        branch = "Chennai"
        state = "Tamil Nadu"
    elif "BLR" in customer_name:
        branch = "Bangalore"
        state = "Karnataka"

    return JsonResponse({
        'gstin': customer.cu_gst or '',
        'customer_short_name': customer.cu_nameshort or '',
        'branch': branch,
        'state': state,
    })


from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

@login_required(login_url='login_page')
def trans_invoice_list_woh(request, customer_id):
    first_name = request.session.get('first_name')
    customer = get_object_or_404(CustomerInfo, id=customer_id)

    # ==========================
    # HANDLE ADD FROM MASTER
    # ==========================
    if request.method == "POST" and request.POST.get("action") == "add":
        import datetime
        try:
            # these MUST be Trip IDs
            trip_ids = request.POST.getlist('invoice_list[]')

            if not trip_ids:
                return JsonResponse({'status': 'error', 'message': 'No trips selected'}, status=400)

            # 1. Determine Branch/State Logic for this Customer
            customer_name = str(customer).upper()
            branch = ""
            state = ""
            if "MAA" in customer_name:
                branch = "Chennai"
                state = "Tamil Nadu"
            elif "BLR" in customer_name:
                branch = "Bangalore"
                state = "Karnataka"

            # 2. Iterate and Create/Update Invoice
            for t_id in trip_ids:
                # fetch trip
                trip = TripdetailInfo.objects.filter(id=t_id).first()
                if not trip:
                    continue

                # fetch consignment
                cons = trip.tr_consignmentnumber  # Check if None
                # fetch goods
                goods = None
                if cons:
                    goods = ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber=cons).order_by('-id').first()

                # Department
                department = ""
                if getattr(trip, 'tr_enquirynumber', None):
                    enq = trip.tr_enquirynumber
                    if enq.en_customerdepartment:
                         department = getattr(enq.en_customerdepartment, 'ct_customerdepartment', "") or ""

                # GST, Pincode, Short Name from Customer
                gst_in = getattr(customer, 'cu_gst', '') or ""
                pincode = getattr(customer, 'cu_pincode', '') or ""
                cust_short = getattr(customer, 'cu_nameshort', '') or ""

                # GENERATE TEMP INV fields
                # unique inv no format: "WOH-{trip_id}-{customer_id}" or similar.
                # Since ti_inv_no is unique, and we might add/remove/add again, we need it to be stable for the trip
                # OR if we removed it, we might have deleted it?
                # Actually, remove logic (trans_invoice_remove_woh) only updates is_woh=False, it does NOT delete the record.
                # So if it already exists, update_or_create works fine.
                # If it does NOT exist, we create it.
                inv_no = f"WOH-{trip.tr_tripnumber or trip.id}"
                today = datetime.date.today()

                TransInvoiceInfo.objects.update_or_create(
                    ti_trip=trip,
                    ti_customer=customer,
                    defaults={
                        "is_woh": True,
                        "ti_consignment": cons,
                        "ti_goods": goods,
                        "ti_department": department,
                        "ti_gst_in": gst_in,
                        "ti_pincode": pincode,
                        "ti_customer_short_name": cust_short,
                        "ti_branch": branch,
                        "ti_state": state,
                        # Required fields
                        "ti_inv_no": inv_no,
                        "ti_inv_date": today,
                        # Map Costs
                        "ti_transportation_charges": trip.tc_tripcost,
                        "ti_toll_charges": trip.tc_tollcost,
                        "ti_parking_charges": trip.tc_parkingcost,
                        "ti_loading_charges": trip.tc_loadingcost,
                        "ti_unloading_charges": trip.tc_unloadingcost,
                        "ti_halting_charges": trip.tc_haltingcost,
                        # "ti_docket_charges": 0, # No direct map
                        "ti_weighment_charges": trip.tc_weighmentcost,
                        "ti_handling_charges": trip.tc_handlingcost,
                        "ti_cancellation_charges": trip.tc_cancellation,
                        # Total
                        "ti_total": (
                                trip.tc_tripcost +
                                trip.tc_tollcost +
                                trip.tc_parkingcost +
                                trip.tc_loadingcost +
                                trip.tc_unloadingcost +
                                trip.tc_haltingcost +
                                trip.tc_weighmentcost +
                                trip.tc_handlingcost +
                                trip.tc_cancellation
                        )
                    }
                )

            return JsonResponse({'status': 'success'})

        except Exception as e:
            # Return detailed error
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # ==========================
    # TRANS INVOICE LIST (SELECTED ONLY)
    # ==========================

    # ==========================
    # MASTER LIST (NOT SELECTED)
    # ==========================
    selected_trip_ids = (
        TransInvoiceInfo.objects
        .filter(
            ti_customer_id=customer_id,
            is_woh=True
        )
        .values_list('ti_trip_id', flat=True)
    )
    trans_invoice_list = (
        TripdetailInfo.objects
        .filter(id__in=selected_trip_ids)
        .select_related(
            'tr_enquirynumber',
            'tr_consignmentnumber',
            'tr_vehicletype',
            'tr_vehiclesource',
        )
        .annotate(
            trip_total=Coalesce(F('tc_tripcost'), 0.0) +
                       Coalesce(F('tc_tollcost'), 0.0) +
                       Coalesce(F('tc_parkingcost'), 0.0) +
                       Coalesce(F('tc_loadingcost'), 0.0) +
                       Coalesce(F('tc_unloadingcost'), 0.0) +
                       Coalesce(F('tc_haltingcost'), 0.0) +
                       Coalesce(F('tc_rtocost'), 0.0) +
                       Coalesce(F('tc_weighmentcost'), 0.0) +
                       Coalesce(F('tc_handlingcost'), 0.0) +
                       Coalesce(F('tc_cancellation'), 0.0)
        )
        .order_by('-tr_created_at')

    )
    invoice_list_master = (
        TripdetailInfo.objects
        .filter(
            tr_enquirynumber__en_customername_id=customer_id
        )
        .exclude(
            id__in=selected_trip_ids
        )
        .select_related(
            'tr_enquirynumber',
            'tr_consignmentnumber',
            'tr_vehicletype',
            'tr_vehiclesource',
        )
        .annotate(
            trip_total=Coalesce(F('tc_tripcost'), 0.0) +
                       Coalesce(F('tc_tollcost'), 0.0) +
                       Coalesce(F('tc_parkingcost'), 0.0) +
                       Coalesce(F('tc_loadingcost'), 0.0) +
                       Coalesce(F('tc_unloadingcost'), 0.0) +
                       Coalesce(F('tc_haltingcost'), 0.0) +
                       Coalesce(F('tc_rtocost'), 0.0) +
                       Coalesce(F('tc_weighmentcost'), 0.0) +
                       Coalesce(F('tc_handlingcost'), 0.0) +
                       Coalesce(F('tc_cancellation'), 0.0)
        )
        .order_by('-tr_created_at')
    )
    # ==========================
    # ATTACH INVOICE FIELDS TO TRIP OBJECTS (NO TEMPLATE FILTERS)
    # ==========================
    invoice_qs = (
        TransInvoiceInfo.objects
        .filter(
            ti_trip_id__in=selected_trip_ids,
            ti_customer_id=customer_id,
            is_woh=True
        )
    )

    # map: trip_id -> invoice object
    invoice_map = {inv.ti_trip_id: inv for inv in invoice_qs}

    # attach needed invoice fields dynamically to trip
    for trip in trans_invoice_list:
        inv = invoice_map.get(trip.id)

        trip.ti_gst_in = inv.ti_gst_in if inv else ""
        trip.ti_state = inv.ti_state if inv else ""
        trip.ti_pincode = inv.ti_pincode if inv else ""
        trip.ti_branch = inv.ti_branch if inv else ""
        trip.ti_customer_short_name = inv.ti_customer_short_name if inv else ""

    customer = get_object_or_404(CustomerInfo, id=customer_id)

    departments = (
        TripdetailInfo.objects
        .filter(
            tr_enquirynumber__en_customername_id=customer_id,
            tr_enquirynumber__en_customerdepartment__isnull=False
        )
        .exclude(tr_enquirynumber__en_customerdepartment__ct_customerdepartment="")
        .values_list('tr_enquirynumber__en_customerdepartment__ct_customerdepartment', flat=True)
        .distinct()
        .order_by('tr_enquirynumber__en_customerdepartment__ct_customerdepartment')
    )
    
    # Check if departments are empty, maybe en_customerdepartment is just a charfield?
    # In step 100, I saw CustomerdepartmentInfo(models.Model): ct_customerdepartment = CharField
    # So it is a model. And Enquiry likely links to it.
    
    departments = [d for d in departments if d]

    # map trip_id → state & pincode (optional invoice info)
    invoice_meta = {
        obj.ti_trip_id: {
            "state": obj.ti_state,
            "pincode": obj.ti_pincode,
        }
        for obj in TransInvoiceInfo.objects.filter(
            ti_trip_id__in=selected_trip_ids
        )
    }

    return render(
        request,
        "asset_mgt_app/trans_invoice_list_WOH.html",
        {
            "trans_invoice_list": trans_invoice_list,  # TripdetailInfo list
            "invoice_list_master": invoice_list_master,
            "invoice_meta": invoice_meta,
            "departments": departments, # 👈 Added to context
            "customer": customer,
            "first_name": first_name,
        }
    )


@login_required(login_url='login_page')
def trans_invoice_remove_woh(request):
    trip_ids = request.GET.getlist('invoice_list[]')

    TransInvoiceInfo.objects.filter(
        ti_trip_id__in=trip_ids
    ).update(is_woh=False)

    return JsonResponse({'status': 'success'})

@login_required(login_url='login_page')
def trans_invoice_add_woh(request):
    trip_ids = request.POST.getlist('ids[]')

    for trip_id in trip_ids:
        TransInvoiceInfo.objects.update_or_create(
            ti_trip_id=trip_id,
            defaults={"is_woh": True}
        )

    return JsonResponse({'status': 'success'})

def trans_invoice_excel(request, invoice_no):

    # 🔹 FETCH DATA (USE FK PROPERLY)
    # 🔹 FETCH DATA (MATCHING WOH LIST LOGIC - BY CUSTOMER)
    # First, identify the customer from the passed invoice_no
    first_record = TransInvoiceInfo.objects.filter(ti_inv_no=invoice_no).first()
    
    if not first_record:
        # Graceful fallback if invoice not found, though unlikely via UI
        qs = TransInvoiceInfo.objects.none()
    else:
        customer = first_record.ti_customer
        qs = (
            TransInvoiceInfo.objects
            .filter(ti_customer=customer, is_woh=True)
            .select_related(
                "ti_customer",
                "ti_trip",
                "ti_consignment",
                "ti_goods"
            )
        )

    wb = Workbook()
    ws = wb.active
    ws.title = "Transport Invoice WOH"

    # 🔹 HEADERS
    headers = [
        "INV DATE",
        "Customer Name",
        "GST IN",
        "State",
        "Pincode",

        "INV NO",
        "Branch",
        "Vehicle Source",
        "Customer Short Name",

        "Tally Veh No",
        "Planning Date",
        "Cnote No",

        "From",
        "To",
        "Department",

        "Vehicle No",
        "Vehicle Type",

        "Vehicle Placed Date & Time",
        "Vehicle Released Date & Time",
        "Vehicle Arrived Date & Time",
        "Vehicle Dispatched Date & Time",

        "Consignee",
        "Reference No",
        "HAWB No",

        "No. of Pcs",
        "Weight",

        "Transportation Charges",
        "Toll Charges",
        "Parking Charges",
        "Loading Charges",
        "Unloading Charges",
        "Halting Charges",
        "Docket Charges",
        "Weighment Charges",
        "Handling Charges",
        "Cancellation Charges",

        "TOTAL"
    ]
    ws.append(headers)

    # 🔹 COLUMN WIDTH (FIX ##### ISSUE)
    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["K"].width = 18
    ws.column_dimensions["R"].width = 22
    ws.column_dimensions["S"].width = 22
    ws.column_dimensions["T"].width = 22
    ws.column_dimensions["U"].width = 22

    # safe attribute helper
    def sget(o, attr):
        try:
            if o is None:
                return ""
            val = getattr(o, attr)
            return "" if val is None else val
        except Exception:
            return ""
    # alias backwards-compatible name used in previous edits
    safe = sget

    # 🔹 DATA ROWS
    def safe(val):
        return val if val is not None else ""

    for obj in qs:

        # 🔹 1️⃣ GET CONSIGNMENT (fallback if FK missing)
        cons = obj.ti_consignment

        if not cons:
            cons = (
                ConsignmentdetailInfo.objects
                .filter(co_customer=obj.ti_customer)
                .order_by('-id')
                .first()
            )

        # 🔹 2️⃣ GET TRIP
        trip = obj.ti_trip
        if not trip and cons:
            trip = (
                TripdetailInfo.objects
                .filter(tr_consignmentnumber=cons)
                .order_by('-id')
                .first()
            )

        # 🔹 3️⃣ GET GOODS
        goods = obj.ti_goods
        if not goods and cons:
            goods = (
                ConsignmentgoodsInfo.objects
                .filter(cg_consignmentnumber=cons)
                .order_by('-id')
                .first()
            )

        # Calculate Trip Total dynamically
        trip_total = 0.0
        if trip:
            trip_total = (
                (trip.tc_tripcost or 0) +
                (trip.tc_tollcost or 0) +
                (trip.tc_parkingcost or 0) +
                (trip.tc_loadingcost or 0) +
                (trip.tc_unloadingcost or 0) +
                (trip.tc_haltingcost or 0) +
                (trip.tc_rtocost or 0) +
                (trip.tc_weighmentcost or 0) +
                (trip.tc_handlingcost or 0) +
                (trip.tc_cancellation or 0)
            )

        ws.append([
            safe(obj.ti_inv_date),
            safe(str(trip.tr_enquirynumber.en_customername) if trip and getattr(trip, 'tr_enquirynumber', None) else ""),  # from Trip
            safe(obj.ti_gst_in),
            safe(obj.ti_state),
            safe(obj.ti_pincode),
            # safe(obj.ti_inv_no), # User requested removal of INV NO in list, maybe in excel too? Keeping it as per header but list logic removed it.
            # Wait, headers still have INV NO. Let's keep it but formatted correctly or empty if requested?
            # User said "data in trans_invoice_list_WOH must be downloaded". WOH list DOES NOT show INV NO.
            # But header list has "INV NO". I will keep it for now as per existing header.
            safe(obj.ti_inv_no),

            safe(obj.ti_branch),
            safe(str(trip.tr_vehiclesource) if trip and getattr(trip, 'tr_vehiclesource', None) else ""),
            safe(str(trip.tr_enquirynumber.en_customername) if trip and getattr(trip, 'tr_enquirynumber', None) else ""),  # from Trip (Short Name)
            safe(get_tally_vehicle_no(obj)),
            safe(str(trip.tr_departeddate) if trip and getattr(trip, 'tr_departeddate', None) else ""),

            safe(str(cons.co_consignmentnumber) if cons and getattr(cons, 'co_consignmentnumber', None) else ""),
            safe(str(trip.tr_departedlocation) if trip and getattr(trip, 'tr_departedlocation', None) else ""),
            safe(str(trip.tr_reportedlocation) if trip and getattr(trip, 'tr_reportedlocation', None) else ""),
            safe(obj.ti_department),

            safe(str(trip.tr_vehiclenumber) if trip and getattr(trip, 'tr_vehiclenumber', None) else ""),
            safe(str(trip.tr_vehicletype) if trip and getattr(trip, 'tr_vehicletype', None) else ""),

            safe(str(trip.tr_departeddate_pickup) if trip and getattr(trip, 'tr_departeddate_pickup', None) else ""),
            safe(str(trip.tr_dock_out_time) if trip and getattr(trip, 'tr_dock_out_time', None) else ""),
            safe(str(trip.tr_reporteddate) if trip and getattr(trip, 'tr_reporteddate', None) else ""),
            safe(str(trip.tr_departeddate_delivery) if trip and getattr(trip, 'tr_departeddate_delivery', None) else ""),

            safe(str(goods.cg_consignee) if goods and getattr(goods, 'cg_consignee', None) else ""),
            safe(str(cons.co_cusrefnum) if cons and getattr(cons, 'co_cusrefnum', None) else ""),
            safe(str(goods.cg_hawbno) if goods and getattr(goods, 'cg_hawbno', None) else ""),

            safe(str(goods.cg_qty) if goods and getattr(goods, 'cg_qty', None) else ""),
            safe(str(goods.cg_weight) if goods and getattr(goods, 'cg_weight', None) else ""),

            safe(trip.tc_tripcost if trip else 0),
            safe(trip.tc_tollcost if trip else 0),
            safe(trip.tc_parkingcost if trip else 0),
            safe(trip.tc_loadingcost if trip else 0),
            safe(trip.tc_unloadingcost if trip else 0),
            safe(trip.tc_haltingcost if trip else 0),
            # safe(obj.ti_docket_charges), # Trip doesn't have docket charges, using obj or 0? List uses trip. Let's use 0 or check if trip has it. Trip model check previously showed no docket.
            safe(0), # Docket
            safe(trip.tc_weighmentcost if trip else 0),
            safe(trip.tc_handlingcost if trip else 0),
            safe(trip.tc_cancellation if trip else 0),

            safe(trip_total)
        ])

    # 🔹 RESPONSE — write workbook to a BytesIO buffer then return bytes
    from io import BytesIO

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="WOH_invoice_{invoice_no}.xlsx"'
    )

    return response


def get_tally_vehicle_no(invoice):
    trip = invoice.ti_trip
    if not trip:
        return ""

    # 1️⃣ Resolve vehicle number robustly
    vehicle_no = ""

    if hasattr(trip, "tr_vehiclenumber") and trip.tr_vehiclenumber:
        vehicle_no = trip.tr_vehiclenumber

    elif hasattr(trip, "tr_vehicle") and trip.tr_vehicle:
        vehicle_no = getattr(trip.tr_vehicle, "tr_vehiclenumber", "")

    vehicle_no = (vehicle_no or "").strip()

    # 2️⃣ Resolve vehicle source safely
    vehicle_source_obj = trip.tr_vehiclesource
    if not vehicle_source_obj:
        return ""

    vehicle_source = str(vehicle_source_obj).upper()

    # 3️⃣ Apply Tally rules
    if "OWN" in vehicle_source:
        return vehicle_no

    elif "ATTACHED" in vehicle_source:
        return f"{vehicle_no}(A)" if vehicle_no else "(A)"

    elif "MARKET" in vehicle_source:
        return "MKT"

    return ""
