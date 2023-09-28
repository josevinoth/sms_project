from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from ..forms import FuelfillingForm
from ..models import Fuelfillinginfo
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required(login_url='login_page')
def fuelfilling_add(request,fuelfilling_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if fuelfilling_id == 0:
            form = FuelfillingForm()
        else:
            fuelfilling=Fuelfillinginfo.objects.get(pk=fuelfilling_id)
            form = FuelfillingForm(instance=fuelfilling)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                }
        return render(request, "asset_mgt_app/fuelfilling_add.html", context)
    else:
        if fuelfilling_id == 0:
            form = FuelfillingForm(request.POST)
            if form.is_valid():
                form.save()
                print("Fuelfillinginfo Form is Valid")
                last_id = (Fuelfillinginfo.objects.latest('id')).id
                messages.success(request, 'Record Updated Successfully')
                # return redirect(request.META['HTTP_REFERER'])
                return redirect('/SMS/fuelfilling_update/' + str(last_id))
            else:
                print("Fuelfillinginfo Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            fuelfilling = Fuelfillinginfo.objects.get(pk=fuelfilling_id)
            form = FuelfillingForm(request.POST,instance=fuelfilling)
            if form.is_valid():
                form.save()
                print("FuelfillingForm Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("FuelfillingForm Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

# List fuelfilling
@login_required(login_url='login_page')
def fuelfilling_list(request):
    first_name = request.session.get('first_name')
    context = {'fuelfilling_list' : Fuelfillinginfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/fuelfilling_list.html",context)

#Delete fuelfilling
@login_required(login_url='login_page')
def fuelfilling_delete(request,fuelfilling_id):
    fuelfilling = Fuelfillinginfo.objects.get(pk=fuelfilling_id)
    fuelfilling.delete()
    return redirect('/SMS/fuelfilling_list')