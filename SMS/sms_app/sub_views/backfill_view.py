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
