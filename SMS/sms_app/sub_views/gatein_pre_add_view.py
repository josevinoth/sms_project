from random import randint

from django.db import transaction
from django.shortcuts import render, redirect
from ..forms import Gatein_preaddForm
from django.contrib.auth.decorators import login_required
from ..models import Gatein_pre_info
from ..models import User_extInfo,Location_info
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
            print("I am inside Get add Pre Gatein")
            gatein_pre_form = Gatein_preaddForm()
        else:
            gatein_pre_info = Gatein_pre_info.objects.get(pk=gatein_pre_id)
            gatein_pre_form = Gatein_preaddForm(instance=gatein_pre_info)
        context = {
            'first_name': first_name,
            'gatein_pre_form': gatein_pre_form,
            'user_branch_id': user_branch_id,
            'user_id': user_id,
        }
        return render(request, "asset_mgt_app/gatein_pre_add.html", context)
    else:
        if gatein_pre_id == 0:
            print("I am inside post add Pre-Gatein")
            gatein_pre_form = Gatein_preaddForm(request.POST,request.FILES)
            if gatein_pre_form.is_valid():
                print( "Pre-Gate-in Main Form is Valid")
                # Generate Random pre-gatein number
                try:
                    last_id = (Gatein_pre_info.objects.latest('id')).id
                    # last_id = (Gatein_pre_info.objects.values_list('gatein_pre_number',flat=True)).last()
                    pre_gatein_num = (int((Gatein_pre_info.objects.get(id=last_id)).gatein_pre_number) + 1)
                except ObjectDoesNotExist:
                    pre_gatein_num = (randint(10000, 999999))
                gatein_pre_form.save()
                last_id = (Gatein_pre_info.objects.latest('id')).id
                Gatein_pre_info.objects.filter(id=last_id).update(gatein_pre_number=pre_gatein_num)
                messages.success(request, 'Record Updated Successfully')
                job_id = Gatein_pre_info.objects.get(gatein_pre_number=pre_gatein_num).id
                url = 'gatein_pre_update/' + str(job_id)
                return redirect(url)
            else:
                print("Pre-Gate-in Main Form is In-Valid")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("I am inside post edit Pre Gatein")
            gatein_pre_info = Gatein_pre_info.objects.get(pk=gatein_pre_id)
            gatein_pre_form = Gatein_preaddForm(request.POST,request.FILES,instance=gatein_pre_info)

            if gatein_pre_form.is_valid():
                print("Main Form is Valid")
                gatein_pre_form.save()
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Main Form is In-Valid")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
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
    gatein_pre_del.delete()
    return redirect('/SMS/gatein_pre_list')


