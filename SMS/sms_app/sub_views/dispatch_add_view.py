import time
from datetime import datetime

from django.db.models.aggregates import Sum
from django.http import JsonResponse
from django.template.loader import get_template
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import View
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Frame, PageTemplate, BaseDocTemplate
from xhtml2pdf import pisa

from ..forms import DispatchaddForm
from django.contrib.auth.decorators import login_required
from ..models import Warehouse_goods_info,Dispatch_info
from django.contrib import messages
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from ..views import warehousevolme_area_calc
from django.http import HttpResponse
from reportlab.pdfgen import canvas

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

            if dispatch_form.is_valid():
                # Generate Random pre-Dispatch number
                try:
                    last_id = (Dispatch_info.objects.latest('id')).id
                    # last_id = (Gatein_pre_info.objects.values_list('gatein_pre_number',flat=True)).last()
                    dispatch_num_next = str('Dispatch_') + str(
                        (int((Dispatch_info.objects.get(id=last_id).dispatch_num).replace('Dispatch_', '')) + 1))
                    print(dispatch_num_next)
                except ObjectDoesNotExist:
                    dispatch_num_next = str('Dispatch_') + str(1000000)
                dispatch_form.save()
                print("Form Saved")
                last_id = (Dispatch_info.objects.latest('id')).id
                Dispatch_info.objects.filter(id=last_id).update(dispatch_num=dispatch_num_next)
                messages.success(request, 'Record Updated Successfully')
                # sales_num = request.POST.get('s_sale_number')
                dipstach_id = Dispatch_info.objects.get(dispatch_num=dispatch_num_next).id
                return redirect('/SMS/dispatch_update/' + str(dipstach_id))
                # return redirect(request.META['HTTP_REFERER'])
            else:
                print("Form Not Saved")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("I am inside post edit dispatch")
            dispatch_info = Dispatch_info.objects.get(pk=dispatch_id)
            dispatch_form = DispatchaddForm(request.POST, instance=dispatch_info)

            if dispatch_form.is_valid():
                dispatch_form.save()
                print("Form Saved")
                messages.success(request, 'Record Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
            else:
                print("Form Not Saved")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/dispatch_list')

# List Dispatch Job
@login_required(login_url='login_page')
def dispatch_list(request):
    first_name = request.session.get('first_name')
    dispatch_list= (Dispatch_info.objects.all()).order_by('-dispatch_created_at')
    page_number = request.GET.get('page')
    paginator = Paginator(dispatch_list, 10000)
    page_obj = paginator.get_page(page_number)
    context = {
        'dispatch_list': dispatch_list,
        'first_name': first_name,
        'page_obj': page_obj,
    }
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
    dispatch_customer = Dispatch_info.objects.get(pk=dispatch_id).dispatch_customer
    print('dispatch_customer',dispatch_customer)
    request.session['ses_dispatch_num_val'] = dispatch_num_val
    # # dispatch_num_val = Dispatch_info.objects.get(pk=dispatch_id).dispatch_num
    dispatch_master_list=Warehouse_goods_info.objects.filter(wh_check_in_out=1,wh_customer_name=dispatch_customer)
    goods_list=Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num_val)
    context = {'goods_list' : goods_list,
               'first_name': first_name,
               'dispatch_master_list':dispatch_master_list,
               'dispatch_num_val':dispatch_num_val,
               }
    return render(request,"asset_mgt_app/dispatch_goods_list_woh.html",context)

@login_required(login_url='login_page')
def dispatch_remove_goods(request):
    selected_stocks = request.GET.getlist('myList[]')
    print('selected_stocks',selected_stocks)
    for i in selected_stocks:
        Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_dispatch_num=None)
        Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_dispatch_id="")
        Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_check_in_out=1)
        Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_storage_time=0)
        Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_checkout_time=None)
        Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_dispatch_id="")
        Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_truck_type=None)
    dispatch_num_val=request.session.get('ses_dispatch_num_val')
    first_name = request.session.get('first_name')
    dispatch_invoice_job_update(dispatch_num_val)
    warehousevolme_area_calc(request)
    context = {
               'first_name': first_name,
               }
    return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/dispatch_goods_list')

# @login_required(login_url='login_page')
# def dispatch_add_goods(request):
#     dispatch_num_val=request.session.get('ses_dispatch_num_val')
#     # selected_stocks = request.GET.getlist('myList[]')
#     # Get dispatch number greater than Nov 3
#     dispatch_num_list=list(Dispatch_info.objects.filter(dispatch_depature_date__gt='2023-11-01').values_list('dispatch_num',flat=True))
#
#     first_name = request.session.get('first_name')
#     current_date=(timezone.now()).astimezone(timezone.get_current_timezone())
#     for k in dispatch_num_list:
#         try:
#             selected_stocks = Warehouse_goods_info.objects.filter(wh_dispatch_num=k).values_list('wh_qr_rand_num', flat=True)
#             print(selected_stocks)
#             for i in selected_stocks:
#                 fumigation_action = Warehouse_goods_info.objects.get(wh_qr_rand_num=i).wh_fumigation_action
#                 fumigation_date = Warehouse_goods_info.objects.get(wh_qr_rand_num=i).wh_fumigation_date
#                 if str(fumigation_action) == 'BVM' and fumigation_date == None:
#                     messages.error(request, 'Fumigation Date not entered for this Stock')
#                     return redirect(request.META['HTTP_REFERER'])
#                 else:
#                     check_out_time = Warehouse_goods_info.objects.get(wh_dispatch_num=k).wh_checkout_time
#                     vehicle_type = Dispatch_info.objects.get(dispatch_num=k).dispatch_truck_type
#                     Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_check_in_out=2)
#                     Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_dispatch_num=dispatch_num_val)
#                     Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_checkout_time=check_out_time)
#                     Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_truck_type=vehicle_type)
#                     check_in_date = Warehouse_goods_info.objects.get(wh_qr_rand_num=i).wh_checkin_time
#                     check_out_date = Warehouse_goods_info.objects.get(wh_qr_rand_num=i).wh_checkout_time
#                     date_diff = (check_out_date - check_in_date)  # Differnce between dates
#                     date_diff_days = date_diff.days
#                     duration_in_s = date_diff.total_seconds()  # Total number of seconds between dates
#                     storage_hours = divmod(duration_in_s, 3600)[0]  # Seconds in an hour = 3600
#                     # storage_days = (check_out_date - check_in_date).days  # In days
#                     storage_days = float(round(storage_hours / 24, 2))  # In days
#                     Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_storage_time=date_diff_days)
#                     print("warehouseoutinfo is Valid")
#                     try:
#                         dispatch_num_id = Dispatch_info.objects.get(dispatch_num=dispatch_num_val).id
#                         Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num_val).update(wh_dispatch_id=dispatch_num_id)
#                     except ObjectDoesNotExist:
#                         pass
#                 dispatch_invoice_job_update(dispatch_num_val)
#                 warehousevolme_area_calc(request)
#                 print("Inside dispatch_add_goods end")
#         except:
#             pass
#     context = {
#                 'first_name': first_name,
#                 'dispatch_goods_list':dispatch_goods_list,
#                }
#     return redirect(request.META['HTTP_REFERER'])
#     # return redirect('/SMS/dispatch_goods_list')

# new
@login_required(login_url='login_page')
def dispatch_add_goods(request):
    dispatch_num_val=request.session.get('ses_dispatch_num_val')
    selected_stocks = request.GET.getlist('myList[]')
    vehicle_type = Dispatch_info.objects.get(dispatch_num=dispatch_num_val).dispatch_truck_type
    first_name = request.session.get('first_name')
    # current_date=(timezone.now()).astimezone(timezone.get_current_timezone())
    current_date=(timezone.now())
    for i in selected_stocks:
        fumigation_action = Warehouse_goods_info.objects.get(wh_qr_rand_num=i).wh_fumigation_action
        fumigation_date = Warehouse_goods_info.objects.get(wh_qr_rand_num=i).wh_fumigation_date
        if str(fumigation_action) == 'BVM' and fumigation_date == None:
            messages.error(request, 'Fumigation Date not entered for this Stock')
            return redirect(request.META['HTTP_REFERER'])
        else:
            Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_check_in_out=2)
            Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_dispatch_num=dispatch_num_val)
            Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_checkout_time=current_date)
            Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_truck_type=vehicle_type)
            check_in_date = Warehouse_goods_info.objects.get(wh_qr_rand_num=i).wh_checkin_time
            check_out_date = Warehouse_goods_info.objects.get(wh_qr_rand_num=i).wh_checkout_time
            date_diff = (check_out_date - check_in_date)  # Differnce between dates
            date_diff_days = date_diff.days
            duration_in_s = date_diff.total_seconds()  # Total number of seconds between dates
            storage_hours = divmod(duration_in_s, 3600)[0]  # Seconds in an hour = 3600
            # storage_days = (check_out_date - check_in_date).days  # In days
            storage_days = float(round(storage_hours / 24, 2))  # In days
            Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_storage_time=date_diff_days)
            print("warehouseoutinfo is Valid")
            try:
                dispatch_num_id = Dispatch_info.objects.get(dispatch_num=dispatch_num_val).id
                Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num_val).update(wh_dispatch_id=dispatch_num_id)
            except ObjectDoesNotExist:
                pass
        dispatch_invoice_job_update(dispatch_num_val)
        warehousevolme_area_calc(request)
        print("Inside dispatch_add_goods end")

    context = {
                'first_name': first_name,
                'dispatch_goods_list':dispatch_goods_list,
               }
    return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/dispatch_goods_list')
def dispatch_stock_list(request):
    myList = request.GET.getlist('myList[]')
    print(myList)
    # Return a response, for example, a JSON response
    response_data = {
        'result': 'success',
        'data': myList,
    }
    return JsonResponse(response_data)
def dispatch_invoice_job_update(dispatch_num_val):
    print("Inside dispatch_invoice_job_update")
    dispatch_invoice_list = list(Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num_val).values_list('wh_goods_invoice',flat=True).distinct())
    dispatch_job_num_list = list(Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num_val).values_list('wh_job_no',flat=True).distinct())
    Dispatch_info.objects.filter(dispatch_num=dispatch_num_val).update(dispatch_invoice_list=dispatch_invoice_list)
    Dispatch_info.objects.filter(dispatch_num=dispatch_num_val).update(dispatch_job_num_list=dispatch_job_num_list)
    total_weight=Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num_val).aggregate(Sum('wh_goods_weight'))['wh_goods_weight__sum']
    total_goods=Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num_val).aggregate(Sum('wh_goods_pieces'))['wh_goods_pieces__sum']
    Dispatch_info.objects.filter(dispatch_num=dispatch_num_val).update(dispatch_total_weight=total_weight)
    Dispatch_info.objects.filter(dispatch_num=dispatch_num_val).update(dispatch_total_goods=total_goods)
    return ()
@login_required(login_url='login_page')
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

@login_required(login_url='login_page')
def dispatch_search(request):
    first_name = request.session.get('first_name')
    dispatch_number = request.GET.get('dispatch_number')
    job_number = request.GET.get('job_number')
    if not dispatch_number:
        dispatch_number = ""
    if not job_number:
        job_number = ""
    dispatch_list = (Dispatch_info.objects.filter((Q(dispatch_num__icontains =dispatch_number)|Q(dispatch_num__isnull=True)) & (Q(dispatch_job_num_list__icontains =job_number)|Q(dispatch_job_num_list__isnull=True)))).order_by('-dispatch_created_at')
    page_number = request.GET.get('page')
    paginator = Paginator(dispatch_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
        # 'sales_list': sales_list,
        'first_name': first_name,
        'page_obj': page_obj,
        }
    return render(request, "asset_mgt_app/dispatch_list.html", context)
@login_required(login_url='login_page')
def dispatch_gatepass_pdf(request,dispatch_id=0):
    dispatch_num=Dispatch_info.objects.get(id=dispatch_id).dispatch_num
    wh_dispatch_details = (Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num)).order_by('id')
    dispatch_details = (Dispatch_info.objects.filter(dispatch_num=dispatch_num)).order_by('-id')
    context = {
        'dispatch_details': dispatch_details,
        'wh_dispatch_details': wh_dispatch_details,
    }
    dispatch_invoice_job_update(dispatch_num)
    file_name=str("WH_Gate_Pass_")+str(dispatch_num)+str(".pdf")
    template_path = 'asset_mgt_app/wh_gate_pass.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    template = get_template(template_path)
    html = template.render(context)

    # Create PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We has some error <pre>' + html + '</pre>')
    return response

