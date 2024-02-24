from django.contrib.auth.decorators import login_required
from ..forms import DepartmentaddForm
from ..models import Department_info
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def department_add(request,department_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if department_id == 0:
            form = DepartmentaddForm()
        else:
            departmnent=Department_info.objects.get(pk=department_id)
            form = DepartmentaddForm(instance=departmnent)
        return render(request, "asset_mgt_app/department_add.html", {'form': form,'first_name': first_name})
    else:
        if department_id == 0:
            form = DepartmentaddForm(request.POST)
        else:
            department = Department_info.objects.get(pk=department_id)
            form = DepartmentaddForm(request.POST,instance=department)
        if form.is_valid():
            form.save()
        return redirect('/SMS/department_list')

# List Department
@login_required(login_url='login_page')
def department_list(request):
    first_name = request.session.get('first_name')
    context = {'department_list' : Department_info.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/department_list.html",context)

#Delete Department
@login_required(login_url='login_page')
def department_delete(request,department_id):
    department = Department_info.objects.get(pk=department_id)
    department.delete()
    return redirect('/SMS/department_list')