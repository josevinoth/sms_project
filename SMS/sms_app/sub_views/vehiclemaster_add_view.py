from django.contrib.auth.decorators import login_required
from ..forms import VehiclemasteraddForm
from ..models import VehiclemasterInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def vehiclemaster_add(request,vehiclemaster_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if vehiclemaster_id == 0:
            form = VehiclemasteraddForm()
        else:
            vehiclemaster = VehiclemasterInfo.objects.get(pk=vehiclemaster_id)
            form = VehiclemasteraddForm(instance=vehiclemaster)
        return render(request, "asset_mgt_app/vehiclemaster_add.html", {'form': form,'first_name': first_name})
    else:
        if vehiclemaster_id == 0:
            form = VehiclemasteraddForm(request.POST)
        else:
            vehiclemaster = VehiclemasterInfo.objects.get(pk=vehiclemaster_id)
            form = VehiclemasteraddForm(request.POST,instance=vehiclemaster)
        if form.is_valid():
            form.save()
        return redirect('/SMS/vehiclemaster_list')

# List vehiclemaster
@login_required(login_url='login_page')
def vehiclemaster_list(request):
    first_name = request.session.get('first_name')
    context = {'vehiclemaster_list' : VehiclemasterInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/vehiclemaster_list.html",context)

#Delete vehiclemaster
@login_required(login_url='login_page')
def vehiclemaster_delete(request,vehiclemaster_id):
    vehiclemaster = VehiclemasterInfo.objects.get(pk=vehiclemaster_id)
    vehiclemaster.delete()
    return redirect('/SMS/vehiclemaster_list')