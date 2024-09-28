from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse

from ..forms import SalescommentForm,SalesinfoaddForm
from ..models import RoleInfo,Sales_Comments_Info,User_extInfo,SalesInfo
from django.shortcuts import render, redirect
from random import randint

from ..sub_models.customer_mod import CustomerInfo


@login_required(login_url='login_page')
def sales_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id=RoleInfo.objects.get(role_name=role).id

    if role_id==3:
        sales_list= (SalesInfo.objects.all()).order_by('-s_created_at')
    elif role_id==1:
        sales_list = (SalesInfo.objects.all()).order_by('-s_created_at')
    else:
        sales_list = (SalesInfo.objects.filter(s_created_by=user_id)).order_by('-s_created_at')
    page_number = request.GET.get('page')
    paginator = Paginator(sales_list, 10000)
    page_obj = paginator.get_page(page_number)
    context = {
        # 'sales_list': sales_list,
        'first_name': first_name,
        'role': role,
        'page_obj': page_obj,
    }
    return render(request, "asset_mgt_app/sales_list.html", context)

@login_required(login_url='login_page')
def sales_add(request, sales_id=0):
    context = {}
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = User_extInfo.objects.get(user=user_id).emp_role.id
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
                # 'sales_num': sales_num,
            }
            return render(request, "asset_mgt_app/sales_add.html", context)
        else:
            salesinfo = SalesInfo.objects.get(pk=sales_id)
            form = SalesinfoaddForm(instance=salesinfo)
            ses_sales_num_val = request.session.get('ses_sales_num')
            sale_num = SalesInfo.objects.get(pk=sales_id).s_sale_number
            sale_num_id=SalesInfo.objects.get(s_sale_number=sale_num).id
            request.session['ses_sales_num_id'] = sale_num_id
            comments_list_filterd = (Sales_Comments_Info.objects.filter(sc_sales_number=sale_num_id)).order_by('-sc_created_at')

            context={
                'form': form,
                'role': role,
                'role_id': role_id,
                'sales_id':sales_id,
                'first_name': first_name,
                'user_id': user_id,
                'comments_list_filterd': comments_list_filterd,
            }
            return render(request, "asset_mgt_app/sales_add.html", context)
    else:
        if sales_id == 0:
            form = SalesinfoaddForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                print("Sales Form Saved")
                try:
                    last_id = SalesInfo.objects.latest('id').id
                    # sales_num_next =str('S_')+str(int(((SalesInfo.objects.get(id=last_id)).s_sale_number).replace('S_', ''))+1)
                    sales_num_next=1000000+last_id
                except ObjectDoesNotExist:
                    # sales_num_next = str('S_') + str(randint(10000, 99999))
                    sales_num_next=1000000
                sales_num_next = str('S_') +str(sales_num_next)
                SalesInfo.objects.filter(id=last_id).update(s_sale_number=sales_num_next)
                messages.success(request, 'Record Updated Successfully')
                # sales_num = request.POST.get('s_sale_number')
                sales_id = SalesInfo.objects.get(s_sale_number=sales_num_next).id
                # url = 'sales_update/' + str(sales_id)
                # print(url)
                return redirect('/SMS/sales_update/' + str(sales_id))
                # return redirect(url)
            else:
                print("Sales Form not saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
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
        return redirect('/SMS/sales_list')
        # return redirect(request.META['HTTP_REFERER'])
@login_required(login_url='login_page')
def sales_comments_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = RoleInfo.objects.get(role_name=role).id

    if role_id == 3:
        sales_comments_list=(Sales_Comments_Info.objects.all()).order_by('-sc_created_at')
    elif role_id == 1:
        sales_comments_list=(Sales_Comments_Info.objects.all()).order_by('-sc_created_at')
    else:
        sales_comments_list = (Sales_Comments_Info.objects.all(sc_updated_by=user_id)).order_by('-sc_created_at')
    page_number = request.GET.get('page')
    paginator = Paginator(sales_comments_list, 10000)
    page_obj = paginator.get_page(page_number)

    context = {
        'comments_list':sales_comments_list,
        'role': role,
        'user_id': user_id,
        'first_name': first_name,
        'page_obj': page_obj,
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
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = RoleInfo.objects.get(role_name=role).id
    if not sales_number:
        sales_number = ""

    if role_id == 3:
        sales_list = SalesInfo.objects.filter((Q(s_sale_number__icontains=sales_number)) | (Q(s_sale_number__isnull=True))).order_by('-s_created_at')
    elif role_id == 1:
        sales_list = SalesInfo.objects.filter((Q(s_sale_number__icontains=sales_number)) | (Q(s_sale_number__isnull=True))).order_by('-s_created_at')
    else:
        sales_list = SalesInfo.objects.filter((Q(s_sale_number__icontains =sales_number,s_created_by=user_id))|(Q(s_sale_number__isnull=True,s_created_by=user_id))).order_by('-s_created_at')

    page_number = request.GET.get('page')
    paginator = Paginator(sales_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
        # 'sales_list': sales_list,
        'first_name': first_name,
        'page_obj': page_obj,
        }
    return render(request, "asset_mgt_app/sales_list.html", context)

@login_required(login_url='login_page')
def sales_comments_search(request):
    first_name = request.session.get('first_name')
    sales_number = request.GET.get('sales_number')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = RoleInfo.objects.get(role_name=role).id

    if not sales_number:
        sales_number = ""

    if role_id == 3:
        sales_comments_list = (Sales_Comments_Info.objects.filter(Q(sc_sales_number__s_sale_number__icontains=sales_number) | Q(sc_sales_number__s_sale_number__isnull=True))).order_by('-sc_created_at')
    elif role_id == 1:
        sales_comments_list = (Sales_Comments_Info.objects.filter(Q(sc_sales_number__s_sale_number__icontains=sales_number) | Q(sc_sales_number__s_sale_number__isnull=True))).order_by('-sc_created_at')
    else:
        sales_comments_list = (Sales_Comments_Info.objects.filter(Q(sc_sales_number__s_sale_number__icontains =sales_number,sc_updated_by=user_id)|Q(sc_sales_number__s_sale_number__isnull=True,sc_updated_by=user_id))).order_by('-sc_created_at')

    page_number = request.GET.get('page')
    paginator = Paginator(sales_comments_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
        # 'sales_list': sales_list,
        'first_name': first_name,
        'page_obj': page_obj,
        }
    return render(request, "asset_mgt_app/sales_comments_list.html", context)
