from django.contrib.auth.decorators import login_required
from .general_utils import get_financial_year, generate_next_number
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
            form = AssetinfoaddForm(request.POST,request.FILES)
            if form.is_valid():
                asset_obj = form.save()
                branch_id = asset_obj.asset_location.id
                
                # Branch mapping
                branch_map = {1: 'BLR', 2: 'MAA', 3: 'PYN', 4: 'HYD', 5: 'CBE'}
                branch_code = branch_map.get(branch_id, 'UNC')
                
                # Generate Asset number based on financial year
                fy = get_financial_year()
                prefix = f"{fy}_{branch_code}_AST_"
                asset_num_next = generate_next_number(AssetInfo, 'asset_number', prefix, 6)

                AssetInfo.objects.filter(id=asset_obj.id).update(asset_number=asset_num_next)
                print("Asset Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Form is In-Valid")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
            # return redirect(request.META['HTTP_REFERER'])
            return redirect('/SMS/asset_update/' + str(asset_obj.id))
        else:
            print("Inside Post Asset Edit")
            assetinfo = AssetInfo.objects.get(pk=asset_id)
            form = AssetinfoaddForm(request.POST, request.FILES, instance=assetinfo)
            if form.is_valid():
                form.save()
                print("Form is Valid")
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

@login_required(login_url='login_page')
def un_assigned_asset_list(request):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    unassigned_asset_list= AssetInfo.objects.filter(asset_assignedto__isnull=True).order_by('-id')
    page_number = request.GET.get('page')
    paginator = Paginator(unassigned_asset_list, 100000)
    page_obj = paginator.get_page(page_number)
    context = {
        'unassigned_asset_list': unassigned_asset_list,
        'first_name': first_name,
        'role': role,
        'page_obj': page_obj,
    }
    return render(request, "asset_mgt_app/unassigned_asset_list.html", context)