from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.utils import timezone
from xhtml2pdf import pisa
import datetime

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


@login_required(login_url='login_page')
def pk_invoice_list(request):
    """List all PMS invoices."""
    invoice_list = PkInvoice.objects.select_related(
        'inv_customer_name', 'inv_customer_po', 'inv_assessment_num'
    ).all()
    return render(request, 'asset_mgt_app/pk_invoice_list.html', {
        'invoice_list': invoice_list,
        'first_name': request.session.get('first_name'),
    })


@login_required(login_url='login_page')
def pk_invoice_add(request, invoice_id=0):
    """
    Create or Edit a PMS Invoice.
    GET ?job_no=XXX — auto-fills from costing summary + PO dimensions.
    POST — saves PkInvoice header + PkInvoiceItem rows.
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

        return render(request, 'asset_mgt_app/pk_invoice_add.html', {
            'invoice': invoice,
            'items': items,
            'first_name': first_name,
            'assessment_id': assessment_id,
            'tracker_flags': get_tracker_flags(assessment_id),
            'current_step': 'invoice',
        })

    # ── CREATE MODE ──────────────────────────────────────────────────────────
    customer_id = request.GET.get('customer_id', '')
    customers = CustomerInfo.objects.all().order_by('cu_name')

    po_items = []
    customer_name = ''
    po_num = 'Multiple'
    po_date = ''
    gst_rate = 18.0
    base_amount = 0.0

    if customer_id:
        cust = CustomerInfo.objects.filter(id=customer_id).first()
        if cust:
            customer_name = str(cust.cu_name)
            # Find all uninvoiced PO dimensions for this customer's POs
            invoiced_pod_ids = PkInvoiceItem.objects.values_list('inv_pod_dimension_id', flat=True)
            po_items = POdimension.objects.filter(
                pod_po_num__po_customer_name_id=customer_id
            ).exclude(
                id__in=invoiced_pod_ids
            ).select_related('pod_type_of_req', 'pod_uom', 'pod_po_num')
            
            # Use the GST rate of the first PO as a default (user can override)
            first_po = po_items.first()
            if first_po and first_po.pod_po_num and first_po.pod_po_num.po_tax:
                gst_rate = first_po.pod_po_num.po_tax

    if request.method == 'POST':
        _save_invoice(request)
        return redirect('pk_invoice_list')

    # Auto-generate invoice number preview
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
        'po_items': po_items,
        'customer_name': customer_name,
        'po_num': po_num,
        'po_date': po_date,
        'gst_rate': gst_rate,
        'base_amount': round(base_amount, 2),
        'next_inv_no': next_inv_no,
        'today': datetime.date.today().strftime('%Y-%m-%d'),
    })


def _save_invoice(request, invoice=None):
    """
    Internal helper — saves PkInvoice + PkInvoiceItem from POST data.
    If `invoice` is provided, it's an update; otherwise it creates new.
    """
    data = request.POST

    # Header fields
    inv_number = data.get('inv_number', '').strip()
    job_no = data.get('inv_job_no', '').strip()
    inv_date_str = data.get('inv_date', '')
    inv_date = datetime.date.fromisoformat(inv_date_str) if inv_date_str else datetime.date.today()
    gst_rate = float(data.get('inv_gst_rate', 18))
    base_amount = float(data.get('inv_base_amount', 0))
    remarks = data.get('inv_remarks', '')
    payment_status = data.get('inv_payment_status', 'Pending')

    # GST split: IGST or CGST+SGST (use_igst = 1 means inter-state)
    use_igst = data.get('use_igst', '0') == '1'
    gst_total = round(base_amount * gst_rate / 100, 2)
    if use_igst:
        igst = gst_total
        cgst = sgst = 0.0
    else:
        igst = 0.0
        cgst = sgst = round(gst_total / 2, 2)

    total_amount = round(base_amount + gst_total, 2)

    # FK lookups
    assessment_num_id = data.get('inv_assessment_num_id') or None
    customer_po_id = data.get('inv_customer_po_id') or None
    customer_name_id = data.get('inv_customer_name_id') or None

    if invoice is None:
        invoice = PkInvoice(inv_created_by=request.user)

    invoice.inv_number = inv_number
    invoice.inv_job_no = job_no
    invoice.inv_date = inv_date
    invoice.inv_gst_rate = gst_rate
    invoice.inv_base_amount = base_amount
    invoice.inv_cgst_amount = cgst
    invoice.inv_sgst_amount = sgst
    invoice.inv_igst_amount = igst
    invoice.inv_total_amount = total_amount
    invoice.inv_remarks = remarks
    invoice.inv_payment_status = payment_status

    if assessment_num_id:
        invoice.inv_assessment_num_id = assessment_num_id
    if customer_po_id:
        invoice.inv_customer_po_id = customer_po_id
    if customer_name_id:
        invoice.inv_customer_name_id = customer_name_id

    invoice.save()

    # Save line items
    PkInvoiceItem.objects.filter(inv_master=invoice).delete()

    # Each item row is submitted as: item_pod_id_X, item_qty_X, item_unit_value_X
    import re
    for key in data.keys():
        m = re.match(r'^item_pod_id_(\d+)$', key)
        if m:
            idx = m.group(1)
            pod_id = data.get(f'item_pod_id_{idx}', '')
            qty = int(data.get(f'item_qty_{idx}', 0) or 0)
            unit_value = float(data.get(f'item_unit_value_{idx}', 0) or 0)
            item_number = data.get(f'item_number_{idx}', '')
            description = data.get(f'item_description_{idx}', '')
            length = float(data.get(f'item_length_{idx}', 0) or 0)
            width = float(data.get(f'item_width_{idx}', 0) or 0)
            height = float(data.get(f'item_height_{idx}', 0) or 0)
            uom = data.get(f'item_uom_{idx}', '')

            pod_obj = None
            if pod_id:
                try:
                    pod_obj = POdimension.objects.get(pk=int(pod_id))
                except POdimension.DoesNotExist:
                    pass

            PkInvoiceItem.objects.create(
                inv_master=invoice,
                inv_pod_dimension=pod_obj,
                inv_item_number=item_number,
                inv_description=description,
                inv_length=length,
                inv_width=width,
                inv_height=height,
                inv_uom=uom,
                inv_qty=qty,
                inv_unit_value=unit_value,
                inv_total_value=round(qty * unit_value, 2),
            )

    return invoice


@login_required(login_url='login_page')
def pk_invoice_pdf(request, invoice_id):
    """Render GST Tax Invoice as PDF."""
    invoice = get_object_or_404(PkInvoice, pk=invoice_id)
    items = PkInvoiceItem.objects.filter(inv_master=invoice)

    # Amount in words helper
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
    """
    AJAX endpoint — returns POdimension items for a given job_no.
    Used by the invoice add form to dynamically load line items.
    """
    job_no = request.GET.get('job_no', '').strip()
    if not job_no:
        return JsonResponse({'items': [], 'customer': '', 'po_num': '', 'gst_rate': 18})

    costing = PkcostingsummaryInfo.objects.filter(cs_job_no=job_no).first()
    if not costing:
        return JsonResponse({'items': [], 'customer': '', 'po_num': '', 'gst_rate': 18})

    assess_ids = PkcostingInfo.objects.filter(
        ct_job_no=job_no
    ).values_list('ct_assessment_num', flat=True).distinct()

    po_dims = POdimension.objects.filter(
        pod_assess_num__in=assess_ids,
        pod_po_num=costing.cs_customer_po
    ).select_related('pod_type_of_req', 'pod_uom')

    items_data = []
    for pod in po_dims:
        items_data.append({
            'pod_id': pod.id,
            'item_number': pod.pod_item or '',
            'description': str(pod.pod_type_of_req) if pod.pod_type_of_req else '',
            'length': pod.pod_length or 0,
            'width': pod.pod_width or 0,
            'height': pod.pod_height or 0,
            'uom': str(pod.pod_uom) if pod.pod_uom else 'mm',
            'qty': pod.pod_quantity or 0,
            'unit_value': pod.pod_value or 0,
            'total_value': round((pod.pod_value or 0) * (pod.pod_quantity or 0), 2),
        })

    gst_rate = costing.cs_customer_po.po_tax if (costing.cs_customer_po and costing.cs_customer_po.po_tax) else 18.0

    return JsonResponse({
        'items': items_data,
        'customer': str(costing.cs_customer_name) if costing.cs_customer_name else '',
        'customer_id': costing.cs_customer_name_id or '',
        'po_num': str(costing.cs_customer_po) if costing.cs_customer_po else '',
        'po_id': costing.cs_customer_po_id or '',
        'assessment_id': costing.cs_assessment_num_id or '',
        'gst_rate': gst_rate,
    })
