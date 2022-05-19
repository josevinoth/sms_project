from django.contrib.auth.decorators import login_required
from ..forms import ProducttypeaddForm
from ..models import Prod_Type
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def producttype_add(request,producttype_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if producttype_id == 0:
            form = ProducttypeaddForm()
        else:
            producttype=Prod_Type.objects.get(pk=producttype_id)
            form = ProducttypeaddForm(instance=producttype)
        return render(request, "asset_mgt_app/producttype_add.html", {'form': form,'first_name': first_name})
    else:
        if producttype_id == 0:
            form = ProducttypeaddForm(request.POST)
        else:
            producttype = Prod_Type.objects.get(pk=producttype_id)
            form = ProducttypeaddForm(request.POST,instance=producttype)
        if form.is_valid():
            form.save()
        return redirect('/SMS/producttype_list')

# List Product
@login_required(login_url='login_page')
def producttype_list(request):
    first_name = request.session.get('first_name')
    context = {'producttype_list' : Prod_Type.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/producttype_list.html",context)

#Delete Product
@login_required(login_url='login_page')
def producttype_delete(request,producttype_id):
    producttype = Prod_Type.objects.get(pk=producttype_id)
    producttype.delete()
    return redirect('/SMS/producttype_list')