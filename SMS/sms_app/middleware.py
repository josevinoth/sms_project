import re
from django.shortcuts import redirect
from django.contrib import messages
from .sub_models.user_ext_mod import User_extInfo

# Public routes accessible without authentication
PUBLIC_PREFIXES = (
    '/SMS/login_page',
    '/SMS/logout_page',
    '/SMS/registration_page',
    '/SMS/driver/',
    '/SMS/password_reset',
    '/SMS/privacy-policy',
    '/SMS/customer_login',
    '/SMS/customer_register',
    '/SMS/ajax/get-customer-departments',
    '/admin/',
    '/static/',
    '/media/',
)

# Common routes accessible to any authenticated user
COMMON_PREFIXES = (
    '/SMS/home_page',
    '/SMS/driver/dashboard',
    '/SMS/load_currency_value',
    '/SMS/search_vehicle_numbers',
    '/SMS/print_pdf',
    '/SMS/asset_qr_id',
    '/SMS/goods_qr_id',
    '/SMS/api/',
    '/SMS/SMS/customer_',
    '/SMS/customer_',
    '/SMS/ajax/',
)

# Module Route Prefixes Mapping
MODULE_ROUTES = {
    'admin': (
        '/SMS/user_list',
        '/SMS/user_insert',
        '/SMS/user_update',
        '/SMS/user_delete',
        '/SMS/user_approval_list',
        '/SMS/user_approve',
        '/SMS/user_reject',
        '/SMS/user_control',
        '/SMS/department_list',
        '/SMS/department_insert',
        '/SMS/department_update',
        '/SMS/department_delete',
        '/SMS/designation_list',
        '/SMS/designation_insert',
        '/SMS/designation_update',
        '/SMS/designation_delete',
        '/SMS/role_list',
        '/SMS/role_insert',
        '/SMS/role_update',
        '/SMS/role_delete',
        '/SMS/deletion_log_list',
        '/SMS/customer_registration',
        '/SMS/insurance',
        '/SMS/location_list',
        '/SMS/country_',
        '/SMS/state_',
        '/SMS/city_',
        '/SMS/places_',
        # Administration Masters
        '/SMS/location_master',
        '/SMS/charge_master',
        '/SMS/bunkname',
        '/SMS/vehiclemaster',
        '/SMS/halting',
        '/SMS/vehiclecategory',
        '/SMS/vehicletype',
        '/SMS/movementtype',
        '/SMS/vhmanufacturer',
        '/SMS/vehiclemodel',
        '/SMS/ownership',
        '/SMS/body_',
        '/SMS/axletype',
        '/SMS/fueltype',
        '/SMS/vehiclecolour',
        '/SMS/permittype',
        '/SMS/rtratemaster',
        '/SMS/vendorratemaster',
        '/SMS/whratemaster',
        '/SMS/locationmaster',
        '/SMS/materialhandling',
        '/SMS/packagetype',
        '/SMS/currencytype',
        '/SMS/stocktype',
    ),
    'ems': (
        '/SMS/user_list',
        '/SMS/user_insert',
        '/SMS/user_update',
        '/SMS/user_delete',
        '/SMS/emp_',
        '/SMS/designation_',
        '/SMS/role_',
    ),
    'tms': (
        '/SMS/enquirynote',
        '/SMS/vehicle_allotment',
        '/SMS/consignmentdetail',
        '/SMS/tripdetail',
        '/SMS/tripclosure',
        '/SMS/tripapproval',
        '/SMS/tms_dashboard',
        '/SMS/trans_',
        '/SMS/attached_bill',
        '/SMS/market_bill',
        '/SMS/invoice_documents',
        '/SMS/track_vehicle',
        '/SMS/vehicle_availability',
        '/SMS/fleet_management',
        '/SMS/transport_reports',
        '/SMS/tms_petty_cash',
        '/SMS/maintenance',
    ),
    'wms': (
        '/SMS/gatein',
        '/SMS/wh_job',
        '/SMS/goods_',
        '/SMS/loadingbay',
        '/SMS/unit_',
        '/SMS/bay_',
        '/SMS/whstoragetype',
        '/SMS/wh_highvaluecheck',
        '/SMS/dg_cargo',
    ),
    'fms': (
        '/SMS/ar_',
        '/SMS/arcomments',
        '/SMS/budget',
        '/SMS/business_revenue',
        '/SMS/expense',
        '/SMS/iou',
        '/SMS/performance_audit',
        '/SMS/finance_reports',
        '/SMS/attached_bill',
        '/SMS/market_bill',
        '/SMS/maintenance_bill',
        '/SMS/trip_settlement',
    ),
    'pms': (
        '/SMS/pk_production',
        '/SMS/pk_return',
        '/SMS/pk_purchase',
        '/SMS/pk_quality',
        '/SMS/pk_invoice',
        '/SMS/pk_accept',
        '/SMS/pk_reject',
        '/SMS/pk_process',
        '/SMS/pk_create',
        '/SMS/pk_get',
        '/SMS/pk_item',
        '/SMS/pk_costing',
        '/SMS/pk_stock',
        '/SMS/pk_quotation',
        '/SMS/needassessment',
        '/SMS/purchaseorder',
        '/SMS/costingsummary',
        '/SMS/stockpurchases',
        '/SMS/stock_description',
        '/SMS/part_code',
    ),
    'ams': (
        '/SMS/asset_',
        '/SMS/assign_asset',
        '/SMS/unassigned_asset',
        '/SMS/product_',
        '/SMS/producttype_',
        '/SMS/reports',
        '/SMS/damage_',
    ),
    'vms': (
        '/SMS/vendor_',
    ),
    'cms': (
        '/SMS/customer_',
        '/SMS/crcountfrom_',
        '/SMS/customertype_',
        '/SMS/customername_',
        '/SMS/customerdepartment_',
        '/SMS/gstexcepmtion_',
        '/SMS/gstmodel_',
        '/SMS/paymenttype_',
        '/SMS/trbusinesstype_',
        '/SMS/email_master_',
    ),
    'supports': (
        '/SMS/task_',
        '/SMS/timesheet_',
        '/SMS/requirements_',
        '/SMS/open_requirements',
    ),
    'prime': (
        '/SMS/prime_',
    ),
}

class GlobalModuleAuthorizationMiddleware:
    """
    Middleware to globally enforce role and module-level route authorization.
    Prevents users from bypassing UI controls by manually typing URLs in the browser bar.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # 1. Allow public routes
        if any(path.startswith(prefix) for prefix in PUBLIC_PREFIXES):
            return self.get_response(request)

        # 2. Require authentication for all other routes
        if not request.user or not request.user.is_authenticated:
            return redirect('login_page')

        # 3. Allow common logged-in routes
        if any(path.startswith(prefix) for prefix in COMMON_PREFIXES):
            return self.get_response(request)

        # 4. Superusers and staff get full access
        if request.user.is_superuser or request.user.is_staff:
            return self.get_response(request)

        user_id = request.session.get('ses_userID') or request.user.id
        user_role_str = (request.session.get('ses_role') or '').lower().strip()

        # Admin and Superuser session roles get full access
        if user_role_str in ['admin', 'super user', 'superuser']:
            return self.get_response(request)

        # Transparent movement branch scoping (uses existing views' built-in branch handling)
        try:
            from .utils.page_catalog import get_user_movement_branches, ALL_BRANCH_CODES
            allowed_branches = get_user_movement_branches(request.user)
            if allowed_branches and allowed_branches != ALL_BRANCH_CODES and len(allowed_branches) == 1:
                single_branch = next(iter(allowed_branches))
                branch_id_map = {"BLR": 1, "MAA": 2, "PNY": 3, "HYD": 4, "CJB": 5}
                if single_branch in branch_id_map:
                    request.session['ses_branch_id'] = branch_id_map[single_branch]
                if not request.GET.get('branch'):
                    mutable_get = request.GET.copy()
                    mutable_get['branch'] = single_branch
                    request.GET = mutable_get
        except Exception:
            pass

        # Retrieve user extended info for module capability resolution
        try:
            user_ext = User_extInfo.objects.select_related(
                'emp_organisation', 'department', 'emp_role', 'emp_designation'
            ).get(user_id=user_id)
        except User_extInfo.DoesNotExist:
            messages.error(request, "User profile not found. Access denied.")
            return redirect('home_page')

        org_id = user_ext.emp_organisation_id if user_ext.emp_organisation else None
        org_name = str(user_ext.emp_organisation).lower() if user_ext.emp_organisation else ''
        dept_name = str(user_ext.department).lower() if user_ext.department else ''
        desig_name = str(user_ext.emp_designation).lower() if user_ext.emp_designation else ''

        # Determine allowed modules for this user
        allowed_modules = set()

        # Check TMS Manager override
        is_tms_mgr = (user_role_str == 'user' and 'trans' in org_name and 'manager' in desig_name)
        if is_tms_mgr:
            allowed_modules.add('tms')
        else:
            # Department based access
            if 'corporate' in dept_name:
                allowed_modules.update(['cms', 'vms', 'ams', 'tms', 'wms', 'pms', 'fms'])
            elif 'human resource' in dept_name or 'hr' in dept_name:
                allowed_modules.add('ems')
            elif 'finance' in dept_name:
                allowed_modules.add('fms')
            elif 'sales' in dept_name:
                allowed_modules.update(['sales', 'cms', 'vms'])
            elif 'customer service' in dept_name or getattr(user_ext, 'department_id', None) == 4:
                allowed_modules.update(['tms', 'prime'])
            elif 'operation' in dept_name or getattr(user_ext, 'department_id', None) == 2:
                if org_id == 1 or 'storage' in org_name:
                    allowed_modules.add('wms')
                elif org_id == 2 or 'trans' in org_name or request.user.username.upper().startswith('TRA'):
                    allowed_modules.update(['tms', 'vms', 'prime'])
                elif org_id == 3 or 'pack' in org_name or request.user.username.upper().startswith('PK'):
                    allowed_modules.add('pms')
                else:
                    allowed_modules.update(['tms', 'wms', 'prime'])

            # Business Solution / Organisation based access
            # Org 1: BVM Storage Solutions (WMS)
            # Org 2: BVM Trans Solutions (TMS)
            # Org 3: BVM Pack Solutions (PMS)
            if org_id == 1 or 'storage' in org_name:
                allowed_modules.add('wms')
            if org_id == 2 or 'trans' in org_name or request.user.username.upper().startswith('TRA'):
                allowed_modules.update(['tms', 'vms', 'prime'])
            if org_id == 3 or 'pack' in org_name or request.user.username.upper().startswith('PK'):
                allowed_modules.add('pms')

        # Check if user has custom granular page permissions defined in UserPageAccess
        from .models import UserPageAccess
        import json

        # Central Granular CRUD Enforcement via UserPageAccess
        if request.user.is_authenticated:
            try:
                from .utils.page_catalog import resolve_request_crud, get_user_page_crud_permissions
                action, pkey = resolve_request_crud(path)
                if pkey:
                    perms = get_user_page_crud_permissions(request.user, pkey)
                    request.page_permissions = perms
                    request.page_permissions_json = json.dumps(perms)
                    request.current_page_key = pkey

                    # Enforce CRUD checks for non-administrators
                    if not (request.user.is_superuser or request.user.is_staff):
                        is_ajax = (request.headers.get('x-requested-with') == 'XMLHttpRequest' or 
                                   request.content_type == 'application/json')
                        
                        def _access_denied_response(msg):
                            if is_ajax:
                                from django.http import JsonResponse
                                return JsonResponse({'status': 'error', 'message': msg}, status=403)
                            messages.error(request, msg)
                            referer = request.META.get('HTTP_REFERER')
                            if referer and referer != request.build_absolute_uri():
                                return redirect(referer)
                            return redirect('home_page')

                        if action == 'view' and not perms['can_view']:
                            return _access_denied_response("View Access Denied: You do not have permission to view this page.")
                        elif action == 'create' and not perms['can_create']:
                            return _access_denied_response("Create Access Denied: You do not have permission to create records on this page.")
                        elif action == 'edit' and not perms['can_edit']:
                            return _access_denied_response("Edit Access Denied: You do not have permission to edit records on this page.")
                        elif action == 'delete' and not perms['can_delete']:
                            return _access_denied_response("Delete Access Denied: You do not have permission to delete records on this page.")
            except Exception:
                pass

        has_custom = UserPageAccess.objects.filter(user=request.user).exists()
        if has_custom:
            try:
                from .utils.page_catalog import get_user_allowed_route_prefixes
                custom_prefixes = get_user_allowed_route_prefixes(request.user)
                # Check if current path matches any protected route in MODULE_ROUTES
                matched_prefixes = [pfx for prefixes in MODULE_ROUTES.values() for pfx in prefixes if path.startswith(pfx)]
                if matched_prefixes:
                    if any(path.startswith(prefix) for prefix in custom_prefixes):
                        return self.get_response(request)
                    else:
                        messages.error(
                            request,
                            "View Access Denied: You do not have permission to view this page."
                        )
                        return redirect('home_page')
            except Exception:
                pass

        # Check if the requested path belongs to any disallowed module
        matched_modules = []
        for mod, prefixes in MODULE_ROUTES.items():
            if any(path.startswith(prefix) for prefix in prefixes):
                matched_modules.append(mod)

        if matched_modules:
            # If path matches one or more modules, check if user has access to AT LEAST ONE
            has_access = any(mod in allowed_modules for mod in matched_modules)
            if not has_access:
                is_cust = getattr(user_ext, 'linked_customer', None) or (user_ext.emp_role and user_ext.emp_role.role_name.lower() == 'customer') or getattr(user_ext, 'is_lp_customer', False)
                if is_cust:
                    messages.error(
                        request,
                        f"Access Restricted: Customer accounts do not have access to internal staff modules ({', '.join(m.upper() for m in matched_modules)})."
                    )
                    return redirect('customer_dashboard')

                messages.error(
                    request,
                    f"Access Denied: The {', '.join(m.upper() for m in matched_modules)} module is not enabled for your account."
                )
                return redirect('home_page')

        return self.get_response(request)
