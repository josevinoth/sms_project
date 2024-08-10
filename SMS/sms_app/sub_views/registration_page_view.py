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
            user_name = form.cleaned_data.get('first_name')
            messages.success(request,f'Account created for {user_name}')
            return redirect('login_page')
        else:
            # Show errors if the forms are not valid
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CreateUserForm()
        user_ext_form = UserextForm()

    context = {'user_ext_form': user_ext_form,'form': form}
    return render(request, "asset_mgt_app/registration_form.html",context)

