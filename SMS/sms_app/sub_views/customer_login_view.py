from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from ..sub_models.business_solutions_mod import Business_Sol_info
from ..models import User_extInfo
from ..sub_models.customer_mod import CustomerInfo
from ..models import Department_info
from ..sub_models.customerdepartment_mod import CustomerdepartmentInfo


def ajax_get_customer_departments(request):
    """AJAX view to return all available customer departments."""
    departments = CustomerdepartmentInfo.objects.all().values('id', 'ct_customerdepartment')
    return JsonResponse(list(departments), safe=False)


def customer_login(request, business_id):
    """Customer-scoped login view supporting two modes:
    - Customer login (customer id + password)
    - Agent login (select customer, agent name, department, password)

    Preserves submitted values on validation failure and exposes
    'active_tab' in context so the template can show the relevant tab.
    """
    business_name = ''
    customers = []
    departments = []
    active_tab = 'customer'

    try:
        business = Business_Sol_info.objects.get(id=business_id)
        business_name = business.bvm_business
    except Business_Sol_info.DoesNotExist:
        business = None
        business_name = ''

    if business:
        customers = CustomerInfo.objects.filter(cu_business_sol=business).order_by('cu_name')

    try:
        departments = Department_info.objects.all().order_by('dept_name')
    except Exception:
        departments = []

    # Values to prefill the form on error
    prefill = {
        'customer_id': '',
        'agent_name': '',
        'selected_customer': '',
        'department': '',
    }

    if request.method == 'POST':
        mode = request.POST.get('mode', 'customer')
        active_tab = mode

        if mode == 'customer':
            customer_id = request.POST.get('customer_id', '').strip()
            password = request.POST.get('password', '')
            prefill['customer_id'] = customer_id

            if not customer_id or not password:
                messages.error(request, 'Please provide both Customer ID and Password')
                return render(request, 'asset_mgt_app/customer_login.html', {
                    'business_name': business_name,
                    'customers': customers,
                    'departments': departments,
                    'active_tab': active_tab,
                    'prefill': prefill,
                    'business_id': business_id,
                })

            try:
                user_obj = User.objects.get(username=customer_id)
                user_ext = User_extInfo.objects.get(user=user_obj)
            except User.DoesNotExist:
                messages.error(request, 'Customer account not found')
                return render(request, 'asset_mgt_app/customer_login.html', {
                    'business_name': business_name,
                    'customers': customers,
                    'departments': departments,
                    'active_tab': active_tab,
                    'prefill': prefill,
                    'business_id': business_id,
                })
            except User_extInfo.DoesNotExist:
                messages.error(request, 'Extended user info not found for this customer')
                return render(request, 'asset_mgt_app/customer_login.html', {
                    'business_name': business_name,
                    'customers': customers,
                    'departments': departments,
                    'active_tab': active_tab,
                    'prefill': prefill,
                    'business_id': business_id,
                })

            user_org_id = user_ext.emp_organisation.id if user_ext.emp_organisation else None
            if user_org_id != business_id:
                messages.error(request, 'You are not authorised to login on this customer portal')
                return render(request, 'asset_mgt_app/customer_login.html', {
                    'business_name': business_name,
                    'customers': customers,
                    'departments': departments,
                    'active_tab': active_tab,
                    'prefill': prefill,
                    'business_id': business_id,
                })

            user = authenticate(request, username=customer_id, password=password)
            if user is not None:
                request.session['ses_userID'] = user_obj.id
                request.session['first_name'] = f"{user_obj.first_name} {user_obj.last_name}"
                
                # Handle selected customer department for regular users
                selected_dept_id = request.POST.get('customer_department')
                if selected_dept_id:
                    try:
                        dept_obj = CustomerdepartmentInfo.objects.get(id=selected_dept_id)
                        request.session['ses_customer_dept_id'] = dept_obj.id
                        request.session['ses_customer_dept_name'] = dept_obj.ct_customerdepartment
                    except CustomerdepartmentInfo.DoesNotExist:
                        pass

                request.session['ses_department_id'] = user_ext.department.id if user_ext.department else None
                request.session['ses_department_name'] = user_ext.department.dept_name if user_ext.department else None
                request.session['ses_role_id'] = user_ext.emp_role.id if user_ext.emp_role else None
                request.session['ses_role'] = user_ext.emp_role.role_name if user_ext.emp_role else None
                request.session['ses_organisation_id'] = user_org_id

                login(request, user)
                return redirect('customer_dashboard')
            else:
                messages.error(request, 'Customer ID or Password is incorrect')

        elif mode == 'agent':
            selected_customer_id = request.POST.get('customer_select')
            agent_name = request.POST.get('agent_name', '').strip()
            department_id = request.POST.get('department')
            password = request.POST.get('password', '')

            prefill['agent_name'] = agent_name
            prefill['selected_customer'] = selected_customer_id
            prefill['department'] = department_id

            if not selected_customer_id or not agent_name or not department_id or not password:
                messages.error(request, 'Please provide customer, agent name, department and password')
                return render(request, 'asset_mgt_app/customer_login.html', {
                    'business_name': business_name,
                    'customers': customers,
                    'departments': departments,
                    'active_tab': active_tab,
                    'prefill': prefill,
                    'business_id': business_id,
                })

            try:
                cust = CustomerInfo.objects.get(id=selected_customer_id, cu_business_sol=business)
            except CustomerInfo.DoesNotExist:
                messages.error(request, 'Selected customer is invalid for this portal')
                return render(request, 'asset_mgt_app/customer_login.html', {
                    'business_name': business_name,
                    'customers': customers,
                    'departments': departments,
                    'active_tab': active_tab,
                    'prefill': prefill,
                    'business_id': business_id,
                })

            try:
                user_obj = User.objects.get(username=agent_name)
                user_ext = User_extInfo.objects.get(user=user_obj)
            except User.DoesNotExist:
                messages.error(request, 'Agent account not found')
                return render(request, 'asset_mgt_app/customer_login.html', {
                    'business_name': business_name,
                    'customers': customers,
                    'departments': departments,
                    'active_tab': active_tab,
                    'prefill': prefill,
                    'business_id': business_id,
                })
            except User_extInfo.DoesNotExist:
                messages.error(request, 'Extended user info not found for this agent')
                return render(request, 'asset_mgt_app/customer_login.html', {
                    'business_name': business_name,
                    'customers': customers,
                    'departments': departments,
                    'active_tab': active_tab,
                    'prefill': prefill,
                    'business_id': business_id,
                })

            user_org_id = user_ext.emp_organisation.id if user_ext.emp_organisation else None
            if user_org_id != business_id:
                messages.error(request, 'Agent is not authorised for this customer portal')
                return render(request, 'asset_mgt_app/customer_login.html', {
                    'business_name': business_name,
                    'customers': customers,
                    'departments': departments,
                    'active_tab': active_tab,
                    'prefill': prefill,
                    'business_id': business_id,
                })

            try:
                dept_id_int = int(department_id)
            except Exception:
                dept_id_int = None

            user_dept_id = user_ext.department.id if user_ext.department else None
            if user_dept_id != dept_id_int:
                messages.error(request, 'Agent does not belong to the selected department')
                return render(request, 'asset_mgt_app/customer_login.html', {
                    'business_name': business_name,
                    'customers': customers,
                    'departments': departments,
                    'active_tab': active_tab,
                    'prefill': prefill,
                    'business_id': business_id,
                })

            user = authenticate(request, username=agent_name, password=password)
            if user is not None:
                request.session['ses_userID'] = user_obj.id
                request.session['first_name'] = f"{user_obj.first_name} {user_obj.last_name}"
                request.session['ses_department_id'] = user_ext.department.id if user_ext.department else None
                request.session['ses_department_name'] = user_ext.department.dept_name if user_ext.department else None
                request.session['ses_role_id'] = user_ext.emp_role.id if user_ext.emp_role else None
                request.session['ses_role'] = user_ext.emp_role.role_name if user_ext.emp_role else None
                request.session['ses_organisation_id'] = user_org_id
                request.session['agent_selected_customer_id'] = cust.id

                login(request, user)
                return redirect('customer_dashboard')
            else:
                messages.error(request, 'Agent name or Password is incorrect')

        else:
            messages.error(request, 'Invalid login mode')

    return render(request, 'asset_mgt_app/customer_login.html', {
        'business_name': business_name,
        'customers': customers,
        'departments': departments,
        'active_tab': active_tab,
        'prefill': prefill,
        'business_id': business_id,
    })
