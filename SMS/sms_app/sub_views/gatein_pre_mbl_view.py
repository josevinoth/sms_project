from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from ..models import Gatein_pre_info,Pregateintruckinfo
from ..sub_models.location_info_mod import Location_info
from ..sub_models.status_list_mod import StatusList
from django.core.paginator import Paginator



@login_required(login_url='login_page')
def gatein_pre_mbl_add(request, gpm_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    page_obj = Pregateintruckinfo.objects.filter(pregatein_number=gpm_id)
    # Fetch dropdown options
    Locations = Location_info.objects.all()
    Status = StatusList.objects.all()

    if request.method == "GET":
        if gpm_id == 0:
            # Auto-generate next Gatein Number
            latest_gatein = Gatein_pre_info.objects.order_by('-id').values_list('id', flat=True).first()
            next_gatein_number = 2000000 + latest_gatein

            form = gateinpre_mblForm(initial={'gatein_pre_number': next_gatein_number})
        else:
            gateinpre = get_object_or_404(Gatein_pre_info, pk=gpm_id)
            form = gateinpre_mblForm(instance=gateinpre)
            page_obj = Pregateintruckinfo.objects.filter(pregatein_number=gpm_id)
            request.session['ses_gpm_id'] = gpm_id

        return render(request, "asset_mgt_app/gatein_pre_mbl_add.html", {
            'form': form,
            'first_name': first_name,
            'Location': Locations,
            'Status': Status,
            'user_id': user_id,
            'page_obj': page_obj,
        })

    else:
        if gpm_id == 0:
            # Assign auto-generated Gatein Number before saving
            latest_gatein = Gatein_pre_info.objects.order_by('-id').values_list('id', flat=True).first()
            next_gatein_number = 2000000 + latest_gatein

            form = gateinpre_mblForm(request.POST, request.FILES)
            if form.is_valid():
                gateinpre = form.save(commit=False)
                gateinpre.gatein_pre_number = next_gatein_number  # Assign generated number
                gateinpre.save()
                messages.success(request, 'Record Saved Successfully')
                return redirect('/SMS/gatein_pre_mbl_add')
        else:
            gateinpre = get_object_or_404(Gatein_pre_info, pk=gpm_id)
            form = gateinpre_mblForm(request.POST, request.FILES, instance=gateinpre)

            if form.is_valid():
                form.save()
                messages.success(request, 'Record Updated Successfully')
                return redirect('/SMS/gatein_pre_mbl_add')

    return render(request, "asset_mgt_app/gatein_pre_mbl_add.html", {
        'form': form,
        'first_name': first_name,
        'Location': Locations,
        'Status': Status,
        'page_obj': page_obj,
    })


@login_required(login_url='login_page')
def gatein_pre_mbl_list(request):
    first_name = request.session.get('first_name')
    gatein_pre = Gatein_pre_info.objects.all()
    page_number = request.GET.get('page')
    paginator = Paginator(gatein_pre, 20)
    page_obj = paginator.get_page(page_number)
    context = {
        # 'Gatein_pre_list' : Gatein_pre_info.objects.all(),
        'first_name': first_name,
        'page_obj': page_obj,
    }
    return render(request, "asset_mgt_app/gatein_pre_mbl_list.html", {'first_name': first_name,'page_obj': page_obj,})

@login_required(login_url='login_page')
def gatein_pre_mbl_delete(request, gpm_id):
    gateinpre = Gatein_pre_info.objects.get(pk=gpm_id)
    gateinpre.delete()
    return redirect('/SMS/gatein_pre_mbl_list')
