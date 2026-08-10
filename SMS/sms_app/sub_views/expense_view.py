from django.contrib import messages
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from ..models import ExpenseInfo, ExpenseExtinfo
from django.shortcuts import render, redirect
from ..forms import ExpenseaddForm,ExpenseextaddForm
from datetime import datetime, time
from django.utils import timezone

# Invoicecity
@login_required(login_url='login_page')
def expense_add(request, expense_id=0, is_petty_cash=False, petty_cash_type=None):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if expense_id == 0:
            initial_data = {}
            if is_petty_cash:
                from ..models import Business_Sol_info, CreditLedgerInfo
                
                business_search = 'BVM Trans'
                ledger_prefix = 'Trans Petty Cash'
                
                if petty_cash_type == 'wms':
                    business_search = 'BVM Storage'
                    ledger_prefix = 'WH Petty Cash'
                elif petty_cash_type == 'pms':
                    business_search = 'BVM Pack'
                    ledger_prefix = 'Pack Petty Cash'
                    
                bvm_business = Business_Sol_info.objects.filter(bvm_business__icontains=business_search).first()
                if bvm_business:
                    initial_data['exp_business'] = bvm_business.id
                
                branch_id = get_session_branch_id(request)
                branch_code = get_branch_code(branch_id)
                ledger = CreditLedgerInfo.objects.filter(ledger_name__icontains=f'{ledger_prefix} - {branch_code}').first()
                if ledger:
                    initial_data['exp_credit_ledger'] = ledger.id
            
            expense_form = ExpenseaddForm(initial=initial_data)
            if is_petty_cash:
                from ..models import User_extInfo, MyUser
                bvm_business_id = initial_data.get('exp_business')
                branch_id = get_session_branch_id(request)
                if bvm_business_id and branch_id:
                    user_ids = User_extInfo.objects.filter(emp_organisation_id=bvm_business_id, emp_branch_id=branch_id).values_list('user_id', flat=True)
                    expense_form.fields['exp_to'].queryset = MyUser.objects.filter(id__in=user_ids)
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
            
            from ..models import User_extInfo, MyUser
            bvm_business_id = expense.exp_business_id
            branch_id = get_session_branch_id(request)
            if bvm_business_id and branch_id:
                user_ids = User_extInfo.objects.filter(emp_organisation_id=bvm_business_id, emp_branch_id=branch_id).values_list('user_id', flat=True)
                expense_form.fields['exp_to'].queryset = MyUser.objects.filter(id__in=user_ids)

            context = {
                'expense_form': expense_form,
                'first_name': first_name,
                'user_id': user_id,
                'expense_ext_list': expense_ext_list,
                'parent_business': expense.exp_business.bvm_business if expense.exp_business else "",
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
                branch_id = get_session_branch_id(request)
                branch_code = get_branch_code(branch_id)
                cat_prefix = 'C_' if saved_expense.exp_category.id == 1 else 'B_'
                prefix = f"{fy}_{branch_code}_EXP_{cat_prefix}"
                expense_num = generate_next_number(ExpenseInfo, 'exp_number', prefix, 6)

                # Update the expense with the generated number
                saved_expense.exp_number = expense_num
                saved_expense.save()

            messages.success(request, 'Record Updated Successfully')
            # Preserve filter parameters in redirect
            filter_params = f"?from_date={request.GET.get('from_date', '')}&to_date={request.GET.get('to_date', '')}&expense_number={request.GET.get('expense_number', '')}"
            return redirect('/SMS/expense_update/' + str(saved_expense.id) + filter_params)
        else:
            messages.error(request, 'Record Not Saved. Please Enter All Required Fields')
            # return redirect('expense_list')
            return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login_page')
def expense_list(request):
    return expense_search(request)

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
    expense_number = request.GET.get('expense_number', "")
    organisation_id = request.session.get('ses_organisation_id')
    role_id = request.session.get('ses_role_id')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    show_all = request.GET.get('show_all') == 'true'

    filters = Q()
    if expense_number:
        filters &= Q(exp_number__icontains=expense_number)
    
    if role_id == 2:
        filters &= Q(exp_business=organisation_id)

    # Date filter logic (Service Start Date)
    if from_date:
        try:
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            from_dt = timezone.make_aware(datetime.combine(from_dt.date(), time.min))
            filters &= Q(exp_service_start_date__gte=from_dt)
        except (ValueError, TypeError):
            pass
    if to_date:
        try:
            to_dt = datetime.strptime(to_date, '%Y-%m-%d')
            to_dt = timezone.make_aware(datetime.combine(to_dt.date(), time.max))
            filters &= Q(exp_service_start_date__lte=to_dt)
        except (ValueError, TypeError):
            pass

    expense_list_qs = ExpenseInfo.objects.filter(filters).order_by('-id')

    # If date filter is applied OR show_all, return all matching records (no pagination)
    # This ensures DataTables can search across ALL filtered results
    if show_all or from_date or to_date:
        page_obj = expense_list_qs
    else:
        paginator = Paginator(expense_list_qs, 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    context = {
        'expense_list': expense_list_qs,
        'first_name': first_name,
        'page_obj': page_obj,
        'role': request.session.get('ses_role'),
        'role_id': role_id,
        'show_all': show_all,
    }
    return render(request, "asset_mgt_app/expense_list.html", context)

@login_required(login_url='login_page')
def expense_ext_add(request, expense_ext_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    expense_id = request.session.get('ses_expense_id')

    if request.method == "GET":
        parent_expense = ExpenseInfo.objects.get(pk=expense_id)
        if expense_ext_id == 0:
            form = ExpenseextaddForm(initial={'exp_ext_credit_ledger': parent_expense.exp_credit_ledger})
        else:
            try:
                expense_ext = ExpenseExtinfo.objects.get(pk=expense_ext_id)
                form = ExpenseextaddForm(instance=expense_ext)
            except ExpenseExtinfo.DoesNotExist:
                messages.error(request, 'Expense attachment not found.')
                return redirect('/SMS/expense_ext_list')

        expense_ext_list = ExpenseExtinfo.objects.filter(exp_ext_expense_number=expense_id)

        context = {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'expense_id': expense_id,
            'expense_ext_list': expense_ext_list,
            'parent_business': parent_expense.exp_business.bvm_business if parent_expense.exp_business else "",
        }
        return render(request, "asset_mgt_app/expense_ext_add.html", context)


    elif request.method == "POST":

        if expense_ext_id == 0:

            form = ExpenseextaddForm(request.POST, request.FILES)

            if form.is_valid():

                form.save()

                messages.success(request, 'Saved successfully.')

                if 'save_and_add' in request.POST:
                    return redirect('/SMS/expense_ext_add')
                else:
                    expense_id = request.session.get('ses_expense_id')
                    expense_ext_id = max(
                        ExpenseExtinfo.objects.filter(exp_ext_expense_number=expense_id).values_list('id', flat=True))
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

                if 'save_and_add' in request.POST:
                    return redirect('/SMS/expense_ext_add')
                else:
                    return redirect(request.META.get('HTTP_REFERER', '/SMS/expense_ext_list'))

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