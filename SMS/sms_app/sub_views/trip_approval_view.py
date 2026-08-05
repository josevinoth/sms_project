from django.shortcuts import render, get_object_or_404, redirect
from ..models import TripdetailInfo, ConsignmentgoodsInfo, approval_status_info, Trip_approval_info, Emailmaster, EnquirynoteInfo
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .send_department_email import send_department_email

def format_email_date(dt):
    if not dt:
        return ""
    try:
        # Convert to local timezone (IST)
        local_dt = timezone.localtime(dt)
        return local_dt.strftime("%d-%m-%Y %H:%M")
    except Exception:
        return str(dt)

@login_required(login_url='login_page')
def trip_approval_view(request):
    trip_list = TripdetailInfo.objects.select_related(
        'tr_consignmentnumber',
        'tr_approval',
        'tr_approval__ta_approval_status'
    ).filter(
        Q(tr_category=1),
        Q(tr_departeddate__isnull=False),
        Q(tc_financestatus_id=8) | Q(tr_approval__ta_approval_status__id=3)
    ).exclude(
        tr_approval__ta_approval_status__id=1
    )

    return render(request, "asset_mgt_app/trip_approval.html", {
        'trip_list': trip_list,
        'status_list': approval_status_info.objects.all(),
        'today': timezone.now().date()
    })

@login_required
def update_trip_approval(request, trip_id):
    if request.method == 'POST':
        approval_status_id = request.POST.get('ta_approval_status')
        trip = get_object_or_404(TripdetailInfo, pk=trip_id)
        status_obj = get_object_or_404(approval_status_info, pk=approval_status_id)

        if trip.tr_approval:
            approval = trip.tr_approval
            approval.ta_approval_status = status_obj
            approval.ta_approved_by = request.user
        else:
            approval = Trip_approval_info.objects.create(
                ta_approval_status=status_obj,
                ta_approved_by=request.user
            )

        approval.save()
        trip.tr_approval = approval

        if status_obj.approval_name == "Approved":
            trip.tc_financestatus_id = 1
            trip.tr_operational_status_id = 1
            
            # ✅ AUTOMATED EMAIL: Trip Started
            if not trip.tr_trip_started_mail_sent:
                try:
                    # 1. Get Recipients from Emailmaster (Type 2)
                    enquiry = trip.tr_enquirynumber
                    customer = enquiry.en_customername
                    department = enquiry.en_customerdepartment
                    
                    email_qs = Emailmaster.objects.filter(em_Customer_name=customer, em_emailtype_id=2)
                    if department:
                        email_qs = email_qs.filter(em_customerdepartment=department)
                    
                    email_obj = email_qs.first()
                    recipients = []
                    if email_obj:
                        to = email_obj.em_to_names or ""
                        cc = email_obj.em_cc_names or ""
                        recipients = [x.strip() for x in to.split(",") if x.strip()]
                        if cc:
                            recipients.extend([x.strip() for x in cc.split(",") if x.strip()])
                    
                    if not recipients:
                        recipients = ["itadmin@bvm.com"]

                    # 2. Construct Email
                    customer_name = customer.cu_name if customer else "N/A"
                    from_location = trip.tr_departedlocation.place_name if trip.tr_departedlocation else "N/A"
                    reported_dt = format_email_date(trip.tr_departeddate_pickup)
                    consignment = trip.tr_consignmentnumber.co_consignmentnumber if trip.tr_consignmentnumber else "N/A"
                    started_dt = format_email_date(trip.tr_departeddate)
                    vehicle_number = trip.tr_vehiclenumber or "N/A"

                    subject = f"Trip Started Alert - {vehicle_number}"
                    email_body = f"""
                    <html>
                    <body>
                        <p>Dear Customer,</p>
                        <p>Status Update: Trip Started Alert (Automated).</p>
                        <table style="border-collapse: collapse; width: 70%; border: 1px solid #ddd; font-family: Arial, sans-serif; margin-left: auto; margin-right: auto;">
                            <thead style="background-color: #003366; color: white;">
                                <tr><th colspan="2" style="padding: 10px; text-align: center;">Trip Started Details</th></tr>
                            </thead>
                            <tbody>
                                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Customer Name</b></td><td style="padding: 8px; border: 1px solid #ddd;">{customer_name}</td></tr>
                                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Vehicle Number</b></td><td style="padding: 8px; border: 1px solid #ddd;">{vehicle_number}</td></tr>
                                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>From Location</b></td><td style="padding: 8px; border: 1px solid #ddd;">{from_location}</td></tr>
                                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Vehicle Reported Date & Time</b></td><td style="padding: 8px; border: 1px solid #ddd;">{reported_dt or "N/A"}</td></tr>
                                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Consignment Number</b></td><td style="padding: 8px; border: 1px solid #ddd;">{consignment}</td></tr>
                                <tr><td style="padding: 8px; border: 1px solid #ddd;"><b>Vehicle Started Date & Time</b></td><td style="padding: 8px; border: 1px solid #ddd;">{started_dt or "N/A"}</td></tr>
                            </tbody>
                        </table>
                        <p>Regards,<br>BVM Transport Team</p>
                    </body>
                    </html>
                    """
                    
                    send_department_email(
                        department="itadmin",
                        subject=subject,
                        message=email_body,
                        recipient_list=recipients,
                        email_type=1
                    )
                    trip.tr_trip_started_mail_sent = True
                    try:
                        messages.info(request, "Automated 'Trip Started' email sent.")
                    except Exception:
                        pass
                except Exception as e:
                    print(f"Error sending automated email: {str(e)}")
                    try:
                        messages.error(request, f"Error sending automated email: {str(e)}")
                    except Exception:
                        pass

        trip.save()

        try:
            messages.success(request, "Approval updated.")
        except Exception:
            pass
    return redirect('trip_approval_view')
