from django.contrib.auth.decorators import login_required
from ..forms import CustomerdepartmentaddForm
from ..models import CustomerdepartmentInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def customerdepartment_add(request,customerdepartment_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if customerdepartment_id == 0:
            form = CustomerdepartmentaddForm()
        else:
            customerdepartment=CustomerdepartmentInfo.objects.get(pk=customerdepartment_id)
            form = CustomerdepartmentaddForm(instance=customerdepartment)
        return render(request, "asset_mgt_app/customerdepartment_add.html", {'form': form,'first_name': first_name})
    else:
        if customerdepartment_id == 0:
            form = CustomerdepartmentaddForm(request.POST)
        else:
            customerdepartment = CustomerdepartmentInfo.objects.get(pk=customerdepartment_id)
            form = CustomerdepartmentaddForm(request.POST,instance=customerdepartment)
        if form.is_valid():
            form.save()
        return redirect('/SMS/customerdepartment_list')

# List customerdepartment
@login_required(login_url='login_page')
def customerdepartment_list(request):
    first_name = request.session.get('first_name')
    context = {'customerdepartment_list' : CustomerdepartmentInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/customerdepartment_list.html",context)

#Delete customerdepartment
@login_required(login_url='login_page')
def customerdepartment_delete(request,customerdepartment_id):
    customerdepartment = CustomerdepartmentInfo.objects.get(pk=customerdepartment_id)
    customerdepartment.delete()
    return redirect('/SMS/customerdepartment_list')