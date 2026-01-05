from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .driver_settlement_view import recalc_driver_settlement
from ..models import Driverexpense,TripdetailInfo,driver_settlement_info
from ..sub_forms.driver_expense_form import DriverExpenseForm


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
        if not settlement_id:
            messages.error(request, "Please open expense from Driver Settlement")
            return redirect('driver_settlement_list')

        settlement = get_object_or_404(driver_settlement_info, id=settlement_id)

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
            form = DriverExpenseForm(
                initial={'driver_name': settlement.driver},
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
        trip = TripdetailInfo.objects.get(id=trip_id)

        data = {
            'parking': trip.tc_parkingcost or 0,
            'loading': trip.tc_loadingcost or 0,
            'unloading': trip.tc_unloadingcost or 0,
            'weighment': trip.tc_weighmentcost or 0,
            'supervisor': trip.tc_supervisorcost or 0,
        }

        data['total'] = sum(data.values())

        return JsonResponse(data)

    except TripdetailInfo.DoesNotExist:
        return JsonResponse({'error': 'Trip not found'}, status=404)