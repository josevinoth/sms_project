from django.contrib.auth.decorators import login_required
from ..forms import StatusaddForm
from ..models import StatusList
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def status_add(request,status_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if status_id == 0:
            form = StatusaddForm()
        else:
            status=StatusList.objects.get(pk=status_id)
            form = StatusaddForm(instance=status)
        return render(request, "asset_mgt_app/status_add.html", {'form': form,'first_name': first_name})
    else:
        if status_id == 0:
            form = StatusaddForm(request.POST)
        else:
            status = StatusList.objects.get(pk=status_id)
            form = StatusaddForm(request.POST,instance=status)
        if form.is_valid():
            form.save()
        return redirect('/SMS/status_list')

# List status
@login_required(login_url='login_page')
def status_list(request):
    first_name = request.session.get('first_name')
    context = {'status_list' : StatusList.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/status_list.html",context)

#Delete status
@login_required(login_url='login_page')
def status_delete(request,status_id):
    status = StatusList.objects.get(pk=status_id)
    status.delete()
    return redirect('/SMS/status_list')