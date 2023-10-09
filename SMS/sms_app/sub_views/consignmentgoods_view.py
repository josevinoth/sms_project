import json
from django.contrib.auth.decorators import login_required
from ..forms import ConsignmentgoodsaddForm
from ..models import ConsignmentgoodsInfo,ConsignmentdetailInfo
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

@login_required(login_url='login_page')
def consignmentgoods_add(request,consignmentgoods_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if consignmentgoods_id == 0:
            form = ConsignmentgoodsaddForm()
        else:
            consignmentgoods=ConsignmentgoodsInfo.objects.get(pk=consignmentgoods_id)
            form = ConsignmentgoodsaddForm(instance=consignmentgoods)
        consignmentgoods_list = ConsignmentgoodsInfo.objects.all()
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'consignmentgoods_list': consignmentgoods_list,
                }
        return render(request, "asset_mgt_app/consignmentgoods_add.html", context)
    else:
        if consignmentgoods_id == 0:
            form = ConsignmentgoodsaddForm(request.POST)
            if form.is_valid():
                form.save()
                print("consignmentgoods Form is Valid")
                last_id = (ConsignmentgoodsInfo.objects.latest('id')).id
                messages.success(request, 'Record Updated Successfully')
                return redirect('/SMS/consignmentgoods_update/'+str(last_id))
            else:
                print("consignmentgoods Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            consignmentgoods = ConsignmentgoodsInfo.objects.get(pk=consignmentgoods_id)
            form = ConsignmentgoodsaddForm(request.POST,instance=consignmentgoods)
            if form.is_valid():
                form.save()
                print("consignmentgoods Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("consignmentgoods Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

# List consignmentgoods
@login_required(login_url='login_page')
def consignmentgoods_list(request):
    first_name = request.session.get('first_name')
    context = {'consignmentgoods_list' : ConsignmentgoodsInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/consignmentgoods_list.html",context)

#Delete consignmentgoods
@login_required(login_url='login_page')
def consignmentgoods_delete(request,consignmentgoods_id):
    consignmentgoods = ConsignmentgoodsInfo.objects.get(pk=consignmentgoods_id)
    consignmentgoods.delete()
    return redirect('/SMS/consignmentgoods_list')

@login_required(login_url='login_page')
def consignmentgoods_nav(request,consignmentdetails_id):
    consignment_num = ConsignmentdetailInfo.objects.get(pk=consignmentdetails_id).id
    print(consignment_num)
    # return redirect('/SMS/costingsummary_update/' + str(costing_summary_id))
    return redirect(request.META['HTTP_REFERER'])
