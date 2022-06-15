from django.shortcuts import render, redirect
from ..forms import GateinaddForm
from django.contrib.auth.decorators import login_required
from ..models import Gatein_info

# Main page
@login_required(login_url='login_page')
def gatein_add(request, gatein_id=0):
    first_name = request.session.get('first_name')
    gatein_form = GateinaddForm()
    if gatein_form.is_valid():
        gatein_form.save()
    context = {
        'first_name': first_name,
        'gatein_form': gatein_form,
    }
    return render(request, "asset_mgt_app/wh_job_add.html", context)


# Add gatein
@login_required(login_url='login_page')
def wh_job_add(request, gatein_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if gatein_id == 0:
            gatein_form = GateinaddForm()
            context = {
                'gatein_form': gatein_form
            }
        else:
            gatein_info = Gatein_info.objects.get(pk=gatein_id)
            gatein_form = GateinaddForm(instance=gatein_info)
            context={
                'gatein_form': gatein_form,
                'first_name': first_name,
            }
        return render(request, "asset_mgt_app/wh_job_add.html", context)
    else:
        if gatein_id == 0:
            gatein_form = GateinaddForm(request.POST)
        else:
           gatein_info = Gatein_info.objects.get(pk=gatein_id)
           gatein_form = GateinaddForm(request.POST, instance=gatein_info)
        if gatein_form.is_valid():
            gatein_form.save()
        return redirect('/SMS/wh_job_add')
