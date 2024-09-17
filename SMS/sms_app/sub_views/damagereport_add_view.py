from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..forms import DamagereportaddForm,DamagereportImagesForm
from ..models import Location_info,DamagereportInfo,Loadingbay_Info,Gatein_info,Warehouse_goods_info,DamagereportImages
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from ..models import User_extInfo
from random import randint
@login_required(login_url='login_page')
def damagereport_add(request,damagereport_id=0):
    first_name = request.session.get('first_name')
    wh_job_id = request.session.get('ses_gatein_id_nam')
    user_id = request.session.get('ses_userID')
    user_branch = User_extInfo.objects.get(user_id=user_id).emp_branch
    user_branch_id = Location_info.objects.get(loc_name=user_branch).id

    # Gate In Status Check
    try:
        gatein_status = Gatein_info.objects.get(gatein_job_no=wh_job_id).gatein_status  # fetch gatein status
    except ObjectDoesNotExist:
        gatein_status = "No Status"
    # Loading Bay Status Check
    try:
        loadingbay_status = Loadingbay_Info.objects.get(lb_job_no=wh_job_id).lb_status  # fetch loadingbay status
    except ObjectDoesNotExist:
        loadingbay_status = "No Status"
    # Damage/Before Status Check
    try:
        damage_before_status = DamagereportInfo.objects.get(dam_wh_job_num=wh_job_id).dam_status  # fetch damage report status
    except ObjectDoesNotExist:
        damage_before_status = "No Status"
    # Damage/After Status Check
    try:
        goods_status = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_goods_status',flat=True)  # count records
        goods_status_list = list(goods_status)
        if goods_status_list == []:
            damage_after_status = "Empty"
        elif all(element == None for element in (goods_status_list)):
            damage_after_status = "None"
        elif all(element == 5 for element in (goods_status_list)):
            damage_after_status = "Completed"  # get goods status
        else:
            damage_after_status = "No Status"  # get goods status
    except ObjectDoesNotExist:
        damage_after_status = "No Status"

    # Warehousein Status Check
    try:
        warehousein_stack_layer = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list(
            'wh_stack_layer', flat=True)  # count records
        warehousein_stack_layer_list = list(warehousein_stack_layer)
        if warehousein_stack_layer_list == []:
            warehousein_status = "Empty"
        elif all(element == None for element in (warehousein_stack_layer_list)):
            warehousein_status = "None"
        elif None not in warehousein_stack_layer_list:
            warehousein_status = "Completed"  # get goods status
        else:
            warehousein_status = "No Status"  # get goods status
    except ObjectDoesNotExist:
        warehousein_status = "No Status"

    if request.method == "GET":
        if damagereport_id == 0:
            print("I am inside Get add damagereport")
            damagereport_form = DamagereportaddForm()
            damagereportimg_form = DamagereportImagesForm()
            context = {
                'first_name': first_name,
                'damagereport_form': damagereport_form,
                'damagereportimg_form':damagereportimg_form,
                'loadingbay_list': Loadingbay_Info.objects.filter(lb_job_no=wh_job_id),
                'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
                'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
                'wh_job_id': wh_job_id,
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
                'gatein_status': gatein_status,
                'loadingbay_status': loadingbay_status,
                'damage_before_status': damage_before_status,
                'warehousein_status': warehousein_status,
                'user_branch': user_branch,
            }
        else:
            print("I am inside get edit damagereport")
            damagereport_info=DamagereportInfo.objects.get(dam_wh_job_num=wh_job_id)
            damagereport_form = DamagereportaddForm(instance=damagereport_info)
            damagereportimg_info = DamagereportImages.objects.get(damimage_wh_job_num=wh_job_id)
            damagereportimg_form = DamagereportImagesForm(request.FILES, instance=damagereportimg_info)
            context = {
                'damagereport_form': damagereport_form,
                'damagereportimg_form':damagereportimg_form,
                'first_name': first_name,
                'loadingbay_list': Loadingbay_Info.objects.filter(lb_job_no=wh_job_id),
                'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
                'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
                'wh_job_id': wh_job_id,
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
                'gatein_status': gatein_status,
                'loadingbay_status': loadingbay_status,
                'damage_before_status': damage_before_status,
                'damage_after_status': damage_after_status,
                'warehousein_status': warehousein_status,
            }
        return render(request, "asset_mgt_app/damagereport_add.html", context)
    else:
        if damagereport_id == 0:
            print("I am inside post add damagereport")
            damagereport_form = DamagereportaddForm(request.POST)
            damagereportimg_form=DamagereportImagesForm(request.POST,request.FILES)
            if damagereport_form.is_valid():
                print("Main Form Saved")
                if damagereportimg_form.is_valid():
                    print("SubForm Saved")
                    damagereportimg_form.save()
                else:
                    print("Sub Form Not saved")
                # Generate Random GRN number
                if user_branch_id == 1:
                    branch = 'BLR_GRN_'
                elif user_branch_id == 2:
                    branch = 'MAA_GRN_'
                elif user_branch_id == 3:
                    branch = 'PNY_GRN_'
                else:
                    branch = 'HYD_GRN_'
                try:
                    group = []
                    for i in wh_job_id:
                        try:
                            int(i)
                            group.append(i)
                        except ValueError:
                            pass
                    wh_grn_num_next = str(branch) + str(int(''.join(group)))
                except ObjectDoesNotExist:
                    wh_grn_num_next = str(branch) + str(randint(10000, 99999))
                damagereport_form.save()
                print('wh_grn_num_next',wh_grn_num_next)
                last_id = (DamagereportInfo.objects.values_list('id', flat=True)).last()
                DamagereportInfo.objects.filter(id=last_id).update(dam_GRN_num=wh_grn_num_next)
                messages.success(request, 'Record Updated Successfully')
                url = 'damagereport_update/' + str(last_id)
                return redirect(url)
            else:
                print("Main Form Not saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("I am inside post edit damagereport")
            damagereport_info = DamagereportInfo.objects.get(pk=damagereport_id)
            damagereport_form = DamagereportaddForm(request.POST,instance=damagereport_info)
            damagereportimg_info = DamagereportImages.objects.get(damimage_wh_job_num=wh_job_id)
            damagereportimg_form = DamagereportImagesForm(request.POST,request.FILES,instance=damagereportimg_info)
            if damagereport_form.is_valid():
                print("Damage_Report Main Form Saved")
                damagereport_form.save()
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Damage_Report Form Not saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')

            if damagereportimg_form.is_valid():
                print("Damage_Report SubForm Saved")
                damagereportimg_form.save()
            else:
                print("Damage_Report Sub Form Not saved")
            return redirect(request.META['HTTP_REFERER'])
            # return redirect('/SMS/gatein_list')

# List damagereport
@login_required(login_url='login_page')
def damagereport_list(request):
    first_name = request.session.get('first_name')
    context = {'damagereport_list' : DamagereportInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/damagereport_list.html",context)

# #Delete damagereport
# @login_required(login_url='login_page')
# def damagereport_delete(request,damagereport_id):
#     damagereport = DamagereportInfo.objects.get(pk=damagereport_id)
#
#     damagereport.delete()
#     return redirect('/SMS/damagereport_list')
