import json
from datetime import timedelta, date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.aggregates import Sum
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
            print('Inside Get')
            lm_record_count = LocationmasterInfo.objects.filter(lm_concatenate=con_val).count()
            if lm_record_count == 1:
                print('Inside GET first loop')
                messages.info(request, 'Record Exist')
                return redirect(request.META['HTTP_REFERER'])
            else:
                print('Inside GET second loop')
                form = LocationmasteraddForm()
                area_occupied = 0
                volume_occupied = 0
                context = {
                    'form': form,
                    'first_name': first_name,
                    'area_occupied': area_occupied,
                    'volume_occupied': volume_occupied,
                }
                return render(request, "asset_mgt_app/locationmaster_add.html", context)
        else:
            print('Inside Get Else')
            # Branch_val = LocationmasterInfo.objects.get(pk=locationmaster_id).lm_wh_location.id
            # Unit_val = LocationmasterInfo.objects.get(pk=locationmaster_id).lm_wh_unit.id
            # Bay_val = LocationmasterInfo.objects.get(pk=locationmaster_id).lm_areaside.id
            # wh_goods_list = Warehouse_goods_info.objects.filter(wh_branch_id=Branch_val, wh_unit_id=Unit_val,
            #                                                     wh_bay_id=Bay_val)
            # stack_layer = wh_goods_list.values('wh_stack_layer_id')
            # volume = wh_goods_list.values('wh_goods_volume_weight')
            # area = wh_goods_list.values('wh_goods_area')
            # check_in_out_list = wh_goods_list.values('wh_check_in_out')
            # area_occupied = 0
            # volume_occupied = 0
            # for j in range(len(wh_goods_list)):
            #     if check_in_out_list[j]['wh_check_in_out'] == 1:
            #         volume_occupied = round((volume_occupied + volume[j]['wh_goods_volume_weight']),3)
            #         if stack_layer[j]['wh_stack_layer_id'] == 1:
            #             area_occupied = round((area_occupied + area[j]['wh_goods_area']),3)
            #         else:
            #             print("No Area")
            locationmaster=LocationmasterInfo.objects.get(pk=locationmaster_id)
            form = LocationmasteraddForm(instance=locationmaster)
            context = {
                'form': form,
                'first_name': first_name,
                # 'area_occupied':area_occupied,
                # 'volume_occupied':volume_occupied,
            }
        return render(request, "asset_mgt_app/locationmaster_add.html",context)
    else:
        if locationmaster_id == 0:
            con_val = request.POST.get('lm_concatenate')
            print('Inside Post')
            lm_record_check=LocationmasterInfo.objects.filter(lm_concatenate=con_val)
            lm_record_count=LocationmasterInfo.objects.filter(lm_concatenate=con_val).count()
            if lm_record_count==1:
                print('Inside Post first loop')
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
            # con_val = LocationmasterInfo.objects.get(pk=locationmaster_id).lm_concatenate
            # if form.is_valid():
            #     form.save()
            lm_record_count = LocationmasterInfo.objects.filter(lm_concatenate=con_val).count()
            if lm_record_count>1:
                print('Inside Post Else first loop')
                messages.info(request, 'Record Exist')
                return redirect(request.META['HTTP_REFERER'])
            else:
                print('Inside Post Else Second loop')
                locationmaster = LocationmasterInfo.objects.get(pk=locationmaster_id)
                form = LocationmasteraddForm(request.POST, instance=locationmaster)
                if form.is_valid():
                    # LocationmasterInfo.objects.filter(pk=locationmaster_id).update(lm_area_occupied=area_occupied)
                    # LocationmasterInfo.objects.filter(pk=locationmaster_id).update(lm_volume_occupied=volume_occupied)
                    form.save()
                    print('Form Saved Successfully')
                    messages.success(request, 'Record Updated Successfully')
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    print('Form Not Saved Successfully')
                    messages.error(request, 'Record Not Updated Successfully')
                    return redirect(request.META['HTTP_REFERER'])
            # return redirect('/SMS/locationmaster_list')

# List locationmaster
@login_required(login_url='login_page')
def locationmaster_list(request):
    first_name = request.session.get('first_name')
    warehousevolme_area_calc(request)
    context =   {
                    'locationmaster_list' : LocationmasterInfo.objects.all(),
                    'first_name': first_name
                }
    return render(request,"asset_mgt_app/locationmaster_list.html",context)

#Calculate warehouse area and volume
@login_required(login_url='login_page')
def warehousevolme_area_calc(request):
    print("Inside warehousevolme_area_calc")
    warehouse_list = LocationmasterInfo.objects.all().values_list('id', flat=True)
    for i in warehouse_list:
        branch = LocationmasterInfo.objects.get(pk=i).lm_wh_location
        unit = LocationmasterInfo.objects.get(pk=i).lm_wh_unit
        bay = LocationmasterInfo.objects.get(pk=i).lm_areaside
        volume_occupied = Warehouse_goods_info.objects.filter(wh_branch=branch, wh_unit=unit, wh_bay=bay,wh_check_in_out=1).aggregate(Sum('wh_goods_volume_weight'))['wh_goods_volume_weight__sum']
        area_occupied = Warehouse_goods_info.objects.filter(wh_branch=branch, wh_unit=unit, wh_bay=bay, wh_check_in_out=1,wh_stack_layer=1).aggregate(Sum('wh_goods_area'))['wh_goods_area__sum']

        if volume_occupied==None:
            volume_occupied_val=0
        else:
            volume_occupied_val=volume_occupied

        if area_occupied == None:
            area_occupied_val = 0
        else:
            area_occupied_val = area_occupied

        # Get Total Volume
        total_volume = LocationmasterInfo.objects.get(lm_wh_location=branch, lm_wh_unit=unit,lm_areaside=bay).lm_total_volume

        # Get Total Area
        total_area = LocationmasterInfo.objects.get(lm_wh_location=branch, lm_wh_unit=unit, lm_areaside=bay).lm_size

        # Calculate_Available Volume
        available_volume = total_volume - volume_occupied_val

        # Calculate_Available Ara
        available_area = total_area - area_occupied_val

        # Update Volume and Area
        LocationmasterInfo.objects.filter(lm_wh_location=branch, lm_wh_unit=unit, lm_areaside=bay).update(lm_available_area=round(available_area, 2))
        LocationmasterInfo.objects.filter(lm_wh_location=branch, lm_wh_unit=unit, lm_areaside=bay).update(lm_available_volume=round(available_volume, 2))
        LocationmasterInfo.objects.filter(lm_wh_location=branch, lm_wh_unit=unit, lm_areaside=bay).update(lm_volume_occupied=round(volume_occupied_val, 2))
        LocationmasterInfo.objects.filter(lm_wh_location=branch, lm_wh_unit=unit, lm_areaside=bay).update(lm_area_occupied=round(area_occupied_val, 2))
    return()
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

#Get Customer Model
@login_required(login_url='login_page')
def load_customer_model(request):
    lm_customer_name_id = request.GET.get('lm_customer_name_id')
    customer_businessmodel = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_businessmodel')
    customer_short_name = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_nameshort')
    customer_code = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_customercode')
    customer_GST = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_gst')
    customer_person = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_customerperson')
    customer_contact = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_contactno')
    customer_address = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_address')
    customer_type = CustomerInfo.objects.filter(cu_name=lm_customer_name_id).values('cu_type')
    customer_email = CustomerInfo.objects.get(cu_name=lm_customer_name_id).cu_email
    try:
        customer_info = CustomerInfo.objects.get(cu_name=lm_customer_name_id)
        industry_type = customer_info.cu_industry_type.id if customer_info.cu_industry_type else ""
    except ObjectDoesNotExist:
        industry_type = ""
    customer_businessmodel_val=customer_businessmodel[0]['cu_businessmodel'] #Get value from Queryset
    customer_short_name_val=customer_short_name[0]['cu_nameshort'] #Get value from Queryset
    customer_code_val=customer_code[0]['cu_customercode'] #Get value from Queryset
    customer_GST_val=customer_GST[0]['cu_gst'] #Get value from Queryset
    customer_person_val=customer_person[0]['cu_customerperson'] #Get value from Queryset
    customer_contact_val = customer_contact[0]['cu_contactno']  # Get value from Queryset
    customer_address_val = customer_address[0]['cu_address']  # Get value from Queryset
    customer_type_val = customer_type[0]['cu_type']  # Get value from Queryset
    lm_customer_model_id=TrbusinesstypeInfo.objects.filter(id=customer_businessmodel_val).values('tb_trbusinesstype')
    customer_businessmodel_txt= lm_customer_model_id[0]['tb_trbusinesstype']  # Get value from Queryset
    # wh_rate = WhratemasterInfo.objects.filter(whrm_customer_name=customer_id, whrm_max_wt__lte=total_weight,whrm_min_wt__gte=total_weight,whrm_charge_type=1).values('whrm_rate')
    # wh_rate_val=wh_rate[0]['whrm_rate']
    # wh_rate = 1
    data = {
        'customer_businessmodel_val':customer_businessmodel_val,
        'customer_short_name_val':customer_short_name_val,
        'customer_code_val':customer_code_val,
        'customer_GST_val':customer_GST_val,
        'customer_person_val':customer_person_val,
        'customer_contact_val':customer_contact_val,
        'customer_address_val':customer_address_val,
        'customer_type_val':customer_type_val,
        'customer_email':customer_email,
        'industry_type': str(industry_type),
    }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))