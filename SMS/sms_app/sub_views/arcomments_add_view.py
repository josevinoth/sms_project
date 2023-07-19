from django.contrib import messages
from django.contrib.auth.decorators import login_required
from numpy.ma import count

from ..forms import ArCommentsaddForm
from ..models import MyUser,CustomerInfo,Ar_Info,Ar_comments_Info
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def arcomments_add(request,arcomments_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print(user_id)
    if request.method == "GET":
        if arcomments_id == 0:
            Ar_comments_form= ArCommentsaddForm()
            print("Inside Get Add")
        else:
            print("Inside Get Edit")
            arcomments=Ar_comments_Info.objects.get(pk=arcomments_id)
            Ar_comments_form= ArCommentsaddForm(instance=arcomments)
        ar_invoice_list=Ar_Info.objects.filter(ar_status=6)
        context={
                'Ar_comments_form': Ar_comments_form,
                'first_name': first_name,
                'ar_invoice_list': ar_invoice_list,
                'user_id': user_id,
                }
        return render(request, "asset_mgt_app/ar_comments_add.html", context)
    else:
        if arcomments_id == 0:
            # Ar_comments_form= ArCommentsaddForm(request.POST)
            print("Inside post add")
            invoice_comments = request.POST.get('arc_comments')
            invoice_updated_by = MyUser.objects.get(id=int(request.POST.get('arc_updated_by')))
            invoice_customer = CustomerInfo.objects.get(id=int(request.POST.get('arc_customer')))
            invoice_number = request.POST.get('arc_invoice_num')
            customer_contact_name = request.POST.get('arc_customer_contact_name')
            customer_contact_designation = request.POST.get('arc_customer_contact_designation')
            invoice_number_list = list(invoice_number.split(','))
            for i in range(0, count(list(invoice_number_list))):
                instance = Ar_comments_Info(arc_invoice_num=invoice_number_list[i], arc_comments=invoice_comments,
                                            arc_customer=invoice_customer, arc_updated_by=invoice_updated_by,arc_customer_contact_name=customer_contact_name,arc_customer_contact_designation=customer_contact_designation)
                instance.save()
            messages.success(request, 'Record Updated Successfully')
        else:
            print("Inside post edit")
            arcomments = Ar_comments_Info.objects.get(pk=arcomments_id)
            Ar_comments_form= ArCommentsaddForm(request.POST,instance=arcomments)
            if Ar_comments_form.is_valid():
                Ar_comments_form.save()
                print("Ar Comments main form saved")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Ar Comments main form not saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
        return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/ar_comments_list')

# List ar_comments
@login_required(login_url='login_page')
def arcomments_list(request):
    first_name = request.session.get('first_name')
    context = {
                'arcomments_list' : Ar_comments_Info.objects.all(),
                'first_name': first_name
            }
    return render(request,"asset_mgt_app/ar_comments_list.html",context)

#Delete ar_comments
@login_required(login_url='login_page')
def arcomments_delete(request,arcomments_id):
    arcomments = Ar_comments_Info.objects.get(pk=arcomments_id)
    arcomments.delete()
    return redirect('/SMS/ar_comments_list')