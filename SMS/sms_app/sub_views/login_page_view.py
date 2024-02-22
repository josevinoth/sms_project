from django.contrib.sessions import serializers
from django.core.exceptions import ObjectDoesNotExist
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
        print('username',username)
        print('password',password)
        try:
            user_id = User_extInfo.objects.get(user_name=username).id
        except ObjectDoesNotExist:
            messages.error(request, 'User does not exist.')
            return redirect(request.META['HTTP_REFERER'])
        user_name = User_extInfo.objects.get(pk=user_id).user_name
        pwd_1=User_extInfo.objects.get(pk=user_id).password
        request.session['ses_userID'] = user_id
        request.session['first_name'] = user_name
        if password==pwd_1:
            print('Password Matched')
            return redirect('home_page')
        else:
            print('Password Not Matched')
            messages.error(request,'Username Or Password is Incorrect')
            return redirect(request.META['HTTP_REFERER'])
    context = {}
    return render(request, "asset_mgt_app/login.html", context)