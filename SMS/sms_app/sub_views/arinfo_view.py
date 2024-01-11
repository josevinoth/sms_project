from django.contrib.auth.decorators import login_required
from ..forms import ArinfoaddForm
from ..models import BilingInfo,Ar_comments_Info,User_extInfo,Ar_Info
from django.shortcuts import render, redirect
import qrcode
from io import BytesIO
import qrcode.image.svg

@login_required(login_url='login_page')
def ar_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    context = {
        'ar_list': Ar_Info.objects.all(),
        'first_name': first_name,
        'role': role,
    }
    return render(request, "asset_mgt_app/ar_list.html", context)

@login_required(login_url='login_page')
def ar_add(request, ar_id=0):
    context = {}
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    if request.method == "GET":
        if ar_id == 0:
            form = ArinfoaddForm()
            context = {
                'form': form,
                'role': role,
                'first_name': first_name,
                'user_id': user_id,
            }
        else:
            invoice_number=Ar_Info.objects.get(pk=ar_id).ar_invoice_num
            arcomments_list= Ar_comments_Info.objects.filter(arc_invoice_num=invoice_number)
            arinfo = Ar_Info.objects.get(pk=ar_id)
            form = ArinfoaddForm(instance=arinfo)
            invoice_list_ar=list((Ar_Info.objects.values_list('ar_invoice_num',flat=True)).distinct())
            print('invoice_list_ar',invoice_list_ar)
            for i in invoice_list_ar:
                print(i)
                try:
                    billing_id=BilingInfo.objects.get(bill_invoice_ref=i).id
                    print(billing_id.bill_invoice_ref)
                except:
                    pass
            context={
                'form': form,
                'role': role,
                'first_name': first_name,
                'user_id': user_id,
                'arcomments_list': arcomments_list,
            }
        return render(request, "asset_mgt_app/ar_add.html", context)
    else:
        if ar_id == 0:
            form = ArinfoaddForm(request.POST)
        else:
            arinfo = Ar_Info.objects.get(pk=ar_id)
            form = ArinfoaddForm(request.POST, instance=arinfo)
        if form.is_valid():
            form.save()
            print('Main Form Saved')
        else:
            print("Main Form Not Saved")
        return redirect('/SMS/ar_list')

# Delete Assets
@login_required(login_url='login_page')
def ar_delete(request, ar_id):
    arinfo = Ar_Info.objects.get(pk=ar_id)
    arinfo.delete()
    return redirect('/SMS/ar_list')