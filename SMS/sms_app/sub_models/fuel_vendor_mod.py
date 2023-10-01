from django.db import models

class Fuelvendor(models.Model):
    fuel_vendor = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["fuel_vendor"]

    def __str__(self):
        return self.fuel_vendor