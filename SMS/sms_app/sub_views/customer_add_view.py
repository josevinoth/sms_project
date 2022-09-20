from django.contrib.auth.decorators import login_required
from ..forms import CustomeraddForm
from ..models import CustomerInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def customer_add(request,customer_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if customer_id == 0:
            form = CustomeraddForm()
        else:
            customer=CustomerInfo.objects.get(pk=customer_id)
            form = CustomeraddForm(instance=customer)
        context={
                'form': form,
                'first_name': first_name,
                'user_id':user_id,
        }
        return render(request, "asset_mgt_app/customer_add.html",context )
    else:
        if customer_id == 0:
            form = CustomeraddForm(request.POST)
        else:
            customer = CustomerInfo.objects.get(pk=customer_id)
            form = CustomeraddForm(request.POST,instance=customer)
        if form.is_valid():
            print("Form is Valid")
            form.save()
        else:
            print("Form is Not Valid")
        return redirect('/SMS/customer_list')

# List customer
@login_required(login_url='login_page')
def customer_list(request):
    first_name = request.session.get('first_name')
    context = {'customer_list' : CustomerInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/customer_list.html",context)

#Delete customer
@login_required(login_url='login_page')
def customer_delete(request,customer_id):
    customer = CustomerInfo.objects.get(pk=customer_id)
    customer.delete()
    return redirect('/SMS/customer_list')