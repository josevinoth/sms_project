import json
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Sum

from ..forms import PrimeEnquirynoteaddForm
from ..models import PrimeEnquirynoteInfo, VehicletypeInfo, Tr_triptype_Info
from ..sub_forms.prime_enquiry_vehicle_form import PrimeEnquiryVehicleForm
from ..sub_models.prime_enquiry_vehicle_mod import PrimeEnquiryVehicle
from .general_utils import get_financial_year, generate_next_number, get_branch_code, get_session_branch_id


@login_required(login_url='login_page')
def prime_enquiry_vehicle_add(request, pev_id=0, enquiry_num_id=0):
    """
    Handles the Add / Edit of a Prime business-type vehicle detail row.
    Mirrors the logic in enquirynotevehicle_add.
    """
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    enquirynote = None
    prime_vehicle_list = []

    if enquiry_num_id == 0:
        # Create flow
        form = PrimeEnquirynoteaddForm(initial={'en_assignedto': user_id, 'en_business_type': 'Prime'})
    else:
        # Update flow
        try:
            enquirynote = PrimeEnquirynoteInfo.objects.get(pk=enquiry_num_id)
        except PrimeEnquirynoteInfo.DoesNotExist:
            messages.error(request, 'Enquiry not found.')
            return redirect('/SMS/prime_enquiry_vehicle_insert/')

        form = PrimeEnquirynoteaddForm(instance=enquirynote)
        prime_vehicle_list = PrimeEnquiryVehicle.objects.filter(pev_enquirynumber=enquiry_num_id)

        # ---- Auto-generate ENP_ booking number immediately if not already set ----
        current_number = enquirynote.pen_enquirynumber or ''
        if '_ENP_' not in current_number:
            branch_id = get_session_branch_id(request)
            branch_code = get_branch_code(branch_id)
            current_fy = get_financial_year()
            prefix = f"{current_fy}_{branch_code}_ENP_"
            new_booking_num = generate_next_number(PrimeEnquirynoteInfo, 'pen_enquirynumber', prefix, 6)
            enquirynote.pen_enquirynumber = new_booking_num
            # Refresh the form to show the new booking number in the UI, but DO NOT save to DB yet!
            form = PrimeEnquirynoteaddForm(instance=enquirynote)

    if request.method == 'GET':
        if pev_id == 0:
            prime_vehicle_form = PrimeEnquiryVehicleForm()
        else:
            try:
                pev = PrimeEnquiryVehicle.objects.get(pk=pev_id)
                prime_vehicle_form = PrimeEnquiryVehicleForm(instance=pev)
            except PrimeEnquiryVehicle.DoesNotExist:
                messages.error(request, 'Vehicle detail record not found.')
                return redirect(
                    request.META.get('HTTP_REFERER', f'/SMS/prime_enquiry_update/{enquiry_num_id}')
                )
        # Clear the datetime fields so they appear blank instead of auto-filled
        form.initial['pen_pickupdatetime'] = None
        

    else:  # POST
        if 'save_enquiry' in request.POST:
            post_data = request.POST.copy()
            
            # The database has a NOT NULL constraint on pen_trip_type.
            # If it's missing (because it's hidden in the Prime UI), inject a valid default.
            if not post_data.get('en_trip_type'):
                first_trip_type = Tr_triptype_Info.objects.first()
                if first_trip_type:
                    post_data['pen_trip_type'] = first_trip_type.id
                    
            form = PrimeEnquirynoteaddForm(post_data, instance=enquirynote)
            
            # Disable requirement for other hidden fields that might be empty
            form.fields['pen_fromlocaion'].required = False
            form.fields['pen_tolocation'].required = False
            form.fields['pen_status'].required = False
            form.fields['pen_assignedto'].required = False
            
            if form.is_valid():
                instance = form.save(commit=False)
                instance.pen_updated_by_id = user_id

                # Auto-generate booking number with ENP_ prefix if not already set
                if not instance.pen_enquirynumber or not instance.pen_enquirynumber.startswith(
                    get_financial_year()
                ) or '_ENP_' not in (instance.pen_enquirynumber or ''):
                    branch_id = get_session_branch_id(request)
                    branch_code = get_branch_code(branch_id)
                    current_fy = get_financial_year()
                    prefix = f"{current_fy}_{branch_code}_ENP_"
                    booking_num = generate_next_number(PrimeEnquirynoteInfo, 'pen_enquirynumber', prefix, 6)
                    instance.pen_enquirynumber = booking_num

                instance.save()
                messages.success(request, 'Prime Booking Note updated successfully.')
                return redirect(f'/SMS/prime_enquiry_update/{instance.id}/')
            else:
                messages.error(request, f'Failed to update Prime Booking Note. Errors: {form.errors.as_text()}')
                prime_vehicle_form = PrimeEnquiryVehicleForm()
            
        else:
            if pev_id == 0:
                prime_vehicle_form = PrimeEnquiryVehicleForm(request.POST)
                if prime_vehicle_form.is_valid():
                    pev_instance = prime_vehicle_form.save(commit=False)
                    parent_enquiry = pev_instance.pev_enquirynumber
                    
                    req_qty = parent_enquiry.pen_no_of_vehicles or 0
                    existing_qty_sum = PrimeEnquiryVehicle.objects.filter(
                        pev_enquirynumber=parent_enquiry
                    ).aggregate(sum=Sum('pev_quantity'))['sum'] or 0
                    new_qty = pev_instance.pev_quantity or 0
                    
                    if existing_qty_sum + new_qty > req_qty:
                        messages.error(request, f'Total vehicle details quantity ({existing_qty_sum + new_qty}) cannot exceed the number of vehicles requested ({req_qty}) on the Booking Note.')
                        return redirect(f'/SMS/prime_enquiry_update/{parent_enquiry.id}/')
                        
                    pev_instance.save()
                    messages.success(request, 'Vehicle record saved successfully.')
                    return redirect(f'/SMS/prime_enquiry_update/{parent_enquiry.id}/')
                else:
                    messages.error(request, 'Vehicle record not saved. Please check the fields.')
            else:
                try:
                    pev = PrimeEnquiryVehicle.objects.get(pk=pev_id)
                    prime_vehicle_form = PrimeEnquiryVehicleForm(request.POST, instance=pev)
                    if prime_vehicle_form.is_valid():
                        pev_instance = prime_vehicle_form.save(commit=False)
                        parent_enquiry = pev_instance.pev_enquirynumber
                        
                        req_qty = parent_enquiry.pen_no_of_vehicles or 0
                        existing_qty_sum = PrimeEnquiryVehicle.objects.filter(
                            pev_enquirynumber=parent_enquiry
                        ).exclude(pk=pev_id).aggregate(sum=Sum('pev_quantity'))['sum'] or 0
                        new_qty = pev_instance.pev_quantity or 0
                        
                        if existing_qty_sum + new_qty > req_qty:
                            messages.error(request, f'Total vehicle details quantity ({existing_qty_sum + new_qty}) cannot exceed the number of vehicles requested ({req_qty}) on the Booking Note.')
                            return redirect(f'/SMS/prime_enquiry_update/{parent_enquiry.id}/')
                            
                        pev_instance.save()
                        messages.success(request, 'Vehicle record updated successfully.')
                        return redirect(f'/SMS/prime_enquiry_update/{parent_enquiry.id}/')
                    else:
                        messages.error(request, 'Vehicle record not updated.')
                except PrimeEnquiryVehicle.DoesNotExist:
                    messages.error(request, 'Vehicle detail record not found.')
                    return redirect(request.META.get('HTTP_REFERER', f'/SMS/prime_enquiry_update/{enquiry_num_id}'))

    # Common render block for GET and failed POST
    context = {
        'form': form,
        'prime_vehicle_form': prime_vehicle_form,
        'first_name': first_name,
        'user_id': user_id,
        'enquiry_num_id': enquiry_num_id,
        'prime_vehicle_list': prime_vehicle_list,
        'booking_number': enquirynote.pen_enquirynumber if enquirynote else '',
        'vehicle_type_list': VehicletypeInfo.objects.all().order_by('vt_vehicletype')
    }
    return render(request, 'asset_mgt_app/prime_enquiry_note_add.html', context)


@login_required(login_url='login_page')
def prime_enquiry_vehicle_list(request):
    """Simple list view for all Prime vehicle rows (utility / admin use)."""
    first_name = request.session.get('first_name')
    context = {
        'prime_vehicle_list': PrimeEnquiryVehicle.objects.all(),
        'first_name': first_name,
    }
    return render(request, 'asset_mgt_app/prime_enquiry_vehicle_list.html', context)


@login_required(login_url='login_page')
def prime_enquiry_booking_list(request):
    """
    Lists all Prime Enquiry Bookings (ENP_ entries).
    User picks a booking from here and is taken to its update/detail page.
    """
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    enquiry_number = request.GET.get('enquiry_number', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    queryset = PrimeEnquirynoteInfo.objects.filter(
        pen_enquirynumber__icontains='_ENP_'
    ).select_related('pen_customername', 'pen_status').prefetch_related(
        'primevehicleallotmentinfo_set__pva_vehiclesource', 
        'primevehicleallotmentinfo_set__pva_vehiclenumber'
    ).order_by('-pen_created_at', '-id')

    if enquiry_number:
        queryset = queryset.filter(pen_enquirynumber__icontains=enquiry_number)

    if date_from:
        queryset = queryset.filter(pen_created_at__date__gte=date_from)

    if date_to:
        queryset = queryset.filter(pen_created_at__date__lte=date_to)

    return render(request, 'asset_mgt_app/prime_enquiry_booking_list.html', {
        'first_name': first_name,
        'user_id': user_id,
        'enquiry_list': queryset,
    })


@login_required(login_url='login_page')
def prime_enquiry_vehicle_delete(request, pev_id):
    """Delete a single Prime vehicle detail row."""
    enquiry_num_id = request.session.get('enquiry_num_id')
    try:
        pev = PrimeEnquiryVehicle.objects.get(pk=pev_id)
        pev.delete()
    except PrimeEnquiryVehicle.DoesNotExist:
        messages.error(request, 'Vehicle detail record not found.')
    return redirect(
        request.META.get('HTTP_REFERER', '/SMS/enquirynote_list/')
    )


@login_required(login_url='login_page')
def prime_enquiry_vehicle_cancel(request):
    """Cancel and return to the enquiry update page."""
    enquiry_num_id = request.session.get('enquiry_num_id')
    return redirect('/SMS/prime_enquiry_update/' + str(enquiry_num_id))
