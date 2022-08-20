from django.db import transaction
from django.shortcuts import render, redirect
from ..forms import DispatchaddForm
from django.contrib.auth.decorators import login_required
from ..models import Gatein_info,Loadingbay_Info,DamagereportInfo,Warehouse_goods_info,DamagereportImages,Dispatch_info
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

# Add Dispatch Job
@transaction.atomic
@login_required(login_url='login_page')
def dispatch_add(request, dispatch_id=0):
    first_name = request.session.get('first_name')
    ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
    tot_package = request.POST.get('gatein_no_of_pkg')
    print(ses_gatein_id_nam)
    wh_job_id = ses_gatein_id_nam
    # dispatch_list = Dispatch_info.objects.filter(dispatch_job_no=wh_job_id)
    dispatch_list = Dispatch_info.objects.all()
    if request.method == "GET":
        if dispatch_id == 0:
            print("I am inside Get add dispatch")
            dispatch_form = DispatchaddForm()
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
            #     warehousein_status = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list(
            #         'wh_check_in_out', flat=True)  # count records
            #     print(list(warehousein_status))
            #     warehousein_status_list = list(warehousein_status)
            #     if warehousein_status_list != []:
            #         if warehousein_status_list[0] == 1:
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
                'dispatch_form': dispatch_form,
                'loadingbay_list': Loadingbay_Info.objects.filter(lb_job_no=wh_job_id),
                'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
                'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
                'wh_job_id': wh_job_id,
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
                'dispatch_list':dispatch_list,
                'gatein_status': gatein_status,
                'loadingbay_status': loadingbay_status,
                'damage_before_status': damage_before_status,
                'damage_after_status': damage_after_status,
                'warehousein_status': warehousein_status,
            }
        else:
            print("I am inside get edit Dispatch")
            dispatch_info = Dispatch_info.objects.get(pk=dispatch_id)
            dispatch_form = DispatchaddForm(instance=dispatch_info)
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
            # # Warehousein Status Check
            # try:
            #     warehousein_status = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list(
            #         'wh_check_in_out', flat=True)  # count records
            #     print(list(warehousein_status))
            #     warehousein_status_list = list(warehousein_status)
            #     if warehousein_status_list != []:
            #         if warehousein_status_list[0] == 1:
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
            loadingbay_list= Loadingbay_Info.objects.filter(lb_job_no=wh_job_id)
            gatein_list=Gatein_info.objects.filter(gatein_job_no=wh_job_id)
            goods_list= Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id)
            # dispatch_list = Dispatch_info.objects.filter(dispatch_job_no=wh_job_id)
            dispatch_list = Dispatch_info.objects.all()
            context = {
                'dispatch_form': dispatch_form,
                'first_name': first_name,
                'loadingbay_list': loadingbay_list,
                'gatein_list':gatein_list,
                'goods_list': goods_list,
                'dispatch_list':dispatch_list,
                'gatein_status':gatein_status,
                'loadingbay_status':loadingbay_status,
                'damage_before_status':damage_before_status,
                'damage_after_status': damage_after_status,
                'warehousein_status': warehousein_status,
            }
        return render(request, "asset_mgt_app/dispatch_add.html", context)
    else:
        if dispatch_id == 0:
            print("I am inside post add dispatch")
            dispatch_form = DispatchaddForm(request.POST)
        else:
            print("I am inside post edit dispatch")
            dispatch_info = Dispatch_info.objects.get(pk=dispatch_id)
            dispatch_form = DispatchaddForm(request.POST, instance=dispatch_info)
        if dispatch_form.is_valid():
            dispatch_form.save()
            messages.info(request, 'Record Updated Successfully')
        return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/gatein_list')
# List Dispatch Job
@login_required(login_url='login_page')
def dispatch_list(request):
    first_name = request.session.get('first_name')
    context = {
                'Dispatch_list' : Dispatch_info.objects.all(),
                'first_name': first_name,}
    return render(request,"asset_mgt_app/dispatch_list.html",context)

#Delete Dispatch Job
@login_required(login_url='login_page')
def dispatch_delete(request,dispatch_id):
    # wh_job_id=Dispatch_info.objects.get(pk=dispatch_id).dispatch_job_no
    # wh_job_id = request.session.get('ses_dispatch_id_nam')
    dispatch_del = Dispatch_info.objects.get(pk=dispatch_id)
    dispatch_del.delete()
    return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/dispatch_list')

@login_required(login_url='login_page')
def dispatch_goods_list(request,dispatch_id):
    # wh_job_id = request.session.get('ses_gatein_id_nam')
    first_name = request.session.get('first_name')
    dispatch_num_val = Dispatch_info.objects.get(pk=dispatch_id).dispatch_num
    request.session['ses_dispatch_num_val'] = dispatch_num_val
    # # dispatch_num_val = Dispatch_info.objects.get(pk=dispatch_id).dispatch_num
    print(dispatch_num_val)
    dispatch_master_list=Warehouse_goods_info.objects.filter(wh_check_in_out=1)
    goods_list=Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num_val)
    context = {'goods_list' : goods_list,
               'first_name': first_name,
               'dispatch_master_list':dispatch_master_list,
               'dispatch_num_val':dispatch_num_val,
               }
    return render(request,"asset_mgt_app/dispatch_goods_list_woh.html",context)

@login_required(login_url='login_page')
def dispatch_remove_goods(request,dispatch_id):
    dispatch_num_update = Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_dispatch_num="None")
    dispatch_goods_checkin = Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_check_in_out=1)
    print(dispatch_goods_checkin)
    wh_dispatch_num=request.session.get('ses_dispatch_num_val')
    print(wh_dispatch_num)
    # dispatch_dipatch_num_checkin = Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_check_in_out=1)
    first_name = request.session.get('first_name')
    context = {
               'first_name': first_name,
               }
    return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/dispatch_goods_list')


@login_required(login_url='login_page')
def dispatch_add_goods(request,dispatch_id):
    dispatch_num_val=request.session.get('ses_dispatch_num_val')
    dispatch_goods_checkout = Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_check_in_out=2)
    dispatch_num_update = Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_dispatch_num=dispatch_num_val)
    print(dispatch_goods_checkout)
    first_name = request.session.get('first_name')
    context = {
               'first_name': first_name,
               }
    return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/dispatch_goods_list')



