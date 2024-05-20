from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from xhtml2pdf import pisa

from ..forms import PkquotationsummaryForm
from ..models import User_extInfo,Nadimension,PkquotationsummaryInfo,PkneedassessmentInfo,PkquotationInfo
from django.shortcuts import render, redirect
from django.db.models.aggregates import Sum
from django.contrib import messages
from django.http import JsonResponse, HttpResponse


@login_required(login_url='login_page')
def pk_quotationsummary_add(request,pk_quotationsummary_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = User_extInfo.objects.get(user=user_id).emp_role.id
    if request.method == "GET":
        if pk_quotationsummary_id == 0:
            form = PkquotationsummaryForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'role': role,
                'role_id': role_id,
            }
        else:
            quotationsummary=PkquotationsummaryInfo.objects.get(pk=pk_quotationsummary_id)
            needassessment_num = PkquotationsummaryInfo.objects.get(pk=pk_quotationsummary_id).qs_assessment_num
            needassessment_id = PkneedassessmentInfo.objects.get(na_assessment_num=needassessment_num).id
            customer_name_id = PkquotationsummaryInfo.objects.get(pk=pk_quotationsummary_id).qs_customer_name_2.id
            request.session['na_assessment_id'] = needassessment_id
            request.session['na_customer_name_id'] = customer_name_id
            form = PkquotationsummaryForm(instance=quotationsummary)
            quotation_list = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id)
            # wood_cost = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id,pkqt_cost_type=8,pkqt_stock_type=1,pkqt_stock_type=4).aggregate(Sum('pkqt_total_cost'))['pkqt_total_cost__sum']
            wood_cost = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id,pkqt_stock_type__in=[1, 4],pkqt_cost_type=8).aggregate(Sum('pkqt_total_cost'))['pkqt_total_cost__sum']
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

            # making_labour_cost = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id, pkqt_cost_type=2).aggregate(Sum('pkqt_total_cost'))['pkqt_total_cost__sum']
            # if making_labour_cost is not None:
            #     making_labour_cost = round(making_labour_cost, 2)
            # else:
            #     making_labour_cost = 0.0

            packing_labour_cost = PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id, pkqt_cost_type=3).aggregate(Sum('pkqt_total_cost'))['pkqt_total_cost__sum']
            if packing_labour_cost is not None:
                packing_labour_cost = round(packing_labour_cost, 2)
            else:
                packing_labour_cost = 0.0

            # labour_cost=making_labour_cost+packing_labour_cost
            labour_cost=packing_labour_cost
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
                    'quotation_list': quotation_list,
                    'wood_cost': wood_cost,
                    'engineer_cost': engineer_cost,
                    'labour_cost': labour_cost,
                    'crane_cost': crane_cost,
                    'ht_cost': ht_cost,
                    'management_cost': management_cost,
                    'material_cost': material_cost,
                    'transport_cost': transport_cost,
                    'role_id': role_id,
                    'role': role,
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
        # return redirect('/SMS/pk_quotationsummary_list')

# List quotationsummary
@login_required(login_url='login_page')
def pk_quotationsummary_list(request):
    first_name = request.session.get('first_name')
    context = {'quotationsummary_list' : PkquotationsummaryInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/pk_quotationsummary_list.html",context)

#Delete quotationsummary
@login_required(login_url='login_page')
def pk_quotationsummary_delete(request,pk_quotationsummary_id):
    quotationsummary = PkquotationsummaryInfo.objects.get(pk=pk_quotationsummary_id)
    quotationsummary.delete()
    return redirect('/SMS/pk_quotationsummary_list')

@login_required(login_url='login_page')
def pk_quotation_summary_check_unique_field(request):
    qs_assessment_num = request.GET.get('qs_assessment_num')
    customer_name_id=PkneedassessmentInfo.objects.get(id=qs_assessment_num).na_customer_name.id
    exists = PkquotationsummaryInfo.objects.filter(qs_assessment_num=qs_assessment_num).exists()
    return JsonResponse(
        {
            'exists': exists,
            'customer_name_id':customer_name_id,
        }
    )

@login_required(login_url='login_page')
def pk_bvm_quotation_pdf(request,quotation_id=0):
    needassessment_id = request.session.get('na_assessment_id')
    address=PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id).qs_address
    cost_includes=PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id).qs_cost_includes
    notes=PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id).qs_notes
    terms_condition=PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id).qs_terms_condition
    client_scope=PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id).qs_client_scope
    bvm_scope=PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id).qs_bvm_scope
    needassessment_num=PkneedassessmentInfo.objects.get(pk=needassessment_id).na_assessment_num
    quotation=Nadimension.objects.filter(nad_assess_num=needassessment_id)
    # get requirement type from need assessment dimension model
    na_req=Nadimension.objects.filter(nad_assess_num=needassessment_id)
    quotation_number = PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id).qs_quotation_number
    margin = PkquotationsummaryInfo.objects.get(qs_assessment_num=needassessment_id).qs_margin
    total_sum=0
    for i in na_req:
        j=i.nad_item
        k=i.id
        qty=i.nad_quantity
        total_cost_wom=PkquotationInfo.objects.filter(pkqt_assessment_num=needassessment_id,pkqt_requirement=i).aggregate(total_cost=Sum('pkqt_total_cost'))['total_cost'] or 0
        total_cost=total_cost_wom+(total_cost_wom*margin/100)
        Nadimension.objects.filter(pk=k).update(nad_cost_total=round(total_cost,2))
        try:
            Nadimension.objects.filter(pk=k).update(nad_cost_unit=round(total_cost/qty,2))
        except:
            Nadimension.objects.filter(pk=k).update(nad_cost_unit=0)
        total_sum=total_sum+total_cost
    gst=round(total_sum*18/100,2)
    final_cost=round((total_sum+gst),2)
    today = datetime.now()
    formatted_date = today.strftime("%d-%b-%Y")
    context = {
        'address': address,
        'cost_includes': cost_includes,
        'notes': notes,
        'terms_condition': terms_condition,
        'client_scope': client_scope,
        'bvm_scope': bvm_scope,
        'quotation': quotation,
        'total_sum': total_sum,
        'gst': gst,
        'final_cost': final_cost,
        'quotation_number': quotation_number,
        'today_date': formatted_date,
    }
    file_name = str("Quotation_") + str(needassessment_num) + str(".pdf")
    template_path = 'asset_mgt_app/bvm_pk_quotation_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    template = get_template(template_path)
    html = template.render(context)

    # Create PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We has some error <pre>' + html + '</pre>')
    return response