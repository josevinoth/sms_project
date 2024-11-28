from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..forms import CustomeraddForm,CustomerattachForm
from ..models import CustomerInfo,Customerattach
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def customer_add(request,customer_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    customer_attachment_list = Customerattach.objects.all()
    if request.method == "GET":
        if customer_id == 0:
            form = CustomeraddForm()
        else:
            customer=CustomerInfo.objects.get(pk=customer_id)
            form = CustomeraddForm(instance=customer)
            customer_attachment_list = Customerattach.objects.filter(ca_customer_name=customer_id)
            request.session['ses_customer_id'] = customer_id
            print(customer_id)
        context={
                'form': form,
                'first_name': first_name,
                'user_id':user_id,
                'customer_attach_list' : customer_attachment_list,
        }
        return render(request, "asset_mgt_app/customer_add.html",context )
    else:
        if customer_id == 0:
            form = CustomeraddForm(request.POST)
            if form.is_valid():
                form.save()
                print("Customer Form is Valid")
                customer_name = request.POST.get('cu_nameshort')
                customer_id = CustomerInfo.objects.get(cu_nameshort=customer_name).id
                url = 'customer_update/' + str(customer_id)
                messages.success(request, 'Record Updated Successfully')
                request.session['ses_customer_id'] = customer_id
                return redirect(url)
            else:
                print("Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            customer = CustomerInfo.objects.get(pk=customer_id)
            form = CustomeraddForm(request.POST,instance=customer)
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


@login_required(login_url='login_page')
def customer_attach_add(request, attach_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    customer_id = request.session.get('ses_customer_id')
    print('customer_id',customer_id)
    if request.method == "GET":
        if attach_id == 0:
            form = CustomerattachForm()
        else:
            try:
                attach = Customerattach.objects.get(pk=attach_id)
                form = CustomerattachForm(instance=attach)
            except Customerattach.DoesNotExist:
                messages.error(request, 'Attachment not found')
                return redirect('/SMS/customer_attachment_list')
        return render(request, "asset_mgt_app/customer_attach_add.html", {'form': form, 'first_name': first_name,'customer_id':customer_id,'user_id':user_id})

    elif request.method == "POST":
        if attach_id == 0:
            form = CustomerattachForm(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                customer_id = request.session.get('ses_customer_id')
                customer_attachment_id =  max(Customerattach.objects.filter(ca_customer_name=customer_id).values_list('id',flat=True))
                print('customer_attachment_id',customer_attachment_id)
                messages.success(request, 'Attachment saved successfully')
                return redirect('/SMS/customer_attachment_update/'+str(customer_attachment_id))
            else:
                messages.error(request, 'Form is not valid')
                print(form.errors)  # Print form errors to the console for debugging
                return redirect('/SMS/customer_attachment_add')
        else:
            attach = Customerattach.objects.get(pk=attach_id)
            form = CustomerattachForm(request.POST,request.FILES, instance=attach)
            if form.is_valid():
                form.save()
                messages.success(request, 'Attachment saved successfully')
                return redirect(request.META['HTTP_REFERER'])
            else:
                messages.error(request, 'Form is not valid')
                print(form.errors)  # Print form errors to the console for debugging
                return redirect(request.META['HTTP_REFERER'])

# List bay
@login_required(login_url='login_page')
def customer_attach_list(request):
    first_name = request.session.get('first_name')  # If needed for context
    # Fetch all customer attachments
    customer_attachment_list = Customerattach.objects.all()

    context = {
        'customer_attach_list': customer_attachment_list,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/customer_attach_list.html", context)
#Delete bay
@login_required(login_url='login_page')
def customer_attach_delete(request, attach_id):
    attach = Customerattach.objects.get(pk=attach_id)
    attach.delete()
    messages.success(request, 'Attachment deleted successfully')
    return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login_page')
def customer_attach_cancel(request, customer_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    attach_id = request.session.get('attach_id')
    customer_id = request.session.get('ses_customer_id')
    return redirect(f'/SMS/customer_update/{customer_id}')




