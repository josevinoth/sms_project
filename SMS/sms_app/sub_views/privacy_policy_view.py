from django.shortcuts import render

def privacy_policy(request):
    return render(request, 'asset_mgt_app/privacy_policy.html')
