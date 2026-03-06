from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, JsonResponse
import json

from ..forms import FuelfillingForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum, Max
from openpyxl import Workbook
from io import BytesIO
import datetime
from datetime import date
from ..models import Fuelfillinginfo, Places, Bunkname, TripdetailInfo

@login_required(login_url='login_page')
def fuelfilling_add(request, fuelfilling_id=0):
    first_name = request.session.get('first_name')
    user_id = request.session.get('ses_userID')

    # If editing, fetch the existing instance
    if fuelfilling_id != 0:
        fuelfilling = get_object_or_404(Fuelfillinginfo, pk=fuelfilling_id)
    else:
        fuelfilling = None

    if request.method == "POST":
        form = FuelfillingForm(request.POST, instance=fuelfilling)

        if form.is_valid():
            instance = form.save()
            if fuelfilling is None:
                print("Fuelfillinginfo Form is Valid - New Record")
                messages.success(request, 'Fuel Filling Record Added Successfully')
                return redirect('/SMS/fuelfilling_update/' + str(instance.id))
            else:
                print("Fuelfillinginfo Form is Valid - Updated Record")
                messages.success(request, 'Fuel Filling Record Updated Successfully')
                return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            print("Fuelfillinginfo Form is Not Valid")
            for field, errors in form.errors.items():
                for error in errors:
                    print(f"Error in {field}: {error}")
                    messages.error(request, f"{field}: {error}")
            # fall through to render the form with errors below

    else:
        # GET request
        form = FuelfillingForm(instance=fuelfilling)

    context = {
        'form': form,
        'first_name': first_name,
        'user_id': user_id,
    }
    return render(request, "asset_mgt_app/fuelfilling_add.html", context)

                # return redirect(request.META['HTTP_REFERER'])

        # return redirect('/SMS/requirements_list')


# List fuelfilling
@login_required(login_url='login_page')
def fuelfilling_list(request):
    first_name = request.session.get('first_name')
    context = {'fuelfilling_list' : Fuelfillinginfo.objects.all(),'first_name': first_name}
    return render(request,"asset_mgt_app/fuelfilling_list.html",context)

#Delete fuelfilling
@login_required(login_url='login_page')
def fuelfilling_delete(request,fuelfilling_id):
    fuelfilling = Fuelfillinginfo.objects.get(pk=fuelfilling_id)
    fuelfilling.delete()
    return redirect('/SMS/fuelfilling_list')

@login_required(login_url='login_page')
def load_location(request):
    # Fetch location
    location_list=[]
    location_id_list=[]
    ff_city_id = request.GET.get('cityId_1')
    # Fetch Unit Details
    location = Places.objects.filter(city=ff_city_id).values('place_name').distinct()
    location_id = Places.objects.filter(city=ff_city_id).values('id').distinct()
    location_count=location.count()
    for i in range(location_count):
        location_list.append(location[i]['place_name'])
        location_id_list.append(location_id[i]['id'])
    data = {
        'location_id_list':location_id_list,
        'location_list': location_list,
    }
    return HttpResponse(json.dumps(data))
    # return JsonResponse((data))

@login_required(login_url='login_page')
def fetch_bunk_details(request):
    bunk_name = request.GET.get('bunk_name', '')
    if bunk_name:
        try:
            bunk = Bunkname.objects.get(bunk_name=bunk_name)
            return JsonResponse({
                'bunk_state': bunk.bunk_state or '',
                'bunk_location_name': bunk.bunk_location_name or '',
            })
        except Bunkname.DoesNotExist:
            return JsonResponse({'error': 'Bunk not found'})
    return JsonResponse({'error': 'No bunk name provided'})

import calendar

@login_required(login_url='login_page')
def fuelfilling_export_excel(request):
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if not month or not year:
        return HttpResponse("Month and Year are required", status=400)
        
    month = int(month)
    year = int(year)
    
    # Get last day of the month
    last_day = calendar.monthrange(year, month)[1]
    last_date_of_month = datetime.date(year, month, last_day)
    
    queryset = Fuelfillinginfo.objects.filter(
        ff_date__year=year,
        ff_date__month=month
    )
        
    # Group by vehicle (monthly summary for the selected period)
    grouped_data = {}
    for record in queryset:
        if not record.ff_vehicle_num:
            continue
            
        key = record.ff_vehicle_num.id
        if key not in grouped_data:
            grouped_data[key] = {
                'vehicle': record.ff_vehicle_num,
                'total_amt': 0,
                'vendor': record.ff_bunk_name.bunk_fuel_vendor.fuel_vendor if record.ff_bunk_name and record.ff_bunk_name.bunk_fuel_vendor else "BPCL - Trans"
            }
        grouped_data[key]['total_amt'] += record.ff_fuel_price

    wb = Workbook()
    ws = wb.active
    ws.title = "Fuel Format"
    
    headers = [
        "VOUCHER NUMBER", "DATE", "REF NO.", "SUNDRY CREDITORS", 
        "TOTAL AMT", "EXPENSES LEDGER", "AMOUNT", "PRIMARY COST CATEGORY", 
        "JOB NO", "VEH. NO.", "CUSTOMER"
    ]
    ws.append(headers)
    
    # Adjust column widths
    for col in range(1, len(headers) + 1):
        ws.column_dimensions[ws.cell(row=1, column=col).column_letter].width = 20

    def get_financial_year(date_obj):
        year_val = date_obj.year
        if date_obj.month >= 4:
            return f"{str(year_val)[2:]}{str(year_val+1)[2:]}"
        else:
            return f"{str(year_val-1)[2:]}{str(year_val)[2:]}"

    for idx, (key, data) in enumerate(grouped_data.items(), 1):
        vehicle = data['vehicle']
        
        # Voucher format: Diesel_{month}_{FY}-{serial}
        mm = str(month).zfill(2)
        fy = get_financial_year(last_date_of_month)
        voucher_no = f"Diesel_{mm}_{fy}-{str(idx).zfill(3)}"
        
        # Ref No: Month-Year (e.g., Apr-26)
        ref_no = last_date_of_month.strftime('%b-%y')
        
        # Get Primary Cost Category from Vehicle Master Ownership
        primary_cost_category = ""
        if vehicle.vm_ownership:
            ownership_name = str(vehicle.vm_ownership.ow_ownership).upper()
            if "OWN" in ownership_name:
                primary_cost_category = "BVM - OWN"
            elif "MARKET" in ownership_name:
                primary_cost_category = "MARKET"
            else:
                primary_cost_category = ownership_name # Fallback to actual ownership name

        row = [
            voucher_no,
            last_date_of_month.strftime("%d/%m/%Y"),
            ref_no,
            data['vendor'],
            data['total_amt'],
            "Diesel - Vehicle",
            data['total_amt'],
            primary_cost_category,
            "N/A(J)", # Static Job No
            str(vehicle),
            "N/A(C)"  # Static Customer
        ]
        ws.append(row)

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    
    filename = f"Fuel_Export_{month}_{year}.xlsx"
    response = HttpResponse(
        buffer.getvalue(), 
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
