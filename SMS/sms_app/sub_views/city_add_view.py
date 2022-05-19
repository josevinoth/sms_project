from django.contrib.auth.decorators import login_required
from ..forms import CityaddForm
from ..models import City
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def city_add(request,city_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if city_id == 0:
            form = CityaddForm()
        else:
            city=City.objects.get(pk=city_id)
            form = CityaddForm(instance=city)
        return render(request, "asset_mgt_app/city_add.html", {'form': form,'first_name': first_name})
    else:
        if city_id == 0:
            form = CityaddForm(request.POST)
        else:
            city = City.objects.get(pk=city_id)
            form = CityaddForm(request.POST,instance=city)
        if form.is_valid():
            form.save()
        return redirect('/SMS/city_list')

# List city
@login_required(login_url='login_page')
def city_list(request):
    first_name = request.session.get('first_name')
    context = {'city_list' : City.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/city_list.html",context)

#Delete city
@login_required(login_url='login_page')
def city_delete(request,city_id):
    city = City.objects.get(pk=city_id)
    city.delete()
    return redirect('/SMS/city_list')