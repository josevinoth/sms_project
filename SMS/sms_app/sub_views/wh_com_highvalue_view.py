from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from ..models import Pregateintruckinfo, approval_status_info


@login_required(login_url='login_page')
def pregatein_approval_view(request):
    # Filter based on conditions
    pregatein_list = Pregateintruckinfo.objects.select_related(
        'pregatein_number',
        'pregatein_commodity',
        'pregatein_approval_status'
    ).filter(
        ( Q(pregatein_commodity__id__gte=11, pregatein_commodity__id__lte=14) |
        Q(pregatein_invoice_value__gt=250000) ) & Q(pregatein_approval_status__id=2)
    )

    return render(request, "asset_mgt_app/pregatein_approval1.html", {
        "pregatein_list": pregatein_list,
        "status_list": approval_status_info.objects.all()
    })

@login_required
def update_pregatein_approval(request, pregatein_id):
    if request.method == "POST":
        # ✅ Only users 93, 1, 86 can update
        if request.user.id not in [93, 1, 86]:
            messages.error(request, "You are not authorized to update this approval.")
            return redirect("pregatein_approval_view")

        pregatein = get_object_or_404(Pregateintruckinfo, pk=pregatein_id)

        # ✅ If invoice value > 250000 → force status to ID=3
        if pregatein.pregatein_invoice_value > 250000:
            pregatein.pregatein_approval_status_id = 3
            messages.success(request, "Pregatein sent for Sony approval .")
        else:
            # ✅ Normal approval flow
            approval_status_id = request.POST.get("pregatein_approval_status")
            status_obj = get_object_or_404(approval_status_info, pk=approval_status_id)
            pregatein.pregatein_approval_status = status_obj
            messages.success(request, "Pregatein approval updated.")

        pregatein.save()

    return redirect("pregatein_approval_view")


@login_required(login_url='login_page')
def pregatein_approval2_view(request):
    # ✅ Show only records with status = 3
    pregatein_list = Pregateintruckinfo.objects.select_related(
        'pregatein_number',
        'pregatein_commodity',
        'pregatein_approval_status'
    ).filter(pregatein_approval_status__id=3)

    return render(request, "asset_mgt_app/pregatein_approval2.html", {
        "pregatein_list": pregatein_list,
        "status_list": approval_status_info.objects.all()
    })


@login_required(login_url='login_page')
def update_pregatein_approval2(request, pregatein_id):
    if request.method == "POST":
        # ✅ Only users with ID in [93, 1, 2, 36] can update
        allowed_users = [93, 1, 2, 36]
        if request.user.id not in allowed_users:
            messages.error(request, "You are not authorized to update this approval.")
            return redirect("pregatein_approval2_view")

        pregatein = get_object_or_404(Pregateintruckinfo, pk=pregatein_id)

        approval_status_id = request.POST.get("pregatein_approval_status")
        status_obj = get_object_or_404(approval_status_info, pk=approval_status_id)

        pregatein.pregatein_approval_status = status_obj
        pregatein.save()

        messages.success(request, "Pregatein approved by Sony .")

    return redirect("pregatein_approval2_view")


