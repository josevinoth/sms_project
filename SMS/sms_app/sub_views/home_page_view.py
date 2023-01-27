from django.contrib.auth.decorators import login_required
from ..forms import AssetinfoaddForm
from ..models import Warehouse_goods_info,AssetInfo,Vendor_info,Location_info,Product_info,User,Service_Info
from django.shortcuts import render, redirect
from django.db.models import Sum

@login_required(login_url='login_page')
def home_page(request):
    first_name=request.session.get('first_name')
    ses_username = request.session.get('ses_username', request.POST.get('username'))
    checked_out_goods_list=list(Warehouse_goods_info.objects.filter(wh_voucher_num=None,wh_check_in_out=2).values_list('wh_job_no',flat=True).distinct())
    checked_out_goods=len(checked_out_goods_list)
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
               'checked_out_goods': checked_out_goods,
               }
    return render(request, 'asset_mgt_app/home_page.html', context)
