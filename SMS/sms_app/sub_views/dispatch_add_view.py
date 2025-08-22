import time
from datetime import datetime
from itertools import groupby
from operator import attrgetter

from django.db.models.aggregates import Sum
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils.timezone import now
from xhtml2pdf import pisa

from .send_department_email import send_department_email
from ..forms import DispatchaddForm
from django.contrib.auth.decorators import login_required
from ..models import Check_in_out,Warehouse_goods_info,Dispatch_info,GoodsPartialDispatchInfo
from django.contrib import messages
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from ..views import warehousevolme_area_calc
from io import BytesIO
from django.views.decorators.http import require_POST
from django.db.models import F, ExpressionWrapper, IntegerField
import base64
from django.core.files.base import ContentFile


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
                'dispatch_id': dispatch_id,
            }
        else:
            print("I am inside get edit Dispatch")
            dispatch_info = Dispatch_info.objects.get(pk=dispatch_id)
            dispatch_form = DispatchaddForm(instance=dispatch_info)
            dispatch_list = Dispatch_info.objects.all()
            dispatch_num_val = Dispatch_info.objects.get(pk=dispatch_id).dispatch_num
            dispatch_goods_list= Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num_val)
            request.session['ses_dispatch_id'] = dispatch_info.id
            gate_out_email_count=Dispatch_info.objects.get(pk=dispatch_id).dispatch_email_count
            context = {
                'dispatch_form': dispatch_form,
                'first_name': first_name,
                'dispatch_list':dispatch_list,
                'user_id':user_id,
                'dispatch_goods_list':dispatch_goods_list,
                'dispatch_id':dispatch_id,
                'gate_out_email_count':gate_out_email_count,
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
                dispatch = dispatch_form.save(commit=False)
                # Process driver signature
                driver_data = request.POST.get('driver_signature_data')
                if driver_data:
                    format, imgstr = driver_data.split(';base64,')
                    ext = format.split('/')[-1]
                    data = ContentFile(base64.b64decode(imgstr), name=f'driver_signature.{ext}')
                    dispatch.dispatch_driver_signature = data

                # Process supervisor signature
                supervisor_data = request.POST.get('supervisor_signature_data')
                if supervisor_data:
                    format, imgstr = supervisor_data.split(';base64,')
                    ext = format.split('/')[-1]
                    data = ContentFile(base64.b64decode(imgstr), name=f'supervisor_signature.{ext}')
                    dispatch.dispatch_supervisor_signature = data

                dispatch.save()
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
def dispatch_goods_list(request):
    first_name = request.session.get('first_name')
    dispatch_id = request.session.get('ses_dispatch_id')
    dispatch_info = Dispatch_info.objects.get(pk=dispatch_id)

    dispatch_num_val = dispatch_info.dispatch_num
    dispatch_customer = dispatch_info.dispatch_customer

    request.session['ses_dispatch_num_val'] = dispatch_num_val
    request.session['ses_dispatch_id_val'] = dispatch_id

    dispatch_master_list = Warehouse_goods_info.objects.filter(
        wh_customer_name=dispatch_customer,
        wh_check_in_out__in=[1, 4]
    )

    for goods in dispatch_master_list:
        total_dispatched = GoodsPartialDispatchInfo.objects.filter(
            pd_goods=goods
        ).aggregate(total=Sum('pd_dispatch_qty'))['total'] or 0

        goods.dispatched_total = total_dispatched
        goods.remaining_qty = goods.wh_goods_pieces - total_dispatched


    dispatch_master_list = [g for g in dispatch_master_list if g.remaining_qty > 0]

    partial_goods = GoodsPartialDispatchInfo.objects.filter(
        pd_dispatch_info=dispatch_info
    ).select_related('pd_goods')

    goods_list = []
    for entry in partial_goods:
        goods = entry.pd_goods
        goods.dispatched_total = entry.pd_dispatch_qty
        goods.all_dispatch_nums = dispatch_num_val
        goods_list.append(goods)

    context = {
        'goods_list': goods_list,
        'dispatch_master_list': dispatch_master_list,
        'first_name': first_name,
        'dispatch_num_val': dispatch_num_val,
    }

    return render(request, "asset_mgt_app/dispatch_goods_list_woh.html", context)

@login_required(login_url='login_page')
def dispatch_remove_goods(request):
    selected_stocks = request.GET.getlist('myList[]')
    print('selected_stocks',selected_stocks)
    dispatch_id_val = request.session.get('ses_dispatch_id_val')
    current_dispatch = Dispatch_info.objects.get(pk=dispatch_id_val)

    for qr_num in selected_stocks:
        try:
            goods = Warehouse_goods_info.objects.get(wh_qr_rand_num=qr_num)

            GoodsPartialDispatchInfo.objects.filter(
                pd_goods=goods,
                pd_dispatch_info=current_dispatch
            ).delete()

            if goods.wh_dispatch_id == current_dispatch:
                goods.wh_dispatch_num = None
                goods.wh_dispatch_id = None
                goods.wh_dispatch_qty = 0
                goods.wh_check_in_out = Check_in_out.objects.get(pk=1)
                goods.wh_storage_time = 0
                goods.wh_checkout_time = None
                goods.wh_truck_type = None
                goods.save()

        except Warehouse_goods_info.DoesNotExist:
            continue

    dispatch_num_val=request.session.get('ses_dispatch_num_val')
    first_name = request.session.get('first_name')

    dispatch_invoice_job_update(dispatch_num_val)
    warehousevolme_area_calc(request)
    context = {
               'first_name': first_name,
               }
    # return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/dispatch_goods_list')
    return redirect('/SMS/dispatch_goods_list/' + str(dispatch_id_val))

def dispatch_stock_list(request):
    myList = request.GET.getlist('myList[]')
    # Return a response, for example, a JSON response
    response_data = {
        'result': 'success',
        'data': myList,
    }
    return JsonResponse(response_data)

@login_required(login_url='login_page')
def dispatch_add_goods(request):
    dispatch_num_val = request.session.get('ses_dispatch_num_val')
    dispatch_id_val = request.session.get('ses_dispatch_id_val')
    selected_stocks = request.GET.getlist('myList[]')
    current_date = now()

    try:
        dispatch_info = Dispatch_info.objects.get(dispatch_num=dispatch_num_val)
        vehicle_type = dispatch_info.dispatch_truck_type
    except Dispatch_info.DoesNotExist:
        messages.error(request, 'Dispatch information not found.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Get the Check_in_out instance for value 2
    try:
        check_in_out_instance = Check_in_out.objects.get(id=2)
    except Check_in_out.DoesNotExist:
        messages.error(request, 'Check_in_out instance with id=2 not found.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    goods_to_update = []
    for stock in selected_stocks:
        try:
            goods_info = Warehouse_goods_info.objects.get(wh_qr_rand_num=stock)
        except Warehouse_goods_info.DoesNotExist:
            messages.error(request, f'Stock with QR {stock} not found.')
            continue

        fumigation_action = goods_info.wh_fumigation_action
        fumigation_date = goods_info.wh_fumigation_date

        if str(fumigation_action) == 'BVM' and not fumigation_date:
            messages.error(request, f'Fumigation Date not entered for stock {stock}.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        goods_info.wh_dispatch_qty = goods_info.wh_goods_pieces
        # Prepare goods for bulk update
        goods_info.wh_check_in_out = check_in_out_instance  # Assign the Check_in_out instance
        goods_info.wh_dispatch_num = dispatch_num_val
        goods_info.wh_checkout_time = current_date
        goods_info.wh_truck_type = vehicle_type

        check_in_date = goods_info.wh_checkin_time.date()
        check_out_date = current_date.date()
        date_diff = (check_out_date - check_in_date).days
        goods_info.wh_storage_time = date_diff

        goods_to_update.append(goods_info)
        GoodsPartialDispatchInfo.objects.create(
            pd_goods=goods_info,
            pd_dispatch_info=dispatch_info,
            pd_dispatch_qty=goods_info.wh_goods_pieces,
            pd_updated_by=request.user,
        )

    # Bulk update all modified goods
    Warehouse_goods_info.objects.bulk_update(
        goods_to_update,
        ['wh_check_in_out', 'wh_dispatch_num', 'wh_checkout_time', 'wh_truck_type', 'wh_storage_time','wh_dispatch_qty','wh_goods_pieces']
    )

    Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num_val).update(wh_dispatch_id=dispatch_info.id)

    # Additional tasks
    dispatch_invoice_job_update(dispatch_num_val)
    warehousevolme_area_calc(request)

    print("Inside dispatch_add_goods end")
    # return HttpResponseRedirect(f'/SMS/dispatch_goods_list/{dispatch_id_val}?refresh=1')
    return redirect('/SMS/dispatch_goods_list/' + str(dispatch_id_val))

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
    dispatch_number = request.GET.get('dispatch_number', '')
    job_number = request.GET.get('job_number', '')

    dispatch_list = Dispatch_info.objects.filter(
        (Q(dispatch_num__icontains=dispatch_number) | Q(dispatch_num__isnull=True)) &
        (Q(dispatch_job_num_list__icontains=job_number) | Q(dispatch_job_num_list__isnull=True))
    ).order_by('-dispatch_created_at')

    # Convert signatures to base64
    for d in dispatch_list:
        d.driver_signature_base64 = get_base64_image(d.dispatch_driver_signature)
        d.supervisor_signature_base64 = get_base64_image(d.dispatch_supervisor_signature)

    # Pagination
    page_number = request.GET.get('page')
    paginator = Paginator(dispatch_list, 50)
    page_obj = paginator.get_page(page_number)

    context = {
        'first_name': first_name,
        'page_obj': page_obj,
    }
    return render(request, "asset_mgt_app/dispatch_list.html", context)


def get_base64_image(image_field):
    if not image_field:
        return None
    with image_field.open('rb') as img_file:
        return 'data:image/png;base64,' + base64.b64encode(img_file.read()).decode('utf-8')
@login_required(login_url='login_page')
def dispatch_gatepass_pdf(request, dispatch_id=0, download=False):
    dispatch_num = Dispatch_info.objects.get(id=dispatch_id).dispatch_num
    # Fetch data from the database
    wh_dispatch_details = Warehouse_goods_info.objects.filter(
        wh_dispatch_num=dispatch_num
    ).order_by('wh_goods_invoice', 'id')

    # Group by `wh_goods_invoice` and calculate totals
    grouped_details = []
    for invoice, items in groupby(wh_dispatch_details, key=attrgetter('wh_goods_invoice')):
        items_list = list(items)  # Convert group iterator to list
        total_pieces = sum(item.wh_goods_pieces for item in items_list)
        total_weight = sum(item.wh_goods_weight for item in items_list)
        first_item = items_list[0]  # Use the first item for non-aggregated fields

        grouped_details.append({
            'wh_consigner': first_item.wh_consigner,
            'wh_goods_invoice': invoice,
            'total_pieces': total_pieces,
            'total_weight': total_weight,
            'gatein_destination': first_item.wh_gate_injob_no_id.gatein_destination,
            'gatein_hawb': first_item.wh_gate_injob_no_id.gatein_hawb,
        })

    dispatch_details = Dispatch_info.objects.filter(dispatch_num=dispatch_num).order_by('-id')
    wh_location = Warehouse_goods_info.objects.filter(wh_dispatch_num=dispatch_num).values_list('wh_branch__loc_name', flat=True).order_by('id').first()
    for d in dispatch_details:
        d.driver_signature_base64 = get_base64_image(d.dispatch_driver_signature)
        d.supervisor_signature_base64 = get_base64_image(d.dispatch_supervisor_signature)
    context = {
        'dispatch_details': dispatch_details,
        'grouped_dispatch_details': grouped_details,
        'wh_dispatch_details': wh_dispatch_details,
        'wh_location': wh_location,
    }

    dispatch_invoice_job_update(dispatch_num)
    template_path = 'asset_mgt_app/wh_gate_pass.html'

    # Render HTML
    template = get_template(template_path)
    html = template.render(context)

    # Generate PDF in memory
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)

    if pisa_status.err:
        raise ValueError('Error generating PDF')

    # Get the PDF data as bytes
    pdf_buffer.seek(0)  # Move the pointer to the beginning
    pdf_data = pdf_buffer.read()
    pdf_buffer.close()

    if download:
        # Return the PDF as a downloadable file in the HTTP response
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="WH_Gate_Pass_{dispatch_num}.pdf"'
        return response

    return pdf_data  # Return raw PDF data for use in email attachment

@login_required(login_url='login_page')
def dispatch_gatepass_pdf_download(request, dispatch_id):
    return dispatch_gatepass_pdf(request, dispatch_id, download=True)

@login_required(login_url='login_page')
def dispatch_goods_back(request):
    dispatch_id = request.session.get('ses_dispatch_id')

    return redirect('/SMS/dispatch_update/' + str(dispatch_id))

@login_required(login_url='login_page')
def gate_out_email(request, dispatch_id=0):
    if request.method == 'POST':
        recipient = request.POST.get('recipient')
        message = request.POST.get('message')
        recipient_list = [email.strip() for email in recipient.split(',')]
        dispatch_id=request.session.get('ses_dispatch_id')
        # Call dispatch_gatepass_pdf to get the PDF and its filename
        pdf_data = dispatch_gatepass_pdf(request, dispatch_id)
        dispatch_number=Dispatch_info.objects.get(pk=dispatch_id).dispatch_num
        subject = f"{dispatch_number}_Gate-Out Alert"
        gate_out_email_count = Dispatch_info.objects.get(pk=dispatch_id).dispatch_email_count
        file_name = f"WH_Gate_Pass_{dispatch_number}.pdf"
        # Send the email with the PDF attachment
        send_department_email('warehouse', subject, message, recipient_list, pdf_data, 'application/pdf', file_name)
        gate_out_email_count=gate_out_email_count+1
        Dispatch_info.objects.filter(pk=dispatch_id).update(dispatch_email_count=gate_out_email_count)
        # Redirect back to the previous page
        return redirect(request.META['HTTP_REFERER'])
    else:
        messages.error(request, 'Invalid input in the email form.')
    return redirect(request.META['HTTP_REFERER'])


@require_POST
@login_required(login_url='login_page')
def dispatch_partial_goods(request):
    goods_id = request.POST.get('goods_id')
    dispatch_qty = float(request.POST.get('dispatch_qty'))
    goods = Warehouse_goods_info.objects.get(id=goods_id)
    dispatch_num_val = request.session.get('ses_dispatch_num_val')
    dispatch_info = Dispatch_info.objects.get(dispatch_num=dispatch_num_val)

    total_dispatched = GoodsPartialDispatchInfo.objects.filter(pd_goods=goods).aggregate(
        total=Sum('pd_dispatch_qty')
    )['total'] or 0

    remaining_qty = goods.wh_goods_pieces - total_dispatched

    if dispatch_qty > remaining_qty:
        return JsonResponse({'error': 'Cannot dispatch more than remaining quantity'}, status=400)

    # Create a dispatch log record
    GoodsPartialDispatchInfo.objects.create(
        pd_goods=goods,
        pd_dispatch_qty=dispatch_qty,
        pd_dispatch_info=dispatch_info,
        pd_updated_by=request.user
    )
    goods.wh_dispatch_num = dispatch_info.dispatch_num
    goods.wh_dispatch_id = dispatch_info
    goods.wh_checkout_time = now()

    new_total_dispatched = total_dispatched + dispatch_qty
    if new_total_dispatched >= goods.wh_goods_pieces:
        goods.wh_dispatch_qty = goods.wh_goods_pieces
        goods.wh_check_in_out = Check_in_out.objects.get(id=2)  # Fully out
    else:
        goods.wh_dispatch_qty = new_total_dispatched
        goods.wh_check_in_out = Check_in_out.objects.get(id=4)

    goods.save()
    return JsonResponse({'message': f'{dispatch_qty} units dispatched successfully.'})
