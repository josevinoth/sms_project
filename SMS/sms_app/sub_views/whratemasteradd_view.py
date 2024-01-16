from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from ..forms import WhratemasteraddForm
from ..models import WhratemasterInfo
from django.shortcuts import render, redirect

# List whratemaster
@login_required(login_url='login_page')
def whratemaster_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    whratemaster_list= (WhratemasterInfo.objects.all()).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(whratemaster_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
                'whratemaster_list':whratemaster_list,
                'page_obj':page_obj,
                'first_name': first_name,
                'user_id':user_id,
            }
    return render(request, "asset_mgt_app/whratemaster_list.html", context)


# Add whratemaster
@login_required(login_url='login_page')
def whratemaster_add(request, whratemaster_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print('user_id',user_id)
    if request.method == "GET":
        if whratemaster_id == 0:
            form = WhratemasteraddForm()
        else:
            whratemasterinfo = WhratemasterInfo.objects.get(pk=whratemaster_id)
            form = WhratemasteraddForm(instance=whratemasterinfo)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
        }
        return render(request, "asset_mgt_app/whratemaster_add.html", context)
    else:
        if whratemaster_id == 0:
            form = WhratemasteraddForm(request.POST)
        else:
            whratemasterinfo = WhratemasterInfo.objects.get(pk=whratemaster_id)
            form = WhratemasteraddForm(request.POST, instance=whratemasterinfo)
        if form.is_valid():
            form.save()
            print("Main form saved")
        else:
            print("Main form not saved")
        return redirect('/SMS/whratemaster_list')


# Delete whratemaster
@login_required(login_url='login_page')
def whratemaster_delete(request, whratemaster_id):
    whratemasterinfo = WhratemasterInfo.objects.get(pk=whratemaster_id)
    whratemasterinfo.delete()
    return redirect('/SMS/whratemaster_list')