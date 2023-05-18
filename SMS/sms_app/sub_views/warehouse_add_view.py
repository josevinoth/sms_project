import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from ..forms import GoodsaddForm,WarehoseinaddForm,WarehoseoutaddForm
from ..models import Location_info,User_extInfo,Warehouse_goods_info,Gatein_info,DamagereportInfo,Loadingbay_Info,LocationmasterInfo,UnitInfo,BayInfo
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

# Add goods
@login_required(login_url='login_page')
def warehousein_add(request, warehousein_id=0):
    first_name = request.session.get('first_name')
    ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
    wh_job_id = ses_gatein_id_nam
    # get branch name & ID
    user_id = request.session.get('ses_userID')
    user_branch = User_extInfo.objects.get(user_id=user_id).emp_branch
    user_branch_id = Location_info.objects.get(loc_name=user_branch).id
    # get emp role
    user_role=User_extInfo.objects.get(user_id=user_id).emp_role

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
    if request.method == "GET":
        if warehousein_id == 0:
            print("I am inside Get add warehousein")
            warehousein_form = WarehoseinaddForm()
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
                'user_role':user_role,
                'user_branch_id':user_branch_id,
                'user_branch':user_branch,
            }
        else:
            print("I am inside get edit warehousein")
            ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
            wh_job_id = ses_gatein_id_nam
            goodsinfo = Warehouse_goods_info.objects.get(pk=warehousein_id)
            warehousein_form = WarehoseinaddForm(instance=goodsinfo)
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
                'user_role': user_role,
                'user_branch_id': user_branch_id,
                'user_branch': user_branch,
            }
        return render(request, "asset_mgt_app/warehousein_add.html", context)
    else:
        if warehousein_id == 0:
            print("I am inside post add warehousein")
            warehousein_form = WarehoseinaddForm(request.POST)
            available_area_val = request.POST.get('wh_available_area')
            available_volume_val = request.POST.get('wh_available_volume')
            stack_layer_val = request.POST.get('wh_stack_layer')
            # Warehouse_goods_info.objects.filter(pk=warehousein_id).update(wh_checkin_time=timezone.now())
        else:
            print("I am inside post edit warehousein")
            warehouseininfo = Warehouse_goods_info.objects.get(pk=warehousein_id)
            warehousein_form = WarehoseinaddForm(request.POST, instance=warehouseininfo)
            available_area_val = request.POST.get('wh_available_area')
            available_volume_val = request.POST.get('wh_available_volume')
            required_area_val = request.POST.get('wh_goods_area')
            required_volume_val = request.POST.get('wh_goods_volume_weight')
            stack_layer_val = request.POST.get('wh_stack_layer')
            # Warehouse_goods_info.objects.filter(pk=warehousein_id).update(wh_checkin_time=timezone.now())
        if warehousein_form.is_valid():
            print("warehousein_form is Valid")
            if (float(available_area_val) < float(required_area_val)):
                if (float(stack_layer_val)==1):
                    messages.error(request, 'Area Not Sufficient for Storage. Try to Stack in next layer!')
                else:
                    messages.success(request, 'Goods Stacked above Ground Level!')
                    if (float(available_volume_val) < float(required_volume_val)):
                        messages.error(request, 'Volume Not Sufficient for Storage!')
                    else:
                        warehousein_form.save()
            else:
                if (float(available_volume_val) < float(required_volume_val)):
                    messages.error(request, 'Volume Not Sufficient for Storage!')
                else:
                    messages.success(request, 'Goods Stored!')
                    warehousein_form.save()
            # Update Invoice weight, qty,value
            # wh_invoice_list = Warehouse_goods_info.objects.all().values_list('wh_job_no',flat=True).distinct()
            # for wh_job_id in wh_invoice_list:
            invoice_id = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('id',flat=True)
            stock_id = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_qr_rand_num',flat=True)
            job_num = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_job_no',flat=True)
            invoice_weight = Gatein_info.objects.get(gatein_job_no=wh_job_id).gatein_weight
            invoice_package = Gatein_info.objects.get(gatein_job_no=wh_job_id).gatein_no_of_pkg
            invoice_value = Loadingbay_Info.objects.get(lb_job_no=wh_job_id).lb_stock_invoice_value
            invoice_amount_inr = Loadingbay_Info.objects.get(lb_job_no=wh_job_id).lb_stock_amount_in
            gross_wt = 0
            total_qty = 0
            for j in stock_id:
                gross_wt=gross_wt+(Warehouse_goods_info.objects.get(wh_qr_rand_num=j).wh_goods_weight)
                total_qty=total_qty+(Warehouse_goods_info.objects.get(wh_qr_rand_num=j).wh_goods_pieces)

            for i in range(0,len(invoice_id)):
                print(i)
                print(job_num[i])
                if i==0:
                    Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_invoice_amount_inr=invoice_amount_inr)
                    Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_invoice_weight_unit=invoice_weight)
                    Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_invoice_value=invoice_value)
                    Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_invoice_qty=invoice_package)
                    Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_gross_weight=gross_wt)
                    Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_total_qty=total_qty)
                else:
                    Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_invoice_amount_inr=0.0)
                    Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_invoice_weight_unit=0.0)
                    Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_invoice_value=0.0)
                    Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_invoice_qty=0)
                    Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_gross_weight=0.0)
                    Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_total_qty=0)

            # update area and volume
            Branch_val = request.POST.get('wh_branch')
            Unit_val = request.POST.get('wh_unit')
            Bay_val = request.POST.get('wh_bay')
            wh_goods_list = Warehouse_goods_info.objects.filter(wh_branch_id=Branch_val, wh_unit_id=Unit_val,
                                                                wh_bay_id=Bay_val)
            stack_layer = wh_goods_list.values('wh_stack_layer_id')
            volume = wh_goods_list.values('wh_goods_volume_weight')
            check_in_out_list = wh_goods_list.values('wh_check_in_out')
            area = wh_goods_list.values('wh_goods_area')
            area_final = 0
            volume_final = 0
            for j in range(len(wh_goods_list)):
                if check_in_out_list[j]['wh_check_in_out']==1:
                    volume_final = volume_final + volume[j]['wh_goods_volume_weight']
                    LocationmasterInfo.objects.filter(lm_wh_location=Branch_val, lm_wh_unit=Unit_val,
                                                      lm_areaside=Bay_val).update(lm_volume_occupied=volume_final)
                    if stack_layer[j]['wh_stack_layer_id'] == 1:
                        area_final = area_final + area[j]['wh_goods_area']
                        LocationmasterInfo.objects.filter(lm_wh_location=Branch_val, lm_wh_unit=Unit_val,lm_areaside=Bay_val).update(lm_area_occupied=area_final)
                    else:
                        print("No Area")
                # else:
                #     print('check_in_out_list', check_in_out_list[j]['wh_check_in_out'])

            total_area_data=LocationmasterInfo.objects.get(lm_wh_location=Branch_val, lm_wh_unit=Unit_val,lm_areaside=Bay_val).lm_size
            total_volume_data=LocationmasterInfo.objects.get(lm_wh_location=Branch_val, lm_wh_unit=Unit_val,lm_areaside=Bay_val).lm_total_volume
            available_area_final =round((total_area_data-area_final),3)
            available_volume_final =round((total_volume_data-volume_final),3)
            LocationmasterInfo.objects.filter(lm_wh_location=Branch_val, lm_wh_unit=Unit_val,lm_areaside=Bay_val).update(lm_available_area=available_area_final)
            LocationmasterInfo.objects.filter(lm_wh_location=Branch_val, lm_wh_unit=Unit_val,lm_areaside=Bay_val).update(lm_available_volume=available_volume_final)
        else:
            print("warehousein_form is not Valid")
            messages.error(request, 'Record not Updated!')
        return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/stock_list')

@login_required(login_url='login_page')
def warehouseout_add(request, warehouseout_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        print("I am inside get edit warehouseout")
        ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
        warehouseoutinfo = Warehouse_goods_info.objects.get(pk=warehouseout_id)
        warehouseout_form = WarehoseoutaddForm(instance=warehouseoutinfo)
        context = {
                      'first_name': first_name,
                      'warehouseout_form': warehouseout_form,
        }
        return render(request, "asset_mgt_app/warehouseout_add.html", context)
    else:
        print("I am inside post edit warehouseout")
        print('warehouseout_id',warehouseout_id)
        warehouseoutinfo = Warehouse_goods_info.objects.get(pk=warehouseout_id)
        warehouseout_form = WarehoseoutaddForm(request.POST, instance=warehouseoutinfo)
    if warehouseout_form.is_valid():
        warehouseout_form.save()
        print("warehouseoutinfo is Valid")
        dispatch_num_val = request.session.get('ses_dispatch_num_val')
        print('dispatch_num_val', dispatch_num_val)
        Warehouse_goods_info.objects.filter(pk=warehouseout_id).update(wh_check_in_out=2)
        Warehouse_goods_info.objects.filter(pk=warehouseout_id).update(wh_dispatch_num=dispatch_num_val)
        check_in_date = Warehouse_goods_info.objects.get(pk=warehouseout_id).wh_checkin_time
        check_out_date = Warehouse_goods_info.objects.get(pk=warehouseout_id).wh_checkout_time
        date_diff = (check_out_date - check_in_date)  # Differnce between dates
        date_diff_days = date_diff.days
        duration_in_s = date_diff.total_seconds()  # Total number of seconds between dates
        storage_hours = divmod(duration_in_s, 3600)[0]  # Seconds in an hour = 3600
        # storage_days = (check_out_date - check_in_date).days  # In days
        storage_days = float(round(storage_hours / 24, 2))  # In days
        Warehouse_goods_info.objects.filter(pk=warehouseout_id).update(wh_storage_time=date_diff_days)
    else:
        print("warehouseoutinfo is Not-Valid")
    return redirect('/SMS/warehouseout_cancel')

@login_required(login_url='login_page')
def warehouseout_cancel(request):
    dispatch_num_val = request.session.get('ses_dispatch_num_val')
    first_name = request.session.get('first_name')
    dispatch_master_list = Warehouse_goods_info.objects.filter(wh_check_in_out=1)
    goods_list = Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num_val)
    context = {'goods_list': goods_list,
               'first_name': first_name,
               'dispatch_master_list': dispatch_master_list,
               'dispatch_num_val': dispatch_num_val,
               }
    return render(request, "asset_mgt_app/dispatch_goods_list_woh.html", context)

# Search Space Availability
@login_required(login_url='login_page')
def wh_space_availability(request):
    wh_branch_val = request.GET.get('wh_branch')
    wh_unit_val = request.GET.get('wh_unit')
    wh_bay_val = request.GET.get('wh_bay')
    context = {
        'wh_branch_val': wh_branch_val,
    }
    return render(request, "asset_mgt_app/goods_add.html", context)

# Load Units
@login_required(login_url='login_page')
def load_units_origin(request):
    # Fetch unit
    unit_list=[]
    unit_id=[]
    unit_name_list = []
    wh_branch_id = request.GET.get('branchId')
    # Fetch Unit Details
    units = UnitInfo.objects.filter(ui_branch_name=wh_branch_id).values('unit_name').distinct()
    units_id = UnitInfo.objects.filter(ui_branch_name=wh_branch_id).values('id').distinct()
    units_count=units.count()
    for i in range(units_count):
        unit_list.append(units[i]['unit_name'])
        unit_id.append(units_id[i]['id'])
    data = {
        'unit_id':unit_id,
        'unit_name_list': unit_list,
    }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))

@login_required(login_url='login_page')
def load_units(request):
    # Fetch unit
    unit_list=[]
    unit_name=[]
    unit_name_list = []
    wh_branch_id = request.GET.get('branchId')
    # Fetch Unit Details
    units = LocationmasterInfo.objects.filter(lm_wh_location=wh_branch_id).values('lm_wh_unit').distinct()
    units_count=units.count()
    for i in range(units_count):
        unit_list.append(units[i]['lm_wh_unit'])
    for j in unit_list:
        unit_name=UnitInfo.objects.filter(id=j).values('unit_name')
        unit_name_list.append(unit_name[0]['unit_name'])
    data = {
        'unit_id':unit_list,
        'unit_name_list': unit_name_list,
    }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))

# Load Bays
@login_required(login_url='login_page')
def load_bays_origin(request):
    # Fetch Bays
    bay_list = []
    bay_id= []
    bay_name_list = []
    wh_branch_id = request.GET.get('branchId')
    untid_id = request.GET.get('unitId')
    # Fetch Bay details
    bays = BayInfo.objects.filter(bay_branch_name=wh_branch_id,Bay_unit_name=untid_id).values('bay_bayname').distinct()
    bays_id = BayInfo.objects.filter(bay_branch_name=wh_branch_id,Bay_unit_name=untid_id).values('id').distinct()
    bays_count = bays.count()
    for k in range(bays_count):
        print("k",k)
        bay_list.append(bays[k]['bay_bayname'])
        bay_id.append(bays_id[k]['id'])
    # for m in bay_list:
    #     print("m",m)
    #     bay_name=BayInfo.objects.filter(id=m).values('bay_bayname')
    #     bay_name_list.append(bay_name[0]['bay_bayname'])
    #     print(bay_name)
    # print(bay_name_list)
    # print(len(list(bay_name_list)))
    data = {
        'bay_id':bay_id,
        'bay_name_list':bay_list,
    }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))
@login_required(login_url='login_page')
def load_bays(request):
    # Fetch Bays
    bay_list = []
    bay_name = []
    bay_name_list = []
    wh_branch_id = request.GET.get('branchId')
    untid_id = request.GET.get('unitId')
    # Fetch Bay details
    bays = LocationmasterInfo.objects.filter(lm_wh_location=wh_branch_id,lm_wh_unit=untid_id).values('lm_areaside').distinct()
    bays_count = bays.count()
    for k in range(bays_count):
        bay_list.append(bays[k]['lm_areaside'])
    for m in bay_list:
        bay_name=BayInfo.objects.filter(id=m).values('bay_bayname')
        bay_name_list.append(bay_name[0]['bay_bayname'])
    data = {
        'bay_id':bay_list,
        'bay_name_list':bay_name_list,
    }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))

# Load Bays
@login_required(login_url='login_page')
def load_area_volume(request):
    # Fetch Area & Volume
    wh_branch_id = request.GET.get('branchId')
    untid_id = request.GET.get('unitId')
    bayId = request.GET.get('bayId')
    req_area_val = float(request.GET.get('req_area_val'))
    req_volume_val = float(request.GET.get('req_volume_val'))
    # Fetch Bay details
    lm_available_area_val = LocationmasterInfo.objects.filter(lm_wh_location=wh_branch_id,lm_wh_unit=untid_id,lm_areaside=bayId).values('lm_available_area').distinct()
    lm_available_volume_val = LocationmasterInfo.objects.filter(lm_wh_location=wh_branch_id,lm_wh_unit=untid_id,lm_areaside=bayId).values('lm_available_volume').distinct()
    area_count = lm_available_area_val.count()
    for k in range(area_count):
        available_area_final=lm_available_area_val[k]['lm_available_area']
        available_volume_final=lm_available_volume_val[k]['lm_available_volume']
        data = {
            'available_area_final':available_area_final,
            'available_volume_final':available_volume_final,
        }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))