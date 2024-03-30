from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from ..forms import WhratemasteraddForm
from ..models import WhratemasterInfo
from django.shortcuts import render, redirect

# List whratemaster
@login_required(login_url='login_page')
def whratemaster_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    whratemaster_list= (WhratemasterInfo.objects.all()).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(whratemaster_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
                'whratemaster_list':whratemaster_list,
                'page_obj':page_obj,
                'first_name': first_name,
                'user_id':user_id,
            }
    return render(request, "asset_mgt_app/whratemaster_list.html", context)


# Add whratemaster
@login_required(login_url='login_page')
def whratemaster_add(request, whratemaster_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print('user_id',user_id)
    if request.method == "GET":
        if whratemaster_id == 0:
            form = WhratemasteraddForm()
        else:
            whratemasterinfo = WhratemasterInfo.objects.get(pk=whratemaster_id)
            form = WhratemasteraddForm(instance=whratemasterinfo)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
        }
        return render(request, "asset_mgt_app/whratemaster_add.html", context)
    else:
        form = WhratemasteraddForm(request.POST)
        if form.is_valid():
            # Check for duplicates before saving
            whrm_customer_name = form.cleaned_data['whrm_customer_name']
            whrm_businessmodel = form.cleaned_data['whrm_businessmodel']
            whrm_charge_type = form.cleaned_data['whrm_charge_type']
            whrm_max_wt = form.cleaned_data['whrm_max_wt']
            whrm_min_wt = form.cleaned_data['whrm_min_wt']
            whrm_min_area = form.cleaned_data['whrm_min_area']
            whrm_max_area = form.cleaned_data['whrm_max_area']
            whrm_rate = form.cleaned_data['whrm_rate']
            whrm_description = form.cleaned_data['whrm_description']
            whrm_vehicle_type = form.cleaned_data['whrm_vehicle_type']
            print('whrm_customer_name',whrm_customer_name)
            if not WhratemasterInfo.objects.filter(whrm_customer_name=whrm_customer_name,whrm_businessmodel=whrm_businessmodel,whrm_charge_type=whrm_charge_type,whrm_max_wt=whrm_max_wt,whrm_min_wt=whrm_min_wt,whrm_min_area=whrm_min_area,whrm_max_area=whrm_max_area,whrm_rate=whrm_rate,whrm_description=whrm_description,whrm_vehicle_type=whrm_vehicle_type).exclude(id=whratemaster_id).exists():
                if whratemaster_id == 0:
                    print("Inside post add")
                    form = WhratemasteraddForm(request.POST)
                    form.save()
                    print("Warehouse Rate master form saved")
                    messages.success(request, 'Record Updated Successfully')
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    print("Inside post edit")
                    whratemasterinfo = WhratemasterInfo.objects.get(pk=whratemaster_id)
                    form = WhratemasteraddForm(request.POST, instance=whratemasterinfo)
                    form.save()
                    print("Warehouse Rate master form saved")
                    messages.success(request, 'Record Updated Successfully')
                    return redirect(request.META['HTTP_REFERER'])
            else:
                print("Main form not saved")
                messages.error(request, 'Similar record exist. Please enter Unique values.')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("PkpurchaseorderInfo Form is Not Valid")
            messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/whratemaster_list')


# Delete whratemaster
@login_required(login_url='login_page')
def whratemaster_delete(request, whratemaster_id):
    whratemasterinfo = WhratemasterInfo.objects.get(pk=whratemaster_id)
    whratemasterinfo.delete()
    return redirect('/SMS/whratemaster_list')