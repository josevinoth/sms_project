from django.contrib.auth.decorators import login_required
from ..forms import VehiclesourceaddForm
from ..models import VehiclesourceInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def vehiclesource_add(request,vehiclesource_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if vehiclesource_id == 0:
            form = VehiclesourceaddForm()
        else:
            vehiclesource=VehiclesourceInfo.objects.get(pk=vehiclesource_id)
            form = VehiclesourceaddForm(instance=vehiclesource)
        return render(request, "asset_mgt_app/vehiclesource_add.html", {'form': form,'first_name': first_name})
    else:
        if vehiclesource_id == 0:
            form = VehiclesourceaddForm(request.POST)
        else:
            vehiclesource = VehiclesourceInfo.objects.get(pk=vehiclesource_id)
            form = VehiclesourceaddForm(request.POST,instance=vehiclesource)
        if form.is_valid():
            form.save()
        return redirect('/SMS/vehiclesource_list')

# List vehiclesource
@login_required(login_url='login_page')
def vehiclesource_list(request):
    first_name = request.session.get('first_name')
    context = {'vehiclesource_list' : VehiclesourceInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/vehiclesource_list.html",context)

#Delete vehiclesource
@login_required(login_url='login_page')
def vehiclesource_delete(request,vehiclesource_id):
    vehiclesource = VehiclesourceInfo.objects.get(pk=vehiclesource_id)
    vehiclesource.delete()
    return redirect('/SMS/vehiclesource_list')