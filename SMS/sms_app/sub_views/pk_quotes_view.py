from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from ..forms import PkquotesForm
from ..models import PkquotesInfo
from django.shortcuts import render, redirect
from random import randint
from django.contrib import messages

@login_required(login_url='login_page')
def quotes_add(request,quotes_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if quotes_id == 0:
            form = PkquotesForm()
        else:
            quotes=PkquotesInfo.objects.get(pk=quotes_id)
            form = PkquotesForm(instance=quotes)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                }
        return render(request, "asset_mgt_app/pk_quotes_add.html", context)
    else:
        if quotes_id == 0:
            form = PkquotesForm(request.POST)
            if form.is_valid():
                # Generate Random quotes number
                try:
                    last_id = PkquotesInfo.objects.latest('id').id
                    quotes_num_next = str('QT_') + str(
                        int(((PkquotesInfo.objects.get(id=last_id)).qt_quotes_num).replace('QT_','')) + 1)
                except ObjectDoesNotExist:
                    quotes_num_next = str('QT_') + str(randint(10000, 99999))
                form.save()
                print("PkquotesInfo Form is Valid")
                last_id = (PkquotesInfo.objects.latest('id')).id
                PkquotesInfo.objects.filter(id=last_id).update(qt_quotes_num=quotes_num_next)
                messages.success(request, 'Record Updated Successfully')
                # return redirect(request.META['HTTP_REFERER'])
                return redirect('/SMS/quotes_update/' + str(last_id))
            else:
                print("PkquotesInfo Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            quotes = PkquotesInfo.objects.get(pk=quotes_id)
            form = PkquotesForm(request.POST,instance=quotes)
            if form.is_valid():
                form.save()
                print("PkquotesForm Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("PkquotesForm Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/quotes_list')

# List quotes
@login_required(login_url='login_page')
def quotes_list(request):
    first_name = request.session.get('first_name')
    context = {'quotes_list' : PkquotesInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_quotes_list.html",context)

#Delete quotes
@login_required(login_url='login_page')
def quotes_delete(request,quotes_id):
    quotes = PkquotesInfo.objects.get(pk=quotes_id)
    quotes.delete()
    return redirect('/SMS/quotes_list')