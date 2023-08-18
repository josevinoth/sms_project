from random import randint

from django.db import transaction
from django.shortcuts import render, redirect
from ..forms import Gatein_preaddForm,Gatein_pre_att_addForm,GateinaddForm
from django.contrib.auth.decorators import login_required
from ..models import Gatein_info,Gatein_pre_info,Gatein_pre_info_att,Loadingbay_Info,DamagereportInfo,Warehouse_goods_info,DamagereportImages
from ..models import User_extInfo,Location_info
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

# Add WH Job
@transaction.atomic
@login_required(login_url='login_page')
def gatein_pre_add(request, gatein_pre_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    user_branch = User_extInfo.objects.get(user_id=user_id).emp_branch
    user_branch_id=Location_info.objects.get(loc_name=user_branch).id
    if request.method == "GET":
        if gatein_pre_id == 0:
            print("I am inside Get add Gatein")
            gatein_pre_form = Gatein_preaddForm()
            gatein_preimg_form = Gatein_pre_att_addForm()
        else:
            gatein_pre_number_sess=Gatein_pre_info.objects.get(pk=gatein_pre_id).gatein_pre_number
            request.session['gatein_pre_number_sess'] = gatein_pre_number_sess
            gatein_pre_info = Gatein_pre_info.objects.get(pk=gatein_pre_id)
            gatein_pre_form = Gatein_preaddForm(instance=gatein_pre_info)
            gatein_preimg_info=Gatein_pre_info_att.objects.get(gatein_pre_number_att=gatein_pre_number_sess)
            gatein_preimg_form = Gatein_pre_att_addForm(request.FILES,instance=gatein_preimg_info)
        context = {
            'first_name': first_name,
            'gatein_pre_form': gatein_pre_form,
            'gatein_preimg_form': gatein_preimg_form,
            'user_branch_id': user_branch_id,
            'user_id': user_id,
        }
        return render(request, "asset_mgt_app/gatein_pre_add.html", context)
    else:
        if gatein_pre_id == 0:
            print("I am inside post add Gatein")
            gatein_pre_form = Gatein_preaddForm(request.POST)
            gatein_preimg_form = Gatein_pre_att_addForm(request.POST,request.FILES)
            if gatein_pre_form.is_valid():
                print("Main Form is Valid")
                # Generate Random pre-gatein number
                try:
                    last_id = (Gatein_pre_info.objects.values_list('id', flat=True)).last()
                    pre_gatein_num = (int((Gatein_pre_info.objects.get(id=last_id)).gatein_pre_number) + 1)
                except ObjectDoesNotExist:
                    pre_gatein_num = (randint(10000, 99999))
                gatein_pre_form.save()
                last_id = (Gatein_pre_info.objects.values_list('id', flat=True)).last()
                last_id_img = (Gatein_pre_info_att.objects.values_list('id', flat=True)).last()
                Gatein_pre_info.objects.filter(id=last_id).update(gatein_pre_number=pre_gatein_num)
                messages.success(request, 'Record Updated Successfully')
                job_id = Gatein_pre_info.objects.get(gatein_pre_number=pre_gatein_num).id
                url = 'gatein_pre_update/' + str(job_id)

                if gatein_preimg_form.is_valid():
                    print("Sub Form is Valid")
                    gatein_preimg_form.save()
                    Gatein_pre_info_att.objects.filter(id=last_id_img + 1).update(gatein_pre_number_att=pre_gatein_num)
                else:
                    print("Sub Form Not Valid")
                return redirect(url)
            else:
                print("Main Form is In-Valid")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("I am inside post edit Gatein")
            gatein_pre_number_sess_val =  request.session['gatein_pre_number_sess']
            gatein_pre_info = Gatein_pre_info.objects.get(pk=gatein_pre_id)
            gatein_pre_form = Gatein_preaddForm(request.POST, instance=gatein_pre_info)
            gatein_preimg_info = Gatein_pre_info_att.objects.get(gatein_pre_number_att=gatein_pre_number_sess_val)
            gatein_preimg_form = Gatein_pre_att_addForm(request.POST,request.FILES, instance=gatein_preimg_info)

            if gatein_pre_form.is_valid():
                print("Main Form is Valid")
                gatein_pre_form.save()
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Main Form is In-Valid")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')

            if gatein_preimg_form.is_valid():
                print("Sub Form is Valid")
                gatein_preimg_form.save()
            else:
                print("Sub Form Not Valid")
            return redirect(request.META['HTTP_REFERER'])
            # return redirect('/SMS/gatein_pre_list')
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
    gatein_pre_number_sess = Gatein_pre_info.objects.get(pk=gatein_pre_id).gatein_pre_number
    gatein_pre_att_del=Gatein_pre_info_att.objects.get(gatein_pre_number_att=gatein_pre_number_sess)
    gatein_pre_del.delete()
    gatein_pre_att_del.delete()
    return redirect('/SMS/gatein_pre_list')


