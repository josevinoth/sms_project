from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count, Q,Sum,Case, When, Value, CharField, Min,FloatField, F
from django.db.models import F, Subquery, OuterRef
from django.db.models.functions import Coalesce,Round
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime
from ..models import Warehouse_goods_info,ExpenseExtinfo,Location_info,UnitInfo,Business_Sol_info,TrbusinesstypeInfo,CustomerInfo,ExpenseTypeInfo,Ar_Info



def finance_reports(request):
    first_name = request.session.get('first_name')
    context = {
               'first_name': first_name
               }
    return render(request,"asset_mgt_app/finance_reports.html",context)


def branch_profit_loss(request):
    first_name = request.session.get('first_name')
    branches = Location_info.objects.all()
    selected_branch = request.GET.get('branch', '')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    expenses_filter = {}
    invoices_filter = {}

    if selected_branch:
        expenses_filter['exp_ext_branch__loc_name'] = selected_branch  # Adjust to match the loc_name field.
        invoices_filter['wh_branch__loc_name'] = selected_branch

    if from_date:
        from_date = timezone.make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
        expenses_filter['exp_ext_updated_on__gte'] = from_date
        invoices_filter['wh_checkin_time__gte'] = from_date

    if to_date:
        to_date = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))
        expenses_filter['exp_ext_updated_on__lte'] = to_date
        invoices_filter['wh_checkin_time__lte'] = to_date

    expenses_data = (
        ExpenseExtinfo.objects.filter(**expenses_filter)
        .values('exp_ext_branch', 'exp_ext_branch__loc_name')
        .annotate(total_expense=Sum('exp_ext_amount'))
    )

    invoice_data = (
        Warehouse_goods_info.objects.filter(**invoices_filter)
        .values('wh_branch', 'wh_branch__loc_name')
        .annotate(total_invoice_cost=Sum('wh_total_invoice_cost'))
    )

    combined_data = {}

    for expense in expenses_data:
        key = (expense['exp_ext_branch'])
        combined_data[key] = {
            'branch': expense['exp_ext_branch__loc_name'],
            'total_expense': expense['total_expense'],
            'total_invoice_cost': 0.0,
            'profit_loss': -expense['total_expense'],
            'profit_loss_percentage': 0.0,
        }

    # Process invoice data and combine with expenses data
    for invoice in invoice_data:
        key = (invoice['wh_branch'])
        if key in combined_data:
            combined_data[key]['total_invoice_cost'] = invoice['total_invoice_cost']
            combined_data[key]['profit_loss'] += invoice['total_invoice_cost']
        else:
            combined_data[key] = {
                'branch': invoice['wh_branch__loc_name'],
                'total_expense': 0.0,
                'total_invoice_cost': invoice['total_invoice_cost'],
                'profit_loss': invoice['total_invoice_cost'],
                'profit_loss_percentage': 0.0,
            }
    for key, data in combined_data.items():
        if data['total_invoice_cost'] > 0:  # Avoid division by zero
            data['profit_loss_percentage'] = (data['profit_loss'] / data['total_invoice_cost']) * 100
        else:
            data['profit_loss_percentage'] = 0.0  # Set percentage to 0.0 if no invoice cost

    # Remove entries with zero expenses and invoice cost (if necessary)
    summary_data = [
        row for row in combined_data.values()
        if row['total_expense'] != 0.0 or row['total_invoice_cost'] != 0.0
    ]
    chart_labels = [row['branch'] for row in summary_data]
    chart_income = [row['total_invoice_cost'] for row in summary_data]
    chart_expenses = [row['total_expense'] for row in summary_data]
    chart_profit_loss = [row['profit_loss'] for row in summary_data]

    # Pass the data to the template
    context = {
        'summary_data': summary_data,
        'branches': branches,
        'first_name': first_name,
        'selected_branch': selected_branch,
        'from_date': from_date.strftime('%Y-%m-%d') if from_date else '',
        'to_date': to_date.strftime('%Y-%m-%d') if to_date else '',
        'chart_labels': chart_labels,  # Pass as a Python list
        'chart_income': chart_income,  # Pass as a Python list
        'chart_expenses': chart_expenses,  # Pass as a Python list
        'chart_profit_loss': chart_profit_loss,  # Pass as a Python list
    }

    return render(request, "asset_mgt_app/fin_branch_PL_report.html", context)


def branch_unit_profit_loss(request):
    first_name = request.session.get('first_name')
    branches = Location_info.objects.all()
    units = UnitInfo.objects.all().distinct()

    selected_branch = request.GET.get('branch', '')
    selected_unit = request.GET.get('unit', '')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if selected_branch:

        units = UnitInfo.objects.filter(ui_branch_name__loc_name=selected_branch).distinct('unit_name')
    else:
        units = UnitInfo.objects.all().distinct('unit_name')

    expenses_filter = {}
    invoices_filter = {}

    if selected_branch:
        expenses_filter['exp_ext_branch__loc_name'] = selected_branch  # Adjust to match the loc_name field.
        invoices_filter['wh_branch__loc_name'] = selected_branch

    if selected_unit:
        expenses_filter['exp_ext_unit__unit_name'] = selected_unit
        invoices_filter['wh_unit__unit_name'] = selected_unit

    if from_date:
        from_date = timezone.make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
        expenses_filter['exp_ext_updated_on__gte'] = from_date
        invoices_filter['wh_checkin_time__gte'] = from_date

    if to_date:
        to_date = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))
        expenses_filter['exp_ext_updated_on__lte'] = to_date
        invoices_filter['wh_checkin_time__lte'] = to_date

    expenses_data = (
        ExpenseExtinfo.objects.filter(**expenses_filter)
        .values('exp_ext_branch', 'exp_ext_unit', 'exp_ext_branch__loc_name', 'exp_ext_unit__unit_name')
        .annotate(total_expense=Sum('exp_ext_amount'))
    )

    invoice_data = (
        Warehouse_goods_info.objects.filter(**invoices_filter)
        .values('wh_branch', 'wh_unit', 'wh_branch__loc_name', 'wh_unit__unit_name')
        .annotate(total_invoice_cost=Sum('wh_total_invoice_cost'))
    )

    combined_data = {}

    for expense in expenses_data:
        key = (expense['exp_ext_branch'], expense['exp_ext_unit'])
        combined_data[key] = {
            'branch': expense['exp_ext_branch__loc_name'],
            'unit': expense['exp_ext_unit__unit_name'],
            'total_expense': expense['total_expense'],
            'total_invoice_cost': 0.0,
            'profit_loss': -expense['total_expense'],
            'profit_loss_percentage': 0.0,
        }

    # Process invoice data and combine with expenses data
    for invoice in invoice_data:
        key = (invoice['wh_branch'], invoice['wh_unit'])
        if key in combined_data:
            combined_data[key]['total_invoice_cost'] = invoice['total_invoice_cost']
            combined_data[key]['profit_loss'] += invoice['total_invoice_cost']
        else:
            combined_data[key] = {
                'branch': invoice['wh_branch__loc_name'],
                'unit': invoice['wh_unit__unit_name'],
                'total_expense': 0.0,
                'total_invoice_cost': invoice['total_invoice_cost'],
                'profit_loss': invoice['total_invoice_cost'],
                'profit_loss_percentage': 0.0,
            }
    for key, data in combined_data.items():
        if data['total_invoice_cost'] > 0:  # Avoid division by zero
            data['profit_loss_percentage'] = (data['profit_loss'] / data['total_invoice_cost']) * 100
        else:
            data['profit_loss_percentage'] = 0.0  # Set percentage to 0.0 if no invoice cost

    # Remove entries with zero expenses and invoice cost (if necessary)
    summary_data = [
        row for row in combined_data.values()
        if row['total_expense'] != 0.0 or row['total_invoice_cost'] != 0.0
    ]
    chart_labels = [row['unit'] for row in summary_data]
    chart_income = [row['total_invoice_cost'] for row in summary_data]
    chart_expenses = [row['total_expense'] for row in summary_data]
    chart_profit_loss = [row['profit_loss'] for row in summary_data]

    # Pass the data to the template
    context = {
        'summary_data': summary_data,
        'branches': branches,
        'first_name': first_name,
        'units': units,
        'selected_branch': selected_branch,
        'selected_unit': selected_unit,
        'from_date': from_date.strftime('%Y-%m-%d') if from_date else '',
        'to_date': to_date.strftime('%Y-%m-%d') if to_date else '',
        'chart_labels': chart_labels,
        'chart_income': chart_income,
        'chart_expenses': chart_expenses,
        'chart_profit_loss': chart_profit_loss,  # Pass as a Python list
    }

    return render(request, "asset_mgt_app/fin_unit_PL_report.html", context)


def businessmodel_PL(request):
    first_name = request.session.get('first_name')
    branch_filter = request.GET.get('branch')
    unit_filter = request.GET.get('unit')
    businessmodel_filter = request.GET.get('businessmodel')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    branches = Location_info.objects.all()
    businessmodels = TrbusinesstypeInfo.objects.all()

    if from_date:
        from_date = timezone.make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
    if to_date:
        to_date = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))

    income_queryset = Warehouse_goods_info.objects.all()
    if branch_filter:
        income_queryset = income_queryset.filter(wh_branch__loc_name=branch_filter)
    if unit_filter:
        income_queryset = income_queryset.filter(wh_unit__unit_name=unit_filter)
    if businessmodel_filter:
        income_queryset = income_queryset.filter(wh_customer_type__tb_trbusinesstype=businessmodel_filter)
    if from_date:
        income_queryset = income_queryset.filter(wh_checkin_time__gte=from_date)
    if to_date:
        income_queryset = income_queryset.filter(wh_checkin_time__lte=to_date)

    # Aggregate income
    income_data = income_queryset.values(
        branch_name=F('wh_branch__loc_name'),
        unit_name=F('wh_unit__unit_name'),
        businessmodel=F('wh_customer_type__tb_trbusinesstype')
    ).annotate(total_income=Sum('wh_total_invoice_cost'))

    # Filter Expense table based on parameters
    expense_queryset = ExpenseExtinfo.objects.all()
    if branch_filter:
        expense_queryset = expense_queryset.filter(exp_ext_branch__loc_name=branch_filter)
    if unit_filter:
        expense_queryset = expense_queryset.filter(exp_ext_unit__unit_name=unit_filter)
    if from_date:
        expense_queryset = expense_queryset.filter(exp_ext_updated_on__gte=from_date)
    if to_date:
        expense_queryset = expense_queryset.filter(exp_ext_updated_on__lte=to_date)

    # Map Expenses to Business Models using Branch and Unit
    expense_data = (
        expense_queryset.values(
            branch_name=F('exp_ext_branch__loc_name'),
            unit_name=F('exp_ext_unit__unit_name'),
        )
        .annotate(total_expense=Sum('exp_ext_amount'))
    )

    # Combine Income and Expense Data
    results = []
    for income in income_data:
        branch = income['branch_name']
        unit = income['unit_name']
        businessmodel = income['businessmodel']
        total_income = income['total_income']

        # Find matching expense for branch and unit
        matching_expense = next(
            (exp for exp in expense_data if exp['branch_name'] == branch and exp['unit_name'] == unit), None
        )
        total_expense = matching_expense['total_expense'] if matching_expense else 0

        # Calculate profit/loss and percentage
        profit_loss = total_income - total_expense
        profit_loss_percentage = (profit_loss / total_income * 100) if total_income != 0 else 0

        results.append({
            'branch': branch,
            'unit': unit,
            'businessmodel': businessmodel,
            'total_income': total_income,
            'total_expense': total_expense,
            'profit_loss': profit_loss,
            'profit_loss_percentage': round(profit_loss_percentage, 2),
        })
    chart_data = {}

    # Aggregate business model-wise totals
    for result in results:
        businessmodel = result['businessmodel']
        if businessmodel not in chart_data:
            chart_data[businessmodel] = {
                'income': 0,
                'expense': 0,
                'profit_loss': 0,
            }
        chart_data[businessmodel]['income'] += result['total_income']
        chart_data[businessmodel]['expense'] += result['total_expense']
        chart_data[businessmodel]['profit_loss'] += result['profit_loss']

    # Prepare chart labels and values
    chart_labels = list(chart_data.keys())
    income_values = [data['income'] for data in chart_data.values()]
    expense_values = [data['expense'] for data in chart_data.values()]
    profit_loss_values = [data['profit_loss'] for data in chart_data.values()]

    # Prepare context with data to pass to the template
    context = {
        'first_name': first_name,
        'from_date': from_date.strftime('%Y-%m-%d') if from_date else '',
        'to_date': to_date.strftime('%Y-%m-%d') if to_date else '',
        'results': results,
        'branches': branches,
        'businessmodels': businessmodels,
        'branch_filter': branch_filter,
        'businessmodel_filter': businessmodel_filter,
        'chart_labels': chart_labels,
        'income_values': income_values,
        'expense_values': expense_values,
        'profit_loss_values': profit_loss_values,
    }

    return render(request, "asset_mgt_app/fin_businessmodel_PL_report.html", context)


def customerwise_PL(request):
    first_name = request.session.get('first_name')
    selected_branch = request.GET.get('branch', '')
    selected_businessmodel = request.GET.get('businessmodel', '')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    branches = Location_info.objects.all()
    businessmodels = TrbusinesstypeInfo.objects.all()

    invoice_filters = Q()
    expense_filters = Q()

    # Apply date filters
    if from_date:
        invoice_filters &= Q(wh_checkin_time__gte=from_date)
        expense_filters &= Q(exp_ext_updated_on__gte=from_date)
    if to_date:
        invoice_filters &= Q(wh_checkin_time__lte=to_date)
        expense_filters &= Q(exp_ext_updated_on__lte=to_date)

    # Subquery for total expenses
    total_expenses_subquery = ExpenseExtinfo.objects.filter(
        exp_ext_branch=OuterRef('wh_branch')
    ).values('exp_ext_branch').annotate(
        total_expenses=Sum('exp_ext_amount')
    ).values('total_expenses')

    # Data for the table: Detailed data
    business_summary = Warehouse_goods_info.objects.values(
        'wh_customer_type__tb_trbusinesstype',  # Customer type
        'wh_branch__loc_name',                  # Branch
        'wh_customer_name__cu_nameshort'        # Customer name
    ).annotate(
        total_invoice_amount=Coalesce(Sum('wh_total_invoice_cost', filter=invoice_filters), 0.0),
        total_expenses=Coalesce(Subquery(total_expenses_subquery), 0.0),
        profit_loss=F('total_invoice_amount') - F('total_expenses'),
        profit_loss_percentage=Case(
            When(total_invoice_amount=0, then=Value(0.0)),
            default=(F('profit_loss') / F('total_invoice_amount') * 100),
            output_field=FloatField()
        )
    )

    # Apply branch and business model filters for the table
    if selected_branch:
        business_summary = business_summary.filter(wh_branch__loc_name=selected_branch)
    if selected_businessmodel:
        business_summary = business_summary.filter(wh_customer_type__tb_trbusinesstype=selected_businessmodel)

    # Data for the bar chart: Aggregated by customer type
    chart_summary = Warehouse_goods_info.objects.values(
        'wh_customer_type__tb_trbusinesstype'  # Group by customer type
    ).annotate(
        total_invoice_amount=Coalesce(Sum('wh_total_invoice_cost', filter=invoice_filters), 0.0),
        total_expenses=Coalesce(Sum(Subquery(total_expenses_subquery)), 0.0),
        profit_loss=F('total_invoice_amount') - F('total_expenses')
    )

    # Prepare chart data
    chart_labels = []
    income_values = []
    expense_values = []
    profit_loss_values = []

    for entry in chart_summary:
        customer_type = entry['wh_customer_type__tb_trbusinesstype']
        chart_labels.append(customer_type)  # Use customer type as label
        income_values.append(entry['total_invoice_amount'] or 0)  # Income value
        expense_values.append(entry['total_expenses'] or 0)  # Expense value
        profit_loss_values.append(entry['profit_loss'] or 0)  # Profit/Loss value

    # Context for rendering template
    context = {
        'business_summary': business_summary,  # Detailed data for the table
        'first_name': first_name,
        'branches': branches,
        'businessmodels': businessmodels,
        'selected_branch': selected_branch,
        'selected_businessmodel': selected_businessmodel,
        'from_date': from_date,
        'to_date': to_date,
        'chart_labels': chart_labels,  # Customer type labels for the chart
        'income_values': income_values,  # Income values for the chart
        'expense_values': expense_values,  # Expense values for the chart
        'profit_loss_values': profit_loss_values,  # Profit/Loss values for the chart
    }

    return render(request, "asset_mgt_app/fin_customerwise_PL_report.html", context)


def fin_profit_loss_view(request):
    first_name = request.session.get('first_name')
    branch_filter = request.GET.get('branch')
    unit_filter = request.GET.get('unit')
    businessmodel_filter = request.GET.get('businessmodel')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    branches = Location_info.objects.all()
    businessmodels = TrbusinesstypeInfo.objects.all()
    if from_date:
        from_date = timezone.make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
    if to_date:
        to_date = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))

    # Filter Income table based on parameters
    income_queryset = Warehouse_goods_info.objects.all()
    if branch_filter:
        income_queryset = income_queryset.filter(wh_branch__loc_name=branch_filter)
    if unit_filter:
        income_queryset = income_queryset.filter(wh_unit__unit_name=unit_filter)
    if businessmodel_filter:
        income_queryset = income_queryset.filter(wh_customer_type__tb_trbusinesstype=businessmodel_filter)
    if from_date:
        income_queryset = income_queryset.filter(wh_checkin_time__gte=from_date)
    if to_date:
        income_queryset = income_queryset.filter(wh_checkin_time__lte=to_date)

    # Aggregate income grouped only by branch and unit
    income_data = income_queryset.values(
        branch_name=F('wh_branch__loc_name'),
        unit_name=F('wh_unit__unit_name'),
    ).annotate(
        total_income=Sum('wh_total_invoice_cost')
    )

    # Filter Expense table based on parameters
    expense_queryset = ExpenseExtinfo.objects.all()
    if branch_filter:
        expense_queryset = expense_queryset.filter(exp_ext_branch__loc_name=branch_filter)
    if unit_filter:
        expense_queryset = expense_queryset.filter(exp_ext_unit__unit_name=unit_filter)
    if from_date:
        expense_queryset = expense_queryset.filter(exp_ext_updated_on__gte=from_date)
    if to_date:
        expense_queryset = expense_queryset.filter(exp_ext_updated_on__lte=to_date)

    # Map Expenses to Branch and Unit
    expense_data = (
        expense_queryset.values(
            branch_name=F('exp_ext_branch__loc_name'),
            unit_name=F('exp_ext_unit__unit_name'),
        )
        .annotate(total_expense=Sum('exp_ext_amount'))
    )

    # Combine Income and Expense Data
    results = []
    chart_labels = []  # For branch/unit labels
    income_values = []  # For income values
    expense_values = []  # For expense values
    profit_loss_values = []

    for income in income_data:
        branch = income['branch_name']
        unit = income['unit_name']
        total_income = income['total_income']

        # Find matching expense for branch and unit
        matching_expense = next(
            (exp for exp in expense_data if exp['branch_name'] == branch and exp['unit_name'] == unit), None
        )
        total_expense = matching_expense['total_expense'] if matching_expense else 0

        # Calculate profit/loss and percentage
        profit_loss = total_income - total_expense
        profit_loss_percentage = (profit_loss / total_income * 100) if total_income != 0 else 0

        results.append({
            'branch': branch,
            'unit': unit,
            'total_income': total_income,
            'total_expense': total_expense,
            'profit_loss': profit_loss,
            'profit_loss_percentage': round(profit_loss_percentage, 2),
        })
        label = f"{branch} - {unit}"  # Combine branch and unit for labels
        chart_labels.append(label)
        income_values.append(total_income)
        expense_values.append(total_expense)
        profit_loss_values.append(profit_loss)

    context = {
        'first_name':first_name,
        'results': results,
        'branches': branches,
        'businessmodels': businessmodels,
        'branch_filter': branch_filter,
        'businessmodel_filter': businessmodel_filter,
        'chart_labels': chart_labels,  # Bar chart labels
        'income_values': income_values,  # Income data for chart
        'expense_values': expense_values,  # Expense data for chart
        'profit_loss_values': profit_loss_values,
        'from_date': from_date.strftime('%Y-%m-%d') if from_date else '',
        'to_date': to_date.strftime('%Y-%m-%d') if to_date else '',
    }

    return render(request, "asset_mgt_app/fin_PL_report.html", context)


def expenses_report(request):
    first_name = request.session.get('first_name')
    branch_filter = request.GET.get('branch')
    unit_filter = request.GET.get('unit')
    company_filter = request.GET.get('company')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    branches = Location_info.objects.all()
    companies = Business_Sol_info.objects.values_list('bvm_business', flat=True).distinct()
    expense_summary = ExpenseExtinfo.objects.all()

    # Apply filters
    if branch_filter:
        expense_summary = expense_summary.filter(exp_ext_branch__loc_name=branch_filter)
    if unit_filter:
        expense_summary = expense_summary.filter(exp_ext_unit__unit_name=unit_filter)
    if from_date:
        from_date = timezone.make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
        expense_summary = expense_summary.filter(exp_ext_updated_on__gte=from_date)
    if to_date:
        to_date = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))
        expense_summary = expense_summary.filter(exp_ext_updated_on__lte=to_date)
    if company_filter:
        expense_summary = expense_summary.filter(
            exp_ext_expense_number__exp_business__bvm_business=company_filter
            )

    # Aggregate expense by expense type
    expense_summary = (
        expense_summary.values(expense_type=F('exp_ext_expense_number__exp_expense_type__exp_type_name'))
        .annotate(total_expense=Sum('exp_ext_amount'))
        .order_by('expense_type')
    )

    chart_labels = [entry['expense_type'] for entry in expense_summary]
    chart_data = [entry['total_expense'] for entry in expense_summary]

    context = {
        'first_name': first_name,
        'branches': branches,
        'companies': companies,
        'branch_filter': branch_filter,
        'company_filter': company_filter,
        'from_date': request.GET.get('from_date', ''),
        'to_date': request.GET.get('to_date', ''),
        'expense_summary': expense_summary,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }

    return render(request, "asset_mgt_app/fin_expenses_report.html", context)



def ar_due_reports(request):
    first_name = request.session.get('first_name')
    branch_filter = request.GET.get('branch')
    unit_filter = request.GET.get('unit')
    company_filter = request.GET.get('company')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    branches = Location_info.objects.all()
    companies = Business_Sol_info.objects.values_list('bvm_business', flat=True).distinct()
    ar_summary = Ar_Info.objects.all()

    # Apply filters
    if branch_filter:
        ar_summary = ar_summary.filter(ar_branch__loc_name=branch_filter)
    if unit_filter:
        ar_summary = ar_summary.filter(ar_unit__unit_name=unit_filter)
    if from_date:
        from_date = timezone.make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
        ar_summary = ar_summary.filter(ar_updated_at__gte=from_date)
    if to_date:
        to_date = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))
        ar_summary = ar_summary.filter(ar_updated_at__lte=to_date)
    if company_filter:
        ar_summary = ar_summary.filter(ar_company__bvm_business=company_filter)

    # Data for Line Graphs
    due_from_submission_data = (
        ar_summary
        .values('ar_due_from_submission_date')
        .annotate(total_amount=Sum('ar_amount'))
        .order_by('ar_due_from_submission_date')
    )

    due_from_operation_data = (
        ar_summary
        .values('ar_due_from_operation_date')
        .annotate(total_amount=Sum('ar_amount'))
        .order_by('ar_due_from_operation_date')
    )

    due_from_invoice_data = (
        ar_summary
        .values('ar_due_from_invoice_date')
        .annotate(total_amount=Sum('ar_amount'))
        .order_by('ar_due_from_invoice_date')
    )

    # Convert QuerySets to Lists for JavaScript
    submission_labels = [entry['ar_due_from_submission_date'] for entry in due_from_submission_data]
    submission_amounts = [entry['total_amount'] for entry in due_from_submission_data]

    operation_labels = [entry['ar_due_from_operation_date'] for entry in due_from_operation_data]
    operation_amounts = [entry['total_amount'] for entry in due_from_operation_data]

    invoice_labels = [entry['ar_due_from_invoice_date'] for entry in due_from_invoice_data]
    invoice_amounts = [entry['total_amount'] for entry in due_from_invoice_data]

    context = {
        'first_name': first_name,
        'branches': branches,
        'companies': companies,
        'branch_filter': branch_filter,
        'company_filter': company_filter,
        'from_date': request.GET.get('from_date', ''),
        'to_date': request.GET.get('to_date', ''),
        'due_from_submission_data': due_from_submission_data,
        'due_from_invoice_data': due_from_invoice_data,
        'due_from_operation_data': due_from_operation_data,
        'submission_labels': submission_labels,
        'submission_amounts': submission_amounts,
        'operation_labels': operation_labels,
        'operation_amounts': operation_amounts,
        'invoice_labels': invoice_labels,
        'invoice_amounts': invoice_amounts,
    }

    return render(request, "asset_mgt_app/ar_due_reports.html", context)
