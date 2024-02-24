from django.contrib.auth.decorators import login_required
from ..forms import VehiclemodeladdForm
from ..models import VehiclemodelInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def vehiclemodel_add(request,vehiclemodel_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if vehiclemodel_id == 0:
            form = VehiclemodeladdForm()
        else:
            vehiclemodel=VehiclemodelInfo.objects.get(pk=vehiclemodel_id)
            form = VehiclemodeladdForm(instance=vehiclemodel)
        return render(request, "asset_mgt_app/vehiclemodel_add.html", {'form': form,'first_name': first_name})
    else:
        if vehiclemodel_id == 0:
            form = VehiclemodeladdForm(request.POST)
        else:
            vehiclemodel = VehiclemodelInfo.objects.get(pk=vehiclemodel_id)
            form = VehiclemodeladdForm(request.POST,instance=vehiclemodel)
        if form.is_valid():
            form.save()
        return redirect('/SMS/vehiclemodel_list')

# List vehiclemodel
@login_required(login_url='login_page')
def vehiclemodel_list(request):
    first_name = request.session.get('first_name')
    context = {'vehiclemodel_list' : VehiclemodelInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/vehiclemodel_list.html",context)

#Delete vehiclemodel
@login_required(login_url='login_page')
def vehiclemodel_delete(request,vehiclemodel_id):
    vehiclemodel = VehiclemodelInfo.objects.get(pk=vehiclemodel_id)
    vehiclemodel.delete()
    return redirect('/SMS/vehiclemodel_list')