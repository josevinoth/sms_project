from django.contrib.auth.decorators import login_required
from django.core.checks import messages
from django.shortcuts import render, redirect
from ..forms import vechicle_procurementForm
from ..models import Vehicle_procurementInfo

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import vechicle_procurementForm
from ..models import Vehicle_procurementInfo


@login_required(login_url='login_page')
def vehicle_procurement_add(request, vp_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if vp_id == 0:
            form = vechicle_procurementForm()
        else:
            vehicle_procurement = Vehicle_procurementInfo.objects.get(pk=vp_id)
            form = vechicle_procurementForm(instance=vehicle_procurement)
        return render(request, "asset_mgt_app/vehicle_procurement_add.html", {'first_name': first_name,
        'user_id': user_id,'form': form})
    else:
        if vp_id == 0:
            form = vechicle_procurementForm(request.POST)
        else:
            vehicle_procurement = Vehicle_procurementInfo.objects.get(pk=vp_id)
            form = vechicle_procurementForm(request.POST, instance=vehicle_procurement)

        if form.is_valid():
            form.save(commit=False)  # Prevent automatic saving
            form.instance.save()  # Explicitly save the instance
            messages.success(request, 'Vehicle Updated Successfully')
            return redirect('/SMS/vehicle_procurement_list')
        else:
            print(form.errors)  # Debugging: Print form errors to console
            messages.error(request, 'Vehicle not Updated Successfully')

            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")
                    messages.error(request, f"Error in {field}: {error}")

        return render(request, "asset_mgt_app/vehicle_procurement_add.html", {'form': form, 'first_name': first_name})


@login_required(login_url='login_page')
def vehicle_procurement_list(request):
    first_name = request.session.get('first_name')
    context = {'vehicle_procurement_list': Vehicle_procurementInfo.objects.all(), 'first_name': first_name}
    return render(request, "asset_mgt_app/vehicle_procurement_list.html", context)

@login_required(login_url='login_page')
def vehicle_procurement_delete(request, vp_id):
    vehicle_procurement = Vehicle_procurementInfo.objects.get(pk=vp_id)
    vehicle_procurement.delete()
    return redirect('/SMS/vehicle_procurement_list')
