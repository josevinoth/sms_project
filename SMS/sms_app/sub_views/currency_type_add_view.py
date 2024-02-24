from django.contrib.auth.decorators import login_required
from ..forms import CurrencytypeaddForm
from ..models import Currency_type
from django.shortcuts import render, redirect

#Add Currency Type
@login_required(login_url='login_page')
def currencytype_add(request,currencytype_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if currencytype_id == 0:
            Currencytype_form = CurrencytypeaddForm()
        else:
            Currencytype_info=Currency_type.objects.get(pk=currencytype_id)
            Currencytype_form = CurrencytypeaddForm(instance=Currencytype_info)
        return render(request, "asset_mgt_app/currencytype_add.html", {'Currencytype_form': Currencytype_form,'first_name': first_name})
    else:
        if currencytype_id == 0:
            Currencytype_form = CurrencytypeaddForm(request.POST)
        else:
            Currencytype_info = Currency_type.objects.get(pk=currencytype_id)
            Currencytype_form = CurrencytypeaddForm(request.POST,instance=Currencytype_info)
        if Currencytype_form.is_valid():
            Currencytype_form.save()
        return redirect('/SMS/currencytype_list')

# List Currency Type
@login_required(login_url='login_page')
def currencytype_list(request):
    first_name = request.session.get('first_name')
    context = {'currencytype_list' : Currency_type.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/currencytype_list.html",context)

#Delete Currency Type
@login_required(login_url='login_page')
def currencytype_delete(request,currencytype_id):
    Currencytype_info = Currency_type.objects.get(pk=currencytype_id)
    Currencytype_info.delete()
    return redirect('/SMS/currencytype_list')