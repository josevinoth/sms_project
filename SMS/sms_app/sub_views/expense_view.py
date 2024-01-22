from django.contrib import messages
from django.contrib.auth.decorators import login_required
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
    expense_list_val = (ExpenseInfo.objects.all()).order_by('-id')
    context =   {
                'expense_list_val' : expense_list_val,
                'first_name': first_name,
                }
    return render(request,"asset_mgt_app/expense_list.html",context)

@login_required(login_url='login_page')
def expense_delete(request,expense_id):
    expense_del = ExpenseInfo.objects.get(pk=expense_id)
    expense_del.delete()
    return redirect('/asset_mgt_app/expense_list')


