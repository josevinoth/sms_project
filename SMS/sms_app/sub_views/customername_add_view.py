from django.contrib.auth.decorators import login_required
from ..forms import CustomernameaddForm
from ..models import CustomernameInfo_new
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def customername_add(request,customername_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if customername_id == 0:
            form = CustomernameaddForm()
        else:
            customername=CustomernameInfo_new.objects.get(pk=customername_id)
            form = CustomernameaddForm(instance=customername)
        return render(request, "asset_mgt_app/customername_add.html", {'form': form,'first_name': first_name})
    else:
        if customername_id == 0:
            form = CustomernameaddForm(request.POST)
        else:
            customername = CustomernameInfo_new.objects.get(pk=customername_id)
            form = CustomernameaddForm(request.POST,instance=customername)
        if form.is_valid():
            form.save()
        return redirect('/SMS/customername_list')

# List customername
@login_required(login_url='login_page')
def customername_list(request):
    first_name = request.session.get('first_name')
    context = {'customername_list' : CustomernameInfo_new.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/customername_list.html",context)

#Delete customername
@login_required(login_url='login_page')
def customername_delete(request,customername_id):
    customername = CustomernameInfo_new.objects.get(pk=customername_id)
    customername.delete()
    return redirect('/SMS/customername_list')