from django.contrib.auth.decorators import login_required
from ..forms import CustomertypeaddForm
from ..models import CustomertypeInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def customertype_add(request,customertype_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if customertype_id == 0:
            form = CustomertypeaddForm()
        else:
            customertype=CustomertypeInfo.objects.get(pk=customertype_id)
            form = CustomertypeaddForm(instance=customertype)
        return render(request, "asset_mgt_app/customertype_add.html", {'form': form,'first_name': first_name})
    else:
        if customertype_id == 0:
            form = CustomertypeaddForm(request.POST)
        else:
            customertype = CustomertypeInfo.objects.get(pk=customertype_id)
            form = CustomertypeaddForm(request.POST,instance=customertype)
        if form.is_valid():
            form.save()
        return redirect('/SMS/customertype_list')

# List customertype
@login_required(login_url='login_page')
def customertype_list(request):
    first_name = request.session.get('first_name')
    context = {'customertype_list' : CustomertypeInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/customertype_list.html",context)

#Delete customertype
@login_required(login_url='login_page')
def customertype_delete(request,customertype_id):
    customertype = CustomertypeInfo.objects.get(pk=customertype_id)
    customertype.delete()
    return redirect('/SMS/customertype_list')