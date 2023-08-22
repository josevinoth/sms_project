from django.db import models
from ..models import MyUser,Category,Stock_type,Natypeofwood,Source,Vendor_info

class PkstockpurchasesInfo(models.Model):
    sp_category = models.ForeignKey(Category, on_delete=models.CASCADE, default='')
    sp_stock_type = models.ForeignKey(Stock_type, on_delete=models.CASCADE, default='')
    sp_type_of_wood= models.ForeignKey(Natypeofwood, on_delete=models.CASCADE, default='')
    sp_source = models.ForeignKey(Source, on_delete=models.CASCADE, default='')
    sp_vendor_name = models.ForeignKey(Vendor_info, on_delete=models.CASCADE, default='')
    sp_vendor_bill = models.CharField(max_length=30,default = '')
    sp_vendor_bill_date = models.DateField(blank=True,null=True)
    sp_thick_height = models.IntegerField(blank=True, null=True,default=0)
    sp_width = models.IntegerField(blank=True, null=True,default=0)
    sp_length= models.IntegerField(blank=True, null=True,default=0)
    sp_cft = models.FloatField(blank=True, null=True,default=0.0)
    sp_price = models.FloatField(blank=True, null=True,default=0.0)
    sp_quantity= models.IntegerField(blank=True, null=True,default=0)
    sp_total_cft = models.IntegerField(blank=True, null=True,default=0)
    sp_value = models.IntegerField(blank=True, null=True,default=0)
    sp_gst = models.IntegerField(blank=True, null=True,default=0)
    sp_gst_amount = models.FloatField(blank=True, null=True,default=0.0)
    sp_totalbill_amount = models.FloatField(blank=True, null=True,default=0.0)
    sp_created_at = models.DateField(null=True, auto_now_add=True)
    sp_updated_at = models.DateField(null=True, auto_now=True)
    sp_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='sp_updated_by',db_column='sp_updated_by', null=True)

    class Meta:
        ordering = ["sp_vendor_name"]

    def __str__(self):
        return self.sp_vendor_name