from django.contrib.auth.decorators import login_required
from ..forms import TripHighvalueForm
from ..models import TripHighvalueInfo,TripdetailInfo
from django.contrib import messages
from django.shortcuts import render, redirect



@login_required(login_url='login_page')
def trip_highvalue_add(request, high_value_id=0):
    first_name = request.session.get('first_name')
    tripdetail_id = request.session.get('ses_tripdetail_id')

    try:
        trip = TripdetailInfo.objects.get(pk=tripdetail_id)
    except TripdetailInfo.DoesNotExist:
        messages.error(request, 'Trip not found.')
        return redirect('some_fallback_url')

    enquiry = trip.tr_enquirynumber

    if request.method == "GET":
        if high_value_id == 0:
            form = TripHighvalueForm(initial={
                'thc_tripnumber': trip.id,
                'thc_enquirynumber': enquiry.id,
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
            high.save()
            if high_value_id == 0:
                messages.success(request, 'Record Saved Successfully')
            else:
                messages.success(request, 'Record Updated Successfully')
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

