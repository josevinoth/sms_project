from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from ..forms import PregateintruckmblForm
from ..models import Pregateintruckinfo,HighvalueInfo
from ..sub_models.gatein_mod_pre import Gatein_pre_info
from ..sub_models.vehicletype_mod import VehicletypeInfo
from ..sub_models.typeofotl_mod import TypeofotlInfo
from ..sub_models.gstexcemption_mod import GstexcemptionInfo
from ..sub_models.yesno_info_mod import YesNoInfo
from ..sub_models.storage_cross_label_mod import storagecrosslabelInfo
from django.core.paginator import Paginator


@login_required(login_url='login_page')
def gatein_pre_truck_mbl_add(request, gp_tm_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    # Fetch dropdown options
    Gatein_pre = Gatein_pre_info.objects.all()
    Vehicletype = VehicletypeInfo.objects.all()
    Typeofotl = TypeofotlInfo.objects.all()
    Gstexcemption = GstexcemptionInfo.objects.all()
    YesNo = YesNoInfo.objects.all()
    storagecrosslabel = storagecrosslabelInfo.objects.all()

    if request.method == "GET":
        if gp_tm_id == 0:
            form = PregateintruckmblForm()
        else:
            gateinpretruck = get_object_or_404(Pregateintruckinfo, pk=gp_tm_id)
            form = PregateintruckmblForm(instance=gateinpretruck)

        return render(request, "asset_mgt_app/pregateintruck_mbl_add.html", {
            'form': form,
            'first_name': first_name,
            'Gatein_pre': Gatein_pre,
            'Vehicletype': Vehicletype,
            'Typeofotl': Typeofotl,
            'Gstexcemption': Gstexcemption,
            'YesNo': YesNo,
            'storagecrosslabel': storagecrosslabel,
            'user_id': user_id,
        })

    else:
        if gp_tm_id == 0:
            form = PregateintruckmblForm(request.POST)
        else:
            gateinpretruck = get_object_or_404(Pregateintruckinfo, pk=gp_tm_id)
            form = PregateintruckmblForm(request.POST,instance=gateinpretruck)


        if form.is_valid():
            form.save()
            messages.success(request, 'Record Updated Successfully')
            return redirect('/SMS/gatein_pre_truck_mbl_add')

        else:
            messages.error(request, "Error while saving the form.")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")

        return render(request, "asset_mgt_app/pregateintruck_mbl_add.html", {
        'form': form,
        'first_name': first_name,
        'Gatein_pre': Gatein_pre,
        'Vehicletype': Vehicletype,
        'Typeofotl': Typeofotl,
        'Gstexcemption': Gstexcemption,
        'YesNo': YesNo,
        'storagecrosslabel': storagecrosslabel,
        'user_id': user_id,
    })


@login_required(login_url='login_page')
def gatein_pre_truck_mbl_list(request):
    first_name = request.session.get('first_name')
    gpm_id = request.session.get('ses_gpm_id')
    gatein_pre = Pregateintruckinfo.objects.all()
    page_number = request.GET.get('page')
    paginator = Paginator(gatein_pre, 10)
    page_obj = paginator.get_page(page_number)
    context = {
        # 'Gatein_pre_list' : Gatein_pre_info.objects.all(),
        'first_name': first_name,
        'page_obj': page_obj,
    }
    return render(request, "asset_mgt_app/pregateintruck_mbl_list.html", {'first_name': first_name,'page_obj': page_obj,})


@login_required(login_url='login_page')
def gatein_pre_truck_mbl_delete(request, gp_tm_id):
    gateinpretruck = Pregateintruckinfo.objects.get(pk=gp_tm_id)
    gateinpretruck.delete()
    return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login_page')
def gatein_pre_truck_mbl_cancel(request,gpm_id=0):
    gpm_id = request.session['ses_gpm_id']
    return redirect('/SMS/gatein_pre_mbl_edit/' + str(gpm_id))
