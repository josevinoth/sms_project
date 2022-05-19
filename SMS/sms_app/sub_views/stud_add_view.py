from django.contrib.auth.decorators import login_required
from ..forms import StudaddForm
from ..models import Stud_reg
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def stud_add(request,stud_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if stud_id == 0:
            form = StudaddForm()
        else:
            stud=Stud_reg.objects.get(pk=stud_id)
            form = StudaddForm(instance=stud)
        return render(request, "asset_mgt_app/stud_add.html", {'form': form,'first_name': first_name})
    else:
        if stud_id == 0:
            form = StudaddForm(request.POST)
        else:
            stud = Stud_reg.objects.get(pk=stud_id)
            form = StudaddForm(request.POST,instance=stud)
        if form.is_valid():
            form.save()
        return redirect('/SMS/stud_list')

# List stud
@login_required(login_url='login_page')
def stud_list(request):
    first_name = request.session.get('first_name')
    context = {'stud_list' : Stud_reg.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/stud_list.html",context)

#Delete stud
@login_required(login_url='login_page')
def stud_delete(request,stud_id):
    stud = Stud_reg.objects.get(pk=stud_id)
    stud.delete()
    return redirect('/SMS/stud_list')