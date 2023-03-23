from django.contrib.auth.decorators import login_required
from ..forms import SalesinfoaddForm
from ..models import User_extInfo,SalesInfo
from django.shortcuts import render, redirect
import qrcode
from io import BytesIO
import qrcode.image.svg
@login_required(login_url='login_page')
def sales_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    context = {
        'sales_list': SalesInfo.objects.all(),
        'first_name': first_name,
        'role': role,
    }
    return render(request, "asset_mgt_app/sales_list.html", context)

@login_required(login_url='login_page')
def sales_add(request, sales_id=0):
    context = {}
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    if request.method == "GET":
        if sales_id == 0:
            form = SalesinfoaddForm()
        else:
            factory = qrcode.image.svg.SvgImage
            img = qrcode.make(request.POST.get("qr_text", ""), image_factory=factory, box_size=10)
            stream = BytesIO()
            img.save(stream)
            context["svg"] = stream.getvalue().decode()
            # print(context)
            salesinfo = SalesInfo.objects.get(pk=sales_id)
            form = SalesinfoaddForm(instance=salesinfo)
        context={
            'form': form,
            'role': role,
            'first_name': first_name,
        }
        return render(request, "asset_mgt_app/sales_add.html", context)
    else:
        if sales_id == 0:
            form = SalesinfoaddForm(request.POST)
        else:
            salesinfo = SalesInfo.objects.get(pk=sales_id)
            form = SalesinfoaddForm(request.POST, instance=salesinfo)
        if form.is_valid():
            form.save()
        return redirect('/SMS/sales_list')

# Delete Assets
@login_required(login_url='login_page')
def sales_delete(request, sales_id):
    salesinfo = SalesInfo.objects.get(pk=sales_id)
    salesinfo.delete()
    return redirect('/SMS/sales_list')