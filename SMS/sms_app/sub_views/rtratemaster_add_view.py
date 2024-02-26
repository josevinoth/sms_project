from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..forms import RtratemasteraddForm
from ..models import RtratemasterInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def rtratemaster_add(request,rtratemaster_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if rtratemaster_id == 0:
            form = RtratemasteraddForm()
        else:
            rtratemaster = RtratemasterInfo.objects.get(pk=rtratemaster_id)
            form = RtratemasteraddForm(instance=rtratemaster)
        return render(request, "asset_mgt_app/rtratemaster_add.html", {'form': form,'first_name': first_name})
    else:
        if rtratemaster_id == 0:
            form = RtratemasteraddForm(request.POST)
            if form.is_valid():
                form.save()
                print("Transport route rate master Form saved")
                messages.success(request, 'Record Updated Successfully')
                last_id = (RtratemasterInfo.objects.values_list('id', flat=True)).last()
                print('last_id', last_id)
                url = '/SMS/rtratemaster_update/' + str(last_id)
                print('url', url)
                return redirect(url)
            else:
                print("Transport route rate master not saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
                return redirect(request.META['HTTP_REFERER'])
        else:
            rtratemaster = RtratemasterInfo.objects.get(pk=rtratemaster_id)
            form = RtratemasteraddForm(request.POST,instance=rtratemaster)
            if form.is_valid():
                form.save()
                print("Location Form saved")
                messages.success(request, 'Record Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
            else:
                print("Location Form not saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
                return redirect(request.META['HTTP_REFERER'])
                # return redirect('/SMS/rtratemaster_list')

# List rtratemaster
@login_required(login_url='login_page')
def rtratemaster_list(request):
    first_name = request.session.get('first_name')
    context = {'rtratemaster_list' : RtratemasterInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/rtratemaster_list.html",context)

#Delete rtratemaster
@login_required(login_url='login_page')
def rtratemaster_delete(request,rtratemaster_id):
    rtratemaster = RtratemasterInfo.objects.get(pk=rtratemaster_id)
    rtratemaster.delete()
    return redirect('/SMS/rtratemaster_list')