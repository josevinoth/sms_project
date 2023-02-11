from django.contrib.auth.decorators import login_required
from ..forms import InsuranceaddForm
from ..models import Insurance_Info
from django.shortcuts import render, redirect

# List Insurance
@login_required(login_url='login_page')
def insurance_list(request):
    first_name = request.session.get('first_name')
    context = {'insurance_list': Insurance_Info.objects.all(),'first_name': first_name}
    return render(request, "asset_mgt_app/insurance_list.html", context)


# Add Insurance
@login_required(login_url='login_page')
def insurance_add(request, insurance_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if insurance_id == 0:
            form = InsuranceaddForm()
        else:
            insuranceinfo = Insurance_Info.objects.get(pk=insurance_id)
            form = InsuranceaddForm(instance=insuranceinfo)
        context={
            'user_id':user_id,
            'form': form,
            'first_name': first_name
        }
        return render(request, "asset_mgt_app/insurance_add.html", context)
    else:
        if insurance_id == 0:
            form = InsuranceaddForm(request.POST)
        else:
            insuranceinfo = Insurance_Info.objects.get(pk=insurance_id)
            form = InsuranceaddForm(request.POST, instance=insuranceinfo)
        if form.is_valid():
            form.save()
            print("Main Form Saved")
        else:
            print("Main Form Not saved")
        return redirect('/SMS/insurance_list')


# Delete Insurance
@login_required(login_url='login_page')
def insurance_delete(request, service_id):
    insuranceinfo = Insurance_Info.objects.get(pk=service_id)
    insuranceinfo.delete()
    return redirect('/SMS/insurance_list')