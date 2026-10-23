from django.utils import timezone
from datetime import datetime, date

AVAILABLE_CHARGES = [
    {"key": "tripcost", "label": "Trip / Freight Charges"},
    {"key": "loading", "label": "Loading Charges"},
    {"key": "unloading", "label": "Unloading Charges"},
    {"key": "halting", "label": "Halting Charges"},
    {"key": "toll", "label": "Toll Charges / Toll Pass"},
    {"key": "parking", "label": "Parking Charges"},
    {"key": "weighment", "label": "Weighment Charges"},
    {"key": "handling", "label": "Handling / Additional Charges"},
    {"key": "cancellation", "label": "Cancellation Charges"},
    {"key": "supervisor", "label": "Supervisor Charges"},
]

DMR_PAGE_CATALOG = [
    {
        "id": "ENQUIRY",
        "title": "Enquiry & Indent Page",
        "icon": "fas fa-clipboard-list",
        "color": "primary",
        "fields": [
            {"key": "en_enquirynumber", "label": "Enquiry No", "type": "string", "desc": "Trip enquiry reference"},
            {"key": "en_customername", "label": "Customer Name", "type": "string", "desc": "Customer display name"},
            {"key": "en_customerdepartment", "label": "Department Name", "type": "string", "desc": "Customer division / department"},
            {"key": "pickup_date", "label": "Pickup Date", "type": "date", "desc": "Trip pickup / indent departure date"},
            {"key": "pickup_time", "label": "Pickup Time", "type": "time", "desc": "Trip pickup / indent departure time"},
            {"key": "planning_date", "label": "Planning Received Date", "type": "date", "desc": "Enquiry creation / planning date"},
            {"key": "planning_time", "label": "Planning Received Time", "type": "time", "desc": "Enquiry creation / planning time"},
            {"key": "planning_datetime", "label": "Planning Date & Time", "type": "datetime", "desc": "Planning timestamp"},
            {"key": "en_assignedto", "label": "CS Name / Requestor", "type": "string", "desc": "Customer service assigned user"},
            {"key": "en_fromlocation", "label": "From Location", "type": "string", "desc": "Enquiry pickup place"},
            {"key": "en_tolocation", "label": "To Location / Destination", "type": "string", "desc": "Enquiry delivery place"},
            {"key": "booking_no", "label": "Booking No / PO #", "type": "string", "desc": "Customer booking or PO reference"},
            {"key": "en_branch", "label": "Branch", "type": "string", "desc": "Operating BVM branch"},
        ]
    },
    {
        "id": "CONSIGNMENT",
        "title": "Consignment & Goods Page",
        "icon": "fas fa-boxes",
        "color": "success",
        "fields": [
            {"key": "co_consignmentnumber", "label": "Consignment No / LR / Job No", "type": "string", "desc": "C-Note / LLR / BVM Job No"},
            {"key": "cg_consigner", "label": "Shipper Name / Consignor", "type": "string", "desc": "Shipper / Supplier name"},
            {"key": "cg_consignee", "label": "Consignee Name", "type": "string", "desc": "Consignee / Receiver name"},
            {"key": "cg_deliverylocation", "label": "Delivery Place", "type": "string", "desc": "Goods specific delivery point"},
            {"key": "co_cusrefnum", "label": "Invoice No / Customer Ref No", "type": "string", "desc": "Master Invoice # / Ref #"},
            {"key": "cg_hawbno", "label": "HAWB # / HBL #", "type": "string", "desc": "House Airway Bill / House Bill of Lading"},
            {"key": "cg_mawbno", "label": "MAWB #", "type": "string", "desc": "Master Airway Bill"},
            {"key": "cg_boeno", "label": "BOE #", "type": "string", "desc": "Bill of Entry"},
            {"key": "cg_ebillno", "label": "E-Way Bill #", "type": "string", "desc": "E-Way Bill number"},
            {"key": "cg_qty", "label": "No of Pieces / Pkgs", "type": "number", "desc": "Cargo pieces or package quantity"},
            {"key": "cg_weight", "label": "Actual Weight (Kgs)", "type": "number", "desc": "Gross / Cargo weight"},
            {"key": "chargeable_weight", "label": "Chargeable Weight", "type": "string", "desc": "Billing chargeable weight"},
            {"key": "cg_cbm", "label": "CBM / Volume", "type": "string", "desc": "Cubic meter cargo volume"},
            {"key": "hbl_wise_split_cost", "label": "HBL Wise Split Cost", "type": "number", "desc": "Trip cost split equally across consignment goods for C-Note (Trip Cost / Goods Count)"},
            {"key": "co_seal_number", "label": "Shipper Seal # / Smart Lock", "type": "string", "desc": "Seal or security lock number"},
            {"key": "co_remarks", "label": "Consignment Remarks", "type": "string", "desc": "Remarks recorded on consignment"},
        ]
    },
    {
        "id": "ALLOTMENT",
        "title": "Vehicle Allotment Page",
        "icon": "fas fa-truck-moving",
        "color": "warning",
        "fields": [
            {"key": "va_vendor", "label": "Transporter / Vendor Name", "type": "string", "desc": "Assigned transporter or vendor"},
            {"key": "va_vendor_code", "label": "Vendor Code", "type": "string", "desc": "Transporter vendor code"},
            {"key": "tr_vehiclenumber", "label": "Truck No / Vehicle No", "type": "string", "desc": "Placed vehicle registration number"},
            {"key": "tr_vehicletype", "label": "Truck Type / Container Size", "type": "string", "desc": "Requested vehicle size or type"},
            {"key": "tr_vehicletype_placed", "label": "Placed Vehicle Size", "type": "string", "desc": "Actual vehicle size placed"},
            {"key": "driver_name", "label": "Driver Name", "type": "string", "desc": "Assigned driver name"},
            {"key": "driver_mobile", "label": "Driver Mobile No", "type": "string", "desc": "Driver contact number"},
            {"key": "driver_dl", "label": "Driver DL #", "type": "string", "desc": "Driver driving license number"},
            {"key": "vehicle_placed_date", "label": "Vehicle Placed Date", "type": "date", "desc": "Date vehicle placed at point"},
            {"key": "vehicle_placed_time", "label": "Vehicle Placed Time", "type": "time", "desc": "Time vehicle placed at point"},
        ]
    },
    {
        "id": "TRIP_LOADING",
        "title": "Dispatch & Loading Page",
        "icon": "fas fa-stopwatch",
        "color": "info",
        "fields": [
            {"key": "tr_tripnumber", "label": "Trip Sheet No / Trip No", "type": "string", "desc": "BVM internal trip number"},
            {"key": "tr_departedlocation", "label": "Pickup Location / Origin", "type": "string", "desc": "Departure / Loading location"},
            {"key": "pickup_date", "label": "Pickup Date", "type": "date", "desc": "Departure or loading date"},
            {"key": "pickup_in_date", "label": "Pickup Point In Date", "type": "date", "desc": "Arrival at pickup shipper dock"},
            {"key": "pickup_in_time", "label": "Pickup Point In Time", "type": "time", "desc": "Arrival time at pickup shipper dock"},
            {"key": "pickup_out_date", "label": "Pickup Point Out Date", "type": "date", "desc": "Departed date from shipper dock"},
            {"key": "pickup_out_time", "label": "Pickup Point Out Time", "type": "time", "desc": "Departed time from shipper dock"},
            {"key": "loading_reported_datetime", "label": "Reported Date & Time @ Loading", "type": "datetime", "desc": "Combined timestamp at loading"},
            {"key": "loading_started_datetime", "label": "Started Date & Time @ Loading", "type": "datetime", "desc": "Started timestamp at loading"},
            {"key": "starting_km", "label": "Starting KM / Reported KM", "type": "number", "desc": "Odometer KM at start of trip"},
        ]
    },
    {
        "id": "TRIP_UNLOADING",
        "title": "Unloading & Delivery Page",
        "icon": "fas fa-flag-checkered",
        "color": "secondary",
        "fields": [
            {"key": "tr_reportedlocation", "label": "Unloading Point / Destination", "type": "string", "desc": "Unloading plant / hub location"},
            {"key": "unloading_in_date", "label": "Unloading Point In Date", "type": "date", "desc": "Arrival at destination plant"},
            {"key": "unloading_in_time", "label": "Unloading Point In Time", "type": "time", "desc": "Arrival time at destination plant"},
            {"key": "unloading_out_date", "label": "Unloading Point Out Date", "type": "date", "desc": "Release date from destination"},
            {"key": "unloading_out_time", "label": "Unloading Point Out Time", "type": "time", "desc": "Release time from destination"},
            {"key": "delivery_date", "label": "Delivery Date", "type": "date", "desc": "Final delivery completion date"},
            {"key": "unloading_reported_datetime", "label": "Reported Date & Time @ Unloading", "type": "datetime", "desc": "Combined timestamp at unloading"},
            {"key": "unloading_started_datetime", "label": "Started Date & Time @ Unloading", "type": "datetime", "desc": "Closing timestamp at unloading"},
            {"key": "closing_km", "label": "Closing KM", "type": "number", "desc": "Odometer KM at end of trip"},
            {"key": "used_km", "label": "Used KM", "type": "number", "desc": "Calculated total KM used"},
            {"key": "halting_days", "label": "No of Days Halting / Detention", "type": "number", "desc": "Halting days count"},
            {"key": "halting_status", "label": "Halting Status (YES / NO)", "type": "string", "desc": "Whether halting occurred"},
            {"key": "delivery_status", "label": "Delivery Status / POD Status", "type": "string", "desc": "Finance/Operations status of trip"},
            {"key": "tr_remarks", "label": "Trip Remarks", "type": "string", "desc": "Trip closure comments or notes"},
        ]
    },
    {
        "id": "CHARGES_FINANCE",
        "title": "Charges & Finance Page",
        "icon": "fas fa-rupee-sign",
        "color": "danger",
        "fields": [
            {"key": "tripcost", "label": "Trip Charges / Freight Cost", "type": "number", "desc": "Base transportation rate/charge"},
            {"key": "loading_charges", "label": "Loading Charges", "type": "number", "desc": "Loading cost"},
            {"key": "unloading_charges", "label": "Unloading Charges", "type": "number", "desc": "Unloading cost"},
            {"key": "halting_charges", "label": "Halting Charges", "type": "number", "desc": "Halting / detention charges"},
            {"key": "toll_charges", "label": "Toll Charges / Toll Pass", "type": "number", "desc": "Toll pass cost"},
            {"key": "parking_charges", "label": "Parking Charges", "type": "number", "desc": "Parking fee"},
            {"key": "weighment_charges", "label": "Weighment Charges", "type": "number", "desc": "Weighment slip charges"},
            {"key": "additional_charges", "label": "Handling / Additional Charges", "type": "number", "desc": "Handling or extra charges"},
            {"key": "cancellation_charges", "label": "Cancellation Charges", "type": "number", "desc": "Cancellation cost"},
            {"key": "parking_unloading_combined", "label": "Parking / Unloading Charges (Combined)", "type": "number", "desc": "Sum of parking and unloading"},
            {"key": "loading_unloading_combined", "label": "Loading / Unloading Charges (Combined)", "type": "number", "desc": "Sum of loading and unloading charges"},
            {"key": "hbl_wise_split_cost", "label": "HBL Wise Split Cost", "type": "number", "desc": "Trip cost split equally across consignment goods for C-Note (Trip Cost / Goods Count)"},
            {"key": "custom_total_charges", "label": "Total Charges / Cost (Configurable)", "type": "number", "desc": "Configurable summation of selected charges", "has_multi_charges": True},
        ]
    },
    {
        "id": "SYSTEM",
        "title": "System & Custom Fields",
        "icon": "fas fa-cogs",
        "color": "dark",
        "fields": [
            {"key": "s_no", "label": "S.NO (Serial Number)", "type": "number", "desc": "Auto-incrementing row number (1, 2, 3...)"},
            {"key": "month_name", "label": "Month Name", "type": "string", "desc": "E.g., January, February"},
            {"key": "static_text", "label": "Static Text / Fixed Value", "type": "string", "desc": "Fixed constant text in every row", "has_static_value": True},
            {"key": "blank_column", "label": "Blank / Empty Column", "type": "string", "desc": "Empty placeholder column"},
        ]
    }
]


def _safe_fmt(dt, fmt="%d-%m-%Y"):
    if not dt:
        return ""
    try:
        if isinstance(dt, datetime):
            dt = timezone.localtime(dt)
    except Exception:
        pass
    try:
        return dt.strftime(fmt)
    except Exception:
        return str(dt)


def _safe_str(v):
    return "" if v is None else str(v)


def _safe_num(v):
    try:
        return float(v) if v not in ("", None, "None") else 0.0
    except Exception:
        return 0.0


# EIPL Cargo / Goods line-item fields that must NEVER merge (remain individual per package/invoice):
CARGO_GOODS_FIELD_KEYS = {
    'cg_hawbno',             # HAWB # / HBL #
    'cg_mawbno',             # MAWB #
    'cg_boeno',              # BOE #
    'cg_ebillno',            # E-Way Bill #
    'cg_ewaybill',           # E-Way Bill alias
    'co_cusrefnum',          # Invoice No / Customer Ref No
    'cg_qty',                # No of Pieces / Pkgs
    'cg_weight',             # Actual Weight (Kgs)
    'chargeable_weight',     # Chargeable Weight
    'cg_cbm',                # CBM / Volume
    'hbl_wise_split_cost',   # Split cost per HBL line item (must not merge)
    'split_cost',
    'co_seal_number',        # Shipper Seal # / Smart Lock
    'static_text',           # Fixed text
    'blank_column',          # Blank placeholder
}

CARGO_HEADER_KEYWORDS = [
    'hawb', 'hbl', 'boe', 'eway', 'e-way', 'pieces', 'pkgs', 'pkg', 'pcs',
    'actual weight', 'gross weight', 'chargeable weight', 'cargo weight', 'weight (kgs)',
    'cbm', 'volume', 'invoice', 'ref no', 'ref num', 'master invoice', 'seal', 'capacity',
    'be#', 'be #', 'be no', 'b/e no', 'b/e #',
    'split cost', 'split'
]

def is_dmr_column_mergeable(field_key=None, column_header=None):
    """
    Returns True if the column is a trip/consignment/charges level field that should merge
    vertically across rows belonging to the same trip (like in EIPL).
    Returns False for cargo/goods level fields that must stay distinct per line item.
    """
    if field_key:
        fk = str(field_key).strip().lower()
        if fk in CARGO_GOODS_FIELD_KEYS:
            return False
    if column_header:
        ch = str(column_header).strip().lower()
        if ch in ('weight', 'wt', 'net weight', 'pcs', 'pkgs', 'pkg'):
            return False
        if any(kw in ch for kw in CARGO_HEADER_KEYWORDS):
            return False
    return True


def calculate_custom_charge_total(trip, effective_tripcost, included_charges_str):
    """
    Dynamically sums charges based on the user's multi-selected charges.
    If included_charges_str is empty/None, sums all standard charges by default.
    """
    charge_map = {
        "tripcost": effective_tripcost,
        "loading": _safe_num(trip.tc_loadingcost),
        "unloading": _safe_num(trip.tc_unloadingcost),
        "halting": _safe_num(trip.tc_haltingcost),
        "toll": _safe_num(trip.tc_tollcost),
        "parking": _safe_num(trip.tc_parkingcost),
        "weighment": _safe_num(trip.tc_weighmentcost),
        "handling": _safe_num(trip.tc_handlingcost),
        "cancellation": _safe_num(trip.tc_cancellation),
        "supervisor": _safe_num(trip.tc_supervisorcost),
    }

    if not included_charges_str:
        # Default: sum all charges
        return sum(charge_map.values())

    selected_keys = [k.strip().lower() for k in included_charges_str.split(",") if k.strip()]
    total = 0.0
    for key in selected_keys:
        if key in charge_map:
            total += charge_map[key]
    return total


def extract_dmr_cell_value(field_key, trip, cons_goods=None, cons_detail=None, va=None,
                            effective_tripcost=0.0, row_idx=1, date_fmt=None,
                            included_charges=None, static_val="", goods_count=1):
    """
    Unified extraction engine mapping any field_key from the catalog to its dynamic value.
    """
    try:
        return _extract_dmr_cell_value_inner(
            field_key, trip, cons_goods, cons_detail, va,
            effective_tripcost, row_idx, date_fmt,
            included_charges, static_val, goods_count
        )
    except Exception:
        return ""


def _extract_dmr_cell_value_inner(field_key, trip, cons_goods=None, cons_detail=None, va=None,
                                   effective_tripcost=0.0, row_idx=1, date_fmt=None,
                                   included_charges=None, static_val="", goods_count=1):
    fk = (field_key or "").strip().lower()
    df = date_fmt.strip() if date_fmt else ""

    # 1. System / Custom
    if fk == "s_no":
        return row_idx
    if fk == "blank_column":
        return ""
    if fk == "static_text":
        return static_val or ""
    if fk == "month_name":
        dt = trip.tr_loading_time or trip.tr_departeddate or trip.tr_created_at
        return _safe_fmt(dt, "%B") if dt else ""

    # 2. Enquiry Page
    if fk == "en_enquirynumber":
        return _safe_str(trip.tr_enquirynumber.en_enquirynumber if trip.tr_enquirynumber else "")
    if fk == "en_customername":
        return _safe_str(trip.tr_enquirynumber.en_customername if trip.tr_enquirynumber else "")
    if fk == "en_customerdepartment":
        return _safe_str(trip.tr_enquirynumber.en_customerdepartment if trip.tr_enquirynumber else "")
    if fk == "planning_date":
        en_dt = getattr(trip.tr_enquirynumber, "en_created_at", None)
        return _safe_fmt(en_dt, df or "%d-%m-%Y") if en_dt else ""
    if fk == "planning_time":
        en_dt = getattr(trip.tr_enquirynumber, "en_created_at", None)
        return _safe_fmt(en_dt, df or "%H:%M") if en_dt else ""
    if fk == "planning_datetime":
        en_dt = getattr(trip.tr_enquirynumber, "en_created_at", None)
        return _safe_fmt(en_dt, df or "%d-%m-%Y %H:%M") if en_dt else ""
    if fk == "en_assignedto":
        return _safe_str(trip.tr_enquirynumber.en_assignedto if trip.tr_enquirynumber else "")
    if fk == "en_fromlocation":
        return _safe_str(trip.tr_departedlocation or (trip.tr_enquirynumber.en_fromlocaion if trip.tr_enquirynumber else ""))
    if fk in ("en_tolocation", "delivery_location", "cg_deliverylocation"):
        val = (cons_goods.cg_deliverylocation if cons_goods and getattr(cons_goods, "cg_deliverylocation", None) else None) or trip.tr_reportedlocation or (trip.tr_enquirynumber.en_tolocation if trip.tr_enquirynumber else "")
        return _safe_str(val)
    if fk == "booking_no":
        return _safe_str(getattr(trip, "tr_customerref", None) or (cons_detail.co_cusrefnum if cons_detail else ""))
    if fk == "en_branch":
        return _safe_str(getattr(trip.tr_enquirynumber, "en_branch", ""))

    # 3. Consignment & Goods Page
    if fk == "co_consignmentnumber":
        return _safe_str(cons_detail.co_consignmentnumber if cons_detail else "")
    if fk == "cg_consigner":
        return _safe_str(cons_goods.cg_consigner if cons_goods else "")
    if fk == "cg_consignee":
        return _safe_str(cons_goods.cg_consignee if cons_goods else "")
    if fk == "co_cusrefnum":
        return _safe_str(cons_detail.co_cusrefnum if cons_detail else "")
    if fk == "cg_hawbno":
        return _safe_str(cons_goods.cg_hawbno if cons_goods else "")
    if fk == "cg_mawbno":
        return _safe_str(cons_goods.cg_mawbno if cons_goods else "")
    if fk in ("cg_boeno", "cg_boe", "boeno", "boe"):
        return _safe_str(cons_goods.cg_boeno if cons_goods and getattr(cons_goods, 'cg_boeno', None) else "")
    if fk in ("cg_ebillno", "cg_ewaybill", "cg_eway_bill", "ebillno", "ewaybill", "eway_bill"):
        return _safe_str(cons_goods.cg_ebillno if cons_goods and getattr(cons_goods, 'cg_ebillno', None) else "")
    if fk == "cg_qty":
        qty = cons_goods.cg_loaded_qty if cons_goods and cons_goods.cg_loaded_qty else (cons_goods.cg_qty if cons_goods else "")
        return _safe_str(qty)
    if fk == "cg_weight":
        return _safe_str(cons_goods.cg_weight if cons_goods else "")
    if fk == "chargeable_weight":
        return ""
    if fk in ("cg_cbm", "cbm"):
        if cons_goods and getattr(cons_goods, 'cg_cbm', None) not in (None, '', 0, 0.0, '0', '0.0'):
            return cons_goods.cg_cbm
        if cons_goods and getattr(cons_goods, 'cg_length', 0) and getattr(cons_goods, 'cg_width', 0) and getattr(cons_goods, 'cg_height', 0):
            cbm = (cons_goods.cg_length * cons_goods.cg_width * cons_goods.cg_height) / 1000000.0
            return round(cbm, 3)
        if cons_goods and getattr(cons_goods, 'cg_cbm', None) not in (None, ''):
            val = cons_goods.cg_cbm
            return val if str(val) not in ('0', '0.0') else ""
        return ""
    if fk == "co_seal_number":
        return _safe_str((cons_detail.co_seal_number or cons_detail.co_smart_lock_number) if cons_detail else "")
    if fk == "co_remarks":
        val = (cons_detail.co_remarks if cons_detail and cons_detail.co_remarks else "") or (trip.tr_remarks or "")
        return _safe_str(val)

    # 4. Vehicle Allotment Page
    if fk == "va_vendor":
        return "BVM"
    if fk == "va_vendor_code":
        return _safe_str(va.va_vendor.vm_vendorcode if va and va.va_vendor else "")
    if fk == "tr_vehiclenumber":
        return _safe_str(trip.tr_vehiclenumber)
    if fk == "tr_vehicletype":
        return _safe_str(trip.tr_vehicletype)
    if fk == "tr_vehicletype_placed":
        return _safe_str(trip.tr_vehicletype_placed or trip.tr_vehicletype)
    if fk == "driver_name":
        return _safe_str(trip.tr_drivername or (va.va_drivername if va else "") or (va.va_driver.dm_name if va and va.va_driver else ""))
    if fk == "driver_mobile":
        return _safe_str(trip.tr_drivernumber or (va.va_drivernumber if va else "") or (va.va_driver.dm_drivernumber if va and va.va_driver else ""))
    if fk == "driver_dl":
        return _safe_str(trip.tr_driver_lic or (va.va_driver_lic if va else "") or (va.va_driver.dm_driver_lic if va and va.va_driver else ""))
    if fk == "vehicle_placed_date":
        v = trip.tr_loading_time or (va.va_created_at if va else None)
        return _safe_fmt(v, df or "%d-%m-%Y") if v else ""
    if fk == "vehicle_placed_time":
        v = trip.tr_loading_time or (va.va_created_at if va else None)
        return _safe_fmt(v, df or "%H:%M") if v else ""

    # 5. Dispatch & Loading Page
    if fk == "tr_tripnumber":
        return _safe_str(trip.tr_tripnumber)
    if fk == "tr_departedlocation":
        return _safe_str(trip.tr_departedlocation)
    if fk in ("pickup_date", "en_pickup_date"):
        val = trip.tr_departeddate_pickup or trip.tr_loading_time or trip.tr_departeddate or getattr(trip.tr_enquirynumber, "en_pickupdatetime", None)
        return _safe_fmt(val, df or "%d-%m-%Y") if val else ""
    if fk in ("pickup_time", "en_pickup_time"):
        val = trip.tr_departeddate_pickup or trip.tr_loading_time or getattr(trip.tr_enquirynumber, "en_pickupdatetime", None)
        return _safe_fmt(val, df or "%H:%M") if val else ""
    if fk == "pickup_in_date":
        val = trip.tr_departeddate_pickup or trip.tr_loading_time
        return _safe_fmt(val, df or "%d-%m-%Y") if val else ""
    if fk == "pickup_in_time":
        val = trip.tr_departeddate_pickup or trip.tr_loading_time
        return _safe_fmt(val, df or "%H:%M") if val else ""
    if fk == "pickup_out_date":
        val = trip.tr_dock_out_time or trip.tr_departeddate or trip.tr_dock_in_time or trip.tr_loading_time
        return _safe_fmt(val, df or "%d-%m-%Y") if val else ""
    if fk == "pickup_out_time":
        val = trip.tr_dock_out_time or trip.tr_departeddate or trip.tr_dock_in_time or trip.tr_loading_time
        return _safe_fmt(val, df or "%H:%M") if val else ""
    if fk == "loading_reported_datetime":
        val = trip.tr_loading_time or trip.tr_departeddate_pickup or trip.tr_departeddate
        return _safe_fmt(val, df or "%d-%m-%Y %H:%M") if val else ""
    if fk == "loading_started_datetime":
        val = trip.tr_departeddate or trip.tr_loading_time or trip.tr_departeddate_pickup
        return _safe_fmt(val, df or "%d-%m-%Y %H:%M") if val else ""
    if fk == "starting_km":
        return _safe_str(trip.tr_reportedkm_pickup)

    # 6. Unloading & Delivery Page
    if fk in ("tr_reportedlocation", "unloading_point"):
        val = trip.tr_reportedlocation or (trip.tr_enquirynumber.en_tolocation if trip.tr_enquirynumber else "") or (cons_goods.cg_deliverylocation if cons_goods and getattr(cons_goods, "cg_deliverylocation", None) else "")
        return _safe_str(val)
    if fk == "unloading_in_date":
        val = trip.tr_reporteddate or trip.tr_reporteddate_delivery or trip.tr_departeddate_delivery
        return _safe_fmt(val, df or "%d-%m-%Y") if val else ""
    if fk == "unloading_in_time":
        val = trip.tr_reporteddate or trip.tr_reporteddate_delivery or trip.tr_departeddate_delivery
        return _safe_fmt(val, df or "%H:%M") if val else ""
    if fk == "unloading_out_date":
        val = trip.tr_unloading_time or trip.tr_reporteddate_pickup or trip.tr_departeddate_delivery
        return _safe_fmt(val, df or "%d-%m-%Y") if val else ""
    if fk == "unloading_out_time":
        val = trip.tr_unloading_time or trip.tr_reporteddate_pickup or trip.tr_departeddate_delivery
        return _safe_fmt(val, df or "%H:%M") if val else ""
    if fk == "delivery_date":
        val = trip.tr_unloading_time or trip.tr_reporteddate_pickup or trip.tr_reporteddate or trip.tr_departeddate_delivery
        return _safe_fmt(val, df or "%d-%m-%Y") if val else ""
    if fk == "unloading_reported_datetime":
        val = trip.tr_reporteddate or trip.tr_departeddate_delivery
        return _safe_fmt(val, df or "%d-%m-%Y %H:%M") if val else ""
    if fk == "unloading_started_datetime":
        val = trip.tr_unloading_time or trip.tr_reporteddate_pickup or trip.tr_reporteddate
        return _safe_fmt(val, df or "%d-%m-%Y %H:%M") if val else ""
    if fk == "closing_km":
        val = trip.tr_reportedkm_delivery if trip.tr_category_id == 1 else trip.tr_reportedkm
        return _safe_str(val)
    if fk == "used_km":
        diff = ((trip.tr_reportedkm or 0) - (trip.tr_reportedkm_pickup or 0)) if trip.tr_category_id in (2, 3) else (
            (trip.tr_reportedkm_delivery or 0) - (trip.tr_reportedkm_pickup or 0)
        )
        return _safe_num(diff)
    if fk == "halting_days":
        return _safe_num(trip.tc_no_of_days_halting)
    if fk == "halting_status":
        days = _safe_num(trip.tc_no_of_days_halting)
        return "YES" if days > 0 else "NO"
    if fk == "delivery_status":
        return str(trip.tc_financestatus.status if trip.tc_financestatus else "PENDING")
    if fk == "tr_remarks":
        val = (trip.tr_remarks or "") or (cons_detail.co_remarks if cons_detail and cons_detail.co_remarks else "")
        return _safe_str(val)

    # 7. Charges & Finance Page
    if fk == "tripcost":
        return effective_tripcost
    if fk == "loading_charges":
        return _safe_num(trip.tc_loadingcost)
    if fk == "unloading_charges":
        return _safe_num(trip.tc_unloadingcost)
    if fk == "halting_charges":
        return _safe_num(trip.tc_haltingcost)
    if fk == "toll_charges":
        return _safe_num(trip.tc_tollcost)
    if fk == "parking_charges":
        return _safe_num(trip.tc_parkingcost)
    if fk == "weighment_charges":
        return _safe_num(trip.tc_weighmentcost)
    if fk == "additional_charges":
        return _safe_num(trip.tc_handlingcost)
    if fk == "cancellation_charges":
        return _safe_num(trip.tc_cancellation)
    if fk == "parking_unloading_combined":
        return _safe_num(trip.tc_parkingcost) + _safe_num(trip.tc_unloadingcost)
    if fk in ("loading_unloading_combined", "loading_unloading_charges"):
        return _safe_num(trip.tc_loadingcost) + _safe_num(trip.tc_unloadingcost)
    if fk in ("hbl_wise_split_cost", "split_cost"):
        g_cnt = goods_count if goods_count and goods_count > 0 else 1
        return round(effective_tripcost / g_cnt, 2)
    if fk in ("custom_total_charges", "total_charges"):
        return calculate_custom_charge_total(trip, effective_tripcost, included_charges)

    return ""
