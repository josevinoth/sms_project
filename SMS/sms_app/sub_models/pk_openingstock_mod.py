from django.db import models
from ..models import MyUser,Natypeofwood,Stock_type,Category,Source

class PkopeningstockInfo(models.Model):
    os_item_num = models.IntegerField(blank=True, null=True,default=0.0)
    os_category = models.ForeignKey(Category, on_delete=models.CASCADE, default='')
    os_stock_type = models.ForeignKey(Stock_type, on_delete=models.CASCADE, default='')
    os_type_of_wood= models.ForeignKey(Natypeofwood,on_delete=models.CASCADE,default='')
    os_source = models.ForeignKey(Source,on_delete=models.CASCADE,default='')
    os_thick_height = models.IntegerField(blank=True, null=True,default=0)
    os_width = models.IntegerField(blank=True, null=True,default=0)
    os_length= models.IntegerField(blank=True, null=True,default=0)
    os_cft = models.FloatField(blank=True, null=True,default=0.0)
    os_price = models.FloatField(blank=True, null=True,default=0.0)
    os_quantity= models.IntegerField(blank=True, null=True,default=0)
    os_total_cft = models.IntegerField(blank=True, null=True,default=0)
    os_value = models.IntegerField(blank=True, null=True,default=0)
    os_gst = models.IntegerField(blank=True, null=True,default=0)
    os_gst_amount = models.FloatField(blank=True, null=True,default=0.0)
    os_totalbill_amount = models.FloatField(blank=True, null=True,default=0.0)
    os_created_at = models.DateField(null=True, auto_now_add=True)
    os_updated_at = models.DateField(null=True, auto_now=True)
    os_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='os_updated_by',db_column='os_updated_by', null=True)

    class Meta:
        ordering = ["os_item_num"]

    def __str__(self):
        return self.os_item_num