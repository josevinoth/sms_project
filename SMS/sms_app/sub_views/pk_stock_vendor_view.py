from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from ..forms import PkstockvendorForm
from ..models import PkstockvebdorInfo,PkstockpurchasesInfo
from ..sub_models.stock_maintenance_mod import StockMaintenance
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def pk_stock_vendor_add(request,stock_vendor_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if stock_vendor_id == 0:
            if 'ses_stock_vendor_id' in request.session:
                del request.session['ses_stock_vendor_id']
            if 'ses_pk_vendor_bill' in request.session:
                del request.session['ses_pk_vendor_bill']
            psv_form = PkstockvendorForm()
            pk_vendor_bill = ''
            stockpurchases_list = PkstockpurchasesInfo.objects.filter(sp_vendor_bill=pk_vendor_bill)
            stockmaintenance_list = StockMaintenance.objects.none()
        else:
            pk_vendor_bill = PkstockvebdorInfo.objects.get(pk=stock_vendor_id).spv_vendor_bill
            pk_vendor_bill_id = PkstockvebdorInfo.objects.get(pk=stock_vendor_id).id
            request.session['ses_pk_vendor_bill'] = pk_vendor_bill
            request.session['ses_stock_vendor_id'] = stock_vendor_id
            pk_stock_vendor = PkstockvebdorInfo.objects.get(pk=stock_vendor_id)
            psv_form = PkstockvendorForm(instance=pk_stock_vendor)
            # pk_vendor_bill = request.session.get('ses_pk_vendor_bill')
            stockpurchases_list = PkstockpurchasesInfo.objects.filter(sp_vendor_bill_id=pk_vendor_bill_id)
            stockmaintenance_list = StockMaintenance.objects.filter(Q(sm_vendor_id=pk_vendor_bill_id) | Q(sm_invoice_no=pk_vendor_bill)).order_by('-sm_created_at')
        context={
                'psv_form': psv_form,
                'first_name': first_name,
                'user_id': user_id,
                'stockpurchases_list': stockpurchases_list,
                'stockmaintenance_list': stockmaintenance_list,
        }
        return render(request, "asset_mgt_app/pk_stock_vendor_add.html", context)
    else:
        psv_form = PkstockvendorForm(request.POST)

        if psv_form.is_valid():
            spv_vendor_bill = psv_form.cleaned_data['spv_vendor_bill']
            
            if PkstockvebdorInfo.objects.filter(spv_vendor_bill=spv_vendor_bill).exclude(id=stock_vendor_id).exists():
                messages.error(request, 'Duplicate Found. Please enter a Unique Vendor Bill.')
                return redirect(request.META['HTTP_REFERER'])

            if stock_vendor_id == 0:
                new_place = psv_form.save()
                
                # Auto-link any unlinked StockMaintenance entries that match this new invoice number
                StockMaintenance.objects.filter(sm_invoice_no=new_place.spv_vendor_bill, sm_vendor__isnull=True).update(sm_vendor=new_place)

                messages.success(request, 'Record Saved Successfully')
                url = new_place.get_absolute_url_pk_stock_vendor()
                return redirect(url)
            else:
                pk_stock_vendor = PkstockvebdorInfo.objects.get(pk=stock_vendor_id)
                psv_form = PkstockvendorForm(request.POST, instance=pk_stock_vendor)
                psv_form.save()
                
                # Auto-link any unlinked StockMaintenance entries that match this invoice number
                StockMaintenance.objects.filter(sm_invoice_no=pk_stock_vendor.spv_vendor_bill, sm_vendor__isnull=True).update(sm_vendor=pk_stock_vendor)
                
                print("psv_form saved")
                messages.success(request, 'Record Updated Successfully')
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
    pk_stock_vendor.delete()
    return redirect('/SMS/pk_stock_vendor_list')