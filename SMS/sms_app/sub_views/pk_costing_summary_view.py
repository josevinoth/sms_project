from django.contrib.auth.decorators import login_required

from ..forms import PkcostingsummaryForm
from ..models import PkcostingsummaryInfo,PkneedassessmentInfo,PkcostingInfo
from django.shortcuts import render, redirect
from django.db.models.aggregates import Sum, Max
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

            wood_cost = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id,ct_cost_type=1).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            if wood_cost is not None:
                wood_cost = round(wood_cost, 2)
            else:
                wood_cost = 0.0
            # print(wood_cost)
            PkcostingsummaryInfo.objects.filter(cs_assessment_num=needassessment_id).update(cs_wood_cost=wood_cost)

            total_cft = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id, ct_cost_type=1).aggregate(Sum('ct_cft'))['ct_cft__sum']
            if total_cft is not None:
                total_cft = round(total_cft, 2)
            else:
                total_cft = 0.0
            # print(total_cft)
            PkcostingsummaryInfo.objects.filter(cs_assessment_num=needassessment_id).update(cs_total_cft=total_cft)

            engineer_cost = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id, ct_cost_type=3).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            if engineer_cost is not None:
                engineer_cost = round(engineer_cost, 2)
            else:
                engineer_cost = 0.0
            # print(engineer_cost)
            PkcostingsummaryInfo.objects.filter(cs_assessment_num=needassessment_id).update(cs_engineer_cost=engineer_cost)

            labour_cost = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id, ct_cost_type=2).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']+PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id, ct_cost_type=8).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            if labour_cost is not None:
                labour_cost = round(labour_cost, 2)
            else:
                labour_cost = 0.0
            print(labour_cost)
            PkcostingsummaryInfo.objects.filter(cs_assessment_num=needassessment_id).update(cs_labour_cost=labour_cost)

            crane_cost = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id, ct_cost_type=6).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            if crane_cost is not None:
                crane_cost = round(crane_cost, 2)
            else:
                crane_cost = 0.0
            # print(crane_cost)
            PkcostingsummaryInfo.objects.filter(cs_assessment_num=needassessment_id).update(cs_crane_cost=crane_cost)

            ht_cost = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id, ct_cost_type=5).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            if ht_cost is not None:
                ht_cost = round(ht_cost, 2)
            else:
                ht_cost = 0.0
            # print(ht_cost)
            PkcostingsummaryInfo.objects.filter(cs_assessment_num=needassessment_id).update(cs_ht_cost=ht_cost)

            management_cost = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id, ct_cost_type=7).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            if management_cost is not None:
                management_cost = round(management_cost, 2)
            else:
                management_cost = 0.0
            # print(management_cost)
            PkcostingsummaryInfo.objects.filter(cs_assessment_num=needassessment_id).update(cs_management_cost=management_cost)

            material_cost = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id, ct_cost_type=9).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            # Check if material_cost is not None before rounding it
            if material_cost is not None:
                material_cost = round(material_cost, 2)
            else:
                material_cost = 0.0
            # print(material_cost)
            PkcostingsummaryInfo.objects.filter(cs_assessment_num=needassessment_id).update(cs_material_cost=material_cost)

            transport_cost = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id, ct_cost_type=4).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            if transport_cost is not None:
                transport_cost = round(transport_cost, 2)
            else:
                transport_cost = 0.0
            # print(transport_cost)
            PkcostingsummaryInfo.objects.filter(cs_assessment_num=needassessment_id).update(cs_transport_cost=transport_cost)
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