from django.db import models

class Supplyinfo(models.Model):
    supply_type = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["supply_type"]

    def __str__(self):
        return self.supply_type