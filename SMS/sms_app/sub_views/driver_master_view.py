from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
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


@login_required(login_url='login_page')
def get_employee_driver_details(request):
    user_id = request.GET.get('user_id')

    try:
        user = User.objects.select_related('user_extinfo').get(id=user_id)
        return JsonResponse({
            'name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'mobile': user.user_extinfo.emp_contact if hasattr(user, 'user_extinfo') else ''
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'Invalid user'}, status=400)

def driver_autocomplete(request):
    term = request.GET.get('term', '').strip()

    drivers = DrivermasterInfo.objects.filter(
        dm_name__icontains=term
    )[:10]

    data = [{
        'id': d.id,  # 🔥 ADD THIS
        'name': d.dm_name,
        'number': d.dm_drivernumber,
        'lic': d.dm_driver_lic,
        'expiry': d.dm_driver_lic_expiry
    } for d in drivers]

    return JsonResponse(data, safe=False)