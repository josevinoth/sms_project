from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .user_add_view import check_is_admin

@login_required(login_url='login_page')
def registration_page(request):
    """
    Public registration is locked down for security.
    Only authorized administrators can provision new user accounts.
    Redirects administrators to the secure Administration User Creation console.
    """
    if not check_is_admin(request):
        messages.error(request, "Access restricted to administrators. Public user registration is disabled.")
        return redirect('home_page')
    
    return redirect('user_insert')
