from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from ..forms import SalestargetaddForm
from ..models import Sales_target_info, MyUser
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def sales_target_add(request, sales_target_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if sales_target_id == 0:
            sales_target_form = SalestargetaddForm()
        else:
            sales_target_info = Sales_target_info.objects.get(pk=sales_target_id)
            # If old legacy record has total revenue/customers but no split, populate existing
            if (not sales_target_info.st_target_revenue_existing and not sales_target_info.st_target_revenue_new) and (sales_target_info.st_target_revenue or 0) > 0:
                sales_target_info.st_target_revenue_existing = round(float(sales_target_info.st_target_revenue) / 100000.0, 2)
            if (not sales_target_info.st_target_customers_existing and not sales_target_info.st_target_customers_new) and (sales_target_info.st_target_customer or 0) > 0:
                sales_target_info.st_target_customers_existing = sales_target_info.st_target_customer
            sales_target_form = SalestargetaddForm(instance=sales_target_info)
        context = {
            'sales_target_form': sales_target_form,
            'first_name': first_name,
            'user_id': user_id,
            'sales_target_id': sales_target_id,
        }
        return render(request, "asset_mgt_app/sales_target_add.html", context)
    else:
        if sales_target_id == 0:
            sales_target_form = SalestargetaddForm(request.POST)
        else:
            sales_target_info = Sales_target_info.objects.get(pk=sales_target_id)
            sales_target_form = SalestargetaddForm(request.POST, instance=sales_target_info)
        if sales_target_form.is_valid():
            target_obj = sales_target_form.save(commit=False)

            # Auto-compute total revenue (INR) from Lakhs (New + Existing)
            rev_new = float(target_obj.st_target_revenue_new or 0.0)
            rev_exist = float(target_obj.st_target_revenue_existing or 0.0)
            target_obj.st_target_revenue = round((rev_new + rev_exist) * 100000.0, 2)

            # Auto-compute total customers (New + Existing)
            cust_new = int(target_obj.st_target_customers_new or 0)
            cust_exist = int(target_obj.st_target_customers_existing or 0)
            target_obj.st_target_customer = cust_new + cust_exist

            if user_id:
                try:
                    target_obj.st_updated_by = MyUser.objects.get(pk=user_id)
                except Exception:
                    pass
            target_obj.save()
            messages.success(request, "Sales Target saved successfully!")
            return redirect('/SMS/sales_target_list')
        else:
            for field, errors in sales_target_form.errors.items():
                for error in errors:
                    messages.error(request, error)
            context = {
                'sales_target_form': sales_target_form,
                'first_name': first_name,
                'user_id': user_id,
                'sales_target_id': sales_target_id,
            }
            return render(request, "asset_mgt_app/sales_target_add.html", context)

# AJAX helper to check if a salesperson already has an unexpired target
@login_required(login_url='login_page')
def check_sales_target_active(request):
    sales_person_id = request.GET.get('sales_person_id')
    current_target_id = request.GET.get('target_id', 0)
    start_date_str = request.GET.get('start_date', '')

    if not sales_person_id:
        return JsonResponse({'status': 'ok', 'has_unexpired': False})

    today = timezone.now().date()
    qs = Sales_target_info.objects.filter(st_sales_person_id=sales_person_id)
    if current_target_id and str(current_target_id).isdigit() and int(current_target_id) > 0:
        qs = qs.exclude(pk=int(current_target_id))

    # Check for targets whose end date has not expired (>= today)
    unexpired = qs.filter(st_end_date__gte=today).order_by('-st_end_date').first()

    # Also check if new start date falls on/before an existing target's end date
    if not unexpired and start_date_str:
        try:
            start_d = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            unexpired = qs.filter(st_end_date__gte=start_d).order_by('-st_end_date').first()
        except Exception:
            pass

    if unexpired:
        end_str = unexpired.st_end_date.strftime('%d-%m-%Y') if unexpired.st_end_date else ''
        start_str = unexpired.st_start_date.strftime('%d-%m-%Y') if unexpired.st_start_date else ''
        return JsonResponse({
            'status': 'ok',
            'has_unexpired': True,
            'target_id': unexpired.id,
            'start_date': start_str,
            'end_date': end_str,
            'message': f"The target which is previously given doesn't reached the end date (Ends on {end_str})."
        })

    return JsonResponse({'status': 'ok', 'has_unexpired': False})

# List sales_target
@login_required(login_url='login_page')
def sales_target_list(request):
    first_name = request.session.get('first_name')
    context = {
        'sales_target_list': Sales_target_info.objects.select_related('st_sales_person', 'st_updated_by', 'st_company').all().order_by('-id'),
        'first_name': first_name
    }
    return render(request, "asset_mgt_app/sales_target_list.html", context)

# Delete sales_target
@login_required(login_url='login_page')
def sales_target_delete(request, sales_target_id):
    sales_target_info = Sales_target_info.objects.get(pk=sales_target_id)
    sales_target_info.delete()
    messages.success(request, "Sales Target deleted successfully!")
    return redirect('/SMS/sales_target_list')