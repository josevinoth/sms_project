import csv
from itertools import chain
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template.loader import get_template
from django.http import HttpResponse
from django.utils import timezone
from xhtml2pdf import pisa
from ..models import Gatein_info,LocationmasterInfo,Loadingbay_Info,DamagereportInfo,Warehouse_goods_info
from django.db.models.aggregates import Sum
from datetime import date, datetime,timedelta

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
    checkin_goods_list=Warehouse_goods_info.objects.all().values_list().distinct()
    # cursor = connection.cursor()
    # # cursor.execute("SELECT * FROM sms_app_warehouse_goods_info w INNER JOIN sms_app_gatein_info g ON w.wh_job_no=g.gatein_job_no INNER JOIN sms_app_loadingbay_info l ON w.wh_job_no=l.lb_job_no LEFT JOIN sms_app_dispatch_info d on w.wh_dispatch_num=d.dispatch_num")
    # cursor.execute("SELECT \
    #     		w.wh_job_no as WH_Job_Number,\
    #            	w.wh_qr_rand_num as Stock_number,\
    #     		w.wh_customer_name as Customer,\
    #     	  	g.gatein_arrival_date as Arrival_Date,\
    #            	l.lb_stock_unloading_start_time as Loading_Time,\
    #            	l.lb_stock_unloading_end_time as Unloading_Time,\
    #            	g.gatein_transporter as Transporter,\
    #            	g.gatein_truck_number as Truck_Number,\
    #            	g.gatein_shipper as Consigner,\
    #            	g.gatein_consignee as Consignee,\
    #            	re.received_not_name as DOCS_Received,\
    #     		g.gatein_hawb as HAWB,\
    #     	   	g.gatein_destination as Destination,\
    #            	g.gatein_invoice as Customer_Invoice,\
    #             w.wh_po_num as Case_Number,\
    #             w.wh_invoice_qty as Invoice_Qty,\
    #             w.wh_invoice_weight_unit as Invoice_Weight,\
    #     		w.wh_gross_weight as Checkin_Weight,\
    #             uo.uom_name as UOM,\
    #         	w.wh_goods_length as Length,\
    #         	w.wh_goods_width as Width,\
    #         	w.wh_goods_height as Height,\
    #     		w.wh_goods_pieces as Dims_Qty,\
    #     		p.package_type as Package_Type,\
    #     		w.wh_chargeable_weight as Volume_Weight,\
    #     		w.wh_cbm as CBM,\
    #             w.wh_invoice_value as Invoice_Value,\
    #     		c.currency_type as Currency_Type,\
    #     		w.wh_invoice_amount_inr as Invoice_Value_INR,\
    #     		l.lb_eway_bill as E_Way_Bill,\
    #     		l.lb_validity_date as E_Way_Bill_Validity,\
    #     		yn.ge_gstexcepmtion as Fumigation_Status,\
    #             ch.check_in_out_name as Checked_In_Out,\
    #     		lo.loc_name as Branch,\
    #     		u.unit_name as Unit,\
    #     		b.bay_bayname as bay,\
    #     		w.wh_storage_time as Storage_Days,\
    #             d.dispatch_truck_number as Truck_Number,\
    #             vt.vt_vehicletype as Truck_Type,\
    #             d.dispatch_depature_date as Truck_Out_Time,\
    #             lp.lp_name as Labels_Pasted_By,\
    #             d.dispatch_mawb as MAWB,\
    #             w.wh_dispatch_num as dispatch_Number\
    #     FROM sms_app_warehouse_goods_info w\
    #     INNER JOIN sms_app_gatein_info g ON g.gatein_job_no=w.wh_job_no\
    #     INNER JOIN sms_app_loadingbay_info l ON l.lb_job_no=w.wh_job_no\
    #     Left JOIN sms_app_dispatch_info d on d.dispatch_num=w.wh_dispatch_num\
    #     LEFT JOIN sms_app_unitinfo u ON u.id=w.wh_unit_id\
    #     LEFT JOIN sms_app_location_info lo ON lo.id=w.wh_branch_id\
    #     LEFT JOIN sms_app_bayinfo b ON b.id=w.wh_bay_id\
    #     LEFT JOIN sms_app_packagetype_info p ON p.id=w.wh_goods_package_type_id\
    #     LEFT JOIN sms_app_currency_type c ON c.id=l.lb_stock_invoice_currency_id\
    #     LEFT JOIN sms_app_received_not re ON re.id=l.lb_packing_list\
    #     LEFT JOIN sms_app_check_in_out ch ON ch.id=w.wh_check_in_out\
    #     LEFT JOIN sms_app_uom uo ON uo.id=w.wh_uom\
    #     LEFT JOIN sms_app_vehicletypeinfo vt ON vt.id = d.dispatch_truck_type_id\
    #     LEFT JOIN sms_app_labels_pasted_info lp ON lp.id = d.dispatch_sticker_pasted_bvm\
    #     LEFT JOIN sms_app_gstexcemptioninfo yn ON yn.id = w.wh_fumigation_process")
    # row = cursor.fetchall()

    # calculate storage days
    # stocks=list(Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_qr_rand_num',flat=True))
    print("Before Loop")
    stocks = list(Warehouse_goods_info.objects.filter(wh_check_in_out=1).values_list('wh_qr_rand_num', flat=True))
    for i in stocks:
        try:
            check_in_date = datetime.date(Warehouse_goods_info.objects.get(wh_qr_rand_num=i).wh_checkin_time)
            current_date = date.today()
            date_diff = (current_date - check_in_date)  # Differnce between dates
            date_diff_days = date_diff.days
            Warehouse_goods_info.objects.filter(wh_qr_rand_num=i).update(wh_storage_time=date_diff_days)
        except TypeError:
            pass
    print("After Loop")
    goods_list=(Warehouse_goods_info.objects.all()).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(goods_list, 50)
    page_obj = paginator.get_page(page_number)

    ########### Calculate Check-In & Check-Out stock value####################
    # Calculate Check - In & Check - Out stock value - Current Day
    # Get the current date
    current_date = datetime.now()
    print(current_date)
    # Calculate the first day of the current month
    first_day_of_current_month = datetime(current_date.year, current_date.month, 1)
    # Chennai Warehouse
    maa_in_stock_value_cud = (Warehouse_goods_info.objects.filter(wh_branch=2,wh_check_in_out=1,wh_checkin_time__lte=current_date)).aggregate(Sum('wh_invoice_amount_inr'))['wh_invoice_amount_inr__sum']
    if maa_in_stock_value_cud is not None:
        maa_in_stock_value_cud_val = maa_in_stock_value_cud
    else:
        maa_in_stock_value_cud_val = 0

    maa_out_stock_value_cud = (Warehouse_goods_info.objects.filter(wh_branch=2,wh_check_in_out=2,wh_checkin_time__lte=current_date)).aggregate(Sum('wh_invoice_amount_inr'))['wh_invoice_amount_inr__sum']
    if maa_out_stock_value_cud is not None:
        maa_out_stock_value_cud_val = maa_out_stock_value_cud
    else:
        maa_out_stock_value_cud_val = 0

    maa_total_cud = (Warehouse_goods_info.objects.filter(wh_branch=2, wh_checkin_time__lte=current_date)).aggregate(Sum('wh_invoice_amount_inr'))['wh_invoice_amount_inr__sum']
    if maa_total_cud is not None:
        maa_total_cud_val = maa_total_cud
    else:
        maa_total_cud_val = 0

    # Bengaluru Warehouse
    blr_in_stock_value_cud = (Warehouse_goods_info.objects.filter(wh_branch=1, wh_check_in_out=1, wh_checkin_time__lte=current_date)).aggregate(Sum('wh_invoice_amount_inr'))['wh_invoice_amount_inr__sum']
    if blr_in_stock_value_cud is not None:
        blr_in_stock_value_cud_val = blr_in_stock_value_cud
    else:
        blr_in_stock_value_cud_val = 0

    blr_out_stock_value_cud = (Warehouse_goods_info.objects.filter(wh_branch=1, wh_check_in_out=2, wh_checkin_time__lte=current_date)).aggregate(Sum('wh_invoice_amount_inr'))['wh_invoice_amount_inr__sum']
    if blr_out_stock_value_cud is not None:
        blr_out_stock_value_cud_val = blr_out_stock_value_cud
    else:
        blr_out_stock_value_cud_val = 0

    blr_total_cud = (Warehouse_goods_info.objects.filter(wh_branch=1, wh_checkin_time__lte=current_date)).aggregate(Sum('wh_invoice_amount_inr'))['wh_invoice_amount_inr__sum']
    if blr_total_cud is not None:
        blr_total_cud_val = blr_total_cud
    else:
        blr_total_cud_val = 0

    # Hyderabad Warehouse
    hyd_in_stock_value_cud = (Warehouse_goods_info.objects.filter(wh_branch=4, wh_check_in_out=1,wh_checkin_time__lte=current_date)).aggregate(
        Sum('wh_invoice_amount_inr'))['wh_invoice_amount_inr__sum']
    if hyd_in_stock_value_cud is not None:
        hyd_in_stock_value_cud_val = hyd_in_stock_value_cud
    else:
        hyd_in_stock_value_cud_val = 0

    hyd_out_stock_value_cud = (Warehouse_goods_info.objects.filter(wh_branch=4, wh_check_in_out=2,wh_checkin_time__lte=current_date)).aggregate(
        Sum('wh_invoice_amount_inr'))['wh_invoice_amount_inr__sum']
    if hyd_out_stock_value_cud is not None:
        hyd_out_stock_value_cud_val = hyd_out_stock_value_cud
    else:
        hyd_out_stock_value_cud_val = 0

    hyd_total_cud = (Warehouse_goods_info.objects.filter(wh_branch=4, wh_checkin_time__lte=current_date)).aggregate(Sum('wh_invoice_amount_inr'))['wh_invoice_amount_inr__sum']
    if hyd_total_cud is not None:
        hyd_total_cud_val = hyd_total_cud
    else:
        hyd_total_cud_val = 0

    # Pondichery Warehouse
    pny_in_stock_value_cud = (Warehouse_goods_info.objects.filter(wh_branch=3, wh_check_in_out=1,wh_checkin_time__lte=current_date)).aggregate(Sum('wh_invoice_amount_inr'))['wh_invoice_amount_inr__sum']
    if pny_in_stock_value_cud is not None:
        pny_in_stock_value_cud_val = pny_in_stock_value_cud
    else:
        pny_in_stock_value_cud_val = 0

    pny_out_stock_value_cud = (Warehouse_goods_info.objects.filter(wh_branch=3, wh_check_in_out=2,wh_checkin_time__lte=current_date)).aggregate(Sum('wh_invoice_amount_inr'))['wh_invoice_amount_inr__sum']
    if pny_out_stock_value_cud is not None:
        pny_out_stock_value_cud_val = pny_out_stock_value_cud
    else:
        pny_out_stock_value_cud_val = 0

    pny_total_cud = (Warehouse_goods_info.objects.filter(wh_branch=3, wh_checkin_time__lte=current_date)).aggregate(Sum('wh_invoice_amount_inr'))['wh_invoice_amount_inr__sum']
    if pny_total_cud is not None:
        pny_total_cud_val = pny_total_cud
    else:
        pny_total_cud_val = 0
    context = {
                'stock_value_list': Loadingbay_Info.objects.all(),
                'first_name': first_name,
                'checkin_goods_list': checkin_goods_list,
                'page_obj': page_obj,
                'maa_in_stock_value_cud': round(maa_in_stock_value_cud_val,0),
                'maa_out_stock_value_cud': round(maa_out_stock_value_cud_val,0),
                'maa_total_cud': round(maa_total_cud_val,0),
                'blr_in_stock_value_cud': round(blr_in_stock_value_cud_val, 0),
                'blr_out_stock_value_cud': round(blr_out_stock_value_cud_val, 0),
                'blr_total_cud': round(blr_total_cud_val, 0),
                'hyd_in_stock_value_cud': round(hyd_in_stock_value_cud_val, 0),
                'hyd_out_stock_value_cud': round(hyd_out_stock_value_cud_val, 0),
                'hyd_total_cud': round(hyd_total_cud_val, 0),
                'pny_in_stock_value_cud': round(pny_in_stock_value_cud_val, 0),
                'pny_out_stock_value_cud': round(pny_out_stock_value_cud_val, 0),
                'pny_total_cud': round(pny_total_cud_val, 0),
                # 'goods_list': goods_list,
                # 'row': row,
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

def export_stockreport_to_csv(request):
    # Fetch your data from the model or any other data source
    data = (Warehouse_goods_info.objects.all()).order_by('-id')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Stock_Report.csv"'

    writer = csv.writer(response)

    # Write the header row
    writer.writerow(['Job Number', 'Stock Number', 'Customer','Date Of Arrival','Unloading Start Time','Unloading End Time','Transporter','Truck Number','Consigner','Consignee','Docs Received','HAWB','Destination','Invoice Number','Case Number','Invoice Qty','Invoice Weight (kg)','Checkin Weight (kg)','UOM','Length','Width','Height','Dims Qty','Package Type','Volume Weight','CBM','Invoice Value','Invoice Currency','Invoice (INR)','E-Way Bill#','E-Way Bill Validity','Fumigation Status','Check In-Out?','Branch','Unit','Bay','Storage Days','Truck_Number(Out)','Truck_Type(Out)','Truck_Depature_Time(Out)','Labels_Pasted_By','MAWB','Dispatch_Number'])  # Replace with actual column names

    # Iterate through the data and apply modifications as needed
    for stock_value in data:
        # Check if the item or its attributes are None
        if stock_value is not None:
            try:
                Job_Number=stock_value.wh_job_no
            except:
                Job_Number='null'

            try:
                Stock_Number=stock_value.wh_qr_rand_num
            except:
                Stock_Number='null'

            try:
                Customer=stock_value.wh_customer_name
            except:
                Customer='null'

            try:
                Date_Of_Arrival=((stock_value.wh_gate_injob_no_id.gatein_arrival_date).astimezone(timezone.get_current_timezone())).strftime('%Y-%m-%d %H:%M:%S')
            except:
                Date_Of_Arrival='null'

            try:
                Unloading_Start_Time=((stock_value.wh_lb_job_no_id.lb_stock_unloading_start_time).astimezone(timezone.get_current_timezone())).strftime('%Y-%m-%d %H:%M:%S')
            except:
                Unloading_Start_Time='null'

            try:
                Unloading_End_Time=((stock_value.wh_lb_job_no_id.lb_stock_unloading_end_time).astimezone(timezone.get_current_timezone())).strftime('%Y-%m-%d %H:%M:%S')
            except:
                Unloading_End_Time='null'

            try:
                Transporter=stock_value.wh_gate_injob_no_id.gatein_transporter
            except:
                Transporter='null'

            try:
                Truck_Number=stock_value.wh_gate_injob_no_id.gatein_truck_number
            except:
                Truck_Number='null'

            try:
                Consigner=stock_value.wh_consigner
            except:
                Consigner='null'

            try:
                Consignee=stock_value.wh_consignee
            except:
                Consignee='null'

            try:
                Docs_Received=stock_value.wh_lb_job_no_id.lb_packing_list
            except:
                Docs_Received='null'

            try:
                HAWB= stock_value.wh_gate_injob_no_id.gatein_hawb
            except:
                HAWB='null'

            try:
                Destination=stock_value.wh_gate_injob_no_id.gatein_destination
            except:
                Destination='null'

            try:
                Invoice_Number=stock_value.wh_gate_injob_no_id.gatein_invoice
            except:
                Invoice_Number='null'

            try:
                Case_Number=stock_value.wh_po_num
            except:
                Case_Number='null'

            try:
                Invoice_Qty=stock_value.wh_total_qty
            except:
                Invoice_Qty='null'

            try:
                Invoice_Weight_kg=stock_value.wh_gross_weight
            except:
                Invoice_Weight_kg='null'

            try:
                Checkin_Weight_kg=stock_value.wh_invoice_weight_unit
            except:
                Checkin_Weight_kg='null'

            try:
                UOM=stock_value.wh_uom
            except:
                UOM='null'

            try:
                Length=stock_value.wh_goods_length
            except:
                Length='null'

            try:
                Width=stock_value.wh_goods_width
            except:
                Width='null'

            try:
                Height=stock_value.wh_goods_height
            except:
                Height='null'

            try:
                Dims_Qty=stock_value.wh_goods_pieces
            except:
                Dims_Qty='null'

            try:
                Package_Type=stock_value.wh_goods_package_type
            except:
                Package_Type='null'

            try:
                Volume_Weight=stock_value.wh_chargeable_weight
            except:
                Volume_Weight='null'

            try:
                CBM=stock_value.wh_cbm
            except:
                CBM='null'

            try:
                Invoice_Value=stock_value.wh_invoice_value
            except:
                Invoice_Value='null'

            try:
                Invoice_Currency=stock_value.wh_lb_job_no_id.lb_stock_invoice_currency
            except:
                Invoice_Currency='null'

            try:
                Invoice_INR=stock_value.wh_invoice_amount_inr
            except:
                Invoice_INR='null'

            try:
                E_Way_Bill=stock_value.wh_lb_job_no_id.lb_eway_bill
            except:
                E_Way_Bill='null'

            try:
                E_Way_Bill_Validity=((stock_value.wh_lb_job_no_id.lb_validity_date).astimezone(timezone.get_current_timezone())).strftime('%Y-%m-%d %H:%M:%S')
            except:
                E_Way_Bill_Validity='null'

            try:
                Fumigation_Status=stock_value.wh_fumigation_process
            except:
                Fumigation_Status='null'

            try:
                Check_In_Out=stock_value.wh_check_in_out
            except:
                Check_In_Out='null'

            try:
                Branch=stock_value.wh_branch
            except:
                Branch='null'

            try:
                Unit=stock_value.wh_unit
            except:
                Unit='null'

            try:
                Bay=stock_value.wh_bay
            except:
                Bay='null'

            try:
                Storage_Days=stock_value.wh_storage_time
            except:
                Storage_Days='null'

            try:
                # Truck_Number_out=stock_value.wh_dispatch_id.dispatch_truck_number if stock_value.wh_dispatch_id.dispatch_truck_number is not None else 'null',
                Truck_Number_out=stock_value.wh_dispatch_id.dispatch_truck_number
            except:
                Truck_Number_out='null'

            try:
                # Truck_Type_out=stock_value.wh_dispatch_id.dispatch_truck_type if stock_value.wh_dispatch_id.dispatch_truck_type is not None else 'null',
                Truck_Type_out=stock_value.wh_dispatch_id.dispatch_truck_type
            except:
                Truck_Type_out='null'
            try:
                # Truck_Depature_Time_out=stock_value.wh_dispatch_id.dispatch_depature_date if stock_value.wh_dispatch_id.dispatch_depature_date is not None else 'null',
                Truck_Depature_Time_out=((stock_value.wh_dispatch_id.dispatch_depature_date).astimezone(timezone.get_current_timezone())).strftime('%Y-%m-%d %H:%M:%S')
            except:
                Truck_Depature_Time_out='null'
            try:
                # Labels_Pasted_By=stock_value.wh_dispatch_id.dispatch_sticker_pasted_bvm if stock_value.wh_dispatch_id.dispatch_sticker_pasted_bvm is not None else 'null',
                Labels_Pasted_By=stock_value.wh_dispatch_id.dispatch_sticker_pasted_bvm
            except:
                Labels_Pasted_By='null'
            try:
                # MAWB=stock_value.wh_dispatch_id.dispatch_mawb if stock_value.wh_dispatch_id.dispatch_mawb is not None else 'null',
                MAWB=stock_value.wh_dispatch_id.dispatch_mawb
            except:
                MAWB='null'
            try:
                # Dispatch_Number=stock_value.wh_dispatch_id.dispatch_num if stock_value.wh_dispatch_id.dispatch_num is not None else 'null',
                Dispatch_Number=stock_value.wh_dispatch_id.dispatch_num
            except:
                Dispatch_Number='null'

            writer.writerow([Job_Number,Stock_Number,Customer,Date_Of_Arrival,Unloading_Start_Time,Unloading_End_Time,Transporter,Truck_Number,Consigner,Consignee,Docs_Received,HAWB,Destination,Invoice_Number,Case_Number,Invoice_Qty,Invoice_Weight_kg,Checkin_Weight_kg,UOM,Length,Width,Height,Dims_Qty,Package_Type,Volume_Weight,CBM,Invoice_Value,Invoice_Currency,Invoice_INR,E_Way_Bill,E_Way_Bill_Validity,Fumigation_Status,Check_In_Out,Branch,Unit,Bay,Storage_Days,Truck_Number_out,Truck_Type_out,Truck_Depature_Time_out,Labels_Pasted_By,MAWB,Dispatch_Number])
        else:
            # Handle the case where the item is None (e.g., the object doesn't exist)
            writer.writerow(['NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA','NA'])
    return response