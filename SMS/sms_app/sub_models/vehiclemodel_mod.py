from django.db import models
class VehiclemodelInfo(models.Model):
    vl_vehiclemodel = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.vl_vehiclemodel