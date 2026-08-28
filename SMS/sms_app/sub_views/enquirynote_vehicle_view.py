import json
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from ..forms import EnquirynotevehicleForm, EnquirynoteaddForm
from ..models import Costdescription, Enquirynotevehicle, EnquirynoteInfo, Vehicle_allotmentInfo
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages


def _get_allotted_count(enquiry_id, vehicletype_id):
    """Returns the number of vehicles allotted for a given enquiry and vehicle type."""
    return Vehicle_allotmentInfo.objects.filter(
        va_enquirynumber_id=enquiry_id,
        va_vehicletype_id=vehicletype_id
    ).count()


def _get_other_requested_qty(enquiry_id, vehicletype_id, exclude_id=None):
    """Returns total requested quantity of other vehicle detail rows for same enquiry + vehicle type."""
    qs = Enquirynotevehicle.objects.filter(
        env_enquirynumber_id=enquiry_id,
        env_vehicletype_id=vehicletype_id
    )
    if exclude_id:
        qs = qs.exclude(pk=exclude_id)
    return qs.aggregate(total=Sum('env_quantity'))['total'] or 0


def _get_total_requested(enquiry_id, vehicletype_id):
    """Returns total requested quantity for a vehicle type in an enquiry across all rows."""
    return Enquirynotevehicle.objects.filter(
        env_enquirynumber_id=enquiry_id,
        env_vehicletype_id=vehicletype_id
    ).aggregate(total=Sum('env_quantity'))['total'] or 0


def _build_vehicle_list_with_delete_flag(enquiry_id):
    """
    Returns enquirynotevehicle queryset along with a dict of {id: is_delete_allowed}.
    Rule: Delete is LOCKED only when allotted >= total_requested for that vehicle type
    (i.e., all requested vehicles are fully allotted).
    If even 1 vehicle is un-allotted, delete is allowed.
    """
    vehicle_list = Enquirynotevehicle.objects.filter(env_enquirynumber=enquiry_id)
    delete_allowed_map = {}
    for env in vehicle_list:
        total_requested = _get_total_requested(enquiry_id, env.env_vehicletype_id)
        allotted = _get_allotted_count(enquiry_id, env.env_vehicletype_id)
        delete_allowed_map[env.id] = allotted < total_requested
    return vehicle_list, delete_allowed_map


@login_required(login_url='login_page')
def enquirynotevehicle_add(request, enquirynotevehicle_id=0):
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
    enquirynotevehicle_list, delete_allowed_map = _build_vehicle_list_with_delete_flag(enquiry_num_id)
    # Build a list of (env_obj, can_delete) tuples for the template
    enquirynotevehicle_list_with_flags = [
        (env, delete_allowed_map.get(env.id, True))
        for env in enquirynotevehicle_list
    ]

    if request.method == "GET":
        if enquirynotevehicle_id == 0:
            enquiryvechicle_form = EnquirynotevehicleForm()
        else:
            try:
                enquirynotevehicle = Enquirynotevehicle.objects.get(pk=enquirynotevehicle_id)
                enquiryvechicle_form = EnquirynotevehicleForm(instance=enquirynotevehicle)
            except Enquirynotevehicle.DoesNotExist:
                messages.error(request, 'Vehicle detail record not found.')
                return redirect(request.META.get('HTTP_REFERER', f'/SMS/enquirynote_update/{enquiry_num_id}'))
        context = {
            'form': form,
            'enquiryvechicle_form': enquiryvechicle_form,
            'first_name': first_name,
            'user_id': user_id,
            'enquiry_num_id': enquiry_num_id,
            'enquirynotevehicle_list': enquirynotevehicle_list,
            'enquirynotevehicle_list_with_flags': enquirynotevehicle_list_with_flags,
        }
        return render(request, "asset_mgt_app/enquirynote_add.html", context)
    else:
        if enquirynotevehicle_id == 0:
            form = EnquirynotevehicleForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                # Auto-fill env_special_sale from env_sale if left blank or 0
                if not instance.env_special_sale or float(instance.env_special_sale) == 0:
                    if instance.env_sale and float(instance.env_sale) > 0:
                        instance.env_special_sale = float(instance.env_sale)
                instance.save()
                form.save_m2m()
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
                old_vehicletype_id = enquirynotevehicle.env_vehicletype_id
                form = EnquirynotevehicleForm(request.POST, instance=enquirynotevehicle)
                if form.is_valid():
                    updated_instance = form.save(commit=False)
                    new_vehicletype_id = updated_instance.env_vehicletype_id
                    new_quantity = updated_instance.env_quantity or 0

                    # 1. If vehicle type changed, check the old type still has enough requested qty
                    if old_vehicletype_id != new_vehicletype_id:
                        old_allotted = _get_allotted_count(enquiry_num_id, old_vehicletype_id)
                        old_other_qty = _get_other_requested_qty(enquiry_num_id, old_vehicletype_id, exclude_id=enquirynotevehicle_id)
                        if old_other_qty < old_allotted:
                            messages.error(
                                request,
                                f"Cannot change vehicle type. {old_allotted} vehicle(s) have already been allotted for the previous vehicle type."
                            )
                            return redirect(request.META.get('HTTP_REFERER', f'/SMS/enquirynote_update/{enquiry_num_id}'))

                    # 2. Check that new quantity + other rows >= already allotted for this vehicle type
                    allotted_count = _get_allotted_count(enquiry_num_id, new_vehicletype_id)
                    other_qty = _get_other_requested_qty(enquiry_num_id, new_vehicletype_id, exclude_id=enquirynotevehicle_id)

                    if (other_qty + new_quantity) < allotted_count:
                        min_allowed = max(0, allotted_count - other_qty)
                        messages.error(
                            request,
                            f"Cannot reduce quantity to {new_quantity}. Already {allotted_count} vehicle(s) have been allotted for this vehicle type (Minimum allowed: {min_allowed})."
                        )
                        return redirect(request.META.get('HTTP_REFERER', f'/SMS/enquirynote_update/{enquiry_num_id}'))

                    # Auto-fill env_special_sale from env_sale if left blank or 0
                    if not updated_instance.env_special_sale or float(updated_instance.env_special_sale) == 0:
                        if updated_instance.env_sale and float(updated_instance.env_sale) > 0:
                            updated_instance.env_special_sale = float(updated_instance.env_sale)

                    updated_instance.save()
                    form.save_m2m()
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
    context = {'costing_list': Enquirynotevehicle.objects.all(), 'first_name': first_name}
    return render(request, "asset_mgt_app/enquirynotevehicle_list.html", context)


# Delete enquirynotevehicle
@login_required(login_url='login_page')
def enquirynotevehicle_delete(request, enquirynotevehicle_id):
    try:
        enquirynotevehicle = Enquirynotevehicle.objects.get(pk=enquirynotevehicle_id)
        enquiry_id = enquirynotevehicle.env_enquirynumber_id
        vehicletype_id = enquirynotevehicle.env_vehicletype_id

        total_requested = _get_total_requested(enquiry_id, vehicletype_id)
        allotted = _get_allotted_count(enquiry_id, vehicletype_id)

        # Block deletion only when all requested vehicles are fully allotted
        if allotted >= total_requested and allotted > 0:
            vtype_name = str(enquirynotevehicle.env_vehicletype) if enquirynotevehicle.env_vehicletype else "this vehicle type"
            messages.error(
                request,
                f"Cannot delete: All {allotted} requested vehicle(s) of type '{vtype_name}' have already been allotted."
            )
            return redirect(request.META.get('HTTP_REFERER', f'/SMS/enquirynote_update/{enquiry_id}'))

        enquirynotevehicle.delete()
        messages.success(request, 'Vehicle detail deleted successfully.')
    except Enquirynotevehicle.DoesNotExist:
        messages.error(request, 'Vehicle detail record not found.')
    return redirect(request.META.get('HTTP_REFERER', '/SMS/enquirynote_list/'))



@login_required(login_url='login_page')
def enquirynotevehicle_cancel(request):
    enquiry_num_id = request.session.get('enquiry_num_id')
    return redirect('/SMS/enquirynote_update/' + str(enquiry_num_id))
