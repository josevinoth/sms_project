from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from ..forms import DsrForm
from ..models import Warehouse_goods_info


from django.shortcuts import redirect
from ..forms import dsr_EmailForm
from ..sub_models.gatein_mod import Gatein_info
from ..views import send_department_email

@login_required(login_url='login_page')
def dsr_reports(request):
    first_name = request.session.get('first_name')
    form = DsrForm(request.POST or None)
    customer_name = request.POST.get('ds_customer', '')
    goods_list = Warehouse_goods_info.objects.all()
    if customer_name:
        goods_list = goods_list.filter(wh_customer_name=customer_name)
        print(f"Filtering by customer name: {customer_name}")
    paginator = Paginator(goods_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'first_name': first_name,
        'form': form,
        'page_obj': page_obj,
        'customer_name': customer_name,
    }
    return render(request, "asset_mgt_app/dsr_report.html", context)


def dsr_send_email_view(request):
    if request.method == 'POST':
        form_dsr_email = dsr_EmailForm(request.POST)
        if form_dsr_email.is_valid():
            recipient = form_dsr_email.cleaned_data['recipient']
            subject = form_dsr_email.cleaned_data['subject']
            message = form_dsr_email.cleaned_data['message']
            job_number=request.session.get('ses_gatein_id_nam')
            gatein_email_count=Gatein_info.objects.get(gatein_job_no=job_number).gatein_email_count
            recipient_list = [email.strip() for email in recipient.split(',')]
            send_department_email('warehouse', subject, message, recipient_list)
            gatein_email_count=gatein_email_count+1
            Gatein_info.objects.filter(gatein_job_no=job_number).update(gatein_email_count=gatein_email_count)
            return redirect(request.META['HTTP_REFERER'])
