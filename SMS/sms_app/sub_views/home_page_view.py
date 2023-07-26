from django.contrib.auth.decorators import login_required
from ..forms import AssetinfoaddForm
from ..models import TrbusinesstypeInfo,User_extInfo,Warehouse_goods_info,AssetInfo,Vendor_info,Location_info,Product_info,User,Service_Info
from django.shortcuts import render, redirect
from django.db.models import Sum

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
               }
    return render(request, 'asset_mgt_app/home_page.html', context)
