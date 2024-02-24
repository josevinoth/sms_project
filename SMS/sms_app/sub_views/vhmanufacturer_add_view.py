from django.contrib.auth.decorators import login_required
from ..forms import VhmanufactureraddForm
from ..models import VhmanufacturerInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def vhmanufacturer_add(request,vhmanufacturer_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if vhmanufacturer_id == 0:
            form = VhmanufactureraddForm()
        else:
            vhmanufacturer=VhmanufacturerInfo.objects.get(pk=vhmanufacturer_id)
            form = VhmanufactureraddForm(instance=vhmanufacturer)
        return render(request, "asset_mgt_app/vhmanufacturer_add.html", {'form': form,'first_name': first_name})
    else:
        if vhmanufacturer_id == 0:
            form = VhmanufactureraddForm(request.POST)
        else:
            vhmanufacturer = VhmanufacturerInfo.objects.get(pk=vhmanufacturer_id)
            form = VhmanufactureraddForm(request.POST,instance=vhmanufacturer)
        if form.is_valid():
            form.save()
        return redirect('/SMS/vhmanufacturer_list')

# List vhmanufacturer
@login_required(login_url='login_page')
def vhmanufacturer_list(request):
    first_name = request.session.get('first_name')
    context = {'vhmanufacturer_list' : VhmanufacturerInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/vhmanufacturer_list.html",context)

#Delete vhmanufacturer
@login_required(login_url='login_page')
def vhmanufacturer_delete(request,vhmanufacturer_id):
    vhmanufacturer = VhmanufacturerInfo.objects.get(pk=vhmanufacturer_id)
    vhmanufacturer.delete()
    return redirect('/SMS/vhmanufacturer_list')