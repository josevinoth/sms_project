from django.contrib.auth.decorators import login_required
from ..forms import RoleaddForm
from ..models import RoleInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def role_add(request,role_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if role_id == 0:
            form = RoleaddForm()
        else:
            role=RoleInfo.objects.get(pk=role_id)
            form = RoleaddForm(instance=role)
        return render(request, "asset_mgt_app/role_add.html", {'form': form,'first_name': first_name})
    else:
        if role_id == 0:
            form = RoleaddForm(request.POST)
        else:
            role = RoleInfo.objects.get(pk=role_id)
            form = RoleaddForm(request.POST,instance=role)
        if form.is_valid():
            form.save()
        return redirect('/SMS/role_list')

# List role
@login_required(login_url='login_page')
def role_list(request):
    first_name = request.session.get('first_name')
    context = {'role_list' : RoleInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/role_list.html",context)

#Delete role
@login_required(login_url='login_page')
def role_delete(request,role_id):
    role = RoleInfo.objects.get(pk=role_id)
    role.delete()
    return redirect('/SMS/role_list')