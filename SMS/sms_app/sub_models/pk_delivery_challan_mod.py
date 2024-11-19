from django.db import models
from ..models import CustomerInfo,Unitofmeasure,PkneedassessmentInfo,PkpurchaseorderInfo
class Pkdeliverychallan(models.Model):
    dc_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, blank=True, null=True)
    dc_sales_order_po = models.CharField(max_length=25)
    dc_uom = models.ForeignKey(Unitofmeasure, on_delete=models.CASCADE, default='',blank=True, null=True)
    dc_customer_address = models.CharField(max_length=200,blank=True, null=True)
    dc_customer_gstin = models.CharField(max_length=50,blank=True, null=True)
    dc_eway_billno = models.CharField(max_length=25,blank=True, null=True)
    dc_eway_date = models.DateField(blank=True, null=True)
    dc_grn = models.CharField(max_length=25,blank=True, null=True)
    dc_stock_register = models.CharField(max_length=100,blank=True, null=True)
    dc_transporter_name = models.CharField(max_length=25,blank=True, null=True)
    dc_consignment_note = models.CharField(max_length=25,blank=True, null=True)
    dc_date = models.DateField(blank=True, null=True)
    dc_vehicle_no = models.CharField(max_length=15,blank=True, null=True)
    dc_driver_name = models.CharField(max_length=25,blank=True, null=True)
    dc_driver_mobile_num = models.CharField(max_length=10,blank=True, null=True)
    dc_assessment_num=models.ForeignKey(PkneedassessmentInfo, on_delete=models.CASCADE)
    dc_customer_po = models.ForeignKey(PkpurchaseorderInfo, on_delete=models.CASCADE,blank=True, null=True)

    def __str__(self):
        return f"gate pass at {self.dc_customer_name}"