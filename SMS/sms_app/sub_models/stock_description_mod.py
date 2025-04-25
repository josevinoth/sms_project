from django.db import models
from ..models import Pkstocktype,Unitofmeasure

class Stockdescription(models.Model):
    stock_description = models.CharField(max_length=100, default='')
    stock_type = models.ForeignKey(Pkstocktype,on_delete=models.CASCADE,default='')
    stock_received = models.ForeignKey(Unitofmeasure, on_delete=models.CASCADE,related_name='stock_received', db_column='stock_received',null=True, blank=True)
    stock_Consumption = models.ForeignKey(Unitofmeasure, on_delete=models.CASCADE,related_name='stock_Consumption', db_column='stock_Consumption',null=True, blank=True)

    class Meta:
        ordering = ["stock_description"]

    def __str__(self):
        return self.stock_description