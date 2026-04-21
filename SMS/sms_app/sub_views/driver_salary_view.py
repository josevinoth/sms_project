from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from ..models import DriverSalaryInfo, DrivermasterInfo, Location_info, User_extInfo
from ..sub_forms.driver_salary_form import DriverSalaryForm
from datetime import datetime

@login_required(login_url='login_page')
def driver_salary_list(request):
    first_name = request.session.get('first_name')
    
    # Get filters from request
    branch_id = request.GET.get('branch')
    driver_id = request.GET.get('driver')
    month_val = request.GET.get('month') # Expecting YYYY-MM
    
    salary_list = DriverSalaryInfo.objects.all()
    
    if branch_id and branch_id != '':
        salary_list = salary_list.filter(ds_branch_id=branch_id)
    if driver_id and driver_id != '':
        salary_list = salary_list.filter(ds_driverid_id=driver_id)
    if month_val and month_val != '':
        try:
            # Parse YYYY-MM and filter by month/year
            month_date = datetime.strptime(month_val, '%Y-%m')
            salary_list = salary_list.filter(ds_month__year=month_date.year, ds_month__month=month_date.month)
        except ValueError:
            pass

    branches = Location_info.objects.filter(loc_name__in=['BVM MAA', 'BVM BLR'])
    drivers = DrivermasterInfo.objects.all()

    return render(request, "asset_mgt_app/driver_salary_list.html", {
        'salary_list': salary_list,
        'branches': branches,
        'drivers': drivers,
        'first_name': first_name,
        'filters': {
            'branch': branch_id,
            'driver': driver_id,
            'month': month_val
        }
    })

@login_required(login_url='login_page')
def driver_salary_add(request, salary_id=0):
    first_name = request.session.get('first_name')
    salary_instance = None
    if salary_id:
        salary_instance = get_object_or_404(DriverSalaryInfo, pk=salary_id)

    if request.method == "POST":
        form = DriverSalaryForm(request.POST, instance=salary_instance)
        if form.is_valid():
            salary = form.save(commit=False)
            # Re-fetch branch and name from driver to ensure data integrity
            driver = salary.ds_driverid
            salary.ds_driver_name = driver.dm_name
            # Try to get branch from User_extInfo
            if driver.dm_user_id:
                try:
                    user_ext = User_extInfo.objects.get(user=driver.dm_user_id)
                    salary.ds_branch = user_ext.emp_branch
                except User_extInfo.DoesNotExist:
                    pass
            
            salary.save()
            messages.success(request, "Driver salary saved successfully ✅")
            return redirect('driver_salary_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DriverSalaryForm(instance=salary_instance)

    return render(request, "asset_mgt_app/driver_salary_add.html", {
        'form': form,
        'first_name': first_name,
        'salary_instance': salary_instance
    })

@login_required(login_url='login_page')
def driver_salary_delete(request, salary_id):
    salary = get_object_or_404(DriverSalaryInfo, pk=salary_id)
    salary.delete()
    messages.success(request, "Driver salary deleted successfully 🗑️")
    return redirect('driver_salary_list')

def get_driver_salary_details(request):
    driver_id = request.GET.get('driver_id')
    if not driver_id:
        return JsonResponse({'error': 'No driver ID selected'}, status=400)
    
    try:
        driver = DrivermasterInfo.objects.get(id=driver_id)
        data = {
            'driver_name': driver.dm_name,
            'branch': '',
            'branch_id': ''
        }
        
        if driver.dm_user_id:
            try:
                user_ext = User_extInfo.objects.get(user=driver.dm_user_id)
                if user_ext.emp_branch:
                    data['branch'] = user_ext.emp_branch.loc_name
                    data['branch_id'] = user_ext.emp_branch.id
            except (User_extInfo.DoesNotExist, Exception):
                pass
        
        return JsonResponse(data)
    except DrivermasterInfo.DoesNotExist:
        return JsonResponse({'error': 'Driver not found'}, status=404)
