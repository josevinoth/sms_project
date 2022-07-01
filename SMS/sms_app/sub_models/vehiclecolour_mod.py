from django.db import models
class VehiclecolourInfo(models.Model):
    vh_vehiclecolour = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.vh_vehiclecolour