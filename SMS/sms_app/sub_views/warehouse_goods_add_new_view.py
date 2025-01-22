from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from ..forms import warehouse_goodsadd_gatein_form
from ..models import Location_info,User_extInfo,warehouse_goodsnew_info
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction


@login_required(login_url='login_page')
def warehouse_goods_add_gatein(request,wh_goods_gatein_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    user_branch = User_extInfo.objects.get(user_id=user_id).emp_branch
    user_branch_id = Location_info.objects.get(loc_name=user_branch).id
    if request.method == "GET":
        if wh_goods_gatein_id == 0:
            wh_goods_gatein_form = warehouse_goodsadd_gatein_form()
        else:
            wh_goods_gatein=warehouse_goodsnew_info.objects.get(pk=wh_goods_gatein_id)
            wh_goods_gatein_form = warehouse_goodsadd_gatein_form(instance=wh_goods_gatein)
        context={
                'wh_goods_gatein_form': wh_goods_gatein_form,
                'first_name': first_name,
                'user_id': user_id,
                }
        return render(request, "asset_mgt_app/warehouse_jobs_add.html",context )
    else:
        if wh_goods_gatein_id == 0:
            wh_goods_gatein_form = warehouse_goodsadd_gatein_form(request.POST)
            if wh_goods_gatein_form.is_valid():
                # Use commit=False to delay saving
                wh_goods_gatein_instance = wh_goods_gatein_form.save(commit=False)

                try:
                    with transaction.atomic():
                        # Retrieve the current instance ID after saving to avoid conflicts
                        wh_goods_gatein_instance.save()
                        current_id = wh_goods_gatein_instance.id

                        # Generate WH Job # based on the saved ID
                        if user_branch_id == 1:
                            branch = 'BLR_WH_Job_'
                        elif user_branch_id == 2:
                            branch = 'MAA_WH_Job_'
                        elif user_branch_id == 3:
                            branch = 'PNY_WH_Job_'
                        else:
                            branch = 'HYD_WH_Job_'

                        wh_job_num_next = f"{branch}{2000000 + current_id}"
                        wh_goods_gatein_instance.whn_job_no = wh_job_num_next

                        # Save the instance again with the updated WH Job #
                        wh_goods_gatein_instance.save()

                except Exception as e:
                    messages.error(request, f"An error occurred: {str(e)}")
                    return redirect(request.META['HTTP_REFERER'])

                messages.success(request, 'Record Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])

            else:
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            wh_goods_gatein = warehouse_goodsnew_info.objects.get(pk=wh_goods_gatein_id)
            wh_goods_gatein_form = warehouse_goodsadd_gatein_form(request.POST,instance=wh_goods_gatein)
            if wh_goods_gatein_form.is_valid():
                wh_goods_gatein_form.save()
                messages.success(request, 'Record Updated Successfully')
                # return redirect('/SMS/warehouse_goods_gatein_list')
                return redirect(request.META['HTTP_REFERER'])
            else:
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])

# wh_goods_gatein list
@login_required(login_url='login_page')
def warehouse_goods_gatein_list(request):
    first_name = request.session.get('first_name')
    context = {
            'warehouse_goods_gatein_list' : warehouse_goodsnew_info.objects.all(),
            'first_name': first_name
            }
    return render(request,"asset_mgt_app/warehouse_jobs_list.html",context)

#wh_goods_gatein delete
@login_required(login_url='login_page')
def warehouse_goods_gatein_delete(request,wh_goods_gatein_id):
    warehouse_goods = warehouse_goodsnew_info.objects.get(pk=wh_goods_gatein_id)
    warehouse_goods.delete()
    return redirect('/SMS/warehouse_goods_gatein_list')