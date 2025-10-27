from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from ..models import HighvalueInfo, approval_status_info


# 🔹 First approval view
@login_required(login_url='login_page')
def highvalue_approval_view(request):
    # Filter: commodity 11–14 OR value > 250000 AND pending approval
    highvalue_list = HighvalueInfo.objects.select_related(
        "hc_pregatein_number",
        "hc_commodity",
        "hc_approval_status"
    ).filter(
        (Q(hc_commodity__id__gte=11, hc_commodity__id__lte=14) | Q(hc_value__gt=2500000))
        & Q(hc_approval_status__id=2)  # pending
    )

    return render(request, "asset_mgt_app/pregatein_approval1.html", {
        "highvalue_list": highvalue_list,
        "status_list": approval_status_info.objects.all(),
    })


@login_required
def update_highvalue_approval(request, highvalue_id):
    if request.method == "POST":
        # Only certain users can approve
        if request.user.id not in [93, 1, 86, 89,137]:
            messages.error(request, "You are not authorized to update this approval.")
            return redirect("highvalue_approval_view")

        highvalue = get_object_or_404(HighvalueInfo, pk=highvalue_id)

        # Force Sony approval if > 250000
        if highvalue.hc_value > 2500000:
            highvalue.hc_approval_status_id = 3
            highvalue.hc_first_approval_id = 3
            messages.success(request, "Highvalue sent for Sony approval.")
        else:
            approval_status_id = request.POST.get("hc_approval_status")
            status_obj = get_object_or_404(approval_status_info, pk=approval_status_id)
            highvalue.hc_approval_status = status_obj
            highvalue.hc_first_approval = status_obj
            messages.success(request, "Highvalue approval updated.")

        highvalue.save()

    return redirect("highvalue_approval_view")


# 🔹 Second approval view
@login_required(login_url='login_page')
def highvalue_approval2_view(request):
    highvalue_list = HighvalueInfo.objects.select_related(
        "hc_pregatein_number",
        "hc_commodity",
        "hc_approval_status"
    ).filter(hc_approval_status__id=3)

    return render(request, "asset_mgt_app/pregatein_approval2.html", {
        "highvalue_list": highvalue_list,
        "status_list": approval_status_info.objects.all(),
    })


@login_required
def update_highvalue_approval2(request, highvalue_id):
    if request.method == "POST":
        # Sony approvers only
        allowed_users = [93, 1, 57,86]
        if request.user.id not in allowed_users:
            messages.error(request, "You are not authorized to update this approval.")
            return redirect("highvalue_approval2_view")

        highvalue = get_object_or_404(HighvalueInfo, pk=highvalue_id)

        approval_status_id = request.POST.get("hc_approval_status")
        status_obj = get_object_or_404(approval_status_info, pk=approval_status_id)

        highvalue.hc_approval_status = status_obj
        highvalue.hc_second_approval = status_obj
        highvalue.save()

        messages.success(request, "Highvalue approved by Prem Sundar.")

    return redirect("highvalue_approval2_view")
