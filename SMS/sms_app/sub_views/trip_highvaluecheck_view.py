from datetime import date, datetime
from django.contrib.auth.decorators import login_required
from ..forms import TripHighvalueForm
from ..models import TripHighvalueInfo, TripdetailInfo, VehiclemasterInfo
from django.contrib import messages
from django.shortcuts import render, redirect


def parse_to_date(val):
    if not val:
        return None
    if isinstance(val, date):
        return val
    if hasattr(val, 'date'):
        return val.date()
    if isinstance(val, str):
        val_str = val.strip()
        for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S'):
            try:
                return datetime.strptime(val_str, fmt).date()
            except ValueError:
                pass
    return None


@login_required(login_url='login_page')
def trip_highvalue_add(request, high_value_id=0):
    first_name = request.session.get('first_name')
    tripdetail_id = request.session.get('ses_tripdetail_id')

    try:
        trip = TripdetailInfo.objects.get(pk=tripdetail_id)
    except TripdetailInfo.DoesNotExist:
        messages.error(request, 'Trip not found.')
        return redirect('/SMS/tripdetail_list')

    enquiry = trip.tr_enquirynumber
    today = date.today()

    vehicle_obj = None
    vehicle_docs_info = {
        'rc_status': False,
        'rc_expiry': None,
        'rc_attach': None,
        'insurance_status': False,
        'insurance_expiry': None,
        'insurance_attach': None,
        'permit_status': False,
        'permit_expiry': None,
        'permit_attach': None,
        'ownership': 'N/A'
    }

    if trip.tr_vehiclenumber:
        vehicle_obj = VehiclemasterInfo.objects.filter(vm_registrationnumber__iexact=trip.tr_vehiclenumber.strip()).first()

    if vehicle_obj:
        if vehicle_obj.vm_ownership:
            vehicle_docs_info['ownership'] = str(vehicle_obj.vm_ownership)

        # Insurance
        ins_exp = vehicle_obj.vm_policyexpirydate
        ins_exp_date = parse_to_date(ins_exp)
        vehicle_docs_info['insurance_expiry'] = ins_exp_date or ins_exp
        if vehicle_obj.vm_insurance_attach:
            try:
                vehicle_docs_info['insurance_attach'] = vehicle_obj.vm_insurance_attach.url
            except Exception:
                vehicle_docs_info['insurance_attach'] = None
        if ins_exp_date and ins_exp_date >= today:
            vehicle_docs_info['insurance_status'] = True

        # Permit
        permit_exp = vehicle_obj.vm_permitexpirydate
        permit_exp_date = parse_to_date(permit_exp)
        vehicle_docs_info['permit_expiry'] = permit_exp_date or permit_exp
        if vehicle_obj.vm_permit_attach:
            try:
                vehicle_docs_info['permit_attach'] = vehicle_obj.vm_permit_attach.url
            except Exception:
                vehicle_docs_info['permit_attach'] = None
        if permit_exp_date and permit_exp_date >= today:
            vehicle_docs_info['permit_status'] = True

        # RC / FC
        fc_exp = vehicle_obj.vm_fcexpirydate or vehicle_obj.vm_registrationdate
        fc_exp_date = parse_to_date(fc_exp)
        vehicle_docs_info['rc_expiry'] = fc_exp_date or fc_exp
        if vehicle_obj.vm_rc_attach:
            try:
                vehicle_docs_info['rc_attach'] = vehicle_obj.vm_rc_attach.url
            except Exception:
                vehicle_docs_info['rc_attach'] = None
        if (fc_exp_date and fc_exp_date >= today) or vehicle_obj.vm_rc_attach:
            vehicle_docs_info['rc_status'] = True

    if request.method == "GET":
        if high_value_id == 0:
            form = TripHighvalueForm(initial={
                'thc_tripnumber': trip.id,
                'thc_enquirynumber': enquiry.id,
                'thc_vehicleRC': 1 if vehicle_docs_info['rc_status'] else 2,
                'thc_vehicle_insurance': 1 if vehicle_docs_info['insurance_status'] else 2,
                'thc_goodspermit': 1 if vehicle_docs_info['permit_status'] else 2,
                'thc_vehiclenumber': trip.tr_vehiclenumber or '',
            })
        else:
            high = TripHighvalueInfo.objects.get(pk=high_value_id)
            form = TripHighvalueForm(instance=high)

        context = {
            'form': form,
            'first_name': first_name,
            'tripdetail_id': tripdetail_id,
            'trip': trip,
            'enquiry': enquiry,
            'vehicle_obj': vehicle_obj,
            'vehicle_docs_info': vehicle_docs_info,
        }
        return render(request, "asset_mgt_app/trip_highvaluecheck_add.html", context)

    else:
        if high_value_id == 0:
            form = TripHighvalueForm(request.POST)
        else:
            high = TripHighvalueInfo.objects.get(pk=high_value_id)
            form = TripHighvalueForm(request.POST, instance=high)

        if form.is_valid():
            high = form.save(commit=False)
            high.thc_tripnumber = trip
            high.thc_enquirynumber = enquiry

            # Check if any inspection / document item is set to 'No' (2)
            check_fields = [
                high.thc_vehicleRC_id, high.thc_vehicle_insurance_id, high.thc_goodspermit_id,
                high.thc_outside_undercarriage_id, high.thc_inoutside_doors_id, high.thc_rightinnerwall_id,
                high.thc_leftinnerwall_id, high.thc_frontinnerwall_id, high.thc_roof_id, high.thc_floorinside_id,
                high.thc_gpsfit_id, high.thc_simtracking_id, high.thc_smartlock_id, high.thc_smartlockbaterry_id,
                high.thc_bottle_otlseal_id, high.thc_commercialinvoice_id, high.thc_packinglist_id,
                high.thc_eipl_coc_id, high.thc_consignmentnote_id, high.thc_ewaybill_id
            ]

            has_no_item = any(val == 2 for val in check_fields if val is not None)

            if has_no_item and high.thc_approval_status_id == 1:
                high.thc_approval_status_id = 2
                messages.warning(request, '⚠️ Approval Blocked: High Value Checklist cannot be approved because one or more items are set to "No". Record saved as Not Approved.')
            elif high_value_id == 0:
                messages.success(request, 'Record Saved Successfully')
            else:
                messages.success(request, 'Record Updated Successfully')

            high.save()
        else:
            messages.error(request, 'Error: Please correct the errors below.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")

        return redirect(f'/SMS/tripdetail_update/{tripdetail_id}')
        #return redirect(request.META['HTTP_REFERER'])

@login_required(login_url='login_page')
def trip_highvalue_list(request):
    first_name = request.session.get('first_name')
    high_list = TripHighvalueInfo.objects.filter(thc_approval_status=2)
    context = {'high_list': high_list, 'first_name': first_name}
    return render(request, "asset_mgt_app/trip_highvaluecheck_list.html", context)


@login_required(login_url='login_page')
def trip_highvalue_delete(request,high_value_id):
    high = TripHighvalueInfo.objects.get(pk=high_value_id)
    high.delete()
    return redirect('/SMS/high_value_list')

@login_required(login_url='login_page')
def trip_highvalue_cancel(request, tripdetail_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    tripdetail_id = request.session.get('ses_tripdetail_id')
    return redirect(f'/SMS/tripdetail_update/{tripdetail_id}')

