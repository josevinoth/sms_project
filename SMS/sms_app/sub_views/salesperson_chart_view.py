from django.db.models import Count
from django.shortcuts import render
from django.db.models import Count, Q
from django.db.models import F, Subquery, OuterRef
from ..models import Sales_Comments_Info, MyUser,SalesInfo,Sales_target_info,BusinessrevenueInfo


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


from django.db.models import Subquery, OuterRef, Count, Q

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
    sales_data_query = Sales_Comments_Info.objects.values('sc_updated_by__first_name').annotate(
        total_sales_calls=Count('id'),
        total_sales_info=Count('sc_sales_number__id'),
        unique_customers=Count('sc_sales_number__s_customer_name', distinct=True),  # Unique customers
        total_quotes=Count('sc_sales_number__s_quote_ref', distinct=True),  # Total quotes
        won_business_count=Count(
            'sc_sales_number__s_bus_won_not',
            filter=Q(sc_sales_number__s_bus_won_not=1),
        ),
    )

    # Prepare chart data
    labels = []
    performance_percentages = []
    productivity_percentages = []

    for item in sales_data_query:
        labels.append(item["sc_updated_by__first_name"])
        performance_percentages.append(
            round((item['unique_customers'] / item['total_sales_calls']) * 100, 2)
            if item['total_sales_calls'] > 0 else 0.0
        )
        productivity_percentages.append(
            round((item['won_business_count'] / item['total_quotes']) * 100, 2)
            if item['total_quotes'] > 0 else 0.0
        )

    # Combine the data into a single dictionary
    chart_data = {
        "labels": labels,
        "performance_percentages": performance_percentages,
        "productivity_percentages": productivity_percentages,
    }

    context = {
        'chart_data': chart_data,
    }

    return render(request, "asset_mgt_app/donut_chart.html", context)
