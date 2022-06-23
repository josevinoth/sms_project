from django.db import models
class VehicletypeInfo(models.Model):
    vt_vehicletype = models.CharField(max_length=100, null=True,default='')

    def __str__(self):
        return self.vt_vehicletype