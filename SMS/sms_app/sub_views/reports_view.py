from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from ..models import Gatein_info


@login_required(login_url='login_page')
def reports(request):
    first_name = request.session.get('first_name')
    context = {
               'first_name': first_name
               }
    return render(request,"asset_mgt_app/reports.html",context)

@login_required(login_url='login_page')
def damage_report_pdf(request):
    wh_job_id = request.session.get('ses_gatein_id_nam')
    print('wh_job_id',wh_job_id)
    damage_list=Gatein_info.objects.filter(gatein_job_no=wh_job_id)
    print(damage_list)
    context={
        'damage_list':damage_list,
    }
    template_path='asset_mgt_app/damage_report_new.html'
    response=HttpResponse(content_type='application/pdf')
    response['Content-Disposition']='attachment; filename="Damage_Report.pdf"'

    template=get_template(template_path)
    html=template.render(context)

    # Create PDF
    pisa_status=pisa.CreatePDF(html,dest=response)

    if pisa_status.err:
        return HttpResponse('We has some error <pre>'+ html +'</pre>')
    return response
    # # Create the HttpResponse object with the appropriate PDF headers.
    # response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename="Damage_Report.pdf"'
    #
    # buffer = BytesIO()
    #
    # # Create the PDF object, using the BytesIO object as its "file."
    # p = canvas.Canvas(buffer)
    # ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
    # print(ses_gatein_id_nam)
    # # Draw things on the PDF. Here's where the PDF generation happens.
    # # See the ReportLab documentation for the full list of functionality.
    # # p.drawString(100, 100, "Hello world.")
    # p.drawString(50, 100, ses_gatein_id_nam)
    # p.setTitle("ReportLab PDF Generation User Guide")
    # # Close the PDF object cleanly.
    # p.showPage()
    # p.save()
    #
    # # Get the value of the BytesIO buffer and write it to the response.
    # pdf = buffer.getvalue()
    # buffer.close()
    # response.write(pdf)
    # return response