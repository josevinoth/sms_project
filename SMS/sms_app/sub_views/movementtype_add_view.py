from django.contrib.auth.decorators import login_required
from ..forms import MovementtypeaddForm
from ..models import MovementtypeInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def movementtype_add(request,movementtype_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if movementtype_id == 0:
            form = MovementtypeaddForm()
        else:
            movementtype=MovementtypeInfo.objects.get(pk=movementtype_id)
            form = MovementtypeaddForm(instance=movementtype)
        return render(request, "asset_mgt_app/movementtype_add.html", {'form': form,'first_name': first_name})
    else:
        if movementtype_id == 0:
            form = MovementtypeaddForm(request.POST)
        else:
            movementtype = MovementtypeInfo.objects.get(pk=movementtype_id)
            form = MovementtypeaddForm(request.POST,instance=movementtype)
        if form.is_valid():
            form.save()
        return redirect('/SMS/movementtype_list')

# List movementtype
@login_required(login_url='login_page')
def movementtype_list(request):
    first_name = request.session.get('first_name')
    context = {'movementtype_list' : MovementtypeInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/movementtype_list.html",context)

#Delete movementtype
@login_required(login_url='login_page')
def movementtype_delete(request,movementtype_id):
    movementtype = MovementtypeInfo.objects.get(pk=movementtype_id)
    movementtype.delete()
    return redirect('/SMS/movementtype_list')