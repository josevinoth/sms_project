import json
from datetime import timedelta, date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
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
                    messages.success(request, 'Record Created Successfully')
                    return redirect('/SMS/locationmaster_list')
                else:
                    print(form.errors)
                    messages.error(request, 'Form is invalid. Please check the fields.')
                    # Re-render with errors
                    context = {
                        'form': form,
                        'first_name': first_name,
                        'area_occupied': 0,
                        'volume_occupied': 0,
                    }
                    return render(request, "asset_mgt_app/locationmaster_add.html", context)
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
                    return redirect('/SMS/locationmaster_list')
                else:
                    print('Form Not Saved Successfully')
                    print(form.errors)
                    messages.error(request, 'Record Not Updated Successfully. ' + str(form.errors))
                    context = {
                        'form': form,
                        'first_name': first_name,
                    }
                    return render(request, "asset_mgt_app/locationmaster_add.html", context)
            # return redirect('/SMS/locationmaster_list')

# List locationmaster
@login_required(login_url='login_page')
def locationmaster_list(request):
    first_name = request.session.get('first_name')
    # warehousevolme_area_calc(request) # Removed to speed up page load!
    context =   {
                    'first_name': first_name
                }
    return render(request,"asset_mgt_app/locationmaster_list.html",context)

#Calculate warehouse area and volume
@login_required(login_url='login_page')
def warehousevolme_area_calc(request):
    print("Inside warehousevolme_area_calc")
    # Fetch all LocationmasterInfo objects once
    warehouse_objects = list(LocationmasterInfo.objects.all())
    
    # Bulk aggregate occupied volume for all locations
    volume_stats = Warehouse_goods_info.objects.filter(
        wh_check_in_out=1
    ).values('wh_branch_id', 'wh_unit_id', 'wh_bay_id').annotate(
        total_vol=Sum('wh_goods_volume_weight')
    )
    
    # Bulk aggregate occupied area for all locations
    area_stats = Warehouse_goods_info.objects.filter(
        wh_check_in_out=1,
        wh_stack_layer__in=[1, 2]
    ).values('wh_branch_id', 'wh_unit_id', 'wh_bay_id').annotate(
        total_area=Sum('wh_goods_area')
    )
    
    vol_dict = {(s['wh_branch_id'], s['wh_unit_id'], s['wh_bay_id']): s['total_vol'] or 0 for s in volume_stats}
    area_dict = {(s['wh_branch_id'], s['wh_unit_id'], s['wh_bay_id']): s['total_area'] or 0 for s in area_stats}
    
    for loc in warehouse_objects:
        key = (loc.lm_wh_location_id, loc.lm_wh_unit_id, loc.lm_areaside_id)
        volume_occupied = vol_dict.get(key, 0)
        area_occupied = area_dict.get(key, 0)

        # Use attributes from the 'loc' object directly
        total_volume = loc.lm_total_volume or 0
        total_area = loc.lm_size or 0

        # Self-healing: If total area or volume is 0, try to calculate from dimensions
        if total_area == 0 and loc.lm_length > 0 and loc.lm_width > 0:
            total_area = round(loc.lm_length * loc.lm_width, 2)
            loc.lm_size = total_area
        
        if total_volume == 0 and loc.lm_length > 0 and loc.lm_width > 0:
            height = loc.lm_height if loc.lm_height > 0 else 5.0 # Default height 5.0 as discussed
            if loc.lm_height == 0:
                loc.lm_height = height
            total_volume = round(loc.lm_length * loc.lm_width * height, 2)
            loc.lm_total_volume = total_volume

        # Calculate Available Volume and Area
        available_volume = total_volume - volume_occupied
        available_area = total_area - area_occupied

        # Update the specific object 'loc' instead of filtering again
        loc.lm_available_area = round(available_area, 2)
        loc.lm_available_volume = round(available_volume, 2)
        loc.lm_volume_occupied = round(volume_occupied, 2)
        loc.lm_area_occupied = round(area_occupied, 2)
        
    # Bulk update all locations in one query
    LocationmasterInfo.objects.bulk_update(
        warehouse_objects, 
        ['lm_available_area', 'lm_available_volume', 'lm_volume_occupied', 'lm_area_occupied', 'lm_size', 'lm_total_volume', 'lm_height']
    )
    
    return
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


@login_required(login_url='login_page')
def locationmaster_list_ajax(request):
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')

    queryset = LocationmasterInfo.objects.select_related('lm_wh_location', 'lm_wh_unit', 'lm_areaside').all()

    if search_value:
        queryset = queryset.filter(
            Q(lm_wh_location__loc_name__icontains=search_value) |
            Q(lm_wh_unit__unit_name__icontains=search_value) |
            Q(lm_areaside__bay_bayname__icontains=search_value)
        )

    total_records = LocationmasterInfo.objects.count()
    filtered_records = queryset.count()

    order_column_index = request.GET.get('order[0][column]', 1)
    order_dir = request.GET.get('order[0][dir]', 'desc')

    columns = [
        'edit', 'lm_wh_location__loc_name', 'lm_wh_unit__unit_name', 'lm_areaside__bay_bayname',
        'lm_size', 'lm_area_occupied', 'lm_available_area',
        'lm_total_volume', 'lm_volume_occupied', 'lm_available_volume', 'id'
    ]

    if int(order_column_index) < len(columns):
        order_by = columns[int(order_column_index)]
        if order_by and order_by not in ['id', 'edit']:
            if order_dir == 'desc':
                order_by = f"-{order_by}"
            queryset = queryset.order_by(order_by)
    else:
        queryset = queryset.order_by('-id')

    data = []
    for item in queryset[start:start+length]:
        update_url = reverse('locationmaster_update', args=[item.id])
        delete_url = reverse('locationmaster_delete', args=[item.id])
        csrf_token = request.COOKIES.get('csrftoken', '')
        
        edit_btn = f'''<div class="d-flex justify-content-center">
            <a class="btn btn-submit" style="background: linear-gradient(135deg, #fbbf24, #f59e0b); border: none; color: white;" href="{update_url}" >
                <i class="far fa-edit"></i>
            </a>
        </div>'''
        
        delete_btn = f'''<div class="d-flex justify-content-center">
            <form action="{delete_url}" method="post" onsubmit="return confirm('Are you sure you want to delete this record?');">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                <button type="submit" class="btn shadow-sm" style="background: white; color: #dc3545; border-radius: 20px; border: 1px solid #f1f3f5; padding: 6px 16px; display: inline-flex; align-items: center; justify-content: center;">
                    <i class="fas fa-trash-alt"></i>
                </button>
            </form>
        </div>'''

        data.append({
            'edit': edit_btn,
            'lm_wh_location': str(item.lm_wh_location.loc_name) if hasattr(item, 'lm_wh_location') and item.lm_wh_location else '',
            'lm_wh_unit': str(item.lm_wh_unit.unit_name) if hasattr(item, 'lm_wh_unit') and item.lm_wh_unit else '',
            'lm_areaside': str(item.lm_areaside.bay_bayname) if hasattr(item, 'lm_areaside') and item.lm_areaside else '',
            'lm_size': item.lm_size or 0,
            'lm_area_occupied': item.lm_area_occupied or 0,
            'lm_available_area': item.lm_available_area or 0,
            'lm_total_volume': item.lm_total_volume or 0,
            'lm_volume_occupied': item.lm_volume_occupied or 0,
            'lm_available_volume': item.lm_available_volume or 0,
            'delete': delete_btn
        })

    return JsonResponse({
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    })
