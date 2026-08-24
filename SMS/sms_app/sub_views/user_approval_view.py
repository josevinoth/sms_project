from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import User_extInfo, RoleInfo, Location_info, Department_info, DesignationInfo, Business_Sol_info

@login_required(login_url='login_page')
def user_approval_list(request):
    """View pending user registrations for Admin approval."""
    user_id = request.session.get('ses_userID') or request.user.id
    try:
        user_ext = User_extInfo.objects.get(user_id=user_id)
        # Check if user is staff/admin or superuser or has Admin role
        is_admin_user = request.user.is_staff or request.user.is_superuser or (user_ext.emp_role and 'admin' in user_ext.emp_role.role_name.lower())
    except User_extInfo.DoesNotExist:
        is_admin_user = request.user.is_staff or request.user.is_superuser

    if not is_admin_user:
        messages.error(request, "Access restricted to administrators.")
        return redirect('home_page')

    pending_users = User_extInfo.objects.filter(is_approved=False).select_related('user', 'emp_role', 'department', 'emp_branch', 'emp_designation', 'emp_organisation')
    roles = RoleInfo.objects.all().order_by('role_name')
    branches = Location_info.objects.all().order_by('loc_name')
    departments = Department_info.objects.all().order_by('dept_name')
    designations = DesignationInfo.objects.all().order_by('des_designation_name')
    organisations = Business_Sol_info.objects.all().order_by('bvm_business')
    first_name = request.session.get('first_name')

    return render(request, "asset_mgt_app/user_approval_list.html", {
        'pending_users': pending_users,
        'roles': roles,
        'branches': branches,
        'departments': departments,
        'designations': designations,
        'organisations': organisations,
        'first_name': first_name,
    })


from django.core.mail import send_mail
from django.conf import settings

@login_required(login_url='login_page')
def user_approve(request, user_id):
    """Approve user registration, assign role, designation and notify user via email."""
    current_uid = request.session.get('ses_userID') or request.user.id
    try:
        user_ext_curr = User_extInfo.objects.get(user_id=current_uid)
        is_admin_user = request.user.is_staff or request.user.is_superuser or (user_ext_curr.emp_role and 'admin' in user_ext_curr.emp_role.role_name.lower())
    except User_extInfo.DoesNotExist:
        is_admin_user = request.user.is_staff or request.user.is_superuser

    if not is_admin_user:
        messages.error(request, "Access restricted to administrators.")
        return redirect('home_page')

    if request.method == 'POST':
        user_ext = get_object_or_404(User_extInfo, user_id=user_id)
        user = user_ext.user

        role_id = request.POST.get('role')
        desig_id = request.POST.get('designation')

        if role_id:
            try:
                user_ext.emp_role = RoleInfo.objects.get(id=role_id)
            except RoleInfo.DoesNotExist:
                pass

        if desig_id:
            try:
                user_ext.emp_designation = DesignationInfo.objects.get(id=desig_id)
            except DesignationInfo.DoesNotExist:
                pass

        user.is_active = True
        user.save()

        user_ext.is_approved = True
        user_ext.save()

        # Send approval confirmation email to user's registered email ID
        if user.email:
            subject = "BVM Management System Account Registration Approved"
            message = (
                f"Dear {user.first_name or user.username},<br><br>"
                f"Your account registration for the <b>BVM Management System</b> has been <b>APPROVED</b> by the Administrator.<br><br>"
                f"<b>Account Details:</b><br>"
                f"Username / Employee ID: <b>{user.username}</b><br>"
                f"Role: <b>{user_ext.emp_role.role_name if user_ext.emp_role else 'Standard User'}</b><br><br>"
                f"You can now log into the application using your credentials.<br><br>"
                f"Regards,<br>"
                f"Administration Team<br>"
                f"<b>The BVM Group</b>"
            )
            try:
                from .send_department_email import send_department_email_html
                send_department_email_html(
                    department='itadmin',
                    subject=subject,
                    message=message,
                    recipient_list=[user.email]
                )
            except Exception as e:
                print(f"[user_approve] Email sending error: {e}")

        messages.success(request, f"User '{user.username}' registration approved successfully and notification sent to {user.email}!")

    return redirect('user_approval_list')


@login_required(login_url='login_page')
def user_reject(request, user_id):
    """Reject pending user registration and notify user via email."""
    current_uid = request.session.get('ses_userID') or request.user.id
    try:
        user_ext_curr = User_extInfo.objects.get(user_id=current_uid)
        is_admin_user = request.user.is_staff or request.user.is_superuser or (user_ext_curr.emp_role and 'admin' in user_ext_curr.emp_role.role_name.lower())
    except User_extInfo.DoesNotExist:
        is_admin_user = request.user.is_staff or request.user.is_superuser

    if not is_admin_user:
        messages.error(request, "Access restricted to administrators.")
        return redirect('home_page')

    if request.method == 'POST':
        user_ext = get_object_or_404(User_extInfo, user_id=user_id)
        user = user_ext.user
        recipient_email = user.email
        username = user.username

        # Send rejection email to user's registered email ID before deleting record
        if recipient_email:
            subject = "BVM Management System Account Registration Update"
            message = (
                f"Dear {user.first_name or username},<br><br>"
                f"Your registration request for the <b>BVM Management System</b> has been reviewed.<br><br>"
                f"Regrettably, your account request was not approved at this time. "
                f"If you believe this is an error, please contact your department administrator.<br><br>"
                f"Regards,<br>"
                f"Administration Team<br>"
                f"<b>The BVM Group</b>"
            )
            try:
                from .send_department_email import send_department_email_html
                send_department_email_html(
                    department='itadmin',
                    subject=subject,
                    message=message,
                    recipient_list=[recipient_email]
                )
            except Exception as e:
                print(f"[user_reject] Email sending error: {e}")

        user.is_active = False
        user.save()

        user_ext.delete()
        user.delete()

        messages.success(request, f"User registration request for '{username}' has been rejected.")

    return redirect('user_approval_list')


