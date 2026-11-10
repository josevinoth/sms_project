import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from ..models import (
    User_extInfo, RoleInfo, Location_info, DesignationInfo, 
    Business_Sol_info, Department_info
)
from .send_department_email import send_department_email_html


def check_is_admin(request):
    """
    Check if the current logged-in user is an administrator.
    Checks superuser status, staff status, session role, or User_extInfo emp_role containing 'admin'.
    """
    if not request.user or not request.user.is_authenticated:
        return False
    if request.user.is_superuser or request.user.is_staff:
        return True
    user_role = (request.session.get('ses_role') or '').lower().strip()
    if user_role in ['admin', 'super user', 'superuser']:
        return True
    user_id = request.session.get('ses_userID') or request.user.id
    try:
        user_ext = User_extInfo.objects.get(user_id=user_id)
        if user_ext.emp_role and 'admin' in user_ext.emp_role.role_name.lower():
            return True
    except Exception:
        pass
    return False


def validate_password_strength(password):
    """
    Validate that password meets enterprise security standards:
    - At least 8 characters long
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter (A-Z)."
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter (a-z)."
    if not re.search(r'[0-9]', password):
        return "Password must contain at least one number (0-9)."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/]', password):
        return "Password must contain at least one special character (!@#$%^&* etc.)."
    return None


@login_required(login_url='login_page')
def user_add(request, user_id=0):
    """
    Admin-only console for creating or editing user logins.
    Ensures strict validation, PBKDF2 password hashing, and active pre-approval.
    """
    if not check_is_admin(request):
        messages.error(request, "Access restricted to administrators. Only admins can create or manage user logins.")
        return redirect('home_page')

    first_name_session = request.session.get('first_name')
    roles = RoleInfo.objects.all().order_by('role_name')
    branches = Location_info.objects.all().order_by('loc_name')
    departments = Department_info.objects.all().order_by('dept_name')
    designations = DesignationInfo.objects.all().order_by('des_designation_name')
    organisations = Business_Sol_info.objects.all().order_by('bvm_business')

    is_create = (user_id == 0)
    user_obj = None
    user_ext = None

    if not is_create:
        user_obj = get_object_or_404(User, pk=user_id)
        user_ext, _ = User_extInfo.objects.get_or_create(user=user_obj)

    if request.method == "GET":
        form_data = {}
        if is_create:
            form_data = {
                'is_active': True,
                'send_welcome_email': True,
            }
        else:
            form_data = {
                'username': user_obj.username,
                'first_name': user_obj.first_name,
                'last_name': user_obj.last_name,
                'email': user_obj.email,
                'is_active': user_obj.is_active,
                'emp_contact': user_ext.emp_contact or '',
                'emp_organisation': str(user_ext.emp_organisation_id) if user_ext.emp_organisation_id else '',
                'department': str(user_ext.department_id) if user_ext.department_id else '',
                'emp_branch': str(user_ext.emp_branch_id) if user_ext.emp_branch_id else '',
                'emp_designation': str(user_ext.emp_designation_id) if user_ext.emp_designation_id else '',
                'emp_role': str(user_ext.emp_role_id) if user_ext.emp_role_id else '',
                'emp_DOB': user_ext.emp_DOB or '',
                'emp_DOJ': user_ext.emp_DOJ or '',
                'emp_pan': user_ext.emp_pan or '',
                'emp_uan': user_ext.emp_uan or '',
                'emp_esi': user_ext.emp_esi or '',
                'emp_aadhar': user_ext.emp_aadhar or '',
            }

        context = {
            'is_create': is_create,
            'user_obj': user_obj,
            'user_ext': user_ext,
            'form_data': form_data,
            'roles': roles,
            'branches': branches,
            'departments': departments,
            'designations': designations,
            'organisations': organisations,
            'first_name': first_name_session,
        }
        return render(request, "asset_mgt_app/emp_add.html", context)

    # POST handling
    username = request.POST.get('username', '').strip()
    first_name_val = request.POST.get('first_name', '').strip()
    last_name_val = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip().lower()
    password = request.POST.get('password', '')
    confirm_password = request.POST.get('confirm_password', '')
    is_active = True if request.POST.get('is_active') in ['on', 'true', 'True', '1', True] else False
    emp_contact = request.POST.get('emp_contact', '').strip()
    emp_organisation_id = request.POST.get('emp_organisation') or None
    department_id = request.POST.get('department') or None
    emp_branch_id = request.POST.get('emp_branch') or None
    emp_designation_id = request.POST.get('emp_designation') or None
    emp_role_id = request.POST.get('emp_role') or None
    emp_DOB = request.POST.get('emp_DOB', '').strip() or None
    emp_DOJ = request.POST.get('emp_DOJ', '').strip() or None
    emp_pan = request.POST.get('emp_pan', '').strip() or None
    emp_uan = request.POST.get('emp_uan', '').strip() or None
    emp_esi = request.POST.get('emp_esi', '').strip() or None
    emp_aadhar = request.POST.get('emp_aadhar', '').strip() or None
    send_welcome_email = True if request.POST.get('send_welcome_email') in ['on', 'true', 'True', '1', True] else False

    form_data = {
        'username': username,
        'first_name': first_name_val,
        'last_name': last_name_val,
        'email': email,
        'is_active': is_active,
        'emp_contact': emp_contact,
        'emp_organisation': str(emp_organisation_id or ''),
        'department': str(department_id or ''),
        'emp_branch': str(emp_branch_id or ''),
        'emp_designation': str(emp_designation_id or ''),
        'emp_role': str(emp_role_id or ''),
        'emp_DOB': emp_DOB or '',
        'emp_DOJ': emp_DOJ or '',
        'emp_pan': emp_pan or '',
        'emp_uan': emp_uan or '',
        'emp_esi': emp_esi or '',
        'emp_aadhar': emp_aadhar or '',
        'send_welcome_email': send_welcome_email,
    }

    errors = []

    # Username validation
    if is_create:
        if not username:
            errors.append("Employee ID / Username is required.")
        elif not re.match(r'^[a-zA-Z0-9_.\-]+$', username):
            errors.append("Employee ID / Username may only contain letters, numbers, hyphens, underscores, or periods.")
        elif User.objects.filter(username__iexact=username).exists():
            errors.append(f"Username / Employee ID '{username}' already exists. Please select a unique ID.")

    # Name validation
    if not first_name_val:
        errors.append("First Name is required.")
    if not last_name_val:
        errors.append("Last Name is required.")

    # Email validation
    if not email:
        errors.append("Official email address is required.")
    elif not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
        errors.append("Please enter a valid email address.")
    else:
        existing_email_qs = User.objects.filter(email__iexact=email)
        if not is_create:
            existing_email_qs = existing_email_qs.exclude(pk=user_obj.id)
        if existing_email_qs.exists():
            errors.append(f"Email address '{email}' is already in use by another account.")

    # Password validation
    if is_create:
        if not password:
            errors.append("Password is required for new user creation.")
        elif password != confirm_password:
            errors.append("Password and Confirm Password do not match.")
        else:
            pw_err = validate_password_strength(password)
            if pw_err:
                errors.append(pw_err)
    else:
        # Edit mode: password change is optional
        if password or confirm_password:
            if password != confirm_password:
                errors.append("New Password and Confirm Password do not match.")
            else:
                pw_err = validate_password_strength(password)
                if pw_err:
                    errors.append(pw_err)

    if errors:
        for err in errors:
            messages.error(request, err)
        context = {
            'is_create': is_create,
            'user_obj': user_obj,
            'user_ext': user_ext,
            'form_data': form_data,
            'roles': roles,
            'branches': branches,
            'departments': departments,
            'designations': designations,
            'organisations': organisations,
            'first_name': first_name_session,
        }
        return render(request, "asset_mgt_app/emp_add.html", context)

    # Save user
    if is_create:
        user = User(
            username=username,
            first_name=first_name_val,
            last_name=last_name_val,
            email=email,
            is_active=is_active,
        )
        user.set_password(password)  # Secure PBKDF2 hashing
        user.save()

        user_ext = User_extInfo.objects.create(
            user=user,
            emp_contact=emp_contact,
            emp_organisation_id=emp_organisation_id,
            department_id=department_id,
            emp_branch_id=emp_branch_id,
            emp_designation_id=emp_designation_id,
            emp_role_id=emp_role_id,
            emp_DOB=emp_DOB,
            emp_DOJ=emp_DOJ,
            emp_pan=emp_pan,
            emp_uan=emp_uan,
            emp_esi=emp_esi,
            emp_aadhar=emp_aadhar,
            is_approved=True,  # Pre-approved by Admin
        )

        # Send welcome email if selected
        if send_welcome_email and email:
            role_name = user_ext.emp_role.role_name if user_ext.emp_role else "Standard User"
            org_name = user_ext.emp_organisation.bvm_business if user_ext.emp_organisation else "The BVM Group"
            subject = f"Welcome to {org_name} - Login Account Created"
            message = (
                f"Dear {first_name_val} {last_name_val},<br><br>"
                f"Your official login account for the <b>BVM Management System</b> has been created by the System Administrator.<br><br>"
                f"<b>Account Details:</b><br>"
                f"• Portal URL: <a href='https://sms.thebvmgroup.com/SMS/login_page'>https://sms.thebvmgroup.com/SMS/login_page</a><br>"
                f"• User ID / Employee ID: <b>{username}</b><br>"
                f"• Official Email: <b>{email}</b><br>"
                f"• Assigned Role: <b>{role_name}</b><br><br>"
                f"You can now sign in using your credentials.<br>"
                f"<i>Security Notice: Please keep your login credentials strictly confidential and do not share them.</i><br><br>"
                f"Regards,<br>"
                f"Administration Team<br>"
                f"<b>The BVM Group</b>"
            )
            try:
                send_department_email_html(
                    department='itadmin',
                    subject=subject,
                    message=message,
                    recipient_list=[email]
                )
            except Exception as e:
                print(f"[user_add] Email notification failed: {e}")

        messages.success(request, f"User account '{username}' created successfully for {first_name_val} {last_name_val}.")
    else:
        user_obj.first_name = first_name_val
        user_obj.last_name = last_name_val
        user_obj.email = email
        user_obj.is_active = is_active
        if password:
            user_obj.set_password(password)  # Securely update password
        user_obj.save()

        user_ext.emp_contact = emp_contact
        user_ext.emp_organisation_id = emp_organisation_id
        user_ext.department_id = department_id
        user_ext.emp_branch_id = emp_branch_id
        user_ext.emp_designation_id = emp_designation_id
        user_ext.emp_role_id = emp_role_id
        user_ext.emp_DOB = emp_DOB
        user_ext.emp_DOJ = emp_DOJ
        user_ext.emp_pan = emp_pan
        user_ext.emp_uan = emp_uan
        user_ext.emp_esi = emp_esi
        user_ext.emp_aadhar = emp_aadhar
        user_ext.is_approved = True
        user_ext.save()

        messages.success(request, f"User account '{user_obj.username}' updated successfully.")

    return redirect('user_list')


@login_required(login_url='login_page')
def user_list(request):
    """
    Admin-only listing of all system user accounts.
    """
    if not check_is_admin(request):
        messages.error(request, "Access restricted to administrators.")
        return redirect('home_page')

    first_name = request.session.get('first_name')
    users = User.objects.all().select_related(
        'user_extinfo',
        'user_extinfo__emp_role',
        'user_extinfo__department',
        'user_extinfo__emp_branch'
    ).order_by('id')
    total_users = users.count()
    active_users = sum(1 for u in users if u.is_active)
    inactive_users = total_users - active_users

    context = {
        'user_list': users,
        'first_name': first_name,
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
    }
    return render(request, "asset_mgt_app/employee_list.html", context)


@login_required(login_url='login_page')
def user_delete(request, user_id):
    """
    Admin-only secure user deletion with self-deletion and superuser guards.
    """
    if not check_is_admin(request):
        messages.error(request, "Access restricted to administrators.")
        return redirect('home_page')

    user = get_object_or_404(User, pk=user_id)

    if user.id == request.user.id:
        messages.error(request, "Security violation: You cannot delete your own account.")
        return redirect('user_list')

    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, "Security violation: Only a superuser can delete superuser accounts.")
        return redirect('user_list')

    username = user.username
    user.delete()
    messages.success(request, f"User account '{username}' was successfully deleted.")
    return redirect('user_list')
