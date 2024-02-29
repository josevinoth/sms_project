from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..forms import IouForm
from ..models import iuo_info
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def iou_add(request,iou_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if iou_id == 0:
            form = IouForm()
        else:
            iou = iuo_info.objects.get(pk=iou_id)
            form = IouForm(instance=iou)
        return render(request, "asset_mgt_app/iou_add.html", {'form': form, 'first_name': first_name,'user_id':user_id,})
    else:
        form = IouForm(request.POST)

        if form.is_valid():
            # Check for duplicates before saving
            staff_name = form.cleaned_data['staff_name']
            transaction_type = form.cleaned_data['transaction_type']
            transaction_date = form.cleaned_data['transaction_date']
            business_type = form.cleaned_data['business_type']
            amount = form.cleaned_data['amount']
            if not iuo_info.objects.filter(staff_name=staff_name,transaction_type=transaction_type,transaction_date=transaction_date,business_type=business_type,amount=amount).exclude(id=iou_id).exists():
                if iou_id == 0:
                    new_place = form.save()
                    print("IOU Form saved")
                    messages.success(request, 'Record Updated Successfully')
                    url = new_place.get_absolute_url_iou()
                    return redirect(url)
                else:
                    iou = iuo_info.objects.get(pk=iou_id)
                    form = IouForm(request.POST, instance=iou)
                    form.save()
                    print("IOU Form saved")
                    messages.success(request, 'Record Updated Successfully')
                    return redirect(request.META['HTTP_REFERER'])
            else:
                print("IOU Form not saved - Duplicate found")
                messages.error(request, 'Duplicate Record Found. Please enter a unique name.')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("IOU Form not saved")
            messages.error(request, 'Record Not Saved. Please Enter All Required Fields')
            return redirect(request.META['HTTP_REFERER'])

# List iou
@login_required(login_url='login_page')
def iou_list(request):
    first_name = request.session.get('first_name')
    context = {'iou_list' : iuo_info.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/iou_list.html",context)

#Delete iou
@login_required(login_url='login_page')
def iou_delete(request,iou_id):
    iou = iuo_info.objects.get(pk=iou_id)
    iou.delete()
    return redirect('/SMS/iou_list')