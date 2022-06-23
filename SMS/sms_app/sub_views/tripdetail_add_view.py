from django.contrib.auth.decorators import login_required
from ..forms import TripdetailaddForm
from ..models import TripdetailInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def tripdetail_add(request,tripdetail_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if tripdetail_id == 0:
            form = TripdetailaddForm()
        else:
            tripdetail=TripdetailInfo.objects.get(pk=tripdetail_id)
            form = TripdetailaddForm(instance=tripdetail)
        return render(request, "asset_mgt_app/tripdetail_add.html", {'form': form,'first_name': first_name})
    else:
        if tripdetail_id == 0:
            form = TripdetailaddForm(request.POST)
        else:
            tripdetail = TripdetailInfo.objects.get(pk=tripdetail_id)
            form = TripdetailaddForm(request.POST,instance=tripdetail)
        if form.is_valid():
            form.save()
        return redirect('/SMS/tripdetail_list')

# List tripdetail
@login_required(login_url='login_page')
def tripdetail_list(request):
    first_name = request.session.get('first_name')
    context = {'tripdetail_list' : TripdetailInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/tripdetail_list.html",context)

#Delete tripdetail
@login_required(login_url='login_page')
def tripdetail_delete(request,tripdetail_id):
    tripdetail = TripdetailInfo.objects.get(pk=tripdetail_id)
    tripdetail.delete()
    return redirect('/SMS/tripdetail_list')