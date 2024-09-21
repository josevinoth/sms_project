# views.py
from django.shortcuts import redirect
from ..forms import warehouse_EmailForm
from ..sub_models.gatein_mod import Gatein_info
from ..views import send_department_email


def warehouse_send_email_view(request):
    if request.method == 'POST':
        form_warehouse_email = warehouse_EmailForm(request.POST)
        if form_warehouse_email.is_valid():
            recipient = form_warehouse_email.cleaned_data['recipient']
            subject = form_warehouse_email.cleaned_data['subject']
            message = form_warehouse_email.cleaned_data['message']
            job_number=request.session.get('ses_gatein_id_nam')
            gatein_email_count=Gatein_info.objects.get(gatein_job_no=job_number).gatein_email_count
            print('email_count_before', gatein_email_count)
            recipient_list = [email.strip() for email in recipient.split(',')]
            send_department_email('warehouse', subject, message, recipient_list)
            gatein_email_count=gatein_email_count+1
            print('gatein_email_count',gatein_email_count)
            Gatein_info.objects.filter(gatein_job_no=job_number).update(gatein_email_count=gatein_email_count)
            return redirect(request.META['HTTP_REFERER'])
