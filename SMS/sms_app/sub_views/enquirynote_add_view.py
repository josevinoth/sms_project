from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

from ..forms import ConsignmentdetailaddForm,EnquirynoteaddForm,EnquirynotevehicleForm
from ..models import Vehicle_allotmentInfo,User_extInfo,TripdetailInfo,ConsignmentdetailInfo,EnquirynoteInfo,Enquirynotevehicle
from django.shortcuts import render, redirect
from django.core.paginator import Paginator

from ..sub_models.customer_mod import CustomerInfo


@login_required(login_url='login_page')
def enquirynote_nav(request,enquirynote_id=0,enquirynotevehicle_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if enquirynote_id == 0:
        print("I am inside Get add Enquirynote")
        form = EnquirynoteaddForm()
        enquiryvechicle_form = EnquirynotevehicleForm()
        context = {
            'user_id': user_id,
            'form': form,
            'enquiryvechicle_form': enquiryvechicle_form,
            'first_name': first_name,
        }
    else:
        print("I am inside get edit Enuirynote")
        enquirynote = EnquirynoteInfo.objects.get(pk=enquirynote_id)
        form = EnquirynoteaddForm(instance=enquirynote)
        enquiryvechicle_form = EnquirynotevehicleForm()
        enquirynotevehicle_list = Enquirynotevehicle.objects.filter(env_enquirynumber=enquirynote_id)
        context = {
            'user_id': user_id,
            'form': form,
            'enquiryvechicle_form': enquiryvechicle_form,
            'first_name': first_name,
            'enquirynotevehicle_list': enquirynotevehicle_list,
            'enquirynote_id': enquirynote_id,
        }
    return render(request, "asset_mgt_app/enquirynote_add.html", context)
@login_required(login_url='login_page')
def enquirynote_add(request,enquirynote_id=0,enquirynotevehicle_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if enquirynote_id == 0:
            print("I am inside Get add Enquirynote")
            form = EnquirynoteaddForm()
            enquiryvechicle_form = EnquirynotevehicleForm()
            context = {
                'user_id': user_id,
                'form': form,
                'enquiryvechicle_form': enquiryvechicle_form,
                'first_name': first_name,
            }
        else:
            print("I am inside get edit Enuirynote")
            enquirynote=EnquirynoteInfo.objects.get(pk=enquirynote_id)
            enquiry_num_id = EnquirynoteInfo.objects.get(pk=enquirynote_id).id
            request.session['enquiry_num_id'] = enquiry_num_id
            tr_enqiury_id = EnquirynoteInfo.objects.get(pk=enquirynote_id).en_enquirynumber
            request.session['ses_enqiury_id'] = tr_enqiury_id
            form = EnquirynoteaddForm(instance=enquirynote)
            # enquirynotevehicle = Enquirynotevehicle.objects.get(pk=enquirynotevehicle_id)
            enquiryvechicle_form = EnquirynotevehicleForm()
            enquirynotevehicle_list=Enquirynotevehicle.objects.filter(env_enquirynumber=enquirynote_id)
            context={
                'user_id': user_id,
                'form': form,
                'enquiryvechicle_form': enquiryvechicle_form,
                'first_name': first_name,
                'enquirynotevehicle_list': enquirynotevehicle_list,
                'enquiry_num_id': enquiry_num_id,
            }
        return render(request, "asset_mgt_app/enquirynote_add.html",context)
    else:
        if enquirynote_id == 0:
            print("I am inside post add Enuirynote")
            form = EnquirynoteaddForm(request.POST)
            if form.is_valid():
                try:
                    last_id = EnquirynoteInfo.objects.latest('id').id
                    enquiry_num_next = str('EN_') + str(int(((EnquirynoteInfo.objects.get(id=last_id)).en_enquirynumber).replace('EN_', '')) + 1)
                except ObjectDoesNotExist:
                    enquiry_num_next = str('EN_') + str(1000000)
                form.save()
                print("Enquiry Main Form Saved")
                last_id = EnquirynoteInfo.objects.latest('id').id
                EnquirynoteInfo.objects.filter(id=last_id).update(en_enquirynumber=enquiry_num_next)
                messages.success(request, 'Record Updated Successfully')
                enquiry_id = EnquirynoteInfo.objects.get(en_enquirynumber=enquiry_num_next).id
                return redirect('/SMS/enquirynote_update/' + str(enquiry_id))
            else:
                print("Enquiry Main Form not Saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print("I am inside post edit Enquirynote")
            enquirynote = EnquirynoteInfo.objects.get(pk=enquirynote_id)
            form = EnquirynoteaddForm(request.POST,instance=enquirynote)
            if form.is_valid():
                form.save()
                print("Enquiry Main Form Saved")
                messages.success(request, 'Record Updated Successfully')
                return redirect(request.META['HTTP_REFERER'])
            else:
                print("Enquiry Main Form not Saved")
                messages.error(request, 'Record Not Saved.Please Enter All Required Fields')
                return redirect(request.META['HTTP_REFERER'])
            # return redirect('/SMS/enquirynote_list')

# List enquirynote
@login_required(login_url='login_page')
def enquirynote_list(request):
    global trip_dict
    print("Inside Enquiry List")

    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    user_role = User_extInfo.objects.get(user_id=user_id).emp_role
    print('user_role:', user_role)

    # Fetch paginated enquiry notes
    enquirynote_queryset = EnquirynoteInfo.objects.order_by('id')
    paginator = Paginator(enquirynote_queryset, 50)

    page_number = request.GET.get('page')
    if page_number and page_number.isdigit():
        page_number = int(page_number)
    else:
        page_number = 1  # Default to first page

    page_obj = paginator.get_page(page_number)

    # Extract only valid enquiry IDs
    enquiry_ids = [enq.id for enq in page_obj if enq.id is not None and isinstance(enq.id, int)]

    consignment_data = ConsignmentdetailInfo.objects.filter(co_enquirynumber__in=enquiry_ids)
    # trip_data = TripdetailInfo.objects.filter(tr_enquirynumber_id__in=enquiry_ids)
    # print(trip_data)
    vehicle_data = Vehicle_allotmentInfo.objects.filter(va_enquirynumber__in=enquiry_ids).values_list('va_enquirynumber', 'va_vehiclenumber__vm_registrationnumber', 'va_vehiclenumber_mkt')

    # Convert vehicle data into a dictionary for easy lookup
    vehicle_dict = {}

    for enq_id, reg_num, mkt_num in vehicle_data:
        # Filter out None values
        valid_numbers = [num for num in (reg_num, mkt_num) if num]

        if valid_numbers:  # Only add to dict if there's at least one valid vehicle number
            vehicle_dict.setdefault(enq_id, []).extend(valid_numbers)
        else:
            vehicle_dict.setdefault(enq_id, []).append("No Vehicle")  # Add fallback

        trip_data = TripdetailInfo.objects.filter(tr_enquirynumber_id__in=enquiry_ids).values_list('tr_enquirynumber','tr_tripnumber','tc_financestatus__status','tc_financestatus')

        # Convert trip data into a dictionary for easy lookup
        trip_dict = {}

        for enq_id, trip_num, trip_status,trip_status_id in trip_data:
            if trip_num:
                trip_dict.setdefault(enq_id, []).append((trip_num, trip_status,trip_status_id))
            else:
                trip_dict.setdefault(enq_id, []).append(("No Trip", "Not Applicable"))

    # Organize the data for the template
    enquiry_data = []
    trip_dict = {}
    for enquiry in page_obj:
        enquiry_data.append({
            'enquiry': enquiry,
            'consignments': consignment_data.filter(co_enquirynumber=enquiry),
            'trips': trip_dict.get(enquiry.id, []),
            'vehicles': vehicle_dict.get(enquiry.id, []),  # Use dictionary lookup
        })

    context = {
        'page_obj': page_obj,
        'first_name': first_name,
        'role': user_role,
        'enquiry_data': enquiry_data,
    }
    return render(request, "asset_mgt_app/enquirynote_list.html", context)


# Connect to consignemnt Note
@login_required(login_url='login_page')
def consignment_note_connect(request,enquirynote_id):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    enquiry_num=EnquirynoteInfo.objects.get(pk=enquirynote_id).en_enquirynumber
    request.session['ses_enquiry_note']=enquiry_num
    try:
        consignment_num=ConsignmentdetailInfo.objects.get(co_enquirynumber=enquiry_num).co_consignmentnumber
    except ObjectDoesNotExist:
        consignment_num=None

    if request.method == "GET":
        if consignment_num==None:
            print("I am inside Get add consignmentdetails")
            con_det_form = ConsignmentdetailaddForm()
        else:
            print("I am inside get edit consignmentdetails")
            try:
                consignmentdetail = ConsignmentdetailInfo.objects.get(co_consignmentnumber=consignment_num)
            except ObjectDoesNotExist:
                consignmentdetail = None
            con_det_form = ConsignmentdetailaddForm(instance=consignmentdetail)
        context = {
            'first_name': first_name,
            'con_det_form': con_det_form,
            'enquiry_num': enquiry_num,
            'user_id': user_id,
            'consignmentdetail_list': ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num),
        }
        return render(request, "asset_mgt_app/consignmentdetail_add.html", context)
    else:
        if consignment_num==None:
            print("I am inside post add consignmentdetails")
            con_det_form = ConsignmentdetailaddForm(request.POST)
        else:
            print("I am inside post edit consignmentdetails")
            try:
                consignmentdetail = ConsignmentdetailInfo.objects.get(co_consignmentnumber=consignment_num)
            except ObjectDoesNotExist:
                consignmentdetail = None
            con_det_form = ConsignmentdetailaddForm(request.POST, instance=consignmentdetail)
        if con_det_form.is_valid():
            con_det_form.save()
            print("con_det_form Main Form is Valid")
        else:
            print("con_det_form Form is not Valid")

        return redirect('/SMS/enquirynote_list')
#Delete enquirynote
@login_required(login_url='login_page')
def enquirynote_delete(request,enquirynote_id):
    enquiry_num = EnquirynoteInfo.objects.get(pk=enquirynote_id).en_enquirynumber
    enquiry_num_id = EnquirynoteInfo.objects.get(pk=enquirynote_id).id
    consignment_num_list = list(ConsignmentdetailInfo.objects.filter(co_enquirynumber=enquiry_num_id).values_list('co_consignmentnumber',flat=True))
    tripdetails_list=list(TripdetailInfo.objects.filter(tr_enquirynumber=enquiry_num_id).values_list('tr_tripnumber',flat=True))
    for i in consignment_num_list:
        consignment_note=ConsignmentdetailInfo.objects.get(co_consignmentnumber=i)
        consignment_note.delete()
    for j in tripdetails_list:
        tripdetails_note=TripdetailInfo.objects.get(tr_tripnumber=j)
        tripdetails_note.delete()
    enquirynote = EnquirynoteInfo.objects.get(pk=enquirynote_id)
    enquirynote.delete()
    return redirect('/SMS/enquirynote_list')

@login_required(login_url='login_page')
def get_customer_details(request):
    customer_id = request.GET.get('customer_id')  # Get customer ID from AJAX request
    try:
        customer = CustomerInfo.objects.get(id=customer_id)
        data = {
            'customer_contact': customer.cu_contactno,
            'customer_email': customer.cu_email,
        }
        return JsonResponse(data)  # Return JSON response
    except CustomerInfo.DoesNotExist:
        return JsonResponse({'error': 'Customer not found'}, status=404)
