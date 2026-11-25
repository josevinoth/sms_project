from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.utils import timezone
from django.db.models import Max
from xhtml2pdf import pisa
import datetime
import json
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from ..models import (
    PkcostingsummaryInfo, PkcostingInfo, PkneedassessmentInfo,
    PkpurchaseorderInfo, CustomerInfo, POdimension
)
from ..sub_models.pk_invoice_mod import PkInvoice, PkInvoiceItem
from .general_utils import (
    get_financial_year, generate_next_number,
    get_branch_code, get_session_branch_id
)
from .pk_needassessment_view import get_tracker_flags

GST_STATE_MAP = {
    '01': 'Jammu & Kashmir', '02': 'Himachal Pradesh', '03': 'Punjab', '04': 'Chandigarh',
    '05': 'Uttarakhand', '06': 'Haryana', '07': 'Delhi', '08': 'Rajasthan',
    '09': 'Uttar Pradesh', '10': 'Bihar', '11': 'Sikkim', '12': 'Arunachal Pradesh',
    '13': 'Nagaland', '14': 'Manipur', '15': 'Mizoram', '16': 'Tripura',
    '17': 'Meghalaya', '18': 'Assam', '19': 'West Bengal', '20': 'Jharkhand',
    '21': 'Odisha', '22': 'Chhattisgarh', '23': 'Madhya Pradesh', '24': 'Gujarat',
    '26': 'Dadra & Nagar Haveli', '27': 'Maharashtra', '29': 'Karnataka',
    '30': 'Goa', '31': 'Lakshadweep', '32': 'Kerala', '33': 'Tamil Nadu',
    '34': 'Puducherry', '35': 'Andaman & Nicobar Islands', '36': 'Telangana', '37': 'Andhra Pradesh',
    '38': 'Ladakh', '97': 'Other Territory'
}

def get_state_from_gstin_or_addr(gstin, address=''):
    if gstin and len(gstin) >= 2 and gstin[:2].isdigit():
        code = gstin[:2]
        if code in GST_STATE_MAP:
            return GST_STATE_MAP[code]
    if address:
        for name in GST_STATE_MAP.values():
            if name.lower() in address.lower():
                return name
    return 'Tamil Nadu'


@login_required(login_url='login_page')
def pk_invoice_list(request):
    """List all PMS invoices."""
    invoice_list = PkInvoice.objects.select_related(
        'inv_customer_name', 'inv_customer_po', 'inv_assessment_num'
    ).prefetch_related('items').all()
    return render(request, 'asset_mgt_app/pk_invoice_list.html', {
        'invoice_list': invoice_list,
        'first_name': request.session.get('first_name'),
    })


@login_required(login_url='login_page')
def pk_invoice_get_customer_jobs(request):
    """
    AJAX endpoint — returns customer details and all uninvoiced Jobs (PkcostingsummaryInfo).
    Supports multi-job selection for a single customer.
    """
    customer_id = request.GET.get('customer_id') or request.POST.get('customer_id')
    invoice_id = request.GET.get('invoice_id') or request.POST.get('invoice_id')
    if not customer_id:
        return JsonResponse({'success': False, 'message': 'Missing customer_id', 'jobs': []})

    cust = CustomerInfo.objects.filter(id=customer_id).first()
    if not cust:
        return JsonResponse({'success': False, 'message': 'Customer not found', 'jobs': []})

    gstin = cust.cu_gst or ''
    pincode = cust.cu_pincode or ''
    state = get_state_from_gstin_or_addr(gstin, cust.cu_address or '')
    default_gst_rate = float(cust.cu_gstpercentage or 18.0)

    # Invoiced job numbers (excluding the current invoice being edited)
    invoiced_jobs_qs = PkInvoiceItem.objects.all()
    if invoice_id:
        invoiced_jobs_qs = invoiced_jobs_qs.exclude(inv_master_id=invoice_id)
    invoiced_job_nos = set(invoiced_jobs_qs.values_list('inv_job_no', flat=True))

    # Fetch jobs belonging to this customer
    jobs_qs = PkcostingsummaryInfo.objects.filter(
        cs_customer_name_id=customer_id
    ).select_related('cs_customer_po', 'cs_assessment_num').order_by('-id')

    # If no jobs found directly, also check PO customer name
    if not jobs_qs.exists():
        jobs_qs = PkcostingsummaryInfo.objects.filter(
            cs_customer_po__po_customer_name_id=customer_id
        ).select_related('cs_customer_po', 'cs_assessment_num').order_by('-id')

    jobs_data = []
    for cs in jobs_qs:
        j_no = cs.cs_job_no or f"JOB-{cs.id}"
        # Determine if already invoiced
        is_invoiced = j_no in invoiced_job_nos

        # Get unique boxes/items in this job
        costings = PkcostingInfo.objects.filter(ct_job_no=cs.cs_job_no)
        pod_ids = list(set(costings.values_list('ct_po_dimension_id', flat=True)))
        
        items_desc_list = []
        total_job_val = 0.0
        primary_pod_id = None
        box_qty = 1
        unit_rate = 0.0

        for pid in pod_ids:
            if not pid:
                continue
            pod = POdimension.objects.filter(id=pid).first()
            if not pod:
                continue
            primary_pod_id = pod.id
            item_job_qty = costings.filter(ct_po_dimension=pod).aggregate(m=Max('ct_na_quantity'))['m'] or 1.0
            box_qty = int(item_job_qty)
            u_rate = float(pod.pod_cost_unit or 0.0)
            if u_rate <= 0 and pod.pod_quantity and pod.pod_value:
                u_rate = round(float(pod.pod_value) / float(pod.pod_quantity), 2)
            unit_rate = u_rate
            line_val = round(item_job_qty * u_rate, 2)
            total_job_val += line_val
            items_desc_list.append(f"{pod.pod_item} ({pod.pod_length}×{pod.pod_width}×{pod.pod_height}) — Qty: {int(item_job_qty)}")

        if not items_desc_list:
            items_desc_list = [f"Packaging Job {j_no}"]

        jobs_data.append({
            'job_id': cs.id,
            'job_no': j_no,
            'is_invoiced': is_invoiced,
            'job_date': cs.cs_created_at.strftime('%Y-%m-%d') if cs.cs_created_at else '',
            'po_num': str(cs.cs_customer_po.po_num if cs.cs_customer_po else ''),
            'po_id': cs.cs_customer_po_id or '',
            'assessment_num': str(cs.cs_assessment_num or ''),
            'assessment_id': cs.cs_assessment_num_id or '',
            'description': '; '.join(items_desc_list),
            'qty': box_qty,
            'unit_rate': unit_rate,
            'base_value': total_job_val if total_job_val > 0 else float(cs.cs_totalbox_cost or 0.0),
            'pod_id': primary_pod_id or ''
        })

    return JsonResponse({
        'success': True,
        'customer_name': cust.cu_name,
        'customer_fullname': cust.cu_nameshort or cust.cu_name,
        'gstin': gstin,
        'state': state,
        'pincode': pincode,
        'default_gst_rate': default_gst_rate,
        'jobs': jobs_data
    })


@login_required(login_url='login_page')
def pk_invoice_add(request, invoice_id=0):
    """
    Create or Edit a PMS Invoice with Multi-Job selection.
    """
    first_name = request.session.get('first_name')
    assessment_id = request.session.get('na_assessment_id')

    # ── EDIT MODE ───────────────────────────────────────────────────────────
    if invoice_id:
        invoice = get_object_or_404(PkInvoice, pk=invoice_id)
        items = PkInvoiceItem.objects.filter(inv_master=invoice)
        assessment_id = invoice.inv_assessment_num_id or assessment_id

        if request.method == 'POST':
            _save_invoice(request, invoice=invoice)
            return redirect('pk_invoice_list')

        customers = CustomerInfo.objects.all().order_by('cu_name')
        return render(request, 'asset_mgt_app/pk_invoice_add.html', {
            'invoice': invoice,
            'items': items,
            'first_name': first_name,
            'assessment_id': assessment_id,
            'tracker_flags': get_tracker_flags(assessment_id),
            'current_step': 'invoice',
            'customers': customers,
            'customer_id': invoice.inv_customer_name_id,
            'customer_name': invoice.inv_customer_name.cu_name if invoice.inv_customer_name else '',
            'next_inv_no': invoice.inv_number,
            'today': datetime.date.today().strftime('%Y-%m-%d'),
        })

    # ── CREATE MODE ──────────────────────────────────────────────────────────
    if request.method == 'POST':
        inv = _save_invoice(request)
        return redirect('pk_invoice_list')

    customers = CustomerInfo.objects.all().order_by('cu_name')
    customer_id = request.GET.get('customer_id', '')

    branch_id = get_session_branch_id(request)
    branch_code = get_branch_code(branch_id)
    fy = get_financial_year()
    inv_prefix = f"INV-{branch_code}-{fy}-"
    next_inv_no = generate_next_number(PkInvoice, 'inv_number', inv_prefix, 4)

    return render(request, 'asset_mgt_app/pk_invoice_add.html', {
        'first_name': first_name,
        'assessment_id': assessment_id,
        'tracker_flags': get_tracker_flags(assessment_id),
        'current_step': 'invoice',
        'customers': customers,
        'customer_id': customer_id,
        'next_inv_no': next_inv_no,
        'today': datetime.date.today().strftime('%Y-%m-%d'),
    })


def _save_invoice(request, invoice=None):
    """
    Internal helper — saves PkInvoice + PkInvoiceItem records from POST data.
    Supports multi-job selection and PMS Tally revenue/tax breakdown.
    """
    data = request.POST

    inv_number = data.get('inv_number', '').strip()
    inv_date_str = data.get('inv_date', '')
    inv_date = datetime.date.fromisoformat(inv_date_str) if inv_date_str else datetime.date.today()
    customer_name_id = data.get('inv_customer_name_id') or None
    gst_rate = float(data.get('inv_gst_rate', 18) or 18)
    remarks = data.get('inv_remarks', '')
    payment_status = data.get('inv_payment_status', 'Pending')

    customer_state = data.get('inv_customer_state', '').strip()
    customer_pincode = data.get('inv_customer_pincode', '').strip()
    customer_gstin = data.get('inv_customer_gstin', '').strip()

    if invoice is None:
        invoice = PkInvoice(inv_created_by=request.user)

    invoice.inv_number = inv_number
    invoice.inv_date = inv_date
    invoice.inv_customer_name_id = customer_name_id
    invoice.inv_customer_state = customer_state
    invoice.inv_customer_pincode = customer_pincode
    invoice.inv_customer_gstin = customer_gstin
    invoice.inv_gst_rate = gst_rate
    invoice.inv_remarks = remarks
    invoice.inv_payment_status = payment_status
    invoice.save()

    # Clear existing items if updating
    invoice.items.all().delete()

    # Collect multi-job lines
    # Inputs sent as: job_checked_X, job_no_X, job_id_X, job_desc_X, job_cat_X, job_tax_type_X, job_base_X, etc.
    total_base = 0.0
    total_cgst = 0.0
    total_sgst = 0.0
    total_igst = 0.0
    selected_job_numbers = []

    # State check: Tamil Nadu is branch home state (33)
    is_interstate = (customer_state and customer_state.lower() != 'tamil nadu')

    import re
    row_indices = set()
    for key in data.keys():
        m = re.match(r'^(?:job_checked_|job_no_|item_pod_id_)(\d+)$', key)
        if m:
            row_indices.add(m.group(1))

    for idx in sorted(list(row_indices), key=lambda x: int(x)):
        # If checkbox present, ensure it's checked
        if f'job_checked_{idx}' in data and data.get(f'job_checked_{idx}') not in ['1', 'on', 'true']:
            continue
        if f'item_checked_{idx}' in data and data.get(f'item_checked_{idx}') not in ['1', 'on', 'true']:
            continue

        job_no = data.get(f'job_no_{idx}', '').strip()
        job_id = data.get(f'job_id_{idx}', '')
        pod_id = data.get(f'item_pod_id_{idx}', '')
        item_number = data.get(f'item_number_{idx}', '') or job_no or f"Line-{idx}"
        description = data.get(f'job_desc_{idx}', '') or data.get(f'item_description_{idx}', '')
        qty = int(data.get(f'job_qty_{idx}', 0) or data.get(f'item_qty_{idx}', 0) or 1)
        base_val = float(data.get(f'job_base_{idx}', 0) or data.get(f'item_total_{idx}', 0) or 0)
        u_val = float(data.get(f'job_rate_{idx}', 0) or data.get(f'item_unit_value_{idx}', 0) or (base_val / qty if qty else 0))
        
        category = data.get(f'job_cat_{idx}', 'Packing Charges')
        tax_type = data.get(f'job_tax_type_{idx}', '18%')
        job_date_str = data.get(f'job_date_{idx}', '')
        job_date = datetime.date.fromisoformat(job_date_str) if job_date_str else inv_date

        if job_no and job_no not in selected_job_numbers:
            selected_job_numbers.append(job_no)

        # Detailed charge breakdowns (if entered, else default to base_val in category)
        handling = float(data.get(f'charge_handling_{idx}', 0) or 0)
        loading = float(data.get(f'charge_loading_{idx}', 0) or 0)
        unloading = float(data.get(f'charge_unloading_{idx}', 0) or 0)
        scrap_wood = float(data.get(f'charge_scrap_wood_{idx}', 0) or 0)
        repacking = float(data.get(f'charge_repacking_{idx}', 0) or 0)
        supply_mat = float(data.get(f'charge_supply_mat_{idx}', 0) or 0)

        # Main packing charges bucket
        sum_breakdowns = handling + loading + unloading + scrap_wood + repacking + supply_mat
        packing_charges = max(0.0, base_val - sum_breakdowns) if sum_breakdowns > 0 else base_val

        # Specific Tally charge buckets according to tax type and interstate
        p_5 = 0.0
        p_igst = 0.0
        p_service = 0.0
        p_service_igst = 0.0
        p_service_sez = 0.0
        p_sez = 0.0
        rep_igst = 0.0
        sup_igst = 0.0

        if tax_type == 'SEZ':
            if 'service' in category.lower():
                p_service_sez = packing_charges
            else:
                p_sez = packing_charges
        elif is_interstate or 'igst' in tax_type.lower():
            if 'service' in category.lower():
                p_service_igst = packing_charges
            elif 'supply' in category.lower():
                sup_igst = packing_charges
            else:
                p_igst = packing_charges
            if repacking:
                rep_igst = repacking
                repacking = 0.0
            if supply_mat:
                sup_igst += supply_mat
                supply_mat = 0.0
        elif tax_type == 'GST-5%':
            p_5 = packing_charges
        else:
            if 'service' in category.lower():
                p_service = packing_charges
            elif 'supply' in category.lower():
                supply_mat += packing_charges
            else:
                p_service = packing_charges

        # Tax calculation
        cgst_9 = sgst_9 = cgst_6 = sgst_6 = cgst_2_5 = sgst_2_5 = igst_val = 0.0
        if tax_type not in ['LUT', 'Nil tax', 'SEZ']:
            rate = 5.0 if tax_type == 'GST-5%' else (float(tax_type.replace('%', '').replace('IGST', '').strip()) if any(k in tax_type for k in ['18', '12', '5']) else gst_rate)
            tax_amount = round(base_val * (rate / 100.0), 2)
            if is_interstate or 'igst' in tax_type.lower():
                igst_val = tax_amount
            else:
                half = round(tax_amount / 2.0, 2)
                if rate == 18.0:
                    cgst_9 = sgst_9 = half
                elif rate == 12.0:
                    cgst_6 = sgst_6 = half
                elif rate == 5.0:
                    cgst_2_5 = sgst_2_5 = half
                else:
                    cgst_9 = sgst_9 = half

        line_total = round(base_val + cgst_9 + sgst_9 + cgst_6 + sgst_6 + cgst_2_5 + sgst_2_5 + igst_val, 2)

        total_base += base_val
        total_cgst += (cgst_9 + cgst_6 + cgst_2_5)
        total_sgst += (sgst_9 + sgst_6 + sgst_2_5)
        total_igst += igst_val

        pod_obj = POdimension.objects.filter(pk=int(pod_id)).first() if pod_id and str(pod_id).isdigit() else None
        cs_obj = PkcostingsummaryInfo.objects.filter(pk=int(job_id)).first() if job_id and str(job_id).isdigit() else None

        PkInvoiceItem.objects.create(
            inv_master=invoice,
            inv_costing_summary=cs_obj,
            inv_job_no=job_no,
            inv_job_date=job_date,
            inv_primary_cost_category=category,
            inv_tax_type=tax_type,
            inv_pod_dimension=pod_obj,
            inv_item_number=item_number,
            inv_description=description,
            inv_qty=qty,
            inv_unit_value=u_val,
            inv_total_value=base_val,
            inv_handling_charges=handling,
            inv_loading_charges=loading,
            inv_unloading_charges=unloading,
            inv_packing_charges_5=p_5,
            inv_packing_charges_igst=p_igst,
            inv_packing_charges_service=p_service,
            inv_packing_charges_service_igst=p_service_igst,
            inv_packing_charges_service_sez=p_service_sez,
            inv_packing_charges_sez=p_sez,
            inv_repacking_charges=repacking,
            inv_repacking_charges_igst=rep_igst,
            inv_scrap_wood=scrap_wood,
            inv_supply_packing_materials=supply_mat,
            inv_supply_packing_materials_igst=sup_igst,
            inv_cgst_9=cgst_9,
            inv_sgst_9=sgst_9,
            inv_cgst_6=cgst_6,
            inv_sgst_6=sgst_6,
            inv_cgst_2_5=cgst_2_5,
            inv_sgst_2_5=sgst_2_5,
            inv_igst=igst_val,
            inv_line_total=line_total,
        )

    invoice.inv_job_no = ', '.join(selected_job_numbers)
    invoice.inv_base_amount = round(total_base, 2)
    invoice.inv_cgst_amount = round(total_cgst, 2)
    invoice.inv_sgst_amount = round(total_sgst, 2)
    invoice.inv_igst_amount = round(total_igst, 2)
    invoice.inv_total_amount = round(total_base + total_cgst + total_sgst + total_igst, 2)
    invoice.save()

    return invoice


@login_required(login_url='login_page')
def pk_invoice_tally_excel(request, invoice_id):
    """
    Exports a PMS Invoice to the exact BMS_Tally Excel format matching the user's template.
    Includes all headers, yellow GSTIN highlight, charge ledgers (Cols R to AE) and tax breakdown (Cols AF to AL).
    """
    invoice = get_object_or_404(PkInvoice, pk=invoice_id)
    items = invoice.items.all().select_related('inv_costing_summary')

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"

    yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
    header_font = Font(name="Calibri", size=9, bold=True)
    regular_font = Font(name="Calibri", size=9)
    bold_font = Font(name="Calibri", size=9, bold=True)
    
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )

    headers_37 = {
        'B': 'PMS',
        'C': 'Invoice',
        'D': 'DATE',
        'E': 'VOUCHER NO.',
        'F': 'GSTIN',
        'G': 'SUNDRY DEBTORS',
        'H': 'STATE',
        'I': 'PINCODE',
        'J': 'PRIMARY COST CATEGORY',
        'K': 'JOB NO.',
        'L': 'CUSTOMER',
        'M': 'DATE',
        'N': 'Description',
        'R': 'Handling Charges',
        'S': 'Loading Charges',
        'T': 'Packing Charges - 5%',
        'U': 'Packing Charges - IGST',
        'V': 'Packing Charges - Service',
        'W': 'Packing Charges - Service - IGST',
        'X': 'Packing Charges - Service - SEZ',
        'Y': 'Packing Charges - SEZ',
        'Z': 'Repacking Charges',
        'AA': 'Repacking Charges - IGST',
        'AB': 'Scrap Wood',
        'AC': 'Supply of Packing Materials',
        'AD': 'Supply of Packing Materials - IGST',
        'AE': 'Unloading Charges',
        'AF': 'CGST Output @ 9%',
        'AG': 'SGST Output @ 9%',
        'AH': 'CGST Output @ 6%',
        'AI': 'SGST Output @ 6%',
        'AJ': 'CGST Output @ 2.5%',
        'AK': 'SGST Output @ 2.5%',
        'AL': 'IGST',
        'AM': 'TOTAL',
    }

    # Write Row 37 headers
    for col_letter, title in headers_37.items():
        cell = ws[f"{col_letter}37"]
        cell.value = title
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
        if col_letter == 'F':
            cell.fill = yellow_fill

    # Row 38 Sub-row
    ws["B38"] = 12
    ws["B38"].alignment = Alignment(horizontal="center", vertical="center")
    ws["B38"].font = header_font
    ws["B38"].border = thin_border

    # Row 39 descriptive labels
    sub_labels = {
        'D': 'Invoice Date',
        'E': 'Invoice Number',
        'F': 'GST No',
        'G': 'Customer fullname',
        'L': 'Customer short name',
    }
    for col_letter, lbl in sub_labels.items():
        cell = ws[f"{col_letter}38"]
        cell.value = lbl
        cell.font = Font(name="Calibri", size=8, italic=True, color="555555")
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    cust = invoice.inv_customer_name
    cust_full = cust.cu_nameshort or cust.cu_name if cust else ''
    cust_short = cust.cu_name if cust else ''
    gstin = invoice.inv_customer_gstin or (cust.cu_gst if cust else '')
    state = invoice.inv_customer_state or get_state_from_gstin_or_addr(gstin, cust.cu_address if cust else '')
    pincode = invoice.inv_customer_pincode or (cust.cu_pincode if cust else '')

    row_idx = 39
    for item in items:
        ws[f"B{row_idx}"] = "PMS"
        ws[f"C{row_idx}"] = "Invoice"
        ws[f"D{row_idx}"] = invoice.inv_date.strftime('%d-%m-%Y') if invoice.inv_date else ''
        ws[f"E{row_idx}"] = invoice.inv_number
        ws[f"F{row_idx}"] = gstin
        ws[f"G{row_idx}"] = cust_full
        ws[f"H{row_idx}"] = state
        ws[f"I{row_idx}"] = pincode
        ws[f"J{row_idx}"] = item.inv_primary_cost_category
        ws[f"K{row_idx}"] = item.inv_job_no or ''
        ws[f"L{row_idx}"] = cust_short
        ws[f"M{row_idx}"] = item.inv_job_date.strftime('%d-%m-%Y') if item.inv_job_date else (invoice.inv_date.strftime('%d-%m-%Y') if invoice.inv_date else '')
        ws[f"N{row_idx}"] = item.inv_description or ''

        # Numeric charges
        ws[f"R{row_idx}"] = item.inv_handling_charges or ""
        ws[f"S{row_idx}"] = item.inv_loading_charges or ""
        ws[f"T{row_idx}"] = item.inv_packing_charges_5 or ""
        ws[f"U{row_idx}"] = item.inv_packing_charges_igst or ""
        ws[f"V{row_idx}"] = item.inv_packing_charges_service or ""
        ws[f"W{row_idx}"] = item.inv_packing_charges_service_igst or ""
        ws[f"X{row_idx}"] = item.inv_packing_charges_service_sez or ""
        ws[f"Y{row_idx}"] = item.inv_packing_charges_sez or ""
        ws[f"Z{row_idx}"] = item.inv_repacking_charges or ""
        ws[f"AA{row_idx}"] = item.inv_repacking_charges_igst or ""
        ws[f"AB{row_idx}"] = item.inv_scrap_wood or ""
        ws[f"AC{row_idx}"] = item.inv_supply_packing_materials or ""
        ws[f"AD{row_idx}"] = item.inv_supply_packing_materials_igst or ""
        ws[f"AE{row_idx}"] = item.inv_unloading_charges or ""

        # Taxes
        ws[f"AF{row_idx}"] = item.inv_cgst_9 or ""
        ws[f"AG{row_idx}"] = item.inv_sgst_9 or ""
        ws[f"AH{row_idx}"] = item.inv_cgst_6 or ""
        ws[f"AI{row_idx}"] = item.inv_sgst_6 or ""
        ws[f"AJ{row_idx}"] = item.inv_cgst_2_5 or ""
        ws[f"AK{row_idx}"] = item.inv_sgst_2_5 or ""
        ws[f"AL{row_idx}"] = item.inv_igst or ""
        ws[f"AM{row_idx}"] = item.inv_line_total or item.inv_total_value

        # Styling
        for col_letter in headers_37.keys():
            c = ws[f"{col_letter}{row_idx}"]
            c.font = regular_font
            c.border = thin_border
            if col_letter in ['R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM']:
                c.alignment = Alignment(horizontal="right")
                if c.value != "":
                    c.number_format = '#,##0.00'
            else:
                c.alignment = Alignment(horizontal="left")

        row_idx += 1

    # Adjust column widths
    col_widths = {
        'B': 8, 'C': 10, 'D': 12, 'E': 20, 'F': 18, 'G': 32, 'H': 16, 'I': 10,
        'J': 24, 'K': 20, 'L': 18, 'M': 12, 'N': 35, 'R': 15, 'S': 15, 'T': 18,
        'U': 18, 'V': 20, 'W': 24, 'X': 22, 'Y': 18, 'Z': 16, 'AA': 20, 'AB': 12,
        'AC': 24, 'AD': 28, 'AE': 16, 'AF': 15, 'AG': 15, 'AH': 15, 'AI': 15,
        'AJ': 15, 'AK': 15, 'AL': 15, 'AM': 18
    }
    for col, width in col_widths.items():
        ws.column_dimensions[col].width = width

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    safe_inv = invoice.inv_number.replace('/', '_').replace('\\', '_')
    response['Content-Disposition'] = f'attachment; filename="BMS_Tally_{safe_inv}.xlsx"'
    wb.save(response)
    return response


@login_required(login_url='login_page')
def pk_invoice_pdf(request, invoice_id):
    """Render GST Tax Invoice as PDF."""
    invoice = get_object_or_404(PkInvoice, pk=invoice_id)
    items = PkInvoiceItem.objects.filter(inv_master=invoice)

    def amount_in_words(amount):
        try:
            from num2words import num2words
            rupees = int(amount)
            paise = round((amount - rupees) * 100)
            text = num2words(rupees, lang='en_IN').title() + ' Rupees'
            if paise:
                text += ' And ' + num2words(paise, lang='en_IN').title() + ' Paise'
            return text + ' Only'
        except Exception:
            return f'₹ {amount:,.2f}'

    context = {
        'invoice': invoice,
        'items': items,
        'amount_in_words': amount_in_words(invoice.inv_total_amount),
    }

    template_path = 'asset_mgt_app/pk_invoice_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Invoice_{invoice.inv_number}.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation error: <pre>' + html + '</pre>')
    return response


@login_required(login_url='login_page')
def pk_invoice_get_po_items(request):
    """Legacy support endpoint."""
    return pk_invoice_get_customer_jobs(request)
