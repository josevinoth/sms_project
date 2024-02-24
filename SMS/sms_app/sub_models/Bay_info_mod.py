from django.db import models
from ..models import Location_info,UnitInfo

class BayInfo(models.Model):
    bay_bayname = models.CharField(max_length=100, default='')
    bay_branch_name = models.ForeignKey(Location_info,on_delete=models.CASCADE,default='')
    Bay_unit_name = models.ForeignKey(UnitInfo,on_delete=models.CASCADE,default='')

    class Meta:
        ordering = ["bay_bayname"]

    def __str__(self):
        return self.bay_bayname