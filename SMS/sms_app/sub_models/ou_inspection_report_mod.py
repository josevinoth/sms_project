from django.db import models
from ..models import Product_info,Department_info,MyUser,Location_info,Vendor_info,Insurance_Info,UnitInfo

class Ouinspectreport(models.Model):
    ou_pur_order_no = models.CharField(blank=True, null=True,max_length=10,default = '')
    ou_pur_order_date = models.DateField(blank=True, null=True,)
    ou_cus_name = models.CharField(blank=True, null=True,max_length=10,default = '')
    ou_invoice_no = models.CharField(blank=True, null=True,max_length=30)
    ou_invoice_date = models.DateField(blank=True, null=True,)
    ou_trans_name = models.CharField(blank=True, null=True,max_length=10,default = '')
    ou_vehicle_no = models.CharField(blank=True, null=True,max_length=10,default='')
    ou_driver_name = models.CharField(blank=True, null=True,max_length=30)
    ou_driver_mob_no = models.IntegerField(blank=True, null=True,default = 0)
    ou_length=models.FloatField(blank=True, null=True,default = 0.0)
    ou_width = models.FloatField(blank=True, null=True,default = 0.0)
    ou_thickness = models.FloatField(blank=True, null=True,default = 0.0)
    ou_kg_mtr = models.FloatField(blank=True, null=True,default = 0.0)
    ou_check_mtd = models.CharField(blank=True, null=True,max_length=10,default = '')
    ou_rej_qty = models.IntegerField(blank=True, null=True,default = 0)
    ou_acc_qty = models.IntegerField(blank=True, null=True,default = 0)
    ou_remark = models.CharField(blank=True, null=True,max_length=10,default = '')
    ou_check_by = models.CharField(blank=True, null=True,max_length=10,default = '')
    ou_inspec_by = models.CharField(blank=True, null=True,max_length=10,default = '')
    ou_appr_by = models.CharField(blank=True, null=True,max_length=10,default = '')

    class Meta:
        ordering = ["ou_pur_order_no"]

    def __str__(self):
        return self.ou_pur_order_no