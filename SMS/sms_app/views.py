from .sub_views.assetinfo_view import assetinfo_add,asset_list,asset_delete
from .sub_views.assign_asset_add_view import assign_asset_add,assign_asset_delete,assign_asset_list_new
from .sub_views.department_add_view import department_add,department_delete,department_list
from .sub_views.goods_add_view import goods_add,goods_list,goods_delete
from .sub_views.goods_check_view import goods_check
from .sub_views.home_page_view import home_page
from .sub_views.insurance_add_view import insurance_add,insurance_delete,insurance_list
from .sub_views.location_add_view import location_add,location_list,location_delete
from .sub_views.login_page_view import login_page
from .sub_views.login_page_view_new import login_page_new,home_page_new
from .sub_views.logout_page_view import logout_page
from .sub_views.print_pdf_view import print_pdf
from .sub_views.product_add_view import product_add,product_list,product_delete
from .sub_views.producttype_add_view import producttype_list,producttype_delete,producttype_add
from .sub_views.qr_code_asset_view import qr_code_asset
from .sub_views.qr_code_goods_view import qr_code_goods
from .sub_views.registration_page_view import registration_page
from .sub_views.reports_view import reports,damage_report_pdf,warehouse_reports,space_utilization_reports,stock_value_reports,damage_reports_list,deviation_report
from .sub_views.service_add_view import service_add,service_list,service_delete
from .sub_views.stock_add_view import stock_add,stock_list,stock_delete
from .sub_views.user_add_view import user_add,user_list,user_delete
from .sub_views.vendor_add_view import vendor_add,vendor_list,vendor_delete
from .sub_views.country_add_view import country_list,country_delete,country_add
from .sub_views.state_add_view import state_list,state_delete,state_add
from .sub_views.city_add_view import city_add,city_list,city_delete
from .sub_views.insurancetype_add_view import insurancetype_add,insurancetype_delete,insurancetype_list
from .sub_views.stud_add_view import stud_add,stud_delete,stud_list
from .sub_views.peo_add_view import peo_add,peo_list,peo_delete
from .sub_views.damage_add_view import damage_add,damage_list,damage_delete
from .sub_views.damagereport_add_view import damagereport_add,damagereport_list
from .sub_views.locationmaster_add_view import locationmaster_add,locationmaster_list,locationmaster_delete,load_customer_model
from .sub_views.employee_add_view import emp_add,emp_list,emp_delete,emp_registration_page
from .sub_views.unit_add_view import unit_add,unit_list,unit_delete
from .sub_views.Bay_add_view import bay_add,bay_list,bay_delete
from .sub_views.status_add_view import status_add,status_list,status_delete
from .sub_views.Customertype_add_view import customertype_add,customertype_list,customertype_delete
from .sub_views.whratemasteradd_view import whratemaster_add,whratemaster_list,whratemaster_delete
from .sub_views.designation_add_view import designation_add,designation_list,designation_delete
from .sub_views.whstoragetype_add_view import whstoragetype_add,whstoragetype_list,whstoragetype_delete
from .sub_views.role_add_view import role_add,role_list,role_delete
from .sub_views.password_reset_request_view import password_reset_request
from .sub_views.wh_job_add_view import wh_job_add,wh_job_list,wh_job_delete
from .sub_views.gatein_add_view import gatein_add,gatein_list,gatein_delete,load_pre_gate_in,get_queryset
from .sub_views.loadingbay_add_view import loadingbay_add,load_currency_value
from .sub_views.enquirynote_add_view import enquirynote_add,enquirynote_list,enquirynote_delete,consignment_note_connect
from .sub_views.consignmentdetail_add_view import consignmentdetail_add,consignmentdetail_list,consignmentdetail_delete,consignmentdetail_nav
from .sub_views.vehicledetail_add_view import vehicledetail_add,vehicledetail_list,vehicledetail_delete
from .sub_views.customername_add_view import customername_add,customername_list,customername_delete
from .sub_views.vehiclecategory_add_view import vehiclecategory_add,vehiclecategory_list,vehiclecategory_delete
from .sub_views.customerdepartment_add_view import customerdepartment_add,customerdepartment_list,customerdepartment_delete
from .sub_views.vehicletype_add_view import vehicletype_add,vehicletype_list,vehicletype_delete
from .sub_views.tripdetail_add_view import tripdetail_add,tripdetail_list,tripdetail_delete,tripdetail_nav
from .sub_views.movementtype_add_view import movementtype_add,movementtype_list,movementtype_delete
from .sub_views.trbusinesstype_add_view import trbusinesstype_add,trbusinesstype_list,trbusinesstype_delete
from .sub_views.vehiclesource_add_view import vehiclesource_add,vehiclesource_list,vehiclesource_delete
from .sub_views.vehiclenumber_add_view import vehiclenumber_add,vehiclenumber_list,vehiclenumber_delete
from .sub_views.tripclosure_add_view import tripclosure_add,tripclosure_list,tripclosure_delete,tripclosure_nav
from .sub_views.vhmanufacturer_add_view import vhmanufacturer_add,vhmanufacturer_list,vhmanufacturer_delete
from .sub_views.vehiclemodel_add_view import vehiclemodel_add,vehiclemodel_list,vehiclemodel_delete
from .sub_views.ownership_add_view import ownership_add,ownership_list,ownership_delete
from .sub_views.body_add_view import body_add,body_list,body_delete
from .sub_views.axletype_add_view import axletype_add,axletype_list,axletype_delete
from .sub_views.fueltype_add_view import fueltype_add,fueltype_list,fueltype_delete
from .sub_views.vehiclecolour_add_view import vehiclecolour_add,vehiclecolour_list,vehiclecolour_delete
from .sub_views.permittype_add_view import permittype_add,permittype_list,permittype_delete
from .sub_views.vehiclemaster_add_view import vehiclemaster_add,vehiclemaster_list,vehiclemaster_delete
from .sub_views.rtratemaster_add_view import rtratemaster_add,rtratemaster_list,rtratemaster_delete
from .sub_views.gstexcepmtion_add_view import gstexcepmtion_add,gstexcepmtion_list,gstexcepmtion_delete
from .sub_views.gstmodel_add_view import gstmodel_add,gstmodel_list,gstmodel_delete
from .sub_views.paymenttype_add_view import paymenttype_add,paymenttype_list,paymenttype_delete
from .sub_views.crcountfrom_add_view import crcountfrom_add,crcountfrom_list,crcountfrom_delete
from .sub_views.customer_add_view import customer_add,customer_list,customer_delete
from .sub_views.materialhandling_add_view import materialhandling_list,materialhandling_delete,materialhandling_add
from .sub_views.packagetype_add_view import packagetype_list,packagetype_delete,packagetype_add
from .sub_views.currency_type_add_view import currencytype_add,currencytype_list,currencytype_delete
from .sub_views.stock_type_add_view import stocktype_add,stocktype_delete,stocktype_list
from .sub_views.warehouse_add_view import warehousein_add,load_units,load_bays,load_area_volume,load_units_origin,load_bays_origin,warehouseout_add,warehouseout_cancel
from .sub_views.storage_add_view import storage_list
from .sub_views.dispatch_add_view import dispatch_list,dispatch_delete,dispatch_add,dispatch_goods_list,dispatch_remove_goods,dispatch_add_goods,qr_dispatch_decoder
from .sub_views.message_test import message_test
from .sub_views.gatein_pre_add_view import gatein_pre_add,gatein_pre_list,gatein_pre_delete,pre_gatein_search
from .sub_views.invoice_view import invoice_list,invoice_add,invoice_delete,shipper_invoice_list,shipper_invoice_add,shipper_invoice_remove,load_whrate_model,case_to_case_invoice_list_open,dedicated_invoice_list_open,exclusive_invoice_list_open,invoice_report
from .sub_views.expense_view import expense_add,expense_list,expense_delete
from .sub_views.salesinfo_view import sales_add,sales_list,sales_delete,sales_comments_list,sales_comments_add,sales_comments_delete,sales_search,sales_comments_search
from .sub_views.ininspectionreport_view import ininspectreport_add,ininspectreport_list,ininspectreport_delete
from .sub_views.ouinspectionreport_view import ouinspectreport_add,ouinspectreport_list,ouinspectreport_delete
from .sub_views.materialstock_view import materialstock_add,materialstock_list,materialstock_delete
from .sub_views.packingjobs_view import packingjobs_add,packingjobs_list,packingjobs_delete
from .sub_views.arinfo_view import ar_add,ar_list,ar_delete
from .sub_views.sales_target_add_view import sales_target_add,sales_target_list,sales_target_delete
from .sub_views.arcomments_add_view import arcomments_add,arcomments_list,arcomments_delete
from .sub_views.Requirements_add_view import requirements_add,requirements_list,requirements_delete
from .sub_views.pk_needassessment_view import needassessment_add,needassessment_list,needassessment_delete,na_dimension_add,na_dimension_list,na_dimension_delete,na_dimension_cancel
from .sub_views.pk_openingstock_view import openingstock_add,openingstock_list,openingstock_delete
from .sub_views.pk_stockpurchases_view import stockpurchases_add,stockpurchases_list,stockpurchases_delete
from .sub_views.pk_purchaseorder_view import purchaseorder_add,purchaseorder_list,purchaseorder_delete
from .sub_views.pk_quotes_view import quotes_add,quotes_list,quotes_delete
from .sub_views.pk_costing_view import costing_add,costing_list,costing_delete
from .sub_views.pk_costing_summary_view import costingsummary_add,costingsummary_list,costingsummary_delete
from .sub_views.vehicle_allotment_view import vehicle_allotment_list,vehicle_allotment_add,vehicle_allotment_delete,vehicle_allotment_nav