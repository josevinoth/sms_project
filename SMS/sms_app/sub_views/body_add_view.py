from django.contrib.auth.decorators import login_required
from ..forms import BodyaddForm
from ..models import BodyInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def body_add(request,body_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if body_id == 0:
            form = BodyaddForm()
        else:
            body=BodyInfo.objects.get(pk=body_id)
            form = BodyaddForm(instance=body)
        return render(request, "asset_mgt_app/body_add.html", {'form': form,'first_name': first_name})
    else:
        if body_id == 0:
            form = BodyaddForm(request.POST)
        else:
            body = BodyInfo.objects.get(pk=body_id)
            form = BodyaddForm(request.POST,instance=body)
        if form.is_valid():
            form.save()
        return redirect('/SMS/body_list')

# List body
@login_required(login_url='login_page')
def body_list(request):
    first_name = request.session.get('first_name')
    context = {'body_list' : BodyInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/body_list.html",context)

#Delete body
@login_required(login_url='login_page')
def body_delete(request,body_id):
    body = BodyInfo.objects.get(pk=body_id)
    body.delete()
    return redirect('/SMS/body_list')