from django.contrib.auth.decorators import login_required
from ..forms import DamagereportaddForm
from ..models import DamagereportInfo,Loadingbay_Info,Gatein_info,Warehouse_goods_info
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def damagereport_add(request,damagereport_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if damagereport_id == 0:
            print("I am inside Get add damagereport")
            damagereport_form = DamagereportaddForm()
            ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
            print(ses_gatein_id_nam)
            wh_job_id = ses_gatein_id_nam
            context = {
                'first_name': first_name,
                'damagereport_form': damagereport_form,
                'loadingbay_list': Loadingbay_Info.objects.filter(lb_job_no=wh_job_id),
                'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
                'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
                'wh_job_id': wh_job_id,
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
            }
        else:
            print("I am inside get edit damagereport")
            ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
            print(ses_gatein_id_nam)
            wh_job_id = ses_gatein_id_nam
            damagereport_info=DamagereportInfo.objects.get(dam_wh_job_num=wh_job_id)
            damagereport_form = DamagereportaddForm(instance=damagereport_info)
            context = {
                'damagereport_form': damagereport_form,
                'first_name': first_name,
                'loadingbay_list': Loadingbay_Info.objects.filter(lb_job_no=wh_job_id),
                'gatein_list': Gatein_info.objects.filter(gatein_job_no=wh_job_id),
                'damagereport_list': DamagereportInfo.objects.filter(dam_wh_job_num=wh_job_id),
                'wh_job_id': wh_job_id,
                'goods_list': Warehouse_goods_info.objects.filter(wh_job_no=wh_job_id),
            }
        return render(request, "asset_mgt_app/damagereport_add.html", context)
    else:
        if damagereport_id == 0:
            print("I am inside post add damagereport")
            damagereport_form = DamagereportaddForm(request.POST)
        else:
            print("I am inside post edit damagereport")
            ses_gatein_id_nam = request.session.get('ses_gatein_id_nam')
            print(ses_gatein_id_nam)
            wh_job_id = ses_gatein_id_nam
            damagereport_info = DamagereportInfo.objects.get(pk=damagereport_id)
            damagereport_form = DamagereportaddForm(request.POST,instance=damagereport_info)
        if damagereport_form.is_valid():
            damagereport_form.save()
        # return redirect(request.META['HTTP_REFERER'])
        return redirect('/SMS/gatein_list')

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