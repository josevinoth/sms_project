from django.contrib import messages
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
            form = CustomeraddForm(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                print("Customer Form is Valid")
                customer_name = request.POST.get('cu_nameshort')
                customer_id = CustomerInfo.objects.get(cu_nameshort=customer_name).id
                url = 'customer_update/' + str(customer_id)
                messages.success(request, 'Record Updated Successfully')
                return redirect(url)
            else:
                print("Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            customer = CustomerInfo.objects.get(pk=customer_id)
            form = CustomeraddForm(request.POST,request.FILES,instance=customer)
            if form.is_valid():
                form.save()
                print("Customer Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/customer_list')

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