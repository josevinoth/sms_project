from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .driver_settlement_view import recalc_driver_settlement
from ..models import Driverexpense,TripdetailInfo,driver_settlement_info
from ..sub_forms.driver_expense_form import DriverExpenseForm
from datetime import datetime

from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

@login_required(login_url='login_page')
def driver_expense_add(request, expense_id=0):
    first_name = request.session.get('first_name')

    expense = None
    settlement = None

    # ================= 1️⃣ RESOLVE SETTLEMENT FIRST =================
    if expense_id:
        # EDIT MODE
        expense = get_object_or_404(Driverexpense, pk=expense_id)
        settlement = expense.de_driver_id
    else:
        # ADD MODE
        settlement_id = request.GET.get('settlement_id')
        driver_master_id = request.GET.get('driver_master_id')

        if settlement_id:
            settlement = get_object_or_404(driver_settlement_info, id=settlement_id)
        elif driver_master_id:
            from ..sub_models.driver_master_mod import DrivermasterInfo
            master = get_object_or_404(DrivermasterInfo, id=driver_master_id)
            # Auto-create settlement record if it doesn't exist
            settlement, created = driver_settlement_info.objects.get_or_create(
                driver=master,
                defaults={
                    'driver_id_value': master.dm_id,
                    'driver_name': master.dm_name,
                    'driver_phone': master.dm_drivernumber,
                    'driver_licence': master.dm_driver_lic,
                    'driver_licence_expiry': master.dm_driver_lic_expiry
                }
            )
        else:
            messages.error(request, "Please open expense from Driver Settlement")
            return redirect('driver_settlement_list')

    # ================= 2️⃣ CALCULATE TOTALS (AFTER settlement) =================
    advance_total = Driverexpense.objects.filter(
        de_driver_id=settlement,
        de_expense_type__id=1   # ADVANCE
    ).aggregate(t=Sum('de_total_cost'))['t'] or 0

    expense_total = Driverexpense.objects.filter(
        de_driver_id=settlement,
        de_expense_type__id=2   # EXPENSE
    ).aggregate(t=Sum('de_total_cost'))['t'] or 0

    current_balance = advance_total - expense_total

    # ================= 3️⃣ POST =================
    if request.method == "POST":
        form = DriverExpenseForm(request.POST, instance=expense, settlement=settlement)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.driver_name = settlement.driver
            exp.de_driver_id = settlement
            exp.save()

            # 🔥 ALWAYS recalc after save
            recalc_driver_settlement(settlement)

            messages.success(request, "Driver expense saved successfully ✅")
            return redirect('driver_settlement_update', ds_id=settlement.id)

    # ================= 4️⃣ GET =================
    else:
        if expense:
            form = DriverExpenseForm(instance=expense,settlement=settlement)
        else:
            initial_data = {'driver_name': settlement.driver}
            
            trip_id = request.GET.get('trip_id')
            if trip_id:
                initial_data['trip_number'] = trip_id
                initial_data['de_expense_type'] = 2  # Preselect Expense
                # Try prepopulating date too
                try:
                    trip = TripdetailInfo.objects.get(id=trip_id)
                    if trip.tr_departeddate:
                        initial_data['trip_date'] = trip.tr_departeddate.date()
                except TripdetailInfo.DoesNotExist:
                    pass

            form = DriverExpenseForm(
                initial=initial_data,
                settlement=settlement
            )

    # ================= 5️⃣ RENDER =================
    return render(request, "asset_mgt_app/driver_expense_add.html", {
        'form': form,
        'first_name': first_name,
        'settlement': settlement,
        'advance_total': advance_total,
        'expense_total': expense_total,
        'current_balance': current_balance,
        'auto_trip_id': request.GET.get('trip_id') if not expense else None
    })


# ============================================================
# LIST DRIVER EXPENSE
# ============================================================
@login_required(login_url='login_page')
def driver_expense_list(request):
    first_name = request.session.get('first_name')

    context = {
        'expense_list': Driverexpense.objects.all().order_by('-id'),
        'first_name': first_name
    }

    return render(
        request,
        "asset_mgt_app/driver_expense_list.html",
        context
    )


@login_required(login_url='login_page')
def driver_expense_delete(request, expense_id):
    expense = get_object_or_404(Driverexpense, pk=expense_id)
    settlement = expense.de_driver_id

    expense.delete()

    # 🔥 RECALC AFTER DELETE
    recalc_driver_settlement(settlement)

    messages.success(request, "Driver expense deleted successfully 🗑️")
    return redirect('driver_settlement_add', ds_id=settlement.id)

def get_trip_charges(request):
    trip_id = request.GET.get('trip_id')

    if not trip_id:
        return JsonResponse({'error': 'No trip id'}, status=400)

    try:
        if str(trip_id).isdigit():
            trip = TripdetailInfo.objects.get(id=trip_id)
        else:
            trip = TripdetailInfo.objects.get(tr_tripnumber=trip_id)

        data = {
            # COSTS
            'parking': trip.tc_parkingcost or 0,
            'loading': trip.tc_loadingcost or 0,
            'unloading': trip.tc_unloadingcost or 0,
            'weighment': trip.tc_weighmentcost or 0,
            'supervisor': trip.tc_supervisorcost or 0,
            'rto': trip.tc_rtocost or 0,
            'batta': trip.tc_betacost or 0,

            # 🔥 NEW DETAILS
            'vehicle_number': trip.tr_vehiclenumber or "",
            'from_location': trip.tr_departedlocation.place_name if trip.tr_departedlocation else "",
            'to_location': trip.tr_reportedlocation.place_name if trip.tr_reportedlocation else "",
        }

        data['total'] = sum([
            data['parking'],
            data['loading'],
            data['unloading'],
            data['weighment'],
            data['supervisor'],
            data['rto'],
            data['batta'],
        ])

        return JsonResponse(data)

    except TripdetailInfo.DoesNotExist:
        return JsonResponse({'error': 'Trip not found'}, status=404)

@login_required(login_url='login_page')
def filter_trips_by_date(request):
    trip_date = request.GET.get('trip_date')
    settlement_id = request.GET.get('settlement_id')

    if not trip_date or not settlement_id:
        return JsonResponse([], safe=False)

    # ✅ FIX FORMAT (strip time if present)
    if 'T' in trip_date:
        trip_date = trip_date.split('T')[0]

    try:
        trip_date = datetime.strptime(trip_date, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse([], safe=False)

    settlement = get_object_or_404(driver_settlement_info, id=settlement_id)

    qs = TripdetailInfo.objects.filter(
        tc_financestatus__id__in=[5, 7, 9]
    )

    # Filter by driver
    if getattr(settlement, 'driver_master_id', None):
        qs = qs.filter(tr_driver_master_id=settlement.driver_master_id)
    else:
        qs = qs.filter(tr_drivername=settlement.driver)

    # ✅ FILTER BY DATE
    qs = qs.filter(tr_departeddate__date=trip_date)

    data = [
        {
            'id': t.id, 
            'trip_number': t.tr_tripnumber,
            'vehicle': t.tr_vehiclenumber,
            'from': t.tr_departedlocation.place_name if t.tr_departedlocation else "",
            'to': t.tr_reportedlocation.place_name if t.tr_reportedlocation else "",
            'date': t.tr_departeddate.strftime('%Y-%m-%d') if t.tr_departeddate else "",
            'parking': t.tc_parkingcost or 0,
            'loading': t.tc_loadingcost or 0,
            'unloading': t.tc_unloadingcost or 0,
            'weighment': t.tc_weighmentcost or 0,
            'supervisor': t.tc_supervisorcost or 0,
            'rto': t.tc_rtocost or 0,
            'batta': t.tc_betacost or 0
        }
        for t in qs
    ]

    return JsonResponse(data, safe=False)
