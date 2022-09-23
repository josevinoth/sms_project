from itertools import chain

from django.contrib.auth.decorators import login_required
from ..forms import CityaddForm
from ..models import Warehouse_goods_info,Gatein_info
from django.shortcuts import render, redirect

# Invoicecity
@login_required(login_url='login_page')
def invoice_list(request):
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

    # Get invoice list from Gate-In table
    invoice_list=Gatein_info.objects.all().values_list('gatein_invoice',flat=True)
    print('invoice_list',invoice_list)

    # Get invoice list from WH_Goods Table
    invoice_goods_list=Warehouse_goods_info.objects.all().values_list('wh_goods_invoice',flat=True)
    print('invoice_goods_list',invoice_goods_list)

    # Check invoice from Gate-in list inside WH_Goods list
    for i in range(0,len(invoice_list)):
        print(invoice_list[i])
        if invoice_list[i] in invoice_goods_list:
            print("In list")
            matching_invoice_list.append(invoice_list[i])
        else:
            print("Not in list")

    # store matching invoice as list
    print('matching_invoice_list',matching_invoice_list)

    # For matching invoices get check-In-Out Status
    for j in range(0,len(matching_invoice_list)):
        goods_check_in_out_list=(Warehouse_goods_info.objects.filter(wh_goods_invoice=matching_invoice_list[j])).values_list('wh_check_in_out',flat=True)
        print('goods_check_in_out_list',goods_check_in_out_list)
        # Get all invoice which are checked out
        if all(status == 2 for status in (goods_check_in_out_list)):
            checkedout_invoice_list.append(matching_invoice_list[j])

    # Final list of Invoices checked-out
    print('Checked_Out-invoice_list',checkedout_invoice_list)

    # Get desired elements for list of Invoices checked-out
    for k in checkedout_invoice_list:
        wh_job_num_list.append((Gatein_info.objects.get(gatein_invoice=k).gatein_job_no))
        customer_invoice_list.append((Gatein_info.objects.get(gatein_invoice=k).gatein_invoice))
        customer_name_list.append((Gatein_info.objects.get(gatein_invoice=k).gatein_customer))
        customer_type_list.append((Gatein_info.objects.get(gatein_invoice=k).gatein_customer_type))
        consigner_list.append((Gatein_info.objects.get(gatein_invoice=k).gatein_shipper))
        consignee_list.append((Gatein_info.objects.get(gatein_invoice=k).gatein_consignee))

    print('wh_job_num_list',wh_job_num_list)
    print('gatein_invoice_list',customer_invoice_list)
    print('customer_name_list',customer_name_list)
    print('customer_type_list',customer_type_list)
    print('consigner_list',consigner_list)
    print('consignee_list',consignee_list)

    # Get min start date and max end date for an invoice
    for inv in checkedout_invoice_list:
        print('inv',inv)
        start_date_list.append(min(Warehouse_goods_info.objects.filter(wh_goods_invoice=inv).values_list('wh_checkin_time', flat=True)))
        end_date_list.append(max(Warehouse_goods_info.objects.filter(wh_goods_invoice=inv).values_list('wh_checkout_time', flat=True)))
    print('start_date_list',start_date_list)
    print('end_date_list',end_date_list)
    invoice_list_final=[]
    for k in checkedout_invoice_list:
        print(k)
        invoice_list=Warehouse_goods_info.objects.filter(wh_goods_invoice=k)
        invoice_list_final.append(invoice_list)
    print('invoice_list',invoice_list)
    print('invoice_list_final',invoice_list_final)

    for inv in checkedout_invoice_list:
        final_goods_list.append(Gatein_info.objects.filter(gatein_invoice=inv).all())
    print(final_goods_list)
    context = {
        'invoice_list' : checkedout_invoice_list,
        'first_name': first_name,
        'checkedout_invoice_list': checkedout_invoice_list,
        'wh_job_num_list': wh_job_num_list,
        'customer_invoice_list':customer_invoice_list,
        'customer_name_list': customer_name_list,
        'customer_type_list': customer_type_list,
        'consigner_list': consigner_list,
        'consignee_list': consignee_list,
        'len':len(wh_job_num_list),
    }
    return render(request,"asset_mgt_app/invoice_list.html",context)
