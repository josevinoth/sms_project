from django.db import models
from django.urls import reverse

from .stock_purchase_status_mod import PkstockpurchaseStatus
from ..models import MyUser,Category,Pkstocktype,Source,Stockdescription,Unitofmeasure

class PkstockpurchasesInfo(models.Model):
    sp_category = models.ForeignKey(Category, on_delete=models.CASCADE, default='')
    sp_stock_type = models.ForeignKey(Pkstocktype, on_delete=models.CASCADE, default='')
    sp_source = models.ForeignKey(Source, on_delete=models.CASCADE, default='')
    sp_thick_height = models.FloatField(blank=True, null=True,default=0.0)
    sp_width = models.FloatField(blank=True, null=True,default=0.0)
    sp_length= models.FloatField(blank=True, null=True,default=0.0)
    sp_cft = models.FloatField(blank=True, null=True,default=0.0)
    sp_quantity= models.FloatField(blank=True, null=True,default=0.0)
    sp_total_cft = models.FloatField(blank=True, null=True,default=0.0)
    sp_gst = models.FloatField(blank=True, null=True,default=0.0)
    sp_gst_amount = models.FloatField(blank=True, null=True,default=0.0)
    sp_totalbill_amount = models.FloatField(blank=True, null=True,default=0.0)
    sp_created_at = models.DateTimeField(null=True, auto_now_add=True)
    sp_updated_at = models.DateTimeField(null=True, auto_now=True)
    sp_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='sp_updated_by',db_column='sp_updated_by', null=True)
    sp_purchase_num=models.CharField(max_length=50,blank=True,null=True)
    sp_stock_description = models.ForeignKey(Stockdescription, on_delete=models.CASCADE, default='',blank=True, null=True)
    sp_uom = models.ForeignKey(Unitofmeasure, on_delete=models.CASCADE, default='',blank=True, null=True)
    sp_size = models.FloatField(blank=True, null=True, default=0.0)
    sp_rate = models.FloatField(blank=True, null=True, default=0.0)
    sp_price = models.FloatField(blank=True, null=True, default=0)
    sp_stock_in_date = models.DateTimeField(blank=True, null=True)
    sp_remarks = models.TextField(blank=True, null=True)
    sp_vendor_bill = models.CharField(max_length=100,blank=True, null=True)
    sp_thick_height_reduced = models.FloatField(blank=True, null=True, default=0.0)
    sp_width_reduced = models.FloatField(blank=True, null=True, default=0.0)
    sp_length_reduced = models.FloatField(blank=True, null=True, default=0.0)
    sp_quantity_reduced = models.FloatField(blank=True, null=True, default=0.0)
    sp_cft_reduced = models.FloatField(blank=True, null=True, default=0.0)
    sp_weight = models.FloatField(blank=True, null=True, default=0.0)
    sp_status = models.ForeignKey(PkstockpurchaseStatus, on_delete=models.CASCADE, default='')
    class Meta:
        ordering = ["sp_purchase_num"]

    def __str__(self):
        if self.sp_purchase_num is None:
            return "None"  # Or any other default representation
        else:
            return str(self.sp_purchase_num)  # Convert the value to a string

    def get_absolute_url_pk_stock_purchases(self):
        return reverse('stockpurchases_update', args=[str(self.id)])