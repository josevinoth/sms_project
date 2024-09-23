from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q

from ..models import ExpenseInfo
from django.shortcuts import render, redirect
from ..forms import ExpenseaddForm

# Invoicecity
@login_required(login_url='login_page')
def expense_add(request, expense_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if expense_id == 0:
            expense_form = ExpenseaddForm()
        else:
            try:
                expense = ExpenseInfo.objects.get(pk=expense_id)
                expense_form = ExpenseaddForm(instance=expense)
            except ExpenseInfo.DoesNotExist:
                messages.error(request, "Expense not found.")
                return redirect('expense_list')  # or handle as needed

        context = {
            'expense_form': expense_form,
            'first_name': first_name,
            'user_id': user_id,
        }
        return render(request, "asset_mgt_app/expense_add.html", context)

    else:
        if expense_id == 0:
            expense_form = ExpenseaddForm(request.POST)
        else:
            try:
                expense = ExpenseInfo.objects.get(pk=expense_id)
                expense_form = ExpenseaddForm(request.POST, instance=expense)
            except ExpenseInfo.DoesNotExist:
                messages.error(request, "Expense not found.")
                return redirect('expense_list')

        if expense_form.is_valid():
            expense_form.save()

            # Generate the expense number
            try:
                last_expense = ExpenseInfo.objects.latest('id')
                expense_num = 1000000 + last_expense.id
            except ObjectDoesNotExist:
                expense_num = 100000

            expense_category_id = last_expense.exp_category.id
            prefix = 'C_' if expense_category_id == 1 else 'B_'
            expense_num = f'{prefix}{expense_num}'

            # Update the expense with the generated number
            last_expense.exp_number = expense_num
            last_expense.save()

            messages.success(request, 'Record Updated Successfully')
        else:
            messages.error(request, 'Record Not Saved. Please Enter All Required Fields')

        return redirect('/SMS/expense_update/' + str(last_expense.id))


@login_required(login_url='login_page')
def expense_list(request):
    first_name = request.session.get('first_name')
    organisation_id = request.session.get('ses_organisation_id')
    role_id = request.session.get('ses_role_id')

    expense_list_val = ExpenseInfo.objects.filter(exp_business=organisation_id).order_by('-id')
    paginator = Paginator(expense_list_val, 50)  # Adjust the pagination size if needed
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'expense_list_val': expense_list_val,
        'first_name': first_name,
        'page_obj': page_obj,
        'role_id': role_id,
    }
    return render(request, "asset_mgt_app/expense_list.html", context)

@login_required(login_url='login_page')
def expense_delete(request, expense_id):
    try:
        expense_del = ExpenseInfo.objects.get(pk=expense_id)
        expense_del.delete()
        messages.success(request, 'Expense deleted successfully.')
    except ExpenseInfo.DoesNotExist:
        messages.error(request, 'Expense not found.')

    return redirect('/SMS/expense_list')


@login_required(login_url='login_page')
def expense_search(request):
    first_name = request.session.get('first_name')
    expense_number = request.GET.get('expense_number', "")  # Set a default empty string
    organisation_id = request.session.get('ses_organisation_id')
    role_id = request.session.get('ses_role_id')

    if role_id == 2:
        expense_list = ExpenseInfo.objects.filter(
            Q(exp_business=organisation_id) &
            (Q(exp_number__icontains=expense_number) | Q(exp_number__isnull=True))
        ).order_by('-id')
    else:
        expense_list = ExpenseInfo.objects.filter(
            Q(exp_number__icontains=expense_number) | Q(exp_number__isnull=True)
        ).order_by('-id')

    paginator = Paginator(expense_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'expense_list': expense_list,
        'first_name': first_name,
        'page_obj': page_obj,
        'role': request.session.get('ses_role'),
    }
    return render(request, "asset_mgt_app/expense_list.html", context)


