from django.db import models
from .sub_models.assign_status import assign_status_info
from .sub_models.pk_item_mod import pk_itemInfo
from .sub_models.pk_itemdescription_mod import pk_itemdescriptionInfo
from .sub_models.pk_stock_status_mod import pk_stock_statusinfo
from .sub_models.gst_payable_mod import GST_payable_info
from .sub_models.tr_businesstype_mod import Tr_businesstype_Info
from .sub_models.tr_triptype_mod import Tr_triptype_Info
from .sub_models.trip_status_mod import Tripstatusinfo
from .sub_models.labels_pasted_mod import Labels_pasted_Info
from.sub_models.business_solutions_mod import Business_Sol_info
from.sub_models.yesno_info_mod import YesNoInfo
from.sub_models.prespective_customer_no_info_mod import Prespectivec_customer_NoInfo
from.sub_models.business_won_no_info_mod import Business_won_NoInfo
from.sub_models.faciltiy_requirement_mod import faciltiyrequirementinfo
from.sub_models.manpower_requirement_mod import manpowerrequirementinfo
from .sub_models.cus_new_exist_mod import Cusnewexist
from .sub_models.industry_type_mod import Industrytype
from .sub_models.wh_requirement_mod import Whrequirementinfo
from .sub_models.trans_requirement_mod import Transrequirementinfo
from .sub_models.pack_requirement_mod import Packreuqirementinfo
from .sub_models.supply_info_mod import Supplyinfo
from .sub_models.call_type_mod import Calltype
from .sub_models.call_nature_mod import Callnature
from .sub_models.call_purpose_mod import Callpurpose
from .sub_models.sales_status_mod import Salestatus
from .sub_models.bus_notwon_mod import Busnotwon
from.sub_models.service_type_info_mod import servicetype_info
from.sub_models.whchargetype_mod import Wh_chargetype
from .sub_models.stacking_mod import StackingInfo
from.sub_models.activeinactive_mod import ActiveinactiveInfo
from .sub_models.designation_mod import DesignationInfo
from .sub_models.role_mod import RoleInfo
from .sub_models.country_mod import Country
from .sub_models.state_mod import State
from .sub_models.city_mod import City
from .sub_models.places_mod import Places
from .sub_models.fumigation_action_mod import Fumigation_ActionInfo
from .sub_models.status_list_mod import StatusList
from .sub_models.location_info_mod import Location_info
from .sub_models.unit_info_mod import UnitInfo
from .sub_models.department_info_mod import Department_info
from django.contrib.auth.models import User
from .sub_models.insurance_type_mod import Insurance_Type
from .sub_models.prod_type_mod import Prod_Type
from .sub_models.prod_cat_mod import Prod_Cat
from .sub_models.product_info_mod import Product_info
from .sub_models.my_user_mod import MyUser
from .sub_models.comments_mod import commentsInfo
from .sub_models.pk_stock_purchase_type_mod import Pkstockpurchasetype
from .sub_models.vendor_info_mod import Vendor_info
from .sub_models.insurance_info_mod import Insurance_Info
from .sub_models.asset_info_mod import AssetInfo
from .sub_models.service_info_mod import Service_Info
from .sub_models.enquire_info_mod import Enquiry_Info
from .sub_models.stock_movement_type_mod import Stock_movement_type
from .sub_models.stock_type_mod import Stock_type
from .sub_models.currency_type_mod import Currency_type
from .sub_models.package_type_mod import Packagetype_info
from .sub_models.damage_mod import DamageInfo
from .sub_models.Bay_info_mod import BayInfo
from .sub_models.payment_cycle_mod import PaymentcycleInfo
from .sub_models.Customertype_info_mod import CustomertypeInfo
from .sub_models.customerdepartment_mod import CustomerdepartmentInfo
from .sub_models.gstexcemption_mod import GstexcemptionInfo
from .sub_models.gstmodel_mod import GstmodelInfo
from .sub_models.paymenttype_mod import PaymenttypeInfo
from .sub_models.crcountfrom_mod import CrcountfromInfo
from .sub_models.trbusinesstype_mod import TrbusinesstypeInfo
from .sub_models.customer_mod import CustomerInfo
from .sub_models.locationmaster_mod import LocationmasterInfo
from .sub_models.check_in_out_mod import Check_in_out
from .sub_models.uom_mod import UOM
from .sub_models.warehouse_stock_info_mod import Warehouse_stock_info
from .sub_models.assign_asset_info_mod import Assign_asset_info
from .sub_models.employee_mod import Employee
from .sub_models.student_mod import Stud_reg
from .sub_models.peo_mod import Peo_reg
from .sub_models.user_ext_mod import User_extInfo
from .sub_models.whstoragetype_mod import WhstoragetypeInfo
from .sub_models.vehicletype_mod import VehicletypeInfo
from .sub_models.Whratemaster_mod import WhratemasterInfo
from .sub_models.materialhandling_mod import Materialhandling_Info
from .sub_models.movementtype_mod import MovementtypeInfo
from .sub_models.received_not_mod import Received_not
from .sub_models.typeofotl_mod import TypeofotlInfo
from .sub_models.sealedoropened_mod import SealedoropenedInfo
from.sub_models.gatein_mod_pre import Gatein_pre_info,Gatein_pre_info_att
from .sub_models.pregatein_truck_mod import Pregateintruckinfo
from .sub_models.gatein_mod import Gatein_info
from .sub_models.damagereport_mod import DamagereportInfo,DamagereportImages
from .sub_models.loadingbay_mod import Loadingbay_Info,Loadingbayimages_Info
from .sub_models.customername_mod import CustomernameInfo_new
from .sub_models.vehiclecategory_mod import VehiclecategoryInfo
from .sub_models.dispatch_mod import Dispatch_info
from .sub_models.warehouse_goods_info_mod import Warehouse_goods_info
from .sub_models.expense_category_mod import ExpenseCategoryInfo
from .sub_models.enquirynote_mod import EnquirynoteInfo
from .sub_models.iou_mod import iou_info
from .sub_models.consignmentdetail_mod import ConsignmentdetailInfo
from .sub_models.ownership_mod import OwnershipInfo
from .sub_models.vhmanufacturer_mod import VhmanufacturerInfo
from .sub_models.vehiclemodel_mod import VehiclemodelInfo
from .sub_models.body_mod import BodyInfo
from .sub_models.axletype_mod import AxletypeInfo
from .sub_models.fueltype_mod import FueltypeInfo
from .sub_models.vehiclecolour_mod import VehiclecolourInfo
from .sub_models.permittype_mod import PermittypeInfo
from .sub_models.vehiclemaster_mod import VehiclemasterInfo
from .sub_models.tripdetail_mod import TripdetailInfo,Trip_category_info,Trip_closure_files_Info
from .sub_models.rtratemaster_mod import RtratemasterInfo
from .sub_models.upload_mod import UploadInfo
from.sub_models.expense_type_mod import ExpenseTypeInfo
from.sub_models.expense_uom_mod import ExpenseUOMInfo
from.sub_models.expense_mod import ExpenseInfo
from.sub_models.sales_info_mod import SalesInfo
from .sub_models.billing_mod import BilingInfo
from.sub_models.in_inspection_report_mod import Ininspectreport
from.sub_models.ou_inspection_report_mod import Ouinspectreport
from.sub_models.material_stock_mod import Materialstock
from.sub_models.packing_jobs_mod import Packingjobs
from.sub_models.sales_comments_mod import Sales_Comments_Info
from.sub_models.bvm_product_mod import Bvmproduct
from.sub_models.ar_info_mod import Ar_Info
from .sub_models.stock_report_combo_mod import Stock_report_combo
from .sub_models.sales_target_mod import Sales_target_info
from .sub_models.ar_comments_info_mod import Ar_comments_Info
from .sub_models.Req_module_mod import Reqmodule
from .sub_models.Req_bugimprove_mod import Reqbugimprove
from .sub_models.Requirements_mod import RequirementsInfo
from .sub_models.na_itemname_mod import Naitemname
from .sub_models.na_typeofwork_mod import Natypeofwork
from .sub_models.na_typeofpack_mod import Natypeofpack
from .sub_models.na_typeofreq_mod import Natypeofreq
from .sub_models.na_plywoodthickness_mod import Naplywoodthickness
from .sub_models.na_typeofplywood_mod import Natypeofplywood
from .sub_models.na_woodtreatmentreq_mod import Nawoodtreatmentreq
from .sub_models.na_typeofwood_mod import Natypeofwood
from .sub_models.na_bvm_customer_mod import Nabvmcustomer
from.sub_models.pk_delivery_type_mod import Nadeliverytype
from .sub_models.na_woodnorms_mod import Nawoodnorms
from .sub_models.na_typeofaccess_mod import Natypeofaccess
from .sub_models.na_consumables_mod import Naconsumables
from .sub_models.category_mod import Category
from .sub_models.source_mod import Source
from .sub_models.cost_type_mod import Costtype
from .sub_models.cost_description_mod import Costdescription
from .sub_models.unit_of_measure_mod import Unitofmeasure
from .sub_models.pk_stock_type_mod import Pkstocktype
from .sub_models.stock_description_mod import Stockdescription
from .sub_models.pk_packing_field_mod import Napackingfield
from .sub_models.pk_special_requirements import Naspecialrequirements
from .sub_models.pk_needassessment_mod import PkneedassessmentInfo
from .sub_models.pk_openingstock_mod import PkopeningstockInfo
from .sub_models.pk_stockpurchases_mod import PkstockpurchasesInfo
from .sub_models.pk_dimension_type_mod import Nadimensiontype
from .sub_models.na_dimension_mod import Nadimension
from .sub_models.pk_quotes_mod import PkquotesInfo
from .sub_models.pk_retrival_mod import PkretrivalInfo
from .sub_models.pk_quotation_mod import PkquotationInfo
from .sub_models.pk_quotation_summary_mod import PkquotationsummaryInfo
from .sub_models.pk_purchaseorder_mod import PkpurchaseorderInfo
from .sub_models.po_dimension_mod import POdimension
from .sub_models.pk_costing_mod import PkcostingInfo
from .sub_models.pk_costing_summary_mod import PkcostingsummaryInfo
from .sub_models.vehicle_allotment_mod import Vehicle_allotmentInfo
from .sub_models.test_info_mod import TestInfo
from .sub_models.fuel_vendor_mod import Fuelvendor
from .sub_models.bunk_name_mod import Bunkname
from .sub_models.fuelfilling_mod import Fuelfillinginfo
from .sub_models.enquirynote_vehicle_mod import Enquirynotevehicle
from .sub_models.consignmentgoods_mod import ConsignmentgoodsInfo
from .sub_models.pk_stock_vendor_mod import PkstockvebdorInfo
from .sub_models.applicaiton_mod import applicaiton_Info
from .sub_models.task_mod import task_Info
from .sub_models.timesheet_mod import timesheet_Info
from .sub_models.ml_category_mod_ import ml_Category,ml_Product
from .sub_models.business_revenue_mod import BusinessrevenueInfo
from .sub_models.damage_image_type_mod import damage_image_type_info
from .sub_models.picture_mod import PictureImage