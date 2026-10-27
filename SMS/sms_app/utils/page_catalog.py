"""
Page Catalog and Permission Registry for SMS (BVM Management System)
Defines all functional modules, categories, and granular pages for User Control.
"""

PAGE_CATALOG = [
    {
        'module_id': 'tms',
        'module_name': 'Transport Management System (TMS)',
        'icon': 'fas fa-truck',
        'color': '#3b82f6',
        'groups': [
            {
                'group_name': 'Operations',
                'pages': [
                    {'key': 'tms_enquirynote', 'name': 'Booking Note', 'url_name': 'enquirynote_list', 'prefixes': ['/SMS/enquirynote'], 'icon': 'fas fa-clipboard-list'},
                    {'key': 'tms_vehicle_allotment', 'name': 'Vehicle Allotment', 'url_name': 'vehicle_allotment_list', 'prefixes': ['/SMS/vehicle_allotment'], 'icon': 'fas fa-truck-loading'},
                    {'key': 'tms_consignment', 'name': 'Consignment Detail', 'url_name': 'consignmentdetail_list', 'prefixes': ['/SMS/consignmentdetail'], 'icon': 'fas fa-file-contract'},
                    {'key': 'tms_tripdetail', 'name': 'Trip Detail', 'url_name': 'tripdetail_list', 'prefixes': ['/SMS/tripdetail'], 'icon': 'fas fa-route'},
                    {'key': 'tms_track_vehicle', 'name': 'Track Vehicle Position', 'url_name': 'track_vehicle_position', 'prefixes': ['/SMS/track_vehicle'], 'icon': 'fas fa-map-marker-alt'},
                ]
            },
            {
                'group_name': 'Settlement & Closure',
                'pages': [
                    {'key': 'tms_tripclosure', 'name': 'Trip Closure', 'url_name': 'tripclosure_list', 'prefixes': ['/SMS/tripclosure'], 'icon': 'fas fa-check-circle'},
                    {'key': 'tms_trip_settlement', 'name': 'Trip Settlement', 'url_name': 'trip_settlement_view', 'prefixes': ['/SMS/trip_settlement'], 'icon': 'fas fa-handshake'},
                ]
            },
            {
                'group_name': 'Billing & Invoicing',
                'pages': [
                    {'key': 'tms_trans_invoice', 'name': 'Invoice List', 'url_name': 'trans_invoice_list', 'prefixes': ['/SMS/trans_invoice'], 'icon': 'fas fa-file-invoice'},
                    {'key': 'tms_invoice_docs', 'name': 'Invoice Supportings', 'url_name': 'invoice_documents_list', 'prefixes': ['/SMS/invoice_documents'], 'icon': 'fas fa-file-alt'},
                    {'key': 'tms_attached_bill', 'name': 'Attached Bill', 'url_name': 'attached_bill_list', 'prefixes': ['/SMS/attached_bill'], 'icon': 'fas fa-paperclip'},
                    {'key': 'tms_market_bill', 'name': 'Market Bill', 'url_name': 'market_bill_list', 'prefixes': ['/SMS/market_bill'], 'icon': 'fas fa-shopping-cart'},
                ]
            },
            {
                'group_name': 'Approvals',
                'pages': [
                    {'key': 'tms_trip_approval', 'name': 'Trip Approval', 'url_name': 'trip_approval_view', 'prefixes': ['/SMS/tripapproval', '/SMS/trip_approval'], 'icon': 'fas fa-user-check'},
                    {'key': 'tms_manager_approval', 'name': 'Manager Approval', 'url_name': 'manager_approval_list', 'prefixes': ['/SMS/maintenance/manager-approval', '/SMS/maintenance/manager-approve', '/SMS/manager_approval'], 'icon': 'fas fa-user-tie'},
                    {'key': 'tms_sell_rate_approval', 'name': 'Sell Rate Approval', 'url_name': 'sell_rate_approval_list', 'prefixes': ['/SMS/sell_rate_approval'], 'icon': 'fas fa-tags'},
                    {'key': 'tms_finance_approval_trip', 'name': 'Finance Approval (Trip)', 'url_name': 'trip_finance_approval_view', 'prefixes': ['/SMS/trip_finance_approval'], 'icon': 'fas fa-money-check-alt'},
                    {'key': 'tms_finance_approval_admin', 'name': 'Finance Approval (Admin)', 'url_name': 'finance_approval_list', 'prefixes': ['/SMS/maintenance/finance-approval', '/SMS/maintenance/finance-approve', '/SMS/finance_approval'], 'icon': 'fas fa-wallet'},
                    {'key': 'tms_checklist_approval', 'name': 'Check List Approval', 'url_name': 'trip_highvalue_list', 'prefixes': ['/SMS/trip_highvalue'], 'icon': 'fas fa-clipboard-check'},
                ]
            },
            {
                'group_name': 'Fleet & Maintenance',
                'pages': [
                    {'key': 'tms_maintenance', 'name': 'PO / Maintenance', 'url_name': 'maintenance_list', 'prefixes': ['/SMS/maintenance_'], 'icon': 'fas fa-tools'},
                    {'key': 'tms_maintenance_bill', 'name': 'Maintenance Bill', 'url_name': 'maintenance_bill_list', 'prefixes': ['/SMS/maintenance_bill'], 'icon': 'fas fa-file-invoice-dollar'},
                    {'key': 'tms_fuelfilling', 'name': 'Fuel Filling', 'url_name': 'fuelfilling_list', 'prefixes': ['/SMS/fuelfilling'], 'icon': 'fas fa-gas-pump'},
                    {'key': 'tms_vehicle_availability', 'name': 'Vehicle Availability', 'url_name': 'vehicle_availability', 'prefixes': ['/SMS/vehicle_availability'], 'icon': 'fas fa-truck-moving'},
                    {'key': 'tms_fleet_management', 'name': 'Fleet Management', 'url_name': 'fleet_management_view', 'prefixes': ['/SMS/fleet_management'], 'icon': 'fas fa-tachometer-alt'},
                ]
            },
            {
                'group_name': 'Drivers',
                'pages': [
                    {'key': 'tms_driver_master', 'name': 'Driver Master', 'url_name': 'driver_list', 'prefixes': ['/SMS/driver_list', '/SMS/driver_add', '/SMS/driver_edit', '/SMS/driver_delete', '/SMS/driver_active', '/SMS/driver_details'], 'icon': 'fas fa-user-cog'},
                    {'key': 'tms_driver_settlement', 'name': 'Driver Settlement', 'url_name': 'driver_settlement_list', 'prefixes': ['/SMS/driver_settlement'], 'icon': 'fas fa-user-shield'},
                    {'key': 'tms_driver_salary', 'name': 'Driver Salary', 'url_name': 'driver_salary_list', 'prefixes': ['/SMS/driver_salary'], 'icon': 'fas fa-money-bill-wave'},
                    {'key': 'tms_petty_cash', 'name': 'Petty Cash (TMS)', 'url_name': 'tms_petty_cash_list', 'prefixes': ['/SMS/tms_petty_cash'], 'icon': 'fas fa-money-bill-alt'},
                ]
            },
            {
                'group_name': 'Reports & KPI',
                'pages': [
                    {'key': 'tms_cs_dashboard', 'name': 'CS Dashboard', 'url_name': 'cs_kpi_dashboard', 'prefixes': ['/SMS/cs_kpi_dashboard'], 'icon': 'fas fa-chart-line'},
                    {'key': 'tms_reports', 'name': 'Transport Reports', 'url_name': 'transport_reports', 'prefixes': ['/SMS/transport_reports'], 'icon': 'fas fa-book'},
                ]
            }
        ]
    },
    {
        'module_id': 'wms',
        'module_name': 'Warehouse Management System (WMS)',
        'icon': 'fas fa-warehouse',
        'color': '#10b981',
        'groups': [
            {
                'group_name': 'Operations',
                'pages': [
                    {'key': 'wms_pre_gatein', 'name': 'Pre-Gate-In', 'url_name': 'pre_gatein_search', 'prefixes': ['/SMS/pre_gatein'], 'icon': 'fas fa-space-shuttle'},
                    {'key': 'wms_gatein', 'name': 'Gate-In', 'url_name': 'gatein_list', 'prefixes': ['/SMS/gatein'], 'icon': 'fas fa-door-open'},
                    {'key': 'wms_high_value', 'name': 'High-Value Checklist', 'url_name': 'high_value_list', 'prefixes': ['/SMS/high_value', '/SMS/wh_highvalue'], 'icon': 'fas fa-tasks'},
                    {'key': 'wms_highvalue_app1', 'name': 'Approval 1 (High Value)', 'url_name': 'highvalue_approval_view', 'prefixes': ['/SMS/highvalue/approval/'], 'icon': 'fas fa-check'},
                    {'key': 'wms_highvalue_app2', 'name': 'Approval 2 (High Value)', 'url_name': 'highvalue_approval2_view', 'prefixes': ['/SMS/highvalue/approval2/'], 'icon': 'fas fa-check-double'},
                    {'key': 'wms_jobs', 'name': 'Warehouse Jobs', 'url_name': 'search', 'prefixes': ['/SMS/wh_job', '/SMS/search'], 'icon': 'fas fa-dolly'},
                    {'key': 'wms_dg_cargo', 'name': 'DG Cargo', 'url_name': 'dg_cargo_list', 'prefixes': ['/SMS/dg_cargo'], 'icon': 'fas fa-biohazard'},
                    {'key': 'wms_dispatch', 'name': 'Dispatch', 'url_name': 'dispatch_search', 'prefixes': ['/SMS/dispatch'], 'icon': 'fas fa-shipping-fast'},
                ]
            },
            {
                'group_name': 'Invoicing',
                'pages': [
                    {'key': 'wms_c2c_invoice', 'name': 'Case To Case Invoice', 'url_name': 'case_to_case_open_invoice', 'prefixes': ['/SMS/case_to_case_open_invoice'], 'icon': 'fas fa-box'},
                    {'key': 'wms_dedicated_invoice', 'name': 'Dedicated Invoice', 'url_name': 'dedicated_open_invoice', 'prefixes': ['/SMS/dedicated_open_invoice'], 'icon': 'fas fa-building'},
                    {'key': 'wms_exclusive_invoice', 'name': 'Exclusive Invoice', 'url_name': 'exclusive_open_invoice', 'prefixes': ['/SMS/exclusive_open_invoice'], 'icon': 'fas fa-star'},
                    {'key': 'wms_invoice_list', 'name': 'Invoice List', 'url_name': 'invoice_list', 'prefixes': ['/SMS/invoice_list'], 'icon': 'fas fa-file-invoice'},
                ]
            },
            {
                'group_name': 'Reports & Quality',
                'pages': [
                    {'key': 'wms_reports', 'name': 'Warehouse Reports', 'url_name': 'warehouse_reports', 'prefixes': ['/SMS/warehouse_reports'], 'icon': 'fas fa-chart-pie'},
                    {'key': 'wms_gate_meeting', 'name': 'Gate Meeting Report (Daily)', 'url_name': 'gate_meeting_list', 'prefixes': ['/SMS/gate_meeting'], 'icon': 'fas fa-users'},
                    {'key': 'wms_ops_audit', 'name': 'Ops Audit Score Card', 'url_name': 'ops_audit_score_list', 'prefixes': ['/SMS/ops_audit_score'], 'icon': 'fas fa-award'},
                    {'key': 'wms_incident', 'name': 'Incident Report', 'url_name': 'incident_list', 'prefixes': ['/SMS/incident_'], 'icon': 'fas fa-exclamation-triangle'},
                    {'key': 'wms_customer_claims', 'name': 'Customer Claims (WMS)', 'url_name': 'customer_claims_list', 'prefixes': ['/SMS/customer_claims'], 'icon': 'fas fa-file-invoice-dollar'},
                    {'key': 'wms_wrong_labelling', 'name': 'Wrong Labelling', 'url_name': 'wrong_labelling_list', 'prefixes': ['/SMS/wrong_labelling'], 'icon': 'fas fa-tags'},
                    {'key': 'wms_petty_cash', 'name': 'Petty Cash (WMS)', 'url_name': 'wms_petty_cash_list', 'prefixes': ['/SMS/wms_petty_cash'], 'icon': 'fas fa-money-bill-alt'},
                ]
            },
            {
                'group_name': 'Masters & Config',
                'pages': [
                    {'key': 'wms_bays', 'name': 'Bays', 'url_name': 'bay_list', 'prefixes': ['/SMS/bay_'], 'icon': 'fas fa-th-large'},
                    {'key': 'wms_damage_report', 'name': 'Damage Report', 'url_name': 'damagereport_list', 'prefixes': ['/SMS/damagereport'], 'icon': 'fas fa-heart-broken'},
                    {'key': 'wms_units', 'name': 'Units', 'url_name': 'unit_list', 'prefixes': ['/SMS/unit_'], 'icon': 'fas fa-ruler-combined'},
                ]
            }
        ]
    },
    {
        'module_id': 'fms',
        'module_name': 'Finance Management System (FMS)',
        'icon': 'fas fa-coins',
        'color': '#f59e0b',
        'groups': [
            {
                'group_name': 'Accounting & Cash Flow',
                'pages': [
                    {'key': 'fms_ar', 'name': 'Accounts Receivable (AR)', 'url_name': 'ar_list', 'prefixes': ['/SMS/ar_list', '/SMS/ar_add', '/SMS/ar_insert'], 'icon': 'fas fa-file-invoice'},
                    {'key': 'fms_ar_receipt', 'name': 'AR Receipt List', 'url_name': 'ar_receipt_list', 'prefixes': ['/SMS/ar_receipt_list'], 'icon': 'fas fa-receipt'},
                    {'key': 'fms_ar_comments', 'name': 'AR Comments', 'url_name': 'ar_comments_list', 'prefixes': ['/SMS/ar_comments'], 'icon': 'fas fa-comments'},
                    {'key': 'fms_budget', 'name': 'Budget', 'url_name': 'budget_form_list', 'prefixes': ['/SMS/budget'], 'icon': 'fas fa-calculator'},
                    {'key': 'fms_business_revenue', 'name': 'Business Revenue', 'url_name': 'business_revenue_list', 'prefixes': ['/SMS/business_revenue'], 'icon': 'fas fa-chart-line'},
                    {'key': 'fms_expenses', 'name': 'Expenses', 'url_name': 'expense_search', 'prefixes': ['/SMS/expense'], 'icon': 'fas fa-money-check'},
                    {'key': 'fms_iou', 'name': 'IOU', 'url_name': 'iou_list', 'prefixes': ['/SMS/iou'], 'icon': 'fas fa-hand-holding-usd'},
                    {'key': 'fms_performance_audit', 'name': 'Performance Audit', 'url_name': 'performance_audit_list', 'prefixes': ['/SMS/performance_audit'], 'icon': 'fas fa-search-dollar'},
                    {'key': 'fms_reports', 'name': 'Finance Reports', 'url_name': 'finance_reports', 'prefixes': ['/SMS/finance_reports'], 'icon': 'fas fa-file-excel'},
                ]
            }
        ]
    },
    {
        'module_id': 'pms',
        'module_name': 'Packaging Management System (PMS)',
        'icon': 'fas fa-box-open',
        'color': '#8b5cf6',
        'groups': [
            {
                'group_name': 'Packaging Operations',
                'pages': [
                    {'key': 'pms_needassessment', 'name': 'Need Assessment', 'url_name': 'needassessment_list', 'prefixes': ['/SMS/needassessment'], 'icon': 'fas fa-clipboard-check'},
                    {'key': 'pms_quotation_summary', 'name': 'Quotation Summary', 'url_name': 'pk_quotationsummary_list', 'prefixes': ['/SMS/pk_quotation'], 'icon': 'fas fa-file-invoice'},
                    {'key': 'pms_purchaseorder', 'name': 'Purchase Order', 'url_name': 'purchaseorder_list', 'prefixes': ['/SMS/purchaseorder'], 'icon': 'fas fa-shopping-bag'},
                    {'key': 'pms_costingsummary', 'name': 'Indent Summary', 'url_name': 'costingsummary_list', 'prefixes': ['/SMS/costingsummary'], 'icon': 'fas fa-list-ol'},
                    {'key': 'pms_retrieval', 'name': 'Stock Retrieval', 'url_name': 'pk_retrival_list', 'prefixes': ['/SMS/pk_retrival'], 'icon': 'fas fa-boxes'},
                    {'key': 'pms_acceptance', 'name': 'Stock Acceptance', 'url_name': 'pk_acceptance_list', 'prefixes': ['/SMS/pk_acceptance', '/SMS/pk_accept'], 'icon': 'fas fa-check-circle'},
                    {'key': 'pms_production_dashboard', 'name': 'Production Dashboard', 'url_name': 'pk_production_dashboard', 'prefixes': ['/SMS/pk_production'], 'icon': 'fas fa-industry'},
                    {'key': 'pms_return_acceptance', 'name': 'Return Acceptance Queue', 'url_name': 'pk_return_acceptance_list', 'prefixes': ['/SMS/pk_return'], 'icon': 'fas fa-undo-alt'},
                    {'key': 'pms_invoice', 'name': 'Invoice (PMS)', 'url_name': 'pk_invoice_list', 'prefixes': ['/SMS/pk_invoice'], 'icon': 'fas fa-file-invoice-dollar'},
                    {'key': 'pms_gatepass', 'name': 'GatePass', 'url_name': 'packing_gate_list', 'prefixes': ['/SMS/packing_gate'], 'icon': 'fas fa-ticket-alt'},
                    {'key': 'pms_delivery', 'name': 'Delivery Challan', 'url_name': 'packing_delivery_list', 'prefixes': ['/SMS/packing_delivery'], 'icon': 'fas fa-truck'},
                    {'key': 'pms_petty_cash', 'name': 'Petty Cash (PMS)', 'url_name': 'pms_petty_cash_list', 'prefixes': ['/SMS/pms_petty_cash'], 'icon': 'fas fa-money-bill-alt'},
                ]
            }
        ]
    },
    {
        'module_id': 'admin',
        'module_name': 'Administration & System Masters',
        'icon': 'fas fa-users-cog',
        'color': '#ef4444',
        'groups': [
            {
                'group_name': 'Core Administration',
                'pages': [
                    {'key': 'admin_user_control', 'name': 'User Control (Access Rights)', 'url_name': 'user_control_view', 'prefixes': ['/SMS/user_control'], 'icon': 'fas fa-user-shield'},
                    {'key': 'admin_departments', 'name': 'Departments', 'url_name': 'department_list', 'prefixes': ['/SMS/department_'], 'icon': 'far fa-building'},
                    {'key': 'admin_user_approval', 'name': 'User Registration Approval', 'url_name': 'user_approval_list', 'prefixes': ['/SMS/user_approval'], 'icon': 'fas fa-user-check'},
                    {'key': 'admin_deletion_logs', 'name': 'Deletion Logs', 'url_name': 'deletion_log_list', 'prefixes': ['/SMS/deletion_log'], 'icon': 'fas fa-history'},
                    {'key': 'admin_customer_registration', 'name': 'Customer Registration', 'url_name': 'customer_registration_list', 'prefixes': ['/SMS/customer_registration'], 'icon': 'fas fa-id-card'},
                    {'key': 'admin_locations', 'name': 'Locations & Branches', 'url_name': 'location_list', 'prefixes': ['/SMS/location_', '/SMS/country_', '/SMS/state_', '/SMS/city_', '/SMS/places_'], 'icon': 'fas fa-map-marked-alt'},
                    {'key': 'admin_insurance', 'name': 'Insurance', 'url_name': 'insurance_list', 'prefixes': ['/SMS/insurance'], 'icon': 'fas fa-shield-alt'},
                ]
            },
            {
                'group_name': 'Customer & Vendor Masters',
                'pages': [
                    {'key': 'admin_customers', 'name': 'Customer Masters', 'url_name': 'customer_list', 'prefixes': ['/SMS/customer_', '/SMS/customertype_', '/SMS/crcountfrom_', '/SMS/customername_', '/SMS/customerdepartment_', '/SMS/gstexcepmtion_', '/SMS/gstmodel_', '/SMS/paymenttype_', '/SMS/trbusinesstype_'], 'icon': 'fas fa-users'},
                    {'key': 'admin_vendors', 'name': 'Vendor Masters (VMS)', 'url_name': 'vendor_list', 'prefixes': ['/SMS/vendor_'], 'icon': 'fas fa-handshake'},
                ]
            },
            {
                'group_name': 'Transport & Warehouse Masters',
                'pages': [
                    {'key': 'admin_transport_masters', 'name': 'Transport & Fleet Masters', 'url_name': 'location_master_list', 'prefixes': ['/SMS/location_master', '/SMS/charge_master', '/SMS/trans_fastag', '/SMS/bunkname', '/SMS/vehiclemaster', '/SMS/halting', '/SMS/vehiclecategory', '/SMS/vehicletype', '/SMS/movementtype', '/SMS/vhmanufacturer', '/SMS/vehiclemodel', '/SMS/ownership', '/SMS/body_', '/SMS/axletype', '/SMS/fueltype', '/SMS/vehiclecolour', '/SMS/permittype', '/SMS/rtratemaster', '/SMS/vendorratemaster'], 'icon': 'fas fa-truck-moving'},
                    {'key': 'admin_warehouse_masters', 'name': 'Warehouse Masters', 'url_name': 'whratemaster_list', 'prefixes': ['/SMS/whratemaster', '/SMS/locationmaster', '/SMS/materialhandling', '/SMS/packagetype', '/SMS/currencytype', '/SMS/stocktype'], 'icon': 'fas fa-cubes'},
                    {'key': 'admin_packing_masters', 'name': 'Packing Masters', 'url_name': 'stockpurchases_list', 'prefixes': ['/SMS/stockpurchases', '/SMS/stock_description', '/SMS/part_code', '/SMS/pk_stock_vendor', '/SMS/pk_purchase_return', '/SMS/pk_tool_master'], 'icon': 'fas fa-boxes'},
                ]
            }
        ]
    },
    {
        'module_id': 'ems',
        'module_name': 'Employee Management System (EMS)',
        'icon': 'fas fa-id-badge',
        'color': '#06b6d4',
        'groups': [
            {
                'group_name': 'Employees & Roles',
                'pages': [
                    {'key': 'ems_employees', 'name': 'Employees Directory', 'url_name': 'user_list', 'prefixes': ['/SMS/user_list', '/SMS/user_insert', '/SMS/user_update', '/SMS/user_delete', '/SMS/emp_'], 'icon': 'fas fa-user-friends'},
                    {'key': 'ems_designations', 'name': 'Designations', 'url_name': 'designation_list', 'prefixes': ['/SMS/designation_'], 'icon': 'fas fa-briefcase'},
                    {'key': 'ems_roles', 'name': 'Roles', 'url_name': 'role_list', 'prefixes': ['/SMS/role_'], 'icon': 'fas fa-user-tag'},
                ]
            }
        ]
    },
    {
        'module_id': 'ams',
        'module_name': 'Asset Management System (AMS)',
        'icon': 'fas fa-drafting-compass',
        'color': '#ec4899',
        'groups': [
            {
                'group_name': 'Assets & Products',
                'pages': [
                    {'key': 'ams_assets', 'name': 'Assets Search & Assignment', 'url_name': 'assign_asset_search', 'prefixes': ['/SMS/asset_', '/SMS/assign_asset', '/SMS/unassigned_asset'], 'icon': 'fas fa-laptop'},
                    {'key': 'ams_products', 'name': 'Products & Categories', 'url_name': 'product_list', 'prefixes': ['/SMS/product_', '/SMS/producttype_'], 'icon': 'fas fa-barcode'},
                    {'key': 'ams_reports', 'name': 'Asset Reports', 'url_name': 'reports', 'prefixes': ['/SMS/reports'], 'icon': 'fas fa-file-alt'},
                ]
            }
        ]
    },
    {
        'module_id': 'prime',
        'module_name': 'Express (Prime)',
        'icon': 'fas fa-shipping-fast',
        'color': '#f97316',
        'groups': [
            {
                'group_name': 'Prime Operations',
                'pages': [
                    {'key': 'prime_enquiry', 'name': 'Prime Booking Note', 'url_name': 'prime_enquiry_list', 'prefixes': ['/SMS/prime_enquiry'], 'icon': 'fas fa-clipboard-list'},
                    {'key': 'prime_allotment', 'name': 'Prime Vehicle Allotment', 'url_name': 'prime_vehicle_allotment_list', 'prefixes': ['/SMS/prime_vehicle_allotment'], 'icon': 'fas fa-truck-loading'},
                    {'key': 'prime_trip', 'name': 'Prime Trip Detail', 'url_name': 'prime_trip_list', 'prefixes': ['/SMS/prime_trip'], 'icon': 'fas fa-route'},
                ]
            }
        ]
    },
    {
        'module_id': 'sales',
        'module_name': 'Sales & Customer Management (SMS)',
        'icon': 'fas fa-chart-line',
        'color': '#14b8a6',
        'groups': [
            {
                'group_name': 'Sales Pipeline',
                'pages': [
                    {'key': 'sales_search', 'name': 'Sales List', 'url_name': 'sales_search', 'prefixes': ['/SMS/sales_search'], 'icon': 'fas fa-chart-bar'},
                    {'key': 'sales_target', 'name': 'Sales Target', 'url_name': 'sales_target_list', 'prefixes': ['/SMS/sales_target'], 'icon': 'fas fa-bullseye'},
                    {'key': 'sales_reports', 'name': 'Sales Reports', 'url_name': 'sales_reports', 'prefixes': ['/SMS/sales_reports'], 'icon': 'fas fa-file-contract'},
                    {'key': 'sales_enquiry', 'name': 'Sales Enquiry', 'url_name': 'sale_enquiry_list', 'prefixes': ['/SMS/sale_enquiry'], 'icon': 'fas fa-phone'},
                ]
            }
        ]
    },
    {
        'module_id': 'supports',
        'module_name': 'Supports & Timesheet',
        'icon': 'fas fa-headset',
        'color': '#6366f1',
        'groups': [
            {
                'group_name': 'Requirements & Time',
                'pages': [
                    {'key': 'supports_requirements', 'name': 'Requirements & Bug Tracker', 'url_name': 'requirements_search', 'prefixes': ['/SMS/requirements_', '/SMS/open_requirements'], 'icon': 'fas fa-bug'},
                    {'key': 'supports_tasks', 'name': 'Task List', 'url_name': 'task_list', 'prefixes': ['/SMS/task_'], 'icon': 'fas fa-tasks'},
                    {'key': 'supports_timesheets', 'name': 'Time Sheet & Reports', 'url_name': 'timesheet_list', 'prefixes': ['/SMS/timesheet_'], 'icon': 'fas fa-clock'},
                ]
            }
        ]
    }
]

# Overall Movement Visibility Scope Catalog (Displayed as overall top section)
BRANCH_MOVEMENTS_CATALOG = [
    {
        'key': 'tms_branch_maa',
        'name': 'Chennai (MAA) Movements',
        'code': 'MAA',
        'prefixes': [],
        'icon': 'fas fa-city',
        'desc': 'Shows all Chennai (MAA) movements, bookings & trips'
    },
    {
        'key': 'tms_branch_blr',
        'name': 'Bengaluru (BLR) Movements',
        'code': 'BLR',
        'prefixes': [],
        'icon': 'fas fa-city',
        'desc': 'Shows all Bengaluru (BLR) movements, bookings & trips'
    },
    {
        'key': 'tms_branch_hyd',
        'name': 'Hyderabad (HYD) Movements',
        'code': 'HYD',
        'prefixes': [],
        'icon': 'fas fa-city',
        'desc': 'Shows all Hyderabad (HYD) movements, bookings & trips'
    },
    {
        'key': 'tms_branch_cjb',
        'name': 'Coimbatore (CJB) Movements',
        'code': 'CJB',
        'prefixes': [],
        'icon': 'fas fa-city',
        'desc': 'Shows all Coimbatore (CJB) movements, bookings & trips'
    },
    {
        'key': 'tms_branch_pny',
        'name': 'Pondicherry (PNY) Movements',
        'code': 'PNY',
        'prefixes': [],
        'icon': 'fas fa-city',
        'desc': 'Shows all Pondicherry (PNY) movements, bookings & trips'
    },
]

BRANCH_CODE_MAP = {bm['key']: bm['code'] for bm in BRANCH_MOVEMENTS_CATALOG}
ALL_BRANCH_CODES = set(BRANCH_CODE_MAP.values())

def get_all_page_keys():
    """Returns a flat list of all functional page keys in the catalog (excluding movement branch scopes)."""
    keys = []
    for mod in PAGE_CATALOG:
        for grp in mod.get('groups', []):
            for p in grp.get('pages', []):
                keys.append(p['key'])
    return keys

def get_movement_keys():
    """Returns the set of page keys reserved for branch movement scopes."""
    return set(BRANCH_CODE_MAP.keys())

def get_page_by_key(page_key):
    """Finds a single page dict by its key."""
    for p in BRANCH_MOVEMENTS_CATALOG:
        if p['key'] == page_key:
            return p
    for mod in PAGE_CATALOG:
        for grp in mod.get('groups', []):
            for p in grp.get('pages', []):
                if p['key'] == page_key:
                    return p
    return None

def get_default_available_page_keys_for_user(user):
    """
    Determines the baseline set of available (permitted) pages for a user
    based on the system's role, department, organisation, and special permissions logic
    from middleware.py and home_page.html.
    Pages not in this set are currently BLOCKED for the user.
    """
    all_keys = set(get_all_page_keys())

    # Retrieve user extended info
    user_ext = getattr(user, 'user_extinfo', None)
    if not user_ext:
        from ..models import User_extInfo
        try:
            user_ext = User_extInfo.objects.select_related(
                'emp_organisation', 'department', 'emp_role', 'emp_designation'
            ).get(user=user)
        except Exception:
            user_ext = None

    if not user_ext and not (user.is_superuser or user.is_staff):
        return set()

    role_name = (user_ext.emp_role.role_name if user_ext and user_ext.emp_role else '').lower().strip()
    org_id = user_ext.emp_organisation_id if user_ext and user_ext.emp_organisation else None
    org_name = str(user_ext.emp_organisation).lower() if user_ext and user_ext.emp_organisation else ''
    dept_name = str(user_ext.department).lower() if user_ext and user_ext.department else ''
    desig_name = str(user_ext.emp_designation).lower() if user_ext and user_ext.emp_designation else ''
    user_id = user.id

    is_admin = role_name in ['admin', 'super user', 'superuser'] or user.is_superuser or user.is_staff

    if is_admin:
        available_keys = all_keys.copy()
        if role_name in ['admin', 'super user', 'superuser']:
            available_keys |= set(BRANCH_CODE_MAP.keys())
    else:
        # Determine allowed modules for regular staff based on middleware & home_page logic
        allowed_modules = set()

        # TMS Manager override
        is_tms_mgr = (role_name == 'user' and 'trans' in org_name and 'manager' in desig_name)
        if is_tms_mgr:
            allowed_modules.update(['tms', 'prime'])
        else:
            # Department based access
            if 'corporate' in dept_name:
                allowed_modules.update(['cms', 'vms', 'ams', 'tms', 'wms', 'pms', 'fms', 'sales', 'prime', 'supports'])
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
                elif org_id == 2 or 'trans' in org_name or user.username.upper().startswith('TRA'):
                    allowed_modules.update(['tms', 'prime'])
                elif org_id == 3 or 'pack' in org_name or user.username.upper().startswith('PK'):
                    allowed_modules.add('pms')
                else:
                    allowed_modules.update(['tms', 'wms', 'prime'])

            # Role based access for Customer vs Internal staff
            if role_name == 'customer' or getattr(user_ext, 'emp_role_id', None) == 4 or getattr(user_ext, 'linked_customer_id', None) is not None:
                # External customer accounts only access customer portal
                allowed_modules = {'cms'}
            else:
                # Business Solution / Organisation based access for internal staff:
                # Org 1: BVM Storage Solutions (WMS)
                if org_id == 1 or 'storage' in org_name:
                    allowed_modules.add('wms')
                # Org 2: BVM Trans Solutions (TMS)
                if org_id == 2 or 'trans' in org_name or user.username.upper().startswith('TRA'):
                    allowed_modules.update(['tms', 'prime'])
                # Org 3: BVM Pack Solutions (PMS)
                if org_id == 3 or 'pack' in org_name or user.username.upper().startswith('PK'):
                    allowed_modules.add('pms')

        # Specific user whitelist overrides from home_page.html
        if user_id in (57, 140, 142, 143):
            allowed_modules.update(['admin', 'cms', 'vms'])

        available_keys = set()
        for mod in PAGE_CATALOG:
            mod_id = mod['module_id']
            for grp in mod.get('groups', []):
                for p in grp.get('pages', []):
                    pkey = p['key']

                    # Check module-level membership
                    if mod_id in allowed_modules:
                        # Specific sub-page blocks:
                        if pkey == 'tms_trip_approval' and user_id not in (1, 2, 57, 68, 86, 93, 142, 143, 158, 164):
                            continue  # Blocked for regular users
                        if pkey == 'wms_highvalue_app2' and user_id not in (1, 2, 36, 93):
                            continue  # Strictly ID restricted
                        if pkey in ('supports_tasks', 'supports_timesheets'):
                            continue  # Handled strictly via ID whitelists below
                        if pkey in ('tms_finance_approval_trip', 'tms_finance_approval_admin'):
                            if 'finance' not in dept_name and role_name not in ['admin', 'super user', 'superuser'] and not user.is_superuser:
                                continue  # Finance approvals belong strictly to Finance
                        if pkey in ('tms_sell_rate_approval', 'tms_manager_approval', 'tms_checklist_approval'):
                            if role_name not in ['admin', 'super user', 'superuser', 'manager'] and 'manager' not in role_name and not user.is_superuser:
                                continue  # Rate, job card, and checklist approvals belong strictly to Managers/Admins
                        if pkey in ('admin_user_approval', 'admin_user_control', 'admin_deletion_logs'):
                            if role_name not in ['admin', 'super user', 'superuser'] and not user.is_superuser:
                                continue  # Blocked for non-admins
                        if pkey in ('tms_enquirynote', 'prime_enquiry') and ('operation' in dept_name or getattr(user_ext, 'department_id', None) == 2):
                            if role_name not in ['admin', 'super user', 'superuser'] and not user.is_superuser:
                                continue  # Booking Note is owned by Customer Service, not Operations
                        available_keys.add(pkey)

                    # Special checks for individual pages:
                    elif mod_id == 'supports':
                        if pkey == 'supports_requirements':
                            available_keys.add(pkey)

                    # Specific customer / vendor master pages when cms/vms is allowed
                    elif mod_id == 'admin':
                        if pkey == 'admin_customers' and 'cms' in allowed_modules:
                            available_keys.add(pkey)
                        elif pkey == 'admin_vendors' and 'vms' in allowed_modules:
                            available_keys.add(pkey)

    # STRICT ID-RESTRICTED PAGES ENFORCEMENT (Applies to ALL users across the board):
    # 1. Trip Approval: strictly restricted to [1, 2, 57, 68, 86, 93, 142, 143, 158, 164]
    TRIP_APPROVAL_IDS = {1, 2, 57, 68, 86, 93, 142, 143, 158, 164}
    if user_id in TRIP_APPROVAL_IDS:
        available_keys.add('tms_trip_approval')
    else:
        available_keys.discard('tms_trip_approval')

    # 2. Tasks: strictly restricted to [1, 86, 88, 93, 100, 158, 164]
    SUPPORTS_TASK_IDS = {1, 86, 88, 93, 100, 158, 164}
    if user_id in SUPPORTS_TASK_IDS:
        available_keys.add('supports_tasks')
    else:
        available_keys.discard('supports_tasks')

    # 3. Timesheets: strictly restricted to [1]
    if user_id == 1:
        available_keys.add('supports_timesheets')
    else:
        available_keys.discard('supports_timesheets')

    # 4. Approval 2 (High Value): strictly restricted to [1, 2, 36, 93]
    HV2_APPROVAL_IDS = {1, 2, 36, 93}
    if user_id in HV2_APPROVAL_IDS:
        available_keys.add('wms_highvalue_app2')
    else:
        available_keys.discard('wms_highvalue_app2')

    # 5. Administration / Customer / Vendor masters:
    # Strictly for designated IDs [57, 140, 142, 143] as well as all Admins & Super Users:
    ADMIN_ID_MASTERS = [
        'admin_customers',
        'admin_vendors',
        'admin_departments',
        'admin_locations',
        'admin_insurance',
        'admin_transport_masters',
    ]
    if is_admin or user_id in (57, 140, 142, 143):
        available_keys.update(ADMIN_ID_MASTERS)

    # Overall Movement Visibility default baseline across all branches
    branch_str = str(user_ext.emp_branch or '').upper() if user_ext else ''
    is_admin = role_name in ['admin', 'super user', 'superuser'] or 'corporate' in dept_name or user.is_superuser or user.is_staff

    # Department-level users who must have all branch movement visibility scopes UNCHECKED by default
    is_dept_level_user = (
        'operation' in dept_name or getattr(user_ext, 'department_id', None) == 2 or
        'customer service' in dept_name or getattr(user_ext, 'department_id', None) == 4 or
        'sales' in dept_name or getattr(user_ext, 'department_id', None) == 5 or
        'warehouse' in dept_name or org_id == 1 or 'storage' in org_name or
        role_name == 'customer' or getattr(user_ext, 'emp_role_id', None) == 4 or
        getattr(user_ext, 'linked_customer_id', None) is not None or getattr(user_ext, 'is_lp_customer', False)
    )

    if role_name == 'customer' or getattr(user_ext, 'emp_role_id', None) == 4 or getattr(user_ext, 'linked_customer_id', None) is not None or getattr(user_ext, 'is_lp_customer', False):
        # Customers never get branch movements
        pass
    elif is_dept_level_user and not is_admin:
        # Department level users (Operations, Customer Service, Sales, Warehouse) have all branch movement visibility unchecked by default
        pass
    elif is_admin or not branch_str:
        # Admins, superusers, and corporate get ALL branches ON by default
        for pkey in BRANCH_CODE_MAP.keys():
            available_keys.add(pkey)
    else:
        # User gets their assigned branch ON, others OFF
        matched = False
        for pkey, code in BRANCH_CODE_MAP.items():
            if code in branch_str:
                available_keys.add(pkey)
                matched = True
        if not matched:
            pass

    return available_keys

MODULE_THEME_MAP = {
    'dashboard': {'class': 'mod-header-dashboard', 'badge': '#1e40af'},
    'sales': {'class': 'mod-header-enquiry', 'badge': '#166534'},
    'tms': {'class': 'mod-header-tms', 'badge': '#854d0e'},
    'wms': {'class': 'mod-header-wms', 'badge': '#5b21b6'},
    'pms': {'class': 'mod-header-pms', 'badge': '#115e59'},
    'fms': {'class': 'mod-header-fms', 'badge': '#065f46'},
    'prime': {'class': 'mod-header-prime', 'badge': '#3730a3'},
    'ams': {'class': 'mod-header-ams', 'badge': '#334155'},
    'ems': {'class': 'mod-header-ems', 'badge': '#9f1239'},
    'admin': {'class': 'mod-header-master', 'badge': '#991b1b'},
    'supports': {'class': 'mod-header-dashboard', 'badge': '#1e40af'},
}

def get_catalog_for_user(user, granted_keys=None):
    """
    Returns the complete catalog with granular CRUD permissions (can_view, can_create, can_edit, can_delete)
    and has_access boolean flag attached to each page and counts for each module/group.
    If granted_keys is None, checks UserPageAccess. If no custom records exist,
    defaults to the user's baseline available pages.
    """
    from ..models import UserPageAccess
    user_access_qs = UserPageAccess.objects.filter(user=user)
    has_custom = user_access_qs.exists() and not (user.is_superuser or user.is_staff)

    if has_custom:
        access_map = {row.page_key: row for row in user_access_qs}
        granted_keys = {row.page_key for row in user_access_qs if row.can_view}
    else:
        access_map = {}
        if granted_keys is None:
            granted_keys = get_default_available_page_keys_for_user(user)
        else:
            granted_keys = set(granted_keys)

    catalog_data = []
    for mod in PAGE_CATALOG:
        theme = MODULE_THEME_MAP.get(mod['module_id'], {'class': 'mod-header-tms', 'badge': '#1e293b'})
        mod_copy = {
            'module_id': mod['module_id'],
            'module_name': mod['module_name'],
            'icon': mod['icon'],
            'color': mod['color'],
            'theme_class': theme['class'],
            'badge_color': theme['badge'],
            'total_pages': 0,
            'granted_pages': 0,
            'pages': [],
            'groups': []
        }
        for grp in mod.get('groups', []):
            grp_copy = {
                'group_name': grp['group_name'],
                'total_pages': 0,
                'granted_pages': 0,
                'pages': []
            }
            for p in grp.get('pages', []):
                pkey = p['key']
                if has_custom:
                    row = access_map.get(pkey)
                    if row:
                        can_v = bool(row.can_view)
                        can_c = bool(row.can_create)
                        can_e = bool(row.can_edit)
                        can_d = bool(row.can_delete)
                    else:
                        can_v = False
                        can_c = False
                        can_e = False
                        can_d = False
                else:
                    can_v = pkey in granted_keys
                    can_c = can_v
                    can_e = can_v
                    user_role = getattr(getattr(user, 'user_extinfo', None), 'emp_role', None)
                    role_str = (user_role.role_name.lower().strip() if user_role else '')
                    is_customer = ('cust' in role_str)
                    can_d = False if is_customer else can_v

                p_copy = dict(p)
                p_copy['has_access'] = can_v
                p_copy['can_view'] = can_v
                p_copy['can_create'] = can_c
                p_copy['can_edit'] = can_e
                p_copy['can_delete'] = can_d
                p_copy['group_name'] = grp['group_name']

                grp_copy['pages'].append(p_copy)
                mod_copy['pages'].append(p_copy)
                grp_copy['total_pages'] += 1
                if can_v:
                    grp_copy['granted_pages'] += 1

            mod_copy['total_pages'] += grp_copy['total_pages']
            mod_copy['granted_pages'] += grp_copy['granted_pages']
            mod_copy['groups'].append(grp_copy)

        catalog_data.append(mod_copy)

    return catalog_data, granted_keys

def get_user_allowed_route_prefixes(user):
    """
    Returns a set of URL route prefixes that the user is allowed to access
    based on their UserPageAccess records or baseline permissions.
    """
    from ..models import UserPageAccess
    user_access_qs = UserPageAccess.objects.filter(user=user)
    if user_access_qs.exists():
        user_keys = set(user_access_qs.filter(can_view=True).values_list('page_key', flat=True))
    else:
        user_keys = get_default_available_page_keys_for_user(user)

    prefixes = set()
    for mod in PAGE_CATALOG:
        for grp in mod.get('groups', []):
            for p in grp.get('pages', []):
                if p['key'] in user_keys:
                    prefixes.update(p.get('prefixes', []))
    return prefixes

def get_user_movement_branches(user):
    """
    Returns the set of branch codes (e.g. {'MAA'}, {'BLR'}, {'HYD'}, etc.)
    that the user is permitted to see based on their UserPageAccess toggles.
    If the user is superuser/admin, returns ALL_BRANCH_CODES (meaning unrestricted cross-branch access).
    """
    if not user or not user.is_authenticated:
        return ALL_BRANCH_CODES

    if user.is_superuser or user.is_staff:
        return ALL_BRANCH_CODES

    user_ext = getattr(user, 'user_extinfo', None)
    role_name = (user_ext.emp_role.role_name if user_ext and user_ext.emp_role else '').lower().strip()
    if role_name in ['admin', 'super user', 'superuser']:
        return ALL_BRANCH_CODES

    from ..models import UserPageAccess
    user_access_qs = UserPageAccess.objects.filter(user=user)
    if user_access_qs.exists() and not (user.is_superuser or user.is_staff):
        keys = set(user_access_qs.filter(can_view=True).values_list('page_key', flat=True))
    else:
        keys = get_default_available_page_keys_for_user(user)

    return {code for pkey, code in BRANCH_CODE_MAP.items() if pkey in keys}


# Lookup map of route prefixes to page keys for fast CRUD routing resolution
PREFIX_TO_PAGE_MAP = {}
for _mod in PAGE_CATALOG:
    for _grp in _mod.get('groups', []):
        for _p in _grp.get('pages', []):
            for _pfx in _p.get('prefixes', []):
                PREFIX_TO_PAGE_MAP[_pfx] = _p['key']


def resolve_request_crud(path):
    """
    Given a request path, returns:
    (action, page_key)
    action is one of ('view', 'create', 'edit', 'delete')
    """
    if not path:
        return None, None

    matched_prefix = None
    matched_page_key = None
    for pfx, pkey in PREFIX_TO_PAGE_MAP.items():
        if path.startswith(pfx):
            if matched_prefix is None or len(pfx) > len(matched_prefix):
                matched_prefix = pfx
                matched_page_key = pkey

    if not matched_prefix or not matched_page_key:
        return None, None

    url_name = ''
    func_name = ''
    try:
        from django.urls import resolve
        match = resolve(path)
        url_name = match.url_name or ''
        func_name = getattr(match.func, '__name__', '')
    except Exception:
        pass

    clean_path = path.rstrip('/')
    base_segment = clean_path.split('/')[-1] if not clean_path.split('/')[-1].isdigit() else clean_path.split('/')[-2]
    combined_tokens = [base_segment, path, url_name, func_name]

    # Explicit route handling: non-standard Create/Add form URLs
    if clean_path in ('/SMS/market_bill', '/market_bill',
                      '/SMS/budget_form', '/budget_form',
                      '/SMS/packing_gate', '/packing_gate',
                      '/SMS/packing_delivery', '/packing_delivery'):
        return 'create', matched_page_key

    # Delete
    if any(any(k in tok for k in ['_delete', 'delete_', '/delete', '/delete/']) for tok in combined_tokens):
        return 'delete', matched_page_key

    # Specific parameterized edit routes using an add URL pattern (e.g. dg_cargo_add/<id>/)
    if clean_path.split('/')[-1].isdigit() and 'dg_cargo_add' in base_segment:
        return 'edit', matched_page_key

    # Edit / Update
    if any(any(k in tok for k in ['_update', 'update_', '/update', '_edit', 'edit_', '/edit', '_modify', '_upload', '/upload', 'approve', '_approve']) for tok in combined_tokens):
        return 'edit', matched_page_key

    # Create / Insert / Add
    if any(any(k in tok for k in ['_insert', '_add', 'add_', '_create', '/add', '/add/']) for tok in combined_tokens):
        return 'create', matched_page_key

    return 'view', matched_page_key


def get_user_page_crud_permissions(user, page_key):
    """
    Returns {'can_view': bool, 'can_create': bool, 'can_edit': bool, 'can_delete': bool}
    for the specified user and page_key.
    """
    if not user or not user.is_authenticated:
        return {'can_view': False, 'can_create': False, 'can_edit': False, 'can_delete': False}

    if user.is_superuser or user.is_staff:
        return {'can_view': True, 'can_create': True, 'can_edit': True, 'can_delete': True}

    from ..models import UserPageAccess, User_extInfo
    user_access_qs = UserPageAccess.objects.filter(user=user)
    has_custom = user_access_qs.exists()

    if has_custom:
        rec = user_access_qs.filter(page_key=page_key).first()
        if rec:
            return {
                'can_view': bool(rec.can_view),
                'can_create': bool(rec.can_create),
                'can_edit': bool(rec.can_edit),
                'can_delete': bool(rec.can_delete),
            }
        else:
            return {'can_view': False, 'can_create': False, 'can_edit': False, 'can_delete': False}
    else:
        baseline_keys = get_default_available_page_keys_for_user(user)
        can_v = (page_key in baseline_keys)
        user_role = getattr(getattr(user, 'user_extinfo', None), 'emp_role', None)
        role_str = (user_role.role_name.lower().strip() if user_role else '')
        is_customer = ('cust' in role_str)
        return {
            'can_view': can_v,
            'can_create': can_v,
            'can_edit': can_v,
            'can_delete': (False if is_customer else can_v),
        }


MODULE_DOM_MAP = {
    'tms': 'transport',
    'wms': 'warehouse',
    'fms': 'finance',
    'pms': 'packing',
    'admin': 'administration',
    'ems': 'employee_management_system',
    'ams': 'asset',
    'prime': 'express_prime',
    'sales': 'sales',
    'supports': 'supports',
}


def get_user_navigation_permissions(user):
    """
    Returns navigation permissions for the sidebar on home_page:
    - blocked_prefixes: list of URL prefixes that are blocked for this user
    - allowed_prefixes: list of URL prefixes that are allowed
    - blocked_module_dom_ids: list of DOM IDs for sidebar modules that have 0 granted pages
    - allowed_module_dom_ids: list of DOM IDs for sidebar modules that have >= 1 granted pages
    - is_admin: whether user is admin or superuser
    """
    if not user or not user.is_authenticated:
        return {
            'is_admin': False,
            'blocked_prefixes': [],
            'allowed_prefixes': [],
            'blocked_module_dom_ids': list(MODULE_DOM_MAP.values()),
            'allowed_module_dom_ids': []
        }

    is_admin = user.is_superuser or user.is_staff
    if not is_admin:
        try:
            from ..models import User_extInfo
            user_ext = User_extInfo.objects.select_related('emp_role').get(user=user)
            role_name = (user_ext.emp_role.role_name if user_ext.emp_role else '').lower().strip()
            if role_name in ['admin', 'super user', 'superuser']:
                is_admin = True
        except Exception:
            pass

    if is_admin:
        return {
            'is_admin': True,
            'blocked_prefixes': [],
            'allowed_prefixes': [],
            'blocked_module_dom_ids': [],
            'allowed_module_dom_ids': list(MODULE_DOM_MAP.values())
        }

    catalog_data, granted_keys = get_catalog_for_user(user)

    blocked_prefixes = []
    allowed_prefixes = []
    blocked_module_dom_ids = []
    allowed_module_dom_ids = []

    for mod in catalog_data:
        dom_id = MODULE_DOM_MAP.get(mod['module_id'])
        if mod['granted_pages'] == 0:
            if dom_id:
                blocked_module_dom_ids.append(dom_id)
        else:
            if dom_id:
                allowed_module_dom_ids.append(dom_id)

        for grp in mod.get('groups', []):
            for p in grp.get('pages', []):
                prefixes = p.get('prefixes', [])
                if p.get('has_access'):
                    allowed_prefixes.extend(prefixes)
                else:
                    blocked_prefixes.extend(prefixes)

    return {
        'is_admin': False,
        'blocked_prefixes': list(set(blocked_prefixes)),
        'allowed_prefixes': list(set(allowed_prefixes)),
        'blocked_module_dom_ids': blocked_module_dom_ids,
        'allowed_module_dom_ids': allowed_module_dom_ids
    }


def apply_movement_branch_filter(queryset, user, field_name='en_enquirynumber'):
    """
    Applies movement branch scoping based on the user's allocated branch toggles in User Control.
    If the user has unrestricted access (e.g. Superuser/Admin or all branches checked), returns queryset unchanged.
    Otherwise filters where field_name contains ANY of the user's permitted branch codes.
    """
    from django.db.models import Q
    allowed_branches = get_user_movement_branches(user)
    if allowed_branches == ALL_BRANCH_CODES:
        return queryset

    q = Q()
    for code in allowed_branches:
        q |= Q(**{f"{field_name}__icontains": code})
    return queryset.filter(q)

