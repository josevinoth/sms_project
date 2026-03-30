from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from ..forms import ChargeMasterForm
from ..sub_models.charge_master_mod import ChargeMasterInfo

@login_required(login_url='login_page')
def charge_master_add(request, cm_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    
    if request.method == "GET":
        if cm_id == 0:
            form = ChargeMasterForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
            }
        else:
            charge = ChargeMasterInfo.objects.get(pk=cm_id)
            form = ChargeMasterForm(instance=charge)
            context = {
                'form': form,
                'first_name': first_name,
                'cm_id': cm_id,
            }
        return render(request, "asset_mgt_app/charge_master_add.html", context)

    else:
        if cm_id == 0:
            form = ChargeMasterForm(request.POST)
        else:
            charge = ChargeMasterInfo.objects.get(pk=cm_id)
            form = ChargeMasterForm(request.POST, instance=charge)
        
        if form.is_valid():
            form.save()
            if cm_id == 0:
                messages.success(request, 'Charge Master Record Saved Successfully')
            else:
                messages.success(request, 'Charge Master Record Updated Successfully')
            return redirect('charge_master_list')
        else:
            messages.error(request, 'Error: Please correct the errors below.')
            context = {
                'form': form,
                'first_name': first_name,
                'cm_id': cm_id,
            }
            return render(request, "asset_mgt_app/charge_master_add.html", context)

@login_required(login_url='login_page')
def charge_master_list(request):
    first_name = request.session.get('first_name')
    charge_list = ChargeMasterInfo.objects.all()
    context = {
        'charge_list': charge_list,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/charge_master_list.html", context)

@login_required(login_url='login_page')
def charge_master_delete(request, cm_id):
    charge = ChargeMasterInfo.objects.get(pk=cm_id)
    charge.delete()
    messages.success(request, 'Charge Master Record deleted successfully.')
    return redirect('charge_master_list')
