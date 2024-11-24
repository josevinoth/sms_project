from django.contrib.auth.decorators import login_required
from ..forms import BudgetForm
from ..models import BudgetInfo
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404

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
            'bf_start_date': budget.bf_start_date,
            'bf_end_date': budget.bf_end_date,
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
            unique_start_date = form.cleaned_data['bf_start_date']
            unique_end_date = form.cleaned_data['bf_end_date']
            existing_budget = BudgetInfo.objects.filter(bf_start_date=unique_start_date, bf_end_date=unique_end_date).exists()

            if existing_budget:
                messages.error(request, 'A budget record with the same start and end dates already exists.')
            else:
                cloned_budget = form.save(commit=False)
                cloned_budget.created_by = request.user
                cloned_budget.save()
                messages.success(request, 'Budget record cloned successfully.')
                return redirect('budget_form_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
            messages.error(request, 'Form is not valid. Please correct the errors.')

        return redirect(request.META.get('HTTP_REFERER', '/'))



