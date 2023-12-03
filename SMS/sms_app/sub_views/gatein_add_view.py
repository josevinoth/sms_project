from random import randint
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect
from ..forms import GateinaddForm
from django.contrib.auth.decorators import login_required
from ..models import VehicletypeInfo,Pregateintruckinfo,Location_info,Gatein_info,Loadingbay_Info,DamagereportInfo,Warehouse_goods_info,DamagereportImages,Gatein_pre_info
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
    user_branch_id = Location_info.objects.get(loc_name=user_branch).id
    ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
    wh_job_id = ses_gatein_id_nam
    tot_package = request.POST.get('gatein_no_of_pkg')
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
            if gatein_form.is_valid():
                print("Form is Valid")
                # Generate Random WH_job number
                if user_branch_id == 1:
                    branch = 'BLR_WH_Job_'
                elif user_branch_id == 2:
                    branch = 'MAA_WH_Job_'
                elif user_branch_id == 3:
                    branch = 'PNY_WH_Job_'
                else:
                    branch = 'HYD_WH_Job_'
                try:
                    last_id = Gatein_info.objects.latest('id').id
                    wh_job_num=Gatein_info.objects.get(id=last_id).gatein_job_no
                    group=[]
                    for i in wh_job_num:
                        try:
                            int(i)
                            group.append(i)
                        except ValueError:
                            pass
                    wh_job_num_next = str(branch) + str(int(''.join(group)) + 1)
                except ObjectDoesNotExist:
                    wh_job_num_next = str(branch) + str(randint(10000, 99999))
                gatein_form.save()
                last_id = (Gatein_info.objects.values_list('id', flat=True)).last()
                Gatein_info.objects.filter(id=last_id).update(gatein_job_no=wh_job_num_next)
                messages.success(request, 'Record Updated Successfully')
                job_id = Gatein_info.objects.get(gatein_job_no=wh_job_num_next).id
                url = 'gatein_update/' + str(job_id)
                return redirect(url)
            else:
                print("Form is In-Valid")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("I am inside post edit Gatein")
            gatein_info = Gatein_info.objects.get(pk=gatein_id)
            gatein_form = GateinaddForm(request.POST, instance=gatein_info)
            if gatein_form.is_valid():
                print("Form is Valid")
                gatein_form.save()
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Form is In-Valid")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/gatein_list')
# List WH Job

@login_required(login_url='login_page')
def gatein_list(request):
    first_name = request.session.get('first_name')
    Gatein_list= (Gatein_info.objects.all()).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(Gatein_list, 10000)
    page_obj = paginator.get_page(page_number)
    context = {
        # 'Gatein_list' : Gatein_list,
        'first_name': first_name,
        'page_obj': page_obj,
    }
    return render(request,"asset_mgt_app/gatein_list.html",context)
@login_required(login_url='login_page')
def get_queryset(request):
    first_name = request.session.get('first_name')
    pre_gate_in = request.GET.get("pre_gate_in")
    job_number = request.GET.get("job_number")
    invoice_number = request.GET.get("invoice_number")
    if not pre_gate_in:
        pre_gate_in = ""
    if not job_number:
        job_number = ""
    if not invoice_number:
        invoice_number = ""
    Gatein_list = (Gatein_info.objects.filter((Q(gatein_job_no__icontains =job_number)|Q(gatein_job_no__isnull=True)) & (Q(gatein_invoice__icontains =invoice_number)|Q(gatein_invoice__isnull=True)) & (Q(gatein_pre_id__gatein_pre_number__icontains =pre_gate_in)|Q(gatein_pre_id__isnull=True)))).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(Gatein_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
        'Gatein_list': Gatein_list,
        'first_name': first_name,
        'page_obj': page_obj,
        }
    return render(request, "asset_mgt_app/gatein_list.html", context)

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
    print('pre_gatein_val',pre_gatein_val)
    pre_gatein_id=Gatein_pre_info.objects.get(gatein_pre_number=pre_gatein_val).id
    # Fetch Bay details
    pre_gatein_val_final = Pregateintruckinfo.objects.filter(pregatein_number=pre_gatein_id).values()
    print('pre_gatein_val_final',pre_gatein_val_final)
    # Transporter=pre_gatein_val_final[0]['pregatein_transporter']
    Transporter=Pregateintruckinfo.objects.filter(pregatein_number=pre_gatein_id).values_list('pregatein_transporter',flat=True)
    print('Transporter',Transporter)
    # Driver_Name=pre_gatein_val_final[0]['gatein_pre_driver']
    Driver_Name=Pregateintruckinfo.objects.filter(pregatein_number=pre_gatein_id).values_list('pregatein_driver',flat=True)
    # Driver_Contact=pre_gatein_val_final[0]['gatein_pre_contact_number']
    Driver_Contact=Pregateintruckinfo.objects.filter(pregatein_number=pre_gatein_id).values_list('pregatein_contact_number',flat=True)
    # Driver_License=pre_gatein_val_final[0]['gatein_pre_DL_number']
    Driver_License=Pregateintruckinfo.objects.filter(pregatein_number=pre_gatein_id).values_list('pregatein_dl_number',flat=True)
    # OTL=pre_gatein_val_final[0]['gatein_pre_otl']
    OTL=Pregateintruckinfo.objects.filter(pregatein_number=pre_gatein_id).values_list('pregatein_otl',flat=True)
    # Truck_Number=pre_gatein_val_final[0]['gatein_pre_truck_number']
    Truck_Number=Pregateintruckinfo.objects.filter(pregatein_number=pre_gatein_id).values_list('pregatein_truck_number',flat=True)
    # Truck_Type=pre_gatein_val_final[0]['gatein_pre_truck_type_id']
    Truck_Type=Pregateintruckinfo.objects.filter(pregatein_number=pre_gatein_id).values_list('pregatein_truck_type',flat=True)
    Truck_Name=[]
    for i in Truck_Type:
        Truck_Name.append(VehicletypeInfo.objects.get(id=i).vt_vehicletype)
    data = {
            'Transporter': list(Transporter),
            'Driver_Name': list(Driver_Name),
            'Driver_Contact': list(Driver_Contact),
            'Driver_License': list(Driver_License),
            'OTL': list(OTL),
            'Truck_Number':list(Truck_Number),
            'Truck_Type': list(Truck_Name),
        }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))
