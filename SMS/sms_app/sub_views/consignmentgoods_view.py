from django.contrib.auth.decorators import login_required

from ..forms import ConsignmentgoodsaddForm,ConsignmentdetailaddForm
from ..models import EnquirynoteInfo,ConsignmentgoodsInfo,ConsignmentdetailInfo
from django.shortcuts import render, redirect
from django.contrib import messages


@login_required(login_url='login_page')
def consignmentgoods_add(request, consignmentgoods_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    consignment_detail_id = request.session.get('ses_consignment_detail_id')
    print('consignment_detail_id', consignment_detail_id)
    if request.method == "GET":
        if consignmentgoods_id == 0:
            form = ConsignmentgoodsaddForm()
            consignmentdetail = ConsignmentdetailInfo.objects.get(pk=consignment_detail_id)
            con_det_form = ConsignmentdetailaddForm(instance=consignmentdetail)
        else:
            consignmentgoods = ConsignmentgoodsInfo.objects.get(pk=consignmentgoods_id)
            consignmentdetail = ConsignmentdetailInfo.objects.get(pk=consignment_detail_id)
            con_det_form = ConsignmentdetailaddForm(instance=consignmentdetail)
            form = ConsignmentgoodsaddForm(instance=consignmentgoods)
        context = {
            'form': form,
            'con_det_form': con_det_form,
            'first_name': first_name,
            'user_id': user_id,
            'consignmentdetail_id': consignment_detail_id,
            'consignmentgoods_list': ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber=consignment_detail_id),
        }
        return render(request, "asset_mgt_app/consignmentdetail_add.html", context)

    else:
        if consignmentgoods_id == 0:
            form = ConsignmentgoodsaddForm(request.POST)
        else:
            consignmentgoods = ConsignmentgoodsInfo.objects.get(pk=consignmentgoods_id)
            form = ConsignmentgoodsaddForm(request.POST,instance=consignmentgoods)
        if form.is_valid() :
            form.save()
            messages.success(request, 'Record  Updated Successfully')
            print("Consignment Goods form is valid")
            return redirect(request.META['HTTP_REFERER'])
        else:
            print("Consignment Goods form is not valid")
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

