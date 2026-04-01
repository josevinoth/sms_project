from django.contrib import messages
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from ..forms import SalescommentForm,SalesinfoaddForm,SalesmultipleitemForm
from ..models import RoleInfo,Sales_Comments_Info,User_extInfo,SalesInfo,SalesmultipleitemInfo
from django.shortcuts import render, redirect
from random import randint

from ..sub_models.customer_mod import CustomerInfo


@login_required(login_url='login_page')
def sales_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id=RoleInfo.objects.get(role_name=role).id

    sales_data_query = SalesInfo.objects.all()
    if from_date:
        sales_data_query = sales_data_query.filter(s_updated_at__date__gte=from_date)
    if to_date:
        sales_data_query = sales_data_query.filter(s_updated_at__date__lte=to_date)

    if role_id==3:
        sales_list= sales_data_query.order_by('-s_created_at')
    elif role_id==1:
        sales_list = sales_data_query.order_by('-s_created_at')
    else:
        sales_list = (sales_data_query.filter(s_created_by=user_id)).order_by('-s_created_at')

    page_number = request.GET.get('page')
    paginator = Paginator(sales_list, 10000)
    page_obj = paginator.get_page(page_number)
    context = {
        # 'sales_list': sales_list,
        'first_name': first_name,
        'role': role,
        'page_obj': page_obj,
        'from_date': from_date,
        'to_date': to_date,
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
                form.save()
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
@login_required(login_url='login_page')
def sales_comments_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)

    # Get user's role
    user_ext = User_extInfo.objects.get(user=user_id)
    role_id = RoleInfo.objects.get(role_name=user_ext.emp_role).id

    sales_data_query = Sales_Comments_Info.objects.all()
    if from_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__gte=from_date)
    if to_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__lte=to_date)
    # Filtering based on role
    if role_id in [1, 3]:  # Role ID 1 & 3 should see all records
        sales_comments_list = sales_data_query.order_by('-sc_created_at')  # Latest created at first
    else:
        sales_comments_list = sales_data_query.filter(sc_updated_by=user_id).order_by('-sc_created_at')

    # Paginate results
    paginator = Paginator(sales_comments_list, 10000)  # Large number to ensure all results load
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'comments_list': sales_comments_list,  # All records (useful for processing)
        'role': user_ext.emp_role,
        'user_id': user_id,
        'first_name': first_name,
        'page_obj': page_obj,  # Paginated data for the table
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, "asset_mgt_app/sales_comments_list.html", context)
@login_required(login_url='login_page')
def sales_comments_delete(request, sales_comments_id):
    salescommentsinfo = Sales_Comments_Info.objects.get(pk=sales_comments_id)
    salescommentsinfo.delete()
    return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/sales_list')

@login_required(login_url='login_page')
def sales_search(request):
    first_name = request.session.get('first_name')
    sales_number = request.GET.get('sales_number')
    user_id = request.session.get('ses_userID')
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = RoleInfo.objects.get(role_name=role).id
    sales_data_query = SalesInfo.objects.all()
    if from_date:
        sales_data_query = sales_data_query.filter(s_updated_at__date__gte=from_date)
    if to_date:
        sales_data_query = sales_data_query.filter(s_updated_at__date__lte=to_date)

    if not sales_number:
        sales_number = ""

    if role_id == 3:
        sales_list = sales_data_query.filter((Q(s_sale_number__icontains=sales_number)) | (Q(s_sale_number__isnull=True))).order_by('-s_created_at')
    elif role_id == 1:
        sales_list = sales_data_query.filter((Q(s_sale_number__icontains=sales_number)) | (Q(s_sale_number__isnull=True))).order_by('-s_created_at')
    else:
        sales_list = sales_data_query.filter((Q(s_sale_number__icontains =sales_number,s_created_by=user_id))|(Q(s_sale_number__isnull=True,s_created_by=user_id))).order_by('-s_created_at')

    page_number = request.GET.get('page')
    paginator = Paginator(sales_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
        # 'sales_list': sales_list,
        'first_name': first_name,
        'page_obj': page_obj,
        'from_date': from_date,
        'to_date': to_date,
        }
    return render(request, "asset_mgt_app/sales_list.html", context)

@login_required(login_url='login_page')
def sales_comments_search(request):
    first_name = request.session.get('first_name')
    sales_number = request.GET.get('sales_number')
    user_id = request.session.get('ses_userID')
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = RoleInfo.objects.get(role_name=role).id
    sales_data_query = Sales_Comments_Info.objects.all()
    if from_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__gte=from_date)
    if to_date:
        sales_data_query = sales_data_query.filter(sc_updated_at__date__lte=to_date)
    if not sales_number:
        sales_number = ""

    if role_id == 3:
        sales_comments_list = (sales_data_query.filter(Q(sc_sales_number__s_sale_number__icontains=sales_number) | Q(sc_sales_number__s_sale_number__isnull=True))).order_by('-sc_created_at')
    elif role_id == 1:
        sales_comments_list = (sales_data_query.filter(Q(sc_sales_number__s_sale_number__icontains=sales_number) | Q(sc_sales_number__s_sale_number__isnull=True))).order_by('-sc_created_at')
    else:
        sales_comments_list = (sales_data_query.filter(Q(sc_sales_number__s_sale_number__icontains =sales_number,sc_updated_by=user_id)|Q(sc_sales_number__s_sale_number__isnull=True,sc_updated_by=user_id))).order_by('-sc_created_at')

    page_number = request.GET.get('page')
    paginator = Paginator(sales_comments_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
        # 'sales_list': sales_list,
        'first_name': first_name,
        'page_obj': page_obj,
        'from_date': from_date,
        'to_date': to_date,
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
def sales_multiple_item_add(request, sales_multiple_id=0):
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