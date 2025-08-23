from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.paginator import Paginator
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from .send_department_email import send_department_email
from ..forms import DsrForm
from ..models import CustomerInfo,Warehouse_goods_info
from django.shortcuts import redirect
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
def dsr_send_email_view(request,pre_gatein_id=None,customer_name=None,subject=None):
    print('Entering dsr_send_email_view')
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
        ws.title = "DSR Report"

        # Write the headers
        headers = [
            'Job Number', 'Stock Number', 'Customer', 'Date Of Arrival', 'Unloading Start Time',
            'Unloading End Time', 'Transporter', 'Truck Number', 'Consignor', 'Consignee',
            'Docs Received', 'HAWB', 'Destination', 'Invoice Number', 'Case Number',
            'Invoice Qty', 'Invoice Weight (kg)', 'Checkin Weight (kg)', 'UOM', 'Length',
            'Width', 'Height', 'Dims Qty', 'Package Type', 'Volume Weight', 'CBM',
            'Invoice Value', 'Invoice Currency', 'Invoice (INR)', 'E-Way Bill#', 'E-Way Bill Validity',
            'Fumigation Status', 'Check In-Out?', 'Branch', 'Unit', 'Bay', 'Storage Days','Damage?','Type of Damage','GRN Number'
        ]
        ws.append(headers)

        # Fetch the IDs from Gatein_info
        gate_in_ids = Gatein_info.objects.filter(gatein_pre_id=pre_gatein_id).values_list('id', flat=True)

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
            stock_values = stock_values.filter(wh_check_in_out="1").order_by(
                '-wh_gate_injob_no_id__gatein_arrival_date'
            )

            # Step 2: In the loop, replace the date with timezone-free date objects
            for stock_value in stock_values:
                date_of_arrival = stock_value.wh_gate_injob_no_id.gatein_arrival_date
                if date_of_arrival:
                    date_of_arrival = date_of_arrival.replace(tzinfo=None)  # Keep both date and time
                has_damage = "Yes" if stock_value.wh_Dam_rep_job_num_id else "No"
                damage_type = str(getattr(getattr(stock_value.wh_Dam_rep_job_num_id, 'dam_damage_type', ''), 'damage_name', '') or '')

                row = [
                    stock_value.wh_job_no,  # Index 0
                    stock_value.wh_qr_rand_num,  # Index 1
                    str(stock_value.wh_customer_name),  # Index 2
                    date_of_arrival if date_of_arrival else '',  # Index 3: Only Date, no time
                    stock_value.wh_lb_job_no_id.lb_stock_unloading_start_time.replace(tzinfo=None)
                    if stock_value.wh_lb_job_no_id and stock_value.wh_lb_job_no_id.lb_stock_unloading_start_time else '',

                    stock_value.wh_lb_job_no_id.lb_stock_unloading_end_time.replace(tzinfo=None)
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

                    "Stock on Hand" if str(stock_value.wh_check_in_out) == "Checked-In" else "Checked-In",  # Index 32
                    str(stock_value.wh_branch),  # Index 33
                    str(stock_value.wh_unit),  # Index 34
                    str(stock_value.wh_bay),  # Index 35
                    stock_value.wh_storage_time,# Index 36
                    has_damage,# Index 37
                    damage_type,
                    # getattr(stock_value.wh_damages, 'damage_name', ''), # Index 38
                    getattr(stock_value.wh_Dam_rep_job_num_id, 'dam_GRN_num', ''),
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

        red_font = Font(color="FF0000")
        for row_index, row in enumerate(sheet.iter_rows(min_row=2), start=2):
            damage_cell = row[len(headers) - 3]  # Last column index
            if damage_cell.value == "Yes":
                for cell in row:
                    cell.font = red_font

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
            subject = f"{customer_name}_DSR Report"
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
