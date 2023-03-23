from django.db import models
from ..models import Product_info,Department_info,MyUser,Location_info,Vendor_info,Insurance_Info,UnitInfo

class Ininspectreport(models.Model):
    in_pur_order_no = models.CharField(blank=True, null=True,max_length=10,default = '')
    in_pur_order_date = models.DateField(blank=True, null=True,)
    in_supp_name = models.CharField(blank=True, null=True,max_length=10,default = '')
    in_supp_invoice_no = models.CharField(blank=True, null=True,max_length=30)
    in_supp_invoice_date = models.DateField(blank=True, null=True,)
    in_trans_name = models.CharField(blank=True, null=True,max_length=10,default = '')
    in_vehicle_no = models.CharField(blank=True, null=True,max_length=10,default='')
    in_driver_name = models.CharField(blank=True, null=True,max_length=30)
    in_driver_mob_no = models.IntegerField(blank=True, null=True,default = 0)
    in_grn_no = models.CharField(blank=True, null=True,max_length=30)
    in_length=models.FloatField(blank=True, null=True,default = 0.0)
    in_width = models.FloatField(blank=True, null=True,default = 0.0)
    in_thickness = models.FloatField(blank=True, null=True,default = 0.0)
    in_kg_mtr = models.FloatField(blank=True, null=True,default = 0.0)
    in_check_mtd = models.CharField(blank=True, null=True,max_length=10,default = '')
    in_rec_qty = models.IntegerField(blank=True, null=True,default = 0)
    in_rej_qty = models.IntegerField(blank=True, null=True,default = 0)
    in_acc_qty = models.IntegerField(blank=True, null=True,default = 0)
    in_remark = models.CharField(blank=True, null=True,max_length=10,default = '')
    in_check_by = models.CharField(blank=True, null=True,max_length=10,default = '')
    in_inspec_by = models.CharField(blank=True, null=True,max_length=10,default = '')
    in_appr_by = models.CharField(blank=True, null=True,max_length=10,default = '')

    class Meta:
        ordering = ["in_pur_order_no"]

    def __str__(self):
        return self.in_pur_order_no