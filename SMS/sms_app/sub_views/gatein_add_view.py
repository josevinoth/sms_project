from django.db import transaction
from django.shortcuts import render, redirect
from ..forms import GateinaddForm
from django.contrib.auth.decorators import login_required
from ..models import Gatein_info,Loadingbay_Info,DamagereportInfo,Warehouse_goods_info,DamagereportImages,Gatein_pre_info
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from ..models import User_extInfo
import json
# Add WH Job
@transaction.atomic
@login_required(login_url='login_page')
def gatein_add(request, gatein_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    user_branch = User_extInfo.objects.get(user_id=user_id).emp_branch
    ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
    tot_package = request.POST.get('gatein_no_of_pkg')
    wh_job_id = ses_gatein_id_nam
    if request.method == "GET":
        if gatein_id == 0:
            print("I am inside Get add Gatein")
            gatein_form = GateinaddForm()
            context = {
                'user_id': user_id,
                'first_name': first_name,
                'gatein_form': gatein_form,
                'loadingbay_list': Loadingbay_Info.objects.filter(lb_job_no=wh_job_id),
                'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
                'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
                'wh_job_id': wh_job_id,
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
                'user_branch':user_branch,
            }
        else:
            print("I am inside get edit Gatein")
            wh_job_id = Gatein_info.objects.get(pk=gatein_id).gatein_job_no
            wh_customer_name = Gatein_info.objects.get(pk=gatein_id).gatein_customer
            wh_customer_type = Gatein_info.objects.get(pk=gatein_id).gatein_customer_type
            wh_invoice = Gatein_info.objects.get(pk=gatein_id).gatein_invoice
            wh_total_packages = Gatein_info.objects.get(pk=gatein_id).gatein_no_of_pkg
            wh_invoice_weight = Gatein_info.objects.get(pk=gatein_id).gatein_weight
            wh_po_num = Gatein_info.objects.get(pk=gatein_id).gatein_po_num
            request.session['ses_gatein_id_nam'] = wh_job_id
            request.session['ses_customer_name'] = str(wh_customer_name)
            request.session['ses_customer_type'] = str(wh_customer_type)
            request.session['ses_wh_invoice'] = wh_invoice
            request.session['ses_gatein_no_of_pkg'] = wh_total_packages
            request.session['ses_gatein_weight'] = wh_invoice_weight
            request.session['ses_consigner']=Gatein_info.objects.get(pk=gatein_id).gatein_shipper
            request.session['ses_consignee'] = Gatein_info.objects.get(pk=gatein_id).gatein_consignee
            request.session['ses_po_num'] = wh_po_num
            request.session['ses_wh_gatein_id'] = gatein_id
            # wh_job_id_sess=request.session.get('ses_gatein_id_nam')
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

            loadingbay_list= Loadingbay_Info.objects.filter(lb_job_no=wh_job_id)
            damagereport_list= DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id)
            gatein_list=Gatein_info.objects.filter(gatein_job_no=wh_job_id)
            goods_list= Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id)
            gatein_info = Gatein_info.objects.get(pk=gatein_id)
            gatein_form = GateinaddForm(instance=gatein_info)
            context = {
                'user_id': user_id,
                'gatein_form': gatein_form,
                'first_name': first_name,
                'damagereport_list':damagereport_list,
                'loadingbay_list': loadingbay_list,
                'gatein_list':gatein_list,
                'goods_list': goods_list,
                'gatein_status':gatein_status,
                'loadingbay_status':loadingbay_status,
                'damage_before_status':damage_before_status,
                'damage_after_status': damage_after_status,
                'warehousein_status': warehousein_status,
            }
        return render(request, "asset_mgt_app/gatein_add.html", context)
    else:
        if gatein_id == 0:
            print("I am inside post add Gatein")
            gatein_form = GateinaddForm(request.POST)
        else:
            print("I am inside post edit Gatein")
            gatein_info = Gatein_info.objects.get(pk=gatein_id)
            gatein_form = GateinaddForm(request.POST, instance=gatein_info)
        if gatein_form.is_valid():
            print("Form is Valid")
            gatein_form.save()
            # raw_data = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list('wh_goods_pieces',flat=True)
            # cumsum = sum(raw_data)
            # print("Sum is",cumsum)
            # print("Total Package is", tot_package)
            # if cumsum > float(tot_package):
            #     messages.info(request, 'Total Packages count is lower than package count inside Warehouse ')
            #     transaction.set_rollback(True)
            #     return redirect(request.META['HTTP_REFERER'])
            # else:
            #     messages.info(request, 'Record Updated Successfully')
        else:
            print("Form is In-Valid")
        return redirect('/SMS/gatein_list')
# List WH Job
@login_required(login_url='login_page')
def gatein_list(request):
    first_name = request.session.get('first_name')
    context = {'Gatein_list' : Gatein_info.objects.all(),'first_name': first_name,}
    return render(request,"asset_mgt_app/gatein_list.html",context)

#Delete WH Job
@login_required(login_url='login_page')
def gatein_delete(request,gatein_id):
    wh_job_id=Gatein_info.objects.get(pk=gatein_id).gatein_job_no
    # wh_job_id = request.session.get('ses_gatein_id_nam')
    gatein_del = Gatein_info.objects.get(pk=gatein_id)
    gatein_del.delete()

    # Delete loading Bay
    try:
        loadingbay_del = Loadingbay_Info.objects.filter(lb_job_no=wh_job_id)
        loadingbay_del.delete()
    except ObjectDoesNotExist:
        print("Loading bay Object does not exist")
        pass

    # Delete Damage/Check Before
    try:
        damagereport_del=DamagereportInfo.objects.get(dam_wh_job_num=wh_job_id)
        damagereportimg_del = DamagereportImages.objects.get(damimage_wh_job_num=wh_job_id)
        damagereport_del.delete()
        damagereportimg_del.delete()
    except ObjectDoesNotExist:
        print("Damage/Check Before Object does not exist")
        pass

    # Delete Damage/Check After
    try:
        Warehouse_goods_del = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id)
        Warehouse_goods_del.delete()
    except ObjectDoesNotExist:
        print("Damage/Check After Object does not exist")
        pass

    return redirect('/SMS/gatein_list')

#Delete WH Job
@login_required(login_url='login_page')
def load_pre_gate_in(request):
    # Fetch pre_gate_in details
    pre_gatein_val = request.GET.get('pre_gatein_val')
    # Fetch Bay details
    pre_gatein_val_final = Gatein_pre_info.objects.filter(gatein_pre_number=pre_gatein_val).values()
    Transporter=pre_gatein_val_final[0]['gatein_pre_transporter']
    Driver_Name=pre_gatein_val_final[0]['gatein_pre_driver']
    Driver_Contact=pre_gatein_val_final[0]['gatein_pre_contact_number']
    Driver_License=pre_gatein_val_final[0]['gatein_pre_DL_number']
    OTL=pre_gatein_val_final[0]['gatein_pre_otl']
    Truck_Number=pre_gatein_val_final[0]['gatein_pre_truck_number']
    Truck_Type=pre_gatein_val_final[0]['gatein_pre_truck_type_id']
    data = {
            'Transporter': Transporter,
            'Driver_Name': Driver_Name,
            'Driver_Contact': Driver_Contact,
            'Driver_License': Driver_License,
            'OTL': OTL,
            'Truck_Number':Truck_Number,
            'Truck_Type': Truck_Type,
        }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))

