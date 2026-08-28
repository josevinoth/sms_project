from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sms_app.sub_models.pk_manpower_consumption_mod import PkManpowerConsumption
from sms_app.sub_models.pk_costing_summary_mod import PkcostingsummaryInfo
from datetime import datetime


@csrf_exempt
@login_required(login_url='login_page')
def add_manpower_consumption(request):
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id', '').strip()
        customer = request.POST.get('customer', '').strip()
        job_no = request.POST.get('job_no', '').strip()
        date_str = request.POST.get('date', '').strip()
        worker_type = request.POST.get('worker_type', 'Skilled').strip()
        no_of_workers_str = request.POST.get('no_of_workers', '1').strip()
        rate_str = request.POST.get('rate', '0').strip()
        hours_worked_str = request.POST.get('hours_worked', '0').strip()

        if not job_no:
            return JsonResponse({'status': 'error', 'message': 'Job No is required.'})

        try:
            no_of_workers = int(no_of_workers_str) if no_of_workers_str else 1
            rate = float(rate_str) if rate_str else 0.0
            hours_worked = float(hours_worked_str) if hours_worked_str else 0.0
            amount = round(no_of_workers * rate * hours_worked, 2)

            entry_date = None
            if date_str:
                try:
                    entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    entry_date = datetime.now().date()
            else:
                entry_date = datetime.now().date()

            # If customer is not provided, lookup from Costing Summary
            if not customer and job_no:
                costing = PkcostingsummaryInfo.objects.filter(cs_job_no__iexact=job_no).first()
                if costing:
                    customer = costing.cs_customer_name.cu_name if costing.cs_customer_name else costing.cs_customer_new_name or ''

            if entry_id:
                # Update existing record
                manpower_obj = PkManpowerConsumption.objects.filter(id=entry_id).first()
                if not manpower_obj:
                    return JsonResponse({'status': 'error', 'message': 'Entry not found for update.'})
                manpower_obj.mc_customer = customer
                manpower_obj.mc_job_no = job_no
                manpower_obj.mc_date = entry_date
                manpower_obj.mc_worker_type = worker_type
                manpower_obj.mc_no_of_workers = no_of_workers
                manpower_obj.mc_rate = rate
                manpower_obj.mc_hours_worked = hours_worked
                manpower_obj.mc_amount = amount
                manpower_obj.save()
                msg = 'Manpower consumption record updated successfully.'
            else:
                # Create new record
                manpower_obj = PkManpowerConsumption.objects.create(
                    mc_customer=customer,
                    mc_job_no=job_no,
                    mc_date=entry_date,
                    mc_worker_type=worker_type,
                    mc_no_of_workers=no_of_workers,
                    mc_rate=rate,
                    mc_hours_worked=hours_worked,
                    mc_amount=amount
                )
                msg = 'Manpower consumption record saved successfully.'

            return JsonResponse({
                'status': 'success',
                'message': msg,
                'id': manpower_obj.id,
                'amount': float(manpower_obj.mc_amount)
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


@csrf_exempt
@login_required(login_url='login_page')
def delete_manpower_consumption(request):
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id', '').strip()
        if not entry_id:
            return JsonResponse({'status': 'error', 'message': 'Entry ID is required.'})

        try:
            PkManpowerConsumption.objects.filter(id=entry_id).delete()
            return JsonResponse({'status': 'success', 'message': 'Manpower entry deleted successfully.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


@login_required(login_url='login_page')
def get_manpower_consumption_logs(request):
    job_no = request.GET.get('job_no', '').strip()
    if not job_no:
        return JsonResponse({'status': 'error', 'message': 'Job No is required.'})

    logs = PkManpowerConsumption.objects.filter(mc_job_no__iexact=job_no).order_by('-id')
    log_data = []
    total_amount = 0.0
    total_hours = 0.0

    for item in logs:
        amt = float(item.mc_amount or 0.0)
        hrs = float(item.mc_hours_worked or 0.0)
        total_amount += amt
        total_hours += hrs
        log_data.append({
            'id': item.id,
            'customer': item.mc_customer or '',
            'job_no': item.mc_job_no or '',
            'date': item.mc_date.strftime('%Y-%m-%d') if item.mc_date else '',
            'worker_type': item.mc_worker_type or 'Skilled',
            'no_of_workers': item.mc_no_of_workers,
            'rate': float(item.mc_rate or 0.0),
            'hours_worked': hrs,
            'amount': amt,
        })

    return JsonResponse({
        'status': 'success',
        'job_no': job_no,
        'logs': log_data,
        'total_amount': round(total_amount, 2),
        'total_hours': round(total_hours, 2),
        'count': len(log_data)
    })
