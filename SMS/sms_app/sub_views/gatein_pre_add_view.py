from django.db import transaction
from django.shortcuts import render, redirect
from ..forms import Gatein_preaddForm
from django.contrib.auth.decorators import login_required
from ..models import Gatein_pre_info,Loadingbay_Info,DamagereportInfo,Warehouse_goods_info,DamagereportImages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

# Add WH Job
@transaction.atomic
@login_required(login_url='login_page')
def gatein_pre_add(request, gatein_pre_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if gatein_pre_id == 0:
            print("I am inside Get add Gatein")
            gatein_pre_form = Gatein_preaddForm()
            context = {
                'first_name': first_name,
                'gatein_pre_form': gatein_pre_form,
            }
        else:
            print("I am inside get edit Gatein")
            gatein_pre_info = Gatein_pre_info.objects.get(pk=gatein_pre_id)
            gatein_pre_form = Gatein_preaddForm(instance=gatein_pre_info)
            context = {
                'gatein_pre_form': gatein_pre_form,
                'first_name': first_name,
            }
        return render(request, "asset_mgt_app/gatein_pre_add.html", context)
    else:
        if gatein_pre_id == 0:
            print("I am inside post add Gatein")
            gatein_pre_form = Gatein_preaddForm(request.POST)
        else:
            print("I am inside post edit Gatein")
            gatein_pre_info = Gatein_pre_info.objects.get(pk=gatein_pre_id)
            gatein_pre_form = Gatein_preaddForm(request.POST, instance=gatein_pre_info)
        if gatein_pre_form.is_valid():
            print("Form is Valid")
            gatein_pre_form.save()
        else:
            print("Form is In-Valid")
        return redirect('/SMS/gatein_pre_list')
# List WH Job
@login_required(login_url='login_page')
def gatein_pre_list(request):
    first_name = request.session.get('first_name')
    context = {'Gatein_pre_list' : Gatein_pre_info.objects.all(),'first_name': first_name,}
    return render(request,"asset_mgt_app/gatein_pre_list.html",context)

#Delete WH Job
@login_required(login_url='login_page')
def gatein_pre_delete(request,gatein_pre_id):
    gatein_pre_del = Gatein_pre_info.objects.get(pk=gatein_pre_id)
    gatein_pre_del.delete()
    return redirect('/SMS/gatein_pre_list')


