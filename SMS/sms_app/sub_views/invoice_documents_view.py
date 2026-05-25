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


def _stored_file_content(file_field):
    if not file_field or not file_field.name:
        return None
    try:
        if not file_field.storage.exists(file_field.name):
            print(f"Skipping missing stored file: {file_field.name}")
            return None
        file_field.open('rb')
        return file_field.read()
    except FileNotFoundError:
        print(f"Skipping missing stored file: {file_field.name}")
        return None
    finally:
        try:
            file_field.close()
        except Exception:
            pass


def _copy_stored_file(target_field, source_field):
    content = _stored_file_content(source_field)
    if content is None:
        return False
    target_field.save(
        source_field.name.split('/')[-1],
        ContentFile(content),
        save=False
    )
    return True


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
                content = _stored_file_content(file_field)
                if content is None:
                    continue
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
                    content = _stored_file_content(file_field)
                    if content is None:
                        continue
                    img = Image.open(io.BytesIO(content))
                    if img.mode != 'RGB': img = img.convert('RGB')
                    pages.append(img)
                except:
                    pass
            if pages:
                output = io.BytesIO()
                pages[0].save(output, format='PDF', save_all=True, append_images=pages[1:])
                output.seek(0)
                inv_obj.id_merged_pdf.save(f"merged_{inv_obj.id_tripnumber}.pdf", ContentFile(output.read()), save=True)
        except:
            pass


@login_required
def invoice_documents_list(request):
    veh_no = request.GET.get('veh_no', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    return render(request, 'asset_mgt_app/invoice_documents_list.html', {
        'veh_no': veh_no,
        'date_from': date_from,
        'date_to': date_to,
    })

@login_required
def invoice_documents_list_ajax_view(request):
    from django.http import JsonResponse
    try:
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        
        veh_no = request.GET.get('veh_no', '').strip()
        date_from = request.GET.get('date_from', '').strip()
        date_to = request.GET.get('date_to', '').strip()
        search_value = request.GET.get('search[value]', '').strip()

        from ..sub_models.trans_invoice_mod import TransInvoiceInfo
        from ..sub_models.consignmentgoods_mod import ConsignmentgoodsInfo

        status_ids = list(Tripstatusinfo.objects.filter(
            status__in=['Trip Settled', 'Ready for Invoice']
        ).values_list('id', flat=True))
        if not status_ids:
            status_ids = [7, 9]

        # Materialize subqueries into Python lists to avoid slow MySQL NOT IN (SELECT ...)
        invoiced_trip_ids = list(TransInvoiceInfo.objects.filter(ti_trip__isnull=False).values_list('ti_trip_id', flat=True))
        invoiced_cons_ids = set(TransInvoiceInfo.objects.filter(ti_consignment__isnull=False).values_list('ti_consignment_id', flat=True))
        invoiced_goods_ids = list(TransInvoiceInfo.objects.filter(ti_goods__isnull=False).values_list('ti_goods_id', flat=True))

        # Combine both consignment exclusion sources into one set
        cons_from_goods = set(ConsignmentgoodsInfo.objects.filter(id__in=invoiced_goods_ids).values_list(
            'cg_consignmentnumber_id', flat=True))
        excluded_cons_ids = list(invoiced_cons_ids | cons_from_goods)

        trip_list = TripdetailInfo.objects.select_related(
            'tr_enquirynumber',
            'tr_enquirynumber__en_customername',
            'tr_consignmentnumber',
            'tc_financestatus',
            'tr_departedlocation',
            'tr_reportedlocation',
        ).filter(
            tc_financestatus_id__in=status_ids
        ).exclude(
            id__in=invoiced_trip_ids
        ).exclude(
            tr_consignmentnumber_id__in=excluded_cons_ids
        )

        if veh_no:
            trip_list = trip_list.filter(tr_vehiclenumber__icontains=veh_no)
        if date_from:
            trip_list = trip_list.filter(tr_departeddate__date__gte=date_from)
        if date_to:
            trip_list = trip_list.filter(tr_departeddate__date__lte=date_to)

        # Count before search filter for recordsTotal
        records_total = trip_list.count()

        if search_value:
            trip_list = trip_list.filter(
                Q(tr_tripnumber__icontains=search_value) |
                Q(tr_consignmentnumber__co_consignmentnumber__icontains=search_value) |
                Q(tr_enquirynumber__en_enquirynumber__icontains=search_value) |
                Q(tr_enquirynumber__en_customername__cu_name__icontains=search_value) |
                Q(tr_vehiclenumber__icontains=search_value)
            )

        records_filtered = trip_list.count()

        # Ordering
        order_col = int(request.GET.get('order[0][column]', 3))
        order_dir = request.GET.get('order[0][dir]', 'desc')

        col_map = {
            1: 'tr_enquirynumber__en_enquirynumber',
            2: 'tr_consignmentnumber__co_consignmentnumber',
            3: 'tr_tripnumber',
            4: 'tr_enquirynumber__en_customername__cu_name',
            5: 'tr_vehiclenumber',
            6: 'tr_departedlocation__place_name',
            7: 'tr_reportedlocation__place_name',
            8: 'tr_departeddate_pickup',
        }
        
        order_field = col_map.get(order_col, '-tr_tripnumber')
        if order_dir == 'desc' and not order_field.startswith('-'):
            order_field = '-' + order_field
            
        trip_list = trip_list.order_by(order_field)

        # Pagination
        if length != -1:
            trip_list = trip_list[start:start + length]

        trip_numbers = [t.tr_tripnumber for t in trip_list if t.tr_tripnumber]
        invoice_docs = InvoiceDocumentInfo.objects.filter(id_tripnumber__in=trip_numbers).select_related('id_status')
        invoice_doc_map = {doc.id_tripnumber: doc for doc in invoice_docs}

        data = []
        for idx, trip in enumerate(trip_list):
            doc = invoice_doc_map.get(trip.tr_tripnumber)
            
            invoice_status = doc.id_status.status if doc and doc.id_status else '-'
            
            if doc and doc.id_merged_pdf:
                pdf_btn = f'<a href="{doc.id_merged_pdf.url}" target="_blank" class="btn-modern btn-highlight-cyan py-1 px-2 d-inline-flex align-items-center" style="font-size:0.8rem;text-decoration:none;border-radius:8px;gap:5px;"><i class="fas fa-file-pdf"></i> PDF</a>'
            else:
                pdf_btn = '<span style="color:var(--text-muted);font-size:0.85rem;font-style:italic;">Not generated</span>'
                
            from django.urls import reverse
            edit_url = reverse('invoice_documents_add', args=[trip.id])
            edit_btn = f'<a class="btn-modern btn-submit py-1 px-2 d-inline-flex align-items-center justify-content-center" href="{edit_url}" style="font-size:0.8rem;text-decoration:none;min-height:auto;border-radius:8px;"><i class="far fa-edit"></i></a>'
            
            data.append([
                str(start + idx + 1),
                str(trip.tr_enquirynumber) if trip.tr_enquirynumber else '',
                str(trip.tr_consignmentnumber) if trip.tr_consignmentnumber else '',
                str(trip.tr_tripnumber) if trip.tr_tripnumber else '',
                str(trip.tr_enquirynumber.en_customername) if trip.tr_enquirynumber and trip.tr_enquirynumber.en_customername else '',
                str(trip.tr_vehiclenumber) if trip.tr_vehiclenumber else '',
                str(trip.tr_departedlocation) if trip.tr_departedlocation else '',
                str(trip.tr_reportedlocation) if trip.tr_reportedlocation else '',
                trip.tr_departeddate_pickup.strftime("%d-%m-%Y") if trip.tr_departeddate_pickup else '',
                invoice_status,
                pdf_btn,
                edit_btn
            ])

        return JsonResponse({
            'draw': draw,
            'recordsTotal': records_total,
            'recordsFiltered': records_filtered,
            'data': data
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'error': str(e)})


@login_required
def invoice_documents_add(request, trip_id):
    trip = get_object_or_404(TripdetailInfo, pk=trip_id)

    # Load or initialise Trip_closure_files record (read-only display)
    files_instance = Trip_closure_files_Info.objects.filter(
        tcf_tripnumber=trip.tr_tripnumber
    ).order_by('-id').first()
    if not files_instance:
        files_instance = Trip_closure_files_Info(tcf_tripnumber=trip.tr_tripnumber)

    # Pre-populate and copy POD from Trip Detail if missing
    if not files_instance.tcf_pod:
        if trip.tc_pod_attachment:
            if _copy_stored_file(files_instance.tcf_pod, trip.tc_pod_attachment):
                files_instance.save()
        elif trip.td_pod:
            if _copy_stored_file(files_instance.tcf_pod, trip.td_pod):
                files_instance.save()

    # Load or initialise InvoiceDocumentInfo record
    invoice_doc = InvoiceDocumentInfo.objects.filter(
        id_tripnumber=trip.tr_tripnumber
    ).first()

    # Pre-populate and copy POD from Trip Detail / closure if missing
    if invoice_doc and not invoice_doc.id_pod_doc:
        if files_instance.tcf_pod:
            if _copy_stored_file(invoice_doc.id_pod_doc, files_instance.tcf_pod):
                invoice_doc.save()
        elif trip.tc_pod_attachment:
            if _copy_stored_file(invoice_doc.id_pod_doc, trip.tc_pod_attachment):
                invoice_doc.save()
        elif trip.td_pod:
            if _copy_stored_file(invoice_doc.id_pod_doc, trip.td_pod):
                invoice_doc.save()
    elif not invoice_doc:
        ready_status = Tripstatusinfo.objects.filter(Q(id=9) | Q(status='Ready for Invoice')).first()
        ready_status_id = ready_status.id if ready_status else 9

        invoice_doc = InvoiceDocumentInfo(
            id_tripnumber=trip.tr_tripnumber,
            id_status=ready_status,
            id_updated_by=request.user
        )
        if files_instance.tcf_pod:
            _copy_stored_file(invoice_doc.id_pod_doc, files_instance.tcf_pod)
        elif trip.tc_pod_attachment:
            _copy_stored_file(invoice_doc.id_pod_doc, trip.tc_pod_attachment)
        elif trip.td_pod:
            _copy_stored_file(invoice_doc.id_pod_doc, trip.td_pod)
        invoice_doc.save()

    # Fields editable in the settlement form on this page (status and parking charges)
    editable_fields = ['tc_financestatus', 'tc_parkingcost', 'tc_parkingcost_check']

    if request.method == 'POST':
        settlement_form = TripSettlementForm(request.POST, request.FILES, instance=trip)
        files_form = TripclosurefilesForm(request.POST, request.FILES, instance=files_instance)
        invoice_form = InvoiceDocumentForm(request.POST, request.FILES, instance=invoice_doc)

        # Only show 'Ready for Invoice' (ID 9 or by name)
        settlement_form.fields['tc_financestatus'].queryset = Tripstatusinfo.objects.filter(
            Q(id=9) | Q(status='Ready for Invoice'))
        invoice_form.fields['id_status'].queryset = Tripstatusinfo.objects.filter(
            Q(id=9) | Q(status='Ready for Invoice'))

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

            # Ensure tcf_pod is populated on POST save
            if not files_obj.tcf_pod:
                if trip_obj.tc_pod_attachment:
                    _copy_stored_file(files_obj.tcf_pod, trip_obj.tc_pod_attachment)
                elif trip_obj.td_pod:
                    _copy_stored_file(files_obj.tcf_pod, trip_obj.td_pod)
            files_obj.save()

            # Save invoice document record
            inv_obj = invoice_form.save(commit=False)
            inv_obj.id_tripnumber = trip.tr_tripnumber
            inv_obj.id_updated_by = request.user

            # Ensure id_pod_doc is populated on POST save
            if not inv_obj.id_pod_doc:
                if files_obj.tcf_pod:
                    _copy_stored_file(inv_obj.id_pod_doc, files_obj.tcf_pod)
                elif trip_obj.tc_pod_attachment:
                    _copy_stored_file(inv_obj.id_pod_doc, trip_obj.tc_pod_attachment)
                elif trip_obj.td_pod:
                    _copy_stored_file(inv_obj.id_pod_doc, trip_obj.td_pod)
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

        # Default status to Ready for Invoice (ID 9 or by name)
        ready_status = Tripstatusinfo.objects.filter(Q(id=9) | Q(status='Ready for Invoice')).first()
        ready_status_id = ready_status.id if ready_status else 9

        if not invoice_doc:
            invoice_form = InvoiceDocumentForm(initial={'id_status': ready_status_id})
        else:
            invoice_form = InvoiceDocumentForm(instance=invoice_doc)

        # Strictly enforce only 'Ready for Invoice' in the dropdown
        invoice_form.fields['id_status'].queryset = Tripstatusinfo.objects.filter(
            Q(id=9) | Q(status='Ready for Invoice')
        )

        # Pre-populate read-only display fields
        if trip.tr_enquirynumber:
            settlement_form.fields['customer_name'].initial = str(
                trip.tr_enquirynumber.en_customername
            )
        if trip.tr_departeddate_pickup:
            settlement_form.fields['trip_date'].initial = (
                trip.tr_departeddate_pickup.strftime('%d-%m-%Y')
            )

        # Only show 'Ready for Invoice' (ID 9 or by name)
        settlement_form.fields['tc_financestatus'].queryset = Tripstatusinfo.objects.filter(
            Q(id=9) | Q(status='Ready for Invoice'))

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
