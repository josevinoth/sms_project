from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from ..forms import PkneedassessmentForm
from ..models import PkneedassessmentInfo
from django.shortcuts import render, redirect
from random import randint
from django.contrib import messages

@login_required(login_url='login_page')
def needassessment_add(request,needassessment_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if needassessment_id == 0:
            form = PkneedassessmentForm()
        else:
            needassessment=PkneedassessmentInfo.objects.get(pk=needassessment_id)
            form = PkneedassessmentForm(instance=needassessment)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                }
        return render(request, "asset_mgt_app/pk_needassessment_add.html", context)
    else:
        if needassessment_id == 0:
            form = PkneedassessmentForm(request.POST)
            if form.is_valid():
                # Generate Random Assessment number
                try:
                    last_id = (PkneedassessmentInfo.objects.values_list('id', flat=True)).last()
                    assessment_num_next = str('Assess_') + str(int(((PkneedassessmentInfo.objects.get(id=last_id)).na_assessment_num).replace('Assess_', '')) + 1)
                except ObjectDoesNotExist:
                    assessment_num_next = str('Assess_') + str(randint(10000, 99999))
                form.save()
                print("needassessment Form is Valid")
                last_id = (PkneedassessmentInfo.objects.values_list('id', flat=True)).last()
                PkneedassessmentInfo.objects.filter(id=last_id).update(na_assessment_num=assessment_num_next)
                messages.success(request, 'Record Updated Successfully')
                return redirect('/SMS/needassessment_update/'+ str(last_id))
            else:
                print("needassessment Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            needassessment = PkneedassessmentInfo.objects.get(pk=needassessment_id)
            form = PkneedassessmentForm(request.POST,instance=needassessment)
            if form.is_valid():
                form.save()
                print("needassessment Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("needassessment Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

# List needassessment
@login_required(login_url='login_page')
def needassessment_list(request):
    first_name = request.session.get('first_name')
    context = {'needassessment_list' : PkneedassessmentInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_needassessment_list.html",context)

#Delete needassessment
@login_required(login_url='login_page')
def needassessment_delete(request,needassessment_id):
    needassessment = PkneedassessmentInfo.objects.get(pk=needassessment_id)
    needassessment.delete()
    return redirect('/SMS/needassessment_list')