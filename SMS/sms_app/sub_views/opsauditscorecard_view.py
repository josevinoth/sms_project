from django.contrib.auth.decorators import login_required
from ..forms import OpsauditscorecardForm
from ..models import OpsauditscorecardInfo
from django.shortcuts import render, redirect
from django.contrib import messages
from .send_department_email import send_department_email


@login_required(login_url='login_page')
def opsauditscorecard_add(request, ops_audit_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    categories = {
        "Admin": {"fields": ["ops_weighing_scale_calibration", "ops_calibration_equipment_list", "ops_AMC_contracts"],
                  "expected_score": 3},
        "CCTV": {"fields": [
            "ops_CCTV_availability_working_condition", "ops_CCTV_DVR_kept_under_lock", "ops_CCTV_AMC",
            "ops_CCTV_maintenance_reports", "ops_CCTV_monthly_visits", "ops_CCTV_monthly_report_observations",
            "ops_CCTV_image_quality", "ops_CCTV_cleaning_of_lenses", "ops_CCTV_positioning", "ops_CCTV_UPS",
            "ops_CCTV_record_availability_30_days", "ops_CCTV_storage_data_90_days"], "expected_score": 12},
        "Compliance": {"fields": ["ops_S_E_registration", "ops_CLRA_certification", "ops_insurance_policy_validity",
                                  "ops_Contract_validity"], "expected_score": 4},
        "Customer": {"fields": ["ops_incident_accident_reporting", "ops_monthly_reviews_done"], "expected_score": 2},
        "Facility": {"fields": ["ops_entry_ways_clean", "ops_facility_exterior_interior_scrap",
                                "ops_exterior_walls_clean_cracks",
                                "ops_No_broken_windows_glass", "ops_all_dock_good_working_condition",
                                "ops_adequate_lights_loading_unloading", "ops_adequate_lights_CCTV_coverage",
                                "ops_dock_leveller_used_sheets_used", "ops_warehouse_cleanliness",
                                "ops_open_carton_boxes_items", "ops_dumping_cargo"], "expected_score": 11},
        "Finance": {"fields": ["ops_timely_accurate_billing"], "expected_score": 1},
        "HR": {"fields": ["ops_staff_attendance", "ops_working_hours_information_board",
                          "ops_employees_wearing_company_issued_badges", "ops_manpower_contract"],
               "expected_score": 4},
        "Process": {"fields": ["ops_vehicle_inward_register", "ops_truck_validation", "ops_driver_validation",
                               "ops_document_validation",
                               "ops_shipment_validation", "ops_check_OSD_packages", "ops_driver_ACk_copy",
                               "ops_shipment_weighment_process",
                               "ops_shipment_dimensions_process", "ops_cargo_storage_stacking_SOP",
                               "ops_more_than_3_days_cargo_report_mail",
                               "ops_dispatch_process", "ops_receive_print_tally_airline_labels",
                               "ops_double_check_shipments",
                               "ops_Truck_validation", "ops_Driver_validation", "ops_Document_validation",
                               "ops_check_OSD_Packages",
                               "ops_OTL_process", "ops_gate_Pass", "ops_outward_dispatch_register",
                               "ops_seal_integrity_prior_unsealing_unloading",
                               "ops_stacking"], "expected_score": 23},
        "Reports": {"fields": ["ops_daily_stock_register", "ops_daily_weekly_physical_stock_report"],
                    "expected_score": 2},
        "Safety": {
            "fields": ["ops_are_handlers_wearing_reflective_vests", "ops_are_loaders_handlers_wearing_safety_shoes",
                       "ops_are_fire_extinguishers_present_validity",
                       "ops_fire_extinguishers_access_clear_without_hindrance",
                       "ops_fire_alarm_system_working_condition", "ops_first_aid_box", "ops_DG_cargo"],
            "expected_score": 7},
        "Security": {"fields": ["ops_warehouse_key_register", "ops_facility_opening_checklist", "ops_high_value_cargo",
                                "ops_seal_inventory_usage_records", "ops_warehouse_office_key_control",
                                "ops_authorized_personnel_display_available", "ops_checklist_facility_closing",
                                "ops_intrusion_alarm_systems_availability",
                                "ops_emergency_contact_names_numbers_display",
                                "ops_each_employee_alarm_code_password_unique", "ops_daily_trash_checklist",
                                "ops_key_index_form", "ops_no_of_security_available_contract",
                                "ops_whether_continuous_shift_not",
                                "ops_last_30_days_CCTV_check_random_absence_sleeping",
                                "ops_registers_maintained_properly_not",
                                "ops_security_attire", "ops_supervisor_visit", "ops_night_visit_check",
                                "ops_night_hourly_pictures_captured_CCTV",
                                "ops_seal_inventory_proper_maintenance_storage"], "expected_score": 21},
        "Systems": {"fields": ["ops_are_systems_unique_and_password_protected", "ops_unused_systems_equipment",
                               "ops_condition_system_keeping_maintenance",
                               "ops_AMC_systems", "ops_to_check_inspection_report_system_maintenance"],
                    "expected_score": 5},
        "Visitors": {"fields": ["ops_visitor_log", "ops_visitor_badges_are_present_log"], "expected_score": 2},
        "WMS Usage": {"fields": ["ops_timely_complete_data_entry", "ops_rate_updation_contract_updation",
                                 "ops_reports_including_DSR_correctness"], "expected_score": 3},
    }

    category_counts = {}
    for category, data in categories.items():
        fields = data["fields"]
        count = sum(OpsauditscorecardInfo.objects.filter(**{f"{field}__exact": "1"}).count() for field in fields)
        category_counts[category] = {
            "actual_score": count,
            "expected_score": data["expected_score"]
        }
    overall_expected_count = sum(data["expected_score"] for data in categories.values())
    overall_total_yes = sum(item["actual_score"] for item in category_counts.values())


    if request.method == "GET":
        if ops_audit_id == 0:
            print("I am inside Get add Ops Audit Score Card")
            form = OpsauditscorecardForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'category_counts': category_counts,
                'overall_total_yes': overall_total_yes,
                'overall_expected_count': overall_expected_count,
            }
        else:
            print("I am inside get edit Ops Audit Score Card")
            opsaudit = OpsauditscorecardInfo.objects.get(pk=ops_audit_id)
            form = OpsauditscorecardForm(instance=opsaudit)
            request.session['ses_ops_audit_id'] = ops_audit_id

            context = {
                'form': form,
                'first_name': first_name,
                'category_counts': category_counts,
                'overall_total_yes': overall_total_yes,
                'overall_expected_count': overall_expected_count,
            }

        return render(request, "asset_mgt_app/opsauditscorecard_add.html", context)

    else:
        if ops_audit_id == 0:
            form = OpsauditscorecardForm(request.POST)
        else:
            opsaudit = OpsauditscorecardInfo.objects.get(pk=ops_audit_id)
            form = OpsauditscorecardForm(request.POST, instance=opsaudit)

        if form.is_valid():
            form.save()
            if ops_audit_id == 0:
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
def opsauditscorecard_list(request):
    first_name = request.session.get('first_name')
    context = {'ops_audit_list' : OpsauditscorecardInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/opsauditscorecard_list.html",context)


#Delete
@login_required(login_url='login_page')
def opsauditscorecard_delete(request,ops_audit_id):
    opsaudit = OpsauditscorecardInfo.objects.get(pk=ops_audit_id)
    opsaudit.delete()
    return redirect('/SMS/ops_audit_score_list')


@login_required(login_url='login_page')
def send_ops_audit_email(request):
    ops_audit_id = request.session.get('ses_ops_audit_id')
    print('ops_audit_id',ops_audit_id)
    categories = {
        "Admin": {"fields": ["ops_weighing_scale_calibration", "ops_calibration_equipment_list", "ops_AMC_contracts"],
                  "expected_score": 3},
        "CCTV": {"fields": [
            "ops_CCTV_availability_working_condition", "ops_CCTV_DVR_kept_under_lock", "ops_CCTV_AMC",
            "ops_CCTV_maintenance_reports", "ops_CCTV_monthly_visits", "ops_CCTV_monthly_report_observations",
            "ops_CCTV_image_quality", "ops_CCTV_cleaning_of_lenses", "ops_CCTV_positioning", "ops_CCTV_UPS",
            "ops_CCTV_record_availability_30_days", "ops_CCTV_storage_data_90_days"], "expected_score": 12},
        "Compliance": {"fields": ["ops_S_E_registration", "ops_CLRA_certification", "ops_insurance_policy_validity",
                                  "ops_Contract_validity"], "expected_score": 4},
        "Customer": {"fields": ["ops_incident_accident_reporting", "ops_monthly_reviews_done"], "expected_score": 2},
        "Facility": {"fields": ["ops_entry_ways_clean", "ops_facility_exterior_interior_scrap",
                                "ops_exterior_walls_clean_cracks",
                                "ops_No_broken_windows_glass", "ops_all_dock_good_working_condition",
                                "ops_adequate_lights_loading_unloading", "ops_adequate_lights_CCTV_coverage",
                                "ops_dock_leveller_used_sheets_used", "ops_warehouse_cleanliness",
                                "ops_open_carton_boxes_items", "ops_dumping_cargo"], "expected_score": 11},
        "Finance": {"fields": ["ops_timely_accurate_billing"], "expected_score": 1},
        "HR": {"fields": ["ops_staff_attendance", "ops_working_hours_information_board",
                          "ops_employees_wearing_company_issued_badges", "ops_manpower_contract"],
               "expected_score": 4},
        "Process": {"fields": ["ops_vehicle_inward_register", "ops_truck_validation", "ops_driver_validation",
                               "ops_document_validation",
                               "ops_shipment_validation", "ops_check_OSD_packages", "ops_driver_ACk_copy",
                               "ops_shipment_weighment_process",
                               "ops_shipment_dimensions_process", "ops_cargo_storage_stacking_SOP",
                               "ops_more_than_3_days_cargo_report_mail",
                               "ops_dispatch_process", "ops_receive_print_tally_airline_labels",
                               "ops_double_check_shipments",
                               "ops_Truck_validation", "ops_Driver_validation", "ops_Document_validation",
                               "ops_check_OSD_Packages",
                               "ops_OTL_process", "ops_gate_Pass", "ops_outward_dispatch_register",
                               "ops_seal_integrity_prior_unsealing_unloading",
                               "ops_stacking"], "expected_score": 23},
        "Reports": {"fields": ["ops_daily_stock_register", "ops_daily_weekly_physical_stock_report"],
                    "expected_score": 2},
        "Safety": {
            "fields": ["ops_are_handlers_wearing_reflective_vests", "ops_are_loaders_handlers_wearing_safety_shoes",
                       "ops_are_fire_extinguishers_present_validity",
                       "ops_fire_extinguishers_access_clear_without_hindrance",
                       "ops_fire_alarm_system_working_condition", "ops_first_aid_box", "ops_DG_cargo"],
            "expected_score": 7},
        "Security": {"fields": ["ops_warehouse_key_register", "ops_facility_opening_checklist", "ops_high_value_cargo",
                                "ops_seal_inventory_usage_records", "ops_warehouse_office_key_control",
                                "ops_authorized_personnel_display_available", "ops_checklist_facility_closing",
                                "ops_intrusion_alarm_systems_availability",
                                "ops_emergency_contact_names_numbers_display",
                                "ops_each_employee_alarm_code_password_unique", "ops_daily_trash_checklist",
                                "ops_key_index_form", "ops_no_of_security_available_contract",
                                "ops_whether_continuous_shift_not",
                                "ops_last_30_days_CCTV_check_random_absence_sleeping",
                                "ops_registers_maintained_properly_not",
                                "ops_security_attire", "ops_supervisor_visit", "ops_night_visit_check",
                                "ops_night_hourly_pictures_captured_CCTV",
                                "ops_seal_inventory_proper_maintenance_storage"], "expected_score": 21},
        "Systems": {"fields" : ["ops_are_systems_unique_and_password_protected", "ops_unused_systems_equipment",
                               "ops_condition_system_keeping_maintenance",
                               "ops_AMC_systems", "ops_to_check_inspection_report_system_maintenance"],
                    "expected_score": 5},
        "Visitors": {"fields": ["ops_visitor_log", "ops_visitor_badges_are_present_log"], "expected_score": 2},
        "WMS Usage": {"fields": ["ops_timely_complete_data_entry", "ops_rate_updation_contract_updation",
                                 "ops_reports_including_DSR_correctness"], "expected_score": 3},
    }

    category_counts = {}
    for category, data in categories.items():
        fields = data["fields"]
        count = sum(OpsauditscorecardInfo.objects.filter(**{f"{field}__exact": "1"}).count() for field in fields)
        category_counts[category] = {
            "actual_score": count,
            "expected_score": data["expected_score"]
        }

    overall_expected_count = sum(data["expected_score"] for data in categories.values())
    overall_total_yes = sum(item["actual_score"] for item in category_counts.values())

    audit_info = OpsauditscorecardInfo.objects.first()
    location = audit_info.ops_branch
    branch = audit_info.ops_unit
    date = audit_info.ops_date
    start_date = audit_info.ops_audit_start_date
    end_date = audit_info.ops_audit_end_date

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
            </style>
        </head>
        <body>
            <p>Dear Team,</p>
            <p>Please find below the Ops Audit Scorecard details:</p>
            <table>
                <tr><th>Location</th><td>{location}</td></tr>
                <tr><th>Branch</th><td>{branch}</td></tr>
                <tr><th>Date</th><td>{date}</td></tr>
                <tr><th>Audit Start Date</th><td>{start_date}</td></tr>
                <tr><th>Audit End Date</th><td>{end_date}</td></tr>
            </table>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Expected Score</th>
                        <th>Actual Score</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(f'<tr><td>{cat}</td><td>{data["expected_score"]}</td><td>{data["actual_score"]}</td></tr>' for cat, data in category_counts.items())}
                </tbody>
            </table>
            <table>
                <tr><th>Overall Score</th><td>{ overall_expected_count} / {overall_total_yes}</td></tr>
            </table>

            <br>
            <p>Regards,<br><b> Ops Audit Admin</b></p>
        </body>
    </html>
    """

    recipient_list = [
        'hariharasudhanh968@gmail.com',
    ]

    subject = f"Ops Audit Scorecard Report - "

    send_department_email('itadmin', subject, email_body, recipient_list, email_type=1)

    messages.success(request, "Ops Audit Scorecard email sent successfully.")

    return redirect(request.META.get('HTTP_REFERER', '/'))
