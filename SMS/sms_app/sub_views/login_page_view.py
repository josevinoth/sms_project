from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages

def login_page(request):
    request.session['ses_username'] = request.POST.get('username')
    if request.user.is_authenticated:
        return redirect('home_page')
    else:
        if request.method=='POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user_id = User.objects.get(username=username).id
            first_name1 = User.objects.get(pk=user_id).first_name
            last_name=User.objects.get(pk=user_id).last_name
            first_name=first_name1+" " +last_name
            pwd_1=User.objects.get(pk=user_id).password
            un_1 = User.objects.get(pk=user_id).username
            print(first_name)
            print(un_1)
            print(pwd_1)
            print("Form Username",username)
            print("Form password",password)
            user = authenticate(request, username=username,password=password)
            request.session['first_name'] = first_name
            if user is not None:
                login(request,user)
                return redirect('home_page')
            else:
                messages.info(request,'Username Or Password is Incorrect')

        context = {}
        return render(request, "asset_mgt_app/login.html", context)