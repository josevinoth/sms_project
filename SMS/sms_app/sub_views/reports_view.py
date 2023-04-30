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
    invoice_list=Warehouse_goods_info.objects.all().values_list('wh_goods_invoice',flat=True).distinct()
    print('invoice_list',invoice_list)
    checkin_goods_list=Warehouse_goods_info.objects.filter(wh_check_in_out=1).distinct()
    print('checkin_goods_list',checkin_goods_list)
    cursor = connection.cursor()
    # cursor.execute("SELECT * FROM sms_app_warehouse_goods_info w INNER JOIN sms_app_gatein_info g ON w.wh_job_no=g.gatein_job_no INNER JOIN sms_app_loadingbay_info l ON w.wh_job_no=l.lb_job_no LEFT JOIN sms_app_dispatch_info d on w.wh_dispatch_num=d.dispatch_num")
    cursor.execute("SELECT \
    		w.wh_job_no as WH_Job_Number,\
           	w.wh_qr_rand_num as Stock_number,\
    		w.wh_customer_name as Customer,\
    	  	g.gatein_arrival_date as Arrival_Date,\
           	l.lb_stock_unloading_start_time as Loading_Time,\
           	l.lb_stock_unloading_end_time as Unloading_Time,\
           	g.gatein_transporter as Transporter,\
           	g.gatein_truck_number as Truck_Number,\
           	g.gatein_shipper as Consignee,\
           	g.gatein_consignee as Consigner,\
           	re.received_not_name as DOCS_Received,\
    		d.dispatch_comments as HAWB,\
    	   	d.dispatch_destination as Destination,\
           	g.gatein_invoice as Customer_Invoice,\
    		g.gatein_actual_weight as Checkin_Weight,\
    		g.gatein_actual_count as Checkin_Qty,\
    		p.package_type as Package_Type,\
    		g.gatein_weight as Invoice_Weight,\
    		g.gatein_no_of_pkg as Invoice_Qty,\
    		w.wh_goods_length as Length,\
    		w.wh_goods_width as Width,\
    		w.wh_goods_height as Height,\
    		w.wh_goods_volume_weight as Volume_Weight,\
    		w.wh_goods_volume_weight as CBM,\
    		c.currency_type as Currency_Type,\
    		l.lb_stock_invoice_value as Invoice_Value,\
    		l.lb_stock_amount_in as Invoice_Value_INR,\
    		d.dispatch_destination as E_Way_Bill,\
    		w.wh_fumigation_date as Fumigation_Date,\
    		lo.loc_name as Branch,\
    		u.unit_name as Unit,\
    		b.bay_bayname as bay,\
           	ch.check_in_out_name as Checked_In_Out,\
    		w.wh_storage_time as Storage_Days\
    FROM sms_app_warehouse_goods_info w\
    INNER JOIN sms_app_gatein_info g ON g.gatein_job_no=w.wh_job_no\
    INNER JOIN sms_app_loadingbay_info l ON l.lb_job_no=w.wh_job_no\
    Left JOIN sms_app_dispatch_info d on d.dispatch_num=w.wh_dispatch_num\
    LEFT JOIN sms_app_unitinfo u ON u.id=w.wh_unit_id\
    LEFT JOIN sms_app_location_info lo ON lo.id=w.wh_branch_id\
    LEFT JOIN sms_app_bayinfo b ON b.id=w.wh_bay_id\
    LEFT JOIN sms_app_packagetype_info p ON p.id=w.wh_goods_package_type_id\
    LEFT JOIN sms_app_currency_type c ON c.id=l.lb_stock_invoice_currency_id\
    LEFT JOIN sms_app_received_not re ON re.id=l.lb_packing_list\
    LEFT JOIN sms_app_check_in_out ch ON ch.id=w.wh_check_in_out")
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
    return render(request,"asset_mgt_app/stock_values_report_new.html",context)

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