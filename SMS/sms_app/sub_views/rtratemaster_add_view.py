from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..forms import RtratemasteraddForm
from ..models import RtratemasterInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def rtratemaster_add(request,rtratemaster_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if rtratemaster_id == 0:
            form = RtratemasteraddForm()
        else:
            rtratemaster = RtratemasterInfo.objects.get(pk=rtratemaster_id)
            form = RtratemasteraddForm(instance=rtratemaster)
        return render(request, "asset_mgt_app/rtratemaster_add.html", {'form': form,'first_name': first_name,'user_id':user_id,})
    else:
        form = RtratemasteraddForm(request.POST)
        if form.is_valid():
            # Check for duplicates before saving
            ro_fromlocation = form.cleaned_data['ro_fromlocation']
            ro_tolocation = form.cleaned_data['ro_tolocation']
            ro_vehicletype = form.cleaned_data['ro_vehicletype']
            ro_customer = form.cleaned_data['ro_customer']
            ro_customerdepartment = form.cleaned_data['ro_customerdepartment']
            ro_vehiclecategory = form.cleaned_data['ro_vehiclecategory']
            ro_touchpoint = form.cleaned_data['ro_touchpoint']
            ro_touchpoint2 = form.cleaned_data['ro_touchpoint2']
            ro_touchpoint3 = form.cleaned_data['ro_touchpoint3']
            ro_touchpoint4 = form.cleaned_data['ro_touchpoint4']
            if not RtratemasterInfo.objects.filter(ro_fromlocation=ro_fromlocation,ro_tolocation=ro_tolocation,ro_vehicletype=ro_vehicletype,ro_customer=ro_customer,ro_customerdepartment=ro_customerdepartment,ro_vehiclecategory=ro_vehiclecategory,ro_touchpoint=ro_touchpoint,ro_touchpoint2=ro_touchpoint2,ro_touchpoint3=ro_touchpoint3,ro_touchpoint4=ro_touchpoint4).exclude(id=rtratemaster_id).exists():
                if rtratemaster_id == 0:
                    new_rate = form.save()
                    print("Transport Route Rate master Form saved")
                    messages.success(request, 'Record Updated Successfully')
                    url = new_rate.get_absolute_url_trans_route_ratemaster()
                    # return redirect(url)
                    return redirect('/SMS/rtratemaster_list')
                else:
                    rtratemaster = RtratemasterInfo.objects.get(pk=rtratemaster_id)
                    form = RtratemasteraddForm(request.POST, instance=rtratemaster)
                    form.save()
                    print("Transport Route Rate master Form saved")
                    messages.success(request, 'Record Updated Successfully')
                    return redirect(request.META['HTTP_REFERER'])
            else:
                print("Transport Route Rate master Form not saved - Duplicate found")
                messages.error(request, 'Duplicate Record Found. Please enter a Unique Values.')
                return redirect(request.META['HTTP_REFERER'])
        else:
            rtratemaster = RtratemasterInfo.objects.get(pk=rtratemaster_id)
            form = RtratemasteraddForm(request.POST,instance=rtratemaster)
            if form.is_valid():
                form.save()
                print("Transport Route Rate master Form saved")
                messages.success(request, 'Record Updated Successfully')
                # return redirect(request.META['HTTP_REFERER'])
                return redirect('/SMS/rtratemaster_list')
            else:
                print("Transport Route Rate Form not saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
                return redirect(request.META['HTTP_REFERER'])

# List rtratemaster
@login_required(login_url='login_page')
def rtratemaster_list(request):
    first_name = request.session.get('first_name')
    context = {'rtratemaster_list' : RtratemasterInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/rtratemaster_list.html",context)

#Delete rtratemaster
@login_required(login_url='login_page')
def rtratemaster_delete(request,rtratemaster_id):
    rtratemaster = RtratemasterInfo.objects.get(pk=rtratemaster_id)
    rtratemaster.delete()
    return redirect('/SMS/rtratemaster_list')