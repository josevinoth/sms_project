import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from ..models import TripdetailInfo, Trip_closure_files_Info, Vehicle_allotmentInfo, TripAttachmentInfo
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

    # Also collect multi-file attachments from TripAttachmentInfo
    trip_num = getattr(inv_obj, 'id_tripnumber', None)
    if trip_num:
        multi_atts = TripAttachmentInfo.objects.filter(ta_tripnumber=trip_num)
        for att in multi_atts:
            if att.ta_file:
                file_fields.append(att.ta_file)

    IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp')
    has_any = False

    try:
        from pypdf import PdfWriter, PdfReader
        writer = PdfWriter()

        seen_sizes = set()

        for file_field in file_fields:
            if not file_field or not file_field.name:
                continue
            try:
                content = _stored_file_content(file_field)
                if content is None:
                    continue
                
                content_size = len(content)
                if content_size in seen_sizes:
                    continue
                seen_sizes.add(content_size)

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


def sync_closure_files_to_invoice(request, trip, files_obj):
    """
    Sync files uploaded via TripclosurefilesForm (tcf_*) to InvoiceDocumentInfo (id_*).
    Then regenerate the merged PDF.
    """
    invoice_doc = InvoiceDocumentInfo.objects.filter(id_tripnumber=trip.tr_tripnumber).first()
    if not invoice_doc:
        invoice_doc = InvoiceDocumentInfo(
            id_tripnumber=trip.tr_tripnumber,
            id_updated_by=request.user
        )

    # Inherit the current trip's financial status instead of forcing 'Ready for Invoice'
    changed = False
    if trip.tc_financestatus and invoice_doc.id_status != trip.tc_financestatus:
        invoice_doc.id_status = trip.tc_financestatus
        changed = True

    if 'tcf_trip_cost' in request.FILES and files_obj.tcf_trip_cost:
        _copy_stored_file(invoice_doc.id_trip_cost_doc, files_obj.tcf_trip_cost)
        changed = True
    elif request.POST.get('tcf_trip_cost-clear'):
        invoice_doc.id_trip_cost_doc = None
        changed = True

    if 'tcf_parking_cost' in request.FILES and files_obj.tcf_parking_cost:
        _copy_stored_file(invoice_doc.id_parking_doc, files_obj.tcf_parking_cost)
        changed = True
    elif request.POST.get('tcf_parking_cost-clear'):
        invoice_doc.id_parking_doc = None
        changed = True

    if 'tcf_toll_cost' in request.FILES and files_obj.tcf_toll_cost:
        _copy_stored_file(invoice_doc.id_toll_doc, files_obj.tcf_toll_cost)
        changed = True
    elif request.POST.get('tcf_toll_cost-clear'):
        invoice_doc.id_toll_doc = None
        changed = True

    if 'tcf_loading_cost' in request.FILES and files_obj.tcf_loading_cost:
        _copy_stored_file(invoice_doc.id_loading_doc, files_obj.tcf_loading_cost)
        changed = True
    elif request.POST.get('tcf_loading_cost-clear'):
        invoice_doc.id_loading_doc = None
        changed = True

    if 'tcf_unloading_cost' in request.FILES and files_obj.tcf_unloading_cost:
        _copy_stored_file(invoice_doc.id_unloading_doc, files_obj.tcf_unloading_cost)
        changed = True
    elif request.POST.get('tcf_unloading_cost-clear'):
        invoice_doc.id_unloading_doc = None
        changed = True

    if 'tcf_weighment_cost' in request.FILES and files_obj.tcf_weighment_cost:
        _copy_stored_file(invoice_doc.id_weighment_doc, files_obj.tcf_weighment_cost)
        changed = True
    elif request.POST.get('tcf_weighment_cost-clear'):
        invoice_doc.id_weighment_doc = None
        changed = True

    if 'tcf_handling_cost' in request.FILES and files_obj.tcf_handling_cost:
        _copy_stored_file(invoice_doc.id_handling_doc, files_obj.tcf_handling_cost)
        changed = True
    elif request.POST.get('tcf_handling_cost-clear'):
        invoice_doc.id_handling_doc = None
        changed = True

    if 'tcf_pod' in request.FILES and files_obj.tcf_pod:
        _copy_stored_file(invoice_doc.id_pod_doc, files_obj.tcf_pod)
        changed = True
    elif request.POST.get('tcf_pod-clear'):
        invoice_doc.id_pod_doc = None
        changed = True

    if changed or not invoice_doc.pk or TripAttachmentInfo.objects.filter(ta_tripnumber=trip.tr_tripnumber).exists():
        invoice_doc.id_updated_by = request.user
        invoice_doc.save()
        _try_merge_pdfs(invoice_doc)

@login_required
def invoice_documents_list(request):
    veh_no = request.GET.get('veh_no', '').strip()
    # Use timezone-aware datetime strings to prevent RuntimeWarning
    date_from = request.GET.get('date_from', '').strip() or '2026-05-01T00:00:00+05:30'
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
        # Use timezone-aware datetime strings to prevent RuntimeWarning
        date_from = request.GET.get('date_from', '').strip() or '2026-05-01T00:00:00+05:30'
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
            tc_financestatus_id__in=status_ids,
            tr_category_id__in=[1, 3]
        ).filter(
            Q(tr_enquirynumber__en_customername__cu_name__icontains='MAA') |
            Q(tr_enquirynumber__en_customername__cu_name__icontains='BLR')
        ).exclude(
            id__in=invoiced_trip_ids
        ).exclude(
            tr_consignmentnumber_id__in=excluded_cons_ids
        )

        if veh_no:
            trip_list = trip_list.filter(tr_vehiclenumber__icontains=veh_no)
        if date_from:
            trip_list = trip_list.filter(
                Q(tr_departeddate_pickup__gte=date_from) |
                Q(tr_departeddate__gte=date_from)
            )
        if date_to:
            date_to_end = f"{date_to} 23:59:59"
            trip_list = trip_list.filter(
                Q(tr_departeddate_pickup__lte=date_to_end) |
                Q(tr_departeddate__lte=date_to_end)
            )

        # Count before search filter for recordsTotal
        records_total = trip_list.count()

        if search_value:
            matching_invoice_trip_numbers = list(InvoiceDocumentInfo.objects.filter(
                id_status__status__icontains=search_value
            ).exclude(
                id_tripnumber__isnull=True
            ).exclude(
                id_tripnumber__exact=''
            ).values_list('id_tripnumber', flat=True))

            q_objects = (
                Q(tr_tripnumber__icontains=search_value) |
                Q(tr_consignmentnumber__co_consignmentnumber__icontains=search_value) |
                Q(tr_enquirynumber__en_enquirynumber__icontains=search_value) |
                Q(tr_enquirynumber__en_customername__cu_name__icontains=search_value) |
                Q(tr_vehiclenumber__icontains=search_value) |
                Q(tr_departedlocation__place_name__icontains=search_value) |
                Q(tr_reportedlocation__place_name__icontains=search_value) |
                Q(tc_financestatus__status__icontains=search_value)
            )

            if matching_invoice_trip_numbers:
                q_objects |= Q(tr_tripnumber__in=matching_invoice_trip_numbers)

            trip_list = trip_list.filter(q_objects)

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
        invoice_doc = InvoiceDocumentInfo(
            id_tripnumber=trip.tr_tripnumber,
            id_updated_by=request.user
        )
        if files_instance.tcf_pod:
            _copy_stored_file(invoice_doc.id_pod_doc, files_instance.tcf_pod)
        elif trip.tc_pod_attachment:
            _copy_stored_file(invoice_doc.id_pod_doc, trip.tc_pod_attachment)
        elif trip.td_pod:
            _copy_stored_file(invoice_doc.id_pod_doc, trip.td_pod)
        invoice_doc.save()

    # Fields editable in the settlement form on this page (status and all charges except trip cost)
    editable_fields = [
        'tc_financestatus', 
        'tc_parkingcost', 'tc_parkingcost_check',
        'tc_tollcost', 'tc_tollcost_check',
        'tc_loadingcost', 'tc_loadingcost_check',
        'tc_unloadingcost', 'tc_unloadingcost_check',
        'tc_weighmentcost', 'tc_weighmentcost_check',
        'tc_handlingcost', 'tc_handlingcost_check',
        'tc_supervisorcost', 'tc_supervisorcost_check',
        'tc_haltingcost', 'tc_haltingcost_check',
        'tc_rtocost', 'tc_rtocost_check',
        'tc_betacost', 'tc_betacost_check',
        'tc_cancellation', 'tc_cancellation_check',
        'tc_tripcost_check'
    ]

    if request.method == 'POST':
        settlement_form = TripSettlementForm(request.POST, request.FILES, instance=trip)
        files_form = TripclosurefilesForm(request.POST, request.FILES, instance=files_instance)
        invoice_form = InvoiceDocumentForm(request.POST, request.FILES, instance=invoice_doc)

        current_status_id = trip.tc_financestatus_id if trip.tc_financestatus_id else 9
        settlement_form.fields['tc_financestatus'].queryset = Tripstatusinfo.objects.filter(
            Q(id=9) | Q(id=current_status_id)
        )
        invoice_form.fields['id_status'].queryset = Tripstatusinfo.objects.filter(
            Q(id=9) | Q(id=current_status_id)
        )

        # Disable all settlement fields except status
        for field in settlement_form.fields:
            if field not in editable_fields:
                settlement_form.fields[field].disabled = True
                settlement_form.fields[field].required = False

        # All file-upload (closure) fields optional
        for field in files_form.fields:
            files_form.fields[field].required = False

        # Validate Sell Rate Doc if Special Sell > Standard Sell
        allotment = Vehicle_allotmentInfo.objects.filter(
            va_enquirynumber=trip.tr_enquirynumber
        ).filter(
            Q(va_vehiclenumber__vm_registrationnumber=trip.tr_vehiclenumber) |
            Q(va_vehiclenumber_mkt=trip.tr_vehiclenumber)
        ).first()
        if allotment and float(allotment.va_special_sale or 0) > float(allotment.va_sale or 0):
            has_sell_rate_doc = 'id_sell_rate_doc' in request.FILES or (invoice_doc and invoice_doc.id_sell_rate_doc and not request.POST.get('id_sell_rate_doc-clear'))
            if not has_sell_rate_doc:
                messages.error(request, "Sell Rate Doc is mandatory because Special Sell > Standard Sell.")
                return redirect('invoice_documents_add', trip_id=trip_id)

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

            # --- Sync from invoice documents to trip closure files ---
            if 'id_trip_cost_doc' in request.FILES and inv_obj.id_trip_cost_doc:
                _copy_stored_file(files_obj.tcf_trip_cost, inv_obj.id_trip_cost_doc)
            elif request.POST.get('id_trip_cost_doc-clear'):
                files_obj.tcf_trip_cost = None

            if 'id_parking_doc' in request.FILES and inv_obj.id_parking_doc:
                _copy_stored_file(files_obj.tcf_parking_cost, inv_obj.id_parking_doc)
            elif request.POST.get('id_parking_doc-clear'):
                files_obj.tcf_parking_cost = None

            if 'id_toll_doc' in request.FILES and inv_obj.id_toll_doc:
                _copy_stored_file(files_obj.tcf_toll_cost, inv_obj.id_toll_doc)
            elif request.POST.get('id_toll_doc-clear'):
                files_obj.tcf_toll_cost = None

            if 'id_loading_doc' in request.FILES and inv_obj.id_loading_doc:
                _copy_stored_file(files_obj.tcf_loading_cost, inv_obj.id_loading_doc)
            elif request.POST.get('id_loading_doc-clear'):
                files_obj.tcf_loading_cost = None

            if 'id_unloading_doc' in request.FILES and inv_obj.id_unloading_doc:
                _copy_stored_file(files_obj.tcf_unloading_cost, inv_obj.id_unloading_doc)
            elif request.POST.get('id_unloading_doc-clear'):
                files_obj.tcf_unloading_cost = None

            if 'id_weighment_doc' in request.FILES and inv_obj.id_weighment_doc:
                _copy_stored_file(files_obj.tcf_weighment_cost, inv_obj.id_weighment_doc)
            elif request.POST.get('id_weighment_doc-clear'):
                files_obj.tcf_weighment_cost = None

            if 'id_handling_doc' in request.FILES and inv_obj.id_handling_doc:
                _copy_stored_file(files_obj.tcf_handling_cost, inv_obj.id_handling_doc)
            elif request.POST.get('id_handling_doc-clear'):
                files_obj.tcf_handling_cost = None

            if 'id_pod_doc' in request.FILES and inv_obj.id_pod_doc:
                _copy_stored_file(files_obj.tcf_pod, inv_obj.id_pod_doc)
            elif request.POST.get('id_pod_doc-clear'):
                files_obj.tcf_pod = None

            files_obj.save()
            # -------------------------------------------------------

            # Synchronize trip status with document status for consistency
            if inv_obj.id_status and trip_obj.tc_financestatus != inv_obj.id_status:
                trip_obj.tc_financestatus = inv_obj.id_status
                trip_obj.save()

            # Sync checked/unchecked charge amounts to any linked TransInvoiceInfo record
            from .trans_invoice_view import sync_trip_charges_to_invoice
            sync_trip_charges_to_invoice(trip_obj)

            # Save multi-file attachments per category
            MULTI_CAT_MAP = {
                'id_trip_cost_files': 'TRIP_CHARGES',
                'id_parking_files': 'PARKING',
                'id_toll_files': 'TOLL',
                'id_loading_files': 'LOADING',
                'id_unloading_files': 'UNLOADING',
                'id_weighment_files': 'WEIGHMENT',
                'id_handling_files': 'HANDLING',
                'id_pod_files': 'POD',
            }
            for field_name, cat in MULTI_CAT_MAP.items():
                for uploaded_file in request.FILES.getlist(field_name):
                    TripAttachmentInfo.objects.create(
                        ta_tripnumber=trip.tr_tripnumber,
                        ta_file=uploaded_file,
                        ta_filename=uploaded_file.name,
                        ta_category=cat,
                    )

            # Attempt PDF merge using both record types
            _try_merge_pdfs(inv_obj, files_obj)

            messages.success(request, 'Invoice documents saved successfully.')
            return redirect('invoice_documents_list')

    else:
        settlement_form = TripSettlementForm(instance=trip)
        files_form = TripclosurefilesForm(instance=files_instance)

        # Map Ready for Invoice status by its ID 9
        ready_status = Tripstatusinfo.objects.filter(id=9).first()
        if invoice_doc and not invoice_doc.id_status and ready_status:
            invoice_doc.id_status = ready_status

        if not invoice_doc:
            invoice_form = InvoiceDocumentForm(initial={'id_status': ready_status})
        else:
            # Force the form to default to 'Ready for Invoice' for user convenience
            if invoice_doc and invoice_doc.id_status_id != 9:
                invoice_doc.id_status_id = 9
                
            invoice_form = InvoiceDocumentForm(instance=invoice_doc)
        
        # Only show 'Ready for Invoice' (ID 9) and the actual trip's current status (so it doesn't fail validation)
        current_status_id = trip.tc_financestatus_id if trip.tc_financestatus_id else 9
        invoice_form.fields['id_status'].queryset = Tripstatusinfo.objects.filter(
            Q(id=9) | Q(id=current_status_id)
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

        # Only show 'Ready for Invoice' (ID 9) and the current status
        current_status_id = trip.tc_financestatus_id if trip.tc_financestatus_id else 9
        settlement_form.fields['tc_financestatus'].queryset = Tripstatusinfo.objects.filter(
            Q(id=9) | Q(id=current_status_id)
        )
        
        # Default to 'Ready for Invoice' (ID 9) so they don't have to manually select it
        settlement_form.fields['tc_financestatus'].initial = 9
        # Restrict huge querysets for disabled fields to speed up page loading
        if trip.tr_enquirynumber_id:
            settlement_form.fields['tr_enquirynumber'].queryset = settlement_form.fields['tr_enquirynumber'].queryset.filter(id=trip.tr_enquirynumber_id)
        if trip.tr_consignmentnumber_id:
            settlement_form.fields['tr_consignmentnumber'].queryset = settlement_form.fields['tr_consignmentnumber'].queryset.filter(id=trip.tr_consignmentnumber_id)
        if trip.tr_departedlocation_id:
            settlement_form.fields['tr_departedlocation'].queryset = settlement_form.fields['tr_departedlocation'].queryset.filter(id=trip.tr_departedlocation_id)
        if trip.tr_reportedlocation_id:
            settlement_form.fields['tr_reportedlocation'].queryset = settlement_form.fields['tr_reportedlocation'].queryset.filter(id=trip.tr_reportedlocation_id)
        if trip.tr_vehiclesource_id:
            settlement_form.fields['tr_vehiclesource'].queryset = settlement_form.fields['tr_vehiclesource'].queryset.filter(id=trip.tr_vehiclesource_id)
        if trip.tr_vehicletype_id:
            settlement_form.fields['tr_vehicletype'].queryset = settlement_form.fields['tr_vehicletype'].queryset.filter(id=trip.tr_vehicletype_id)
        if trip.tr_vehicletype_placed_id:
            settlement_form.fields['tr_vehicletype_placed'].queryset = settlement_form.fields['tr_vehicletype_placed'].queryset.filter(id=trip.tr_vehicletype_placed_id)
        if trip.tr_category_id:
            settlement_form.fields['tr_category'].queryset = settlement_form.fields['tr_category'].queryset.filter(id=trip.tr_category_id)

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
    is_sell_rate_doc_required = False
    if allotment and float(allotment.va_special_sale or 0) > float(allotment.va_sale or 0):
        is_sell_rate_doc_required = True

    # Build attachments grouped by category for collapsible dropdowns
    raw_atts = TripAttachmentInfo.objects.filter(ta_tripnumber=trip.tr_tripnumber).order_by('ta_uploaded_at')
    attachments_by_cat = {}
    for att in raw_atts:
        attachments_by_cat.setdefault(att.ta_category, []).append(att)

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
        'is_sell_rate_doc_required': is_sell_rate_doc_required,
        'live_customer_ref': (
            trip.tr_consignmentnumber.co_cusrefnum
            if trip.tr_consignmentnumber and trip.tr_consignmentnumber.co_cusrefnum
            else trip.tr_customerref or ''
        ),
        'attachments_by_cat': attachments_by_cat,
    })
