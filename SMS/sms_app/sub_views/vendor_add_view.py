from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..forms import VendoraddForm
from ..models import Vendor_info

@login_required(login_url='login_page')
def vendor_add(request,vendor_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print('user_id',user_id)
    if request.method == "GET":
        if vendor_id == 0:
            form = VendoraddForm()
        else:
            vendor=Vendor_info.objects.get(pk=vendor_id)
            form = VendoraddForm(instance=vendor)
        context={
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
        }
        return render(request, "asset_mgt_app/vendor_add.html",context )
    else:
        if vendor_id == 0:
            form = VendoraddForm(request.POST,request.FILES)
        else:
            vendor = Vendor_info.objects.get(pk=vendor_id)
            form = VendoraddForm(request.POST,request.FILES,instance=vendor)
        if form.is_valid():
            form.save()
            print("Main Form Saved")
        else:
            print("Main form not saved")
        return redirect('/SMS/vendor_list')

# List Vendor
@login_required(login_url='login_page')
def vendor_list(request):
    first_name = request.session.get('first_name')
    context = {'vendor_list' : Vendor_info.objects.all(),'first_name': first_name,}
    return render(request,"asset_mgt_app/vendor_list.html",context)

#Delete Vendor
@login_required(login_url='login_page')
def vendor_delete(request,vendor_id):
    vendor = Vendor_info.objects.get(pk=vendor_id)
    vendor.delete()
    return redirect('/SMS/vendor_list')