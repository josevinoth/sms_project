from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from ..forms import IncidentReportForm,IncidentEmailForm
from ..models import IncidentReportInfo
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from django.core.paginator import Paginator
from ..views import send_department_email


@login_required(login_url='login_page')
def incident_add(request, incident_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    form_incident_email = IncidentEmailForm()  # initialize for both add/edit

    if request.method == "GET":
        if incident_id == 0:
            form = IncidentReportForm()
        else:
            incident = IncidentReportInfo.objects.get(pk=incident_id)
            form = IncidentReportForm(instance=incident)

        context = {
            'form': form,
            'first_name': first_name,
            'form_incident_email': form_incident_email,
            'user_id': user_id,
        }
        return render(request, "asset_mgt_app/incident_report_add.html", context)
    else:
        # POST - save the incident
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
                    messages.error(request, f"Error in {field}: {error}")

        return redirect(request.META['HTTP_REFERER'])



@login_required(login_url='login_page')
def incident_list(request):
    first_name = request.session.get('first_name')
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)
    incident_list = IncidentReportInfo.objects.select_related('inc_branch', 'inc_unit', 'inc_customer', 'inc_details', 'inc_status', 'inc_approval_status').all()
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
    incident_list = IncidentReportInfo.objects.select_related('inc_branch', 'inc_unit', 'inc_customer', 'inc_details', 'inc_status', 'inc_approval_status').all()
    if from_date:
        incident_list = incident_list.filter(inc_incident_date__date__gte=from_date)

    if to_date:
        incident_list = incident_list.filter(inc_incident_date__date__lte=to_date)

    if request.GET.get('draw'):
        from django.http import JsonResponse
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))

        total_records = incident_list.count()
        paginated_list = incident_list[start:start+length]

        data = []
        for item in paginated_list:
            data.append([
                str(item.id),
                item.inc_incident_date.strftime('%b %d, %Y, %I:%M %p') if item.inc_incident_date else '',
                str(item.inc_branch if item.inc_branch else ''),
                str(item.inc_unit if item.inc_unit else ''),
                str(item.inc_customer if item.inc_customer else ''),
                str(item.inc_details if item.inc_details else ''),
                str(item.inc_analysis if item.inc_analysis else ''),
                item.inc_CAPA_issueddate.strftime('%b. %d, %Y') if item.inc_CAPA_issueddate else 'None',
                item.inc_CAPA_closeddate.strftime('%b. %d, %Y') if item.inc_CAPA_closeddate else 'None',
                str(item.inc_status if item.inc_status else ''),
                str(item.inc_approval_status if item.inc_approval_status else '')
            ])

        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': data
        })

    context = {
        'first_name': first_name,
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, "asset_mgt_app/incident_report.html", context)



@login_required(login_url='login_page')
def incident_send_email(request):
    if request.method == 'POST':
        form_incident_email = IncidentEmailForm(request.POST)
        if form_incident_email.is_valid():
            recipient = form_incident_email.cleaned_data.get("recipient")
            subject = form_incident_email.cleaned_data.get("subject", "Incident Report")
            message = form_incident_email.cleaned_data.get("message", "")

            if not recipient:
                messages.error(request, "Please provide a recipient email.")
                return redirect(request.META.get('HTTP_REFERER', '/'))

            recipient_list = [email.strip() for email in recipient.split(",") if email.strip()]
            send_department_email('warehouse', subject, message.replace('\n', '<br>'), recipient_list, email_type=1)

            messages.success(request, "Incident email sent successfully.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.error(request, "Form is invalid. Please check your input.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

    messages.error(request, "Invalid request method.")
    return redirect(request.META.get('HTTP_REFERER', '/'))



