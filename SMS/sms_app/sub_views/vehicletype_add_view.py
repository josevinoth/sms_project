from django.contrib.auth.decorators import login_required
from ..forms import VehicletypeaddForm
from ..models import VehicletypeInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def vehicletype_add(request,vehicletype_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if vehicletype_id == 0:
            form = VehicletypeaddForm()
        else:
            vehicletype=VehicletypeInfo.objects.get(pk=vehicletype_id)
            form = VehicletypeaddForm(instance=vehicletype)
        return render(request, "asset_mgt_app/vehicletype_add.html", {'form': form,'first_name': first_name})
    else:
        if vehicletype_id == 0:
            form = VehicletypeaddForm(request.POST)
        else:
            vehicletype = VehicletypeInfo.objects.get(pk=vehicletype_id)
            form = VehicletypeaddForm(request.POST,instance=vehicletype)
        if form.is_valid():
            form.save()
        return redirect('/SMS/vehicletype_list')

# List vehicletype
@login_required(login_url='login_page')
def vehicletype_list(request):
    first_name = request.session.get('first_name')
    context = {'vehicletype_list' : VehicletypeInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/vehicletype_list.html",context)

#Delete vehicletype
@login_required(login_url='login_page')
def vehicletype_delete(request,vehicletype_id):
    vehicletype = VehicletypeInfo.objects.get(pk=vehicletype_id)
    vehicletype.delete()
    return redirect('/SMS/vehicletype_list')