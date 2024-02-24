from django.contrib.auth.decorators import login_required
from ..forms import AxletypeaddForm
from ..models import AxletypeInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def axletype_add(request,axletype_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if axletype_id == 0:
            form = AxletypeaddForm()
        else:
            axletype=AxletypeInfo.objects.get(pk=axletype_id)
            form = AxletypeaddForm(instance=axletype)
        return render(request, "asset_mgt_app/axletype_add.html", {'form': form,'first_name': first_name})
    else:
        if axletype_id == 0:
            form = AxletypeaddForm(request.POST)
        else:
            axletype = AxletypeInfo.objects.get(pk=axletype_id)
            form = AxletypeaddForm(request.POST,instance=axletype)
        if form.is_valid():
            form.save()
        return redirect('/SMS/axletype_list')

# List axletype
@login_required(login_url='login_page')
def axletype_list(request):
    first_name = request.session.get('first_name')
    context = {'axletype_list' : AxletypeInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/axletype_list.html",context)

#Delete axletype
@login_required(login_url='login_page')
def axletype_delete(request,axletype_id):
    axletype = AxletypeInfo.objects.get(pk=axletype_id)
    axletype.delete()
    return redirect('/SMS/axletype_list')