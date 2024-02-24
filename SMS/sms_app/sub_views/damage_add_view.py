from django.contrib.auth.decorators import login_required
from ..forms import DamageaddForm
from ..models import DamageInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def damage_add(request,damage_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if damage_id == 0:
            form = DamageaddForm()
        else:
            damage=DamageInfo.objects.get(pk=damage_id)
            form = DamageaddForm(instance=damage)
        context={
                'form': form,
                'first_name': first_name,
                }
        return render(request, "asset_mgt_app/damage_add.html",context )
    else:
        if damage_id == 0:
            form = DamageaddForm(request.POST)
        else:
            damage = DamageInfo.objects.get(pk=damage_id)
            form = DamageaddForm(request.POST,instance=damage)
        if form.is_valid():
            form.save()
        return redirect('/SMS/damage_list')

# List damage
@login_required(login_url='login_page')
def damage_list(request):
    first_name = request.session.get('first_name')
    context = {'damage_list' : DamageInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/damage_list.html",context)

#Delete damage
@login_required(login_url='login_page')
def damage_delete(request,damage_id):
    damage = DamageInfo.objects.get(pk=damage_id)
    damage.delete()
    return redirect('/SMS/damage_list')