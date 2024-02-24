from django.contrib.auth.decorators import login_required
from ..forms import MaterialhandlingaddForm
from ..models import Materialhandling_Info
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def materialhandling_add(request,material_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if material_id == 0:
            material_form = MaterialhandlingaddForm()
        else:
            materialhandling_info=Materialhandling_Info.objects.get(pk=material_id)
            material_form = MaterialhandlingaddForm(instance=materialhandling_info)
        return render(request, "asset_mgt_app/materialhandling_add.html", {'material_form': material_form,'first_name': first_name})
    else:
        if material_id == 0:
            material_form = MaterialhandlingaddForm(request.POST)
        else:
            materialhandling_info = Materialhandling_Info.objects.get(pk=material_id)
            material_form = MaterialhandlingaddForm(request.POST,instance=materialhandling_info)
        if material_form.is_valid():
            material_form.save()
        return redirect('/SMS/materialhandling_list')

# List material handling
@login_required(login_url='login_page')
def materialhandling_list(request):
    first_name = request.session.get('first_name')
    context = {'materailhandling_list' : Materialhandling_Info.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/materialhandling_list.html",context)

#Delete material handling
@login_required(login_url='login_page')
def materialhandling_delete(request,material_id):
    materialhandling = Materialhandling_Info.objects.get(pk=material_id)
    materialhandling.delete()
    return redirect('/SMS/materialhandling_list')