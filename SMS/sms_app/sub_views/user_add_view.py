from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import CreateUserForm,UserextForm,EmpeditForm,UserexteditForm
from django.contrib.auth.models import User
from ..models import User_extInfo
@login_required(login_url='login_page')
def user_add(request,user_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if user_id == 0:
            form = EmpeditForm()
            user_ext_edit_form = UserexteditForm()
        else:
            user=User.objects.get(pk=user_id)
            user_ext=User_extInfo.objects.get(user_id=user_id)
            form = EmpeditForm(instance=user)
            user_ext_edit_form = UserexteditForm(instance=user_ext)
        return render(request, "asset_mgt_app/emp_add.html", {'form': form,'user_ext_edit_form': user_ext_edit_form,'first_name': first_name})
    else:
        if user_id == 0:
            form = EmpeditForm(request.POST)
            user_ext_edit_form = UserexteditForm(request.POST)
        else:
            user = User.objects.get(pk=user_id)
            user_ext = User_extInfo.objects.get(user_id=user_id)
            form = EmpeditForm(request.POST,instance=user)
            user_ext_edit_form = UserexteditForm(request.POST,instance=user_ext)
            if form.is_valid() and user_ext_edit_form.is_valid():
            # if form.is_valid():
                user = form.save()
                user_ext = user_ext_edit_form.save(commit=False)
                user_ext.user = user
                user_ext.save()
                form.save()
                user_ext_edit_form.save()
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