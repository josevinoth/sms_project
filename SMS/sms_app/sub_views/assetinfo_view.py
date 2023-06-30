from django.contrib.auth.decorators import login_required
from ..forms import AssetinfoaddForm
from ..models import User_extInfo,AssetInfo
from django.shortcuts import render, redirect
import qrcode
from io import BytesIO
import qrcode.image.svg
from random import randint
from django.contrib import messages

@login_required(login_url='login_page')
def asset_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    context = {
        'asset_list': AssetInfo.objects.all(),
        'first_name': first_name,
        'role': role,
    }
    return render(request, "asset_mgt_app/asset_list.html", context)

@login_required(login_url='login_page')
def assetinfo_add(request, asset_id=0):
    context = {}
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    print('user_id',user_id)
    # Generate Random Asset number
    last_id = (AssetInfo.objects.values_list('id', flat=True)).last()
    if last_id == None:
        last_id = 0
    asset_num = randint(10000, 99999) + last_id + 1
    print('asset_num',asset_num)
    if request.method == "GET":
        if asset_id == 0:
            print("Inside Get Asset Add")
            form = AssetinfoaddForm()
            context = {
                'form': form,
                'role': role,
                'first_name': first_name,
                'asset_num': asset_num,
                'user_id': user_id,
            }
        else:
            factory = qrcode.image.svg.SvgImage
            img = qrcode.make(request.POST.get("qr_text", ""), image_factory=factory, box_size=10)
            stream = BytesIO()
            img.save(stream)
            context["svg"] = stream.getvalue().decode()
            # print(context)
            print("Inside Get Asset Edit")
            assetinfo = AssetInfo.objects.get(pk=asset_id)
            form = AssetinfoaddForm(instance=assetinfo)
            context={
                'form': form,
                'role': role,
                'first_name': first_name,
                'asset_num': asset_num,
                'user_id': user_id,
            }
        return render(request, "asset_mgt_app/asset_add.html", context)
    else:
        if asset_id == 0:
            print("Inside Post Asset Add")
            form = AssetinfoaddForm(request.POST)
        else:
            print("Inside Post Asset Edit")
            assetinfo = AssetInfo.objects.get(pk=asset_id)
            form = AssetinfoaddForm(request.POST, instance=assetinfo)
        if form.is_valid():
            form.save()
            print("Form is Valid")
            form.save()
            messages.success(request, 'Record Updated Successfully')
        else:
            print("Form is In-Valid")
            messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
        return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/asset_list')

# Delete Assets
@login_required(login_url='login_page')
def asset_delete(request, asset_id):
    assetinfo = AssetInfo.objects.get(pk=asset_id)
    assetinfo.delete()
    return redirect('/SMS/asset_list')