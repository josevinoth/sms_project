from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from ..forms import WhratemasteraddForm
from ..models import WhratemasterInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def whratemaster_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    whratemaster_list = WhratemasterInfo.objects.select_related(
        'whrm_customer_name', 'whrm_businessmodel', 'whrm_charge_type',
        'whrm_vehicle_type', 'whrm_updated_by'
    ).only(
        'id', 'whrm_customer_name', 'whrm_businessmodel', 'whrm_charge_type',
        'whrm_vehicle_type', 'whrm_min_wt', 'whrm_max_wt', 'whrm_min_area',
        'whrm_max_area', 'whrm_rate', 'whrm_description',
        'whrm_updated_on', 'whrm_updated_by'
    ).order_by('-id')
    context = {
        'whratemaster_list': whratemaster_list,
        'first_name': first_name,
        'user_id': user_id,
    }
    return render(request, "asset_mgt_app/whratemaster_list.html", context)


# Add whratemaster
@login_required(login_url='login_page')
def whratemaster_add(request, whratemaster_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print('user_id',user_id)
    if request.method == "GET":
        if whratemaster_id == 0:
            form = WhratemasteraddForm()
        else:
            whratemasterinfo = WhratemasterInfo.objects.get(pk=whratemaster_id)
            form = WhratemasteraddForm(instance=whratemasterinfo)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
        }
        return render(request, "asset_mgt_app/whratemaster_add.html", context)
    else:
        form = WhratemasteraddForm(request.POST)
        if form.is_valid():
            # Check for duplicates before saving
            whrm_customer_name = form.cleaned_data['whrm_customer_name']
            whrm_businessmodel = form.cleaned_data['whrm_businessmodel']
            whrm_charge_type = form.cleaned_data['whrm_charge_type']
            whrm_max_wt = form.cleaned_data['whrm_max_wt']
            whrm_min_wt = form.cleaned_data['whrm_min_wt']
            whrm_min_area = form.cleaned_data['whrm_min_area']
            whrm_max_area = form.cleaned_data['whrm_max_area']
            whrm_rate = form.cleaned_data['whrm_rate']
            whrm_description = form.cleaned_data['whrm_description']
            whrm_vehicle_type = form.cleaned_data['whrm_vehicle_type']
            print('whrm_customer_name',whrm_customer_name)
            if not WhratemasterInfo.objects.filter(whrm_customer_name=whrm_customer_name,whrm_businessmodel=whrm_businessmodel,whrm_charge_type=whrm_charge_type,whrm_max_wt=whrm_max_wt,whrm_min_wt=whrm_min_wt,whrm_min_area=whrm_min_area,whrm_max_area=whrm_max_area,whrm_rate=whrm_rate,whrm_description=whrm_description,whrm_vehicle_type=whrm_vehicle_type).exclude(id=whratemaster_id).exists():
                if whratemaster_id == 0:
                    print("Inside post add")
                    form = WhratemasteraddForm(request.POST)
                    form.save()
                    print("Warehouse Rate master form saved")
                    messages.success(request, 'Record Updated Successfully')
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    print("Inside post edit")
                    whratemasterinfo = WhratemasterInfo.objects.get(pk=whratemaster_id)
                    form = WhratemasteraddForm(request.POST, instance=whratemasterinfo)
                    form.save()
                    print("Warehouse Rate master form saved")
                    messages.success(request, 'Record Updated Successfully')
                    return redirect(request.META['HTTP_REFERER'])
            else:
                print("Main form not saved")
                messages.error(request, 'Similar record exist. Please enter Unique values.')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("PkpurchaseorderInfo Form is Not Valid")
            messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/whratemaster_list')


# Delete whratemaster
@login_required(login_url='login_page')
def whratemaster_delete(request, whratemaster_id):
    whratemasterinfo = WhratemasterInfo.objects.get(pk=whratemaster_id)
    whratemasterinfo.delete()
    return redirect('/SMS/whratemaster_list')

from django.http import JsonResponse

from django.db.models import Q

from django.urls import reverse

from django.contrib.auth.decorators import login_required





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

            'whrm_updated_on': item.whrm_updated_on.strftime('%b %d, %Y') if item.whrm_updated_on else '',

            'whrm_updated_by': str(item.whrm_updated_by.username) if hasattr(item, 'whrm_updated_by') and item.whrm_updated_by else '',

            'delete': delete_btn

        })



    return JsonResponse({

        'draw': draw,

        'recordsTotal': total_records,

        'recordsFiltered': filtered_records,

        'data': data

    })

from django.http import JsonResponse

from django.db.models import Q

from django.urls import reverse

from django.contrib.auth.decorators import login_required





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

            'whrm_updated_on': item.whrm_updated_on.strftime('%b %d, %Y') if item.whrm_updated_on else '',

            'whrm_updated_by': str(item.whrm_updated_by.username) if hasattr(item, 'whrm_updated_by') and item.whrm_updated_by else '',

            'delete': delete_btn

        })



    return JsonResponse({

        'draw': draw,

        'recordsTotal': total_records,

        'recordsFiltered': filtered_records,

        'data': data

    })



from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth.decorators import login_required


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
            Q(whrm_businessmodel__tb_trbusinesstype__icontains=search_value) |
            Q(whrm_charge_type__charge_Type__icontains=search_value) |
            Q(whrm_vehicle_type__vt_vehicletype__icontains=search_value)
        )

    total_records = WhratemasterInfo.objects.count()
    filtered_records = queryset.count()

    order_column_index = request.GET.get('order[0][column]', 1)
    order_dir = request.GET.get('order[0][dir]', 'desc')

    columns = [
        'id', 'id', 'whrm_customer_name__cu_name', 'whrm_businessmodel__tb_trbusinesstype',
        'whrm_charge_type__charge_Type', 'whrm_vehicle_type__vt_vehicletype', 'whrm_min_wt',
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
            'whrm_businessmodel': str(item.whrm_businessmodel.tb_trbusinesstype) if hasattr(item, 'whrm_businessmodel') and item.whrm_businessmodel else '',
            'whrm_charge_type': str(item.whrm_charge_type.charge_Type) if hasattr(item, 'whrm_charge_type') and item.whrm_charge_type else '',
            'whrm_vehicle_type': str(item.whrm_vehicle_type.vt_vehicletype) if hasattr(item, 'whrm_vehicle_type') and item.whrm_vehicle_type else '',
            'whrm_min_wt': item.whrm_min_wt or 0,
            'whrm_max_wt': item.whrm_max_wt or 0,
            'whrm_min_area': item.whrm_min_area or 0,
            'whrm_max_area': item.whrm_max_area or 0,
            'whrm_rate': item.whrm_rate or 0,
            'whrm_description': item.whrm_description or '',
            'whrm_updated_on': item.whrm_updated_on.strftime('%b %d, %Y') if item.whrm_updated_on else '',
            'whrm_updated_by': str(item.whrm_updated_by.username) if hasattr(item, 'whrm_updated_by') and item.whrm_updated_by else '',
            'delete': delete_btn
        })

    return JsonResponse({
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    })
