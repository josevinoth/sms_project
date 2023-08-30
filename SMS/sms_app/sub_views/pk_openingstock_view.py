from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from ..forms import PkopeningstockForm
from ..models import PkopeningstockInfo
from django.shortcuts import render, redirect
from random import randint
from django.contrib import messages

@login_required(login_url='login_page')
def openingstock_add(request,openingstock_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if openingstock_id == 0:
            form = PkopeningstockForm()
        else:
            openingstock=PkopeningstockInfo.objects.get(pk=openingstock_id)
            form = PkopeningstockForm(instance=openingstock)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                }
        return render(request, "asset_mgt_app/pk_openingstock_add.html", context)
    else:
        if openingstock_id == 0:
            form = PkopeningstockForm(request.POST)
            if form.is_valid():
                # Generate Random Opening Stock number
                try:
                    last_id = PkopeningstockInfo.objects.latest('id').id
                    openingstock_num_next = str('openstk_') + str(
                        int(((PkopeningstockInfo.objects.get(id=last_id)).os_openingstock_num).replace('openstk_','')) + 1)
                except ObjectDoesNotExist:
                    openingstock_num_next = str('openstk_') + str(randint(10000, 99999))
                form.save()
                print("openingstock Form is Valid")
                last_id = (PkopeningstockInfo.objects.latest('id')).id
                PkopeningstockInfo.objects.filter(id=last_id).update(os_openingstock_num=openingstock_num_next)
                messages.success(request, 'Record Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
                # return redirect('/SMS/openingstock_update/')
            else:
                print("openingstock Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            openingstock = PkopeningstockInfo.objects.get(pk=openingstock_id)
            form = PkopeningstockForm(request.POST,instance=openingstock)
            if form.is_valid():
                form.save()
                print("openingstock Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("openingstock Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

# List openingstock
@login_required(login_url='login_page')
def openingstock_list(request):
    first_name = request.session.get('first_name')
    context = {'openingstock_list' : PkopeningstockInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_openingstock_list.html",context)

#Delete openingstock
@login_required(login_url='login_page')
def openingstock_delete(request,openingstock_id):
    openingstock = PkopeningstockInfo.objects.get(pk=openingstock_id)
    openingstock.delete()
    return redirect('/SMS/openingstock_list')