from django.contrib.auth.decorators import login_required
from ..forms import PeoaddForm
from ..models import Peo_reg
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def peo_add(request,peo_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if peo_id == 0:
            form = PeoaddForm()
        else:
            peo = Peo_reg.objects.get(pk=peo_id)
            form = PeoaddForm(instance=peo)
        return render(request, "asset_mgt_app/peo_add.html", {'form': form,'first_name': first_name})
    else:
        if peo_id == 0:
            form = PeoaddForm(request.POST)
        else:
            peo = Peo_reg.objects.get(pk=peo_id)
            form = PeoaddForm(request.POST,instance=peo)
        if form.is_valid():
            form.save()
        return redirect('/SMS/peo_list')

# List Peo
@login_required(login_url='login_page')
def peo_list(request):
    first_name = request.session.get('first_name')
    context = {'peo_list' : Peo_reg.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/peo_list.html",context)

#Delete Peo
@login_required(login_url='login_page')
def peo_delete(request,peo_id):
    peo = Peo_reg.objects.get(pk=peo_id)
    peo.delete()
    return redirect('/SMS/peo_list')