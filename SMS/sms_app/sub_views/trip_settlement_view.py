from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from ..models import  TripdetailInfo,Trip_closure_files_Info
from ..forms import TripSettlementForm,TripclosurefilesForm
from ..sub_models.trip_status_mod import Tripstatusinfo


@login_required
def trip_settlement_view(request):
    trip_list = TripdetailInfo.objects.select_related(
        'tr_consignmentnumber',
        'tr_approval',
        'tr_approval__ta_approval_status'
    ).filter( tc_financestatus_id=4 )# Awaiting trip settlement)
    return render(request, "asset_mgt_app/trip_settlement.html", {
        'tripsettlement_list': trip_list
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

    if request.method == "POST":

        print("---- POST RECEIVED ----")
        print(request.POST)
        print(request.FILES)

        form = TripSettlementForm(request.POST, request.FILES, instance=trip)
        files_form = TripclosurefilesForm(request.POST, request.FILES, instance=files_instance)

        # restrict statuses
        form.fields['tc_financestatus'].queryset = Tripstatusinfo.objects.filter(id__in=[4, 7])

        # Disable and un-require all other fields
        for field in form.fields:
            if field != "tc_financestatus":
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
        files_form = TripclosurefilesForm(instance=files_instance)

        form.fields['tc_financestatus'].queryset = Tripstatusinfo.objects.filter(id__in=[4, 7])

        for field in form.fields:
            if field != "tc_financestatus":
                form.fields[field].disabled = True
                form.fields[field].required = False

        for field in files_form.fields:
            files_form.fields[field].required = False

    return render(request, "asset_mgt_app/trip_settlement_edit.html", {
        'trip': trip,
        'tripclosure_form': form,
        'tripclosurefiles_form': files_form
    })
