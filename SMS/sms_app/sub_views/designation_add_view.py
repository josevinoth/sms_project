from django.contrib.auth.decorators import login_required
from ..forms import DesignationaddForm
from ..models import DesignationInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def designation_add(request,designation_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if designation_id == 0:
            form = DesignationaddForm()
        else:
            designation=DesignationInfo.objects.get(pk=designation_id)
            form = DesignationaddForm(instance=designation)
        return render(request, "asset_mgt_app/designation_add.html", {'form': form,'first_name': first_name})
    else:
        if designation_id == 0:
            form = DesignationaddForm(request.POST)
        else:
            designation = DesignationInfo.objects.get(pk=designation_id)
            form = DesignationaddForm(request.POST,instance=designation)
        if form.is_valid():
            form.save()
        return redirect('/SMS/designation_list')

# List designation
@login_required(login_url='login_page')
def designation_list(request):
    first_name = request.session.get('first_name')
    context = {'designation_list' : DesignationInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/designation_list.html",context)

#Delete designation
@login_required(login_url='login_page')
def designation_delete(request,designation_id):
    designation = DesignationInfo.objects.get(pk=designation_id)
    designation.delete()
    return redirect('/SMS/designation_list')