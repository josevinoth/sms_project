import json
from django.contrib.auth.decorators import login_required
from ..forms import EnquirynotevehicleForm
from ..models import Costdescription,Enquirynotevehicle
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

@login_required(login_url='login_page')
def enquirynotevehicle_add(request,enquirynotevehicle_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    enquiry_num_id = request.session['enquiry_num_id']
    if request.method == "GET":
        if enquirynotevehicle_id == 0:
            form = EnquirynotevehicleForm()
        else:
            enquirynotevehicle=Enquirynotevehicle.objects.get(pk=enquirynotevehicle_id)
            form = EnquirynotevehicleForm(instance=enquirynotevehicle)
        context={
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'enquiry_num_id': enquiry_num_id,
                }
        return render(request, "asset_mgt_app/enquirynotevehicle_add.html", context)
    else:
        if enquirynotevehicle_id == 0:
            form = EnquirynotevehicleForm(request.POST)
            if form.is_valid():
                form.save()
                print("enquirynotevehicle Form is Valid")
                last_id = (Enquirynotevehicle.objects.latest('id')).id
                messages.success(request, 'Record Updated Successfully')
                return redirect('/SMS/enquirynotevehicle_update/'+str(last_id))
            else:
                print("enquirynotevehicle Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
        else:
            enquirynotevehicle = Enquirynotevehicle.objects.get(pk=enquirynotevehicle_id)
            form = EnquirynotevehicleForm(request.POST,instance=enquirynotevehicle)
            if form.is_valid():
                form.save()
                print("enquirynotevehicle Form is Valid")
                messages.success(request, 'Record Updated Successfully')
            else:
                print("enquirynotevehicle Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
            return redirect(request.META['HTTP_REFERER'])
        # return redirect('/SMS/requirements_list')

# List enquirynotevehicle
@login_required(login_url='login_page')
def enquirynotevehicle_list(request):
    first_name = request.session.get('first_name')
    context = {'costing_list' : Enquirynotevehicle.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/enquirynotevehicle_list.html",context)

#Delete enquirynotevehicle
@login_required(login_url='login_page')
def enquirynotevehicle_delete(request,enquirynotevehicle_id):
    enquirynotevehicle = Enquirynotevehicle.objects.get(pk=enquirynotevehicle_id)
    enquirynotevehicle.delete()
    return redirect('/SMS/enquirynotevehicle_list')

@login_required(login_url='login_page')
def enquirynotevehicle_cancel(request):
    enquiry_num_id = request.session.get('enquiry_num_id')
    return redirect('/SMS/enquirynote_update/' + str(enquiry_num_id))

