from django.db import models
from ..models import MyUser,Natypeofwood,Pkstocktype,Category,Source

class PkopeningstockInfo(models.Model):
    os_category = models.ForeignKey(Category, on_delete=models.CASCADE, default='')
    os_stock_type = models.ForeignKey(Pkstocktype, on_delete=models.CASCADE, default='')
    os_type_of_wood= models.ForeignKey(Natypeofwood,on_delete=models.CASCADE,default='')
    os_source = models.ForeignKey(Source,on_delete=models.CASCADE,default='')
    os_thick_height = models.IntegerField(blank=True, null=True,default=0)
    os_width = models.IntegerField(blank=True, null=True,default=0)
    os_length= models.IntegerField(blank=True, null=True,default=0)
    os_cft = models.FloatField(blank=True, null=True,default=0.0)
    os_price = models.FloatField(blank=True, null=True,default=0.0)
    os_quantity= models.IntegerField(blank=True, null=True,default=0)
    os_total_cft = models.FloatField(blank=True, null=True,default=0.0)
    os_value = models.FloatField(blank=True, null=True,default=0.0)
    os_gst =models.FloatField(blank=True, null=True,default=0.0)
    os_gst_amount = models.FloatField(blank=True, null=True,default=0.0)
    os_totalbill_amount = models.FloatField(blank=True, null=True,default=0.0)
    os_created_at = models.DateField(null=True, auto_now_add=True)
    os_updated_at = models.DateField(null=True, auto_now=True)
    os_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='os_updated_by',db_column='os_updated_by', null=True)
    os_stock_number= models.CharField(max_length=50,null=True,blank=True)

    class Meta:
        ordering = ["os_stock_number"]

    def __str__(self):
        return self.os_stock_number