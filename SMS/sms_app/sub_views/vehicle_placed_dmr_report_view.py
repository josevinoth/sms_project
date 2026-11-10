import json
from datetime import datetime, date, timedelta
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from collections import defaultdict

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from ..models import Vehicle_allotmentInfo, DmrInfo


def _parse_dates(request):
    """
    Utility to parse from_date and to_date from request.
    If not provided, returns None and empty strings so that NO default date filter is imposed.
    """
    from_date_str = (request.GET.get('from_date') or request.POST.get('from_date') or '').strip()
    to_date_str = (request.GET.get('to_date') or request.POST.get('to_date') or '').strip()

    from_date = None
    if from_date_str:
        try:
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
        except ValueError:
            from_date = None
            from_date_str = ''

    to_date = None
    if to_date_str:
        try:
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
        except ValueError:
            to_date = None
            to_date_str = ''

    return from_date, to_date, from_date_str, to_date_str


def _fetch_report_data(from_date, to_date, branch):
    """
    Fetches daily counts for vehicles placed and DMR emails dispatched,
    linking the customers with vehicles placed against DMR email dispatch status.
    """
    allots_qs = Vehicle_allotmentInfo.objects.exclude(va_status_id__in=[2, 4])
    dmr_qs = DmrInfo.objects.select_related('dmr_customer', 'dmr_sent_by').all().order_by('-dmr_sent_at')

    if branch == "MAA":
        allots_qs = allots_qs.filter(va_enquirynumber__en_enquirynumber__icontains="MAA")
        dmr_qs = dmr_qs.filter(dmr_customer__cu_name__icontains="MAA")
    elif branch == "BLR":
        allots_qs = allots_qs.filter(va_enquirynumber__en_enquirynumber__icontains="BLR")
        dmr_qs = dmr_qs.filter(dmr_customer__cu_name__icontains="BLR")
    elif branch:
        allots_qs = allots_qs.filter(va_enquirynumber__en_enquirynumber__icontains=branch)
        dmr_qs = dmr_qs.filter(dmr_customer__cu_name__icontains=branch)

    if from_date:
        allots_qs = allots_qs.filter(va_created_at__date__gte=from_date)
        dmr_qs = dmr_qs.filter(dmr_sent_at__date__gte=from_date)

    if to_date:
        allots_qs = allots_qs.filter(va_created_at__date__lte=to_date)
        dmr_qs = dmr_qs.filter(dmr_sent_at__date__lte=to_date)

    # 1. Grouped query: Placements by Date and Customer
    allots_by_date_cust = (
        allots_qs
        .annotate(d=TruncDate('va_created_at'))
        .values('d', 'va_enquirynumber__en_customername__id', 'va_enquirynumber__en_customername__cu_name')
        .annotate(placed_cnt=Count('id'))
        .order_by('-d', '-placed_cnt')
    )

    placed_cust_map = defaultdict(dict)  # d -> {cust_id: (cust_name, placed_cnt)}
    placed_totals = defaultdict(int)     # d -> total placed

    for item in allots_by_date_cust:
        d = item['d']
        if not d:
            continue
        cid = item['va_enquirynumber__en_customername__id']
        cname = item['va_enquirynumber__en_customername__cu_name'] or "N/A"
        cnt = item['placed_cnt']
        placed_cust_map[d][cid] = (cname, cnt)
        placed_totals[d] += cnt

    # 2. Grouped query: DMR Emails by Date and Customer
    dmr_cust_map = defaultdict(lambda: defaultdict(list))  # d -> {cust_id: [log_item, ...]}
    dmr_totals = defaultdict(int)                          # d -> total dmr sent
    full_dmr_log_list = []

    for log in dmr_qs:
        local_dt = timezone.localtime(log.dmr_sent_at) if log.dmr_sent_at else None
        d = local_dt.date() if local_dt else None
        if not d:
            continue

        cid = log.dmr_customer_id
        cname = log.dmr_customer.cu_name if log.dmr_customer else "N/A"
        sent_by_name = ""
        if log.dmr_sent_by:
            sent_by_name = log.dmr_sent_by.get_full_name() or log.dmr_sent_by.username

        log_item = {
            'id': log.id,
            'date': d.strftime('%d-%m-%Y'),
            'date_iso': d.strftime('%Y-%m-%d'),
            'time': local_dt.strftime('%I:%M %p') if local_dt else '-',
            'customer_name': cname,
            'recipient': log.dmr_recipient or '-',
            'cc': log.dmr_cc or '-',
            'sent_by': sent_by_name or 'System'
        }

        full_dmr_log_list.append(log_item)
        dmr_cust_map[d][cid].append(log_item)
        dmr_totals[d] += 1

    today = timezone.localtime(timezone.now()).date()

    if from_date and to_date:
        dates_list = []
        curr = to_date
        while curr >= from_date:
            dates_list.append(curr)
            curr -= timedelta(days=1)
    elif from_date:
        dates_list = []
        curr = today
        while curr >= from_date:
            dates_list.append(curr)
            curr -= timedelta(days=1)
    else:
        # Default state: No date filter applied. Show all dates with data.
        raw_dates = set([d for d in list(placed_totals.keys()) + list(dmr_totals.keys()) if d is not None])
        if to_date:
            raw_dates = set([d for d in raw_dates if d <= to_date])
        raw_dates.add(today)
        dates_list = sorted(raw_dates, reverse=True)

    daily_data = []
    customer_breakdown_by_date = {}  # date_iso -> list of customer records
    total_placed = 0
    total_dmr_sent = 0

    for d in dates_list:
        p_count = placed_totals.get(d, 0)
        d_count = dmr_totals.get(d, 0)
        date_iso = d.strftime('%Y-%m-%d')
        date_str = d.strftime('%d-%m-%Y')

        # Combine all customers for this date (both placed and emailed)
        cust_placed_dict = placed_cust_map.get(d, {})
        cust_dmr_dict = dmr_cust_map.get(d, {})
        all_cids = set(list(cust_placed_dict.keys()) + list(cust_dmr_dict.keys()))

        cust_breakdown = []
        for cid in all_cids:
            cname, p_cnt = cust_placed_dict.get(cid, ("N/A", 0))
            dmr_logs = cust_dmr_dict.get(cid, [])
            is_sent = len(dmr_logs) > 0

            # If customer name is still N/A, try to get from DMR logs
            if cname == "N/A" and dmr_logs:
                cname = dmr_logs[0]['customer_name']

            cust_breakdown.append({
                'customer_name': cname,
                'vehicles_placed': p_cnt,
                'dmr_sent': is_sent,
                'dmr_status': 'Sent' if is_sent else 'Pending',
                'dmr_time': dmr_logs[0]['time'] if is_sent else '-',
                'dmr_recipient': dmr_logs[0]['recipient'] if is_sent else '-',
                'dmr_sent_by': dmr_logs[0]['sent_by'] if is_sent else '-'
            })

        # Sort: Highest placements first, then sent status
        cust_breakdown.sort(key=lambda x: (x['vehicles_placed'], x['dmr_sent']), reverse=True)
        customer_breakdown_by_date[date_iso] = cust_breakdown

        daily_data.append({
            'date': date_str,
            'date_iso': date_iso,
            'day_name': d.strftime('%A'),
            'vehicles_placed': p_count,
            'dmr_mails_sent': d_count,
            'has_details': (p_count > 0 or d_count > 0),
        })

        total_placed += p_count
        total_dmr_sent += d_count

    return daily_data, total_placed, total_dmr_sent, full_dmr_log_list, customer_breakdown_by_date


@login_required(login_url='login_page')
def vehicle_placed_dmr_report_view(request):
    """
    Clean 2-column report against Date:
    1. Date
    2. Vehicles Placed
    3. DMR Mails Sent
    Eyeball button shows the customer-level breakdown of placed vehicles against DMR dispatch status.
    """
    first_name = request.session.get('first_name')
    from_date, to_date, from_date_str, to_date_str = _parse_dates(request)
    branch = (request.GET.get('branch') or request.POST.get('branch') or '').strip()

    daily_data, total_placed, total_dmr_sent, full_dmr_log_list, cust_breakdown_map = _fetch_report_data(from_date, to_date, branch)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'status': True,
            'daily_data': daily_data,
            'total_placed': total_placed,
            'total_dmr_sent': total_dmr_sent,
            'full_dmr_log_list': full_dmr_log_list,
            'customer_breakdown': cust_breakdown_map
        })

    return render(request, "asset_mgt_app/vehicle_placed_dmr_report.html", {
        'first_name': first_name,
        'from_date': from_date_str,
        'to_date': to_date_str,
        'branch': branch,
        'daily_data': daily_data,
        'total_placed': total_placed,
        'total_dmr_sent': total_dmr_sent,
        'full_dmr_log_list': full_dmr_log_list,
        'customer_breakdown_json': json.dumps(cust_breakdown_map),
    })


@login_required(login_url='login_page')
def vehicle_placed_dmr_export_excel(request):
    """
    Exports clean 2-column report against Date to Excel,
    including a dedicated customer-level breakdown sheet.
    """
    from_date, to_date, from_date_str, to_date_str = _parse_dates(request)
    branch = (request.GET.get('branch') or request.POST.get('branch') or '').strip()

    daily_data, total_placed, total_dmr_sent, full_dmr_log_list, cust_breakdown_map = _fetch_report_data(from_date, to_date, branch)

    wb = Workbook()

    # ════ SHEET 1: Daily Summary ════
    ws1 = wb.active
    ws1.title = "Daily Summary"

    headers1 = ["S.No", "Date", "Day", "Vehicles Placed", "DMR Mails Sent"]
    ws1.append(headers1)

    s_no = 1
    for row in daily_data:
        ws1.append([
            s_no,
            row['date'],
            row['day_name'],
            row['vehicles_placed'],
            row['dmr_mails_sent']
        ])
        s_no += 1

    total_row = ["TOTAL", "", "", total_placed, total_dmr_sent]
    ws1.append(total_row)

    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    for cell in ws1[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    last_row1 = ws1.max_row
    total_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    total_font = Font(name="Calibri", size=11, bold=True, color="000000")
    for cell in ws1[last_row1]:
        cell.fill = total_fill
        cell.font = total_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    for r in range(2, last_row1 + 1):
        for cell in ws1[r]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

    ws1.column_dimensions['A'].width = 10
    ws1.column_dimensions['B'].width = 18
    ws1.column_dimensions['C'].width = 16
    ws1.column_dimensions['D'].width = 22
    ws1.column_dimensions['E'].width = 22

    # ════ SHEET 2: Customer Placed vs DMR Status ════
    ws2 = wb.create_sheet(title="Customer Placed & DMR")
    headers2 = ["S.No", "Date", "Customer Name", "Vehicles Placed", "DMR Mail Status", "Dispatch Time", "Recipient (To)", "Sent By"]
    ws2.append(headers2)

    for cell in ws2[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    log_sno = 1
    for date_iso, cust_list in cust_breakdown_map.items():
        for item in cust_list:
            ws2.append([
                log_sno,
                date_iso,
                item['customer_name'],
                item['vehicles_placed'],
                item['dmr_status'],
                item['dmr_time'],
                item['dmr_recipient'],
                item['dmr_sent_by']
            ])
            log_sno += 1

    last_row2 = ws2.max_row
    for r in range(2, last_row2 + 1):
        for cell in ws2[r]:
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

    ws2.column_dimensions['A'].width = 10
    ws2.column_dimensions['B'].width = 16
    ws2.column_dimensions['C'].width = 25
    ws2.column_dimensions['D'].width = 18
    ws2.column_dimensions['E'].width = 18
    ws2.column_dimensions['F'].width = 16
    ws2.column_dimensions['G'].width = 32
    ws2.column_dimensions['H'].width = 20

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    if from_date_str and to_date_str:
        filename = f"Vehicles_Placed_and_DMR_Mails_Sent_{from_date_str}_to_{to_date_str}.xlsx"
    elif from_date_str:
        filename = f"Vehicles_Placed_and_DMR_Mails_Sent_from_{from_date_str}.xlsx"
    elif to_date_str:
        filename = f"Vehicles_Placed_and_DMR_Mails_Sent_up_to_{to_date_str}.xlsx"
    else:
        filename = "Vehicles_Placed_and_DMR_Mails_Sent_All_Dates.xlsx"

    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
