from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..forms import timesheetaddForm
from ..models import task_Info,timesheet_Info
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def timesheet_add(request,timesheet_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if timesheet_id == 0:
            form = timesheetaddForm()
        else:
            timesheet=timesheet_Info.objects.get(pk=timesheet_id)
            form = timesheetaddForm(instance=timesheet)
        return render(request, "asset_mgt_app/timesheet_add.html", {'form': form,'first_name': first_name})
    else:
        if timesheet_id == 0:
            form = timesheetaddForm(request.POST)
        else:
            timesheet = timesheet_Info.objects.get(pk=timesheet_id)
            form = timesheetaddForm(request.POST,instance=timesheet)
        if form.is_valid():
            form.save()
        return redirect('/SMS/timesheet_list')

@login_required(login_url='login_page')
def timesheet_nav(request,task_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print("I am inside Get add timesheet_nav")
    timesheet_form = timesheetaddForm(request.POST)
    request.session['ses_task_id'] = task_id
    application=task_Info.objects.get(pk=task_id).application
    print('application',application)
    main_task=task_Info.objects.get(pk=task_id).main_task
    print('main_task', main_task)
    sub_task=task_Info.objects.get(pk=task_id).sub_task
    print('sub_task', sub_task)
    context = {
        'first_name': first_name,
        'user_id': user_id,
        'timesheet_form': timesheet_form,
        'application': application,
        'main_task': main_task,
        'sub_task': sub_task,
    }
    if timesheet_form.is_valid():
        timesheet_form.save()
        print("Main Form is Valid")
        messages.success(request, 'Record Updated Successfully')
    else:
        print("Main Form is not Valid")
        messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
    return render(request, "asset_mgt_app/timesheet_add.html", context)
# List timesheet
@login_required(login_url='login_page')
def timesheet_list(request):
    first_name = request.session.get('first_name')
    context = {'timesheet_list' : timesheet_Info.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/timesheet_list.html",context)

#Delete timesheet
@login_required(login_url='login_page')
def timesheet_delete(request,timesheet_id):
    timesheet = timesheet_Info.objects.get(pk=timesheet_id)
    timesheet.delete()
    return redirect('/SMS/timesheet_list')