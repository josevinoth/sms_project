from django.contrib.auth.decorators import login_required
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id
from django.core.exceptions import ObjectDoesNotExist

from ..forms import PkopeningstockForm
from ..models import PkopeningstockInfo
from django.shortcuts import render, redirect
from random import randint
from django.contrib import messages

@login_required(login_url='login_page')
def openingstock_add(request,openingstock_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if openingstock_id == 0:
            form = PkopeningstockForm()
        else:
            openingstock=PkopeningstockInfo.objects.get(pk=openingstock_id)
            form = PkopeningstockForm(instance=openingstock)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                }
        return render(request, "asset_mgt_app/pk_openingstock_add.html", context)
    else:
        if openingstock_id == 0:
            form = PkopeningstockForm(request.POST)
            if form.is_valid():
                # Generate Opening Stock number based on financial year (Branch specific)
                fy = get_financial_year()
                branch_id = get_session_branch_id(request)
                branch_code = get_branch_code(branch_id)
                prefix = f"{fy}_{branch_code}_OS_"
                openingstock_num_next = generate_next_number(PkopeningstockInfo, 'os_stock_number', prefix, 6)
                instance = form.save()
                print("openingstock Form is Valid")
                PkopeningstockInfo.objects.filter(id=instance.id).update(os_stock_number=openingstock_num_next)
                messages.success(request, 'Record Updated Successfully')
                # return redirect(request.META['HTTP_REFERER'])
                return redirect('/SMS/openingstock_update/'+str(instance.id))
            else:
                print("openingstock Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            openingstock = PkopeningstockInfo.objects.get(pk=openingstock_id)
            form = PkopeningstockForm(request.POST,instance=openingstock)
            if form.is_valid():
                form.save()
                print("openingstock Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("openingstock Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

# List openingstock
@login_required(login_url='login_page')
def openingstock_list(request):
    first_name = request.session.get('first_name')
    context = {'openingstock_list' : PkopeningstockInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_openingstock_list.html",context)

#Delete openingstock
@login_required(login_url='login_page')
def openingstock_delete(request,openingstock_id):
    openingstock = PkopeningstockInfo.objects.get(pk=openingstock_id)
    openingstock.delete()
    return redirect('/SMS/openingstock_list')