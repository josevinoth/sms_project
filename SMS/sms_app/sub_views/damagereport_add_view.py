from django.contrib.auth.decorators import login_required
from ..forms import DamagereportaddForm
from ..models import DamagereportInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def damagereport_add(request,damagereport_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if damagereport_id == 0:
            form = DamagereportaddForm()
        else:
            damagereport=DamagereportInfo.objects.get(pk=damagereport_id)
            form = DamagereportaddForm(instance=damagereport)
        return render(request, "asset_mgt_app/damagereport_add.html", {'form': form,'first_name': first_name})
    else:
        if damagereport_id == 0:
            form = DamagereportaddForm(request.POST)
        else:
            damagereport = DamagereportInfo.objects.get(pk=damagereport_id)
            form = DamagereportaddForm(request.POST,instance=damagereport)
        if form.is_valid():
            form.save()
        return redirect('/SMS/damagereport_list')

# List damagereport
@login_required(login_url='login_page')
def damagereport_list(request):
    first_name = request.session.get('first_name')
    context = {'damagereport_list' : DamagereportInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/damagereport_list.html",context)

#Delete damagereport
@login_required(login_url='login_page')
def damagereport_delete(request,damagereport_id):
    damagereport = DamagereportInfo.objects.get(pk=damagereport_id)
    damagereport.delete()
    return redirect('/SMS/damagereport_list')