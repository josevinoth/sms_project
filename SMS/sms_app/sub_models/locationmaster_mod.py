from django.db import models
from ..models import Location_info,UnitInfo,BayInfo,CustomerInfo

class LocationmasterInfo(models.Model):
    lm_wh_location = models.ForeignKey(Location_info, on_delete=models.CASCADE, default='')
    lm_wh_unit = models.ForeignKey(UnitInfo, on_delete=models.CASCADE, default='')
    lm_areaside = models.ForeignKey(BayInfo, on_delete=models.CASCADE, default='')
    lm_length = models.FloatField(default='0.0')
    lm_width = models.FloatField(default='0.0')
    lm_height = models.FloatField(default='0.0')
    lm_size = models.FloatField(default='0.0')
    lm_area_occupied = models.FloatField(default='0.0')
    lm_available_area = models.FloatField(default='0.0')
    lm_total_volume = models.FloatField(default='0.0')
    lm_available_volume = models.FloatField(default='0.0')
    lm_volume_occupied = models.FloatField(default='0.0')
    lm_concatenate = models.CharField(max_length=10,default = '')
    lm_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, default='')
    lm_customer_model = models.CharField(blank=True, null=True, max_length=20)
    def __str__(self):
        return str([self.lm_wh_unit,self.lm_areaside])

