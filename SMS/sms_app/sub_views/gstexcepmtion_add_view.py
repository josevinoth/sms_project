from django.contrib.auth.decorators import login_required
from ..forms import GstexcemptionForm
from ..models import GstexcemptionInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def gstexcepmtion_add(request,gstexcepmtion_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if gstexcepmtion_id == 0:
            form = GstexcemptionForm()
        else:
            gstexcepmtion = GstexcemptionInfo.objects.get(pk=gstexcepmtion_id)
            form = GstexcemptionForm(instance=gstexcepmtion)
        return render(request, "asset_mgt_app/gstexcepmtion_add.html", {'form': form,'first_name': first_name})
    else:
        if gstexcepmtion_id == 0:
            form = GstexcemptionForm(request.POST)
        else:
            gstexcepmtion = GstexcemptionInfo.objects.get(pk=gstexcepmtion_id)
            form = GstexcemptionForm(request.POST,instance=gstexcepmtion)
        if form.is_valid():
            form.save()
        return redirect('/SMS/gstexcepmtion_list')

# List gstexcepmtion
@login_required(login_url='login_page')
def gstexcepmtion_list(request):
    first_name = request.session.get('first_name')
    context = {'gstexcepmtion_list' : GstexcemptionInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/gstexcepmtion_list.html",context)

#Delete gstexcepmtion
@login_required(login_url='login_page')
def gstexcepmtion_delete(request,gstexcepmtion_id):
    gstexcepmtion = GstexcemptionInfo.objects.get(pk=gstexcepmtion_id)
    gstexcepmtion.delete()
    return redirect('/SMS/gstexcepmtion_list')