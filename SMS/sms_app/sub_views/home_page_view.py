from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ..models import Gatein_info,Loadingbay_Info,TrbusinesstypeInfo,User_extInfo,Warehouse_goods_info,AssetInfo,Vendor_info,Location_info,Product_info,User,Service_Info
from django.shortcuts import render, redirect
from django.db.models import Sum
from datetime import datetime
@login_required(login_url='login_page')
def home_page(request):
    first_name=request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role=User_extInfo.objects.get(user=user_id).emp_role
    ses_username = request.session.get('ses_username', request.POST.get('username'))
    case_to_case=str(TrbusinesstypeInfo.objects.get(id=1))
    exlcusive=str(TrbusinesstypeInfo.objects.get(id=2))
    dedicated=str(TrbusinesstypeInfo.objects.get(id=3))
    house_hold=str(TrbusinesstypeInfo.objects.get(id=4))
    case_to_case_list=list(Warehouse_goods_info.objects.filter(wh_voucher_num=None,wh_check_in_out=2,wh_customer_type=case_to_case).values_list('wh_job_no',flat=True).distinct())
    dedicated_list=list(Warehouse_goods_info.objects.filter(wh_voucher_num=None,wh_check_in_out=2,wh_customer_type=dedicated).values_list('wh_job_no',flat=True).distinct())
    exclusive_list=list(Warehouse_goods_info.objects.filter(wh_voucher_num=None,wh_check_in_out=1,wh_customer_type=exlcusive).values_list('wh_job_no',flat=True).distinct())
    a=wh_e_way_bill_validity(request)
    wh_job_count=a[0]
    wh_job_list=a[1]
    context = {'count_asset': AssetInfo.objects.all().count(),
               'count_vendors': Vendor_info.objects.filter(vend_status=1).count(),
               'count_ass_asset': AssetInfo.objects.filter(asset_assignedto__isnull=False).count(),
               'count_unass_asset': AssetInfo.objects.filter(asset_assignedto__isnull=True).count(),
               'count_location': Location_info.objects.filter(loc_status=1).count(),
               'count_product': Product_info.objects.all().count(),
               'count_employee': User.objects.all().count(),
               'sum_ass_cost': AssetInfo.objects.aggregate(sum=Sum('asset_cost'))['sum'] or 0.00,
               'sum_service_cost':Service_Info.objects.aggregate(sum=Sum('ser_cost'))['sum'] or 0.00,
               'ses_username': ses_username,
               'first_name': first_name,
               'case_to_case_list': len(case_to_case_list),
               'dedicated_list': len(dedicated_list),
               'exclusive_list': len(exclusive_list),
               'role': role,
               'wh_job_list': wh_job_list,
               'wh_job_count': wh_job_count,
               }
    return render(request, 'asset_mgt_app/home_page.html', context)
@login_required(login_url='login_page')
def wh_e_way_bill_validity(request):
    # Get warehouse e-way bill
    wh_check_in_jobs = list((Warehouse_goods_info.objects.filter(wh_check_in_out=1).values_list('wh_job_no', flat=True)).distinct())
    wh_job_list = []
    for i in wh_check_in_jobs:
        wh_e_way_bill_date = (Loadingbay_Info.objects.get(lb_job_no=i).lb_validity_date)
        if wh_e_way_bill_date is not None:
            time_now = ((timezone.now()).astimezone(timezone.get_current_timezone())).strftime('%Y-%m-%d %H:%M:%S')
            time_now_new = datetime.strptime(time_now, '%Y-%m-%d %H:%M:%S')
            validity_hours = round((((wh_e_way_bill_date - time_now_new).total_seconds()) / 3600), 1)
            if validity_hours<4:
                wh_job_list.append(i)
            else:
                pass
        else:
            pass
    wh_job_count=len(wh_job_list)
    wh_job_list=wh_job_list
    return (wh_job_count,wh_job_list)

@login_required(login_url='login_page')
def wh_e_way_bill_list(request):
    a = wh_e_way_bill_validity(request)
    wh_job_list = a[1]
    first_name = request.session.get('first_name')
    context = {
                'wh_job_list' : wh_job_list,
                'first_name': first_name
            }
    return render(request,"asset_mgt_app/wh_e_way_bill_list.html",context)
@login_required(login_url='login_page')
def edit_wh_e_way_bill_list(request,wh_job_id):
    # wh_job_list_id=Gatein_info.objects.get(gatein_job_no=wh_job_num).id
    # job_id = Gatein_info.objects.get(gatein_job_no=wh_job_num_next).id
    url = 'gatein_update/' + str(2)
    return redirect(url)