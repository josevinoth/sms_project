from django.contrib.auth.decorators import login_required
from ..forms import CityaddForm
from ..models import Warehouse_goods_info,Gatein_info
from django.shortcuts import render, redirect

# Invoicecity
@login_required(login_url='login_page')
def invoice_list(request):
    final_invoice_list=[]
    matching_invoice_list=[]
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
            final_invoice_list.append(matching_invoice_list[j])

    # Final list of Invoices checked-out
    print('final_invoice_list',final_invoice_list)

    context = {
        'invoice_list' : Warehouse_goods_info.objects.all(),
        'first_name': first_name,
    }
    return render(request,"asset_mgt_app/invoice_list.html",context)
