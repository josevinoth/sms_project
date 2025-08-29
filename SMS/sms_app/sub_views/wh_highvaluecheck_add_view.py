from django.contrib.auth.decorators import login_required
from ..forms import HighvalueForm
from ..models import HighvalueInfo
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from ..sub_models.gatein_mod_pre import Gatein_pre_info

@login_required(login_url='login_page')
def highvalue_add(request, high_value_id=0):
    first_name = request.session.get('first_name')
    pregateintruck_id = request.session.get('ses_pregateintruck_id')
    gatein_num_id = request.session.get('gatein_num_id')  # this is Gatein_pre_info.id
    print("Gatein Num ID:", gatein_num_id, "Pregatein ID:", pregateintruck_id)

    if request.method == "GET":
        if high_value_id == 0:
            form = HighvalueForm()
        else:
            high = get_object_or_404(HighvalueInfo, pk=high_value_id)
            # Sync session with this record’s gatein
            request.session['ses_pregateintruck_id'] = high.hc_pregatein_number.id
            form = HighvalueForm(instance=high)

        context = {
            'form': form,
            'first_name': first_name,
            'pregateintruck_id': pregateintruck_id,
            'gatein_num_id': gatein_num_id,
        }
        return render(request, "asset_mgt_app/wh_highvaluecheck_add.html", context)

    else:
        if high_value_id == 0:
            form = HighvalueForm(request.POST)
        else:
            high = get_object_or_404(HighvalueInfo, pk=high_value_id)
            form = HighvalueForm(request.POST, instance=high)

        if form.is_valid():
            try:
                # gatein_num_id is the PK → filter by id
                gatein_obj = Gatein_pre_info.objects.get(id=gatein_num_id)
            except Gatein_pre_info.DoesNotExist:
                messages.error(request, f"No Gatein record found with ID {gatein_num_id}")
                return redirect(request.META.get('HTTP_REFERER', '/'))

            obj = form.save(commit=False)
            obj.hc_pregatein_number = gatein_obj
            obj.save()

            if high_value_id == 0:
                messages.success(request, 'Record Saved Successfully')
            else:
                messages.success(request, 'Record Updated Successfully')
        else:
            messages.error(request, 'Error: Please correct the errors below.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")

        return redirect(request.META.get('HTTP_REFERER', '/'))

# List bay
@login_required(login_url='login_page')
def highvalue_list(request):
    first_name = request.session.get('first_name')
    pregateintruck_id = request.session.get('ses_pregateintruck_id')
    high_list = HighvalueInfo.objects.filter(hc_pregatein_number=pregateintruck_id)
    context = {'high_list': high_list, 'first_name': first_name}
    return render(request, "asset_mgt_app/wh_highvaluecheck_list.html", context)

#Delete bay
@login_required(login_url='login_page')
def highvalue_delete(request,high_value_id):
    high = HighvalueInfo.objects.get(pk=high_value_id)
    high.delete()
    return redirect('/SMS/high_value_list')

@login_required(login_url='login_page')
def highvalue_cancel(request, pregateintruck_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    pregateintruck_id = request.session.get('ses_pregateintruck_id')
    return redirect(f'/SMS/pregateintruck_update/{pregateintruck_id}')

