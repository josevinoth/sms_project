import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse

from ..forms import GoodsaddForm,WarehoseinaddForm
from ..models import Warehouse_goods_info,Gatein_info,DamagereportInfo,Loadingbay_Info,LocationmasterInfo,UnitInfo
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

# # List goods
# @login_required(login_url='login_page')
# def goods_list(request):
#     first_name = request.session.get('first_name')
#     context = {'goods_list': Warehouse_goods_info.objects.all(),'first_name': first_name}
#     return render(request, "asset_mgt_app/goods_list.html", context)


# Add goods
@login_required(login_url='login_page')
def warehousein_add(request, warehousein_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if warehousein_id == 0:
            print("I am inside Get add warehousein")
            warehousein_form = WarehoseinaddForm()
            ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
            print(ses_gatein_id_nam)
            wh_job_id = ses_gatein_id_nam
            # Gate In Status Check
            try:
                gatein_status = Gatein_info.objects.get(gatein_job_no=wh_job_id).gatein_status  # fetch gatein status
            except ObjectDoesNotExist:
                gatein_status = "No Status"
            # Loading Bay Status Check
            try:
                loadingbay_status = Loadingbay_Info.objects.get(lb_job_no=wh_job_id).lb_status  # fetch loadingbay status
            except ObjectDoesNotExist:
                loadingbay_status = "No Status"
            # Damage/Before Status Check
            try:
                damage_before_status = DamagereportInfo.objects.get(dam_wh_job_num=wh_job_id).dam_status  # fetch damage report status
            except ObjectDoesNotExist:
                damage_before_status = "No Status"
            # Damage/After Status Check
            try:
                goods_status = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_goods_status',flat=True)  # count records
                print(list(goods_status))
                goods_status_list = list(goods_status)
                if goods_status_list != []:
                    if goods_status_list[0] == 5:
                        result = all(element == (goods_status_list[0]) for element in (goods_status_list))
                    else:
                        result = False
                else:
                    result = False
                print(result)
                if (result):
                    damage_after_status = "Completed"  # get goods status
                    print(damage_after_status)
                else:
                    damage_after_status = "No Status"  # get goods status
                    print(damage_after_status)
            except ObjectDoesNotExist:
                damage_after_status = "No Status"
            # Warehousein Status Check
            # try:
            #     warehousein_status = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_check_in_out', flat=True)  # count records
            #     print(list(warehousein_status))
            #     warehousein_status_list = list(warehousein_status)
            #     if warehousein_status_list != []:
            #         if warehousein_status_list[0] != 0:
            #             print("Inside If loop")
            #             result = all(element == (warehousein_status_list[0]) for element in (warehousein_status_list))
            #             print("Result is",result)
            #         else:
            #             print("Inside Else loop")
            #             result = False
            #     else:
            #         result = False
            #     print(result)
            #     if (result):
            #         warehousein_status = "Completed"  # get goods status
            #         print(warehousein_status)
            #     else:
            #         warehousein_status = "No Status"  # get goods status
            #         print(warehousein_status)
            # except ObjectDoesNotExist:
            #     warehousein_status = "No Status"
            warehousein_status = "Completed"
            context = {
                'first_name': first_name,
                'warehousein_form': warehousein_form,
                'wh_job_id': wh_job_id,
                'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
                'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
                'loadingbay_list': Loadingbay_Info.objects.filter(lb_job_no=wh_job_id),
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
                'gatein_status': gatein_status,
                'loadingbay_status': loadingbay_status,
                'damage_before_status': damage_before_status,
                'damage_after_status': damage_after_status,
                'warehousein_status':warehousein_status,
            }
        else:
            print("I am inside get edit warehousein")
            ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
            print(ses_gatein_id_nam)
            wh_job_id = ses_gatein_id_nam
            goodsinfo = Warehouse_goods_info.objects.get(pk=warehousein_id)
            warehousein_form = WarehoseinaddForm(instance=goodsinfo)
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
                print(list(goods_status))
                goods_status_list = list(goods_status)
                if goods_status_list != []:
                    if goods_status_list[0] == 5:
                        result = all(element == (goods_status_list[0]) for element in (goods_status_list))
                    else:
                        result = False
                else:
                    result = False
                print(result)
                if (result):
                    damage_after_status = "Completed"  # get goods status
                    print(damage_after_status)
                else:
                    damage_after_status = "No Status"  # get goods status
                    print(damage_after_status)
            except ObjectDoesNotExist:
                damage_after_status = "No Status"
            # # Warehousein Status Check
            # try:
            #     warehousein_status = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_check_in_out', flat=True)  # count records
            #     print(list(warehousein_status))
            #     warehousein_status_list = list(warehousein_status)
            #     if warehousein_status_list != []:
            #         if warehousein_status_list[0] == 9:
            #             result = all(element == (warehousein_status_list[0]) for element in (warehousein_status_list))
            #         else:
            #             result = False
            #     else:
            #         result = False
            #     print(result)
            #     if (result):
            #         warehousein_status = "Completed"  # get goods status
            #         print(warehousein_status)
            #     else:
            #         warehousein_status = "No Status"  # get goods status
            #         print(warehousein_status)
            # except ObjectDoesNotExist:
            #     warehousein_status = "No Status"
            warehousein_status = "Completed"
            context = {
                'first_name': first_name,
                'warehousein_form': warehousein_form,
                'wh_job_id': wh_job_id,
                'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
                'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
                'loadingbay_list': Loadingbay_Info.objects.filter(lb_job_no=wh_job_id),
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
                'gatein_status': gatein_status,
                'loadingbay_status': loadingbay_status,
                'damage_before_status': damage_before_status,
                'damage_after_status': damage_after_status,
                'warehousein_status': warehousein_status,
            }
        return render(request, "asset_mgt_app/warehousein_add.html", context)
    else:
        if warehousein_id == 0:
            print("I am inside post add warehousein")
            warehousein_form = WarehoseinaddForm(request.POST)
        else:
            print("I am inside post edit warehousein")
            ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
            print(ses_gatein_id_nam)
            wh_job_id = ses_gatein_id_nam
            warehouseininfo = Warehouse_goods_info.objects.get(pk=warehousein_id)
            warehousein_form = WarehoseinaddForm(request.POST, instance=warehouseininfo)
        if warehousein_form.is_valid():
            warehousein_form.save()
        return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/stock_list')


# # Delete goods
# @login_required(login_url='login_page')
# def goods_delete(request, goods_id):
#     goodsinfo = Warehouse_goods_info.objects.get(pk=goods_id)
#     goodsinfo.delete()
#     return redirect('/SMS/goods_insert')

# Search Space Availability
@login_required(login_url='login_page')
def wh_space_availability(request):
    wh_branch_val = request.GET.get('wh_branch')
    wh_unit_val = request.GET.get('wh_unit')
    wh_bay_val = request.GET.get('wh_bay')
    print("wh_branch_val",wh_branch_val)
    print("wh_unit_val", wh_unit_val)
    print("wh_bay_val", wh_bay_val)
    context = {
        'wh_branch_val': wh_branch_val,
    }
    return render(request, "asset_mgt_app/goods_add.html", context)

# Load Units
@login_required(login_url='login_page')
def load_units(request):
    unit_list=[]
    unit_name=[]
    unit_name_list = []
    wh_branch_id = request.GET.get('branchId')
    print("Branch_ID",wh_branch_id)
    units = LocationmasterInfo.objects.filter(lm_wh_location=wh_branch_id).values('lm_wh_unit')
    print("Units",units)
    units_count=units.count()
    for i in range(units_count):
        print("i",i)
        unit_list.append(units[i]['lm_wh_unit'])
    print("Unit_list",unit_list)
    print("Length Unit_list",len(unit_list))
    for j in unit_list:
        print("j",j)
        unit_name=UnitInfo.objects.filter(id=j).values('unit_name')
        unit_name_list.append(unit_name[0]['unit_name'])
        print(unit_name)
    print(unit_name_list)
    print(len(list(unit_name_list)))
    data = {
        'unit_name_list': list(unit_name_list)
    }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))
