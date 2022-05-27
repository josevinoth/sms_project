from django.db import models
from ..models import Location_info,UnitInfo

class BayInfo(models.Model):
    bay_branch = models.ForeignKey(Location_info, on_delete=models.CASCADE, default='')
    bay_unit = models.ForeignKey(UnitInfo, on_delete=models.CASCADE, default='')
    bay_bayname = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.bay_bayname