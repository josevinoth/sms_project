from django.contrib.auth.decorators import login_required
from ..forms import WhstoragetypeaddForm
from ..models import WhstoragetypeInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def whstoragetype_add(request,whstoragetype_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if whstoragetype_id == 0:
            form = WhstoragetypeaddForm()
        else:
            whstoragetype=WhstoragetypeInfo.objects.get(pk=whstoragetype_id)
            form = WhstoragetypeaddForm(instance=whstoragetype)
        return render(request, "asset_mgt_app/whstoragetype_add.html", {'form': form,'first_name': first_name})
    else:
        if whstoragetype_id == 0:
            form = WhstoragetypeaddForm(request.POST)
        else:
            whstoragetype = WhstoragetypeInfo.objects.get(pk=whstoragetype_id)
            form = WhstoragetypeaddForm(request.POST,instance=whstoragetype)
        if form.is_valid():
            form.save()
        return redirect('/SMS/whstoragetype_list')

# List whstoragetype
@login_required(login_url='login_page')
def whstoragetype_list(request):
    first_name = request.session.get('first_name')
    context = {'whstoragetype_list' : WhstoragetypeInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/whstoragetype_list.html",context)

#Delete whstoragetype
@login_required(login_url='login_page')
def whstoragetype_delete(request,whstoragetype_id):
    whstoragetype = WhstoragetypeInfo.objects.get(pk=whstoragetype_id)
    whstoragetype.delete()
    return redirect('/SMS/whstoragetype_list')