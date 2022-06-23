from django.contrib.auth.decorators import login_required
from ..forms import PermittypeaddForm
from ..models import PermittypeInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def permittype_add(request,permittype_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if permittype_id == 0:
            form = PermittypeaddForm()
        else:
            permittype=PermittypeInfo.objects.get(pk=permittype_id)
            form = PermittypeaddForm(instance=permittype)
        return render(request, "asset_mgt_app/role_add.html", {'form': form,'first_name': first_name})
    else:
        if permittype_id == 0:
            form = PermittypeaddForm(request.POST)
        else:
            permittype = PermittypeInfo.objects.get(pk=permittype_id)
            form = PermittypeaddForm(request.POST,instance=permittype)
        if form.is_valid():
            form.save()
        return redirect('/SMS/permittype_list')

# List permittype
@login_required(login_url='login_page')
def permittype_list(request):
    first_name = request.session.get('first_name')
    context = {'permittype_list' : PermittypeInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/permittype_list.html",context)

#Delete permittype
@login_required(login_url='login_page')
def permittype_delete(request,permittype_id):
    permittype = PermittypeInfo.objects.get(pk=permittype_id)
    permittype.delete()
    return redirect('/SMS/permittype_list')