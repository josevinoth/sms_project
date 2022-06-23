from django.contrib.auth.decorators import login_required
from ..forms import VehicledetailaddForm
from ..models import VehicledetailInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def vehicledetail_add(request,vehicledetail_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if vehicledetail_id == 0:
            form = VehicledetailaddForm()
        else:
            vehicledetail = VehicledetailInfo.objects.get(pk=vehicledetail_id)
            form = VehicledetailaddForm(instance=vehicledetail)
        return render(request, "asset_mgt_app/vehicledetail_add.html", {'form': form,'first_name': first_name})
    else:
        if vehicledetail_id == 0:
            form = VehicledetailaddForm(request.POST)
        else:
            vehicledetail = VehicledetailInfo.objects.get(pk=vehicledetail_id)
            form = VehicledetailaddForm(request.POST,instance=vehicledetail)
        if form.is_valid():
            form.save()
        return redirect('/SMS/vehicledetail_list')

# List vehicledetail
@login_required(login_url='login_page')
def vehicledetail_list(request):
    first_name = request.session.get('first_name')
    context = {'vehicledetail_list' : VehicledetailInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/vehicledetail_list.html",context)

#Delete enquirynote
@login_required(login_url='login_page')
def vehicledetail_delete(request,vehicledetail_id):
    vehicledetail = VehicledetailInfo.objects.get(pk=vehicledetail_id)
    vehicledetail.delete()
    return redirect('/SMS/vehicledetail_list')