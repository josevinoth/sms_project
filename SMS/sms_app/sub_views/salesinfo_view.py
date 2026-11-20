from django.contrib import messages
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.http import JsonResponse

from ..forms import SalescommentForm,SalesinfoaddForm,SalesmultipleitemForm
from ..models import RoleInfo,Sales_Comments_Info,User_extInfo,SalesInfo,SalesmultipleitemInfo,CustomertypeInfo,NewCustomerMaster
from django.shortcuts import render, redirect
from random import randint
from django.utils import timezone
from ..sub_models.customer_mod import CustomerInfo
from ..sub_models.my_user_mod import MyUser


def handle_business_won_customer(sales_instance):
    """
    If Business Won is 'Yes' (id=1):
    1. Check if a new customer name was used (s_customer_new_name).
    2. Add/find the customer in CustomerInfo (Customer Name master).
    3. Update sales_instance.s_customer_name to this CustomerInfo record so the won customer is set in Customer Name.
    4. Mark NewCustomerMaster for this customer as inactive (is_active=False),
       is_business_won=True, business_won_date=..., and link it.
    """
    if not sales_instance or not sales_instance.s_bus_won_not:
        return

    is_won = (sales_instance.s_bus_won_not_id == 1 or str(sales_instance.s_bus_won_not).strip().lower() == 'yes')
    if not is_won:
        return

    new_cust_name = (sales_instance.s_customer_new_name or '').strip()
    if not new_cust_name:
        return

    won_date = sales_instance.s_yesdate_business or timezone.now().date()

    # 1. Find or create in CustomerInfo (Customer Name field master)
    cust_obj = CustomerInfo.objects.filter(cu_name__iexact=new_cust_name).first()
    if not cust_obj:
        cust_type = None
        try:
            if sales_instance.s_customer_type_id:
                cust_type = sales_instance.s_customer_type
        except Exception:
            cust_type = None
        if not cust_type:
            cust_type = CustomertypeInfo.objects.first()

        industry_type = None
        try:
            if sales_instance.s_industry_type_id:
                industry_type = sales_instance.s_industry_type
        except Exception:
            industry_type = None

        cust_code = getattr(sales_instance, 's_customer_code', '') or new_cust_name[:50]
        cust_obj = CustomerInfo.objects.create(
            cu_name=new_cust_name,
            cu_nameshort=new_cust_name[:100],
            cu_customercode=cust_code,
            cu_type=cust_type,
            cu_industry_type=industry_type,
            cu_customerperson=sales_instance.s_Person_name or '',
            cu_designation=sales_instance.s_designation or '',
            cu_contactno=sales_instance.s_contact_no or '',
            cu_email=sales_instance.s_email_id or '',
            cu_business_sol=sales_instance.s_company,
            cu_lastmodifiedby=sales_instance.s_created_by or sales_instance.s_updated_by,
            cu_gstexcepmtion_id=1,
            cu_gstmodel_id=1,
            cu_paymenttype_id=1,
            cu_creditcountfrom_id=1,
            cu_businessmodel_id=1,
        )

    # 2. Update sales_instance to have this won customer in the Customer Name field
    if sales_instance.s_customer_name_id != cust_obj.id:
        SalesInfo.objects.filter(pk=sales_instance.pk).update(s_customer_name=cust_obj)
        sales_instance.s_customer_name = cust_obj

    # 3. Mark NewCustomerMaster record as inactive with business won date
    ncm_records = NewCustomerMaster.objects.filter(customer_name__iexact=new_cust_name)
    if ncm_records.exists():
        ncm_records.update(
            is_active=False,
            is_business_won=True,
            business_won_date=won_date,
            linked_customer=cust_obj
        )
    else:
        NewCustomerMaster.objects.create(
            customer_name=new_cust_name,
            is_active=False,
            is_business_won=True,
            business_won_date=won_date,
            linked_customer=cust_obj,
            created_by=sales_instance.s_created_by or sales_instance.s_updated_by
        )



def get_sales_queryset(user_id, sales_number=None, salesperson_id=None, search_query=None, from_date=None, to_date=None):
    user_ext = User_extInfo.objects.get(user=user_id)
    role_id = RoleInfo.objects.get(role_name=user_ext.emp_role).id

    sales_data_query = SalesInfo.objects.select_related(
        's_created_by',
        's_customer_name',
        's_industry_type',
        's_bus_won_not',
        's_status',
        's_updated_by'
    ).annotate(
        creator_full_name=Concat('s_created_by__first_name', Value(' '), 's_created_by__last_name'),
        updater_full_name=Concat('s_updated_by__first_name', Value(' '), 's_updated_by__last_name')
    )
    if from_date:
        sales_data_query = sales_data_query.filter(s_updated_at__date__gte=from_date)
    if to_date:
        sales_data_query = sales_data_query.filter(s_updated_at__date__lte=to_date)

    # 1. Sales Number filter (STRICTLY filter by Sale Number)
    if sales_number and sales_number.strip():
        sales_data_query = sales_data_query.filter(s_sale_number__icontains=sales_number.strip())

    # 2. Salesperson filter (STRICTLY filter by Salesperson / Created By)
    if salesperson_id and str(salesperson_id).strip():
        sp = str(salesperson_id).strip()
        if sp.isdigit():
            sales_data_query = sales_data_query.filter(s_created_by_id=int(sp))
        else:
            sales_data_query = sales_data_query.filter(
                Q(creator_full_name__icontains=sp) |
                Q(s_created_by__first_name__icontains=sp) |
                Q(s_created_by__last_name__icontains=sp) |
                Q(s_created_by__username__icontains=sp)
            )

    # 3. Global search above the table (searches across all fields)
    if search_query and search_query.strip():
        terms = search_query.strip().split()
        for term in terms:
            q_term = (
                Q(s_sale_number__icontains=term) |
                Q(creator_full_name__icontains=term) |
                Q(s_created_by__username__icontains=term) |
                Q(s_created_by__first_name__icontains=term) |
                Q(s_created_by__last_name__icontains=term) |
                Q(updater_full_name__icontains=term) |
                Q(s_updated_by__username__icontains=term) |
                Q(s_customer_name__cu_name__icontains=term) |
                Q(s_customer_name__cu_customercode__icontains=term) |
                Q(s_customer_new_name__icontains=term) |
                Q(s_industry_type__industry_type__icontains=term) |
                Q(s_status__status__icontains=term) |
                Q(s_bus_won_not__yesno_name__icontains=term) |
                Q(s_Person_name__icontains=term) |
                Q(s_contact_no__icontains=term) |
                Q(s_email_id__icontains=term)
            )
            if term.isdigit():
                q_term |= Q(id=int(term))
            sales_data_query = sales_data_query.filter(q_term)

    if role_id in [1, 3]:
        sales_list = sales_data_query.order_by('-s_created_at')
    else:
        sales_list = sales_data_query.filter(s_created_by=user_id).order_by('-s_created_at')

    return sales_list


@login_required(login_url='login_page')
def sales_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    sales_number = (request.GET.get('sales_number') or '').strip()
    salesperson_id = (request.GET.get('salesperson') or '').strip()
    search_query = (request.GET.get('search') or '').strip()
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)
    role = User_extInfo.objects.get(user=user_id).emp_role

    salespersons = MyUser.objects.filter(
        Q(user_extinfo__department__dept_name="Sales") | Q(s_created_by__isnull=False)
    ).distinct().order_by('first_name', 'last_name')

    sales_list = get_sales_queryset(
        user_id,
        sales_number=sales_number,
        salesperson_id=salesperson_id,
        search_query=search_query,
        from_date=from_date,
        to_date=to_date
    )

    page_number = request.GET.get('page')
    paginator = Paginator(sales_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
        'first_name': first_name,
        'role': role,
        'page_obj': page_obj,
        'from_date': from_date,
        'to_date': to_date,
        'sales_number': sales_number,
        'salespersons': salespersons,
        'selected_salesperson': salesperson_id,
        'search_query': search_query,
    }
    return render(request, "asset_mgt_app/sales_list.html", context)

@login_required(login_url='login_page')
def sales_add(request, sales_id=0):
    context = {}
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = User_extInfo.objects.get(user=user_id).emp_role.id
    Salesmultipleitem_list = SalesmultipleitemInfo.objects.filter(sm_sales_num=sales_id)
    if request.method == "GET":
        if sales_id == 0:
            form = SalesinfoaddForm()
            created_by=user_id
            context = {
                'form': form,
                'role': role,
                'role_id': role_id,
                'sales_id':sales_id,
                'first_name': first_name,
                'created_by': created_by,
                'user_id': user_id,
                'Salesmultipleitem_list': Salesmultipleitem_list,
                # 'sales_num': sales_num,
            }
            return render(request, "asset_mgt_app/sales_add.html", context)
        else:
            salesinfo = SalesInfo.objects.get(pk=sales_id)
            form = SalesinfoaddForm(instance=salesinfo)
            # ses_sales_num_val = request.session.get('ses_sales_num')
            # sale_num = SalesInfo.objects.get(pk=sales_id).s_sale_number
            # sale_num_id=SalesInfo.objects.get(s_sale_number=sale_num).id
            request.session['ses_sales_num_id'] = sales_id
            comments_list_filterd = (Sales_Comments_Info.objects.filter(sc_sales_number=sales_id)).order_by('-sc_created_at')
            Sales_multiple_item_list = SalesmultipleitemInfo.objects.filter(sm_sales_num=sales_id)
            request.session['ses_sales_id'] = sales_id

            context={
                'form': form,
                'role': role,
                'role_id': role_id,
                'sales_id':sales_id,
                'first_name': first_name,
                'user_id': user_id,
                'comments_list_filterd': comments_list_filterd,
                'Salesmultipleitem_list': Sales_multiple_item_list,
            }
            return render(request, "asset_mgt_app/sales_add.html", context)
    else:
        print("I am inside POST")
        if sales_id == 0:
            form = SalesinfoaddForm(request.POST, request.FILES)
            if form.is_valid():
                # Save form but do not commit yet
                sales_instance = form.save(commit=False)

                # Generate Sale number based on financial year (Branch specific)
                fy = get_financial_year()
                branch_id = sales_instance.s_location.id if sales_instance.s_location else get_session_branch_id(request)
                branch_code = get_branch_code(branch_id)
                prefix = f"{fy}_{branch_code}_SL_"
                sales_instance.s_sale_number = generate_next_number(SalesInfo, 's_sale_number', prefix, 6)
                sales_instance.save()
                handle_business_won_customer(sales_instance)

                messages.success(request, 'Record Saved Successfully')
                request.session['ses_sales_id'] = sales_instance.id

                return redirect(f'/SMS/sales_update/{sales_instance.id}')
            else:
                print("Sales Form not saved")
                messages.error(request, 'Record Not Saved. Please Enter All Required Fields')
                # Display form errors
                for field, errors in form.errors.items():
                    for error in errors:
                        print(f"Error in {field}: {error}")
                        messages.error(request, f"Error in {field}: {error}")
                return redirect(request.META['HTTP_REFERER'])
        else:
            sale_num = SalesInfo.objects.get(pk=sales_id).s_sale_number
            request.session['ses_sales_num'] = sale_num
            salesinfo = SalesInfo.objects.get(pk=sales_id)
            form = SalesinfoaddForm(request.POST, request.FILES, instance=salesinfo)
            if form.is_valid():
                saved_sales = form.save()
                handle_business_won_customer(saved_sales)
                print("Sales Form Saved")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Sales Form not saved")
                # Display form errors
                for field, errors in form.errors.items():
                    for error in errors:
                        print(f"Error in {field}: {error}")
                        messages.error(request, f"Error in {field}: {error}")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
        return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/sales_list')

# Delete Assets
@login_required(login_url='login_page')
def sales_delete(request, sales_id):
    salesinfo = SalesInfo.objects.get(pk=sales_id)
    sales_num = SalesInfo.objects.get(pk=sales_id).s_sale_number
    salesinfo.delete()
    print('sales_num',sales_num)
    salescommentsinfo = (Sales_Comments_Info.objects.filter(sc_sales_number=sales_id)).order_by('-sc_created_at')
    for k in salescommentsinfo:
        k.delete()
    return redirect('/SMS/sales_list')

@login_required(login_url='login_page')
def sales_comments_add(request, sales_comments_id=0):
    context = {}
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    ses_sales_num_id=request.session.get('ses_sales_num_id')
    if request.method == "GET":
        if sales_comments_id == 0:
            sales_comments_form = SalescommentForm()
        else:
            # print(context)
            salescommentsinfo = Sales_Comments_Info.objects.get(pk=sales_comments_id)
            sales_comments_form = SalescommentForm(instance=salescommentsinfo)
        context={
            'sales_comments_form': sales_comments_form,
            'role': role,
            'first_name': first_name,
            'user_id': user_id,
            'ses_sales_num_id': ses_sales_num_id,
        }
        return render(request, "asset_mgt_app/sales_comments_add.html", context)
    else:
        if sales_comments_id == 0:
            sales_comments_form = SalescommentForm(request.POST)
        else:
            salescommentsinfo = Sales_Comments_Info.objects.get(pk=sales_comments_id)
            sales_comments_form = SalescommentForm(request.POST, instance=salescommentsinfo)
        if sales_comments_form.is_valid():
            sales_comments_form.save()
            print("Main Form Saved")
        else:
            print("Main form not saved")
        return redirect('/SMS/sales_update/' + str(ses_sales_num_id))
        # return redirect(request.META['HTTP_REFERER'])

        # return redirect(request.META['HTTP_REFERER'])
def get_sales_comments_queryset(user_id, search_query=None, from_date=None, to_date=None):
    user_ext = User_extInfo.objects.get(user=user_id)
    role_id = RoleInfo.objects.get(role_name=user_ext.emp_role).id

    comments_data_query = Sales_Comments_Info.objects.select_related(
        'sc_sales_number',
        'sc_sales_number__s_created_by',
        'sc_sales_number__s_customer_name',
        'sc_call_type',
        'sc_call_nature',
        'sc_call_purpose',
        'sc_updated_by'
    ).annotate(
        updater_full_name=Concat('sc_updated_by__first_name', Value(' '), 'sc_updated_by__last_name'),
        creator_full_name=Concat('sc_sales_number__s_created_by__first_name', Value(' '), 'sc_sales_number__s_created_by__last_name')
    )
    if from_date:
        comments_data_query = comments_data_query.filter(sc_date_of_call__gte=from_date)
    if to_date:
        comments_data_query = comments_data_query.filter(sc_date_of_call__lte=to_date)

    if search_query:
        terms = search_query.strip().split()
        for term in terms:
            q_term = (
                Q(sc_sales_number__s_sale_number__icontains=term) |
                Q(sc_sales_number__s_customer_name__cu_name__icontains=term) |
                Q(sc_sales_number__s_customer_new_name__icontains=term) |
                Q(creator_full_name__icontains=term) |
                Q(sc_sales_number__s_created_by__username__icontains=term) |
                Q(updater_full_name__icontains=term) |
                Q(sc_updated_by__username__icontains=term) |
                Q(sc_updated_by__first_name__icontains=term) |
                Q(sc_updated_by__last_name__icontains=term) |
                Q(sc_call_type__call_type__icontains=term) |
                Q(sc_call_nature__call_nature__icontains=term) |
                Q(sc_call_purpose__call_purpose__icontains=term) |
                Q(sc_comments__icontains=term)
            )
            if term.isdigit():
                q_term |= Q(id=int(term)) | Q(sc_sales_number__id=int(term))
            comments_data_query = comments_data_query.filter(q_term)

    if role_id in [1, 3]:
        comments_list = comments_data_query.order_by('-sc_date_of_call', '-sc_created_at')
    else:
        comments_list = comments_data_query.filter(sc_updated_by=user_id).order_by('-sc_date_of_call', '-sc_created_at')

    return comments_list


@login_required(login_url='login_page')
def sales_comments_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    search_query = (request.GET.get('sales_number') or request.GET.get('search') or '').strip()
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)
    user_ext = User_extInfo.objects.get(user=user_id)

    sales_comments_list = get_sales_comments_queryset(user_id, search_query=search_query, from_date=from_date, to_date=to_date)

    if from_date or to_date or search_query:
        paginator = Paginator(sales_comments_list, 10000)
    else:
        paginator = Paginator(sales_comments_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'comments_list': sales_comments_list,
        'role': user_ext.emp_role,
        'user_id': user_id,
        'first_name': first_name,
        'page_obj': page_obj,
        'from_date': from_date,
        'to_date': to_date,
        'sales_number': search_query,
    }
    return render(request, "asset_mgt_app/sales_comments_list.html", context)


@login_required(login_url='login_page')
def sales_comments_delete(request, sales_comments_id):
    salescommentsinfo = Sales_Comments_Info.objects.get(pk=sales_comments_id)
    salescommentsinfo.delete()
    return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login_page')
def sales_search(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    sales_number = (request.GET.get('sales_number') or '').strip()
    salesperson_id = (request.GET.get('salesperson') or '').strip()
    search_query = (request.GET.get('search') or '').strip()
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)
    role = User_extInfo.objects.get(user=user_id).emp_role

    salespersons = MyUser.objects.filter(
        Q(user_extinfo__department__dept_name="Sales") | Q(s_created_by__isnull=False)
    ).distinct().order_by('first_name', 'last_name')

    sales_list = get_sales_queryset(
        user_id,
        sales_number=sales_number,
        salesperson_id=salesperson_id,
        search_query=search_query,
        from_date=from_date,
        to_date=to_date
    )

    page_number = request.GET.get('page')
    paginator = Paginator(sales_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
        'first_name': first_name,
        'role': role,
        'page_obj': page_obj,
        'from_date': from_date,
        'to_date': to_date,
        'sales_number': sales_number,
        'salespersons': salespersons,
        'selected_salesperson': salesperson_id,
        'search_query': search_query,
    }
    return render(request, "asset_mgt_app/sales_list.html", context)


@login_required(login_url='login_page')
def sales_comments_search(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    search_query = (request.GET.get('sales_number') or request.GET.get('search') or '').strip()
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)
    user_ext = User_extInfo.objects.get(user=user_id)

    sales_comments_list = get_sales_comments_queryset(user_id, search_query=search_query, from_date=from_date, to_date=to_date)

    if from_date or to_date or search_query:
        paginator = Paginator(sales_comments_list, 10000)
    else:
        paginator = Paginator(sales_comments_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'first_name': first_name,
        'role': user_ext.emp_role,
        'user_id': user_id,
        'page_obj': page_obj,
        'from_date': from_date,
        'to_date': to_date,
        'sales_number': search_query,
    }
    return render(request, "asset_mgt_app/sales_comments_list.html", context)

@login_required(login_url='login_page')
def sales_reports(request):
    first_name = request.session.get('first_name')
    context = {
               'first_name': first_name
               }
    return render(request,"asset_mgt_app/sales_reports.html",context)

@login_required(login_url='login_page')
def sales_multiple_item_add(request, sales_multiple_id=0, enquiry_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    sales_id = request.session.get('ses_sales_id')
    print('sales_id',sales_id)
    if request.method == "GET":
        if sales_multiple_id == 0:
            form = SalesmultipleitemForm()
        else:
            salesmultiple = SalesmultipleitemInfo.objects.get(pk=sales_multiple_id)
            form = SalesmultipleitemForm(instance=salesmultiple)
        context={
                    'form': form,
                    'first_name': first_name,
                    'sales_id': sales_id,
                    'enquiry_id': enquiry_id,
                    'user_id': user_id
                }
        return render(request, "asset_mgt_app/salesmultipleitem_add.html", context)
    else:
        if sales_multiple_id == 0:
            form = SalesmultipleitemForm(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                sales_id = (SalesmultipleitemInfo.objects.latest('id')).id
                messages.success(request, 'saved successfully')
                return redirect('/SMS/sales_multiple_item_update/' + str(sales_id))  # Use the new item's ID
            else:
                messages.error(request, 'Form is not valid')
                print(form.errors)  # Debugging
                return redirect('/SMS/sales_multiple_item_add')
        else:
            try:
                salesmultiple = SalesmultipleitemInfo.objects.get(pk=sales_multiple_id)
            except SalesmultipleitemInfo.DoesNotExist:
                messages.error(request, 'Sales multiple item not found.')
                return redirect('/SMS/salesmultipleitem_list')

            form = SalesmultipleitemForm(request.POST,request.FILES, instance=salesmultiple)
            if form.is_valid():
                form.save()
                messages.success(request, ' updated successfully')
                return redirect(request.META.get('HTTP_REFERER', '/SMS/salesmultipleitem_list'))
            else:
                messages.error(request, 'Form is not valid')
                print(form.errors)  # Debugging
                return redirect(request.META.get('HTTP_REFERER', '/SMS/salesmultipleitem_list'))


@login_required(login_url='login_page')
def sales_multiple_item_list(request):
    first_name = request.session.get('first_name')
    sales_id = request.session.get('ses_sales_id')

    Salesmultipleitem_list = SalesmultipleitemInfo.objects.filter(sm_customer_name=sales_id)

    context = {
        'Salesmultipleitem_list': Salesmultipleitem_list,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/salesmultipleitem_list.html", context)

@login_required(login_url='login_page')
def sales_multiple_item_delete(request, sales_multiple_id):
    salesmultiple = SalesmultipleitemInfo.objects.get(pk=sales_multiple_id)
    salesmultiple.delete()
    messages.success(request, 'deleted successfully')
    return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login_page')
def sales_multiple_item_cancel(request, sales_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    salesmultiple_id = request.session.get('sales_multiple_id')
    sales_id = request.session.get('ses_sales_id')
    return redirect(f'/SMS/sales_update/{sales_id}')