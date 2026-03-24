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
            invoice.ti_total = 0  # Initialize to 0 as no WOH items yet
            invoice.ti_transportation_charges = 0
            invoice.ti_toll_charges = 0
            invoice.ti_parking_charges = 0
            invoice.ti_loading_charges = 0
            invoice.ti_unloading_charges = 0
            invoice.ti_halting_charges = 0
            invoice.ti_docket_charges = 0
            invoice.ti_weighment_charges = 0
            invoice.ti_handling_charges = 0
            invoice.ti_cancellation_charges = 0

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
            # -------------------------
            # NEW: enforce UNIQUE invoice number on add page
            # If an invoice number is provided and already exists (case-insensitive), do not save.
            # -------------------------
            inv_no = (invoice.ti_inv_no or "").strip()
            if inv_no:
                # Check existence across the table (case-insensitive)
                if TransInvoiceInfo.objects.filter(ti_inv_no__iexact=inv_no).exists():
                    messages.error(request, f"Invoice number '{inv_no}' already exists. Please use a unique invoice number.")
                else:
                    # assign stripped value and save
                    invoice.ti_inv_no = inv_no
                    invoice.save()
                    saved = True
            else:
                # No invoice number provided; save as before
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



from django.db.models import Sum, F, Value, FloatField, Subquery, OuterRef
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
            ti_inv_no=invoice.ti_inv_no,
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
    totals = invoice_list.aggregate(
        transport=Sum('ti_trip__tc_tripcost'),
        toll=Sum('ti_trip__tc_tollcost'),
        parking=Sum('ti_trip__tc_parkingcost'),
        loading=Sum('ti_trip__tc_loadingcost'),
        unloading=Sum('ti_trip__tc_unloadingcost'),
        halting=Sum('ti_trip__tc_haltingcost'),
        docket=Sum('ti_docket_charges'), 
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

            # RE-CALCULATE TOTALS FROM SAVED WOH ITEMS (Ignore form read-only inputs)
            # Fetch WOH items again to be sure
            woh_items = TransInvoiceInfo.objects.filter(
                ti_customer=invoice.ti_customer,
                ti_inv_no=invoice.ti_inv_no, # Ensure we only sum items for THIS invoice number
                is_woh=True
            )
            
            # Aggregate again
            aggs = woh_items.aggregate(
                transport=Sum('ti_trip__tc_tripcost'),
                toll=Sum('ti_trip__tc_tollcost'),
                parking=Sum('ti_trip__tc_parkingcost'),
                loading=Sum('ti_trip__tc_loadingcost'),
                unloading=Sum('ti_trip__tc_unloadingcost'),
                halting=Sum('ti_trip__tc_haltingcost'),
                docket=Sum('ti_docket_charges'),
                weighment=Sum('ti_trip__tc_weighmentcost'),
                handling=Sum('ti_trip__tc_handlingcost'),
                cancellation=Sum('ti_trip__tc_cancellation'),
            )
            
            # Helper to safe get
            def get_val(k): return aggs.get(k) or 0.0

            invoice.ti_transportation_charges = get_val('transport')
            invoice.ti_toll_charges = get_val('toll')
            invoice.ti_parking_charges = get_val('parking')
            invoice.ti_loading_charges = get_val('loading')
            invoice.ti_unloading_charges = get_val('unloading')
            invoice.ti_halting_charges = get_val('halting')
            invoice.ti_docket_charges = get_val('docket')
            invoice.ti_weighment_charges = get_val('weighment')
            invoice.ti_handling_charges = get_val('handling')
            invoice.ti_cancellation_charges = get_val('cancellation')

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

    queryset = (
        TransInvoiceInfo.objects
        .filter(is_woh=False)
        .order_by('-id')
    )

    return render(
        request,
        "asset_mgt_app/trans_invoice_list.html",
        {
            'trans_invoice_list': queryset,
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
            'customer_name': '',
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
        'customer_name': customer_name,
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
            trip_ids = request.POST.getlist('invoice_list[]')
            invoice_id = request.POST.get('invoice_id')
            if not invoice_id or invoice_id == 'null':
                return JsonResponse({'status': 'error', 'message': 'Master invoice ID is required. Please save the invoice first.'}, status=400)

            master_inv = TransInvoiceInfo.objects.filter(id=invoice_id).first()
            if not master_inv:
                return JsonResponse({'status': 'error', 'message': 'Master invoice not found.'}, status=404)

            manual_inv_no = master_inv.ti_inv_no
            manual_inv_date = master_inv.ti_inv_date
            
            if not manual_inv_no:
                return JsonResponse({'status': 'error', 'message': 'Invoice number is missing in the master invoice. Please enter it first.'}, status=400)

            customer_name = str(customer).upper()
            branch = ""
            state = ""
            if "MAA" in customer_name:
                branch = "Chennai"
                state = "Tamil Nadu"
            elif "BLR" in customer_name:
                branch = "Bangalore"
                state = "Karnataka"

            for t_id in trip_ids:
                trip = TripdetailInfo.objects.filter(id=t_id).first()
                if not trip: continue

                cons = trip.tr_consignmentnumber
                goods = None
                if cons:
                    goods = ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber=cons).order_by('-id').first()

                department = ""
                if getattr(trip, 'tr_enquirynumber', None):
                    enq = trip.tr_enquirynumber
                    if enq.en_customerdepartment:
                         department = getattr(enq.en_customerdepartment, 'ct_customerdepartment', "") or ""

                gst_in = getattr(customer, 'cu_gst', '') or ""
                pincode = getattr(customer, 'cu_pincode', '') or ""
                cust_short = getattr(customer, 'cu_nameshort', '') or ""

                inv_no = manual_inv_no
                inv_date = manual_inv_date if manual_inv_date else datetime.date.today()

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
                        "ti_inv_no": inv_no,
                        "ti_inv_date": inv_date,
                        "ti_transportation_charges": trip.tc_tripcost,
                        "ti_toll_charges": trip.tc_tollcost,
                        "ti_parking_charges": trip.tc_parkingcost,
                        "ti_loading_charges": trip.tc_loadingcost,
                        "ti_unloading_charges": trip.tc_unloadingcost,
                        "ti_halting_charges": trip.tc_haltingcost,
                        "ti_weighment_charges": trip.tc_weighmentcost,
                        "ti_handling_charges": trip.tc_handlingcost,
                        "ti_cancellation_charges": trip.tc_cancellation,
                        "ti_total": (
                                (trip.tc_tripcost or 0) +
                                (trip.tc_tollcost or 0) +
                                (trip.tc_parkingcost or 0) +
                                (trip.tc_loadingcost or 0) +
                                (trip.tc_unloadingcost or 0) +
                                (trip.tc_haltingcost or 0) +
                                (trip.tc_weighmentcost or 0) +
                                (trip.tc_handlingcost or 0) +
                                (trip.tc_cancellation or 0)
                        )
                    }
                )

            # Recalculate Master Invoice Totals
            if master_inv:
                woh_items = TransInvoiceInfo.objects.filter(
                    ti_customer=customer,
                    ti_inv_no=manual_inv_no,
                    is_woh=True
                )
                from django.db.models import Sum
                aggs = woh_items.aggregate(
                    transport=Sum('ti_trip__tc_tripcost'),
                    toll=Sum('ti_trip__tc_tollcost'),
                    parking=Sum('ti_trip__tc_parkingcost'),
                    loading=Sum('ti_trip__tc_loadingcost'),
                    unloading=Sum('ti_trip__tc_unloadingcost'),
                    halting=Sum('ti_trip__tc_haltingcost'),
                    weighment=Sum('ti_trip__tc_weighmentcost'),
                    handling=Sum('ti_trip__tc_handlingcost'),
                    cancellation=Sum('ti_trip__tc_cancellation'),
                )
                def get_val(k): return aggs.get(k) or 0.0

                master_inv.ti_transportation_charges = get_val('transport')
                master_inv.ti_toll_charges = get_val('toll')
                master_inv.ti_parking_charges = get_val('parking')
                master_inv.ti_loading_charges = get_val('loading')
                master_inv.ti_unloading_charges = get_val('unloading')
                master_inv.ti_halting_charges = get_val('halting')
                master_inv.ti_weighment_charges = get_val('weighment')
                master_inv.ti_handling_charges = get_val('handling')
                master_inv.ti_cancellation_charges = get_val('cancellation')

                master_inv.ti_total = (
                    master_inv.ti_transportation_charges +
                    master_inv.ti_toll_charges +
                    master_inv.ti_parking_charges +
                    master_inv.ti_loading_charges +
                    master_inv.ti_unloading_charges +
                    master_inv.ti_halting_charges +
                    (master_inv.ti_docket_charges or 0.0) +
                    master_inv.ti_weighment_charges +
                    master_inv.ti_handling_charges +
                    master_inv.ti_cancellation_charges
                )
                master_inv.save()

            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    # ==========================
    # FETCH LIST SHOWN BELOW
    # ==========================
    # Capture invoice_id for filtering
    invoice_id = request.GET.get('invoice_id')
    inv_no_filter = ""
    if invoice_id:
        master_inv = TransInvoiceInfo.objects.filter(id=invoice_id).first()
        if master_inv:
            inv_no_filter = master_inv.ti_inv_no

    # 1. Trips for the current manual invoice (to show in WOH list)
    current_woh_trip_ids = []
    if inv_no_filter:
        current_woh_trip_ids = (
            TransInvoiceInfo.objects
            .filter(ti_customer_id=customer_id, ti_inv_no=inv_no_filter, is_woh=True)
            .exclude(ti_trip_id__isnull=True)
            .values_list('ti_trip_id', flat=True)
        )

    # 2. ALL trips already assigned to ANY invoice record for this customer
    # (These must be excluded from the Master list, even if they are from another invoice)
    all_assigned_trip_ids = (
        TransInvoiceInfo.objects
        .filter(ti_customer_id=customer_id)
        .exclude(ti_trip_id__isnull=True)
        .values_list('ti_trip_id', flat=True)
    )

    trans_invoice_list = (
        TripdetailInfo.objects
        .filter(id__in=current_woh_trip_ids)
        .select_related('tr_enquirynumber','tr_consignmentnumber','tr_vehicletype','tr_vehiclesource')
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
            tr_enquirynumber__en_customername_id=customer_id,
            tc_financestatus_id=7  # Only show settled trips
        )
        .exclude(tr_consignmentnumber__co_consignmentnumber__isnull=True)
        .exclude(tr_consignmentnumber__co_consignmentnumber='')
        .exclude(id__in=all_assigned_trip_ids)
        .select_related('tr_enquirynumber','tr_consignmentnumber','tr_vehicletype','tr_vehiclesource')
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

    invoice_qs = TransInvoiceInfo.objects.filter(ti_trip_id__in=current_woh_trip_ids, ti_customer_id=customer_id, is_woh=True)
    invoice_map = {inv.ti_trip_id: inv for inv in invoice_qs}

    for trip in trans_invoice_list:
        inv = invoice_map.get(trip.id)
        if inv:
            trip.ti_gst_in = inv.ti_gst_in
            trip.ti_state = inv.ti_state
            trip.ti_pincode = inv.ti_pincode
            trip.ti_branch = inv.ti_branch
            trip.ti_customer_short_name = inv.ti_customer_short_name
            # Map only needed invoice fields to trip object for display
            trip.ti_inv_no = inv.ti_inv_no
            trip.ti_inv_date = inv.ti_inv_date
            trip.tally_vehicle_no = get_tally_vehicle_no(inv)
        else:
            trip.ti_gst_in = ""
            trip.ti_state = ""
            trip.ti_pincode = ""
            trip.ti_branch = ""
            trip.ti_customer_short_name = ""
            trip.tally_vehicle_no = ""
            trip.ti_inv_no = ""
            trip.ti_inv_date = ""

    customer = get_object_or_404(CustomerInfo, id=customer_id)
    departments = (
        TripdetailInfo.objects
        .filter(tr_enquirynumber__en_customername_id=customer_id, tr_enquirynumber__en_customerdepartment__isnull=False)
        .exclude(tr_enquirynumber__en_customerdepartment__ct_customerdepartment="")
        .values_list('tr_enquirynumber__en_customerdepartment__ct_customerdepartment', flat=True)
        .distinct()
        .order_by('tr_enquirynumber__en_customerdepartment__ct_customerdepartment')
    )
    departments = [d for d in departments if d]

    invoice_meta = {
        obj.ti_trip_id: {"state": obj.ti_state, "pincode": obj.ti_pincode}
        for obj in TransInvoiceInfo.objects.filter(ti_trip_id__in=current_woh_trip_ids)
    }

    return render(
        request,
        "asset_mgt_app/trans_invoice_list_WOH.html",
        {
            "trans_invoice_list": trans_invoice_list,
            "invoice_list_master": invoice_list_master,
            "invoice_meta": invoice_meta,
            "departments": departments,
            "customer": customer,
            "first_name": first_name,
        }
    )


from django.db.models import Sum

@login_required(login_url='login_page')
def trans_invoice_remove_woh(request):
    trip_ids = request.GET.getlist('invoice_list[]')
    
    # Get master invoice specs before deleting
    woh_items = TransInvoiceInfo.objects.filter(ti_trip_id__in=trip_ids, is_woh=True)
    affected_pairs = list(woh_items.values('ti_inv_no', 'ti_customer_id').distinct())

    # Delete the specified WOH items
    woh_items.delete()

    # Recalculate totals for the affected master invoices
    for pair in affected_pairs:
        inv_no = pair['ti_inv_no']
        cid = pair['ti_customer_id']
        master_inv = TransInvoiceInfo.objects.filter(ti_inv_no=inv_no, ti_customer_id=cid, is_woh=False).first()
        if master_inv:
            woh_remaining = TransInvoiceInfo.objects.filter(ti_inv_no=inv_no, ti_customer_id=cid, is_woh=True)
            aggs = woh_remaining.aggregate(
                transport=Sum('ti_trip__tc_tripcost'),
                toll=Sum('ti_trip__tc_tollcost'),
                parking=Sum('ti_trip__tc_parkingcost'),
                loading=Sum('ti_trip__tc_loadingcost'),
                unloading=Sum('ti_trip__tc_unloadingcost'),
                halting=Sum('ti_trip__tc_haltingcost'),
                weighment=Sum('ti_trip__tc_weighmentcost'),
                handling=Sum('ti_trip__tc_handlingcost'),
                cancellation=Sum('ti_trip__tc_cancellation'),
            )
            def get_val(k): return aggs.get(k) or 0.0

            master_inv.ti_transportation_charges = get_val('transport')
            master_inv.ti_toll_charges = get_val('toll')
            master_inv.ti_parking_charges = get_val('parking')
            master_inv.ti_loading_charges = get_val('loading')
            master_inv.ti_unloading_charges = get_val('unloading')
            master_inv.ti_halting_charges = get_val('halting')
            master_inv.ti_weighment_charges = get_val('weighment')
            master_inv.ti_handling_charges = get_val('handling')
            master_inv.ti_cancellation_charges = get_val('cancellation')

            master_inv.ti_total = (
                master_inv.ti_transportation_charges +
                master_inv.ti_toll_charges +
                master_inv.ti_parking_charges +
                master_inv.ti_loading_charges +
                master_inv.ti_unloading_charges +
                master_inv.ti_halting_charges +
                (master_inv.ti_docket_charges or 0.0) +
                master_inv.ti_weighment_charges +
                master_inv.ti_handling_charges +
                master_inv.ti_cancellation_charges
            )
            master_inv.save()

    return JsonResponse({'status': 'success'})

@login_required(login_url='login_page')
def trans_invoice_add_woh(request):
    trip_ids = request.POST.getlist('ids[]')
    for trip_id in trip_ids:
        TransInvoiceInfo.objects.update_or_create(ti_trip_id=trip_id, defaults={"is_woh": True})
    return JsonResponse({'status': 'success'})


def trans_invoice_excel(request, invoice_no):
    first_record = TransInvoiceInfo.objects.filter(ti_inv_no=invoice_no).first()
    if not first_record:
        qs = TransInvoiceInfo.objects.none()
    else:
        customer = first_record.ti_customer
        qs = TransInvoiceInfo.objects.filter(ti_customer=customer, ti_inv_no=invoice_no, is_woh=True).select_related("ti_customer","ti_trip","ti_consignment","ti_goods")

    wb = Workbook()
    ws = wb.active
    ws.title = "Transport Invoice WOH"

    # 🔹 HEADERS
    customer_name = str(customer).upper() if first_record and first_record.ti_customer else ""

    # 🔹 HEADERS
    base_headers = [
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
        "Toll Charges",
        "Parking Charges",
        "Loading Charges",
        "Unloading Charges",
        "Halting Charges",
        "Docket Charges",
        "Weighment Charges",
        "Transportation Handling Charges",
        "Cancellation Charges",
        "Total",
    ]

    extra_headers = []
    if "DSV" in customer_name:
        extra_headers = ["AAI S.no", "Eway Bill No"]
    elif "APM" in customer_name:
        extra_headers = ["Requestor"]
    elif "DBS" in customer_name:
        extra_headers = ["Adhoc Rate /Contracted Rate"]
    elif "CEVA" in customer_name:
        extra_headers = ["Requestor", "BOE NO"]
    elif "EIPL" in customer_name:
        extra_headers = ["Eway Bill No", "No. of Halting Days", "Billing SOW/Non BillingSOW"]
    
    # Default case: extra_headers remains empty []

    ws.append(base_headers + extra_headers)

    ws.column_dimensions["A"].width = 18
    for col in "HIJK": ws.column_dimensions[col].width = 25

    def safe(val): return val if val is not None else ""

    for obj in qs:
        trip = obj.ti_trip
        cons = obj.ti_consignment
        goods = obj.ti_goods
        trip_total = 0.0
        if trip:
            trip_total = (
                (trip.tc_tripcost or 0) + (trip.tc_tollcost or 0) + (trip.tc_parkingcost or 0) +
                (trip.tc_loadingcost or 0) + (trip.tc_unloadingcost or 0) + (trip.tc_haltingcost or 0) +
                (trip.tc_rtocost or 0) + (trip.tc_weighmentcost or 0) + (trip.tc_handlingcost or 0) +
                (trip.tc_cancellation or 0)
            )

        row = [
            safe(trip.tr_enquirynumber.en_pickupdatetime.strftime('%d/%m/%Y') if trip and trip.tr_enquirynumber and trip.tr_enquirynumber.en_pickupdatetime else ""),
            safe(str(cons.co_consignmentnumber) if cons else ""),
            safe(str(trip.tr_departedlocation) if trip else ""),
            safe(str(trip.tr_reportedlocation) if trip else ""),
            safe(obj.ti_department),
            safe(str(trip.tr_vehiclenumber) if trip else ""),
            safe(str(trip.tr_vehicletype) if trip else ""),
            safe(trip.tr_departeddate_pickup.strftime('%d/%m/%Y %H:%M') if trip and trip.tr_departeddate_pickup else ""),
            safe(trip.tr_departeddate.strftime('%d/%m/%Y %H:%M') if trip and trip.tr_departeddate else ""),
            safe(trip.tr_reporteddate.strftime('%d/%m/%Y %H:%M') if trip and trip.tr_reporteddate else ""),
            safe(trip.tr_reporteddate_pickup.strftime('%d/%m/%Y %H:%M') if trip and trip.tr_reporteddate_pickup else ""),
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
            safe(0), safe(trip.tc_weighmentcost if trip else 0),
            safe(trip.tc_handlingcost if trip else 0), safe(trip.tc_cancellation if trip else 0),
            safe(trip_total),
        ]

        extra_values = []
        if "DSV" in customer_name:
            extra_values = [
                safe(obj.ti_aai_sno),
                safe(goods.cg_ebillno if goods else ""),
            ]
        elif "APM" in customer_name:
            extra_values = [
                safe(trip.tr_enquirynumber.en_requestor if trip and trip.tr_enquirynumber else ""),
            ]
        elif "DBS" in customer_name:
            extra_values = [
                safe(obj.ti_type_of_rate),
            ]
        elif "CEVA" in customer_name:
            extra_values = [
                safe(trip.tr_enquirynumber.en_requestor if trip and trip.tr_enquirynumber else ""),
                "",  # BOE NO - kept empty as Cnote No already displays consignment number
            ]
        elif "EIPL" in customer_name:
            extra_values = [
                safe(goods.cg_ebillno if goods else ""),
                safe(trip.tc_no_of_days_halting if trip else 0),
                safe(obj.ti_sow),
            ]
        
        ws.append(row + extra_values)

    from io import BytesIO
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="WOH_invoice_{invoice_no}.xlsx"'
    return response


def get_tally_vehicle_no(invoice):
    trip = invoice.ti_trip
    if not trip: return ""
    vehicle_no = (getattr(trip, "tr_vehiclenumber", "") or getattr(getattr(trip, "tr_vehicle", None), "tr_vehiclenumber", "") or "").strip()
    vehicle_source_obj = trip.tr_vehiclesource
    if not vehicle_source_obj: return ""
    vehicle_source = str(vehicle_source_obj).upper()
    if "OWN" in vehicle_source: return vehicle_no
    elif "ATTACHED" in vehicle_source: return f"{vehicle_no}(A)" if vehicle_no else "(A)"
    elif "MARKET" in vehicle_source: return "MKT"
    return ""


@login_required(login_url='login_page')
def trans_invoice_tally_excel(request, customer_id):
    customer = get_object_or_404(CustomerInfo, id=customer_id)
    qs = TransInvoiceInfo.objects.filter(ti_customer=customer, is_woh=True).select_related("ti_customer","ti_trip","ti_consignment","ti_goods")
    if not qs.exists():
        messages.warning(request, "No invoices found in WOH list for this customer.")
        return redirect('trans_invoice_list')
    wb = Workbook()
    ws = wb.active
    ws.title = "Tally Export"
    headers = [
        "Date", "Sundry Debtors", "State", "Pincode", "Voucher No.", "Primary Cost Category", "Customer", "Job No.", "Vehicle Number",
        "Transportation Charges", "Toll Charges", "Parking Charges", "Loading Charges", "Unloading Charges", "Halting Charges",
        "Docket Charges", "Weighment Charges", "Transportation Handling Charges", "Total"
    ]
    ws.append(headers)
    ws.column_dimensions["A"].width = 15
    for col in "BCDE": ws.column_dimensions[col].width = 25
    def safe(val): return val if val is not None else ""
    for obj in qs:
        trip = obj.ti_trip
        cons = obj.ti_consignment
        
        # Calculate total from TransInvoiceInfo charges (not trip charges)
        total_val = (
            (obj.ti_transportation_charges or 0) + (obj.ti_toll_charges or 0) + (obj.ti_parking_charges or 0) +
            (obj.ti_loading_charges or 0) + (obj.ti_unloading_charges or 0) + (obj.ti_halting_charges or 0) +
            (obj.ti_docket_charges or 0) + (obj.ti_weighment_charges or 0) + (obj.ti_handling_charges or 0) +
            (obj.ti_cancellation_charges or 0)
        )
        
        # Format date as dd/mm/yyyy
        formatted_date = obj.ti_inv_date.strftime('%d/%m/%Y') if obj.ti_inv_date else ""
        
        ws.append([
            formatted_date,
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
            safe(obj.ti_handling_charges or 0), 
            safe(total_val)
        ])
    from io import BytesIO
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="Tally_Export_{customer.cu_nameshort or customer.id}.xlsx"'
    return response
