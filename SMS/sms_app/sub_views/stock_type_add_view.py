from django.contrib.auth.decorators import login_required
from ..forms import StocktypeaddForm
from ..models import Stock_type
from django.shortcuts import render, redirect

#Add Stock Type
@login_required(login_url='login_page')
def stocktype_add(request,stocktype_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if stocktype_id == 0:
            Stocktype_form = StocktypeaddForm()
        else:
            Stocktype_info=Stock_type.objects.get(pk=stocktype_id)
            Stocktype_form = StocktypeaddForm(instance=Stocktype_info)
        return render(request, "asset_mgt_app/stocktype_add.html", {'Stocktype_form': Stocktype_form,'first_name': first_name})
    else:
        if stocktype_id == 0:
            Stocktype_form = StocktypeaddForm(request.POST)
        else:
            Stocktype_info = Stock_type.objects.get(pk=stocktype_id)
            Stocktype_form = StocktypeaddForm(request.POST,instance=Stocktype_info)
        if Stocktype_form.is_valid():
            Stocktype_form.save()
        return redirect('/SMS/stocktype_list')

# List Stock Type
@login_required(login_url='login_page')
def stocktype_list(request):
    first_name = request.session.get('first_name')
    context = {'stocktype_list' : Stock_type.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/stocktype_list.html",context)

#Delete stock Type
@login_required(login_url='login_page')
def stocktype_delete(request,stocktype_id):
    Stocktype_info = Stock_type.objects.get(pk=stocktype_id)
    Stocktype_info.delete()
    return redirect('/SMS/stocktype_list')