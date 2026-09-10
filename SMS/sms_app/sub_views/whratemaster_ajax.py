from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from ..models import WhratemasterInfo

@login_required(login_url='login_page')
def whratemaster_list_ajax(request):
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')

    queryset = WhratemasterInfo.objects.select_related(
        'whrm_customer_name', 'whrm_businessmodel', 'whrm_charge_type',
        'whrm_vehicle_type', 'whrm_updated_by'
    ).all()

    if search_value:
        queryset = queryset.filter(
            Q(whrm_customer_name__cu_name__icontains=search_value) |
            Q(whrm_businessmodel__tr_bussinesstype_name__icontains=search_value) |
            Q(whrm_charge_type__ch_description__icontains=search_value) |
            Q(whrm_vehicle_type__veh_type__icontains=search_value)
        )

    total_records = WhratemasterInfo.objects.count()
    filtered_records = queryset.count()

    order_column_index = request.GET.get('order[0][column]', 1)
    order_dir = request.GET.get('order[0][dir]', 'desc')

    columns = [
        'id', 'id', 'whrm_customer_name__cu_name', 'whrm_businessmodel__tr_bussinesstype_name',
        'whrm_charge_type__ch_description', 'whrm_vehicle_type__veh_type', 'whrm_min_wt',
        'whrm_max_wt', 'whrm_min_area', 'whrm_max_area', 'whrm_rate', 'whrm_description',
        'whrm_updated_on', 'whrm_updated_by__username'
    ]

    if int(order_column_index) < len(columns):
        order_by = columns[int(order_column_index)]
        if order_by:
            if order_dir == 'desc':
                order_by = f"-{order_by}"
            queryset = queryset.order_by(order_by)
    else:
        queryset = queryset.order_by('-id')

    data = []
    for item in queryset[start:start+length]:
        update_url = reverse('whratemaster_update', args=[item.id])
        delete_url = reverse('whratemaster_delete', args=[item.id])
        csrf_token = request.COOKIES.get('csrftoken', '')
        
        edit_btn = f'''<div class="d-flex justify-content-center gap-1">
            <a class="btn btn-primary btn-sm" href="{update_url}" >
                <i class="far fa-edit"></i>
            </a>
        </div>'''
        
        delete_btn = f'''<div class="d-flex justify-content-center gap-1">
            <form action="{delete_url}" method="post" onclick="return confirm('Are you sure?');">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                <button type="submit" class="btn btn-danger btn-sm">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </form>
        </div>'''

        data.append({
            'edit': edit_btn,
            'id': item.id,
            'whrm_customer_name': str(item.whrm_customer_name.cu_name) if hasattr(item, 'whrm_customer_name') and item.whrm_customer_name else '',
            'whrm_businessmodel': str(item.whrm_businessmodel.tr_bussinesstype_name) if hasattr(item, 'whrm_businessmodel') and item.whrm_businessmodel else '',
            'whrm_charge_type': str(item.whrm_charge_type.ch_description) if hasattr(item, 'whrm_charge_type') and item.whrm_charge_type else '',
            'whrm_vehicle_type': str(item.whrm_vehicle_type.veh_type) if hasattr(item, 'whrm_vehicle_type') and item.whrm_vehicle_type else '',
            'whrm_min_wt': item.whrm_min_wt or 0,
            'whrm_max_wt': item.whrm_max_wt or 0,
            'whrm_min_area': item.whrm_min_area or 0,
            'whrm_max_area': item.whrm_max_area or 0,
            'whrm_rate': item.whrm_rate or 0,
            'whrm_description': item.whrm_description or '',
            'whrm_updated_on': timezone.localtime(item.whrm_updated_on).strftime('%b %d, %Y') if item.whrm_updated_on else '',
            'whrm_updated_by': str(item.whrm_updated_by.username) if hasattr(item, 'whrm_updated_by') and item.whrm_updated_by else '',
            'delete': delete_btn
        })

    return JsonResponse({
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    })
