from django.urls import path
from django.views.generic import TemplateView

from . import views
from django.contrib.auth import views as auth_views  # import this

urlpatterns = [
    path('print_pdf', views.print_pdf, name='print_pdf'),  # Print PDF
    path('asset_qr_id/<int:asset_qr_id>', views.qr_code_asset, name='asset_qr_id'),  # qr_code
    path('goods_qr_id/<int:goods_qr_id>', views.qr_code_goods, name='goods_qr_id'),  # goods qr_code
    path('registration_page', views.registration_page, name='registration_page'),  # Registration_page
    path('login_page', views.login_page, name='login_page'),  # Login_page
    path('logout_page', views.logout_page, name='logout_page'),  # Logout_page
    path('driver/login/', views.driver_login, name='driver_login'),
    path('driver/login/', views.driver_login, name='driver_login'),
    path('driver/logout/', views.driver_logout, name='driver_logout'),
    path('driver/dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('home_page', views.home_page, name='home_page'),  # Home_page
    path('asset_insert', views.assetinfo_add, name='asset_insert'),  # Add Asset
    path('asset_update/<int:asset_id>/', views.assetinfo_add, name='asset_update'),  # Update asset
    path('asset_delete/<int:asset_id>/', views.asset_delete, name='asset_delete'),  # Delete asset
    path('asset_list/', views.asset_list, name='asset_list'),  # List Asset
    path('user_list/', views.user_list, name='user_list'),  # List user,
    path('user_insert', views.user_add, name='user_insert'),  # Add user
    path('user_update/<int:user_id>/', views.user_add, name='user_update'),  # Update User
    path('user_delete/<int:user_id>/', views.user_delete, name='user_delete'),  # Delete User
    path('vendor_list/', views.vendor_list, name='vendor_list'),  # List vendor,
    path('vendor_insert', views.vendor_add, name='vendor_insert'),  # Add vendor
    path('vendor_update/<int:vendor_id>/', views.vendor_add, name='vendor_update'),  # Update Vendor
    path('vendor_delete/<int:vendor_id>/', views.vendor_delete, name='vendor_delete'),  # Delete Vendor
    path('location_list/', views.location_list, name='location_list'),  # List location,
    path('location_insert', views.location_add, name='location_insert'),  # Add location
    path('location_update/<int:location_id>/', views.location_add, name='location_update'),  # Update location
    path('location_delete/<int:location_id>/', views.location_delete, name='location_delete'),  # Delete location
    path('department_list/', views.department_list, name='department_list'),  # List department,
    path('department_insert', views.department_add, name='department_insert'),  # Add department
    path('department_update/<int:department_id>/', views.department_add, name='department_update'),  # Update department
    path('department_delete/<int:department_id>/', views.department_delete, name='department_delete'),
    # Delete department
    path('product_list/', views.product_list, name='product_list'),  # List product,
    path('product_insert', views.product_add, name='product_insert'),  # Add product
    path('product_update/<int:product_id>/', views.product_add, name='product_update'),  # Update product
    path('product_delete/<int:product_id>/', views.product_delete, name='product_delete'),  # Delete product
    path('producttype_list/', views.producttype_list, name='producttype_list'),  # List producttype,
    path('producttype_insert', views.producttype_add, name='producttype_insert'),  # Add producttype
    path('producttype_update/<int:producttype_id>/', views.producttype_add, name='producttype_update'),
    # Update producttype
    path('producttype_delete/<int:producttype_id>/', views.producttype_delete, name='producttype_delete'),
    # Delete producttype
    path('country_list/', views.country_list, name='country_list'),  # List country,
    path('country_insert', views.country_add, name='country_insert'),  # Add country
    path('country_update/<int:country_id>/', views.country_add, name='country_update'),  # Update country
    path('country_delete/<int:country_id>/', views.country_delete, name='country_delete'),  # Delete country
    path('state_list/', views.state_list, name='state_list'),  # List state,
    path('state_insert', views.state_add, name='state_insert'),  # Add state
    path('state_update/<int:state_id>/', views.state_add, name='state_update'),  # Update state
    path('state_delete/<int:state_id>/', views.state_delete, name='state_delete'),  # Delete state
    path('city_list/', views.city_list, name='city_list'),  # List city,
    path('city_insert', views.city_add, name='city_insert'),  # Add city
    path('city_update/<int:city_id>/', views.city_add, name='city_update'),  # Update city
    path('city_delete/<int:city_id>/', views.city_delete, name='city_delete'),  # Delete city
    path('insurance_list/', views.insurance_list, name='insurance_list'),  # List insurance,
    path('insurance_insert', views.insurance_add, name='insurance_insert'),  # Add insurance
    path('insurance_update/<int:insurance_id>/', views.insurance_add, name='insurance_update'),  # Update insurance
    path('insurance_delete/<int:insurance_id>/', views.insurance_delete, name='insurance_delete'),  # Delete insurance
    path('insurancetype_list/', views.insurancetype_list, name='insurancetype_list'),  # List insurancetype,
    path('insurancetype_insert', views.insurancetype_add, name='insurancetype_insert'),  # Add insurancetype
    path('insurancetype_update/<int:insurancetype_id>/', views.insurancetype_add, name='insurancetype_update'),
    # Update insurancetype
    path('insurancetype_delete/<int:insurancetype_id>/', views.insurancetype_delete, name='insurancetype_delete'),
    # Delete insurancetype
    path('service_list/', views.service_list, name='service_list'),  # List service,
    path('service_insert', views.service_add, name='service_insert'),  # Add service
    path('service_update/<int:service_id>/', views.service_add, name='service_update'),  # Update service
    path('service_delete/<int:service_id>/', views.service_delete, name='service_delete'),  # Delete service
    path('goods_list/', views.goods_list, name='goods_list'),  # List goods,
    path('goods_insert', views.goods_add, name='goods_insert'),  # Add goods
    path('goods_update/<int:goods_id>/', views.goods_add, name='goods_update'),  # Update goods
    path('goods_delete/<int:goods_id>/', views.goods_delete, name='goods_delete'),  # Delete goods
    path('assign_asset_list/<int:user_id>/', views.assign_asset_list_new, name='assign_asset_list'),
    # List assign_asset,
    path('assign_asset_insert', views.assign_asset_add, name='assign_asset_insert'),  # Add assign_asset
    path('assign_asset_search', views.asset_search, name='assign_asset_search'),  # search assign_asset
    path('unassigned_asset_list', views.un_assigned_asset_list, name='unassigned_asset_list'),
    # search unassigned_asset_list
    path('assign_asset_update/<int:assign_asset_id>/', views.assign_asset_add, name='assign_asset_update'),
    # Update assign_asset
    path('assign_asset_delete/<int:assign_asset_id>/', views.assign_asset_delete, name='assign_asset_delete'),
    # Delete assign_asset
    path('stock_list/', views.stock_list, name='stock_list'),  # List stock,
    path('stock_insert', views.stock_add, name='stock_insert'),  # Add stock
    path('stock_update/<int:stock_id>/', views.stock_add, name='stock_update'),  # Update stock
    path('stock_delete/<int:stock_id>/', views.stock_delete, name='stock_delete'),  # Delete stock
    path('reports/', views.reports, name='reports'),  # Reports
    path('damage_report/', views.damage_report_pdf, name='damage_report'),  # Damage Reports
    path('stud_list/', views.stud_list, name='stud_list'),  # List stud,
    path('stud_insert', views.stud_add, name='stud_insert'),  # Add stud
    path('stud_update/<int:stud_id>/', views.stud_add, name='stud_update'),  # Update stud
    path('stud_delete/<int:stud_id>/', views.stud_delete, name='stud_delete'),  # Delete stud
    path('peo_list/', views.peo_list, name='peo_list'),  # List peo,
    path('peo_insert', views.peo_add, name='peo_insert'),  # Add peo
    path('peo_update/<int:peo_id>/', views.peo_add, name='peo_update'),  # Update peo
    path('peo_delete/<int:peo_id>/', views.peo_delete, name='peo_delete'),  # Delete peo
    path('damage_list/', views.damage_list, name='damage_list'),  # List damage,
    path('damage_insert', views.damage_add, name='damage_insert'),  # Add damage
    path('damage_update/<int:damage_id>/', views.damage_add, name='damage_update'),  # Update damage
    path('damage_delete/<int:damage_id>/', views.damage_delete, name='damage_delete'),  # Delete damage
    path('damagereport_list/', views.damagereport_list, name='damagereport_list'),  # List damagereport,
    path('damagereport_insert', views.damagereport_add, name='damagereport_insert'),  # Add damagereport
    path('damagereport_update/<int:damagereport_id>/', views.damagereport_add, name='damagereport_update'),
    # Update damagereport
    path('locationmaster_list/', views.locationmaster_list, name='locationmaster_list'),  # List locationmaster,
    path('locationmaster_insert', views.locationmaster_add, name='locationmaster_insert'),  # Add locationmaster
    path('locationmaster_update/<int:locationmaster_id>/', views.locationmaster_add, name='locationmaster_update'),
    # Update locationmaster
    path('locationmaster_delete/<int:locationmaster_id>/', views.locationmaster_delete, name='locationmaster_delete'),
    # Delete locationmaster
    path('emp_list/', views.emp_list, name='emp_list'),  # List employee,
    path('emp_insert', views.emp_add, name='emp_insert'),  # Add employee
    path('emp_update/<int:emp_id>/', views.emp_add, name='emp_update'),  # Update employee
    path('emp_delete/<int:emp_id>/', views.emp_delete, name='emp_delete'),  # Delete employee
    path('unit_list/', views.unit_list, name='unit_list'),  # List unit,
    path('unit_insert', views.unit_add, name='unit_insert'),  # Add unit
    path('unit_update/<int:unit_id>/', views.unit_add, name='unit_update'),  # Update unit
    path('unit_delete/<int:unit_id>/', views.unit_delete, name='unit_delete'),  # Delete unit
    path('bay_list/', views.bay_list, name='bay_list'),  # List bay,
    path('bay_insert', views.bay_add, name='bay_insert'),  # Add bay
    path('bay_update/<int:bay_id>/', views.bay_add, name='bay_update'),  # Update bay
    path('bay_delete/<int:bay_id>/', views.bay_delete, name='bay_delete'),  # Delete bay
    path('status_list/', views.status_list, name='status_list'),  # List status,
    path('status_insert', views.status_add, name='status_insert'),  # Add status
    path('status_update/<int:status_id>/', views.status_add, name='status_update'),  # Update status
    path('status_delete/<int:status_id>/', views.status_delete, name='status_delete'),  # Delete status
    path('customertype_list/', views.customertype_list, name='customertype_list'),  # List customertype
    path('customertype_insert', views.customertype_add, name='customertype_insert'),  # Add customertype
    path('customertype_update/<int:customertype_id>/', views.customertype_add, name='customertype_update'),
    # Update customertype
    path('customertype_delete/<int:customertype_id>/', views.customertype_delete, name='customertype_delete'),
    # Delete customertype
    path('whratemaster_list/', views.whratemaster_list, name='whratemaster_list'),  # List whratemaster,
    path('whratemaster_insert', views.whratemaster_add, name='whratemaster_insert'),  # Add whratemaster
    path('whratemaster_update/<int:whratemaster_id>/', views.whratemaster_add, name='whratemaster_update'),
    # Update whratemaster
    path('whratemaster_delete/<int:whratemaster_id>/', views.whratemaster_delete, name='whratemaster_delete'),
    # Delete whratemaster
    path('designation_list/', views.designation_list, name='designation_list'),  # List designation,
    path('designation_insert', views.designation_add, name='designation_insert'),  # Add designation
    path('designation_update/<int:designation_id>/', views.designation_add, name='designation_update'),
    # Update designation
    path('designation_delete/<int:designation_id>/', views.designation_delete, name='designation_delete'),
    # Delete designation
    path('whstoragetype_list/', views.whstoragetype_list, name='whstoragetype_list'),  # List whstoragetype,
    path('whstoragetype_insert', views.whstoragetype_add, name='whstoragetype_insert'),  # Add whstoragetype
    path('whstoragetype_update/<int:whstoragetype_id>/', views.whstoragetype_add, name='whstoragetype_update'),
    # Update whstoragetype
    path('whstoragetype_delete/<int:whstoragetype_id>/', views.whstoragetype_delete, name='whstoragetype_delete'),
    # Delete whstoragetype
    path('role_list/', views.role_list, name='role_list'),  # List role,
    path('role_insert', views.role_add, name='role_insert'),  # Add role
    path('role_update/<int:role_id>/', views.role_add, name='role_update'),  # Update role
    path('role_delete/<int:role_id>/', views.role_delete, name='role_delete'),  # Delete role
    path('password_reset/', views.password_reset_request, name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name="password/password_reset_done.html"),
         name='password_reset_done'),  # Password Reset
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="password/password_reset_confirm.html"),
         name='password_reset_confirm'),  # Password Reset
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'),
         name='password_reset_complete'),  # Password Reset
    path('gatein_insert', views.gatein_add, name='gatein_insert'),  # gatein add
    path('gatein_list/', views.gatein_list, name='gatein_list'),  # List gatein,
    path('gatein_update/<int:gatein_id>/', views.gatein_add, name='gatein_update'),  # Update gatein
    path('gatein_delete/<int:gatein_id>/', views.gatein_delete, name='gatein_delete'),  # Delete gatein
    path('gatein_pre_insert', views.gatein_pre_add, name='gatein_pre_insert'),  # gatein Pre add
    path('gatein_pre_list/', views.gatein_pre_list, name='gatein_pre_list'),  # List gatein pre,
    path('gatein_pre_update/<int:gatein_pre_id>/', views.gatein_pre_add, name='gatein_pre_update'),  # Update gatein pre
    path('gatein_pre_delete/<int:gatein_pre_id>/', views.gatein_pre_delete, name='gatein_pre_delete'),
    # Delete gatein pre
    path('loadingbay_update/<int:loadingbay_id>/', views.loadingbay_add, name='loadingbay_update'),  # loadingbay update
    path('loadingbay_insert', views.loadingbay_add, name='loadingbay_insert'),  # loadingbay insert
    path('load_currency_value/', views.load_currency_value, name='load_currency_value'),
    # Load currency coversion value
    path('wh_job_insert', views.wh_job_add, name='wh_job_insert'),  # wh Job insert
    path('wh_job_update/<int:gatein_id>/', views.wh_job_add, name='wh_job_update'),  # wh_job update
    path('wh_job_list', views.wh_job_list, name='wh_job_list'),  # wh Job list
    path('wh_job_delete/<int:gatein_id>/', views.wh_job_delete, name='wh_job_delete'),  # wh Job list
    path('enquirynote_list/', views.enquirynote_list, name='enquirynote_list'),  # List enquirynote,
    path('enquirynote_insert', views.enquirynote_add, name='enquirynote_insert'),  # Add enquirynote
    path('enquirynote_update/<int:enquirynote_id>/', views.enquirynote_add, name='enquirynote_update'),  # Update enquirynote
    path('enquirynote_delete/<int:enquirynote_id>/', views.enquirynote_delete, name='enquirynote_delete'),  # Delete enquirynote
    path('consignmentdetail_enquiry/<int:enquiry_id>/<str:consignment_number>/', views.consignmentdetail_enquiry, name='consignmentdetail_enquiry'),  # List consignmentdetail,
    path('consignmentdetail_list/', views.consignmentdetail_list, name='consignmentdetail_list'),  # List consignmentdetail,
    path('consignmentdetail_list_ajax/', views.consignmentdetail_list_ajax, name='consignmentdetail_list_ajax'),  # AJAX data for consignmentdetail
    path('consignmentdetail_insert', views.consignmentdetail_add, name='consignmentdetail_insert'),  # Add consignmentdetail
    path('consignmentdetail_update/<int:consignmentdetail_id>/', views.consignmentdetail_add, name='consignmentdetail_update'),  # Update consignmentdetail
    path('consignmentdetail_nav/<int:consignmentdetail_id>/', views.consignmentdetail_nav, name='consignmentdetail_nav'),  # Update consignmentdetail
    path('consignment_note_connect/<int:enquirynote_id>/', views.consignment_note_connect, name='consignment_note_connect'),  # Connect consignmentdetail
    path('consignmentdetail_delete/<int:consignmentdetail_id>/', views.consignmentdetail_delete, name='consignmentdetail_delete'),  # Delete consignmentdetail
    path('consignmentdetail_delete/<int:consignmentdetail_id>/', views.consignmentdetail_delete, name='consignmentdetail_delete'),  # Delete consignmentdetail
    path('customername_list/', views.customername_list, name='customername_list'),  # List customername,
    path('customername_insert', views.customername_add, name='customername_insert'),  # Add customername
    path('customername_update/<int:customername_id>/', views.customername_add, name='customername_update'),  # Update customername
    path('customername_delete/<int:customername_id>/', views.customername_delete, name='customername_delete'),  # Delete customername
    path('vehiclecategory_list/', views.vehiclecategory_list, name='vehiclecategory_list'),  # List vehiclecategory,
    path('vehiclecategory_insert', views.vehiclecategory_add, name='vehiclecategory_insert'),  # Add vehiclecategory
    path('vehiclecategory_update/<int:vehiclecategory_id>/', views.vehiclecategory_add, name='vehiclecategory_update'),  # Update vehiclecategory
    path('vehiclecategory_delete/<int:vehiclecategory_id>/', views.vehiclecategory_delete, name='vehiclecategory_delete'),  # Delete vehiclecategory
    path('customerdepartment_list/', views.customerdepartment_list, name='customerdepartment_list'),  # List customerdepartment,
    path('customerdepartment_insert', views.customerdepartment_add, name='customerdepartment_insert'),  # Add customerdepartment
    path('customerdepartment_update/<int:customerdepartment_id>/', views.customerdepartment_add, name='customerdepartment_update'),  # Update customerdepartment
    path('customerdepartment_delete/<int:customerdepartment_id>/', views.customerdepartment_delete, name='customerdepartment_delete'),  # Delete customerdepartment
    path('vehicletype_list/', views.vehicletype_list, name='vehicletype_list'),  # List vehicletype,
    path('vehicletype_insert', views.vehicletype_add, name='vehicletype_insert'),  # Add vehicletype
    path('vehicletype_update/<int:vehicletype_id>/', views.vehicletype_add, name='vehicletype_update'),  # Update vehicletype
    path('vehicletype_delete/<int:vehicletype_id>/', views.vehicletype_delete, name='vehicletype_delete'),  # Delete vehicletype
    path('tripdetail_enquiry/<int:enquiry_id>/<str:trip_num>/', views.tripdetail_enquiry, name='tripdetail_enquiry'),  # tripdetail_enquiry,
    path('tripdetail_list/', views.tripdetail_list, name='tripdetail_list'),  # List tripdetail,
    path('tripdetail_list_ajax/', views.tripdetail_list_ajax, name='tripdetail_list_ajax'),  # AJAX data for tripdetail
    path('tripdetail_insert', views.tripdetail_add, name='tripdetail_insert'),  # Add tripdetail
    path('tripdetail_update/<int:tripdetail_id>/', views.tripdetail_add, name='tripdetail_update'),  # Update tripdetail
    path('tripdetail_nav/<int:tripdetail_id>/', views.tripdetail_nav, name='tripdetail_nav'),  # Navigate tripdetail
    path('tripdetail_delete/<int:tripdetail_id>/', views.tripdetail_delete, name='tripdetail_delete'),  # Delete tripdetail
    path('trip_email/', views.trip_email, name='trip_email'),
    path('get_trip_email_recipients/', views.get_trip_email_recipients, name='get_trip_email_recipients'),
    path('movementtype_list/', views.movementtype_list, name='movementtype_list'),  # List movementtype,
    path('movementtype_insert', views.movementtype_add, name='movementtype_insert'),  # Add movementtype
    path('movementtype_update/<int:movementtype_id>/', views.movementtype_add, name='movementtype_update'),  # Update movementtype
    path('movementtype_delete/<int:movementtype_id>/', views.movementtype_delete, name='movementtype_delete'),  # Delete movementtype
    path('trbusinesstype_list/', views.trbusinesstype_list, name='trbusinesstype_list'),  # List trbusinesstype,
    path('trbusinesstype_insert', views.trbusinesstype_add, name='trbusinesstype_insert'),  # Add trbusinesstype
    path('trbusinesstype_update/<int:trbusinesstype_id>/', views.trbusinesstype_add, name='trbusinesstype_update'),  # Update trbusinesstype
    path('trbusinesstype_delete/<int:trbusinesstype_id>/', views.trbusinesstype_delete, name='trbusinesstype_delete'),  # Delete trbusinesstype
    path('tripclosure_list/', views.tripclosure_list, name='tripclosure_list'),  # List tripclosure,
    path('tripclosure_list_ajax/', views.tripclosure_list_ajax, name='tripclosure_list_ajax'),  # AJAX data for tripclosure
    path('tripclosure_insert', views.tripclosure_add, name='tripclosure_insert'),  # Add tripclosure
    path('tripclosure_update/<int:tripclosure_id>/', views.tripclosure_add, name='tripclosure_update'),  # Update tripclosure
    path('tripclosure_nav/<int:tripclosure_id>/', views.tripclosure_nav, name='tripclosure_nav'),  # Nav tripclosure
    path('tripclosure_enquiry/<int:enquiry_id>/<str:trip_num>/', views.tripclosure_enquiry, name='tripclosure_enquiry'),# tripclosure_enquiry,
    path('tripclosure_delete/<int:tripclosure_id>/', views.tripclosure_delete, name='tripclosure_delete'),  # Delete tripclosure
    path('vhmanufacturer_list/', views.vhmanufacturer_list, name='vhmanufacturer_list'),  # List vhmanufacturer,
    path('vhmanufacturer_insert', views.vhmanufacturer_add, name='vhmanufacturer_insert'),  # Add vhmanufacturer
    path('vhmanufacturer_update/<int:vhmanufacturer_id>/', views.vhmanufacturer_add, name='vhmanufacturer_update'),  # Update vhmanufacturer
    path('vhmanufacturer_delete/<int:vhmanufacturer_id>/', views.vhmanufacturer_delete, name='vhmanufacturer_delete'),  # Delete vhmanufacturer
    path('vehiclemodel_list/', views.vehiclemodel_list, name='vehiclemodel_list'),  # List vehiclemodel,
    path('vehiclemodel_insert', views.vehiclemodel_add, name='vehiclemodel_insert'),  # Add vehiclemodel
    path('vehiclemodel_update/<int:vehiclemodel_id>/', views.vehiclemodel_add, name='vehiclemodel_update'),  # Update vehiclemodel
    path('vehiclemodel_delete/<int:vehiclemodel_id>/', views.vehiclemodel_delete, name='vehiclemodel_delete'),  # Delete vehiclemodel
    path('ownership_list/', views.ownership_list, name='ownership_list'),  # List ownership,
    path('ownership_insert', views.ownership_add, name='ownership_insert'),  # Add ownership
    path('ownership_update/<int:ownership_id>/', views.ownership_add, name='ownership_update'),  # Update ownership
    path('ownership_delete/<int:ownership_id>/', views.ownership_delete, name='ownership_delete'),  # Delete ownership
    path('body_list/', views.body_list, name='body_list'),  # List body,
    path('body_insert', views.body_add, name='body_insert'),  # Add body
    path('body_update/<int:body_id>/', views.body_add, name='body_update'),  # Update body
    path('body_delete/<int:body_id>/', views.body_delete, name='body_delete'),  # Delete body
    path('axletype_list/', views.axletype_list, name='axletype_list'),  # List axletype,
    path('axletype_insert', views.axletype_add, name='axletype_insert'),  # Add axletype
    path('axletype_update/<int:axletype_id>/', views.axletype_add, name='axletype_update'),  # Update axletype
    path('axletype_delete/<int:axletype_id>/', views.axletype_delete, name='axletype_delete'),  # Delete axletype
    path('fueltype_list/', views.fueltype_list, name='fueltype_list'),  # List fueltype,
    path('fueltype_insert', views.fueltype_add, name='fueltype_insert'),  # Add fueltype
    path('fueltype_update/<int:fueltype_id>/', views.fueltype_add, name='fueltype_update'),  # Update fueltype
    path('fueltype_delete/<int:fueltype_id>/', views.fueltype_delete, name='fueltype_delete'),  # Delete fueltype
    path('vehiclecolour_list/', views.vehiclecolour_list, name='vehiclecolour_list'),  # List vehiclecolour,
    path('vehiclecolour_insert', views.vehiclecolour_add, name='vehiclecolour_insert'),  # Add vehiclecolour
    path('vehiclecolour_update/<int:vehiclecolour_id>/', views.vehiclecolour_add, name='vehiclecolour_update'),  # Update vehiclecolour
    path('vehiclecolour_delete/<int:vehiclecolour_id>/', views.vehiclecolour_delete, name='vehiclecolour_delete'),  # Delete vehiclecolour
    path('permittype_list/', views.permittype_list, name='permittype_list'),  # List permittype,
    path('permittype_insert', views.permittype_add, name='permittype_insert'),  # Add permittype
    path('permittype_update/<int:permittype_id>/', views.permittype_add, name='permittype_update'),  # Update permittype
    path('permittype_delete/<int:permittype_id>/', views.permittype_delete, name='permittype_delete'),  # Delete permittype
    path('vehiclemaster_list/', views.vehiclemaster_list, name='vehiclemaster_list'),  # List vehiclemaster,
    path('vehiclemaster_insert', views.vehiclemaster_add, name='vehiclemaster_insert'),  # Add vehiclemaster
    path('vehiclemaster_update/<int:vehiclemaster_id>/', views.vehiclemaster_add, name='vehiclemaster_update'),
    # Update vehiclemaster
    path('vehiclemaster_delete/<int:vehiclemaster_id>/', views.vehiclemaster_delete, name='vehiclemaster_delete'),
    # Delete vehiclemaster
    path('rtratemaster_list/', views.rtratemaster_list, name='rtratemaster_list'),  # List rtratemaster,
    path('rtratemaster_insert', views.rtratemaster_add, name='rtratemaster_insert'),  # Add rtratemaster
    path('rtratemaster_update/<int:rtratemaster_id>/', views.rtratemaster_add, name='rtratemaster_update'),
    # Update rtratemaster
    path('rtratemaster_delete/<int:rtratemaster_id>/', views.rtratemaster_delete, name='rtratemaster_delete'),
    # Delete rtratemaster
    path('gstexcepmtion_list/', views.gstexcepmtion_list, name='gstexcepmtion_list'),  # List gstexcepmtion,
    path('gstexcepmtion_insert', views.gstexcepmtion_add, name='gstexcepmtion_insert'),  # Add gstexcepmtion
    path('gstexcepmtion_update/<int:gstexcepmtion_id>/', views.gstexcepmtion_add, name='gstexcepmtion_update'),
    # Update gstexcepmtion
    path('gstexcepmtion_delete/<int:gstexcepmtion_id>/', views.gstexcepmtion_delete, name='gstexcepmtion_delete'),
    # Delete gstexcepmtion
    path('gstmodel_list/', views.gstmodel_list, name='gstmodel_list'),  # List gstmodel,
    path('gstmodel_insert', views.gstmodel_add, name='gstmodel_insert'),  # Add gstmodel
    path('gstmodel_update/<int:gstmodel_id>/', views.gstmodel_add, name='gstmodel_update'),  # Update gstmodel
    path('gstmodel_delete/<int:gstmodel_id>/', views.gstmodel_delete, name='gstmodel_delete'),  # Delete gstmodel
    path('paymenttype_list/', views.paymenttype_list, name='paymenttype_list'),  # List paymenttype,
    path('paymenttype_insert', views.paymenttype_add, name='paymenttype_insert'),  # Add paymenttype
    path('paymenttype_update/<int:paymenttype_id>/', views.paymenttype_add, name='paymenttype_update'),
    # Update paymenttype
    path('paymenttype_delete/<int:paymenttype_id>/', views.paymenttype_delete, name='paymenttype_delete'),
    # Delete paymenttype
    path('crcountfrom_list/', views.crcountfrom_list, name='crcountfrom_list'),  # List crcountfrom,
    path('crcountfrom_insert', views.crcountfrom_add, name='crcountfrom_insert'),  # Add crcountfrom
    path('crcountfrom_update/<int:crcountfrom_id>/', views.crcountfrom_add, name='crcountfrom_update'),
    # Update crcountfrom
    path('crcountfrom_delete/<int:crcountfrom_id>/', views.crcountfrom_delete, name='crcountfrom_delete'),
    # Delete crcountfrom
    path('customer_list/', views.customer_list, name='customer_list'),  # List customer,
    path('customer_insert', views.customer_add, name='customer_insert'),  # Add customer
    path('customer_update/<int:customer_id>/', views.customer_add, name='customer_update'),  # Update customer
    path('customer_delete/<int:customer_id>/', views.customer_delete, name='customer_delete'),  # Delete customer
    path('damagereport_update/<int:damagereport_id>/', views.damagereport_add, name='damagereport_update'),
    # damagereport update
    path('damagereport_insert', views.damagereport_add, name='damagereport_insert'),  # damagereport insert
    path('materialhandling_list/', views.materialhandling_list, name='materialhandling_list'),
    # List Material Handling,
    path('materialhandling_insert', views.materialhandling_add, name='materialhandling_insert'),
    # Add Material Handling
    path('materialhandling_update/<int:material_id>/', views.materialhandling_add, name='materialhandling_update'),
    # Update Material Handling
    path('materialhandling_delete/<int:material_id>/', views.materialhandling_delete, name='materialhandling_delete'),
    # Delete Material Handling
    path('packagetype_list/', views.packagetype_list, name='packagetype_list'),  # List packagetype ,
    path('packagetype_insert', views.packagetype_add, name='packagetype_insert'),  # Add packagetype
    path('packagetype_update/<int:packagetype_id>/', views.packagetype_add, name='packagetype_update'),
    # Update packagetype
    path('packagetype_delete/<int:packagetype_id>/', views.packagetype_delete, name='packagetype_delete'),
    # Delete packagetype
    path('currencytype_list/', views.currencytype_list, name='currencytype_list'),  # List currencytype ,
    path('currencytype_insert', views.currencytype_add, name='currencytype_insert'),  # Add currencytype
    path('currencytype_update/<int:currencytype_id>/', views.currencytype_add, name='currencytype_update'),
    # Update currencytype
    path('currencytype_delete/<int:currencytype_id>/', views.currencytype_delete, name='currencytype_delete'),
    # Delete currencytype
    path('stocktype_list/', views.stocktype_list, name='stocktype_list'),  # List stocktype ,
    path('stocktype_insert', views.stocktype_add, name='stocktype_insert'),  # Add stocktype
    path('stocktype_update/<int:stocktype_id>/', views.stocktype_add, name='stocktype_update'),  # Update stocktype
    path('stocktype_delete/<int:stocktype_id>/', views.stocktype_delete, name='stocktype_delete'),
    # Delete currencytype
    path('load_units/', views.load_units, name='load_units'),
    path('load_units_origin/', views.load_units_origin, name='load_units_origin'),
    path('load_bays/', views.load_bays, name='load_bays'),
    path('load_bays_origin/', views.load_bays_origin, name='load_bays_origin'),
    path('warehousein_insert', views.warehousein_add, name='warehousein_insert'),  # Add warehousein
    path('warehousein_update/<int:warehousein_id>/', views.warehousein_add, name='warehousein_update'),
    # Update warehousein
    path('warehouseout_update/<int:warehouseout_id>/', views.warehouseout_add, name='warehouseout_update'),
    # Update warehouseout
    path('warehouseout_cancel/', views.warehouseout_cancel, name='warehouseout_cancel'),  # Cancel warehouseout
    path('storage_list/', views.storage_list, name='storage_list'),  # List Storage
    path('load_customer_model/', views.load_customer_model, name='load_customer_model'),
    path('dispatch_list/', views.dispatch_list, name='dispatch_list'),  # List currencytype ,
    path('dispatch_insert', views.dispatch_add, name='dispatch_insert'),  # Add dispatch
    path('dispatch_update/<int:dispatch_id>/', views.dispatch_add, name='dispatch_update'),  # Update dispatch
    path('dispatch_delete/<int:dispatch_id>/', views.dispatch_delete, name='dispatch_delete'),  # Delete dispatch
    # path('dispatch_goods_list/<int:dispatch_id>/', views.dispatch_goods_list, name='dispatch_goods_list'),# Dispatch Goods List
    path('dispatch_goods_list/', views.dispatch_goods_list, name='dispatch_goods_list'),  # Dispatch Goods List
    path('dispatch_remove_goods/', views.dispatch_remove_goods, name='dispatch_remove_goods'),  # Remove Dispatch Goods
    path('dispatch_add_goods/', views.dispatch_add_goods, name='dispatch_add_goods'),  # Add Dispatch Goods
    path('dispatch_goods_back/', views.dispatch_goods_back, name='dispatch_goods_back'),  # back Dispatch Goods
    path('qr_dispatch_decoder/<int:dispatch_id>', views.qr_dispatch_decoder, name='qr_dispatch_decoder'),
    # qr_dispatch_decoder
    path('message_test/', views.message_test, name='message_test'),
    path('load_area_volume/', views.load_area_volume, name='load_area_volume'),
    # path("get_available_pre_gateins/", views.get_available_pre_gateins, name="get_available_pre_gateins"),
    path('load_pre_gate_in/', views.load_pre_gate_in, name='load_pre_gate_in'),
    path('load_pre_gate_in_truck_details/', views.load_pre_gate_in_truck_details,
         name='load_pre_gate_in_truck_details'),
    path('invoice_list/', views.invoice_list, name='invoice_list'),  # List invoice
    path('invoice_report/', views.invoice_report, name='invoice_report'),  # List invoice report
    path('invoice_insert/', views.invoice_add, name='invoice_insert'),  # Add invoice
    path('invoice_update/<int:invoice_id>', views.invoice_add, name='invoice_update'),  # update invoice
    path('invoice_delete/<int:invoice_id>', views.invoice_delete, name='invoice_delete'),  # delete invoice
    path('warehouse_reports/', views.warehouse_reports, name='warehouse_reports'),
    path('transport_reports/', views.transport_reports, name='transport_reports'),
    path('space_utilization_reports/', views.space_utilization_reports, name='space_utilization_reports'),
    path('space_availability_reports/', views.space_availability_reports, name='space_availability_reports'),
    path('stock_value_report/', views.stock_value_reports, name='stock_value_report'),
    path('damage_report_list/', views.damage_reports_list, name='damage_report_list'),
    path('deviation_report/', views.deviation_report, name='deviation_report'),
    path('shipperinvoice_list/<int:voucher_id>', views.shipper_invoice_list, name='shipperinvoice_list'),
    # List invoice
    path('shipper_invoice_goods_add/', views.shipper_invoice_goods_add, name='shipper_invoice_goods_add'),
    # add shipper invoice to voucher list
    path('shipper_invoice_goods_remove/', views.shipper_invoice_goods_remove, name='shipper_invoice_goods_remove'),
    # remove shipper invoice to voucher list
    path('load_whrate_model/', views.load_whrate_model, name='load_whrate_model'),  # load WH rate
    path('expense_list/', views.expense_list, name='expense_list'),  # List expense
    path('expense_insert/', views.expense_add, name='expense_insert'),  # Add expense
    path('expense_update/<int:expense_id>', views.expense_add, name='expense_update'),  # update expense
    path('expense_delete/<int:expense_id>', views.expense_delete, name='expense_delete'),  # delete expense
    path('expense_search/', views.expense_search, name='expense_search'),  # search expense
    path('case_to_case_open_invoice/', views.case_to_case_invoice_list_open, name='case_to_case_open_invoice'),
    # case to case Open invoice list
    path('exclusive_open_invoice/', views.exclusive_invoice_list_open, name='exclusive_open_invoice'),
    # exclusive Open invoice list
    path('dedicated_open_invoice/', views.dedicated_invoice_list_open, name='dedicated_open_invoice'),
    # dedicated Open invoice list
    path('sales_list/', views.sales_list, name='sales_list'),  # List sales
    path('sales_insert/', views.sales_add, name='sales_insert'),  # Add sales
    path('sales_update/<int:sales_id>', views.sales_add, name='sales_update'),  # update sales
    path('sales_delete/<int:sales_id>', views.sales_delete, name='sales_delete'),  # delete sales
    path('sales_comments_list/', views.sales_comments_list, name='sales_comments_list'),  # List sales comments
    path('sales_comments_insert/', views.sales_comments_add, name='sales_comments_insert'),  # Add sales comments
    path('sales_comments_update/<int:sales_comments_id>', views.sales_comments_add, name='sales_comments_update'),
    # update sales comments
    path('sales_comments_delete/<int:sales_comments_id>', views.sales_comments_delete, name='sales_comments_delete'),
    # delete sales comments
    path('ininspectreport_list/', views.ininspectreport_list, name='ininspectreport_list'),  # List ininspectreport
    path('ininspectreport_insert/', views.ininspectreport_add, name='ininspectreport_insert'),  # Add ininspectreport
    path('ininspectreport_update/<int:ininspectreport_id>', views.ininspectreport_add, name='ininspectreport_update'),
    # update ininspectreport
    path('ininspectreport_delete/<int:ininspectreport_id>', views.ininspectreport_delete,
         name='ininspectreport_delete'),  # delete ininspectreport
    path('ouinspectreport_list/', views.ouinspectreport_list, name='ouinspectreport_list'),  # List ouinspectreport
    path('ouinspectreport_insert/', views.ouinspectreport_add, name='ouinspectreport_insert'),  # Add ouinspectreport
    path('ouinspectreport_update/<int:ouinspectreport_id>', views.ouinspectreport_add, name='ouinspectreport_update'),
    # update ouinspectreport
    path('ouinspectreport_delete/<int:ouinspectreport_id>', views.ouinspectreport_delete,
         name='ouinspectreport_delete'),  # delete ouinspectreport
    path('materialstock_list/', views.materialstock_list, name='materialstock_list'),  # List materialstock
    path('materialstock_insert/', views.materialstock_add, name='materialstock_insert'),  # Add materialstock
    path('materialstock_update/<int:materialstock_id>', views.materialstock_add, name='materialstock_update'),
    # update materialstock
    path('materialstock_delete/<int:materialstock_id>', views.materialstock_delete, name='materialstock_delete'),
    # delete materialstock
    path('packingjobs_list/', views.packingjobs_list, name='packingjobs_list'),  # List packingjobs
    path('packingjobs_insert/', views.packingjobs_add, name='packingjobs_insert'),  # Add packingjobs
    path('packingjobs_update/<int:packingjobs_id>', views.packingjobs_add, name='packingjobs_update'),
    # update packingjobs
    path('packingjobs_delete/<int:packingjobs_id>', views.packingjobs_delete, name='packingjobs_delete'),
    # delete packingjobs
    path('ar_list/', views.ar_list, name='ar_list'),  # List ar
    path('ar_insert/', views.ar_add, name='ar_insert'),  # Add ar
    path('ar_update/<int:ar_id>', views.ar_add, name='ar_update'),  # update ar
    path('ar_delete/<int:ar_id>', views.ar_delete, name='ar_delete'),  # delete ar
    path('sales_target_list/', views.sales_target_list, name='sales_target_list'),  # List sales
    path('sales_target_insert/', views.sales_target_add, name='sales_target_insert'),  # Add sale
    path('sales_target_update/<int:sales_target_id>', views.sales_target_add, name='sales_target_update'),
    # update sales
    path('sales_target_delete/<int:sales_target_id>', views.sales_target_delete, name='sales_target_delete'),
    # delete sales
    path('ar_comments_list/', views.arcomments_list, name='ar_comments_list'),  # List ar_comments
    path('ar_comments_insert/', views.arcomments_add, name='ar_comments_insert'),  # Add ar_comments
    path('ar_comments_update/<int:arcomments_id>', views.arcomments_add, name='ar_comments_update'),
    # update ar_comments
    path('ar_comments_delete/<int:arcomments_id>', views.arcomments_delete, name='ar_comments_delete'),
    # delete ar_comments
    path('open_requirements_list/', views.open_requirements_list, name='open_requirements_list'),
    # open List requirements
    path('requirements_list/', views.requirements_list, name='requirements_list'),  # List requirements
    path('requirements_insert/', views.requirements_add, name='requirements_insert'),  # Add requirements
    path('requirements_update/<int:requirements_id>', views.requirements_add, name='requirements_update'),
    # update requirements
    path('requirements_delete/<int:requirements_id>', views.requirements_delete, name='requirements_delete'),
    # delete requirements
    path('requirements_search/', views.requirements_search, name='requirements_search'),  # search requirements
    path('needassessment_list/', views.needassessment_list, name='needassessment_list'),  # List needassessment
    path('needassessment_insert/', views.needassessment_add, name='needassessment_insert'),  # Add needassessment
    path('needassessment_update/<int:needassessment_id>', views.needassessment_add, name='needassessment_update'),
    # update needassessment
    path('needassessment_delete/<int:needassessment_id>', views.needassessment_delete, name='needassessment_delete'),
    # delete needassessment
    path('openingstock_list/', views.openingstock_list, name='openingstock_list'),  # List openingstock
    path('openingstock_insert/', views.openingstock_add, name='openingstock_insert'),  # Add openingstock
    path('openingstock_update/<int:openingstock_id>', views.openingstock_add, name='openingstock_update'),
    # update openingstock
    path('openingstock_delete/<int:openingstock_id>', views.openingstock_delete, name='openingstock_delete'),
    # delete openingstock
    path('stockpurchases_list/', views.stockpurchases_list, name='stockpurchases_list'),  # List stockpurchases
    path('stockpurchases_cancel/', views.stockpurchases_cancel, name='stockpurchases_cancel'),  # Cancel stockpurchases
    path('stockpurchases_insert/', views.stockpurchases_add, name='stockpurchases_insert'),  # Add stockpurchases
    path('stockpurchases_update/<int:stockpurchases_id>', views.stockpurchases_add, name='stockpurchases_update'),
    # update stockpurchases
    path('stockpurchases_delete/<int:stockpurchases_id>', views.stockpurchases_delete, name='stockpurchases_delete'),
    # delete stockpurchases
    path('purchaseorder_list/', views.purchaseorder_list, name='purchaseorder_list'),  # List purchaseorder
    path('purchaseorder_insert/', views.purchaseorder_add, name='purchaseorder_insert'),  # Add purchaseorder
    path('purchaseorder_update/<int:purchaseorder_id>', views.purchaseorder_add, name='purchaseorder_update'),
    # update purchaseorder
    path('purchaseorder_delete/<int:purchaseorder_id>', views.purchaseorder_delete, name='purchaseorder_delete'),
    # delete purchaseorder
    path('na_dimension_list/', views.na_dimension_list, name='na_dimension_list'),  # List Na Dimension
    path('na_dimension_insert/', views.na_dimension_add, name='na_dimension_insert'),  # Add Na Dimension
    path('na_dimension_update/<int:na_dimension_id>', views.na_dimension_add, name='na_dimension_update'),
    # update Na Dimension
    path('na_dimension_delete/<int:na_dimension_id>', views.na_dimension_delete, name='na_dimension_delete'),
    # delete Na Dimension
    path('na_dimension_cancel', views.na_dimension_cancel, name='na_dimension_cancel'),  # cancel Na Dimension
    path('quotes_list/', views.quotes_list, name='quotes_list'),  # List quotes
    path('quotes_insert/', views.quotes_add, name='quotes_insert'),  # Add quotes
    path('quotes_update/<int:quotes_id>', views.quotes_add, name='quotes_update'),  # update quotes
    path('quotes_delete/<int:quotes_id>', views.quotes_delete, name='quotes_delete'),  # delete quotes
    path('export_costingreport/', views.export_cost_assessment_to_excel, name='export_costingreport'),
    # export stock value report
    path('costing_list/', views.costing_list, name='costing_list'),  # List costing
    path('costing_insert/', views.costing_add, name='costing_insert'),  # Add costing
    path('costing_update/<int:costing_id>', views.costing_add, name='costing_update'),  # update costing
    path('costing_delete/<int:costing_id>', views.costing_delete, name='costing_delete'),  # delete costing
    path('costing_cancel/', views.costing_cancel, name='costing_cancel'),  # cancel costing
    path('pk_item_search_page/', views.pk_item_search_page, name='pk_item_search_page'),  # pk_item_search_page
    path('pk_item_search_page_costing/', views.pk_item_search_page_costing, name='pk_item_search_page_costing'),
    # pk_item_search_page_costing
    path('costingsummary_list/', views.costingsummary_list, name='costingsummary_list'),  # List costingsummary
    path('get_partcode_summary/', views.get_partcode_summary, name='get_partcode_summary'),
    path('costingsummary_insert/', views.costingsummary_add, name='costingsummary_insert'),  # Add costingsummary
    path('costingsummary_update/<int:costingsummary_id>', views.costingsummary_add, name='costingsummary_update'),
    # update costingsummary
    path('costingsummary_delete/<int:costingsummary_id>', views.costingsummary_delete, name='costingsummary_delete'),
    # delete costingsummary
    path('pk_costing_summary_check_unique_field/', views.pk_costing_summary_check_unique_field,
         name='pk_costing_summary_check_unique_field'),  # costing_summary_check_unique_field
    path('pk_costing_get_customer/', views.pk_costing_get_customer, name='pk_costing_get_customer'),
    # costing_summary_check_unique_field
    path('vehicle_allotment_list/', views.vehicle_allotment_list, name='vehicle_allotment_list'),
    path('vehicle_allotment_insert/<int:enquiry_id>/', views.vehicle_allotment_add, name='vehicle_allotment_insert'),
    path('vehicle_allotment_update/<int:vehicle_allotment_id>/', views.vehicle_allotment_add,
         name='vehicle_allotment_update'),
    path('vehicle_allotment_update_enquiry/<int:enquiry_id>/<str:vehicle_number>/', views.vehicle_allotment_enquiry,
         name='vehicle_allotment_update_enquiry'),
    path('vehicle_allotment_delete/<int:vehicle_allotment_id>/', views.vehicle_allotment_delete,
         name='vehicle_allotment_delete'),
    path('vehicle_allotment_nav/<int:vehicle_allotment_id>/', views.vehicle_allotment_nav,
         name='vehicle_allotment_nav'),
    path('search/', views.get_queryset, name='search'),  # View Gate-in search
    path('pre_gatein_search/', views.pre_gatein_search, name='pre_gatein_search'),  # View pre Gate-in search
    path('partcode_search/', views.partcode_search, name='partcode_search'),  # View pre Gate-in search
    path('sales_search/', views.sales_search, name='sales_search'),  # View pre Sales search
    path('sales_comments_search/', views.sales_comments_search, name='sales_comments_search'),
    # View pre Sales comments search
    path('dispatch_search/', views.dispatch_search, name='dispatch_search'),  # View dispatch search
    path('load_stock_description/', views.load_stock_description, name='load_stock_description'),
    path('load_pk_wood_description/', views.load_pk_wood_description, name='load_pk_wood_description'),
    # Load stock description
    path('load_vehicle_source/', views.load_vehicle_source, name='load_vehicle_source'),  # Load vehicle_source
    path('load_vehicle_number/', views.load_vehicle_number, name='load_vehicle_number'),  # Load vehicle_details
    path('load_driver_details/', views.load_driver_details, name='load_driver_details'),  # Load driver_details
    path('load_vehicle_details/', views.load_vehicle_details, name='load_vehicle_details'),  # Load vehicle_details
    path('fuelfilling_list/', views.fuelfilling_list, name='fuelfilling_list'),  # List fuelfilling
    path('fuelfilling_insert/', views.fuelfilling_add, name='fuelfilling_insert'),  # Add fuelfilling
    path('fuelfilling_update/<int:fuelfilling_id>', views.fuelfilling_add, name='fuelfilling_update'),
    # update fuelfilling
    path('fuelfilling_delete/<int:fuelfilling_id>', views.fuelfilling_delete, name='fuelfilling_delete'),
    # delete fuelfilling
    path('bunkname_list/', views.bunkname_list, name='bunkname_list'),  # List bunkname
    path('bunkname_insert/', views.bunkname_add, name='bunkname_insert'),  # Add bunkname
    path('bunkname_update/<int:bunkname_id>', views.bunkname_add, name='bunkname_update'),  # update bunkname
    path('bunkname_delete/<int:bunkname_id>', views.bunkname_delete, name='bunkname_delete'),  # delete bunkname
    path('places_list/', views.places_list, name='places_list'),  # List places
    path('places_insert/', views.places_add, name='places_insert'),  # Add places
    path('places_update/<int:places_id>', views.places_add, name='places_update'),  # update places
    path('places_delete/<int:places_id>', views.places_delete, name='places_delete'),  # delete places
    path('enquirynotevehicle_list/', views.enquirynotevehicle_list, name='enquirynotevehicle_list'),
    # List enquirynotevehicle
    path('enquirynotevehicle_insert/', views.enquirynotevehicle_add, name='enquirynotevehicle_insert'),
    # Add enquirynotevehicle
    path('enquirynotevehicle_update/<int:enquirynotevehicle_id>', views.enquirynotevehicle_add,
         name='enquirynotevehicle_update'),  # update enquirynotevehicle
    path('enquirynotevehicle_delete/<int:enquirynotevehicle_id>', views.enquirynotevehicle_delete,
         name='enquirynotevehicle_delete'),  # delete enquirynotevehicle
    path('enquirynotevehicle_cancel/', views.enquirynotevehicle_cancel, name='enquirynotevehicle_cancel'),
    # Cancel enquirynotevehicle
    path('consignmentgoods_list/', views.consignmentgoods_list, name='consignmentgoods_list'),  # List consignmentgoods
    path('consignmentgoods_insert/', views.consignmentgoods_add, name='consignmentgoods_insert'),
    # Add consignmentgoods
    path('consignmentgoods_update/<int:consignmentgoods_id>', views.consignmentgoods_add,
         name='consignmentgoods_update'),  # update consignmentgoods
    path('consignmentgoods_delete/<int:consignmentgoods_id>', views.consignmentgoods_delete,
         name='consignmentgoods_delete'),  # delete consignmentgoods
    path('consignmentgoods_nav/<int:consignmentdetails_id>', views.consignmentgoods_nav, name='consignmentgoods_nav'),
    # nav consignmentgoods
    # path('transport_nav/', views.transport_nav, name='transport_nav'),  # nav transport
    path('transport_nav/', TemplateView.as_view(template_name='asset_mgt_app/transport_nav.html'),
         name='transport_nav'),
    path('consignmentgoods_cancel/', views.consignmentgoods_cancel, name='consignmentgoods_cancel'),
    # Cancel consignmentgoods
    path('consignmentgoods_back/', views.consignmentgoods_back, name='consignmentgoods_back'),
    # Cancel consignmentgoods
    path('load_location/', views.load_location, name='load_location'),
    path('export_stockreport/', views.export_stockreport_to_csv, name='export_stockreport'),
    # export stock value report
    path('dispatch_stock_list/', views.dispatch_stock_list, name='dispatch_stock_list'),  # dispatch_stock_list
    path('wh_e_way_bill_list/', views.wh_e_way_bill_list, name='wh_e_way_bill_list'),  # wh_e_way_bill_list
    path('edit_wh_e_way_bill_list/<int:wh_job_id>', views.edit_wh_e_way_bill_list, name='edit_wh_e_way_bill_list'),
    # edit_wh_e_way_bill_list
    path('pregateintruck_list/', views.pregateintruck_list, name='pregateintruck_list'),  # List pregateintruck
    path('pregateintruck_insert/', views.pregateintruck_add, name='pregateintruck_insert'),  # Add pregateintruck
    path('pregateintruck_update/<int:pregateintruck_id>', views.pregateintruck_add, name='pregateintruck_update'),
    # update pregateintruck
    path('pregateintruck_delete/<int:pregateintruck_id>', views.pregateintruck_delete, name='pregateintruck_delete'),
    # delete pregateintruck
    path('pregateintruck_cancel/', views.pregateintruck_cancel, name='pregateintruck_cancel'),  # cancel pregateintruck
    path('dispatch_gatepass_pdf/<int:dispatch_id>', views.dispatch_gatepass_pdf, name='dispatch_gatepass_pdf'),
    # dispatch_gatepass_pdf
    path('revenue_report/', views.revenue_report, name='revenue_report'),  # Revenue Report
    path('expense_report/', views.expense_report, name='expense_report'),  # Expense Report
    path('consignment_note_pdf/<int:consignment_note_id>/', views.consignment_note_pdf, name='consignment_note_pdf'),
    path('goods_in_out_reports_list/', views.goods_in_out_reports_list, name='goods_in_out_reports_list'),
    # List pregateintruck
    path('pk_stock_vendor_list/', views.pk_stock_vendor_list, name='pk_stock_vendor_list'),  # List pk_stock_vendor
    path('pk_stock_vendor_insert/', views.pk_stock_vendor_add, name='pk_stock_vendor_insert'),  # Add pk_stock_vendor
    path('pk_stock_vendor_update/<int:stock_vendor_id>', views.pk_stock_vendor_add, name='pk_stock_vendor_update'),
    # update pk_stock_vendor
    path('pk_stock_vendor_delete/<int:stock_vendor_id>', views.pk_stock_vendor_delete, name='pk_stock_vendor_delete'),
    # delete pk_stock_vendor
    path('pk_quotation_list/', views.pk_quotation_list, name='pk_quotation_list'),  # List quotation
    path('pk_quotation_insert/', views.pk_quotation_add, name='pk_quotation_insert'),  # Add quotation
    path('pk_quotation_update/<int:quotation_id>', views.pk_quotation_add, name='pk_quotation_update'),
    # update quotation
    path('pk_quotation_delete/<int:quotation_id>', views.pk_quotation_delete, name='pk_quotation_delete'),
    # delete quotation
    path('pk_quotation_cancel/', views.pK_quotation_cancel, name='pk_quotation_cancel'),  # cancel quotation
    path('pk_quotationsummary_list/', views.pk_quotationsummary_list, name='pk_quotationsummary_list'),
    path('pk_quotationsummary_clone/<int:pk_quotationsummary_id>/', views.pk_quotationsummary_clone,
         name='pk_quotationsummary_clone'),
    path('pk_quotationsummary_insert/', views.pk_quotationsummary_add, name='pk_quotationsummary_insert'),
    # Add pk_quotationsummary
    path('pk_quotationsummary_update/<int:pk_quotationsummary_id>', views.pk_quotationsummary_add,
         name='pk_quotationsummary_update'),  # update pk_quotationsummary
    path('pk_quotationsummary_delete/<int:pk_quotationsummary_id>', views.pk_quotationsummary_delete,
         name='pk_quotationsummary_delete'),  # delete pk_quotationsummary
    path('pk_quotation_summary_check_unique_field/', views.pk_quotation_summary_check_unique_field,
         name='pk_quotation_summary_check_unique_field'),  # pk_quotation_summary_check_unique_field
    path('transport_calculate_trip_charges/', views.transport_calculate_trip_charges,
         name='transport_calculate_trip_charges'),  # transport_calculate_trip_charges
    path('iou_get_full_name/', views.get_full_name_iou, name='iou_get_full_name'),  # iou_get_full_name
    path('iou_list/', views.iou_list, name='iou_list'),  # List IOU
    path('iou_insert/', views.iou_add, name='iou_insert'),  # Add IOU
    path('iou_update/<int:iou_id>', views.iou_add, name='iou_update'),  # update IOU
    path('iou_delete/<int:iou_id>', views.iou_delete, name='iou_delete'),  # delete IOU
    path('pk_return_excess_to_stock/<int:costing_id>/', views.pk_return_excess_to_stock, name='pk_return_excess_to_stock'),
    path('modify_dimensions_view/', views.modify_dimensions_view, name='modify_dimensions_view'),
    # modify_dimensions_view
    path('pk_return_list/', views.pk_return_list, name='pk_return_list'),  # List retrival
    path('pk_retrival_list/', views.pk_retrival_list, name='pk_retrival_list'),  # List retrival
    path('pk_retrival_insert/', views.pk_retrival_add, name='pk_retrival_insert'),  # Add retrival
    path('pk_retrival_update/<int:retrival_id>', views.pk_retrival_add, name='pk_retrival_update'),  # update retrival
    path('pk_retrival_delete/<int:retrival_id>', views.pk_retrival_delete, name='pk_retrival_delete'),
    # delete retrival
    path('pk_retrival_cancel/', views.pK_retrival_cancel, name='pk_retrival_cancel'),  # cancel retrival
    path('pk_acceptance_list/', views.pk_acceptance_list, name='pk_acceptance_list'),  # List acceptance
    path('pk_acceptance_update/<int:retrival_id>', views.pk_acceptance_add, name='pk_acceptance_update'),
    # update acceptance
    path('comments_list/', views.comments_list, name='comments_list'),  # List comments
    path('comments_insert/', views.comments_add, name='comments_insert'),  # Add comments
    path('comments_update/<int:comments_id>', views.comments_add, name='comments_update'),  # update comments
    path('comments_delete/<int:comments_id>', views.comments_delete, name='comments_delete'),  # delete comments
    path('comments_cancel/', views.comments_cancel, name='comments_cancel'),  # cancel comments
    path('pk_get_item_description/', views.pk_get_item_description, name='pk_get_item_description'),
    # get item_description
    path('pk_get_customer/', views.pk_get_customer, name='pk_get_customer'),  # pk_get_customer
    path('pk_get_po_requirement_type/', views.pk_get_po_requirement_type, name='pk_get_po_requirement_type'),
    # pk_get_po_requirement_type
    path('pk_get_pk_requirement_type/', views.pk_get_pk_requirement_type, name='pk_get_pk_requirement_type'),
    # pk_get_pk_requirement_type
    path('pk_bvm_quotation_pdf/', views.pk_bvm_quotation_pdf, name='bvm_quotation_pdf'),  # bvm_quotation_pdf
    path('pk_bvm_invoice_pdf/', views.pk_bvm_invoice_pdf, name='pk_bvm_invoice_pdf'),  # pk_bvm_invoice_pdf
    path('pk_bvm_invoice_excel/', views.pk_bvm_invoice_excel, name='pk_bvm_invoice_excel'),  # pk_bvm_invoice_excel
    path('pk_store_po_dimension_id/', views.pk_store_po_dimension_id, name='pk_store_po_dimension_id'),
    # pk_store_po_dimension_id
    path('pk_store_na_dimension_id/', views.pk_store_na_dimension_id, name='pk_store_na_dimension_id'),
    # pk_store_na_dimension_id
    path('fetch_part_code_details/', views.fetch_part_code_details, name='fetch_part_code_details'),
    path('po_dimension_list/', views.po_dimension_list, name='po_dimension_list'),  # List po_dimension
    path('po_dimension_insert/', views.po_dimension_add, name='po_dimension_insert'),  # Add po_dimension
    path('po_dimension_update/<int:po_dimension_id>', views.po_dimension_add, name='po_dimension_update'),
    # update po_dimension
    path('po_dimension_delete/<int:po_dimension_id>', views.po_dimension_delete, name='po_dimension_delete'),
    # delete po_dimension
    path('po_dimension_cancel/', views.po_dimension_cancel, name='po_dimension_cancel'),  # cancel po_dimension
    path('bar_chart_data/', views.bar_chart_data, name='bar_chart_data'),
    path('bar_chart/', views.bar_chart, name='bar_chart'),
    path('get_requirement_description/', views.get_requirement_description, name='get_requirement_description'),
    # List task
    path('task_list/', views.task_list, name='task_list'),  # List task
    path('task_insert/', views.task_add, name='task_insert'),  # Add task
    path('task_update/<int:task_id>', views.task_add, name='task_update'),  # update task
    path('task_delete/<int:task_id>', views.task_delete, name='task_delete'),  # delete task
    path('timesheet_list/', views.timesheet_list, name='timesheet_list'),  # List timesheet
    path('timesheet_insert/', views.timesheet_add, name='timesheet_insert'),  # Add timesheet
    path('timesheet_update/<int:timesheet_id>', views.timesheet_add, name='timesheet_update'),  # update timesheet
    path('timesheet_delete/<int:timesheet_id>', views.timesheet_delete, name='timesheet_delete'),  # delete timesheet
    path('timesheet_nav/<int:task_id>', views.timesheet_nav, name='timesheet_nav'),  # delete timesheet
    path('ml_product_add', views.create_product, name='ml_product_add'),  # multi select
    path('ml_product_edit/<int:product_id>', views.create_product, name='ml_product_edit'),  # multi select
    path('ml_product_list', views.ml_product_list, name='ml_product_list'),  # multi select
    path('ml_product_delete/<int:product_id>', views.ml_product_delete, name='ml_product_delete'),  # multi select
    path('business_revenue_list/', views.business_revenue_list, name='business_revenue_list'),  # List business_revenue
    path('business_revenue_insert/', views.business_revenue_add, name='business_revenue_insert'),
    # Add business_revenue
    path('business_revenue_update/<int:business_id>', views.business_revenue_add, name='business_revenue_update'),
    # update business_revenue
    path('business_revenue_delete/<int:business_id>', views.business_revenue_delete, name='business_revenue_delete'),
    # delete business_revenue
    path('warehouse_send_email/', views.warehouse_send_email_view, name='warehouse_send_email'),  # send emails
    path('picture/', views.picture_add, name='picture_add'),
    path('picture_list/', views.picture_list, name='picture_list'),
    path('picture_update/<int:picture_id>/', views.picture_add, name='picture_add'),
    path('picture_delete/<int:picture_id>/', views.picture_delete, name='picture_delete'),
    path('packing_gate/', views.gate_return_add, name='packing_gate'),
    path('packing_gate_list/', views.gate_return_list, name='packing_gate_list'),
    path('packing_gate_update/<int:gate_id>/', views.gate_return_add, name='packing_gate_update'),
    path('packing_gate_delete/<int:gate_id>/', views.gate_return_delete, name='packing_gate_delete'),
    path('packing_gate_pdf/<int:gate_id>', views.gate_return_pdf, name='packing_gate_pdf'),
    path('customer_attachment_add/', views.customer_attach_add, name='customer_attachment_add'),
    path('customer_attachment_list/', views.customer_attach_list, name='customer_attachment_list'),
    path('customer_attachment_update/<int:attach_id>/', views.customer_attach_add, name='customer_attachment_update'),
    path('customer_attachment_delete/<int:attach_id>/', views.customer_attach_delete,
         name='customer_attachment_delete'),
    path('customer_attachment_cancel/', views.customer_attach_cancel, name='customer_attachment_cancel'),
    path('customer_contract_rate_dues_list/', views.customer_contract_rate_dues_list,
         name='customer_contract_rate_dues_list'),
    path('customer_contract_rate_due_days/', views.customer_contract_rate_due_days,
         name='customer_contract_rate_due_days'),
    path('packing_delivery/', views.delivery_challan_add, name='packing_delivery'),
    path('packing_delivery_list/', views.delivery_challan_list, name='packing_delivery_list'),
    path('packing_delivery_update/<int:delivery_id>/', views.delivery_challan_add, name='packing_delivery_update'),
    path('packing_delivery_delete/<int:delivery_id>/', views.delivery_challan_delete, name='packing_delivery_delete'),
    path('packing_delivery_pdf/<int:delivery_id>', views.delivery_challan_pdf, name='packing_delivery_pdf'),
    path('budget_form/', views.budgetform_add, name='budget_form'),
    path('budget_form_list/', views.budgetform_list, name='budget_form_list'),
    path('budget_form_update/<int:budget_id>/', views.budgetform_add, name='budget_form_update'),
    path('budget_form_delete/<int:budget_id>/', views.budgetform_delete, name='budget_form_delete'),
    path('budget_form_clone/<int:budget_id>/', views.budgetform_clone, name='budget_form_clone'),
    path('expense_ext_add/', views.expense_ext_add, name='expense_ext_add'),
    path('expense_ext_list/', views.expense_ext_list, name='expense_ext_list'),
    path('expense_ext_update/<int:expense_ext_id>/', views.expense_ext_add, name='expense_ext_update'),
    path('expense_ext_delete/<int:expense_ext_id>/', views.expense_ext_delete, name='expense_ext_delete'),
    path('expense_ext_cancel/', views.expense_ext_cancel, name='expense_ext_cancel'),
    path('gate_return_employee_id/', views.gate_return_employee_id, name='gate_return_employee_id'),
    path('costing_excess_insert/', views.pk_excess_stock_add, name='costing_excess_insert'),  # Add costing
    path('costing_excess_update/<int:costing_id>', views.pk_excess_stock_add, name='costing_excess_update'),
    path('pk_excess_stock_list/', views.pk_excess_stock_list, name='pk_excess_stock_list'),  # Ensure this name matches
    path('high_value_add/', views.highvalue_add, name='high_value_add'),
    path('high_value_list/', views.highvalue_list, name='high_value_list'),
    path('high_value_update/<int:high_value_id>/', views.highvalue_add, name='high_value_update'),
    path('high_value_delete/<int:high_value_id>/', views.highvalue_delete, name='high_value_delete'),
    path('high_value_cancel/', views.highvalue_cancel, name='high_value_cancel'),
    path('dsr_reports/', views.dsr_reports, name='dsr_reports'),
    path('dsr_send_email/', views.dsr_send_email_view, name='dsr_send_email'),
    path('gate_out_send_email/', views.gate_out_email, name='gate_out_send_email'),
    path('profit_loss_report/', views.profit_loss_report, name='profit_loss_report'),
    path('gate_in_send_email/', views.gate_in_email, name='gate_in_send_email'),
    path('dispatch_gatepass_pdf_download/<int:dispatch_id>', views.dispatch_gatepass_pdf_download,
         name='dispatch_gatepass_pdf_download'),
    path('sales_reports/', views.sales_reports, name='sales_reports'),
    path('sales_call_report/', views.sales_call_report, name='sales_call_report'),
    path('salesperson_chart/', views.salesperson_chart, name='salesperson_chart'),
    path('monthly_summary/', views.monthly_summary, name='monthly_summary'),
    path('salesperson_productivity_performance/', views.salesperson_productivity_performance,
         name='salesperson_productivity_performance'),
    path('salescalls_details/', views.salescalls_details, name='salescalls_details'),
    path('target_actuals/', views.targets_actuals, name='targets_actuals'),
    path('warehouse_jobs_add/', views.warehouse_jobs_add, name='warehouse_jobs_add'),
    path('salesperson_wise_chart/', views.salesperson_wise_chart, name='salesperson_wise_chart'),
    path('business_won_chart/', views.businesswon_chart, name='businesswon_chart'),
    path('business_won_chart/', views.businesswon_chart, name='businesswon_chart'),
    path('branch_profit_loss/', views.branch_profit_loss, name='branch_profit_loss'),
    path('branch_unit_profit_loss/', views.branch_unit_profit_loss, name='branch_unit_profit_loss'),
    path('finance_reports/', views.finance_reports, name='finance_reports'),
    path('businessmodel_PL/', views.businessmodel_PL, name='businessmodel_PL'),
    path('customerwise_PL/', views.customerwise_PL, name='customerwise_PL'),
    path('fin_profit_loss/', views.fin_profit_loss_view, name='fin_profit_loss_view'),
    path('expenses_report/', views.expenses_report, name='expenses_report'),
    path('ar_due_reports/', views.ar_due_reports, name='ar_due_reports'),
    path('budget_expense_report/', views.budget_expense, name='budget_expense'),
    path('budget_expense_mis/', views.budget_expense_mis, name='budget_expense_mis'),
    path('vehicle_availability/', views.vehicle_availability_list, name='vehicle_availability'),
    path('get_customer_details/', views.get_customer_details, name='get_customer_details'),
    path('vehicle_procurement_add/', views.vehicle_procurement_add, name='vehicle_procurement_add'),
    path('vehicle_procurement_list/', views.vehicle_procurement_list, name='vehicle_procurement_list'),
    path('vehicle_procurement_update/<int:vp_id>/', views.vehicle_procurement_add, name='vehicle_procurement_update'),
    path('vehicle_procurement_delete/<int:vp_id>/', views.vehicle_procurement_delete,
         name='vehicle_procurement_delete'),
    path('stock_value_send_email_view/', views.stock_value_send_email_view, name='stock_value_send_email_view'),
    path('gate_meeting_add/', views.gatemeeting_add, name='gate_meeting_add'),
    path('gate_meeting_list/', views.gatemeeting_list, name='gate_meeting_list'),
    path('gate_meeting_update/<int:gate_meet_id>/', views.gatemeeting_add, name='gate_meeting_update'),
    path('gate_meeting_delete/<int:gate_meet_id>/', views.gatemeeting_delete, name='gate_meeting_delete'),
    path('gate_meeting_send_email/', views.gate_meeting_send_email, name='gate_meeting_send_email'),
    path('ops_audit_score_add/', views.opsauditscorecard_add, name='ops_audit_score_add'),
    path('ops_audit_score_list/', views.opsauditscorecard_list, name='ops_audit_score_list'),
    path('ops_audit_score_update/<int:ops_audit_id>/', views.opsauditscorecard_add, name='ops_audit_score_update'),
    path('ops_audit_score_delete/<int:ops_audit_id>/', views.opsauditscorecard_delete, name='ops_audit_score_delete'),
    path('send_ops_audit_email/', views.send_ops_audit_email, name='send_ops_audit_email'),
    path('wh_damage_report/', views.wh_damage_report, name='wh_damage_report'),
    path('wh_stock_report/', views.wh_stock_report, name='wh_stock_report'),
    path('wh_space_availability_report/', views.wh_space_availability_report, name='wh_space_availability_report'),
    path('wh_space_utilization_report/', views.wh_space_utilization_report, name='wh_space_utilization_report'),
    path('performance_audit_add/', views.performanceaudit_add, name='performance_audit_add'),
    path('performance_audit_list/', views.performanceaudit_list, name='performance_audit_list'),
    path('performance_audit_update/<int:perform_audit_id>/', views.performanceaudit_add,
         name='performance_audit_update'),
    path('performance_audit_delete/<int:perform_audit_id>/', views.performanceaudit_delete,
         name='performance_audit_delete'),
    path('send_performance_audit_email/', views.send_performance_audit_email, name='send_performance_audit_email'),
    path('salesperson_wise_table/', views.salesperson_wise_table, name='salesperson_wise_table'),
    path('sales_multiple_item_add/', views.sales_multiple_item_add, name='sales_multiple_item_add'),
    path('sales_multiple_item_list/', views.sales_multiple_item_list, name='sales_multiple_item_list'),
    path('sales_multiple_item_update/<int:sales_multiple_id>/', views.sales_multiple_item_add,
         name='sales_multiple_item_update'),
    path('sales_multiple_item_delete/<int:sales_multiple_id>/', views.sales_multiple_item_delete,
         name='sales_multiple_item_delete'),
    path('sales_multiple_item_cancel/', views.sales_multiple_item_cancel, name='sales_multiple_item_cancel'),
    path('part_code_add/', views.part_code_add, name='part_code_add'),
    path('part_code_add/<int:pc_id>/', views.part_code_add, name='part_code_edit'),
    path('part_code_list/', views.part_code_list, name='part_code_list'),
    path('part_code_delete/<int:pc_id>/', views.part_code_delete, name='part_code_delete'),
    path('get_stock_descriptions/', views.get_stock_descriptions, name='get_stock_descriptions'),
    path('get_part_code/', views.get_part_code, name='get_part_code'),
    path('timesheet_report/', views.timesheet_report, name='timesheet_report'),
    path('vehicle_requested/', views.vehicle_requested, name='vehicle_requested'),
    path('vehicle_type_counts/', views.vehicle_type_counts, name='vehicle_type_counts'),
    path('vehicle_allotted/', views.vehicle_allotted, name='vehicle_allotted'),
    path('consignmentdetail_cancel/', views.consignmentdetail_cancel, name='consignmentdetail_cancel'),
    path('load_truck_details/', views.load_truck_details, name='load_truck_details'),
    path('timesheet_report/', views.timesheet_report, name='timesheet_report'),
    path('fin_mis/', views.fin_mis, name='fin_mis'),
    path('fin_mis_warehouse/', views.fin_mis_warehouse, name='fin_mis_warehouse'),
    path("trans_fastag/", views.fastag_enquiry_view, name="trans_fastag"),
    path("trans_fastag_export_excel/", views.trans_fastag_export_excel, name="trans_fastag_export_excel"),
    path('track_vehicle_position/', views.track_vehicle_position, name='track_vehicle_position'),
    path("get_vehicle_data/", views.get_vehicle_data, name="get_vehicle_data"),
    path('get_remaining_quantity/<int:enquiry_id>/<int:vehicle_type_id>/', views.get_remaining_quantity,
         name='get_remaining_quantity'),
    path('get_vehicle_type/<str:vehicle_id>/', views.get_vehicle_type, name='get_vehicle_type'),
    path('add-description/', views.add_description, name='add_description'),
    path('fleet_management_view/', views.fleet_management_view, name='fleet_management_view'),
    path('vendorratemaster_list/', views.vendorratemaster_list, name='vendorratemaster_list'),
    path('vendorratemaster_insert', views.vendorratemaster_add, name='vendorratemaster_insert'),
    path('vendorratemaster_update/<int:vendorratemaster_id>/', views.vendorratemaster_add,
         name='vendorratemaster_update'),
    path('vendorratemaster_delete/<int:vendorratemaster_id>/', views.vendorratemaster_delete,
         name='vendorratemaster_delete'),
    path('get_vendor_buy_rate/', views.get_vendor_buy_rate, name='get_vendor_buy_rate'),
    path('get_vendor_sale_rate/', views.get_vendor_sale_rate, name='get_vendor_sale_rate'),
    path('consignment_pdf_download/', views.consignment_pdf_download, name='consignment_pdf_download'),
    path('location_master_add/', views.location_master_add, name='location_master_add'),
    path('location_master_edit/<int:loc_id>/', views.location_master_add, name='location_master_edit'),
    path('location_master_delete/<int:loc_id>/', views.location_master_delete, name='location_master_delete'),
    path('location_master_list/', views.location_master_list, name='location_master_list'),
    path('fetch_bunk_details/', views.fetch_bunk_details, name='fetch_bunk_details'),
    path('trip_approval_view/', views.trip_approval_view, name='trip_approval_view'),
    path('trip-approval/update/<int:trip_id>/', views.update_trip_approval, name='update_trip_approval'),
    path('add_consigner/', views.add_consigner, name='add_consigner'),
    path('add_consignee/', views.add_consignee, name='add_consignee'),
    path('partial_dispatch/', views.dispatch_partial_goods, name='dispatch_partial_goods'),
    path('need-assessment/print/<int:assessment_id>/', views.need_assessment_print_pdf, name='need_assessment_print'),
    path('trip_highvalue_add/', views.trip_highvalue_add, name='trip_highvalue_add'),
    path('trip_highvalue_list/', views.trip_highvalue_list, name='trip_highvalue_list'),
    path('trip_highvalue_update/<int:high_value_id>/', views.trip_highvalue_add, name='trip_highvalue_update'),
    path('trip_highvalue_delete/<int:high_value_id>/', views.trip_highvalue_delete, name='trip_highvalue_delete'),
    path('trip_highvalue_cancel/', views.trip_highvalue_cancel, name='trip_highvalue_cancel'),
    path('get_sim_tracking_data/', views.get_sim_tracking_data, name='get_sim_tracking_data'),
    path('backfill-preview/', views.backfill_preview, name='backfill_preview'),
    path('backfill-one/', views.backfill_one_record, name='backfill_one_record'),
    path('backfill-all/', views.backfill_all_records, name='backfill_all_records'),
    path('backfill_weight/', views.backfill_goods_weight, name='backfill_goods_weight'),
    path('get_fastag_toll_cost_ajax/', views.get_fastag_toll_cost_ajax, name='get_fastag_toll_cost_ajax'),
    path('vendor_filter/', views.vendor_filter, name='vendor_filter'),
    path('consignmentgoods/<int:pk>/upload/<str:att_type>/', views.consignmentgoods_upload_attachment,
         name='consignmentgoods_upload_attachment'),
    path('consignmentgoods/delete-attachment/<int:pk>/<str:att_type>/', views.consignmentgoods_delete_attachment,
         name='consignmentgoods_delete_attachment'),
    path('incident_add/', views.incident_add, name='incident_add'),
    path('incident_list/', views.incident_list, name='incident_list'),
    path('incident_update/<int:incident_id>/', views.incident_add, name='incident_update'),
    path('incident_delete/<int:incident_id>/', views.incident_delete, name='incident_delete'),
    path('customer_claims_add/', views.customer_claims_add, name='customer_claims_add'),
    path('customer_claims_list/', views.customer_claims_list, name='customer_claims_list'),
    path('customer_claims_update/<int:claim_id>/', views.customer_claims_add, name='customer_claims_update'),
    path('customer_claims_delete/<int:claim_id>/', views.customer_claims_delete, name='customer_claims_delete'),
    path('customer_claims_report/', views.customer_claims_report, name='customer_claims_report'),
    path('trans_customer_claims_add/', views.trans_customer_claims_add, name='trans_customer_claims_add'),
    path('trans_customer_claims_list/', views.trans_customer_claims_list, name='trans_customer_claims_list'),
    path('trans_customer_claims_update/<int:claim_id>/', views.trans_customer_claims_add, name='trans_customer_claims_update'),
    path('trans_customer_claims_delete/<int:claim_id>/', views.trans_customer_claims_delete, name='trans_customer_claims_delete'),
    path('fetch_trip_details_by_cnote/', views.fetch_trip_details_by_cnote, name='fetch_trip_details_by_cnote'),
    path('wrong_labelling_add/', views.wrong_labelling_add, name='wrong_labelling_add'),
    path('wrong_labelling_list/', views.wrong_labelling_list, name='wrong_labelling_list'),
    path('wrong_labelling_update/<int:wrong_labelling_id>/', views.wrong_labelling_add, name='wrong_labelling_update'),
    path('wrong_labelling_delete/<int:wrong_labelling_id>/', views.wrong_labelling_delete,
         name='wrong_labelling_delete'),
    path('add_transporter/', views.add_transporter, name='add_transporter'),
    path('pregatein_gatepass/<int:pregatein_id>/', views.pregatein_gatepass_pdf, name='pregatein_gatepass_pdf'),
    path('pregatein_gatepass_pdf_download/<int:pregatein_id>/', views.pregatein_gatepass_pdf_download,
         name='pregatein_gatepass_pdf_download'),
    path('get_units/', views.get_units_for_user, name='get_units_for_user'),
    path("get_shippers/", views.get_shippers, name="get_shippers"),
    path("get_consignees/", views.get_consignees, name="get_consignees"),
    path('gatein/<int:gatein_id>/pdf/', views.gatein_pdf_download, name='gatein_pdf_download'),
    path("highvalue/approval/", views.highvalue_approval_view, name="highvalue_approval_view"),
    path("highvalue/approval/update/<int:highvalue_id>/", views.update_highvalue_approval,
         name="update_highvalue_approval"),
    path("highvalue/approval2/", views.highvalue_approval2_view, name="highvalue_approval2_view"),
    path("highvalue/approval2/update/<int:highvalue_id>/", views.update_highvalue_approval2,
         name="update_highvalue_approval2"),
    path("gatein/upload/<int:pk>/", views.gatein_upload_attachment, name="gatein_upload_attachment"),
    path('gatein/<int:pk>/upload/<str:att_type>/', views.gatein_upload_attachment, name='gatein_upload_attachment'),
    path('gatein/<int:pk>/delete/<str:att_type>/', views.gatein_delete_attachment, name='gatein_delete_attachment'),
    path("dg_cargo_add/", views.dg_cargo_add, name="dg_cargo_add"),
    path("dg_cargo_add/<int:cargo_id>/", views.dg_cargo_add, name="dg_cargo_add"),
    path('dg_cargo_list/', views.dg_cargo_list, name='dg_cargo_list'),
    path('dg_cargo_report_list/', views.dg_cargo_report_list, name='dg_cargo_report_list'),
    path('dg_cargo_delete/<int:cargo_id>/', views.dg_cargo_delete, name='dg_cargo_delete'),
    path("dg_cargo/approval/", views.dg_cargo_approval_view, name="dg_cargo_approval_view"),
    path("dg_cargo/approval/update/<int:cargo_id>/", views.update_dg_cargo_approval, name="update_dg_cargo_approval"),
    path('overdue_jobs_report/', views.overdue_jobs_report, name='overdue_jobs_report'),
    path('incident_report/', views.incident_report, name='incident_report'),
    path('wrong_labelling_report/', views.wrong_labelling_report, name='wrong_labelling_report'),
    path('customer_claims_report/', views.customer_claims_report, name='customer_claims_report'),
    path('highvalue_report_list/', views.highvalue_report_list, name='highvalue_report_list'),
    path('warehouse_dashboard/', views.warehouse_dashboard, name='warehouse_dashboard'),
    path('customer_contract_rate_report/', views.customer_contract_rate_report, name='customer_contract_rate_report'),
    path("get-customer-pan-gst/", views.get_customer_pan_gst, name="get_customer_pan_gst"),
    path('vehicle_allotment_email/', views.vehicle_allotment_email, name='vehicle_allotment_email'),
    path('trip_report/', views.trip_report, name='trip_report'),
    path('trip_send_email/', views.trip_send_email, name='trip_send_email'),
    path('incident_send_email/', views.incident_send_email, name='incident_send_email'),
    path('truck_send_email_view', views.truck_send_email_view, name='truck_send_email_view'),
    path('driver_settlement_add/', views.driver_settlement_add, name='driver_settlement_add'),
    path('driver_settlement_update/<int:ds_id>/', views.driver_settlement_add, name='driver_settlement_update'),
    path('driver_settlement_list/', views.driver_settlement_list, name='driver_settlement_list'),
    path('driver_settlement_delete/<int:ds_id>/', views.driver_settlement_delete, name='driver_settlement_delete'),
    # path('driver_get_full_name/', views.get_full_name_driver, name='driver_get_full_name'),
    path('get_trip_totalcost/', views.get_trip_totalcost, name='get_trip_totalcost'),
    path('get_customer_ref/', views.get_customer_ref, name='get_customer_ref'),
    path('fetch_enquiry_locations/', views.fetch_enquiry_locations, name='fetch_enquiry_locations'),
    path('trip_settlement_view/', views.trip_settlement_view, name='trip_settlement_view'),
    path('trip_settlement/edit/<int:trip_id>/', views.trip_settlement_edit, name='trip_settlement_edit'),
    path("trip_finance_approval_view/", views.trip_finance_approval_view, name="trip_finance_approval_view"),
    path("trip_finance_approval/update/<int:trip_id>/", views.update_trip_finance_approval,
         name="update_trip_finance_approval"),
    path('halting_charges/<int:halting_id>/', views.halting_charges_add, name='halting_charges'),
    path('halting_charges_add/', views.halting_charges_add, name='halting_charges_add'),
    path('halting_list/', views.halting_list, name='halting_list'),
    path('halting_delete/<int:halting_id>/', views.halting_delete, name='halting_delete'),
    path('halting_charges_edit/<int:halting_id>/', views.halting_charges_add, name='halting_charges_edit'),
    path("email_master_add/", views.email_master_add, name="email_master_add"),  # Add new
    path("email_master/<int:record_id>/", views.email_master_add, name="email_master_edit"),  # Edit existing
    path("email_master_list/", views.email_master_list, name="email_master_list"),  # List page
    path("email_delete/<int:record_id>/", views.email_delete, name="email_delete"),  # Delete record
    path('get_halting_charge/', views.get_halting_charge, name='get_halting_charge'),
    path('get_route_rate/', views.get_vendor_buy_rate, name='get_route_rate'),
    path('driver_expense_add/', views.driver_expense_add, name='driver_expense_add'),
    path('driver_expense_list/', views.driver_expense_list, name='driver_expense_list'),
    path('driver_expense_add/<int:expense_id>/', views.driver_expense_add, name='driver_expense_add'),
    path('driver_expense_delete/<int:expense_id>/', views.driver_expense_delete, name='driver_expense_delete'),
    # path('driver-expense-by-driver/', views.driver_expense_by_driver,name='driver_expense_by_driver'),
    # path('get-driver-name-by-staff-id/', views.get_driver_name_by_staff_id, name='get_driver_name_by_staff_id'),
    # path('get-driver-details/', views.get_driver_details, name='get_driver_details' ),
    path('get-vendor-by-vehicle/', views.get_vendor_by_vehicle, name='get_vendor_by_vehicle'),
    path('driver_add/', views.driver_add, name='driver_add'),
    path('driver_edit/<int:driver_id>/', views.driver_add, name='driver_edit'),
    path('driver_list/', views.driver_list, name='driver_list'),
    path('driver_delete/<int:driver_id>/', views.driver_delete, name='driver_delete'),
    path('ajax/get-driver-details/', views.get_driver_details_from_master, name='get_driver_details_from_master'),
    path('get-dmr-email-details/', views.get_dmr_email_details, name='get_dmr_email_details'),
    path('ajax/get-employee-driver/', views.get_employee_driver_details, name='get_employee_driver_details'),
    path('ajax/get-trip-charges/', views.get_trip_charges, name='get_trip_charges'),
    path('driver-autocomplete/', views.driver_autocomplete, name='driver_autocomplete'),
    path("get_last_reported_km/", views.get_last_reported_km, name="get_last_reported_km"),
    path('trans_invoice_add/', views.trans_invoice_add, name='trans_invoice_add'),
    path('trans_invoice_edit/<int:invoice_id>/', views.trans_invoice_edit, name='trans_invoice_edit'),
    path('trans_invoice_list/', views.trans_invoice_list, name='trans_invoice_list'),
    path('trans_invoice_list_woh/<int:customer_id>/', views.trans_invoice_list_woh, name='trans_invoice_list_woh'),
    path('trans_invoice_delete/<int:invoice_id>/', views.trans_invoice_delete, name='trans_invoice_delete'),
    path('fetch_customer_details/', views.fetch_customer_details, name='fetch_customer_details'),
    path('trans_invoice_remove_woh/', views.trans_invoice_remove_woh, name='trans_invoice_remove_woh'),
    path('trans_invoice_add_woh/', views.trans_invoice_add_woh, name='trans_invoice_add_woh'),
    path('maintenance_add/', views.maintenance_add, name='maintenance_add'),
    path('fetch_vehicle_details/', views.fetch_vehicle_details, name='fetch_vehicle_details'),
    path('fetch_filtered_vehicles/', views.fetch_filtered_vehicles, name='fetch_filtered_vehicles'),
    path('maintenance_edit/<int:id>/', views.maintenance_edit, name='maintenance_edit'),
    path('maintenance_delete/<int:id>/', views.maintenance_delete, name='maintenance_delete'),
    path('maintenance_list/', views.maintenance_list, name='maintenance_list'),
    path('shipper_invoice_export_excel/<int:invoice_id>/', views.shipper_invoice_export_excel,
         name='shipper_invoice_export_excel'),
    path('invoice_export_excel/<int:invoice_id>/', views.invoice_export_excel, name='invoice_export_excel'),

    # Customer Registration URLs
    path('customer_register/<int:business_id>/', views.customer_register, name='customer_register'),
    path('customer_registration_list/', views.customer_registration_list, name='customer_registration_list'),
    path('customer_registration_approve/<int:registration_id>/', views.customer_registration_approve,
         name='customer_registration_approve'),
    path('customer_registration_reject/<int:registration_id>/', views.customer_registration_reject,
         name='customer_registration_reject'),
    path('customer_login/<int:business_id>/', views.customer_login, name='customer_login'),

    # Customer Enquiry URLs
    path('SMS/customer_enquiry_add/', views.customer_enquiry_add, name='customer_enquiry_add'),
    path('SMS/customer_enquiry_edit/<int:enquiry_id>/', views.customer_enquiry_edit, name='customer_enquiry_edit'),
    path('SMS/customer_enquiry_list/', views.customer_enquiry_list, name='customer_enquiry_list'),
    path('SMS/customer_track_vehicle/', views.customer_track_vehicle, name='customer_track_vehicle'),
    path('ajax/search-customers/', views.ajax_search_customers, name='ajax_search_customers'),
    path('ajax/check-customer-code/', views.ajax_check_customer_code, name='ajax_check_customer_code'),
    path('ajax/get-customer-departments/', views.ajax_get_customer_departments, name='ajax_get_customer_departments'),
    path('ajax/get-vehicle-types/', views.ajax_get_vehicle_types, name='ajax_get_vehicle_types'),
    path('SMS/customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('SMS/customer_tracking/<int:trip_id>/', views.customer_shipment_tracking, name='customer_tracking'),
    path('SMS/download_pod/<int:trip_id>/', views.download_pod, name='download_pod'),
    path('SMS/download_dmr/<int:trip_id>/', views.download_dmr, name='download_dmr'),
    path('SMS/customer_documents/', views.customer_documents, name='customer_documents'),
    path('SMS/customer_profile/', views.customer_profile, name='customer_profile'),
    path('SMS/customer_support/', views.customer_support, name='customer_support'),
    path('ajax/filter-trips-by-date/', views.filter_trips_by_date, name='filter_trips_by_date'),
    path('insurance_renewal_report/', views.insurance_renewal_report_view, name='insurance_renewal_report'),
    path('diesel_vs_revenue_report/', views.diesel_vs_revenue_report_view, name='diesel_vs_revenue_report'),
    path('own_v_mkt_sales/', views.own_vs_market_sales_report_view, name='own_v_mkt_sales'),
    path('maintenance_report/', views.maintenance_report_view, name='maintenance_report'),
    path('stock_maintenance_list/', views.stock_maintenance_list, name='stock_maintenance_list'),
    path('stock_maintenance_insert/', views.stock_maintenance_add, name='stock_maintenance_add'),
    path('stock_maintenance_add_for_vendor/', views.stock_maintenance_add_for_vendor, name='stock_maintenance_add_for_vendor'),
    path('stock_maintenance_update/<int:pk>/', views.stock_maintenance_edit, name='stock_maintenance_edit'),
    path('get_part_details/', views.get_part_details, name='get_part_details'),
    path('stock_maintenance_delete/<int:pk>/', views.stock_maintenance_delete, name='stock_maintenance_delete'),
    path('stock_usage_breakdown/', views.stock_usage_breakdown, name='stock_usage_breakdown'),
    path('trans-invoice/excel/<path:invoice_no>/',views.trans_invoice_excel,name='trans_invoice_excel'),
    path('trans-invoice/tally-excel/<path:invoice_no>/', views.trans_invoice_tally_excel, name='trans_invoice_tally_excel'),
    path("maintenance/pdf/<int:id>/",views.maintenance_pdf,name="maintenance_pdf"),
    path('vehicle_log_report/', views.vehicle_log_report_view, name='vehicle_log_report'),
    path('trip_cancellation_report/', views.trip_cancellation_report_view, name='trip_cancellation_report'),
    path('ref_no_pending_report/', views.ref_no_pending_report_view, name='ref_no_pending_report'),
    path('vehicle_utilization_report/', views.vehicle_utilization_report_view, name='vehicle_utilization_report'),
    path('drivers_advance_report/', views.drivers_advance_report_view, name='drivers_advance_report'),
    path('invoice_pending_report/', views.invoice_pending_report_view, name='invoice_pending_report'),
    path('vendor_p_l_mkt_report/', views.vendor_p_l_mkt_report_view, name='vendor_p_l_mkt_report'),
    path('vendor_p_l_attached_report/', views.vendor_p_l_attached_report_view, name='vendor_p_l_attached_report'),
    path('whatsapp_delivery_status_report/', views.whatsapp_delivery_status_report_view,name='whatsapp_delivery_status_report'),
    path('daily_trip_count_report/', views.daily_trip_count_report_view, name='daily_trip_count_report'),
    path('own_vehicle_pl_report/', views.own_vehicle_pl_report_view, name='own_vehicle_pl_report'),
    path('claim_pending_report/', views.claim_pending_report_view, name='claim_pending_report'),
    path('enquiry_pending_report/', views.enquiry_pending_report_view, name='enquiry_pending_report'),
    path('halting_report/', views.halting_report_view, name='halting_report'),
    path("trip_send_loading_report_mail/", views.trip_send_loading_report_mail, name="trip_send_loading_report_mail"),
    path("trip_send_trip_started_mail/", views.trip_send_trip_started_mail, name="trip_send_trip_started_mail"),
    path("trip_send_unloading_report_mail/", views.trip_send_unloading_report_mail, name="trip_send_unloading_report_mail"),
    path("trip_send_trip_closed_mail/", views.trip_send_trip_closed_mail, name="trip_send_trip_closed_mail"),
    path("maintenance/manager-approval/", views.manager_approval_list, name="manager_approval_list"),
    path("maintenance/manager-approve/<int:id>/", views.manager_approve, name="manager_approve"),
    path("maintenance/finance-approval/", views.finance_approval_list, name="finance_approval_list"),
    path("maintenance/finance-approve/<int:id>/", views.finance_approve, name="finance_approve"),
    # Market Bill
    path('market_bill/', views.market_bill_add, name='market_bill_add'),
    path('market_bill/list/', views.market_bill_list, name='market_bill_list'),
    path('market_bill/<int:id>/edit/', views.market_bill_edit, name='market_bill_edit'),
    path('market_bill/<int:id>/delete/', views.market_bill_delete, name='market_bill_delete'),
    path('market_bill/<int:id>/upload/', views.market_bill_upload, name='market_bill_upload'),
    path('market_bill/<int:id>/mail_upload/<int:trip_id>/', views.market_mail_upload, name='market_mail_upload'),
    path('ajax/get_trips_by_vendor/', views.get_trips_by_vendor, name='get_trips_by_vendor'),
    path('maintenance_bill_add/', views.maintenance_bill_add, name='maintenance_bill_add'),
    path('maintenance_bill_list/', views.maintenance_bill_list, name='maintenance_bill_list'),
    path('maintenance_bill/<int:id>/edit/', views.maintenance_bill_edit, name='maintenance_bill_edit'),
    path('maintenance_bill/<int:id>/delete/', views.maintenance_bill_delete, name='maintenance_bill_delete'),
    path('attached_bill_list/', views.attached_bill_list, name='attached_bill_list'),
    path('attached_bill_add/', views.attached_bill_add, name='attached_bill_add'),
    path('attached_bill_edit/<int:id>/', views.attached_bill_edit, name='attached_bill_edit'),
    path('attached_bill_delete/<int:id>/', views.attached_bill_delete, name='attached_bill_delete'),
    path('attached_bill_upload/<int:id>/', views.attached_bill_upload, name='attached_bill_upload'),
    path('attached_bill_summary/<int:id>/', views.attached_bill_summary, name='attached_bill_summary'),
    path('get_attached_vehicle_details/', views.get_attached_vehicle_details, name='get_attached_vehicle_details'),
    path('get_vehicles_by_vendor/', views.get_vehicles_by_vendor, name='get_vehicles_by_vendor'),
    path('fetch_maintenance_bill_details/', views.fetch_maintenance_bill_details, name='fetch_maintenance_bill_details'),
    path('get_maintenance_records_by_vehicle/', views.get_maintenance_records_by_vehicle, name='get_maintenance_records_by_vehicle'),
    path('fuelfilling_export_excel/', views.fuelfilling_export_excel, name='fuelfilling_export_excel'),
]
