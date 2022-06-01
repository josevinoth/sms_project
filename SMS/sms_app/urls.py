from django.urls import path
from . import views

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
    path('damagereport_delete/<int:damagereport_id>/', views.damagereport_delete, name='damagereport_delete'),  # Delete damagereport
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
]