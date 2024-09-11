from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from ..models import ml_Product
from ..forms import ProductForm

@login_required(login_url='login_page')
def create_product(request,product_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if product_id == 0:
            form = ProductForm()
        else:
            prod=ml_Product.objects.get(pk=product_id)
            form = ProductForm(instance=prod)
        return render(request, "asset_mgt_app/create_product.html", {'form': form,'first_name': first_name})
    else:
        if product_id == 0:
            form = ProductForm(request.POST)
        else:
            prod = ml_Product.objects.get(pk=product_id)
            form = ProductForm(request.POST,instance=prod)
        if form.is_valid():
            form.save()
        return redirect('/SMS/ml_product_list')


@login_required(login_url='login_page')
def ml_product_list(request):
    first_name = request.session.get('first_name')
    context = {'ml_product_list' : ml_Product.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/ml_list.html",context)

@login_required(login_url='login_page')
def ml_product_delete(request, product_id):
    ml_prod = ml_Product.objects.get(pk=product_id)
    ml_prod.delete()
    return redirect('/SMS/ml_product_list')
