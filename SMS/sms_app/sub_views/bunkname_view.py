from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from ..forms import BunknameForm
from ..models import Bunkname
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required(login_url='login_page')
def bunkname_add(request,bunkname_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if bunkname_id == 0:
            form = BunknameForm()
        else:
            bunkname=Bunkname.objects.get(pk=bunkname_id)
            form = BunknameForm(instance=bunkname)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                }
        return render(request, "asset_mgt_app/bunkname_add.html", context)
    else:
        if bunkname_id == 0:
            form = BunknameForm(request.POST)
            if form.is_valid():
                form.save()
                print("Bunkname Form is Valid")
                last_id = (Bunkname.objects.latest('id')).id
                messages.success(request, 'Record Updated Successfully')
                # return redirect(request.META['HTTP_REFERER'])
                return redirect('/SMS/bunkname_update/' + str(last_id))
            else:
                print("Bunkname Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            bunkname = Bunkname.objects.get(pk=bunkname_id)
            form = BunknameForm(request.POST,instance=bunkname)
            if form.is_valid():
                form.save()
                print("Bunkname Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("Bunkname Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

# List Bunkname
@login_required(login_url='login_page')
def bunkname_list(request):
    first_name = request.session.get('first_name')
    context = {'bunkname_list' : Bunkname.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/bunkname_list.html",context)

#Delete bunkname
@login_required(login_url='login_page')
def bunkname_delete(request,bunkname_id):
    bunkname = Bunkname.objects.get(pk=bunkname_id)
    bunkname.delete()
    return redirect('/SMS/bunkname_list')