from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q

from ..forms import RequirementForm
from ..models import RequirementsInfo
from django.shortcuts import render, redirect
from random import randint
from django.contrib import messages

@login_required(login_url='login_page')
def requirements_add(request,requirements_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if requirements_id == 0:
            form = RequirementForm()
        else:
            requirements=RequirementsInfo.objects.get(pk=requirements_id)
            form = RequirementForm(instance=requirements)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                }
        return render(request, "asset_mgt_app/requirements_add.html", context)
    else:
        if requirements_id == 0:
            form = RequirementForm(request.POST,request.FILES)
            if form.is_valid():
                # Generate Random requirement number
                try:
                    last_id = (RequirementsInfo.objects.values_list('id', flat=True)).last()
                    req_num_next = str('Req_') + str(int(((RequirementsInfo.objects.get(id=last_id)).req_number).replace('Req_', '')) + 1)
                except ObjectDoesNotExist:
                    req_num_next = str('Req_') + str(randint(10000, 99999))
                form.save()
                print("Requirement Form is Valid")
                last_id = (RequirementsInfo.objects.values_list('id', flat=True)).last()
                RequirementsInfo.objects.filter(id=last_id).update(req_number=req_num_next)
                req_id = RequirementsInfo.objects.get(req_number=req_num_next).id
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
    requirements_list= (RequirementsInfo.objects.all()).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(requirements_list, 10000)
    page_obj = paginator.get_page(page_number)
    context = {
                'requirements_list' : requirements_list,
                'first_name': first_name,
                'page_obj': page_obj,
                }
    return render(request,"asset_mgt_app/requirements_list.html",context)

@login_required(login_url='login_page')
def requirements_search(request):
    global requirements_list
    first_name = request.session.get('first_name')
    requirement_number = request.GET.get('requirement_number')
    print('requirement_number',requirement_number)
    if not requirement_number:
        requirement_number = ""
    requirements_list = RequirementsInfo.objects.filter((Q(req_number__icontains=requirement_number)) | (Q(req_number__isnull=True))).order_by('-id')
    # requirements_list= (RequirementsInfo.objects.all()).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(requirements_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
            'requirements_list' : requirements_list,
            'first_name': first_name,
            'page_obj': page_obj,
            }
    return render(request,"asset_mgt_app/requirements_list.html",context)
#Delete requirements
@login_required(login_url='login_page')
def requirements_delete(request,requirements_id):
    requirements = RequirementsInfo.objects.get(pk=requirements_id)
    requirements.delete()
    return redirect('/SMS/requirements_search')