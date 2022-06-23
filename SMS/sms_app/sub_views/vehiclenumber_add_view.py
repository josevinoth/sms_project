from django.contrib.auth.decorators import login_required
from ..forms import VehiclenumberaddForm
from ..models import VehiclenumberInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def vehiclenumber_add(request,vehiclesource_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if vehiclenumber_id == 0:
            form = VehiclenumberaddForm()
        else:
            vehiclenumber = VehiclenumberInfo.objects.get(pk=vehiclenumber_id)
            form = VehiclenumberaddForm(instance=vehiclenumber)
        return render(request, "asset_mgt_app/vehiclenumber_add.html", {'form': form,'first_name': first_name})
    else:
        if vehiclenumber_id == 0:
            form = VehiclenumberaddForm(request.POST)
        else:
            vehiclenumber = VehiclenumberInfo.objects.get(pk=vehiclenumber_id)
            form = VehiclenumberaddForm(request.POST,instance=vehiclenumber)
        if form.is_valid():
            form.save()
        return redirect('/SMS/vehiclenumber_list')

# List vehiclenumber
@login_required(login_url='login_page')
def vehiclenumber_list(request):
    first_name = request.session.get('first_name')
    context = {'vehiclenumber_list' : VehiclenumberInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/vehiclenumber_list.html",context)

#Delete vehiclenumber
@login_required(login_url='login_page')
def vehiclenumber_delete(request,vehiclenumber_id):
    vehiclenumber = VehiclenumberInfo.objects.get(pk=vehiclenumber_id)
    vehiclenumber.delete()
    return redirect('/SMS/vehiclenumber_list')