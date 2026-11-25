from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render, redirect

from ..forms import SaleEnquiryForm
from ..models import SaleEnquiry, RoleInfo, User_extInfo, SalesmultipleitemInfo, Mc_vehicletype
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id
from ..sub_models.customer_mod import CustomerInfo

@login_required(login_url='login_page')
def sale_enquiry_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    user_ext = User_extInfo.objects.filter(user=user_id).first()
    role = user_ext.emp_role if user_ext else None
    role_info = RoleInfo.objects.filter(role_name=role).first() if role else None
    role_id = role_info.id if role_info else 1

    sale_enquiry_query = SaleEnquiry.objects.all()

    if role_id not in [1, 3]:
        from django.db.models import Q
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(pk=user_id)
            current_user_name = f"{user.first_name} {user.last_name}".strip() or user.username
            sale_enquiry_query = sale_enquiry_query.filter(Q(created_by=user_id) | Q(assigned_to=current_user_name))
        except User.DoesNotExist:
            sale_enquiry_query = sale_enquiry_query.filter(created_by=user_id)

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    if from_date:
        sale_enquiry_query = sale_enquiry_query.filter(enquiry_date_time__date__gte=from_date)
    if to_date:
        sale_enquiry_query = sale_enquiry_query.filter(enquiry_date_time__date__lte=to_date)

    enquiry_list = sale_enquiry_query.order_by('-created_at')
    
    from ..models import SalesmultipleitemInfo
    for enquiry in enquiry_list:
        quotes = SalesmultipleitemInfo.objects.filter(sm_enquiry_num=enquiry)
        enquiry.quote_count = quotes.count()
        latest_quote = quotes.order_by('-sm_updated_at').first()
        enquiry.latest_quote_status = latest_quote.sm_quote_status if latest_quote else '-'

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
            'mc_vehicle_types': Mc_vehicletype.objects.all().order_by('mc_vehicletype'),
        }
        
        if enquiry_id != 0:

            context['Salesmultipleitem_list'] = SalesmultipleitemInfo.objects.filter(sm_enquiry_num=enquiry_id)
        else:
            context['Salesmultipleitem_list'] = []

        return render(request, "asset_mgt_app/sale_enquiry_add.html", context)
    else:
        if enquiry_id == 0:
            form = SaleEnquiryForm(request.POST, request.FILES)
            if form.is_valid():
                enquiry_instance = form.save(commit=False)
                if enquiry_instance.mc_vehicle_source and 'BVM' in str(enquiry_instance.mc_vehicle_source).upper():
                    dropdown_val = request.POST.get('mc_vehicle_type_select')
                    if dropdown_val:
                        enquiry_instance.mc_vehicle_type = dropdown_val
                
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
                if enquiry_instance.mc_vehicle_source and 'BVM' in str(enquiry_instance.mc_vehicle_source).upper():
                    dropdown_val = request.POST.get('mc_vehicle_type_select')
                    if dropdown_val:
                        enquiry_instance.mc_vehicle_type = dropdown_val
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
            
            # Fetch the latest sales record for this customer to get the sales number
            from ..models import SalesInfo
            latest_sale = SalesInfo.objects.filter(s_customer_name=customer).order_by('-s_created_at').first()
            sales_number = latest_sale.s_sale_number if latest_sale else ''
            
            # Prepare data to return
            data = {
                'status': 'success',
                'customer_code': customer.cu_customercode,
                'sales_number': sales_number,
                'contact_person': customer.cu_customerperson,
                'contact_no': customer.cu_contactno,
                'mail': customer.cu_email,
                'service_type': str(customer.cu_type) if customer.cu_type else '',
                'address': customer.cu_address
            }
            return JsonResponse(data)
        except CustomerInfo.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Customer not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def get_sale_details(request):
    sale_number = request.GET.get('sale_number')
    if sale_number:
        try:
            from ..models import SalesInfo
            sale = SalesInfo.objects.filter(s_sale_number=sale_number).first()
            if sale:
                # If s_customer_new_name exists, it's a new customer scenario
                is_new_customer = bool(sale.s_customer_new_name)
                
                data = {
                    'status': 'success',
                    'customer_id': '' if is_new_customer else (sale.s_customer_name.id if sale.s_customer_name else ''),
                    'new_customer_name': sale.s_customer_new_name or '',
                    'customer_code': sale.s_customer_code or (sale.s_customer_name.cu_customercode if sale.s_customer_name else ''),
                    'contact_person': sale.s_Person_name or '',
                    'contact_no': sale.s_contact_no or '',
                    'mail': sale.s_email_id or '',
                    'service_type': str(sale.s_industry_type) if sale.s_industry_type else '',
                    'address': sale.s_customer_name.cu_address if sale.s_customer_name else ''
                }
                return JsonResponse(data)
            else:
                return JsonResponse({'status': 'error', 'message': 'Sale number not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


@login_required(login_url='login_page')
def mc_tours_calendar_events(request):
    enquiries = SaleEnquiry.objects.filter(mc_customer_type__isnull=False)
    events = []

    STATUS_CONFIG = {
        'business won':  {
            'label': 'Business Won',
            'bg': '#10b981',
            'border': '#059669',
            'icon': 'fa-check-circle',
        },
        'in discussion': {
            'label': 'In Discussion',
            'bg': '#f59e0b',
            'border': '#d97706',
            'icon': 'fa-comments',
        },
    }

    for enq in enquiries:
        if not enq.mc_travel_date:
            continue

        quotes = SalesmultipleitemInfo.objects.filter(sm_enquiry_num=enq)
        latest_quote = quotes.order_by('-sm_updated_at').first()
        if not latest_quote or not latest_quote.sm_quote_status:
            continue

        raw_status = latest_quote.sm_quote_status.quote_status
        status_key = raw_status.strip().lower()

        if status_key not in STATUS_CONFIG:
            won_quote = quotes.filter(sm_quote_status__quote_status__iexact='Business Won').order_by('-sm_updated_at').first()
            if won_quote:
                status_key = 'business won'
            else:
                continue

        cust_name = enq.effective_customer_name
        cfg = STATUS_CONFIG[status_key]

        is_tours = False
        customer_type_name = ''
        if enq.mc_customer_type:
            customer_type_name = str(enq.mc_customer_type.tt_requirement).strip()
            if customer_type_name.lower() == 'tours':
                is_tours = True

        travel_date_str = enq.mc_travel_date.strftime('%d-%m-%Y')
        return_date_str = enq.mc_return_date.strftime('%d-%m-%Y') if enq.mc_return_date else '-'

        vehicle_info = ''
        if not is_tours:
            vehicle_source = str(enq.mc_vehicle_source) if enq.mc_vehicle_source else '-'
            vehicle_type = enq.mc_vehicle_type or '-'
            vehicle_info = f"{vehicle_source} / {vehicle_type}"

        description = (
            f"<b>[{cfg['label']}]</b><br>"
            f"Enquiry No: {enq.enquiry_id or enq.id}<br>"
            f"Customer: {cust_name}<br>"
            f"Travel Date: {travel_date_str}<br>"
            f"Return Date: {return_date_str}<br>"
            f"From: {enq.mc_from or '-'}<br>"
            f"To: {enq.mc_to or '-'}"
        )
        if vehicle_info:
            description += f"<br>Vehicle: {vehicle_info}"

        start_date = enq.mc_travel_date
        return_date = enq.mc_return_date

        status_slug = 'business-won' if status_key == 'business won' else 'in-discussion'

        duration_days = 1
        if return_date and return_date >= start_date:
            duration_days = (return_date - start_date).days + 1

        vehicle_src = str(enq.mc_vehicle_source.ow_ownership) if enq.mc_vehicle_source else ''
        vehicle_tp = str(enq.mc_vehicle_type or '')

        event_data = {
            'id': str(enq.id),
            'title': str(enq.enquiry_id or f"Enquiry #{enq.id}"),
            'start': start_date.isoformat(),
            'description': description,
            'url': f"/SMS/sale_enquiry_update/{enq.id}",
            'backgroundColor': cfg['bg'],
            'borderColor': cfg['border'],
            'textColor': '#ffffff',
            'allDay': True,
            'classNames': [f"fc-event-status-{status_slug}"],
            'extendedProps': {
                'status': status_key,
                'statusLabel': cfg['label'],
                'customer': cust_name,
                'customerType': customer_type_name,
                'isTours': is_tours,
                'from': enq.mc_from or '-',
                'to': enq.mc_to or '-',
                'travelDate': travel_date_str,
                'returnDate': return_date_str,
                'durationDays': duration_days,
                'vehicle': vehicle_info,
                'vehicleSource': vehicle_src,
                'vehicleType': vehicle_tp,
                'passengers': enq.mc_no_of_passengers or '-',
                'hotelReq': str(enq.mc_hotel_req or '-'),
                'packageReq': str(enq.mc_package_req or '-'),
                'remarks': str(enq.mc_remarks or ''),
                'enquiryId': enq.enquiry_id or str(enq.id),
                'icon': cfg['icon'],
            }
        }

        # FullCalendar end date is exclusive for all-day events.
        # Adding 1 day ensures the return date is visually included in the span.
        if return_date and return_date >= start_date:
            event_data['end'] = (return_date + timedelta(days=1)).isoformat()
        else:
            event_data['end'] = (start_date + timedelta(days=1)).isoformat()

        events.append(event_data)

    return JsonResponse(events, safe=False)
