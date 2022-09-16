
import time

from django.db import transaction
from django.shortcuts import render, redirect
from django.template.defaultfilters import join
from django.utils.datetime_safe import datetime
from pyzbar import pyzbar

from ..forms import DispatchaddForm
from django.contrib.auth.decorators import login_required
from ..models import Gatein_info,Loadingbay_Info,DamagereportInfo,Warehouse_goods_info,DamagereportImages,Dispatch_info
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
import cv2
import numpy as np
from pyzbar.pyzbar import decode

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
    # Warehousein Status Check
    try:
        warehousein_status = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list(
            'wh_check_in_out', flat=True)  # count records
        print(list(warehousein_status))
        warehousein_status_list = list(warehousein_status)
        if warehousein_status_list != []:
            if warehousein_status_list[0] == 1:
                result = all(element == (warehousein_status_list[0]) for element in (warehousein_status_list))
            else:
                result = False
        else:
            result = False
        print(result)
        if (result):
            warehousein_status = "Completed"  # get goods status
            print(warehousein_status)
        else:
            warehousein_status = "No Status"  # get goods status
            print(warehousein_status)
    except ObjectDoesNotExist:
        warehousein_status = "No Status"
    # warehousein_status = "Completed"
    dispatch_list = Dispatch_info.objects.all()
    if request.method == "GET":
        if dispatch_id == 0:
            print("I am inside Get add dispatch")
            dispatch_form = DispatchaddForm()
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
            loadingbay_list= Loadingbay_Info.objects.filter(lb_job_no=wh_job_id)
            gatein_list=Gatein_info.objects.filter(gatein_job_no=wh_job_id)
            goods_list= Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id)
            # dispatch_list = Dispatch_info.objects.filter(dispatch_job_no=wh_job_id)
            dispatch_list = Dispatch_info.objects.all()
            dispatch_num_val = Dispatch_info.objects.get(pk=dispatch_id).dispatch_num
            dispatch_goods_list= Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num_val)
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
                'dispatch_goods_list':dispatch_goods_list,
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
            messages.success(request, 'Record Updated Successfully')
        # return redirect(request.META['HTTP_REFERER'])
        return redirect('/SMS/dispatch_list')
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
    Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_storage_time=0)
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
                'dispatch_goods_list':dispatch_goods_list,
               }
    return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/dispatch_goods_list')

def qr_dispatch_decoder(request,dispatch_id):
    # Scanning QR Code from Camera Feed
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 740)
    used_code=[]
    camera=True
    dispatch_num_val = request.session.get('ses_dispatch_num_val')
    stock_num_val = Warehouse_goods_info.objects.get(pk=dispatch_id).wh_qr_rand_num
    print(stock_num_val)
    while camera==True:
        success, img = cap.read()
        for qrcode in decode(img):
            text = qrcode.data.decode('utf-8')
            t1=text.replace("{","")
            t2=t1.replace("}","")
            t3=t2.replace("'","")
            print(text)
            print(t3)
            polygon_Points = np.array([qrcode.polygon], np.int32)
            polygon_Points = polygon_Points.reshape(-1, 1, 2)
            rect_Points = qrcode.rect
            cv2.polylines(img, [polygon_Points], True, (255, 255, 0), 5)
            cv2.putText(img, text, (rect_Points[0], rect_Points[1]), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 0), 2)
            if t3 ==stock_num_val:
                cv2.destroyAllWindows()
                Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_check_in_out=2)
                Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_dispatch_num=dispatch_num_val)
                Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_checkout_time=datetime.now())
                messages.success(request,'Stock Matching.Approved for Dispatch')
                print("Stock Matching.Approved to Move")
                time.sleep(5)
                check_in_date = Warehouse_goods_info.objects.get(pk=dispatch_id).wh_checkin_time
                check_out_date = Warehouse_goods_info.objects.get(pk=dispatch_id).wh_checkout_time
                date_diff=(check_out_date - check_in_date) # Differnce between dates
                duration_in_s = date_diff.total_seconds() # Total number of seconds between dates
                storage_days = (check_out_date - check_in_date).days # In days
                storage_hours = divmod(duration_in_s, 3600)[0]  # Seconds in an hour = 3600
                storage_minutes = divmod(duration_in_s, 60)[0]  # Seconds in a minute = 60
                # date_dif_final=(storage_days[0], storage_hours[0], storage_minutes[0])
                # print(date_dif_final)
                print("Storage_Days", storage_days)
                print("Storage_Hours", storage_hours)
                # Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_storage_time=date_diff)
                return redirect(request.META['HTTP_REFERER'])
            else:
                time.sleep(5)
                cv2.destroyAllWindows()
                messages.error(request, 'Stock Not Matching')
                print("Stock Not Matching")
                return redirect(request.META['HTTP_REFERER'])

        cv2.imshow("Video", img)
        k=cv2.waitKey(1)
        if k == 27:  # wait for ESC key to exit and terminate program,
            cv2.destroyAllWindows()
            break

    return redirect(request.META['HTTP_REFERER'])

