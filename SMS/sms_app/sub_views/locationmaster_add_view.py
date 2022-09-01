import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from ..forms import LocationmasteraddForm
from ..models import LocationmasterInfo,CustomerInfo,TrbusinesstypeInfo,Warehouse_goods_info
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def locationmaster_add(request,locationmaster_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if locationmaster_id == 0:
            con_val = request.GET.get('lm_concatenate')
            print(con_val)
            print('Inside Get')
            lm_record_count = LocationmasterInfo.objects.filter(lm_concatenate=con_val).count()
            print("Record Count", lm_record_count)
            if lm_record_count == 1:
                print('Inside GET first loop')
                print('Record Exist')
                messages.info(request, 'Record Exist')
                return redirect(request.META['HTTP_REFERER'])
            else:
                print('Inside GET second loop')
                form = LocationmasteraddForm()
        else:
            print('Inside Get Else')
            locationmaster=LocationmasterInfo.objects.get(pk=locationmaster_id)
            form = LocationmasteraddForm(instance=locationmaster)
        return render(request, "asset_mgt_app/locationmaster_add.html", {'form': form,'first_name': first_name})
    else:
        if locationmaster_id == 0:
            con_val = request.POST.get('lm_concatenate')
            print(con_val)
            print('Inside Post')
            lm_record_count=LocationmasterInfo.objects.filter(lm_concatenate=con_val).count()
            print("Record Count",lm_record_count)
            if lm_record_count==1:
                print('Inside Post first loop')
                print('Record Exist')
                messages.info(request, 'Record Exist')
                return redirect(request.META['HTTP_REFERER'])
            else:
                print('Inside Post second loop')
                form = LocationmasteraddForm(request.POST)
                if form.is_valid():
                    form.save()
                return redirect('/SMS/locationmaster_list')
        else:
            print('Inside Post Else')
            con_val = request.POST.get('lm_concatenate')
            print(con_val)
            # con_val = LocationmasterInfo.objects.get(pk=locationmaster_id).lm_concatenate
            # if form.is_valid():
            #     form.save()
            lm_record_count = LocationmasterInfo.objects.filter(lm_concatenate=con_val).count()
            print("Record Count",lm_record_count)
            if lm_record_count>1:
                print('Inside Post Else first loop')
                print('Record Exist')
                messages.info(request, 'Record Exist')
                return redirect(request.META['HTTP_REFERER'])
            else:
                print('Inside Post Else Second loop')
                locationmaster = LocationmasterInfo.objects.get(pk=locationmaster_id)
                form = LocationmasteraddForm(request.POST, instance=locationmaster)
                if form.is_valid():
                    Branch_val = LocationmasterInfo.objects.get(pk=locationmaster_id).lm_wh_location.id
                    Unit_val = LocationmasterInfo.objects.get(pk=locationmaster_id).lm_wh_unit.id
                    Bay_val = LocationmasterInfo.objects.get(pk=locationmaster_id).lm_areaside.id
                    print(Branch_val)
                    print(Unit_val)
                    print(Bay_val)
                    wh_goods_list = Warehouse_goods_info.objects.filter(wh_branch_id=Branch_val, wh_unit_id=Unit_val,wh_bay_id=Bay_val)
                    stack_layer = wh_goods_list.values('wh_stack_layer_id')
                    volume = wh_goods_list.values('wh_goods_volume_weight')
                    area = wh_goods_list.values('wh_goods_area')
                    area_final = 0
                    volume_final = 0
                    for j in range(len(stack_layer)):
                        # print("Stack Layer",stack_layer[j]['wh_stack_layer_id'])
                        # print("Volume Occupied", volume[j]['wh_goods_volume_weight'])
                        volume_final = volume_final + volume[j]['wh_goods_volume_weight']
                        if stack_layer[j]['wh_stack_layer_id'] == 1:
                            # print("Area Occupied", area[j]['wh_goods_area'])
                            area_final = area_final + area[j]['wh_goods_area']
                        else:
                            print("No Area")
                    print("Total_Area", area_final)
                    print("Total_Volume",volume_final)
                    LocationmasterInfo.objects.filter(pk=locationmaster_id).update(lm_area_occupied=area_final)
                    LocationmasterInfo.objects.filter(pk=locationmaster_id).update(lm_volume_occupied=volume_final)

                    form.save()
            return redirect('/SMS/locationmaster_list')

# List locationmaster
@login_required(login_url='login_page')
def locationmaster_list(request):
    first_name = request.session.get('first_name')
    context = {'locationmaster_list' : LocationmasterInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/locationmaster_list.html",context)

#Delete locationmaster
@login_required(login_url='login_page')
def locationmaster_delete(request,locationmaster_id):
    locationmaster = LocationmasterInfo.objects.get(pk=locationmaster_id)
    locationmaster.delete()
    return redirect('/SMS/locationmaster_list')

#Update Location master
@login_required(login_url='login_page')
def update_location_master(request):
    wh_branch=LocationmasterInfo.object.all()
    print(wh_branch)

#Get Customer Model
@login_required(login_url='login_page')
def load_customer_model(request):
    unit_list=[]
    unit_name=[]
    unit_name_list = []
    lm_customer_name_id = request.GET.get('lm_customer_name_id')
    print("Customer Model ID",lm_customer_name_id)
    customer_businessmodel = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_businessmodel')
    print("customer_businessmodel",customer_businessmodel)
    customer_businessmodel_val=customer_businessmodel[0]['cu_businessmodel'] #Get value from Queryset
    print(customer_businessmodel_val)
    lm_customer_model_id=TrbusinesstypeInfo.objects.filter(id=customer_businessmodel_val).values('tb_trbusinesstype')
    print("customer_businessmodel_id", lm_customer_model_id)
    customer_businessmodel_txt= lm_customer_model_id[0]['tb_trbusinesstype']  # Get value from Queryset
    print(customer_businessmodel_txt)
    data = {
        'customer_businessmodel_val':customer_businessmodel_val
    }
    return HttpResponse(customer_businessmodel_val)
    # return JsonResponse((data))