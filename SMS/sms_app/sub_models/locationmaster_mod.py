from django.db import models
from ..models import Location_info,UnitInfo,BayInfo,CustomerInfo,TrbusinesstypeInfo

class LocationmasterInfo(models.Model):
    lm_wh_location = models.ForeignKey(Location_info, on_delete=models.CASCADE)
    lm_wh_unit = models.ForeignKey(UnitInfo, on_delete=models.CASCADE)
    lm_areaside = models.ForeignKey(BayInfo, on_delete=models.CASCADE)
    lm_length = models.FloatField(default='0.0')
    lm_width = models.FloatField(default='0.0')
    lm_height = models.FloatField(default='0.0')
    lm_size = models.FloatField(default='0.0')
    lm_area_occupied = models.FloatField(default='0.0')
    lm_available_area = models.FloatField(default='0.0')
    lm_total_volume = models.FloatField(default='0.0')
    lm_available_volume = models.FloatField(default='0.0')
    lm_volume_occupied = models.FloatField(default='0.0')
    lm_concatenate = models.CharField(max_length=100,default = '')
    lm_customer_name = models.ForeignKey(CustomerInfo, on_delete=models.CASCADE, null=True, blank=True)
    lm_customer_model = models.ForeignKey(TrbusinesstypeInfo,on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Auto-calculate area and volume if they are 0 but dimensions are provided
        if self.lm_size == 0 and self.lm_length > 0 and self.lm_width > 0:
            self.lm_size = round(self.lm_length * self.lm_width, 2)
        if self.lm_total_volume == 0 and self.lm_length > 0 and self.lm_width > 0 and self.lm_height > 0:
            self.lm_total_volume = round(self.lm_length * self.lm_width * self.lm_height, 2)
        
        # Ensure available area/volume are updated if area/volume were just calculated
        if self.lm_available_area == 0 and self.lm_size > 0:
            self.lm_available_area = self.lm_size - self.lm_area_occupied
        if self.lm_available_volume == 0 and self.lm_total_volume > 0:
            self.lm_available_volume = self.lm_total_volume - self.lm_volume_occupied
            
        super(LocationmasterInfo, self).save(*args, **kwargs)

    def __str__(self):
        return str([self.lm_wh_unit,self.lm_areaside])

