from django.shortcuts import render, redirect
from ..forms import GateinaddForm,LoadingbayddForm
from django.contrib.auth.decorators import login_required
from ..models import Gatein_info,Loadingbay_Info

# Add WH Job
@login_required(login_url='login_page')
def wh_job_add(request, gatein_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if gatein_id == 0:
            gatein_form = GateinaddForm()
            loadingbay_form=LoadingbayddForm()
            context = {
                'first_name': first_name,
                'gatein_form': gatein_form,
                'loadingbay_form': loadingbay_form,
            }
        else:
            gatein_info = Gatein_info.objects.get(pk=gatein_id)
            get_jobnum=Gatein_info.objects.get(pk=gatein_id).gatein_job_no
            request.session['ses_jobnum'] = get_jobnum
            set_jobnum = request.session.get('ses_jobnum')
            loadingbay_info=Loadingbay_Info.objects.get(lb_job_no=set_jobnum)
            loadingbay_form = LoadingbayddForm(instance=loadingbay_info)
            loadingbay_list = Loadingbay_Info.objects.filter(lb_job_no=set_jobnum)
            gatein_form = GateinaddForm(instance=gatein_info)
            gatein_list = Gatein_info.objects.filter(gatein_job_no=set_jobnum)
            context = {
                'gatein_form': gatein_form,
                'gatein_list': gatein_list,
                'first_name': first_name,
                'loadingbay_form': loadingbay_form,
                'loadingbay_list': loadingbay_list,
            }
        return render(request, "asset_mgt_app/wh_job_add.html", context)
    else:
        if gatein_id == 0:
            gatein_form = GateinaddForm(request.POST)
            loadingbay_form = LoadingbayddForm(request.POST)
        else:
            gatein_info = Gatein_info.objects.get(pk=gatein_id)
            get_jobnum = Gatein_info.objects.get(pk=gatein_id).gatein_job_no
            set_jobnum = request.session.get('ses_jobnum')
            loadingbay_info = Loadingbay_Info.objects.get(lb_job_no=set_jobnum)
            gatein_form = GateinaddForm(request.POST, instance=gatein_info)
            loadingbay_form = LoadingbayddForm(instance=loadingbay_info)
        if gatein_form.is_valid():
            gatein_form.save()
        elif loadingbay_form.is_valid():
            loadingbay_form.save()
        # return redirect(request.META['HTTP_REFERER'])
        return redirect('/SMS/wh_job_list')

# List WH Job
@login_required(login_url='login_page')
def wh_job_list(request):
    first_name = request.session.get('first_name')
    context = {'Gatein_list' : Gatein_info.objects.all(),'first_name': first_name,}
    return render(request,"asset_mgt_app/wh_job_list.html",context)

#Delete WH Job
@login_required(login_url='login_page')
def wh_job_delete(request,gatein_id):
    wh_job = Gatein_info.objects.get(pk=gatein_id)
    wh_job.delete()
    return redirect('/SMS/wh_job_list')


from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from sms_app.models import Gatein_info

def wh_job_list_ajax(request):
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')

    queryset = Gatein_info.objects.select_related('gatein_customer').all()

    if search_value:
        queryset = queryset.filter(
            Q(gatein_job_no__icontains=search_value) |
            Q(gatein_invoice__icontains=search_value) |
            Q(gatein_customer__cu_name__icontains=search_value)
        )

    total_records = Gatein_info.objects.count()
    filtered_records = queryset.count()
    
    # Ordering
    order_column_index = request.GET.get('order[0][column]', 0)
    order_dir = request.GET.get('order[0][dir]', 'desc')
    
    columns = ['gatein_job_no', 'gatein_invoice', 'gatein_customer__cu_name']
    
    if int(order_column_index) < len(columns):
        order_by = columns[int(order_column_index)]
        if order_dir == 'desc':
            order_by = f"-{order_by}"
        queryset = queryset.order_by(order_by)
    else:
        queryset = queryset.order_by('-id')

    data = []
    for item in queryset[start:start+length]:
        edit_btn = f'''
        <div class="d-flex justify-content-center gap-1">
            <a class="btn btn-submit" style="background: linear-gradient(135deg, #fbbf24, #f59e0b); border: none; color: white; width: 34px; height: 34px; display: inline-flex; align-items: center; justify-content: center; border-radius: 8px;" href="/SMS/wh_job_update/{item.id}/" >
                <i class="far fa-edit"></i>
            </a>
        </div>'''
        delete_btn = f'''
        <div class="d-flex justify-content-center gap-1">
            <form action="/SMS/wh_job_delete/{item.id}/" method="post" onclick="return confirm('Are you sure?');">
                <input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get('CSRF_COOKIE', '')}">
                <button type="submit" class="btn" style="background: #ef4444; border: none; color: white; width: 34px; height: 34px; display: inline-flex; align-items: center; justify-content: center; border-radius: 8px;">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </form>
        </div>'''

        data.append({
            'job_no': item.gatein_job_no or '',
            'invoice': item.gatein_invoice or '',
            'customer': str(item.gatein_customer.cu_name) if item.gatein_customer else 'None',
            'edit': edit_btn,
            'delete': delete_btn
        })

    return JsonResponse({
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    })
