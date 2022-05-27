from django.contrib.auth.decorators import login_required
from ..forms import UnitaddForm
from ..models import UnitInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def unit_add(request,unit_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if unit_id == 0:
            form = UnitaddForm()
        else:
            unit=UnitInfo.objects.get(pk=unit_id)
            form = UnitaddForm(instance=unit)
        return render(request, "asset_mgt_app/unit_add.html", {'form': form,'first_name': first_name})
    else:
        if unit_id == 0:
            form = UnitaddForm(request.POST)
        else:
            unit = UnitInfo.objects.get(pk=unit_id)
            form = UnitaddForm(request.POST,instance=unit)
        if form.is_valid():
            form.save()
        return redirect('/SMS/unit_list')

# List unit
@login_required(login_url='login_page')
def unit_list(request):
    first_name = request.session.get('first_name')
    context = {'unit_list' :UnitInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/unit_list.html",context)

#Delete unit
@login_required(login_url='login_page')
def unit_delete(request,unit_id):
    unit = UnitInfo.objects.get(pk=unit_id)
    unit.delete()
    return redirect('/SMS/unit_list')