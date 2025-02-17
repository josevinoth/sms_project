import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..forms import ConsignmentgoodsaddForm,ConsignmentgoodsnewaddForm,ConsignmentdetailaddForm
from ..models import EnquirynoteInfo,ConsignmentgoodsInfo,ConsignmentdetailInfo,consignmentsgoods_new_info
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


@login_required(login_url='login_page')
def consignmentgoods_add(request, consignmentgoods_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    consignmentgoods_id_val = request.session.get('ses_consignment_id')

    if request.method == "GET":
        if consignmentgoods_id == 0:
            form = ConsignmentgoodsaddForm()
            cn_form = ConsignmentgoodsnewaddForm()
            con_det_form = ConsignmentdetailaddForm()
        else:
            consignmentgoods = ConsignmentgoodsInfo.objects.get(pk=consignmentgoods_id)
            form = ConsignmentgoodsaddForm(instance=consignmentgoods)
            cn_form = ConsignmentgoodsnewaddForm()
            con_det_form = ConsignmentdetailaddForm()

        context = {
            'form': form,
            'cn_form': cn_form,
            'con_det_form': con_det_form,
            'first_name': first_name,
            'user_id': user_id,
            'consignmentgoods_list': ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber=consignmentgoods_id_val),
            'consignmentgoods_id_val': consignmentgoods_id_val,
        }
        return render(request, "asset_mgt_app/consignmentgoods_add.html", context)

    else:
        form = ConsignmentgoodsaddForm(request.POST)
        cn_form = ConsignmentgoodsnewaddForm(request.POST)
        con_det_form = ConsignmentdetailaddForm(request.POST)

        if form.is_valid() and cn_form.is_valid() and con_det_form.is_valid():
            consignment_goods = form.save()
            new_goods = cn_form.save(commit=False)
            new_goods.consignmentgoods = consignment_goods
            new_goods.save()

            consignment_detail = con_det_form.save(commit=False)
            consignment_detail.co_consignmentnumber = consignmentgoods_id_val
            consignment_detail.save()

            last_id = ConsignmentgoodsInfo.objects.latest('id').id
            messages.success(request, 'Record Updated Successfully')
            return redirect(f'/SMS/consignmentgoods_update/{last_id}')
        else:
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

    # assessment_num_val = request.session.get('na_assessment_id')
    # costing_summary_id=PkcostingsummaryInfo.objects.get(cs_assessment_num=assessment_num_val).id
    # return redirect('/SMS/consignmentdetail_update/' + str(costing_summary_id))
    # return render(request,"asset_mgt_app/consignmentdetails_list.html",context)
    # return redirect('/SMS/consignmentdetail_list')
    return render(request, "asset_mgt_app/consignmentgoods_list.html", context)
#Delete consignmentgoods
@login_required(login_url='login_page')
def consignmentgoods_delete(request,consignmentgoods_id):
    consignmentgoods = ConsignmentgoodsInfo.objects.get(pk=consignmentgoods_id)
    consignmentgoods.delete()
    return redirect('/SMS/consignmentgoods_list')

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
