import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.db import transaction
from django.db.models import Count

from ..sub_models.dmr_template_studio_mod import DmrTemplateMaster, DmrTemplateColumn
from ..sub_models.customer_mod import CustomerInfo
from ..sub_models.customerdepartment_mod import CustomerdepartmentInfo
from ..models import TripdetailInfo, ConsignmentgoodsInfo, ConsignmentdetailInfo, Vehicle_allotmentInfo
from .dmr_field_catalog import DMR_PAGE_CATALOG, AVAILABLE_CHARGES, extract_dmr_cell_value, is_dmr_column_mergeable
from sms_app.sub_views.transport_reports_view import get_tms_report_transport_charge


@login_required(login_url='login_page')
def dmr_template_list(request):
    """
    Lists all configurable DMR report templates with quick filters and actions.
    """
    templates = DmrTemplateMaster.objects.select_related('customer', 'department').annotate(
        col_count=Count('columns')
    ).order_by('-updated_at')

    customer_filter = request.GET.get('customer')
    if customer_filter:
        templates = templates.filter(customer_id=customer_filter)

    customers = CustomerInfo.objects.filter(cu_name__icontains='(T)').order_by('cu_name')

    context = {
        'templates': templates,
        'customers': customers,
        'selected_customer': customer_filter or '',
    }
    return render(request, "asset_mgt_app/dmr_template_list.html", context)


@login_required(login_url='login_page')
def dmr_template_create_or_edit(request, template_id=None):
    """
    Interactive Studio for creating or editing a DMR Report Excel template.
    """
    template_obj = None
    existing_columns = []
    if template_id:
        template_obj = get_object_or_404(DmrTemplateMaster, id=template_id)
        existing_columns = list(template_obj.columns.all().order_by('column_order').values(
            'id', 'column_order', 'column_header', 'source_page', 'field_key',
            'date_format', 'included_charges', 'static_value', 'column_width'
        ))

    customers = CustomerInfo.objects.filter(cu_name__icontains='(T)').order_by('cu_name')
    departments = CustomerdepartmentInfo.objects.all().order_by('ct_customerdepartment')

    context = {
        'template_obj': template_obj,
        'existing_columns_json': json.dumps(existing_columns),
        'page_catalog_json': json.dumps(DMR_PAGE_CATALOG),
        'available_charges_json': json.dumps(AVAILABLE_CHARGES),
        'page_catalog': DMR_PAGE_CATALOG,
        'available_charges': AVAILABLE_CHARGES,
        'customers': customers,
        'departments': departments,
    }
    return render(request, "asset_mgt_app/dmr_template_studio.html", context)


@login_required(login_url='login_page')
def dmr_template_save_ajax(request):
    """
    AJAX endpoint to save template master & its ordered columns in a single transaction.
    """
    if request.method != 'POST':
        return JsonResponse({'status': False, 'message': 'Invalid request method.'}, status=400)

    try:
        data = json.loads(request.body)
        template_id = data.get('template_id')
        template_name = (data.get('template_name') or '').strip()
        customer_id = data.get('customer_id') or None
        department_id = data.get('department_id') or None
        description = data.get('description', '')
        is_active = bool(data.get('is_active', True))
        is_default = bool(data.get('is_default', False))
        merge_identical_cells = bool(data.get('merge_identical_cells', False))
        columns_data = data.get('columns', [])

        if not template_name:
            return JsonResponse({'status': False, 'message': 'Template Name is required.'}, status=400)

        if not columns_data:
            return JsonResponse({'status': False, 'message': 'Please add at least one column to the template.'}, status=400)

        with transaction.atomic():
            if template_id:
                master = get_object_or_404(DmrTemplateMaster, id=template_id)
                master.template_name = template_name
                master.customer_id = customer_id
                master.department_id = department_id
                master.description = description
                master.is_active = is_active
                master.is_default = is_default
                master.merge_identical_cells = merge_identical_cells
                master.save()
                # Clear old columns to re-insert in current order
                master.columns.all().delete()
            else:
                master = DmrTemplateMaster.objects.create(
                    template_name=template_name,
                    customer_id=customer_id,
                    department_id=department_id,
                    description=description,
                    is_active=is_active,
                    is_default=is_default,
                    merge_identical_cells=merge_identical_cells,
                )

            # Insert columns
            cols_to_create = []
            for idx, c in enumerate(columns_data, start=1):
                cols_to_create.append(DmrTemplateColumn(
                    template=master,
                    column_order=idx,
                    column_header=c.get('column_header') or f"Col {idx}",
                    source_page=c.get('source_page') or 'SYSTEM',
                    field_key=c.get('field_key') or 'blank_column',
                    date_format=c.get('date_format') or '',
                    included_charges=c.get('included_charges') or '',
                    static_value=c.get('static_value') or '',
                    column_width=int(c.get('column_width') or 15),
                ))
            DmrTemplateColumn.objects.bulk_create(cols_to_create)

        from django.urls import reverse
        return JsonResponse({
            'status': True,
            'message': 'Template saved successfully!',
            'template_id': master.id,
            'redirect_url': reverse('dmr_template_edit', args=[master.id])
        })
    except Exception as e:
        return JsonResponse({'status': False, 'message': f"Error saving template: {str(e)}"}, status=500)


@login_required(login_url='login_page')
def dmr_template_delete(request, template_id):
    """
    Deletes a template and its columns.
    """
    template_obj = get_object_or_404(DmrTemplateMaster, id=template_id)
    template_name = template_obj.template_name
    template_obj.delete()
    messages.success(request, f"Template '{template_name}' was successfully deleted.")
    return redirect('dmr_template_list')


@login_required(login_url='login_page')
def dmr_template_duplicate(request, template_id):
    """
    Duplicates an existing template with all its configured columns.
    """
    orig = get_object_or_404(DmrTemplateMaster, id=template_id)
    with transaction.atomic():
        clone = DmrTemplateMaster.objects.create(
            template_name=f"Copy of {orig.template_name}",
            customer=orig.customer,
            department=orig.department,
            description=orig.description,
            is_active=True,
            is_default=False,
            merge_identical_cells=orig.merge_identical_cells,
        )
        cols = orig.columns.all().order_by('column_order')
        clone_cols = [
            DmrTemplateColumn(
                template=clone,
                column_order=c.column_order,
                column_header=c.column_header,
                source_page=c.source_page,
                field_key=c.field_key,
                date_format=c.date_format,
                included_charges=c.included_charges,
                static_value=c.static_value,
                column_width=c.column_width,
            ) for c in cols
        ]
        DmrTemplateColumn.objects.bulk_create(clone_cols)

    messages.success(request, f"Duplicated as '{clone.template_name}'. You can now customize it.")
    return redirect('dmr_template_edit', template_id=clone.id)


@login_required(login_url='login_page')
def dmr_template_preview_ajax(request):
    """
    Live sample preview: returns top 3 sample rows based on the current template columns.
    """
    try:
        data = json.loads(request.body)
        customer_id = data.get('customer_id')
        columns_data = data.get('columns', [])

        if not columns_data:
            return JsonResponse({'status': False, 'message': 'No columns defined to preview.'})

        # Fetch representative trips for sample data (prefer trips with completed delivery for full timestamps)
        base_qs = TripdetailInfo.objects.filter(tr_category_id=1).select_related(
            'tr_enquirynumber', 'tr_enquirynumber__en_customername',
            'tr_enquirynumber__en_customerdepartment', 'tr_consignmentnumber'
        )
        if customer_id:
            base_qs = base_qs.filter(tr_enquirynumber__en_customername_id=customer_id)

        sample_trips = list(base_qs.filter(tr_reporteddate__isnull=False).order_by('-id')[:3])
        if len(sample_trips) < 3:
            more_trips = list(base_qs.order_by('-id')[:3])
            # Merge without duplicates maintaining order
            seen_ids = set()
            combined = []
            for t in sample_trips + more_trips:
                if t.id not in seen_ids:
                    seen_ids.add(t.id)
                    combined.append(t)
            sample_trips = combined[:3]

        if not sample_trips:
            sample_trips = list(TripdetailInfo.objects.filter(tr_category_id=1).select_related(
                'tr_enquirynumber', 'tr_enquirynumber__en_customername',
                'tr_enquirynumber__en_customerdepartment', 'tr_consignmentnumber'
            ).order_by('-id')[:3])

        trip_cons_nums = [t.tr_consignmentnumber_id for t in sample_trips if t.tr_consignmentnumber_id]
        trip_enq_nums = [t.tr_enquirynumber_id for t in sample_trips]

        goods_map = {}
        for g in ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber_id__in=trip_cons_nums):
            goods_map.setdefault(g.cg_consignmentnumber_id, []).append(g)

        va_map = {
            v.va_enquirynumber_id: v for v in Vehicle_allotmentInfo.objects.filter(
                va_enquirynumber_id__in=trip_enq_nums
            ).select_related('va_vendor', 'va_driver')
        }
        cons_detail_map = {c.id: c for c in ConsignmentdetailInfo.objects.filter(id__in=trip_cons_nums)}

        columns_meta = []
        for i, c in enumerate(columns_data, 1):
            f_key = c.get('field_key')
            c_header = c.get('column_header') or f"Col {i}"
            is_merge = is_dmr_column_mergeable(field_key=f_key, column_header=c_header)
            columns_meta.append({
                'header': c_header,
                'field_key': f_key,
                'is_mergeable': is_merge
            })

        headers = [cm['header'] for cm in columns_meta]
        preview_rows = []

        for trip_idx, trip in enumerate(sample_trips, start=1):
            cons_detail = cons_detail_map.get(trip.tr_consignmentnumber_id)
            goods_list = goods_map.get(trip.tr_consignmentnumber_id) or [None]
            va = va_map.get(trip.tr_enquirynumber_id)
            try:
                cancellation_val = float(trip.tc_cancellation) if trip.tc_cancellation not in (None, "", "None") else 0.0
            except Exception:
                cancellation_val = 0.0
            effective_tripcost = 0.0 if cancellation_val > 0 else get_tms_report_transport_charge(trip, allotment=va)

            trip_key = f"trip_{trip.id}"
            for cons_goods in goods_list:
                row = []
                for c in columns_data:
                    val = extract_dmr_cell_value(
                        field_key=c.get('field_key'),
                        trip=trip,
                        cons_goods=cons_goods,
                        cons_detail=cons_detail,
                        va=va,
                        effective_tripcost=effective_tripcost,
                        row_idx=trip_idx,
                        date_fmt=c.get('date_format'),
                        included_charges=c.get('included_charges'),
                        static_val=c.get('static_value', '')
                    )
                    row.append(val)
                preview_rows.append({
                    'data': row,
                    'trip_key': trip_key
                })

        return JsonResponse({
            'status': True,
            'headers': headers,
            'columns_meta': columns_meta,
            'rows': [r['data'] for r in preview_rows],
            'row_items': preview_rows
        })
    except Exception as e:
        return JsonResponse({'status': False, 'message': str(e)}, status=500)
