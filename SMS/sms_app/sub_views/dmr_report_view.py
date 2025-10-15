from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment

from ..models import TripdetailInfo, EnquirynoteInfo, ConsignmentdetailInfo, MyUser
from .send_department_email import send_department_email
from ..sub_forms.dmr_report_form import DmrForm
from ..sub_models.consignmentgoods_mod import ConsignmentgoodsInfo
from ..sub_models.customer_mod import CustomerInfo

@login_required(login_url='login_page')
def trip_report(request):
    first_name = request.session.get('first_name')
    form = DmrForm(request.POST or None)
    customer_id = request.POST.get('dmr_customer')

    trips = TripdetailInfo.objects.all().order_by('-tr_tripnumber')

    if customer_id:
        trips = trips.filter(tr_enquirynumber__en_customername_id=customer_id)

    for trip in trips:
        # 🔹 Attach consigner name from ConsignmentgoodsInfo
        consigner_name = ''
        try:
            consignment_goods = ConsignmentgoodsInfo.objects.filter(
                cg_consignmentnumber=trip.tr_consignmentnumber
            ).first()
            if consignment_goods and consignment_goods.cg_consigner:
                consigner_name = str(consignment_goods.cg_consigner)
        except Exception as e:
            print(f"Error fetching consigner for trip {trip.id}: {e}")
        trip.consigner_name = consigner_name

        # 🔹 Attach co_cusrefnum from ConsignmentdetailInfo
        co_cusrefnum = ''
        try:
            consignment = ConsignmentdetailInfo.objects.filter(
                co_consignmentnumber=trip.tr_consignmentnumber
            ).first()
            if consignment:
                co_cusrefnum = consignment.co_cusrefnum
        except Exception as e:
            print(f"Error fetching co_cusrefnum for trip {trip.id}: {e}")
        trip.co_cusrefnum = co_cusrefnum

    # Pagination
    paginator = Paginator(trips, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'first_name': first_name,
        'form': form,
        'page_obj': page_obj,
        'customer_id': customer_id or '',
    }

    return render(request, "asset_mgt_app/dmr_report.html", context)


@login_required(login_url='login_page')
def trip_send_email(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer_id')
        recipient = request.POST.get('recipient')
        subject = request.POST.get('subject')
        message_body = request.POST.get('message', '')

        if not customer_id:
            messages.error(request, "Please select a customer.")
            return redirect('trip_report')

        if not recipient:
            messages.error(request, "Please enter recipient emails.")
            return redirect('trip_report')

        # Get Customer object
        try:
            customer_obj = CustomerInfo.objects.get(id=customer_id)
        except CustomerInfo.DoesNotExist:
            messages.error(request, "Selected customer does not exist.")
            return redirect('trip_report')

        # Get trips for this customer
        trips = TripdetailInfo.objects.filter(tr_enquirynumber__en_customername_id=customer_id).order_by('-tr_tripnumber')

        # Generate Excel
        from openpyxl import Workbook
        from io import BytesIO

        wb = Workbook()
        ws = wb.active
        ws.title = "DMR Report"

        # Headers
        headers = [
            "SR. NO.", "TRIP DATE", "CONSIGNMENT NOTE NO", "CUSTOMER NAME", "CUSTOMER DEPT",
            "SHIPPER", "FROM", "TO", "VEH NO", "VEH TYPE", "TRIPCOST", "AAI CHARGES",
            "UNLOADING CHARGES", "LOADING CHARGES", "HALTING CHARGE", "HANDLING CHARGES",
            "SUPERVISOR CHARGES", "TOTAL CHARGES", "REFERENCE # (JOB ID/HAWB)",
            "VEH REPORTED KM @ LOADING POINT", "VEH REPORTED TIME @ LOADING POINT",
            "LOADING DATE", "LOADING TIME", "VEH REPORTED KM @ UNLOADING POINT",
            "VEH REPORTED TIME @ UNLOADING POINT", "UNLOADING DATE", "UNLOADING TIME",
            "NO OF HALTING DAYS"
        ]
        ws.append(headers)

        # Append trip data
        for idx, trip in enumerate(trips, start=1):
            consigner_name = ''
            co_cusrefnum = ''

            if trip.tr_consignmentnumber:
                try:
                    # Get consignment details
                    consignment = ConsignmentdetailInfo.objects.get(co_consignmentnumber=trip.tr_consignmentnumber)
                    co_cusrefnum = consignment.co_cusrefnum or ''

                    # Get consigner name from goods
                    consignment_goods = ConsignmentgoodsInfo.objects.filter(
                        cg_consignmentnumber=trip.tr_consignmentnumber).first()
                    if consignment_goods and consignment_goods.cg_consigner:
                        consigner_name = str(consignment_goods.cg_consigner)
                except ConsignmentdetailInfo.DoesNotExist:
                    co_cusrefnum = ''
                except Exception as e:
                    print(f"Error fetching consignment for trip {trip.id}: {e}")

            ws.append([
                idx,
                trip.tr_departeddate.strftime("%d-%m-%Y") if trip.tr_departeddate else '',
                str(trip.tr_consignmentnumber) if trip.tr_consignmentnumber else '',
                str(trip.tr_enquirynumber.en_customername) if trip.tr_enquirynumber else '',
                str(trip.tr_enquirynumber.en_customerdepartment) if trip.tr_enquirynumber else '',
                consigner_name,
                str(trip.tr_departedlocation) if trip.tr_departedlocation else '',
                str(trip.tr_reportedlocation) if trip.tr_reportedlocation else '',
                str(trip.tr_vehiclenumber) if trip.tr_vehiclenumber else '',
                str(trip.tr_vehicletype) if trip.tr_vehicletype else '',
                trip.tc_tripcost or 0,
                trip.tc_parkingcost or 0,
                trip.tc_unloadingcost or 0,
                trip.tc_loadingcost or 0,
                trip.tc_haltingcost or 0,
                trip.tc_handlingcost or 0,
                trip.tc_supervisorcost or 0,
                sum([
                    trip.tc_tripcost or 0,
                    trip.tc_parkingcost or 0,
                    trip.tc_unloadingcost or 0,
                    trip.tc_loadingcost or 0,
                    trip.tc_haltingcost or 0,
                    trip.tc_handlingcost or 0,
                    trip.tc_supervisorcost or 0
                ]),
                co_cusrefnum,  # 🔹 This will now appear in the Excel
                trip.tr_departedkm or 0,
                trip.tr_departeddate.strftime("%H:%M") if trip.tr_departeddate else '',
                trip.tr_loading_time.strftime("%d-%m-%Y") if trip.tr_loading_time else '',
                trip.tr_loading_time.strftime("%H:%M") if trip.tr_loading_time else '',
                trip.tr_reportedkm or 0,
                trip.tr_reporteddate.strftime("%H:%M") if trip.tr_reporteddate else '',
                trip.tr_unloading_time.strftime("%d-%m-%Y") if trip.tr_unloading_time else '',
                trip.tr_unloading_time.strftime("%H:%M") if trip.tr_unloading_time else '',
                trip.tc_no_of_days_halting or 0
            ])

        # Save to BytesIO
        excel_file = BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)

        # Prepare recipient list
        recipient_list = [x.strip() for x in recipient.split(',') if x.strip()]

        # Prepare email subject
        if not subject:
            subject = f"{customer_obj.cu_name}_DMRReport"

        # Send email with attachment
        file_name = f"{customer_obj.cu_name}_DMR_Report.xlsx"
        attachment = excel_file
        attachment_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

        send_department_email(
            department='itadmin',
            subject=subject,
            message=message_body,
            recipient_list=recipient_list,
            attachment=attachment,
            attachment_type=attachment_type,
            file_name=file_name
        )

        messages.success(request, f"Trip report sent successfully to {', '.join(recipient_list)}.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    messages.error(request, "Invalid request.")
    return redirect(request.META.get('HTTP_REFERER', '/'))
