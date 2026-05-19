import json
from django.contrib.auth.decorators import login_required
from ..forms import EnquirynotevehicleForm,EnquirynoteaddForm
from ..models import Costdescription,Enquirynotevehicle,EnquirynoteInfo
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages

@login_required(login_url='login_page')
def enquirynotevehicle_add(request,enquirynotevehicle_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    
    enquiry_num_id = request.session.get('enquiry_num_id')
    if not enquiry_num_id:
        messages.error(request, 'Session expired or invalid Enquiry. Please select an enquiry note first.')
        return redirect('/SMS/enquirynote_list/')
        
    try:
        enquirynote = EnquirynoteInfo.objects.get(pk=enquiry_num_id)
    except EnquirynoteInfo.DoesNotExist:
        messages.error(request, 'Enquiry not found.')
        return redirect('/SMS/enquirynote_list/')
        
    form = EnquirynoteaddForm(instance=enquirynote)
    enquirynotevehicle_list = Enquirynotevehicle.objects.filter(env_enquirynumber=enquiry_num_id)
    if request.method == "GET":
        if enquirynotevehicle_id == 0:
            enquiryvechicle_form = EnquirynotevehicleForm()
        else:
            try:
                enquirynotevehicle=Enquirynotevehicle.objects.get(pk=enquirynotevehicle_id)
                enquiryvechicle_form = EnquirynotevehicleForm(instance=enquirynotevehicle)
            except Enquirynotevehicle.DoesNotExist:
                messages.error(request, 'Vehicle detail record not found.')
                return redirect(request.META.get('HTTP_REFERER', f'/SMS/enquirynote_update/{enquiry_num_id}'))
        context={
                'form': form,
                'enquiryvechicle_form': enquiryvechicle_form,
                'first_name': first_name,
                'user_id': user_id,
                'enquiry_num_id': enquiry_num_id,
                'enquirynotevehicle_list': enquirynotevehicle_list,
                }
        return render(request, "asset_mgt_app/enquirynote_add.html", context)
    else:
        if enquirynotevehicle_id == 0:
            form = EnquirynotevehicleForm(request.POST)
            if form.is_valid():
                form.save()
                print("enquirynotevehicle Form is Valid")
                try:
                    last_id = (Enquirynotevehicle.objects.latest('id')).id
                except Enquirynotevehicle.DoesNotExist:
                    pass
                messages.success(request, 'Record Updated Successfully')
                return redirect('/SMS/enquirynotevehicle_insert/')
            else:
                print("enquirynotevehicle Form is Not Valid")
                messages.error(request, 'Record Not Updated Successfully')
                return redirect(request.META.get('HTTP_REFERER', f'/SMS/enquirynote_update/{enquiry_num_id}'))
        else:
            try:
                enquirynotevehicle = Enquirynotevehicle.objects.get(pk=enquirynotevehicle_id)
                form = EnquirynotevehicleForm(request.POST,instance=enquirynotevehicle)
                if form.is_valid():
                    form.save()
                    print("enquirynotevehicle Form is Valid")
                    messages.success(request, 'Record Updated Successfully')
                else:
                    print("enquirynotevehicle Form is Not Valid")
                    messages.error(request, 'Record Not Updated Successfully')
            except Enquirynotevehicle.DoesNotExist:
                messages.error(request, 'Vehicle detail record not found.')
            return redirect(request.META.get('HTTP_REFERER', f'/SMS/enquirynote_update/{enquiry_num_id}'))
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
    try:
        enquirynotevehicle = Enquirynotevehicle.objects.get(pk=enquirynotevehicle_id)
        enquirynotevehicle.delete()
    except Enquirynotevehicle.DoesNotExist:
        messages.error(request, 'Vehicle detail record not found.')
    return redirect(request.META.get('HTTP_REFERER', '/SMS/enquirynote_list/'))
    # return redirect('/SMS/enquirynotevehicle_list')

@login_required(login_url='login_page')
def enquirynotevehicle_cancel(request):
    enquiry_num_id = request.session.get('enquiry_num_id')
    return redirect('/SMS/enquirynote_update/' + str(enquiry_num_id))

