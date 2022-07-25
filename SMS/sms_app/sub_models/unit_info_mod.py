from django.db import models
from ..models import Location_info

class UnitInfo(models.Model):
    unit_name = models.CharField(max_length=100, default='')
    ui_branch_name=models.ForeignKey(Location_info,on_delete=models.CASCADE,default='')
    def __str__(self):
        return self.unit_name