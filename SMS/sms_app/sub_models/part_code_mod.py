from django.db import models
from ..models import Pkstocktype,MyUser,Costtype,Stockdescription,Unitofmeasure,PkneedassessmentInfo,Nadimensiontype

class PkpartcodeInfo(models.Model):
    pc_code = models.CharField(blank=True, null=True,max_length=50, unique=True)
    pc_stock_description = models.ForeignKey(Stockdescription, on_delete=models.CASCADE, blank=True, null=True)
    pc_length = models.FloatField(blank=True, null=True, default=0.0)
    pc_width = models.FloatField(blank=True, null=True, default=0.0)
    pc_height = models.FloatField(blank=True, null=True, default=0.0)
    pc_size = models.FloatField(blank=True, null=True, default=0.0)
    pc_uom = models.ForeignKey(Unitofmeasure, on_delete=models.CASCADE,related_name='pc_uom', db_column='pc_uom', default='', blank=True, null=True)
    pc_stock_type = models.ForeignKey(Pkstocktype, on_delete=models.CASCADE, blank=True, null=True)



    class Meta:
        ordering = ["pc_code"]

    def __str__(self):
        return str(self.pc_code)