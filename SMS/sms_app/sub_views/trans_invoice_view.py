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
                invoice.ti_gst_in = getattr(cust, 'CustomerInfo.cu_gst', '') or invoice.ti_gst_in
                invoice.ti_pincode = getattr(cust, 'CustomerInfo.cu_pincode', '') or invoice.ti_pincode
                invoice.ti_customer_short_name = (
                    getattr(cust, 'CustomerInfo.cu_nameshort', '') or invoice.ti_customer_short_name
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
            "invoice": invoice,
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
        .exclude(ti_trip_id__isnull=True)
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
            tr_consignmentnumber__co_consignmentnumber__isnull=True
        )
        .exclude(
            tr_consignmentnumber__co_consignmentnumber=''
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
    # 🔹 FETCH DATA (MATCHING WOH LIST LOGIC - BY CUSTOMER)
    first_record = TransInvoiceInfo.objects.filter(ti_inv_no=invoice_no).first()
    
    if not first_record:
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
        "Planning Date",
        "Cnote No",
        "From",
        "To",
        "Dept",
        "Veh No",
        "Veh Type",
        "Veh reported Date & Time at Loading Point",
        "Veh started Date & Time at Loading Point",
        "Veh Reported Date & Time at unloading Point",
        "Trip Closed Date & Time at Unloading Point",
        "Consignee",
        "Reference No",
        "HAWB No",
        "No.of Pcs",
        "Weight",
        "Transportation Charges",
        "TOLL CHARGES",
        "Parking Charges",
        "Loading Charges",
        "Unloading Charges",
        "HALTING CHARGES",
        "DOCKET CHARGES",
        "WEIGHMENT CHARGES",
        "Transportation Handling Charges",
        "Cancellation Charges",
        "TOTAL"
    ]
    ws.append(headers)

    # 🔹 COLUMN WIDTH
    ws.column_dimensions["A"].width = 18
    ws.column_dimensions["H"].width = 25
    ws.column_dimensions["I"].width = 25
    ws.column_dimensions["J"].width = 25
    ws.column_dimensions["K"].width = 25

    def safe(val):
        return val if val is not None else ""

    for obj in qs:
        # Resolve related objects safely
        trip = obj.ti_trip
        cons = obj.ti_consignment
        goods = obj.ti_goods

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
            safe(str(trip.tr_departeddate) if trip else ""),
            safe(str(cons.co_consignmentnumber) if cons else ""),
            safe(str(trip.tr_departedlocation) if trip else ""),
            safe(str(trip.tr_reportedlocation) if trip else ""),
            safe(obj.ti_department),
            safe(str(trip.tr_vehiclenumber) if trip else ""),
            safe(str(trip.tr_vehicletype) if trip else ""),
            safe(str(trip.tr_departeddate_pickup) if trip else ""),
            safe(str(trip.tr_dock_out_time) if trip else ""),
            safe(str(trip.tr_reporteddate) if trip else ""),
            safe(str(trip.tr_departeddate_delivery) if trip else ""),
            safe(str(goods.cg_consignee) if goods else ""),
            safe(str(cons.co_cusrefnum) if cons else ""),
            safe(str(goods.cg_hawbno) if goods else ""),
            safe(str(goods.cg_qty) if goods else ""),
            safe(str(goods.cg_weight) if goods else ""),
            safe(trip.tc_tripcost if trip else 0),
            safe(trip.tc_tollcost if trip else 0),
            safe(trip.tc_parkingcost if trip else 0),
            safe(trip.tc_loadingcost if trip else 0),
            safe(trip.tc_unloadingcost if trip else 0),
            safe(trip.tc_haltingcost if trip else 0),
            safe(0), # DOCKET CHARGES (Placeholder as not in trip)
            safe(trip.tc_weighmentcost if trip else 0),
            safe(trip.tc_handlingcost if trip else 0),
            safe(trip.tc_cancellation if trip else 0),
            safe(trip_total)
        ])

    from io import BytesIO
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="WOH_invoice_{invoice_no}.xlsx"'

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


@login_required(login_url='login_page')
def trans_invoice_tally_excel(request, customer_id):
    customer = get_object_or_404(CustomerInfo, id=customer_id)
    
    # Fetch trips where is_woh=True for this customer
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

    if not qs.exists():
        messages.warning(request, "No invoices found in WOH list for this customer.")
        return redirect('trans_invoice_list')

    wb = Workbook()
    ws = wb.active
    ws.title = "Tally Export"

    # 🔹 HEADERS (Specialized for Tally)
    headers = [
        "DATE",
        "SUNDRY DEBTORS",
        "STATE",
        "PINCODE",
        "VOUCHER NO.",
        "PRIMARY COST CATEGORY",
        "CUSTOMER",
        "JOB NO.",
        "VEHICLE NUMBER",
        "Transportation Charges",
        "Toll Charges",
        "Parking Charges",
        "Loading Charges",
        "Unloading Charges",
        "Halting Charges",
        "Docket Charges",
        "Weighment Charges",
        "EXTRA KM CHARGES",
        "EXTRA HOUR CHARGES",
        "TRANSPORTATION HANDLING CHARGES",
        "TOTAL"
    ]
    ws.append(headers)

    # 🔹 COLUMN WIDTH
    ws.column_dimensions["A"].width = 15
    ws.column_dimensions["B"].width = 25
    ws.column_dimensions["C"].width = 10
    ws.column_dimensions["D"].width = 10
    ws.column_dimensions["E"].width = 15

    def safe(val):
        return val if val is not None else ""

    for obj in qs:
        trip = obj.ti_trip
        cons = obj.ti_consignment
        
        # Calculate Total based on the specific fields being displayed
        total_val = (
            (obj.ti_transportation_charges or 0) +
            (obj.ti_toll_charges or 0) +
            (obj.ti_parking_charges or 0) +
            (obj.ti_loading_charges or 0) +
            (obj.ti_unloading_charges or 0) +
            (obj.ti_halting_charges or 0) +
            (obj.ti_docket_charges or 0) +
            (obj.ti_weighment_charges or 0) +
            (obj.ti_handling_charges or 0)
        )

        ws.append([
            safe(obj.ti_inv_date),
            safe(obj.ti_customer_short_name),
            safe(obj.ti_state),
            safe(obj.ti_pincode),
            safe(obj.ti_inv_no),
            safe(str(trip.tr_vehiclesource) if trip and trip.tr_vehiclesource else ""),
            safe(str(customer.cu_name).strip().upper()),
            safe(str(cons.co_consignmentnumber) if cons else ""),
            safe(get_tally_vehicle_no(obj)),
            safe(obj.ti_transportation_charges or 0),
            safe(obj.ti_toll_charges or 0),
            safe(obj.ti_parking_charges or 0),
            safe(obj.ti_loading_charges or 0),
            safe(obj.ti_unloading_charges or 0),
            safe(obj.ti_halting_charges or 0),
            safe(obj.ti_docket_charges or 0),
            safe(obj.ti_weighment_charges or 0),
            safe(0), # EXTRA KM CHARGES
            safe(0), # EXTRA HOUR CHARGES
            safe(obj.ti_handling_charges or 0), # TRANSPORTATION HANDLING CHARGES
            safe(total_val)
        ])

    from io import BytesIO
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="Tally_Export_{customer.cu_nameshort or customer.id}.xlsx"'
    return response
