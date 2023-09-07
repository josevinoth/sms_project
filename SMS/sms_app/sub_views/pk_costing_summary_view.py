from django.contrib.auth.decorators import login_required

from ..forms import PkcostingsummaryForm
from ..models import PkcostingsummaryInfo,PkneedassessmentInfo,PkcostingInfo
from django.shortcuts import render, redirect

from django.contrib import messages

@login_required(login_url='login_page')
def costingsummary_add(request,costingsummary_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if costingsummary_id == 0:
            form = PkcostingsummaryForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
            }
        else:
            costingsummary=PkcostingsummaryInfo.objects.get(pk=costingsummary_id)
            needassessment_num = PkcostingsummaryInfo.objects.get(pk=costingsummary_id).cs_assessment_num
            needassessment_id = PkneedassessmentInfo.objects.get(na_assessment_num=needassessment_num).id
            request.session['na_assessment_id'] = needassessment_id
            form = PkcostingsummaryForm(instance=costingsummary)
            costing_list = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id)
            context={
                    'form': form,
                    'first_name': first_name,
                    'user_id': user_id,
                    'costing_list': costing_list,
                    }
        return render(request, "asset_mgt_app/pk_costingsummary_add.html", context)
    else:
        if costingsummary_id == 0:
            form = PkcostingsummaryForm(request.POST)
            if form.is_valid():
                # # Generate Random costingsummary number
                # try:
                #     last_id = PkcostingsummaryInfo.objects.latest('id').id
                #     costingsummary_num_next = str('QT_') + str(
                #         int(((PkcostingsummaryInfo.objects.get(id=last_id)).qt_costingsummary_num).replace('QT_','')) + 1)
                # except ObjectDoesNotExist:
                #     costingsummary_num_next = str('QT_') + str(randint(10000, 99999))
                form.save()
                print("PkcostingsummaryInfo Form is Valid")
                last_id = (PkcostingsummaryInfo.objects.latest('id')).id
                # PkcostingsummaryInfo.objects.filter(id=last_id).update(cs_costingsummary_num=costingsummary_num_next)
                messages.success(request, 'Record Updated Successfully')
                # return redirect(request.META['HTTP_REFERER'])
                return redirect('/SMS/costingsummary_update/' + str(last_id))
            else:
                print("PkcostingsummaryInfo Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            costingsummary = PkcostingsummaryInfo.objects.get(pk=costingsummary_id)
            form = PkcostingsummaryForm(request.POST,instance=costingsummary)
            if form.is_valid():
                form.save()
                print("PkcostingsummaryForm Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("PkcostingsummaryForm Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/costingsummary_list')

# List costingsummary
@login_required(login_url='login_page')
def costingsummary_list(request):
    first_name = request.session.get('first_name')
    context = {'costingsummary_list' : PkcostingsummaryInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_costingsummary_list.html",context)

#Delete costingsummary
@login_required(login_url='login_page')
def costingsummary_delete(request,costingsummary_id):
    costingsummary = PkcostingsummaryInfo.objects.get(pk=costingsummary_id)
    costingsummary.delete()
    return redirect('/SMS/costingsummary_list')