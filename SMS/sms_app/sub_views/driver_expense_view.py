from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import driver_settlement_info
from ..sub_models.driver_expense_mod import Driverexpense
from ..sub_forms.driver_expense_form import DriverExpenseForm

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from ..sub_forms.driver_expense_form import DriverExpenseForm
from ..sub_models.driver_expense_mod import Driverexpense
from ..models import driver_settlement_info


@login_required(login_url='login_page')
def driver_expense_add(request, expense_id=0):
    settlement_id = request.GET.get('settlement_id')

    settlement = None
    if settlement_id:
        settlement = get_object_or_404(driver_settlement_info, pk=settlement_id)

    if request.method == "GET":
        if expense_id == 0:
            form = DriverExpenseForm()
        else:
            expense = get_object_or_404(Driverexpense, pk=expense_id)
            form = DriverExpenseForm(instance=expense)

        return render(request, "asset_mgt_app/driver_expense_add.html", {
            'form': form,
            'settlement': settlement
        })

    else:
        if expense_id == 0:
            form = DriverExpenseForm(request.POST)
        else:
            expense = get_object_or_404(Driverexpense, pk=expense_id)
            form = DriverExpenseForm(request.POST, instance=expense)

        if form.is_valid():
            exp = form.save(commit=False)

            # 🔒 FORCE settlement + driver data
            exp.driver_settlement = settlement
            exp.de_driver_name = settlement.driver_name
            exp.de_driver_id = settlement.driver_id_value

            exp.save()   # ✅ GUARANTEED SAVE
            return redirect('/SMS/driver_expense_list')

        return render(request, "asset_mgt_app/driver_expense_add.html", {
            'form': form,
            'settlement': settlement
        })

@login_required(login_url='login_page')
def driver_expense_list(request):
    context = {
        'expense_list': Driverexpense.objects.all()
    }
    return render(request, "asset_mgt_app/driver_expense_list.html", context)

@login_required(login_url='login_page')
def driver_expense_delete(request, expense_id):
    expense = get_object_or_404(Driverexpense, pk=expense_id)
    expense.delete()
    return redirect('/SMS/driver_expense_list')

@login_required(login_url='login_page')
def driver_expense_by_driver(request):
    driver_id = request.GET.get('driver_id')

    expenses = Driverexpense.objects.filter(
        driverexpense__dm_id=driver_id
    ).select_related('expense_type').values(
        'expense_type__exp_category_name',   # ✅ FIXED
        'expense_type__id'
    ).annotate(
        total_amount=Sum('de_amount')
    )

    return JsonResponse(list(expenses), safe=False)
