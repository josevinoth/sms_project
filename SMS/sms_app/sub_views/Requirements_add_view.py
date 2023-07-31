from django.contrib.auth.decorators import login_required
from ..forms import RequirementForm
from ..models import RequirementsInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def requirements_add(request,requirements_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if requirements_id == 0:
            form = RequirementForm()
        else:
            requirements=RequirementsInfo.objects.get(pk=requirements_id)
            form = RequirementForm(instance=requirements)
        return render(request, "asset_mgt_app/requirements_add.html", {'form': form,'first_name': first_name})
    else:
        if requirements_id == 0:
            form = RequirementForm(request.POST)
        else:
            requirements = RequirementsInfo.objects.get(pk=requirements_id)
            form = RequirementForm(request.POST,instance=requirements)
        if form.is_valid():
            form.save()
        return redirect('/SMS/requirements_list')

# List requirements
@login_required(login_url='login_page')
def requirements_list(request):
    first_name = request.session.get('first_name')
    context = {'requirements_list' : RequirementsInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/requirements_list.html",context)

#Delete requirements
@login_required(login_url='login_page')
def requirements_delete(request,requirements_id):
    requirements = RequirementsInfo.objects.get(pk=requirements_id)
    requirements.delete()
    return redirect('/SMS/requirements_list')