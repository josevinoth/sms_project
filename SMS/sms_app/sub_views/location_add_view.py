from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ..forms import LocationaddForm
from ..models import Location_info

@login_required(login_url='login_page')
def location_add(request,location_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if location_id == 0:
            form = LocationaddForm()
        else:
            location=Location_info.objects.get(pk=location_id)
            form = LocationaddForm(instance=location)
        return render(request, "asset_mgt_app/location_add.html", {'form': form,'first_name': first_name,})
    else:
        if location_id == 0:
            form = LocationaddForm(request.POST)
        else:
            location = Location_info.objects.get(pk=location_id)
            form = LocationaddForm(request.POST,instance=location)
        if form.is_valid():
            form.save()
        return redirect('/SMS/location_list')

# List Location
@login_required(login_url='login_page')
def location_list(request):
    first_name = request.session.get('first_name')
    context = {'location_list' : Location_info.objects.all(),'first_name': first_name,}
    return render(request,"asset_mgt_app/location_list.html",context)

#Delete Location
@login_required(login_url='login_page')
def location_delete(request,location_id):
    location = Location_info.objects.get(pk=location_id)
    location.delete()
    return redirect('/SMS/location_list')