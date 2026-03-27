from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date

from ..forms import TransCustomerClaimsForm
from ..sub_models.trans_customer_claims_mod import TransCustomerClaimsInfo
from django.contrib import messages
from django.shortcuts import render, redirect



@login_required(login_url='login_page')
def trans_customer_claims_add(request,claim_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if claim_id == 0:
            form = TransCustomerClaimsForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
            }
        else:
            claim = TransCustomerClaimsInfo.objects.get(pk=claim_id)
            form = TransCustomerClaimsForm(instance=claim)
            context = {
                'form': form,
                'first_name': first_name,
                'claim_id': claim_id,
            }
        return render(request, "asset_mgt_app/trans_customer_claim_add.html", context)

    else:
        if claim_id == 0:
            form = TransCustomerClaimsForm(request.POST)
        else:
            claim = TransCustomerClaimsInfo.objects.get(pk=claim_id)
            form = TransCustomerClaimsForm(request.POST, instance=claim)
        if form.is_valid():
            instance = form.save(commit=False)

            instance.save()
            if claim_id == 0:
                messages.success(request, 'Record Saved Successfully')
            else:
                messages.success(request, 'Record Updated Successfully')
        else:
            messages.error(request, 'Error: Please correct the errors below.')

        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error in {field}: {error}")
                messages.error(request, f"Error in {field}: {error}")
        return redirect('trans_customer_claims_list')

@login_required(login_url='login_page')
def trans_customer_claims_list(request):
    first_name = request.session.get('first_name')
    from_date = request.GET.get('from_date', None)
    to_date = request.GET.get('to_date', None)
    customer_claim_list = TransCustomerClaimsInfo.objects.all()
    if from_date:
        customer_claim_list = customer_claim_list.filter(tcc_trip_date__gte=from_date)

    if to_date:
        customer_claim_list = customer_claim_list.filter(tcc_trip_date__lte=to_date)

    context = {
        'customer_claim_list': customer_claim_list,
        'first_name': first_name,
        'from_date': from_date,
        'to_date': to_date,
    }
    return render(request, "asset_mgt_app/trans_customer_claim_list.html", context)


from django.db.models import Sum
from django.http import JsonResponse
from ..sub_models.trans_customer_claims_mod import TransCustomerClaimsInfo
from ..sub_models.tripdetail_mod import TripdetailInfo
from ..sub_models.consignmentgoods_mod import ConsignmentgoodsInfo
from ..sub_models.consignmentdetail_mod import ConsignmentdetailInfo
from ..sub_models.gatein_mod import Gatein_info
from ..sub_models.warehouse_goods_info_mod import Warehouse_goods_info
from ..sub_models.damagereport_mod import DamagereportInfo


@login_required(login_url='login_page')
def trans_customer_claims_delete(request, claim_id):
        claim = TransCustomerClaimsInfo.objects.get(pk=claim_id)
        claim.delete()
        messages.success(request, 'Customer Claim deleted successfully.')
        return redirect(request.META.get('HTTP_REFERER', 'trans_customer_claims_list'))

def fetch_trip_details_by_cnote(request):
    cnote_id = request.GET.get('cnote_id')
    data = {}
    if cnote_id:
        try:
            # ConsignmentdetailInfo ID is passed
            # TripdetailInfo links to ConsignmentdetailInfo via tr_consignmentnumber
            trip = TripdetailInfo.objects.filter(tr_consignmentnumber_id=cnote_id).first()
            if trip:
                data = {
                    'trip_date': trip.tr_departeddate.strftime('%Y-%m-%d') if trip.tr_departeddate else '',
                    'from_loc': trip.tr_departedlocation.place_name if trip.tr_departedlocation else '',
                    'to_loc': trip.tr_reportedlocation.place_name if trip.tr_reportedlocation else (trip.tr_consignmentnumber.co_tolocation.place_name if trip.tr_consignmentnumber and trip.tr_consignmentnumber.co_tolocation else ''),
                    'veh_no': trip.tr_vehiclenumber or '',
                    'veh_type': trip.tr_vehicletype.vt_vehicletype if trip.tr_vehicletype else '',
                    'driver_no': trip.tr_drivernumber or '',
                    'driver_name': trip.tr_drivername or '',
                    'shipper_ref_no': trip.tr_customerref or '',
                }
                # Total PKG from ConsignmentgoodsInfo
                total_pkg = ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber_id=cnote_id).aggregate(Sum('cg_qty'))['cg_qty__sum']
                data['total_pkg'] = total_pkg or 0

                # --- 🔹 FETCH DAMAGE DETAILS FROM WAREHOUSE MODULE ---
                try:
                    cnote_no = trip.tr_consignmentnumber.co_consignmentnumber
                    # Link via gatein_invoice matching the Cnote number
                    gatein = Gatein_info.objects.filter(gatein_invoice=cnote_no).first()
                    
                    if gatein:
                        job_no = gatein.gatein_job_no
                        
                        # 1. Damaged Pkg Count (Sum of pieces where wh_damage_check=1 "Yes")
                        damaged_pkg = Warehouse_goods_info.objects.filter(
                            wh_job_no=job_no, 
                            wh_damage_check=1
                        ).aggregate(Sum('wh_goods_pieces'))['wh_goods_pieces__sum']
                        
                        data['damaged_pkg'] = int(damaged_pkg) if damaged_pkg else 0
                        
                        # 2. Damage Remarks (From DamagereportInfo comments)
                        damage_report = DamagereportInfo.objects.filter(dam_wh_job_num=job_no).first()
                        if damage_report:
                            data['damage_remarks'] = damage_report.dam_comments or ''
                    else:
                        data['damaged_pkg'] = 0
                        data['damage_remarks'] = ''
                        
                except Exception as ex:
                    print(f"Error fetching warehouse damage data: {ex}")
                    data['damaged_pkg'] = 0
                    data['damage_remarks'] = ''

        except Exception as e:
            print(f"Error fetching trip details: {e}")
            
    return JsonResponse(data)
