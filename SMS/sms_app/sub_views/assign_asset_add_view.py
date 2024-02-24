from django.contrib.auth.decorators import login_required
from ..forms import AssignassetaddForm
from ..models import AssetInfo,Assign_asset_info
from django.shortcuts import render,redirect
from django.contrib.auth.models import User

# List Assign Asset_new
@login_required(login_url='login_page')
def assign_asset_list_new(request,user_id=0):
    first_name = request.session.get('first_name')
    asset_user=User.objects.get(pk=user_id).first_name + " " + User.objects.get(pk=user_id).last_name
    asset_user_id=User.objects.get(pk=user_id).id
    request.session['asset_user'] = asset_user
    request.session['asset_user_id'] = asset_user_id
    print(asset_user)
    print(asset_user_id)
    context = {
                # 'asset_assign_list': Assign_asset_info.objects.all(),
                'asset_list': AssetInfo.objects.filter(asset_assignedto_id=asset_user_id),
                'first_name': first_name
               }
            # form = AssignassetaddForm(instance=user)
        # return render(request, "asset_mgt_app/assign_asset_list.html", {'form': form,'first_name': first_name})
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