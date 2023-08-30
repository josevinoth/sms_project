from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from ..forms import PkquoteForm
from ..models import PkquoteInfo
from django.shortcuts import render, redirect
from random import randint
from django.contrib import messages

@login_required(login_url='login_page')
def quote_add(request,quote_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if quote_id == 0:
            form = PkquoteForm()
        else:
            quote=PkquoteInfo.objects.get(pk=quote_id)
            form = PkquoteForm(instance=quote)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                }
        return render(request, "asset_mgt_app/pk_quote_add.html", context)
    else:
        if quote_id == 0:
            form = PkquoteForm(request.POST)
            if form.is_valid():
                # Generate Random quote number
                try:
                    last_id = PkquoteInfo.objects.latest('id').id
                    quote_num_next = str('quote_') + str(int(((PkquoteInfo.objects.get(id=last_id)).qt_quote_num).replace('quote_','')) + 1)
                except ObjectDoesNotExist:
                    quote_num_next = str('quote_') + str(randint(10000, 99999))
                form.save()
                print("quote Form is Valid")
                last_id = (PkquoteInfo.objects.latest('id')).id
                PkquoteInfo.objects.filter(id=last_id).update(qt_quote_num=quote_num_next)
                messages.success(request, 'Record Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
                # return redirect('/SMS/quote_update/')
            else:
                print("quote Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            quote = PkquoteInfo.objects.get(pk=quote_id)
            form = PkquoteForm(request.POST,instance=quote)
            if form.is_valid():
                form.save()
                print("quote Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("quote Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

# List quote
@login_required(login_url='login_page')
def quote_list(request):
    first_name = request.session.get('first_name')
    context = {'quote_list' : PkquoteInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_quote_list.html",context)

#Delete quote
@login_required(login_url='login_page')
def quote_delete(request,quote_id):
    quote = PkquoteInfo.objects.get(pk=quote_id)
    quote.delete()
    return redirect('/SMS/quote_list')