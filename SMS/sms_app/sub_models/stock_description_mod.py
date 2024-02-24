from django.db import models
from ..models import Pkstocktype

class Stockdescription(models.Model):
    stock_description = models.CharField(max_length=100, default='')
    stock_type = models.ForeignKey(Pkstocktype,on_delete=models.CASCADE,default='')


    class Meta:
        ordering = ["stock_description"]

    def __str__(self):
        return self.stock_description