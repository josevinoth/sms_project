from django.contrib.auth.decorators import login_required
from ..forms import PkstockpurchasesForm
from ..models import PkstockpurchasesInfo
from django.shortcuts import render, redirect
from random import randint
from django.contrib import messages

@login_required(login_url='login_page')
def stockpurchases_add(request,stockpurchases_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if stockpurchases_id == 0:
            form = PkstockpurchasesForm()
        else:
            stockpurchases=PkstockpurchasesInfo.objects.get(pk=stockpurchases_id)
            form = PkstockpurchasesForm(instance=stockpurchases)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                }
        return render(request, "asset_mgt_app/pk_stockpurchases_add.html", context)
    else:
        if stockpurchases_id == 0:
            form = PkstockpurchasesForm(request.POST)
            if form.is_valid():
                form.save()
                print("stockpurchases Form is Valid")
                messages.success(request, 'Record Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
                # return redirect('/SMS/stockpurchases_update/')
            else:
                print("stockpurchases Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            stockpurchases = PkstockpurchasesInfo.objects.get(pk=stockpurchases_id)
            form = PkstockpurchasesForm(request.POST,instance=stockpurchases)
            if form.is_valid():
                form.save()
                print("stockpurchases Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("stockpurchases Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

# List stockpurchases
@login_required(login_url='login_page')
def stockpurchases_list(request):
    first_name = request.session.get('first_name')
    context = {'stockpurchases_list' : PkstockpurchasesInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_stockpurchases_list.html",context)

#Delete stockpurchases
@login_required(login_url='login_page')
def stockpurchases_delete(request,stockpurchases_id):
    stockpurchases = PkstockpurchasesInfo.objects.get(pk=stockpurchases_id)
    stockpurchases.delete()
    return redirect('/SMS/stockpurchases_list')