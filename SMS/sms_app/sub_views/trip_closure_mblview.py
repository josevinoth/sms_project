from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import Trclosure_mblForm
from ..models import Trclosure_mblInfo
from ..sub_models.places_mod import Places
from ..sub_models.trip_status_mod import Tripstatusinfo
from ..sub_models.tripdetail_mod import TripdetailInfo


@login_required(login_url='login_page')
def trclosure_mbl_add(request, trm_id=0):
    first_name = request.session.get('first_name')

    # Fetch dropdown options
    trips = TripdetailInfo.objects.all()
    places = Places.objects.all()
    statuses = Tripstatusinfo.objects.all()

    if request.method == "GET":
        if trm_id == 0:
            form = Trclosure_mblForm()
        else:
            trclosure = Trclosure_mblInfo.objects.get(pk=trm_id)
            form = Trclosure_mblForm(instance=trclosure)

        return render(request, "asset_mgt_app/trclosure_mbl_add.html", {
            'form': form,
            'first_name': first_name,
            'trips': trips,
            'places': places,
            'statuses': statuses
        })

    else:
        if trm_id == 0:
            form = Trclosure_mblForm(request.POST, request.FILES)
        else:
            trclosure = get_object_or_404(Trclosure_mblInfo, pk=trm_id)
            form = Trclosure_mblForm(request.POST, request.FILES, instance=trclosure)

        if form.is_valid():
            form.save()
            messages.success(request, 'Record Saved Successfully')
            return redirect('/SMS/trclosure_mbl_add')

    return render(request, "asset_mgt_app/trclosure_mbl_add.html", {
        'form': form,
        'first_name': first_name,
        'trips': trips,
        'places': places,
        'statuses': statuses
    })

@login_required(login_url='login_page')
def trclosure_mbl_list(request):
    trip_closures = Trclosure_mblInfo.objects.all()
    return render(request, "asset_mgt_app/trclosure_mbl_list.html", {"trip_closures": trip_closures})

@login_required(login_url='login_page')
def trclosure_mbl_delete(request, trm_id):
    trclosure = Trclosure_mblInfo.objects.get(pk=trm_id)
    trclosure.delete()
    return redirect('/SMS/trclosure_mbl_list')
