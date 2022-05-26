from django.shortcuts import render, redirect
from ..forms import CreateUserForm,UserextForm
from django.contrib import messages

def registration_page(request):
    # form = CreateUserForm()
    # user_ext_form = UserextForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        user_ext_form=UserextForm(request.POST)
        if form.is_valid() and user_ext_form.is_valid():
            user= form.save()
            user_ext= user_ext_form.save(commit=False)
            user_ext.user=user
            user_ext.save()
            # messages.success(request, 'Account was created for ' + user)
            return redirect('login_page')
    else:
        form = CreateUserForm()
        user_ext_form = UserextForm()
    context = {'user_ext_form': user_ext_form,'form': form}
    return render(request, "asset_mgt_app/registration_form.html",context)
    # if request.user.is_authenticated:
    #     return redirect('home_page')
    # else:
    #     form = CreateUserForm()
    #     user_ext_form = UserextForm()
    #     if request.method=='POST':
    #         form=CreateUserForm(request.POST)
    #         user_ext_form=UserextForm(request.POST)
    #         if form.is_valid() and user_ext_form.is_valid():
    #             form.save()
    #             user_ext_form.save()
    #             user = form.cleaned_data.get('first_name')
    #             messages.success(request,'Account was created for '+ user)
    #             return redirect('login_page')
    #
    #
    #     context={'form':form, 'user_ext_form' : user_ext_form }
    #     return render(request, "asset_mgt_app/registration_form.html",context)
