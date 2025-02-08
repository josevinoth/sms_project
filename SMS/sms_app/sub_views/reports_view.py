import csv
from itertools import chain
from io import BytesIO
from django.http import StreamingHttpResponse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db.models import Q, ExpressionWrapper, fields, F, DurationField
from django.db.models.functions import Cast, Extract
from django.shortcuts import render
from django.template.loader import get_template
from django.http import HttpResponse
from django.utils import timezone
from django.utils.timezone import make_naive
from xhtml2pdf import pisa
from ..models import CustomerInfo,ExpenseInfo,Gatein_info,LocationmasterInfo,Loadingbay_Info,DamagereportInfo,Warehouse_goods_info,ExpenseExtinfo
from datetime import date,timedelta
import datetime
from django.db.models import Count, Sum
import openpyxl
from openpyxl.styles import Font, Border, Side, PatternFill, Alignment
from .send_department_email import send_department_email
from django.shortcuts import redirect
from django.contrib import messages
from ..forms import DsrForm


from itertools import zip_longest


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
    form = DsrForm(request.POST or None)
    customer_name = request.POST.get('ds_customer', '').strip()

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
    if customer_name:
        goods_list = goods_list.filter(wh_customer_name=customer_name)
        print(f"Filtering by customer name: {customer_name}")
    page_number = request.GET.get('page')
    paginator = Paginator(goods_list, 50)
    page_obj = paginator.get_page(page_number)


    current_date = datetime.date.today()

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
                'form': form,
                'customer_name': customer_name,
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
    warehouse_data = Warehouse_goods_info.objects.exclude(wh_voucher_num__isnull=True)
    expense_data = ExpenseExtinfo.objects.all()

    branch_unit_results = {}

    for warehouse in warehouse_data:
        branch_unit_key = (warehouse.wh_branch, warehouse.wh_unit)
        revenue = float(warehouse.wh_total_invoice_cost or 0)
        total_expense = 0.0
        for expense in expense_data:
            if expense.exp_ext_branch == warehouse.wh_branch and expense.exp_ext_unit == warehouse.wh_unit:
                total_expense += float(expense.exp_ext_amount or 0)
        if branch_unit_key not in branch_unit_results:
            branch_unit_results[branch_unit_key] = {'revenue': 0.0, 'expense': 0.0}
        branch_unit_results[branch_unit_key]['revenue'] += revenue
        branch_unit_results[branch_unit_key]['expense'] += total_expense

    result_list = []
    for (branch, unit), totals in branch_unit_results.items():
        revenue = totals['revenue']
        expense = totals['expense']
        profit_loss = revenue - expense
        profit_loss_percentage = (profit_loss / expense) * 100 if expense > 0 else 0.0

        result_list.append({
            'branch': branch,
            'unit': unit,
            'date': warehouse.wh_checkin_time,
            'revenue': round(revenue, 2),
            'expense': round(expense, 2),
            'profit_loss': round(profit_loss, 2),
            'profit_loss_percentage': round(profit_loss_percentage, 2),
        })

    context = {
        'result_list': result_list,
        'first_name': first_name,
    }

    return render(request, "asset_mgt_app/profit_loss_report.html", context)


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

    # Query data
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
        'arrival_date', 'unloading_start_time', 'unloading_end_time',
        'wh_gate_injob_no_id__gatein_transporter',
        'wh_gate_injob_no_id__gatein_truck_number',
        'wh_consigner', 'wh_consignee', 'wh_lb_job_no_id__lb_packing_list__ge_gstexcepmtion',
        'wh_gate_injob_no_id__gatein_hawb', 'wh_gate_injob_no_id__gatein_destination',
        'wh_gate_injob_no_id__gatein_invoice', 'wh_po_num', 'wh_total_qty',
        'wh_gross_weight', 'wh_invoice_weight_unit', 'wh_uom__uom_name', 'wh_goods_length',
        'wh_goods_width', 'wh_goods_height', 'wh_goods_pieces',
        'wh_goods_package_type__package_type', 'wh_chargeable_weight', 'wh_cbm', 'wh_invoice_value',
        'wh_lb_job_no_id__lb_stock_invoice_currency__currency_type', 'wh_invoice_amount_inr',
        'wh_lb_job_no_id__lb_eway_bill', 'eway_bill_validity',
        'wh_fumigation_process__ge_gstexcepmtion', 'wh_check_in_out__check_in_out_name', 'wh_branch__loc_name',
        'wh_unit__unit_name',
        'wh_bay__bay_bayname', 'wh_storage_time', 'wh_dispatch_id__dispatch_truck_number',
        'wh_dispatch_id__dispatch_truck_type__vt_vehicletype','departure_time',
        'wh_dispatch_id__dispatch_sticker_pasted_bvm__lp_name', 'wh_dispatch_id__dispatch_mawb',
        'wh_dispatch_id__dispatch_num',
    )

    # Header row
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

    def generate_streamed_excel():
        # Create an in-memory buffer
        output = BytesIO()
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Stock Report"

        # Write headers
        for col_num, header in enumerate(headers, 1):
            cell = sheet.cell(row=1, column=col_num, value=header)
            cell.font = Font(name='Bookman Old Style', size=10, bold=True, color="000000")
            cell.fill = PatternFill(start_color="FFCC00", end_color="FFCC00", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Write data rows
        for row_num, row_data in enumerate(data, 2):
            for col_num, value in enumerate(row_data, 1):
                # Convert timezone-aware datetime to naive
                if isinstance(value, (datetime.date, datetime.datetime)) and hasattr(value,'tzinfo') and value.tzinfo is not None:
                    value = make_naive(value)  # Convert to naive datetime in the local timezone
                cell = sheet.cell(row=row_num, column=col_num, value=value)
                cell.font = Font(name='Bookman Old Style', size=9, bold=False, color="000000")

        # Get the last row and column with data
        max_row = sheet.max_row
        max_col = sheet.max_column

        # Define a thin border
        thin_border = Border(left=Side(style='thin'),
                             right=Side(style='thin'),
                             top=Side(style='thin'),
                             bottom=Side(style='thin'))

        # Apply the border to all cells from A1 to the bottom-right cell
        for row in sheet.iter_rows(min_row=1, max_row=max_row, min_col=1, max_col=max_col):
            for cell in row:
                cell.border = thin_border

        # Set all column widths to 25
        for col in sheet.columns:
            col_letter = col[0].column_letter  # Get the column letter (e.g., A, B, C)
            sheet.column_dimensions[col_letter].width = 25

        # Save workbook to buffer
        workbook.save(output)
        output.seek(0)  # Reset buffer pointer
        yield output.read()  # Yield content of buffer
        output.close()

    # Return streaming response
    response = StreamingHttpResponse(
        generate_streamed_excel(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    # Get the current time in UTC and then convert to IST (UTC + 5:30)
    ist_time = timezone.now() + timedelta(hours=5, minutes=30)

    # Format the time with an underscore between the date and time
    filename = f'Stock_Report_{ist_time.strftime("%Y%m%d_%H%M")}.xlsx'

    # Set the Content-Disposition header with the formatted filename
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
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

@login_required(login_url='login_page')
def stock_value_send_email_view(request,pre_gatein_id=None,customer_name=None,subject=None):
    print('Entering stcokvalue_send_email_view')
    if request.method == 'POST':
        recipient = request.POST.get('recipient')
        # subject = request.POST.get('subject')
        message = request.POST.get('message')
        customer_name_1=customer_name
        print(customer_name_1)
        if customer_name_1==None:
            customer_name = request.POST.get('ds_customer')
        else:
            customer_name=customer_name
        recipient_list = [email.strip() for email in recipient.split(',')]

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Stock Value Report"

        # Write the headers
        headers = [
            'Job Number', 'Stock Number', 'Customer', 'Date Of Arrival', 'Unloading Start Time',
            'Unloading End Time', 'Transporter', 'Truck Number', 'Consigner', 'Consignee',
            'Docs Received', 'HAWB', 'Destination', 'Invoice Number', 'Case Number',
            'Invoice Qty', 'Invoice Weight (kg)', 'Checkin Weight (kg)', 'UOM', 'Length',
            'Width', 'Height', 'Dims Qty', 'Package Type', 'Volume Weight', 'CBM',
            'Invoice Value', 'Invoice Currency', 'Invoice (INR)', 'E-Way Bill#', 'E-Way Bill Validity',
            'Fumigation Status', 'Check In-Out?', 'Branch', 'Unit', 'Bay', 'Storage Days',
            'Truck_Number(Out)','Truck_Type(Out)','Truck_Depature_Time(Out)','Labels_Pasted_By',
            'MAWB','Dispatch_Number','Dispatch quantity','Stock On Hand'
        ]
        ws.append(headers)

        # Fetch the IDs from Gatein_info
        gate_in_ids = Gatein_info.objects.filter(gatein_pre_id=pre_gatein_id).values_list('id', flat=True)

        three_months_ago = timezone.now() - timedelta(days=90)

        # Initialize query to none
        stock_values = None

        # Build query conditions dynamically
        if customer_name and gate_in_ids.exists():
            print ("Inside first loop")
            stock_values = Warehouse_goods_info.objects.filter(
                wh_customer_name=customer_name,
                wh_gate_injob_no_id__in=list(gate_in_ids)
            )
        elif customer_name:
            print ("Inside second loop")
            stock_values = Warehouse_goods_info.objects.filter(
                wh_customer_name=customer_name
            )
        elif gate_in_ids.exists():
            print ("Inside third loop")
            stock_values = Warehouse_goods_info.objects.filter(
                wh_gate_injob_no_id__in=list(gate_in_ids)
            )
        # Add a comment or log to explain cases where it isn't used
        if stock_values is None:
            print("No stock values found for the given conditions.")
        else:
            # Step 1: Filter stock_values and ensure the date fields are timezone-free
            stock_values = stock_values.filter(
                Q(wh_check_in_out=1) |
                Q(wh_check_in_out=2, wh_checkout_time__isnull=False, wh_checkout_time__gte=three_months_ago)

            ).order_by('-wh_gate_injob_no_id__gatein_arrival_date')

            # Step 2: In the loop, replace the date with timezone-free date objects
            for stock_value in stock_values:
                date_of_arrival = stock_value.wh_gate_injob_no_id.gatein_arrival_date
                if date_of_arrival:
                    date_of_arrival = date_of_arrival.replace(tzinfo=None).date()  # Convert to date object

                checkin_weight = stock_value.wh_gross_weight if stock_value.wh_gross_weight else 0
                dispatch_qty = stock_value.wh_dispatch_id.dispatch_total_goods if stock_value.wh_dispatch_id and stock_value.wh_dispatch_id.dispatch_total_goods else 0

                stock_on_hand = checkin_weight - dispatch_qty  # Subtract dispatch quantity
                row = [
                    stock_value.wh_job_no,  # Index 0
                    stock_value.wh_qr_rand_num,  # Index 1
                    str(stock_value.wh_customer_name),  # Index 2
                    date_of_arrival if date_of_arrival else '',  # Index 3: Only Date, no time
                    stock_value.wh_lb_job_no_id.lb_stock_unloading_start_time.replace(tzinfo=None).date()
                    if stock_value.wh_lb_job_no_id and stock_value.wh_lb_job_no_id.lb_stock_unloading_start_time else '',
                    stock_value.wh_lb_job_no_id.lb_stock_unloading_end_time.replace(tzinfo=None).date()
                    if stock_value.wh_lb_job_no_id and stock_value.wh_lb_job_no_id.lb_stock_unloading_end_time else '',
                    # Index 6: gatein_transporter
                    getattr(stock_value.wh_gate_injob_no_id, 'gatein_transporter', ''),

                    # Index 7: gatein_truck_number
                    getattr(stock_value.wh_gate_injob_no_id, 'gatein_truck_number', ''),

                    stock_value.wh_consigner,  # Index 8
                    stock_value.wh_consignee,  # Index 9

                    # Index 10: lb_packing_list
                    str(getattr(stock_value.wh_lb_job_no_id, 'lb_packing_list', '')),

                    # Index 11-13: gatein_hawb, gatein_destination, gatein_invoice
                    getattr(stock_value.wh_gate_injob_no_id, 'gatein_hawb', ''),
                    getattr(stock_value.wh_gate_injob_no_id, 'gatein_destination', ''),
                    getattr(stock_value.wh_gate_injob_no_id, 'gatein_invoice', ''),

                    stock_value.wh_po_num,  # Index 14
                    stock_value.wh_total_qty,  # Index 15
                    stock_value.wh_gross_weight,  # Index 16
                    stock_value.wh_invoice_weight_unit,  # Index 17

                    # Index 18: wh_uom
                    str(stock_value.wh_uom),

                    stock_value.wh_goods_length,  # Index 19
                    stock_value.wh_goods_width,  # Index 20
                    stock_value.wh_goods_height,  # Index 21
                    stock_value.wh_goods_pieces,  # Index 22

                    # Index 23: wh_goods_package_type
                    str(stock_value.wh_goods_package_type),

                    stock_value.wh_chargeable_weight,  # Index 24
                    stock_value.wh_cbm,  # Index 25
                    stock_value.wh_invoice_value,  # Index 26

                    # Index 27: lb_stock_invoice_currency
                    str(getattr(stock_value.wh_lb_job_no_id, 'lb_stock_invoice_currency', '')),

                    stock_value.wh_invoice_amount_inr,  # Index 28

                    # Index 29: lb_eway_bill
                    getattr(stock_value.wh_lb_job_no_id, 'lb_eway_bill', ''),

                    # Index 30: lb_validity_date (remove tzinfo)
                    getattr(stock_value.wh_lb_job_no_id, 'lb_validity_date', None).replace(tzinfo=None)
                    if getattr(stock_value.wh_lb_job_no_id, 'lb_validity_date', None) else None,

                    # Index 31: wh_fumigation_process
                    str(stock_value.wh_fumigation_process or ''),

                    "Stock on Hand" if str(stock_value.wh_check_in_out) == "Checked-In" else "Checked-In", # Index # Index 32
                    str(stock_value.wh_branch),  # Index 33
                    str(stock_value.wh_unit),  # Index 34
                    str(stock_value.wh_bay),  # Index 35
                    stock_value.wh_storage_time,# Index 36
                    getattr(stock_value.wh_dispatch_id, 'dispatch_truck_number', ''),# Index 37
                    getattr(stock_value.wh_dispatch_id, 'dispatch_truck_type', ''),# Index 38
                    getattr(stock_value.wh_dispatch_id, 'dispatch_depature_date', ''),# Index 39
                    getattr(stock_value.wh_dispatch_id, 'dispatch_sticker_pasted_bvm', ''),# Index 40
                    getattr(stock_value.wh_dispatch_id, 'dispatch_mawb', ''),# Index 41
                    getattr(stock_value.wh_dispatch_id, 'dispatch_num', ''),# Index 42
                    getattr(stock_value.wh_dispatch_id, 'dispatch_total_goods', ''),# Index 43
                    stock_on_hand,# Index 44
                ]

                # # Debugging the row values
                # for idx, value in enumerate(row):
                #     print(f"Index {idx}: Value={value}, Type={type(value)}")

                ws.append(row)  # Append the row to the worksheet


        sheet = wb.active

        # Format the first row (Header)
        header_font = Font(name="Arial",bold=True,size=11)  # Make the header row bold
        cell_font = Font(name="Arial",bold=False,size=10)  # settings fro cells
        yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")  # Yellow fill
        border_style = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin'),
        )
        customer_name = CustomerInfo.objects.filter(cu_name=customer_name).first()

        file_name = str(customer_name)+'_Stock Value_report.xlsx'  # Set your desired file name
        # Apply formatting to the first row
        for cell in sheet[1]:
            cell.font = header_font
            cell.fill = yellow_fill
            cell.border = border_style
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Apply borders to the rest of the cells in the sheet, skipping the first row
        for row_index, row in enumerate(sheet.iter_rows(), start=1):
            if row_index == 1:
                continue  # Skip the first row
            for cell in row:
                if cell.value:  # Skip empty cells
                    cell.border = border_style
                    cell.font = cell_font

        # Set column width for all columns
        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter  # Get the column name (e.g., 'A')
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            sheet.column_dimensions[column].width =adjusted_width  # Set column width to 20
            # Save the workbook to a BytesIO object
            excel_file = BytesIO()
            wb.save(excel_file)
        excel_file.seek(0)
        attachment = excel_file
        attachment_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        if subject==None:
            subject = f"{customer_name}Stock Value Report"
        else:
            subject = subject
        pre_gatein_id = request.session.get('ses_pre_gatein_id')
        send_department_email('warehouse', subject, message, recipient_list,attachment,attachment_type,file_name)
        # Redirect back to the previous page
        messages.success(request, f"E-mail sent successfully")
        return redirect(request.META['HTTP_REFERER'])
    else:
        messages.error(request, 'Invalid input in the email form.')
    return redirect(request.META['HTTP_REFERER'])
    # return render(request, "asset_mgt_app/dsr_send_email.html", context)
