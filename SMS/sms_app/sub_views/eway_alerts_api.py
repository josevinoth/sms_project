from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from ..models import Loadingbay_Info, Warehouse_goods_info, ConsignmentgoodsInfo


def get_eway_expiry_alerts(request):
    """
    Returns JSON list of E-Way Bills that are expired or expiring within 24 hours.
    """
    try:
        now = timezone.now()
        threshold_date = now + timedelta(days=1)
        alerts = []

        # Filter alerts strictly for users belonging to 'BVM Trans Solutions pvt ltd'
        user = request.user
        if user.is_authenticated:
            from ..models import User_extInfo
            user_ext = User_extInfo.objects.filter(user=user).select_related('emp_organisation').first()
            if user_ext and user_ext.emp_organisation:
                org_name = str(user_ext.emp_organisation.bvm_business or '')
                if 'Trans' not in org_name and not user.is_superuser:
                    # Non-transport organisation users (e.g. Storage/Pack/Express) do not receive transport E-Way Bill alerts
                    return JsonResponse({'success': True, 'count': 0, 'alerts': []})

        # Fetch trips that are currently active in 'Trip Started' status (tc_financestatus_id=1)
        from ..models import TripdetailInfo
        active_trip_consignment_ids = TripdetailInfo.objects.filter(
            tc_financestatus_id=1,
            tr_consignmentnumber__isnull=False
        ).values_list('tr_consignmentnumber_id', flat=True)

        # Rolling window: Include validity dates from last 3 days up to tomorrow (now + 1 day)
        min_date = now.date() - timedelta(days=3)

        # Consignment Goods E-Way Bills linked ONLY to active trips in 'Trip Started' status (status 1) within last 3 days window
        cg_records = ConsignmentgoodsInfo.objects.filter(
            cg_consignmentnumber_id__in=active_trip_consignment_ids,
            cg_dateofvalidity__isnull=False,
            cg_dateofvalidity__gte=min_date,
            cg_dateofvalidity__lte=threshold_date.date()
        ).select_related('cg_consignmentnumber')

        seen_consignments = set()

        for cg in cg_records:
            if not cg.cg_consignmentnumber:
                continue

            cons_id = cg.cg_consignmentnumber.id
            if cons_id in seen_consignments:
                continue
            seen_consignments.add(cons_id)

            val_date = cg.cg_dateofvalidity
            is_expired = val_date < now.date()
            cons_no = cg.cg_consignmentnumber.co_consignmentnumber or f"CG-{cg.id}"

            # Count total expiring items for this consignment
            items_count = ConsignmentgoodsInfo.objects.filter(
                cg_consignmentnumber_id=cons_id,
                cg_dateofvalidity__isnull=False,
                cg_dateofvalidity__lte=threshold_date.date()
            ).count()

            alerts.append({
                'type': 'Consignment',
                'ref_no': cons_no,
                'eway_no': cg.cg_ebillno or 'N/A',
                'items_count': items_count,
                'expiry_date': val_date.strftime('%Y-%m-%d'),
                'is_expired': is_expired,
                'status_text': 'EXPIRED' if is_expired else 'Expiring Soon',
                'update_url': f"/SMS/consignmentdetail_update/{cg.cg_consignmentnumber.id}/"
            })

        return JsonResponse({
            'success': True,
            'count': len(alerts),
            'alerts': alerts
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e),
            'alerts': []
        })


def verify_trip_eway_details(request, trip_id):
    """
    Compares Software Details vs E-Way Bill PDF details for the modal popup.
    """
    try:
        from ..models import TripdetailInfo, ConsignmentgoodsInfo
        from .eway_partb_validator import parse_eway_bill_pdf, clean_vehicle_no
        import os

        trip = TripdetailInfo.objects.filter(id=trip_id).select_related('tr_consignmentnumber').first()
        if not trip:
            return JsonResponse({'success': False, 'message': 'Trip not found'})

        consignment = trip.tr_consignmentnumber
        if not consignment:
            return JsonResponse({'success': False, 'message': 'No consignment linked to trip'})

        assigned_vehicle = consignment.co_vehicelnumber or trip.tr_vehiclenumber or "N/A"
        assigned_veh_clean = clean_vehicle_no(assigned_vehicle)

        goods_records = ConsignmentgoodsInfo.objects.filter(cg_consignmentnumber=consignment)
        
        items = []
        overall_match = True

        for g in goods_records:
            sw_val = g.cg_consignervalue if (g.cg_consignervalue is not None and g.cg_consignervalue > 0) else (g.cg_valueininr or 0.0)
            pdf_val = parsed_val = None

            item_info = {
                'ebill_no': g.cg_ebillno or 'N/A',
                'invoice_no': g.cg_consignerinvoice or 'N/A',
                'software_vehicle': assigned_vehicle,
                'pdf_vehicle': 'N/A',
                'pdf_eway_no': 'N/A',
                'software_value': f"₹{sw_val:,.2f}" if sw_val else 'N/A',
                'pdf_value': 'N/A',
                'value_matched': True,
                'has_part_b': False,
                'is_match': False,
                'status_message': ''
            }

            if not g.cg_ewaybill_att:
                item_info['status_message'] = 'Missing PDF Attachment'
                overall_match = False
                items.append(item_info)
                continue

            file_path = g.cg_ewaybill_att.path
            ext = os.path.splitext(file_path)[1].lower()

            if ext in ['.jfif', '.jpeg', '.jpg', '.png', '.bmp', '.webp']:
                item_info['status_message'] = 'Photo scan uploaded (.jpg/.jfif). PDF required.'
                overall_match = False
                items.append(item_info)
                continue

            parsed = parse_eway_bill_pdf(file_path)
            item_info['pdf_eway_no'] = parsed.get('eway_no') or 'N/A'
            
            pdf_val = parsed.get('goods_value')
            if pdf_val is not None:
                item_info['pdf_value'] = f"₹{pdf_val:,.2f}"
                # Value match check (allow within ₹1 rounding difference)
                if sw_val > 0:
                    item_info['value_matched'] = abs(sw_val - pdf_val) <= 1.0

            pdf_vehs = parsed.get('vehicles_in_part_b', [])
            item_info['pdf_vehicle'] = ", ".join(pdf_vehs) if pdf_vehs else 'None / Missing Part-B'
            item_info['has_part_b'] = parsed.get('has_part_b', False)

            # Verification Logic: E-Way Bill Number AND Vehicle Number AND Invoice Value MUST match
            clean_software_ewb = str(g.cg_ebillno or '').replace(' ', '').strip()
            clean_pdf_ewb = str(parsed.get('eway_no') or '').replace(' ', '').strip()
            all_pdf_ewbs = parsed.get('all_ewb_numbers', [])

            ewb_no_matched = (clean_software_ewb and (clean_software_ewb == clean_pdf_ewb or clean_software_ewb in all_pdf_ewbs))

            if not parsed.get('has_part_b'):
                item_info['status_message'] = 'Part-B Missing in PDF ❌'
                item_info['is_match'] = False
                overall_match = False
            elif not ewb_no_matched:
                item_info['status_message'] = f"EWB No Mismatch (Software: {clean_software_ewb} vs PDF: {clean_pdf_ewb}) ❌"
                item_info['is_match'] = False
                overall_match = False
            elif not item_info['value_matched']:
                item_info['status_message'] = f"Value Mismatch (Software: ₹{sw_val:,.2f} vs PDF: ₹{pdf_val:,.2f}) ❌"
                item_info['is_match'] = False
                overall_match = False
            elif assigned_veh_clean and assigned_veh_clean in pdf_vehs:
                item_info['status_message'] = 'MATCHED ✅'
                item_info['is_match'] = True
            else:
                item_info['status_message'] = f"Vehicle Mismatch (PDF: {item_info['pdf_vehicle']}) ❌"
                item_info['is_match'] = False
                overall_match = False

            items.append(item_info)

        return JsonResponse({
            'success': True,
            'trip_no': trip.tr_tripnumber,
            'customer_name': str(trip.tr_enquirynumber.en_customername) if trip.tr_enquirynumber and trip.tr_enquirynumber.en_customername else 'N/A',
            'overall_match': overall_match,
            'items': items
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

