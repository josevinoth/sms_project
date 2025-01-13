from django.contrib.auth.decorators import login_required
from ..forms import warehouse_goodsadd_gatein_form,CityaddForm
from ..models import warehouse_goodsnew_info
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def warehouse_goods_add_gatein(request,wh_goods_gatein_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if wh_goods_gatein_id == 0:
            wh_goods_gatein_form = warehouse_goodsadd_gatein_form()
        else:
            wh_goods_gatein=warehouse_goodsnew_info.objects.get(pk=wh_goods_gatein_id)
            wh_goods_gatein_form = warehouse_goodsadd_gatein_form(instance=wh_goods_gatein)
        context={
                'wh_goods_gatein_form': wh_goods_gatein_form,
                'first_name': first_name,
                }
        return render(request, "asset_mgt_app/warehouse_jobs_add.html",context )
    else:
        if wh_goods_gatein_id == 0:
            wh_goods_gatein_form = warehouse_goodsadd_gatein_form(request.POST)
        else:
            wh_goods_gatein = warehouse_goodsnew_info.objects.get(pk=wh_goods_gatein_id)
            wh_goods_gatein_form = CityaddForm(request.POST,instance=wh_goods_gatein)
        if wh_goods_gatein_form.is_valid():
            wh_goods_gatein_form.save()
        return redirect('/SMS/city_list')

# # List city
# @login_required(login_url='login_page')
# def city_list(request):
#     first_name = request.session.get('first_name')
#     context = {'city_list' : City.objects.all(),'first_name': first_name}
#     return render(request,"asset_mgt_app/city_list.html",context)
#
# #Delete city
# @login_required(login_url='login_page')
# def city_delete(request,city_id):
#     city = City.objects.get(pk=city_id)
#     city.delete()
#     return redirect('/SMS/city_list')