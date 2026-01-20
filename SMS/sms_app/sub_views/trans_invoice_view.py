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



from django.db.models import Sum
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
        docket=Sum('ti_docket_charges'),
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


@login_required(login_url='login_page')
def trans_invoice_list_woh(request, customer_id):
    first_name = request.session.get('first_name')

    # ==========================
    # HANDLE ADD FROM MASTER
    # ==========================
    if request.method == "POST" and request.POST.get("action") == "add":

        ids = request.POST.getlist('invoice_list[]')

        if ids:
            TransInvoiceInfo.objects.filter(
                id__in=ids,
                is_woh=False,
                ti_customer_id=customer_id
            ).update(is_woh=True)

        return JsonResponse({'status': 'success'})

    # ==========================
    # NORMAL PAGE LOAD
    # ==========================
    trans_invoice_list = (
        TransInvoiceInfo.objects
        .filter(is_woh=True, ti_customer_id=customer_id)
        .select_related(
            'ti_customer',
            'ti_trip',
            'ti_consignment',
            'ti_goods',
            'ti_trip__tr_enquirynumber',
        )
        .order_by('-id')
    )
    # ==================================================
    # ATTACH TALLY VEHICLE NO (STEP 1)
    # ==================================================
    for inv in trans_invoice_list:
        inv.tally_vehicle_no = get_tally_vehicle_no(inv)

    invoice_list_master = (
        TransInvoiceInfo.objects
        .filter(is_woh=False, ti_customer_id=customer_id)
        .select_related(
            'ti_customer',
            'ti_trip',
            'ti_consignment',
            'ti_goods',
            'ti_trip__tr_enquirynumber',
        )
        .order_by('-id')
    )

    customer = get_object_or_404(CustomerInfo, id=customer_id)

    departments = (
        TransInvoiceInfo.objects
        .filter(ti_department__isnull=False)
        .exclude(ti_department="")
        .values_list('ti_department', flat=True)
        .distinct()
        .order_by('ti_department')
    )

    return render(
        request,
        "asset_mgt_app/trans_invoice_list_WOH.html",
        {
            "trans_invoice_list": trans_invoice_list,
            "invoice_list_master": invoice_list_master,
            "departments": departments,
            "customer": customer,
            "first_name": first_name,
        }
    )

@login_required(login_url='login_page')
def trans_invoice_remove_woh(request):
    ids = request.GET.getlist('invoice_list[]')

    TransInvoiceInfo.objects.filter(
        id__in=ids
    ).update(is_woh=False)

    messages.success(request, "Selected Transport Invoices removed from the list")
    return JsonResponse({'status': 'success'})


@login_required(login_url='login_page')
def trans_invoice_add_woh(request):
    ids = request.POST.getlist('ids[]')

    TransInvoiceInfo.objects.filter(
        id__in=ids
    ).update(is_woh=True)

    messages.success(request, "Selected Transport Invoices added to the list")
    return JsonResponse({'status': 'success'})

def trans_invoice_excel(request, invoice_no):

    # 🔹 FETCH DATA (USE FK PROPERLY)
    qs = (
        TransInvoiceInfo.objects
        .filter(ti_inv_no=invoice_no, is_woh=True)
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

        ws.append([
            safe(obj.ti_inv_date),
            safe(str(obj.ti_customer) if obj.ti_customer else ""),  # FK
            safe(obj.ti_gst_in),
            safe(obj.ti_state),
            safe(obj.ti_pincode),
            safe(obj.ti_inv_no),

            safe(obj.ti_branch),
            safe(str(trip.tr_vehiclesource) if trip and getattr(trip, 'tr_vehiclesource', None) else ""),  # FK
            safe(str(obj.ti_customer_short_name) if getattr(obj, 'ti_customer_short_name', None) else ""),  # FK
            safe(get_tally_vehicle_no(obj)),            # FK
            safe(str(trip.tr_departeddate) if trip and getattr(trip, 'tr_departeddate', None) else ""),  # FK

            safe(str(cons.co_consignmentnumber) if cons and getattr(cons, 'co_consignmentnumber', None) else ""),  # FK
            safe(str(trip.tr_departedlocation) if trip and getattr(trip, 'tr_departedlocation', None) else ""),  # FK
            safe(str(trip.tr_reportedlocation) if trip and getattr(trip, 'tr_reportedlocation', None) else ""),  # FK
            safe(obj.ti_department),

            safe(str(trip.tr_vehiclenumber) if trip and getattr(trip, 'tr_vehiclenumber', None) else ""),  # FK
            safe(str(trip.tr_vehicletype) if trip and getattr(trip, 'tr_vehicletype', None) else ""),  # FK

            # 🔴 THESE FOUR ARE FK → FIXED
            safe(str(trip.tr_departeddate_pickup) if trip and getattr(trip, 'tr_departeddate_pickup', None) else ""),
            safe(str(trip.tr_dock_out_time) if trip and getattr(trip, 'tr_dock_out_time', None) else ""),
            safe(str(trip.tr_reporteddate) if trip and getattr(trip, 'tr_reporteddate', None) else ""),
            safe(str(trip.tr_departeddate_delivery) if trip and getattr(trip, 'tr_departeddate_delivery', None) else ""),

            safe(str(goods.cg_consignee) if goods and getattr(goods, 'cg_consignee', None) else ""),  # FK
            safe(str(cons.co_cusrefnum) if cons and getattr(cons, 'co_cusrefnum', None) else ""),  # FK
            safe(str(goods.cg_hawbno) if goods and getattr(goods, 'cg_hawbno', None) else ""),  # FK

            # 🔴 THESE TWO ARE FK → FIXED
            safe(str(goods.cg_qty) if goods and getattr(goods, 'cg_qty', None) else ""),
            safe(str(goods.cg_weight) if goods and getattr(goods, 'cg_weight', None) else ""),

            safe(obj.ti_transportation_charges),
            safe(obj.ti_toll_charges),
            safe(obj.ti_parking_charges),
            safe(obj.ti_loading_charges),
            safe(obj.ti_unloading_charges),
            safe(obj.ti_halting_charges),
            safe(obj.ti_docket_charges),
            safe(obj.ti_weighment_charges),
            safe(obj.ti_handling_charges),
            safe(obj.ti_cancellation_charges),

            safe(obj.ti_total)
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
