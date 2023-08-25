from django.db import models
from ..models import Location_info,UnitInfo,BayInfo,CustomerInfo,TrbusinesstypeInfo

class LocationmasterInfo(models.Model):
    lm_wh_location = models.ForeignKey(Location_info, on_delete=models.CASCADE, default='')
    lm_wh_unit = models.ForeignKey(UnitInfo, on_delete=models.CASCADE, default='')
    lm_areaside = models.ForeignKey(BayInfo, on_delete=models.CASCADE, default='')
    lm_length = models.DecimalField(default='0.0',max_digits=50,decimal_places=3)
    lm_width = models.DecimalField(default='0.0',max_digits=50,decimal_places=3)
    lm_height = models.DecimalField(default='0.0',max_digits=50,decimal_places=3)
    lm_size = models.DecimalField(default='0.0',max_digits=50,decimal_places=3)
    lm_area_occupied = models.DecimalField(default='0.0',max_digits=50,decimal_places=3)
    lm_available_area = models.DecimalField(default='0.0',max_digits=50,decimal_places=3)
    lm_total_volume = models.DecimalField(default='0.0',max_digits=50,decimal_places=3)
    lm_available_volume = models.DecimalField(default='0.0',max_digits=50,decimal_places=3)
    lm_volume_occupied = models.DecimalField(default='0.0',max_digits=50,decimal_places=3)
    lm_concatenate = models.CharField(max_length=10,default = '')
    lm_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, default='')
    lm_customer_model = models.ForeignKey(TrbusinesstypeInfo,on_delete=models.CASCADE, default='')

    def __str__(self):
        return str([self.lm_wh_unit,self.lm_areaside])

