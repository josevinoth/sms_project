from django.contrib.auth.decorators import login_required
from ..forms import RequirementForm
from ..models import RequirementsInfo
from django.shortcuts import render, redirect
from random import randint
from django.contrib import messages

@login_required(login_url='login_page')
def requirements_add(request,requirements_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    # Generate Random requirement number
    last_id = (RequirementsInfo.objects.values_list('id', flat=True)).last()
    if last_id == None:
        last_id = 0
    req_num = randint(10000, 99999) + last_id + 1
    if request.method == "GET":
        if requirements_id == 0:
            form = RequirementForm()
        else:
            requirements=RequirementsInfo.objects.get(pk=requirements_id)
            form = RequirementForm(instance=requirements)
        context={
                'form': form,
                'first_name': first_name,
                'req_num': req_num,
                'user_id': user_id,
                }
        return render(request, "asset_mgt_app/requirements_add.html", context)
    else:
        if requirements_id == 0:
            form = RequirementForm(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                print("Requirement Form is Valid")
                req_number = request.POST.get('req_number')
                req_id = RequirementsInfo.objects.get(req_number=req_number).id
                messages.success(request, 'Record Updated Successfully')
                return redirect('/SMS/requirements_update/'+ str(req_id))
            else:
                print("Requirement Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            requirements = RequirementsInfo.objects.get(pk=requirements_id)
            form = RequirementForm(request.POST,request.FILES,instance=requirements)
            if form.is_valid():
                form.save()
                print("Requirement Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Requirement Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

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