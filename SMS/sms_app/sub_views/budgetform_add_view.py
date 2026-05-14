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
            instance = form.save(commit=False)

            # Add the corp staff calculation logic here:
            instance.bf_corp_staff = (
                    (instance.bf_bonus_corp_staff or 0) +
                    (instance.bf_EDLI_contribution_corp_staff or 0) +
                    (instance.bf_employer_contribution_to_ESI_corp_staff or 0) +
                    (instance.bf_employer_contribution_to_PF_corp_staff or 0)+
                    (instance.bf_EPF_admin_charges_corp_staff or 0) +
                    (instance.bf_exgratia_corp_staff or 0) +
                    (instance.bf_gratuity_corp_staff or 0) +
                    (instance.bf_incentive_corp_staff or 0) +
                    (instance.bf_insurance_corp_staff or 0) +
                    (instance.bf_lwf_corp_staff or 0) +
                    (instance.bf_salaries_wages_corp_staff or 0)
            )
            instance.bf_dept_staff = (
                    (instance.bf_bonus_staff or 0) +
                    (instance.bf_EDLI_contribution_staff or 0) +
                    (instance.bf_employer_contribution_to_ESI_staff or 0) +
                    (instance.bf_employer_contribution_to_PF_staff or 0) +
                    (instance.bf_EPF_admin_charges_staff or 0) +
                    (instance.bf_exgratia_dept_staff or 0) +
                    (instance.bf_gratuity_staff or 0) +
                    (instance.bf_incentive_dept_staff or 0) +
                    (instance.bf_insurance_staff or 0) +
                    (instance.bf_lwf_dept_staff or 0) +
                    (instance.bf_salaries_wages_staff or 0)
            )
            instance.bf_driver_staff = (
                    (instance.bf_bonus_drivers or 0) +
                    (instance.bf_EDLI_contribution_drivers or 0) +
                    (instance.bf_employer_contribution_to_ESI_drivers or 0) +
                    (instance.bf_employer_contribution_to_PF_drivers or 0) +
                    (instance.bf_EPF_admin_charges_drivers or 0) +
                    (instance.bf_exgratia_drivers or 0) +
                    (instance.bf_gratuity_drivers or 0) +
                    (instance.bf_incentive_drivers or 0) +
                    (instance.bf_insurance_drivers or 0) +
                    (instance.bf_lwf_drivers or 0) +
                    (instance.bf_salaries_wages_drivers or 0)
            )
            instance.bf_fixed = (
                    (instance.bf_insurance_warehouse or 0) +
                    (instance.bf_insurance_wcc or 0) +
                    (instance.bf_rent_premises or 0) +
                    (instance.bf_security_service_charges or 0) +
                    (instance.bf_manpower_supply_expenses or 0) +
                    (instance.bf_gprs_access_service or 0) +
                    (instance.bf_insurance_vehicles or 0) +
                    (instance.bf_vehicle_hire or 0)
            )
            instance.bf_variable = (
                    (instance.bf_crane_handling_expenses or 0) +
                    (instance.bf_diesel_expenses_forklift or 0) +
                    (instance.bf_forklift_handling_expenses or 0) +
                    (instance.bf_packing_services or 0) +
                    (instance.bf_support_handling or 0) +
                    (instance.bf_fumigation_expenses or 0) +
                    (instance.bf_acting_driver or 0) +
                    (instance.bf_cng or 0) +
                    (instance.bf_diesel_vehicle or 0) +
                    (instance.bf_driver_betta or 0) +
                    (instance.bf_extra_hrs or 0) +
                    (instance.bf_extra_km or 0) +
                    (instance.bf_halting or 0) +
                    (instance.bf_loading or 0) +
                    (instance.bf_parking or 0) +
                    (instance.bf_rates_taxes or 0) +
                    (instance.bf_toll or 0) +
                    (instance.bf_transportation or 0) +
                    (instance.bf_unloading or 0) +
                    (instance.bf_vehicle_maintenance or 0) +
                    (instance.bf_weighment or 0)
            )
            instance.bf_oe_Fixed = (
                    (instance.bf_amc or 0) +
                    (instance.bf_depreciation or 0) +
                    (instance.bf_internet_data_card_expenses or 0) +
                    (instance.bf_rent_plant_machinery or 0) +
                    (instance.bf_software_AMC_charges or 0)
            )
            instance.bf_oe_variable = (
                    (instance.bf_CGST_ineligible_ITC or 0) +
                    (instance.bf_conveyance_expenses or 0) +
                    (instance.bf_diesel_expenses_gense or 0) +
                    (instance.bf_handling_expenses or 0) +
                    (instance.bf_hotel_boarding_lodging_expenses or 0) +
                    (instance.bf_IGST_ineligible_ITC or 0) +
                    (instance.bf_office_supplies_general_expenses or 0)+
                    (instance.bf_postage_courier or 0) +
                    (instance.bf_power_fuel or 0) +
                    (instance.bf_printing_stationery or 0) +
                    (instance.bf_service_maintenance_expenses or 0) +
                    (instance.bf_SGST_ineligible_ITC or 0) +
                    (instance.bf_staff_welfare_staff or 0) +
                    (instance.bf_telephone_mobile_expenses or 0) +
                    (instance.bf_training_expenses or 0) +
                    (instance.bf_travelling_expenses or 0)
            )
            instance.save()
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

    # Initialize subtotal variables
    income_total = 0
    department_expenses_total = 0
    employee_benefits_total = 0

    operational_expenses_total = 0
    non_operational_expenses_total = 0
    overall_total = 0

    # Calculate subtotals
    for budget in budget_list:
        income_total += (
                budget.bf_Airport_Handling_Charges +
                budget.bf_Crane_Handling_Charges +
                budget.bf_Forklift_Handling_Charges +
                budget.bf_Handling_Charges +
                budget.bf_Packing_Charges +
                budget.bf_Warehouse_Handling_Charges +
                budget.bf_Warehouse_Loading_Charges +
                budget.bf_Warehouse_Storage_Charges +
                budget.bf_Warehouse_Unloading_Charges +
                (budget.bf_Halting_Charges or 0) +
                (budget.bf_Halting_Charges_SEZ or 0) +
                (budget.bf_Loading_Charges or 0) +
                (budget.bf_Parking_Charges or 0) +
                (budget.bf_Parking_Charges_SEZ or 0) +
                (budget.bf_Toll_Charges or 0) +
                (budget.bf_Transportation_Charges or 0) +
                (budget.bf_Transportation_Charges_Interstate or 0) +
                (budget.bf_Transportation_Charges_SEZ or 0) +
                (budget.bf_Transportation_Handling_Charges or 0) +
                (budget.bf_Transportation_Handling_Charges_SEZ or 0) +
                (budget.bf_Unloading_Charges or 0) +
                (budget.bf_Weighment_Charges or 0)
        )  # Assuming 'bf_fixed' is for Income

        department_expenses_total += (
                budget.bf_advertisement_business_promotion +
                budget.bf_bank_charges +
                budget.bf_celebration_expenses +
                budget.bf_consultancy_charges +
                budget.bf_directors_remuneration +
                budget.bf_housekeeping_salary +
                budget.bf_office_repairs_maintenance +
                budget.bf_interest_on_statutory_dues +
                budget.bf_professional_legal_charges +
                budget.bf_rent_furniture_fittings +
                budget.bf_rent_office +
                budget.bf_subscription_membership
        )

        employee_benefits_total += (
                budget.bf_corp_staff +
                budget.bf_dept_staff +
                (budget.bf_driver_staff or 0)
        )

        operational_expenses_total += (
                budget.bf_fixed +
                budget.bf_insurance_warehouse +
                budget.bf_insurance_wcc +
                budget.bf_rent_premises +
                budget.bf_security_service_charges +
                budget.bf_manpower_supply_expenses
        )

        non_operational_expenses_total += (
                budget.bf_oe_Fixed +
                budget.bf_depreciation +
                budget.bf_software_AMC_charges +
                budget.bf_amc +
                budget.bf_internet_data_card_expenses +
                budget.bf_rent_plant_machinery +
                budget.bf_oe_variable +
                budget.bf_CGST_ineligible_ITC +
                budget.bf_conveyance_expenses +
                budget.bf_diesel_expenses_gense +
                budget.bf_handling_expenses +
                budget.bf_hotel_boarding_lodging_expenses +
                budget.bf_IGST_ineligible_ITC +
                budget.bf_office_supplies_general_expenses +
                budget.bf_power_fuel +
                budget.bf_postage_courier +
                budget.bf_printing_stationery +
                budget.bf_service_maintenance_expenses +
                budget.bf_SGST_ineligible_ITC +
                budget.bf_staff_welfare_staff +
                budget.bf_telephone_mobile_expenses +
                budget.bf_training_expenses +
                budget.bf_travelling_expenses
        )

    # Calculate the overall total
    overall_total = (
            income_total + department_expenses_total + employee_benefits_total +
            operational_expenses_total + non_operational_expenses_total
    )
    income_total = round(income_total, 2)
    department_expenses_total = round(department_expenses_total, 2)
    employee_benefits_total = round(employee_benefits_total, 2)

    operational_expenses_total = round(operational_expenses_total, 2)
    non_operational_expenses_total = round(non_operational_expenses_total, 2)
    overall_total = round(overall_total, 2)

    context = {
        'budget_list': budget_list,
        'first_name': first_name,
        'income_total': income_total,
        'department_expenses_total': department_expenses_total,
        'employee_benefits_total': employee_benefits_total,

        'operational_expenses_total': operational_expenses_total,
        'non_operational_expenses_total': non_operational_expenses_total,
        'overall_total': overall_total,
    }

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
            'bf_company': budget.bf_company,
            'bf_location': budget.bf_location,
            'bf_unit_reference': budget.bf_unit_reference,
            'bf_Airport_Handling_Charges': budget.bf_Airport_Handling_Charges,
            'bf_Crane_Handling_Charges': budget.bf_Crane_Handling_Charges,
            'bf_Forklift_Handling_Charges': budget.bf_Forklift_Handling_Charges,
            'bf_Handling_Charges': budget.bf_Handling_Charges,
            'bf_Packing_Charges': budget.bf_Packing_Charges,
            'bf_Warehouse_Handling_Charges': budget.bf_Warehouse_Handling_Charges,
            'bf_Warehouse_Loading_Charges': budget.bf_Warehouse_Loading_Charges,
            'bf_Warehouse_Storage_Charges': budget.bf_Warehouse_Storage_Charges,
            'bf_Warehouse_Unloading_Charges': budget.bf_Warehouse_Unloading_Charges,
            'bf_advertisement_business_promotion':budget.bf_advertisement_business_promotion,
            'bf_bank_charges': budget.bf_bank_charges,
            'bf_celebration_expenses': budget.bf_celebration_expenses,
            'bf_consultancy_charges': budget.bf_consultancy_charges,
            'bf_directors_remuneration': budget.bf_directors_remuneration,
            'bf_office_repairs_maintenance':budget.bf_office_repairs_maintenance,
            'bf_housekeeping_salary': budget.bf_housekeeping_salary,
            'bf_interest_on_statutory_dues': budget.bf_interest_on_statutory_dues,
            'bf_professional_legal_charges': budget.bf_professional_legal_charges,
            'bf_rent_furniture_fittings':budget.bf_rent_furniture_fittings,
            'bf_rent_office':budget.bf_rent_office,
            'bf_subscription_membership': budget.bf_subscription_membership,
            'bf_corp_staff': budget.bf_corp_staff,
            'bf_bonus_corp_staff': budget.bf_bonus_corp_staff,
            'bf_EDLI_contribution_corp_staff': budget.bf_EDLI_contribution_corp_staff,
            'bf_employer_contribution_to_ESI_corp_staff': budget.bf_employer_contribution_to_ESI_corp_staff,
            'bf_employer_contribution_to_PF_corp_staff': budget.bf_employer_contribution_to_PF_corp_staff,
            'bf_EPF_admin_charges_corp_staff': budget.bf_EPF_admin_charges_corp_staff,
            'bf_exgratia_corp_staff':budget.bf_exgratia_corp_staff,
            'bf_gratuity_corp_staff': budget.bf_gratuity_corp_staff,
            'bf_incentive_corp_staff':budget.bf_incentive_corp_staff,
            'bf_insurance_corp_staff':budget.bf_insurance_corp_staff,
            'bf_lwf_corp_staff':budget.bf_lwf_corp_staff,
            'bf_salaries_wages_corp_staff': budget.bf_salaries_wages_corp_staff,
            'bf_dept_staff': budget.bf_dept_staff,
            'bf_bonus_staff': budget.bf_bonus_staff,
            'bf_EDLI_contribution_staff': budget.bf_EDLI_contribution_staff,
            'bf_employer_contribution_to_ESI_staff': budget.bf_employer_contribution_to_ESI_staff,
            'bf_employer_contribution_to_PF_staff': budget.bf_employer_contribution_to_PF_staff,
            'bf_EPF_admin_charges_staff': budget.bf_EPF_admin_charges_staff,
            'bf_exgratia_dept_staff':budget.bf_exgratia_dept_staff,
            'bf_gratuity_staff': budget.bf_gratuity_staff,
            'bf_insurance_staff':budget.bf_insurance_staff,
            'bf_lwf_dept_staff':budget.bf_lwf_dept_staff,
            'bf_incentive_dept_staff':budget.bf_incentive_dept_staff,
            'bf_salaries_wages_staff': budget.bf_salaries_wages_staff,
            'bf_fixed': budget.bf_fixed,
            'bf_insurance_warehouse': budget.bf_insurance_warehouse,
            'bf_insurance_wcc':budget.bf_insurance_wcc,
            'bf_rent_premises': budget.bf_rent_premises,
            'bf_security_service_charges': budget.bf_security_service_charges,
            'bf_manpower_supply_expenses': budget.bf_manpower_supply_expenses,
            'bf_variable': budget.bf_variable,
            'bf_crane_handling_expenses': budget.bf_crane_handling_expenses,
            'bf_diesel_expenses_forklift': budget.bf_diesel_expenses_forklift,
            'bf_forklift_handling_expenses': budget.bf_forklift_handling_expenses,
            'bf_fumigation_expenses': budget.bf_fumigation_expenses,
            'bf_packing_services':budget.bf_packing_services,
            'bf_support_handling':budget.bf_support_handling,
            'bf_oe_Fixed': budget.bf_oe_Fixed,
            'bf_depreciation': budget.bf_depreciation,
            'bf_internet_data_card_expenses': budget.bf_internet_data_card_expenses,
            'bf_rent_plant_machinery': budget.bf_rent_plant_machinery,
            'bf_amc': budget.bf_amc,
            'bf_software_AMC_charges':budget.bf_software_AMC_charges,
            'bf_oe_variable': budget.bf_oe_variable,
            'bf_CGST_ineligible_ITC': budget.bf_CGST_ineligible_ITC,
            'bf_conveyance_expenses': budget.bf_conveyance_expenses,
            'bf_diesel_expenses_gense': budget.bf_diesel_expenses_gense,
            'bf_handling_expenses': budget.bf_handling_expenses,
            'bf_hotel_boarding_lodging_expenses': budget.bf_hotel_boarding_lodging_expenses,
            'bf_IGST_ineligible_ITC': budget.bf_IGST_ineligible_ITC,
            'bf_office_supplies_general_expenses': budget.bf_office_supplies_general_expenses,
            'bf_postage_courier': budget.bf_postage_courier,
            'bf_power_fuel': budget.bf_power_fuel,
            'bf_printing_stationery': budget.bf_printing_stationery,
            'bf_service_maintenance_expenses': budget.bf_service_maintenance_expenses,
            'bf_SGST_ineligible_ITC':budget.bf_SGST_ineligible_ITC,
            'bf_staff_welfare_staff': budget.bf_staff_welfare_staff,
            'bf_telephone_mobile_expenses': budget.bf_telephone_mobile_expenses,
            'bf_training_expenses': budget.bf_training_expenses,
            'bf_travelling_expenses': budget.bf_travelling_expenses,

            # New fields for BVM Trans Solutions pvt ltd
            'bf_Halting_Charges': budget.bf_Halting_Charges,
            'bf_Halting_Charges_SEZ': budget.bf_Halting_Charges_SEZ,
            'bf_Loading_Charges': budget.bf_Loading_Charges,
            'bf_Parking_Charges': budget.bf_Parking_Charges,
            'bf_Parking_Charges_SEZ': budget.bf_Parking_Charges_SEZ,
            'bf_Toll_Charges': budget.bf_Toll_Charges,
            'bf_Transportation_Charges': budget.bf_Transportation_Charges,
            'bf_Transportation_Charges_Interstate': budget.bf_Transportation_Charges_Interstate,
            'bf_Transportation_Charges_SEZ': budget.bf_Transportation_Charges_SEZ,
            'bf_Transportation_Handling_Charges': budget.bf_Transportation_Handling_Charges,
            'bf_Transportation_Handling_Charges_SEZ': budget.bf_Transportation_Handling_Charges_SEZ,
            'bf_Unloading_Charges': budget.bf_Unloading_Charges,
            'bf_Weighment_Charges': budget.bf_Weighment_Charges,
            'bf_driver_staff': budget.bf_driver_staff,
            'bf_bonus_drivers': budget.bf_bonus_drivers,
            'bf_EDLI_contribution_drivers': budget.bf_EDLI_contribution_drivers,
            'bf_employer_contribution_to_ESI_drivers': budget.bf_employer_contribution_to_ESI_drivers,
            'bf_employer_contribution_to_PF_drivers': budget.bf_employer_contribution_to_PF_drivers,
            'bf_EPF_admin_charges_drivers': budget.bf_EPF_admin_charges_drivers,
            'bf_exgratia_drivers': budget.bf_exgratia_drivers,
            'bf_gratuity_drivers': budget.bf_gratuity_drivers,
            'bf_incentive_drivers': budget.bf_incentive_drivers,
            'bf_insurance_drivers': budget.bf_insurance_drivers,
            'bf_lwf_drivers': budget.bf_lwf_drivers,
            'bf_salaries_wages_drivers': budget.bf_salaries_wages_drivers,
            'bf_gprs_access_service': budget.bf_gprs_access_service,
            'bf_insurance_vehicles': budget.bf_insurance_vehicles,
            'bf_vehicle_hire': budget.bf_vehicle_hire,
            'bf_acting_driver': budget.bf_acting_driver,
            'bf_cng': budget.bf_cng,
            'bf_diesel_vehicle': budget.bf_diesel_vehicle,
            'bf_driver_betta': budget.bf_driver_betta,
            'bf_extra_hrs': budget.bf_extra_hrs,
            'bf_extra_km': budget.bf_extra_km,
            'bf_halting': budget.bf_halting,
            'bf_loading': budget.bf_loading,
            'bf_parking': budget.bf_parking,
            'bf_rates_taxes': budget.bf_rates_taxes,
            'bf_toll': budget.bf_toll,
            'bf_transportation': budget.bf_transportation,
            'bf_unloading': budget.bf_unloading,
            'bf_vehicle_maintenance': budget.bf_vehicle_maintenance,
            'bf_weighment': budget.bf_weighment,
            'bf_vehicle_source': budget.bf_vehicle_source,
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
            existing_budget = BudgetInfo.objects.filter(
                bf_start_date_year__year=year,
                bf_start_date_year__month=month,
                bf_company=form.cleaned_data['bf_company'],
                bf_location=form.cleaned_data['bf_location'],
                bf_unit_reference=form.cleaned_data['bf_unit_reference'],
                bf_vehicle_source=form.cleaned_data['bf_vehicle_source']
            ).exists()

            if existing_budget:
                messages.error(request, f'A budget record for {unique_start_date.strftime("%B %Y")} in the selected company, branch, and unit already exists.')
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
