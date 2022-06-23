from django.contrib.auth.decorators import login_required
from ..forms import FueltypeaddForm
from ..models import FueltypeInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def fueltype_add(request,fueltype_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if fueltype_id == 0:
            form = FueltypeaddForm()
        else:
            fueltype=FueltypeInfo.objects.get(pk=fueltype_id)
            form = FueltypeaddForm(instance=fueltype)
        return render(request, "asset_mgt_app/fueltype_add.html", {'form': form,'first_name': first_name})
    else:
        if fueltype_id == 0:
            form = FueltypeaddForm(request.POST)
        else:
            fueltype = FueltypeInfo.objects.get(pk=fueltype_id)
            form = FueltypeaddForm(request.POST,instance=fueltype)
        if form.is_valid():
            form.save()
        return redirect('/SMS/fueltype_list')

# List fueltype
@login_required(login_url='login_page')
def fueltype_list(request):
    first_name = request.session.get('first_name')
    context = {'fueltype_list' : FueltypeInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/fueltype_list.html",context)

#Delete fueltype
@login_required(login_url='login_page')
def fueltype_delete(request,fueltype_id):
    fueltype = FueltypeInfo.objects.get(pk=fueltype_id)
    fueltype.delete()
    return redirect('/SMS/fueltype_list')