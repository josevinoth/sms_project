from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Q
from ..forms import AssetinfoaddForm
from ..models import User_extInfo,AssetInfo
from django.shortcuts import render, redirect
import qrcode
from io import BytesIO
import qrcode.image.svg
from django.contrib import messages

@login_required(login_url='login_page')
def asset_search(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    # asset_number = request.GET.get('asset_number')
    # asset_ID = request.GET.get('asset_id')
    role = User_extInfo.objects.get(user=user_id).emp_role
    asset_list= AssetInfo.objects.all().order_by('-id')
    # asset_list = AssetInfo.objects.filter(Q(asset_number__icontains=asset_number) | Q(asset_number='') | Q(asset_number__in=[None, ''])).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(asset_list, 50)
    page_obj = paginator.get_page(page_number)
    context = {
        'asset_list': asset_list,
        'first_name': first_name,
        'role': role,
        'page_obj': page_obj,
    }
    return render(request, "asset_mgt_app/asset_list.html", context)
@login_required(login_url='login_page')
def asset_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    asset_list= AssetInfo.objects.all().order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(asset_list, 100000)
    page_obj = paginator.get_page(page_number)
    context = {
        'asset_list': asset_list,
        'first_name': first_name,
        'role': role,
        'page_obj': page_obj,
    }
    return render(request, "asset_mgt_app/asset_list.html", context)

@login_required(login_url='login_page')
def assetinfo_add(request, asset_id=0):
    context = {}
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    if request.method == "GET":
        if asset_id == 0:
            print("Inside Get Asset Add")
            form = AssetinfoaddForm()
            context = {
                'form': form,
                'role': role,
                'first_name': first_name,
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
                'user_id': user_id,
            }
        return render(request, "asset_mgt_app/asset_add.html", context)
    else:
        if asset_id == 0:
            print("Inside Post Asset Add")
            form = AssetinfoaddForm(request.POST)
            if form.is_valid():
                form.save()
                try:
                    last_id = (AssetInfo.objects.values_list('id', flat=True)).last()
                    reg_number=100000+last_id
                    # req_num_next = str('Req_') + str(int(((RequirementsInfo.objects.get(id=last_id)).req_number).replace('Req_', '')) + 1)
                except ObjectDoesNotExist:
                    reg_number=100000
                    # req_num_next = str('Req_') + str(randint(10000, 99999))
                last_id = (AssetInfo.objects.values_list('id', flat=True)).last()
                branch = AssetInfo.objects.get(id=last_id).asset_location.id
                if branch==1:
                    asset_num_next=str('BLR_')+str(reg_number)
                elif branch==2:
                    asset_num_next = str('MAA_') + str(reg_number)
                elif branch==3:
                    asset_num_next = str('PYN_') + str(reg_number)
                elif branch==4:
                    asset_num_next = str('HYD_') + str(reg_number)
                elif branch==5:
                    asset_num_next = str('CBE_') + str(reg_number)
                else:
                    messages.error(request, 'Branch Code Not available. Please connect to adminstrator')
                    return redirect(request.META['HTTP_REFERER'])

                AssetInfo.objects.filter(id=last_id).update(asset_number=asset_num_next)
                print("Asset Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Form is In-Valid")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
            # return redirect(request.META['HTTP_REFERER'])
            return redirect('/SMS/asset_update/' + str(last_id))
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