from django.shortcuts import render
from django.contrib.auth.models import User
from django.db.models import Count, Q,Sum,Case, When, Value, CharField, Min,FloatField, F
from django.db.models import F, Subquery, OuterRef
from django.db.models.functions import Coalesce,Round
from django.utils.dateparse import parse_date
from django.utils import timezone
from datetime import datetime
from ..models import Sales_Comments_Info, MyUser,SalesInfo,Sales_target_info,BusinessrevenueInfo,Calltype,Callpurpose,Callnature,User_extInfo,CustomerInfo,YesNoInfo,Business_Sol_info,Location_info
from ..models import Warehouse_goods_info,ExpenseExtinfo,Location_info,UnitInfo


def salesperson_chart(request):
    first_name = request.session.get('first_name')
    selected_salesperson = request.GET.get('salesperson', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    salespersons = MyUser.objects.select_related('user_extinfo').filter(
        user_extinfo__department__dept_name="Sales",is_active=True
    ).distinct().values_list('first_name', flat=True)

    sales_data_query = Sales_Comments_Info.objects.filter(
        sc_updated_by__user_extinfo__department__dept_name="Sales",sc_updated_by__is_active=True
    )

    if selected_salesperson:
        sales_data_query = sales_data_query.filter(sc_updated_by__first_name=selected_salesperson)

    if from_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__gte=from_date)

    if to_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__lte=to_date)

    sales_data = sales_data_query.values('sc_updated_by__first_name').annotate(sales_count=Count('id'))

    labels = [item['sc_updated_by__first_name'] for item in sales_data]
    data = [item['sales_count'] for item in sales_data]

    table_data = zip(labels, data)

    context = {
        'first_name': first_name,
        'labels': labels,
        'data': data,
        'table_data': table_data,
        'salespersons': salespersons,
        'selected_salesperson': selected_salesperson,
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, "asset_mgt_app/salesperson_chart.html", context)


def monthly_summary(request):
    first_name = request.session.get('first_name')
    selected_salesperson = request.GET.get('salesperson', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    salespersons = MyUser.objects.select_related('user_extinfo').filter(
        user_extinfo__department__dept_name="Sales", is_active=True
    ).distinct().values_list('first_name', flat=True)

    target_existing_customers_subquery = Sales_target_info.objects.filter(
        st_sales_person__first_name=OuterRef('sc_updated_by__first_name')
    ).values('st_target_calls_existing_customer')[:1]

    target_new_customers_subquery = Sales_target_info.objects.filter(
        st_sales_person__first_name=OuterRef('sc_updated_by__first_name')
    ).values('st_target_calls_new_customer')[:1]

    target_revenue_subquery = Sales_target_info.objects.filter(
        st_sales_person__first_name=OuterRef('sc_updated_by__first_name')
    ).values('st_target_revenue')[:1]

    actual_revenue_subquery = BusinessrevenueInfo.objects.filter(
        br_sale_person__first_name=OuterRef('sc_updated_by__first_name')
     ).values('br_revenue_1')[:1]

    sales_data_query = Sales_Comments_Info.objects.filter(
        sc_updated_by__user_extinfo__department__dept_name="Sales",sc_updated_by__is_active=True
    )

    if selected_salesperson:
        sales_data_query = sales_data_query.filter(sc_updated_by__first_name=selected_salesperson)

    if from_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__gte=from_date)

    if to_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__lte=to_date)

    sales_data_query = sales_data_query.values('sc_updated_by__first_name').annotate(
        total_sales=Count('id'),
        new_customer_calls=Count('id', filter=Q(sc_sales_number__s_customer_name_id=210)),
        existing_customer_calls=Count('id', filter=~Q(sc_sales_number__s_customer_name_id=210)),
        unique_customers=Count('sc_sales_number__s_customer_name', distinct=True),  # Unique customers
        total_quotes=Count('sc_sales_number__s_quote_ref', distinct=True),  # Total quotes
        won_business_count=Count(
            'sc_sales_number__s_bus_won_not',
            filter=Q(sc_sales_number__s_bus_won_not=1)
        ),
        target_existing_customer_calls=Subquery(target_existing_customers_subquery),
        target_new_customer_calls=Subquery(target_new_customers_subquery),
        target_revenue=Subquery(target_revenue_subquery),
        actual_revenue=Subquery(actual_revenue_subquery),
    )

    # Prepare data for the template
    sales_data = [
        {
            "salesperson": item['sc_updated_by__first_name'],
            "total_sales": item['total_sales'],
            "new_customer_calls": item['new_customer_calls'],
            "existing_customer_calls": item['existing_customer_calls'],
            "target_existing_customer_calls": item['target_existing_customer_calls'] or 0,  # Default to 0 if None
            "target_new_customer_calls": item['target_new_customer_calls'] or 0,
            "target_revenue": item['target_revenue'] or 0,
            "actual_revenue": item['actual_revenue'] or 0,
            "performance_percentage": round(
                (item['unique_customers'] / item['total_sales']) * 100, 2
            ) if item['total_sales'] > 0 else 0.0,  # Performance % calculation
            "productivity_percentage": round(
                (item['won_business_count'] / item['total_quotes']) * 100, 2
            ) if item['total_quotes'] > 0 else 0.0,  # Productivity % calculation
        }
        for item in sales_data_query
    ]

    # Chart data
    labels = [item['salesperson'] for item in sales_data]
    new_customer_calls = [item['new_customer_calls'] for item in sales_data]
    existing_customer_calls = [item['existing_customer_calls'] for item in sales_data]
    target_new_customer_calls = [item['target_new_customer_calls'] for item in sales_data]
    target_existing_customer_calls = [item['target_existing_customer_calls'] for item in sales_data]
    target_revenue = [item['target_revenue'] for item in sales_data]
    actual_revenue = [item['actual_revenue'] for item in sales_data]

    # Context for the template
    context = {
        'first_name': first_name,
        'labels': labels,
        'new_customer_calls': new_customer_calls,
        'existing_customer_calls': existing_customer_calls,
        'target_new_customer_calls': target_new_customer_calls,
        'target_existing_customer_calls': target_existing_customer_calls,
        'target_revenue': target_revenue,
        'actual_revenue': actual_revenue,
        "sales_data": sales_data,
        'salespersons': salespersons,
        'selected_salesperson': selected_salesperson,
        'from_date': from_date,
        'to_date': to_date,
    }

    return render(request, "asset_mgt_app/monthlysummary.html", context)


def salesperson_productivity_performance(request):
    first_name = request.session.get('first_name')
    selected_salesperson = request.GET.get('salesperson', None)
    selected_company = request.GET.get('company', None)
    selected_branch = request.GET.get('branch', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    salespersons = MyUser.objects.select_related('user_extinfo').filter(
        user_extinfo__department__dept_name="Sales", is_active=True
    ).distinct().values_list('first_name', flat=True)

    company_name = Business_Sol_info.objects.filter(
        id__in=SalesInfo.objects.values_list('s_company', flat=True)
    ).distinct().values_list('bvm_business', flat=True)

    branch_name = Location_info.objects.filter(
        id__in=SalesInfo.objects.values_list('s_location', flat=True)
    ).distinct().values_list('loc_name', flat=True)

    target_existing_customers_subquery = Sales_target_info.objects.filter(
        st_sales_person__first_name=OuterRef('sc_updated_by__first_name')  # Adjust field name if needed
    ).values('st_target_calls_existing_customer')[:1]

    target_new_customers_subquery = Sales_target_info.objects.filter(
        st_sales_person__first_name=OuterRef('sc_updated_by__first_name')  # Adjust field name if needed
    ).values('st_target_calls_new_customer')[:1]

    target_revenue_subquery = Sales_target_info.objects.filter(
        st_sales_person__first_name=OuterRef('sc_updated_by__first_name')  # Adjust field name if needed
    ).values('st_target_revenue')[:1]

    actual_revenue_subquery = BusinessrevenueInfo.objects.filter(
        br_sale_person__first_name=OuterRef('sc_updated_by__first_name')  # Adjust field name if needed
    ).values('br_revenue_1')[:1]

    sales_data_query = Sales_Comments_Info.objects.filter(
        sc_updated_by__user_extinfo__department__dept_name="Sales",sc_updated_by__is_active=True
    )

    if selected_salesperson:
        sales_data_query = sales_data_query.filter(sc_updated_by__first_name=selected_salesperson)

    if from_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__gte=from_date)

    if to_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__lte=to_date)

    if selected_company:
        sales_data_query = sales_data_query.filter(sc_sales_number__s_company__bvm_business=selected_company)

    if selected_branch:
        sales_data_query = sales_data_query.filter(sc_sales_number__s_location__loc_name=selected_branch)

    sales_data_query = sales_data_query.values('sc_updated_by__first_name').annotate(
        total_sales=Count('id'),
        new_customer_calls=Count('id', filter=Q(sc_sales_number__s_customer_name_id=210)),
        existing_customer_calls=Count('id', filter=~Q(sc_sales_number__s_customer_name_id=210)),
        unique_customers=Count('sc_sales_number__s_customer_name', distinct=True),
        total_quotes=Count('sc_sales_number__s_quote_ref', distinct=True),
        won_business_count=Count(
            'sc_sales_number__s_bus_won_not',
            filter=Q(sc_sales_number__s_bus_won_not=1)
        ),
        target_existing_customer_calls=Subquery(target_existing_customers_subquery),
        target_new_customer_calls=Subquery(target_new_customers_subquery),
        target_revenue=Subquery(target_revenue_subquery),
        actual_revenue=Subquery(actual_revenue_subquery),
    )

    sales_data = []
    performance_percentages = []
    productivity_percentages = []

    for item in sales_data_query:
        total_sales = item['total_sales']
        total_quotes = item['total_quotes']
        won_business_count = item['won_business_count']  # Ensure this is captured
        performance_percentage = round(
            (item['unique_customers'] / total_sales) * 100, 2
        ) if total_sales > 0 else 0.0

        productivity_percentage = round(
            (item['won_business_count'] / total_quotes) * 100, 2
        ) if total_quotes > 0 else 0.0

        performance_percentages.append(performance_percentage)
        productivity_percentages.append(productivity_percentage)

        sales_data.append({
            "salesperson": item['sc_updated_by__first_name'],
            "total_sales": total_sales,
            "new_customer_calls": item['new_customer_calls'],
            "existing_customer_calls": item['existing_customer_calls'],
            "won_business_count": won_business_count,
            "total_quotes": total_quotes,  # Ensure total quotes is included
            "target_existing_customer_calls": item['target_existing_customer_calls'] or 0,
            "target_new_customer_calls": item['target_new_customer_calls'] or 0,
            "target_revenue": item['target_revenue'] or 0,
            "actual_revenue": item['actual_revenue'] or 0,
            "performance_percentage": performance_percentage,
            "productivity_percentage": productivity_percentage,
        })

    # Chart data
    labels = [item['salesperson'] for item in sales_data]
    new_customer_calls = [item['new_customer_calls'] for item in sales_data]
    existing_customer_calls = [item['existing_customer_calls'] for item in sales_data]
    target_new_customer_calls = [item['target_new_customer_calls'] for item in sales_data]
    target_existing_customer_calls = [item['target_existing_customer_calls'] for item in sales_data]
    target_revenue = [item['target_revenue'] for item in sales_data]
    actual_revenue = [item['actual_revenue'] for item in sales_data]

    context = {
        'first_name': first_name,
        'labels': labels,
        'new_customer_calls': new_customer_calls,
        'existing_customer_calls': existing_customer_calls,
        'target_new_customer_calls': target_new_customer_calls,
        'target_existing_customer_calls': target_existing_customer_calls,
        'target_revenue': target_revenue,
        'actual_revenue': actual_revenue,
        "performance_percentages": performance_percentages,
        "productivity_percentages": productivity_percentages,
        "sales_data": sales_data,
        'salespersons': salespersons,
        'selected_salesperson': selected_salesperson,
        'company_name': company_name,
        'branch_name': branch_name,
        'selected_company': selected_company,
        'selected_branch': selected_branch,
        'from_date': from_date,
        'to_date': to_date,
    }

    return render(request, "asset_mgt_app/donut_chart.html", context)


def salescalls_details(request):
    first_name = request.session.get('first_name')
    selected_salesperson = request.GET.get('salesperson', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    # Fetch salespersons
    salespersons = MyUser.objects.select_related('user_extinfo').filter(
        user_extinfo__department__dept_name="Sales", is_active=True
    ).distinct().values_list('first_name', flat=True)

    call_types = Calltype.objects.values_list('call_type', flat=True)
    call_purposes = Callpurpose.objects.values_list('call_purpose', flat=True)
    call_natures = Callnature.objects.values_list('call_nature', flat=True)

    sales_data_query = Sales_Comments_Info.objects.filter(
        sc_updated_by__user_extinfo__department__dept_name="Sales",sc_updated_by__is_active=True
    )

    if selected_salesperson:
        sales_data_query = sales_data_query.filter(sc_updated_by__first_name=selected_salesperson)

    if from_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__gte=from_date)

    if to_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__lte=to_date)

    def sanitize_key(key):
        return key.replace(" ", "_").replace("-", "_").replace("/", "_")

    # Aggregate data by salesperson and call type
    call_type_aggregation = {
        sanitize_key(call_type): Count(Case(When(sc_call_type__call_type=call_type, then=1)))
        for call_type in call_types
    }
    call_purpose_aggregation = {
        sanitize_key(call_purpose): Count(Case(When(sc_call_purpose__call_purpose=call_purpose, then=1)))
        for call_purpose in call_purposes
    }
    call_nature_aggregation = {
        sanitize_key(call_nature): Count(Case(When(sc_call_nature__call_nature=call_nature, then=1)))
        for call_nature in call_natures
    }

    # Fetch data for each table
    sales_data_types = sales_data_query.values('sc_updated_by__first_name').annotate(**call_type_aggregation)
    sales_data_purposes = sales_data_query.values('sc_updated_by__first_name').annotate(**call_purpose_aggregation)
    sales_data_natures = sales_data_query.values('sc_updated_by__first_name').annotate(**call_nature_aggregation)

    # Prepare the data for the chart
    call_type_labels = list(call_types)
    call_type_counts = [
        sum(salesperson.get(sanitize_key(call_type), 0) for salesperson in sales_data_types)
        for call_type in call_types
    ]
    call_purpose_labels = list(call_purposes)  # Should return a list of purposes
    call_purpose_counts = [
        sum(salesperson.get(sanitize_key(call_purpose), 0) for salesperson in sales_data_purposes)
        for call_purpose in call_purposes
    ]

    call_nature_labels = list(call_natures)
    call_nature_counts = [
        sum(salesperson.get(sanitize_key(call_nature), 0) for salesperson in sales_data_natures)
        for call_nature in call_natures
    ]

    def prepare_table_data(sales_data, fields):
        table_data = []
        for salesperson in sales_data:
            row = [salesperson['sc_updated_by__first_name']]
            for field in fields:
                sanitized_field = sanitize_key(field)
                row.append(salesperson.get(sanitized_field, 0))
            table_data.append(row)
        return table_data

    table_data_types = prepare_table_data(sales_data_types, call_types)
    table_data_purposes = prepare_table_data(sales_data_purposes, call_purposes)
    table_data_natures = prepare_table_data(sales_data_natures, call_natures)

    context = {
        'first_name': first_name,
        'salespersons': salespersons,
        'selected_salesperson': selected_salesperson,
        'from_date': from_date,
        'to_date': to_date,
        'call_types': call_types,
        'call_purposes': call_purposes,
        'call_natures': call_natures,
        'table_data_types': table_data_types,
        'table_data_purposes': table_data_purposes,
        'table_data_natures': table_data_natures,
        'call_type_labels': call_type_labels,  # Labels for the chart
        'call_type_counts': call_type_counts,  # Data for the chart
        'call_purpose_labels': call_purpose_labels,  # Labels for the chart
        'call_purpose_counts': call_purpose_counts,
        'call_nature_labels': call_nature_labels,  # Labels for the chart
        'call_nature_counts': call_nature_counts,

    }
    return render(request, "asset_mgt_app/salescalls_detail_report.html", context)


def targets_actuals(request):
    first_name = request.session.get('first_name')
    selected_salesperson = request.GET.get('salesperson', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    salespersons = MyUser.objects.select_related('user_extinfo').filter(
        user_extinfo__department__dept_name="Sales", is_active=True
    ).distinct().values_list('first_name', flat=True)

    target_filter = Q()
    if selected_salesperson:
        target_filter &= Q(st_sales_person__first_name=selected_salesperson)
    if from_date:
        target_filter &= Q(st_updated_at__gte=from_date)
    if to_date:
        target_filter &= Q(st_updated_at__lte=to_date)

    actual_filter = Q()
    if selected_salesperson:
        actual_filter &= Q(s_updated_by__first_name=selected_salesperson)
    if from_date:
        actual_filter &= Q(s_updated_at__gte=from_date)
    if to_date:
        actual_filter &= Q(s_updated_at__lte=to_date)

    calls_filter = Q()
    if selected_salesperson:
        calls_filter &= Q(sc_updated_by__first_name=selected_salesperson)
    if from_date:
        calls_filter &= Q(sc_updated_at__date__gte=from_date)
    if to_date:
        calls_filter &= Q(sc_updated_at__date__lte=to_date)

    revenue_filter = Q()
    if selected_salesperson:
        revenue_filter &= Q(br_sale_person__first_name=selected_salesperson)
    if from_date:
        revenue_filter &= Q(br_updated_on__gte=from_date)
    if to_date:
        revenue_filter &= Q(br_updated_on__lte=to_date)

    # Apply filters to each dataset
    target_data = Sales_target_info.objects.filter(target_filter, st_sales_person__is_active=True).values(
        'st_sales_person__id', 'st_sales_person__first_name'
    ).annotate(
        total_target_customers=Sum('st_target_customer'),
        target_new_customer_calls=Sum('st_target_calls_new_customer'),
        target_existing_customer_calls=Sum('st_target_calls_existing_customer'),
        target_revenue=Sum('st_target_revenue')
    )

    actual_data = SalesInfo.objects.filter(actual_filter, s_updated_by__user_extinfo__department__dept_name="Sales",s_updated_by__is_active=True).values(
        's_updated_by__id', 's_updated_by__first_name'
    ).annotate(
        total_actual_customers=Count('s_customer_name', distinct=False),
        total_new_customers=Count('s_customer_new_name', distinct=False),
        total_existing_customers=Count('s_customer_name', filter=~Q(s_customer_name=210), distinct=False)
    )

    sales_calls = Sales_Comments_Info.objects.filter(calls_filter, sc_updated_by__user_extinfo__department__dept_name="Sales",sc_updated_by__is_active=True).values(
        'sc_updated_by__id', 'sc_updated_by__first_name'
    ).annotate(
        total_sales_calls=Count('id'),
        actual_new_customer_calls=Count('id', filter=Q(sc_sales_number__s_customer_name_id=210)),
        actual_existing_customer_calls=Count('id', filter=~Q(sc_sales_number__s_customer_name_id=210))
    )

    actual_revenue = BusinessrevenueInfo.objects.filter(revenue_filter).values(
        'br_sale_person__id', 'br_sale_person__first_name'
    ).annotate(
        actual_revenue=Sum('br_revenue_1')
    )

    summary = []
    salesperson_ids = set(
        list(target['st_sales_person__id'] for target in target_data) +
        list(actual['s_updated_by__id'] for actual in actual_data) +
        list(call['sc_updated_by__id'] for call in sales_calls) +
        list(revenue['br_sale_person__id'] for revenue in actual_revenue)
    )

    for salesperson_id in salesperson_ids:
        salesperson_name = next(
            (t['st_sales_person__first_name'] for t in target_data if t['st_sales_person__id'] == salesperson_id),
            None
        ) or next(
            (a['s_updated_by__first_name'] for a in actual_data if a['s_updated_by__id'] == salesperson_id),
            None
        ) or next(
            (c['sc_updated_by__first_name'] for c in sales_calls if c['sc_updated_by__id'] == salesperson_id),
            "Unknown"
        ) or next(
            (rev['br_sale_person__first_name'] for rev in actual_revenue if rev['br_sale_person__id'] == salesperson_id),
            "Unknown"
        )

        # Fetch target, actuals, and calls
        target = next((t for t in target_data if t['st_sales_person__id'] == salesperson_id), {})
        actual = next((a for a in actual_data if a['s_updated_by__id'] == salesperson_id), {})
        calls = next((c for c in sales_calls if c['sc_updated_by__id'] == salesperson_id), {})
        revenue = next((rev for rev in actual_revenue if rev['br_sale_person__id'] == salesperson_id), {})

        summary.append({
            'salesperson': salesperson_name,
            'total_target_customers': target.get('total_target_customers', 0),
            'target_new_customer_calls': target.get('target_new_customer_calls', 0),
            'target_existing_customer_calls': target.get('target_existing_customer_calls', 0),
            'target_revenue': target.get('target_revenue', 0),
            'total_actual_customers': actual.get('total_actual_customers', 0),
            'total_new_customers': actual.get('total_new_customers', 0),
            'total_existing_customers': actual.get('total_existing_customers', 0),
            'total_sales_calls': calls.get('total_sales_calls', 0),
            'actual_new_customer_calls': calls.get('actual_new_customer_calls', 0),
            'actual_existing_customer_calls': calls.get('actual_existing_customer_calls', 0),
            'actual_revenue': revenue.get('actual_revenue', 0)
        })

    return render(request, "asset_mgt_app/target_actuals_report.html", {
        'summary': summary,
        'first_name': first_name,
        'salespersons': salespersons,
        'selected_salesperson': selected_salesperson,
        'from_date': from_date,
        'to_date': to_date
    })


def sales_call_report(request):
    # Query SalesInfo and related Sales_Comments_Info
    sales_reports = Sales_Comments_Info.objects.select_related(
        'sc_sales_number',
        'sc_updated_by'
    ).all()

    context = {
        'sales_reports': sales_reports
    }
    return render(request,"asset_mgt_app/sales_call_report.html",context)


def businesswon_chart(request):
    first_name = request.session.get('first_name')
    selected_salesperson = request.GET.get('salesperson', None)
    selected_company = request.GET.get('company', None)
    selected_branch = request.GET.get('branch', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    salespersons = MyUser.objects.select_related('user_extinfo').filter(
        user_extinfo__department__dept_name="Sales", is_active=True
    ).distinct().values_list('first_name', flat=True)

    company_name = Business_Sol_info.objects.filter(
        id__in=SalesInfo.objects.values_list('s_company', flat=True)
    ).distinct().values_list('bvm_business', flat=True)

    branch_name = Location_info.objects.filter(
        id__in=SalesInfo.objects.values_list('s_location', flat=True)
    ).distinct().values_list('loc_name', flat=True)

    yesno_names = YesNoInfo.objects.values_list('yesno_name', flat=True)

    sales_data_query = SalesInfo.objects.all()
    sales_data_query = SalesInfo.objects.filter(
        s_updated_by__user_extinfo__department__dept_name="Sales",s_updated_by__is_active=True
    )

    if selected_salesperson:
        sales_data_query = sales_data_query.filter(s_updated_by__first_name=selected_salesperson)
    if from_date:
        sales_data_query = sales_data_query.filter(s_updated_at__date__gte=from_date)
    if to_date:
        sales_data_query = sales_data_query.filter(s_updated_at__date__lte=to_date)
    if selected_company:
        sales_data_query = sales_data_query.filter(s_company__bvm_business=selected_company)
    if selected_branch:
        sales_data_query = sales_data_query.filter(s_location__loc_name=selected_branch)

    def sanitize_key(key):
        return key.replace(" ", "_").replace("-", "_").replace("/", "_")

    bus_won_aggregation = {
        "new_customer": Count(Case(When(s_customer_name="210", then=1))),
        "existing_customer": Count(Case(When(~Q(s_customer_name="210"), then=1))),
    }

    sales_data = sales_data_query.values('s_bus_won_not__yesno_name').annotate(**bus_won_aggregation)

    yesno_labels = list(yesno_names)

    # Bar chart data
    new_customer_counts = [
        sum(sales_entry.get("new_customer", 0) for sales_entry in sales_data if sales_entry["s_bus_won_not__yesno_name"] == yesno)
        for yesno in yesno_labels
    ]
    existing_customer_counts = [
        sum(sales_entry.get("existing_customer", 0) for sales_entry in sales_data if sales_entry["s_bus_won_not__yesno_name"] == yesno)
        for yesno in yesno_labels
    ]

    # Donut chart data for yes/no (new/existing customers)
    new_customers_yesno = [
        sales_data_query.filter(s_customer_name="210", s_bus_won_not__yesno_name=yesno).count()
        for yesno in yesno_labels
    ]
    existing_customers_yesno = [
        sales_data_query.filter(~Q(s_customer_name="210"), s_bus_won_not__yesno_name=yesno).count()
        for yesno in yesno_labels
    ]

    donut_chart_data = {
        "new_customers": new_customers_yesno,
        "existing_customers": existing_customers_yesno,
    }
    donut_chart_labels = [
        f"New Customers ({yesno})" for yesno in yesno_labels
    ] + [
        f"Existing Customers ({yesno})" for yesno in yesno_labels
    ]


    salesperson_data = (
        sales_data_query.filter(s_bus_won_not=1)  # Filter for bus_won_not=1
        .values('s_updated_by__first_name')  # Get the first name of the salesperson
        .annotate(business_won_count=Count('id'))  # Count the business_won (bus_won_not=1)
    )

    salesperson_labels = [
        entry['s_updated_by__first_name'] for entry in salesperson_data
    ]
    salesperson_counts = [
        entry['business_won_count'] for entry in salesperson_data
    ]

    table_data = sales_data_query.values(
        's_updated_by__first_name',
        's_customer_name__cu_nameshort',
        's_customer_new_name',
        's_bus_won_not__yesno_name',
        's_remarks'
    )
    context = {
        'first_name': first_name,
        'salespersons': salespersons,
        'company_name': company_name,
        'branch_name': branch_name,
        'selected_salesperson': selected_salesperson,
        'selected_company': selected_company,
        'selected_branch': selected_branch,
        'from_date': from_date,
        'to_date': to_date,
        'yesno_labels': yesno_labels,  # Labels for the bar chart
        'new_customer_counts': new_customer_counts,  # Data for new customers (bar chart)
        'existing_customer_counts': existing_customer_counts,  # Data for existing customers (bar chart)
        'donut_chart_data': list(donut_chart_data["new_customers"]) + list(donut_chart_data["existing_customers"]),
        'donut_chart_labels': donut_chart_labels,  # Labels for the yes/no donut chart
        'salesperson_labels': salesperson_labels,  # Labels for salesperson donut chart
        'salesperson_counts': salesperson_counts,  # Data for salesperson donut chart
        'table_data': table_data,  # Data for the table
    }
    return render(request, "asset_mgt_app/business_won_chart.html", context)


def salesperson_wise_chart(request):
    first_name = request.session.get('first_name')
    selected_salesperson = request.GET.get('salesperson', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    salespersons = MyUser.objects.select_related('user_extinfo').filter(
        user_extinfo__department__dept_name="Sales", is_active=True
    ).distinct().values_list('first_name', flat=True)

    sales_summary = Sales_Comments_Info.objects.filter(
        sc_updated_by__user_extinfo__department__dept_name="Sales",sc_updated_by__is_active=True
    )

    if selected_salesperson:
        sales_summary = sales_summary.filter(sc_updated_by__first_name=selected_salesperson)
    if from_date:
        sales_summary = sales_summary.filter(sc_updated_at__date__gte=from_date)
    if to_date:
        sales_summary = sales_summary.filter(sc_updated_at__date__lte=to_date)

    sales_summary = sales_summary.values(
        'sc_updated_by__first_name'  # Salesperson's first name
    ).annotate(
        total_customers=Count('sc_sales_number__s_customer_name', distinct=False),
        new_customers=Count(
            'sc_sales_number__s_customer_name',
            filter=Q(sc_sales_number__s_customer_name=210),
            distinct=False,
        ),
        existing_customers=Count(
            'sc_sales_number__s_customer_name',
            filter=~Q(sc_sales_number__s_customer_name=210),
            distinct=False,
        ),
        total_sales_calls=Count('id'),
        new_customer_calls=Count(
            'id',
            filter=Q(sc_sales_number__s_customer_name=210),
        ),
        existing_customer_calls=Count(
            'id',
            filter=~Q(sc_sales_number__s_customer_name=210),
        ),
        total_quotes=Count('sc_sales_number__s_quote_ref', distinct=True),
        won_count=Count(
            'sc_sales_number__s_bus_won_not',
            filter=Q(sc_sales_number__s_bus_won_not=1),
        ),
        performance_percentage=Case(
            When(total_sales_calls__gt=0, then=(F('total_customers') / F('total_sales_calls')) * 100),
            default=Value(0.0),
            output_field=FloatField(),
        ),
        productivity_percentage=Case(
            When(total_quotes__gt=0, then=(F('won_count') / F('total_quotes')) * 100),
            default=Value(0.0),
            output_field=FloatField(),
        ),
        target_revenue=Subquery(
            Sales_target_info.objects.filter(
                st_sales_person=OuterRef('sc_updated_by'),
                **({'st_start_date__gte': from_date} if from_date else {}),
                **({'st_start_date__lte': to_date} if to_date else {}),
            ).values('st_target_revenue')[:1]
        ),
        target_customers=Subquery(
            Sales_target_info.objects.filter(
                st_sales_person=OuterRef('sc_updated_by'),
                **({'st_start_date__gte': from_date} if from_date else {}),
                **({'st_start_date__lte': to_date} if to_date else {}),
            ).values('st_target_customer')[:1]
        ),
        target_calls_new_customer=Subquery(
            Sales_target_info.objects.filter(
                st_sales_person=OuterRef('sc_updated_by'),
                **({'st_start_date__gte': from_date} if from_date else {}),
                **({'st_start_date__lte': to_date} if to_date else {}),
            ).values('st_target_calls_new_customer')[:1]
        ),
        target_calls_existing_customer=Subquery(
            Sales_target_info.objects.filter(
                st_sales_person=OuterRef('sc_updated_by'),
                **({'st_start_date__gte': from_date} if from_date else {}),
                **({'st_start_date__lte': to_date} if to_date else {}),
            ).values('st_target_calls_existing_customer')[:1]
        ),
        total_revenue=Subquery(
            BusinessrevenueInfo.objects.filter(
                br_sale_person=OuterRef('sc_updated_by'),
                **({'br_from_date__gte': from_date} if from_date else {}),
                **({'br_from_date__lte': to_date} if to_date else {}),
            ).values('br_sale_person')
            .annotate(total=Sum('br_revenue_1'))
            .values('total')[:1]
        )
    )

    call_type_summary = sales_summary.values(
        'sc_call_type__call_type'
    ).annotate(
        call_type_count=Count('sc_call_type')
    )

    call_nature_summary = sales_summary.values(
        'sc_call_nature__call_nature'
    ).annotate(
        call_nature_count=Count('sc_call_nature')
    )

    call_purpose_summary = sales_summary.values(
        'sc_call_purpose__call_purpose'
    ).annotate(
        call_purpose_count=Count('sc_call_purpose')
    )
    context = {
        'first_name': first_name,
        'selected_salesperson': selected_salesperson,
        'salespersons': salespersons,
        'from_date': from_date,
        'to_date': to_date,
        'sales_summary': sales_summary,
        'call_type_summary': call_type_summary,
        'call_nature_summary': call_nature_summary,
        'call_purpose_summary': call_purpose_summary,
    }
    return render(request, "asset_mgt_app/salesperson_wise_chart.html", context)



def targets_actuals_table(request):
    first_name = request.session.get('first_name')
    selected_salesperson = request.GET.get('salesperson')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    # Fetch salespersons for the filter dropdown
    salespersons = MyUser.objects.select_related('user_extinfo').filter(
        user_extinfo__department__dept_name="Sales", is_active=True
    ).distinct().values_list('first_name', flat=True)

    # Prepare filters for Sales_target_info
    sales_target_filters = {}
    if selected_salesperson:
        sales_target_filters['st_sales_person__first_name'] = selected_salesperson
    if from_date:
        sales_target_filters['st_updated_at__date__gte'] = from_date
    if to_date:
        sales_target_filters['st_updated_at__date__lte'] = to_date

    # Apply filters to Sales_target_info
    sales_summary = Sales_target_info.objects.filter(**sales_target_filters)

    targets_actuals = Sales_target_info.objects.filter(**sales_target_filters).annotate(
        # Target data from the Sales_target_info model itself
        total_target_customers=Sum('st_target_customer'),
        target_new_customer_calls=Sum('st_target_calls_new_customer'),
        target_existing_customer_calls=Sum('st_target_calls_existing_customer'),
        target_revenue=Sum('st_target_revenue'),

        # Actual data from related SalesInfo
        total_actual_customers=Count('st_sales_person__s_updated_by__s_customer_name', distinct=True),
        total_new_customers=Count('st_sales_person__s_updated_by__s_customer_new_name', distinct=True),

        # Calls data from related SalesCommentsInfo
        total_sales_calls=Count('st_sales_person__sc_added_by', distinct=True),
        actual_new_customer_calls=Count(
            'st_sales_person__sc_added_by',
            filter=Q(st_sales_person__sc_added_by__sc_sales_number__s_customer_new_name__isnull=False),
            distinct=True
        ),
        actual_existing_customer_calls=Count(
            'st_sales_person__sc_added_by',
            filter=Q(st_sales_person__sc_added_by__sc_sales_number__s_customer_new_name__isnull=True),
            distinct=True
        ),

        # Revenue data from related BusinessRevenueInfo
        actual_revenue=Sum('st_sales_person__br_sale_person__br_revenue_1', distinct=True),
    ).distinct()

    # Return the context to render the template
    context = {
        'targets_actuals': targets_actuals,
        'from_date': from_date,
        'to_date': to_date,
        'selected_salesperson': selected_salesperson,
        'salespersons': salespersons,
    }

    return render(request, "asset_mgt_app/Reports_example.html", context)


