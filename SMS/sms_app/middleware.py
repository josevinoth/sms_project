import re
from django.shortcuts import redirect
from django.contrib import messages
from .sub_models.user_ext_mod import User_extInfo

# Public routes accessible without authentication
PUBLIC_PREFIXES = (
    '/SMS/login_page',
    '/SMS/logout_page',
    '/SMS/registration_page',
    '/SMS/driver/login',
    '/SMS/driver/logout',
    '/SMS/password_reset',
    '/SMS/privacy-policy',
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
        '/SMS/tripdetail',
        '/SMS/tripclosure',
        '/SMS/tripapproval',
        '/SMS/tms_dashboard',
        '/SMS/trans_',
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
                allowed_modules.update(['cms', 'vms'])

            # Business Solution / Organisation based access
            # Org 1: BVM Storage Solutions (WMS)
            # Org 2: BVM Trans Solutions (TMS)
            # Org 3: BVM Pack Solutions (PMS)
            if org_id == 1 or 'storage' in org_name:
                allowed_modules.add('wms')
            if org_id == 2 or 'trans' in org_name:
                allowed_modules.update(['tms', 'vms'])
            if org_id == 3 or 'pack' in org_name:
                allowed_modules.add('pms')

        # Check if the requested path belongs to any disallowed module
        matched_modules = []
        for mod, prefixes in MODULE_ROUTES.items():
            if any(path.startswith(prefix) for prefix in prefixes):
                matched_modules.append(mod)

        if matched_modules:
            # If path matches one or more modules, check if user has access to AT LEAST ONE
            has_access = any(mod in allowed_modules for mod in matched_modules)
            if not has_access:
                messages.error(
                    request,
                    f"Access Restricted: You do not have permission to access this module ({', '.join(m.upper() for m in matched_modules)})."
                )
                return redirect('home_page')

        return self.get_response(request)
