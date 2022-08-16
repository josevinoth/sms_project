from django.shortcuts import render, redirect
from ..forms import GateinaddForm
from django.contrib.auth.decorators import login_required
from ..models import Gatein_info,Loadingbay_Info,DamagereportInfo,Warehouse_goods_info,DamagereportImages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages

# Add WH Job
@login_required(login_url='login_page')
def gatein_add(request, gatein_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if gatein_id == 0:
            print("I am inside Get add Gatein")
            gatein_form = GateinaddForm()
            ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
            print(ses_gatein_id_nam)
            wh_job_id = ses_gatein_id_nam
            context = {
                'first_name': first_name,
                'gatein_form': gatein_form,
                'loadingbay_list': Loadingbay_Info.objects.filter(lb_job_no=wh_job_id),
                'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
                'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
                'wh_job_id': wh_job_id,
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
            }
        else:
            print("I am inside get edit Gatein")
            wh_job_id = Gatein_info.objects.get(pk=gatein_id).gatein_job_no
            wh_customer_name = Gatein_info.objects.get(pk=gatein_id).gatein_customer
            wh_customer_type = Gatein_info.objects.get(pk=gatein_id).gatein_customer_type
            wh_invoice = Gatein_info.objects.get(pk=gatein_id).gatein_invoice
            wh_total_packages = Gatein_info.objects.get(pk=gatein_id).gatein_no_of_pkg
            request.session['ses_gatein_id_nam'] = wh_job_id
            request.session['ses_customer_name'] = str(wh_customer_name)
            request.session['ses_customer_type'] = str(wh_customer_type)
            request.session['ses_wh_invoice'] = wh_invoice
            request.session['ses_gatein_no_of_pkg'] = wh_total_packages
            print("Customer Name",wh_customer_name)
            print("Customer Type",wh_customer_type)
            print("Invoice",wh_invoice)
            print("wh_total_packages",wh_total_packages)
            wh_job_id_sess=request.session.get('ses_gatein_id_nam')
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
                print(list(goods_status))
                goods_status_list = list(goods_status)
                if goods_status_list != []:
                    if goods_status_list[0] == 5:
                        result = all(element == (goods_status_list[0]) for element in (goods_status_list))
                    else:
                        result = False
                else:
                    result = False
                print(result)
                if (result):
                    damage_after_status = "Completed"  # get goods status
                    print(damage_after_status)
                else:
                    damage_after_status = "No Status"  # get goods status
                    print(damage_after_status)
            except ObjectDoesNotExist:
                damage_after_status = "No Status"
            # Warehousein Status Check
            try:
                warehousein_status = Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id).values_list(
                    'wh_check_in_out', flat=True)  # count records
                print(list(warehousein_status))
                warehousein_status_list = list(warehousein_status)
                if warehousein_status_list != []:
                    if warehousein_status_list[0] == 1:
                        result = all(element == (warehousein_status_list[0]) for element in (warehousein_status_list))
                    else:
                        result = False
                else:
                    result = False
                print(result)
                if (result):
                    warehousein_status = "Completed"  # get goods status
                    print(warehousein_status)
                else:
                    warehousein_status = "No Status"  # get goods status
                    print(warehousein_status)
            except ObjectDoesNotExist:
                warehousein_status = "No Status"

            loadingbay_list= Loadingbay_Info.objects.filter(lb_job_no=wh_job_id)
            gatein_list=Gatein_info.objects.filter(gatein_job_no=wh_job_id_sess)
            goods_list= Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id)

            print("Wh_job_id",wh_job_id)
            print("Gatein Status",gatein_status)
            print("Loadingbay Satus",loadingbay_status)
            print("Damage_before_status", damage_before_status)
            print("Damage_After_status", damage_after_status)
            print("Ware_Housein_status", warehousein_status)
            print("Gatein ID", gatein_id)
            gatein_info = Gatein_info.objects.get(pk=gatein_id)
            gatein_form = GateinaddForm(instance=gatein_info)
            context = {
                'gatein_form': gatein_form,
                'first_name': first_name,
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
            gatein_form.save()
        # return redirect(request.META['HTTP_REFERER'])
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


