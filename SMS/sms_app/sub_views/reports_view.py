import csv
from itertools import chain
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q, ExpressionWrapper, fields, F, DurationField, Func, Value, CharField
from django.db.models.functions import Cast, Extract
from django.shortcuts import render
from django.template.loader import get_template
from django.http import HttpResponse
from django.utils import timezone
from xhtml2pdf import pisa
from ..models import ExpenseInfo,Gatein_info,LocationmasterInfo,Loadingbay_Info,DamagereportInfo,Warehouse_goods_info
from datetime import date, datetime,timedelta
from django.db.models import Count, Sum
import openpyxl
from openpyxl.styles import Font, Border, Side, PatternFill, Alignment


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
    first_name = request.session.get('first_name')
    # Calculate and update wh_storage_time on the database side
    Warehouse_goods_info.objects.filter(wh_check_in_out=1).update(
        wh_storage_time=Cast(
            Extract(ExpressionWrapper(
                date.today()-F('wh_checkin_time'),
                output_field=DurationField()
            ), 'days'),
            output_field=fields.FloatField()  # Cast to double precision
        )
    )
    checkin_goods_list=Warehouse_goods_info.objects.all().values_list().distinct()


    goods_list=(Warehouse_goods_info.objects.all()).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(goods_list, 50)
    page_obj = paginator.get_page(page_number)


    current_date = datetime.now()

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
                 }
    return render(request,"asset_mgt_app/stock_values_report.html",context)
@login_required(login_url='login_page')
def damage_reports_list(request):
    first_name = request.session.get('first_name')
    damage_list=DamagereportInfo.objects.exclude(dam_damage_type=6)
    gate_in_list=Gatein_info.objects.all()
    result_list = list(chain(damage_list, gate_in_list))
    context = {
                'result_list':result_list,
                'damage_list': damage_list,
                'first_name': first_name,
                }
    return render(request,"asset_mgt_app/damage_report.html",context)

@login_required(login_url='login_page')
def deviation_report(request):
    first_name = request.session.get('first_name')
    deviation_list=Warehouse_goods_info.objects.filter(Q(wh_weights_deviation=1) | Q(wh_dimension_deviation=1)| Q(wh_no_of_units_deviation=1)| (~Q(wh_damages=6))| Q(wh_mismatches=1))
    context = {
                'deviation_list': deviation_list,
                'first_name': first_name,
                }
    return render(request,"asset_mgt_app/deviation_report.html",context)

@login_required(login_url='login_page')
def revenue_report(request):
    first_name = request.session.get('first_name')
    revenue_list=Warehouse_goods_info.objects.exclude(wh_voucher_num__isnull=True)
    context = {
                'revenue_list': revenue_list,
                'first_name': first_name,
                }
    return render(request,"asset_mgt_app/revenue_report.html",context)

@login_required(login_url='login_page')
def profit_loss_report(request):
    first_name = request.session.get('first_name')
    expense_list=ExpenseInfo.objects.all()

    context = {
                'expense_list': expense_list,
                'first_name': first_name,
                }
    return render(request,"asset_mgt_app/expense_report.html",context)

@login_required(login_url='login_page')
def expense_report(request):
    first_name = request.session.get('first_name')
    expense_list=ExpenseInfo.objects.all()
    context = {
                'expense_list': expense_list,
                'first_name': first_name,
                }
    return render(request,"asset_mgt_app/expense_report.html",context)
@login_required(login_url='login_page')
def damage_report_pdf(request):
    wh_job_id = request.session.get('ses_gatein_id_nam')
    damage_list=DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id)
    context={
        'damage_list':damage_list,
    }
    file_name=str("Damage_Report_")+str(wh_job_id)+str(".pdf")
    template_path='asset_mgt_app/damage_report_pdf.html'
    response=HttpResponse(content_type='application/pdf')
    response['Content-Disposition']=f'attachment; filename={file_name}'

    template=get_template(template_path)
    html=template.render(context)

    # Create PDF
    pisa_status=pisa.CreatePDF(html,dest=response)

    if pisa_status.err:
        return HttpResponse('We has some error <pre>'+ html +'</pre>')
    return response

def export_stockreport_to_csv(request):
    four_months_ago = timezone.now() - timedelta(days=120)

    # Get relevant data
    data = Warehouse_goods_info.objects.filter(
        Q(wh_check_in_out=1) | (Q(wh_check_in_out=2, wh_checkout_time__gte=four_months_ago))
    ).annotate(
        arrival_date=ExpressionWrapper(F('wh_gate_injob_no_id__gatein_arrival_date'),
                                       output_field=fields.DateTimeField()),
        unloading_start_time=ExpressionWrapper(F('wh_lb_job_no_id__lb_stock_unloading_start_time'),
                                               output_field=fields.DateTimeField()),
        unloading_end_time=ExpressionWrapper(F('wh_lb_job_no_id__lb_stock_unloading_end_time'),
                                             output_field=fields.DateTimeField()),
        eway_bill_validity=ExpressionWrapper(F('wh_lb_job_no_id__lb_validity_date'),
                                             output_field=fields.DateTimeField()),
        departure_time=ExpressionWrapper(F('wh_dispatch_id__dispatch_depature_date'),
                                         output_field=fields.DateTimeField()),
    ).order_by('-arrival_date').values_list(
        'wh_job_no', 'wh_qr_rand_num', 'wh_customer_name__cu_name',
        Func('arrival_date', Value('YYYY-MM-DD HH24:MI:SS'), function='to_char', output_field=CharField()),
        Func('unloading_start_time', Value('YYYY-MM-DD HH24:MI:SS'), function='to_char', output_field=CharField()),
        Func('unloading_end_time', Value('YYYY-MM-DD HH24:MI:SS'), function='to_char', output_field=CharField()),
        'wh_gate_injob_no_id__gatein_transporter',
        'wh_gate_injob_no_id__gatein_truck_number',
        'wh_consigner', 'wh_consignee', 'wh_lb_job_no_id__lb_packing_list__ge_gstexcepmtion',
        'wh_gate_injob_no_id__gatein_hawb', 'wh_gate_injob_no_id__gatein_destination',
        'wh_gate_injob_no_id__gatein_invoice', 'wh_po_num', 'wh_total_qty',
        'wh_gross_weight', 'wh_invoice_weight_unit', 'wh_uom__uom_name', 'wh_goods_length',
        'wh_goods_width', 'wh_goods_height', 'wh_goods_pieces',
        'wh_goods_package_type__package_type', 'wh_chargeable_weight', 'wh_cbm', 'wh_invoice_value',
        'wh_lb_job_no_id__lb_stock_invoice_currency__currency_type', 'wh_invoice_amount_inr',
        'wh_lb_job_no_id__lb_eway_bill',
        Func('eway_bill_validity', Value('YYYY-MM-DD HH24:MI:SS'), function='to_char', output_field=CharField()),
        'wh_fumigation_process__ge_gstexcepmtion', 'wh_check_in_out__check_in_out_name', 'wh_branch__loc_name',
        'wh_unit__unit_name',
        'wh_bay__bay_bayname', 'wh_storage_time', 'wh_dispatch_id__dispatch_truck_number',
        'wh_dispatch_id__dispatch_truck_type__vt_vehicletype',
        Func('departure_time', Value('YYYY-MM-DD HH24:MI:SS'), function='to_char', output_field=CharField()),
        'wh_dispatch_id__dispatch_sticker_pasted_bvm__lp_name', 'wh_dispatch_id__dispatch_mawb',
        'wh_dispatch_id__dispatch_num'
    )

    # Create an Excel workbook and sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Stock Report"

    # Write the header row with styling
    headers = [
        'Job Number', 'Stock Number', 'Customer', 'Date Of Arrival',
        'Unloading Start Time', 'Unloading End Time', 'Transporter',
        'Truck Number', 'Consigner', 'Consignee', 'Docs Received', 'HAWB',
        'Destination', 'Invoice Number', 'Case Number', 'Invoice Qty',
        'Invoice Weight (kg)', 'Checkin Weight (kg)', 'UOM', 'Length',
        'Width', 'Height', 'Dims Qty', 'Package Type', 'Volume Weight',
        'CBM', 'Invoice Value', 'Invoice Currency', 'Invoice (INR)',
        'E-Way Bill#', 'E-Way Bill Validity', 'Fumigation Status',
        'Check In-Out?', 'Branch', 'Unit', 'Bay', 'Storage Days',
        'Truck_Number(Out)', 'Truck_Type(Out)', 'Truck_Depature_Time(Out)',
        'Labels_Pasted_By', 'MAWB', 'Dispatch_Number'
    ]
    for col_num, header in enumerate(headers, 1):
        cell = sheet.cell(row=1, column=col_num, value=header)
        cell.font = Font(name='Bookman Old Style', size=10, bold=True, color="000000")
        cell.fill = PatternFill(start_color="FFCC00", end_color="FFCC00", fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Write data rows and style them
    for row_num, row_data in enumerate(data, 2):
        for col_num, value in enumerate(row_data, 1):
            cell = sheet.cell(row=row_num, column=col_num, value=value)
            cell.font = Font(name='Bookman Old Style', size=9)

    # Apply borders to all cells
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    for row in sheet.iter_rows(min_row=1, max_row=sheet.max_row, min_col=1, max_col=len(headers)):
        for cell in row:
            cell.border = thin_border

    # Set all column widths to 25
    for col in sheet.columns:
        col_letter = col[0].column_letter  # Get the column letter (e.g., A, B, C)
        sheet.column_dimensions[col_letter].width = 25

    # Create the HTTP response with the Excel file
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="Stock_Report.xlsx"'
    workbook.save(response)
    return response

@login_required(login_url='login_page')
def goods_in_out_reports_list(request):
    first_name = request.session.get('first_name')

    # Grouping by branch, unit, and date for check-in
    in_statistics = Warehouse_goods_info.objects.filter(wh_check_in_out=1).values(
        'wh_branch__loc_name',
        'wh_unit__unit_name',
        'wh_gate_injob_no_id__gatein_created_at__date'  # Truncate to date for date-wise grouping
    ).annotate(
        total_invoices=Count('wh_goods_invoice', distinct=True),
        total_trucks=Count('wh_gate_injob_no_id__gatein_pre_id', distinct=True),
        total_weights=(Sum('wh_goods_weight')/1000)
    )

    # Grouping by branch, unit, and date for check-out
    out_statistics = Warehouse_goods_info.objects.filter(wh_check_in_out=2).values(
        'wh_branch__loc_name',
        'wh_unit__unit_name',
        'wh_dispatch_id__dispatch_depature_date__date',  # Truncate to date for date-wise grouping
    ).annotate(
        total_invoices=Count('wh_goods_invoice', distinct=True),
        total_trucks=Count('wh_dispatch_num', distinct=True),
        total_weights=(Sum('wh_goods_weight') / 1000)
    )

    context = {
        'first_name': first_name,
        'in_statistics': in_statistics.order_by('wh_gate_injob_no_id__gatein_created_at__date', 'id'),
        'out_statistics': out_statistics.order_by('wh_dispatch_id__dispatch_depature_date__date', 'id'),
    }
    return render(request, "asset_mgt_app/goods_in_out_reports_list.html", context)
