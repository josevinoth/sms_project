from django.contrib.auth.decorators import login_required
from ..forms import CrcountfromForm
from ..models import CrcountfromInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def crcountfrom_add(request,crcountfrom_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if crcountfrom_id == 0:
            form = CrcountfromForm()
        else:
            crcountfrom=CrcountfromInfo.objects.get(pk=crcountfrom_id)
            form = CrcountfromForm(instance=crcountfrom)
        return render(request, "asset_mgt_app/crcountfrom_add.html", {'form': form,'first_name': first_name})
    else:
        if crcountfrom_id == 0:
            form = CrcountfromForm(request.POST)
        else:
            crcountfrom = CrcountfromInfo.objects.get(pk=crcountfrom_id)
            form = CrcountfromForm(request.POST,instance=crcountfrom)
        if form.is_valid():
            form.save()
        return redirect('/SMS/crcountfrom_list')

# List crcountfrom
@login_required(login_url='login_page')
def crcountfrom_list(request):
    first_name = request.session.get('first_name')
    context = {'crcountfrom_list' : CrcountfromInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/crcountfrom_list.html",context)

#Delete crcountfrom
@login_required(login_url='login_page')
def crcountfrom_delete(request,crcountfrom_id):
    crcountfrom = CrcountfromInfo.objects.get(pk=crcountfrom_id)
    crcountfrom.delete()
    return redirect('/SMS/crcountfrom_list')