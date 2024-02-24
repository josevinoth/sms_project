from django.contrib.auth.decorators import login_required
from ..forms import InsurancetypeaddForm
from ..models import Insurance_Type
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def insurancetype_add(request,insurancetype_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if insurancetype_id == 0:
            form = InsurancetypeaddForm()
        else:
            insurancetype=Insurance_Type.objects.get(pk=insurancetype_id)
            form = InsurancetypeaddForm(instance=insurancetype)
        return render(request, "asset_mgt_app/insurancetype_add.html", {'form': form,'first_name': first_name})
    else:
        if insurancetype_id == 0:
            form = InsurancetypeaddForm(request.POST)
        else:
            insurancetype = Insurance_Type.objects.get(pk=insurancetype_id)
            form = InsurancetypeaddForm(request.POST,instance=insurancetype)
        if form.is_valid():
            form.save()
        return redirect('/SMS/insurancetype_list')

# List Product
@login_required(login_url='login_page')
def insurancetype_list(request):
    first_name = request.session.get('first_name')
    context = {'insurancetype_list' : Insurance_Type.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/insurancetype_list.html",context)

#Delete Product
@login_required(login_url='login_page')
def insurancetype_delete(request,insurancetype_id):
    insurancetype = Insurance_Type.objects.get(pk=insurancetype_id)
    insurancetype.delete()
    return redirect('/SMS/insurancetype_list')