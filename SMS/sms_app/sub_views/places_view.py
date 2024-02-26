from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
            places = Places.objects.get(pk=places_id)
            form = PlacesForm(instance=places)
        return render(request, "asset_mgt_app/places_add.html", {'form': form, 'first_name': first_name})
    else:
        form = PlacesForm(request.POST)

        if form.is_valid():
            # Check for duplicates before saving
            place_name = form.cleaned_data['place_name']
            if not Places.objects.filter(place_name=place_name).exclude(id=places_id).exists():
                if places_id == 0:
                    new_place = form.save()
                    print("Location Form saved")
                    messages.success(request, 'Record Updated Successfully')
                    url = new_place.get_absolute_url()
                    return redirect(url)
                else:
                    places = Places.objects.get(pk=places_id)
                    form = PlacesForm(request.POST, instance=places)
                    form.save()
                    print("Location Form saved")
                    messages.success(request, 'Record Updated Successfully')
                    return redirect(request.META['HTTP_REFERER'])
            else:
                print("Location Form not saved - Duplicate found")
                messages.error(request, 'Duplicate Record Found. Please enter a unique name.')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("Location Form not saved")
            messages.error(request, 'Record Not Saved. Please Enter All Required Fields')
            return redirect(request.META['HTTP_REFERER'])

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