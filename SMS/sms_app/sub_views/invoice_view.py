from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.aggregates import Sum, Max
from django.http import HttpResponse
import json
from django.contrib import messages

from ..forms import InvoiceaddForm
from ..models import VehicletypeInfo,Dispatch_info,Loadingbay_Info,TrbusinesstypeInfo,CustomerInfo,Warehouse_goods_info,WhratemasterInfo,BilingInfo
from django.shortcuts import render, redirect
from datetime import timedelta, date, datetime


# Invoicecity
@login_required(login_url='login_page')
def invoice_add(request,invoice_id=0):
    global min_check_in_time, max_check_out_time, max_storage_days
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if invoice_id == 0:
            invoice_form = InvoiceaddForm()
            context={
                'invoice_form': invoice_form,
                'first_name':first_name,
                'user_id':user_id,
            }
        else:
            invoice = BilingInfo.objects.get(pk=invoice_id)
            invoice_form = InvoiceaddForm(instance=invoice)
            voucher_num = BilingInfo.objects.get(pk=invoice_id).bill_invoice_ref

            # Calculate Warehouse Storage Charges
            dispatch_num = (Warehouse_goods_info.objects.filter(wh_voucher_num=voucher_num).values_list('wh_dispatch_num',flat=True)).distinct()
            customer_name = BilingInfo.objects.get(bill_invoice_ref=voucher_num).bill_customer_name
            customer_id = CustomerInfo.objects.get(cu_name=customer_name).id
            customer_type = CustomerInfo.objects.get(cu_name=customer_name).cu_businessmodel
            customer_type_id = TrbusinesstypeInfo.objects.get(tb_trbusinesstype=customer_type).id
            shipper_invoice = (Warehouse_goods_info.objects.filter(wh_voucher_num=voucher_num).values_list('wh_goods_invoice',flat=True)).distinct()
            shipper_invoice_count = len(shipper_invoice)

            for k in shipper_invoice:
                try:
                    if customer_type_id== 2:
                        warehouse_charge = WhratemasterInfo.objects.get(whrm_customer_name=customer_id,whrm_charge_type=1).whrm_rate
                        warehouse_charge_1 = warehouse_charge / shipper_invoice_count
                        storage_cost_total = round((warehouse_charge_1), 2)
                        date_today = date.today()
                        year = date_today.year
                        month = date_today.month
                        min_check_in_time = date(year, month, 1)
                        if month == 12:
                            max_check_out_time = date(year, month, 31)
                        else:
                            max_check_out_time = date(year, month + 1, 1) + timedelta(days=-1)
                        max_storage_days = ((max_check_out_time - min_check_in_time).days)+1
                    else:
                        try:
                            vehicle_type = Dispatch_info.objects.get(dispatch_num=dispatch_num[0]).dispatch_truck_type
                        except IndexError:
                            messages.error(request,'Click "Shipper Invoice List" button to add shipper invoice and proceed!')
                            return redirect(request.META['HTTP_REFERER'])
                        vehicle_type_id = VehicletypeInfo.objects.get(vt_vehicletype=vehicle_type).id
                        try:
                            min_check_in_time = datetime.date((min(Warehouse_goods_info.objects.filter(wh_voucher_num=voucher_num).values_list('wh_checkin_time')))[0])
                            max_check_out_time = datetime.date((max(Warehouse_goods_info.objects.filter(wh_voucher_num=voucher_num).values_list('wh_checkout_time')))[0])
                        except:
                            min_check_in_time = 0
                            max_check_out_time = 0
                        warehouse_charge = WhratemasterInfo.objects.get(whrm_customer_name=customer_id,whrm_charge_type=1,whrm_vehicle_type=vehicle_type_id).whrm_rate
                        # max_storage_days = max(Warehouse_goods_info.objects.filter(wh_voucher_num=voucher_num,wh_goods_invoice=k).values_list('wh_storage_time', flat=True))
                        max_storage_days = ((max_check_out_time-min_check_in_time).days)
                        warehouse_charge_1 = warehouse_charge / shipper_invoice_count
                        storage_cost_total = round((warehouse_charge_1 * max_storage_days), 2)
                except ObjectDoesNotExist:
                    messages.error(request,'Warehouse Storage Charges not available in master for selected Customer and Vehicle Type!')
                    return redirect(request.META['HTTP_REFERER'])


                # Calculate Loading & Unloading Charge
                total_weight = Warehouse_goods_info.objects.filter(wh_goods_invoice=k).aggregate(Sum('wh_goods_weight'))['wh_goods_weight__sum']
                no_of_pieces = Warehouse_goods_info.objects.filter(wh_goods_invoice=k).aggregate(Sum('wh_goods_pieces'))['wh_goods_pieces__sum']
                try:
                    weight_per_piece = round((total_weight) / (no_of_pieces),2)
                except ZeroDivisionError:
                    weight_per_piece = float(0.0)

                if customer_type_id==2:
                    piece_rate_val = 0
                    total_loading_cost = piece_rate_val * no_of_pieces
                else:
                    try:
                        piece_rate = WhratemasterInfo.objects.get(whrm_customer_name=customer_id,whrm_min_wt__lte=weight_per_piece,whrm_max_wt__gt=weight_per_piece, whrm_charge_type=3)
                        piece_rate_val = piece_rate.whrm_rate
                        total_loading_cost = piece_rate_val * no_of_pieces
                    except ObjectDoesNotExist:
                        messages.error(request,'Loading/Unloading Charges not available in master for selected Customer!')
                        return redirect(request.META['HTTP_REFERER'])

                # Calculate Crane and Forklift cost
                try:
                    crane_hours = Loadingbay_Info.objects.get(lb_invoice=k).lb_crane_time
                    forklift_hours = Loadingbay_Info.objects.get(lb_invoice=k).lb_forklift_time
                    forklift_charge_l2h = Loadingbay_Info.objects.get(lb_invoice=k).lb_forklift_charges_mod_l2h
                    forklift_charge_g2h = Loadingbay_Info.objects.get(lb_invoice=k).lb_forklift_charges_mod_g2hr
                    crane_charge_l2h = Loadingbay_Info.objects.get(lb_invoice=k).lb_crane_charges_mod_l2h
                    crane_charge_g2h = Loadingbay_Info.objects.get(lb_invoice=k).lb_crane_charges_mod_g2hr
                    no_of_cranes = Loadingbay_Info.objects.get(lb_invoice=k).lb_no_of_crane
                    no_of_forklifts = Loadingbay_Info.objects.get(lb_invoice=k).lb_no_of_forklift
                except ObjectDoesNotExist:
                    crane_hours = 0
                    forklift_hours = 0
                    forklift_charge_l2h = 0
                    forklift_charge_g2h = 0
                    crane_charge_l2h = 0
                    crane_charge_g2h = 0
                    no_of_cranes = 0
                    no_of_forklifts = 0
                if crane_hours <= 2 and forklift_hours <= 2:
                    print("inside Condition 1")
                    crane_cost_l2hr = round((2 * crane_charge_l2h * no_of_cranes), 2)
                    crane_cost_g2hr = 0
                    forklift_cost_l2hr = round((2 * forklift_charge_l2h * no_of_forklifts), 2)
                    forklift_cost_g2hr = 0
                    crane_cost = crane_cost_l2hr + crane_cost_g2hr
                    forklift_cost = forklift_cost_l2hr + forklift_cost_g2hr
                elif forklift_hours <= 2 and crane_hours > 2:
                    print("inside Condition 3")
                    crane_hours_aft_2 = int(crane_hours) - 2
                    crane_cost_l2hr = round((2 * crane_charge_l2h * no_of_cranes), 2)
                    crane_cost_g2hr = round((crane_charge_g2h * crane_hours_aft_2 * no_of_cranes), 2)
                    forklift_cost_l2hr = round((2 * forklift_charge_l2h * no_of_forklifts), 2)
                    forklift_cost_g2hr = 0

                    crane_cost = crane_cost_l2hr + crane_cost_g2hr
                    forklift_cost = forklift_cost_l2hr + forklift_cost_g2hr
                elif crane_hours <= 2 and forklift_hours > 2:
                    print("inside Condition 4")
                    forklift_hours_aft_2 = forklift_hours - 2
                    crane_cost_l2hr = round((2 * crane_charge_l2h * no_of_cranes), 2)
                    crane_cost_g2hr = 0
                    forklift_cost_l2hr = round((2 * forklift_charge_l2h * no_of_forklifts), 2)
                    forklift_cost_g2hr = round((forklift_charge_g2h * forklift_hours_aft_2 * no_of_forklifts), 2)

                    crane_cost = crane_cost_l2hr + crane_cost_g2hr
                    forklift_cost = forklift_cost_l2hr + forklift_cost_g2hr
                else:
                    print("inside Condition 5")
                    crane_hours_aft_2 = int(crane_hours) - 2
                    forklift_hours_aft_2 = forklift_hours - 2
                    crane_cost_l2hr = round((2 * crane_charge_l2h * no_of_cranes), 2)
                    crane_cost_g2hr = round((crane_charge_g2h * crane_hours_aft_2 * no_of_cranes), 2)
                    forklift_cost_l2hr = round((2 * forklift_charge_l2h * no_of_forklifts), 2)
                    forklift_cost_g2hr = round((forklift_charge_g2h * forklift_hours_aft_2 * no_of_forklifts), 2)

                    crane_cost = crane_cost_l2hr + crane_cost_g2hr
                    forklift_cost = forklift_cost_l2hr + forklift_cost_g2hr

                invoice_id = list(Warehouse_goods_info.objects.filter(wh_goods_invoice=k).values_list('id',flat=True))
                invoice_id.sort()
                for i in range(0, len(invoice_id)):
                    if i == 0:
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_storage_cost_per_day=warehouse_charge_1)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_storage_cost_total=storage_cost_total)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_crane_cost_l2h=crane_cost_l2hr)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_crane_cost_g2h=crane_cost_g2hr)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_crane_cost=crane_cost)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_forklift_cost_l2hr=forklift_cost_l2hr)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_forklift_cost_g2hr=forklift_cost_g2hr)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_forklift_cost=forklift_cost)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_loading_charge_unit=piece_rate_val)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_total_loading_cost=total_loading_cost)
                    else:
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_storage_cost_per_day=0)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update( wh_storage_cost_total=0)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_crane_cost_l2h=0)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_crane_cost_g2h=0)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_crane_cost=0)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_forklift_cost_l2hr=0)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_forklift_cost_g2hr=0)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_forklift_cost=0)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_loading_charge_unit=0)
                        Warehouse_goods_info.objects.filter(pk=invoice_id[i]).update(wh_total_loading_cost=0)
            messages.success(request, 'Invoice List Updated Successfully!')

            # Total Cost calculation
            shipper_invoice_list = Warehouse_goods_info.objects.filter(wh_voucher_num = voucher_num)
            weight_sum=Warehouse_goods_info.objects.filter(wh_voucher_num = voucher_num).aggregate(Sum('wh_goods_weight'))['wh_goods_weight__sum']
            crane_cost_sum=Warehouse_goods_info.objects.filter(wh_voucher_num = voucher_num).aggregate(Sum('wh_crane_cost'))['wh_crane_cost__sum']
            forklift_cost_sum=Warehouse_goods_info.objects.filter(wh_voucher_num = voucher_num).aggregate(Sum('wh_forklift_cost'))['wh_forklift_cost__sum']
            wh_storage_cost_sum=Warehouse_goods_info.objects.filter(wh_voucher_num = voucher_num).aggregate(Sum('wh_storage_cost_total'))['wh_storage_cost_total__sum']
            no_of_days=Warehouse_goods_info.objects.filter(wh_voucher_num = voucher_num).aggregate(Max('wh_storage_time'))['wh_storage_time__max']
            no_of_pieces=Warehouse_goods_info.objects.filter(wh_voucher_num = voucher_num).aggregate(Sum('wh_goods_pieces'))['wh_goods_pieces__sum']
            total_loading_cost=Warehouse_goods_info.objects.filter(wh_voucher_num = voucher_num).aggregate(Sum('wh_total_loading_cost'))['wh_total_loading_cost__sum']

            job_num = (Warehouse_goods_info.objects.filter(wh_voucher_num=voucher_num).distinct().values_list('wh_job_no',flat=True))
            crane_time=0
            forklift_time=0
            for i in job_num:
                crane_time=crane_time+Loadingbay_Info.objects.get(lb_job_no=i).lb_crane_time
                forklift_time=forklift_time+Loadingbay_Info.objects.get(lb_job_no=i).lb_forklift_time
            context= {
                'user_id':user_id,
                'invoice_form': invoice_form,
                'first_name': first_name,
                'shipper_invoice_list':shipper_invoice_list,
                'weight_sum':weight_sum,
                # 'no_of_days':no_of_days,
                'no_of_days':max_storage_days,
                'no_of_pieces':no_of_pieces,
                'crane_time':crane_time,
                'forklift_time':forklift_time,
                'min_check_in_time':str(min_check_in_time),
                'max_check_out_time':str(max_check_out_time),
                'total_loading_cost':total_loading_cost,
                'wh_storage_cost_sum':wh_storage_cost_sum,
                'crane_cost_sum':crane_cost_sum,
                'forklift_cost_sum':forklift_cost_sum,
                }
        return render(request, "asset_mgt_app/invoice_add.html", context)
    else:
        if invoice_id == 0:
            invoice_form = InvoiceaddForm(request.POST)
            if invoice_form.is_valid():
                invoice_form.save()
                print("Main Form Saved")
                messages.success(request, 'Record Addedd Successfully!')
            else:
                print("Main Form Not Saved")
                messages.error(request, 'Check all mandatory fields!')
            return redirect('/SMS/invoice_list')
        else:
            invoice = BilingInfo.objects.get(pk=invoice_id)
            invoice_form = InvoiceaddForm(request.POST, instance=invoice)
            if invoice_form.is_valid():
                invoice_form.save()
                print("Main Form Saved")
                messages.success(request, 'Record Updated Successfully!')
                voucher_num_val = BilingInfo.objects.get(pk=invoice_id).bill_invoice_ref
                # update total invoice cost in warehouse goods table
                stock_id = list(
                    Warehouse_goods_info.objects.filter(wh_voucher_num=voucher_num_val).values_list('id', flat=True))
                total_invoice_cost = BilingInfo.objects.get(bill_invoice_ref=voucher_num_val).bill_total_post_gst
                stock_id.sort()
                for i in range(0, len(stock_id)):
                    if i == 0:
                        Warehouse_goods_info.objects.filter(pk=stock_id[i]).update(
                            wh_total_invoice_cost=total_invoice_cost)
                    else:
                        Warehouse_goods_info.objects.filter(pk=stock_id[i]).update(wh_total_invoice_cost=0)
            else:
                print("Main Form Not Saved")
                messages.error(request, 'Check all mandatory fields!')
            return redirect(request.META['HTTP_REFERER'])
            # return redirect('/SMS/invoice_list')
@login_required(login_url='login_page')
def invoice_report(request):
    first_name = request.session.get('first_name')
    goods_list=Warehouse_goods_info.objects.exclude(wh_voucher_num=None)
    context =   {
                'first_name': first_name,
                'goods_list': goods_list,
                }
    return render(request,"asset_mgt_app/invoice_report.html",context)
@login_required(login_url='login_page')
def invoice_list(request):
    first_name = request.session.get('first_name')
    invoice_list_val = BilingInfo.objects.all()
    context =   {
                'invoice_list_val' : invoice_list_val,
                'first_name': first_name,
                }
    return render(request,"asset_mgt_app/invoice_list.html",context)

@login_required(login_url='login_page')
def invoice_delete(request,invoice_id):
    invoice_del = BilingInfo.objects.get(pk=invoice_id)
    invoice_ref=BilingInfo.objects.get(pk=invoice_id).bill_invoice_ref
    wh_jobs=list(Warehouse_goods_info.objects.filter(wh_voucher_num=invoice_ref).values_list('wh_job_no',flat=True))
    for i in wh_jobs:
        Warehouse_goods_info.objects.filter(wh_job_no=i).update(wh_voucher_num=None)
    invoice_del.delete()
    return redirect('/SMS/invoice_list')

@login_required(login_url='login_page')
def shipper_invoice_list(request,voucher_id):
    first_name = request.session.get('first_name')
    voucher_num_val = BilingInfo.objects.get(pk=voucher_id).bill_invoice_ref
    customer_name_val = BilingInfo.objects.get(pk=voucher_id).bill_customer_name
    customer_type = CustomerInfo.objects.get(cu_name=customer_name_val).cu_businessmodel
    customer_type_id = TrbusinesstypeInfo.objects.get(tb_trbusinesstype=customer_type).id
    request.session['ses_voucher_num_val'] = voucher_num_val
    shipper_invoice_list=Warehouse_goods_info.objects.filter(wh_voucher_num=voucher_num_val)
    if customer_type_id==2:
        print("Inside Exclusive Loop")
        invoice_list_master = Warehouse_goods_info.objects.filter(wh_customer_name=customer_name_val,wh_check_in_out=1,wh_voucher_num=None)
    else:
        print("Inside Non Exclusive Loop")
        invoice_list_master = Warehouse_goods_info.objects.filter(wh_customer_name=customer_name_val, wh_check_in_out=2,wh_voucher_num=None)
    context =   {
                'shipper_invoice_list' : shipper_invoice_list,
                'first_name': first_name,
                'invoice_list_master': invoice_list_master,
                }
    return render(request,"asset_mgt_app/shipper_invoice_list.html",context)
@login_required(login_url='login_page')
def shipper_invoice_add(request,voucher_id):
    first_name = request.session.get('first_name')
    voucher_num_val = request.session.get('ses_voucher_num_val')
    Warehouse_goods_info.objects.filter(pk=voucher_id).update(wh_voucher_num=voucher_num_val)
    context =   {
                # 'shipper_invoice_list' : shipper_invoice_list,
                'first_name': first_name,
                # 'invoice_list_master': invoice_list_master,
                }
    return redirect(request.META['HTTP_REFERER'])
    # return render(request,"asset_mgt_app/shipper_invoice_list.html",context)

@login_required(login_url='login_page')
def shipper_invoice_remove(request,voucher_id):
    first_name = request.session.get('first_name')
    Warehouse_goods_info.objects.filter(pk=voucher_id).update(wh_voucher_num=None)
    context =   {
                'first_name': first_name,
                }
    return redirect(request.META['HTTP_REFERER'])
    # return render(request,"asset_mgt_app/shipper_invoice_list.html",context)

@login_required(login_url='login_page')
def load_whrate_model(request):
    lm_customer_name_id = request.GET.get('lm_customer_name_id')
    print('lm_customer_name_id',lm_customer_name_id)
    customer_businessmodel = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_businessmodel')
    customer_short_name = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_nameshort')
    customer_code = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_customercode')
    customer_GST = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_gst')
    customer_person = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_customerperson')
    customer_contact = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_contactno')
    customer_address = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_address')
    customer_businessmodel_val=customer_businessmodel[0]['cu_businessmodel'] #Get value from Queryset
    customer_short_name_val=customer_short_name[0]['cu_nameshort'] #Get value from Queryset
    customer_code_val=customer_code[0]['cu_customercode'] #Get value from Queryset
    customer_GST_val=customer_GST[0]['cu_gst'] #Get value from Queryset
    customer_person_val=customer_person[0]['cu_customerperson'] #Get value from Queryset
    customer_contact_val = customer_contact[0]['cu_contactno']  # Get value from Queryset
    customer_address_val = customer_address[0]['cu_address']  # Get value from Queryset
    data = {
        'customer_businessmodel_val':customer_businessmodel_val,
        'customer_short_name_val':customer_short_name_val,
        'customer_code_val':customer_code_val,
        'customer_GST_val':customer_GST_val,
        'customer_person_val':customer_person_val,
        'customer_contact_val':customer_contact_val,
        'customer_address_val':customer_address_val,
    }
    return HttpResponse(json.dumps(data))

@login_required(login_url='login_page')
def case_to_case_invoice_list_open(request):
    first_name = request.session.get('first_name')
    case_to_case = str(TrbusinesstypeInfo.objects.get(id=1))
    open_invoice_list=Warehouse_goods_info.objects.filter(wh_voucher_num=None,wh_check_in_out=2,wh_customer_type=case_to_case)
    context={
        'open_invoice_list':open_invoice_list,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/invoice_list_open.html", context)\

@login_required(login_url='login_page')
def dedicated_invoice_list_open(request):
    first_name = request.session.get('first_name')
    dedicated = str(TrbusinesstypeInfo.objects.get(id=3))
    open_invoice_list=Warehouse_goods_info.objects.filter(wh_voucher_num=None,wh_check_in_out=2,wh_customer_type=dedicated)
    context={
        'open_invoice_list':open_invoice_list,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/invoice_list_open.html", context)\

@login_required(login_url='login_page')
def exclusive_invoice_list_open(request):
    first_name = request.session.get('first_name')
    exlcusive = str(TrbusinesstypeInfo.objects.get(id=2))
    open_invoice_list=Warehouse_goods_info.objects.filter(wh_voucher_num=None,wh_check_in_out=1,wh_customer_type=exlcusive)
    context={
        'open_invoice_list':open_invoice_list,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/invoice_list_open.html", context)
@login_required(login_url='login_page')
def invoice_list_query(request):
    first_name = request.session.get('first_name')
    context = {
        'first_name': first_name,
    }
    return render(request,"asset_mgt_app/invoice_list.html",context)
