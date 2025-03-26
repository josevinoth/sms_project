from django.contrib.auth.decorators import login_required
from ..forms import PerformanceauditForm
from ..models import PerformanceauditInfo
from django.shortcuts import render, redirect
from django.contrib import messages
from .send_department_email import send_department_email


@login_required(login_url='login_page')
def performanceaudit_add(request, perform_audit_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    enable = perform_audit_id != 0

    categories = {
        "Implementation of Takeaways and Directions": {"fields": ["pa_Listing_the_Take_ways_Directions", "pa_Owner_Defined_Trained", "pa_Periodical_Monitoring_template_provided",
        "pa_Progress_visibility","pa_Process_defined_followed","pa_Weekly_reporting_Management_progress","pa_Completed_Timeline",
        "pa_Outcome_reported_Management"]},
        "Staff Attendance and Timely Reporting": {"fields": [
            "pa_Timely_reporting_staffs_labourers", "pa_Attendance_thru_Biometric", "pa_Permissions_slip_provided_instances",
            "pa_Monthly_attendance_provided_HR_1st_working_day", "pa_Monthly_closing_process_followed", "pa_New_staff_formalities_followed",
            "pa_Resignation_process_followed"]},
        "Extended Working Hours": {"fields": ["pa_Is_extended_working_hours_agreed", "pa_Is_overtime_exceeded_per_law", "pa_Is_expenses_billed_back_customer"]},
        "Additional Labour Deployed / Labour Reduction": {"fields": ["pa_Labour_Addition_DGM_Approval", "pa_Adequate_Employee_compensation_insurance_taken",
        "pa_Reduction_labour_approval","pa_Finance_informed_salary_reduction"]},
        "Warehouse / Office Maintenance": {"fields": ["pa_Cleanliness_Office_Warehouse", "pa_Dump_seen_warehouse",
                                "pa_Empty_pallets_kept_order",
                                "pa_Pest_control_done_monthly", "pa_Cob_wires",
                                "pa_Leakages", "pa_Is_pathways_clean",
                                "pa_Fire_Extinguisher_easily_accessable", "pa_Daily_gate_meeting_photos_cleanliness",
                                "pa_First_box_compliance_standards", "pa_Adequate_Lighting_lights_functional"]},
        "Space Management": {"fields": ["pa_Physical_location_DSR_matching","pa_DG_cargo_handled_without_management_approval","pa_Idle_space_reported_management_time",
                                        "pa_Stacking_done_SOP_agreed","pa_Inter_change_of_Location"]},
        "WMS and Reports": {"fields": ["pa_WMS_usage", "pa_Any_back_date_entries",
                          "pa_AMC_contract_available", "pa_Periodical_service","pa_Reports_shared_per_calendar"]},
        "Customer Service / Retention / Development": {"fields": ["pa_DSR_Pre_alerts_working_days", "pa_Email_response_time", "pa_Escalations_customers",
                               "pa_Monthly_reviews_KAM_accounts",
                               "pa_Quarterly_reviews_Non_KAM_accounts", "pa_Conversion_customers_customers", "pa_Additional_business_Existing_customers",
                               "pa_Customer_Claims_NIL",
                               "pa_KAM_Program_followed_KAM_manual"]},
        "Compliance - Documentation / E-way bill / Invoice": {"fields": ["pa_All_shipments_dispatched", "pa_Clean_POD_obtained_all_dispatch",
                                "pa_All_PODs_scanned","pa_Safety_Security_compliance_followed","pa_HVC_checklist_prepared_scanned_WMS",
                                "pa_Workmen_compensation_insurance","pa_E_Way_bill_Ref_number_Validity","pa_Customer_Vendor_contracts_available",
                                "pa_Record_keeping_policy_followed","pa_Shop_Establishment_Compliance_audit_scores","pa_Only_Approved_vendors_engaged"]},
        "Controls on Cross Labelling": {
            "fields": ["pa_Is_double_check_done_dispatches", "pa_WMS_to_have_has_provision"]},
        "Stock": {"fields": ["pa_High_value_cargo_Daily_opening", "pa_Others_Physical_stock_count", "pa_Day_run_stock_done_WMS",
                                "pa_Closing_value_exceeding_Insurance", "pa_Excess_value_reported_Finance"]},
        "Manual Entries - WMS": {"fields": ["pa_Prior_approval_obtained", "pa_Regularised_Subsequently",
                               "pa_Stock_check_done"]},
        "Security Management": {"fields": ["pa_Valid_contract_place", "pa_Attendance","pa_Reporting","pa_Continuous_shifts","pa_Night_partrolling",
                                           "pa_Supervisor_visits_meeting","pa_WH_Key_management"]},
        "Procurement": {"fields": ["pa_Three_quotes_obtained", "pa_Procurement_done_time",]},
        "Month end details / Invoicing details / WMS month end closing ": {"fields": ["pa_Month_end_details_per_template",
                                    "pa_WMS_month_end_closing_Billing","pa_Providing_Reports_management" ]},
        "Incident and Accident": {"fields": ["pa_Incident_Accident_recorded", "pa_Reported_management_immediately", ]},
        "Sales Program / Sales meetings / Quotation management": {"fields": ["pa_Sales_calls_weekly_Sales_planning", "pa_Updating_all_sales","pa_New_customer_boarding"
                                        ,"pa_Meeting_new_customers","pa_Attending_sales_meeting"]},
        "Budget Vs Actuals, MIS Analysis and Reviews": {"fields": ["pa_WMS_updated_with_Budget", "pa_WMS_updated_with_Actuals",
                                        "pa_PL_customer_wise_unit_wise_business_model_wise","pa_Monthly_Sales_pl_budget_achieved",
                                        "pa_Budget_Actuals_Monthly","pa_MIS_analysis_meeting_Sony","pa_Action_points_arrive_based_MIS_Analysis_Meeting",
                                        "pa_Monthly_reviews_presentations","pa_Quarterly_reviews_presentations"]},
        "Travel and Outstation Managemnet": {"fields": ["pa_Monthly_visit_required_locations", "pa_Travel_made_BLR_per_agenda","pa_Travel_request_submitted_one_week",
                                   "pa_Details_travel_sent_Email","pa_Travel_report_discussed_Director" ]},
        "Warehouse Insurance": {"fields": ["pa_Insurance_policy_valid_throughout", "pa_Renewed_time","pa_All_units_covered_adequate_value"]},
        "Accounts Receivable": {"fields": ["pa_AR_more_than_15_days_of_credit_period", "pa_Weekly_AR_meeting_attended","pa_Very_precise_accurate_remarks_provided",
                                           "pa_AR_more_than_75_days_NIL","pa_Bad_debts_NIL"]},
        "Ops Audit Compliance": {"fields": ["pa_Internal_audit_score_card"]},
        "Vendor Management": {"fields": ["pa_Meeting_Vendors_Monthly_Report", "pa_Vendors_bills_submitted_time","pa_Data_asked_Finance_processing_PO" ]},
        "General": {"fields": ["pa_Daily_Gate_meeting_Supervisors_Labourers" ]},
    }
    category_counts = {}
    total_A = 0
    total_B = 0
    total_A_count = 0
    total_B_count = 0

    for category, data in categories.items():
        fields = data["fields"]

        count_A = sum(
            PerformanceauditInfo.objects.filter(id=perform_audit_id, **{f"{field}__exact": 1}).count()
            for field in fields
        )

        count_B = sum(
            PerformanceauditInfo.objects.filter(id=perform_audit_id, **{f"{field}__exact": 2}).count()
            for field in fields
        )

        total_A += count_A * 2
        total_B += count_B
        total_A_count += count_A
        total_B_count += count_B

        category_counts[category] = {
            "actual_score_A": count_A * 2,
            "actual_score_B": count_B,
        }
        overall_total_A = total_A
        overall_total_B = total_B

        total = overall_total_A + overall_total_B

    if request.method == "GET":
        if perform_audit_id == 0:
            print("I am inside Get add Ops Audit Score Card")
            form = PerformanceauditForm()
            context = {
                'form': form,
                'first_name': first_name,
                'user_id': user_id,
                'category_counts': category_counts,
                'overall_total_A': overall_total_A,
                'overall_total_B': overall_total_B,
                'total': total,
                'total_A_count': total_A_count,
                'total_B_count': total_B_count,


            }
        else:
            print("I am inside get edit Ops Audit Score Card")
            performaudit = PerformanceauditInfo.objects.get(pk=perform_audit_id)
            form = PerformanceauditForm(instance=performaudit)
            request.session['ses_perform_audit_id'] = perform_audit_id
            context = {
                'form': form,
                'first_name': first_name,
                'category_counts': category_counts,
                'overall_total_A': overall_total_A,
                'overall_total_B': overall_total_B,
                'total': total,
                'total_A_count': total_A_count,
                'total_B_count': total_B_count,
                'enable': enable,

            }

        return render(request, "asset_mgt_app/performance_audit_add.html", context)

    else:
        if perform_audit_id == 0:
            form = PerformanceauditForm(request.POST)
        else:
            performaudit = PerformanceauditInfo.objects.get(pk=perform_audit_id)
            form = PerformanceauditForm(request.POST, instance=performaudit)

        if form.is_valid():
            form.save()
            if perform_audit_id == 0:
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
def performanceaudit_list(request):
    first_name = request.session.get('first_name')
    context = {'performaudit_list' : PerformanceauditInfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/performance_audit_list.html",context)


#Delete
@login_required(login_url='login_page')
def performanceaudit_delete(request,perform_audit_id):
    performaudit = PerformanceauditInfo.objects.get(pk=perform_audit_id)
    performaudit.delete()
    return redirect('/SMS/performance_audit_list')


@login_required(login_url='login_page')
def send_performance_audit_email(request):
    perform_audit_id = request.session.get('ses_perform_audit_id')
    print('perform_audit_id', perform_audit_id)

    performance_audit_entry = PerformanceauditInfo.objects.filter(id=perform_audit_id).first()

    branch = performance_audit_entry.pa_branch
    unit = performance_audit_entry.pa_unit
    date = performance_audit_entry.pa_date

    categories = {
        "Implementation of Takeaways and Directions": {
            "fields": ["pa_Listing_the_Take_ways_Directions", "pa_Owner_Defined_Trained",
                       "pa_Periodical_Monitoring_template_provided",
                       "pa_Progress_visibility", "pa_Process_defined_followed",
                       "pa_Weekly_reporting_Management_progress", "pa_Completed_Timeline",
                       "pa_Outcome_reported_Management"]},
        "Staff Attendance and Timely Reporting": {"fields": [
            "pa_Timely_reporting_staffs_labourers", "pa_Attendance_thru_Biometric",
            "pa_Permissions_slip_provided_instances",
            "pa_Monthly_attendance_provided_HR_1st_working_day", "pa_Monthly_closing_process_followed",
            "pa_New_staff_formalities_followed",
            "pa_Resignation_process_followed"]},
        "Extended Working Hours": {"fields": ["pa_Is_extended_working_hours_agreed", "pa_Is_overtime_exceeded_per_law",
                                              "pa_Is_expenses_billed_back_customer"]},
        "Additional Labour Deployed / Labour Reduction": {
            "fields": ["pa_Labour_Addition_DGM_Approval", "pa_Adequate_Employee_compensation_insurance_taken",
                       "pa_Reduction_labour_approval", "pa_Finance_informed_salary_reduction"]},
        "Warehouse / Office Maintenance": {"fields": ["pa_Cleanliness_Office_Warehouse", "pa_Dump_seen_warehouse",
                                                      "pa_Empty_pallets_kept_order",
                                                      "pa_Pest_control_done_monthly", "pa_Cob_wires",
                                                      "pa_Leakages", "pa_Is_pathways_clean",
                                                      "pa_Fire_Extinguisher_easily_accessable",
                                                      "pa_Daily_gate_meeting_photos_cleanliness",
                                                      "pa_First_box_compliance_standards",
                                                      "pa_Adequate_Lighting_lights_functional"]},
        "Space Management": {
            "fields": ["pa_Physical_location_DSR_matching", "pa_DG_cargo_handled_without_management_approval",
                       "pa_Idle_space_reported_management_time",
                       "pa_Stacking_done_SOP_agreed", "pa_Inter_change_of_Location"]},
        "WMS and Reports": {"fields": ["pa_WMS_usage", "pa_Any_back_date_entries",
                                       "pa_AMC_contract_available", "pa_Periodical_service",
                                       "pa_Reports_shared_per_calendar"]},
        "Customer Service / Retention / Development": {
            "fields": ["pa_DSR_Pre_alerts_working_days", "pa_Email_response_time", "pa_Escalations_customers",
                       "pa_Monthly_reviews_KAM_accounts",
                       "pa_Quarterly_reviews_Non_KAM_accounts", "pa_Conversion_customers_customers",
                       "pa_Additional_business_Existing_customers",
                       "pa_Customer_Claims_NIL",
                       "pa_KAM_Program_followed_KAM_manual"]},
        "Compliance - Documentation / E-way bill / Invoice": {
            "fields": ["pa_All_shipments_dispatched", "pa_Clean_POD_obtained_all_dispatch",
                       "pa_All_PODs_scanned", "pa_Safety_Security_compliance_followed",
                       "pa_HVC_checklist_prepared_scanned_WMS",
                       "pa_Workmen_compensation_insurance", "pa_E_Way_bill_Ref_number_Validity",
                       "pa_Customer_Vendor_contracts_available",
                       "pa_Record_keeping_policy_followed", "pa_Shop_Establishment_Compliance_audit_scores",
                       "pa_Only_Approved_vendors_engaged"]},
        "Controls on Cross Labelling": {
            "fields": ["pa_Is_double_check_done_dispatches", "pa_WMS_to_have_has_provision"]},
        "Stock": {"fields": ["pa_High_value_cargo_Daily_opening", "pa_Others_Physical_stock_count",
                             "pa_Day_run_stock_done_WMS",
                             "pa_Closing_value_exceeding_Insurance", "pa_Excess_value_reported_Finance"]},
        "Manual Entries - WMS": {"fields": ["pa_Prior_approval_obtained", "pa_Regularised_Subsequently",
                                            "pa_Stock_check_done"]},
        "Security Management": {
            "fields": ["pa_Valid_contract_place", "pa_Attendance", "pa_Reporting", "pa_Continuous_shifts",
                       "pa_Night_partrolling",
                       "pa_Supervisor_visits_meeting", "pa_WH_Key_management"]},
        "Procurement": {"fields": ["pa_Three_quotes_obtained", "pa_Procurement_done_time", ]},
        "Month end details / Invoicing details / WMS month end closing  / Reports to Management": {
            "fields": ["pa_Month_end_details_per_template",
                       "pa_WMS_month_end_closing_Billing", "pa_Providing_Reports_management"]},
        "Incident and Accident": {"fields": ["pa_Incident_Accident_recorded", "pa_Reported_management_immediately", ]},
        "Sales Program / Sales meetings / Quotation management": {
            "fields": ["pa_Sales_calls_weekly_Sales_planning", "pa_Updating_all_sales", "pa_New_customer_boarding"
                , "pa_Meeting_new_customers", "pa_Attending_sales_meeting"]},
        "Budget Vs Actuals, MIS Analysis and Reviews": {
            "fields": ["pa_WMS_updated_with_Budget", "pa_WMS_updated_with_Actuals",
                       "pa_PL_customer_wise_unit_wise_business_model_wise", "pa_Monthly_Sales_pl_budget_achieved",
                       "pa_Budget_Actuals_Monthly", "pa_MIS_analysis_meeting_Sony",
                       "pa_Action_points_arrive_based_MIS_Analysis_Meeting",
                       "pa_Monthly_reviews_presentations", "pa_Quarterly_reviews_presentations"]},
        "Travel and Outstation Managemnet": {
            "fields": ["pa_Monthly_visit_required_locations", "pa_Travel_made_BLR_per_agenda",
                       "pa_Travel_request_submitted_one_week",
                       "pa_Details_travel_sent_Email", "pa_Travel_report_discussed_Director"]},
        "Warehouse Insurance": {"fields": ["pa_Insurance_policy_valid_throughout", "pa_Renewed_time",
                                           "pa_All_units_covered_adequate_value"]},
        "Accounts Receivable": {"fields": ["pa_AR_more_than_15_days_of_credit_period", "pa_Weekly_AR_meeting_attended",
                                           "pa_Very_precise_accurate_remarks_provided",
                                           "pa_AR_more_than_75_days_NIL", "pa_Bad_debts_NIL"]},
        "Ops Audit Compliance": {"fields": ["pa_Internal_audit_score_card"]},
        "Vendor Management": {"fields": ["pa_Meeting_Vendors_Monthly_Report", "pa_Vendors_bills_submitted_time",
                                         "pa_Data_asked_Finance_processing_PO"]},
        "General": {"fields": ["pa_Daily_Gate_meeting_Supervisors_Labourers"]},
    }

    category_counts = {}
    total_A = 0
    total_B = 0
    total_A_count = 0
    total_B_count = 0

    for category, data in categories.items():
        fields = data["fields"]

        count_A = sum(
            PerformanceauditInfo.objects.filter(id=perform_audit_id, **{f"{field}__exact": 1}).count()
            for field in fields
        )

        count_B = sum(
            PerformanceauditInfo.objects.filter(id=perform_audit_id, **{f"{field}__exact": 2}).count()
            for field in fields
        )

        total_A += count_A * 2
        total_B += count_B
        total_A_count += count_A
        total_B_count += count_B

        category_counts[category] = {
            "actual_score_A": count_A * 2,
            "actual_score_B": count_B,
        }
        overall_total_A = total_A
        overall_total_B = total_B

        total = overall_total_A + overall_total_B


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
                <tr><th>Branch</th><td>{branch}</td></tr>
                <tr><th>Unit</th><td>{unit}</td></tr>
                <tr><th>Date</th><td>{date}</td></tr>
            </table>
            <table>
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Actual Score A</th>
                        <th>Actual Score B</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(f'<tr><td>{cat}</td><td>{data["actual_score_A"]}</td><td>{data["actual_score_B"]}</td></tr>' for cat, data in category_counts.items())}
                </tbody>
            </table>
            <table>
                <tr><th>No. of Questions for - A </th><td>{total_A_count} </td></tr>
                <tr><th>No. of Questions for - B</th><td>{total_B_count} </td></tr>
                <tr><th>Total Marks for - A</th><td>{overall_total_A} </td></tr>
                <tr><th>Total Marks for - B</th><td>{overall_total_B}</td></tr>
                <tr><th>Total</th><td>{total}</td></tr>
            </table>
            <br>
            <p>Regards,<br><b> Performance Audit Admin</b></p>
        </body>
    </html>
    """

    recipient_list = ['hariharasudhanh968@gmail.com',]

    subject = f"Performance Audit Scorecard Report - "

    send_department_email('itadmin', subject, email_body, recipient_list, email_type=1)

    messages.success(request, "Ops Audit Scorecard email sent successfully.")

    return redirect(request.META.get('HTTP_REFERER', '/'))
