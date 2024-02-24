from django.contrib.auth.decorators import login_required
from ..forms import MaterialstockForm
from ..models import User_extInfo,Materialstock
from django.shortcuts import render, redirect
import qrcode
from io import BytesIO
import qrcode.image.svg

@login_required(login_url='login_page')
def materialstock_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    context = {
        'materialstock_list': Materialstock.objects.all(),
        'first_name': first_name,
        'role': role,
    }
    return render(request, "asset_mgt_app/materialstock_list.html", context)

@login_required(login_url='login_page')
def materialstock_add(request, materialstock_id=0):
    context = {}
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    if request.method == "GET":
        if materialstock_id == 0:
            form = MaterialstockForm()
        else:
            factory = qrcode.image.svg.SvgImage
            img = qrcode.make(request.POST.get("qr_text", ""), image_factory=factory, box_size=10)
            stream = BytesIO()
            img.save(stream)
            context["svg"] = stream.getvalue().decode()
            # print(context)
            materialstock = Materialstock.objects.get(pk=materialstock_id)
            form = MaterialstockForm(instance=materialstock)
        context={
            'form': form,
            'role': role,
            'first_name': first_name,
        }
        return render(request, "asset_mgt_app/materialstock_add.html", context)
    else:
        if materialstock_id == 0:
            form = MaterialstockForm(request.POST)
        else:
            materialstock = Materialstock.objects.get(pk=materialstock_id)
            form = MaterialstockForm(request.POST, instance=materialstock)
        if form.is_valid():
            form.save()
        return redirect('/SMS/materialstock_list')

# Delete materialstock
@login_required(login_url='login_page')
def materialstock_delete(request, materialstock_id):
    materialstock = Materialstock.objects.get(pk=materialstock_id)
    materialstock.delete()
    return redirect('/SMS/materialstock_list')