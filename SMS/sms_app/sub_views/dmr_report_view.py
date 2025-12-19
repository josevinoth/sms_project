import calendar
from datetime import datetime, date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl import Workbook

from ..models import TripdetailInfo, EnquirynoteInfo, ConsignmentdetailInfo, MyUser
from .send_department_email import send_department_email
from ..sub_forms.dmr_report_form import DmrForm
from ..sub_models.consignmentgoods_mod import ConsignmentgoodsInfo
from ..sub_models.customer_mod import CustomerInfo
from ..sub_models.vehicle_allotment_mod import Vehicle_allotmentInfo


@login_required(login_url='login_page')
def trip_report(request):
    first_name = request.session.get('first_name')
    form = DmrForm(request.POST or None)

    # -------------------------
    # GET FILTER VALUES
    # -------------------------
    customer_id = request.POST.get('dmr_customer')
    dept_id = request.POST.get('customer_department')   # Add this field in your form
    selected_month = request.POST.get('month')
    selected_year = request.POST.get('year')

    # -------------------------
    # BASE QUERY
    # -------------------------
    trips = TripdetailInfo.objects.all().order_by('-tr_tripnumber')

    # -------------------------
    # FILTER BY CUSTOMER
    # -------------------------
    if customer_id:
        trips = trips.filter(tr_enquirynumber__en_customername_id=customer_id)

    # -------------------------
    # FILTER BY DEPARTMENT
    # -------------------------
    if dept_id:
        trips = trips.filter(tr_enquirynumber__en_customerdepartment_id=dept_id)

    # -------------------------
    # FILTER BY MONTH/YEAR
    # -------------------------
    if selected_month and selected_year:
        selected_month = int(selected_month)
        selected_year = int(selected_year)

        first_day = date(selected_year, selected_month, 1)
        last_day = date(selected_year, selected_month, calendar.monthrange(selected_year, selected_month)[1])

        trips = trips.filter(
            tr_departeddate__date__gte=first_day,
            tr_departeddate__date__lte=last_day
        )

    # -------------------------
    # ATTACH CONSIGNER + REF NO
    # -------------------------
    for trip in trips:
        # Consigner name
        cons_name = ''
        cg = ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber=trip.tr_consignmentnumber).first()
        if cg and cg.cg_consigner:
            cons_name = str(cg.cg_consigner)
        trip.consigner_name = cons_name

        # Reference number
        ref = ''
        cd = ConsignmentdetailInfo.objects.filter(co_consignmentnumber=trip.tr_consignmentnumber).first()
        if cd:
            ref = cd.co_cusrefnum
        trip.co_cusrefnum = ref

    # -------------------------
    # PAGINATION
    # -------------------------
    from_loc = request.POST.get('from_location')
    to_loc = request.POST.get('to_location')

    # Filter by FROM location
    if from_loc:
        trips = trips.filter(tr_enquirynumber__en_fromlocaion_id=from_loc)

    # Filter by TO location
    if to_loc:
        trips = trips.filter(tr_enquirynumber__en_tolocation_id=to_loc)

    # Now paginate AFTER all filters
    paginator = Paginator(trips, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    current_month = datetime.now().month

    # -------------------------
    # YEAR LIST FOR DROPDOWN
    # -------------------------
    current_year = datetime.now().year
    years_list = list(range(current_year - 5, current_year + 1))
    # -------------------------
    # CONTEXT
    # -------------------------
    context = {
        'first_name': first_name,
        'form': form,
        'page_obj': page_obj,
        'customer_id': customer_id or '',
        'dept_id': dept_id or '',
        'selected_month': int(selected_month) if selected_month else current_month,
        'selected_year': int(selected_year) if selected_year else current_year,
        'years': range(current_year - 5, current_year + 1),
        'from_location': int(from_loc) if from_loc else '',
        'to_location': int(to_loc) if to_loc else '',

    }

    return render(request, "asset_mgt_app/dmr_report.html", context)


DMR_TEMPLATES = {
    "Air Export": [
        "S.NO", "DEPARTMENT NAME", "PICKUP DATE", "SHIPPER NAME", "PICKUP LOCATION",
        "CONSIGNEE NAME", "DELIVERY LOCATION", "CS NAME", "PLANNING RECEIVED DATE",
        "PLANNING RECEIVED TIME", "VEHICLE PLACED TIME", "HAWB #", "BOE NUMBER # / EWAYBILL #",
        "REFERENCE NUMBER ( MASTER INVOICE # / FILE # )", "TRUCK NO", "TRUCK TYPE", "VENDOR",
        "CHA NAME", "LLR NO", "DRIVER NAME", "DRIVER MOBILE", "DRIVER DL #",
        "PICKUP POINT IN DATE", "PICKUP POINT IN TIME", "PICKUP POINT OUT DATE",
        "PICKUP POINT OUT TIME", "NO OF PIECES", "ACTUAL WEIGHT", "CHARGEABLE WEIGHT",
        "CBM", "SHIPPER SEAL #", "UNLOADING POINT IN DATE", "UNLOADING POINT IN TIME",
        "UNLOADING POINT", "UNLOADING POINT OUT DATE", "UNLOADING POINT OUT TIME",
        "NO OF DAYS HALTING", "ADDITIONAL CHARGES", "CANCELLATION CHARGES",
        "HALTING CHARGES", "CHARGES", "WEIGHTMENT CHARGES", "PARKING / UNLOADING CHARGES",
        "TOTAL CHARGES", "REMARKS"
    ],
    "Air Import": [
        "S.NO", "DEPARTMENT NAME", "PICKUP DATE", "SHIPPER NAME", "PICKUP LOCATION",
        "CONSIGNEE NAME", "DELIVERY LOCATION", "CS NAME", "PLANNING RECEIVED DATE",
        "PLANNING RECEIVED TIME", "VEHICLE PLACED TIME", "HAWB #", "BOE NUMBER # / EWAYBILL #",
        "REFERENCE NUMBER ( MASTER INVOICE # / FILE # )", "TRUCK NO", "TRUCK TYPE", "VENDOR",
        "CHA NAME", "LLR NO", "DRIVER NAME", "DRIVER MOBILE", "DRIVER DL #",
        "PICKUP POINT IN DATE", "PICKUP POINT IN TIME", "PICKUP POINT OUT DATE",
        "PICKUP POINT OUT TIME", "NO OF PIECES", "ACTUAL WEIGHT", "CHARGEABLE WEIGHT",
        "CBM", "SHIPPER SEAL #", "UNLOADING POINT IN DATE", "UNLOADING POINT IN TIME",
        "UNLOADING POINT", "UNLOADING POINT OUT DATE", "UNLOADING POINT OUT TIME",
        "NO OF DAYS HALTING", "ADDITIONAL CHARGES", "CANCELLATION CHARGES",
        "HALTING CHARGES", "CHARGES", "WEIGHTMENT CHARGES", "PARKING CHARGES",
        "UNLOADING CHARGES", "TOTAL CHARGES", "REMARKS"
    ],
    "CHB": [
        "S.NO", "JOB NO", "DEPARTMENT NAME", "PICKUP DATE", "SHIPPER NAME", "PICKUP LOCATION",
        "CONSIGNEE NAME", "DELIVERY LOCATION", "CS NAME", "PLANNING RECEIVED DATE",
        "PLANNING RECEIVED TIME", "HAWB #", "BOE NUMBER # / EWAYBILL #",
        "REFERENCE NUMBER ( MASTER INVOICE # / FILE # )", "TRUCK NO", "TRUCK TYPE", "VENDOR",
        "CHA NAME", "LLR NO", "DRIVER NAME", "DRIVER MOBILE", "DRIVER DL #",
        "PICKUP POINT IN DATE", "PICKUP POINT IN TIME", "PICKUP POINT OUT DATE",
        "PICKUP POINT OUT TIME", "NO OF PIECES", "ACTUAL WEIGHT (KGS)",
        "CHARGEABLE WEIGHT", "CAPACITY", "SHIPPER SEAL #", "UNLOADING POINT IN DATE",
        "UNLOADING POINT IN TIME", "UNLOADING POINT", "UNLOADING POINT OUT DATE",
        "UNLOADING POINT OUT TIME", "HALTING STATUS (YES / NO)", "NO OF DAYS HALTING",
        "ADDITIONAL CHARGES", "CANCELLATION CHARGES", "HALTING CHARGES", "CHARGES",
        "PARKING / UNLOADING CHARGES", "TOTAL CHARGES", "REMARKS"
    ],
    "Hub Movement": [
        "S.NO", "OFD DATE", "VENDOR NAME", "VEH NO", "COC NO", "ORGIN", "DESTINATION",
        "CONSIGNOR", "CONSIGNEE NAME", "NO PKG", "WEIGHT", "DELIVERY STATUS", "REMARKS",
        "DELAY&ONTIME", "POD REMARKS", "RETURN BOX"
    ],
    "Order Management": [
        "S.NO", "DEPARTMENT NAME", "PICKUP DATE", "SHIPPER NAME", "PICKUP LOCATION",
        "CONSIGNEE NAME", "DELIVERY LOCATION", "CS NAME", "PLANNING RECEIVED DATE",
        "PLANNING RECEIVED TIME", "VEHICLE PLACED TIME", "HAWB #", "BOE NUMBER # / EWAYBILL #",
        "REFERENCE NUMBER ( MASTER INVOICE # / FILE # )", "TRUCK NO", "TRUCK TYPE", "VENDOR",
        "DRIVER NAME", "DRIVER MOBILE", "DRIVER DL #", "PICKUP POINT IN DATE",
        "PICKUP POINT IN TIME", "PICKUP POINT OUT DATE", "PICKUP POINT OUT TIME",
        "NO OF PIECES", "ACTUAL WEIGHT", "CHARGEABLE WEIGHT", "CBM", "SHIPPER SEAL #",
        "UNLOADING POINT IN DATE", "UNLOADING POINT IN TIME", "UNLOADING POINT",
        "UNLOADING POINT OUT DATE", "UNLOADING POINT OUT TIME", "NO OF DAYS HALTING",
        "ADDITIONAL CHARGES", "CANCELLATION CHARGES", "HALTING CHARGES", "CHARGES",
        "WEIGHTMENT CHARGES", "UNLOADING CHARGES", "TOTAL CHARGES", "REMARKS"
    ],
    "Sea Export": [
        "S.NO", "DEPARTMENT NAME", "PICKUP DATE", "SHIPPER NAME", "PICKUP LOCATION",
        "CONSIGNEE NAME", "DELIVERY LOCATION", "CS NAME", "PLANNING RECEIVED DATE",
        "PLANNING RECEIVED TIME", "VEHICLE PLACED TIME", "HAWB #", "BOE NUMBER # / EWAYBILL #",
        "REFERENCE NUMBER ( MASTER INVOICE # / FILE # )", "TRUCK NO", "TRUCK TYPE", "VENDOR",
        "DRIVER NAME", "DRIVER MOBILE", "DRIVER DL #", "PICKUP POINT IN DATE",
        "PICKUP POINT IN TIME", "PICKUP POINT OUT DATE", "PICKUP POINT OUT TIME",
        "NO OF PIECES", "ACTUAL WEIGHT", "CHARGEABLE WEIGHT", "CBM", "SHIPPER SEAL #",
        "UNLOADING POINT IN DATE", "UNLOADING POINT IN TIME", "UNLOADING POINT",
        "UNLOADING POINT OUT DATE", "UNLOADING POINT OUT TIME", "NO OF DAYS HALTING",
        "ADDITIONAL CHARGES", "CANCELLATION CHARGES", "HALTING CHARGES", "CHARGES",
        "WEIGHTMENT CHARGES", "UNLOADING CHARGES", "TOTAL CHARGES", "REMARKS"
    ],
    "Sea Import": [
        "S.NO", "JOB NO", "DEPARTMENT NAME", "PICKUP DATE", "SHIPPER NAME", "PICKUP LOCATION",
        "CONSIGNEE NAME", "DELIVERY LOCATION", "CS NAME", "PLANNING RECEIVED DATE",
        "PLANNING RECEIVED TIME", "HAWB #", "BOE NUMBER # / EWAYBILL #",
        "REFERENCE NUMBER ( MASTER INVOICE # / FILE # )", "TRUCK NO", "TRUCK TYPE", "VENDOR",
        "CHA NAME", "LLR NO", "DRIVER NAME", "DRIVER MOBILE", "DRIVER DL #",
        "PICKUP POINT IN DATE", "PICKUP POINT IN TIME", "PICKUP POINT OUT DATE",
        "PICKUP POINT OUT TIME", "NO OF PIECES", "ACTUAL WEIGHT (KGS)", "CHARGEABLE WEIGHT",
        "CAPACITY", "SHIPPER SEAL #", "UNLOADING POINT IN DATE", "UNLOADING POINT IN TIME",
        "UNLOADING POINT", "UNLOADING POINT OUT DATE", "UNLOADING POINT OUT TIME",
        "HALTING STATUS (YES / NO)", "NO OF DAYS HALTING", "ADDITIONAL CHARGES",
        "CANCELLATION CHARGES", "HALTING CHARGES", "CHARGES", "PARKING / UNLOADING CHARGES",
        "TOTAL CHARGES", "REMARKS"
    ],
    "TCS Local": [
        "SO NO", "JOB NO", "DEPARTMENT NAME", "PICKUP DATE", "SHIPPER NAME", "PICKUP LOCATION",
        "DELIVERY LOCATION", "BOE NUMBER # / EWAYBILL #", "REFERENCE NUMBER ( MASTER INVOICE # / FILE # )",
        "TRUCK NO", "TRUCK TYPE", "VENDOR", "DRIVER MOBILE", "PICKUP POINT IN DATE",
        "PICKUP POINT OUT DATE", "NO OF PIECES", "ACTUAL WEIGHT", "CHARGEABLE WEIGHT", "CBM",
        "SHIPPER SEAL #", "UNLOADING POINT IN DATE", "UNLOADING POINT OUT DATE", "NO OF DAYS HALTING",
        "ADDITIONAL CHARGES", "CANCELLATION CHARGES", "HALTING CHARGES", "CHARGES", "PARKING CHARGES",
        "UNLOADING CHARGES & LASHING CHARGES", "TOTAL CHARGES", "REMARKS"
    ],
    "TCS Outstation": [
        "S.NO", "JOB NO", "DEPARTMENT NAME", "PICKUP DATE", "SHIPPER NAME", "PICKUP LOCATION",
        "DELIVERY LOCATION", "BOE NUMBER # / EWAYBILL #", "REFERENCE NUMBER ( MASTER INVOICE # / FILE # )",
        "TRUCK NO", "TRUCK TYPE", "VENDOR", "DRIVER MOBILE", "PICKUP POINT IN DATE", "PICKUP POINT OUT DATE",
        "NO OF PIECES", "ACTUAL WEIGHT", "CHARGEABLE WEIGHT", "CBM", "SHIPPER SEAL #",
        "UNLOADING POINT IN DATE", "UNLOADING POINT OUT DATE", "NO OF DAYS HALTING", "ADDITIONAL CHARGES",
        "CANCELLATION CHARGES", "HALTING CHARGES", "CHARGES", "PARKING CHARGES",
        "UNLOADING CHARGES AND PARKING CHARGES", "TOTAL CHARGES", "REMARKS"
    ],
    "TCS Reefer": [
        "S.NO", "JOB NO", "DEPARTMENT NAME", "PICKUP DATE", "SHIPPER NAME", "PICKUP LOCATION",
        "DELIVERY LOCATION", "BOE NUMBER # / EWAYBILL #", "REFERENCE NUMBER ( MASTER INVOICE # / FILE # )",
        "TRUCK NO", "TRUCK TYPE", "VENDOR", "DRIVER MOBILE", "PICKUP POINT IN DATE", "PICKUP POINT OUT DATE",
        "NO OF PIECES", "ACTUAL WEIGHT", "CHARGEABLE WEIGHT", "CBM", "SHIPPER SEAL #",
        "UNLOADING POINT IN DATE", "UNLOADING POINT OUT DATE", "NO OF DAYS HALTING", "ADDITIONAL CHARGES",
        "CANCELLATION CHARGES", "HALTING CHARGES", "CHARGES", "PARKING CHARGES",
        "UNLOADING CHARGES AND PARKING CHARGES", "TOTAL CHARGES", "REMARKS"
    ],
    "WH TO AIRPORT": [
        "S.NO", "DEPT", "DATE", "SHIPPER NAME", "FROM", "TO", "CUTOMER SERVICE", "HBL #",
        "TRUCK NO", "TRUCK TYPE", "DRIVER MOBILE", "IN DATE", "IN TIME", "OUT DATE",
        "OUT TIME", "NO OF PIECES", "CARGO WEIGHT", "AIRPORT/BVM GATE IN DATE",
        "AIRPORT/BVM   GATE IN TIME", "UNLOADING  POINT", "IN TIME @ UNLOADING POINT",
        "UNLOADING  TIME", "DLV OUT  DATE", "DLV OUT TIME", "HALTING STATUS   (YES / NO)",
        "NO OF DAYS  HALTING", "ADDITIONAL CHARGES", "CANCELLING CHARGES", "HALTING CHARGES",
        "CHARGES", "WEIGHMENT PASS", "PARKING CHARGES", "TOTAL CHARGES", "REMARKS"
    ],
    "APMT": [
        "MONTH", "REQUESTOR", "SHIPPER", "TRANSPORTER", "CONTAINER SIZE", "BOOKING NO", "FROM",
        "TO", "BVM JOB", "VEHICLE NO.", "DRIVER NO.", "PLACEMENT & VEHICLE PLACED DATE",
        "VEHICLE PLACED TIME", "VEHICLE RELEASED DATE", "VEHICLE RELEASED TIME", "CFS REACHED DATE",
        "CFS REACHED TIME", "UNLOADING CHARGES", "HALTING CHARGES", "TRIP COST", "TOTAL COST",
        "LR NO", "COMMENTS", "DETENTION DAYS", "POD STATUS"
    ],
    "CEVA Air Import": [
        "DATE", "CONSIGNEE NAME", "HBL NUMBER", "BOE NO", "PKGS", "GROSS WEIGHT", "FROM",
        "DELIVERY PLACE", "CEVA JOB NO", "TRUCK NO", "TRUCK TYPE", "DELIVERY DATE",
        "HALTING CHARGES", "UNLOADING CHARGES", "AIRPORT PASS", "TRIP COST", "TOTAL COST",
        "BVM JOB NO", "POD STATUS"
    ],
    "CEVA Export": [
        "DATE", "BVM JOB NO", "CONSIGNEE NAME", "HBL NO", "PKGS", "G WEIGHT", "CEVA JOB NO",
        "FROM", "DELIVERY PLACE", "TRUCK NO", "TRUCK TYPE", "REACHED CFS", "DELIVERY DATE",
        "UNLOADING CHARGES", "TRIP COST", "TOTAL COST", "POD STATUS"
    ],
    "DHL SEA IMPORT": [
        "DATE", "CONSIGNEE NAME", "HBL NO", "BE #", "PKGS", "G WEIGHT", "CBM", "FROM",
        "DELIVERY PLACE", "TRUCK NO", "TRUCK TYPE", "REACHED PLANT", "DELIVERY DATE",
        "HBL WISE SPLIT COST", "LOADING/UNLOADING CHARGES", "HALTING CHARGES",
        "TRANSPORT COST", "TOTAL COST", "VENDOR CODE", "REMARK", "BVM JOB NO", "POD STATUS"
    ],
    "DSV": [
        "DATE", "BVM JOB NO", "BVM LR NO", "USER NAME", "SHIPPER NAME", "HBL NO/REFERENCE NO",
        "TRANSPORT BILL TO", "VEHICLE NO", "VEHICLE TYPE", "DRIVER NAME", "DRIVER NAMBER", "FROM",
        "TO", "DIVISION", "SUM OF PIECES", "WEIGHT", "HALTING CHARGES", "LOADING CHARGES",
        "UNLOADING CHARGES", "WEIGHMENT CHARGES", "AAI S.NO.", "AAI CHARGES", "TRIP COST",
        "TOTAL COST", "E-WAY BILL", "BVM INVOICE", "SEEL NO", "REMARK", "POD", "C NOTE"
    ],
    "DSV DD REPORT": [
        "DATE", "TRIP SHEET NO", "VEHICLE NO", "STARTING TIME", "CLOSING TIME", "STARTING KM",
        "CLOSING KM", "USED KM", "STARTING PLACE", "CLOSING PLACE", "HBL NO/REFERENCE NO",
        "DETENTION HOURS", "RATE PER KM", "TRIP CHARGE", "PARKING CHARGES", "HALTING CHARGES",
        "DETENTION CHARGES", "TOTAL COST"
    ]
}

# default headers (your original DMR view used these)
DEFAULT_HEADERS = [
    "SR. NO.", "TRIP DATE", "CONSIGNMENT NOTE NO", "CUSTOMER NAME", "CUSTOMER DEPT",
    "SHIPPER", "FROM", "TO", "VEH NO", "VEH TYPE", "TRIPCOST", "AAI CHARGES",
    "UNLOADING CHARGES", "LOADING CHARGES", "HALTING CHARGE", "HANDLING CHARGES",
    "SUPERVISOR CHARGES", "TOTAL CHARGES", "REFERENCE # (JOB ID/HAWB)",
    "VEH REPORTED KM @ LOADING POINT", "VEH REPORTED TIME @ LOADING POINT",
    "LOADING DATE", "LOADING TIME", "VEH REPORTED KM @ UNLOADING POINT",
    "VEH REPORTED TIME @ UNLOADING POINT", "UNLOADING DATE", "UNLOADING TIME",
    "NO OF HALTING DAYS"
]

# --------------------------
# Helper: safe getter
# --------------------------
def safe(value):
    if value is None:
        return ""
    return str(value)



def get_consignment_objects(trip):
    """Return consignmentdetail and consignmentgoods related to trip.consignmentnumber"""
    cons_detail = None
    cons_goods = None
    try:
        if getattr(trip, "tr_consignmentnumber", None):
            cons_detail = ConsignmentdetailInfo.objects.filter(
                co_consignmentnumber=trip.tr_consignmentnumber
            ).first()
            cons_goods = ConsignmentgoodsInfo.objects.filter(
                cg_consignmentnumber=trip.tr_consignmentnumber
            ).first()
    except Exception:
        cons_detail = None
        cons_goods = None
    return cons_detail, cons_goods


# --------------------------
# Main view: send DMR by email
# --------------------------
@login_required(login_url='login_page')
def trip_send_email(request):
    if request.method != 'POST':
        messages.error(request, "Invalid request.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # -------------------
    # READ FILTER INPUTS
    # -------------------
    customer_id = request.POST.get('customer_id')
    dept_id = request.POST.get('customer_department') or request.POST.get('dept_id')
    month = request.POST.get('month')
    year = request.POST.get('year')
    from_loc = request.POST.get('from_location')
    to_loc = request.POST.get('to_location')

    recipient = request.POST.get('recipient', "")
    subject = request.POST.get('subject', "")
    message_body = request.POST.get('message', "")

    if not customer_id:
        messages.error(request, "Please select a customer.")
        return redirect('trip_report')

    if not recipient:
        messages.error(request, "Please enter recipient emails.")
        return redirect('trip_report')

    # Validate customer exists
    try:
        customer_obj = CustomerInfo.objects.get(id=customer_id)
    except CustomerInfo.DoesNotExist:
        messages.error(request, "Customer not found.")
        return redirect('trip_report')

    # -------------------
    # BASE QUERY
    # -------------------
    qs = TripdetailInfo.objects.filter(
        tr_enquirynumber__en_customername_id=customer_id,
        tr_category_id=1
    ).order_by('-tr_tripnumber')

    # Department filter
    if dept_id:
        try:
            qs = qs.filter(tr_enquirynumber__en_customerdepartment_id=int(dept_id))
        except:
            qs = qs.filter(tr_enquirynumber__en_customerdepartment__icontains=str(dept_id))

    # Date filter
    if month and year:
        try:
            m = int(month)
            y = int(year)
            first_day = date(y, m, 1)
            last_day = date(y, m, calendar.monthrange(y, m)[1])

            qs = qs.filter(
                tr_departeddate__date__gte=first_day,
                tr_departeddate__date__lte=last_day
            )
        except:
            pass

    # From / To filter
    if from_loc:
        qs = qs.filter(tr_enquirynumber__en_fromlocaion_id=from_loc)

    if to_loc:
        qs = qs.filter(tr_enquirynumber__en_tolocation_id=to_loc)

    trips = list(qs)

    # ---------------------------
    # SORT TRIPS BY PICKUP DATE ASCENDING
    # ---------------------------
    def pickup_sort_key(t):
        try:
            return t.tr_departeddate or datetime.max
        except:
            return datetime.max

    trips = sorted(trips, key=pickup_sort_key)

    # ---------------------------
    # DETECT TEMPLATE HEADER
    # ---------------------------
    dept_name = None
    if trips:
        try:
            dept_name = str(trips[0].tr_enquirynumber.en_customerdepartment)
        except:
            dept_name = None

    template_key = None
    if dept_name:
        lookup = dept_name.lower()
        for key in DMR_TEMPLATES.keys():
            if key.lower() in lookup or lookup in key.lower():
                template_key = key
                break

    headers = DMR_TEMPLATES.get(template_key, DEFAULT_HEADERS)

    # ---------------------------
    # PREPARE EXCEL WORKBOOK
    # ---------------------------
    wb = Workbook()
    ws = wb.active
    ws.title = "DMR Report"

    header_font = Font(bold=True)
    yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    ws.append(headers)
    for cell in ws[1]:
        cell.font = header_font
        cell.fill = yellow_fill
        cell.border = border
        cell.alignment = center_align

    def safe_str(v):
        return "" if v is None else str(v)

    def safe_num(v):
        try:
            return float(v) if v not in ("", None, "None") else 0
        except:
            return 0

    # ---------------------------
    # BUILD ROWS
    # ---------------------------
    for idx, trip in enumerate(trips, start=1):

        cons_detail = ConsignmentdetailInfo.objects.filter(
            co_consignmentnumber=trip.tr_consignmentnumber
        ).first()

        cons_goods = ConsignmentgoodsInfo.objects.filter(
            cg_consignmentnumber=trip.tr_consignmentnumber
        ).first()

        va = Vehicle_allotmentInfo.objects.filter(
            va_enquirynumber=trip.tr_enquirynumber
        ).first()

        row = []

        for h in headers:
            hh = h.strip().lower()

            # ---------------------------------------------------
            # BASIC FIELDS
            # ---------------------------------------------------
            if "s.no" in hh or hh == "sr. no.":
                row.append(idx)
                continue

            if "department name" in hh:
                row.append(safe_str(trip.tr_enquirynumber.en_customerdepartment))
                continue

            # ---------------------------------------------------
            # PICKUP DATE / TIME / LOCATION  (FIXED)
            # ---------------------------------------------------
            if hh == "pickup date":
                row.append(trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else "")
                continue

            if hh == "pickup location":
                row.append(safe_str(trip.tr_departedlocation))
                continue

            if hh == "pickup point in date":
                row.append(trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else "")
                continue

            if hh == "pickup point in time":
                row.append(trip.tr_departeddate.strftime("%H:%M") if trip.tr_departeddate else "")
                continue

            if hh == "pickup point out date":
                row.append(trip.tr_loading_time.strftime("%d-%m-%Y") if trip.tr_loading_time else "")
                continue

            if hh == "pickup point out time":
                row.append(trip.tr_loading_time.strftime("%H:%M") if trip.tr_loading_time else "")
                continue

            # Correct FROM/TO mapping
            if hh == "from":
                row.append(safe_str(trip.tr_departedlocation))
                continue

            # DELIVERY LOCATION
            if hh in ("delivery location",):
                if cons_goods and getattr(cons_goods, "cg_deliverylocation", None):
                    row.append(safe(cons_goods.cg_deliverylocation))
                else:
                    row.append(safe(trip.tr_enquirynumber.en_tolocation))
                continue

            # PLANNING RECEIVED DATE
            if hh == "planning received date":
                en_date = getattr(trip.tr_enquirynumber, "en_created_at", None)
                row.append(en_date.strftime("%d-%m-%Y") if en_date else "")
                continue

            # PLANNING RECEIVED TIME
            if hh == "planning received time":
                en_date = getattr(trip.tr_enquirynumber, "en_created_at", None)
                row.append(en_date.strftime("%H:%M") if en_date else "")
                continue

            # ---------------------------------------------------
            # CONSIGNOR / CONSIGNEE
            # ---------------------------------------------------
            if "shipper" in hh:
                row.append(safe_str(cons_goods.cg_consigner) if cons_goods else "")
                continue

            if "llr no" in hh or "lr no" in hh:
                row.append(safe_str(cons_detail.co_consignmentnumber) if cons_detail else "")
                continue

            if "consignee" in hh:
                row.append(safe_str(cons_goods.cg_consignee) if cons_goods else "")
                continue

            # ---------------------------------------------------
            # CS NAME
            # ---------------------------------------------------
            if "cs name" in hh:
                row.append(safe_str(trip.tr_enquirynumber.en_assignedto))
                continue

            # ---------------------------------------------------
            # VEHICLE PLACED TIME
            # ---------------------------------------------------
            if "vehicle placed time" in hh:
                row.append(va.va_created_at.strftime("%H:%M") if va else "")
                continue

            # ---------------------------------------------------
            # HAWB / HBL / BOE
            # ---------------------------------------------------
            if "hawb" in hh or "hbl" in hh:
                row.append(safe_str(cons_goods.cg_hawbno) if cons_goods else "")
                continue

            if "boe" in hh or "ewaybill" in hh:
                row.append(safe_str(cons_goods.cg_ebillno) if cons_goods else "")
                continue

            # ---------------------------------------------------
            # REFERENCE #
            # ---------------------------------------------------
            if "reference" in hh:
                row.append(safe_str(cons_detail.co_cusrefnum if cons_detail else ""))
                continue

            # ---------------------------------------------------
            # VEHICLE DETAILS
            # ---------------------------------------------------
            if "truck no" in hh or "veh no" in hh:
                row.append(safe_str(trip.tr_vehiclenumber))
                continue

            if "truck type" in hh or "veh type" in hh:
                row.append(safe_str(trip.tr_vehicletype))
                continue

            # VENDOR
            if "vendor" in hh or "transporter" in hh:
                if trip.tr_vehiclesource_id in (2, 3):
                    vendor = safe_str(va.va_vendor) if va else ""
                else:
                    vendor = "OWN VEHICLE"
                row.append(vendor)
                continue

            # ---------------------------------------------------
            # DRIVER DETAILS
            # ---------------------------------------------------
            if "driver name" in hh:
                row.append(safe_str(trip.tr_drivername))
                continue

            if "driver mobile" in hh:
                row.append(safe_str(trip.tr_drivernumber))
                continue

            if "driver dl" in hh:
                row.append(safe_str(trip.tr_driver_lic))
                continue

            # ---------------------------------------------------
            # PIECES / WEIGHT
            # ---------------------------------------------------
            if "no of pieces" in hh:
                qty = cons_goods.cg_loaded_qty if cons_goods and cons_goods.cg_loaded_qty else (
                    cons_goods.cg_qty if cons_goods else "")
                row.append(safe_str(qty))
                continue

            if "actual weight" in hh or "invoice weight" in hh or "gross weight" in hh:
                val = ""
                if cons_goods and getattr(cons_goods, "cg_weight", None):
                    val = cons_goods.cg_weight
                row.append(safe_str(val))
                continue

            if "chargeable weight" in hh:
                row.append("")
                continue

            if "cbm" in hh or "volume" in hh:
                row.append("")
                continue

            # ---------------------------------------------------
            # UNLOADING FIELDS
            # ---------------------------------------------------
            if hh == "unloading point in date":
                row.append(trip.tr_reporteddate.strftime("%d-%m-%Y") if trip.tr_reporteddate else "")
                continue

            if hh == "unloading point in time":
                row.append(trip.tr_reporteddate.strftime("%H:%M") if trip.tr_reporteddate else "")
                continue

            if hh == "unloading point":
                row.append(safe_str(trip.tr_reportedlocation))
                continue

            if hh == "unloading point out date":
                row.append(trip.tr_unloading_time.strftime("%d-%m-%Y") if trip.tr_unloading_time else "")
                continue

            if hh == "unloading point out time":
                row.append(trip.tr_unloading_time.strftime("%H:%M") if trip.tr_unloading_time else "")
                continue

            # ---------------------------------------------------
            # CHARGES
            # ---------------------------------------------------
            if "no of days halting" in hh:
                row.append(safe_num(trip.tc_no_of_days_halting))
                continue

            if "additional charges" in hh:
                row.append(safe_num(trip.tc_handlingcost))
                continue

            if "cancellation charges" in hh:
                row.append(safe_num(trip.tc_cancellation))
                continue

            if "halting charges" in hh:
                row.append(safe_num(trip.tc_haltingcost))
                continue

            if hh == "charges":
                row.append(safe_num(trip.tc_tripcost))
                continue

            if "weightment charges" in hh:
                row.append(safe_num(trip.tc_weighmentcost))
                continue

            # For Air Import – Separate Parking Charges
            if hh == "parking charges":
                row.append(safe_num(trip.tc_parkingcost))
                continue

            # For Air Import – Separate Unloading Charges
            if hh == "unloading charges":
                row.append(safe_num(trip.tc_unloadingcost))
                continue

            if "parking / unloading charges" in hh:
                row.append(safe_num(trip.tc_parkingcost) + safe_num(trip.tc_unloadingcost))
                continue

            if "total charges" in hh:
                total = (
                    safe_num(trip.tc_tripcost) +
                    safe_num(trip.tc_parkingcost) +
                    safe_num(trip.tc_unloadingcost) +
                    safe_num(trip.tc_loadingcost) +
                    safe_num(trip.tc_weighmentcost) +
                    safe_num(trip.tc_handlingcost) +
                    safe_num(trip.tc_supervisorcost) +
                    safe_num(trip.tc_haltingcost)
                )
                row.append(total)
                continue

            # ---------------------------------------------------
            # REMARKS
            # ---------------------------------------------------
            if "remarks" in hh:
                row.append(
                    safe_str(cons_detail.co_remarks) if cons_detail else safe_str(trip.tr_remarks)
                )
                continue

            # ---------------------------------------------------
            # DEFAULT EMPTY CELL
            # ---------------------------------------------------
            row.append("")

        ws.append(row)

    # Auto column width
    for col in ws.columns:
        max_len = max(len(str(cell.value)) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = max_len + 2

    # Save file
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)

    # Send email
    recipient_list = [x.strip() for x in recipient.split(",") if x.strip()]
    subject = subject or f"{customer_obj.cu_name} - {template_key or 'DMR'} Report"
    message = message_body.replace("\n", "<br>")

    send_department_email(
        department='itadmin',
        subject=subject,
        message=message,
        recipient_list=recipient_list,
        attachment=excel_file,
        attachment_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        file_name=f"{customer_obj.cu_name}_DMR_Report.xlsx"
    )

    messages.success(request, "DMR Report sent successfully.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


