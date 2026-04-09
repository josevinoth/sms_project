from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect

from ..forms import SaleEnquiryForm
from ..models import SaleEnquiry, RoleInfo, User_extInfo
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id
from ..sub_models.customer_mod import CustomerInfo

@login_required(login_url='login_page')
def sale_enquiry_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = RoleInfo.objects.get(role_name=role).id

    sale_enquiry_query = SaleEnquiry.objects.all()

    if role_id not in [1, 3]:
        sale_enquiry_query = sale_enquiry_query.filter(created_by=user_id)

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date:
        sale_enquiry_query = sale_enquiry_query.filter(enquiry_date_time__date__gte=from_date)
    if to_date:
        sale_enquiry_query = sale_enquiry_query.filter(enquiry_date_time__date__lte=to_date)

    enquiry_list = sale_enquiry_query.order_by('-created_at')

    page_number = request.GET.get('page')
    paginator = Paginator(enquiry_list, 10000)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'first_name': first_name,
        'role': role,
        'page_obj': page_obj,
    }
    return render(request, "asset_mgt_app/sale_enquiry_list.html", context)


@login_required(login_url='login_page')
def sale_enquiry_add(request, enquiry_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = User_extInfo.objects.get(user=user_id).emp_role.id

    if request.method == "GET":
        if enquiry_id == 0:
            form = SaleEnquiryForm()
        else:
            enquiry = SaleEnquiry.objects.get(pk=enquiry_id)
            form = SaleEnquiryForm(instance=enquiry)
        
        context = {
            'form': form,
            'role': role,
            'role_id': role_id,
            'enquiry_id': enquiry_id,
            'first_name': first_name,
        }
        return render(request, "asset_mgt_app/sale_enquiry_add.html", context)
    else:
        if enquiry_id == 0:
            form = SaleEnquiryForm(request.POST, request.FILES)
            if form.is_valid():
                enquiry_instance = form.save(commit=False)
                
                fy = get_financial_year()
                branch_id = enquiry_instance.branch.id if enquiry_instance.branch else get_session_branch_id(request)
                branch_code = get_branch_code(branch_id)
                prefix = f"{fy}_{branch_code}_ENQ_"
                enquiry_instance.enquiry_id = generate_next_number(SaleEnquiry, 'enquiry_id', prefix, 6)
                
                enquiry_instance.created_by_id = user_id
                enquiry_instance.save()
                
                messages.success(request, 'Record Saved Successfully')
                return redirect(f'/SMS/sale_enquiry_update/{enquiry_instance.id}')
            else:
                messages.error(request, 'Record Not Saved. Please Enter All Required Fields')
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
                return redirect(request.META.get('HTTP_REFERER', '/SMS/sale_enquiry_list/'))
        else:
            enquiry = SaleEnquiry.objects.get(pk=enquiry_id)
            form = SaleEnquiryForm(request.POST, request.FILES, instance=enquiry)
            if form.is_valid():
                enquiry_instance = form.save(commit=False)
                enquiry_instance.updated_by_id = user_id
                enquiry_instance.save()
                messages.success(request, 'Record Updated Successfully')
            else:
                messages.error(request, 'Record Not Saved. Please Enter All Required Fields')
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"Error in {field}: {error}")
            return redirect(request.META.get('HTTP_REFERER', '/SMS/sale_enquiry_list/'))


@login_required(login_url='login_page')
def sale_enquiry_delete(request, enquiry_id):
    enquiry = SaleEnquiry.objects.get(pk=enquiry_id)
    enquiry.delete()
    messages.success(request, 'Record Deleted Successfully')
    return redirect('/SMS/sale_enquiry_list')


def get_customer_code(request):
    customer_id = request.GET.get('customer_id')
    if customer_id:
        try:
            customer = CustomerInfo.objects.get(pk=customer_id)
            return JsonResponse({'status': 'success', 'customer_code': customer.cu_customercode})
        except CustomerInfo.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Customer not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
