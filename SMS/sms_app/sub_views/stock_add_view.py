from django.contrib.auth.decorators import login_required
from ..forms import StockaddForm
from ..models import Warehouse_stock_info,Warehouse_goods_info
from django.shortcuts import render, redirect

# List stocks
@login_required(login_url='login_page')
def stock_list(request):
    first_name = request.session.get('first_name')
    context = {'stock_list': Warehouse_stock_info.objects.all(),'first_name': first_name}
    return render(request, "asset_mgt_app/stock_list.html", context)


# Add stocks
@login_required(login_url='login_page')
def stock_add(request, stock_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if stock_id == 0:
            form = StockaddForm()
            context = {
                'form': form
            }
        else:
            stockinfo = Warehouse_stock_info.objects.get(pk=stock_id)
            invoice_num_stock= stockinfo.wh_stock_invoice
            request.session['invoice_num_stock'] = invoice_num_stock
            request.session['stock_id'] = stock_id
            print(invoice_num_stock,stock_id)
            form = StockaddForm(instance=stockinfo)
            context={
                'form': form,
                'goods_list': Warehouse_goods_info.objects.filter(wh_goods_invoice=invoice_num_stock),
                'first_name': first_name,
            }
        return render(request, "asset_mgt_app/stock_add.html", context)
    else:
        if stock_id == 0:
            form = StockaddForm(request.POST)
        else:
           stockinfo = Warehouse_stock_info.objects.get(pk=stock_id)
           form = StockaddForm(request.POST, instance=stockinfo)
        if form.is_valid():
            form.save()
        return redirect('/SMS/stock_list')


# Delete stocks
@login_required(login_url='login_page')
def stock_delete(request, stock_id):
    stockinfo = Warehouse_stock_info.objects.get(pk=stock_id)
    stockinfo.delete()
    return redirect('/SMS/stock_list')