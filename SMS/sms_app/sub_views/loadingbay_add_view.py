from django.contrib import messages
from django.shortcuts import render, redirect
from ..forms import LoadingbayddForm,LoadingbayImagesForm
from django.contrib.auth.decorators import login_required
from ..models import Gatein_info,Loadingbay_Info,DamagereportInfo,Warehouse_goods_info,Loadingbayimages_Info,Currency_type
from django.core.exceptions import ObjectDoesNotExist

# Add WH Job
@login_required(login_url='login_page')
def loadingbay_add(request, loadingbay_id=0):
    first_name = request.session.get('first_name')
    ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
    print(ses_gatein_id_nam)
    wh_job_id = request.session.get('ses_gatein_id_nam')
    currency_EUR=Currency_type.objects.get(currency_type="EUR").converision_value
    currency_INR=Currency_type.objects.get(currency_type="INR").converision_value
    currency_USD=Currency_type.objects.get(currency_type="USD").converision_value
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
        damage_before_status = DamagereportInfo.objects.get(
            dam_wh_job_num=wh_job_id).dam_status  # fetch damage report status
    except ObjectDoesNotExist:
        damage_before_status = "No Status"
    # Damage/After Status Check
    try:
        goods_status = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_goods_status',
                                                                                                flat=True)  # count records

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

    ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
    wh_job_id = ses_gatein_id_nam
    if request.method == "GET":
        if loadingbay_id == 0:
            print("I am inside Get add Loading bay")
            loadingbay_form = LoadingbayddForm()
            loadingbayimg_form=LoadingbayImagesForm()
            context = {
                'currency_EUR':currency_EUR,
                'currency_INR':currency_INR,
                'currency_USD':currency_USD,
                'first_name': first_name,
                'loadingbay_form': loadingbay_form,
                'loadingbayimg_form':loadingbayimg_form,
                'wh_job_id': wh_job_id,
                'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
                'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
                'gatein_status': gatein_status,
                'loadingbay_status': loadingbay_status,
                'damage_before_status': damage_before_status,
                'damage_after_status': damage_after_status,
                'warehousein_status': warehousein_status,
            }
        else:
            print("I am inside get edit loading bay")
            loadingbay_info = Loadingbay_Info.objects.get(lb_job_no=wh_job_id)
            loadingbay_form = LoadingbayddForm(instance=loadingbay_info)
            loadingbayimg_info=Loadingbayimages_Info.objects.get(lbimg_job_no=wh_job_id)
            loadingbayimg_form = LoadingbayImagesForm(request.FILES,instance=loadingbayimg_info)
            context = {
                'currency_EUR': currency_EUR,
                'currency_INR': currency_INR,
                'currency_USD': currency_USD,
                'loadingbay_form': loadingbay_form,
                'loadingbayimg_form':loadingbayimg_form,
                'first_name': first_name,
                'loadingbay_list': Loadingbay_Info.objects.filter(lb_job_no=wh_job_id),
                'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
                'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
                'wh_job_id':wh_job_id,
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
                'gatein_status': gatein_status,
                'loadingbay_status': loadingbay_status,
                'damage_before_status': damage_before_status,
                'damage_after_status': damage_after_status,
                'warehousein_status': warehousein_status,
            }
        return render(request, "asset_mgt_app/loadingbay_add.html", context)
    else:
        if loadingbay_id == 0:
            print("I am inside post add Loading bay")
            loadingbay_form = LoadingbayddForm(request.POST)
            loadingbayimg_form=LoadingbayImagesForm(request.POST,request.FILES)
        else:
            print("I am inside post edit Loading bay")
            loadingbay_info = Loadingbay_Info.objects.get(pk=loadingbay_id)
            loadingbay_form = LoadingbayddForm(request.POST, instance=loadingbay_info)
            loadingbayimg_info=Loadingbayimages_Info.objects.get(lbimg_job_no=wh_job_id)
            loadingbayimg_form=LoadingbayImagesForm(request.POST,request.FILES,instance=loadingbayimg_info)
        if loadingbay_form.is_valid():
            print("Main Form Saved")
            loadingbay_form.save()
            messages.success(request, 'Record Updated Successfully')
        else:
            print("Main Form Not saved")
            messages.error(request, 'Record Not Saved.Please Enter All Required Fields')

        if loadingbayimg_form.is_valid():
            print("SubForm Saved")
            loadingbayimg_form.save()
        else:
            print("Sub Form Not saved")
        # return redirect(request.META['HTTP_REFERER'])
        return redirect('/SMS/gatein_list')

# # List WH Job
# @login_required(login_url='login_page')
# def gatein_list(request):
#     first_name = request.session.get('first_name')
#     context = {'Gatein_list' : Gatein_info.objects.all(),'first_name': first_name,}
#     return render(request,"asset_mgt_app/gatein_list.html",context)
#
# #Delete WH Job
# @login_required(login_url='login_page')
# def gatein_delete(request,gatein_id):
#     gatein = Gatein_info.objects.get(pk=gatein_id)
#     gatein.delete()
#     return redirect('/SMS/gatein_list')


