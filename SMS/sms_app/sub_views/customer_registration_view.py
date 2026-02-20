from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from ..sub_forms.customer_registration_form import CustomerRegistrationForm
from .send_department_email import send_department_email
from ..sub_models.customer_registration_mod import CustomerRegistrationInfo
from ..sub_models.user_ext_mod import User_extInfo
from ..models import Business_Sol_info, Department_info, CustomertypeInfo, CustomerInfo, RoleInfo, GstexcemptionInfo, GstmodelInfo, PaymenttypeInfo, CrcountfromInfo, TrbusinesstypeInfo


def ajax_search_customers(request):
    """AJAX view to search for customers by short name (triggered after 5+ characters)."""
    query = request.GET.get('q', '').strip()
    if len(query) >= 5:
        customers = CustomerInfo.objects.filter(cu_nameshort__icontains=query).values('id', 'cu_nameshort')[:10]
        results = [{'id': c['id'], 'name': c['cu_nameshort']} for c in customers]
        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)

def ajax_check_customer_code(request):
    """AJAX view to find customer by code."""
    code = request.GET.get('code', '').strip()
    if code:
        customer = CustomerInfo.objects.filter(cu_customercode__iexact=code).first()
        if customer:
            return JsonResponse({'found': True, 'name': customer.cu_nameshort})
    return JsonResponse({'found': False})


def customer_register(request, business_id):
    """
    Public view for customer registration.
    Handles form submission and creation of pending registration records.
    """
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            # Save the business ID they registered through
            try:
                business = Business_Sol_info.objects.get(id=business_id)
                registration.registered_business = business
            except Business_Sol_info.DoesNotExist:
                pass
            registration.save()
            messages.success(request, 'Registration successful! Your account is pending approval by management.')
            return redirect('customer_login', business_id=business_id)  # Redirect to login page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'asset_mgt_app/customer_register.html', {
        'form': form,
        'business_id': business_id
    })


@login_required(login_url='login_page')
def customer_registration_list(request):
    """
    Management view to list pending customer registrations.
    Allows admins to approve or reject registrations.
    """
    # Filter for pending registrations
    pending_registrations = CustomerRegistrationInfo.objects.filter(approval_status='pending').order_by('-created_at')
    
    # Also show approved/rejected for history tab if needed
    processed_registrations = CustomerRegistrationInfo.objects.exclude(approval_status='pending').order_by('-updated_at')[:50]
    
    return render(request, 'asset_mgt_app/customer_registration_list.html', {
        'pending_registrations': pending_registrations,
        'processed_registrations': processed_registrations
    })


@login_required
def customer_registration_approve(request, registration_id):
    """
    Approve a pending registration.
    Creates a User account and User_extInfo record.
    """
    registration = get_object_or_404(CustomerRegistrationInfo, id=registration_id)
    
    if registration.approval_status != 'pending':
        messages.warning(request, 'This registration has already been processed.')
        return redirect('customer_registration_list')
    
    try:
        # 1. Create User account
        user = User.objects.create(
            username=registration.username,
            email=registration.email,
            first_name=registration.company_name[:30],
            is_active=True
        )
        
        # Set the hashed password directly
        user.password = registration.password_hash
        user.save()
        
        # 2. Create User_extInfo
        # Use the business the customer registered through
        business_sol = registration.registered_business
        if not business_sol:
            # Fallback to BVM Storage if not specified (legacy or error)
            business_sol = Business_Sol_info.objects.filter(id=1).first() or Business_Sol_info.objects.first()

        # Fetch/Create a 'Customer' role
        customer_role, created = RoleInfo.objects.get_or_create(role_name='Customer')

        # Map Department
        mapped_department = None
        if registration.customer_department:
            dept_name = registration.customer_department.ct_customerdepartment
            mapped_department = Department_info.objects.filter(dept_name__iexact=dept_name).first()

        # 2. Find existing CustomerInfo (must already exist - validated at registration)
        customer_entity = CustomerInfo.objects.filter(cu_nameshort__iexact=registration.company_name).first()
        
        if not customer_entity:
            if registration.is_lp_customer:
                # Auto-create CustomerInfo for AISATS/LP user using first available defaults
                def_type = CustomertypeInfo.objects.first()
                def_gst_exc = GstexcemptionInfo.objects.first()
                def_gst_model = GstmodelInfo.objects.first()
                def_pay_type = PaymenttypeInfo.objects.first()
                def_cr_count = CrcountfromInfo.objects.first()
                def_biz_model = TrbusinesstypeInfo.objects.first()

                if not all([def_type, def_gst_exc, def_gst_model, def_pay_type, def_cr_count, def_biz_model]):
                     messages.error(request, 'Cannot auto-create customer due to missing system configuration (Default Types/GST/Payment/Business Model).')
                     return redirect('customer_registration_list')
                
                # Create the customer entity
                customer_entity = CustomerInfo.objects.create(
                    cu_customercode = f"LP-{registration.username}",
                    cu_name = registration.company_name,
                    cu_nameshort = registration.company_name,
                    cu_type = def_type,
                    cu_address = "Auto-created from Registration",
                    cu_pan = "", 
                    cu_gst = "",
                    cu_customerperson = registration.username,
                    cu_designation = "Point of Contact",
                    cu_contactno = registration.contact_number[:10] if registration.contact_number else "",
                    cu_email = registration.email,
                    cu_gstexcepmtion = def_gst_exc,
                    cu_gstmodel = def_gst_model,
                    cu_paymenttype = def_pay_type,
                    cu_creditcountfrom = def_cr_count,
                    cu_businessmodel = def_biz_model,
                )
            else:
                messages.error(request, f'Customer "{registration.company_name}" not found in the system. Cannot approve.')
                return redirect('customer_registration_list')

        User_extInfo.objects.create(
            user=user,
            department=mapped_department,
            emp_contact=registration.contact_number[:10],
            emp_organisation=business_sol,
            emp_role=customer_role,
            linked_customer=customer_entity, # Link to the customer entity
            is_lp_customer=registration.is_lp_customer, # Pass the LP status
        )

        # 4. Update Registration Status
        registration.approval_status = 'approved'
        registration.approved_by = request.user if hasattr(request.user, 'myuser') else None 
        registration.approved_at = timezone.now()
        registration.save()
        
        # Send Approval Email
        try:
            subject = f"Registration Approved - {registration.company_name}"
            email_body = f"""
            <html>
            <body>
                <p>Dear {registration.company_name},</p>
                <p>Congratulations! Your registration for the BVM Transport Management System has been approved.</p>
                <p><b>Login Details:</b></p>
                <ul>
                    <li><b>Username:</b> {registration.username}</li>
                    <li><b>Login URL:</b> <a href="http://127.0.0.1:8000/SMS/customer_login/{business_sol.id if business_sol else 1}/">Click here to login</a></li>
                </ul>
                <p>Please use the password you set during registration.</p>
                <p>Regards,<br>BVM Transport Team</p>
            </body>
            </html>
            """
            send_department_email(
                department="itadmin",
                subject=subject,
                message=email_body,
                recipient_list=[registration.email],
                email_type=1
            )
            messages.success(request, f'User {registration.username} approved and email sent.')
        except Exception as e:
            messages.warning(request, f'User {registration.username} approved, but failed to send email: {str(e)}')
        
    except Exception as e:
        messages.error(request, f'Error approving user: {str(e)}')
        if 'user' in locals():
            user.delete()
    return redirect('customer_registration_list')


@login_required
def customer_registration_reject(request, registration_id):
    """
    Reject a pending registration.
    """
    if request.method == 'POST':
        registration = get_object_or_404(CustomerRegistrationInfo, id=registration_id)
        
        if registration.approval_status != 'pending':
            messages.warning(request, 'This registration has already been processed.')
            return redirect('customer_registration_list')
        
        rejection_reason = request.POST.get('rejection_reason', '')
        
        registration.approval_status = 'rejected'
        registration.rejection_reason = rejection_reason
        registration.approved_by = request.user  # Records who rejected it
        registration.approved_at = timezone.now()
        registration.save()
        
        # Send Rejection Email
        try:
            subject = f"Registration Status - {registration.company_name}"
            email_body = f"""
            <html>
            <body>
                <p>Dear {registration.company_name},</p>
                <p>Thank you for your interest in BVM Transport Management System.</p>
                <p>We regret to inform you that your registration request has been declined.</p>
                <p><b>Reason:</b> {rejection_reason}</p>
                <p>Please contact support for further assistance.</p>
                <p>Regards,<br>BVM Transport Team</p>
            </body>
            </html>
            """
            send_department_email(
                department="itadmin",
                subject=subject,
                message=email_body,
                recipient_list=[registration.email],
                email_type=1
            )
            messages.info(request, f'Registration for {registration.username} rejected and email sent.')
        except Exception as e:
            messages.warning(request, f'Registration rejected, but email failed: {str(e)}')
        
    return redirect('customer_registration_list')
