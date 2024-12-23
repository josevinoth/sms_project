from django.shortcuts import render
from ..models import Sales_Comments_Info,Sales_target_info,SalesInfo

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

def sales_targets_view(request):
    sales_targets = Sales_target_info.objects.select_related('st_sales_person').all()
    sales_actuals = SalesInfo.objects.select_related('s_customer_name').all()

    for target in sales_targets:
        target.match_count = sum(
            1 for actual in sales_actuals if actual.s_customer_name_id == target.st_sales_person_id
        )

    context = {
        'sales_targets': sales_targets,
        'sales_actuals': sales_actuals,
    }
    return render(request, "asset_mgt_app/sales_targets.html", context)
