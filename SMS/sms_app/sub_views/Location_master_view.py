from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import LocationMasterForm
from ..models import LocationMaster

@login_required(login_url='login_page')
def location_master_add(request, loc_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if loc_id == 0:
            form = LocationMasterForm()
        else:
            location = LocationMaster.objects.get(pk=loc_id)
            form = LocationMasterForm(instance=location)
        return render(request, "asset_mgt_app/location_master_gmap.html", {'form': form, 'first_name': first_name})
    else:
        if loc_id == 0:
            form = LocationMasterForm(request.POST)
        else:
            location = LocationMaster.objects.get(pk=loc_id)
            form = LocationMasterForm(request.POST, instance=location)
        if form.is_valid():
            form.save()
            return redirect('location_master_list')
        return render(request, "asset_mgt_app/location_master_gmap.html", {'form': form, 'first_name': first_name})

@login_required(login_url='login_page')
def location_master_list(request):
    first_name = request.session.get('first_name')
    locations = LocationMaster.objects.all()
    return render(request, "asset_mgt_app/location_master_list.html", {
        'location_list': locations,
        'first_name': first_name
    })

@login_required(login_url='login_page')
def location_master_delete(request, loc_id):
    location = LocationMaster.objects.get(pk=loc_id)
    location.delete()
    return redirect('location_master_list')
