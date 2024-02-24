from django.contrib.auth.decorators import login_required
from ..forms import PackagetypeaddForm
from ..models import Packagetype_info
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def packagetype_add(request,packagetype_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if packagetype_id == 0:
            packagetype_form = PackagetypeaddForm()
        else:
            packagetype_info=Packagetype_info.objects.get(pk=packagetype_id)
            packagetype_form = PackagetypeaddForm(instance=packagetype_info)
        return render(request, "asset_mgt_app/packagetype_add.html", {'packagetype_form': packagetype_form,'first_name': first_name})
    else:
        if packagetype_id == 0:
            packagetype_form = PackagetypeaddForm(request.POST)
        else:
            packagetype_info = Packagetype_info.objects.get(pk=packagetype_id)
            packagetype_form = PackagetypeaddForm(request.POST,instance=packagetype_info)
        if packagetype_form.is_valid():
            packagetype_form.save()
        return redirect('/SMS/packagetype_list')

# List damage
@login_required(login_url='login_page')
def packagetype_list(request):
    first_name = request.session.get('first_name')
    context = {'packagetype_list' : Packagetype_info.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/packagetype_list.html",context)

#Delete damage
@login_required(login_url='login_page')
def packagetype_delete(request,packagetype_id):
    materialhandling = Packagetype_info.objects.get(pk=packagetype_id)
    materialhandling.delete()
    return redirect('/SMS/packagetype_list')