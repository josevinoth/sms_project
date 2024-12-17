from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from .send_department_email import send_department_email
from ..forms import DsrForm
from ..models import CustomerInfo,Warehouse_goods_info
from django.shortcuts import redirect
from ..forms import dsr_EmailForm
import openpyxl
from io import BytesIO

from ..sub_models.gatein_mod import Gatein_info


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
@login_required(login_url='login_page')
def dsr_send_email_view(request,pre_gatein_id=None,customer_name=None):
    print('Entering dsr_send_email_view')
    if request.method == 'POST':
        recipient = request.POST.get('recipient')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        customer_name = request.POST.get('ds_customer')
        recipient_list = [email.strip() for email in recipient.split(',')]

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "DSR Report"

        # Write the headers
        headers = [
            'Job Number', 'Stock Number', 'Customer', 'Date Of Arrival', 'Unloading Start Time',
            'Unloading End Time', 'Transporter', 'Truck Number', 'Consigner', 'Consignee',
            'Docs Received', 'HAWB', 'Destination', 'Invoice Number', 'Case Number',
            'Invoice Qty', 'Invoice Weight (kg)', 'Checkin Weight (kg)', 'UOM', 'Length',
            'Width', 'Height', 'Dims Qty', 'Package Type', 'Volume Weight', 'CBM',
            'Invoice Value', 'Invoice Currency', 'Invoice (INR)', 'E-Way Bill#', 'E-Way Bill Validity',
            'Fumigation Status', 'Check In-Out?', 'Branch', 'Unit', 'Bay', 'Storage Days'
        ]
        ws.append(headers)

        # Fetch the IDs from Gatein_info
        gate_in_ids = Gatein_info.objects.filter(gatein_pre_id=pre_gatein_id).values_list('id', flat=True)

        # Initialize query to none
        stock_values = Warehouse_goods_info.objects.none()

        # Build query conditions dynamically
        if customer_name and gate_in_ids.exists():
            stock_values = Warehouse_goods_info.objects.filter(
                wh_customer_name=customer_name,
                wh_gate_injob_no_id__in=list(gate_in_ids)
            )
        elif customer_name:
            stock_values = Warehouse_goods_info.objects.filter(
                wh_customer_name=customer_name
            )
        elif gate_in_ids.exists():
            stock_values = Warehouse_goods_info.objects.filter(
                wh_gate_injob_no_id__in=list(gate_in_ids)
            )
        # Write data rows
            for stock_value in stock_values:
                row = [
                    stock_value.wh_job_no,  # Index 0
                    stock_value.wh_qr_rand_num,  # Index 1
                    str(stock_value.wh_customer_name),  # Index 2
                    stock_value.wh_gate_injob_no_id.gatein_arrival_date.strftime('%d-%m-%Y')
                    if stock_value.wh_gate_injob_no_id and stock_value.wh_gate_injob_no_id.gatein_arrival_date else '',
                    # Index 3
                    stock_value.wh_lb_job_no_id.lb_stock_unloading_start_time.strftime('%d-%m-%Y')
                    if stock_value.wh_lb_job_no_id and stock_value.wh_lb_job_no_id.lb_stock_unloading_start_time else '',
                    # Index 4
                    stock_value.wh_lb_job_no_id.lb_stock_unloading_end_time.strftime('%d-%m-%Y')
                    if stock_value.wh_lb_job_no_id and stock_value.wh_lb_job_no_id.lb_stock_unloading_end_time else '',
                    # Index 5
                    stock_value.wh_gate_injob_no_id.gatein_transporter
                    if stock_value.wh_gate_injob_no_id else '',  # Index 6
                    stock_value.wh_gate_injob_no_id.gatein_truck_number
                    if stock_value.wh_gate_injob_no_id else '',  # Index 7
                    stock_value.wh_consigner,  # Index 8
                    stock_value.wh_consignee,  # Index 9
                    str(stock_value.wh_lb_job_no_id.lb_packing_list)
                    if stock_value.wh_lb_job_no_id and stock_value.wh_lb_job_no_id.lb_packing_list else '',
                    # Index 10
                    stock_value.wh_gate_injob_no_id.gatein_hawb
                    if stock_value.wh_gate_injob_no_id else '',  # Index 11
                    stock_value.wh_gate_injob_no_id.gatein_destination
                    if stock_value.wh_gate_injob_no_id else '',  # Index 12
                    stock_value.wh_gate_injob_no_id.gatein_invoice
                    if stock_value.wh_gate_injob_no_id else '',  # Index 13
                    stock_value.wh_po_num,  # Index 14
                    stock_value.wh_total_qty,  # Index 15
                    stock_value.wh_gross_weight,  # Index 16
                    stock_value.wh_invoice_weight_unit,  # Index 17
                    str(stock_value.wh_uom),  # Index 18
                    stock_value.wh_goods_length,  # Index 19
                    stock_value.wh_goods_width,  # Index 20
                    stock_value.wh_goods_height,  # Index 21
                    stock_value.wh_goods_pieces,  # Index 22
                    str(stock_value.wh_goods_package_type),  # Index 23
                    stock_value.wh_chargeable_weight,  # Index 24
                    stock_value.wh_cbm,  # Index 25
                    stock_value.wh_invoice_value,  # Index 26
                    str(stock_value.wh_lb_job_no_id.lb_stock_invoice_currency)
                    if stock_value.wh_lb_job_no_id and stock_value.wh_lb_job_no_id.lb_stock_invoice_currency else '',
                    # Index 27
                    stock_value.wh_invoice_amount_inr,  # Index 28
                    stock_value.wh_lb_job_no_id.lb_eway_bill
                    if stock_value.wh_lb_job_no_id else '',  # Index 29
                    stock_value.wh_lb_job_no_id.lb_validity_date.strftime('%Y-%m-%d')
                    if stock_value.wh_lb_job_no_id and stock_value.wh_lb_job_no_id.lb_validity_date else '',
                    # Index 30
                    str(stock_value.wh_fumigation_process)
                    if stock_value.wh_fumigation_process else '',  # Index 31
                    str(stock_value.wh_check_in_out),  # Index 32
                    str(stock_value.wh_branch),  # Index 33
                    str(stock_value.wh_unit),  # Index 34
                    str(stock_value.wh_bay),  # Index 35
                    stock_value.wh_storage_time,  # Index 36
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
            bottom=Side(style='thin')
        )
        customer_name =CustomerInfo.objects.get(id=customer_name).cu_name
        file_name = str(customer_name)+'_DSR_report.xlsx'  # Set your desired file name
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
        send_department_email('warehouse', subject, message, recipient_list,attachment,attachment_type,file_name)

        # Redirect back to the previous page
        return redirect(request.META['HTTP_REFERER'])
    else:
        messages.error(request, 'Invalid input in the email form.')
    return redirect(request.META['HTTP_REFERER'])
    # return render(request, "asset_mgt_app/dsr_send_email.html", context)
