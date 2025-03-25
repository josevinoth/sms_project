from django.db import models
from ..models import Pkstocktype,MyUser,Costtype,Stockdescription,Unitofmeasure
class PkpartcodeInfo(models.Model):
    pc_code = models.CharField(blank=False, null=False,default='',max_length=50, unique=True)
    pc_stock_description = models.ForeignKey(Stockdescription, on_delete=models.CASCADE, default='',blank=False, null=False)
    pc_length = models.FloatField(blank=True, null=True, default=0.0)
    pc_width = models.FloatField(blank=True, null=True, default=0.0)
    pc_height = models.FloatField(blank=True, null=True, default=0.0)
    pc_uom = models.ForeignKey(Unitofmeasure, on_delete=models.CASCADE,related_name='pc_uom', db_column='pc_uom', default='',blank=True, null=True)
    pc_stock_type = models.ForeignKey(Pkstocktype, on_delete=models.CASCADE,default='', blank=False, null=False)
    pc_created_at = models.DateTimeField(null=True, auto_now_add=True)
    pc_updated_at = models.DateTimeField(null=True, auto_now=True)
    pc_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='pc_updated_by',db_column='pc_updated_by', null=True)
    pc_con_length = models.FloatField(blank=True, null=True, default=0.0)
    pc_diameter_width = models.CharField(blank=True, null=True, default=0.0)

    class Meta:
        ordering = ["pc_code"]

    def __str__(self):
        return str(self.pc_code)