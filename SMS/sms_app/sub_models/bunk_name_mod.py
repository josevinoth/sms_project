from django.db import models
from ..models import Fuelvendor

class Bunkname(models.Model):
    bunk_name = models.CharField(max_length=30,default = '')
    bunk_address = models.TextField(max_length=100,default = '')
    bunk_fuel_vendor = models.ForeignKey(Fuelvendor, on_delete=models.CASCADE, default='')

    class Meta:
        ordering = ["bunk_name"]

    def __str__(self):
        return self.bunk_name