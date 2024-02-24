from django.shortcuts import render, redirect
from ..forms import CreateUserForm,UserextForm
from django.contrib import messages

def registration_page(request):
    # form = CreateUserForm()
    # user_ext_form = UserextForm()
    if request.method == 'POST':
        reg_form = CreateUserForm(request.POST)
        user_ext_form=UserextForm(request.POST)
        if reg_form.is_valid() and user_ext_form.is_valid():
            user= reg_form.save()
            user_ext= user_ext_form.save(commit=False)
            user_ext.user=user
            user_ext.save()
            # user_name = reg_form.cleaned_data.get('first_name')
            # messages.success(request,'Account created for '+ user_name)
            return redirect('login_page')
    else:
        reg_form = CreateUserForm()
        user_ext_form = UserextForm()
    context = {'user_ext_form': user_ext_form,'reg_form': reg_form}
    return render(request, "asset_mgt_app/user_registration.html",context)

