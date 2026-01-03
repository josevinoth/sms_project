from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .driver_settlement_view import recalc_driver_settlement
from ..models import Driverexpense
from ..sub_forms.driver_expense_form import DriverExpenseForm
from ..sub_models.driversettlement_mod import driver_settlement_info


@login_required(login_url='login_page')
def driver_expense_add(request, expense_id=0):
    first_name = request.session.get('first_name')

    # 1️⃣ GET settlement_id ONLY from URL
    settlement_id = request.GET.get('settlement_id')
    if not settlement_id:
        messages.error(request, "Please open expense from Driver Settlement")
        return redirect('driver_settlement_list')

    settlement = get_object_or_404(driver_settlement_info, id=settlement_id)

    expense = None
    if expense_id:
        expense = get_object_or_404(Driverexpense, pk=expense_id)

    # ================= POST =================
    if request.method == "POST":
        form = DriverExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.driver_name = settlement.driver
            exp.de_driver_id = settlement
            exp.save()

            messages.success(request, "Driver expense saved successfully ✅")
            return redirect(f"/SMS/driver_settlement_update/{settlement.id}/")
    # ================= GET =================
    else:
        if expense:
            # EDIT MODE
            form = DriverExpenseForm(instance=expense)
        else:
            # ADD MODE ✅ IMPORTANT
            form = DriverExpenseForm(initial={
                'driver_name': settlement.driver,
            })

    return render(request, "asset_mgt_app/driver_expense_add.html", {
        'form': form,
        'first_name': first_name,
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

