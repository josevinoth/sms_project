from django.contrib.auth.decorators import login_required
from ..forms import GoodsaddForm
from ..models import Warehouse_goods_info
from django.shortcuts import render, redirect

# List goods
@login_required(login_url='login_page')
def goods_list(request):
    first_name = request.session.get('first_name')
    context = {'goods_list': Warehouse_goods_info.objects.all(),'first_name': first_name}
    return render(request, "asset_mgt_app/goods_list.html", context)


# Add goods
@login_required(login_url='login_page')
def goods_add(request, goods_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if goods_id == 0:
            form = GoodsaddForm()
        else:
            goodsinfo = Warehouse_goods_info.objects.get(pk=goods_id)
            form = GoodsaddForm(instance=goodsinfo)
        return render(request, "asset_mgt_app/goods_add.html", {'form': form,'first_name': first_name})
    else:
        if goods_id == 0:
            form = GoodsaddForm(request.POST)
        else:
            goodsinfo = Warehouse_goods_info.objects.get(pk=goods_id)
            form = GoodsaddForm(request.POST, instance=goodsinfo)
        if form.is_valid():
            form.save()
        return redirect('/SMS/stock_list')


# Delete goods
@login_required(login_url='login_page')
def goods_delete(request, goods_id):
    goodsinfo = Warehouse_goods_info.objects.get(pk=goods_id)
    goodsinfo.delete()
    return redirect('/SMS/goods_list')