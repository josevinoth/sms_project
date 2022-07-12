from django.shortcuts import render, redirect
from ..forms import GateinaddForm
from django.contrib.auth.decorators import login_required
from ..models import Gatein_info,Loadingbay_Info,DamagereportInfo,Warehouse_goods_info

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
            gatein_info = Gatein_info.objects.get(pk=gatein_id)
            wh_job_id = Gatein_info.objects.get(pk=gatein_id).gatein_job_no
            request.session['ses_gatein_id_nam'] = wh_job_id
            wh_job_id_sess=request.session.get('ses_gatein_id_nam')
            gatein_status = Gatein_info.objects.get(gatein_job_no=wh_job_id).gatein_status #fetch gatein status
            loadingbay_status = Loadingbay_Info.objects.get(lb_job_no=wh_job_id).lb_status  # fetch loadingbay status
            damage_before_status = DamagereportInfo.objects.get(dam_wh_job_num=wh_job_id).dam_status  # fetch damage report status
            loadingbay_list= Loadingbay_Info.objects.filter(lb_job_no=wh_job_id)
            gatein_list=Gatein_info.objects.filter(gatein_job_no=wh_job_id_sess)
            print(wh_job_id)
            print("Gatein Status",gatein_status)
            print("Loadingbay Satus",loadingbay_status)
            print("Damage_before_status", damage_before_status)
            gatein_form = GateinaddForm(instance=gatein_info)
            context = {
                'gatein_form': gatein_form,
                'first_name': first_name,
                'loadingbay_list': loadingbay_list,
                'gatein_list':gatein_list ,
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
                'gatein_status':gatein_status,
                'loadingbay_status':loadingbay_status,
                'damage_before_status':damage_before_status,
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
    gatein = Gatein_info.objects.get(pk=gatein_id)
    gatein.delete()
    return redirect('/SMS/gatein_list')


