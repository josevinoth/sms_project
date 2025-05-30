from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
import json

from ..forms import FuelfillingForm
from ..models import Fuelfillinginfo,Places,Bunkname
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

@login_required(login_url='login_page')
def fuelfilling_add(request, fuelfilling_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    # If editing, fetch the existing instance
    if fuelfilling_id != 0:
        fuelfilling = get_object_or_404(Fuelfillinginfo, pk=fuelfilling_id)
    else:
        fuelfilling = None

    if request.method == "POST":
        form = FuelfillingForm(request.POST, instance=fuelfilling)

        if form.is_valid():
            instance = form.save()
            if fuelfilling is None:
                print("Fuelfillinginfo Form is Valid - New Record")
                messages.success(request, 'Fuel Filling Record Added Successfully')
                return redirect('/SMS/fuelfilling_update/' + str(instance.id))
            else:
                print("Fuelfillinginfo Form is Valid - Updated Record")
                messages.success(request, 'Fuel Filling Record Updated Successfully')
                return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            print("Fuelfillinginfo Form is Not Valid")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")
                    messages.error(request, f"{field}: {error}")
            # fall through to render the form with errors below

    else:
        # GET request
        form = FuelfillingForm(instance=fuelfilling)

    context = {
        'form': form,
        'first_name': first_name,
        'user_id': user_id,
    }
    return render(request, "asset_mgt_app/fuelfilling_add.html", context)

                # return redirect(request.META['HTTP_REFERER'])

        # return redirect('/SMS/requirements_list')


# List fuelfilling
@login_required(login_url='login_page')
def fuelfilling_list(request):
    first_name = request.session.get('first_name')
    context = {'fuelfilling_list' : Fuelfillinginfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/fuelfilling_list.html",context)

#Delete fuelfilling
@login_required(login_url='login_page')
def fuelfilling_delete(request,fuelfilling_id):
    fuelfilling = Fuelfillinginfo.objects.get(pk=fuelfilling_id)
    fuelfilling.delete()
    return redirect('/SMS/fuelfilling_list')

@login_required(login_url='login_page')
def load_location(request):
    # Fetch location
    location_list=[]
    location_id_list=[]
    ff_city_id = request.GET.get('cityId_1')
    # Fetch Unit Details
    location = Places.objects.filter(city=ff_city_id).values('place_name').distinct()
    location_id = Places.objects.filter(city=ff_city_id).values('id').distinct()
    location_count=location.count()
    for i in range(location_count):
        location_list.append(location[i]['place_name'])
        location_id_list.append(location_id[i]['id'])
    data = {
        'location_id_list':location_id_list,
        'location_list': location_list,
    }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))

@login_required(login_url='login_page')
def fetch_bunk_details(request):
    bunk_name = request.GET.get('bunk_name', '')
    if bunk_name:
        try:
            bunk = Bunkname.objects.get(bunk_name=bunk_name)
            return JsonResponse({
                'bunk_state': bunk.bunk_state or '',
                'bunk_location_name': bunk.bunk_location_name or '',
            })
        except Bunkname.DoesNotExist:
            return JsonResponse({'error': 'Bunk not found'})
    return JsonResponse({'error': 'No bunk name provided'})