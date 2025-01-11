from django.shortcuts import render
from django.db.models import Count, Q,Sum,Case, When, Value, CharField, Min,FloatField, F
from django.db.models import F, Subquery, OuterRef
from ..models import Sales_Comments_Info, MyUser,SalesInfo,Sales_target_info,BusinessrevenueInfo,Calltype,Callpurpose,Callnature,User_extInfo,CustomerInfo,YesNoInfo,Business_Sol_info,Location_info

def salesperson_chart(request):

    selected_salesperson = request.GET.get('salesperson', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)


    salespersons = MyUser.objects.filter(
        sc_added_by__isnull=False
    ).distinct().values_list('first_name', flat=True)

    sales_data_query = Sales_Comments_Info.objects.all()

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
        'labels': labels,
        'data': data,
        'table_data': table_data,
        'salespersons': salespersons,
        'selected_salesperson': selected_salesperson,
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, "asset_mgt_app/salesperson_chart.html", context)


from django.db.models import Sum,Subquery, OuterRef, Count, Q

def monthly_summary(request):
    # Get filters from query parameters
    selected_salesperson = request.GET.get('salesperson', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    # Get all distinct salespersons
    salespersons = MyUser.objects.filter(
        sc_added_by__isnull=False
    ).distinct().values_list('first_name', flat=True)

    # Define Subqueries for target calls
    target_existing_customers_subquery = Sales_target_info.objects.filter(
        st_sales_person__first_name=OuterRef('sc_updated_by__first_name')  # Adjust field name if needed
    ).values('st_target_calls_existing_customer')[:1]  # Replace with correct field in `Sales_target_info`

    target_new_customers_subquery = Sales_target_info.objects.filter(
        st_sales_person__first_name=OuterRef('sc_updated_by__first_name')  # Adjust field name if needed
    ).values('st_target_calls_new_customer')[:1]  # Replace with correct field in `Sales_target_info`

    target_revenue_subquery = Sales_target_info.objects.filter(
        st_sales_person__first_name=OuterRef('sc_updated_by__first_name')  # Adjust field name if needed
    ).values('st_target_revenue')[:1]  # Replace with correct field in `Sales_target_info`

    actual_revenue_subquery = BusinessrevenueInfo.objects.filter(
        br_sale_person__first_name=OuterRef('sc_updated_by__first_name')  # Adjust field name if needed
     ).values('br_revenue_1')[:1]  # Replace with correct field in `Sales_target_info`

    # Filter the data based on filters
    sales_data_query = Sales_Comments_Info.objects.all()

    if selected_salesperson:
        sales_data_query = sales_data_query.filter(sc_updated_by__first_name=selected_salesperson)

    if from_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__gte=from_date)

    if to_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__lte=to_date)

    # Annotate the sales count and group by salesperson
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
    # Fetch data from the database
    selected_salesperson = request.GET.get('salesperson', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    # Get all distinct salespersons
    salespersons = MyUser.objects.filter(
        sc_added_by__isnull=False
    ).distinct().values_list('first_name', flat=True)

    # Define Subqueries for target calls
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

    # Filter the data based on filters
    sales_data_query = Sales_Comments_Info.objects.all()

    if selected_salesperson:
        sales_data_query = sales_data_query.filter(sc_updated_by__first_name=selected_salesperson)

    if from_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__gte=from_date)

    if to_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__lte=to_date)

    # Annotate the sales count and group by salesperson
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

    # Prepare data for the template
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

    # Context for the template
    context = {
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
        'from_date': from_date,
        'to_date': to_date,
    }

    return render(request, "asset_mgt_app/donut_chart.html", context)


def salescalls_details(request):
    selected_salesperson = request.GET.get('salesperson', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    # Fetch salespersons
    salespersons = MyUser.objects.select_related('user_extinfo').filter(
        user_extinfo__department__dept_name ="Sales"
    ).distinct().values_list('first_name', flat=True)

    # Fetch distinct call types, purposes, and natures
    call_types = Calltype.objects.values_list('call_type', flat=True)
    call_purposes = Callpurpose.objects.values_list('call_purpose', flat=True)
    call_natures = Callnature.objects.values_list('call_nature', flat=True)

    # Query sales data
    sales_data_query = Sales_Comments_Info.objects.all()

    if selected_salesperson:
        sales_data_query = sales_data_query.filter(sc_updated_by__first_name=selected_salesperson)

    if from_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__gte=from_date)

    if to_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__lte=to_date)

    # Helper to sanitize keys
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

    # Prepare table data for each aggregation
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
    selected_salesperson = request.GET.get('salesperson', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    # Fetch salespersons
    salespersons = MyUser.objects.select_related('user_extinfo').filter(
        user_extinfo__department__dept_name="Sales"
    ).distinct().values_list('first_name', flat=True)

    # Build individual filter criteria for each model
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
    target_data = Sales_target_info.objects.filter(target_filter).values(
        'st_sales_person__id', 'st_sales_person__first_name'
    ).annotate(
        total_target_customers=Sum('st_target_customer'),
        target_new_customer_calls=Sum('st_target_calls_new_customer'),
        target_existing_customer_calls=Sum('st_target_calls_existing_customer'),
        target_revenue=Sum('st_target_revenue')
    )

    actual_data = SalesInfo.objects.filter(actual_filter).values(
        's_updated_by__id', 's_updated_by__first_name'
    ).annotate(
        total_actual_customers=Count('s_customer_name', distinct=True),
        total_new_customers=Count('s_customer_new_name', distinct=True),
        total_existing_customers=Count('s_customer_name', filter=~Q(s_customer_name=210), distinct=True)
    )

    sales_calls = Sales_Comments_Info.objects.filter(calls_filter).values(
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

    # Combine data into a single structure
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
    selected_salesperson = request.GET.get('salesperson', None)
    selected_company = request.GET.get('company', None)
    selected_branch = request.GET.get('branch', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    # Filter salespersons
    salespersons = MyUser.objects.filter(
        user_extinfo__department__dept_name="Sales"
    ).distinct().values_list('first_name', flat=True)

    company_name = Business_Sol_info.objects.filter(
        id__in=SalesInfo.objects.values_list('s_company', flat=True)
    ).distinct().values_list('bvm_business', flat=True)

    branch_name = Location_info.objects.filter(
        id__in=SalesInfo.objects.values_list('s_location', flat=True)
    ).distinct().values_list('loc_name', flat=True)

    # Base query with annotated CustomerType
    sales_data_query = SalesInfo.objects.select_related(
        's_updated_by', 's_bus_won_not', 's_customer_name'
    ).annotate(
        CustomerType=Case(
            When(s_customer_name__id=210, then=Value("New Customer")),
            default=Value("Existing Customer"),
            output_field=CharField()
        )
    )

    # Apply filters
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

    # Aggregate data for business won by customer type
    aggregated_data = sales_data_query.values(
        's_bus_won_not__yesno_name', 'CustomerType'
    ).annotate(
        count_bus_won=Count('s_bus_won_not')
    )

    # Prepare the data for the chart
    customer_types = ["New Customer", "Existing Customer"]
    yes_no_names = sorted(set(
        (name if name is not None else "Unknown")
        for name in aggregated_data.values_list('s_bus_won_not__yesno_name', flat=True)
    ))

    data_dict = {name: {"New Customer": 0, "Existing Customer": 0} for name in yes_no_names}

    for item in aggregated_data:
        yes_no_name = item['s_bus_won_not__yesno_name'] if item['s_bus_won_not__yesno_name'] is not None else "Unknown"
        data_dict[yes_no_name][item['CustomerType']] = item['count_bus_won']

    datasets = []
    for customer_type in customer_types:
        dataset = {
            'label': customer_type,
            'data': [data_dict[name][customer_type] for name in yes_no_names],
            'backgroundColor': 'rgba(245, 131, 39, 0.5)' if customer_type == "New Customer" else 'rgba(149, 145, 142, 0.5)',
            'borderColor': 'rgb(245, 131, 39)' if customer_type == "New Customer" else 'rgb(149, 145, 142)',
            'borderWidth': 1
        }
        datasets.append(dataset)

    # Data for donut chart (distribution of 'Yes' and 'No' values for all customer types)
    yes_count = sum([data_dict[name]["New Customer"] + data_dict[name]["Existing Customer"] for name in yes_no_names if name == "Yes"])
    no_count = sum([data_dict[name]["New Customer"] + data_dict[name]["Existing Customer"] for name in yes_no_names if name == "No"])

    donut_data = {
        'labels': ['Yes', 'No'],
        'datasets': [{
            'data': [yes_count, no_count],
        }]
    }

    # Step 1: Aggregate business won count by salesperson
    salesperson_data = sales_data_query.filter(s_bus_won_not__yesno_name="Yes").values(
        's_updated_by__first_name'
    ).annotate(
        count_bus_won=Count('s_bus_won_not')
    )

    # Step 2: Prepare the data for the salesperson-wise donut chart
    salesperson_names = sorted(set(
        item['s_updated_by__first_name'] for item in salesperson_data
    ))
    salesperson_counts = [next(
        (item['count_bus_won'] for item in salesperson_data if item['s_updated_by__first_name'] == name), 0
    ) for name in salesperson_names]

    # Step 3: Prepare the data for the new donut chart
    salesperson_donut_data = {
        'labels': salesperson_names,
        'datasets': [{
            'data': salesperson_counts
        }]
    }
    table_data = []
    for item in sales_data_query:
        salesperson = item.s_updated_by.first_name if item.s_updated_by else 'N/A'
        customer_name = item.s_customer_name.cu_nameshort if item.s_customer_name else 'N/A'
        new_customer_name = item.s_customer_new_name if item.s_customer_new_name else 'N/A'
        business_status = item.s_bus_won_not.yesno_name.strip().capitalize() if item.s_bus_won_not else 'N/A'
        remarks = item.s_remarks if item.s_remarks else 'N/A'

        table_data.append({
            'salesperson': salesperson,
            'customer_name': customer_name,
            'new_customer_name': new_customer_name,
            'business_status': business_status,
            'remarks': remarks,
        })

    context = {
        'labels': yes_no_names,
        'datasets': datasets,
        'salespersons': salespersons,
        'company_name': company_name,
        'branch_name': branch_name,
        'selected_salesperson': selected_salesperson,
        'selected_company': selected_company,
        'selected_branch': selected_branch,
        'from_date': from_date,
        'to_date': to_date,
        'table_data': table_data,
        'donut_data': donut_data,
        'salesperson_donut_data': salesperson_donut_data
    }

    return render(request, "asset_mgt_app/business_won_chart.html", context)


def salesperson_wise_chart(request):
    selected_salesperson = request.GET.get('salesperson', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    # Fetch salespersons
    salespersons = MyUser.objects.select_related('user_extinfo').filter(
        user_extinfo__department__dept_name="Sales"
    ).distinct().values_list('first_name', flat=True)

    sales_summary = Sales_Comments_Info.objects.all()

    if selected_salesperson:
        sales_data_query = sales_summary.filter(sc_updated_by__first_name=selected_salesperson)

    if from_date:
        sales_data_query = sales_summary.filter(sc_updated_at__date__gte=from_date)

    if to_date:
        sales_data_query = sales_summary.filter(sc_updated_at__date__lte=to_date)
    sales_summary = Sales_Comments_Info.objects.values(
        'sc_sales_number__s_updated_by__first_name',  # Access salesperson's first name via sc_sales_number
    ).annotate(
        total_customers=Count('sc_sales_number__s_customer_name', distinct=False),
        new_customers=Count(
            'sc_sales_number__s_customer_new_name', filter=Q(sc_sales_number__s_customer_name=210),distinct=False),
        existing_customers=Count(
            'sc_sales_number__s_customer_name',
            filter=~Q(sc_sales_number__s_customer_name=210),distinct=False),
        total_sales_calls=Count('id'),
        new_customer_calls=Count(
            'id',
            filter=Q(sc_sales_number__s_customer_name=210)
        ),
        existing_customer_calls=Count(
            'id',
            filter=~Q(sc_sales_number__s_customer_name=210)
        ),
        total_quotes=Count('sc_sales_number__s_quote_ref', distinct=True),
        won_count=Count(
            'sc_sales_number__s_bus_won_not',
            filter=Q(sc_sales_number__s_bus_won_not=1)
        ),

        performance_percentage=Case(
            When(total_sales_calls__gt=0, then=(F('total_customers') / F('total_sales_calls')) * 100),
            default=Value(0.0),
            output_field=FloatField()
        ),
        # Using Case and When to calculate productivity percentage
        productivity_percentage=Case(
            When(total_quotes__gt=0, then=(F('won_count') / F('total_quotes')) * 100),
            default=Value(0.0),
            output_field=FloatField()
        )
    )

    # Now add target data with a proper subquery for each salesperson.
    sales_summary = sales_summary.annotate(
        # Subquery to get the target revenue, ensuring a single result with OuterRef
        target_revenue=Subquery(
            Sales_target_info.objects.filter(
                st_sales_person=OuterRef('sc_sales_number__s_updated_by')
            ).values('st_target_revenue')[:1]  # Limiting to the first match
        ),
        target_customers=Subquery(
            Sales_target_info.objects.filter(
                st_sales_person=OuterRef('sc_sales_number__s_updated_by')
            ).values('st_target_customer')[:1]  # Limiting to the first match
        ),
        target_calls_new_customer=Subquery(
            Sales_target_info.objects.filter(
                st_sales_person=OuterRef('sc_sales_number__s_updated_by')
            ).values('st_target_calls_new_customer')[:1]  # Limiting to the first match
        ),
        target_calls_existing_customer=Subquery(
            Sales_target_info.objects.filter(
                st_sales_person=OuterRef('sc_sales_number__s_updated_by')
            ).values('st_target_calls_existing_customer')[:1]  # Limiting to the first match
        ),
    )

    sales_summary = sales_summary.annotate(
        # Subquery to get the sum of br_revenue_1 for each salesperson
        total_revenue=Subquery(
            BusinessrevenueInfo.objects.filter(
                br_sale_person=OuterRef('sc_sales_number__s_updated_by')  # Match the salesperson
            ).values('br_sale_person')  # Group by salesperson
            .annotate(total=Sum('br_revenue_1'))  # Calculate the sum of br_revenue_1
            .values('total')[:1]  # Extract the total revenue
        )
    )

    # Count for unique Call Types
    call_type_summary = Sales_Comments_Info.objects.values(
        'sc_call_type__call_type'
    ).annotate(
        call_type_count=Count('sc_call_type')
    )

    # Count for unique Call Natures
    call_nature_summary = Sales_Comments_Info.objects.values(
        'sc_call_nature__call_nature'
    ).annotate(
        call_nature_count=Count('sc_call_nature')
    )

    # Count for unique Call Purposes
    call_purpose_summary = Sales_Comments_Info.objects.values(
        'sc_call_purpose__call_purpose'
    ).annotate(
        call_purpose_count=Count('sc_call_purpose')
    )

    # Return all the summaries
    context = {
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