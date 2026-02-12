from django.db import models
from ..models import CustomerInfo, TripdetailInfo, ConsignmentdetailInfo, ConsignmentgoodsInfo
from .dbs_rate_mod import Dbs_rate
from .sow_choice_mod import Sow_choice


class TransInvoiceInfo(models.Model):
    is_woh = models.BooleanField(default=False)
    ti_inv_date = models.DateField()
    ti_customer = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE)
    ti_trip = models.ForeignKey(TripdetailInfo,on_delete=models.SET_NULL,null=True,blank=True)
    ti_goods = models.ForeignKey(ConsignmentgoodsInfo,on_delete=models.SET_NULL,null=True,blank=True)
    ti_consignment = models.ForeignKey(ConsignmentdetailInfo,on_delete=models.SET_NULL,null=True,blank=True)
    ti_inv_no = models.CharField(max_length=50)
    ti_gst_in = models.CharField(max_length=50, null=True, blank=True)
    ti_customer_short_name = models.CharField(max_length=50)
    ti_state= models.CharField(max_length=10,null=True,blank=True )
    ti_pincode = models.CharField(max_length=10,null=True,blank=True )
    ti_transportation_charges = models.FloatField(default=0, null=True, blank=True, )
    ti_toll_charges = models.FloatField(default=0, null=True, blank=True, )
    ti_parking_charges = models.FloatField(default=0, null=True, blank=True, )
    ti_loading_charges = models.FloatField(default=0, null=True, blank=True, )
    ti_unloading_charges = models.FloatField(default=0, null=True, blank=True,  )
    ti_halting_charges = models.FloatField(default=0, null=True, blank=True,  )
    ti_docket_charges = models.FloatField(default=0, null=True, blank=True, )
    ti_weighment_charges = models.FloatField(default=0, null=True, blank=True, )
    ti_handling_charges = models.FloatField(default=0, null=True, blank=True  ,)
    ti_cancellation_charges = models.FloatField(default=0, null=True, blank=True, )
    ti_total = models.FloatField(default=0)
    ti_department = models.CharField(max_length=100,null=True,blank=True)
    ti_branch = models.CharField(max_length=50,null=True,blank=True)

    # 🔹 CONDITIONAL FIELDS (Manual Entry Only)
    ti_aai_sno = models.CharField(max_length=100, null=True, blank=True)  # DSV
    ti_type_of_rate = models.ForeignKey(Dbs_rate, on_delete=models.SET_NULL, null=True, blank=True)  # DBS
    ti_sow = models.ForeignKey(Sow_choice, on_delete=models.SET_NULL, null=True, blank=True)  # EIPL
    
    # Autofilled fields removed - now pulled from database:
    # - ti_eway_bill_no → goods.cg_ebillno
    # - ti_requestor → trip.tr_enquirynumber.en_requestor
    # - ti_boe_no → cons.co_consignmentnumber
    # - ti_halting_days → trip.tc_no_of_days_halting

    def __str__(self):
        return self.ti_inv_no
