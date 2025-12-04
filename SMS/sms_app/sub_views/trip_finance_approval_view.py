from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from ..models import TripdetailInfo,Tripstatusinfo

from django.db.models import F, ExpressionWrapper, FloatField

@login_required
def trip_finance_approval_view(request):

    trip_list = TripdetailInfo.objects.filter(
        tc_financestatus_id=7
    ).annotate(
        total_amount=(
            (F('tc_tripcost') +
             F('tc_parkingcost') +
             F('tc_tollcost') +
             F('tc_loadingcost') +
             F('tc_unloadingcost') +
             F('tc_weighmentcost') +
             F('tc_handlingcost') +
             F('tc_supervisorcost') +
             F('tc_haltingcost'))
        )
    )

    allowed_statuses = Tripstatusinfo.objects.filter(id__in=[5,6,7])

    return render(request, "asset_mgt_app/trip_finance_approval.html", {
        "trip_list": trip_list,
        "status_list": allowed_statuses,
    })



@login_required
def update_trip_finance_approval(request, trip_id):

    trip = get_object_or_404(TripdetailInfo, pk=trip_id)

    if request.method == "POST":

        approval_status_id = request.POST.get("tc_financestatus")

        # restrict allowed status
        if int(approval_status_id) not in [5, 6, 7]:
            messages.error(request, "Invalid status selection.")
            return redirect("trip_finance_approval_view")

        status_obj = get_object_or_404(Tripstatusinfo, pk=approval_status_id)

        trip.tc_financestatus = status_obj
        trip.tr_updated_by = request.user
        trip.save()

        messages.success(request, "Finance status updated successfully.")

    return redirect("trip_finance_approval_view")
