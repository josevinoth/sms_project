import json
from django.contrib.auth.decorators import login_required
from ..forms import PkquotationForm
from ..models import PkquotationInfo,PkquotationsummaryInfo
from django.shortcuts import render, redirect

from django.contrib import messages

@login_required(login_url='login_page')
def pk_quotation_add(request,quotation_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    na_assessment_num_id = request.session.get('na_assessment_id')
    if request.method == "GET":
        if quotation_id == 0:
            form = PkquotationForm()
        else:
            quotation=PkquotationInfo.objects.get(pk=quotation_id)
            form = PkquotationForm(instance=quotation)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'na_assessment_num_id': na_assessment_num_id,
                }
        return render(request, "asset_mgt_app/pk_quotation_add.html", context)
    else:
        if quotation_id == 0:
            form = PkquotationForm(request.POST)
            if form.is_valid():
                form.save()
                print("quotation Form is Valid")
                last_id = (PkquotationInfo.objects.latest('id')).id
                messages.success(request, 'Record Updated Successfully')
                return redirect('/SMS/pk_quotation_update/'+str(last_id))
            else:
                print("quotation Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            quotation = PkquotationInfo.objects.get(pk=quotation_id)
            form = PkquotationForm(request.POST,instance=quotation)
            if form.is_valid():
                form.save()
                print("quotation Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("quotation Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

# List quotation
@login_required(login_url='login_page')
def pk_quotation_list(request):
    first_name = request.session.get('first_name')
    context = {'pk_quotaiton_list' : PkquotationInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_quotation_list.html",context)

#Delete quotation
@login_required(login_url='login_page')
def pk_quotation_delete(request,quotation_id):
    quotation = PkquotationInfo.objects.get(pk=quotation_id)
    quotation.delete()
    # return redirect('/SMS/pK_quotation_cancel')
    return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def pK_quotation_cancel(request):
    assessment_num_val = request.session.get('na_assessment_id')
    quotation_summary_id=PkquotationsummaryInfo.objects.get(qs_assessment_num=assessment_num_val).id
    return redirect('/SMS/pk_quotationsummary_update/' + str(quotation_summary_id))