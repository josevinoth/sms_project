from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..forms import PkstockvendorForm
from ..models import PkstockvebdorInfo,PkstockpurchasesInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def pk_stock_vendor_add(request,stock_vendor_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if stock_vendor_id == 0:
            psv_form = PkstockvendorForm()
            pk_vendor_bill = ''
            stockpurchases_list = PkstockpurchasesInfo.objects.filter(sp_vendor_bill=pk_vendor_bill)
            context = {
                'psv_form': psv_form,
                'first_name': first_name,
                'user_id': user_id,
                'stockpurchases_list': stockpurchases_list, }
        else:
            pk_vendor_bill = PkstockvebdorInfo.objects.get(pk=stock_vendor_id).spv_vendor_bill
            print('vendor_bill', pk_vendor_bill)
            request.session['ses_pk_vendor_bill'] = pk_vendor_bill
            pk_stock_vendor = PkstockvebdorInfo.objects.get(pk=stock_vendor_id)
            psv_form = PkstockvendorForm(instance=pk_stock_vendor)
            pk_vendor_bill = request.session.get('ses_pk_vendor_bill')
            stockpurchases_list = PkstockpurchasesInfo.objects.filter(sp_vendor_bill=pk_vendor_bill)
            context={
                    'psv_form': psv_form,
                    'first_name': first_name,
                    'user_id': user_id,
                    'stockpurchases_list':stockpurchases_list,}
        return render(request, "asset_mgt_app/pk_stock_vendor_add.html", context)
    else:
        psv_form = PkstockvendorForm(request.POST)

        if psv_form.is_valid():
            # Check for duplicates before saving
            spv_vendor_bill = psv_form.cleaned_data['spv_vendor_bill']
            if not PkstockvebdorInfo.objects.filter(spv_vendor_bill=spv_vendor_bill).exclude(id=stock_vendor_id).exists():
                if stock_vendor_id == 0:
                    new_place = psv_form.save()
                    print("psv_form saved")
                    messages.success(request, 'Record Updated Successfully')
                    url = new_place.get_absolute_url_pk_stock_vendor()
                    return redirect(url)
                else:
                    pk_stock_vendor = PkstockvebdorInfo.objects.get(pk=stock_vendor_id)
                    psv_form = PkstockvendorForm(request.POST, instance=pk_stock_vendor)
                    psv_form.save()
                    print("psv_form saved")
                    messages.success(request, 'Record Updated Successfully')
                    return redirect(request.META['HTTP_REFERER'])
            else:
                print("Data not saved - Duplicate Vendor Bill found")
                messages.error(request, 'Duplicate Found. Please enter a Unique Vendor Bill.')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("Location psv_form not saved")
            messages.error(request, 'Record Not Saved. Please Enter All Required Fields')
            return redirect(request.META['HTTP_REFERER'])

# List places
@login_required(login_url='login_page')
def pk_stock_vendor_list(request):
    first_name = request.session.get('first_name')
    context = {'pk_stock_vendor_list' : PkstockvebdorInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_stock_vendor_list.html",context)

#Delete places
@login_required(login_url='login_page')
def pk_stock_vendor_delete(request,stock_vendor_id):
    pk_stock_vendor = PkstockvebdorInfo.objects.get(pk=stock_vendor_id)
    PkstockvebdorInfo.delete()
    return redirect('/SMS/pk_stock_vendor_list')