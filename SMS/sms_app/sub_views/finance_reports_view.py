from django.shortcuts import render
from django.db.models import Count, Q,Sum,Case, When, Value, CharField, Min,FloatField, F,IntegerField
from django.db.models import F, Subquery, OuterRef
from django.db.models.functions import Coalesce,Round
from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime
from ..models import Warehouse_goods_info,ExpenseExtinfo,Location_info,UnitInfo,Business_Sol_info,TrbusinesstypeInfo,CustomerInfo,ExpenseTypeInfo,Ar_Info,BudgetInfo,ExpenseInfo


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
        expenses_filter['exp_ext_branch__loc_name'] = selected_branch
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
        if data['total_invoice_cost'] > 0:
            data['profit_loss_percentage'] = (data['profit_loss'] / data['total_invoice_cost']) * 100
        else:
            data['profit_loss_percentage'] = 0.0

    summary_data = [
        row for row in combined_data.values()
        if row['total_expense'] != 0.0 or row['total_invoice_cost'] != 0.0
    ]
    chart_labels = [row['branch'] for row in summary_data]
    chart_income = [row['total_invoice_cost'] for row in summary_data]
    chart_expenses = [row['total_expense'] for row in summary_data]
    chart_profit_loss = [row['profit_loss'] for row in summary_data]

    context = {
        'summary_data': summary_data,
        'branches': branches,
        'first_name': first_name,
        'selected_branch': selected_branch,
        'from_date': from_date.strftime('%Y-%m-%d') if from_date else '',
        'to_date': to_date.strftime('%Y-%m-%d') if to_date else '',
        'chart_labels': chart_labels,
        'chart_income': chart_income,
        'chart_expenses': chart_expenses,
        'chart_profit_loss': chart_profit_loss,
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
        expenses_filter['exp_ext_branch__loc_name'] = selected_branch
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
        if data['total_invoice_cost'] > 0:
            data['profit_loss_percentage'] = (data['profit_loss'] / data['total_invoice_cost']) * 100
        else:
            data['profit_loss_percentage'] = 0.0

    summary_data = [
        row for row in combined_data.values()
        if row['total_expense'] != 0.0 or row['total_invoice_cost'] != 0.0
    ]
    chart_labels = [row['unit'] for row in summary_data]
    chart_income = [row['total_invoice_cost'] for row in summary_data]
    chart_expenses = [row['total_expense'] for row in summary_data]
    chart_profit_loss = [row['profit_loss'] for row in summary_data]

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
        'chart_profit_loss': chart_profit_loss,
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

    income_data = income_queryset.values(
        branch_name=F('wh_branch__loc_name'),
        unit_name=F('wh_unit__unit_name'),
        businessmodel=F('wh_customer_type__tb_trbusinesstype')
    ).annotate(total_income=Sum('wh_total_invoice_cost'))

    expense_queryset = ExpenseExtinfo.objects.all()
    if branch_filter:
        expense_queryset = expense_queryset.filter(exp_ext_branch__loc_name=branch_filter)
    if unit_filter:
        expense_queryset = expense_queryset.filter(exp_ext_unit__unit_name=unit_filter)
    if from_date:
        expense_queryset = expense_queryset.filter(exp_ext_updated_on__gte=from_date)
    if to_date:
        expense_queryset = expense_queryset.filter(exp_ext_updated_on__lte=to_date)

    expense_data = (
        expense_queryset.values(
            branch_name=F('exp_ext_branch__loc_name'),
            unit_name=F('exp_ext_unit__unit_name'),
        )
        .annotate(total_expense=Sum('exp_ext_amount'))
    )

    results = []
    for income in income_data:
        branch = income['branch_name']
        unit = income['unit_name']
        businessmodel = income['businessmodel']
        total_income = income['total_income']

        matching_expense = next(
            (exp for exp in expense_data if exp['branch_name'] == branch and exp['unit_name'] == unit), None
        )
        total_expense = matching_expense['total_expense'] if matching_expense else 0

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

    chart_labels = list(chart_data.keys())
    income_values = [data['income'] for data in chart_data.values()]
    expense_values = [data['expense'] for data in chart_data.values()]
    profit_loss_values = [data['profit_loss'] for data in chart_data.values()]

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

    if from_date:
        invoice_filters &= Q(wh_checkin_time__gte=from_date)
        expense_filters &= Q(exp_ext_updated_on__gte=from_date)
    if to_date:
        invoice_filters &= Q(wh_checkin_time__lte=to_date)
        expense_filters &= Q(exp_ext_updated_on__lte=to_date)

    total_expenses_subquery = ExpenseExtinfo.objects.filter(
        exp_ext_branch=OuterRef('wh_branch')
    ).values('exp_ext_branch').annotate(
        total_expenses=Sum('exp_ext_amount')
    ).values('total_expenses')

    business_summary = Warehouse_goods_info.objects.values(
        'wh_customer_type__tb_trbusinesstype',
        'wh_branch__loc_name',
        'wh_customer_name__cu_nameshort'
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

    if selected_branch:
        business_summary = business_summary.filter(wh_branch__loc_name=selected_branch)
    if selected_businessmodel:
        business_summary = business_summary.filter(wh_customer_type__tb_trbusinesstype=selected_businessmodel)


    chart_summary = Warehouse_goods_info.objects.values(
        'wh_customer_type__tb_trbusinesstype'  # Group by customer type
    ).annotate(
        total_invoice_amount=Coalesce(Sum('wh_total_invoice_cost', filter=invoice_filters), 0.0),
        total_expenses=Coalesce(Sum(Subquery(total_expenses_subquery)), 0.0),
        profit_loss=F('total_invoice_amount') - F('total_expenses')
    )

    chart_labels = []
    income_values = []
    expense_values = []
    profit_loss_values = []

    for entry in chart_summary:
        customer_type = entry['wh_customer_type__tb_trbusinesstype']
        chart_labels.append(customer_type)
        income_values.append(entry['total_invoice_amount'] or 0)
        expense_values.append(entry['total_expenses'] or 0)
        profit_loss_values.append(entry['profit_loss'] or 0)

    context = {
        'business_summary': business_summary,
        'first_name': first_name,
        'branches': branches,
        'businessmodels': businessmodels,
        'selected_branch': selected_branch,
        'selected_businessmodel': selected_businessmodel,
        'from_date': from_date,
        'to_date': to_date,
        'chart_labels': chart_labels,
        'income_values': income_values,
        'expense_values': expense_values,
        'profit_loss_values': profit_loss_values,
    }

    return render(request, "asset_mgt_app/fin_customerwise_PL_report.html", context)


def fin_profit_loss_view(request):
    first_name = request.session.get('first_name')
    branch_filter = request.GET.get('branch')
    unit_filter = request.GET.get('unit')
    businessmodel_filter = request.GET.get('businessmodel')
    customer_filter = request.GET.get('customer')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    branches = Location_info.objects.all()
    customers= CustomerInfo.objects.all()
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
    if customer_filter:
        income_queryset = income_queryset.filter(wh_customer_name__cu_nameshort=customer_filter)
    if businessmodel_filter:
        income_queryset = income_queryset.filter(wh_customer_type__tb_trbusinesstype=businessmodel_filter)
    if from_date:
        income_queryset = income_queryset.filter(wh_checkin_time__gte=from_date)
    if to_date:
        income_queryset = income_queryset.filter(wh_checkin_time__lte=to_date)

    income_data = income_queryset.values(
        branch_name=F('wh_branch__loc_name'),
        unit_name=F('wh_unit__unit_name'),
    ).annotate(
        total_income=Sum('wh_total_invoice_cost')
    )

    expense_queryset = ExpenseExtinfo.objects.all()
    if branch_filter:
        expense_queryset = expense_queryset.filter(exp_ext_branch__loc_name=branch_filter)
    if unit_filter:
        expense_queryset = expense_queryset.filter(exp_ext_unit__unit_name=unit_filter)
    if from_date:
        expense_queryset = expense_queryset.filter(exp_ext_updated_on__gte=from_date)
    if to_date:
        expense_queryset = expense_queryset.filter(exp_ext_updated_on__lte=to_date)

    expense_data = (
        expense_queryset.values(
            branch_name=F('exp_ext_branch__loc_name'),
            unit_name=F('exp_ext_unit__unit_name'),
        )
        .annotate(total_expense=Sum('exp_ext_amount'))
    )

    results = []
    chart_labels = []
    income_values = []
    expense_values = []
    profit_loss_values = []

    for income in income_data:
        branch = income['branch_name']
        unit = income['unit_name']
        total_income = income['total_income']

        matching_expense = next(
            (exp for exp in expense_data if exp['branch_name'] == branch and exp['unit_name'] == unit), None
        )
        total_expense = matching_expense['total_expense'] if matching_expense else 0

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
        label = f"{branch} - {unit}"
        chart_labels.append(label)
        income_values.append(total_income)
        expense_values.append(total_expense)
        profit_loss_values.append(profit_loss)

    context = {
        'first_name':first_name,
        'results': results,
        'branches': branches,
        'customers': customers,
        'businessmodels': businessmodels,
        'branch_filter': branch_filter,
        'customer_filter': customer_filter,
        'businessmodel_filter': businessmodel_filter,
        'chart_labels': chart_labels,
        'income_values': income_values,
        'expense_values': expense_values,
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
    units = UnitInfo.objects.values_list('unit_name', flat=True).distinct()
    companies = Business_Sol_info.objects.values_list('bvm_business', flat=True).distinct()
    expense_summary = ExpenseExtinfo.objects.all()

    if branch_filter:
        units = expense_summary.filter(exp_ext_branch__loc_name=branch_filter).values_list('exp_ext_unit__unit_name', flat=True).distinct()
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
        'units': units,
        'companies': companies,
        'branch_filter': branch_filter,
        'unit_filter': unit_filter,
        'company_filter': company_filter,
        'from_date': request.GET.get('from_date', ''),
        'to_date': request.GET.get('to_date', ''),
        'expense_summary': expense_summary,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }

    return render(request, "asset_mgt_app/fin_expenses_report.html", context)


DUE_DAY_GROUPS = [
    (0, 15, '0-15 Days', 1),
    (16, 30, '16-30 Days', 2),
    (31, 45, '31-45 Days', 3),
    (46, 60, '46-60 Days', 4),
    (61, 90, '61-90 Days', 5),
    (91, 120, '91-120 Days', 6),
    (121, 180, '121-180 Days', 7),
    (181, 999999, '180-above Days', 8),
]


def get_due_day_case_expression(field_name):

    return Case(
        *[
            When(**{f"{field_name}__gte": start, f"{field_name}__lte": end}, then=Value(label))
            for start, end, label, _ in DUE_DAY_GROUPS
        ],
        default=Value('Unknown'),
        output_field=CharField()
    )


def get_due_day_sort_expression(field_name):

    return Case(
        *[
            When(**{f"{field_name}": label}, then=Value(order))
            for _, _, label, order in DUE_DAY_GROUPS
        ],
        default=Value(999),
        output_field=IntegerField()
    )


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

    due_from_submission_data = (
        ar_summary
        .annotate(due_range=get_due_day_case_expression('ar_due_from_submission_date'))
        .annotate(due_order=get_due_day_sort_expression('due_range'))
        .values('due_range', 'due_order')
        .annotate(total_amount=Sum('ar_amount'))
        .order_by('due_order')  # Ensure sorting
    )

    due_from_operation_data = (
        ar_summary
        .annotate(due_range=get_due_day_case_expression('ar_due_from_operation_date'))
        .annotate(due_order=get_due_day_sort_expression('due_range'))
        .values('due_range', 'due_order')
        .annotate(total_amount=Sum('ar_amount'))
        .order_by('due_order')
    )

    due_from_invoice_data = (
        ar_summary
        .annotate(due_range=get_due_day_case_expression('ar_due_from_invoice_date'))
        .annotate(due_order=get_due_day_sort_expression('due_range'))
        .values('due_range', 'due_order')
        .annotate(total_amount=Sum('ar_amount'))
        .order_by('due_order')
    )

    submission_labels = [entry['due_range'] for entry in due_from_submission_data]
    submission_amounts = [entry['total_amount'] for entry in due_from_submission_data]

    operation_labels = [entry['due_range'] for entry in due_from_operation_data]
    operation_amounts = [entry['total_amount'] for entry in due_from_operation_data]

    invoice_labels = [entry['due_range'] for entry in due_from_invoice_data]
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


INCOME_CATEGORIES = {
    "Airport Handling Charges": "bf_Airport_Handling_Charges",
    "Forklift Handling Charges": "bf_Forklift_Handling_Charges",
    "Crane Handling Charges": "bf_Crane_Handling_Charges",
    "Handling Charges": "bf_Handling_Charges",
    "Packing - Consumables & Spares": "bf_Packing_Charges",
    "Warehouse Handling Charges": "bf_Warehouse_Handling_Charges",
    "Warehouse Loading Charges": "bf_Warehouse_Loading_Charges",
    "Storage Expenses": "bf_Warehouse_Storage_Charges",
    "Unloading Expenses":"bf_Warehouse_Unloading_Charges",
}
DEPARTMENT_EXPENSES_CATEGORIES = {
    "Audit Fee": "bf_audit_fees",
    "Bad Debts": "bf_bad_debts",
    "Bank Charges": "bf_bank_charges",
    "Consultancy Charges": "bf_consultancy_charges",
    "Celebration Expenses": "bf_celebration_expenses",
    "Directors Remuneration": "bf_directors_remuneration",
    "Insurance Car": "bf_insurance_car",
    "Interest On Statutory Dues": "bf_interest_on_statutory_dues",
    "Professional & Legal Charges": "bf_professional_legal_charges",
    "Subscription Membership": "bf_subscription_membership",
}
EMPLOYEE_BENEFITS_CATEGORIES = {
    "Corp Staff": "bf_corp_staff",
    "Bonus Corp Staff": "bf_bonus_corp_staff",
    "EDLI Contribution Corp Staff": "bf_EDLI_contribution_corp_staff",
    "Employer Contribution to ESI Corp Staff": "bf_employer_contribution_to_ESI_corp_staff",
    "Employer Contribution to PF Corp Staff": "bf_employer_contribution_to_PF_corp_staff",
    "EPF Admin Charges Corp Staff": "bf_EPF_admin_charges_corp_staff",
    "Gratuity Corp Staff": "bf_gratuity_corp_staff",
    "Salaries Wages Corp Staff": "bf_salaries_wages_corp_staff",

    "Dept Staff": "bf_dept_staff",
    "Bonus Staff": "bf_bonus_staff",
    "EDLI Contribution Staff": "bf_EDLI_contribution_staff",
    "Employer Contribution to ESI Staff": "bf_employer_contribution_to_ESI_staff",
    "Employer Contribution to PF Staff": "bf_employer_contribution_to_PF_staff",
    "EPF Admin Charges Staff": "bf_EPF_admin_charges_staff",
    "Gratuity Staff": "bf_gratuity_staff",
    "Salaries Wages Staff": "bf_salaries_wages_staff",
}
INTEREST_EXPENSES_CATEGORIES = {
    "Interest on Borrowings": "bf_interest_on_borrowings",
    "Interest on Other Loans ": "bf_interest_on_other_loans",
}
OPERATIONAL_EXPENSES_CATEGORIES = {
    "Operational Expenses Fixed": "bf_fixed",
    "Depreciation Expenses":"bf_depreciation",
    "Software AMC Charges Expenses":"bf_software_AMC_charges",
    "Insurance Expenses - Warehouse": "bf_insurance_warehouse",
    "Rates & Taxes Expenses": "bf_rates_taxes",
    "Rent - Premises Expenses": "bf_rent_premises",
    "Security Service Charges Expenses": "bf_security_service_charges",
    "Manpower Supply Expenses": "bf_manpower_supply_expenses",

    "Operational Expenses Variable": "bf_variable",
    "Crane Handling Expenses": "bf_crane_handling_expenses",
    "Diesel Expenses - Forklift": "bf_diesel_expenses_forklift",
    "Forklift Handling Expenses": "bf_forklift_handling_expenses",
    "Fumigation Expenses":"bf_fumigation_expenses",
}
NON_OPERATIONAL_EXPENSES_CATEGORIES = {
    "Non-Operational Expenses Fixed": "bf_oe_Fixed",
    "Housekeeping Salary": "bf_housekeeping_salary",
    "Insurance Corp Staff": "bf_insurance_corp_staff",
    "Insurance Staff": "bf_insurance_staff",
    "Internet Data Card Expenses": "bf_internet_data_card_expenses",
    "Rent - Plant & Machinery Expenses":"bf_rent_plant_machinery",
    "System AMC Expenses": "bf_system_amc",

    "Non-Operational Expenses Variable": "bf_oe_variable",
    "Advertisement & Business Promotion Expenses": "bf_advertisement_business_promotion",
    "Conveyance Expenses": "bf_conveyance_expenses",
    "Diesel Expenses - Genset":"bf_diesel_expenses_gense",
    "Handling Expenses": "bf_handling_expenses",
    "Hotel Boarding Lodging Expenses": "bf_hotel_boarding_lodging_expenses",
    "Office Repairs and Maintenance Expenses": "bf_office_repairs_maintenance",
    "Office Supplies & General Expenses": "bf_office_supplies_general_expenses",
    "Postage & Courier Expenses": "bf_postage_courier",
    "Power and Fuel Expenses": "bf_power_fuel",
    "Printing & Stationery Expenses": "bf_printing_stationery",
    "Service and Maintanance Expenses": "bf_service_maintenance_expenses",
    "Staff Welfare Expenses": "bf_staff_welfare_staff",
    "Telephone and Mobile Expenses": "bf_telephone_mobile_expenses",
    "Training Expenses": "bf_training_expenses",
    "Travelling Expenses" : "bf_travelling_expenses",

}

BUDGET_FIELD_MAPPING = {
    "TV Expense":None,
    "Salary Expenses":None,
    "Transportation Expenses":None,
    "Air Conditioning Expenses":None,

    "Airport Handling Charges": "bf_Airport_Handling_Charges",
    "Forklift Handling Charges": "bf_Forklift_Handling_Charges",
    "Crane Handling Charges": "bf_Crane_Handling_Charges",
    "Handling Charges": "bf_Handling_Charges",
    "Packing - Consumables & Spares": "bf_Packing_Charges",
    "Warehouse Handling Charges": "bf_Warehouse_Handling_Charges",
    "Warehouse Loading Charges": "bf_Warehouse_Loading_Charges",
    "Storage Expenses": "bf_Warehouse_Storage_Charges",
    "Unloading Expenses": "bf_Warehouse_Unloading_Charges",
    "Audit Fee": "bf_audit_fees",
    "Bad Debts": "bf_bad_debts",
    "Bank Charges": "bf_bank_charges",
    "Consultancy Charges": "bf_consultancy_charges",
    "Celebration Expenses": "bf_celebration_expenses",
    "Directors Remuneration": "bf_directors_remuneration",
    "Insurance Car": "bf_insurance_car",
    "Interest On Statutory Dues": "bf_interest_on_statutory_dues",
    "Professional & Legal Charges": "bf_professional_legal_charges",
    "Subscription Membership": "bf_subscription_membership",
    "Corp Staff": "bf_corp_staff",
    "Bonus Corp Staff": "bf_bonus_corp_staff",
    "EDLI Contribution Corp Staff": "bf_EDLI_contribution_corp_staff",
    "Employer Contribution to ESI Corp Staff": "bf_employer_contribution_to_ESI_corp_staff",
    "Employer Contribution to PF Corp Staff": "bf_employer_contribution_to_PF_corp_staff",
    "EPF Admin Charges Corp Staff": "bf_EPF_admin_charges_corp_staff",
    "Gratuity Corp Staff": "bf_gratuity_corp_staff",
    "Salaries Wages Corp Staff": "bf_salaries_wages_corp_staff",

    "Dept Staff": "bf_dept_staff",
    "Bonus Staff": "bf_bonus_staff",
    "EDLI Contribution Staff": "bf_EDLI_contribution_staff",
    "Employer Contribution to ESI Staff": "bf_employer_contribution_to_ESI_staff",
    "Employer Contribution to PF Staff": "bf_employer_contribution_to_PF_staff",
    "EPF Admin Charges Staff": "bf_EPF_admin_charges_staff",
    "Gratuity Staff": "bf_gratuity_staff",
    "Salaries Wages Staff": "bf_salaries_wages_staff",
    "Interest on Borrowings": "bf_interest_on_borrowings",
    "Interest on Other Loans ": "bf_interest_on_other_loans",
    "Operational Expenses Fixed": "bf_fixed",
    "Depreciation Expenses": "bf_depreciation",
    "Software AMC Charges Expenses": "bf_software_AMC_charges",
    "Insurance Expenses - Warehouse": "bf_insurance_warehouse",
    "Rates & Taxes Expenses": "bf_rates_taxes",
    "Rent - Premises Expenses": "bf_rent_premises",
    "Security Service Charges Expenses": "bf_security_service_charges",
    "Manpower Supply Expenses": "bf_manpower_supply_expenses",

    "Operational Expenses Variable": "bf_variable",
    "Crane Handling Expenses": "bf_crane_handling_expenses",
    "Diesel Expenses - Forklift": "bf_diesel_expenses_forklift",
    "Forklift Handling Expenses": "bf_forklift_handling_expenses",
    "Fumigation Expenses": "bf_fumigation_expenses",
    "Non-Operational Expenses Fixed": "bf_oe_Fixed",
    "Housekeeping Salary": "bf_housekeeping_salary",
    "Insurance Corp Staff": "bf_insurance_corp_staff",
    "Insurance Staff": "bf_insurance_staff",
    "Internet Data Card Expenses": "bf_internet_data_card_expenses",
    "Rent - Plant & Machinery Expenses":"bf_rent_plant_machinery",
    "System AMC Expenses": "bf_system_amc",

    "Non-Operational Expenses Variable": "bf_oe_variable",
    "Advertisement & Business Promotion Expenses": "bf_advertisement_business_promotion",
    "Conveyance Expenses": "bf_conveyance_expenses",
    "Diesel Expenses - Genset":"bf_diesel_expenses_gense",
    "Handling Expenses": "bf_handling_expenses",
    "Hotel Boarding Lodging Expenses": "bf_hotel_boarding_lodging_expenses",
    "Office Repairs and Maintenance Expenses": "bf_office_repairs_maintenance",
    "Office Supplies & General Expenses": "bf_office_supplies_general_expenses",
    "Postage & Courier Expenses": "bf_postage_courier",
    "Power and Fuel Expenses": "bf_power_fuel",
    "Printing & Stationery Expenses": "bf_printing_stationery",
    "Service and Maintanance Expenses": "bf_service_maintenance_expenses",
    "Staff Welfare Expenses": "bf_staff_welfare_staff",
    "Telephone and Mobile Expenses": "bf_telephone_mobile_expenses",
    "Training Expenses": "bf_training_expenses",
    "Travelling Expenses" : "bf_travelling_expenses",


}
OTHER_EXPENSES_CATEGORIES = {k: v for k, v in BUDGET_FIELD_MAPPING.items() if v not in (
    set(INCOME_CATEGORIES.values()) |
    set(DEPARTMENT_EXPENSES_CATEGORIES.values()) |
    set(EMPLOYEE_BENEFITS_CATEGORIES.values()) |
    set(INTEREST_EXPENSES_CATEGORIES.values()) |
    set(OPERATIONAL_EXPENSES_CATEGORIES.values()) |
    set(NON_OPERATIONAL_EXPENSES_CATEGORIES.values())

)}


def budget_expense(request):
    first_name = request.session.get('first_name')
    selected_branch = request.GET.get('branch')
    selected_unit = request.GET.get('unit')
    selected_company = request.GET.get('company')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    branches = Location_info.objects.all()
    units = UnitInfo.objects.values_list('unit_name', flat=True).distinct()
    companies = Business_Sol_info.objects.values_list('bvm_business', flat=True).distinct()

    if selected_branch:
        units = UnitInfo.objects.filter(ui_branch_name__loc_name=selected_branch).values_list('unit_name', flat=True).distinct()

    expenses_filter = {}
    budget_filter = {}

    if selected_company:
        expenses_filter['exp_ext_expense_number__exp_business__bvm_business'] = selected_company
        budget_filter['bf_company__bvm_business'] = selected_company

    if selected_branch:
        expenses_filter['exp_ext_branch__loc_name'] = selected_branch
        budget_filter['bf_location__loc_name'] = selected_branch

    if selected_unit:
        expenses_filter['exp_ext_unit__unit_name'] = selected_unit
        budget_filter['bf_unit_reference__unit_name'] = selected_unit

    if from_date:
        from_date = timezone.make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
        expenses_filter['exp_ext_updated_on__gte'] = from_date
        budget_filter['bf_updated_at__gte'] = from_date

    if to_date:
        to_date = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))
        expenses_filter['exp_ext_updated_on__lte'] = to_date
        budget_filter['bf_updated_at__lte'] = to_date

    # Get total expenses per category
    expense_summary = ExpenseExtinfo.objects.filter(**expenses_filter).values(
        'exp_ext_expense_number__exp_expense_type__exp_type_name'
    ).annotate(total_expense=Sum('exp_ext_amount'))

    # Convert expenses to dictionary
    expense_dict = {
        item['exp_ext_expense_number__exp_expense_type__exp_type_name']: item['total_expense']
        for item in expense_summary
    }

    budget_totals = BudgetInfo.objects.filter(**budget_filter).aggregate(**{
        field: Sum(field) for field in BUDGET_FIELD_MAPPING.values() if field is not None
    })

    # Convert budget data into a dictionary
    budget_dict = {
        category: budget_totals.get(field, 0.0) if field else 0.0
        for category, field in BUDGET_FIELD_MAPPING.items()
    }

    # Function to generate summaries
    def get_category_summary(category_mapping):
        summary = []
        for category, field in category_mapping.items():
            total_budget = budget_dict.get(category, 0.0) or 0.0  # Ensure default value is 0.0
            total_expense = expense_dict.get(category, 0.0) or 0.0  # Ensure default value is 0.0
            difference = total_budget - total_expense
            pl_percentage = (difference / total_budget * 100) if total_budget > 0 else 0.0  # P/L %

            summary.append({
                "expense_type": category,
                "total_budget": total_budget,
                "total_expense": total_expense,
                "difference": difference,
                "pl_percentage": pl_percentage,
            })
        return summary

    income_summary = get_category_summary(INCOME_CATEGORIES)
    department_expenses_summary = get_category_summary(DEPARTMENT_EXPENSES_CATEGORIES)
    employee_benefits_summary = get_category_summary(EMPLOYEE_BENEFITS_CATEGORIES)
    interest_summary = get_category_summary(INTEREST_EXPENSES_CATEGORIES)
    operational_summary = get_category_summary(OPERATIONAL_EXPENSES_CATEGORIES)
    non_operational_summary = get_category_summary(NON_OPERATIONAL_EXPENSES_CATEGORIES)
    other_expenses_summary = get_category_summary(OTHER_EXPENSES_CATEGORIES)

    total_budget = sum(value if value is not None else 0.0 for value in budget_dict.values())
    total_expense = sum(value if value is not None else 0.0 for value in expense_dict.values())
    total_profit_loss = total_budget - total_expense
    total_pl_percentage = (total_profit_loss / total_budget * 100) if total_budget > 0 else 0.0

    # Pass data to the template
    return render(request, "asset_mgt_app/fin_budget_expense_report.html", {
        "income_summary": income_summary,
        "department_expenses_summary": department_expenses_summary,
        "employee_benefits_summary": employee_benefits_summary,
        "interest_summary": interest_summary,
        "operational_summary": operational_summary,
        "non_operational_summary": non_operational_summary,
        "other_expenses_summary": other_expenses_summary,
        'total_budget': total_budget,
        'total_expense': total_expense,
        'total_profit_loss': total_profit_loss,
        'total_pl_percentage': total_pl_percentage,
        'branches': branches,
        'units': units,
        'companies': companies,
        'selected_company': selected_company,
        'selected_branch': selected_branch,
        'selected_unit': selected_unit,
        'first_name': first_name,
        'from_date': request.GET.get('from_date', ''),
        'to_date': request.GET.get('to_date', ''),
    })