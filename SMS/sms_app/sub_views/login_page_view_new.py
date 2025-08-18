# from django.db.models import Sum
#
# from ..models import Employee, AssetInfo, Vendor_info, Location_info, Product_info, Service_Info
# from ..sub_models.unit_info_mod import UnitInfo
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from django.http import JsonResponse
# from ..models import Employee
# from ..sub_models.unit_info_mod import UnitInfo
#
# def login_page_new(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         selected_unit_id = request.POST.get('unit')
#
#         # Validate user exists
#         try:
#             employee = Employee.objects.get(emp_empid=username)
#         except Employee.DoesNotExist:
#             messages.error(request, "Employee not found. Please register.")
#             return render(request, 'asset_mgt_app/login.html')
#
#         # Organisation id == 1 logic (two-step login)
#         if employee.emp_organisation and employee.emp_organisation.id == 1:
#             # First step: username entered, no password yet - show units form
#             if username and not password:
#                 emp_branch = employee.emp_branch
#                 units = UnitInfo.objects.filter(ui_branch_name=emp_branch) if emp_branch else []
#                 return render(request, 'asset_mgt_app/login.html', {
#                     'username': username,
#                     'units': units,
#                     'show_units': True,
#                 })
#
#             # Second step: username + password + unit
#             if username and password and selected_unit_id:
#                 if employee.emp_password != password:
#                     messages.error(request, "Invalid password.")
#                     emp_branch = employee.emp_branch
#                     units = UnitInfo.objects.filter(ui_branch_name=emp_branch) if emp_branch else []
#                     return render(request, 'asset_mgt_app/login.html', {
#                         'username': username,
#                         'units': units,
#                         'selected_unit_id': selected_unit_id,
#                         'show_units': True,
#                     })
#                 # Password correct
#                 request.session['ses_username'] = employee.emp_empid
#                 request.session['first_name'] = employee.emp_full_name
#                 request.session['ses_emp_branch_id'] = employee.emp_branch.id if employee.emp_branch else None
#                 request.session['ses_unit_id'] = selected_unit_id
#                 messages.success(request, "Logged in successfully!")
#                 return redirect('home_page_new')
#
#             # If password missing or unit missing here, show error
#             messages.error(request, "Please enter password and select unit.")
#             return render(request, 'asset_mgt_app/login.html', {
#                 'username': username,
#                 'show_units': True,
#             })
#
#         else:
#             # Organisation != 1: normal login with username and password only
#             if employee.emp_password != password:
#                 messages.error(request, "Invalid username or password.")
#                 return render(request, 'asset_mgt_app/login.html', {
#                     'username': username,
#                 })
#             # Successful login
#             request.session['ses_username'] = employee.emp_empid
#             request.session['first_name'] = employee.emp_full_name
#             request.session['ses_emp_branch_id'] = employee.emp_branch.id if employee.emp_branch else None
#             messages.success(request, "Logged in successfully!")
#             return redirect('home_page_new')
#
#     # GET request - empty login form
#     return render(request, 'asset_mgt_app/login.html')
# def get_units(request):
#     username = request.GET.get('username', '').strip()
#     print(f"get_units called with username: {username}")
#     if not username:
#         return JsonResponse({'units': [], 'org_id': None})
#     try:
#         employee = Employee.objects.get(emp_empid=username)
#         emp_branch = employee.emp_branch
#         units_qs = UnitInfo.objects.filter(ui_branch_name=emp_branch) if emp_branch else UnitInfo.objects.none()
#         units = [{'id': u.id, 'unit_name': u.unit_name} for u in units_qs]
#         org_id = employee.emp_organisation.id if employee.emp_organisation else None
#         print(f"Returning org_id: {org_id}, units count: {len(units)}")
#         return JsonResponse({'units': units, 'org_id': org_id})
#     except Employee.DoesNotExist:
#         print("Employee not found")
#         return JsonResponse({'units': [], 'org_id': None})
#
#
#
# def home_page_new(request):
#     first_name = request.session.get('first_name')
#     ses_username = request.session.get('ses_username')
#     units = []
#
#     emp_branch_id = request.session.get('ses_emp_branch_id')
#     print(f"Home page loading for branch id: {emp_branch_id}")
#
#     if emp_branch_id:
#         units = UnitInfo.objects.filter(ui_branch_name_id=emp_branch_id)
#         print(f"Units found on home page: {units.count()}")
#
#     context = {
#         'count_asset': AssetInfo.objects.all().count(),
#         'count_vendors': Vendor_info.objects.filter(vend_status=1).count(),
#         'count_ass_asset': AssetInfo.objects.filter(asset_assignedto__isnull=False).count(),
#         'count_unass_asset': AssetInfo.objects.filter(asset_assignedto__isnull=True).count(),
#         'count_location': Location_info.objects.filter(loc_status=1).count(),
#         'count_product': Product_info.objects.all().count(),
#         'count_employee': Employee.objects.all().count(),
#         'sum_ass_cost': AssetInfo.objects.aggregate(sum=Sum('asset_cost'))['sum'] or 0.00,
#         'sum_service_cost': Service_Info.objects.aggregate(sum=Sum('ser_cost'))['sum'] or 0.00,
#         'ses_username': ses_username,
#         'first_name': first_name,
#         'units': units,
#     }
#
#     return render(request, 'asset_mgt_app/home_page.html', context)
