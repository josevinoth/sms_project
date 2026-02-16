import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..forms import ConsignmentgoodsaddForm,ConsignmentdetailaddForm
from ..models import EnquirynoteInfo,ConsignmentgoodsInfo,ConsignmentdetailInfo,Stock_type,ConsigneeInfo,ConsignerInfo
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages



@login_required(login_url='login_page')
def consignmentgoods_add(request, consignmentgoods_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    consignment_detail_id = request.session.get('ses_consignment_detail_id')
    print('consignment_detail_id', consignment_detail_id)
    if request.method == "GET":
        existing_invoices = (
            ConsignmentgoodsInfo.objects
            .filter(cg_consignmentnumber=consignment_detail_id)
            .values_list('cg_consignerinvoice', flat=True)
            .exclude(cg_consignerinvoice__isnull=True)
            .exclude(cg_consignerinvoice__exact='')
            .distinct()
        )
        if consignmentgoods_id == 0:
            form = ConsignmentgoodsaddForm()
            consignmentdetail = ConsignmentdetailInfo.objects.get(pk=consignment_detail_id)
            con_det_form = ConsignmentdetailaddForm(instance=consignmentdetail)

        else:
            consignmentgoods = ConsignmentgoodsInfo.objects.get(pk=consignmentgoods_id)
            consignmentdetail = ConsignmentdetailInfo.objects.get(pk=consignment_detail_id)
            con_det_form = ConsignmentdetailaddForm(instance=consignmentdetail)
            form = ConsignmentgoodsaddForm(instance=consignmentgoods)
            form.fields['cg_description'].queryset = Stock_type.objects.all()
        context = {
            'form': form,
            'con_det_form': con_det_form,
            'first_name': first_name,
            'user_id': user_id,
            'existing_invoices': existing_invoices,
            'consignmentdetail_id': consignment_detail_id,
            'consignmentgoods_list': ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber=consignment_detail_id),
        }
        return render(request, "asset_mgt_app/consignmentdetail_add.html", context)

    else:
        if consignmentgoods_id == 0:
            form = ConsignmentgoodsaddForm(request.POST, request.FILES)
        else:
            consignmentgoods = ConsignmentgoodsInfo.objects.get(pk=consignmentgoods_id)
            form = ConsignmentgoodsaddForm(request.POST, request.FILES, instance=consignmentgoods)

        form.fields['cg_description'].queryset = Stock_type.objects.all()
        if form.is_valid():
            form.save()
            messages.success(request, 'Record  Updated Successfully')
            print("Consignment Goods form is valid", form.errors)
            return redirect(request.META['HTTP_REFERER'])
        else:
            print("Consignment Goods form is not valid", form.errors)
            messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])

# List consignmentgoods
@login_required(login_url='login_page')
def consignmentgoods_list(request):
    first_name = request.session.get('first_name')
    consignmentgoods_id_val = request.session.get('ses_consignment_id')
    consignmentgoods_list=ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber=consignmentgoods_id_val)
    context = {
        'consignmentgoods_list' : consignmentgoods_list,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/consignmentgoods_list.html", context)
#Delete consignmentgoods
@login_required(login_url='login_page')
def consignmentgoods_delete(request,consignmentgoods_id):
    consignmentgoods = ConsignmentgoodsInfo.objects.get(pk=consignmentgoods_id)
    consignmentgoods.delete()
    # return redirect('/SMS/consignmentgoods_list')
    return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login_page')
def consignmentgoods_nav(request,consignmentdetails_id):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    consignmentgoods_id = ConsignmentdetailInfo.objects.get(pk=consignmentdetails_id).id
    request.session['ses_consignment_id']=consignmentgoods_id
    form = ConsignmentgoodsaddForm(request.POST)
    context = {
        'first_name': first_name,
        'user_id': user_id,
        'form': form,
        'consignmentgoods_id': consignmentgoods_id,
        'consignmentgoods_list': ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber=consignmentgoods_id),
    }
    return render(request, "asset_mgt_app/consignmentgoods_nav.html", context)

@login_required(login_url='login_page')
def consignmentgoods_cancel(request):
    consignmentgoods_id_val = request.session.get('ses_consignment_id')
    enquirynote_num=ConsignmentdetailInfo.objects.get(id=consignmentgoods_id_val).co_enquirynumber
    enquirynote_id=EnquirynoteInfo.objects.get(en_enquirynumber=enquirynote_num).id
    # return redirect('/SMS/consignmentdetail_nav/' + str(enquirynote_id))
    return redirect('/SMS/consignmentgoods_nav/' + str(consignmentgoods_id_val))

@login_required(login_url='login_page')
def consignmentgoods_back(request):
    consignmentgoods_id_val = request.session.get('ses_consignment_id')
    enquirynote_num=ConsignmentdetailInfo.objects.get(id=consignmentgoods_id_val).co_enquirynumber
    enquirynote_id=EnquirynoteInfo.objects.get(en_enquirynumber=enquirynote_num).id
    return redirect('/SMS/consignmentdetail_nav/' + str(enquirynote_id))
    # return redirect('/SMS/consignmentgoods_nav/' + str(consignmentgoods_id_val))


def add_description(request):
    if request.method == 'POST':
        name = request.POST.get('cg_description')
        if name:
            existing = Stock_type.objects.filter(stock_type__iexact=name).first()
            if existing:
                return JsonResponse({'id': existing.id, 'stock_type': existing.stock_type})
            new_desc = Stock_type.objects.create(stock_type=name)
            return JsonResponse({'id': new_desc.id, 'stock_type': new_desc.stock_type})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def add_consigner(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if not name:
            return JsonResponse({"success": False, "error": "Consigner name cannot be empty."})

        existing = ConsignerInfo.objects.filter(consigner_name__iexact=name).first()
        if existing:
            return JsonResponse({"success": True, "id": existing.id, "name": existing.consigner_name})

        new = ConsignerInfo.objects.create(consigner_name=name)
        return JsonResponse({"success": True, "id": new.id, "name": new.consigner_name})

    return JsonResponse({"success": False, "error": "Invalid request."})

@csrf_exempt
def add_consignee(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        address = request.POST.get("address", "").strip()
        country_code = request.POST.get("country_code", "").strip()
        
        if not name:
            return JsonResponse({"success": False, "error": "Consignee name cannot be empty."})
        
        existing = ConsigneeInfo.objects.filter(consignee_name__iexact=name).first()
        if existing:
            return JsonResponse({
                "success": False,
                "id": existing.id,
                "name": existing.consignee_name,
                "error": "This consignee already exists."
            })
        
        new = ConsigneeInfo.objects.create(
            consignee_name=name,
            consignee_address=address if address else None,
            consignee_country_code=country_code if country_code else None
        )
        return JsonResponse({"success": True, "id": new.id, "name": new.consignee_name})
    
    return JsonResponse({"success": False, "error": "Invalid request"})


@csrf_exempt
@login_required(login_url='login_page')
def consignmentgoods_upload_attachment(request, pk, att_type):
    if request.method == 'POST' and request.FILES.get('attachment'):
        instance = get_object_or_404(ConsignmentgoodsInfo, pk=pk)
        uploaded_file = request.FILES['attachment']

        if att_type == 'eway':
            instance.cg_ewaybill_att = uploaded_file
        elif att_type == 'invoice':
            instance.cg_invoice_att = uploaded_file
        elif att_type == 'otl':
            instance.cg_otl_att = uploaded_file

        instance.save()
        messages.success(request, 'Attachment uploaded successfully.')
    else:
        messages.error(request, 'Attachment upload failed. Please try again.')

    return redirect(request.META.get('HTTP_REFERER', 'consignmentgoods_list'))

@csrf_exempt
def consignmentgoods_delete_attachment(request, pk, att_type):
    if request.method == 'POST':
        instance = get_object_or_404(ConsignmentgoodsInfo, pk=pk)

        if att_type == 'eway':
            instance.cg_ewaybill_att.delete(save=False)
            instance.cg_ewaybill_att = None
        elif att_type == 'invoice':
            instance.cg_invoice_att.delete(save=False)
            instance.cg_invoice_att = None
        elif att_type == 'otl':
            instance.cg_otl_att.delete(save=False)
            instance.cg_otl_att = None

        instance.save()
    return redirect(request.META.get('HTTP_REFERER', 'consignmentgoods_list'))
