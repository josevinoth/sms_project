from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from ..forms import PregateintruckForm
from ..models import Pregateintruckinfo,Gatein_pre_info
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required(login_url='login_page')
def pregateintruck_add(request,pregateintruck_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    gatein_num_id = request.session['gatein_num_id']
    if request.method == "GET":
        if pregateintruck_id == 0:
            form = PregateintruckForm()
        else:
            pregateintruck=Pregateintruckinfo.objects.get(pk=pregateintruck_id)
            form = PregateintruckForm(instance=pregateintruck)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'gatein_num_id': gatein_num_id,
                }
        return render(request, "asset_mgt_app/pregateintruck_add.html", context)
    else:
        if pregateintruck_id == 0:
            form = PregateintruckForm(request.POST)
            if form.is_valid():
                form.save()
                print("Pregateintruckinfo Form is Valid")
                last_id = (Pregateintruckinfo.objects.latest('id')).id
                messages.success(request, 'Record Updated Successfully')
                # return redirect(request.META['HTTP_REFERER'])
                a=pregateintruckdetails_list(request,gatein_num_id)
                return redirect('/SMS/pregateintruck_update/' + str(last_id))
            else:
                print("Pregateintruckinfo Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            pregateintruck = Pregateintruckinfo.objects.get(pk=pregateintruck_id)
            form = PregateintruckForm(request.POST,instance=pregateintruck)
            if form.is_valid():
                form.save()
                print("pregateintruckForm Form is Valid")
                messages.success(request, 'Record Updated Successfully')
                a = pregateintruckdetails_list(request, gatein_num_id)
            else:
                print("pregateintruckForm Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
def pregateintruckdetails_list(request,gatein_num_id):
    turck_numbers=list(Pregateintruckinfo.objects.filter(pregatein_number=gatein_num_id).values_list('pregatein_truck_number',flat=True))
    driver_names=list(Pregateintruckinfo.objects.filter(pregatein_number=gatein_num_id).values_list('pregatein_driver',flat=True))
    pre_gatein_num=Gatein_pre_info.objects.get(id=gatein_num_id).gatein_pre_number
    Gatein_pre_info.objects.filter(gatein_pre_number=pre_gatein_num).update(gatein_pre_truck_number=turck_numbers)
    Gatein_pre_info.objects.filter(gatein_pre_number=pre_gatein_num).update(gatein_pre_driver_name=driver_names)
    return (turck_numbers,driver_names)

# List pregateintruck
@login_required(login_url='login_page')
def pregateintruck_list(request):
    first_name = request.session.get('first_name')
    Gatein_pre_list=Pregateintruckinfo.objects.all()
    page_number = request.GET.get('page')
    paginator = Paginator(Gatein_pre_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
            'page_obj' :page_obj ,
            'first_name': first_name
        }
    return render(request,"asset_mgt_app/gatein_pre_list.html",context)

#Delete pregateintruck
@login_required(login_url='login_page')
def pregateintruck_delete(request,pregateintruck_id):
    pregateintruck = Pregateintruckinfo.objects.get(pk=pregateintruck_id)
    pregateintruck.delete()
    gatein_num_id = request.session['gatein_num_id']
    pregateintruckdetails_list(request,gatein_num_id)
    return redirect(request.META['HTTP_REFERER'])

