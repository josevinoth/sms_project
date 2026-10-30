from django.contrib.auth.decorators import login_required
from ..forms import AssignassetaddForm
from ..models import AssetInfo,Assign_asset_info
from django.shortcuts import render,redirect
from django.contrib.auth.models import User

# List Assign Asset_new
@login_required(login_url='login_page')
def assign_asset_list_new(request, user_id=0):
    first_name = request.session.get('first_name')
    target_user = User.objects.filter(pk=user_id).first()
    if target_user:
        full_name = f"{target_user.first_name} {target_user.last_name}".strip()
        asset_user = full_name if full_name else target_user.username
        asset_user_id = target_user.id
    else:
        asset_user = "Unknown User"
        asset_user_id = user_id

    request.session['asset_user'] = asset_user
    request.session['asset_user_id'] = asset_user_id
    assigned_assets = AssetInfo.objects.filter(asset_assignedto_id=asset_user_id)
    context = {
        'asset_list': assigned_assets,
        'first_name': first_name,
        'target_user': target_user,
        'asset_user': asset_user,
        'total_assigned': assigned_assets.count(),
    }
    return render(request, "asset_mgt_app/asset_list_view.html", context)

# Add Assign Asset
@login_required(login_url='login_page')
def assign_asset_add(request, assign_asset_id=0):
    first_name = request.session.get('first_name')
    asset_user= request.session.get('asset_user')
    asset_user_id = request.session.get('asset_user_id')
    print(asset_user_id)
    if request.method == "GET":
        if assign_asset_id == 0:
            form = AssignassetaddForm()
        else:
            assignassetinfo = Assign_asset_info.objects.get(pk=assign_asset_id)
            form= AssignassetaddForm(instance=assignassetinfo)
        context={
                'form':form,
                'first_name': first_name,
                'asset_user':asset_user
                }

        return render(request, "asset_mgt_app/assign_asset_add.html", context)
    else:
        if assign_asset_id == 0:
            form = AssignassetaddForm(request.POST)
        else:
            assignassetinfo = Assign_asset_info.objects.get(pk=assign_asset_id)
            form = AssignassetaddForm(request.POST, instance=assignassetinfo)
        if form.is_valid():
            form.save()
        # return render(request, "SMS_app/assign_asset_list.html")
        return redirect('/SMS/user_list')


# Delete Assign Asset
@login_required(login_url='login_page')
def assign_asset_delete(request, assign_asset_id):
    assignassetinfo = Assign_asset_info.objects.get(pk=assign_asset_id)
    assignassetinfo.delete()
    return redirect('/SMS/assign_asset_list/1/')