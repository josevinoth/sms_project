from itertools import chain

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.aggregates import Sum, Max
from django.http import HttpResponse
import json
from django.contrib import messages

from ..forms import InvoiceaddForm
from ..models import Loadingbay_Info,TrbusinesstypeInfo,CustomerInfo,Warehouse_goods_info,WhratemasterInfo,BilingInfo
from django.shortcuts import render, redirect

# Invoicecity
@login_required(login_url='login_page')
def invoice_add(request,invoice_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if invoice_id == 0:
            invoice_form = InvoiceaddForm()
            context={
                'invoice_form': invoice_form,
            }
        else:
            invoice = BilingInfo.objects.get(pk=invoice_id)
            invoice_form = InvoiceaddForm(instance=invoice)
            voucher_num = BilingInfo.objects.get(pk=invoice_id).bill_invoice_ref
            shipper_invoice_list = Warehouse_goods_info.objects.filter(wh_voucher_num = voucher_num)
            weight_sum=Warehouse_goods_info.objects.filter(wh_voucher_num = voucher_num).aggregate(Sum('wh_goods_volume_weight'))['wh_goods_volume_weight__sum']
            no_of_days=Warehouse_goods_info.objects.filter(wh_voucher_num = voucher_num).aggregate(Max('wh_storage_time'))['wh_storage_time__max']
            no_of_pieces=Warehouse_goods_info.objects.filter(wh_voucher_num = voucher_num).aggregate(Sum('wh_goods_pieces'))['wh_goods_pieces__sum']
            print('weight_sum',weight_sum)
            print('no_of_days',no_of_days)
            context= {
                'user_id':user_id,
                'invoice_form': invoice_form,
                'first_name': first_name,
                'shipper_invoice_list':shipper_invoice_list,
                'weight_sum':weight_sum,
                'no_of_days':no_of_days,
                'no_of_pieces':no_of_pieces,
                }
        return render(request, "asset_mgt_app/invoice_add.html", context)
    else:
        if invoice_id == 0:
            invoice_form = InvoiceaddForm(request.POST)
        else:
            invoice = BilingInfo.objects.get(pk=invoice_id)
            invoice_form = InvoiceaddForm(request.POST, instance=invoice)

        if invoice_form.is_valid():
            invoice_form.save()
            print("Main Form Saved")
        else:
            print("Main Form Not Saved")
        return redirect('/SMS/invoice_list')
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
    invoice_del.delete()
    return redirect('/asset_mgt_app/invoice_list')

@login_required(login_url='login_page')
def shipper_invoice_list(request,voucher_id):
    first_name = request.session.get('first_name')
    voucher_num_val = BilingInfo.objects.get(pk=voucher_id).bill_invoice_ref
    customer_name_val = BilingInfo.objects.get(pk=voucher_id).bill_customer_name
    request.session['ses_voucher_num_val'] = voucher_num_val
    print(voucher_num_val)
    print(customer_name_val)
    shipper_invoice_list=Warehouse_goods_info.objects.filter(wh_voucher_num=voucher_num_val)
    invoice_list_master = Warehouse_goods_info.objects.filter(wh_customer_name=customer_name_val,wh_check_in_out=2,wh_voucher_num=None)
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
    voucher_num_update=Warehouse_goods_info.objects.filter(pk=voucher_id).update(wh_voucher_num=voucher_num_val)
    shipper_invoice_list=Warehouse_goods_info.objects.filter(wh_voucher_num=voucher_num_val)
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
    total_weight = request.GET.get('total_weight')
    no_of_pieces = request.GET.get('no_of_pieces')
    voucher_num = request.GET.get('voucher_num')
    weight_per_piece=(float(total_weight)/float(no_of_pieces))
    customer_id=CustomerInfo.objects.get(cu_name=lm_customer_name_id).id
    print(customer_id)
    customer_businessmodel = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_businessmodel')
    customer_short_name = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_nameshort')
    customer_code = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_customercode')
    customer_GST = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_gst')
    customer_person = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_customerperson')
    customer_contact = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_contactno')
    customer_address = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_address')
    print('customer_businessmodel',customer_businessmodel)
    customer_businessmodel_val=customer_businessmodel[0]['cu_businessmodel'] #Get value from Queryset
    customer_short_name_val=customer_short_name[0]['cu_nameshort'] #Get value from Queryset
    customer_code_val=customer_code[0]['cu_customercode'] #Get value from Queryset
    customer_GST_val=customer_GST[0]['cu_gst'] #Get value from Queryset
    customer_person_val=customer_person[0]['cu_customerperson'] #Get value from Queryset
    customer_contact_val = customer_contact[0]['cu_contactno']  # Get value from Queryset
    customer_address_val = customer_address[0]['cu_address']  # Get value from Queryset
    print('customer_businessmodel_val',customer_businessmodel_val)
    lm_customer_model_id=TrbusinesstypeInfo.objects.filter(id=customer_businessmodel_val).values('tb_trbusinesstype')
    customer_businessmodel_txt= lm_customer_model_id[0]['tb_trbusinesstype']  # Get value from Queryset
    # WH Charge
    wh_rate = WhratemasterInfo.objects.filter(whrm_customer_name=customer_id, whrm_max_wt__lte=total_weight,whrm_min_wt__gte=total_weight, whrm_charge_type=1).values('whrm_rate')
    if wh_rate:
        wh_rate_val = wh_rate[0]['whrm_rate']
    else:
        wh_rate_val = 0.0

    # Loading_unloading charge
    piece_rate = WhratemasterInfo.objects.filter(whrm_customer_name=customer_id, whrm_max_wt__lte=weight_per_piece,whrm_min_wt__gte=weight_per_piece, whrm_charge_type=3).values('whrm_rate')
    if piece_rate:
        piece_rate_val = piece_rate[0]['whrm_rate']
    else:
        piece_rate_val = 0.0
        # wh_rate = 1

    # Get Crane and forklift time
    wh_job_list= (Warehouse_goods_info.objects.filter(wh_voucher_num=voucher_num).values('wh_job_no').distinct())
    wh_job_list_lb=(Loadingbay_Info.objects.all().values_list('lb_job_no', flat=True))
    crane_time_tot=0
    forklift_time_tot=0
    for a in wh_job_list:
        b=a['wh_job_no']
        if b in wh_job_list_lb:
            crane_time_val=float(Loadingbay_Info.objects.filter(lb_job_no=b).values('lb_crane_time')[0]['lb_crane_time'])
            forklift_time_val=float(Loadingbay_Info.objects.filter(lb_job_no=b).values('lb_forklift_time')[0]['lb_forklift_time'])
            crane_time_tot=crane_time_tot+crane_time_val
            forklift_time_tot=forklift_time_tot+forklift_time_val
    print('crane_time_tot',crane_time_tot)
    print('forklift_time_tot',forklift_time_tot)

    forklift_2hr = WhratemasterInfo.objects.filter(whrm_customer_name=customer_id, whrm_charge_type=4).values('whrm_rate')
    if forklift_2hr:
        forklift_2hr_val = forklift_2hr[0]['whrm_rate']
    else:
        forklift_2hr_val = 0.0
    print('forklift_2hr_val', forklift_2hr_val)

    forklift_aft2hr = WhratemasterInfo.objects.filter(whrm_customer_name=customer_id, whrm_charge_type=7).values('whrm_rate')
    if forklift_aft2hr:
        forklift_aft2hr_val = forklift_aft2hr[0]['whrm_rate']
    else:
        forklift_aft2hr_val = 0.0
    print('forklift_aft2hr_val',forklift_aft2hr_val)

    crane_2hr = WhratemasterInfo.objects.filter(whrm_customer_name=customer_id, whrm_charge_type=5).values(
        'whrm_rate')
    if crane_2hr:
        crane_2hr_val = crane_2hr[0]['whrm_rate']
    else:
        crane_2hr_val = 0.0
    print('crane_2hr_val', crane_2hr_val)

    crane_aft2hr = WhratemasterInfo.objects.filter(whrm_customer_name=customer_id, whrm_charge_type=6).values(
        'whrm_rate')
    if crane_aft2hr:
        crane_aft2hr_val = crane_aft2hr[0]['whrm_rate']
    else:
        crane_aft2hr_val = 0.0
    print('crane_aft2hr_val', crane_aft2hr_val)

    data = {
        'customer_businessmodel_val':customer_businessmodel_val,
        'customer_short_name_val':customer_short_name_val,
        'customer_code_val':customer_code_val,
        'customer_GST_val':customer_GST_val,
        'customer_person_val':customer_person_val,
        'customer_contact_val':customer_contact_val,
        'customer_address_val':customer_address_val,
        'wh_rate_val':wh_rate_val,
        'piece_rate_val':piece_rate_val,
        'crane_time_tot':crane_time_tot,
        'forklift_time_tot':forklift_time_tot,
        'forklift_2hr_val':forklift_2hr_val,
        'forklift_aft2hr_val':forklift_aft2hr_val,
        'crane_2hr_val':crane_2hr_val,
        'crane_aft2hr_val':crane_aft2hr_val,
    }
    return HttpResponse(json.dumps(data))

@login_required(login_url='login_page')
def invoice_list_query(request):
    checkedout_invoice_list=[]
    final_goods_list=[]
    matching_invoice_list=[]
    wh_job_num_list=[]
    customer_invoice_list=[]
    customer_name_list=[]
    customer_type_list=[]
    consigner_list=[]
    consignee_list=[]
    start_date_list=[]
    min_start_date_list=[]
    end_date_list=[]
    max_end_date_list=[]
    checkintime_list=[]
    checkouttime_list=[]
    check_in_out_list=[]
    first_name = request.session.get('first_name')

    # # Get invoice list from Gate-In table
    # invoice_list=Gatein_info.objects.all().values_list('gatein_invoice',flat=True)
    # print('invoice_list',invoice_list)
    #
    # # Get invoice list from WH_Goods Table
    # invoice_goods_list=Warehouse_goods_info.objects.all().values_list('wh_goods_invoice',flat=True)
    # print('invoice_goods_list',invoice_goods_list)
    #
    # # Check invoice from Gate-in list inside WH_Goods list
    # for i in range(0,len(invoice_list)):
    #     print(invoice_list[i])
    #     if invoice_list[i] in invoice_goods_list:
    #         print("In list")
    #         matching_invoice_list.append(invoice_list[i])
    #     else:
    #         print("Not in list")
    #
    # # store matching invoice as list
    # print('matching_invoice_list',matching_invoice_list)
    #
    # # For matching invoices get check-In-Out Status
    # for j in range(0,len(matching_invoice_list)):
    #     goods_check_in_out_list=(Warehouse_goods_info.objects.filter(wh_goods_invoice=matching_invoice_list[j])).values_list('wh_check_in_out',flat=True)
    #     print('goods_check_in_out_list',goods_check_in_out_list)
    #     # Get all invoice which are checked out
    #     if all(status == 2 for status in (goods_check_in_out_list)):
    #         checkedout_invoice_list.append(matching_invoice_list[j])
    #
    # # Final list of Invoices checked-out
    # print('Checked_Out-invoice_list',checkedout_invoice_list)
    #
    # # Get desired elements for list of Invoices checked-out
    # for k in checkedout_invoice_list:
    #     wh_job_num_list.append((Gatein_info.objects.get(gatein_invoice=k).gatein_job_no))
    #     customer_invoice_list.append((Gatein_info.objects.get(gatein_invoice=k).gatein_invoice))
    #     customer_name_list.append((Gatein_info.objects.get(gatein_invoice=k).gatein_customer))
    #     customer_type_list.append((Gatein_info.objects.get(gatein_invoice=k).gatein_customer_type))
    #     consigner_list.append((Gatein_info.objects.get(gatein_invoice=k).gatein_shipper))
    #     consignee_list.append((Gatein_info.objects.get(gatein_invoice=k).gatein_consignee))
    #
    # print('wh_job_num_list',wh_job_num_list)
    # print('gatein_invoice_list',customer_invoice_list)
    # print('customer_name_list',customer_name_list)
    # print('customer_type_list',customer_type_list)
    # print('consigner_list',consigner_list)
    # print('consignee_list',consignee_list)
    #
    # # Get min start date and max end date for an invoice
    # for inv in checkedout_invoice_list:
    #     print('inv',inv)
    #     start_date_list.append(min(Warehouse_goods_info.objects.filter(wh_goods_invoice=inv).values_list('wh_checkin_time', flat=True)))
    #     end_date_list.append(max(Warehouse_goods_info.objects.filter(wh_goods_invoice=inv).values_list('wh_checkout_time', flat=True)))
    # print('start_date_list',start_date_list)
    # print('end_date_list',end_date_list)
    # invoice_list_final=[]
    # for k in checkedout_invoice_list:
    #     print(k)
    #     invoice_list=Warehouse_goods_info.objects.filter(wh_goods_invoice=k)
    #     invoice_list_final.append(invoice_list)
    # print('invoice_list',invoice_list)
    # print('invoice_list_final',invoice_list_final)
    #
    # for inv in checkedout_invoice_list:
    #     final_goods_list.append(Gatein_info.objects.filter(gatein_invoice=inv).all())
    # print(final_goods_list)
    context = {
        'first_name': first_name,
        # 'invoice_list' : checkedout_invoice_list,
        # 'checkedout_invoice_list': checkedout_invoice_list,
        # 'wh_job_num_list': wh_job_num_list,
        # 'customer_invoice_list':customer_invoice_list,
        # 'customer_name_list': customer_name_list,
        # 'customer_type_list': customer_type_list,
        # 'consigner_list': consigner_list,
        # 'consignee_list': consignee_list,
        # 'len':len(wh_job_num_list),
    }
    return render(request,"asset_mgt_app/invoice_list.html",context)
