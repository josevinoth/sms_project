from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from ..models import Employee
from django.db.models import Sum
from ..models import AssetInfo,Vendor_info,Location_info,Product_info,Employee,Service_Info

def home_page_new(request):
    first_name=request.session.get('first_name')
    ses_username = request.session.get('ses_username', request.POST.get('username'))
    context = {'count_asset': AssetInfo.objects.all().count(),
               'count_vendors': Vendor_info.objects.filter(vend_status=1).count(),
               'count_ass_asset': AssetInfo.objects.filter(asset_assignedto__isnull=False).count(),
               'count_unass_asset': AssetInfo.objects.filter(asset_assignedto__isnull=True).count(),
               'count_location': Location_info.objects.filter(loc_status=1).count(),
               'count_product': Product_info.objects.all().count(),
               'count_employee': Employee.objects.all().count(),
               'sum_ass_cost': AssetInfo.objects.aggregate(sum=Sum('asset_cost'))['sum'] or 0.00,
               'sum_service_cost':Service_Info.objects.aggregate(sum=Sum('ser_cost'))['sum'] or 0.00,
               'ses_username': ses_username,
               'first_name': first_name,
               }
    return render(request, 'asset_mgt_app/home_page.html', context)

def login_page_new(request):
    request.session['ses_username'] = request.POST.get('username')
    if request.method=='POST':
        username_form = request.POST.get('username')
        password_form = request.POST.get('password')
        print(username_form)
        print(password_form)
        user_id = Employee.objects.get(emp_empid=username_form).id
        full_name=Employee.objects.get(pk=user_id).emp_full_name
        emp_id=Employee.objects.get(pk=user_id).emp_empid
        emp_pwd= Employee.objects.get(pk=user_id).emp_password
        print(full_name)
        print(emp_id)
        if emp_id != username_form:
            messages.error(request, 'Employee not available! Please register!')
        elif emp_id==username_form and emp_pwd==password_form:
            messages.success(request, 'Valid Login')
            return redirect('home_page_new')
            # elif password_form==emp_pwd:
            #     return redirect('home_page')
        else:
            messages.error(request,'Username Or Password is Incorrect')
            # user = authenticate(request, username=username_form,password=password_form)
            request.session['first_name'] = full_name
            print(full_name)
            # if user is not None:
            #     login(request,user)
            #     return redirect('home_page')
            # else:
            #     messages.info(request,'Username Or Password is Incorrect')

    context = {}
    return render(request, "asset_mgt_app/login.html", context)