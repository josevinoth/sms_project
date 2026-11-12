import base64
import io
import os
import re
import zipfile

# Allow synchronous Django ORM operations when Playwright's sync API starts an event loop
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import pypdf
from PIL import Image

def number_to_words(n):
    if n == 0 or n is None:
        return 'Zero'
    ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
            'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
    tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']

    def _convert(num):
        if num < 20:
            return ones[num]
        elif num < 100:
            return tens[num // 10] + ('' if num % 10 == 0 else ' ' + ones[num % 10])
        elif num < 1000:
            return ones[num // 100] + ' Hundred' + ('' if num % 100 == 0 else ' ' + _convert(num % 100))
        elif num < 100000:
            return _convert(num // 1000) + ' Thousand' + ('' if num % 1000 == 0 else ' ' + _convert(num % 1000))
        elif num < 10000000:
            return _convert(num // 100000) + ' Lakh' + ('' if num % 100000 == 0 else ' ' + _convert(num % 100000))
        else:
            return _convert(num // 10000000) + ' Crore' + ('' if num % 10000000 == 0 else ' ' + _convert(num % 10000000))

    try:
        n_int = int(n)
        return _convert(n_int) + ' Only'
    except Exception:
        return ''


def get_logo_base64():
    """Retrieve base64 encoded company logo for embedding into PDFs."""
    for logo_name in ['logo4.0.png', 'Company_Logo.png', 'logo1.png']:
        logo_path = os.path.join(settings.MEDIA_ROOT, logo_name)
        if os.path.isfile(logo_path):
            try:
                with open(logo_path, 'rb') as f:
                    return base64.b64encode(f.read()).decode('utf-8')
            except Exception:
                pass
    return ''


def sanitize_filename(name):
    """Sanitize directory or file names for zip archiving (cross-platform safe)."""
    if not name:
        return 'unnamed'
    # Replace slashes, colons, and illegal characters with underscores or hyphens
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', str(name).strip())
    # Collapse multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized).strip(' ._')
    return sanitized or 'unnamed'


def get_petty_cash_voucher_context(obj, pc_type='TMS'):
    """Extract context dictionary for voucher PDF rendering."""
    pc_type = pc_type.upper()
    prefix = pc_type.lower()  # 'tms' -> 'tpc', 'wms' -> 'wpc', 'pms' -> 'ppc'
    if prefix == 'tms':
        field_pfx = 'tpc'
    elif prefix == 'wms':
        field_pfx = 'wpc'
    else:
        field_pfx = 'ppc'

    voucher_no = getattr(obj, f'{field_pfx}_number', '') or f"{pc_type}-{obj.id}"
    
    if pc_type == 'TMS':
        voucher_date = obj.tpc_transaction_date
        trip_date = obj.tpc_trip_date
        amount = obj.tpc_amount or 0.0
        company_name = "BVM TRANS SOLUTIONS PRIVATE LIMITED"
        business_obj = obj.tpc_business
        branch_obj = obj.tpc_branch
        expense_type = obj.tpc_expense_type.tms_exp_type_name if obj.tpc_expense_type else ""
        job_no = obj.tpc_job_no or ""
        unit = obj.tpc_unit or ""
        customer = obj.tpc_customer.cu_name if obj.tpc_customer else ""
        
        # Payment to
        if obj.tpc_to_manual:
            payment_to = obj.tpc_to_manual
        elif obj.tpc_driver_name:
            payment_to = obj.tpc_driver_name.dm_name
        elif obj.tpc_driver_name_manual:
            payment_to = obj.tpc_driver_name_manual
        elif obj.tpc_to:
            payment_to = obj.tpc_to.first_name or obj.tpc_to.username
        else:
            payment_to = ""

        vehicle_no = obj.tpc_vehicle_number.vm_registrationnumber if obj.tpc_vehicle_number else (obj.tpc_vehicle_number_manual or "")
        driver_name = obj.tpc_driver_name.dm_name if obj.tpc_driver_name else (obj.tpc_driver_name_manual or "")

        from_location = ""
        to_location = ""
        if job_no:
            try:
                from ..models import TripdetailInfo
                from django.db.models import Q
                trip = TripdetailInfo.objects.filter(
                    Q(tr_consignmentnumber__co_consignmentnumber=job_no) | Q(tr_tripnumber=job_no)
                ).first()
                if trip:
                    from_location = trip.tr_departedlocation.place_name if trip.tr_departedlocation else ""
                    to_location = trip.tr_reportedlocation.place_name if trip.tr_reportedlocation else ""
            except Exception:
                pass

        remarks = obj.tpc_remarks or ""
        receiver_signature = obj.tpc_receiver_signature or ""
        created_by = obj.tpc_created_by.first_name if obj.tpc_created_by and obj.tpc_created_by.first_name else (obj.tpc_created_by.username if obj.tpc_created_by else "-")
        is_checked = obj.tpc_is_checked
        checked_by = obj.tpc_checked_by.first_name if obj.tpc_checked_by and obj.tpc_checked_by.first_name else (obj.tpc_checked_by.username if obj.tpc_checked_by else "")
        is_verified = obj.tpc_is_verified
        verified_by = obj.tpc_verified_by.first_name if obj.tpc_verified_by and obj.tpc_verified_by.first_name else (obj.tpc_verified_by.username if obj.tpc_verified_by else "")
        is_approved = obj.tpc_is_approved
        approved_by = obj.tpc_approved_by.first_name if obj.tpc_approved_by and obj.tpc_approved_by.first_name else (obj.tpc_approved_by.username if obj.tpc_approved_by else "")
        bill_no = ""
        bill_amount = 0.0
        gst_percentage = 0.0
        gst_amount = 0.0
        total_amount = amount

    elif pc_type == 'WMS':
        voucher_date = obj.wpc_date
        trip_date = obj.wpc_transaction_date
        amount = obj.wpc_total_amount or 0.0
        company_name = "BVM STORAGE SOLUTIONS PRIVATE LIMITED"
        business_obj = obj.wpc_business
        branch_obj = obj.wpc_branch
        expense_type = obj.wpc_expense_type.wms_exp_type_name if obj.wpc_expense_type else ""
        job_no = obj.wpc_job_no or ""
        unit = obj.wpc_unit or ""
        customer = obj.wpc_customer.cu_name if obj.wpc_customer else ""
        
        if obj.wpc_to:
            payment_to = obj.wpc_to.first_name or obj.wpc_to.username
        elif obj.wpc_to_manual:
            payment_to = obj.wpc_to_manual
        else:
            payment_to = ""

        vehicle_no = ""
        driver_name = ""
        from_location = ""
        to_location = ""

        bill_no = obj.wpc_bill_no or ""
        bill_amount = obj.wpc_bill_amount or 0.0
        gst_percentage = obj.wpc_gst_percentage or 0.0
        gst_amount = obj.wpc_gst_amount or 0.0
        total_amount = obj.wpc_total_amount or 0.0

        remarks = obj.wpc_remarks or ""
        receiver_signature = obj.wpc_receiver_signature or ""
        created_by = obj.wpc_created_by.first_name if obj.wpc_created_by and obj.wpc_created_by.first_name else (obj.wpc_created_by.username if obj.wpc_created_by else "-")
        is_checked = obj.wpc_is_checked
        checked_by = obj.wpc_checked_by.first_name if obj.wpc_checked_by and obj.wpc_checked_by.first_name else (obj.wpc_checked_by.username if obj.wpc_checked_by else "")
        is_verified = obj.wpc_is_verified
        verified_by = obj.wpc_verified_by.first_name if obj.wpc_verified_by and obj.wpc_verified_by.first_name else (obj.wpc_verified_by.username if obj.wpc_verified_by else "")
        is_approved = obj.wpc_is_approved
        approved_by = obj.wpc_approved_by.first_name if obj.wpc_approved_by and obj.wpc_approved_by.first_name else (obj.wpc_approved_by.username if obj.wpc_approved_by else "")

    else:  # PMS
        voucher_date = obj.ppc_date
        trip_date = obj.ppc_transaction_date
        amount = obj.ppc_total_amount or obj.ppc_amount or 0.0
        company_name = "BVM PACK SOLUTIONS PRIVATE LIMITED"
        business_obj = obj.ppc_business
        branch_obj = obj.ppc_branch
        expense_type = obj.ppc_expense_type.pms_exp_type_name if obj.ppc_expense_type else ""
        job_no = obj.ppc_job_no or ""
        unit = obj.ppc_unit or ""
        customer = obj.ppc_customer.cu_name if obj.ppc_customer else ""

        if obj.ppc_to:
            payment_to = obj.ppc_to.first_name or obj.ppc_to.username
        elif obj.ppc_to_manual:
            payment_to = obj.ppc_to_manual
        else:
            payment_to = ""

        vehicle_no = obj.ppc_vehicle_number.pc_vehicle_no if obj.ppc_vehicle_number else ""
        driver_name = ""
        from_location = ""
        to_location = ""

        bill_no = obj.ppc_bill_no or ""
        bill_amount = obj.ppc_bill_amount or 0.0
        gst_percentage = obj.ppc_gst_percentage or 0.0
        gst_amount = obj.ppc_gst_amount or 0.0
        total_amount = obj.ppc_total_amount or 0.0

        remarks = obj.ppc_remarks or ""
        receiver_signature = obj.ppc_receiver_signature or ""
        created_by = obj.ppc_created_by.first_name if obj.ppc_created_by and obj.ppc_created_by.first_name else (obj.ppc_created_by.username if obj.ppc_created_by else "-")
        is_checked = obj.ppc_is_checked
        checked_by = obj.ppc_checked_by.first_name if obj.ppc_checked_by and obj.ppc_checked_by.first_name else (obj.ppc_checked_by.username if obj.ppc_checked_by else "")
        is_verified = obj.ppc_is_verified
        verified_by = obj.ppc_verified_by.first_name if obj.ppc_verified_by and obj.ppc_verified_by.first_name else (obj.ppc_verified_by.username if obj.ppc_verified_by else "")
        is_approved = obj.ppc_is_approved
        approved_by = obj.ppc_approved_by.first_name if obj.ppc_approved_by and obj.ppc_approved_by.first_name else (obj.ppc_approved_by.username if obj.ppc_approved_by else "")

    # Clean remarks
    clean_remarks = remarks
    if 'Auto-generated' in clean_remarks:
        clean_remarks = re.sub(r'\s*\[?Auto-generated.*', '', clean_remarks).strip()

    # Address
    branch_name = (branch_obj.loc_name if branch_obj else "")
    if 'BLR' in branch_name.upper() or 'BLR' in voucher_no.upper() or 'B_' in voucher_no:
        company_address = "No. 42/9 &amp; 42/10, Ground Floor, New Airport Road, Adjacent to ITC Factory,<br>Meenakunte Village, Jala Hobli, Bangalore – 562 157"
    else:
        company_address = "No. 70, Adam Nagar Road, Nagalkeni, Chrompet, Chennai - 600 044."

    return {
        'pc_type': pc_type,
        'voucher_no': voucher_no,
        'voucher_date': voucher_date,
        'trip_date': trip_date,
        'amount': amount,
        'amount_in_words': number_to_words(amount),
        'company_name': company_name,
        'company_address': company_address,
        'logo_base64': get_logo_base64(),
        'expense_type': expense_type,
        'payment_to': payment_to,
        'job_no': job_no,
        'unit': unit,
        'customer': customer,
        'vehicle_no': vehicle_no,
        'driver_name': driver_name,
        'from_location': from_location,
        'to_location': to_location,
        'bill_no': bill_no,
        'bill_amount': f"{float(bill_amount):,.2f}",
        'gst_percentage': gst_percentage,
        'gst_amount': f"{float(gst_amount):,.2f}",
        'total_amount': f"{float(total_amount):,.2f}",
        'clean_remarks': clean_remarks,
        'receiver_signature': receiver_signature,
        'created_by': created_by,
        'is_checked': is_checked,
        'checked_by': checked_by,
        'is_verified': is_verified,
        'verified_by': verified_by,
        'is_approved': is_approved,
        'approved_by': approved_by,
    }


def generate_petty_cash_voucher_pdf(obj, pc_type='TMS', browser=None):
    """
    Renders the exact petty cash payment voucher as a single-page A4 landscape PDF.
    Uses Playwright (Chromium) to match the browser print layout with real dotted lines.
    Falls back to xhtml2pdf if Playwright is unavailable.
    """
    pc_type = pc_type.upper()
    logo_b64 = get_logo_base64()

    custom_css = """
<style>
@page { size: A4 landscape !important; margin: 8mm !important; }
@media print { @page { size: A4 landscape !important; margin: 8mm !important; } }
body { padding: 0 !important; margin: 0 !important; background: #fff !important; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
.voucher-container {
    width: 100% !important; max-width: 100% !important; margin: 0 auto !important;
    box-shadow: none !important; border: 2.5px solid #444 !important;
    padding: 24px 34px 20px !important; box-sizing: border-box !important;
}
.header { min-height: 105px !important; margin-bottom: 16px !important; padding-bottom: 10px !important; }
.header img { height: 100px !important; width: 175px !important; object-fit: contain !important; }
.company-info h1 { font-size: 27px !important; }
.company-info p { font-size: 13.5px !important; margin-top: 5px !important; }
.voucher-title { font-size: 20px !important; margin: 8px 0 20px !important; }
.row { margin-bottom: 16px !important; font-size: 17px !important; }
.value { min-height: 24px !important; line-height: 24px !important; border-bottom: 2px dotted #444 !important; }
.narration-value { min-height: 24px !important; line-height: 24px !important; border-bottom: 2px dotted #444 !important; background: none !important; }
.signatures { margin-top: 32px !important; font-size: 17px !important; }
.signature-space { height: 48px !important; }
.prepared-name { font-size: 14px !important; }
</style>
"""

    if pc_type == 'TMS':
        amount_in_words = number_to_words(obj.tpc_amount or 0)
        payment_to = ''
        if obj.tpc_to_manual:
            payment_to = obj.tpc_to_manual
        elif obj.tpc_driver_name:
            payment_to = obj.tpc_driver_name.dm_name
        elif obj.tpc_driver_name_manual:
            payment_to = obj.tpc_driver_name_manual
        elif obj.tpc_to:
            payment_to = obj.tpc_to.first_name or obj.tpc_to.username
        clean_remarks = re.sub(r'\s*\[?Auto-generated.*', '', obj.tpc_remarks or '').strip()
        context = {
            'tpc': obj,
            'amount_in_words': amount_in_words,
            'payment_to': payment_to,
            'clean_remarks': clean_remarks,
        }
        template_name = 'asset_mgt_app/tms_petty_cash_voucher.html'

    elif pc_type == 'WMS':
        total_val = obj.wpc_total_amount if (obj.wpc_total_amount and obj.wpc_total_amount > 0) else (obj.wpc_bill_amount or 0)
        amount_in_words = number_to_words(total_val)
        payment_to = ''
        if obj.wpc_to_manual:
            payment_to = obj.wpc_to_manual
        elif obj.wpc_to:
            payment_to = obj.wpc_to.first_name or obj.wpc_to.username
        clean_remarks = re.sub(r'\s*\[?Auto-generated.*', '', obj.wpc_remarks or '').strip()
        context = {
            'wpc': obj,
            'amount_in_words': amount_in_words,
            'payment_to': payment_to,
            'clean_remarks': clean_remarks,
        }
        template_name = 'asset_mgt_app/wms_petty_cash_voucher.html'

    else:  # PMS
        total_val = obj.ppc_total_amount if (obj.ppc_total_amount and obj.ppc_total_amount > 0) else (obj.ppc_bill_amount or obj.ppc_amount or 0)
        amount_in_words = number_to_words(total_val)
        payment_to = ''
        if obj.ppc_to_manual:
            payment_to = obj.ppc_to_manual
        elif obj.ppc_to:
            payment_to = obj.ppc_to.first_name or obj.ppc_to.username
        clean_remarks = re.sub(r'\s*\[?Auto-generated.*', '', obj.ppc_remarks or '').strip()
        context = {
            'ppc': obj,
            'amount_in_words': amount_in_words,
            'payment_to': payment_to,
            'clean_remarks': clean_remarks,
        }
        template_name = 'asset_mgt_app/pms_petty_cash_voucher.html'

    html = render_to_string(template_name, context)
    html = html.replace('onload="window.print()"', '')
    if logo_b64:
        html = html.replace('/media/logo4.0.png', f'data:image/png;base64,{logo_b64}')
    html = html.replace('</head>', f'{custom_css}</head>')

    # Try Playwright
    try:
        if browser:
            page = browser.new_page()
            page.set_content(html, wait_until='networkidle')
            pdf_bytes = page.pdf(
                format='A4',
                landscape=True,
                print_background=True,
                prefer_css_page_size=True,
                margin={'top': '8mm', 'bottom': '8mm', 'left': '8mm', 'right': '8mm'}
            )
            page.close()
            return pdf_bytes
        else:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                b = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
                page = b.new_page()
                page.set_content(html, wait_until='networkidle')
                pdf_bytes = page.pdf(
                    format='A4',
                    landscape=True,
                    print_background=True,
                    prefer_css_page_size=True,
                    margin={'top': '8mm', 'bottom': '8mm', 'left': '8mm', 'right': '8mm'}
                )
                b.close()
                return pdf_bytes
    except Exception as e:
        print(f"Playwright rendering failed, falling back to xhtml2pdf: {e}")
        ctx = get_petty_cash_voucher_context(obj, pc_type)
        html_fallback = render_to_string('asset_mgt_app/petty_cash_voucher_pdf.html', ctx)
        voucher_pdf_buf = io.BytesIO()
        pisa.CreatePDF(html_fallback, dest=voucher_pdf_buf)
        return voucher_pdf_buf.getvalue()


def generate_petty_cash_combined_pdf(obj, pc_type='TMS', browser=None):
    """
    Renders the payment voucher as PDF and combines it with the attached bill (PDF or image).
    Returns PDF content as bytes.
    """
    pc_type = pc_type.upper()
    voucher_pdf_bytes = generate_petty_cash_voucher_pdf(obj, pc_type, browser=browser)

    writer = pypdf.PdfWriter()
    voucher_reader = pypdf.PdfReader(io.BytesIO(voucher_pdf_bytes))
    for page in voucher_reader.pages:
        writer.add_page(page)

    # Determine attachment field
    if pc_type == 'TMS':
        att_field = getattr(obj, 'tpc_bill_attachment', None)
    elif pc_type == 'WMS':
        att_field = getattr(obj, 'wpc_bill_attachment', None)
    else:
        att_field = getattr(obj, 'ppc_bill_attachment', None)

    if att_field and att_field.name:
        try:
            att_field.open('rb')
            content = att_field.read()
            att_field.close()
            fname = att_field.name.lower()

            if fname.endswith('.pdf'):
                att_reader = pypdf.PdfReader(io.BytesIO(content))
                for page in att_reader.pages:
                    writer.add_page(page)

            elif fname.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp', '.jfif', '.tiff', '.tif')):
                from reportlab.lib.pagesizes import A4, landscape
                from reportlab.pdfgen import canvas
                from reportlab.lib.utils import ImageReader

                img = Image.open(io.BytesIO(content))
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                img_w, img_h = img.size
                if img_w >= img_h:
                    page_w, page_h = landscape(A4)
                else:
                    page_w, page_h = A4
                margin = 20
                avail_w = page_w - (2 * margin)
                avail_h = page_h - (2 * margin)
                scale = min(avail_w / img_w, avail_h / img_h)
                draw_w = img_w * scale
                draw_h = img_h * scale
                x = (page_w - draw_w) / 2
                y = (page_h - draw_h) / 2

                img_pdf_buf = io.BytesIO()
                c = canvas.Canvas(img_pdf_buf, pagesize=(page_w, page_h))
                c.drawImage(ImageReader(img), x, y, width=draw_w, height=draw_h, preserveAspectRatio=True)
                c.showPage()
                c.save()
                img_pdf_buf.seek(0)
                img_reader = pypdf.PdfReader(img_pdf_buf)
                for page in img_reader.pages:
                    writer.add_page(page)

        except Exception as e:
            # If attachment fails, still return voucher PDF rather than breaking completely
            print(f"Warning: Failed to append bill attachment for {obj}: {e}")

    out_buf = io.BytesIO()
    writer.write(out_buf)
    return out_buf.getvalue()


def export_petty_cash_zip(queryset, pc_type='TMS', zip_filename=None):
    """
    Creates a ZIP archive containing attachments and pure voucher PDFs
    organized by: {BU_Folder}/{Voucher_Number}/{attachment and voucher PDF separately}.
    Returns an HttpResponse with the ZIP archive.
    """
    pc_type = pc_type.upper()
    if not zip_filename:
        zip_filename = f"{pc_type}_Petty_Cash_Attachments.zip"

    if pc_type == 'TMS':
        att_attr = 'tpc_bill_attachment'
    elif pc_type == 'WMS':
        att_attr = 'wpc_bill_attachment'
    else:
        att_attr = 'ppc_bill_attachment'

    # If total count is large (> 50), prioritize records that actually have attachments
    total_count = queryset.count()
    if total_count > 50:
        records_to_process = list(queryset.filter(**{f"{att_attr}__isnull": False}).exclude(**{att_attr: ""}))
        if not records_to_process:
            # If none have attachments, take the latest 50 records
            records_to_process = list(queryset[:50])
    else:
        records_to_process = list(queryset)

    # Launch Playwright browser once for the whole batch
    playwright_ctx = None
    browser = None
    try:
        from playwright.sync_api import sync_playwright
        playwright_ctx = sync_playwright().start()
        browser = playwright_ctx.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
    except Exception as e:
        print(f"Could not launch Playwright for zip export: {e}")

    buf = io.BytesIO()
    try:
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for record in records_to_process:
                # Determine BU folder name
                if pc_type == 'TMS':
                    bu = record.tpc_business.bvm_business if record.tpc_business else 'BVM Trans Solutions'
                    voucher_raw = record.tpc_number or f"TMS_{record.id}"
                    att_field = getattr(record, 'tpc_bill_attachment', None)
                elif pc_type == 'WMS':
                    bu = record.wpc_business.bvm_business if record.wpc_business else 'BVM Storage Solutions'
                    voucher_raw = record.wpc_number or f"WMS_{record.id}"
                    att_field = getattr(record, 'wpc_bill_attachment', None)
                else:
                    bu = record.ppc_business.bvm_business if record.ppc_business else 'BVM Pack Solutions'
                    voucher_raw = record.ppc_number or f"PMS_{record.id}"
                    att_field = getattr(record, 'ppc_bill_attachment', None)

                bu_folder = sanitize_filename(bu)
                voucher_folder = sanitize_filename(voucher_raw)
                base_folder = f"{bu_folder}/{voucher_folder}"

                # 1. Add raw attachment if exists (SEPARATELY)
                if att_field and att_field.name:
                    try:
                        att_field.open('rb')
                        att_bytes = att_field.read()
                        att_field.close()
                        att_name = os.path.basename(att_field.name)
                        safe_att_name = sanitize_filename(att_name)
                        zip_file.writestr(f"{base_folder}/{safe_att_name}", att_bytes)
                    except Exception as e:
                        print(f"Error reading attachment for record {record}: {e}")

                # 2. Add pure voucher PDF (SEPARATELY, NOT combined!)
                try:
                    pdf_bytes = generate_petty_cash_voucher_pdf(record, pc_type, browser=browser)
                    if pdf_bytes:
                        zip_file.writestr(f"{base_folder}/{voucher_folder}_voucher.pdf", pdf_bytes)
                except Exception as e:
                    print(f"Error generating voucher PDF for record {record}: {e}")

            if not zip_file.filelist:
                zip_file.writestr("info.txt", "No attachments or vouchers found for the selected filter.")
    finally:
        if browser:
            try:
                browser.close()
            except Exception:
                pass
        if playwright_ctx:
            try:
                playwright_ctx.stop()
            except Exception:
                pass

    buf.seek(0)
    response = HttpResponse(buf.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{zip_filename}"'
    return response
