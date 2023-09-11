from django.contrib import messages
from django.shortcuts import render, redirect
from ..forms import LoadingbayddForm,LoadingbayImagesForm
from django.contrib.auth.decorators import login_required
from ..models import TestInfo,WhratemasterInfo,CustomerInfo,Gatein_info,Loadingbay_Info,DamagereportInfo,Warehouse_goods_info,Loadingbayimages_Info,Currency_type
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
import json

# Add WH Job
@login_required(login_url='login_page')
def loadingbay_add(request, loadingbay_id=0):
    first_name = request.session.get('first_name')
    ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
    wh_job_id = request.session.get('ses_gatein_id_nam')
    shipper_invoice = Gatein_info.objects.get(gatein_job_no=wh_job_id).gatein_invoice
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

    ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')

    # //Calculate Crane and Forklift cost
    wh_job_id = request.session.get('ses_gatein_id_nam')
    customer_name = Gatein_info.objects.get(gatein_job_no=wh_job_id).gatein_customer
    customer_id = CustomerInfo.objects.get(cu_name=customer_name).id
    try:
        crane_1st_2hr = WhratemasterInfo.objects.get(whrm_customer_name=customer_id, whrm_charge_type=5).whrm_rate
        crane_nxt_2hr = WhratemasterInfo.objects.get(whrm_customer_name=customer_id, whrm_charge_type=6).whrm_rate
        forklift_1st_2hr = WhratemasterInfo.objects.get(whrm_customer_name=customer_id, whrm_charge_type=4).whrm_rate
        forklift_nxt_2hr = WhratemasterInfo.objects.get(whrm_customer_name=customer_id, whrm_charge_type=7).whrm_rate

    except ObjectDoesNotExist:
        crane_1st_2hr = None
        crane_nxt_2hr = None
        forklift_1st_2hr = None
        forklift_nxt_2hr = None

    if request.method == "GET":
        job_list=list(TestInfo.objects.all().values_list('stock_num',flat=True))
        for i in job_list:
            try:
                arrival_date=TestInfo.objects.get(stock_num=i).date_of_arrival
                print(type(arrival_date))
                Gatein_info.objects.filter(gatein_job_no=i).update(gatein_arrival_date=arrival_date)
            except ObjectDoesNotExist:
                pass
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
                'crane_1st_2hr': crane_1st_2hr,
                'crane_nxt_2hr': crane_nxt_2hr,
                'forklift_1st_2hr': forklift_1st_2hr,
                'forklift_nxt_2hr': forklift_nxt_2hr,
                'shipper_invoice': shipper_invoice,
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
                'crane_1st_2hr': crane_1st_2hr,
                'crane_nxt_2hr': crane_nxt_2hr,
                'forklift_1st_2hr': forklift_1st_2hr,
                'forklift_nxt_2hr': forklift_nxt_2hr,
                'shipper_invoice': shipper_invoice,
            }
        return render(request, "asset_mgt_app/loadingbay_add.html", context)
    else:
        if loadingbay_id == 0:
            print("I am inside post add Loading bay")
            loadingbay_form = LoadingbayddForm(request.POST)
            loadingbayimg_form=LoadingbayImagesForm(request.POST,request.FILES)
            if loadingbay_form.is_valid():
                if crane_1st_2hr == None or crane_nxt_2hr == None or forklift_1st_2hr == None or forklift_nxt_2hr == None:
                    messages.error(request,'Crane or Forklift Charges not available in master for selected Job/Stock Number!')
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    print("Loadingbay Main Form Saved")
                    loadingbay_form.save()
                    messages.success(request, 'Record Updated Successfully')
            else:
                print("Loadingbay Main Form Not saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')

            if loadingbayimg_form.is_valid():
                if crane_1st_2hr == None or crane_nxt_2hr == None or forklift_1st_2hr == None or forklift_nxt_2hr == None:
                    messages.error(request,'Crane or Forklift Charges not available in master for selected Job/Stock Number!')
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    print("Loadingbay SubForm Saved")
                    loadingbayimg_form.save()
            else:
                print("Loadingbay Sub Form Not saved")

            job_num = request.POST.get('lb_job_no')
            job_id = Loadingbay_Info.objects.get(lb_job_no=job_num).id
            url = 'loadingbay_update/' + str(job_id)
            return redirect(url)
        else:
            print("I am inside post edit Loading bay")
            loadingbay_info = Loadingbay_Info.objects.get(pk=loadingbay_id)
            loadingbay_form = LoadingbayddForm(request.POST, instance=loadingbay_info)
            loadingbayimg_info=Loadingbayimages_Info.objects.get(lbimg_job_no=wh_job_id)
            loadingbayimg_form=LoadingbayImagesForm(request.POST,request.FILES,instance=loadingbayimg_info)
            if loadingbay_form.is_valid():
                if crane_1st_2hr == None or crane_nxt_2hr == None or forklift_1st_2hr == None or forklift_nxt_2hr == None:
                    messages.error(request,
                                   'Crane or Forklift Charges not available in master for selected Job/Stock Number!')
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    loadingbay_form.save()
                    print("Loadingbay Main Form Saved")
                    messages.success(request, 'Record Updated Successfully')
            else:
                print("Loadingbay Main Form Not saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')

            if loadingbayimg_form.is_valid():
                if crane_1st_2hr == None or crane_nxt_2hr == None or forklift_1st_2hr == None or forklift_nxt_2hr == None:
                    messages.error(request,'Crane or Forklift Charges not available in master for selected Job/Stock Number!')
                    return redirect(request.META['HTTP_REFERER'])
                else:
                    print("Loadingbay SubForm Saved")
                    loadingbayimg_form.save()
            else:
                print("Loadingbay Sub Form Not saved")
            return redirect(request.META['HTTP_REFERER'])
            # return redirect('/SMS/gatein_list')

@login_required(login_url='login_page')
def load_currency_value(request):
    currency_type = request.GET.get('currency_type')
    # Fetch Currency Value
    currency_value = Currency_type.objects.get(id=currency_type).converision_value
    data = {
        'currency_value': currency_value,
    }
    return HttpResponse(json.dumps(data))

