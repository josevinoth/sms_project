from django.db import models
class VehiclecategoryInfo(models.Model):
    vc_vehiclecategory = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.vc_vehiclecategory