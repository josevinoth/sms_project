from itertools import chain

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from ..models import Gatein_info,LocationmasterInfo,Loadingbay_Info,DamagereportInfo,Warehouse_goods_info
from django.db import connection

@login_required(login_url='login_page')
def reports(request):
    first_name = request.session.get('first_name')
    context = {
               'first_name': first_name
               }
    return render(request,"asset_mgt_app/reports.html",context)

@login_required(login_url='login_page')
def warehouse_reports(request):
    first_name = request.session.get('first_name')
    context = {
               'first_name': first_name
               }
    return render(request,"asset_mgt_app/warehouse_reports.html",context)

@login_required(login_url='login_page')
def space_utilization_reports(request):
    first_name = request.session.get('first_name')
    context = {
                'space_utilization_list': LocationmasterInfo.objects.all(),
                'first_name': first_name,
                }
    return render(request,"asset_mgt_app/space_utilization_report.html",context)

@login_required(login_url='login_page')
def stock_value_reports(request):
    print("Inside Stock Value Report")
    goods_list=[]
    goods_list_new=[]

    first_name = request.session.get('first_name')
    invoice_list=Warehouse_goods_info.objects.filter(wh_check_in_out=1).values_list('wh_goods_invoice',flat=True).distinct()
    checkin_goods_list=Warehouse_goods_info.objects.filter(wh_check_in_out=1)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM sms_app_warehouse_goods_info w INNER JOIN sms_app_gatein_info g ON w.wh_job_no=g.gatein_job_no INNER JOIN sms_app_loadingbay_info l ON w.wh_job_no=l.lb_job_no LEFT JOIN sms_app_dispatch_info d on w.wh_dispatch_num=d.dispatch_num")
    row = cursor.fetchall()

    for i in invoice_list:
        goods_list.append(Gatein_info.objects.filter(gatein_invoice=i))

    context = {
                'stock_value_list': Loadingbay_Info.objects.all(),
                'first_name': first_name,
                'checkin_goods_list': checkin_goods_list,
                'goods_list': goods_list,
                'row': row,
                 }
    return render(request,"asset_mgt_app/stock_values_report.html",context)

@login_required(login_url='login_page')
def damage_reports_list(request):
    first_name = request.session.get('first_name')
    damage_list=DamagereportInfo.objects.all()
    gate_in_list=Gatein_info.objects.all()
    result_list = list(chain(damage_list, gate_in_list))
    context = {
                'result_list':result_list,
                'damage_list': DamagereportInfo.objects.all(),
                'first_name': first_name,
                }
    return render(request,"asset_mgt_app/damage_report.html",context)

@login_required(login_url='login_page')
def deviation_report(request):
    first_name = request.session.get('first_name')
    deviation_list=Warehouse_goods_info.objects.all()
    context = {
                'deviation_list': deviation_list,
                'first_name': first_name,
                }
    return render(request,"asset_mgt_app/deviation_report.html",context)

@login_required(login_url='login_page')
def damage_report_pdf(request):
    wh_job_id = request.session.get('ses_gatein_id_nam')
    print('wh_job_id',wh_job_id)
    damage_list=Gatein_info.objects.filter(gatein_job_no=wh_job_id)
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