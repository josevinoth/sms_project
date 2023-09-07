from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from ..forms import PkcostingForm
from ..models import PkcostingInfo
from django.shortcuts import render, redirect
from random import randint
from django.contrib import messages

@login_required(login_url='login_page')
def costing_add(request,costing_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    na_assessment_num_id = request.session.get('na_assessment_id')
    if request.method == "GET":
        if costing_id == 0:
            form = PkcostingForm()
        else:
            costing=PkcostingInfo.objects.get(pk=costing_id)
            form = PkcostingForm(instance=costing)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'na_assessment_num_id': na_assessment_num_id,
                }
        return render(request, "asset_mgt_app/pk_costing_add.html", context)
    else:
        if costing_id == 0:
            form = PkcostingForm(request.POST)
            if form.is_valid():
                # # Generate Random Opening Stock number
                # try:
                #     last_id = PkcostingInfo.objects.latest('id').id
                #     costing_num_next = str('OS_') + str(
                #         int(((PkcostingInfo.objects.get(id=last_id)).os_stock_number).replace('OS_','')) + 1)
                # except ObjectDoesNotExist:
                #     costing_num_next = str('OS_') + str(1000000)
                form.save()
                print("costing Form is Valid")
                last_id = (PkcostingInfo.objects.latest('id')).id
                # PkcostingInfo.objects.filter(id=last_id).update(os_stock_number=costing_num_next)
                messages.success(request, 'Record Updated Successfully')
                # return redirect(request.META['HTTP_REFERER'])
                return redirect('/SMS/costing_update/'+str(last_id))
            else:
                print("costing Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            costing = PkcostingInfo.objects.get(pk=costing_id)
            form = PkcostingForm(request.POST,instance=costing)
            if form.is_valid():
                form.save()
                print("costing Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("costing Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

# List costing
@login_required(login_url='login_page')
def costing_list(request):
    first_name = request.session.get('first_name')
    context = {'costing_list' : PkcostingInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_costing_list.html",context)

#Delete costing
@login_required(login_url='login_page')
def costing_delete(request,costing_id):
    costing = PkcostingInfo.objects.get(pk=costing_id)
    costing.delete()
    return redirect('/SMS/costing_list')