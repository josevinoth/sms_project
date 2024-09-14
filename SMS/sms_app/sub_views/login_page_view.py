from django.contrib.sessions import serializers
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from ..models import User_extInfo

def login_page(request):
    request.session['ses_username'] = request.POST.get('username')
    if request.method=='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_id = User.objects.get(username=username).id
        department_id = User_extInfo.objects.get(user=user_id).department.id
        department_name = User_extInfo.objects.get(user=user_id).department.dept_name
        role = User_extInfo.objects.get(user=user_id).emp_role.role_name
        role_id = User_extInfo.objects.get(user=user_id).emp_role.id
        organisation_id = User_extInfo.objects.get(user=user_id).emp_organisation.id
        first_name1 = User.objects.get(pk=user_id).first_name
        last_name=User.objects.get(pk=user_id).last_name
        first_name=first_name1+" " +last_name
        request.session['ses_userID'] = user_id
        user = authenticate(request, username=username,password=password)
        request.session['first_name'] = first_name
        request.session['ses_department_id'] = department_id
        request.session['ses_department_name'] = department_name
        request.session['ses_role_id'] = role_id
        request.session['ses_role'] = role
        request.session['ses_organisation_id'] = organisation_id
        if user is not None:
            login(request,user)
            return redirect('home_page')
        else:
            messages.error(request,'Username Or Password is Incorrect')

    context = {}
    return render(request, "asset_mgt_app/login.html", context)