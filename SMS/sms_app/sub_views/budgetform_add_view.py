from django.contrib.auth.decorators import login_required
from ..forms import BudgetForm
from ..models import BudgetInfo
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.core.paginator import Paginator


@login_required(login_url='login_page')
def budgetform_add(request,budget_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if budget_id == 0:
            print("I am inside Get add budgetform")
            form = BudgetForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
            }
        else:
            print("I am inside get edit budgetform")
            budget = BudgetInfo.objects.get(pk=budget_id)
            form = BudgetForm(instance=budget)
            context = {
                'form': form,
                'first_name': first_name,
            }
        return render(request, "asset_mgt_app/budgetform_add.html", context)

    else:
        if budget_id == 0:
            form = BudgetForm(request.POST)
        else:
            budget = BudgetInfo.objects.get(pk=budget_id)
            form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            if budget_id == 0:
                messages.success(request, 'Record Saved Successfully')
            else:
                messages.success(request, 'Record Updated Successfully')
        else:
            messages.error(request, 'Error: Please correct the errors below.')

        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error in {field}: {error}")
                messages.error(request, f"Error in {field}: {error}")
        return redirect(request.META['HTTP_REFERER'])


# List bay
@login_required(login_url='login_page')
def budgetform_list(request):
    first_name = request.session.get('first_name')
    budget_list = BudgetInfo.objects.all()
    context = {'budget_list': budget_list, 'first_name': first_name}
    return render(request, "asset_mgt_app/budgetform_list.html", context)

#Delete bay
@login_required(login_url='login_page')
def budgetform_delete(request,budget_id):
    budget = BudgetInfo.objects.get(pk=budget_id)
    budget.delete()
    return redirect('/SMS/budget_form_list')


@login_required(login_url='login_page')
def budgetform_clone(request, budget_id):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    budget = get_object_or_404(BudgetInfo, pk=budget_id)
    if request.method == "GET":
        form = BudgetForm(initial={
            'bf_start_date_year': budget.bf_start_date_year,
            'bf_Airport_Handling_Charges': budget.bf_Airport_Handling_Charges,
            'bf_Crane_Handling_Charges': budget.bf_Crane_Handling_Charges,
            'bf_Forklift_Handling_Charges': budget.bf_Forklift_Handling_Charges,
            'bf_Handling_Charges': budget.bf_Handling_Charges,
            'bf_Packing_Charges': budget.bf_Packing_Charges,
            'bf_Warehouse_Handling_Charges': budget.bf_Warehouse_Handling_Charges,
            'bf_Warehouse_Loading_Charges': budget.bf_Warehouse_Loading_Charges,
            'bf_Warehouse_Storage_Charges': budget.bf_Warehouse_Storage_Charges,
            'bf_Warehouse_Unloading_Charges': budget.bf_Warehouse_Unloading_Charges,
            'bf_audit_fees': budget.bf_audit_fees,
            'bf_bad_debts': budget.bf_bad_debts,
            'bf_bank_charges': budget.bf_bank_charges,
            'bf_celebration_expenses': budget.bf_celebration_expenses,
            'bf_consultancy_charges': budget.bf_consultancy_charges,
            'bf_directors_remuneration': budget.bf_directors_remuneration,
            'bf_insurance_car': budget.bf_insurance_car,
            'bf_interest_on_statutory_dues': budget.bf_interest_on_statutory_dues,
            'bf_professional_legal_charges': budget.bf_professional_legal_charges,
            'bf_subscription_membership': budget.bf_subscription_membership,
            'bf_corp_staff': budget.bf_corp_staff,
            'bf_bonus_corp_staff': budget.bf_bonus_corp_staff,
            'bf_EDLI_contribution_corp_staff': budget.bf_EDLI_contribution_corp_staff,
            'bf_employer_contribution_to_ESI_corp_staff': budget.bf_employer_contribution_to_ESI_corp_staff,
            'bf_employer_contribution_to_PF_corp_staff': budget.bf_employer_contribution_to_PF_corp_staff,
            'bf_EPF_admin_charges_corp_staff': budget.bf_EPF_admin_charges_corp_staff,
            'bf_gratuity_corp_staff': budget.bf_gratuity_corp_staff,
            'bf_salaries_wages_corp_staff': budget.bf_salaries_wages_corp_staff,
            'bf_dept_staff': budget.bf_dept_staff,
            'bf_bonus_staff': budget.bf_bonus_staff,
            'bf_EDLI_contribution_staff': budget.bf_EDLI_contribution_staff,
            'bf_employer_contribution_to_ESI_staff': budget.bf_employer_contribution_to_ESI_staff,
            'bf_employer_contribution_to_PF_staff': budget.bf_employer_contribution_to_PF_staff,
            'bf_EPF_admin_charges_staff': budget.bf_EPF_admin_charges_staff,
            'bf_gratuity_staff': budget.bf_gratuity_staff,
            'bf_salaries_wages_staff': budget.bf_salaries_wages_staff,
            'bf_interest_on_borrowings': budget.bf_interest_on_borrowings,
            'bf_interest_on_other_loans': budget.bf_interest_on_other_loans,
            'bf_fixed': budget.bf_fixed,
            'bf_depreciation': budget.bf_depreciation,
            'bf_software_AMC_charges': budget.bf_software_AMC_charges,
            'bf_insurance_warehouse': budget.bf_insurance_warehouse,
            'bf_rates_taxes': budget.bf_rates_taxes,
            'bf_rent_premises': budget.bf_rent_premises,
            'bf_security_service_charges': budget.bf_security_service_charges,
            'bf_manpower_supply_expenses': budget.bf_manpower_supply_expenses,
            'bf_variable': budget.bf_variable,
            'bf_crane_handling_expenses': budget.bf_crane_handling_expenses,
            'bf_diesel_expenses_forklift': budget.bf_diesel_expenses_forklift,
            'bf_forklift_handling_expenses': budget.bf_forklift_handling_expenses,
            'bf_fumigation_expenses': budget.bf_fumigation_expenses,
            'bf_oe_Fixed': budget.bf_oe_Fixed,
            'bf_housekeeping_salary': budget.bf_housekeeping_salary,
            'bf_insurance_corp_staff': budget.bf_insurance_corp_staff,
            'bf_insurance_staff': budget.bf_insurance_staff,
            'bf_internet_data_card_expenses': budget.bf_internet_data_card_expenses,
            'bf_rent_plant_machinery': budget.bf_rent_plant_machinery,
            'bf_system_amc': budget.bf_system_amc,
            'bf_oe_variable': budget.bf_oe_variable,
            'bf_advertisement_business_promotion': budget.bf_advertisement_business_promotion,
            'bf_conveyance_expenses': budget.bf_conveyance_expenses,
            'bf_diesel_expenses_gense': budget.bf_diesel_expenses_gense,
            'bf_handling_expenses': budget.bf_handling_expenses,
            'bf_hotel_boarding_lodging_expenses': budget.bf_hotel_boarding_lodging_expenses,
            'bf_office_repairs_maintenance': budget.bf_office_repairs_maintenance,
            'bf_office_supplies_general_expenses': budget.bf_office_supplies_general_expenses,
            'bf_postage_courier': budget.bf_postage_courier,
            'bf_power_fuel': budget.bf_power_fuel,
            'bf_printing_stationery': budget.bf_printing_stationery,
            'bf_service_maintenance_expenses': budget.bf_service_maintenance_expenses,
            'bf_staff_welfare_staff': budget.bf_staff_welfare_staff,
            'bf_telephone_mobile_expenses': budget.bf_telephone_mobile_expenses,
            'bf_training_expenses': budget.bf_training_expenses,
            'bf_travelling_expenses': budget.bf_travelling_expenses,
        })
        context = {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
        }
        return render(request, "asset_mgt_app/budgetform_add.html", context)

    elif request.method == "POST":
        form = BudgetForm(request.POST)
        if form.is_valid():
            unique_start_date = form.cleaned_data['bf_start_date_year']
            year = unique_start_date.year
            month = unique_start_date.month
            existing_budget = BudgetInfo.objects.filter(bf_start_date_year__year=year,bf_start_date_year__month=month).exists()
            if existing_budget:
                messages.error(request, f'A budget record for {unique_start_date.strftime("%B %Y")} already exists.')
            else:
                cloned_budget = form.save(commit=False)
                cloned_budget.created_by = request.user
                cloned_budget.save()
                messages.success(request, 'Budget record cloned successfully.')
                return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
            messages.error(request, 'Form is not valid. Please correct the errors.')

        return redirect(request.META.get('HTTP_REFERER', '/'))



