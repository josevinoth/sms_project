from django.contrib.auth.decorators import login_required
from ..forms import OwnershipaddForm
from ..models import OwnershipInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def ownership_add(request,ownership_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if ownership_id == 0:
            form = OwnershipaddForm()
        else:
            ownership=OwnershipInfo.objects.get(pk=ownership_id)
            form = OwnershipaddForm(instance=ownership)
        return render(request, "asset_mgt_app/ownership_add.html", {'form': form,'first_name': first_name})
    else:
        if ownership_id == 0:
            form = OwnershipaddForm(request.POST)
        else:
            ownership = OwnershipInfo.objects.get(pk=ownership_id)
            form = OwnershipaddForm(request.POST,instance=ownership)
        if form.is_valid():
            form.save()
        return redirect('/SMS/ownership_list')

# List ownership
@login_required(login_url='login_page')
def ownership_list(request):
    first_name = request.session.get('first_name')
    context = {'ownership_list' : OwnershipInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/ownership_list.html",context)

#Delete ownership
@login_required(login_url='login_page')
def ownership_delete(request,ownership_id):
    ownership = OwnershipInfo.objects.get(pk=ownership_id)
    ownership.delete()
    return redirect('/SMS/ownership_list')