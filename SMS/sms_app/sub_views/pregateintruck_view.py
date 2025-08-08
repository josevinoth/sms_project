from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..forms import PregateintruckForm
from ..models import Pregateintruckinfo,Gatein_pre_info,HighvalueInfo
from django.shortcuts import render, redirect
from django.contrib import messages

from ..sub_models.transporter_mod import Transporter_name


@login_required(login_url='login_page')
def pregateintruck_add(request,pregateintruck_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    gatein_num_id = request.session['gatein_num_id']
    high_list = HighvalueInfo.objects.all()
    if request.method == "GET":
        high_value_check = None
        if pregateintruck_id == 0:
            form = PregateintruckForm()
        else:
            pregateintruck=Pregateintruckinfo.objects.get(pk=pregateintruck_id)
            form = PregateintruckForm(instance=pregateintruck)
            request.session['ses_pregateintruck_id'] = pregateintruck_id
            high_value_check=Pregateintruckinfo.objects.get(pk=pregateintruck_id).pregatein_high_value.id
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'gatein_num_id': gatein_num_id,
                'high_list':high_list,
                'high_value_check':high_value_check,
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
    return (redirect(request.META['HTTP_REFERER'])

# Cancel pregateintruck
@login_required(login_url='login_page'))
def pregateintruck_cancel(request):
    gatein_num_id = request.session['gatein_num_id']
    return redirect('/SMS/gatein_pre_update/' + str(gatein_num_id))
@csrf_exempt
def add_transporter(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if not name:
            return JsonResponse({"success": False, "error": "Transporter name cannot be empty."})

        existing = Transporter_name.objects.filter(transporter_name__iexact=name).first()
        if existing:
            return JsonResponse({
                "success": False,
                "id": existing.id,
                "name": existing.transporter_name,
                "error": "This transporter already exists."
            })

        new = Transporter_name.objects.create(transporter_name=name)
        return JsonResponse({"success": True, "id": new.id, "name": new.transporter_name})

    return JsonResponse({"success": False, "error": "Invalid request"})
