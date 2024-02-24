from django.contrib.auth.decorators import login_required
from ..forms import registrationaddForm
from ..models import User_extInfo
from django.shortcuts import render, redirect

# @login_required(login_url='login_page')
def user_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    # role = User_extInfo.objects.get(user=user_id).emp_role
    context = {
        'user_list': User_extInfo.objects.all(),
        'first_name': first_name,
        # 'role': role,
    }
    return render(request, "asset_mgt_app/user_list.html", context)

# @login_required(login_url='login_page')
def user_add(request, user_id=0):
    first_name = request.session.get('first_name')
    # user_id = request.session.get('ses_userID')
    # role = User_extInfo.objects.get(user_name=user_id).role
    if request.method == "GET":
        if user_id == 0:
            print("Insie user add get")
            reg_form = registrationaddForm()
            context = {
                'reg_form': reg_form,
                # 'role': role,
                'first_name': first_name,
                'user_id': user_id,
            }
        else:
            print("Insie user edit get")
            userinfo = User_extInfo.objects.get(pk=user_id)
            reg_form = registrationaddForm(instance=userinfo)
            context={
                'reg_form': reg_form,
                # 'role': role,
                'first_name': first_name,
                'user_id': user_id,
            }
        return render(request, "asset_mgt_app/user_registration.html", context)
    else:
        if user_id == 0:
            print("Insie user add post")
            reg_form = registrationaddForm(request.POST)
        else:
            print("Insie user edit get")
            userinfo = User_extInfo.objects.get(pk=user_id)
            reg_form = registrationaddForm(request.POST, instance=userinfo)
        if reg_form.is_valid():
            reg_form.save()
            print('Main Form Saved')
        else:
            print("Main Form Not Saved")
        return redirect('/SMS/login_page')

# Delete Assets
# @login_required(login_url='login_page')
def user_delete(request, user_id):
    print("inside user delete")
    userinfo = User_extInfo.objects.get(pk=user_id)
    userinfo.delete()
    return redirect('/SMS/user_list')