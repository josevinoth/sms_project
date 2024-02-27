from django.contrib.auth.decorators import login_required

from ..forms import PkquotationsummaryForm
from ..models import PkquotationsummaryInfo,PkneedassessmentInfo,PkquotationInfo
from django.shortcuts import render, redirect
from django.db.models.aggregates import Sum
from django.contrib import messages
from django.http import JsonResponse

@login_required(login_url='login_page')
def pk_quotationsummary_add(request,pk_quotationsummary_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if pk_quotationsummary_id == 0:
            form = PkquotationsummaryForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
            }
        else:
            quotationsummary=PkquotationsummaryInfo.objects.get(pk=pk_quotationsummary_id)
            needassessment_num = PkquotationsummaryInfo.objects.get(pk=pk_quotationsummary_id).qs_assessment_num
            needassessment_id = PkneedassessmentInfo.objects.get(na_assessment_num=needassessment_num).id
            request.session['na_assessment_id'] = needassessment_id
            print('needassessment_id',needassessment_id)
            form = PkquotationsummaryForm(instance=quotationsummary)
            quotation_list = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id)
            wood_cost = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id,pkqt_cost_type=8,pkqt_stock_type=1).aggregate(Sum('pkqt_total_cost'))['pkqt_total_cost__sum']
            if wood_cost is not None:
                wood_cost = round(wood_cost, 2)
            else:
                wood_cost = 0.0
            # print(wood_cost)
            PkquotationsummaryInfo.objects.filter(qs_assessment_num=needassessment_id).update(qs_wood_cost=wood_cost)

            total_cft = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id, pkqt_cost_type=8,pkqt_stock_type=1).aggregate(Sum('pkqt_cft'))['pkqt_cft__sum']
            if total_cft is not None:
                total_cft = round(total_cft, 2)
            else:
                total_cft = 0.0
            # print(total_cft)
            PkquotationsummaryInfo.objects.filter(qs_assessment_num=needassessment_id).update(qs_total_cft=total_cft)

            engineer_cost = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id, pkqt_cost_type=2).aggregate(Sum('pkqt_total_cost'))['pkqt_total_cost__sum']
            if engineer_cost is not None:
                engineer_cost = round(engineer_cost, 2)
            else:
                engineer_cost = 0.0
            # print(engineer_cost)
            PkquotationsummaryInfo.objects.filter(qs_assessment_num=needassessment_id).update(qs_engineer_cost=engineer_cost)

            making_labour_cost = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id, pkqt_cost_type=2).aggregate(Sum('pkqt_total_cost'))['pkqt_total_cost__sum']
            if making_labour_cost is not None:
                making_labour_cost = round(making_labour_cost, 2)
            else:
                making_labour_cost = 0.0

            packing_labour_cost = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id, pkqt_cost_type=8).aggregate(Sum('pkqt_total_cost'))['pkqt_total_cost__sum']
            if packing_labour_cost is not None:
                packing_labour_cost = round(packing_labour_cost, 2)
            else:
                packing_labour_cost = 0.0

            labour_cost=making_labour_cost+packing_labour_cost
            # print(labour_cost)
            PkquotationsummaryInfo.objects.filter(qs_assessment_num=needassessment_id).update(qs_labour_cost=labour_cost)

            crane_cost = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id, pkqt_cost_type=6).aggregate(Sum('pkqt_total_cost'))['pkqt_total_cost__sum']
            if crane_cost is not None:
                crane_cost = round(crane_cost, 2)
            else:
                crane_cost = 0.0
            # print(crane_cost)
            PkquotationsummaryInfo.objects.filter(qs_assessment_num=needassessment_id).update(qs_crane_cost=crane_cost)

            ht_cost = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id, pkqt_cost_type=5).aggregate(Sum('pkqt_total_cost'))['pkqt_total_cost__sum']
            if ht_cost is not None:
                ht_cost = round(ht_cost, 2)
            else:
                ht_cost = 0.0
            # print(ht_cost)
            PkquotationsummaryInfo.objects.filter(qs_assessment_num=needassessment_id).update(qs_ht_cost=ht_cost)

            management_cost = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id, pkqt_cost_type=7).aggregate(Sum('pkqt_total_cost'))['pkqt_total_cost__sum']
            if management_cost is not None:
                management_cost = round(management_cost, 2)
            else:
                management_cost = 0.0
            # print(management_cost)
            PkquotationsummaryInfo.objects.filter(qs_assessment_num=needassessment_id).update(qs_management_cost=management_cost)

            material_cost = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id, pkqt_cost_type=8,pkqt_stock_type=2).aggregate(Sum('pkqt_total_cost'))['pkqt_total_cost__sum']
            # Check if material_cost is not None before rounding it
            if material_cost is not None:
                material_cost = round(material_cost, 2)
            else:
                material_cost = 0.0
            # print(material_cost)
            PkquotationsummaryInfo.objects.filter(qs_assessment_num=needassessment_id).update(qs_material_cost=material_cost)

            transport_cost = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id, pkqt_cost_type=4).aggregate(Sum('pkqt_total_cost'))['pkqt_total_cost__sum']
            if transport_cost is not None:
                transport_cost = round(transport_cost, 2)
            else:
                transport_cost = 0.0
            # print(transport_cost)
            PkquotationsummaryInfo.objects.filter(qs_assessment_num=needassessment_id).update(qs_transport_cost=transport_cost)
            context={
                    'form': form,
                    'first_name': first_name,
                    'user_id': user_id,
                    'quotation_list':quotation_list,
                    }
        return render(request, "asset_mgt_app/pk_quotationsummary_add.html", context)
    else:
        if pk_quotationsummary_id == 0:
            form = PkquotationsummaryForm(request.POST)
            if form.is_valid():
                form.save()
                print("PkquotationsummaryInfo Form is Valid")
                last_id = (PkquotationsummaryInfo.objects.latest('id')).id
                messages.success(request, 'Record Updated Successfully')
                return redirect('/SMS/pk_quotationsummary_update/' + str(last_id))
            else:
                print("PkquotationsummaryInfo Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            quotationsummary = PkquotationsummaryInfo.objects.get(pk=pk_quotationsummary_id)
            form = PkquotationsummaryForm(request.POST,instance=quotationsummary)
            if form.is_valid():
                form.save()
                print("PkquotationsummaryForm Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("PkquotationsummaryForm Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/costingsummary_list')

# Listquotationsummary
@login_required(login_url='login_page')
def pk_quotationsummary_list(request):
    first_name = request.session.get('first_name')
    context = {'pk_quotationsummary_list' : PkquotationsummaryInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_quotationsummary_list.html",context)

#Deletequotationsummary
@login_required(login_url='login_page')
def pk_quotationsummary_delete(request,pk_quotationsummary_id):
    quotationsummary = PkquotationsummaryInfo.objects.get(pk=pk_quotationsummary_id)
    quotationsummary.delete()
    return redirect('/SMS/pk_quotationsummary_list')

@login_required(login_url='login_page')
def pk_quotation_summary_check_unique_field(request):
    qs_assessment_num = request.GET.get('qs_assessment_num')
    exists = PkquotationsummaryInfo.objects.filter(qs_assessment_num=qs_assessment_num).exists()
    return JsonResponse({'exists': exists})