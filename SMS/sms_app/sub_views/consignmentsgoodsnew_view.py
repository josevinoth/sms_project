from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import ConsignmentgoodsnewaddForm, ConsignmentgoodsaddForm
from ..models import consignmentsgoods_new_info, ConsignmentgoodsInfo


@login_required(login_url='login_page')
def consignment_goods_add(request, goods_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    consignmentgoods_id_val = request.session.get('ses_consignment_id')

    consignmentgoods = ConsignmentgoodsInfo.objects.filter(pk=consignmentgoods_id_val).first()
    form = ConsignmentgoodsaddForm(instance=consignmentgoods)

    # Handling GET request
    if request.method == "GET":
        if goods_id == 0:
            cn_form = ConsignmentgoodsnewaddForm()
        else:
            goods = consignmentsgoods_new_info.objects.filter(pk=goods_id).first()
            cn_form = ConsignmentgoodsnewaddForm(instance=goods) if goods else ConsignmentgoodsnewaddForm()

        return render(request, "asset_mgt_app/consignmentgoods_add.html", {
            'form': form,
            'cn_form': cn_form,
            'first_name': first_name,
            'user_id': user_id,
            'consignmentgoods_id_val': consignmentgoods_id_val,
        })

    else:
        if goods_id == 0:
            cn_form = ConsignmentgoodsnewaddForm(request.POST)
        else:
            goods = consignmentsgoods_new_info.objects.filter(pk=goods_id).first()
            cn_form = ConsignmentgoodsnewaddForm(request.POST, instance=goods)

        if cn_form.is_valid():
            cn_form.save()
            messages.success(request, "Record saved successfully.")

            return redirect('/SMS/consignment_goods_list')

        messages.error(request, "Form is invalid. Please check the inputs.")
        print("Form Errors:", cn_form.errors)  # Debugging
    for field, errors in form.errors.items():
        for error in errors:
            print(f"Error in {field}: {error}")
            messages.error(request, f"Error in {field}: {error}")

    return render(request, "asset_mgt_app/consignmentgoods_add.html", {
        'form': form,
        'cn_form': cn_form,
        'first_name': first_name,
        'user_id': user_id,
        'consignmentgoods_id_val': consignmentgoods_id_val,
    })


@login_required(login_url='login_page')
def consignment_goods_list(request):
    first_name = request.session.get('first_name')
    consignmentgoods_id_val = request.session.get('ses_consignment_id')

    goods_list = consignmentsgoods_new_info.objects.filter(consignment_id=consignmentgoods_id_val)

    context = {
        'goods_list': goods_list,
        'first_name': first_name,
        'consignmentgoods_id_val': consignmentgoods_id_val,
    }

    return render(request, "asset_mgt_app/consignment_goods_list.html", context)


@login_required(login_url='login_page')
def consignment_goods_delete(request, goods_id):
    goods = consignmentsgoods_new_info.objects.filter(pk=goods_id).first()

    if goods:
        goods.delete()
        messages.success(request, "Record deleted successfully.")
    else:
        messages.error(request, "Record not found.")

    return redirect('/SMS/consignment_goods_list')
