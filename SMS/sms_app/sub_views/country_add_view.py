from django.contrib.auth.decorators import login_required
from ..forms import CountryaddForm
from ..models import Country
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def country_add(request,country_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if country_id == 0:
            form = CountryaddForm()
        else:
            country=Country.objects.get(pk=country_id)
            form = CountryaddForm(instance=country)
        return render(request, "asset_mgt_app/country_add.html", {'form': form,'first_name': first_name})
    else:
        if country_id == 0:
            form = CountryaddForm(request.POST)
        else:
            country = Country.objects.get(pk=country_id)
            form = CountryaddForm(request.POST,instance=country)
        if form.is_valid():
            form.save()
        return redirect('/SMS/country_list')

# List country
@login_required(login_url='login_page')
def country_list(request):
    first_name = request.session.get('first_name')
    context = {'country_list' : Country.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/country_list.html",context)

#Delete country
@login_required(login_url='login_page')
def country_delete(request,country_id):
    country = Country.objects.get(pk=country_id)
    country.delete()
    return redirect('/SMS/country_list')