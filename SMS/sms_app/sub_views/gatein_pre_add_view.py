from random import randint
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect
from ..forms import Gatein_preaddForm
from django.contrib.auth.decorators import login_required
from ..models import Pregateintruckinfo,Gatein_pre_info
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
    print('user_branch_id',user_branch_id)
    if request.method == "GET":
        if gatein_pre_id == 0:
            print("I am inside Get add Pre Gatein")
            gatein_pre_form = Gatein_preaddForm()
            context = {
                'first_name': first_name,
                'gatein_pre_form': gatein_pre_form,
                'user_branch_id': user_branch_id,
                'user_id': user_id,
            }
        else:
            gatein_pre_info = Gatein_pre_info.objects.get(pk=gatein_pre_id)
            gatein_num_id = Gatein_pre_info.objects.get(pk=gatein_pre_id).id
            request.session['gatein_num_id'] = gatein_num_id
            gatein_pre_form = Gatein_preaddForm(instance=gatein_pre_info)
            pregateintruck_list = Pregateintruckinfo.objects.filter(pregatein_number=gatein_num_id)
            context = {
            'first_name': first_name,
            'gatein_pre_form': gatein_pre_form,
            'user_branch_id': user_branch_id,
            'user_id': user_id,
            'pregateintruck_list': pregateintruck_list,
        }
        return render(request, "asset_mgt_app/gatein_pre_add.html", context)
    else:
        if gatein_pre_id == 0:
            print("I am inside post add Pre-Gatein")
            gatein_pre_form = Gatein_preaddForm(request.POST,request.FILES)
            if gatein_pre_form.is_valid():
                print( "Pre-Gate-in Main Form is Valid")
                gatein_pre_form.save()

                # Generate Random requirement number
                try:
                    last_id = Gatein_pre_info.objects.order_by('-id').values_list('id', flat=True).first()
                    print('last_id',last_id)
                    pre_gatein_num = 2000000 + last_id
                except ObjectDoesNotExist:
                    pre_gatein_num = 2000000
                print('pre_gatein_num', pre_gatein_num)
                Gatein_pre_info.objects.filter(id=last_id).update(gatein_pre_number=pre_gatein_num)
                messages.success(request, 'Record Updated Successfully')
                url = 'gatein_pre_update/' + str(last_id)
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
    Gatein_pre_list= (Gatein_pre_info.objects.all()).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(Gatein_pre_list, 1000)
    page_obj = paginator.get_page(page_number)
    context = {
        # 'Gatein_pre_list' : Gatein_pre_info.objects.all(),
        'first_name': first_name,
        'page_obj': page_obj,
    }
    return render(request,"asset_mgt_app/gatein_pre_list.html",context)

#Delete WH Job
@login_required(login_url='login_page')
def gatein_pre_delete(request,gatein_pre_id):
    gatein_pre_del = Gatein_pre_info.objects.get(pk=gatein_pre_id)
    gatein_pre_number_sess = Gatein_pre_info.objects.get(pk=gatein_pre_id).gatein_pre_number
    gatein_truck_del=Pregateintruckinfo.objects.filter(pregatein_number=gatein_pre_id)
    gatein_pre_del.delete()
    gatein_truck_del.delete()
    return redirect('/SMS/pre_gatein_search')
@login_required(login_url='login_page')
def pre_gatein_search(request):
    first_name = request.session.get('first_name')
    pre_gate_in = request.GET.get("pre_gate_in")
    truck_number = request.GET.get("truck_number")
    driver_name = request.GET.get("driver_name")
    if not pre_gate_in:
        pre_gate_in = ""
    if not truck_number:
        truck_number = ""
    if not driver_name:
        driver_name = ""
    # Gatein_pre_list = Gatein_pre_info.objects.filter(Q(gatein_pre_number__icontains =pre_gate_in)|Q(gatein_pre_number__isnull=True)).order_by('id')
    Gatein_pre_list = Gatein_pre_info.objects.filter((Q(gatein_pre_number__icontains =pre_gate_in)|Q(gatein_pre_number__isnull=True)) & (Q(gatein_pre_truck_number__icontains =truck_number)|Q(gatein_pre_truck_number__isnull=True)) & (Q(gatein_pre_driver_name__icontains =driver_name)|Q(gatein_pre_driver_name__isnull=True))).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(Gatein_pre_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
        'Gatein_pre_list': Gatein_pre_list,
        'first_name': first_name,
        'page_obj': page_obj,
        }
    return render(request, "asset_mgt_app/gatein_pre_list.html", context)


