from django.shortcuts import render, redirect
from ..forms import GateinaddForm,LoadingbayddForm
from django.contrib.auth.decorators import login_required
from ..models import Gatein_info,Loadingbay_Info

# Add WH Job
@login_required(login_url='login_page')
def wh_job_add(request, gatein_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if gatein_id == 0:
            gatein_form = GateinaddForm()
            loadingbay_form=LoadingbayddForm()
            context = {
                'first_name': first_name,
                'gatein_form': gatein_form,
                'loadingbay_form': loadingbay_form,
            }
        else:
            gatein_info = Gatein_info.objects.get(pk=gatein_id)
            get_jobnum=Gatein_info.objects.get(pk=gatein_id).gatein_job_no
            request.session['ses_jobnum'] = get_jobnum
            print(get_jobnum)
            set_jobnum = request.session.get('ses_jobnum')
            loadingbay_info=Loadingbay_Info.objects.get(lb_job_no=set_jobnum)
            loadingbay_form = LoadingbayddForm(instance=loadingbay_info)
            loadingbay_list = Loadingbay_Info.objects.filter(lb_job_no=set_jobnum)
            gatein_form = GateinaddForm(instance=gatein_info)
            gatein_list = Gatein_info.objects.filter(gatein_job_no=set_jobnum)
            context = {
                'gatein_form': gatein_form,
                'gatein_list': gatein_list,
                'first_name': first_name,
                'loadingbay_form': loadingbay_form,
                'loadingbay_list': loadingbay_list,
            }
        return render(request, "asset_mgt_app/wh_job_add.html", context)
    else:
        if gatein_id == 0:
            gatein_form = GateinaddForm(request.POST)
            loadingbay_form = LoadingbayddForm(request.POST)
        else:
            gatein_info = Gatein_info.objects.get(pk=gatein_id)
            get_jobnum = Gatein_info.objects.get(pk=gatein_id).gatein_job_no
            print(get_jobnum)
            set_jobnum = request.session.get('ses_jobnum')
            loadingbay_info = Loadingbay_Info.objects.get(lb_job_no=set_jobnum)
            gatein_form = GateinaddForm(request.POST, instance=gatein_info)
            loadingbay_form = LoadingbayddForm(instance=loadingbay_info)
        if gatein_form.is_valid():
            gatein_form.save()
        elif loadingbay_form.is_valid():
            loadingbay_form.save()
        # return redirect(request.META['HTTP_REFERER'])
        return redirect('/SMS/wh_job_list')

# List WH Job
@login_required(login_url='login_page')
def wh_job_list(request):
    first_name = request.session.get('first_name')
    context = {'Gatein_list' : Gatein_info.objects.all(),'first_name': first_name,}
    return render(request,"asset_mgt_app/wh_job_list.html",context)

#Delete WH Job
@login_required(login_url='login_page')
def wh_job_delete(request,gatein_id):
    wh_job = Gatein_info.objects.get(pk=gatein_id)
    wh_job.delete()
    return redirect('/SMS/wh_job_list')

