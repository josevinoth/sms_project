from django.db import models
from ..models import Location_info

class LocationmasterInfo(models.Model):
    lm_wh_location = models.ForeignKey(Location_info, on_delete=models.CASCADE, default='')
    lm_wh_unit = models.CharField(max_length=20, default='')
    lm_areaside = models.CharField(max_length=10, default='')
    lm_size = models.IntegerField(default='')

    def __str__(self):
        return self.lm_wh_location