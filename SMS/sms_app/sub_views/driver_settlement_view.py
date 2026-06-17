from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.dateparse import parse_date

from ..forms import DriverSettlementForm
from ..models import driver_settlement_info,Driverexpense
from ..sub_models.driver_master_mod import DrivermasterInfo
from ..sub_models.tripdetail_mod import TripdetailInfo

@login_required(login_url='login_page')
def driver_settlement_add(request, ds_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    settlement = None
    expense_list = Driverexpense.objects.none()

    # ---------- GET ----------
    if request.method == "GET":
        if ds_id == 0:
            form = DriverSettlementForm()
        else:
            settlement = get_object_or_404(driver_settlement_info, pk=ds_id)
            form = DriverSettlementForm(instance=settlement)

            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')

            expense_qs = Driverexpense.objects.filter(de_driver_id=settlement)

            if start_date:
                expense_qs = expense_qs.filter(de_date__date__gte=parse_date(start_date))

            if end_date:
                expense_qs = expense_qs.filter(de_date__date__lte=parse_date(end_date))

            expense_list = expense_qs.order_by('-de_date')

            # Build a trip_number -> TripdetailInfo lookup for C-Note display
            trip_numbers = [
                str(e.trip_number).strip() for e in expense_list
                if e.trip_number and str(e.trip_number).strip()
            ]
            trip_lookup = {}
            if trip_numbers:
                for t in TripdetailInfo.objects.filter(
                    tr_tripnumber__in=trip_numbers
                ).select_related('tr_consignmentnumber'):
                    trip_lookup[str(t.tr_tripnumber).strip()] = t

            # Attach extra fields to each expense (avoids N+1 in template)
            for exp in expense_list:
                tn = str(exp.trip_number).strip() if exp.trip_number else ''
                matched_trip = trip_lookup.get(tn)
                exp.cnote = (
                    matched_trip.tr_consignmentnumber.co_consignmentnumber
                    if matched_trip and matched_trip.tr_consignmentnumber
                    else ''
                )

        return render(request, "asset_mgt_app/driver_settlement_add.html", {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'settlement': settlement,
            'expense_list': expense_list,
        })

    # ---------- POST ----------
    # ---------- POST ----------
    if ds_id == 0:
        form = DriverSettlementForm(request.POST)
    else:
        settlement_obj = get_object_or_404(driver_settlement_info, pk=ds_id)
        form = DriverSettlementForm(request.POST, instance=settlement_obj)

    if form.is_valid():
        settlement = form.save(commit=False)

        # 🔑 Snapshot driver master details
        driver = settlement.driver
        settlement.driver_id_value = driver.dm_id
        settlement.driver_name = driver.dm_name
        settlement.driver_phone = driver.dm_drivernumber
        settlement.driver_licence = driver.dm_driver_lic
        settlement.driver_licence_expiry = driver.dm_driver_lic_expiry

        settlement.save()

        messages.success(request, "Driver settlement updated successfully")
        return redirect('driver_settlement_list')

    messages.error(request, "Record not saved. Please fill all required fields")
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required(login_url='login_page')
def driver_settlement_list(request):
    first_name = request.session.get('first_name')

    settlements = driver_settlement_info.objects.select_related(
        'driver'
    ).order_by('-id')

    driver_id = request.GET.get('driver_id')
    if driver_id:
        settlements = settlements.filter(driver__dm_id=driver_id)

    totals = settlements.aggregate(
        total_advance=Sum('ds_tripadvance'),
        total_balance=Sum('ds_balance')
    )

    context = {
        'driver_settlement_list': settlements,
        'drivers': DrivermasterInfo.objects.all().order_by('dm_name'),
        'selected_driver': driver_id,
        'total_advance': totals['total_advance'] or 0,
        'total_balance': totals['total_balance'] or 0,
        'first_name': first_name,
    }

    return render(request, "asset_mgt_app/driver_settlement_list.html", context)

@login_required(login_url='login_page')
def driver_settlement_delete(request, ds_id):
    settlement = get_object_or_404(driver_settlement_info, pk=ds_id)
    settlement.delete()
    messages.success(request, "Driver settlement deleted successfully")
    return redirect('driver_settlement_list')

@login_required(login_url='login_page')
def get_trip_totalcost(request):
    trip_id = request.GET.get('trip_id')

    try:
        trip = TripdetailInfo.objects.get(id=trip_id)

        details = {
            'Trip Charges': trip.tc_tripcost or 0,
            'Parking Charges': trip.tc_parkingcost or 0,
            'Toll Charges': trip.tc_tollcost or 0,
            'Loading Charges': trip.tc_loadingcost or 0,
            'Unloading Charges': trip.tc_unloadingcost or 0,
            'Weighment Charges': trip.tc_weighmentcost or 0,
            'Handling Charges': trip.tc_handlingcost or 0,
            'Halting Charges': trip.tc_haltingcost or 0,
            'Supervisor Charges': trip.tc_supervisorcost or 0,
        }

        return JsonResponse({
            'details': details,
            'total_cost': sum(details.values())
        })

    except TripdetailInfo.DoesNotExist:
        return JsonResponse({'details': {}, 'total_cost': 0})

@login_required(login_url='login_page')
def get_driver_details_from_master(request):
    driver_id = request.GET.get('driver_id')

    if not driver_id:
        return JsonResponse({})

    try:
        driver = DrivermasterInfo.objects.get(id=driver_id)
        return JsonResponse({
            'driver_id': driver.id,                     # primary key
            'driver_code': driver.dm_id,                # business driver id (optional)
            'driver_name': driver.dm_name,
            'phone': driver.dm_drivernumber,
            'licence': driver.dm_driver_lic,
            'licence_expiry': driver.dm_driver_lic_expiry  # ✅ NEW
        })
    except DrivermasterInfo.DoesNotExist:
        return JsonResponse({})

def recalc_driver_settlement(settlement):
    """
    Recalculate total advance, total expense, and balance
    """

    advance_total = Driverexpense.objects.filter(
        de_driver_id=settlement,
        de_expense_type__id=1   # ADVANCE
    ).aggregate(total=Sum('de_total_cost'))['total'] or 0

    expense_total = Driverexpense.objects.filter(
        de_driver_id=settlement,
        de_expense_type__id=2   # EXPENSE
    ).aggregate(total=Sum('de_total_cost'))['total'] or 0

    settlement.ds_tripadvance = advance_total
    settlement.ds_tripexpense = expense_total
    settlement.ds_balance = advance_total - expense_total
    settlement.save(update_fields=[
        'ds_tripadvance',
        'ds_tripexpense',
        'ds_balance'
    ])