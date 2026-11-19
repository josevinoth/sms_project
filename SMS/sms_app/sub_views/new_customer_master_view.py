from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from ..models import NewCustomerMaster, MyUser
from ..forms import NewCustomerMasterForm

@login_required(login_url='login_page')
def new_customer_master_add(request, customer_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID') or (request.user.id if request.user.is_authenticated else None)

    if request.method == "GET":
        if customer_id == 0:
            form = NewCustomerMasterForm()
            customer = None
        else:
            customer = get_object_or_404(NewCustomerMaster, pk=customer_id)
            form = NewCustomerMasterForm(instance=customer)

        context = {
            'form': form,
            'customer': customer,
            'customer_id': customer_id,
            'first_name': first_name,
            'is_edit': bool(customer_id != 0),
        }
        return render(request, "asset_mgt_app/new_customer_master_add.html", context)

    else:  # POST
        is_ajax = (
            request.headers.get('x-requested-with') == 'XMLHttpRequest' or 
            request.POST.get('is_ajax') == '1'
        )

        if customer_id == 0:
            form = NewCustomerMasterForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                if user_id:
                    try:
                        instance.created_by = MyUser.objects.get(pk=user_id)
                    except MyUser.DoesNotExist:
                        pass
                instance.save()
                
                if is_ajax:
                    return JsonResponse({
                        'status': 'success',
                        'id': instance.id,
                        'customer_name': instance.customer_name,
                        'is_active': instance.is_active,
                        'message': f'Customer "{instance.customer_name}" added successfully.'
                    })

                messages.success(request, f'New Customer "{instance.customer_name}" created successfully!')
                return redirect('new_customer_master_list')
            else:
                if is_ajax:
                    errors = {field: [str(err) for err in errs] for field, errs in form.errors.items()}
                    return JsonResponse({'status': 'error', 'errors': errors}, status=400)
                
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.replace('_', ' ').title()}: {error}")
                
                context = {
                    'form': form,
                    'customer': None,
                    'customer_id': 0,
                    'first_name': first_name,
                    'is_edit': False,
                }
                return render(request, "asset_mgt_app/new_customer_master_add.html", context)

        else:
            customer = get_object_or_404(NewCustomerMaster, pk=customer_id)
            form = NewCustomerMasterForm(request.POST, instance=customer)
            if form.is_valid():
                instance = form.save()
                
                if is_ajax:
                    return JsonResponse({
                        'status': 'success',
                        'id': instance.id,
                        'customer_name': instance.customer_name,
                        'is_active': instance.is_active,
                        'message': f'Customer "{instance.customer_name}" updated successfully.'
                    })

                messages.success(request, f'Customer "{instance.customer_name}" updated successfully!')
                return redirect('new_customer_master_list')
            else:
                if is_ajax:
                    errors = {field: [str(err) for err in errs] for field, errs in form.errors.items()}
                    return JsonResponse({'status': 'error', 'errors': errors}, status=400)

                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field.replace('_', ' ').title()}: {error}")

                context = {
                    'form': form,
                    'customer': customer,
                    'customer_id': customer_id,
                    'first_name': first_name,
                    'is_edit': True,
                }
                return render(request, "asset_mgt_app/new_customer_master_add.html", context)


@login_required(login_url='login_page')
def new_customer_master_list(request):
    first_name = request.session.get('first_name')
    customers = NewCustomerMaster.objects.all().order_by('-created_at')

    # Fetch/sync won business from SalesInfo for any customer where is_business_won wasn't updated yet
    from ..models import SalesInfo
    for c in customers:
        if not c.is_business_won or not c.business_won_date:
            won_sale = SalesInfo.objects.filter(
                s_bus_won_not_id=1,
                s_customer_new_name__iexact=c.customer_name
            ).order_by('-id').first()
            if won_sale:
                c.is_active = False
                c.is_business_won = True
                c.business_won_date = won_sale.s_yesdate_business or (won_sale.s_created_at.date() if won_sale.s_created_at else None)
                c.save(update_fields=['is_active', 'is_business_won', 'business_won_date'])

    customers = NewCustomerMaster.objects.all().order_by('-created_at')
    context = {
        'customers': customers,
        'first_name': first_name,
        'active_count': customers.filter(is_active=True).count(),
        'inactive_count': customers.filter(is_active=False, is_business_won=False).count(),
        'won_count': customers.filter(is_business_won=True).count(),
        'total_count': customers.count(),
    }
    return render(request, "asset_mgt_app/new_customer_master_list.html", context)


@login_required(login_url='login_page')
def new_customer_master_delete(request, customer_id):
    customer = get_object_or_404(NewCustomerMaster, pk=customer_id)
    name = customer.customer_name
    customer.delete()
    messages.success(request, f'Customer "{name}" deleted successfully.')
    return redirect('new_customer_master_list')


@login_required(login_url='login_page')
def new_customer_master_toggle_status(request, customer_id):
    customer = get_object_or_404(NewCustomerMaster, pk=customer_id)
    customer.is_active = not customer.is_active
    customer.save()

    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        request.GET.get('is_ajax') == '1'
    )
    if is_ajax:
        return JsonResponse({
            'status': 'success',
            'id': customer.id,
            'is_active': customer.is_active,
            'status_label': 'Active' if customer.is_active else 'Inactive',
            'message': f'Customer "{customer.customer_name}" is now {"Active" if customer.is_active else "Inactive"}.'
        })

    messages.success(request, f'Customer "{customer.customer_name}" is now {"Active" if customer.is_active else "Inactive"}.')
    return redirect('new_customer_master_list')


@login_required(login_url='login_page')
def new_customer_master_api_list(request):
    """
    JSON endpoint for fetching new customers.
    Query param ?all=1 includes inactive customers too.
    """
    show_all = request.GET.get('all') == '1'
    qs = NewCustomerMaster.objects.all()
    if not show_all:
        qs = qs.filter(is_active=True)

    search = request.GET.get('q', '').strip()
    if search:
        qs = qs.filter(customer_name__icontains=search)

    data = [
        {
            'id': item.id,
            'name': item.customer_name,
            'is_active': item.is_active,
        }
        for item in qs.order_by('customer_name')
    ]
    return JsonResponse({'status': 'success', 'data': data})
