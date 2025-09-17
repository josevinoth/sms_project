from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date

from ..forms import IncidentReportForm
from ..models import IncidentReportInfo
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.core.paginator import Paginator


@login_required(login_url='login_page')
def incident_add(request,incident_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if incident_id == 0:
            form = IncidentReportForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
            }
        else:
            incident = IncidentReportInfo.objects.get(pk=incident_id)
            form = IncidentReportForm(instance=incident)
            context = {
                'form': form,
                'first_name': first_name,
            }
        return render(request, "asset_mgt_app/incident_report_add.html", context)

    else:
        if incident_id == 0:
            form = IncidentReportForm(request.POST)
        else:
            incident = IncidentReportInfo.objects.get(pk=incident_id)
            form = IncidentReportForm(request.POST, instance=incident)
        if form.is_valid():
            instance = form.save(commit=False)

            instance.save()
            if incident_id == 0:
                messages.success(request, 'Record Saved Successfully')
            else:
                messages.success(request, 'Record Updated Successfully')
        else:
            messages.error(request, 'Error: Please correct the errors below.')

        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error in {field}: {error}")
                messages.error(request, f"Error in {field}: {error}")
        return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def incident_list(request):
    first_name = request.session.get('first_name')
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)
    incident_list = IncidentReportInfo.objects.all()
    if from_date:
        incident_list = incident_list.filter(inc_updated_on__date__gte=from_date)

    if to_date:
        incident_list = incident_list.filter(inc_updated_on__date__lte=to_date)

    context = {
        'incident_list': incident_list,
        'first_name': first_name,
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, "asset_mgt_app/incident_report_list.html", context)


# Delete expense attachment
@login_required(login_url='login_page')
def incident_delete(request, incident_id):
        incident = IncidentReportInfo.objects.get(pk=incident_id)
        incident.delete()
        messages.success(request, 'Incident deleted successfully.')
        return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def incident_report(request):
    first_name = request.session.get('first_name')
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)
    incident_list = IncidentReportInfo.objects.all()
    if from_date:
        incident_list = incident_list.filter(inc_incident_date__date__gte=from_date)

    if to_date:
        incident_list = incident_list.filter(inc_incident_date__date__lte=to_date)

    context = {
        'incident_list': incident_list,
        'first_name': first_name,
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, "asset_mgt_app/incident_report.html", context)
