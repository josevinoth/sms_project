from django.db.models import Count
from django.shortcuts import render
from django.db.models import Count, Q
from ..models import Sales_Comments_Info, MyUser,SalesInfo


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


def monthly_summary(request):
    # Get filters from query parameters
    selected_salesperson = request.GET.get('salesperson', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    # Get all distinct salespersons
    salespersons = MyUser.objects.filter(
        sc_added_by__isnull=False
    ).distinct().values_list('first_name', flat=True)

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
    )

    # Prepare data for the template
    sales_data = [
        {
            "salesperson": item['sc_updated_by__first_name'],
            "total_sales": item['total_sales'],
            "new_customer_calls": item['new_customer_calls'],
            "existing_customer_calls": item['existing_customer_calls'],
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

    # Context for the template
    context = {
        'labels': labels,
        'new_customer_calls': new_customer_calls,
        'existing_customer_calls': existing_customer_calls,
        "sales_data": sales_data,
        'salespersons': salespersons,
        'selected_salesperson': selected_salesperson,
        'from_date': from_date,
        'to_date': to_date,
    }

    return render(request, "asset_mgt_app/monthlysummary.html", context)
