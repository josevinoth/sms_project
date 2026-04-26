import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from ..models import TripdetailInfo, Trip_closure_files_Info, Vehicle_allotmentInfo
from ..forms import TripSettlementForm, TripclosurefilesForm
from ..sub_models.invoice_document_mod import InvoiceDocumentInfo
from ..sub_forms.invoice_document_form import InvoiceDocumentForm
from ..sub_models.trip_status_mod import Tripstatusinfo


def _try_merge_pdfs(inv_obj, closure_obj=None):
    """
    Merge all uploaded documents from both InvoiceDocumentInfo and Trip_closure_files_Info
    into a single combined PDF.
    Supports PDF files (via pypdf) and image files (via Pillow).
    """
    file_fields = [
        inv_obj.id_trip_cost_doc,
        inv_obj.id_parking_doc,
        inv_obj.id_toll_doc,
        inv_obj.id_loading_doc,
        inv_obj.id_unloading_doc,
        inv_obj.id_weighment_doc,
        inv_obj.id_handling_doc,
        inv_obj.id_pod_doc,
    ]

    if closure_obj:
        file_fields.extend([
            closure_obj.tcf_trip_cost,
            closure_obj.tcf_parking_cost,
            closure_obj.tcf_toll_cost,
            closure_obj.tcf_loading_cost,
            closure_obj.tcf_unloading_cost,
            closure_obj.tcf_weighment_cost,
            closure_obj.tcf_handling_cost,
            closure_obj.tcf_pod,
        ])

    IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp')
    has_any = False

    try:
        from pypdf import PdfWriter, PdfReader
        writer = PdfWriter()

        for file_field in file_fields:
            if not file_field or not file_field.name:
                continue
            try:
                file_field.open('rb')
                content = file_field.read()
                file_field.close()
                fname = file_field.name.lower()

                if fname.endswith('.pdf'):
                    reader = PdfReader(io.BytesIO(content))
                    for page in reader.pages:
                        writer.add_page(page)
                    has_any = True

                elif fname.endswith(IMAGE_EXTS):
                    from PIL import Image
                    img = Image.open(io.BytesIO(content))
                    if img.mode not in ('RGB', 'L'):
                        img = img.convert('RGB')
                    img_pdf_buf = io.BytesIO()
                    img.save(img_pdf_buf, format='PDF')
                    img_pdf_buf.seek(0)
                    reader = PdfReader(img_pdf_buf)
                    for page in reader.pages:
                        writer.add_page(page)
                    has_any = True

            except Exception as e:
                print(f"Error processing field {file_field}: {e}")

        if has_any:
            output = io.BytesIO()
            writer.write(output)
            output.seek(0)
            pdf_name = 'merged_{}.pdf'.format(inv_obj.id_tripnumber)
            inv_obj.id_merged_pdf.save(pdf_name, ContentFile(output.read()), save=True)
            print(f"Successfully merged documents for {inv_obj.id_tripnumber}")
        else:
            print(f"No documents found to merge for {inv_obj.id_tripnumber}")

    except Exception as e:
        print(f"Merge function robust error: {e}")
        # Simplest fallback (only if images used)
        try:
            from PIL import Image
            pages = []
            for file_field in file_fields:
                if not file_field or not file_field.name: continue
                if not file_field.name.lower().endswith(IMAGE_EXTS): continue
                try:
                    file_field.open('rb')
                    img = Image.open(io.BytesIO(file_field.read()))
                    file_field.close()
                    if img.mode != 'RGB': img = img.convert('RGB')
                    pages.append(img)
                except: pass
            if pages:
                output = io.BytesIO()
                pages[0].save(output, format='PDF', save_all=True, append_images=pages[1:])
                output.seek(0)
                inv_obj.id_merged_pdf.save(f"merged_{inv_obj.id_tripnumber}.pdf", ContentFile(output.read()), save=True)
        except: pass




@login_required
def invoice_documents_list(request):
    veh_no = request.GET.get('veh_no', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    from ..sub_models.trans_invoice_mod import TransInvoiceInfo
    
    # Show settled trips or trips ready for invoice
    status_ids = list(Tripstatusinfo.objects.filter(
        status__in=['Trip Settled', 'Ready for Invoice']
    ).values_list('id', flat=True))
    if not status_ids:
        status_ids = [7, 9]  # Fallback

    # Exclude trips already invoiced (linked in TransInvoiceInfo with is_woh=True)
    invoiced_trip_ids = TransInvoiceInfo.objects.filter(
        is_woh=True, 
        ti_trip_id__isnull=False
    ).values_list('ti_trip_id', flat=True)

    trip_list = TripdetailInfo.objects.select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_consignmentnumber',
        'tc_financestatus',
    ).filter(
        tc_financestatus_id__in=status_ids
    ).exclude(
        id__in=invoiced_trip_ids
    )

    if veh_no:
        trip_list = trip_list.filter(tr_vehiclenumber__icontains=veh_no)
    if date_from:
        trip_list = trip_list.filter(tr_departeddate__date__gte=date_from)
    if date_to:
        trip_list = trip_list.filter(tr_departeddate__date__lte=date_to)

    trip_list = trip_list.order_by('-tr_tripnumber')

    # Map trip_number -> InvoiceDocumentInfo
    trip_numbers = [t.tr_tripnumber for t in trip_list if t.tr_tripnumber]
    invoice_docs = InvoiceDocumentInfo.objects.filter(id_tripnumber__in=trip_numbers)
    invoice_doc_map = {doc.id_tripnumber: doc for doc in invoice_docs}

    trips_with_docs = []
    for trip in trip_list:
        doc = invoice_doc_map.get(trip.tr_tripnumber)
        trips_with_docs.append({
            'trip': trip,
            'invoice_doc': doc,
        })

    return render(request, 'asset_mgt_app/invoice_documents_list.html', {
        'trips_with_docs': trips_with_docs,
        'veh_no': veh_no,
        'date_from': date_from,
        'date_to': date_to,
    })


@login_required
def invoice_documents_add(request, trip_id):
    trip = get_object_or_404(TripdetailInfo, pk=trip_id)

    # Load or initialise Trip_closure_files record (read-only display)
    files_instance = Trip_closure_files_Info.objects.filter(
        tcf_tripnumber=trip.tr_tripnumber
    ).order_by('-id').first()
    if not files_instance:
        files_instance = Trip_closure_files_Info(tcf_tripnumber=trip.tr_tripnumber)

    # Load or initialise InvoiceDocumentInfo record
    invoice_doc = InvoiceDocumentInfo.objects.filter(
        id_tripnumber=trip.tr_tripnumber
    ).first()

    # Fields editable in the settlement form on this page (status only)
    editable_fields = ['tc_financestatus']

    if request.method == 'POST':
        settlement_form = TripSettlementForm(request.POST, request.FILES, instance=trip)
        files_form = TripclosurefilesForm(request.POST, request.FILES, instance=files_instance)
        invoice_form = InvoiceDocumentForm(request.POST, request.FILES, instance=invoice_doc)

        # Restrict status dropdown: Trip Settled (id=7) + Ready for Invoice
        settlement_form.fields['tc_financestatus'].queryset = Tripstatusinfo.objects.filter(
            id__in=[7]
        ) | Tripstatusinfo.objects.filter(status='Ready for Invoice')

        # Disable all settlement fields except status
        for field in settlement_form.fields:
            if field not in editable_fields:
                settlement_form.fields[field].disabled = True
                settlement_form.fields[field].required = False

        # All file-upload (closure) fields optional
        for field in files_form.fields:
            files_form.fields[field].required = False

        if invoice_form.is_valid() and settlement_form.is_valid() and files_form.is_valid():
            # Save status change on trip
            trip_obj = settlement_form.save(commit=False)
            trip_obj.tr_updated_by = request.user
            trip_obj.save()

            # Save closure files if any
            files_obj = files_form.save(commit=False)
            files_obj.tcf_tripnumber = trip.tr_tripnumber
            files_obj.save()

            # Save invoice document record
            inv_obj = invoice_form.save(commit=False)
            inv_obj.id_tripnumber = trip.tr_tripnumber
            inv_obj.id_updated_by = request.user
            inv_obj.save()

            # Synchronize trip status with document status for consistency
            if inv_obj.id_status and trip_obj.tc_financestatus != inv_obj.id_status:
                trip_obj.tc_financestatus = inv_obj.id_status
                trip_obj.save()

            # Attempt PDF merge using both record types
            _try_merge_pdfs(inv_obj, files_obj)

            messages.success(request, 'Invoice documents saved successfully.')
            return redirect('invoice_documents_list')

    else:
        settlement_form = TripSettlementForm(instance=trip)
        files_form = TripclosurefilesForm(instance=files_instance)

        # If no invoice doc exists yet, create an initial form with status defaulted to Trip Settled (7)
        if not invoice_doc:
            invoice_form = InvoiceDocumentForm(initial={'id_status': 7})
        else:
            invoice_form = InvoiceDocumentForm(instance=invoice_doc)

        # Pre-populate read-only display fields
        if trip.tr_enquirynumber:
            settlement_form.fields['customer_name'].initial = str(
                trip.tr_enquirynumber.en_customername
            )
        if trip.tr_departeddate_pickup:
            settlement_form.fields['trip_date'].initial = (
                trip.tr_departeddate_pickup.strftime('%d-%m-%Y')
            )

        # Restrict status dropdown: Trip Settled (id=7) + Ready for Invoice
        settlement_form.fields['tc_financestatus'].queryset = Tripstatusinfo.objects.filter(
            id__in=[7]
        ) | Tripstatusinfo.objects.filter(status='Ready for Invoice')

        # Disable all settlement fields except status
        for field in settlement_form.fields:
            if field not in editable_fields:
                settlement_form.fields[field].disabled = True
                settlement_form.fields[field].required = False

        for field in files_form.fields:
            files_form.fields[field].required = False

    # Sell value for display
    allotment = Vehicle_allotmentInfo.objects.filter(
        va_enquirynumber=trip.tr_enquirynumber
    ).filter(
        Q(va_vehiclenumber__vm_registrationnumber=trip.tr_vehiclenumber) |
        Q(va_vehiclenumber_mkt=trip.tr_vehiclenumber)
    ).first()
    va_sale = allotment.va_sale if allotment else 0

    return render(request, 'asset_mgt_app/invoice_documents_add.html', {
        'trip': trip,
        'tripclosure_form': settlement_form,
        'tripclosurefiles_form': files_form,
        'invoice_form': invoice_form,
        'invoice_doc': invoice_doc,
        'status_selected': trip.tc_financestatus.id if trip.tc_financestatus else None,
        'user_id': request.user.id,
        'enquiry_num': (
            trip.tr_enquirynumber.en_enquirynumber if trip.tr_enquirynumber else ''
        ),
        'va_sale': va_sale,
    })
