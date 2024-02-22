from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

# @login_required(login_url='login_page')
def home_page(request):
    first_name=request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    ses_username = request.session.get('ses_username', request.POST.get('username'))
    context = {
               'ses_username': ses_username,
               'first_name': first_name,
               }
    return render(request, 'asset_mgt_app/home_page.html', context)
