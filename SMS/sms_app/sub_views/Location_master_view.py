from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import LocationMasterForm
from ..models import LocationMaster


@login_required(login_url='login_page')
def location_master_add(request, loc_id=0):
    first_name = request.session.get('first_name')

    if request.method == "GET":
        form = LocationMasterForm(instance=LocationMaster.objects.get(pk=loc_id)) if loc_id else LocationMasterForm()
        return render(request, "asset_mgt_app/location_master_gmap.html", {'form': form, 'first_name': first_name})

    else:
        instance = LocationMaster.objects.get(pk=loc_id) if loc_id else None
        form = LocationMasterForm(request.POST, instance=instance)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Record Saved Successfully')
                return redirect('location_master_list')
            except Exception as e:
                messages.error(request, 'Error saving location: {}'.format(str(e)))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

        return render(request, "asset_mgt_app/location_master_gmap.html", {'form': form, 'first_name': first_name})


@login_required(login_url='login_page')
def location_master_list(request):
    first_name = request.session.get('first_name')
    locations = LocationMaster.objects.all()
    return render(request, "asset_mgt_app/location_master_list.html", {
        'location_list': locations,
        'first_name': first_name
    })

@login_required(login_url='login_page')
def location_master_delete(request, loc_id):
    location = LocationMaster.objects.get(pk=loc_id)
    location.delete()
    return redirect('location_master_list')
