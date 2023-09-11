from django.db import models
from ..models import Location_info,UnitInfo

class TestInfo(models.Model):
    stock_num = models.CharField(max_length=100, default='')
    date_of_arrival = models.DateTimeField(null=True,blank=True)
    unloading_start_time = models.DateTimeField(null=True,blank=True)
    unloading_end_time = models.DateTimeField(null=True,blank=True)

    class Meta:
        ordering = ["stock_num"]

    def __str__(self):
        return self.stock_num