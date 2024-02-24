from django.contrib.auth.decorators import login_required
from ..forms import VehiclecolouraddForm
from ..models import VehiclecolourInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def vehiclecolour_add(request,vehiclecolour_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if vehiclecolour_id == 0:
            form = VehiclecolouraddForm()
        else:
            vehiclecolour=VehiclecolourInfo.objects.get(pk=vehiclecolour_id)
            form = VehiclecolouraddForm(instance=vehiclecolour)
        return render(request, "asset_mgt_app/vehiclecolour_add.html", {'form': form,'first_name': first_name})
    else:
        if vehiclecolour_id == 0:
            form = VehiclecolouraddForm(request.POST)
        else:
            vehiclecolour = VehiclecolourInfo.objects.get(pk=vehiclecolour_id)
            form = VehiclecolouraddForm(request.POST,instance=vehiclecolour)
        if form.is_valid():
            form.save()
        return redirect('/SMS/vehiclecolour_list')

# List vehiclecolour
@login_required(login_url='login_page')
def vehiclecolour_list(request):
    first_name = request.session.get('first_name')
    context = {'vehiclecolour_list' : VehiclecolourInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/vehiclecolour_list.html",context)

#Delete vehiclecolour
@login_required(login_url='login_page')
def vehiclecolour_delete(request,vehiclecolour_id):
    vehiclecolour = VehiclecolourInfo.objects.get(pk=vehiclecolour_id)
    vehiclecolour.delete()
    return redirect('/SMS/vehiclecolour_list')