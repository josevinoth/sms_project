from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .driver_settlement_view import recalc_driver_settlement
from ..models import Driverexpense, TripdetailInfo, driver_settlement_info
from ..sub_forms.driver_expense_form import DriverExpenseForm
from datetime import datetime
from ..sub_models.driver_master_mod import DrivermasterInfo

@login_required(login_url='login_page')
def driver_expense_add(request, expense_id=0):
    first_name = request.session.get('first_name')

    expense = None
    settlement = None

    # ================= 1️⃣ RESOLVE SETTLEMENT FIRST =================
    if expense_id:
        # EDIT MODE
        expense = get_object_or_404(Driverexpense, pk=expense_id)
        settlement = expense.de_driver_id
    else:
        # ADD MODE
        settlement_id = request.GET.get('settlement_id')
        driver_master_id = request.GET.get('driver_master_id')

        if settlement_id:
            settlement = get_object_or_404(driver_settlement_info, id=settlement_id)
        elif driver_master_id:
            from ..sub_models.driver_master_mod import DrivermasterInfo
            master = get_object_or_404(DrivermasterInfo, id=driver_master_id)
            # Auto-create settlement record if it doesn't exist
            settlement, created = driver_settlement_info.objects.get_or_create(
                driver=master,
                defaults={
                    'driver_id_value': master.dm_id,
                    'driver_name': master.dm_name,
                    'driver_phone': master.dm_drivernumber,
                    'driver_licence': master.dm_driver_lic,
                    'driver_licence_expiry': master.dm_driver_lic_expiry
                }
            )
        else:
            messages.error(request, "Please open expense from Driver Settlement")
            return redirect('driver_settlement_list')

    # ================= 2️⃣ CALCULATE TOTALS (AFTER settlement) =================
    advance_total = Driverexpense.objects.filter(
        de_driver_id=settlement,
        de_expense_type__id=1   # ADVANCE
    ).aggregate(t=Sum('de_total_cost'))['t'] or 0

    expense_total = Driverexpense.objects.filter(
        de_driver_id=settlement,
        de_expense_type__id=2   # EXPENSE
    ).aggregate(t=Sum('de_total_cost'))['t'] or 0

    current_balance = advance_total - expense_total

    # ================= 3️⃣ POST =================
    if request.method == "POST":
        form = DriverExpenseForm(request.POST, instance=expense, settlement=settlement)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.driver_name = settlement.driver
            exp.de_driver_id = settlement
            exp.save()

            # ------------------------------------------------------------------
            # AUTO-GENERATE TMS PETTY CASH ENTRIES FOR EXPENSES
            # ------------------------------------------------------------------
            if exp.de_expense_type and exp.de_expense_type.id == 2:
                from ..models import (
                    TMSPettyCashInfo, Business_Sol_info, Location_info, 
                    ExpenseCategoryInfo, CreditLedgerInfo
                )
                from ..sub_models.tms_expense_type_mod import TMSExpenseTypeInfo
                from .tms_petty_cash_view import generate_tms_petty_cash_number
                from .general_utils import get_session_branch_id
                
                # First, delete any previously auto-generated petty cash entries for this specific expense record 
                # (in case the user is editing an existing driver expense)
                TMSPettyCashInfo.objects.filter(tpc_remarks=f"Auto-generated from Driver Settlement Expense ID: {exp.id}").delete()
                
                # 1. Gather defaults
                bvm_trans = Business_Sol_info.objects.filter(bvm_business__icontains='bvm trans solutions').first()
                cash_cat = ExpenseCategoryInfo.objects.filter(exp_category_name__icontains='Cash').first()
                
                branch_id = get_session_branch_id(request)
                branch_obj = Location_info.objects.filter(id=branch_id).first() if branch_id else None
                
                ledger = None
                if branch_obj:
                    branch_code = branch_obj.loc_name.split()[-1]
                    ledger = CreditLedgerInfo.objects.filter(
                        ledger_name__icontains='Trans Petty Cash'
                    ).filter(ledger_name__icontains=branch_code).exclude(
                        ledger_name__icontains='Admin'
                    ).first()
                    if not ledger:
                        ledger = CreditLedgerInfo.objects.filter(
                            ledger_name__icontains='Trans'
                        ).filter(ledger_name__icontains=branch_code).first()

                # Try to determine the vehicle from the trip number
                vehicle_obj = None
                trip_no = exp.trip_number or exp.de_trip_number
                if trip_no:
                    from ..sub_models.tripdetail_mod import TripdetailInfo
                    trip = TripdetailInfo.objects.filter(tr_tripnumber=trip_no).first()
                    if trip and trip.tr_vehiclenumber:
                        from ..models import VehiclemasterInfo
                        vehicle_obj = VehiclemasterInfo.objects.filter(vm_registrationnumber=trip.tr_vehiclenumber).first()

                # Map Driver Expense fields to exact labels shown in Driver Expense form
                expense_mapping = [
                    (exp.de_parkingcost, 'Parking Cost'),
                    (exp.de_loadingcost, 'Loading Cost'),
                    (exp.de_unloadingcost, 'Unloading Cost'),
                    (exp.de_weighmentcost, 'Weighment Cost'),
                    (exp.de_supervisorcost, 'Supervisor Cost'),
                    (exp.de_rtocost, 'RTO Expense'),
                    (exp.de_battacost, 'Batta Expense'),
                ]
                
                for amount, type_name in expense_mapping:
                    if amount and float(amount) > 0.0:
                        tms_exp_type = TMSExpenseTypeInfo.objects.filter(tms_exp_type_name__icontains=type_name).first()
                        
                        if not tms_exp_type:
                            from django.db.models import Max
                            max_id = TMSExpenseTypeInfo.objects.aggregate(Max('id'))['id__max'] or 0
                            tms_exp_type = TMSExpenseTypeInfo.objects.create(id=max_id + 1, tms_exp_type_name=type_name)
                            
                        tpc = TMSPettyCashInfo(
                            tpc_business=bvm_trans,
                            tpc_branch=branch_obj,
                            tpc_category=cash_cat,
                            tpc_transaction_date=exp.de_date.date() if exp.de_date else None,
                            tpc_expense_type=tms_exp_type,
                            tpc_amount=float(amount),
                            tpc_credit_ledger=ledger,
                            tpc_trip_date=exp.trip_date,
                            tpc_job_no=trip_no,
                            tpc_vehicle_number=vehicle_obj,
                            tpc_driver_name=exp.driver_name,
                            tpc_created_by=request.user,
                            tpc_updated_by=request.user,
                            tpc_remarks=f"Auto-generated from Driver Settlement Expense ID: {exp.id}"
                        )
                        tpc.tpc_number = generate_tms_petty_cash_number(TMSPettyCashInfo, 'tpc_number', branch_obj)
                        tpc.save()
            # ------------------------------------------------------------------

            # ALWAYS recalc after save
            recalc_driver_settlement(settlement)

            messages.success(request, "Driver expense saved successfully ✅")
            return redirect('driver_settlement_update', ds_id=settlement.id)

    # ================= 4️⃣ GET =================
    else:
        if expense:
            form = DriverExpenseForm(instance=expense,settlement=settlement)
        else:
            initial_data = {'driver_name': settlement.driver}
            
            trip_id = request.GET.get('trip_id')
            if trip_id:
                initial_data['trip_number'] = trip_id
                initial_data['de_expense_type'] = 2  # Preselect Expense
                # Try prepopulating date too
                try:
                    trip = TripdetailInfo.objects.get(id=trip_id)
                    if trip.tr_departeddate:
                        initial_data['trip_date'] = trip.tr_departeddate.date()
                except TripdetailInfo.DoesNotExist:
                    pass

            form = DriverExpenseForm(
                initial=initial_data,
                settlement=settlement
            )

    # ================= 5️⃣ RENDER =================
    return render(request, "asset_mgt_app/driver_expense_add.html", {
        'form': form,
        'first_name': first_name,
        'settlement': settlement,
        'advance_total': advance_total,
        'expense_total': expense_total,
        'current_balance': current_balance,
        'auto_trip_id': request.GET.get('trip_id') if not expense else None
    })


# ============================================================
# LIST DRIVER EXPENSE
# ============================================================
@login_required(login_url='login_page')
def driver_expense_list(request):
    first_name = request.session.get('first_name')

    context = {
        'expense_list': Driverexpense.objects.all().order_by('-id'),
        'first_name': first_name
    }

    return render(
        request,
        "asset_mgt_app/driver_expense_list.html",
        context
    )


@login_required(login_url='login_page')
def driver_expense_delete(request, expense_id):
    expense = get_object_or_404(Driverexpense, pk=expense_id)
    settlement = expense.de_driver_id

    expense.delete()

    #  RECALC AFTER DELETE
    recalc_driver_settlement(settlement)

    messages.success(request, "Driver expense deleted successfully 🗑️")
    return redirect('driver_settlement_add', ds_id=settlement.id)

def get_trip_charges(request):
    trip_id = request.GET.get('trip_id')

    if not trip_id:
        return JsonResponse({'error': 'No trip id'}, status=400)

    try:
        if str(trip_id).isdigit():
            trip = TripdetailInfo.objects.get(id=trip_id)
        else:
            trip = TripdetailInfo.objects.get(tr_tripnumber=trip_id)

        data = {
            # COSTS
            'parking': trip.tc_parkingcost or 0,
            'loading': trip.tc_loadingcost or 0,
            'unloading': trip.tc_unloadingcost or 0,
            'weighment': trip.tc_weighmentcost or 0,
            'supervisor': trip.tc_supervisorcost or 0,
            'rto': trip.tc_rtocost or 0,
            'batta': trip.tc_betacost or 0,

            #  NEW DETAILS
            'vehicle_number': trip.tr_vehiclenumber or "",
            'from_location': trip.tr_departedlocation.place_name if trip.tr_departedlocation else "",
            'to_location': trip.tr_reportedlocation.place_name if trip.tr_reportedlocation else "",
        }

        data['total'] = sum([
            data['parking'],
            data['loading'],
            data['unloading'],
            data['weighment'],
            data['supervisor'],
            data['rto'],
            data['batta'],
        ])

        return JsonResponse(data)

    except TripdetailInfo.DoesNotExist:
        return JsonResponse({'error': 'Trip not found'}, status=404)

@login_required(login_url='login_page')
def filter_trips_by_date(request):
    trip_date = request.GET.get('trip_date')
    settlement_id = request.GET.get('settlement_id')
    vehicle_no = request.GET.get('vehicle_no')

    if not settlement_id:
        return JsonResponse([], safe=False)

    settlement = get_object_or_404(driver_settlement_info, id=settlement_id)

    qs = TripdetailInfo.objects.filter(
        tc_financestatus__id__in=[5, 7, 9]
    )

    # Filter by driver
    if settlement.driver:
        qs = qs.filter(Q(tr_driver_master_id=settlement.driver.id) | Q(tr_drivername=settlement.driver.dm_name))
    else:
        qs = qs.filter(tr_drivername=settlement.driver_name)

    # ✅ OPTIONAL FILTER BY DATE
    if trip_date:
        # Support both YYYY-MM-DD and DD-MM-YYYY
        parsed_date = None
        
        if 'T' in trip_date:
            trip_date = trip_date.split('T')[0]
            
        # Try YYYY-MM-DD
        try:
            parsed_date = datetime.strptime(trip_date, "%Y-%m-%d").date()
        except ValueError:
            # Try DD-MM-YYYY
            try:
                parsed_date = datetime.strptime(trip_date, "%d-%m-%Y").date()
            except ValueError:
                pass
        
        if parsed_date:
            qs = qs.filter(
                Q(tr_departeddate__date=parsed_date) | 
                Q(tr_reporteddate__date=parsed_date) |
                Q(tr_departeddate_pickup__date=parsed_date) |
                Q(tr_departeddate_delivery__date=parsed_date)
            )

    # ✅ OPTIONAL FILTER BY VEHICLE
    if vehicle_no:
        qs = qs.filter(tr_vehiclenumber__icontains=vehicle_no)

    qs = qs.order_by('-tr_departeddate')

    data = [
        {
            'id': t.id, 
            'trip_number': t.tr_tripnumber,
            'vehicle': t.tr_vehiclenumber,
            'from': t.tr_departedlocation.place_name if t.tr_departedlocation else "",
            'to': t.tr_reportedlocation.place_name if t.tr_reportedlocation else "",
            'date': (t.tr_departeddate_pickup or t.tr_departeddate or t.tr_reporteddate or t.tr_departeddate_delivery).strftime('%Y-%m-%d') if (t.tr_departeddate_pickup or t.tr_departeddate or t.tr_reporteddate or t.tr_departeddate_delivery) else "",
            'parking': t.tc_parkingcost or 0,
            'loading': t.tc_loadingcost or 0,
            'unloading': t.tc_unloadingcost or 0,
            'weighment': t.tc_weighmentcost or 0,
            'supervisor': t.tc_supervisorcost or 0,
            'rto': t.tc_rtocost or 0,
            'batta': t.tc_betacost or 0
        }
        for t in qs
    ]

    return JsonResponse(data, safe=False)
