import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from ..forms import LocationmasteraddForm
from ..models import WhratemasterInfo,LocationmasterInfo,CustomerInfo,TrbusinesstypeInfo,Warehouse_goods_info
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
                area_final = 0
                volume_final = 0
                context = {
                    'form': form,
                    'first_name': first_name,
                    'area_final': area_final,
                    'volume_final': volume_final,
                }
                return render(request, "asset_mgt_app/locationmaster_add.html", context)
        else:
            print('Inside Get Else')
            Branch_val = LocationmasterInfo.objects.get(pk=locationmaster_id).lm_wh_location.id
            Unit_val = LocationmasterInfo.objects.get(pk=locationmaster_id).lm_wh_unit.id
            Bay_val = LocationmasterInfo.objects.get(pk=locationmaster_id).lm_areaside.id
            print("Branch", Branch_val)
            print("Unit", Unit_val)
            print("Bay", Bay_val)
            wh_goods_list = Warehouse_goods_info.objects.filter(wh_branch_id=Branch_val, wh_unit_id=Unit_val,
                                                                wh_bay_id=Bay_val)
            print("Goods List Count",wh_goods_list)
            stack_layer = wh_goods_list.values('wh_stack_layer_id')
            volume = wh_goods_list.values('wh_goods_volume_weight')
            area = wh_goods_list.values('wh_goods_area')
            check_in_out_list = wh_goods_list.values('wh_check_in_out')
            area_final = 0
            volume_final = 0
            for j in range(len(wh_goods_list)):
                if check_in_out_list[j]['wh_check_in_out'] == 1:
                    volume_final = round((volume_final + volume[j]['wh_goods_volume_weight']),3)
                    if stack_layer[j]['wh_stack_layer_id'] == 1:
                        area_final = round((area_final + area[j]['wh_goods_area']),3)
                    else:
                        print("No Area")
            print("Total_Area", area_final)
            print("Total_Volume", volume_final)
            locationmaster=LocationmasterInfo.objects.get(pk=locationmaster_id)
            form = LocationmasteraddForm(instance=locationmaster)
            context = {
                'form': form,
                'first_name': first_name,
                'area_final':area_final,
                'volume_final':volume_final,
            }
        return render(request, "asset_mgt_app/locationmaster_add.html",context)
    else:
        if locationmaster_id == 0:
            con_val = request.POST.get('lm_concatenate')
            print(con_val)
            print('Inside Post')
            lm_record_check=LocationmasterInfo.objects.filter(lm_concatenate=con_val)
            print('lm_record_check',lm_record_check)
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
                    # LocationmasterInfo.objects.filter(pk=locationmaster_id).update(lm_area_occupied=area_final)
                    # LocationmasterInfo.objects.filter(pk=locationmaster_id).update(lm_volume_occupied=volume_final)

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
    total_weight = request.GET.get('total_weight')
    customer_id=CustomerInfo.objects.get(cu_name=lm_customer_name_id).id
    customer_businessmodel = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_businessmodel')
    customer_short_name = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_nameshort')
    customer_code = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_customercode')
    customer_GST = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_gst')
    customer_person = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_customerperson')
    customer_contact = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_contactno')
    customer_address = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_address')
    customer_type = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_type')
    customer_businessmodel_val=customer_businessmodel[0]['cu_businessmodel'] #Get value from Queryset
    customer_short_name_val=customer_short_name[0]['cu_nameshort'] #Get value from Queryset
    customer_code_val=customer_code[0]['cu_customercode'] #Get value from Queryset
    customer_GST_val=customer_GST[0]['cu_gst'] #Get value from Queryset
    customer_person_val=customer_person[0]['cu_customerperson'] #Get value from Queryset
    customer_contact_val = customer_contact[0]['cu_contactno']  # Get value from Queryset
    customer_address_val = customer_address[0]['cu_address']  # Get value from Queryset
    customer_type_val = customer_type[0]['cu_type']  # Get value from Queryset
    print('customer_type_val',customer_type_val)
    lm_customer_model_id=TrbusinesstypeInfo.objects.filter(id=customer_businessmodel_val).values('tb_trbusinesstype')
    customer_businessmodel_txt= lm_customer_model_id[0]['tb_trbusinesstype']  # Get value from Queryset
    # wh_rate = WhratemasterInfo.objects.filter(whrm_customer_name=customer_id, whrm_max_wt__lte=total_weight,whrm_min_wt__gte=total_weight,whrm_charge_type=1).values('whrm_rate')
    # wh_rate_val=wh_rate[0]['whrm_rate']
    # wh_rate = 1
    # print('wh_rate', wh_rate)
    # print('wh_rate_val', wh_rate_val)
    data = {
        'customer_businessmodel_val':customer_businessmodel_val,
        'customer_short_name_val':customer_short_name_val,
        'customer_code_val':customer_code_val,
        'customer_GST_val':customer_GST_val,
        'customer_person_val':customer_person_val,
        'customer_contact_val':customer_contact_val,
        'customer_address_val':customer_address_val,
        'customer_type_val':customer_type_val,
    }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))