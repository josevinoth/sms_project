from django.contrib.auth.decorators import login_required
from ..forms import GstmodelForm
from ..models import GstmodelInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def gstmodel_add(request,gstmodel_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if gstmodel_id == 0:
            form = GstmodelForm()
        else:
            gstmodel=GstmodelInfo.objects.get(pk=gstmodel_id)
            form = GstmodelForm(instance=gstmodel)
        return render(request, "asset_mgt_app/gstmodel_add.html", {'form': form,'first_name': first_name})
    else:
        if gstmodel_id == 0:
            form = GstmodelForm(request.POST)
        else:
            gstmodel = GstmodelInfo.objects.get(pk=gstmodel_id)
            form = GstmodelForm(request.POST,instance=gstmodel)
        if form.is_valid():
            form.save()
        return redirect('/SMS/gstmodel_list')

# List gstmodel
@login_required(login_url='login_page')
def gstmodel_list(request):
    first_name = request.session.get('first_name')
    context = {'gstmodel_list' : GstmodelInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/gstmodel_list.html",context)

#Delete gstmodel
@login_required(login_url='login_page')
def gstmodel_delete(request,gstmodel_id):
    gstmodel = GstmodelInfo.objects.get(pk=gstmodel_id)
    gstmodel.delete()
    return redirect('/SMS/gstmodel_list')