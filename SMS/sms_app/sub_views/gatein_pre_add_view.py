from django.db import transaction
from django.shortcuts import render, redirect
from ..forms import Gatein_preaddForm,Gatein_pre_att_Form
from django.contrib.auth.decorators import login_required
from ..models import Gatein_pre_info,Pre_checkin_att,Loadingbay_Info,DamagereportInfo,Warehouse_goods_info,DamagereportImages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

# Add WH Job
@transaction.atomic
@login_required(login_url='login_page')
def gatein_pre_add(request, gatein_pre_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    gatein_pre_number_sess=request.POST.get('gatein_pre_number')
    if request.method == "GET":
        if gatein_pre_id == 0:
            print("I am inside Get add Gatein")
            gatein_pre_form = Gatein_preaddForm()
            gatein_pre_att_form=Gatein_pre_att_Form()
        else:
            print("I am inside get edit Gatein")
            print('pre_gate_in Number', gatein_pre_number_sess)
            gatein_pre_info = Gatein_pre_info.objects.get(pk=gatein_pre_id)
            gatein_pre_form = Gatein_preaddForm(instance=gatein_pre_info)
            gatein_pre_att_info=Pre_checkin_att.objects.get(pre_att_gatein_pre_number=gatein_pre_number_sess)
            gatein_pre_att_form=Gatein_pre_att_Form(request.FILES, instance=gatein_pre_att_info)

        context = {
            'first_name': first_name,
            'gatein_pre_form': gatein_pre_form,
            'gatein_pre_att_form':gatein_pre_att_form,
            'user_id': user_id,
        }
        return render(request, "asset_mgt_app/gatein_pre_add.html", context)
    else:
        if gatein_pre_id == 0:
            print("I am inside post add Gatein")
            gatein_pre_form = Gatein_preaddForm(request.POST)
            gatein_pre_att_form = Gatein_pre_att_Form(request.POST)
        else:
            print("I am inside post edit Gatein")
            print('pre_gate_in Number',gatein_pre_number_sess)
            gatein_pre_info = Gatein_pre_info.objects.get(pk=gatein_pre_id)
            gatein_pre_form = Gatein_preaddForm(request.POST, instance=gatein_pre_info)
            gatein_pre_att_info = Pre_checkin_att.objects.get(pre_att_gatein_pre_number=gatein_pre_number_sess)
            gatein_pre_att_form = Gatein_pre_att_Form(request.POST, request.FILES, instance=gatein_pre_att_info)
        if gatein_pre_form.is_valid():
            print("Main Form is Valid")
            gatein_pre_form.save()
        else:
            print("Main Form is In-Valid")

        if gatein_pre_att_form.is_valid():
            print("Sub Form is Valid")
            gatein_pre_att_form.save()
        else:
            print("Sub Form is In-Valid")
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


