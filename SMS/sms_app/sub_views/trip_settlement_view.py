from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from ..models import  TripdetailInfo,Trip_closure_files_Info, Vehicle_allotmentInfo
from ..forms import TripSettlementForm,TripclosurefilesForm
from ..sub_models.trip_status_mod import Tripstatusinfo
from django.core.paginator import Paginator
from django.db.models import Q

@login_required
def trip_settlement_view(request):
    veh_no = request.GET.get('veh_no', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()

    trip_list = TripdetailInfo.objects.select_related(
        'tr_enquirynumber',
        'tr_enquirynumber__en_customername',
        'tr_consignmentnumber',
        'tr_approval',
        'tr_approval__ta_approval_status',
        'tr_category'
    ).filter(
        Q(tc_financestatus_id=4) & (
            Q(tr_category_id=1) |
            Q(tr_category_id=3) & (
                Q(tr_consignmentnumber__co_status_id=8) |
                Q(tr_enquirynumber__consignmentdetailinfo__co_status_id=8)
            )
        )
    )

    if veh_no:
        trip_list = trip_list.filter(tr_vehiclenumber__icontains=veh_no)

    if date_from:
        trip_list = trip_list.filter(tr_departeddate__date__gte=date_from)

    if date_to:
        trip_list = trip_list.filter(tr_departeddate__date__lte=date_to)

    trip_list = trip_list.order_by('-tr_tripnumber')

    return render(request, "asset_mgt_app/trip_settlement.html", {
        'tripsettlement_list': trip_list,
        'veh_no': veh_no,
        'date_from': date_from,
        'date_to': date_to,
    })

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
