from django.contrib.auth.decorators import login_required
from ..forms import BusinessrevenueForm
from ..models import BusinessrevenueInfo
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required(login_url='login_page')
def business_revenue_add(request,business_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if business_id == 0:
            form = BusinessrevenueForm()
        else:
            business=BusinessrevenueInfo.objects.get(pk=business_id)
            form = BusinessrevenueForm(instance=business)
        return render(request, "asset_mgt_app/business_revenue_add.html", {'form': form,'first_name': first_name})
    else:
        if business_id == 0:
            form = BusinessrevenueForm(request.POST)
        else:
            business = BusinessrevenueInfo.objects.get(pk=business_id)
            form = BusinessrevenueForm(request.POST,instance=business)
        if form.is_valid():
            form.save()
            messages.success(request, 'Record Saved Successfully')
        return redirect('/SMS/business_revenue_list')

# List bay
@login_required(login_url='login_page')
def business_revenue_list(request):
    first_name = request.session.get('first_name')
    context = {'business_revenue_list' : BusinessrevenueInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/business_revenue_list.html",context)

#Delete bay
@login_required(login_url='login_page')
def business_revenue_delete(request,business_id):
    business = BusinessrevenueInfo.objects.get(pk=business_id)
    business.delete()
    return redirect('/SMS/business_revenue_list')