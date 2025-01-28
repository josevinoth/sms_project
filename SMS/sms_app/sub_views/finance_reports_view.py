from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count, Q,Sum,Case, When, Value, CharField, Min,FloatField, F
from django.db.models import F, Subquery, OuterRef
from django.db.models.functions import Coalesce,Round
from django.utils.dateparse import parse_date
from django.utils import timezone
from datetime import datetime
from ..models import Warehouse_goods_info,ExpenseExtinfo,Location_info,UnitInfo,Business_Sol_info,TrbusinesstypeInfo,CustomerInfo



def finance_reports(request):
    first_name = request.session.get('first_name')
    context = {
               'first_name': first_name
               }
    return render(request,"asset_mgt_app/finance_reports.html",context)


def branch_profit_loss(request):
    first_name = request.session.get('first_name')
    selected_branch = request.GET.get('branch', '')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date:
        from_date = timezone.make_aware(datetime.strptime(from_date, '%Y-%m-%d'))
    if to_date:
        to_date = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))

    invoice_filters = Q()
    expense_filters = Q()

    if from_date:
        invoice_filters &= Q(warehouse_goods_info__wh_checkin_time__gte=from_date)
        expense_filters &= Q(expenseextinfo__exp_ext_updated_on__gte=from_date)
    if to_date:
        invoice_filters &= Q(warehouse_goods_info__wh_checkin_time__lte=to_date)
        expense_filters &= Q(expenseextinfo__exp_ext_updated_on__lte=to_date)

    queryset = Location_info.objects.select_related(
        'warehouse_goods_info',
        'expenseextinfo'
    ).annotate(
        total_invoice_amount=Sum('warehouse_goods_info__wh_total_invoice_cost',distinct=True, filter=invoice_filters, output_field=FloatField()),
        total_expense_amount=Sum('expenseextinfo__exp_ext_amount',distinct=True, filter=expense_filters, output_field=FloatField()),
        profit_loss=F('total_invoice_amount') - F('total_expense_amount')
    )

    if selected_branch:
        queryset = queryset.filter(loc_name=selected_branch)

    data = queryset.values(
        'loc_name', 'total_invoice_amount', 'total_expense_amount', 'profit_loss'
    ).order_by('loc_name')
    branches = Location_info.objects.all()

    context = {
        'data': data,
        'first_name': first_name,
        'branches': branches,
        'selected_branch': selected_branch,
        'from_date': from_date.strftime('%Y-%m-%d') if from_date else '',
        'to_date': to_date.strftime('%Y-%m-%d') if to_date else '',
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

    if from_date:
        from_date = timezone.make_aware(datetime.strptime(from_date, '%Y-%m-%d'))

    if to_date:
        to_date = timezone.make_aware(datetime.strptime(to_date, '%Y-%m-%d'))

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
        expenses_filter['exp_ext_updated_on__gte'] = from_date
        invoices_filter['wh_checkin_time__gte'] = from_date

    if to_date:
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
            }

    # Remove entries with zero expenses and invoice cost (if necessary)
    summary_data = [
        row for row in combined_data.values()
        if row['total_expense'] != 0.0 or row['total_invoice_cost'] != 0.0
    ]

    # Pass the data to the template
    context = {
        'summary_data': summary_data,
        'branches': branches,
        'first_name': first_name,
        'units': units,
        'selected_branch': selected_branch,
        'selected_unit': selected_unit,
        'from_date': from_date,
        'to_date': to_date,
    }

    return render(request, "asset_mgt_app/fin_unit_PL_report.html", context)


def businessmodel_PL(request):
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
        exp_ext_branch=OuterRef('wh_branch')  # Match branch from Warehouse_goods_info
    ).values('exp_ext_branch').annotate(
        total_expenses=Sum('exp_ext_amount')  # Sum of total expenses
    ).values('total_expenses')[:1]

    business_summary = Warehouse_goods_info.objects.values(
        'wh_customer_type__tb_trbusinesstype','wh_branch__loc_name'
    ).annotate(
        total_invoice_amount=Sum('wh_total_invoice_cost',filter=invoice_filters),
        total_expenses=Coalesce(Subquery(total_expenses_subquery,filter=expense_filters), 0.0)  # Total expenses per branch

    ).order_by('wh_customer_type__tb_trbusinesstype')
    if selected_branch:
        business_summary = business_summary.filter(wh_branch__loc_name=selected_branch)

    if selected_businessmodel:
        business_summary = business_summary.filter(wh_customer_type__tb_trbusinesstype=selected_businessmodel)

    context = {
        'business_summary': business_summary,
        'first_name': first_name,
        'branches': branches,
        'businessmodels':businessmodels,
        'selected_branch': selected_branch,
        'selected_businessmodel':selected_businessmodel,
        'from_date': from_date,
        'to_date': to_date,
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
        exp_ext_branch=OuterRef('wh_branch')  # Match branch from Warehouse_goods_info
    ).values('exp_ext_branch').annotate(
        total_expenses=Sum('exp_ext_amount')  # Sum of total expenses
    ).values('total_expenses')[:1]

    business_summary = Warehouse_goods_info.objects.values(
        'wh_customer_type__tb_trbusinesstype','wh_branch__loc_name','wh_customer_name__cu_nameshort'
    ).annotate(
        total_invoice_amount=Sum('wh_total_invoice_cost',filter=invoice_filters),
        total_expenses=Coalesce(Subquery(total_expenses_subquery,filter=expense_filters), 0.0)  # Total expenses per branch

    ).order_by('wh_customer_type__tb_trbusinesstype')
    if selected_branch:
        business_summary = business_summary.filter(wh_branch__loc_name=selected_branch)

    if selected_businessmodel:
        business_summary = business_summary.filter(wh_customer_type__tb_trbusinesstype=selected_businessmodel)

    context = {
        'business_summary': business_summary,
        'first_name': first_name,
        'branches': branches,
        'businessmodels':businessmodels,
        'selected_branch': selected_branch,
        'selected_businessmodel':selected_businessmodel,
        'from_date': from_date,
        'to_date': to_date,
    }

    return render(request, "asset_mgt_app/fin_customerwise_PL_report.html", context)