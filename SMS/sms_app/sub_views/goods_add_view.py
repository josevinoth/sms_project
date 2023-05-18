import json
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django.contrib import messages
from ..forms import GoodsaddForm
from ..models import Warehouse_goods_info,Gatein_info,DamagereportInfo,Loadingbay_Info,LocationmasterInfo,UnitInfo
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from random import randint
# List goods
@login_required(login_url='login_page')
def goods_list(request):
    first_name = request.session.get('first_name')
    context = {'goods_list': Warehouse_goods_info.objects.all(),'first_name': first_name}
    return render(request, "asset_mgt_app/goods_list.html", context)


# Add goods
@transaction.atomic
@login_required(login_url='login_page')
def goods_add(request, goods_id=0):
    first_name = request.session.get('first_name')
    ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
    ses_gatein_no_of_pkg_nam = request.session.get('ses_gatein_no_of_pkg')
    ses_gatein_weight_nam = request.session.get('ses_gatein_weight')
    wh_job_id = ses_gatein_id_nam
    gatein_no_of_pkg_val = ses_gatein_no_of_pkg_nam
    gatein_weight_val = ses_gatein_weight_nam
    gatein_wh_job_id=Gatein_info.objects.get(gatein_job_no=wh_job_id).id
    shipper_invoice=Gatein_info.objects.get(gatein_job_no=wh_job_id).gatein_invoice
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
        if goods_status_list == []:
            damage_after_status = "Empty"
        elif all(element == None for element in (goods_status_list)):
            damage_after_status = "None"
        elif all(element == 5 for element in (goods_status_list)):
            damage_after_status = "Completed"  # get goods status
        else:
            damage_after_status = "No Status"  # get goods status
    except ObjectDoesNotExist:
        damage_after_status = "No Status"

    # Warehousein Status Check
    try:
        warehousein_stack_layer = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_stack_layer', flat=True)  # count records
        warehousein_stack_layer_list = list(warehousein_stack_layer)
        if warehousein_stack_layer_list == []:
            warehousein_status = "Empty"
        elif all(element == None for element in (warehousein_stack_layer_list)):
            warehousein_status = "None"
        elif None not in warehousein_stack_layer_list:
            warehousein_status = "Completed"  # get goods status
        else:
            warehousein_status = "No Status"  # get goods status
    except ObjectDoesNotExist:
        warehousein_status = "No Status"

    raw_data = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_goods_pieces', flat=True)
    cumsum = sum(raw_data)

    tot_package = request.session.get('ses_gatein_no_of_pkg')
    invoice_weight = request.session.get('ses_gatein_weight')

    goods_checkin_weight = \
    Warehouse_goods_info.objects.filter(wh_job_no=ses_gatein_id_nam).aggregate(Sum('wh_goods_weight'))[
            'wh_goods_weight__sum']
    goods_checkin_count = \
    Warehouse_goods_info.objects.filter(wh_job_no=ses_gatein_id_nam).aggregate(Sum('wh_goods_pieces'))[
            'wh_goods_pieces__sum']
    if goods_checkin_weight:
        goods_checkin_weight_val = round(goods_checkin_weight, 2)
        Gatein_info.objects.filter(gatein_job_no=ses_gatein_id_nam).update(gatein_actual_weight=goods_checkin_weight_val)
    else:
        goods_checkin_weight_val = 0.0
        Gatein_info.objects.filter(gatein_job_no=ses_gatein_id_nam).update(gatein_actual_weight=goods_checkin_weight_val)

    if goods_checkin_count:
        goods_checkin_count_val = round(goods_checkin_count, 2)
        Gatein_info.objects.filter(gatein_job_no=ses_gatein_id_nam).update(gatein_actual_count=goods_checkin_count_val)
    else:
        goods_checkin_count_val = 0
        Gatein_info.objects.filter(gatein_job_no=ses_gatein_id_nam).update(gatein_actual_count=goods_checkin_count_val)
        # Generate Random WH_Job number
    try:
        last_id = (Warehouse_goods_info.objects.values_list('id', flat=True)).last()
    except ObjectDoesNotExist:
        last_id = 0
    print(last_id)
    wh_stock_num = randint(10000, 99999) + last_id + 1

    if request.method == "GET":
        if goods_id == 0:
            print("I am inside Get add Goods")
            goods_form = GoodsaddForm()
            context = {
                'first_name': first_name,
                'goods_form': goods_form,
                'wh_job_id': wh_job_id,
                'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
                'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
                'loadingbay_list': Loadingbay_Info.objects.filter(lb_job_no=wh_job_id),
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
                'gatein_status': gatein_status,
                'loadingbay_status': loadingbay_status,
                'damage_before_status': damage_before_status,
                'damage_after_status':damage_after_status,
                'warehousein_status': warehousein_status,
                'gatein_no_of_pkg_val': gatein_no_of_pkg_val,
                'gatein_weight_val': gatein_weight_val,
                'goods_checkin_weight': goods_checkin_weight_val,
                'goods_checkin_count': goods_checkin_count_val,
                'gatein_wh_job_id': gatein_wh_job_id,
                'shipper_invoice': shipper_invoice,
                'wh_stock_num':wh_stock_num
            }
        else:
            print("I am inside get edit Goods")
            goodsinfo = Warehouse_goods_info.objects.get(pk=goods_id)
            goods_form = GoodsaddForm(instance=goodsinfo)
            context = {
                'first_name': first_name,
                'goods_form': goods_form,
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
                'gatein_no_of_pkg_val': gatein_no_of_pkg_val,
                'gatein_weight_val': gatein_weight_val,
                'goods_checkin_weight': goods_checkin_weight,
                'goods_checkin_count': goods_checkin_count_val,
                'gatein_wh_job_id': gatein_wh_job_id,
                'shipper_invoice': shipper_invoice,
            }
        return render(request, "asset_mgt_app/goods_add.html", context)
    else:
        if goods_id == 0:
            print("I am inside post add Goods")
            goods_form = GoodsaddForm(request.POST)
        else:
            print("I am inside post edit Goods")
            goodsinfo = Warehouse_goods_info.objects.get(pk=goods_id)
            goods_form = GoodsaddForm(request.POST, instance=goodsinfo)
        if goods_form.is_valid():
            print("Form is Valid")
            goods_form.save()
            raw_data = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_goods_pieces',flat=True)
            weigth_data = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_goods_weight',flat=True)
            cumsum = sum(raw_data)
            weight_cumsum = sum(weigth_data)
            if cumsum > tot_package:
                messages.error(request, 'Record Not Updated.Number of Pacakges Exceeds Invoice Count')
                # transaction.set_rollback(True)

            elif weight_cumsum > invoice_weight:
                messages.error(request, 'Record Not Updated.Goods Check-In weight Exceeds Invoice Weight')
                # transaction.set_rollback(True)

            else:
                messages.success(request, 'Record Updated Successfully')
        else:
            print("Form is not Valid")
            messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
        return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/stock_list')

# Delete goods
@login_required(login_url='login_page')
def goods_delete(request, goods_id):
    goodsinfo = Warehouse_goods_info.objects.get(pk=goods_id)
    goodsinfo.delete()
    return redirect('/SMS/goods_insert')


