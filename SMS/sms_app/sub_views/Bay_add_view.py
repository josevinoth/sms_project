from django.contrib.auth.decorators import login_required
from ..forms import BayaddForm
from ..models import BayInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def bay_add(request,bay_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if bay_id == 0:
            form = BayaddForm()
        else:
            bay=BayInfo.objects.get(pk=bay_id)
            form = BayaddForm(instance=bay)
        return render(request, "asset_mgt_app/bay_add.html", {'form': form,'first_name': first_name})
    else:
        if bay_id == 0:
            form = BayaddForm(request.POST)
        else:
            bay = BayInfo.objects.get(pk=bay_id)
            form = BayaddForm(request.POST,instance=bay)
        if form.is_valid():
            form.save()
        return redirect('/SMS/bay_list')

# List bay
@login_required(login_url='login_page')
def bay_list(request):
    first_name = request.session.get('first_name')
    context = {'bay_list' : BayInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/bay_list.html",context)

#Delete bay
@login_required(login_url='login_page')
def bay_delete(request,bay_id):
    bay = BayInfo.objects.get(pk=bay_id)
    bay.delete()
    return redirect('/SMS/bay_list')