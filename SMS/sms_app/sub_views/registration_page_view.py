from django.shortcuts import render, redirect
from ..forms import CreateUserForm
from django.contrib import messages

def registration_page(request):
    if request.user.is_authenticated:
        return redirect('home_page')
    else:
        form = CreateUserForm()
        if request.method=='POST':
            form=CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('first_name')
                messages.success(request,'Account was created for '+ user)
                return redirect('login_page')


        context={'form':form}
        return render(request, "asset_mgt_app/registration_form.html",context)
