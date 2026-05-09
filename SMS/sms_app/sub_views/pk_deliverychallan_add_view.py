from django.contrib.auth.decorators import login_required
from ..forms import DeliverychallanForm
from ..models import Pkdeliverychallan,Warehouse_goods_info,CustomerInfo,POdimension
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.shortcuts import render, redirect


@login_required(login_url='login_page')
def delivery_challan_add(request, delivery_id=0):
    first_name = request.session.get('first_name')
    delivery_list = Pkdeliverychallan.objects.all()
    if request.method == "GET":
        if delivery_id == 0:
            print("I am inside Get add dispatch")
            form = DeliverychallanForm()
            context = {
                'form':form,
                'first_name': first_name,
                'delivery_list': delivery_list,
            }
        else:
            print("I am inside get edit Dispatch")
            delivery = Pkdeliverychallan.objects.get(pk=delivery_id)
            form = DeliverychallanForm(instance=delivery)
            deliverychallan_list = POdimension.objects.filter(pod_assess_num=delivery.dc_assessment_num,pod_po_num=delivery.dc_customer_po)
            context = {
                'form':form,
                'deliverychallan_list': deliverychallan_list,
                'first_name': first_name,
            }
        return render(request, "asset_mgt_app/pk_deliverychallan_add.html", context)

    else:
        if delivery_id == 0:
            form = DeliverychallanForm(request.POST)
        else:
            delivery = Pkdeliverychallan.objects.get(pk=delivery_id)
            form = DeliverychallanForm(request.POST, instance=delivery)
        if form.is_valid():
            form.save()
            if delivery_id == 0:
                messages.success(request, 'Record Saved Successfully')
            else:
                messages.success(request, 'Record Updated Successfully')
        else:
            messages.error(request, 'Error: Please correct the errors below.')

        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error in {field}: {error}")
                messages.error(request, f"Error in {field}: {error}")
        return redirect(request.META['HTTP_REFERER'])


# List gatepass
@login_required(login_url='login_page')
def delivery_challan_list(request):
    first_name = request.session.get('first_name')
    delivery_list = Pkdeliverychallan.objects.all()
    context = {'delivery_list': delivery_list, 'first_name': first_name}
    return render(request,"asset_mgt_app/pk_deliverychallan_list.html",context)

#Delete gatepass
@login_required(login_url='login_page')
def delivery_challan_delete(request,delivery_id):
    delivery = Pkdeliverychallan.objects.get(pk=delivery_id)
    delivery.delete()
    return redirect('/SMS/packing_delivery_list')


@login_required(login_url='login_page')
def delivery_challan_pdf(request, delivery_id):
    delivery = Pkdeliverychallan.objects.filter(id=delivery_id).first()
    
    # Use direct link via Job No in Costing for more accurate item listing
    job_no = PkcostingsummaryInfo.objects.filter(cs_customer_po=delivery.dc_customer_po, cs_assessment_num=delivery.dc_assessment_num).values_list('cs_job_no', flat=True).first()
    
    if job_no:
        pod_ids = PkcostingInfo.objects.filter(ct_job_no=job_no).values_list('ct_po_dimension', flat=True).distinct()
        challan_list = POdimension.objects.filter(id__in=pod_ids)
    else:
        challan_list = POdimension.objects.filter(pod_assess_num=delivery.dc_assessment_num,pod_po_num=delivery.dc_customer_po)
    if not delivery:
        messages.error(request, "Record not found.")
        return redirect('/SMS/packing_delivery_list')

    wh_location = None
    if delivery.dc_sales_order_po:
        wh_location = Warehouse_goods_info.objects.filter(wh_dispatch_num=delivery.dc_sales_order_po).values_list(
            'wh_branch__loc_name', flat=True).order_by('id').first()

    print("Warehouse Location:", wh_location)

    if not wh_location:
        wh_location = "BVM Chennai"

    total_qty = sum(item.pod_quantity or 0 for item in challan_list)
    total_base = sum(item.pod_base_value or 0 for item in challan_list)
    total_gst = sum(item.pod_gst_amount or 0 for item in challan_list)
    total_amount = sum(item.pod_total_value or 0 for item in challan_list)

    context = {
        'delivery': delivery,
        'challan_list': challan_list,
        'wh_location': wh_location,
        'total_qty': total_qty,
        'total_base': total_base,
        'total_gst': total_gst,
        'total_amount': total_amount,
    }

    file_name = f"Delivery_Challan_{delivery_id}.pdf"
    template_path = 'asset_mgt_app/pk_deliverychallan_pdf.html'
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We encountered an error while generating the PDF.')

    return response





