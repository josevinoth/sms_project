from django.contrib.auth.decorators import login_required
from ..forms import TripclosureaddForm
from ..models import TripclosureInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def tripclosure_add(request,tripclosure_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if tripclosure_id == 0:
            form = TripclosureaddForm()
        else:
            tripclosure = TripclosureInfo.objects.get(pk=tripclosure_id)
            form = TripclosureaddForm(instance=tripclosure)
        return render(request, "asset_mgt_app/tripclosure_add.html", {'form': form,'first_name': first_name})
    else:
        if tripclosure_id == 0:
            form = TripclosureaddForm(request.POST)
        else:
            tripclosure = TripclosureInfo.objects.get(pk=tripclosure_id)
            form = TripclosureaddForm(request.POST,instance=tripclosure)
        if form.is_valid():
            form.save()
        return redirect('/SMS/tripclosure_list')

# List tripclosure
@login_required(login_url='login_page')
def tripclosure_list(request):
    first_name = request.session.get('first_name')
    context = {'tripclosure_list' : TripclosureInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/tripclosure_list.html",context)

#Delete tripclosure
@login_required(login_url='login_page')
def tripclosure_delete(request,tripclosure_id):
    tripclosure = TripclosureInfo.objects.get(pk=tripclosure_id)
    tripclosure.delete()
    return redirect('/SMS/tripclosure_list')