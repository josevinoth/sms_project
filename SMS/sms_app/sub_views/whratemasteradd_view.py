from django.contrib.auth.decorators import login_required
from ..forms import WhratemasteraddForm
from ..models import WhratemasterInfo
from django.shortcuts import render, redirect

# List whratemaster
@login_required(login_url='login_page')
def whratemaster_list(request):
    first_name = request.session.get('first_name')
    context = {'whratemaster_list': WhratemasterInfo.objects.all(),'first_name': first_name}
    return render(request, "asset_mgt_app/whratemaster_list.html", context)


# Add whratemaster
@login_required(login_url='login_page')
def whratemaster_add(request, whratemaster_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if whratemaster_id == 0:
            form = WhratemasteraddForm()
        else:
            whratemasterinfo = WhratemasterInfo.objects.get(pk=whratemaster_id)
            form = WhratemasteraddForm(instance=whratemasterinfo)
        return render(request, "asset_mgt_app/whratemaster_add.html", {'form': form,'first_name': first_name})
    else:
        if whratemaster_id == 0:
            form = WhratemasteraddForm(request.POST)
        else:
            whratemasterinfo = WhratemasterInfo.objects.get(pk=whratemaster_id)
            form = WhratemasteraddForm(request.POST, instance=whratemasterinfo)
        if form.is_valid():
            form.save()
        return redirect('/SMS/whratemaster_list')


# Delete whratemaster
@login_required(login_url='login_page')
def whratemaster_delete(request, whratemaster_id):
    whratemasterinfo = WhratemasterInfo.objects.get(pk=whratemaster_id)
    whratemasterinfo.delete()
    return redirect('/SMS/whratemaster_list')