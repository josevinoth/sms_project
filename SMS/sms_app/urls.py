from django.urls import path
from . import views
from django.contrib.auth import views as auth_views #import this
urlpatterns = [
    path('print_pdf', views.print_pdf, name='print_pdf'),  # Print PDF
    path('asset_qr_id/<int:asset_qr_id>', views.qr_code_asset, name='asset_qr_id'),  # qr_code
    path('goods_qr_id/<int:goods_qr_id>', views.qr_code_goods, name='goods_qr_id'),  # goods qr_code
    path('registration_page', views.registration_page, name='registration_page'),  # Registration_page
    path('login_page', views.login_page,name='login_page'),#Login_page
    path('logout_page', views.logout_page,name='logout_page'),#Logout_page
    path('home_page', views.home_page,name='home_page'),#Home_page
    path('asset_insert', views.assetinfo_add,name='asset_insert'),#Add Asset
    path('asset_update/<int:asset_id>/', views.assetinfo_add,name='asset_update'),#Update asset
    path('asset_delete/<int:asset_id>/',views.asset_delete,name='asset_delete'), #Delete asset
    path('asset_list/',views.asset_list,name='asset_list'), #List Asset
    path('user_list/', views.user_list, name='user_list'), # List user,
    path('user_insert', views.user_add,name='user_insert'),#Add user
    path('user_update/<int:user_id>/', views.user_add, name='user_update'),  # Update User
    path('user_delete/<int:user_id>/', views.user_delete, name='user_delete'),  # Delete User
    path('vendor_list/', views.vendor_list, name='vendor_list'), # List vendor,
    path('vendor_insert', views.vendor_add,name='vendor_insert'),#Add vendor
    path('vendor_update/<int:vendor_id>/', views.vendor_add, name='vendor_update'),  # Update Vendor
    path('vendor_delete/<int:vendor_id>/', views.vendor_delete, name='vendor_delete'),  # Delete Vendor
    path('location_list/', views.location_list, name='location_list'),  # List location,
    path('location_insert', views.location_add, name='location_insert'),  # Add location
    path('location_update/<int:location_id>/', views.location_add, name='location_update'),  # Update location
    path('location_delete/<int:location_id>/', views.location_delete, name='location_delete'),  # Delete location
    path('department_list/', views.department_list, name='department_list'),  # List department,
    path('department_insert', views.department_add, name='department_insert'),  # Add department
    path('department_update/<int:department_id>/', views.department_add, name='department_update'),  # Update department
    path('department_delete/<int:department_id>/', views.department_delete, name='department_delete'),  # Delete department
    path('product_list/', views.product_list, name='product_list'),  # List product,
    path('product_insert', views.product_add, name='product_insert'),  # Add product
    path('product_update/<int:product_id>/', views.product_add, name='product_update'),  # Update product
    path('product_delete/<int:product_id>/', views.product_delete, name='product_delete'),  # Delete product
    path('producttype_list/', views.producttype_list, name='producttype_list'),  # List producttype,
    path('producttype_insert', views.producttype_add, name='producttype_insert'),  # Add producttype
    path('producttype_update/<int:producttype_id>/', views.producttype_add, name='producttype_update'),  # Update producttype
    path('producttype_delete/<int:producttype_id>/', views.producttype_delete, name='producttype_delete'),  # Delete producttype
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
    path('insurancetype_update/<int:insurancetype_id>/', views.insurancetype_add, name='insurancetype_update'),  # Update insurancetype
    path('insurancetype_delete/<int:insurancetype_id>/', views.insurancetype_delete, name='insurancetype_delete'),  # Delete insurancetype
    path('service_list/', views.service_list, name='service_list'),  # List service,
    path('service_insert', views.service_add, name='service_insert'),  # Add service
    path('service_update/<int:service_id>/', views.service_add, name='service_update'),  # Update service
    path('service_delete/<int:service_id>/', views.service_delete, name='service_delete'),  # Delete service
    path('goods_list/', views.goods_list, name='goods_list'),  # List goods,
    path('goods_insert', views.goods_add, name='goods_insert'),  # Add goods
    path('goods_update/<int:goods_id>/', views.goods_add, name='goods_update'),  # Update goods
    path('goods_delete/<int:goods_id>/', views.goods_delete, name='goods_delete'),  # Delete goods
    path('assign_asset_list/<int:user_id>/', views.assign_asset_list_new, name='assign_asset_list'),  # List assign_asset,
    path('assign_asset_insert', views.assign_asset_add, name='assign_asset_insert'),  # Add assign_asset
    path('assign_asset_update/<int:assign_asset_id>/', views.assign_asset_add, name='assign_asset_update'),  # Update assign_asset
    path('assign_asset_delete/<int:assign_asset_id>/', views.assign_asset_delete, name='assign_asset_delete'),  # Delete assign_asset
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
    path('damagereport_update/<int:damagereport_id>/', views.damagereport_add, name='damagereport_update'),  # Update damagereport
    path('locationmaster_list/', views.locationmaster_list, name='locationmaster_list'),  # List locationmaster,
    path('locationmaster_insert', views.locationmaster_add, name='locationmaster_insert'),  # Add locationmaster
    path('locationmaster_update/<int:locationmaster_id>/', views.locationmaster_add, name='locationmaster_update'),  # Update locationmaster
    path('locationmaster_delete/<int:locationmaster_id>/', views.locationmaster_delete, name='locationmaster_delete'),  # Delete locationmaster
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
    path('customertype_update/<int:customertype_id>/', views.customertype_add, name='customertype_update'),  # Update customertype
    path('customertype_delete/<int:customertype_id>/', views.customertype_delete, name='customertype_delete'),  # Delete customertype
    path('whratemaster_list/', views.whratemaster_list, name='whratemaster_list'),  # List whratemaster,
    path('whratemaster_insert', views.whratemaster_add, name='whratemaster_insert'),  # Add whratemaster
    path('whratemaster_update/<int:whratemaster_id>/', views.whratemaster_add, name='whratemaster_update'),  # Update whratemaster
    path('whratemaster_delete/<int:whratemaster_id>/', views.whratemaster_delete, name='whratemaster_delete'),  # Delete whratemaster
    path('designation_list/', views.designation_list, name='designation_list'),  # List designation,
    path('designation_insert', views.designation_add, name='designation_insert'),  # Add designation
    path('designation_update/<int:designation_id>/', views.designation_add, name='designation_update'),  # Update designation
    path('designation_delete/<int:designation_id>/', views.designation_delete, name='designation_delete'),  # Delete designation
    path('whstoragetype_list/', views.whstoragetype_list, name='whstoragetype_list'),  # List whstoragetype,
    path('whstoragetype_insert', views.whstoragetype_add, name='whstoragetype_insert'),  # Add whstoragetype
    path('whstoragetype_update/<int:whstoragetype_id>/', views.whstoragetype_add, name='whstoragetype_update'),  # Update whstoragetype
    path('whstoragetype_delete/<int:whstoragetype_id>/', views.whstoragetype_delete, name='whstoragetype_delete'),  # Delete whstoragetype
    path('role_list/', views.role_list, name='role_list'),  # List role,
    path('role_insert', views.role_add, name='role_insert'),  # Add role
    path('role_update/<int:role_id>/', views.role_add, name='role_update'),  # Update role
    path('role_delete/<int:role_id>/', views.role_delete, name='role_delete'),  # Delete role
    path('password_reset', views.password_reset_request, name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name="password/password_reset_done.html"), name='password_reset_done'),  # Password Reset
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password/password_reset_confirm.html"), name='password_reset_confirm'),# Password Reset
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password/password_reset_complete.html'), name='password_reset_complete'),# Password Reset
    path('gatein_insert', views.gatein_add, name='gatein_insert'),  # gatein add
    path('gatein_list/', views.gatein_list, name='gatein_list'),  # List gatein,
    path('gatein_update/<int:gatein_id>/', views.gatein_add, name='gatein_update'), # Update gatein
    path('gatein_delete/<int:gatein_id>/', views.gatein_delete, name='gatein_delete'), # Delete gatein
    path('gatein_pre_insert', views.gatein_pre_add, name='gatein_pre_insert'),  # gatein Pre add
    path('gatein_pre_list/', views.gatein_pre_list, name='gatein_pre_list'),  # List gatein pre,
    path('gatein_pre_update/<int:gatein_pre_id>/', views.gatein_pre_add, name='gatein_pre_update'),  # Update gatein pre
    path('gatein_pre_delete/<int:gatein_pre_id>/', views.gatein_pre_delete, name='gatein_pre_delete'),  # Delete gatein pre
    path('loadingbay_update/<int:loadingbay_id>/', views.loadingbay_add, name='loadingbay_update'),  # loadingbay update
    path('loadingbay_insert', views.loadingbay_add, name='loadingbay_insert'),  # loadingbay insert
    path('wh_job_insert', views.wh_job_add, name='wh_job_insert'),  # wh Job insert
    path('wh_job_update/<int:gatein_id>/', views.wh_job_add, name='wh_job_update'),  # wh_job update
    path('wh_job_list', views.wh_job_list, name='wh_job_list'),  # wh Job list
    path('wh_job_delete/<int:gatein_id>/', views.wh_job_delete, name='wh_job_delete'),  # wh Job list
    path('enquirynote_list/', views.enquirynote_list, name='enquirynote_list'),  # List enquirynote,
    path('enquirynote_insert', views.enquirynote_add, name='enquirynote_insert'),  # Add enquirynote
    path('enquirynote_update/<int:enquirynote_id>/', views.enquirynote_add, name='enquirynote_update'),  # Update enquirynote
    path('enquirynote_delete/<int:enquirynote_id>/', views.enquirynote_delete, name='enquirynote_delete'),  # Delete enquirynote
    path('consignmentdetail_list/', views.consignmentdetail_list, name='consignmentdetail_list'),  # List consignmentdetail,
    path('consignmentdetail_insert', views.consignmentdetail_add, name='consignmentdetail_insert'),  # Add consignmentdetail
    path('consignmentdetail_update/<int:consignmentdetail_id>/', views.consignmentdetail_add, name='consignmentdetail_update'),  # Update consignmentdetail
    path('consignmentdetail_delete/<int:consignmentdetail_id>/', views.consignmentdetail_delete, name='consignmentdetail_delete'),  # Delete consignmentdetail
    path('vehicledetail_list/', views.vehicledetail_list, name='vehicledetail_list'),  # List vehicledetail,
    path('vehicledetail_insert', views.vehicledetail_add, name='vehicledetail_insert'),  # Add vehicledetail
    path('vehicledetail_update/<int:vehicledetail_id>/', views.vehicledetail_add, name='vehicledetail_update'),  # Update vehicledetail
    path('vehicledetail_delete/<int:vehicledetail_id>/', views.vehicledetail_delete, name='vehicledetail_delete'),  # Delete vehicledetail
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
    path('tripdetail_list/', views.tripdetail_list, name='tripdetail_list'),  # List tripdetail,
    path('tripdetail_insert', views.tripdetail_add, name='tripdetail_insert'),  # Add tripdetail
    path('tripdetail_update/<int:tripdetail_id>/', views.tripdetail_add, name='tripdetail_update'),  # Update tripdetail
    path('tripdetail_delete/<int:tripdetail_id>/', views.tripdetail_delete, name='tripdetail_delete'),  # Delete tripdetail
    path('movementtype_list/', views.movementtype_list, name='movementtype_list'),  # List movementtype,
    path('movementtype_insert', views.movementtype_add, name='movementtype_insert'),  # Add movementtype
    path('movementtype_update/<int:movementtype_id>/', views.movementtype_add, name='movementtype_update'),  # Update movementtype
    path('movementtype_delete/<int:movementtype_id>/', views.movementtype_delete, name='movementtype_delete'),  # Delete movementtype
    path('trbusinesstype_list/', views.trbusinesstype_list, name='trbusinesstype_list'),  # List trbusinesstype,
    path('trbusinesstype_insert', views.trbusinesstype_add, name='trbusinesstype_insert'),  # Add trbusinesstype
    path('trbusinesstype_update/<int:trbusinesstype_id>/', views.trbusinesstype_add, name='trbusinesstype_update'),  # Update trbusinesstype
    path('trbusinesstype_delete/<int:trbusinesstype_id>/', views.trbusinesstype_delete, name='trbusinesstype_delete'),  # Delete trbusinesstype
    path('vehiclesource_list/', views.vehiclesource_list, name='vehiclesource_list'),  # List vehiclesource,
    path('vehiclesource_insert', views.vehiclesource_add, name='vehiclesource_insert'),  # Add vehiclesource
    path('vehiclesource_update/<int:vehiclesource_id>/', views.vehiclesource_add, name='vehiclesource_update'),  # Update vehiclesource
    path('vehiclesource_delete/<int:vehiclesource_id>/', views.vehiclesource_delete, name='vehiclesource_delete'),  # Delete vehiclesource
    path('vehiclenumber_list/', views.vehiclenumber_list, name='vehiclenumber_list'),  # List vehiclenumber,
    path('vehiclenumber_insert', views.vehiclenumber_add, name='vehiclenumber_insert'),  # Add vehiclenumber
    path('vehiclenumber_update/<int:vehiclenumber_id>/', views.vehiclenumber_add, name='vehiclenumber_update'),  # Update vehiclenumber
    path('vehiclenumber_delete/<int:vehiclenumber_id>/', views.vehiclenumber_delete, name='vehiclenumber_delete'),  # Delete vehiclenumber
    path('tripclosure_list/', views.tripclosure_list, name='tripclosure_list'),  # List tripclosure,
    path('tripclosure_insert', views.tripclosure_add, name='tripclosure_insert'),  # Add tripclosure
    path('tripclosure_update/<int:tripclosure_id>/', views.tripclosure_add, name='tripclosure_update'),  # Update tripclosure
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
    path('vehiclemaster_update/<int:vehiclemaster_id>/', views.vehiclemaster_add, name='vehiclemaster_update'),  # Update vehiclemaster
    path('vehiclemaster_delete/<int:vehiclemaster_id>/', views.vehiclemaster_delete, name='vehiclemaster_delete'),  # Delete vehiclemaster
    path('rtratemaster_list/', views.rtratemaster_list, name='rtratemaster_list'),  # List rtratemaster,
    path('rtratemaster_insert', views.rtratemaster_add, name='rtratemaster_insert'),  # Add rtratemaster
    path('rtratemaster_update/<int:rtratemaster_id>/', views.rtratemaster_add, name='rtratemaster_update'),  # Update rtratemaster
    path('rtratemaster_delete/<int:rtratemaster_id>/', views.rtratemaster_delete, name='rtratemaster_delete'),  # Delete rtratemaster
    path('gstexcepmtion_list/', views.gstexcepmtion_list, name='gstexcepmtion_list'),  # List gstexcepmtion,
    path('gstexcepmtion_insert', views.gstexcepmtion_add, name='gstexcepmtion_insert'),  # Add gstexcepmtion
    path('gstexcepmtion_update/<int:gstexcepmtion_id>/', views.gstexcepmtion_add, name='gstexcepmtion_update'),  # Update gstexcepmtion
    path('gstexcepmtion_delete/<int:gstexcepmtion_id>/', views.gstexcepmtion_delete, name='gstexcepmtion_delete'),  # Delete gstexcepmtion
    path('gstmodel_list/', views.gstmodel_list, name='gstmodel_list'),  # List gstmodel,
    path('gstmodel_insert', views.gstmodel_add, name='gstmodel_insert'),  # Add gstmodel
    path('gstmodel_update/<int:gstmodel_id>/', views.gstmodel_add, name='gstmodel_update'),  # Update gstmodel
    path('gstmodel_delete/<int:gstmodel_id>/', views.gstmodel_delete, name='gstmodel_delete'),  # Delete gstmodel
    path('paymenttype_list/', views.paymenttype_list, name='paymenttype_list'),  # List paymenttype,
    path('paymenttype_insert', views.paymenttype_add, name='paymenttype_insert'),  # Add paymenttype
    path('paymenttype_update/<int:paymenttype_id>/', views.paymenttype_add, name='paymenttype_update'),  # Update paymenttype
    path('paymenttype_delete/<int:paymenttype_id>/', views.paymenttype_delete, name='paymenttype_delete'),  # Delete paymenttype
    path('crcountfrom_list/', views.crcountfrom_list, name='crcountfrom_list'),  # List crcountfrom,
    path('crcountfrom_insert', views.crcountfrom_add, name='crcountfrom_insert'),  # Add crcountfrom
    path('crcountfrom_update/<int:crcountfrom_id>/', views.crcountfrom_add, name='crcountfrom_update'),  # Update crcountfrom
    path('crcountfrom_delete/<int:crcountfrom_id>/', views.crcountfrom_delete, name='crcountfrom_delete'),  # Delete crcountfrom
    path('customer_list/', views.customer_list, name='customer_list'),  # List customer,
    path('customer_insert', views.customer_add, name='customer_insert'),  # Add customer
    path('customer_update/<int:customer_id>/', views.customer_add, name='customer_update'),  # Update customer
    path('customer_delete/<int:customer_id>/', views.customer_delete, name='customer_delete'),  # Delete customer
    path('damagereport_update/<int:damagereport_id>/', views.damagereport_add, name='damagereport_update'),  # damagereport update
    path('damagereport_insert', views.damagereport_add, name='damagereport_insert'),  # damagereport insert
    path('materialhandling_list/', views.materialhandling_list, name='materialhandling_list'),  # List Material Handling,
    path('materialhandling_insert', views.materialhandling_add, name='materialhandling_insert'),  # Add Material Handling
    path('materialhandling_update/<int:material_id>/', views.materialhandling_add, name='materialhandling_update'),  # Update Material Handling
    path('materialhandling_delete/<int:material_id>/', views.materialhandling_delete, name='materialhandling_delete'),  # Delete Material Handling
    path('packagetype_list/', views.packagetype_list, name='packagetype_list'),  # List packagetype ,
    path('packagetype_insert', views.packagetype_add, name='packagetype_insert'),  # Add packagetype
    path('packagetype_update/<int:packagetype_id>/', views.packagetype_add, name='packagetype_update'),  # Update packagetype
    path('packagetype_delete/<int:packagetype_id>/', views.packagetype_delete, name='packagetype_delete'),  # Delete packagetype
    path('currencytype_list/', views.currencytype_list, name='currencytype_list'),  # List currencytype ,
    path('currencytype_insert', views.currencytype_add, name='currencytype_insert'),  # Add currencytype
    path('currencytype_update/<int:currencytype_id>/', views.currencytype_add, name='currencytype_update'),  # Update currencytype
    path('currencytype_delete/<int:currencytype_id>/', views.currencytype_delete, name='currencytype_delete'),  # Delete currencytype
    path('stocktype_list/', views.stocktype_list, name='stocktype_list'),  # List stocktype ,
    path('stocktype_insert', views.stocktype_add, name='stocktype_insert'),  # Add stocktype
    path('stocktype_update/<int:stocktype_id>/', views.stocktype_add, name='stocktype_update'),  # Update stocktype
    path('stocktype_delete/<int:stocktype_id>/', views.stocktype_delete, name='stocktype_delete'),  # Delete currencytype
    path('load_units/', views.load_units, name='load_units'),
    path('load_units_origin/', views.load_units_origin, name='load_units_origin'),
    path('load_bays/', views.load_bays, name='load_bays'),
    path('load_bays_origin/', views.load_bays_origin, name='load_bays_origin'),
    path('warehousein_insert', views.warehousein_add, name='warehousein_insert'),  # Add warehousein
    path('warehousein_update/<int:warehousein_id>/', views.warehousein_add, name='warehousein_update'),  # Update warehousein
    path('storage_list/', views.storage_list, name='storage_list'),  # List Storage
    path('load_customer_model/', views.load_customer_model, name='load_customer_model'),
    path('dispatch_list/', views.dispatch_list, name='dispatch_list'),  # List currencytype ,
    path('dispatch_insert', views.dispatch_add, name='dispatch_insert'),  # Add dispatch
    path('dispatch_update/<int:dispatch_id>/', views.dispatch_add, name='dispatch_update'),# Update dispatch
    path('dispatch_delete/<int:dispatch_id>/', views.dispatch_delete, name='dispatch_delete'),# Delete dispatch
    path('dispatch_goods_list/<int:dispatch_id>/', views.dispatch_goods_list, name='dispatch_goods_list'),# Dispatch Goods List
    path('dispatch_remove_goods/<int:dispatch_id>/', views.dispatch_remove_goods, name='dispatch_remove_goods'),# Remove Dispatch Goods
    path('dispatch_add_goods/<int:dispatch_id>/', views.dispatch_add_goods, name='dispatch_add_goods'),# Add Dispatch Goods
    path('qr_dispatch_decoder/<int:dispatch_id>', views.qr_dispatch_decoder, name='qr_dispatch_decoder'), # qr_dispatch_decoder
    path('message_test/',views.message_test,name='message_test'),
    path('load_area_volume/',views.load_area_volume,name='load_area_volume'),
    path('load_pre_gate_in/',views.load_pre_gate_in,name='load_pre_gate_in'),
    path('invoice_list/',views.invoice_list,name='invoice_list'), # List invoice
    path('invoice_insert/',views.invoice_add,name='invoice_insert'), # Add invoice
    path('invoice_update/<int:invoice_id>',views.invoice_add,name='invoice_update'), # update invoice
    path('invoice_delete/<int:invoice_id>',views.invoice_delete,name='invoice_delete'), # delete invoice
    path('warehouse_reports/',views.warehouse_reports,name='warehouse_reports'),
    path('space_utilization_reports/',views.space_utilization_reports,name='space_utilization_reports'),
    path('stock_value_report/',views.stock_value_reports,name='stock_value_report'),
    path('damage_report_list/',views.damage_reports_list,name='damage_report_list'),
    path('deviation_report/',views.deviation_report,name='deviation_report'),
    path('shipperinvoice_list/<int:voucher_id>', views.shipper_invoice_list, name='shipperinvoice_list'),  # List invoice
    path('shipperinvoice_add/<int:voucher_id>', views.shipper_invoice_add, name='shipperinvoice_add'),  # add shipper invoice to voucher list
    path('shipperinvoice_remove/<int:voucher_id>', views.shipper_invoice_remove, name='shipperinvoice_remove'),  # remove shipper invoice to voucher list
    path('load_whrate_model/', views.load_whrate_model, name='load_whrate_model'),  # load WH rate
    path('expense_list/',views.expense_list,name='expense_list'), # List expense
    path('expense_insert/',views.expense_add,name='expense_insert'), # Add expense
    path('expense_update/<int:expense_id>',views.expense_add,name='expense_update'), # update expense
    path('expense_delete/<int:expense_id>',views.expense_delete,name='expense_delete'), # delete expense
]