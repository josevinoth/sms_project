from django.contrib.auth.decorators import login_required
from ..forms import LocationmasteraddForm
from ..models import LocationmasterInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def locationmaster_add(request,locationmaster_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if locationmaster_id == 0:
            form = LocationmasteraddForm()
        else:
            locationmaster=LocationmasterInfo.objects.get(pk=locationmaster_id)
            form = LocationmasteraddForm(instance=locationmaster)
        return render(request, "asset_mgt_app/locationmaster_add.html", {'form': form,'first_name': first_name})
    else:
        if locationmaster_id == 0:
            form = LocationmasteraddForm(request.POST)
        else:
            locationmaster = LocationmasterInfo.objects.get(pk=locationmaster_id)
            form = LocationmasteraddForm(request.POST,instance=locationmaster)
        if form.is_valid():
            form.save()
        return redirect('/SMS/locationmaster_list')

# List locationmaster
@login_required(login_url='login_page')
def locationmaster_list(request):
    first_name = request.session.get('first_name')
    context = {'locationmaster_list' : LocationmasterInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/locationmaster_list.html",context)

#Delete locationmaster
@login_required(login_url='login_page')
def locationmaster_delete(request,locationmaster_id):
    locationmaster = LocationmasterInfo.objects.get(pk=locationmaster_id)
    locationmaster.delete()
    return redirect('/SMS/locationmaster_list')