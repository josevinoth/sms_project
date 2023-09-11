from django.contrib.auth.decorators import login_required
from ..forms import TripclosurefilesForm,TripclosureaddForm
from ..models import User_extInfo,Trip_closure_files_Info,EnquirynoteInfo,TripdetailInfo
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required(login_url='login_page')
def tripclosure_nav(request,tripclosure_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    print("I am inside Get add tripclosure")
    tripclosure_form = TripclosureaddForm(request.POST)
    tripclosurefiles_form = TripclosurefilesForm(request.POST,request.FILES)
    enquiry_num = EnquirynoteInfo.objects.get(pk=tripclosure_id).en_enquirynumber
    enquiry_num_id = EnquirynoteInfo.objects.get(pk=tripclosure_id).id
    request.session['ses_enqiury_id'] = enquiry_num
    tripclosure_list=TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num_id)
    context = {
        'first_name': first_name,
        'user_id': user_id,
        'tripclosure_form': tripclosure_form,
        'tripclosurefiles_form': tripclosurefiles_form,
        'enquiry_num': enquiry_num,
        'tripclosure_list': tripclosure_list,
    }
    if tripclosure_form.is_valid():
        tripclosure_form.save()
        print("Main Form is Valid")
        tripclosure_list = TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num).values_list('tr_tripnumber', flat=True)
        EnquirynoteInfo.objects.filter(en_enquirynumber=enquiry_num).update(en_tripclosure=list(tripclosure_list))
        messages.success(request, 'Record Updated Successfully')
    else:
        print("Main Form is not Valid")
        messages.error(request, 'Record Not Saved.Please Enter All Required Fields')

    if tripclosurefiles_form.is_valid():
        tripclosurefiles_form.save()
        messages.success(request, 'Record Updated Successfully')
        print("Trip Closure files Form Saved")
    else:
        messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
        print("Trip Closure files Form not Saved")
    return render(request, "asset_mgt_app/tripclosure_add.html", context)

@login_required(login_url='login_page')
def tripclosure_add(request,tripclosure_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    role = User_extInfo.objects.get(user=user_id).emp_role
    if request.method == "GET":
        print("I am inside Get edit Trip Closure")
        if tripclosure_id == 0:
            enquiry_num = TripdetailInfo.objects.get(pk=tripclosure_id).tr_enquirynumber
            print(enquiry_num)
            enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
            consignment_num = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).en_consignmentdetails
            print("I am inside Get add Tripclosure")
            tripclosure_form = TripclosureaddForm()
            tripclosurefiles_form = TripclosurefilesForm()
            context = {
                'tripclosure_form': tripclosure_form,
                'tripclosurefiles_form': tripclosurefiles_form,
                'first_name': first_name,
                'enquiry_num': enquiry_num,
            }
        else:
            trip_num = TripdetailInfo.objects.get(pk=tripclosure_id).tr_tripnumber
            print("Inside Trip closure edit")
            print(trip_num)
            enquiry_num = TripdetailInfo.objects.get(pk=tripclosure_id).tr_enquirynumber
            print(enquiry_num)
            enquiry_num_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).id
            consignment_num = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num).en_consignmentdetails
            tripclosure = TripdetailInfo.objects.get(tr_tripnumber=trip_num)
            tripclosure_form = TripclosureaddForm(instance=tripclosure)
            tripclosure_files = Trip_closure_files_Info.objects.get(tcf_tripnumber=trip_num)
            tripclosurefiles_form = TripclosurefilesForm(instance=tripclosure_files)
            context = {
                'tripclosure_form': tripclosure_form,
                'tripclosurefiles_form': tripclosurefiles_form,
                'first_name': first_name,
                'enquiry_num': enquiry_num,
                'consignment_num': consignment_num,
                'user_id': user_id,
                'role': role,
                'tripclosure_list': TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num),
            }
        return render(request, "asset_mgt_app/tripclosure_add.html", context)
    else:
        if tripclosure_id == 0:
            print("Inside Trip closure post add")
            tripclosure_form = TripclosureaddForm(request.POST)
            tripclosurefiles_form = TripclosurefilesForm(request.POST,request.FILES)
        else:
            print("Inside Trip closure post edit")
            trip_num = TripdetailInfo.objects.get(pk=tripclosure_id).tr_tripnumber
            tripclosure = TripdetailInfo.objects.get(tr_tripnumber=trip_num)
            tripclosure_form = TripclosureaddForm(request.POST,instance=tripclosure)
            tripclosure_files = Trip_closure_files_Info.objects.get(tcf_tripnumber=trip_num)
            tripclosurefiles_form = TripclosurefilesForm(request.POST,request.FILES,instance=tripclosure_files)

    if tripclosure_form.is_valid():
        tripclosure_form.save()
        print("Trip Closure Main Form Saved")
    else:
        print("Trip Closure Main Form not Saved")

    if tripclosurefiles_form.is_valid():
        tripclosurefiles_form.save()
        print("Trip Closure files Form Saved")
        messages.success(request, 'Record Updated Successfully')
    else:
        print("Trip Closure files Form not Saved")
        messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
    return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/enquirynote_list')

# List tripclosure
@login_required(login_url='login_page')
def tripclosure_list(request):
    first_name = request.session.get('first_name')
    context = {'tripclosure_list' : TripdetailInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/tripclosure_list.html",context)

#Delete tripclosure
@login_required(login_url='login_page')
def tripclosure_delete(request,tripclosure_id):
    tripclosure = TripdetailInfo.objects.get(pk=tripclosure_id)
    tripclosure.delete()
    return redirect(request.META['HTTP_REFERER'])
    # return redirect('/SMS/tripclosure_list')
