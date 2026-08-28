from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_page(request):
    referer = request.META.get('HTTP_REFERER', '')
    is_customer = request.GET.get('is_customer') == '1' or 'customer_' in referer
    business_id = request.GET.get('business_id') or '2'
    logout(request)
    
    if is_customer:
        return redirect('customer_login', business_id=business_id)
        
    return redirect('login_page')