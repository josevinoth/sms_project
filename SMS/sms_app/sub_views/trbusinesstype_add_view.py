from django.contrib.auth.decorators import login_required
from ..forms import TrbusinesstypeaddForm
from ..models import TrbusinesstypeInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def trbusinesstype_add(request,trbusinesstype_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if trbusinesstype_id == 0:
            form = TrbusinesstypeaddForm()
        else:
            trbusinesstype=TrbusinesstypeInfo.objects.get(pk=trbusinesstype_id)
            form = TrbusinesstypeaddForm(instance=trbusinesstype)
        return render(request, "asset_mgt_app/trbusinesstype_add.html", {'form': form,'first_name': first_name})
    else:
        if trbusinesstype_id == 0:
            form = TrbusinesstypeaddForm(request.POST)
        else:
            trbusinesstype = TrbusinesstypeInfo.objects.get(pk=trbusinesstype_id)
            form = TrbusinesstypeaddForm(request.POST,instance=trbusinesstype)
        if form.is_valid():
            form.save()
        return redirect('/SMS/trbusinesstype_list')

# List trbusinesstype
@login_required(login_url='login_page')
def trbusinesstype_list(request):
    first_name = request.session.get('first_name')
    context = {'trbusinesstype_list' : TrbusinesstypeInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/trbusinesstype_list.html",context)

#Delete trbusinesstype
@login_required(login_url='login_page')
def trbusinesstype_delete(request,trbusinesstype_id):
    trbusinesstype = TrbusinesstypeInfo.objects.get(pk=trbusinesstype_id)
    trbusinesstype.delete()
    return redirect('/SMS/trbusinesstype_list')