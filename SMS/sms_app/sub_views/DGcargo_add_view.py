from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import DGcargoaddForm
from ..models import DGcargovalueInfo
from ..sub_models.approval_status_mod import approval_status_info
from ..sub_models.gatein_mod import Gatein_info


# Add / Edit DG Cargo
@login_required(login_url='login_page')
def dg_cargo_add(request, cargo_id=0):
    first_name = request.session.get('first_name')
    wh_job_id = request.session.get('ses_gatein_id_nam')
    gatein_id = request.GET.get("gatein_id")  # catch from URL
    gatein_wh_job_id=Gatein_info.objects.get(gatein_job_no=wh_job_id).id
    dg_cargo_list =DGcargovalueInfo.objects.filter(DG_wh_job_no=wh_job_id)

    if request.method == "GET":
        if cargo_id == 0:
            form = DGcargoaddForm()
        else:
            cargo = DGcargovalueInfo.objects.get(pk=cargo_id)
            form = DGcargoaddForm(instance=cargo)
        context = {
            'form': form,
            'first_name': first_name,
            'wh_job_id': wh_job_id,
            'gatein_wh_job_id': gatein_wh_job_id,
            'gatein_id': gatein_id,
            'dg_cargo_list': dg_cargo_list,
        }
        return render(request, "asset_mgt_app/dg_cargo_add.html", context)
    else:
        if cargo_id == 0:
            form = DGcargoaddForm(request.POST)
        else:
            cargo = DGcargovalueInfo.objects.get(pk=cargo_id)
            form = DGcargoaddForm(request.POST, instance=cargo)
        if form.is_valid():
            form.save()
            # Always go back to gatein_update/<gatein_id>
        return redirect(f"/SMS/gatein_update/{gatein_wh_job_id}")


# List DG Cargo
@login_required(login_url='login_page')
def dg_cargo_list(request):
    first_name = request.session.get('first_name')
    wh_job_id = request.session.get('ses_gatein_id_nam')
    print(wh_job_id)

    dg_cargo_list =DGcargovalueInfo.objects.all()
    context = {
        'dg_cargo_list': dg_cargo_list,
        'first_name': first_name
    }
    return render(request, "asset_mgt_app/dg_cargo_list.html", context)


# Delete DG Cargo
@login_required(login_url='login_page')
def dg_cargo_delete(request, cargo_id):
    cargo = DGcargovalueInfo.objects.get(pk=cargo_id)
    cargo.delete()
    return redirect('/SMS/dg_cargo_list')

@login_required(login_url='login_page')
def dg_cargo_approval_view(request):
    first_name = request.session.get('first_name')

    # Only cargo with pending status (id=2)
    dg_cargo_list = DGcargovalueInfo.objects.filter(
        DG_wh_approval_status__id=2
    )

    context = {
        "first_name": first_name,
        "dg_cargo_list": dg_cargo_list,
        "status_list": approval_status_info.objects.all(),
    }
    return render(request, "asset_mgt_app/dg_cargo_approval.html", context)


# Update DG Cargo Approval
@login_required(login_url='login_page')
def update_dg_cargo_approval(request, cargo_id):
    wh_job_id = request.session.get('ses_gatein_id_nam')

    if request.method == "POST":
        if request.user.id not in [93, 1, 86, 7]:
            messages.error(request, "You are not authorized to update this approval.")
            return redirect("dg_cargo_approval_view")

        cargo = get_object_or_404(DGcargovalueInfo, pk=cargo_id)

        approval_status_id = request.POST.get("DG_approval_status")
        status_obj = get_object_or_404(approval_status_info, pk=approval_status_id)

        # Update DG cargo approval
        cargo.DG_wh_approval_status = status_obj
        cargo.save()


        messages.success(request, "DG Cargo approval updated successfully.")

    return redirect("dg_cargo_approval_view")
