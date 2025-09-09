from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Q, Sum, Case, When, Value, CharField, Min, FloatField, F, IntegerField, \
    ExpressionWrapper, fields
from django.db.models import F, Subquery, OuterRef
from django.db.models.functions import Coalesce, Round, ExtractMonth, Now
from django.utils import timezone
from calendar import month_name
from django.db.models.functions import TruncMonth
from django.core.serializers import serialize
import json
from django.utils.timezone import make_aware, now
from datetime import datetime, timedelta
from ..models import Warehouse_goods_info, ExpenseExtinfo, Location_info, UnitInfo, Business_Sol_info, \
    TrbusinesstypeInfo, CustomerInfo, ExpenseTypeInfo, Ar_Info, BudgetInfo, ExpenseInfo, BilingInfo


def finance_reports(request):
    first_name = request.session.get('first_name')
    context = {
        'first_name': first_name
    }
    return render(request, "asset_mgt_app/finance_reports.html", context)


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
        expenses_filter['exp_ext_expense_number__exp_service_start_date__gte'] = from_date
        invoices_filter['wh_checkin_time__gte'] = from_date

    if to_date:
        to_date = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))
        expenses_filter['exp_ext_expense_number__exp_service_start_date__lte'] = to_date
        invoices_filter['wh_checkin_time__lte'] = to_date

    expenses_data = (
        ExpenseExtinfo.objects.filter(**expenses_filter)
        .annotate(month=TruncMonth('exp_ext_expense_number__exp_service_start_date'))  # create "month"
        .values('exp_ext_branch', 'exp_ext_branch__loc_name', 'month')  # now you can use it
        .annotate(total_expense=Sum('exp_ext_amount'))
    )
    invoice_data = (
        Warehouse_goods_info.objects.filter(**invoices_filter)
        .annotate(month=TruncMonth('wh_checkin_time'))  # create "month"
        .values('wh_branch', 'wh_branch__loc_name', 'month')  # now you can use it
        .annotate(total_invoice_cost=Sum('wh_total_invoice_cost'))
    )
    # invoice_data = []
    # voucher_groups = Warehouse_goods_info.objects.filter(**invoices_filter).values('wh_branch', 'wh_branch__loc_name',
    #                                                                                'wh_voucher_num').distinct()

    # for entry in voucher_groups:
    #     voucher = entry['wh_voucher_num']
    #     branch = entry['wh_branch']
    #     branch_name = entry['wh_branch__loc_name']
    #     try:
    #         if voucher:
    #             clean_voucher = voucher.strip()
    #             print(f"Looking for: {clean_voucher}")
    #             pre_gst_total = (
    #                     BilingInfo.objects
    #                     .filter(bill_invoice_ref__iexact=clean_voucher)
    #                     .aggregate(total=Sum('bill_total_pre_gst'))['total'] or 0
    #             )
    #         else:
    #             print(" Skipping: voucher is None or empty.")
    #             pre_gst_total = 0
    #
    #         invoice_data.append({
    #             'wh_branch': branch,
    #             'wh_branch__loc_name': branch_name,
    #             'total_invoice_cost': pre_gst_total
    #         })
    #     except BilingInfo.DoesNotExist:
    #         continue

    combined_data = {}

    for expense in expenses_data:
        key = (expense['exp_ext_branch'], expense['month'])
        combined_data[key] = {
            'branch': expense['exp_ext_branch__loc_name'],
            'month': expense['month'].strftime("%b-%Y") if expense['month'] else '',
            'total_expense': expense['total_expense'],
            'total_invoice_cost': 0.0,
            'profit_loss': -expense['total_expense'],
            'profit_loss_percentage': 0.0,
        }

    for invoice in invoice_data:
        key = (invoice['wh_branch'], invoice['month'])
        if key in combined_data:
            combined_data[key]['total_invoice_cost'] = invoice['total_invoice_cost']
            combined_data[key]['profit_loss'] += invoice['total_invoice_cost']
        else:
            combined_data[key] = {
                'branch': invoice['wh_branch__loc_name'],
                'month': invoice['month'].strftime("%b-%Y") if invoice['month'] else '',
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
    chart_labels = [f"{row['branch']} ({row['month']})" for row in summary_data]

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
        expenses_filter['exp_ext_expense_number__exp_service_start_date__gte'] = from_date
        invoices_filter['wh_checkin_time__gte'] = from_date

    if to_date:
        to_date = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))
        expenses_filter['exp_ext_expense_number__exp_service_start_date__lte'] = to_date
        invoices_filter['wh_checkin_time__lte'] = to_date

    expenses_data = (
        ExpenseExtinfo.objects.filter(**expenses_filter)
        .annotate(month=TruncMonth('exp_ext_expense_number__exp_service_start_date'))
        .values('exp_ext_branch', 'exp_ext_unit', 'exp_ext_branch__loc_name', 'exp_ext_unit__unit_name', 'month')
        .annotate(total_expense=Sum('exp_ext_amount'))
    )

    invoice_data = (
        Warehouse_goods_info.objects.filter(**invoices_filter)
        .annotate(month=TruncMonth('wh_checkin_time'))
        .values('wh_branch', 'wh_unit', 'wh_branch__loc_name', 'wh_unit__unit_name', 'month')
        .annotate(total_invoice_cost=Sum('wh_total_invoice_cost'))
    )

    combined_data = {}

    for expense in expenses_data:
        key = (expense['exp_ext_branch'], expense['exp_ext_unit'], expense['month'])
        combined_data[key] = {
            'branch': expense['exp_ext_branch__loc_name'],
            'unit': expense['exp_ext_unit__unit_name'],
            'month': expense['month'].strftime('%b-%Y') if expense['month'] else '',
            'total_expense': expense['total_expense'],
            'total_invoice_cost': 0.0,
            'profit_loss': -expense['total_expense'],
            'profit_loss_percentage': 0.0,
        }

    for invoice in invoice_data:
        key = (invoice['wh_branch'], invoice['wh_unit'], invoice['month'])
        if key in combined_data:
            combined_data[key]['total_invoice_cost'] = invoice['total_invoice_cost']
            combined_data[key]['profit_loss'] += invoice['total_invoice_cost']
        else:
            combined_data[key] = {
                'branch': invoice['wh_branch__loc_name'],
                'unit': invoice['wh_unit__unit_name'],
                'month': invoice['month'].strftime('%b-%Y') if invoice['month'] else '',
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
    chart_labels = [f"{row['unit']} ({row['month']})" for row in summary_data]
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
        expense_queryset = expense_queryset.filter(exp_ext_expense_number__exp_service_start_date__gte=from_date)
    if to_date:
        expense_queryset = expense_queryset.filter(exp_ext_expense_number__exp_service_start_date__lte=to_date)

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
        expense_filters &= Q(exp_ext_expense_number__exp_service_start_date__gte=from_date)
    if to_date:
        invoice_filters &= Q(wh_checkin_time__lte=to_date)
        expense_filters &= Q(exp_ext_expense_number__exp_service_start_date__lte=to_date)

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
    customers = CustomerInfo.objects.all()
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
        expense_queryset = expense_queryset.filter(exp_ext_expense_number__exp_service_start_date__gte=from_date)
    if to_date:
        expense_queryset = expense_queryset.filter(exp_ext_expense_number__exp_service_start_date__lte=to_date)

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
        'first_name': first_name,
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
        units = expense_summary.filter(exp_ext_branch__loc_name=branch_filter).values_list('exp_ext_unit__unit_name',
                                                                                           flat=True).distinct()
        expense_summary = expense_summary.filter(exp_ext_branch__loc_name=branch_filter)

    if unit_filter:
        expense_summary = expense_summary.filter(exp_ext_unit__unit_name=unit_filter)

    if from_date:
        from_date = timezone.make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
        expense_summary = expense_summary.filter(exp_ext_expense_number__exp_service_start_date__gte=from_date)

    if to_date:
        to_date = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))
        expense_summary = expense_summary.filter(exp_ext_expense_number__exp_service_start_date__lte=to_date)
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
    chart_labels_json = json.dumps(chart_labels)
    chart_data_json = json.dumps(chart_data)

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
        'chart_labels': chart_labels_json,
        'chart_data': chart_data_json,
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



from django.core.paginator import Paginator


@login_required(login_url='login_page')
def overdue_jobs_report(request):
    first_name = request.session.get('first_name')
    branch_filter = request.GET.get('branch')
    unit_filter = request.GET.get('unit')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    today = now().date()
    jobs = (
        Warehouse_goods_info.objects
        .filter(wh_check_in_out=2, wh_voucher_num__isnull=True, wh_checkout_time__isnull=False)
        .select_related("wh_customer_name", "wh_branch", "wh_unit")
    )
    branches = Location_info.objects.all()
    units = UnitInfo.objects.values_list('unit_name', flat=True).distinct()
    if branch_filter:
        units = jobs.filter(wh_branch__loc_name=branch_filter).values_list('wh_unit__unit_name',
                                                                           flat=True).distinct()
        jobs = jobs.filter(wh_branch__loc_name=branch_filter)

    if unit_filter:
        jobs = jobs.filter(wh_unit__unit_name=unit_filter)

    if from_date:
        jobs = jobs.filter(wh_checkout_time__date__gte=from_date)

    if to_date:
        jobs = jobs.filter(wh_checkout_time__date__lte=to_date)
    jobs = jobs.annotate(
        days_since_checkout=ExpressionWrapper(
            Now() - F('wh_checkout_time'),
            output_field=fields.DurationField()
        )
    )

    paginator = Paginator(jobs, 50)  # 50 jobs per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "asset_mgt_app/overdue_job_report.html", {
        "jobs": page_obj,
        "first_name": first_name,
        "branches": branches,
        "units": units,
        "branch_filter": branch_filter,
        "unit_filter": unit_filter,
        "from_date": request.GET.get('from_date', ''),
        "to_date": request.GET.get('to_date', ''),
    })

INCOME_CATEGORIES = {
    "Airport Handling Charges": "bf_Airport_Handling_Charges",
    "Forklift Handling Charges": "bf_Forklift_Handling_Charges",
    "Crane Handling Charges": "bf_Crane_Handling_Charges",
    "Handling Charges": "bf_Handling_Charges",
    "Packing Expenses": "bf_Packing_Charges",
    "Warehouse Handling Charges": "bf_Warehouse_Handling_Charges",
    "Warehouse Loading Charges": "bf_Warehouse_Loading_Charges",
    "Warehouse Storage Charges": "bf_Warehouse_Storage_Charges",
    "Warehouse Unloading Charges": "bf_Warehouse_Unloading_Charges",
}
WAREHOUSE_EXPENSE_FIELD_MAPPING = {
    "Airport Handling Charges": None,  # If this isn't tracked in Warehouse_goods_info
    "Forklift Handling Charges": "wh_forklift_cost",
    "Crane Handling Charges": "wh_crane_cost",
    "Handling Charges": None,  # Assuming this is overall handling
    "Packing Expenses": None,
    "Warehouse Handling Charges": None,  # Optional: reuse if no other field
    "Warehouse Loading Charges": "wh_total_loading_cost",
    "Warehouse Storage Charges": "wh_storage_cost_total",
    "Warehouse Unloading Charges": None,  # Assuming not tracked
}

DEPARTMENT_EXPENSES_CATEGORIES = {
    "Advertisement & Business Promotion Expenses": "bf_advertisement_business_promotion",
    # "Audit Fee": "bf_audit_fees",
    # "Bad Debts": "bf_bad_debts",
    "Bank Charges": "bf_bank_charges",
    "Consultancy Charges": "bf_consultancy_charges",
    "Celebration Expenses": "bf_celebration_expenses",
    "Directors Remuneration": "bf_directors_remuneration",
    "Housekeeping Salary": "bf_housekeeping_salary",
    # "Insurance Car": "bf_insurance_car",
    "Interest On Statutory Dues": "bf_interest_on_statutory_dues",
    "Office Repairs and Maintenance Expenses": "bf_office_repairs_maintenance",
    "Professional & Legal Charges": "bf_professional_legal_charges",
    "Rent Furniture fittings": "bf_rent_furniture_fittings",
    "Rent Office": "bf_rent_office",
    "Subscription Membership": "bf_subscription_membership",
}
EMPLOYEE_BENEFITS_CATEGORIES = {
    "Corp Staff": "bf_corp_staff",
    "Bonus Corp Staff": "bf_bonus_corp_staff",
    "EDLI Contribution Corp Staff": "bf_EDLI_contribution_corp_staff",
    "Employer Contribution to ESI Corp Staff": "bf_employer_contribution_to_ESI_corp_staff",
    "Employer Contribution to PF Corp Staff": "bf_employer_contribution_to_PF_corp_staff",
    "EPF Admin Charges Corp Staff": "bf_EPF_admin_charges_corp_staff",
    "Ex-Gratia Corp Staff": "bf_exgratia_corp_staff",
    "Gratuity Corp Staff": "bf_gratuity_corp_staff",
    "Incentive Corp Staff": "bf_incentive_corp_staff",
    "Insurance Corp Staff": "bf_insurance_corp_staff",
    "LWF Corp Staff": "bf_lwf_corp_staff",
    "Salaries Wages Corp Staff": "bf_salaries_wages_corp_staff",
    "Dept Staff": "bf_dept_staff",
    "Bonus Staff": "bf_bonus_staff",
    "EDLI Contribution Staff": "bf_EDLI_contribution_staff",
    "Employer Contribution to ESI Staff": "bf_employer_contribution_to_ESI_staff",
    "Employer Contribution to PF Staff": "bf_employer_contribution_to_PF_staff",
    "EPF Admin Charges Staff": "bf_EPF_admin_charges_staff",
    "Ex-Gratia Dept Staff": "bf_exgratia_dept_staff",
    "Gratuity Staff": "bf_gratuity_staff",
    "Incentive Dept Staff": "bf_incentive_dept_staff",
    "Insurance Staff": "bf_insurance_staff",
    "LWF Dept Staff": "bf_lwf_dept_staff",
    "Salaries Wages Staff": "bf_salaries_wages_staff",
}

OPERATIONAL_EXPENSES_CATEGORIES = {
    "Operational Expenses Fixed": "bf_fixed",
    "Insurance Expenses - Warehouse": "bf_insurance_warehouse",
    "Insurance - WCC": "bf_insurance_wcc",
    "Manpower Supply Expenses": "bf_manpower_supply_expenses",
    "Rent - Premises Expenses": "bf_rent_premises",
    "Security Service Charges Expenses": "bf_security_service_charges",
    "Operational Expenses Variable": "bf_variable",
    "Crane Handling Expenses": "bf_crane_handling_expenses",
    "Diesel Expenses - Forklift": "bf_diesel_expenses_forklift",
    "Forklift Handling Expenses": "bf_forklift_handling_expenses",
    "Fumigation Expenses": "bf_fumigation_expenses",
    "Packing Services": "bf_packing_services",
    "Support Handling": "bf_support_handling",
}
OPERATIONAL_EXPENSES_FIXED = {
    "Operational Expenses Fixed": "bf_fixed",
    "Insurance Expenses - Warehouse": "bf_insurance_warehouse",
    "Insurance - WCC": "bf_insurance_wcc",
    "Manpower Supply Expenses": "bf_manpower_supply_expenses",
    "Rent - Premises Expenses": "bf_rent_premises",
    "Security Service Charges Expenses": "bf_security_service_charges",

}
OPERATIONAL_EXPENSES_VARIABLE = {
    "Operational Expenses Variable": "bf_variable",
    "Crane Handling Expenses": "bf_crane_handling_expenses",
    "Diesel Expenses - Forklift": "bf_diesel_expenses_forklift",
    "Forklift Handling Expenses": "bf_forklift_handling_expenses",
    "Fumigation Expenses": "bf_fumigation_expenses",
    "Packing Services": "bf_packing_services",
    "Support Handling": "bf_support_handling",
}
NON_OPERATIONAL_EXPENSES_CATEGORIES = {
    "Non-Operational Expenses Fixed": "bf_oe_Fixed",
    "Depreciation Expenses": "bf_depreciation",
    "Internet Data Card Expenses": "bf_internet_data_card_expenses",
    # "Insurance Corp Staff": "bf_insurance_corp_staff",
    # "Insurance Staff": "bf_insurance_staff",

    "Rent - Plant & Machinery Expenses": "bf_rent_plant_machinery",
    "AMC Expenses": "bf_amc",
    "Software AMC Expenses": "bf_software_AMC_charges",

    "Non-Operational Expenses Variable": "bf_oe_variable",
    "CGST Ineligible ITC": "bf_CGST_ineligible_ITC",

    "Conveyance Expenses": "bf_conveyance_expenses",
    "Diesel Expenses - Genset": "bf_diesel_expenses_gense",
    "Handling Expenses": "bf_handling_expenses",
    "Hotel Boarding Lodging Expenses": "bf_hotel_boarding_lodging_expenses",
    "IGST Ineligible ITC": "bf_IGST_ineligible_ITC",

    "Office Supplies & General Expenses": "bf_office_supplies_general_expenses",
    "Postage & Courier Expenses": "bf_postage_courier",
    "Power and Fuel Expenses": "bf_power_fuel",
    "Printing & Stationery Expenses": "bf_printing_stationery",
    "Service and Maintanance Expenses": "bf_service_maintenance_expenses",
    "SGST Ineligible ITC": "bf_SGST_ineligible_ITC",
    "Staff Welfare Expenses": "bf_staff_welfare_staff",
    "Telephone and Mobile Expenses": "bf_telephone_mobile_expenses",
    "Training Expenses": "bf_training_expenses",
    "Travelling Expenses": "bf_travelling_expenses",

}

BUDGET_FIELD_MAPPING = {
    "TV Expense": None,
    "Salary Expenses": None,
    "Transportation Expenses": None,
    "Air Conditioning Expenses": None,

    "Airport Handling Charges": "bf_Airport_Handling_Charges",
    "Forklift Handling Charges": "bf_Forklift_Handling_Charges",
    "Crane Handling Charges": "bf_Crane_Handling_Charges",
    "Handling Charges": "bf_Handling_Charges",
    "Packing Expenses": "bf_Packing_Charges",
    "Warehouse Handling Charges": "bf_Warehouse_Handling_Charges",
    "Warehouse Loading Charges": "bf_Warehouse_Loading_Charges",
    "Warehouse Storage Charges": "bf_Warehouse_Storage_Charges",
    "Warehouse Unloading Charges": "bf_Warehouse_Unloading_Charges",
    # "Unloading Expenses": "bf_Warehouse_Unloading_Charges",
    "Advertisement & Business Promotion Expenses": "bf_advertisement_business_promotion",
    # "Audit Fee": "bf_audit_fees",
    # "Bad Debts": "bf_bad_debts",
    "Bank Charges": "bf_bank_charges",
    "Consultancy Charges": "bf_consultancy_charges",
    "Celebration Expenses": "bf_celebration_expenses",
    "Directors Remuneration": "bf_directors_remuneration",
    # "Insurance Car": "bf_insurance_car",
    "Interest On Statutory Dues": "bf_interest_on_statutory_dues",
    "Professional & Legal Charges": "bf_professional_legal_charges",
    "Subscription Membership": "bf_subscription_membership",
    "Rent Furniture fittings": "bf_rent_furniture_fittings",
    "Rent Office": "bf_rent_office",
    "Corp Staff": "bf_corp_staff",
    "Bonus Corp Staff": "bf_bonus_corp_staff",
    "EDLI Contribution Corp Staff": "bf_EDLI_contribution_corp_staff",
    "Employer Contribution to ESI Corp Staff": "bf_employer_contribution_to_ESI_corp_staff",
    "Employer Contribution to PF Corp Staff": "bf_employer_contribution_to_PF_corp_staff",
    "EPF Admin Charges Corp Staff": "bf_EPF_admin_charges_corp_staff",
    "Ex-Gratia Corp Staff": "bf_exgratia_corp_staff",
    "Gratuity Corp Staff": "bf_gratuity_corp_staff",
    "Incentive Corp Staff": "bf_incentive_corp_staff",
    "Insurance Corp Staff": "bf_insurance_corp_staff",
    "LWF Corp Staff": "bf_lwf_corp_staff",
    "Salaries Wages Corp Staff": "bf_salaries_wages_corp_staff",

    "Dept Staff": "bf_dept_staff",
    "Bonus Staff": "bf_bonus_staff",
    "EDLI Contribution Staff": "bf_EDLI_contribution_staff",
    "Employer Contribution to ESI Staff": "bf_employer_contribution_to_ESI_staff",
    "Employer Contribution to PF Staff": "bf_employer_contribution_to_PF_staff",
    "EPF Admin Charges Staff": "bf_EPF_admin_charges_staff",
    "Ex-Gratia Dept Staff": "bf_exgratia_dept_staff",
    "Gratuity Staff": "bf_gratuity_staff",
    "Incentive Dept Staff": "bf_incentive_dept_staff",
    "Insurance Staff": "bf_insurance_staff",
    "LWF Dept Staff": "bf_lwf_dept_staff",
    "Salaries Wages Staff": "bf_salaries_wages_staff",
    # "Interest on Borrowings": "bf_interest_on_borrowings",
    # "Interest on Other Loans ": "bf_interest_on_other_loans",
    "Operational Expenses Fixed": "bf_fixed",

    "Insurance Expenses - Warehouse": "bf_insurance_warehouse",
    "Insurance - WCC": "bf_insurance_wcc",
    "Manpower Supply Expenses": "bf_manpower_supply_expenses",
    # "Rates & Taxes Expenses": "bf_rates_taxes",
    "Rent - Premises Expenses": "bf_rent_premises",
    "Security Service Charges Expenses": "bf_security_service_charges",
    "Operational Expenses Variable": "bf_variable",
    "Crane Handling Expenses": "bf_crane_handling_expenses",
    "Diesel Expenses - Forklift": "bf_diesel_expenses_forklift",
    "Forklift Handling Expenses": "bf_forklift_handling_expenses",
    "Fumigation Expenses": "bf_fumigation_expenses",
    "Packing Services": "bf_packing_services",
    "Support Handling": "bf_support_handling",
    "Non-Operational Expenses Fixed": "bf_oe_Fixed",
    "Depreciation Expenses": "bf_depreciation",
    "Internet Data Card Expenses": "bf_internet_data_card_expenses",
    "Housekeeping Salary": "bf_housekeeping_salary",
    "Rent - Plant & Machinery Expenses": "bf_rent_plant_machinery",
    "AMC Expenses": "bf_amc",
    "Software AMC Expenses": "bf_software_AMC_charges",
    "Non-Operational Expenses Variable": "bf_oe_variable",
    "CGST Ineligible ITC": "bf_CGST_ineligible_ITC",
    "Conveyance Expenses": "bf_conveyance_expenses",
    "Diesel Expenses - Genset": "bf_diesel_expenses_gense",
    "Handling Expenses": "bf_handling_expenses",
    "Hotel Boarding Lodging Expenses": "bf_hotel_boarding_lodging_expenses",
    "IGST Ineligible ITC": "bf_IGST_ineligible_ITC",
    "Office Repairs and Maintenance Expenses": "bf_office_repairs_maintenance",
    "Office Supplies & General Expenses": "bf_office_supplies_general_expenses",
    "Postage & Courier Expenses": "bf_postage_courier",
    "Power and Fuel Expenses": "bf_power_fuel",
    "Printing & Stationery Expenses": "bf_printing_stationery",
    "Service and Maintanance Expenses": "bf_service_maintenance_expenses",
    "SGST Ineligible ITC": "bf_SGST_ineligible_ITC",
    "Staff Welfare Expenses": "bf_staff_welfare_staff",
    "Telephone and Mobile Expenses": "bf_telephone_mobile_expenses",
    "Training Expenses": "bf_training_expenses",
    "Travelling Expenses": "bf_travelling_expenses",

}
OTHER_EXPENSES_CATEGORIES = {k: v for k, v in BUDGET_FIELD_MAPPING.items() if v not in (
        set(INCOME_CATEGORIES.values()) |
        set(DEPARTMENT_EXPENSES_CATEGORIES.values()) |
        set(EMPLOYEE_BENEFITS_CATEGORIES.values()) |
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
        units = UnitInfo.objects.filter(ui_branch_name__loc_name=selected_branch).values_list('unit_name',
                                                                                              flat=True).distinct()

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
        expenses_filter['exp_ext_expense_number__exp_service_start_date__gte'] = from_date
        budget_filter['bf_start_date_year__gte'] = from_date

    if to_date:
        to_date = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))
        expenses_filter['exp_ext_expense_number__exp_service_start_date__lte'] = to_date
        budget_filter['bf_start_date_year__lte'] = to_date

    # Get total expenses per category
    expense_summary = ExpenseExtinfo.objects.filter(**expenses_filter).values(
        'exp_ext_expense_number__exp_expense_type__exp_type_name'
    ).annotate(total_expense=Sum('exp_ext_amount'))

    expense_dict = {
        item['exp_ext_expense_number__exp_expense_type__exp_type_name']: item['total_expense']
        for item in expense_summary
    }

    budget_totals = BudgetInfo.objects.filter(**budget_filter).aggregate(**{
        field: Sum(field) for field in BUDGET_FIELD_MAPPING.values() if field is not None
    })

    budget_dict = {
        category: budget_totals.get(field, 0.0) if field else 0.0
        for category, field in BUDGET_FIELD_MAPPING.items()
    }

    # Function to generate summaries
    def get_category_summary(category_mapping):
        summary = []
        for category, field in category_mapping.items():
            total_budget = budget_dict.get(category, 0.0) or 0.0
            total_expense = expense_dict.get(category, 0.0) or 0.0
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
    operational_summary = get_category_summary(OPERATIONAL_EXPENSES_CATEGORIES)
    non_operational_summary = get_category_summary(NON_OPERATIONAL_EXPENSES_CATEGORIES)
    other_expenses_summary = get_category_summary(OTHER_EXPENSES_CATEGORIES)

    total_budget = sum(value if value is not None else 0.0 for value in budget_dict.values())
    total_expense = sum(value if value is not None else 0.0 for value in expense_dict.values())
    total_profit_loss = total_budget - total_expense
    total_pl_percentage = (total_profit_loss / total_budget * 100) if total_budget > 0 else 0.0

    return render(request, "asset_mgt_app/fin_budget_expense_report.html", {
        "income_summary": income_summary,
        "department_expenses_summary": department_expenses_summary,
        "employee_benefits_summary": employee_benefits_summary,
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


def budget_expense_mis(request):
    first_name = request.session.get("first_name")
    selected_branch = request.GET.get("branch")
    selected_unit = request.GET.get("unit")
    selected_company = request.GET.get("company")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    selected_year = request.GET.get("year")
    if selected_year:
        try:
            selected_year = int(selected_year)
        except ValueError:
            selected_year = None
    else:
        selected_year = None

    years = list(
        ExpenseExtinfo.objects.dates('exp_ext_expense_number__exp_service_start_date', 'year').values_list(
            'exp_ext_expense_number__exp_service_start_date__year', flat=True)
        .distinct()
    )

    branches = Location_info.objects.all()
    units = UnitInfo.objects.values_list("unit_name", flat=True).distinct()
    companies = Business_Sol_info.objects.values_list("bvm_business", flat=True).distinct()
    years = list(
        ExpenseExtinfo.objects.dates('exp_ext_expense_number__exp_service_start_date', 'year').values_list(
            'exp_ext_expense_number__exp_service_start_date__year', flat=True)
        .distinct()
    )

    if selected_branch:
        units = UnitInfo.objects.filter(ui_branch_name__loc_name=selected_branch).values_list("unit_name",
                                                                                              flat=True).distinct()

    expenses_filter = {}
    budget_filter = {}

    if selected_year:
        expenses_filter["exp_ext_expense_number__exp_service_start_date__year"] = selected_year
        budget_filter["bf_start_date_year__year"] = selected_year
    if selected_company:
        expenses_filter["exp_ext_expense_number__exp_business__bvm_business"] = selected_company
        budget_filter["bf_company__bvm_business"] = selected_company

    if selected_branch:
        expenses_filter["exp_ext_branch__loc_name"] = selected_branch
        budget_filter["bf_location__loc_name"] = selected_branch

    if selected_unit:
        expenses_filter["exp_ext_unit__unit_name"] = selected_unit
        budget_filter["bf_unit_reference__unit_name"] = selected_unit

    if from_date:
        from_date = timezone.make_aware(datetime.strptime(from_date, "%Y-%m-%d"))
        expenses_filter["exp_ext_expense_number__exp_service_start_date__gte"] = from_date
        budget_filter["bf_start_date_year__gte"] = from_date

    if to_date:
        to_date = timezone.make_aware(datetime.strptime(to_date, "%Y-%m-%d"))
        expenses_filter["exp_ext_expense_number__exp_service_start_date__lte"] = to_date
        budget_filter["bf_start_date_year__lte"] = to_date

    expense_summary = (
        ExpenseExtinfo.objects.filter(**expenses_filter)
        .exclude(exp_ext_expense_number__exp_service_start_date__isnull=True)
        .values("exp_ext_expense_number__exp_expense_type__exp_type_name",
                "exp_ext_expense_number__exp_service_start_date__month")
        .annotate(total_expense=Sum("exp_ext_amount"))
        .order_by("exp_ext_expense_number__exp_service_start_date__month")
    )

    expense_dict = {category: {i: 0 for i in range(1, 13)} for category in set(INCOME_CATEGORIES.keys())}
    for item in expense_summary:
        category = item["exp_ext_expense_number__exp_expense_type__exp_type_name"]
        month = item["exp_ext_expense_number__exp_service_start_date__month"]
        expense_dict.setdefault(category, {i: 0 for i in range(1, 13)})  # Initialize if missing
        expense_dict[category][month] += item["total_expense"]  # Ensure cumulative sum if duplicate entries exist

    budget_summary = (
        BudgetInfo.objects.filter(**budget_filter)
        .values("bf_start_date_year__month")
        .annotate(**{field: Sum(field) for field in BUDGET_FIELD_MAPPING.values() if field is not None})
    )

    # Convert the budget data into a dictionary with month-wise budgets
    budget_dict_by_month = {}
    for item in budget_summary:
        month = item["bf_start_date_year__month"]
        for category, field in BUDGET_FIELD_MAPPING.items():
            if field:
                if category not in budget_dict_by_month:
                    budget_dict_by_month[category] = {i: 0 for i in range(1, 13)}  # Initialize for all months (1-12)
                budget_dict_by_month[category][month] = item.get(field, 0.0)  # Store the budget for the specific month

    budget_totals = BudgetInfo.objects.filter(**budget_filter).aggregate(
        **{field: Sum(field) for field in BUDGET_FIELD_MAPPING.values() if field is not None}
    )

    budget_dict = {
        category: budget_totals.get(field, 0.0) if field else 0.0
        for category, field in BUDGET_FIELD_MAPPING.items()
    }

    def get_category_summary(category_mapping):
        summary = []
        for category, field in category_mapping.items():
            monthly_expenses = expense_dict.get(category, {i: 0 for i in range(1, 13)})
            monthly_budgets = budget_dict_by_month.get(category, {i: 0 for i in range(1, 13)})
            monthly_variance = {month: monthly_budgets[month] - monthly_expenses[month] for month in range(1, 13)}

            total_expense = sum(monthly_expenses.values())
            total_budget = sum(monthly_budgets.values())
            total_variance = total_budget - total_expense

            pl_percentage = (total_variance / total_budget * 100) if total_budget > 0 else 0.0

            summary.append({
                "expense_type": category,
                "monthly_expenses": monthly_expenses,
                "monthly_budgets": monthly_budgets,
                "monthly_variance": monthly_variance,
                "total_expense": total_expense,
                "total_budget": total_budget,
                "total_variance": total_variance,
                "pl_percentage": pl_percentage,
            })
        return summary

    # Generate category-wise summaries
    income_summary = get_category_summary(INCOME_CATEGORIES)
    department_expenses_summary = get_category_summary(DEPARTMENT_EXPENSES_CATEGORIES)
    employee_benefits_summary = get_category_summary(EMPLOYEE_BENEFITS_CATEGORIES)
    operational_summary = get_category_summary(OPERATIONAL_EXPENSES_CATEGORIES)
    non_operational_summary = get_category_summary(NON_OPERATIONAL_EXPENSES_CATEGORIES)
    other_expenses_summary = get_category_summary(OTHER_EXPENSES_CATEGORIES)

    # Get total budget and expense for all categories
    total_budget = sum(value if value is not None else 0.0 for value in budget_dict.values())
    total_expense = sum(
        sum(monthly_values.values()) for monthly_values in expense_dict.values()
    )

    total_profit_loss = total_budget - total_expense
    total_pl_percentage = (total_profit_loss / total_budget * 100) if total_budget > 0 else 0.0

    category_totals = {
        "income_budget": 0,
        "income_expense": 0,
        "department_budget": 0,
        "department_expense": 0,
        "employee_budget": 0,
        "employee_expense": 0,
        "interest_budget": 0,
        "interest_expense": 0,
        "operational_budget": 0,
        "operational_fixed_budget": 0,
        "operational_variable_budget": 0,
        "operational_expense": 0,
        "operational_fixed_expense": 0,
        "operational_variable_expense": 0,
        "non_operational_budget": 0,
        "non_operational_expense": 0,
    }

    category_summaries = {
        "income_budget": {i: 0 for i in range(1, 13)},
        "income_expense": {i: 0 for i in range(1, 13)},
        "department_budget": {i: 0 for i in range(1, 13)},
        "department_expense": {i: 0 for i in range(1, 13)},
        "employee_budget": {i: 0 for i in range(1, 13)},
        "employee_expense": {i: 0 for i in range(1, 13)},
        "interest_budget": {i: 0 for i in range(1, 13)},
        "interest_expense": {i: 0 for i in range(1, 13)},
        "operational_budget": {i: 0 for i in range(1, 13)},
        "operational_fixed_budget": {i: 0 for i in range(1, 13)},
        "operational_variable_budget": {i: 0 for i in range(1, 13)},
        "operational_expense": {i: 0 for i in range(1, 13)},
        "operational_fixed_expense": {i: 0 for i in range(1, 13)},
        "operational_variable_expense": {i: 0 for i in range(1, 13)},
        "non_operational_budget": {i: 0 for i in range(1, 13)},
        "non_operational_expense": {i: 0 for i in range(1, 13)},

    }

    for item in budget_summary:
        month = item["bf_start_date_year__month"]
        income_total = sum(item[field] for field in INCOME_CATEGORIES.values() if field in item)
        department_total = sum(item[field] for field in DEPARTMENT_EXPENSES_CATEGORIES.values() if field in item)
        employee_total = sum(item[field] for field in EMPLOYEE_BENEFITS_CATEGORIES.values() if field in item)
        operational_total = sum(item[field] for field in OPERATIONAL_EXPENSES_CATEGORIES.values() if field in item)
        operational_fixed_total = sum(item[field] for field in OPERATIONAL_EXPENSES_FIXED.values() if field in item)
        operational_variable_total = sum(
            item[field] for field in OPERATIONAL_EXPENSES_VARIABLE.values() if field in item)

        non_operational_total = sum(
            item[field] for field in NON_OPERATIONAL_EXPENSES_CATEGORIES.values() if field in item)

        category_summaries["income_budget"][month] = income_total
        category_summaries["department_budget"][month] = department_total
        category_summaries["employee_budget"][month] = employee_total
        category_summaries["operational_budget"][month] = operational_total
        category_summaries["operational_fixed_budget"][month] = operational_fixed_total
        category_summaries["operational_variable_budget"][month] = operational_variable_total

        category_summaries["non_operational_budget"][month] = non_operational_total

        category_totals["income_budget"] += income_total
        category_totals["department_budget"] += department_total
        category_totals["employee_budget"] += employee_total
        category_totals["operational_budget"] += operational_total
        category_totals["operational_fixed_budget"] += operational_fixed_total
        category_totals["operational_variable_budget"] += operational_variable_total
        category_totals["non_operational_budget"] += non_operational_total

    for item in expense_summary:
        month = item["exp_ext_expense_number__exp_service_start_date__month"]
        category = item["exp_ext_expense_number__exp_expense_type__exp_type_name"]
        amount = item["total_expense"]

        if category in INCOME_CATEGORIES:
            category_summaries["income_expense"][month] += amount
            category_totals["income_expense"] += amount
        elif category in OPERATIONAL_EXPENSES_CATEGORIES:
            category_summaries["operational_expense"][month] += amount
            category_totals["operational_expense"] += amount
        elif category in OPERATIONAL_EXPENSES_FIXED:
            category_summaries["operational_fixed_expense"][month] += amount
            category_totals["operational_fixed_expense"] += amount
        elif category in OPERATIONAL_EXPENSES_VARIABLE:
            category_summaries["operational_variable_expense"][month] += amount
            category_totals["operational_variable_expense"] += amount
        elif category in DEPARTMENT_EXPENSES_CATEGORIES:
            category_summaries["department_expense"][month] += amount
            category_totals["department_expense"] += amount
        elif category in EMPLOYEE_BENEFITS_CATEGORIES:
            category_summaries["employee_expense"][month] += amount
            category_totals["employee_expense"] += amount
        elif category in NON_OPERATIONAL_EXPENSES_CATEGORIES:
            category_summaries["non_operational_expense"][month] += amount
            category_totals["non_operational_expense"] += amount

    category_summaries["income_variance"] = {i: 0 for i in range(1, 13)}
    category_summaries["department_variance"] = {i: 0 for i in range(1, 13)}
    category_summaries["employee_variance"] = {i: 0 for i in range(1, 13)}
    category_summaries["interest_variance"] = {i: 0 for i in range(1, 13)}
    category_summaries["operational_variance"] = {i: 0 for i in range(1, 13)}
    category_summaries["operational_fixed_variance"] = {i: 0 for i in range(1, 13)}
    category_summaries["operational_variable_variance"] = {i: 0 for i in range(1, 13)}
    category_summaries["non_operational_variance"] = {i: 0 for i in range(1, 13)}

    for month in range(1, 13):
        category_summaries["income_variance"][month] = (
                category_summaries["income_budget"].get(month, 0) - category_summaries["income_expense"].get(month, 0)
        )

        category_summaries["employee_variance"][month] = (
                category_summaries["employee_budget"].get(month, 0) - category_summaries["employee_expense"].get(month,
                                                                                                                 0)
        )

        category_summaries["department_variance"][month] = (
                category_summaries["department_budget"].get(month, 0) - category_summaries["department_expense"].get(
            month, 0)
        )

        category_summaries["interest_variance"][month] = (
                category_summaries["interest_budget"].get(month, 0) - category_summaries["interest_expense"].get(month,
                                                                                                                 0)
        )
        category_summaries["operational_variance"][month] = (
                category_summaries["operational_budget"].get(month, 0) - category_summaries["operational_expense"].get(
            month, 0)
        )

        category_summaries["operational_fixed_variance"] = {
            i: category_summaries["operational_fixed_budget"][i] - category_summaries["operational_fixed_expense"][i]
            for i in range(1, 13)
        }
        category_summaries["operational_variable_variance"] = {
            i: category_summaries["operational_variable_budget"][i] -
               category_summaries["operational_variable_expense"][i]
            for i in range(1, 13)
        }

        category_totals["operational_fixed_variance"] = (
                category_totals["operational_fixed_budget"] - category_totals["operational_fixed_expense"]
        )

        category_totals["operational_variable_variance"] = (
                category_totals["operational_variable_budget"] - category_totals["operational_variable_expense"]
        )

        category_summaries["non_operational_variance"][month] = (
                category_summaries["non_operational_budget"].get(month, 0) - category_summaries[
            "non_operational_expense"].get(month, 0)
        )
        category_totals["income_variance"] = (
                category_totals["income_budget"] - category_totals["income_expense"]
        )

        category_totals["department_variance"] = (
                category_totals["department_budget"] - category_totals["department_expense"]
        )

        category_totals["employee_variance"] = (
                category_totals["employee_budget"] - category_totals["employee_expense"]
        )

        category_totals["interest_variance"] = (
                category_totals["interest_budget"] - category_totals["interest_expense"]
        )

        category_totals["operational_variance"] = (
                category_totals["operational_budget"] - category_totals["operational_expense"]
        )

        category_totals["non_operational_variance"] = (
                category_totals["non_operational_budget"] - category_totals["non_operational_expense"]
        )

    grand_totals = {
        "monthly_budget": {i: 0 for i in range(1, 13)},
        "monthly_expense": {i: 0 for i in range(1, 13)},
        "monthly_profit_loss": {i: 0 for i in range(1, 13)},
        "monthly_profit_loss_percentage": {i: 0 for i in range(1, 13)}
    }

    # Calculate Grand Totals for Each Month
    for month in range(1, 13):
        grand_totals["monthly_budget"][month] = sum(
            category_summaries[key][month] for key in category_summaries if "budget" in key)
        grand_totals["monthly_expense"][month] = sum(
            category_summaries[key][month] for key in category_summaries if "expense" in key)

        grand_totals["monthly_profit_loss"][month] = (
                grand_totals["monthly_budget"][month] - grand_totals["monthly_expense"][month]
        )

        if grand_totals["monthly_budget"][month] > 0:
            grand_totals["monthly_profit_loss_percentage"][month] = (
                    (grand_totals["monthly_profit_loss"][month] / grand_totals["monthly_budget"][month]) * 100)
        else:
            grand_totals["monthly_profit_loss_percentage"][month] = 0

    total_budget = sum(grand_totals["monthly_budget"].values())
    total_expense = sum(grand_totals["monthly_expense"].values())
    total_profit_loss = sum(grand_totals["monthly_profit_loss"].values())

    total_pl_percentage = (total_profit_loss / total_budget * 100) if total_budget > 0 else 0

    return render(request, "asset_mgt_app/fin_budget_expense_MIS.html", {
        "income_summary": income_summary,
        "category_totals": category_totals,
        "category_summaries": category_summaries,
        "department_expenses_summary": department_expenses_summary,
        "employee_benefits_summary": employee_benefits_summary,
        "operational_summary": operational_summary,
        "non_operational_summary": non_operational_summary,
        "other_expenses_summary": other_expenses_summary,
        "grand_totals": grand_totals,
        "total_budget": total_budget,
        "total_expense": total_expense,
        "total_profit_loss": total_profit_loss,
        "total_pl_percentage": total_pl_percentage,
        "months": [month_name[i] for i in range(1, 13)],
        "branches": branches,
        "units": units,
        "companies": companies,
        "years": years,
        "selected_year": selected_year,
        "selected_company": selected_company,
        "selected_branch": selected_branch,
        "selected_unit": selected_unit,
        "first_name": first_name,
        "from_date": request.GET.get("from_date", ""),
        "to_date": request.GET.get("to_date", ""),
        "operational_fixed_summary": category_summaries["operational_fixed_budget"],
        "operational_fixed_expense_summary": category_summaries["operational_fixed_expense"],
        "operational_variable_summary": category_summaries["operational_variable_budget"],
        "operational_variable_expense_summary": category_summaries["operational_variable_expense"],

    })


def fin_mis(request):
    first_name = request.session.get("first_name")
    selected_branch = request.GET.get("branch")
    selected_unit = request.GET.get("unit")
    selected_company = request.GET.get("company")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    selected_year = request.GET.get("year")
    if selected_year:
        try:
            selected_year = int(selected_year)
        except ValueError:
            selected_year = None
    else:
        selected_year = None

    years = list(
        ExpenseExtinfo.objects.dates('exp_ext_expense_number__exp_service_start_date', 'year').values_list(
            'exp_ext_expense_number__exp_service_start_date__year', flat=True)
        .distinct()
    )

    branches = Location_info.objects.all()
    units = UnitInfo.objects.values_list("unit_name", flat=True).distinct()
    companies = Business_Sol_info.objects.values_list("bvm_business", flat=True).distinct()
    years = list(
        ExpenseExtinfo.objects.dates('exp_ext_expense_number__exp_service_start_date', 'year').values_list(
            'exp_ext_expense_number__exp_service_start_date__year', flat=True)
        .distinct()
    )

    if selected_branch:
        units = UnitInfo.objects.filter(ui_branch_name__loc_name=selected_branch).values_list("unit_name",
                                                                                              flat=True).distinct()

    expenses_filter = {}
    budget_filter = {}

    if selected_year:
        expenses_filter["exp_ext_expense_number__exp_service_start_date__year"] = selected_year
        budget_filter["bf_start_date_year__year"] = selected_year
    if selected_company:
        expenses_filter["exp_ext_expense_number__exp_business__bvm_business"] = selected_company
        budget_filter["bf_company__bvm_business"] = selected_company

    if selected_branch:
        expenses_filter["exp_ext_branch__loc_name"] = selected_branch
        budget_filter["bf_location__loc_name"] = selected_branch

    if selected_unit:
        expenses_filter["exp_ext_unit__unit_name"] = selected_unit
        budget_filter["bf_unit_reference__unit_name"] = selected_unit

    if from_date:
        from_date = timezone.make_aware(datetime.strptime(from_date, "%Y-%m-%d"))
        expenses_filter["exp_ext_expense_number__exp_service_start_date__gte"] = from_date
        budget_filter["bf_start_date_year__gte"] = from_date

    if to_date:
        to_date = timezone.make_aware(datetime.strptime(to_date, "%Y-%m-%d"))
        expenses_filter["exp_ext_expense_number__exp_service_start_date__lte"] = to_date
        budget_filter["bf_start_date_year__lte"] = to_date

    expense_summary = (
        ExpenseExtinfo.objects.filter(**expenses_filter)
        .exclude(exp_ext_expense_number__exp_service_start_date__isnull=True)
        .values("exp_ext_expense_number__exp_expense_type__exp_type_name",
                "exp_ext_expense_number__exp_service_start_date__month")
        .annotate(total_expense=Sum("exp_ext_amount"))
        .order_by("exp_ext_expense_number__exp_service_start_date__month")
    )

    expense_dict = {category: {i: 0 for i in range(1, 13)} for category in set(INCOME_CATEGORIES.keys())}
    for item in expense_summary:
        category = item["exp_ext_expense_number__exp_expense_type__exp_type_name"]
        month = item["exp_ext_expense_number__exp_service_start_date__month"]
        expense_dict.setdefault(category, {i: 0 for i in range(1, 13)})
        expense_dict[category][month] += item["total_expense"]

    budget_summary = (
        BudgetInfo.objects.filter(**budget_filter)
        .values("bf_start_date_year__month")
        .annotate(**{field: Sum(field) for field in BUDGET_FIELD_MAPPING.values() if field is not None})
    )

    budget_dict_by_month = {}
    for item in budget_summary:
        month = item["bf_start_date_year__month"]
        for category, field in BUDGET_FIELD_MAPPING.items():
            if field:
                if category not in budget_dict_by_month:
                    budget_dict_by_month[category] = {i: 0 for i in range(1, 13)}
                budget_dict_by_month[category][month] = item.get(field, 0.0)

    budget_totals = BudgetInfo.objects.filter(**budget_filter).aggregate(
        **{field: Sum(field) for field in BUDGET_FIELD_MAPPING.values() if field is not None}
    )

    budget_dict = {
        category: budget_totals.get(field, 0.0) if field else 0.0
        for category, field in BUDGET_FIELD_MAPPING.items()
    }

    def get_category_summary(category_mapping, category_name):
        summary = []
        grand_monthly_expenses = {i: 0 for i in range(1, 13)}
        grand_monthly_budgets = {i: 0 for i in range(1, 13)}
        grand_total_expense = 0
        grand_total_budget = 0

        for category, field in category_mapping.items():
            monthly_expenses = expense_dict.get(category, {i: 0 for i in range(1, 13)})
            monthly_budgets = budget_dict_by_month.get(category, {i: 0 for i in range(1, 13)})
            monthly_variance = {month: monthly_budgets[month] - monthly_expenses[month] for month in range(1, 13)}

            total_expense = sum(monthly_expenses.values())
            total_budget = sum(monthly_budgets.values())
            total_variance = total_budget - total_expense
            pl_percentage = (total_variance / total_budget * 100) if total_budget > 0 else 0.0

            # Accumulate grand totals
            for month in range(1, 13):
                grand_monthly_expenses[month] += monthly_expenses[month]
                grand_monthly_budgets[month] += monthly_budgets[month]

            grand_total_expense += total_expense
            grand_total_budget += total_budget

            summary.append({
                "expense_type": category,
                "monthly_expenses": monthly_expenses,
                "monthly_budgets": monthly_budgets,
                "monthly_variance": monthly_variance,
                "total_expense": total_expense,
                "total_budget": total_budget,
                "total_variance": total_variance,
                "pl_percentage": pl_percentage,
            })

        grand_monthly_variance = {
            month: grand_monthly_budgets[month] - grand_monthly_expenses[month] for month in range(1, 13)
        }
        grand_total_variance = grand_total_budget - grand_total_expense
        grand_pl_percentage = (grand_total_variance / grand_total_budget * 100) if grand_total_budget > 0 else 0.0

        summary.append({
            "expense_type": f"Total {category_name}",
            "monthly_expenses": grand_monthly_expenses,
            "monthly_budgets": grand_monthly_budgets,
            "monthly_variance": grand_monthly_variance,
            "total_expense": grand_total_expense,
            "total_budget": grand_total_budget,
            "total_variance": grand_total_variance,
            "pl_percentage": grand_pl_percentage,
            "is_total": True,
        })

        return summary

    # Generate category-wise summaries
    income_summary = get_category_summary(INCOME_CATEGORIES, "Income ")
    department_expenses_summary = get_category_summary(DEPARTMENT_EXPENSES_CATEGORIES, "Department Expenses")
    employee_benefits_summary = get_category_summary(EMPLOYEE_BENEFITS_CATEGORIES, "Employee Benefits")
    operational_summary = get_category_summary(OPERATIONAL_EXPENSES_CATEGORIES, "Operational Expenses ")
    non_operational_summary = get_category_summary(NON_OPERATIONAL_EXPENSES_CATEGORIES, "Non-Operational Expenses")
    other_expenses_summary = get_category_summary(OTHER_EXPENSES_CATEGORIES, "Other Expenses")

    income_total_expense = income_summary[-1]["total_expense"]
    income_total_budget = income_summary[-1]["total_budget"]
    income_monthly_expenses = income_summary[-1]["monthly_expenses"]
    income_monthly_budgets = income_summary[-1]["monthly_budgets"]
    expense_summaries = [
        department_expenses_summary,
        employee_benefits_summary,
        operational_summary,
        non_operational_summary,
        other_expenses_summary,
    ]

    total_expense = sum([summary[-1]["total_expense"] for summary in expense_summaries])
    total_budget = sum([summary[-1]["total_budget"] for summary in expense_summaries])
    monthly_expense = {i: 0 for i in range(1, 13)}
    monthly_budget = {i: 0 for i in range(1, 13)}
    for summary in expense_summaries:
        for month in range(1, 13):
            monthly_expense[month] += summary[-1]["monthly_expenses"][month]
            monthly_budget[month] += summary[-1]["monthly_budgets"][month]
    net_actual_total = income_total_expense - total_expense
    net_budget_total = income_total_budget - total_budget
    net_variance_total = net_budget_total - net_actual_total
    net_pl_percentage = (net_variance_total / net_budget_total * 100) if net_budget_total else 0.0

    net_monthly_expense = {month: income_monthly_expenses[month] - monthly_expense[month] for month in range(1, 13)}
    net_monthly_budget = {month: income_monthly_budgets[month] - monthly_budget[month] for month in range(1, 13)}
    net_monthly_variance = {month: net_monthly_budget[month] - net_monthly_expense[month] for month in range(1, 13)}
    net_income_summary = {
        "expense_type": "Profit/Loss",
        "monthly_expenses": net_monthly_expense,
        "monthly_budgets": net_monthly_budget,
        "monthly_variance": net_monthly_variance,
        "total_expense": net_actual_total,
        "total_budget": net_budget_total,
        "total_variance": net_variance_total,
        "pl_percentage": net_pl_percentage,
        "is_total": True,
    }


    # Total % calculations
    net_income_percentage = (net_actual_total / income_total_expense * 100) if income_total_expense else 0.0
    net_budget_percentage = (net_budget_total / income_total_budget * 100) if income_total_budget else 0.0
    net_variance_percentage = (net_variance_total / income_total_expense * 100) if income_total_expense else 0.0

    # Monthly % calculations
    net_income_monthly_percentage = {
        month: (net_monthly_expense[month] / income_monthly_expenses[month] * 100)
        if income_monthly_expenses[month] else 0.0
        for month in range(1, 13)
    }

    net_budget_monthly_percentage = {
        month: (net_monthly_budget[month] / income_monthly_budgets[month] * 100)
        if income_monthly_budgets[month] else 0.0
        for month in range(1, 13)
    }

    net_variance_monthly_percentage = {
        month: (net_monthly_variance[month] / income_monthly_budgets[month] * 100)
        if income_monthly_budgets[month] else 0.0
        for month in range(1, 13)
    }
    net_income_summary["net_income_percentage"] = net_income_percentage
    net_income_summary["net_budget_percentage"] = net_budget_percentage
    net_income_summary["net_variance_percentage"] = net_variance_percentage

    net_income_summary["net_income_monthly_percentage"] = net_income_monthly_percentage
    net_income_summary["net_budget_monthly_percentage"] = net_budget_monthly_percentage
    net_income_summary["net_variance_monthly_percentage"] = net_variance_monthly_percentage
    net_income_summary_percentage = {
        "expense_type": "Profit/Loss %",
        "monthly_expenses": net_income_monthly_percentage,
        "monthly_budgets": net_budget_monthly_percentage,
        "monthly_variance": net_variance_monthly_percentage,
        "total_expense": net_income_percentage,
        "total_budget": net_budget_percentage,
        "total_variance": net_variance_percentage,
        "is_total": True,
    }
    grand_monthly_budgets = {i: 0 for i in range(1, 13)}
    grand_monthly_expenses = {i: 0 for i in range(1, 13)}
    grand_monthly_variance = {i: 0 for i in range(1, 13)}

    for category_dict in [
        income_summary,
        department_expenses_summary,
        employee_benefits_summary,
        operational_summary,
        non_operational_summary,
        other_expenses_summary,
    ]:
        for entry in category_dict:
            if not entry.get("is_total"):  # Only accumulate actual categories, skip their own "Total" rows
                continue
            for month in range(1, 13):
                grand_monthly_budgets[month] += entry["monthly_budgets"].get(month, 0)
                grand_monthly_expenses[month] += entry["monthly_expenses"].get(month, 0)
                grand_monthly_variance[month] += entry["monthly_variance"].get(month, 0)

    total_budget = sum(grand_monthly_budgets.values())
    total_expense = sum(grand_monthly_expenses.values())
    total_variance = sum(grand_monthly_variance.values())
    grand_totals_summary = {
        "expense_type": "Grand Totals",
        "monthly_budgets": grand_monthly_budgets,
        "monthly_expenses": grand_monthly_expenses,
        "monthly_variance": grand_monthly_variance,
        "total_budget": total_budget,
        "total_expense": total_expense,
        "total_variance": total_variance,
        "is_total": True,
    }

    overall_monthly_expenses = {i: 0 for i in range(1, 13)}
    overall_monthly_budgets = {i: 0 for i in range(1, 13)}

    for category_expenses in expense_dict.values():
        for month, amount in category_expenses.items():
            overall_monthly_expenses[month] += amount

    for category_budgets in budget_dict_by_month.values():
        for month, amount in category_budgets.items():
            overall_monthly_budgets[month] += amount

    overall_monthly_variances = {
        month: overall_monthly_budgets[month] - overall_monthly_expenses[month]
        for month in range(1, 13)
    }
    overall_monthly_pl_percentage = {
        month: (overall_monthly_variances[month] / overall_monthly_budgets[month] * 100)
        if overall_monthly_budgets[month] > 0 else 0.0
        for month in range(1, 13)
    }

    total_budget = sum(value if value is not None else 0.0 for value in budget_dict.values())
    total_expense = sum(
        sum(monthly_values.values()) for monthly_values in expense_dict.values()
    )

    total_profit_loss = total_budget - total_expense
    total_pl_percentage = (total_profit_loss / total_budget * 100) if total_budget > 0 else 0.0

    return render(request, "asset_mgt_app/fin_MIS.html", {
        "income_summary": income_summary,
        "department_expenses_summary": department_expenses_summary,
        "employee_benefits_summary": employee_benefits_summary,
        "operational_summary": operational_summary,
        "non_operational_summary": non_operational_summary,
        "other_expenses_summary": other_expenses_summary,

        "total_budget": total_budget,
        "total_expense": total_expense,
        "total_profit_loss": total_profit_loss,
        "total_pl_percentage": total_pl_percentage,
        "months": [month_name[i] for i in range(1, 13)],
        "branches": branches,
        "units": units,
        "companies": companies,
        "years": years,
        "selected_year": selected_year,
        "selected_company": selected_company,
        "selected_branch": selected_branch,
        "selected_unit": selected_unit,
        "first_name": first_name,
        "from_date": request.GET.get("from_date", ""),
        "to_date": request.GET.get("to_date", ""),
        "overall_monthly_expenses": overall_monthly_expenses,
        "overall_monthly_budgets": overall_monthly_budgets,
        "overall_monthly_variances": overall_monthly_variances,
        "overall_monthly_pl_percentage": overall_monthly_pl_percentage,
        "net_income_summary": net_income_summary,
        "net_income_summary_percentage": net_income_summary_percentage,
        "grand_totals_summary": grand_totals_summary,

    })


def fin_mis_warehouse(request):
    first_name = request.session.get("first_name")
    selected_branch = request.GET.get("branch")
    selected_unit = request.GET.get("unit")
    selected_company = request.GET.get("company")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    selected_year = request.GET.get("year")
    if selected_year:
        try:
            selected_year = int(selected_year)
        except ValueError:
            selected_year = None
    else:
        selected_year = None

    years = list(
        ExpenseExtinfo.objects.dates('exp_ext_expense_number__exp_service_start_date', 'year').values_list(
            'exp_ext_expense_number__exp_service_start_date__year', flat=True)
        .distinct()
    )

    branches = Location_info.objects.all()
    units = UnitInfo.objects.values_list("unit_name", flat=True).distinct()
    companies = Business_Sol_info.objects.values_list("bvm_business", flat=True).distinct()
    years = list(
        ExpenseExtinfo.objects.dates('exp_ext_expense_number__exp_service_start_date', 'year').values_list(
            'exp_ext_expense_number__exp_service_start_date__year', flat=True)
        .distinct()
    )

    if selected_branch:
        units = UnitInfo.objects.filter(ui_branch_name__loc_name=selected_branch).values_list("unit_name",
                                                                                              flat=True).distinct()

    expenses_filter = {}
    budget_filter = {}
    warehouse_filter = {}

    if selected_year:
        expenses_filter["exp_ext_expense_number__exp_service_start_date__year"] = selected_year
        budget_filter["bf_start_date_year__year"] = selected_year
        warehouse_filter["wh_checkin_time__year"] = selected_year
    if selected_company:
        expenses_filter["exp_ext_expense_number__exp_business__bvm_business"] = selected_company
        budget_filter["bf_company__bvm_business"] = selected_company

    if selected_branch:
        expenses_filter["exp_ext_branch__loc_name"] = selected_branch
        budget_filter["bf_location__loc_name"] = selected_branch
        warehouse_filter["wh_branch__loc_name"] = selected_branch
    if selected_unit:
        expenses_filter["exp_ext_unit__unit_name"] = selected_unit
        budget_filter["bf_unit_reference__unit_name"] = selected_unit
        warehouse_filter["wh_unit__unit_name"] = selected_unit
    if from_date:
        from_date = timezone.make_aware(datetime.strptime(from_date, "%Y-%m-%d"))
        expenses_filter["exp_ext_expense_number__exp_service_start_date__gte"] = from_date
        budget_filter["bf_start_date_year__gte"] = from_date
        warehouse_filter["wh_checkin_time__gte"] = from_date

    if to_date:
        to_date = timezone.make_aware(datetime.strptime(to_date, "%Y-%m-%d"))
        expenses_filter["exp_ext_expense_number__exp_service_start_date__lte"] = to_date
        budget_filter["bf_start_date_year__lte"] = to_date
        warehouse_filter["wh_checkin_time__lte"] = to_date
    if from_date and to_date:
        months_range = list(range(from_date.month, to_date.month + 1))
    else:
        months_range = list(range(1, 13))
    warehouse_queryset = (
        Warehouse_goods_info.objects
        .filter(**warehouse_filter)
        .annotate(month=ExtractMonth("wh_checkin_time"))
        .values("month")
        .annotate(**{
            f"{field}_sum": Sum(field) for field in WAREHOUSE_EXPENSE_FIELD_MAPPING.values() if field
        })

    )

    warehouse_income_expense_dict = {
        category: {i: 0 for i in months_range}
        for category in INCOME_CATEGORIES.keys()
    }

    for row in warehouse_queryset:
        month = row.get("month")
        if not month:
            continue

        for category, field in WAREHOUSE_EXPENSE_FIELD_MAPPING.items():
            if not field:
                continue  # Nothing to sum
            value = row.get(f"{field}_sum", 0.0) or 0.0
            warehouse_income_expense_dict[category][month] += value

    expense_summary = (
        ExpenseExtinfo.objects.filter(**expenses_filter)
        .exclude(exp_ext_expense_number__exp_service_start_date__isnull=True)
        .values("exp_ext_expense_number__exp_expense_type__exp_type_name",
                "exp_ext_expense_number__exp_service_start_date__month")
        .annotate(total_expense=Sum("exp_ext_amount"))
        .order_by("exp_ext_expense_number__exp_service_start_date__month")
    )

    expense_dict = {category: {i: 0 for i in months_range} for category in set(INCOME_CATEGORIES.keys())}
    for item in expense_summary:
        category = item["exp_ext_expense_number__exp_expense_type__exp_type_name"]
        month = item["exp_ext_expense_number__exp_service_start_date__month"]
        expense_dict.setdefault(category, {i: 0 for i in months_range})
        expense_dict[category][month] += item["total_expense"]

    budget_summary = (
        BudgetInfo.objects.filter(**budget_filter)
        .values("bf_start_date_year__month")
        .annotate(**{field: Sum(field) for field in BUDGET_FIELD_MAPPING.values() if field is not None})
    )

    budget_dict_by_month = {}
    for item in budget_summary:
        month = item["bf_start_date_year__month"]
        for category, field in BUDGET_FIELD_MAPPING.items():
            if field:
                if category not in budget_dict_by_month:
                    budget_dict_by_month[category] = {i: 0 for i in months_range}
                budget_dict_by_month[category][month] = item.get(field, 0.0)

    budget_totals = BudgetInfo.objects.filter(**budget_filter).aggregate(
        **{field: Sum(field) for field in BUDGET_FIELD_MAPPING.values() if field is not None}
    )

    budget_dict = {
        category: budget_totals.get(field, 0.0) if field else 0.0
        for category, field in BUDGET_FIELD_MAPPING.items()
    }

    def get_category_summary(category_mapping, category_name, custom_expense_dict=None):
        summary = []
        expense_source = custom_expense_dict or expense_dict

        grand_monthly_expenses = {i: 0 for i in months_range}
        grand_monthly_budgets = {i: 0 for i in months_range}
        grand_total_expense = 0
        grand_total_budget = 0

        #For expenses: budget - expense, for income: expense - budget
        variance_sign = -1 if category_name == "Income" else 1

        for category, field in category_mapping.items():
            monthly_expenses = expense_source.get(category, {i: 0 for i in months_range})
            monthly_budgets = budget_dict_by_month.get(category, {i: 0 for i in months_range})

            monthly_variance = {
                month: variance_sign * (monthly_budgets[month] - monthly_expenses[month])
                for month in months_range
            }

            total_expense = round(sum(monthly_expenses.values()), 0)
            total_budget = round(sum(monthly_budgets.values()), 0)
            total_variance = variance_sign * round(total_budget - total_expense, 0)

            pl_percentage = round((total_variance / total_budget * 100), 2) if total_budget > 0 else 0.0

            for month in months_range:
                grand_monthly_expenses[month] += monthly_expenses[month]

                if category_name in ["Employee Benefits", "Operational Expenses", "Non-Operational Expenses"]:
                    grand_monthly_budgets[month] += monthly_budgets[month] / 2
                else:
                    grand_monthly_budgets[month] += monthly_budgets[month]

            grand_total_expense += total_expense
            if category_name in ["Employee Benefits", "Operational Expenses", "Non-Operational Expenses"]:
                grand_total_budget += total_budget / 2
            else:
                grand_total_budget += total_budget

            summary.append({
                "expense_type": category,
                "monthly_expenses": monthly_expenses,
                "monthly_budgets": monthly_budgets,
                "monthly_variance": monthly_variance,
                "total_expense": total_expense,
                "total_budget": total_budget,
                "total_variance": total_variance,
                "pl_percentage": pl_percentage,
            })

        grand_monthly_variance = {
            month: variance_sign * (grand_monthly_budgets[month] - grand_monthly_expenses[month])
            for month in months_range
        }
        grand_total_variance = variance_sign * (grand_total_budget - grand_total_expense)
        grand_pl_percentage = (grand_total_variance / grand_total_budget * 100) if grand_total_budget > 0 else 0.0

        summary.append({
            "expense_type": f"Total {category_name}",
            "monthly_expenses": grand_monthly_expenses,
            "monthly_budgets": grand_monthly_budgets,
            "monthly_variance": grand_monthly_variance,
            "total_expense": grand_total_expense,
            "total_budget": grand_total_budget,
            "total_variance": grand_total_variance,
            "pl_percentage": grand_pl_percentage,
            "is_total": True,
        })

        return summary

    # Generate category-wise summaries
    department_expenses_summary = get_category_summary(DEPARTMENT_EXPENSES_CATEGORIES, "Department Expenses")
    employee_benefits_summary = get_category_summary(EMPLOYEE_BENEFITS_CATEGORIES, "Employee Benefits")
    operational_summary = get_category_summary(OPERATIONAL_EXPENSES_CATEGORIES, "Operational Expenses")
    non_operational_summary = get_category_summary(NON_OPERATIONAL_EXPENSES_CATEGORIES, "Non-Operational Expenses")
    other_expenses_summary = get_category_summary(OTHER_EXPENSES_CATEGORIES, "Other Expenses")
    income_summary = get_category_summary(
        INCOME_CATEGORIES,
        "Income",
        custom_expense_dict=warehouse_income_expense_dict
    )

    income_total_expense = income_summary[-1]["total_expense"]
    income_total_budget = income_summary[-1]["total_budget"]
    income_monthly_expenses = income_summary[-1]["monthly_expenses"]
    income_monthly_budgets = income_summary[-1]["monthly_budgets"]
    expense_summaries = [
        department_expenses_summary,
        employee_benefits_summary,
        operational_summary,
        non_operational_summary,
        other_expenses_summary,
    ]

    total_expense = sum([summary[-1]["total_expense"] for summary in expense_summaries])
    total_budget = sum([summary[-1]["total_budget"] for summary in expense_summaries])
    monthly_expense = {i: 0 for i in months_range}
    monthly_budget = {i: 0 for i in months_range}
    for summary in expense_summaries:
        for month in months_range:
            monthly_expense[month] += summary[-1]["monthly_expenses"][month]
            monthly_budget[month] += summary[-1]["monthly_budgets"][month]
    net_actual_total = income_total_expense - total_expense
    net_budget_total = income_total_budget - total_budget
    net_variance_total = net_budget_total - net_actual_total
    net_pl_percentage = (net_variance_total / net_budget_total * 100) if net_budget_total else 0.0

    net_monthly_expense = {month: income_monthly_expenses[month] - monthly_expense[month] for month in months_range}
    net_monthly_budget = {month: income_monthly_budgets[month] - monthly_budget[month] for month in months_range}
    net_monthly_variance = {month: net_monthly_expense[month] - net_monthly_budget[month] for month in months_range}
    net_income_summary = {
        "expense_type": "Profit/Loss",
        "monthly_expenses": net_monthly_expense,
        "monthly_budgets": net_monthly_budget,
        "monthly_variance": net_monthly_variance,
        "total_expense": net_actual_total,
        "total_budget": net_budget_total,
        "total_variance": net_variance_total,
        "pl_percentage": net_pl_percentage,
        "is_total": True,
    }

    def safe_percentage(numerator, denominator):
        return round((numerator / denominator * 100), 2) if denominator else 0.0

    net_income_percentage = safe_percentage(net_actual_total, income_total_expense)
    net_budget_percentage = safe_percentage(net_budget_total, income_total_budget)
    net_variance_percentage = safe_percentage(net_variance_total, income_total_expense)

    # # Total % calculations
    # net_income_percentage = (net_actual_total / income_total_expense * 100) if income_total_expense else 0.0
    # net_budget_percentage = (net_budget_total / income_total_budget * 100) if income_total_budget else 0.0
    # net_variance_percentage = (net_variance_total / income_total_expense * 100) if income_total_budget else 0.0

    # Monthly % calculations
    net_income_monthly_percentage = {
        month: (net_monthly_expense[month] / income_monthly_expenses[month] * 100)
        if income_monthly_expenses[month] else 0.0
        for month in months_range
    }

    net_budget_monthly_percentage = {
        month: (net_monthly_budget[month] / income_monthly_budgets[month] * 100)
        if income_monthly_budgets[month] else 0.0
        for month in months_range
    }

    net_variance_monthly_percentage = {
        month: (net_monthly_variance[month] / income_monthly_budgets[month] * 100)
        if income_monthly_budgets[month] else 0.0
        for month in months_range
    }
    net_income_summary["net_income_percentage"] = net_income_percentage
    net_income_summary["net_budget_percentage"] = net_budget_percentage
    net_income_summary["net_variance_percentage"] = net_variance_percentage

    net_income_summary["net_income_monthly_percentage"] = net_income_monthly_percentage
    net_income_summary["net_budget_monthly_percentage"] = net_budget_monthly_percentage
    net_income_summary["net_variance_monthly_percentage"] = net_variance_monthly_percentage
    net_income_summary_percentage = {
        "expense_type": "Profit/Loss %",
        "monthly_expenses": net_income_monthly_percentage,
        "monthly_budgets": net_budget_monthly_percentage,
        "monthly_variance": net_variance_monthly_percentage,
        "total_expense": net_income_percentage,
        "total_budget": net_budget_percentage,
        "total_variance": net_variance_percentage,
        "is_total": True,
    }
    grand_monthly_budgets = {i: 0 for i in months_range}
    grand_monthly_expenses = {i: 0 for i in months_range}
    grand_monthly_variance = {i: 0 for i in months_range}

    for category_dict in [

        department_expenses_summary,
        employee_benefits_summary,
        operational_summary,
        non_operational_summary,
        other_expenses_summary,
    ]:
        for entry in category_dict:
            if not entry.get("is_total"):  # Only accumulate actual categories, skip their own "Total" rows
                continue
            for month in months_range:
                grand_monthly_budgets[month] += entry["monthly_budgets"].get(month, 0)
                grand_monthly_expenses[month] += entry["monthly_expenses"].get(month, 0)
                grand_monthly_variance[month] += entry["monthly_variance"].get(month, 0)

    total_budget = sum(grand_monthly_budgets.values())
    total_expense = sum(grand_monthly_expenses.values())
    total_variance = sum(grand_monthly_variance.values())
    grand_totals_summary = {
        "expense_type": "Total Expenses",
        "monthly_budgets": grand_monthly_budgets,
        "monthly_expenses": grand_monthly_expenses,
        "monthly_variance": grand_monthly_variance,
        "total_budget": total_budget,
        "total_expense": total_expense,
        "total_variance": total_variance,
        "is_total": True,
    }

    overall_monthly_expenses = {i: 0 for i in months_range}
    overall_monthly_budgets = {i: 0 for i in months_range}

    for category_expenses in expense_dict.values():
        for month, amount in category_expenses.items():
            overall_monthly_expenses[month] += amount

    for category_budgets in budget_dict_by_month.values():
        for month, amount in category_budgets.items():
            overall_monthly_budgets[month] += amount

    overall_monthly_variances = {
        month: overall_monthly_budgets[month] - overall_monthly_expenses[month]
        for month in months_range
    }
    overall_monthly_pl_percentage = {
        month: (overall_monthly_variances[month] / overall_monthly_budgets[month] * 100)
        if overall_monthly_budgets[month] > 0 else 0.0
        for month in months_range
    }

    total_budget = sum(value if value is not None else 0.0 for value in budget_dict.values())
    total_expense = sum(
        sum(monthly_values.values()) for monthly_values in expense_dict.values()
    )

    total_profit_loss = total_budget - total_expense
    total_pl_percentage = (total_profit_loss / total_budget * 100) if total_budget > 0 else 0.0

    return render(request, "asset_mgt_app/fin_mis_warehouse.html", {
        "income_summary": income_summary,
        "department_expenses_summary": department_expenses_summary,
        "employee_benefits_summary": employee_benefits_summary,
        "operational_summary": operational_summary,
        "non_operational_summary": non_operational_summary,
        "other_expenses_summary": other_expenses_summary,

        "total_budget": total_budget,
        "total_expense": total_expense,
        "total_profit_loss": total_profit_loss,
        "total_pl_percentage": total_pl_percentage,
        "months": [month_name[i] for i in months_range],
        "branches": branches,
        "units": units,
        "companies": companies,
        "years": years,
        "selected_year": selected_year,
        "selected_company": selected_company,
        "selected_branch": selected_branch,
        "selected_unit": selected_unit,
        "first_name": first_name,
        "from_date": request.GET.get("from_date", ""),
        "to_date": request.GET.get("to_date", ""),
        "overall_monthly_expenses": overall_monthly_expenses,
        "overall_monthly_budgets": overall_monthly_budgets,
        "overall_monthly_variances": overall_monthly_variances,
        "overall_monthly_pl_percentage": overall_monthly_pl_percentage,
        "net_income_summary": net_income_summary,
        "net_income_summary_percentage": net_income_summary_percentage,
        "grand_totals_summary": grand_totals_summary,

    })
