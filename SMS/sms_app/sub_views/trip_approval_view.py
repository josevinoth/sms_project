from django.shortcuts import render, get_object_or_404, redirect
from ..models import TripdetailInfo, ConsignmentgoodsInfo, approval_status_info, Trip_approval_info
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required(login_url='login_page')
def trip_approval_view(request):
    trip_list = TripdetailInfo.objects.select_related(
        'tr_consignmentnumber',
        'tr_approval'
    ).all()

    consignment_map = {
        trip.id: ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber=trip.tr_consignmentnumber)
        for trip in trip_list
    }

    return render(request, "asset_mgt_app/trip_approval.html", {
        'trip_list': trip_list,
        'consignment_map': consignment_map,
        'status_list': approval_status_info.objects.all()
    })

@login_required
def update_trip_approval(request, trip_id):
    if request.method == 'POST':
        approval_status_id = request.POST.get('ta_approval_status')
        trip = get_object_or_404(TripdetailInfo, pk=trip_id)
        status_obj = get_object_or_404(approval_status_info, pk=approval_status_id)

        if trip.tr_approval:
            approval = trip.tr_approval
            approval.ta_approval_status = status_obj
            approval.ta_approved_by = request.user
        else:
            approval = Trip_approval_info.objects.create(
                ta_approval_status=status_obj,
                ta_approved_by=request.user
            )

        approval.save()
        trip.tr_approval = approval
        trip.save()

        messages.success(request, "Approval updated.")
    return redirect('trip_approval_view')
