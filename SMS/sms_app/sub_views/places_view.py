from django.contrib.auth.decorators import login_required
from ..forms import PlacesForm
from ..models import Places
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def places_add(request,places_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if places_id == 0:
            form = PlacesForm()
        else:
            places=Places.objects.get(pk=places_id)
            form = PlacesForm(instance=places)
        return render(request, "asset_mgt_app/places_add.html", {'form': form,'first_name': first_name})
    else:
        if places_id == 0:
            form = PlacesForm(request.POST)
        else:
            places = Places.objects.get(pk=places_id)
            form = PlacesForm(request.POST,instance=places)
        if form.is_valid():
            form.save()
        return redirect('/SMS/places_list')

# List places
@login_required(login_url='login_page')
def places_list(request):
    first_name = request.session.get('first_name')
    context = {'places_list' : Places.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/places_list.html",context)

#Delete places
@login_required(login_url='login_page')
def places_delete(request,places_id):
    places = Places.objects.get(pk=places_id)
    places.delete()
    return redirect('/SMS/places_list')