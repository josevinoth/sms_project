from django.contrib.auth.decorators import login_required
from ..forms import SalestargetaddForm
from ..models import Sales_target_info
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def sales_target_add(request,sales_target_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print(user_id)
    if request.method == "GET":
        if sales_target_id == 0:
            sales_target_form = SalestargetaddForm()
        else:
            sales_target_info=Sales_target_info.objects.get(pk=sales_target_id)
            sales_target_form = SalestargetaddForm(instance=sales_target_info)
        context={
                'sales_target_form': sales_target_form,
                'first_name': first_name,
                'user_id': user_id,
                }
        return render(request, "asset_mgt_app/sales_target_add.html", context)
    else:
        if sales_target_id == 0:
            sales_target_form = SalestargetaddForm(request.POST)
        else:
            sales_target_info = Sales_target_info.objects.get(pk=sales_target_id)
            sales_target_form = SalestargetaddForm(request.POST,instance=sales_target_info)
        if sales_target_form.is_valid():
            sales_target_form.save()
        return redirect('/SMS/sales_target_list')

# List sales_target
@login_required(login_url='login_page')
def sales_target_list(request):
    first_name = request.session.get('first_name')
    context =   {
                    'sales_target_list' : Sales_target_info.objects.all(),
                    'first_name': first_name
                }
    return render(request,"asset_mgt_app/sales_target_list.html",context)

#Delete sales_target
@login_required(login_url='login_page')
def sales_target_delete(request,sales_target_id):
    sales_target_info = Sales_target_info.objects.get(pk=sales_target_id)
    sales_target_info.delete()
    return redirect('/SMS/sales_target_list')