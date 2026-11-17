from django.db import models

class Mc_vehicletype(models.Model):
    mc_vehicletype = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["mc_vehicletype"]

    def __str__(self):
        return self.mc_vehicletype