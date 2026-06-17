from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Sum, Q
import calendar
from datetime import date as dt_date, timedelta

from ..sub_forms.attached_bill_form import AttachedBillForm
from ..sub_models.attached_bill_mod import AttachedBillInfo
from ..sub_models.vehiclemaster_mod import VehiclemasterInfo
from ..sub_models.tripdetail_mod import TripdetailInfo
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from django.http import HttpResponse


# ==================================================
# ADD ATTACHED BILL
# ==================================================
@login_required(login_url='login_page')
def attached_bill_add(request):
    if request.method == "POST":
        form = AttachedBillForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.ab_created_by = request.user
            obj.save()

            # Save per-trip costs from table
            selected_trips = request.POST.get('ab_selected_trips', '')
            if selected_trips:
                trip_numbers = [t.strip() for t in selected_trips.split(',') if t.strip()]
                # Find trips to get their IDs for input name matching
                trips_to_update = TripdetailInfo.objects.filter(tr_tripnumber__in=trip_numbers)
                for trip in trips_to_update:
                    tid = trip.id
                    t_buy = request.POST.get(f'trip_buy_cost_{tid}')
                    t_parking = request.POST.get(f'trip_parking_cost_{tid}')
                    t_toll = request.POST.get(f'trip_toll_cost_{tid}')

                    if t_buy is not None:
                        trip.tc_tripcost = float(t_buy or 0)
                    if t_parking is not None: trip.tc_parkingcost = float(t_parking or 0)
                    if t_toll is not None: trip.tc_tollcost = float(t_toll or 0)
                    trip.save()

            messages.success(request, "Attached Bill saved successfully.")
            return redirect('attached_bill_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AttachedBillForm()

    return render(
        request,
        "asset_mgt_app/attached_bill_add.html",
        {
            "form": form,
            "title": "Add Attached Bill"
        }
    )


# ==================================================
# LIST ATTACHED BILLS
# ==================================================
@login_required(login_url='login_page')
def attached_bill_list(request):
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')

    bills = AttachedBillInfo.objects.all().order_by('-ab_created_at')
    if from_date:
        bills = bills.filter(ab_bill_date__gte=from_date)
    if to_date:
        bills = bills.filter(ab_bill_date__lte=to_date)
    return render(
        request,
        "asset_mgt_app/attached_bill_list.html",
        {
            "bills": bills,
            "from_date": from_date,
            "to_date": to_date,
        }
    )


# ==================================================
# EDIT ATTACHED BILL
# ==================================================
@login_required(login_url='login_page')
def attached_bill_edit(request, id):
    record = get_object_or_404(AttachedBillInfo, id=id)
    if request.method == "POST":
        form = AttachedBillForm(request.POST, request.FILES, instance=record)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.ab_updated_by = request.user
            obj.save()

            # Save per-trip costs from table
            selected_trips = request.POST.get('ab_selected_trips', '')
            if selected_trips:
                trip_numbers = [t.strip() for t in selected_trips.split(',') if t.strip()]
                trips_to_update = TripdetailInfo.objects.filter(tr_tripnumber__in=trip_numbers)
                for trip in trips_to_update:
                    tid = trip.id
                    t_buy = request.POST.get(f'trip_buy_cost_{tid}')
                    t_parking = request.POST.get(f'trip_parking_cost_{tid}')
                    t_toll = request.POST.get(f'trip_toll_cost_{tid}')

                    if t_buy is not None:
                        trip.tc_tripcost = float(t_buy or 0)
                    if t_parking is not None: trip.tc_parkingcost = float(t_parking or 0)
                    if t_toll is not None: trip.tc_tollcost = float(t_toll or 0)
                    trip.save()

            messages.success(request, "Attached Bill updated successfully.")
            return redirect('attached_bill_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AttachedBillForm(instance=record)

    return render(
        request,
        "asset_mgt_app/attached_bill_add.html",
        {
            "form": form,
            "record": record,
            "title": "Edit Attached Bill"
        }
    )


# ==================================================
# DELETE ATTACHED BILL
# ==================================================
@login_required(login_url='login_page')
def attached_bill_delete(request, id):
    record = get_object_or_404(AttachedBillInfo, id=id)
    if request.method == "POST":
        record.delete()
        messages.success(request, "Attached Bill deleted successfully.")
    return redirect('attached_bill_list')


# ==================================================
# QUICK MEDIA UPLOAD
# ==================================================
@login_required(login_url='login_page')
def attached_bill_upload(request, id):
    record = get_object_or_404(AttachedBillInfo, id=id)
    if request.method == "POST" and request.FILES.get('ab_bill_upload'):
        record.ab_bill_upload = request.FILES.get('ab_bill_upload')
        record.save()
        messages.success(request, "File uploaded successfully.")
    return redirect('attached_bill_list')


# ==================================================
# AJAX: GET VEHICLE DETAILS & KM RUN
# ==================================================
@login_required(login_url='login_page')
def get_attached_vehicle_details(request):
    vendor_id = request.GET.get('vendor_id')
    vehicle_id = request.GET.get('vehicle_id')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    data = {'trips': [], 'total_km_run': 0, 'leave_days': 0, 'vehicle_type': '', 'buy_cost': 0, 'agreed_km': 0, 'extra_km_rate': 0}

    def parse_dt(d_str):
        if not d_str: return None
        try: return dt_date.fromisoformat(d_str)
        except:
            try:
                p = d_str.split('-')
                if len(p) == 3: return dt_date(int(p[2]), int(p[1]), int(p[0]))
            except: pass
        return None

    f_dt_obj = parse_dt(from_date)
    t_dt_obj = parse_dt(to_date)

    try:
        if vehicle_id:
            try:
                vehicle = VehiclemasterInfo.objects.get(id=vehicle_id)
                data.update({
                    'vehicle_type': str(vehicle.vm_vehicletype) if vehicle.vm_vehicletype else "",
                    'buy_cost': float(vehicle.vm_buycost) if vehicle.vm_buycost and str(vehicle.vm_buycost).replace('.','',1).isdigit() else 0.0,
                    'agreed_km': float(vehicle.vm_agreedkm) if vehicle.vm_agreedkm and str(vehicle.vm_agreedkm).replace('.','',1).isdigit() else 0.0,
                    'extra_km_rate': float(vehicle.vm_extrakm) if vehicle.vm_extrakm and str(vehicle.vm_extrakm).replace('.','',1).isdigit() else 0.0,
                })
            except VehiclemasterInfo.DoesNotExist:
                pass
        elif vendor_id:
            pass

        filters = Q()
        if vehicle_id:
            vehicle = VehiclemasterInfo.objects.get(id=vehicle_id)
            filters &= Q(tr_vehiclenumber=vehicle.vm_registrationnumber)
        elif vendor_id:
            vehicle_reg_nos = VehiclemasterInfo.objects.filter(vm_vendor_id=vendor_id).values_list('vm_registrationnumber', flat=True)
            filters &= Q(tr_vehiclenumber__in=vehicle_reg_nos)
        
        if f_dt_obj and t_dt_obj:
            # Fetch trips for [start-1, end+1] to check Sunday neighbors correctly at boundaries
            expanded_start = f_dt_obj - timedelta(days=1)
            expanded_end = t_dt_obj + timedelta(days=1)
            filters &= Q(tr_departeddate__date__range=[expanded_start, expanded_end])

        if filters:
            bill_id = request.GET.get('bill_id')
            billed_trips_query = AttachedBillInfo.objects.all()
            if bill_id:
                billed_trips_query = billed_trips_query.exclude(id=bill_id)
            
            already_billed = []
            for b_trips in billed_trips_query.values_list('ab_selected_trips', flat=True):
                if b_trips:
                    already_billed.extend([t.strip() for t in b_trips.split(',') if t.strip()])
            
            if already_billed:
                filters &= ~Q(tr_tripnumber__in=already_billed)

            trips = TripdetailInfo.objects.filter(filters).filter(tr_category_id=1).order_by('tr_departeddate')
            trip_dates = set()
            
            # For Total KM using Vehicle Log method (Last Closing - First Starting)
            first_start_km = None
            last_close_km = None

            for trip in trips:
                # Per-trip KM logic updated to match Vehicle Log Report
                start_km = trip.tr_reportedkm_pickup if trip.tr_reportedkm_pickup else (trip.tr_departedkm or 0)
                closing_km = trip.tr_reportedkm_delivery if trip.tr_reportedkm_delivery else (trip.tr_reportedkm or 0)
                km = 0
                if closing_km and start_km:
                    diff = closing_km - start_km
                    if 0 < diff < 15000:
                        km = diff

                # Track min departed and max reported for the entire period
                # ONLY track KM for trips within the actual billing period
                trip_dte = trip.tr_departeddate.date() if trip.tr_departeddate else None
                if trip_dte and f_dt_obj <= trip_dte <= t_dt_obj:
                    trip_start_km = trip.tr_departedkm or 0
                    trip_close_km = trip.tr_reportedkm_delivery or trip.tr_reportedkm or 0
                    if trip_start_km > 0 and first_start_km is None:
                        first_start_km = trip_start_km
                    if trip_close_km > 0:
                        last_close_km = trip_close_km

                if trip.tr_departeddate:
                    start_date = trip.tr_departeddate.date()
                    end_date_val = (trip.tr_reporteddate_delivery or trip.tr_reporteddate or trip.tr_departeddate).date()
                    temp_date = start_date
                    while temp_date <= end_date_val:
                        trip_dates.add(temp_date)
                        temp_date += timedelta(days=1)

                # Filter trips for the table display to just the current period
                if trip_dte and f_dt_obj <= trip_dte <= t_dt_obj:
                    customer_name = trip.tr_enquirynumber.en_customername.cu_name if trip.tr_enquirynumber and trip.tr_enquirynumber.en_customername else "N/A"
                    data['trips'].append({
                        'id': trip.id,
                        'trip_date': trip.tr_departeddate.strftime('%d-%m-%Y') if trip.tr_departeddate else "",
                        'trip_no': trip.tr_tripnumber or "",
                        'cnote': trip.tr_consignmentnumber.co_consignmentnumber if trip.tr_consignmentnumber else "",
                        'customer': customer_name,
                        'from': str(trip.tr_departedlocation) if trip.tr_departedlocation else "",
                        'to': str(trip.tr_reportedlocation) if trip.tr_reportedlocation else "",
                        'trip_km': km,
                        'selling_cost': float(trip.tc_tripcost or 0),
                        'buy_cost': 0.0, # Will be calculated on frontend from header distribution
                        'parking_cost': float(trip.tc_parkingcost or 0),
                        'toll_cost': float(trip.tc_tollcost or 0),
                        'total_buy_cost': 0.0 # Will be calculated on frontend
                    })

            # Calculate total KM run for the period (Vehicle Log Method)
            total_km_run = 0
            if first_start_km is not None and last_close_km is not None:
                total_km_run = max(0, last_close_km - first_start_km)
            data['total_km_run'] = total_km_run

            if f_dt_obj and t_dt_obj:
                leave_days_count = 0
                curr = f_dt_obj
                while curr <= t_dt_obj:
                    if curr not in trip_dates:
                        leave_days_count += 1
                    curr += timedelta(days=1)
                data['leave_days'] = leave_days_count
        else:
            data['total_km_run'] = 0
            data['leave_days'] = 0

    except Exception as e:
        data['error'] = str(e)
        import traceback
        data['traceback'] = traceback.format_exc()

    return JsonResponse(data)


@login_required(login_url='login_page')
def attached_bill_export_tally(request):
    """Export Attached Bills in Tally-friendly Excel format.
    Supports optional GET params: from_date and to_date (YYYY-MM-DD).
    """
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')

    bills = AttachedBillInfo.objects.all().order_by('ab_bill_date')
    if from_date:
        bills = bills.filter(ab_bill_date__gte=from_date)
    if to_date:
        bills = bills.filter(ab_bill_date__lte=to_date)

    wb = Workbook()
    ws = wb.active
    ws.title = "Tally Export"

    headers = [
        "VOUCHER NUMBER", "DATE", "REF NO.", "SUNDRY CREDITORS", "TOTAL AMT",
        "EXPENSES LEDGER", "AMOUNT", "Primary Cost Category", "Job No",
        "VEH. NO.", "Customer", "TDS LEDGER", "TDS AMOUNT", "NARRATION"
    ]
    ws.append(headers)

    header_font = Font(bold=True)
    header_fill = PatternFill("solid", fgColor="B2FFFF")
    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center")

    expense_fill = PatternFill("solid", fgColor="FFE5CC")

    for bill in bills:
        selected_trip_numbers = []
        if bill.ab_selected_trips:
            selected_trip_numbers = [t.strip() for t in bill.ab_selected_trips.split(',') if t.strip()]

        trips = TripdetailInfo.objects.filter(tr_tripnumber__in=selected_trip_numbers).select_related('tr_enquirynumber')

        # Financial year and month in voucher
        if bill.ab_bill_date:
            year = bill.ab_bill_date.year
            month = bill.ab_bill_date.month
            if month >= 4:
                fy_str = f"{str(year)[-2:]}-{str(year+1)[-2:]}"
            else:
                fy_str = f"{str(year-1)[-2:]}-{str(year)[-2:]}"
            month_str_num = f"{month:02d}"
        else:
            fy_str = "00-00"
            month_str_num = "00"

        voucher_number = f"MAA_ATT_{fy_str}_{month_str_num}_{bill.id:03d}"
        bill_date = bill.ab_bill_date.strftime("%d-%m-%Y") if bill.ab_bill_date else ""
        ref_no = bill.ab_bill_no or ""
        vendor_name = bill.ab_vendor.vend_name if bill.ab_vendor else ""
        # Show payable amount in the TOTAL AMT column; fall back to bill amount if payable not set
        total_amt = float(bill.ab_payable_amount if (bill.ab_payable_amount is not None and bill.ab_payable_amount != 0) else (bill.ab_bill_amount or 0.0))

        tds_amount = float(bill.ab_tds_amount or 0.0)
        # Determine TDS ledger label based on saved TDS type
        tds_ledger = ""
        try:
            tds_type = (bill.ab_tds_type or '').strip()
            if tds_amount > 0:
                if tds_type == 'Company':
                    tds_ledger = "TDS Payable 194C (Company)"
                else:
                    tds_ledger = "TDS Payable 194C (Non Company)"
        except Exception:
            tds_ledger = "TDS Payable 194C (Non Company)" if tds_amount > 0 else ""

        month_short = bill.ab_bill_date.strftime('%b%y') if bill.ab_bill_date else ""
        rec_date_str = bill.ab_created_at.strftime('%d-%b-%y') if bill.ab_created_at else ""
        narration = f"Being ATT Vehicle expenses for the month of {month_short} (Bill Received on {rec_date_str})"

        is_first_row = True

        if not trips:
            vehicle_disp = ""
            if bill.ab_vehicle_number and getattr(bill.ab_vehicle_number, 'vm_registrationnumber', None):
                vehicle_disp = f"{bill.ab_vehicle_number.vm_registrationnumber} (A)"
            row = [
                voucher_number, bill_date, ref_no, vendor_name, total_amt,
                "Transportation", total_amt, "Maa-Att", "",
                vehicle_disp, "", (tds_ledger if tds_amount > 0 else ""), (tds_amount if tds_amount > 0 else ""), narration
            ]
            ws.append(row)
            continue

        for trip in trips:
            job_no = trip.tr_enquirynumber.en_enquirynumber if trip.tr_enquirynumber else (trip.tr_tripnumber or "")
            customer_name = ""
            if trip.tr_enquirynumber and getattr(trip.tr_enquirynumber, 'en_customername', None):
                # attached billing used cu_name earlier
                try:
                    customer_name = trip.tr_enquirynumber.en_customername.cu_name
                except:
                    customer_name = str(trip.tr_enquirynumber.en_customername)

            transport_cost = float(trip.tc_tripcost or 0)
            expenses = []
            # Include transport and toll only; parking is excluded per request
            if transport_cost > 0:
                expenses.append(("Transportation", transport_cost))
            if trip.tc_tollcost and float(trip.tc_tollcost) > 0:
                expenses.append(("Toll", float(trip.tc_tollcost)))

            vehicle_disp = trip.tr_vehiclenumber or ""
            if vehicle_disp:
                vehicle_disp = f"{vehicle_disp} (A)"

            for exp_name, amt in expenses:
                row = [
                    voucher_number, bill_date, ref_no,
                    vendor_name if is_first_row else "",
                    total_amt if is_first_row else "",
                    exp_name, amt,
                    "Maa-Att", job_no, vehicle_disp, customer_name,
                    tds_ledger if is_first_row else "",
                    tds_amount if is_first_row and tds_amount > 0 else "",
                    narration
                ]
                ws.append(row)
                ws.cell(row=ws.max_row, column=6).fill = expense_fill
                is_first_row = False

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Attached_Bill_Tally_Export.xlsx"'
    wb.save(response)
    return response


@login_required(login_url='login_page')
def attached_bill_summary(request, id):
    """Return structured summary data for the bill summary modal."""
    bill = get_object_or_404(AttachedBillInfo, id=id)
    vehicle = bill.ab_vehicle_number
    vendor = bill.ab_vendor

    # --- Period info ---
    from_date = bill.ab_from_date
    to_date = bill.ab_to_date
    days_in_month = 0
    working_days = 0
    if from_date and to_date:
        days_in_month = (to_date - from_date).days + 1
    # --- Use SAVED bill fields for reliable values ---
    contract_amount = float(bill.ab_buy_cost or 0)
    
    # Recalculate working_days and leave_days based on the new 100% days rule
    working_days = days_in_month  # Denominator is now all days in the month
    leave_per_day = (contract_amount / working_days) if working_days > 0 else 0

    # Fetch ALL trips for this vehicle in the expanded range to calculate leave days correctly
    all_trip_dates = set()
    if vehicle:
        expanded_start = from_date - timedelta(days=1)
        expanded_end = to_date + timedelta(days=1)
        all_trips_in_period = TripdetailInfo.objects.filter(
            tr_vehiclenumber=vehicle.vm_registrationnumber,
            tr_departeddate__date__range=[expanded_start, expanded_end]
        )
        for t in all_trips_in_period:
            if t.tr_departeddate:
                sd = t.tr_departeddate.date()
                ed = (t.tr_reporteddate_delivery or t.tr_reporteddate or t.tr_departeddate).date()
                curr_t = sd
                while curr_t <= ed:
                    all_trip_dates.add(curr_t)
                    curr_t += timedelta(days=1)

    # Use the reliably saved leave days and amount
    leave_days = bill.ab_leave_days or 0
    leave_amount = float(bill.ab_leave_amount or 0)
    agreed_km      = float(bill.ab_agreed_km or 0)
    total_km_saved = float(bill.ab_total_km_run or 0)   # saved total KM from ADD/EDIT
    extra_km       = float(bill.ab_extra_km_run or 0)
    extra_km_amount = float(bill.ab_extra_km_amount or 0)
    toll_cost      = float(bill.ab_toll_cost or 0)
    actual_amount  = float(bill.ab_bill_amount or 0)

    # --- Fetch selected trips ONLY ---
    selected_trip_numbers = [t.strip() for t in (bill.ab_selected_trips or '').split(',') if t.strip()]
    total_trips = len(selected_trip_numbers)

    trips = []
    if selected_trip_numbers:
        trip_filters = Q(tr_tripnumber__in=selected_trip_numbers)
        # Optional: verify vehicle and date range for data integrity
        if vehicle:
            trip_filters &= Q(tr_vehiclenumber=vehicle.vm_registrationnumber)
        
        trips = list(TripdetailInfo.objects.filter(trip_filters).select_related(
            'tr_departedlocation', 'tr_reportedlocation', 'tr_enquirynumber'
        ))

    # --- Fetch selected trips ONLY (for KM/Selling) ---
    selected_trip_numbers = [t.strip() for t in (bill.ab_selected_trips or '').split(',') if t.strip()]
    total_trips = len(selected_trip_numbers)
    trips = []
    if selected_trip_numbers:
        trip_filters = Q(tr_tripnumber__in=selected_trip_numbers)
        if vehicle:
            trip_filters &= Q(tr_vehiclenumber=vehicle.vm_registrationnumber)
        trips = list(TripdetailInfo.objects.filter(trip_filters).select_related(
            'tr_departedlocation', 'tr_reportedlocation', 'tr_enquirynumber'
        ))

    # trip_days for display in summary
    summary_billed_trip_dates = set()
    trip_km_run = 0
    for t in trips:
        start_km = t.tr_reportedkm_pickup if t.tr_reportedkm_pickup else (t.tr_departedkm or 0)
        closing_km = t.tr_reportedkm_delivery if t.tr_reportedkm_delivery else (t.tr_reportedkm or 0)
        if closing_km and start_km:
            diff = closing_km - start_km
            if 0 < diff < 15000:
                trip_km_run += diff
        if t.tr_departeddate:
            summary_billed_trip_dates.add(t.tr_departeddate.date())

    # Use saved total_km_run
    display_total_km = total_km_saved

    days_run   = len(summary_billed_trip_dates)
    trip_index = f"{total_trips} TRIPS / {days_run} DAYS RUN" if days_run else f"{total_trips} TRIPS"

    # --- Empty KM = Agreed KM − Total KM Run ---
    empty_km           = max(0.0, agreed_km - display_total_km)
    per_km_amount      = (actual_amount / total_km_saved) if total_km_saved > 0 else 0
    empty_km_buy_cost  = per_km_amount * empty_km
    business_empty_km          = empty_km
    business_empty_km_buy_cost = empty_km_buy_cost

    # --- Selling = sum of all trip charges billed to customer ---
    selling = 0.0
    for t in trips:
        selling += (float(t.tc_tripcost or 0) + float(t.tc_tollcost or 0) +
                    float(t.tc_supervisorcost or 0) + float(t.tc_loadingcost or 0) +
                    float(t.tc_unloadingcost or 0) + float(t.tc_weighmentcost or 0) +
                    float(t.tc_haltingcost or 0) + float(t.tc_handlingcost or 0))

    # --- Buying = actual bill amount paid to vendor ---
    buying = actual_amount

    # --- Profit / % ---
    profit   = selling - buying
    sell_pct = round((profit / selling) * 100, 2) if selling > 0 else 0
    buy_pct  = round((profit / buying)  * 100, 2) if buying  > 0 else 0

    # --- Title ---
    vendor_name  = vendor.vend_name if vendor else "N/A"
    period_label = from_date.strftime("%b %Y").upper() if from_date else ""
    title        = f"{vendor_name} - {period_label}"

    return JsonResponse({
        'title': title,
        'vehicle_no':   vehicle.vm_registrationnumber if vehicle else '',
        'vehicle_type': str(vehicle.vm_vehicletype) if vehicle and vehicle.vm_vehicletype else '',
        'days_in_month': days_in_month,
        'working_days':  working_days,
        'leave_days':    leave_days,
        'contract_amount': round(contract_amount, 2),
        'toll_cost':       round(toll_cost, 2),
        'leave_per_day':   round(leave_per_day, 2),
        'leave_amount':    round(leave_amount, 2),
        'extra_km':        round(extra_km, 2),
        'extra_km_amount': round(extra_km_amount, 2),
        'actual_amount':   round(actual_amount, 2),
        'total_trips': total_trips,
        'trip_index':  trip_index,
        'total_km':    round(display_total_km, 2),
        'agreed_km':   round(agreed_km, 2),
        'empty_km':              round(empty_km, 2),
        'per_km_amount':         round(per_km_amount, 2),
        'empty_km_buy_cost':     round(empty_km_buy_cost, 2),
        'business_empty_km':          round(business_empty_km, 2),
        'business_empty_km_buy_cost': round(business_empty_km_buy_cost, 2),
        'selling': round(selling, 2),
        'buying':  round(buying, 2),
        'profit':  round(profit, 2),
        'sell_pct': sell_pct,
        'buy_pct':  buy_pct,
    })


@login_required(login_url='login_page')
def get_vehicles_by_vendor(request):
    vendor_id = request.GET.get('vendor_id')
    if not vendor_id:
        return JsonResponse({'vehicles': []})
    
    # Ownership ID 2 = ATTACHED
    vehicles = VehiclemasterInfo.objects.filter(vm_vendor_id=vendor_id, vm_ownership_id=2).order_by('vm_registrationnumber')
    
    veh_list = []
    for v in vehicles:
        veh_list.append({
            'id': v.id,
            'reg_no': v.vm_registrationnumber
        })
    
    return JsonResponse({'vehicles': veh_list})
