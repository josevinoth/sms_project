from django.db import models
from ..models import Fuelvendor

class Bunkname(models.Model):
    bunk_name = models.CharField(max_length=30,default = '')
    bunk_location_name = models.CharField(max_length=255, verbose_name="bunk_location_name", default='')
    bunk_state = models.CharField(max_length=255, blank=True, null=True, verbose_name="bunk_state")
    bunk_address = models.TextField(max_length=100,default = '')
    bunk_fuel_vendor = models.ForeignKey(Fuelvendor, on_delete=models.CASCADE, default='')
    bunk_price = models.FloatField(blank=True, null=True,default=0.0)


    class Meta:
        ordering = ["bunk_name"]

    def __str__(self):
        return self.bunk_name