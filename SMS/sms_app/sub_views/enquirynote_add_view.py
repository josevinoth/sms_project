from django.contrib.auth.decorators import login_required
from ..forms import EnquirynoteaddForm
from ..models import EnquirynoteInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def enquirynote_add(request,enquirynote_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if enquirynote_id == 0:
            form = EnquirynoteaddForm()
        else:
            enquirynote=EnquirynoteInfo.objects.get(pk=enquirynote_id)
            form = EnquirynoteaddForm(instance=enquirynote)
        return render(request, "asset_mgt_app/enquirynote_add.html", {'form': form,'first_name': first_name})
    else:
        if enquirynote_id == 0:
            form = EnquirynoteaddForm(request.POST)
        else:
            enquirynote = EnquirynoteInfo.objects.get(pk=enquirynote_id)
            form = EnquirynoteaddForm(request.POST,instance=enquirynote)
        if form.is_valid():
            form.save()
        return redirect('/SMS/enquirynote_list')

# List enquirynote
@login_required(login_url='login_page')
def enquirynote_list(request):
    first_name = request.session.get('first_name')
    context = {'enquirynote_list' : EnquirynoteInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/enquirynote_list.html",context)

#Delete enquirynote
@login_required(login_url='login_page')
def enquirynote_delete(request,enquirynote_id):
    enquirynote = EnquirynoteInfo.objects.get(pk=enquirynote_id)
    enquirynote.delete()
    return redirect('/SMS/enquirynote_list')