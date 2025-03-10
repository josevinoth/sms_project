from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import gateinpre_mblForm
from ..models import gateinpre_mblInfo
from ..sub_models.location_info_mod import Location_info
from ..sub_models.status_list_mod import StatusList

@login_required(login_url='login_page')
def gatein_pre_mbl_add(request, gpm_id=0):
    first_name = request.session.get('first_name')

    # Fetch dropdown options
    Locations = Location_info.objects.all()
    Status = StatusList.objects.all()


    if request.method == "GET":
        if gpm_id == 0:
            form = gateinpre_mblForm()
        else:
            gateinpre = gateinpre_mblInfo.objects.get(pk=gpm_id)
            form = gateinpre_mblForm(instance=gateinpre)

        return render(request, "asset_mgt_app/gatein_pre_mbl_add.html", {
            'form': form,
            'first_name': first_name,
            'Location': Locations,
            'Status': Status,

        })

    else:
        if gpm_id == 0:
            form = gateinpre_mblForm(request.POST, request.FILES)
        else:
            gateinpre = get_object_or_404(gateinpre_mblInfo, pk=gpm_id)
            form = gateinpre_mblForm(request.POST, request.FILES, instance=gateinpre)

        if form.is_valid():
            form.save()
            messages.success(request, 'Record Saved Successfully')
            return redirect('/SMS/gatein_pre_mbl_add')
            # Display form errors
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error in {field}: {error}")
                messages.error(request, f"Error in {field}: {error}")

    return render(request, "asset_mgt_app/gatein_pre_mbl_add.html", {
        'form': form,
        'first_name': first_name,
        'Location': Locations,
        'Status': Status,
    })

@login_required(login_url='login_page')
def gatein_pre_mbl_list(request):
    gatein_pre = gateinpre_mblInfo.objects.all()
    return render(request, "asset_mgt_app/gatein_pre_mbl_list.html", {"gatein_pre": gatein_pre})

@login_required(login_url='login_page')
def gatein_pre_mbl_delete(request, gpm_id):
    gateinpre = gateinpre_mblInfo.objects.get(pk=gpm_id)
    gateinpre.delete()
    return redirect('/SMS/gatein_pre_mbl_list')
