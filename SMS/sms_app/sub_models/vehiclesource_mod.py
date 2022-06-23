from django.db import models
class VehiclesourceInfo(models.Model):
    vs_vehiclesource = models.CharField(max_length=100, null=True,default='')

    # def __str__(self):
    #     return self.role_name