# views.py
from django.shortcuts import render, redirect
from ..models import Warehouse_goods_info, GoodsPartialDispatchInfo, Dispatch_info
from django.utils.timezone import now
from django.db.models import Q
from django.contrib import messages

def backfill_preview(request):
    record = Warehouse_goods_info.objects.filter(
        wh_dispatch_num__isnull=False
    ).filter(
        Q(wh_dispatch_qty__isnull=True) | Q(wh_dispatch_qty=0),
        wh_goods_pieces__gt=0
    ).exclude(
        id__in=GoodsPartialDispatchInfo.objects.values_list('pd_goods_id', flat=True)
    ).first()

    return render(request, "asset_mgt_app/backfill_preview.html", {'record': record})


def backfill_one_record(request):
    record = Warehouse_goods_info.objects.filter(
        wh_dispatch_num__isnull=False
    ).filter(
        Q(wh_dispatch_qty__isnull=True) | Q(wh_dispatch_qty=0),
        wh_goods_pieces__gt=0
    ).exclude(
        id__in=GoodsPartialDispatchInfo.objects.values_list('pd_goods_id', flat=True)
    ).first()

    if not record:
        messages.warning(request, "No records left to backfill.")
        return redirect('backfill_preview')

    try:
        dispatch_info = Dispatch_info.objects.get(dispatch_num=record.wh_dispatch_num)
    except Dispatch_info.DoesNotExist:
        messages.error(request, f"Dispatch info not found for dispatch_num {record.wh_dispatch_num}")
        return redirect('backfill_preview')

    GoodsPartialDispatchInfo.objects.create(
        pd_goods=record,
        pd_dispatch_info=dispatch_info,
        pd_dispatch_qty=record.wh_goods_pieces,
        pd_dispatch_time=record.wh_checkout_time or now()
    )

    record.wh_dispatch_qty = record.wh_goods_pieces
    record.save(update_fields=['wh_dispatch_qty'])

    messages.success(request, f"Backfilled 1 record: {record.wh_qr_rand_num}")
    return redirect('backfill_preview')

def backfill_all_records(request):
    records = Warehouse_goods_info.objects.filter(
        wh_dispatch_num__isnull=False
    ).filter(
        Q(wh_dispatch_qty__isnull=True) | Q(wh_dispatch_qty=0),
        wh_goods_pieces__gt=0
    ).exclude(
        id__in=GoodsPartialDispatchInfo.objects.values_list('pd_goods_id', flat=True)
    )

    count = 0
    for record in records:
        try:
            dispatch_info = Dispatch_info.objects.get(dispatch_num=record.wh_dispatch_num)
        except Dispatch_info.DoesNotExist:
            continue  # skip if no dispatch info

        GoodsPartialDispatchInfo.objects.create(
            pd_goods=record,
            pd_dispatch_info=dispatch_info,
            pd_dispatch_qty=record.wh_goods_pieces,
            pd_dispatch_time=record.wh_checkout_time or now()
        )

        record.wh_dispatch_qty = record.wh_goods_pieces
        record.save(update_fields=['wh_dispatch_qty'])

        count += 1

    messages.success(request, f" Backfilled {count} records into GoodsPartialDispatchInfo.")
    return redirect('backfill_preview')


from django.utils.timezone import now


def backfill_goods_weight(request):
    records = GoodsPartialDispatchInfo.objects.filter(
        Q(pd_goods_weight__isnull=True) | Q(pd_goods_weight=0)
    )

    updated_count = 0
    for record in records:
        if record.pd_dispatch_qty is None:
            continue

        weight = getattr(record.pd_goods, 'wh_goods_weight', None)
        if weight is not None:
            record.pd_goods_weight = weight
            record.save(update_fields=['pd_goods_weight'])
            updated_count += 1

    messages.success(request, f"Backfilled weight for {updated_count} records.")
    return redirect('backfill_preview')


def backfill_enquiry_sell_rates_logic():
    """
    Backfills missing env_sale and env_special_sale in Enquirynotevehicle from:
    1. Vehicle_allotmentInfo (va_sale & va_special_sale) matching enquiry + vehicle type.
    2. RtratemasterInfo (Route Rate Master) if no allotment exists.
    Returns (updated_count, skipped_count)
    """
    from ..sub_models.enquirynote_vehicle_mod import Enquirynotevehicle
    from ..sub_models.vehicle_allotment_mod import Vehicle_allotmentInfo
    from ..models import RtratemasterInfo
    from django.db.models import Q

    env_records = Enquirynotevehicle.objects.filter(
        Q(env_sale__isnull=True) | Q(env_sale=0)
    )

    updated_count = 0
    skipped_count = 0

    for env in env_records:
        enquiry = env.env_enquirynumber
        vt_id = env.env_vehicletype_id
        if not enquiry or not vt_id:
            skipped_count += 1
            continue

        sale_rate = None
        special_sale_rate = None

        # 1. Match in Vehicle_allotmentInfo
        allotments = Vehicle_allotmentInfo.objects.filter(
            va_enquirynumber=enquiry,
            va_vehicletype_id=vt_id
        )
        if not allotments.exists():
            allotments = Vehicle_allotmentInfo.objects.filter(va_enquirynumber=enquiry)

        for a in allotments:
            if a.va_sale is not None and float(a.va_sale) > 0:
                sale_rate = float(a.va_sale)
            if a.va_special_sale is not None and float(a.va_special_sale) > 0:
                special_sale_rate = float(a.va_special_sale)
            if sale_rate:
                break

        # 2. Fallback to RtratemasterInfo
        if not sale_rate:
            filter_kwargs = {
                'ro_customer': enquiry.en_customername,
                'ro_fromlocation': enquiry.en_fromlocaion,
                'ro_tolocation': enquiry.en_tolocation,
                'ro_vehicletype_id': vt_id,
            }
            if enquiry.en_customerdepartment:
                filter_kwargs['ro_customerdepartment'] = enquiry.en_customerdepartment
            if env.env_vehiclecategory_id:
                filter_kwargs['ro_vehiclecategory_id'] = env.env_vehiclecategory_id

            rate = RtratemasterInfo.objects.filter(**filter_kwargs).first()
            if not rate and enquiry.en_customerdepartment:
                filter_without_dept = {k: v for k, v in filter_kwargs.items() if k != 'ro_customerdepartment'}
                rate = RtratemasterInfo.objects.filter(**filter_without_dept).first()

            if rate and rate.ro_rate:
                sale_rate = float(rate.ro_rate)

        if sale_rate:
            env.env_sale = sale_rate
            env.env_special_sale = special_sale_rate or sale_rate
            env.save(update_fields=['env_sale', 'env_special_sale'])
            updated_count += 1
        else:
            skipped_count += 1

    return updated_count, skipped_count


def backfill_enquiry_sell_rates(request):
    updated, skipped = backfill_enquiry_sell_rates_logic()
    messages.success(request, f"Backfilled sell rates for {updated} Enquiry Vehicle records ({skipped} skipped/unmatched).")
    return redirect('backfill_preview')

