from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import driver_settlement_info
from ..sub_models.driver_expense_mod import Driverexpense
from ..sub_forms.driver_expense_form import DriverExpenseForm


@login_required(login_url='login_page')
def driver_expense_add(request):

    if request.method == "POST":
        form = DriverExpenseForm(request.POST)
        next_url = request.POST.get('next')   # ✅ READ FROM POST

        if form.is_valid():
            form.save()
            messages.success(request, "Expense Saved")

            if next_url:
                return redirect(next_url)

            return redirect('driver_settlement_list')

    else:
        form = DriverExpenseForm()
        next_url = request.GET.get('next')    # ✅ READ FROM GET

    return render(request, 'asset_mgt_app/driver_expense_add.html', {
        'form': form,
        'next': next_url
    })


# ============================================================
# UPDATE DRIVER EXPENSE
# ============================================================
@login_required(login_url='login_page')
def driver_expense_update(request, exp_id):
    expense = get_object_or_404(Driverexpense, id=exp_id)
    settlement = expense.driver_settlement_info

    if request.method == "POST":
        form = DriverExpenseForm(request.POST, instance=expense)

        if form.is_valid():
            exp = form.save(commit=False)

            # 🔒 Keep settlement & driver fixed
            exp.driver_settlement_info = settlement
            exp.de_driver_name = settlement.staff_name
            exp.de_driver_id = settlement.staff_id.username

            exp.save()

            messages.success(request, "Driver Expense updated successfully")
            return redirect('driver_settlement_update', settlement.id)

    else:
        form = DriverExpenseForm(instance=expense)

    return render(request, "asset_mgt_app/driver_expense_add.html", {
        'form': form,
        'settlement': settlement,
    })


# ============================================================
# DELETE DRIVER EXPENSE
# ============================================================
@login_required(login_url='login_page')
def driver_expense_delete(request, exp_id):
    expense = get_object_or_404(Driverexpense, id=exp_id)
    settlement_id = expense.driver_settlement_info.id

    expense.delete()
    messages.success(request, "Driver Expense deleted successfully")

    return redirect('driver_settlement_update', settlement_id)


# ============================================================
# DRIVER EXPENSE LIST (OPTIONAL / STANDALONE)
# ============================================================
@login_required(login_url='login_page')
def driver_expense_list(request):
    expenses = Driverexpense.objects.select_related(
        'driver_settlement_info'
    ).order_by('-id')

    return render(request, "asset_mgt_app/driver_expense_list.html", {
        'expense_list': expenses
    })


@login_required(login_url='login_page')
def driver_expense_by_driver(request):
    driver_id = request.GET.get('driver_id')

    if not driver_id:
        return JsonResponse([], safe=False)

    expenses = Driverexpense.objects.filter(
        de_driver_id=driver_id
    ).values(
        'id',
        'de_driver_name',
        'de_driver_id',
        'de_expense_type__ds_exp_category_name',
        'de_parkingcost',
        'de_loadingcost',
        'de_unloadingcost',
        'de_weighmentcost',
        'de_supervisorcost',
        'de_total_cost'
    )

    data = []
    for exp in expenses:
        data.append({
            'id': exp['id'],
            'de_driver_name': exp['de_driver_name'],
            'de_driver_id': exp['de_driver_id'],
            'de_expense_type': exp['de_expense_type'],
            'de_parkingcost': exp['de_parkingcost'],
            'de_loadingcost': exp['de_loadingcost'],
            'de_unloadingcost': exp['de_unloadingcost'],
            'de_weighmentcost': exp['de_weighmentcost'],
            'de_supervisorcost': exp['de_supervisorcost'],
            'de_total_cost': exp['de_total_cost'],
        })

    return JsonResponse(data, safe=False)