from django.contrib.auth.decorators import login_required
from ..forms import StateaddForm
from ..models import State
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def state_add(request,state_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if state_id == 0:
            form = StateaddForm()
        else:
            state=State.objects.get(pk=state_id)
            form = StateaddForm(instance=state)
        return render(request, "asset_mgt_app/state_add.html", {'form': form,'first_name': first_name})
    else:
        if state_id == 0:
            form = StateaddForm(request.POST)
        else:
            state = State.objects.get(pk=state_id)
            form = StateaddForm(request.POST,instance=state)
        if form.is_valid():
            form.save()
        return redirect('/SMS/state_list')

# List state
@login_required(login_url='login_page')
def state_list(request):
    first_name = request.session.get('first_name')
    context = {'state_list' : State.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/state_list.html",context)

#Delete state
@login_required(login_url='login_page')
def state_delete(request,state_id):
    state = State.objects.get(pk=state_id)
    state.delete()
    return redirect('/SMS/state_list')