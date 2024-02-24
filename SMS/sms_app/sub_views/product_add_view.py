from django.contrib.auth.decorators import login_required
from ..forms import ProductaddForm
from ..models import Product_info
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def product_add(request,product_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if product_id == 0:
            form = ProductaddForm()
        else:
            product=Product_info.objects.get(pk=product_id)
            form = ProductaddForm(instance=product)
        return render(request, "asset_mgt_app/product_add.html", {'form': form,'first_name': first_name})
    else:
        if product_id == 0:
            form = ProductaddForm(request.POST)
        else:
            product = Product_info.objects.get(pk=product_id)
            form = ProductaddForm(request.POST,instance=product)
        if form.is_valid():
            form.save()
        return redirect('/SMS/product_list')

# List Product
@login_required(login_url='login_page')
def product_list(request):
    first_name = request.session.get('first_name')
    context = {'product_list' : Product_info.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/product_list.html",context)

#Delete Product
@login_required(login_url='login_page')
def product_delete(request,product_id):
    product = Product_info.objects.get(pk=product_id)
    product.delete()
    return redirect('/SMS/product_list')