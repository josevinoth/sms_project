from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from ..models import  TripdetailInfo,Trip_closure_files_Info, Vehicle_allotmentInfo
from ..forms import TripSettlementForm,TripclosurefilesForm
from ..sub_models.trip_status_mod import Tripstatusinfo
from django.core.paginator import Paginator
from django.db.models import Q, Exists, OuterRef

@login_required
def trip_settlement_view(request):
    veh_no = request.GET.get('veh_no', '').strip()
    date_from = request.GET.get('date_from', '').strip() or '2026-05-01'
    date_to = request.GET.get('date_to', '').strip()

    return render(request, "asset_mgt_app/trip_settlement.html", {
        'veh_no': veh_no,
        'date_from': date_from,
        'date_to': date_to,
    })

@login_required
def trip_settlement_list_ajax_view(request):
    from django.http import JsonResponse
    from ..sub_models.consignmentdetail_mod import ConsignmentdetailInfo
    try:
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        
        veh_no = request.GET.get('veh_no', '').strip()
        date_from = request.GET.get('date_from', '').strip() or '2026-05-01'
        date_to = request.GET.get('date_to', '').strip()
        search_value = request.GET.get('search[value]', '').strip()

        # Direct Exists subquery on the outer queryset - correct Django ORM pattern
        has_settled_consignment = Exists(
            ConsignmentdetailInfo.objects.filter(
                co_enquirynumber=OuterRef('tr_enquirynumber_id'),
                co_status_id=8
            )
        )

        trip_list = TripdetailInfo.objects.select_related(
            'tr_enquirynumber',
            'tr_enquirynumber__en_customername',
            'tr_consignmentnumber',
            'tr_approval',
            'tr_approval__ta_approval_status',
            'tr_category',
            'tc_financestatus'
        ).filter(
            Q(tc_financestatus_id=4) & (
                Q(tr_category_id=1) |
                (
                    Q(tr_category_id=3) & (
                        Q(tr_consignmentnumber__co_status_id=8) |
                        has_settled_consignment
                    )
                )
            )
        )

        if veh_no:
            trip_list = trip_list.filter(tr_vehiclenumber__icontains=veh_no)
        if date_from:
            trip_list = trip_list.filter(tr_departeddate_pickup__gte=date_from)
        if date_to:
            trip_list = trip_list.filter(tr_departeddate_pickup__lte=f"{date_to} 23:59:59")

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
        order_col = int(request.GET.get('order[0][column]', 2))
        order_dir = request.GET.get('order[0][dir]', 'desc')

        col_map = {
            0: 'tr_enquirynumber__en_enquirynumber',
            1: 'tr_consignmentnumber__co_consignmentnumber',
            2: 'tr_tripnumber',
            3: 'tr_category__category',
            4: 'tr_enquirynumber__en_customername__cu_name',
            5: 'tr_vehiclenumber',
            6: 'tr_departedlocation__place_name',
            7: 'tr_reportedlocation__place_name',
            8: 'tr_departeddate_pickup',
            9: 'tc_tripcost',
            10: 'tc_parkingcost',
            11: 'tc_tollcost',
            12: 'tc_loadingcost',
            13: 'tc_unloadingcost',
            14: 'tc_weighmentcost',
            15: 'tc_handlingcost',
        }

        order_field = col_map.get(order_col, '-tr_tripnumber')
        if order_dir == 'desc' and not order_field.startswith('-'):
            order_field = '-' + order_field
            
        trip_list = trip_list.order_by(order_field)

        # Pagination
        if length != -1:
            trip_list = trip_list[start:start + length]

        data = []
        for trip in trip_list:
            
            from django.urls import reverse
            edit_url = reverse('trip_settlement_edit', args=[trip.id])
            edit_btn = f'<a class="btn btn-primary" href="{edit_url}"><i class="far fa-edit"></i></a>'
            
            data.append([
                str(trip.tr_enquirynumber) if trip.tr_enquirynumber else '',
                str(trip.tr_consignmentnumber) if trip.tr_consignmentnumber else '',
                str(trip.tr_tripnumber) if trip.tr_tripnumber else '',
                str(trip.tr_category.category) if trip.tr_category else '',
                str(trip.tr_enquirynumber.en_customername) if trip.tr_enquirynumber and trip.tr_enquirynumber.en_customername else '',
                str(trip.tr_vehiclenumber) if trip.tr_vehiclenumber else '',
                str(trip.tr_departedlocation) if trip.tr_departedlocation else '',
                str(trip.tr_reportedlocation) if trip.tr_reportedlocation else '',
                trip.tr_departeddate_pickup.strftime("%d-%m-%Y") if trip.tr_departeddate_pickup else '',
                '' if trip.tc_tripcost is None else str(trip.tc_tripcost),
                '' if trip.tc_parkingcost is None else str(trip.tc_parkingcost),
                '' if trip.tc_tollcost is None else str(trip.tc_tollcost),
                '' if trip.tc_loadingcost is None else str(trip.tc_loadingcost),
                '' if trip.tc_unloadingcost is None else str(trip.tc_unloadingcost),
                '' if trip.tc_weighmentcost is None else str(trip.tc_weighmentcost),
                '' if trip.tc_handlingcost is None else str(trip.tc_handlingcost),
                str(trip.tc_financestatus.status) if trip.tc_financestatus else '',
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
def trip_settlement_edit(request, trip_id):

    trip = get_object_or_404(TripdetailInfo, pk=trip_id)

    # Load last file record
    files_instance = Trip_closure_files_Info.objects.filter(
        tcf_tripnumber=trip.tr_tripnumber
    ).order_by('-id').first()

    if not files_instance:
        files_instance = Trip_closure_files_Info(tcf_tripnumber=trip.tr_tripnumber)

    # --- NEW LOGIC: Pre-populate POD from TripdetailInfo if missing ---
    if not files_instance.tcf_pod and trip.tc_pod_attachment:
        from django.core.files.base import ContentFile
        try:
            trip.tc_pod_attachment.open('rb')
            files_instance.tcf_pod.save(
                trip.tc_pod_attachment.name.split('/')[-1],
                ContentFile(trip.tc_pod_attachment.read()),
                save=False 
            )
        except Exception as e:
            print(f"Error copying POD: {e}")
        finally:
            trip.tc_pod_attachment.close()
    # ------------------------------------------------------------------

    if request.method == "POST":
        print("---- POST RECEIVED ----")
        print(request.POST)
        print(request.FILES)

        form = TripSettlementForm(request.POST, request.FILES, instance=trip)
        files_form = TripclosurefilesForm(request.POST, request.FILES, instance=files_instance)

        # restrict statuses
        form.fields['tc_financestatus'].queryset = Tripstatusinfo.objects.filter(id__in=[4, 7])

        # List of fields that SHOULD be editable during settlement
        editable_fields = [
            'tc_financestatus', 'tr_iou', 'tc_tripcost', 'tc_parkingcost', 
            'tc_tollcost', 'tc_loadingcost', 'tc_unloadingcost', 
            'tc_weighmentcost', 'tc_handlingcost', 'tc_supervisorcost', 
            'tc_haltingcost', 'tc_no_of_days_halting','tc_rtocost','tc_betacost',
            'tc_cancellation', 'tc_tripcost_check', 'tc_parkingcost_check', 'tc_tollcost_check',
            'tc_loadingcost_check', 'tc_unloadingcost_check', 'tc_weighmentcost_check',
            'tc_supervisorcost_check', 'tc_handlingcost_check', 'tc_haltingcost_check',
            'tc_total_halting_cost_check', 'tc_rtocost_check', 'tc_betacost_check',
            'tc_cancellation_check'
        ]

        # Disable and un-require all other fields
        for field in form.fields:
            if field not in editable_fields:
                form.fields[field].disabled = True
                form.fields[field].required = False

        # Make all file fields optional
        for field in files_form.fields:
            files_form.fields[field].required = False

        print("FORM ERRORS:", form.errors)
        print("FILE ERRORS:", files_form.errors)

        if form.is_valid() and files_form.is_valid():

            trip_obj = form.save(commit=False)
            trip_obj.tr_updated_by = request.user
            trip_obj.save()

            files_obj = files_form.save(commit=False)
            files_obj.tcf_tripnumber = trip.tr_tripnumber
            files_obj.save()

            messages.success(request, "Trip settlement updated.")
            return redirect('trip_settlement_view')

    else:
        form = TripSettlementForm(instance=trip)
        
        # Populate Customer Name and Trip Date
        if trip.tr_enquirynumber:
            form.fields['customer_name'].initial = str(trip.tr_enquirynumber.en_customername)
        if trip.tr_departeddate_pickup:
            form.fields['trip_date'].initial = trip.tr_departeddate_pickup.strftime('%d-%m-%Y')

        files_form = TripclosurefilesForm(instance=files_instance)

        form.fields['tc_financestatus'].queryset = Tripstatusinfo.objects.filter(id__in=[4, 7])

        # List of fields that SHOULD be editable during settlement
        editable_fields = [
            'tc_financestatus', 'tr_iou', 'tc_tripcost', 'tc_parkingcost', 
            'tc_tollcost', 'tc_loadingcost', 'tc_unloadingcost', 
            'tc_weighmentcost', 'tc_handlingcost', 'tc_supervisorcost', 
            'tc_haltingcost', 'tc_no_of_days_halting','tc_rtocost','tc_betacost',
            'tc_cancellation', 'tc_tripcost_check', 'tc_parkingcost_check', 'tc_tollcost_check',
            'tc_loadingcost_check', 'tc_unloadingcost_check', 'tc_weighmentcost_check',
            'tc_supervisorcost_check', 'tc_handlingcost_check', 'tc_haltingcost_check',
            'tc_total_halting_cost_check', 'tc_rtocost_check', 'tc_betacost_check',
            'tc_cancellation_check'
        ]

        for field in form.fields:
            if field not in editable_fields:
                form.fields[field].disabled = True
                form.fields[field].required = False

        for field in files_form.fields:
            files_form.fields[field].required = False

    # Fetch Sell value from allotment
    allotment = Vehicle_allotmentInfo.objects.filter(
        va_enquirynumber=trip.tr_enquirynumber
    ).filter(
        Q(va_vehiclenumber__vm_registrationnumber=trip.tr_vehiclenumber) |
        Q(va_vehiclenumber_mkt=trip.tr_vehiclenumber)
    ).first()
    va_sale = allotment.va_sale if allotment else 0

    return render(request, "asset_mgt_app/trip_settlement_edit.html", {
        'trip': trip,
        'tripclosure_form': form,
        'tripclosurefiles_form': files_form,
        'status_selected': trip.tc_financestatus.id if trip.tc_financestatus else None,
        'user_id': request.user.id,
        'enquiry_num': trip.tr_enquirynumber.en_enquirynumber if trip.tr_enquirynumber else '',
        'is_edit': True,
        'va_sale': va_sale,
    })
