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

    # Fetch all attachments for the current customer
    customer_attachment_list = Customerattach.objects.filter(ca_customer_name_id=customer_id)
    print("Customer ID:", customer_id)

    if request.method == "GET":
        if attach_id == 0:
            form = CustomerattachForm()
        else:
            try:
                attach = Customerattach.objects.get(pk=attach_id)
                form = CustomerattachForm(instance=attach)
            except Customerattach.DoesNotExist:
                messages.error(request, 'Attachment not found')
                return redirect(f'/SMS/customer_add/{customer_id}')

        context = {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
            'customer_id': customer_id,
            'customer_attachment_list': customer_attachment_list,  # pass the list here
        }
        return render(request, "asset_mgt_app/customer_attach_add.html", context)

    elif request.method == "POST":
        instance = None if attach_id == 0 else Customerattach.objects.get(pk=attach_id)
        form = CustomerattachForm(request.POST, request.FILES, instance=instance)

        if form.is_valid():
            new_category = form.cleaned_data['ca_category']
            new_status = form.cleaned_data['ca_status']

            # Allow only one active attachment per category
            if new_status.id == 1:  # Assuming Status ID 1 = Active
                active_exists = Customerattach.objects.filter(
                    ca_customer_name=customer_id,
                    ca_category=new_category,
                    ca_status_id=1
                )
                if attach_id == 0 and active_exists.exists():
                    messages.error(request, f"Only one active attachment is allowed for {new_category}.")
                    # Re-render page with updated list
                    context = {
                        'form': form,
                        'first_name': first_name,
                        'user_id': user_id,
                        'customer_id': customer_id,
                        'customer_attachment_list': customer_attachment_list,
                    }
                    return render(request, "asset_mgt_app/customer_attach_add.html", context)

            form.save()
            messages.success(request, 'Attachment saved successfully')

            # After saving, refresh the list and render the same page
            customer_attachment_list = Customerattach.objects.filter(ca_customer_name_id=customer_id)
            last_id = Customerattach.objects.filter(ca_customer_name=customer_id).latest('id').id
            form = CustomerattachForm()  # reset form after saving
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'customer_id': customer_id,
                'customer_attachment_list': customer_attachment_list,
            }
            return render(request, "asset_mgt_app/customer_attach_add.html", context)

        else:
            messages.error(request, 'Form is not valid')
            print(form.errors)
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'customer_id': customer_id,
                'customer_attachment_list': customer_attachment_list,
            }
            return render(request, "asset_mgt_app/customer_attach_add.html", context)

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
