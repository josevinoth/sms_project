from django.shortcuts import render
from django.http import JsonResponse

def bar_chart_data(request):
    data = {
        "labels": ["January", "February", "March", "April", "May"],
        "datasets": [
            {
                "label": "Sales",
                "backgroundColor": "rgba(54, 162, 235, 0.6)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 1,
                "data": [65, 59, 80, 81, 56],
            }
        ],
    }
    return JsonResponse(data)

def bar_chart(request):
    return render(request, "asset_mgt_app/chart.html")
