from django.contrib.auth.decorators import login_required
from ..forms import PaymenttypeForm
from ..models import PaymenttypeInfo
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def paymenttype_add(request,paymenttype_id=0):
    first_name = request.session.get('first_name')
    if request.method == "GET":
        if paymenttype_id == 0:
            form = PaymenttypeForm()
        else:
            paymenttype=PaymenttypeInfo.objects.get(pk=paymenttype_id)
            form = PaymenttypeForm(instance=paymenttype)
        return render(request, "asset_mgt_app/paymenttype_add.html", {'form': form,'first_name': first_name})
    else:
        if paymenttype_id == 0:
            form = PaymenttypeForm(request.POST)
        else:
            paymenttype = PaymenttypeInfo.objects.get(pk=paymenttype_id)
            form = PaymenttypeForm(request.POST,instance=paymenttype)
        if form.is_valid():
            form.save()
        return redirect('/SMS/paymenttype_list')

# List paymenttype
@login_required(login_url='login_page')
def paymenttype_list(request):
    first_name = request.session.get('first_name')
    context = {'paymenttype_list' : PaymenttypeInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/paymenttype_list.html",context)

#Delete paymenttype
@login_required(login_url='login_page')
def paymenttype_delete(request,paymenttype_id):
    paymenttype = PaymenttypeInfo.objects.get(pk=paymenttype_id)
    paymenttype.delete()
    return redirect('/SMS/paymenttype_list')