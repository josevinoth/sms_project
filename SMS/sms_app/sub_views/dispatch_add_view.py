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
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from xhtml2pdf import pisa
from django.db.models import CharField, Value
from django.db.models.functions import Concat

from .send_department_email import send_department_email
from ..forms import DispatchaddForm
from django.contrib.auth.decorators import login_required
from ..models import Check_in_out,Warehouse_goods_info,Dispatch_info,GoodsPartialDispatchInfo
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id, get_base64_image
from django.contrib import messages
import cv2
import numpy as np
#from pyzbar.pyzbar import decode
qr_detector = cv2.QRCodeDetector()

from ..sub_models.loadingbay_mod import Loadingbay_Info
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
                # Generate Dispatch number based on financial year (Branch specific)
                fy = get_financial_year()
                branch_id = get_session_branch_id(request)
                branch_code = get_branch_code(branch_id)
                prefix = f"{fy}_{branch_code}_DSP_"
                dispatch_num_next = generate_next_number(Dispatch_info, 'dispatch_num', prefix, 6)
                instance = dispatch_form.save()
                print("Form Saved")
                Dispatch_info.objects.filter(id=instance.id).update(dispatch_num=dispatch_num_next)
                messages.success(request, 'Record Updated Successfully')
                # sales_num = request.POST.get('s_sale_number')
                return redirect('/SMS/dispatch_update/' + str(instance.id))
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

                # Automatic Email Logic
                try:
                    if dispatch.dispatch_status_id == 5: # Completed
                        customer = dispatch.dispatch_customer
                        if customer.cu_automatic_email == 'YES':
                            recipient_list = [customer.cu_email]
                            message = "Dear Customer,\n\nPlease find the Gate-Out Gate Pass attached.\n\nRegards,\nBVM Warehouse Team"
                            send_gate_out_email_logic(dispatch.id, recipient_list, message, request)
                except Exception as e:
                    print(f"Auto-Email Error (Dispatch): {e}")

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
        total_dispatched_weight = GoodsPartialDispatchInfo.objects.filter(
            pd_goods=goods
        ).aggregate(total_wt=Sum('pd_goods_weight'))['total_wt'] or 0

        goods.dispatched_total = total_dispatched
        goods.remaining_qty = goods.wh_goods_pieces - total_dispatched
        goods.dispatched_total_weight = total_dispatched_weight
        goods.remaining_weight = goods.wh_goods_weight - total_dispatched_weight
        goods.loadingbay = Loadingbay_Info.objects.filter(lb_job_no=goods.wh_job_no).first()  # ✅ attach here

    # Only show goods with remaining quantity
    dispatch_master_list = [g for g in dispatch_master_list if g.remaining_qty > 0]
    partial_goods = GoodsPartialDispatchInfo.objects.filter(
        pd_dispatch_info=dispatch_info
    ).select_related('pd_goods')

    goods_list = []
    for entry in partial_goods:
        goods = entry.pd_goods
        goods.dispatched_total = entry.pd_dispatch_qty
        goods.all_dispatch_nums = dispatch_num_val
        goods.loadingbay = Loadingbay_Info.objects.filter(lb_job_no=goods.wh_job_no).first()
        goods_list.append(goods)
    print()
    context = {
        'goods_list': goods_list,
        'dispatch_master_list': dispatch_master_list,
        'first_name': first_name,
        'dispatch_num_val': dispatch_num_val,
        "now": timezone.now().date()   # ✅ pass only date

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
    print('selected',selected_stocks)
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

        total_dispatched = GoodsPartialDispatchInfo.objects.filter(
            pd_goods=goods_info
        ).aggregate(total=Sum('pd_dispatch_qty'))['total'] or 0
        total_dispatched_weight = GoodsPartialDispatchInfo.objects.filter(
            pd_goods=goods_info
        ).aggregate(total_wt=Sum('pd_goods_weight'))['total_wt'] or 0

        remaining_weight = goods_info.wh_goods_weight - total_dispatched_weight
        remaining_qty = goods_info.wh_goods_pieces - total_dispatched

        if remaining_qty < 0 or remaining_weight < 0:
            continue

        # Create dispatch entry with remaining quantity
        if remaining_qty > 0:
            GoodsPartialDispatchInfo.objects.update_or_create(
                pd_goods=goods_info,
                pd_dispatch_info=dispatch_info,
                defaults={
                    'pd_dispatch_qty': remaining_qty,
                    'pd_updated_by': request.user,
                    'pd_goods_weight': remaining_weight,
                }
            )

        # Update goods_info fields
        goods_info.wh_dispatch_qty = total_dispatched + remaining_qty
        goods_info.wh_dispatch_num = dispatch_num_val
        goods_info.wh_dispatch_id = dispatch_info
        goods_info.wh_check_in_out = check_in_out_instance
        goods_info.wh_checkout_time = current_date
        goods_info.wh_truck_type = vehicle_type

        check_in_date = goods_info.wh_checkin_time.date()
        check_out_date = current_date.date()
        date_diff = (check_out_date - check_in_date).days
        goods_info.wh_storage_time = date_diff

        goods_to_update.append(goods_info)

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
def qr_dispatch_decoder(request, dispatch_id):
    # Scanning QR Code from Camera Feed (OpenCV only)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 740)

    dispatch_num_val = request.session.get('ses_dispatch_num_val')
    stock_num_val = Warehouse_goods_info.objects.get(pk=dispatch_id).wh_qr_rand_num

    while True:
        success, img = cap.read()
        if not success:
            break

        # ✅ OpenCV QR Decode
        data, points, _ = qr_detector.detectAndDecode(img)

        if data:
            text = data.strip()

            # sanitize text (same as your logic)
            t1 = text.replace("{", "")
            t2 = t1.replace("}", "")
            t3 = t2.replace("'", "")

            if points is not None:
                # QRCodeDetector returns shape (1, 4, 2)
                pts = points[0].astype(int)  # shape → (4, 2)

                # ✅ Draw QR bounding box
                cv2.polylines(img, [pts], True, (255, 255, 0), 5)

                # ✅ Text position (top-left corner)
                text_x, text_y = pts[0][0], pts[0][1] - 10
                if text_y < 10:
                    text_y = pts[0][1] + 20

                cv2.putText(
                    img,
                    text,
                    (int(text_x), int(text_y)),
                    cv2.FONT_HERSHEY_DUPLEX,
                    0.8,
                    (255, 255, 0),
                    2
                )

            # ✅ MATCHED STOCK
            if t3 == stock_num_val:
                cap.release()
                cv2.destroyAllWindows()

                Warehouse_goods_info.objects.filter(pk=dispatch_id).update(
                    wh_check_in_out=2,
                    wh_dispatch_num=dispatch_num_val,
                    wh_checkout_time=datetime.datetime.now()
                )

                messages.success(request, 'Stock Matching. Approved for Dispatch')

                goods = Warehouse_goods_info.objects.get(pk=dispatch_id)
                check_in_date = goods.wh_checkin_time
                check_out_date = goods.wh_checkout_time
                date_diff_days = (check_out_date - check_in_date).days

                Warehouse_goods_info.objects.filter(pk=dispatch_id).update(
                    wh_storage_time=date_diff_days
                )

                return redirect(request.META['HTTP_REFERER'])

            # ❌ NOT MATCHED
            else:
                cap.release()
                cv2.destroyAllWindows()
                messages.error(request, 'Stock Not Matching')
                return redirect(request.META['HTTP_REFERER'])

        cv2.imshow("QR Scanner", img)

        # ESC to exit
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
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


@login_required(login_url='login_page')
def dispatch_gatepass_pdf(request, dispatch_id=0, download=False):
    dispatch_num = Dispatch_info.objects.get(id=dispatch_id).dispatch_num
    # Fetch data from the database
    wh_dispatch_details = Warehouse_goods_info.objects.filter(
        wh_dispatch_num=dispatch_num
    ).order_by('wh_goods_invoice', 'id')

    # Group by `wh_goods_invoice` and calculate totals
    grouped_details = GoodsPartialDispatchInfo.objects.filter(
        pd_dispatch_info__dispatch_num=dispatch_num
    ).annotate(
        wh_consigner=F('pd_goods__wh_consigner'),
        wh_goods_invoice=F('pd_goods__wh_goods_invoice'),
        pieces_str=Concat(
            F('pd_dispatch_qty'),
            Value('/'),
            F('pd_goods__wh_goods_pieces'),
            output_field=CharField()
        ),
        weight_str=Concat(
            F('pd_goods_weight'),
            Value('/'),
            F('pd_goods__wh_goods_weight'),
            output_field=CharField()
        ),
        total_weight=F('pd_goods__wh_goods_weight'),
        gatein_destination=F('pd_goods__wh_gate_injob_no_id__gatein_destination'),
        gatein_hawb=F('pd_goods__wh_gate_injob_no_id__gatein_hawb')
    ).values(
    'wh_consigner',
    'wh_goods_invoice',
    'pieces_str',
    'weight_str',
    'total_weight',
    'gatein_destination',
    'gatein_hawb',
    'pd_dispatch_qty',
    'pd_goods__wh_goods_pieces',
    'pd_goods_weight',
    'pd_goods__wh_goods_weight'
)

    total_dispatch_qty = sum(d['pd_dispatch_qty'] for d in grouped_details)
    total_pieces_sum = sum(d['pd_goods__wh_goods_pieces'] for d in grouped_details)

    total_dispatch_weight = sum(d['pd_goods_weight'] for d in grouped_details)
    total_weight_sum = sum(d['pd_goods__wh_goods_weight'] for d in grouped_details)

    total_packages_str = f"{int(total_dispatch_qty)}/{int(total_pieces_sum)}"
    total_weight_str = f"{total_dispatch_weight}/{total_weight_sum}"

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
        'total_packages_str': total_packages_str,
        'total_weight_str': total_weight_str,
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

def send_gate_out_email_logic(dispatch_id, recipient_list, message, request=None):
    dispatch = Dispatch_info.objects.get(pk=dispatch_id)
    dispatch_number = dispatch.dispatch_num
    subject = f"{dispatch_number}_Gate-Out Alert"
    
    # Generate PDF (using existing function)
    pdf_data = dispatch_gatepass_pdf(request, dispatch_id)
    file_name = f"WH_Gate_Pass_{dispatch_number}.pdf"
    
    formatted_message = message.replace('\n', '<br>')
    
    send_department_email('warehouse', subject, formatted_message, recipient_list, pdf_data, 'application/pdf', file_name)
    
    # Update email count
    Dispatch_info.objects.filter(pk=dispatch_id).update(dispatch_email_count=F('dispatch_email_count') + 1)

@login_required(login_url='login_page')
def gate_out_email(request, dispatch_id=0):
    if request.method == 'POST':
        recipient = request.POST.get('recipient')
        message = request.POST.get('message', '')
        recipient_list = [email.strip() for email in recipient.split(',') if email.strip()]
        dispatch_id = request.session.get('ses_dispatch_id')
        
        send_gate_out_email_logic(dispatch_id, recipient_list, message, request)
        
        messages.success(request, "Gate-Out E-mail sent successfully.")
        return redirect(request.META['HTTP_REFERER'])
    else:
        messages.error(request, 'Invalid input in the email form.')
    return redirect(request.META['HTTP_REFERER'])


@require_POST
@login_required(login_url='login_page')
def dispatch_partial_goods(request):
    goods_id = request.POST.get('goods_id')
    dispatch_qty = float(request.POST.get('dispatch_qty'))
    dispatch_weight = float(request.POST.get('dispatch_weight') or 0)

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
        pd_updated_by=request.user,
        pd_goods_weight = dispatch_weight
    )
    goods.wh_dispatch_num = dispatch_info.dispatch_num
    goods.wh_dispatch_id = dispatch_info
    goods.wh_checkout_time = now()

    new_total_dispatched = total_dispatched + dispatch_qty
    if new_total_dispatched >= goods.wh_goods_pieces:
        goods.wh_dispatch_qty = goods.wh_goods_pieces
        goods.wh_check_in_out = Check_in_out.objects.get(id=2)
    else:
        goods.wh_dispatch_qty = new_total_dispatched
        goods.wh_check_in_out = Check_in_out.objects.get(id=4)

    goods.save()
    return JsonResponse({'message': f'{dispatch_qty} units dispatched successfully.'})

@csrf_exempt
@login_required(login_url='login_page')
def dispatch_upload_attachment(request, pk, att_type):
    if request.method == 'POST' and request.FILES.get('attachment'):
        instance = get_object_or_404(Dispatch_info, pk=pk)
        uploaded_file = request.FILES['attachment']

        if att_type == 'gatepass':
            instance.dispatch_gatepass_att = uploaded_file

        instance.save()
        messages.success(request, 'Attachment uploaded successfully.')
    else:
        messages.error(request, 'Attachment upload failed. Please try again.')

    return redirect(request.META.get('HTTP_REFERER', 'gatein_list'))
@csrf_exempt
@login_required(login_url='login_page')
def dispatch_delete_attachment(request, pk, att_type):
    if request.method == 'POST':
        instance = get_object_or_404(Dispatch_info, pk=pk)

        if att_type == 'gatepass' and instance.dispatch_gatepass_att:
            instance.dispatch_gatepass_att.delete(save=False)
            instance.dispatch_gatepass_att = None

        instance.save()
        messages.success(request, 'Attachment deleted successfully.')

    return redirect(request.META.get('HTTP_REFERER', 'gatein_list'))
