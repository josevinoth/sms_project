from django.db.models import Count
from django.shortcuts import render
from ..models import Sales_Comments_Info, MyUser


def salesperson_chart(request):
    # Get filters from query parameters
    selected_salesperson = request.GET.get('salesperson', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    # Get all distinct salespersons (first names) for the filter dropdown
    salespersons = MyUser.objects.filter(
        sales_comments_info__isnull=False
    ).distinct().values_list('first_name', flat=True)

    # Filter the data based on filters
    sales_data_query = Sales_Comments_Info.objects.all()

    if selected_salesperson:
        sales_data_query = sales_data_query.filter(sc_updated_by__first_name=selected_salesperson)

    if from_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__gte=from_date)

    if to_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__lte=to_date)

    # Annotate the sales count for each salesperson
    sales_data = sales_data_query.values('sc_updated_by__first_name').annotate(sales_count=Count('id'))

    # Prepare data for the chart
    labels = [item['sc_updated_by__first_name'] for item in sales_data]
    data = [item['sales_count'] for item in sales_data]

    context = {
        'labels': labels,
        'data': data,
        'salespersons': salespersons,  # Pass all salespersons for the dropdown
        'selected_salesperson': selected_salesperson,  # Keep track of the selected value
        'from_date': from_date,  # Keep track of the selected "from" date
        'to_date': to_date,  # Keep track of the selected "to" date
    }
    return render(request, "asset_mgt_app/salesperson_chart.html", context)


from django.db.models import Count
from django.shortcuts import render
from ..models import Sales_Comments_Info, MyUser


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

    context = {
        'labels': labels,
        'data': data,
        'salespersons': salespersons,
        'selected_salesperson': selected_salesperson,
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, "asset_mgt_app/salesperson_chart.html", context)
