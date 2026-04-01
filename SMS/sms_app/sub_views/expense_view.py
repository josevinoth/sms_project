from django.contrib import messages
from .general_utils import get_financial_year, generate_next_number, get_branch_code
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from ..models import ExpenseInfo, ExpenseExtinfo
from django.shortcuts import render, redirect
from ..forms import ExpenseaddForm,ExpenseextaddForm

# Invoicecity
@login_required(login_url='login_page')
def expense_add(request, expense_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if expense_id == 0:
            expense_form = ExpenseaddForm()
            context = {
                'expense_form': expense_form,
                'first_name': first_name,
                'user_id': user_id,
            }
        else:
            try:
                expense = ExpenseInfo.objects.get(pk=expense_id)
                expense_form = ExpenseaddForm(instance=expense)
                expense_ext_list = ExpenseExtinfo.objects.filter(exp_ext_expense_number=expense_id)
                request.session['ses_expense_id'] = expense_id
            except ExpenseInfo.DoesNotExist:
                messages.error(request, "Expense not found.")
                return redirect('expense_list')
            context = {
                'expense_form': expense_form,
                'first_name': first_name,
                'user_id': user_id,
                'expense_ext_list': expense_ext_list,
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
            saved_expense = expense_form.save()

            # Generate the expense number for new expenses based on financial year
            if expense_id == 0:
                fy = get_financial_year()
                branch_id = request.session.get('ses_branch_id', 1)
                branch_code = get_branch_code(branch_id)
                cat_prefix = 'C_' if saved_expense.exp_category.id == 1 else 'B_'
                prefix = f"{fy}_{branch_code}_EXP_{cat_prefix}"
                expense_num = generate_next_number(ExpenseInfo, 'exp_number', prefix, 6)

                # Update the expense with the generated number
                saved_expense.exp_number = expense_num
                saved_expense.save()

            messages.success(request, 'Record Updated Successfully')
            return redirect('/SMS/expense_update/' + str(saved_expense.id))
        else:
            messages.error(request, 'Record Not Saved. Please Enter All Required Fields')
            # return redirect('expense_list')
            return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login_page')
def expense_list(request):
    first_name = request.session.get('first_name')
    organisation_id = request.session.get('ses_organisation_id')
    role_id = request.session.get('ses_role_id')

    # expense_list_val = ExpenseInfo.objects.filter(exp_business=organisation_id).order_by('-id')
    expense_list_val = ExpenseInfo.objects.all().order_by('-id')
    paginator = Paginator(expense_list_val, 50000)  # Adjust the pagination size if needed
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

@login_required(login_url='login_page')
def expense_ext_add(request, expense_ext_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    expense_id = request.session.get('ses_expense_id')

    if request.method == "GET":
        if expense_ext_id == 0:
            form = ExpenseextaddForm()
        else:
            try:
                expense_ext = ExpenseExtinfo.objects.get(pk=expense_ext_id)
                form = ExpenseextaddForm(instance=expense_ext)
            except ExpenseExtinfo.DoesNotExist:
                messages.error(request, 'Expense attachment not found.')
                return redirect('/SMS/expense_ext_list')

        context = {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'expense_id': expense_id,
            'expense_ext_list': expense_ext_list,
        }
        return render(request, "asset_mgt_app/expense_ext_add.html", context)


    elif request.method == "POST":

        if expense_ext_id == 0:

            form = ExpenseextaddForm(request.POST, request.FILES)

            if form.is_valid():

                form.save()

                expense_id = request.session.get('ses_expense_id')

                expense_ext_id = max(
                    ExpenseExtinfo.objects.filter(exp_ext_expense_number=expense_id).values_list('id', flat=True))

                messages.success(request, 'Saved successfully.')

                return redirect(f'/SMS/expense_ext_update/{expense_ext_id}')

            else:

                messages.error(request, 'Form is not valid.')

                print(form.errors)  # Print form errors to the console for debugging

                return redirect('/SMS/expense_ext_add')

        else:

            try:

                expense_ext = ExpenseExtinfo.objects.get(pk=expense_ext_id)

                form = ExpenseextaddForm(request.POST, request.FILES, instance=expense_ext)

            except ExpenseExtinfo.DoesNotExist:

                messages.error(request, 'Expense attachment not found.')

                return redirect('/SMS/expense_ext_list')

            if form.is_valid():

                form.save()

                messages.success(request, 'Saved successfully.')

                return redirect(request.META['HTTP_REFERER'])

            else:

                messages.error(request, 'Form is not valid.')

                print(form.errors)  # Print form errors to the console for debugging

                return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login_page')
def expense_ext_list(request):
    first_name = request.session.get('first_name')  # If needed for context
    # Fetch all expense attachments
    expense_ext_list = ExpenseExtinfo.objects.all()

    context = {
        'expense_ext_list': expense_ext_list,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/expense_ext_list.html", context)


# Delete expense attachment
@login_required(login_url='login_page')
def expense_ext_delete(request, expense_ext_id):
        expense = ExpenseExtinfo.objects.get(pk=expense_ext_id)
        expense.delete()
        messages.success(request, 'Expense deleted successfully.')
        return redirect(request.META['HTTP_REFERER'])


# Cancel and return to the expense update page
@login_required(login_url='login_page')
def expense_ext_cancel(request, expense_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    expense_ext_id = request.session.get('ses_expense_id')
    total_amount = ExpenseExtinfo.objects.filter(
        exp_ext_expense_number=expense_ext_id
    ).aggregate(total=Sum('exp_ext_amount'))['total']

    # If you want to handle the case where total might be None:
    total_amount = total_amount or 0
    ExpenseInfo.objects.filter(pk=expense_ext_id).update(exp_rate=total_amount)
    return redirect(f'/SMS/expense_update/{expense_ext_id}')