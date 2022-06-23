from django.contrib.auth.decorators import login_required
from ..forms import VehiclecategoryaddForm
from ..models import VehiclecategoryInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def vehiclecategory_add(request,vehiclecategory_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if vehiclecategory_id == 0:
            form = VehiclecategoryaddForm()
        else:
            vehiclecategory=VehiclecategoryInfo.objects.get(pk=vehiclecategory_id)
            form = VehiclecategoryaddForm(instance=vehiclecategory)
        return render(request, "asset_mgt_app/vehiclecategory_add.html", {'form': form,'first_name': first_name})
    else:
        if vehiclecategory_id == 0:
            form = VehiclecategoryaddForm(request.POST)
        else:
            vehiclecategory = VehiclecategoryInfo.objects.get(pk=vehiclecategory_id)
            form = VehiclecategoryaddForm(request.POST,instance=vehiclecategory)
        if form.is_valid():
            form.save()
        return redirect('/SMS/vehiclecategory_list')

# List vehiclecategory
@login_required(login_url='login_page')
def vehiclecategory_list(request):
    first_name = request.session.get('first_name')
    context = {'vehiclecategory_list' : VehiclecategoryInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/vehiclecategory_list.html",context)

#Delete vehiclecategory
@login_required(login_url='login_page')
def vehiclecategory_delete(request,vehiclecategory_id):
    vehiclecategory = VehiclecategoryInfo.objects.get(pk=vehiclecategory_id)
    vehiclecategory.delete()
    return redirect('/SMS/vehiclecategory_list')