from django.contrib.auth.decorators import login_required
from ..forms import ServiceaddForm
from ..models import Service_Info
from django.shortcuts import render, redirect

# List Service
@login_required(login_url='login_page')
def service_list(request):
    first_name = request.session.get('first_name')
    context = {'service_list': Service_Info.objects.all(),'first_name': first_name}
    return render(request, "asset_mgt_app/service_list.html", context)


# Add Service
@login_required(login_url='login_page')
def service_add(request, service_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if service_id == 0:
            form = ServiceaddForm()
        else:
            serviceinfo = Service_Info.objects.get(pk=service_id)
            form = ServiceaddForm(instance=serviceinfo)
        return render(request, "asset_mgt_app/service_add.html", {'form': form,'first_name': first_name})
    else:
        if service_id == 0:
            form = ServiceaddForm(request.POST)
        else:
            serviceinfo = Service_Info.objects.get(pk=service_id)
            form = ServiceaddForm(request.POST, instance=serviceinfo)
        if form.is_valid():
            form.save()
        return redirect('/SMS/service_list')


# Delete Service
@login_required(login_url='login_page')
def service_delete(request, service_id):
    serviceinfo = Service_Info.objects.get(pk=service_id)
    serviceinfo.delete()
    return redirect('/SMS/service_list')