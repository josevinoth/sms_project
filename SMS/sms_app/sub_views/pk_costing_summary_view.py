from datetime import datetime
import openpyxl
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from xhtml2pdf import pisa
from ..forms import PkcostingsummaryForm
from ..models import User_extInfo,PkpurchaseorderInfo,POdimension,PkcostingsummaryInfo,PkneedassessmentInfo,PkcostingInfo
from django.shortcuts import render, redirect
from django.db.models.aggregates import Sum
from django.contrib import messages
from django.http import JsonResponse, HttpResponse


@login_required(login_url='login_page')
def costingsummary_add(request,costingsummary_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    role_id = User_extInfo.objects.get(user=user_id).emp_role.id
    if request.method == "GET":
        if costingsummary_id == 0:
            print('Inside costing summary Get add')
            form = PkcostingsummaryForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'role': role,
                'role_id': role_id,
            }
        else:
            print('Inside costing summary Get edit')
            costingsummary=PkcostingsummaryInfo.objects.get(pk=costingsummary_id)
            needassessment_num = PkcostingsummaryInfo.objects.get(pk=costingsummary_id).cs_assessment_num
            needassessment_id = PkneedassessmentInfo.objects.get(na_assessment_num=needassessment_num).id
            customer_name_id = PkcostingsummaryInfo.objects.get(pk=costingsummary_id).cs_customer_name.id
            customer_po_id = PkcostingsummaryInfo.objects.get(pk=costingsummary_id).cs_customer_po.id
            request.session['na_assessment_id'] = needassessment_id
            request.session['na_customer_name_id'] = customer_name_id
            request.session['ses_customer_po_id'] = customer_po_id
            form = PkcostingsummaryForm(instance=costingsummary)
            costing_list = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id)
            # wood_cost = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id,ct_cost_type=8,ct_stock_type=1,ct_stock_type=4).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            wood_cost = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id,ct_stock_type__in=[1, 4],ct_cost_type=8).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            if wood_cost is not None:
                wood_cost = round(wood_cost, 2)
            else:
                wood_cost = 0.0
            # print(wood_cost)
            PkcostingsummaryInfo.objects.filter(cs_assessment_num=needassessment_id).update(cs_wood_cost=wood_cost)

            total_cft = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id, ct_cost_type=8,ct_stock_type=1).aggregate(Sum('ct_cft'))['ct_cft__sum']
            if total_cft is not None:
                total_cft = round(total_cft, 2)
            else:
                total_cft = 0.0
            # print(total_cft)
            PkcostingsummaryInfo.objects.filter(cs_assessment_num=needassessment_id).update(cs_total_cft=total_cft)

            engineer_cost = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id, ct_cost_type=2).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            if engineer_cost is not None:
                engineer_cost = round(engineer_cost, 2)
            else:
                engineer_cost = 0.0
            # print(engineer_cost)
            PkcostingsummaryInfo.objects.filter(cs_assessment_num=needassessment_id).update(cs_engineer_cost=engineer_cost)

            # making_labour_cost = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id, ct_cost_type=2).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            # if making_labour_cost is not None:
            #     making_labour_cost = round(making_labour_cost, 2)
            # else:
            #     making_labour_cost = 0.0

            packing_labour_cost = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id, ct_cost_type=3).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
            print('packing_labour_cost',packing_labour_cost)
            if packing_labour_cost is not None:
                packing_labour_cost = round(packing_labour_cost, 2)
            else:
                packing_labour_cost = 0.0

            # labour_cost=making_labour_cost+packing_labour_cost
            labour_cost=packing_labour_cost
            # print(labour_cost)
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

            material_cost = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id, ct_cost_type=8,ct_stock_type=2).aggregate(Sum('ct_total_cost'))['ct_total_cost__sum']
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
                    'wood_cost': wood_cost,
                    'engineer_cost': engineer_cost,
                    'labour_cost': labour_cost,
                    'crane_cost': crane_cost,
                    'ht_cost': ht_cost,
                    'management_cost': management_cost,
                    'material_cost': material_cost,
                    'transport_cost': transport_cost,
                    'role': role,
                    'role_id': role_id,
                    }
        return render(request, "asset_mgt_app/pk_costingsummary_add.html", context)
    else:
        print('costingsummary_id',costingsummary_id)
        if costingsummary_id == 0:
            print("Inside pk_costing_summary post add")
            form = PkcostingsummaryForm(request.POST)
            if form.is_valid():
                form.save()
                print("PkcostingsummaryInfo Form is Valid")
                last_id = (PkcostingsummaryInfo.objects.latest('id')).id
                messages.success(request, 'Record Updated Successfully')
                return redirect('/SMS/costingsummary_update/' + str(last_id))
            else:
                print("PkcostingsummaryInfo Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("Inside pk_costing_summary post edit")
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

@login_required(login_url='login_page')
def pk_costing_get_customer(request):
    cs_assessment_num = request.GET.get('cs_assessment_num')
    customer_name_id=PkneedassessmentInfo.objects.get(id=cs_assessment_num).na_customer_name.id
    customer_po_qs = PkpurchaseorderInfo.objects.filter(po_assessment_num=cs_assessment_num,po_status=5)
    customer_po_name = list(customer_po_qs.values_list('po_num', flat=True))
    customer_po_id = list(customer_po_qs.values_list('id', flat=True))
    return JsonResponse(
        {
            'customer_name_id':customer_name_id,
            'customer_po_id':customer_po_id,
            'customer_po_name':customer_po_name,
        }
    )

@login_required(login_url='login_page')
def pk_costing_summary_check_unique_field(request):
    cs_assessment_num = request.GET.get('cs_assessment_num')
    cs_po_num = request.GET.get('cs_customer_po_num')
    exists = PkcostingsummaryInfo.objects.filter(cs_assessment_num=cs_assessment_num,cs_customer_po=cs_po_num).exists()
    return JsonResponse(
        {
            'exists': exists,
        }
    )

@login_required(login_url='login_page')
def pk_bvm_invoice_pdf(request,invoice_id=0):
    needassessment_id = request.session.get('na_assessment_id')
    address=PkcostingsummaryInfo.objects.get(cs_assessment_num=needassessment_id).cs_address
    cost_includes=PkcostingsummaryInfo.objects.get(cs_assessment_num=needassessment_id).cs_cost_includes
    notes=PkcostingsummaryInfo.objects.get(cs_assessment_num=needassessment_id).cs_notes
    terms_condition=PkcostingsummaryInfo.objects.get(cs_assessment_num=needassessment_id).cs_terms_condition
    client_scope=PkcostingsummaryInfo.objects.get(cs_assessment_num=needassessment_id).cs_client_scope
    bvm_scope=PkcostingsummaryInfo.objects.get(cs_assessment_num=needassessment_id).cs_bvm_scope
    needassessment_num=PkneedassessmentInfo.objects.get(pk=needassessment_id).na_assessment_num
    invoices=POdimension.objects.filter(pod_assess_num=needassessment_id)
    # get requirement type from need assessment dimension model
    na_req=POdimension.objects.filter(pod_assess_num=needassessment_id)
    po_number = PkcostingsummaryInfo.objects.get(cs_assessment_num=needassessment_id).cs_customer_po
    margin = PkcostingsummaryInfo.objects.get(cs_assessment_num=needassessment_id).cs_margin
    total_sum=0
    for i in na_req:
        j=i.pod_item
        k=i.id
        qty=i.pod_quantity
        total_cost_wom=PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id,ct_requirement=i).aggregate(total_cost=Sum('ct_total_cost'))['total_cost'] or 0
        total_cost=total_cost_wom+(total_cost_wom*margin/100)
        POdimension.objects.filter(pk=k).update(pod_cost_total=round(total_cost,2))
        try:
            POdimension.objects.filter(pk=k).update(pod_cost_unit=round(total_cost/qty,2))
        except:
            POdimension.objects.filter(pk=k).update(pod_cost_unit=0)
        total_sum=round((total_sum+total_cost),2)
    gst_val=PkcostingsummaryInfo.objects.get(cs_assessment_num=needassessment_id).cs_gst
    gst=round(total_sum*gst_val/100,2)
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
        'invoices': invoices,
        'total_sum': total_sum,
        'gst_val': gst_val,
        'gst': gst,
        'final_cost': final_cost,
        'po_number': po_number,
        'today_date': formatted_date,
    }
    file_name = str("Invoice_") + str(needassessment_num) + str(".pdf")
    template_path = 'asset_mgt_app/bvm_pk_invoice_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    template = get_template(template_path)
    html = template.render(context)

    # Create PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We has some error <pre>' + html + '</pre>')
    return response

def pk_bvm_invoice_excel(request, invoice_id=0):
    needassessment_id = request.session.get('na_assessment_id')
    summary_info = PkcostingsummaryInfo.objects.get(cs_assessment_num=needassessment_id)
    needassessment_num = PkneedassessmentInfo.objects.get(pk=needassessment_id).na_assessment_num
    invoices = POdimension.objects.filter(pod_assess_num=needassessment_id)
    na_req = POdimension.objects.filter(pod_assess_num=needassessment_id)
    margin = summary_info.cs_margin
    total_sum = 0

    for i in na_req:
        qty = i.pod_quantity
        total_cost_wom = PkcostingInfo.objects.filter(ct_assessment_num=needassessment_id, ct_requirement=i).aggregate(
            total_cost=Sum('ct_total_cost'))['total_cost'] or 0
        total_cost = total_cost_wom + (total_cost_wom * margin / 100)
        POdimension.objects.filter(pk=i.id).update(pod_cost_total=round(total_cost, 2))
        try:
            POdimension.objects.filter(pk=i.id).update(pod_cost_unit=round(total_cost / qty, 2))
        except:
            POdimension.objects.filter(pk=i.id).update(pod_cost_unit=0)
        total_sum = round((total_sum + total_cost), 2)

    gst_val = summary_info.cs_gst
    gst = round(total_sum * gst_val / 100, 2)
    final_cost = round((total_sum + gst), 2)
    today = datetime.now().strftime("%d-%b-%Y")

    # Create an Excel workbook and add a worksheet.
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Invoice"

    # Write the header
    ws.append([
        "Address", "Cost Includes", "Notes", "Terms & Conditions",
        "Client Scope", "BVM Scope", "PO Number", "Total Sum",
        "GST Value", "GST", "Final Cost", "Date"
    ])
    # Write the summary info
    ws.append([
        summary_info.cs_address, summary_info.cs_cost_includes, summary_info.cs_notes, summary_info.cs_terms_condition,
        summary_info.cs_client_scope, summary_info.cs_bvm_scope, summary_info.cs_customer_po, total_sum,
        gst_val, gst, final_cost, today
    ])

    # Write the invoice items header
    ws.append([
        "Item", "Type of Requirement", "Length", "Width",
        "Height", "Quantity", "Total Cost", "Unit Cost"
    ])
    # Write the invoice items
    for invoice in invoices:
        ws.append([
            invoice.pod_item, invoice.pod_type_of_req, invoice.pod_length, invoice.pod_width,
            invoice.pod_height, invoice.pod_quantity, invoice.pod_cost_total, invoice.pod_cost_unit
        ])

    # Create an HttpResponse with the appropriate Excel content type
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    file_name = f"Invoice_{needassessment_num}.xlsx"
    response['Content-Disposition'] = f'attachment; filename={file_name}'

    # Save the workbook to the response
    wb.save(response)
    return response