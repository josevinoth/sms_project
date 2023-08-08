from random import randint
import time
from datetime import datetime
from django.db import transaction
from django.shortcuts import render, redirect
from ..forms import DispatchaddForm
from django.contrib.auth.decorators import login_required
from ..models import StatusList,Gatein_info,Warehouse_goods_info,Dispatch_info
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
    wh_job_id = ses_gatein_id_nam
    user_id = request.session.get('ses_userID')
    dispatch_list = Dispatch_info.objects.all()
    # Generate Random Dispatch number
    last_id = (Dispatch_info.objects.values_list('id', flat=True)).last()
    if last_id == None:
        last_id = 0
    ran=randint(10000, 99999)
    dispatch_num =  ran + last_id + 1
    if request.method == "GET":
        if dispatch_id == 0:
            print("I am inside Get add dispatch")
            dispatch_form = DispatchaddForm()
            context = {
                'first_name': first_name,
                'dispatch_form': dispatch_form,
                'wh_job_id': wh_job_id,
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
                'dispatch_list':dispatch_list,
                'user_id': user_id,
                'dispatch_num': dispatch_num,
            }
        else:
            print("I am inside get edit Dispatch")
            dispatch_info = Dispatch_info.objects.get(pk=dispatch_id)
            dispatch_form = DispatchaddForm(instance=dispatch_info)
            dispatch_list = Dispatch_info.objects.all()
            dispatch_num_val = Dispatch_info.objects.get(pk=dispatch_id).dispatch_num
            dispatch_goods_list= Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num_val)
            context = {
                'dispatch_form': dispatch_form,
                'first_name': first_name,
                'dispatch_list':dispatch_list,
                'user_id':user_id,
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

            # Update Dispatch status is Gate-In Datatabse
            dispatch_status = Dispatch_info.objects.get(pk=dispatch_id).dispatch_status
            dispatch_status_id = StatusList.objects.get(status_title=dispatch_status).id
            dispatch_num = Dispatch_info.objects.get(pk=dispatch_id).dispatch_num
            wh_job_no_list = list(Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num).values_list('wh_job_no',flat=True).distinct())
            if dispatch_status_id == 5:
                for wh_job in wh_job_no_list:
                    Gatein_info.objects.filter(gatein_job_no=wh_job).update(gatein_job_status=1)
            else:
                print("Not Completed")
                for wh_job in wh_job_no_list:
                    Gatein_info.objects.filter(gatein_job_no=wh_job).update(gatein_job_status=2)

    if dispatch_form.is_valid():
        dispatch_form.save()
        print("Form Saved")
        messages.success(request, 'Record Updated Successfully')
        # return redirect(request.META['HTTP_REFERER'])
    else:
        print("Form Not Saved")
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
    dispatch_num=Dispatch_info.objects.get(pk=dispatch_id).dispatch_num
    stock_list=list(Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num).values_list('wh_qr_rand_num',flat=True))
    for i in stock_list:
        Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_dispatch_num=None)
        Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_check_in_out=1)
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
    Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_dispatch_num="None")
    Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_dispatch_id="")
    Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_check_in_out=1)
    Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_storage_time=0)
    Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_checkout_time=None)
    Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_dispatch_id="")
    dispatch_num_val=request.session.get('ses_dispatch_num_val')
    first_name = request.session.get('first_name')
    dispatch_invoice_list = list(Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num_val).values_list('wh_goods_invoice', flat=True).distinct())
    Dispatch_info.objects.filter(dispatch_num=dispatch_num_val).update(dispatch_invoice_list=dispatch_invoice_list)
    context = {
               'first_name': first_name,
               }
    return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/dispatch_goods_list')
@login_required(login_url='login_page')
def dispatch_add_goods(request,dispatch_id):
    dispatch_num_val=request.session.get('ses_dispatch_num_val')
    Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_check_in_out=2)
    Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_dispatch_num=dispatch_num_val)
    Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_checkout_time=datetime.now())
    first_name = request.session.get('first_name')
    check_in_date = Warehouse_goods_info.objects.get(pk=dispatch_id).wh_checkin_time
    check_out_date = Warehouse_goods_info.objects.get(pk=dispatch_id).wh_checkout_time
    date_diff = (check_out_date - check_in_date)  # Differnce between dates
    date_diff_days=date_diff.days
    duration_in_s = date_diff.total_seconds()  # Total number of seconds between dates
    storage_hours = divmod(duration_in_s, 3600)[0]  # Seconds in an hour = 3600
    # storage_days = (check_out_date - check_in_date).days  # In days
    storage_days = float(round(storage_hours / 24,2))  # In days
    Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_storage_time=date_diff_days)
    dispatch_invoice_list = list(Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num_val).values_list('wh_goods_invoice', flat=True).distinct())
    Dispatch_info.objects.filter(dispatch_num=dispatch_num_val).update(dispatch_invoice_list=dispatch_invoice_list)
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
    while camera==True:
        success, img = cap.read()
        for qrcode in decode(img):
            text = qrcode.data.decode('utf-8')
            t1=text.replace("{","")
            t2=t1.replace("}","")
            t3=t2.replace("'","")
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
                time.sleep(5)
                check_in_date = Warehouse_goods_info.objects.get(pk=dispatch_id).wh_checkin_time
                check_out_date = Warehouse_goods_info.objects.get(pk=dispatch_id).wh_checkout_time
                date_diff=(check_out_date - check_in_date) # Differnce between dates
                date_diff_days = date_diff.days
                duration_in_s = date_diff.total_seconds() # Total number of seconds between dates
                storage_hours = divmod(duration_in_s, 3600)[0]  # Seconds in an hour = 3600
                Warehouse_goods_info.objects.filter(pk=dispatch_id).update(wh_storage_time=date_diff_days)
                return redirect(request.META['HTTP_REFERER'])
            else:
                time.sleep(5)
                cv2.destroyAllWindows()
                messages.error(request, 'Stock Not Matching')
                return redirect(request.META['HTTP_REFERER'])

        cv2.imshow("Video", img)
        k=cv2.waitKey(1)
        if k == 27:  # wait for ESC key to exit and terminate program,
            cv2.destroyAllWindows()
            break

    return redirect(request.META['HTTP_REFERER'])

