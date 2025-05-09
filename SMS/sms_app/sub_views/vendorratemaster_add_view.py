from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..forms import VendorratemasteraddForm
from ..models import VendorratemasterInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def vendorratemaster_add(request,vendorratemaster_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if vendorratemaster_id == 0:
            form = VendorratemasteraddForm()
        else:
            vendorratemaster = VendorratemasterInfo.objects.get(pk=vendorratemaster_id)
            form = VendorratemasteraddForm(instance=vendorratemaster)
        return render(request, "asset_mgt_app/vendorratemaster_add.html", {'form': form,'first_name': first_name,'user_id':user_id,})
    else:
        form = VendorratemasteraddForm(request.POST)
        if form.is_valid():
            # Check for duplicates before saving
            vr_fromlocation = form.cleaned_data['vr_fromlocation']
            vr_tolocation = form.cleaned_data['vr_tolocation']
            vr_vehicletype = form.cleaned_data['vr_vehicletype']
            vr_vendor = form.cleaned_data['vr_vendor']
            vr_vehiclecategory = form.cleaned_data['vr_vehiclecategory']
            vr_touchpoint = form.cleaned_data['vr_touchpoint']
            vr_touchpoint2 = form.cleaned_data['vr_touchpoint2']
            vr_touchpoint3 = form.cleaned_data['vr_touchpoint3']
            vr_touchpoint4 = form.cleaned_data['vr_touchpoint4']
            if not VendorratemasterInfo.objects.filter(vr_fromlocation=vr_fromlocation,vr_tolocation=vr_tolocation,vr_vehicletype=vr_vehicletype,vr_vendor=vr_vendor,vr_vehiclecategory=vr_vehiclecategory,vr_touchpoint=vr_touchpoint,vr_touchpoint2=vr_touchpoint2,vr_touchpoint3=vr_touchpoint3,vr_touchpoint4=vr_touchpoint4).exclude(id=vendorratemaster_id).exists():
                if vendorratemaster_id == 0:
                    new_rate = form.save()
                    print("Vendor Route Rate master Form saved")
                    messages.success(request, 'Record Updated Successfully')
                    #url = new_rate.get_absolute_url_trans_route_ratemaster()
                    # return redirect(url)
                    return redirect('/SMS/vendorratemaster_list')
                else:
                    vendorratemaster = VendorratemasterInfo.objects.get(pk=vendorratemaster_id)
                    form = VendorratemasteraddForm(request.POST, instance=vendorratemaster)
                    form.save()
                    print("Transport Route Rate master Form saved")
                    messages.success(request, 'Record Updated Successfully')
                    return redirect(request.META['HTTP_REFERER'])
            else:
                print("Vendor Route Rate master Form not saved - Duplicate found")
                messages.error(request, 'Duplicate Record Found. Please enter a Unique Values.')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("Vendor Route Rate Form not saved")
            messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
            return redirect(request.META['HTTP_REFERER'])

# List rtratemaster
@login_required(login_url='login_page')
def vendorratemaster_list(request):
    first_name = request.session.get('first_name')
    context = {'vendorratemaster_list' : VendorratemasterInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/vendorratemaster_list.html",context)

#Delete vendorratemaster
@login_required(login_url='login_page')
def vendorratemaster_delete(request,vendorratemaster_id):
    vendorratemaster = VendorratemasterInfo.objects.get(pk=vendorratemaster_id)
    vendorratemaster.delete()
    return redirect('/SMS/vendorratemaster_list')