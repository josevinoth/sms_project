from django.contrib.auth.decorators import login_required
from ..forms import ConsignmentdetailaddForm
from ..models import ConsignmentdetailInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def consignmentdetail_add(request,consignmentdetail_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if consignmentdetail_id == 0:
            form = ConsignmentdetailaddForm()
        else:
            consignmentdetail=ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id)
            form = ConsignmentdetailaddForm(instance=consignmentdetail)
        return render(request, "asset_mgt_app/consignmentdetail_add.html", {'form': form,'first_name': first_name})
    else:
        if consignmentdetail_id == 0:
            form = ConsignmentdetailaddForm(request.POST)
        else:
            consignmentdetail = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id)
            form = ConsignmentdetailaddForm(request.POST,instance=consignmentdetail)
        if form.is_valid():
            form.save()
        return redirect('/SMS/consignmentdetail_list')

# List consignmentdetail
@login_required(login_url='login_page')
def consignmentdetail_list(request):
    first_name = request.session.get('first_name')
    context = {'consignmentdetail_list' : ConsignmentdetailInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/consignmentdetail_list.html",context)

#Delete consignmentdetail
@login_required(login_url='login_page')
def consignmentdetail_delete(request,consignmentdetail_id):
    consignmentdetail = ConsignmentdetailInfo.objects.get(pk=consignmentdetail_id)
    consignmentdetail.delete()
    return redirect('/SMS/consignmentdetail_list')