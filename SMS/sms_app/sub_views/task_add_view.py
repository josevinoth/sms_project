from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from ..forms import taskaddForm
from ..models import RequirementsInfo,timesheet_Info,task_Info
from django.shortcuts import render, redirect, get_object_or_404


@login_required(login_url='login_page')
def task_add(request,task_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if task_id == 0:
            form = taskaddForm()
        else:
            task=task_Info.objects.get(pk=task_id)
            form = taskaddForm(instance=task)
        return render(request, "asset_mgt_app/task_add.html", {'form': form,'first_name': first_name,'user_id':user_id})
    else:
        if task_id == 0:
            form = taskaddForm(request.POST)
            if form.is_valid():
                form.save()
            try:
                last_id = (task_Info.objects.values_list('id', flat=True)).last()
                task_number = 100000 + last_id
                # req_num_next = str('Req_') + str(int(((RequirementsInfo.objects.get(id=last_id)).req_number).replace('Req_', '')) + 1)
            except ObjectDoesNotExist:
                task_number = 100000
                # req_num_next = str('Req_') + str(randint(10000, 99999))
            task_num_next = str('Task_') + str(task_number)
            last_id = (task_Info.objects.values_list('id', flat=True)).last()
            task_Info.objects.filter(id=last_id).update(task_id=task_num_next)
        else:
            task = task_Info.objects.get(pk=task_id)
            form = taskaddForm(request.POST,instance=task)
            if form.is_valid():
                form.save()
        return redirect('/SMS/task_list')

# List task
@login_required(login_url='login_page')
def task_list(request):
    first_name = request.session.get('first_name')
    context = {'task_list' : task_Info.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/task_list.html",context)

#Delete task
@login_required(login_url='login_page')
def task_delete(request,task_id):
    task = task_Info.objects.get(pk=task_id)
    timesheet=timesheet_Info.objects.filter(ts_task_id=task_id)
    for i in timesheet:
        i.delete()
    task.delete()
    return redirect('/SMS/task_list')
@login_required(login_url='login_page')
def get_requirement_description(request):
    requirement_id = request.GET.get('id', None)
    if requirement_id:
        requirement = get_object_or_404(RequirementsInfo, id=requirement_id)
        data = {
            'description': requirement.req_backlogs  # Adjust based on your model's field name
        }
        return JsonResponse(data)
    return JsonResponse({'description': ''})