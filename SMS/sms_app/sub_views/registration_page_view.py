from django.shortcuts import render, redirect
from ..forms import CreateUserForm,UserextForm
from django.contrib import messages

ALLOWED_DOMAINS = [
    'bvmstorage.com',
    'bvmtranssolutions.com',
    'bvmpack.com',
    'thebvmgroup.com',
    'bvmexpress.com',
    'mctours.in',
    'gmail.com',
]

def registration_page(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        user_ext_form = UserextForm(request.POST)
        
        email = request.POST.get('email', '').strip().lower()
        domain = email.split('@')[-1] if '@' in email else ''
        
        if domain not in ALLOWED_DOMAINS:
            messages.error(request, 'Registration failed: Please sign up using your official company email address (@bvmstorage.com, @bvmtranssolutions.com, @bvmpack.com, @thebvmgroup.com, @bvmexpress.com, @mctours.in).')
            context = {'user_ext_form': user_ext_form, 'form': form}
            return render(request, "asset_mgt_app/registration_form.html", context)

        if form.is_valid() and user_ext_form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Account inactive until approved by Admin
            user.save()

            user_ext = user_ext_form.save(commit=False)
            user_ext.user = user
            user_ext.is_approved = False  # Requires Admin approval
            user_ext.save()

            user_name = form.cleaned_data.get('first_name') or user.username
            messages.success(request, f'Registration submitted for {user_name}! Your account is pending Admin review and approval.')
            return redirect('login_page')
        else:
            error_messages = []
            for field, errors in form.errors.items():
                for error in errors:
                    error_messages.append(f"{error}")
            for field, errors in user_ext_form.errors.items():
                for error in errors:
                    error_messages.append(f"{error}")
            
            if error_messages:
                messages.error(request, " | ".join(error_messages))
            else:
                messages.error(request, 'Please correct the errors below.')
    else:
        form = CreateUserForm()
        user_ext_form = UserextForm()

    context = {'user_ext_form': user_ext_form, 'form': form}
    return render(request, "asset_mgt_app/registration_form.html", context)



