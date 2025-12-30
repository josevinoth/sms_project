from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import DriverMasterForm
from ..sub_models.driver_master_mod import DrivermasterInfo


# Add / Edit Driver
@login_required(login_url='login_page')
def driver_add(request, driver_id=0):
    first_name = request.session.get('first_name')

    if request.method == "GET":
        if driver_id == 0:
            form = DriverMasterForm()
        else:
            driver = get_object_or_404(DrivermasterInfo, pk=driver_id)
            form = DriverMasterForm(instance=driver)

        return render(
            request,
            "asset_mgt_app/driver_add.html",
            {'form': form, 'first_name': first_name}
        )

    else:
        if driver_id == 0:
            form = DriverMasterForm(request.POST)
        else:
            driver = get_object_or_404(DrivermasterInfo, pk=driver_id)
            form = DriverMasterForm(request.POST, instance=driver)

        if form.is_valid():
            form.save()

        return redirect('/SMS/driver_list')
@login_required(login_url='login_page')
def driver_list(request):
    first_name = request.session.get('first_name')

    context = {
        'driver_list': DrivermasterInfo.objects.select_related(
            'dm_vehiclesource', 'dm_user_id'
        ),
        'first_name': first_name
    }

    return render(request, "asset_mgt_app/driver_list.html", context)
@login_required(login_url='login_page')
def driver_delete(request, driver_id):
    driver = get_object_or_404(DrivermasterInfo, pk=driver_id)
    driver.delete()
    return redirect('/SMS/driver_list')
