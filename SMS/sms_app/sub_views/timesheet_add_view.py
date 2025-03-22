from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..forms import timesheetaddForm
from ..models import task_Info,timesheet_Info,MyUser,RequirementsInfo
from django.shortcuts import render, redirect
import json
from django.db.models import Count, Q,Sum

@login_required(login_url='login_page')
def timesheet_add(request,timesheet_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if timesheet_id == 0:
            form = timesheetaddForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
            }
        else:
            task_id = timesheet_Info.objects.get(pk=timesheet_id).ts_task_id
            timesheet_list = timesheet_Info.objects.filter(ts_task_id=task_id)
            timesheet=timesheet_Info.objects.get(pk=timesheet_id)
            form = timesheetaddForm(instance=timesheet)
            context={
                        'form': form,
                        'first_name': first_name,
                        'timesheet_list':timesheet_list,
                        'user_id':user_id,
                    }
        return render(request, "asset_mgt_app/timesheet_add.html",context)
    else:
        if timesheet_id == 0:
            form = timesheetaddForm(request.POST)
        else:
            timesheet = timesheet_Info.objects.get(pk=timesheet_id)
            form = timesheetaddForm(request.POST,instance=timesheet)
        if form.is_valid():
            form.save()
        # return redirect('/SMS/timesheet_list')
        return redirect('/SMS/task_list')

@login_required(login_url='login_page')
def timesheet_nav(request,task_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print("I am inside Get add timesheet_nav")
    form = timesheetaddForm(request.POST)
    task_id=task_Info.objects.get(pk=task_id).id
    print('task_id',task_id)
    timesheet_list=timesheet_Info.objects.filter(ts_task_id=task_id)
    context = {
        'first_name': first_name,
        'user_id': user_id,
        'form': form,
        'task_id': task_id,
        'timesheet_list': timesheet_list,
        'timesheet_id': 0,
    }
    if form.is_valid():
        form.save()
        print("Main Form is Valid")
        messages.success(request, 'Record Updated Successfully')
        return redirect('/SMS/task_list')
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


@login_required(login_url='login_page')
def timesheet_report(request):
    first_name = request.session.get('first_name')
    selected_teammember = request.GET.get('teammember', None)
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    teammembers = MyUser.objects.select_related('user_extinfo').filter(
        user_extinfo__department__dept_name="IT", is_active=True
    ).distinct().values_list('first_name', flat=True)

    timesheet_summary = timesheet_Info.objects.filter(
        ts_updated_by__user_extinfo__department__dept_name="IT", ts_updated_by__is_active=True
    )

    if selected_teammember:
        timesheet_summary = timesheet_summary.filter(ts_updated_by__first_name=selected_teammember)
    if from_date:
        timesheet_summary = timesheet_summary.filter(ts_start_date__gte=from_date)
    if to_date:
        timesheet_summary = timesheet_summary.filter(ts_start_date__lte=to_date)

    # First Query: Get detailed data for table (keep per-task breakdown)
    timesheet_table = timesheet_summary.values(
        'ts_updated_by__first_name', 'ts_start_date',
        'ts_task_id__application__app_name', 'ts_task_id__main_task',
        'ts_task_id__sub_task', 'ts_task_id__task_id','ts_task_id__t_requirement_description','ts_task_id__t_requirement_id__req_number'
    ).annotate(total_hours=Sum('ts_hours'))

    # Second Query: Aggregate team-wise total hours (for chart)
    timesheet_chart = timesheet_summary.values('ts_updated_by__first_name').annotate(
        total_hours=Sum('ts_hours')
    )
    req_chart = timesheet_summary.values('ts_task_id__t_requirement_id__req_number').annotate(
        total_hours=Sum('ts_hours')
    )

    # Prepare chart data
    chart_labels = [entry['ts_updated_by__first_name'] for entry in timesheet_chart]
    chart_data = [entry['total_hours'] for entry in timesheet_chart]
    req_labels = [entry['ts_task_id__t_requirement_id__req_number'] for entry in req_chart]
    req_data =[entry['total_hours'] for entry in req_chart]
    context = {
        'first_name': first_name,
        'selected_teammember': selected_teammember,
        'teammembers': teammembers,
        'from_date': from_date,
        'to_date': to_date,
        'timesheet_summary': timesheet_table,  # Table data
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'req_labels': json.dumps(req_labels),
        'req_data': json.dumps(req_data),
    }

    return render(request, "asset_mgt_app/timesheet_report.html", context)
