from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
import json

from ..forms import PregateintruckForm
from ..models import Pregateintruckinfo,Places
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
            else:
                print("pregateintruckForm Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

# List pregateintruck
@login_required(login_url='login_page')
def pregateintruck_list(request):
    first_name = request.session.get('first_name')
    context = {'pregateintruck_list' : Pregateintruckinfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pregateintruck_list.html",context)

#Delete pregateintruck
@login_required(login_url='login_page')
def pregateintruck_delete(request,pregateintruck_id):
    pregateintruck = Pregateintruckinfo.objects.get(pk=pregateintruck_id)
    pregateintruck.delete()
    return redirect(request.META['HTTP_REFERER'])

