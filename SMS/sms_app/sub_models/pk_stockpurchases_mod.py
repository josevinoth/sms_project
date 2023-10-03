from django.db import models
from ..models import MyUser,Category,Pkstocktype,Natypeofwood,Source,Vendor_info,Stockdescription,Unitofmeasure

class PkstockpurchasesInfo(models.Model):
    sp_category = models.ForeignKey(Category, on_delete=models.CASCADE, default='')
    sp_stock_type = models.ForeignKey(Pkstocktype, on_delete=models.CASCADE, default='')
    sp_type_of_wood= models.ForeignKey(Natypeofwood, on_delete=models.CASCADE, default='',blank=True, null=True)
    sp_source = models.ForeignKey(Source, on_delete=models.CASCADE, default='')
    sp_vendor_name = models.ForeignKey(Vendor_info, on_delete=models.CASCADE, default='')
    sp_vendor_bill = models.CharField(max_length=30,default = '')
    sp_vendor_bill_date = models.DateField(blank=True,null=True)
    sp_thick_height = models.FloatField(blank=True, null=True,default=0.0)
    sp_width = models.FloatField(blank=True, null=True,default=0.0)
    sp_length= models.FloatField(blank=True, null=True,default=0.0)
    sp_cft = models.FloatField(blank=True, null=True,default=0.0)
    sp_quantity= models.IntegerField(blank=True, null=True,default=0)
    sp_total_cft = models.FloatField(blank=True, null=True,default=0.0)
    sp_gst = models.FloatField(blank=True, null=True,default=0.0)
    sp_gst_amount = models.FloatField(blank=True, null=True,default=0.0)
    sp_totalbill_amount = models.FloatField(blank=True, null=True,default=0.0)
    sp_created_at = models.DateField(null=True, auto_now_add=True)
    sp_updated_at = models.DateField(null=True, auto_now=True)
    sp_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='sp_updated_by',db_column='sp_updated_by', null=True)
    sp_purchase_num=models.CharField(max_length=50,blank=True,null=True)
    sp_stock_description = models.ForeignKey(Stockdescription, on_delete=models.CASCADE, default='',blank=True, null=True)
    sp_uom = models.ForeignKey(Unitofmeasure, on_delete=models.CASCADE, default='',blank=True, null=True)
    sp_size = models.FloatField(blank=True, null=True, default=0.0)
    sp_rate = models.FloatField(blank=True, null=True, default=0.0)
    sp_price = models.FloatField(blank=True, null=True, default=0)

    class Meta:
        ordering = ["sp_purchase_num"]

    def __str__(self):
        return self.sp_purchase_num