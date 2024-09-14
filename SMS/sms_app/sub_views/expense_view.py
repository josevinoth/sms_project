from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q

from ..models import ExpenseInfo
from django.shortcuts import render, redirect
from ..forms import ExpenseaddForm

# Invoicecity
@login_required(login_url='login_page')
def expense_add(request,expense_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if expense_id == 0:
            expense_form = ExpenseaddForm()
            context={
                'expense_form': expense_form,
                'first_name':first_name,
                'user_id':user_id,
            }
        else:
            expense = ExpenseInfo.objects.get(pk=expense_id)
            expense_form = ExpenseaddForm(instance=expense)
            context= {
                'user_id':user_id,
                'expense_form': expense_form,
                'first_name': first_name,
                }
        return render(request, "asset_mgt_app/expense_add.html", context)
    else:
        if expense_id == 0:
            expense_form = ExpenseaddForm(request.POST)
            if expense_form.is_valid():
                expense_form.save()
                try:
                    last_id = ExpenseInfo.objects.latest('id').id
                    expense_num = 1000000+last_id
                    print('last_id', last_id)
                    print('expense_num', expense_num)
                except ObjectDoesNotExist:
                    expense_num=str(100000)
                expense_category_Id = ExpenseInfo.objects.latest('id').exp_category.id
                print('expense_category_Id', expense_category_Id)
                if expense_category_Id == 1:
                    expense_num = str('C_') + str(expense_num)
                else:
                    expense_num = str('B_') + str(expense_num)

                last_id = ExpenseInfo.objects.latest('id').id
                ExpenseInfo.objects.filter(id=last_id).update(exp_number=expense_num)
                print("Main Form Saved")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Main Form Not Saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
            last_id = ExpenseInfo.objects.latest('id').id
            return redirect('/SMS/expense_update/' + str(last_id))
            # return redirect(request.META['HTTP_REFERER'])
        else:
            expense = ExpenseInfo.objects.get(pk=expense_id)
            expense_form = ExpenseaddForm(request.POST, instance=expense)
            if expense_form.is_valid():
                expense_form.save()
                print("Main Form Saved")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Main Form Not Saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/expense_list')

@login_required(login_url='login_page')
def expense_list(request):
    first_name = request.session.get('first_name')
    organisation_id = request.session.get('ses_organisation_id')
    role_id = request.session.get('ses_role_id')
    expense_list_val = (ExpenseInfo.objects.filter(Q(exp_business=organisation_id))).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(expense_list_val, 1000000)
    page_obj = paginator.get_page(page_number)
    context =   {
                'expense_list_val' : expense_list_val,
                'first_name': first_name,
                'page_obj': page_obj,
                'role_id': role_id,
                }
    return render(request,"asset_mgt_app/expense_list.html",context)

@login_required(login_url='login_page')
def expense_delete(request,expense_id):
    expense_del = ExpenseInfo.objects.get(pk=expense_id)
    expense_del.delete()
    return redirect('/SMS/expense_list')

@login_required(login_url='login_page')
def expense_search(request):
    first_name = request.session.get('first_name')
    expense_number = request.GET.get('expense_number')
    role = request.session.get('ses_role')
    organisation_id = request.session.get('ses_organisation_id')
    print('organisation_id',organisation_id)
    if not expense_number:
        expense_number = ""
    expense_list = ExpenseInfo.objects.filter(Q(exp_business=organisation_id)&(Q(exp_number__icontains=expense_number)) | (Q(exp_number__isnull=True))).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(expense_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
            'expense_list' : expense_list,
            'first_name': first_name,
            'page_obj': page_obj,
            'role': role,
            }
    return render(request,"asset_mgt_app/expense_list.html",context)

