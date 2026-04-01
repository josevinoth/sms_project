from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from ..forms import PkquotesForm
from ..models import PkquotesInfo
from django.shortcuts import render, redirect
from random import randint
from django.contrib import messages
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id

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
                instance = form.save()
                # Generate Quotation number based on financial year
                fy = get_financial_year()
                branch_id = get_session_branch_id(request)
                branch_code = get_branch_code(branch_id)
                prefix = f"{fy}_{branch_code}_QT_"
                quotes_num_next = generate_next_number(PkquotesInfo, 'qt_quotes_num', prefix, 6)
                
                PkquotesInfo.objects.filter(id=instance.id).update(qt_quotes_num=quotes_num_next)
                messages.success(request, 'Record Updated Successfully with Quotation Number: ' + quotes_num_next)
                return redirect(f'/SMS/quotes_update/{instance.id}')
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