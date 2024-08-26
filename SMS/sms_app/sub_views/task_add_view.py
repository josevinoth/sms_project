from django.contrib.auth.decorators import login_required
from ..forms import taskaddForm
from ..models import task_Info
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def task_add(request,task_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if task_id == 0:
            form = taskaddForm()
        else:
            task=task_Info.objects.get(pk=task_id)
            form = taskaddForm(instance=task)
        return render(request, "asset_mgt_app/task_add.html", {'form': form,'first_name': first_name})
    else:
        if task_id == 0:
            form = taskaddForm(request.POST)
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
    task.delete()
    return redirect('/SMS/task_list')