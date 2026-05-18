from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
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
from ..sub_models.invoice_document_mod import InvoiceDocumentInfo
from ..sub_models.trip_status_mod import Tripstatusinfo
from django.db.models import F, Sum, Q, Case, When, Value, FloatField
from django.db.models.functions import Coalesce
from ..utils.pdf_utils import merge_pdf_files



# ==================================================
# PDF SYNC HELPER
# ==================================================
def _sync_trans_invoice_pdf(invoice_no, customer_id):
    """
    Merge PDFs of all trips assigned (is_woh=True) to a given invoice number
    and save the result to the main TransInvoiceInfo record (is_woh=False).
    """
    from ..sub_models.trans_invoice_mod import TransInvoiceInfo
    from ..sub_models.invoice_document_mod import InvoiceDocumentInfo

    master_inv = TransInvoiceInfo.objects.filter(
        ti_inv_no=invoice_no, ti_customer_id=customer_id, is_woh=False
    ).first()
    if not master_inv:
        return

    # Get all detail records
    woh_items = TransInvoiceInfo.objects.filter(
        ti_inv_no=invoice_no, ti_customer_id=customer_id, is_woh=True
    ).exclude(ti_trip_id__isnull=True).select_related('ti_trip')
    
    trip_numbers = [item.ti_trip.tr_tripnumber for item in woh_items if item.ti_trip and item.ti_trip.tr_tripnumber]
    
    # Get individual trip PDFs (already merged in Invoice Document module)
    trip_docs = InvoiceDocumentInfo.objects.filter(id_tripnumber__in=trip_numbers)
    pdf_fields = [doc.id_merged_pdf for doc in trip_docs if doc.id_merged_pdf]
    
    if pdf_fields:
        success, pdf_file = merge_pdf_files(pdf_fields, f"invoice_{invoice_no}.pdf")
        if success:
            master_inv.ti_merged_pdf.save(pdf_file.name, pdf_file, save=True)
    else:
        # If no trip PDFs exist, clear the master PDF
        if master_inv.ti_merged_pdf:
            master_inv.ti_merged_pdf = None
            master_inv.save()


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
            
            # ==================================================
            # CUSTOMER DETAILS
            # ==================================================
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
                    messages.error(request, "Invoice number already exist")
                else:
                    # assign stripped value and save
                    invoice.ti_inv_no = inv_no
                    invoice.save()
                    saved = True
                    # Trigger PDF merge
                    _sync_trans_invoice_pdf(invoice.ti_inv_no, invoice.ti_customer.id)
            else:
                # No invoice number provided; save as before
                invoice.save()
                saved = True
                if invoice.ti_inv_no:
                     _sync_trans_invoice_pdf(invoice.ti_inv_no, invoice.ti_customer.id)

        else:
            pass

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
            ti_inv_no=invoice.ti_inv_no
        )
        .exclude(ti_trip_id__isnull=True)
        .annotate(
            trip_total=(
                Coalesce(F('ti_transportation_charges'), Value(0.0)) +
                Coalesce(F('ti_toll_charges'), Value(0.0)) +
                Coalesce(F('ti_parking_charges'), Value(0.0)) +
                Coalesce(F('ti_loading_charges'), Value(0.0)) +
                Coalesce(F('ti_unloading_charges'), Value(0.0)) +
                Coalesce(F('ti_halting_charges'), Value(0.0)) +
                Coalesce(F('ti_weighment_charges'), Value(0.0)) +
                Coalesce(F('ti_handling_charges'), Value(0.0)) +
                Coalesce(F('ti_cancellation_charges'), Value(0.0))
            )
        )
    )

    # ==================================================
    # AGGREGATE CHARGES FROM LIST
    # ==================================================
    totals = invoice_list.aggregate(
        transport=Sum('ti_transportation_charges'),
        toll=Sum('ti_toll_charges'),
        parking=Sum('ti_parking_charges'),
        loading=Sum('ti_loading_charges'),
        unloading=Sum('ti_unloading_charges'),
        halting=Sum('ti_halting_charges'),
        weighment=Sum('ti_weighment_charges'),
        handling=Sum('ti_handling_charges'),
        cancellation=Sum('ti_cancellation_charges'),
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
                transport=Sum('ti_transportation_charges'),
                toll=Sum('ti_toll_charges'),
                parking=Sum('ti_parking_charges'),
                loading=Sum('ti_loading_charges'),
                unloading=Sum('ti_unloading_charges'),
                halting=Sum('ti_halting_charges'),
                weighment=Sum('ti_weighment_charges'),
                handling=Sum('ti_handling_charges'),
                cancellation=Sum('ti_cancellation_charges'),
            )
            
            # Helper to safe get
            def get_val(k): return aggs.get(k) or 0.0

            invoice.ti_transportation_charges = get_val('transport')
            invoice.ti_toll_charges = get_val('toll')
            invoice.ti_parking_charges = get_val('parking')
            invoice.ti_loading_charges = get_val('loading')
            invoice.ti_unloading_charges = get_val('unloading')
            invoice.ti_halting_charges = get_val('halting')
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
            # Trigger PDF merge
            _sync_trans_invoice_pdf(invoice.ti_inv_no, invoice.ti_customer.id)
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
        invoice.ti_weighment_charges = totals['weighment']
        invoice.ti_handling_charges = totals['handling']
        invoice.ti_cancellation_charges = totals['cancellation']

        invoice.ti_total = sum(totals.values())

        form = TransInvoiceForm(instance=invoice)

    context = {
        'total_charges': invoice.ti_total,
        'form': form,
        'first_name': first_name,
        'invoice': invoice,
        'is_edit': True,
        'invoice_list': invoice_list.select_related("ti_customer", "ti_trip", "ti_consignment", "ti_goods").order_by("-id"),
    }

    # Attach individual trip PDF links for display on edit page
    woh_items = context['invoice_list']
    trip_numbers = [item.ti_trip.tr_tripnumber for item in woh_items if item.ti_trip and item.ti_trip.tr_tripnumber]
    pdf_docs = InvoiceDocumentInfo.objects.filter(id_tripnumber__in=trip_numbers)
    pdf_map = {doc.id_tripnumber: doc.id_merged_pdf.url if doc.id_merged_pdf else None for doc in pdf_docs}
    for item in woh_items:
        if item.ti_trip:
            item.combined_pdf_url = pdf_map.get(item.ti_trip.tr_tripnumber)
    
    return render(request, "asset_mgt_app/trans_invoice_Add.html", context)

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
    
    # If this is a master invoice, delete all its associated WOH detail records as well
    if not invoice.is_woh:
        TransInvoiceInfo.objects.filter(
            ti_inv_no=invoice.ti_inv_no,
            ti_customer=invoice.ti_customer,
            is_woh=True
        ).delete()

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
            'pincode': '',
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
        'pincode': customer.cu_pincode or '',
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
                        "ti_transportation_charges": trip.tc_tripcost if trip.tc_tripcost_check else 0,
                        "ti_toll_charges": trip.tc_tollcost if trip.tc_tollcost_check else 0,
                        "ti_parking_charges": trip.tc_parkingcost if trip.tc_parkingcost_check else 0,
                        "ti_loading_charges": trip.tc_loadingcost if trip.tc_loadingcost_check else 0,
                        "ti_unloading_charges": trip.tc_unloadingcost if trip.tc_unloadingcost_check else 0,
                        "ti_halting_charges": trip.tc_haltingcost if trip.tc_haltingcost_check else 0,
                        "ti_weighment_charges": trip.tc_weighmentcost if trip.tc_weighmentcost_check else 0,
                        "ti_handling_charges": (trip.tc_handlingcost if trip.tc_handlingcost_check else 0) + (trip.tc_supervisorcost if trip.tc_supervisorcost_check else 0),
                        "ti_cancellation_charges": trip.tc_cancellation if trip.tc_cancellation_check else 0,
                        "ti_total": (
                                (trip.tc_tripcost if trip.tc_tripcost_check else 0) +
                                (trip.tc_tollcost if trip.tc_tollcost_check else 0) +
                                (trip.tc_parkingcost if trip.tc_parkingcost_check else 0) +
                                (trip.tc_loadingcost if trip.tc_loadingcost_check else 0) +
                                (trip.tc_unloadingcost if trip.tc_unloadingcost_check else 0) +
                                (trip.tc_haltingcost if trip.tc_haltingcost_check else 0) +
                                (trip.tc_weighmentcost if trip.tc_weighmentcost_check else 0) +
                                (trip.tc_handlingcost if trip.tc_handlingcost_check else 0) +
                                (trip.tc_supervisorcost if trip.tc_supervisorcost_check else 0) +
                                (trip.tc_cancellation if trip.tc_cancellation_check else 0)
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
                    handling=Coalesce(Sum('ti_trip__tc_handlingcost'), Value(0.0)) + Coalesce(Sum('ti_trip__tc_supervisorcost'), Value(0.0)),
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
                    master_inv.ti_weighment_charges +
                    master_inv.ti_handling_charges +
                    master_inv.ti_cancellation_charges
                )
                master_inv.save()
                # Trigger PDF merge
                _sync_trans_invoice_pdf(manual_inv_no, customer.id)

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
        current_woh_trip_ids = list(
            TransInvoiceInfo.objects
            .filter(ti_customer_id=customer_id, ti_inv_no=inv_no_filter)
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
            trip_total=(
                Coalesce(F('tc_tripcost'), Value(0.0)) +
                Coalesce(F('tc_tollcost'), Value(0.0)) +
                Coalesce(F('tc_parkingcost'), Value(0.0)) +
                Coalesce(F('tc_loadingcost'), Value(0.0)) +
                Coalesce(F('tc_unloadingcost'), Value(0.0)) +
                Coalesce(F('tc_haltingcost'), Value(0.0)) +
                Coalesce(F('tc_weighmentcost'), Value(0.0)) +
                Coalesce(F('tc_handlingcost'), Value(0.0)) +
                Coalesce(F('tc_supervisorcost'), Value(0.0)) +
                Coalesce(F('tc_betacost'), Value(0.0)) +
                Coalesce(F('tc_total_halting_cost'), Value(0.0)) +
                Coalesce(F('tc_cancellation'), Value(0.0))
            )
        )
        .order_by('-tr_created_at')
    )

    # Attach PDF links to Current Invoice trips (Top Table)
    curr_trip_numbers = [t.tr_tripnumber for t in trans_invoice_list if t.tr_tripnumber]
    curr_pdf_docs = InvoiceDocumentInfo.objects.filter(id_tripnumber__in=curr_trip_numbers)
    curr_pdf_map = {doc.id_tripnumber: doc.id_merged_pdf.url if doc.id_merged_pdf else None for doc in curr_pdf_docs}
    for trip in trans_invoice_list:
        trip.combined_pdf_url = curr_pdf_map.get(trip.tr_tripnumber)
    invoice_list_master = (
        TripdetailInfo.objects
        .filter(
            tr_enquirynumber__en_customername_id=customer_id,
            tc_financestatus__in=Tripstatusinfo.objects.filter(Q(id=9) | Q(status='Ready for Invoice'))
        )
        .exclude(tr_consignmentnumber__co_consignmentnumber__isnull=True)
        .exclude(tr_consignmentnumber__co_consignmentnumber='')
        .exclude(id__in=all_assigned_trip_ids)
        .select_related('tr_enquirynumber','tr_consignmentnumber','tr_vehicletype','tr_vehiclesource')
        .annotate(
            trip_total=(
                Coalesce(F('tc_tripcost'), Value(0.0)) +
                Coalesce(F('tc_tollcost'), Value(0.0)) +
                Coalesce(F('tc_parkingcost'), Value(0.0)) +
                Coalesce(F('tc_loadingcost'), Value(0.0)) +
                Coalesce(F('tc_unloadingcost'), Value(0.0)) +
                Coalesce(F('tc_haltingcost'), Value(0.0)) +
                Coalesce(F('tc_weighmentcost'), Value(0.0)) +
                Coalesce(F('tc_handlingcost'), Value(0.0)) +
                Coalesce(F('tc_supervisorcost'), Value(0.0)) +
                Coalesce(F('tc_betacost'), Value(0.0)) +
                Coalesce(F('tc_total_halting_cost'), Value(0.0)) +
                Coalesce(F('tc_cancellation'), Value(0.0))
            )
        )
        .order_by('-tr_created_at')
    )

    # Attach PDF links to master list trips
    master_trip_numbers = [t.tr_tripnumber for t in invoice_list_master if t.tr_tripnumber]
    invoice_docs = InvoiceDocumentInfo.objects.filter(id_tripnumber__in=master_trip_numbers)
    pdf_map = {doc.id_tripnumber: doc.id_merged_pdf.url if doc.id_merged_pdf else None for doc in invoice_docs}
    for trip in invoice_list_master:
        trip.combined_pdf_url = pdf_map.get(trip.tr_tripnumber)

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

@csrf_exempt
@login_required(login_url='login_page')
def trans_invoice_remove_woh(request):
    trip_ids = request.POST.getlist('invoice_list[]') or request.GET.getlist('invoice_list[]')

    # -------------------------------------------------------
    # 1. Handle DETAIL records (is_woh=True) — delete them
    # -------------------------------------------------------
    woh_items = TransInvoiceInfo.objects.filter(ti_trip_id__in=trip_ids, is_woh=True)
    affected_pairs = list(woh_items.values('ti_inv_no', 'ti_customer_id').distinct())
    woh_items.delete()

    # -------------------------------------------------------
    # 2. Handle MASTER records (is_woh=False) that still have
    #    a trip attached (legacy from old auto-attach logic).
    #    Clear the trip link and zero out the charges.
    # -------------------------------------------------------
    master_with_trip = TransInvoiceInfo.objects.filter(
        ti_trip_id__in=trip_ids, is_woh=False
    )
    for master in master_with_trip:
        pair = {'ti_inv_no': master.ti_inv_no, 'ti_customer_id': master.ti_customer_id}
        if pair not in affected_pairs:
            affected_pairs.append(pair)
        master.ti_trip = None
        master.ti_consignment = None
        master.ti_goods = None
        master.ti_department = ""
        master.ti_transportation_charges = 0
        master.ti_toll_charges = 0
        master.ti_parking_charges = 0
        master.ti_loading_charges = 0
        master.ti_unloading_charges = 0
        master.ti_halting_charges = 0
        master.ti_weighment_charges = 0
        master.ti_handling_charges = 0
        master.ti_cancellation_charges = 0
        master.ti_total = 0
        master.save()

    # -------------------------------------------------------
    # 3. Recalculate totals for all affected master invoices
    # -------------------------------------------------------
    for pair in affected_pairs:
        inv_no = pair['ti_inv_no']
        cid = pair['ti_customer_id']
        master_inv = TransInvoiceInfo.objects.filter(ti_inv_no=inv_no, ti_customer_id=cid, is_woh=False).first()
        if master_inv:
            woh_remaining = TransInvoiceInfo.objects.filter(ti_inv_no=inv_no, ti_customer_id=cid, is_woh=True)
            aggs = woh_remaining.aggregate(
                transport=Sum('ti_transportation_charges'),
                toll=Sum('ti_toll_charges'),
                parking=Sum('ti_parking_charges'),
                loading=Sum('ti_loading_charges'),
                unloading=Sum('ti_unloading_charges'),
                halting=Sum('ti_halting_charges'),
                weighment=Sum('ti_weighment_charges'),
                handling=Sum('ti_handling_charges'),
                cancellation=Sum('ti_cancellation_charges'),
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
                master_inv.ti_weighment_charges +
                master_inv.ti_handling_charges +
                master_inv.ti_cancellation_charges
            )
            master_inv.save()
            _sync_trans_invoice_pdf(inv_no, cid)

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
        # Use charges directly from TransInvoiceInfo object (obj)
        trip = obj.ti_trip
        goods = obj.ti_goods

        row = [
            safe(obj.ti_trip.tr_enquirynumber.en_pickupdatetime.strftime('%d/%m/%Y') if obj.ti_trip and obj.ti_trip.tr_enquirynumber and obj.ti_trip.tr_enquirynumber.en_pickupdatetime else ""),
            safe(str(obj.ti_consignment.co_consignmentnumber) if obj.ti_consignment else ""),
            safe(str(obj.ti_trip.tr_departedlocation) if obj.ti_trip else ""),
            safe(str(obj.ti_trip.tr_reportedlocation) if obj.ti_trip else ""),
            safe(obj.ti_department),
            safe(str(obj.ti_trip.tr_vehiclenumber) if obj.ti_trip else ""),
            safe(str(obj.ti_trip.tr_vehicletype) if obj.ti_trip else ""),
            safe(obj.ti_trip.tr_departeddate_pickup.strftime('%d/%m/%Y %H:%M') if obj.ti_trip and obj.ti_trip.tr_departeddate_pickup else ""),
            safe(obj.ti_trip.tr_departeddate.strftime('%d/%m/%Y %H:%M') if obj.ti_trip and obj.ti_trip.tr_departeddate else ""),
            safe(obj.ti_trip.tr_reporteddate.strftime('%d/%m/%Y %H:%M') if obj.ti_trip and obj.ti_trip.tr_reporteddate else ""),
            safe(obj.ti_trip.tr_reporteddate_pickup.strftime('%d/%m/%Y %H:%M') if obj.ti_trip and obj.ti_trip.tr_reporteddate_pickup else ""),
            safe(str(obj.ti_goods.cg_consignee) if obj.ti_goods else ""),
            safe(str(obj.ti_consignment.co_cusrefnum) if obj.ti_consignment else ""),
            safe(str(obj.ti_goods.cg_hawbno) if obj.ti_goods else ""),
            safe(str(obj.ti_goods.cg_qty) if obj.ti_goods else ""),
            safe(str(obj.ti_goods.cg_weight) if obj.ti_goods else ""),
            safe(obj.ti_transportation_charges or 0),
            safe(obj.ti_toll_charges or 0),
            safe(obj.ti_parking_charges or 0),
            safe(obj.ti_loading_charges or 0),
            safe(obj.ti_unloading_charges or 0),
            safe(obj.ti_halting_charges or 0),
            safe(obj.ti_weighment_charges or 0),
            safe(obj.ti_handling_charges or 0),
            safe(obj.ti_cancellation_charges or 0),
            safe(obj.ti_total or 0),
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
    response["Content-Disposition"] = f'attachment; filename="Excel_Export_{customer.cu_nameshort or customer.id}.xlsx"'
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
def trans_invoice_tally_excel(request, invoice_no):
    first_record = TransInvoiceInfo.objects.filter(ti_inv_no=invoice_no).first()
    if not first_record:
        messages.warning(request, "Invoice not found.")
        return redirect('trans_invoice_list')
    customer = first_record.ti_customer
    qs = TransInvoiceInfo.objects.filter(ti_customer=customer, ti_inv_no=invoice_no, is_woh=True).select_related("ti_customer","ti_trip","ti_consignment","ti_goods")
    if not qs.exists():
        messages.warning(request, "No trips found in WOH list for this invoice.")
        return redirect('trans_invoice_list')
    wb = Workbook()
    ws = wb.active
    ws.title = "Tally Export"
    headers = [
        "Date", "Sundry Debtors", "State", "GST No.", "Pincode", "Voucher No.", "Primary Cost Category", "Customer", "Job No.", "Vehicle Number",
        "Transportation Charges", "Toll Charges", "Parking Charges", "Loading Charges", "Unloading Charges", "Halting Charges",
        "Weighment Charges", "Transportation Handling Charges", "Total"
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
            (obj.ti_weighment_charges or 0) + (obj.ti_handling_charges or 0) +
            (obj.ti_cancellation_charges or 0)
        )
        
        # Format date as dd/mm/yyyy
        formatted_date = obj.ti_inv_date.strftime('%d/%m/%Y') if obj.ti_inv_date else ""
        
        ws.append([
            formatted_date,
            safe(obj.ti_customer_short_name), 
            safe(obj.ti_state), 
            safe(obj.ti_gst_in),
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
