from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from ..forms import IouForm
from ..models import User,iou_info
from django.shortcuts import render, redirect

@login_required(login_url='login_page')
def iou_add(request,iou_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if iou_id == 0:
            form = IouForm()
        else:
            iou = iou_info.objects.get(pk=iou_id)
            form = IouForm(instance=iou)
        return render(request, "asset_mgt_app/iou_add.html", {'form': form, 'first_name': first_name,'user_id':user_id,})
    else:
        form = IouForm(request.POST)

        if form.is_valid():
            # Check for duplicates before saving
            staff_id = form.cleaned_data['staff_id']
            staff_name = form.cleaned_data['staff_name']
            transaction_type = form.cleaned_data['transaction_type']
            transaction_date = form.cleaned_data['transaction_date']
            business_type = form.cleaned_data['business_type']
            amount = form.cleaned_data['amount']
            if not iou_info.objects.filter(staff_id=staff_id,staff_name=staff_name,transaction_type=transaction_type,transaction_date=transaction_date,business_type=business_type,amount=amount).exclude(id=iou_id).exists():
                if iou_id == 0:
                    new_place = form.save()
                    try:
                        last_id = (iou_info.objects.values_list('id', flat=True)).last()
                        ran_number = 100000 + last_id
                    except ObjectDoesNotExist:
                        ran_number = 100000
                    req_num_next = str('IOU_') + str(ran_number)
                    print("IOU Form is Valid")
                    last_id = (iou_info.objects.values_list('id', flat=True)).last()
                    iou_info.objects.filter(id=last_id).update(iou_number=req_num_next)
                    print("IOU Form saved")
                    messages.success(request, 'Record Updated Successfully')
                    url = new_place.get_absolute_url_iou()
                    return redirect(url)
                else:
                    iou = iou_info.objects.get(pk=iou_id)
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
    context = {'iou_list' : iou_info.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/iou_list.html",context)

#Delete iou
@login_required(login_url='login_page')
def iou_delete(request,iou_id):
    iou = iou_info.objects.get(pk=iou_id)
    iou.delete()
    return redirect('/SMS/iou_list')
@login_required(login_url='login_page')
def get_full_name_iou(request):
    username = request.GET.get('username', None)
    print('username',username)
    if username:
        user = User.objects.get(username=username)
        full_name = user.get_full_name()
        return JsonResponse({'full_name': full_name})

    return JsonResponse({'error': 'Username not provided'}, status=400)