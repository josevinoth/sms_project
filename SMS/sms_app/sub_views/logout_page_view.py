from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_page(request):
    business_id = request.GET.get('business_id')
    logout(request)
    
    if business_id:
        return redirect('customer_login', business_id=business_id)
        
    return redirect('login_page')