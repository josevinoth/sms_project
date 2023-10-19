from django.db import models
from ..models import MyUser,VehiclemasterInfo,Bunkname,City,Places

class Fuelfillinginfo(models.Model):
    ff_vehicle_num = models.ForeignKey(VehiclemasterInfo, on_delete=models.CASCADE)
    ff_fuel_rate = models.FloatField(default=0.0)
    ff_fuel_price = models.FloatField(default=0.0)
    ff_date = models.DateField()
    ff_bunk_name = models.ForeignKey(Bunkname, on_delete=models.CASCADE)
    ff_filled_ltr = models.FloatField(default=0.0)
    ff_odometer_reading = models.IntegerField(default=0)
    ff_remarks = models.TextField(max_length=500, default='', blank=True, null=True)
    ff_created_at = models.DateField(null=True, auto_now_add=True)
    ff_updated_at = models.DateField(null=True, auto_now=True)
    ff_updated_by = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='ff_updated_by',db_column='ff_updated_by', null=True)
    ff_city = models.ForeignKey(City, on_delete=models.CASCADE, default='')
    ff_loaction = models.ForeignKey(Places, on_delete=models.CASCADE, default='')

    class Meta:
        ordering = ["ff_vehicle_num"]

    def __str__(self):
        return self.ff_vehicle_num