from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import EmployeeaddForm
from ..models import Employee
from django.contrib import messages

@login_required(login_url='login_page')
def emp_add(request,emp_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if emp_id == 0:
            form = EmployeeaddForm()
        else:
            emp=Employee.objects.get(pk=emp_id)
            form = EmployeeaddForm(instance=emp)
        return render(request, "asset_mgt_app/emp_add.html", {'form': form,'first_name': first_name})
    else:
        if emp_id == 0:
            form = EmployeeaddForm(request.POST)
        else:
            emp = Employee.objects.get(pk=emp_id)
            form = EmployeeaddForm(request.POST,instance=emp)
        if form.is_valid():
            form.save()
        return redirect('/SMS/emp_list')

# List Emp
@login_required(login_url='login_page')
def emp_list(request):
    first_name = request.session.get('first_name')
    context = {'emp_list' : Employee.objects.all(),'first_name': first_name,}
    return render(request,"asset_mgt_app/emp_list.html",context)

#Delete Emp
@login_required(login_url='login_page')
def emp_delete(request,emp_id):
    emp = Employee.objects.get(pk=emp_id)
    emp.delete()
    return redirect('/SMS/emp_list')

#emp Registration
def emp_registration_page(request):
      form = EmployeeaddForm()
      if request.method=='POST':
        form=EmployeeaddForm(request.POST)
      if form.is_valid():
        form.save()
        # user = form.cleaned_data.get('full_name')
        # messages.success(request,'Account was created for '+ user)
        return redirect('login_page')


      context={'form':form}
      return render(request, "asset_mgt_app/emp_add.html",context)

