from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect
from ..forms import DriverSettlementForm
from ..models import driver_settlement_info, User
from ..sub_models.tripdetail_mod import TripdetailInfo


@login_required(login_url='login_page')
def driver_settlement_add(request, ds_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    if request.method == "GET":
        if ds_id == 0:
            form = DriverSettlementForm()
        else:
            ds = driver_settlement_info.objects.get(pk=ds_id)
            form = DriverSettlementForm(instance=ds)
        return render(request, "asset_mgt_app/driver_settlement_add.html", {
            'form': form,
            'first_name': first_name,
            'user_id': user_id,
        })

    else:
        form = DriverSettlementForm(request.POST)
        if form.is_valid():
            staff_id = form.cleaned_data['staff_id']
            staff_name = form.cleaned_data['staff_name']
            transaction_type = form.cleaned_data['transaction_type']
            transaction_date = form.cleaned_data['transaction_date']
            business_type = form.cleaned_data['business_type']
            amount = form.cleaned_data['amount']

            # Duplicate check
            if not driver_settlement_info.objects.filter(
                staff_id=staff_id,
                staff_name=staff_name,
                transaction_type=transaction_type,
                transaction_date=transaction_date,
                business_type=business_type,
                amount=amount
            ).exclude(id=ds_id).exists():
                if ds_id == 0:
                    new_record = form.save()
                    try:
                        last_id = driver_settlement_info.objects.values_list('id', flat=True).last()
                        ran_number = 200000 + last_id
                    except ObjectDoesNotExist:
                        ran_number = 200000
                    ds_num = f"DS_{ran_number}"
                    driver_settlement_info.objects.filter(id=new_record.id).update(ds_number=ds_num)
                    messages.success(request, 'Record Saved Successfully')
                    return redirect(new_record.get_absolute_url_ds())
                else:
                    ds = driver_settlement_info.objects.get(pk=ds_id)
                    form = DriverSettlementForm(request.POST, instance=ds)
                    form.save()
                    messages.success(request, 'Record Updated Successfully')
                    return redirect(request.META['HTTP_REFERER'])
            else:
                messages.error(request, 'Duplicate Record Found.')
                return redirect(request.META['HTTP_REFERER'])
        else:
            print(form.errors)
            messages.error(request, 'Record Not Saved. Please Fill All Required Fields')
            return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='login_page')
def driver_settlement_list(request):
    first_name = request.session.get('first_name')

    driver_settlements = driver_settlement_info.objects.all().order_by('-id')
    driver_ids = driver_settlement_info.objects.values_list('staff_id', flat=True).distinct()

    driver_id = request.GET.get('driver_id')
    if driver_id:
        driver_settlements = driver_settlements.filter(staff_id=driver_id)

    total_advance = driver_settlements.aggregate(total_advance=Sum('amount'))['total_advance'] or 0
    total_balance = driver_settlements.aggregate(total_balance=Sum('balance'))['total_balance'] or 0

    context = {
        'driver_settlement_list': driver_settlements,
        'driver_ids': driver_ids,
        'selected_driver': driver_id,
        'total_advance': total_advance,
        'total_balance': total_balance,
        'first_name': first_name,
    }
    return render(request, "asset_mgt_app/driver_settlement_list.html", context)


@login_required(login_url='login_page')
def driver_settlement_delete(request, ds_id):
    ds = driver_settlement_info.objects.get(pk=ds_id)
    ds.delete()
    return redirect('/SMS/driver_settlement_list')


@login_required(login_url='login_page')
def get_full_name_driver(request):
    username = request.GET.get('username', None)
    if username:
        user = User.objects.get(username=username)
        return JsonResponse({'full_name': user.get_full_name()})
    return JsonResponse({'error': 'Username not provided'}, status=400)


# ✅ UPDATED VIEW — full breakdown for modal
@login_required(login_url='login_page')
def get_trip_totalcost(request):
    trip_id = request.GET.get('trip_id')
    try:
        trip = TripdetailInfo.objects.get(id=trip_id)
        details = {
            'Trip Charges': trip.tc_tripcost or 0,
            'Parking Charges': trip.tc_parkingcost or 0,
            'Toll Charges': trip.tc_tollcost or 0,
            'Loading Charges': trip.tc_loadingcost or 0,
            'Unloading Charges': trip.tc_unloadingcost or 0,
            'Weighment Charges': trip.tc_weighmentcost or 0,
            'Handling Charges': trip.tc_handlingcost or 0,
            'Halting Charges': trip.tc_haltingcost or 0,
            'Supervisor Charges': trip.tc_supervisorcost or 0,
        }
        total_cost = sum(details.values())
        return JsonResponse({'details': details, 'total_cost': total_cost})
    except TripdetailInfo.DoesNotExist:
        return JsonResponse({'details': {}, 'total_cost': 0})
