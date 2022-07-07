from django.shortcuts import render, redirect
from ..forms import LoadingbayddForm
from django.contrib.auth.decorators import login_required
from ..models import Gatein_info,Loadingbay_Info,DamagereportInfo,Warehouse_goods_info

# Add WH Job
@login_required(login_url='login_page')
def loadingbay_add(request, loadingbay_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if loadingbay_id == 0:
            print("I am inside Get add Loading bay")
            loadingbay_form = LoadingbayddForm()
            ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
            print(ses_gatein_id_nam)
            wh_job_id=ses_gatein_id_nam
            context = {
                'first_name': first_name,
                'loadingbay_form': loadingbay_form,
                'wh_job_id': wh_job_id,
                'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
                'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
            }
        else:
            print("I am inside get edit loading bay")
            ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
            print(ses_gatein_id_nam)
            wh_job_id=ses_gatein_id_nam
            loadingbay_info = Loadingbay_Info.objects.get(lb_job_no=wh_job_id)
            loadingbay_form = LoadingbayddForm(instance=loadingbay_info)
            context = {
                'loadingbay_form': loadingbay_form,
                'first_name': first_name,
                'loadingbay_list': Loadingbay_Info.objects.filter(lb_job_no=wh_job_id),
                'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
                'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
                'wh_job_id':wh_job_id,
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
            }
        return render(request, "asset_mgt_app/loadingbay_add.html", context)
    else:
        if loadingbay_id == 0:
            print("I am inside post add Loading bay")
            loadingbay_form = LoadingbayddForm(request.POST)
        else:
            print("I am inside post edit Loading bay")
            ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
            print(ses_gatein_id_nam)
            wh_job_id = ses_gatein_id_nam
            # loadingbay_id = ses_gatein_id_nam
            loadingbay_info = Loadingbay_Info.objects.get(pk=loadingbay_id)
            loadingbay_form = LoadingbayddForm(request.POST, instance=loadingbay_info)
        if loadingbay_form.is_valid():
            loadingbay_form.save()
        # return redirect(request.META['HTTP_REFERER'])
        return redirect('/SMS/gatein_list')

# # List WH Job
# @login_required(login_url='login_page')
# def gatein_list(request):
#     first_name = request.session.get('first_name')
#     context = {'Gatein_list' : Gatein_info.objects.all(),'first_name': first_name,}
#     return render(request,"asset_mgt_app/gatein_list.html",context)
#
# #Delete WH Job
# @login_required(login_url='login_page')
# def gatein_delete(request,gatein_id):
#     gatein = Gatein_info.objects.get(pk=gatein_id)
#     gatein.delete()
#     return redirect('/SMS/gatein_list')


