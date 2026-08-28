from django.contrib import messages
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
from ..forms import DamagereportaddForm,DamagereportImagesForm
from ..models import PictureImage,Location_info,DamagereportInfo,Loadingbay_Info,Gatein_info,Warehouse_goods_info,DamagereportImages,damage_image_type_info
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from ..models import User_extInfo
from random import randint
# from ..views import picture_add

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

    # Aggregate invoice weight and qty from Inspection (Warehouse_goods_info)
    goods_totals = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).aggregate(
        total_invoice_weight=Sum('wh_invoice_weight_unit'),
        total_invoice_qty=Sum('wh_invoice_qty'),
    )
    invoice_weight_from_inspection = goods_totals.get('total_invoice_weight') or 0.0
    invoice_qty_from_inspection = goods_totals.get('total_invoice_qty') or 0

    if request.method == "GET":
        if damagereport_id == 0:
            print("I am inside Get add damagereport")
            damagereport_form = DamagereportaddForm(initial={
                'dam_invoice_weight': invoice_weight_from_inspection,
                'dam_invoice_qty': invoice_qty_from_inspection,
                'dam_checkin_qty': invoice_qty_from_inspection,
            })
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
                'invoice_weight_from_inspection': invoice_weight_from_inspection,
                'invoice_qty_from_inspection': invoice_qty_from_inspection,
            }
        else:
            print("I am inside get edit damagereport")
            request.session['ses_damagereport_id'] = damagereport_id
            damagereport_info=DamagereportInfo.objects.get(dam_wh_job_num=wh_job_id)
            # On edit: keep the saved values but refresh invoice weight/qty from Inspection
            damagereport_info.dam_invoice_weight = invoice_weight_from_inspection
            damagereport_info.dam_invoice_qty = invoice_qty_from_inspection
            damagereport_form = DamagereportaddForm(instance=damagereport_info)
            damagereportimg_info = DamagereportImages.objects.get(damimage_wh_job_num=wh_job_id)
            damagereportimg_form = DamagereportImagesForm(request.FILES, instance=damagereportimg_info)
            picture_list = PictureImage.objects.filter(pi_reference=damagereport_id)  # Fetch all the pictures
            pictures = damage_image_type_info.objects.all()
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
                'picture_list': picture_list,
                'damagereport_id': damagereport_id,
                'pictures' : pictures,
                'invoice_weight_from_inspection': invoice_weight_from_inspection,
                'invoice_qty_from_inspection': invoice_qty_from_inspection,
            }
        return render(request, "asset_mgt_app/damagereport_add.html", context)
    else:
        if damagereport_id == 0:
            print("I am inside post add damagereport")
            damagereport_form = DamagereportaddForm(request.POST)
            damagereportimg_form=DamagereportImagesForm(request.POST,request.FILES)
            if damagereport_form.is_valid():
                print("Main Form Saved")

                # Save the Main Form but don't commit immediately
                damagereport_instance = damagereport_form.save(commit=False)

                if damagereportimg_form.is_valid():
                    print("SubForm Saved")
                    damagereportimg_form.save()
                else:
                    print("Sub Form Not saved")

                # Generate Damage GRN number based on financial year
                fy = get_financial_year()
                branch_id = get_session_branch_id(request)
                branch_code = get_branch_code(branch_id)
                prefix = f"{fy}_{branch_code}_DR_"
                wh_grn_num_next = generate_next_number(DamagereportInfo, 'dam_GRN_num', prefix, 6)

                # Assigning GRN number and saving the form
                damagereport_instance.dam_GRN_num = wh_grn_num_next
                damagereport_instance.save()

                # Redirecting after successful update
                messages.success(request, 'Record Updated Successfully')
                return redirect(f'damagereport_update/{damagereport_instance.id}')
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
            # url = 'damagereport_update/' + str(damagereport_id)
            # return redirect(url)


# List damagereport
@login_required(login_url='login_page')
def damagereport_list(request):
    first_name = request.session.get('first_name')
    context = {'damagereport_list' : DamagereportInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/damagereport_list.html",context)

#Delete damagereport
@login_required(login_url='login_page')
def damagereport_delete(request,damagereport_id):
    damagereport = DamagereportInfo.objects.get(pk=damagereport_id)
    damagereport.delete()
    return redirect('/SMS/damagereport_list')



from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse

@login_required(login_url='login_page')
def damagereport_list_ajax(request):
    draw = int(request.GET.get('draw', 1))
    start = int(request.GET.get('start', 0))
    length = int(request.GET.get('length', 10))
    search_value = request.GET.get('search[value]', '')

    queryset = DamagereportInfo.objects.all()

    if search_value:
        queryset = queryset.filter(
            Q(dam_wh_job_num__icontains=search_value) |
            Q(dam_damage_type__damage_name__icontains=search_value) |
            Q(dam_GRN_num__icontains=search_value)
        )

    total_records = DamagereportInfo.objects.count()
    filtered_records = queryset.count()
    
    # Ordering
    order_column_index = request.GET.get('order[0][column]', 0)
    order_dir = request.GET.get('order[0][dir]', 'asc')
    
    columns = ['dam_wh_job_num', 'dam_damage_type', 'dam_GRN_num']
    if int(order_column_index) < len(columns):
        order_by = columns[int(order_column_index)]
        if order_dir == 'desc':
            order_by = f"-{order_by}"
        queryset = queryset.order_by(order_by)

    data = []
    for item in queryset[start:start+length]:
        update_url = reverse('damagereport_update', args=[item.id])
        delete_url = reverse('damagereport_delete', args=[item.id])
        csrf_token = request.COOKIES.get('csrftoken', '')
        
        edit_btn = f'<a href="{update_url}" class="btn btn-outline-primary" style="border-radius: 20px; padding: 4px 15px;"><i class="far fa-edit"></i></a>'
        
        # We need a small form for delete, but Datatables usually expects raw html
        delete_btn = f'''<form action="{delete_url}" method="post" onclick="return confirm('Are you sure?');" style="margin:0; display:inline;">
            <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
            <button type="submit" class="btn btn-outline-danger" style="border-radius: 20px; padding: 4px 15px;">
                <i class="fas fa-trash-alt"></i>
            </button>
        </form>'''
        
        report_btn = '<a href="#" class="btn btn-outline-info" style="border-radius: 20px; padding: 4px 15px;"><i class="fa fa-book"></i></a>'

        data.append({
            'dam_wh_job_num': item.dam_wh_job_num or '',
            'dam_damage_type': str(item.dam_damage_type.damage_name) if item.dam_damage_type else 'None',
            'dam_GRN_num': item.dam_GRN_num or '',
            'report': report_btn,
            'edit': edit_btn,
            'delete': delete_btn
        })

    return JsonResponse({
        'draw': draw,
        'recordsTotal': total_records,
        'recordsFiltered': filtered_records,
        'data': data
    })
