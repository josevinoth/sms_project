from django.db import models

class Shipment_type(models.Model):
    shipment_type = models.CharField(max_length=30,default = '')

    class Meta:
        ordering = ["shipment_type"]

    def __str__(self):
        return self.shipment_type