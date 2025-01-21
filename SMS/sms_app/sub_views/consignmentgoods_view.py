import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from ..forms import ConsignmentgoodsaddForm
from ..models import EnquirynoteInfo,ConsignmentgoodsInfo,ConsignmentdetailInfo,consignmentsgoods_new_info
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

@login_required(login_url='login_page')
def consignmentgoods_add(request,consignmentgoods_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    consignmentgoods_id_val=request.session.get('ses_consignment_id')
    if request.method == "GET":
        if consignmentgoods_id == 0:
            form = ConsignmentgoodsaddForm()
        else:
            consignmentgoods=ConsignmentgoodsInfo.objects.get(pk=consignmentgoods_id)
            form = ConsignmentgoodsaddForm(instance=consignmentgoods)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'consignmentgoods_list': ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber=consignmentgoods_id_val),
                'consignmentgoods_id_val': consignmentgoods_id_val,
                }
        return render(request, "asset_mgt_app/consignmentgoods_add.html", context)
    else:
        if consignmentgoods_id == 0:
            form = ConsignmentgoodsaddForm(request.POST)
            if form.is_valid():
                form.save()
                print("consignmentgoods Form is Valid")
                last_id = (ConsignmentgoodsInfo.objects.latest('id')).id
                messages.success(request, 'Record Updated Successfully')
                return redirect('/SMS/consignmentgoods_update/'+str(last_id))
            else:
                print("consignmentgoods Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("Inside consignmentgoods POST edit")
            consignmentgoods = ConsignmentgoodsInfo.objects.get(pk=consignmentgoods_id)
            form = ConsignmentgoodsaddForm(request.POST,instance=consignmentgoods)
            if form.is_valid():
                form.save()
                print("consignmentgoods Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("consignmentgoods Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

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



def save_consignment_data(request):
    # Retrieve consignment ID from session
    consignmentgoods_id_val = request.session.get('ses_consignment_id')
    consignment_instance = ConsignmentgoodsInfo.objects.get(pk=consignmentgoods_id_val)

    # Get the consignment number
    consignment_number = consignment_instance.cn_consignment_num

    if request.method == 'POST':
        # Retrieve POST data
        consignments_nums = request.POST.getlist('consignments[]')
        pieces = request.POST.getlist('pieces[]')
        lengths = request.POST.getlist('length[]')
        widths = request.POST.getlist('width[]')
        heights = request.POST.getlist('height[]')
        weights = request.POST.getlist('weight[]')

        response_data = {'status': 'success', 'message': 'Rows saved successfully.', 'duplicates': []}

        for i in range(len(consignments_nums)):
            # Check if the consignment already exists
            existing_goods = consignmentsgoods_new_info.objects.filter(
                cn_consignment_num=consignment_instance,
                cn_new_goods_pieces=pieces[i],
                cn_new_goods_length=lengths[i],
                cn_new_goods_width=widths[i],
                cn_new_goods_height=heights[i],
                cn_new_goods_weight=weights[i],
            ).first()

            if existing_goods:
                # Update the existing record
                existing_goods.cn_consignment_num = consignment_instance  # No index needed here
                existing_goods.cn_new_goods_pieces = pieces[i]
                existing_goods.cn_new_goods_length = lengths[i]
                existing_goods.cn_new_goods_width = widths[i]
                existing_goods.cn_new_goods_height = heights[i]
                existing_goods.cn_new_goods_weight = weights[i]
                existing_goods.save()
            else:
                # Create a new record
                consignmentsgoods_new_info.objects.create(
                    cn_consignment_num=consignment_instance,
                    cn_new_goods_pieces=pieces[i],
                    cn_new_goods_length=lengths[i],
                    cn_new_goods_width=widths[i],
                    cn_new_goods_height=heights[i],
                    cn_new_goods_weight=weights[i]
                )

        # Prepare a success message and return
        messages.success(request, "Consignment data saved successfully.")
        return redirect('save_consignment_data')

    # Fetch existing consignment goods
    consignmentgoods_new_list = consignmentsgoods_new_info.objects.filter( cn_consignment_num=consignment_instance ) # Fetch all consignment goods for the dropdown list
    consignments_list = ConsignmentgoodsInfo.objects.all()
    return render(request, 'asset_mgt_app/consignmentgoods_new_list.html',
                { 'consignmentgoods_new_list': consignmentgoods_new_list,
                    'consignments_list': consignments_list, # Update to pass the list
                    'consignment_number': consignment_number,
                    'consignment_id': consignmentgoods_id_val, })
@csrf_exempt
def delete_consignment_data(request):
    if request.method == 'POST':
        consignment_id = request.POST.get('ses_consignment_id')
        try:
            # Delete the record from the database
            consignmentsgoods_new_info.objects.filter(pk=consignment_id).delete()
            return JsonResponse({'status': 'success'}, status=200)
        except consignmentsgoods_new_info.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Record not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
