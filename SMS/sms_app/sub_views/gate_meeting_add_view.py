from django.contrib.auth.decorators import login_required
from ..forms import GatemeetingaddForm
from ..models import Gatemeetinginfo
from django.shortcuts import render, redirect
from django.contrib import messages
from .send_department_email import send_department_email

@login_required(login_url='login_page')
def gatemeeting_add(request,gate_meet_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')
    if request.method == "GET":
        if gate_meet_id == 0:
            print("I am inside Get add gatemeeting")
            form = GatemeetingaddForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
            }
        else:
            print("I am inside get edit gatemeeting")
            gatemeet = Gatemeetinginfo.objects.get(pk=gate_meet_id)
            form = GatemeetingaddForm(instance=gatemeet)
            gate_meet_email_count = Gatemeetinginfo.objects.get(pk=gate_meet_id).gm_email_count
            context = {
                'form': form,
                'first_name': first_name,
                'gate_meet_email_count': gate_meet_email_count,
            }
        return render(request, "asset_mgt_app/gate_meeting_add.html", context)

    else:
        if gate_meet_id == 0:
            form = GatemeetingaddForm(request.POST)
        else:
            gatemeet = Gatemeetinginfo.objects.get(pk=gate_meet_id)
            form = GatemeetingaddForm(request.POST, instance=gatemeet)
        if form.is_valid():
            form.save()
            if gate_meet_id == 0:
                messages.success(request, 'Record Saved Successfully')
            else:
                messages.success(request, 'Record Updated Successfully')

        else:
            messages.error(request, 'Error: Please correct the errors below.')

        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error in {field}: {error}")
                messages.error(request, f"Error in {field}: {error}")
        return redirect(request.META['HTTP_REFERER'])

# List
@login_required(login_url='login_page')
def gatemeeting_list(request):
    first_name = request.session.get('first_name')
    context = {'gate_meet_list' : Gatemeetinginfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/gate_meeting_list.html",context)

#Delete
@login_required(login_url='login_page')
def gatemeeting_delete(request,gate_meet_id):
    gatemeet = Gatemeetinginfo.objects.get(pk=gate_meet_id)
    gatemeet.delete()
    return redirect('/SMS/gate_meeting_list')

@login_required(login_url='login_page')
def gate_meeting_send_email(request):
    gate_meet_id = request.session.get('ses_gate_meet_id')
    print(gate_meet_id)

    if not gate_meet_id:
        messages.error(request, "meeting ID is missing. Please try again.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    gate = Gatemeetinginfo.objects.get(pk=gate_meet_id)
    gate_meet_email_count = Gatemeetinginfo.objects.get(pk=gate_meet_id).gm_email_count

    recipient_list = [
        'josevinoth83@gmail.com',
    ]

    subject = f"Gate Meeting {gate.gm_branch} - Update"

    email_body = f""" 
            <html>
                <head>
                    <style>
                        table {{
                            width: 80%;
                            border-collapse: collapse;
                            font-family: Arial, sans-serif;
                            font-size: 14px;
                            border: 1px solid black;
                            margin-top: 10px;
                        }}
                        th, td {{
                            border: 1px solid black;
                            padding: 8px;
                            text-align: left;
                        }}
                        th {{
                            background-color: #dff0d8;
                            color: #333;
                        }}
                        td {{
                            vertical-align: top;
                        }}
                        .remarks {{
                            color: #d9534f; /* Highlights remarks in a different color */
                            font-weight: bold;
                        }}
                    </style>
                </head>
                <body>
                    <p>Dear Team,</p>
                    <p>Please find below the Gate Meeting details:</p>

                    <table>
                        <tr><th>Location</th><td>{gate.gm_branch}</td></tr>
                        <tr><th>Unit Reference</th><td>{gate.gm_unit}</td></tr>
                        <tr><th>Date</th><td>{gate.gm_date}</td></tr>
                    </table>

                    <br>

                    <table>
                        <thead>
                            <tr>
                                <th>Points to Discuss</th>
                                <th>Yes / No</th>
                                <th>Remarks</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr><th>Previous night security monitoring</th><td>{gate.gm_Previous_night_security}</td><td>{gate.gm_Previous_night_security_remark}</td></tr>
                            <tr><th>Any incident of previous day reported to management</th><td>{gate.gm_Any_incident_of_previous_day}</td><td>{gate.gm_Any_incident_of_previous_day_remark}</td></tr>
                            <tr><th>Previous day WH closing checklist </th><td>{gate.gm_Previous_day_WH_closing_checklist}</td><td></td></tr>
                            <tr><th>Current day WH opening checklist</th><td>{gate.gm_Current_day_WH_opening_checklist}</td><td></td></tr>
                            <tr><th>WMS updation - 100% till yesterday </th><td>{gate.gm_WMS_updation_till_yesterday}</td><td></td></tr>
                            <tr><th>DSR sent to all customers - yesterday</th><td>{gate.gm_DSR_sent_to_all_customers_yesterday}</td><td></td></tr>
                            <tr><th>Stock more than 3 days and 5 days informed to Customer</th><td>{gate.gm_Stock_informed_to_Customer}</td><td></td></tr>
                            <tr><th>Pre-alerts shared with customers - 100% for all inbound and outbound</th><td>{gate.gm_Pre_alerts_customers_inbound_outbound}</td><td></td></tr>
                            <tr><th>Acknowledgement for Inbound provided and documents scanned </th><td>{gate.gm_Inbound_documents_scanned}</td><td></td></tr>
                            <tr><th>Acknowledgement for Outbound received and documents scanned</th><td>{gate.gm_Outbound_documents_scanned}</td><td></td></tr>
                            <tr><th>Cleanliness of warehouse </th><td>{gate.gm_Cleanliness_of_warehouse}</td><td></td></tr>
                            <tr><th>Facility walk around - as per checklist provided</th><td>{gate.gm_Facility_checklist_provided}</td><td></td></tr>
                            <tr><th>Space Issues - if any</th><td>{gate.gm_Space_issues}</td><td>{gate.gm_Space_issues_remark}</td></tr>
                            <tr><th>HPTE condition</th><td>{gate.gm_HPTE_condition}</td><td></td></tr>
                            <tr><th>Fork Lift check </th><td>{gate.gm_Fork_Lift_check}</td><td></td></tr>
                            <tr><th>Weightment scale condition</th><td>{gate.gm_Weight_scale_condition}</td><td></td></tr>
                            <tr><th>Fire Extinguisher</th><td>{gate.gm_Fire_Extinguisher}</td><td></td></tr>
                            <tr><th>CCTV condition</th><td>{gate.gm_CCTV_condition}</td><td></td></tr>
                            <tr><th>Lights condition</th><td>{gate.gm_Lights_condition}</td><td></td></tr>
                            <tr><th>UPS Invertor condition</th><td>{gate.gm_UPS_invertor_condition}</td><td></td></tr>
                            <tr><th>Genset condition</th><td>{gate.gm_Genset_condition}</td><td></td></tr>
                            <tr><th>Stock of Diesel for Genset as per Minimum order level </th><td>{gate.gm_Stock_of_Diesel_Genset}</td><td></td></tr>
                            <tr><th>Security Attendance</th><td>{gate.gm_Security_attendance}</td><td></td></tr>
                            <tr><th>Staff Attendance </th><td>{gate.gm_Staff_attendance}</td><td></td></tr>
                            <tr><th>Labour Attendance</th><td>{gate.gm_Labour_attendance}</td><td></td></tr>
                            <tr><th>Todays crucial shipment to be handled</th><td>{gate.gm_Todays_crucial_shipment_handled}</td><td>{gate.gm_Todays_crucial_shipment_handled_remark}</td></tr>
                            <tr><th>Yesterdays pending</th><td>{gate.gm_Yesterdays_pending}</td><td>{gate.gm_Yesterdays_pending_remark}</td></tr>
                            <tr><th>Customer complaints escalations received</th><td>{gate.gm_Customer_complaints_received}</td><td>{gate.gm_Customer_complaints_received_remark}</td></tr>
                            <tr><th>Action for today regarding Audit score improvement plan</th><td>{gate.gm_Audit_score_plan}</td><td>{gate.gm_Audit_score_plan_remark}</td></tr>
                            <tr><th>Floor pallets Stock Number of pallets</th><td>{gate.gm_Floor_pallets_Stock}</td><td></td></tr>
                            <tr><th>Any Approval from DGM pending </th><td>{gate.gm_Approval_DGM_pending}</td><td>{gate.gm_Approval_DGM_pending_remark}</td></tr>
                            <tr><th>Pending task to be completed today </th><td>{gate.gm_Pending_task_today}</td><td>{gate.gm_Pending_task_today_remark}</td></tr>
                        </tbody>
                    </table>

                    <br>

                    <p>Regards,<br><b>gate Meeting Admin</b></p>
                </body>
            </html>
        """

    send_department_email('itadmin',subject, email_body, recipient_list, email_type=1)

    gate_meet_email_count = gate_meet_email_count + 1
    Gatemeetinginfo.objects.filter(pk=gate_meet_id).update(gm_email_count=gate_meet_email_count)

    messages.success(request, "Gate Meeting email sent successfully.")

    return redirect(request.META.get('HTTP_REFERER', '/'))
