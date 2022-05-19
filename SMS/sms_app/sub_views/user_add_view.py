from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import CreateUserForm
from django.contrib.auth.models import User
@login_required(login_url='login_page')
def user_add(request,user_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if user_id == 0:
            form = CreateUserForm()
        else:
            user=User.objects.get(pk=user_id)
            form = CreateUserForm(instance=user)
        return render(request, "asset_mgt_app/user_add.html", {'form': form,'first_name': first_name})
    else:
        if user_id == 0:
            form = CreateUserForm(request.POST)
        else:
            user = User.objects.get(pk=user_id)
            form = CreateUserForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
        return redirect('/SMS/user_list')

# List User
@login_required(login_url='login_page')
def user_list(request):
    first_name = request.session.get('first_name')
    context = {'user_list' : User.objects.all(),'first_name': first_name,}
    return render(request,"asset_mgt_app/employee_list.html",context)

#Delete User
@login_required(login_url='login_page')
def user_delete(request,user_id):
    user = User.objects.get(pk=user_id)
    user.delete()
    return redirect('/SMS/user_list')