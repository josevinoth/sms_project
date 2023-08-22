from django.contrib.auth.decorators import login_required
from datetime import date, datetime

from ..forms import WarehoseinaddForm
from ..models import Check_in_out,Dispatch_info,Warehouse_goods_info,Gatein_info,DamagereportInfo,Loadingbay_Info,LocationmasterInfo,UnitInfo
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

# Add goods
@login_required(login_url='login_page')
def storage_list(request):
    first_name = request.session.get('first_name')
    print("I am inside Get add warehousein")
    warehousein_form = WarehoseinaddForm()
    ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
    wh_job_id = ses_gatein_id_nam
    # Gate In Status Check
    try:
        gatein_status = Gatein_info.objects.get(gatein_job_no=wh_job_id).gatein_status  # fetch gatein status
    except ObjectDoesNotExist:
        gatein_status = "No Status"
    # Loading Bay Status Check
    try:
        loadingbay_status = Loadingbay_Info.objects.get(
            lb_job_no=wh_job_id).lb_status  # fetch loadingbay status
    except ObjectDoesNotExist:
        loadingbay_status = "No Status"
    # Damage/Before Status Check
    try:
        damage_before_status = DamagereportInfo.objects.get(
            dam_wh_job_num=wh_job_id).dam_status  # fetch damage report status
    except ObjectDoesNotExist:
        damage_before_status = "No Status"
    # Damage/After Status Check
    try:
        goods_status = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_goods_status',
                                                                                                flat=True)  # count records
        goods_status_list = list(goods_status)
        if goods_status_list != []:
            if goods_status_list[0] == 5:
                result = all(element == (goods_status_list[0]) for element in (goods_status_list))
            else:
                result = False
        else:
            result = False
        if (result):
            damage_after_status = "Completed"  # get goods status
        else:
            damage_after_status = "No Status"  # get goods status
    except ObjectDoesNotExist:
        damage_after_status = "No Status"
    # Warehousein Status Check
    try:
        warehousein_status = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list(
            'wh_check_in_out', flat=True)  # count records
        warehousein_status_list = list(warehousein_status)
        if warehousein_status_list != []:
            if warehousein_status_list[0] == 9:
                result = all(element == (warehousein_status_list[0]) for element in (warehousein_status_list))
            else:
                result = False
        else:
            result = False
        if (result):
            warehousein_status = "Completed"  # get goods status
        else:
            warehousein_status = "No Status"  # get goods status
    except ObjectDoesNotExist:
        warehousein_status = "No Status"

    # calculate storage days
    stocks=list(Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_qr_rand_num',flat=True))
    for i in stocks:
        print(i)
        goods_status=Warehouse_goods_info.objects.get(wh_qr_rand_num=i).wh_check_in_out
        goods_status_id=Check_in_out.objects.get(check_in_out_name=goods_status).id
        if goods_status_id==1:
            check_in_date = datetime.date(Warehouse_goods_info.objects.get(wh_qr_rand_num=i).wh_checkin_time)
            current_date = date.today()
            date_diff = (current_date - check_in_date)  # Differnce between dates
            date_diff_days = date_diff.days
            Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_storage_time=date_diff_days)
        elif goods_status_id==2:
            check_in_date = datetime.date(Warehouse_goods_info.objects.get(wh_qr_rand_num=i).wh_checkin_time)
            check_out_date = datetime.date(Warehouse_goods_info.objects.get(wh_qr_rand_num=i).wh_checkout_time)
            date_diff = (check_out_date - check_in_date)  # Differnce between dates
            date_diff_days = date_diff.days
            Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_storage_time=date_diff_days)
    context = {
        'first_name': first_name,
        'warehousein_form': warehousein_form,
        'wh_job_id': wh_job_id,
        'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
        'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
        'loadingbay_list': Loadingbay_Info.objects.filter(lb_job_no=wh_job_id),
        'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
        'dispatch_list': Dispatch_info.objects.all(),
        'gatein_status': gatein_status,
        'loadingbay_status': loadingbay_status,
        'damage_before_status': damage_before_status,
        'damage_after_status': damage_after_status,
        'warehousein_status': warehousein_status,
        'locationmaster_list': LocationmasterInfo.objects.all(),
        }
    return render(request, "asset_mgt_app/storage_add.html", context)
